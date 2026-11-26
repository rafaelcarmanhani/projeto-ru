"""
Comparação entre:
  (A)  Baseline: split aleatório 70/30 (train/calib), misturando os 3 anos
  (B)  Temporal "forward": treino = 2023+2024, calibração = 2025
  (B') Temporal "forward" + JITTER: mesma ideia do (B), mas o treino usa
       5 clones jitterados de 2023 e 5 de 2024, e a calibração usa 5 clones
       jitterados de 2025 (calib_fit). O objetivo é suavizar a estimativa do
       quantil (95º percentil dos resíduos), que tende a ficar instável com
       poucos dados — ex.: no diagnóstico anterior, o grupo "transição" da
       área 2 tinha só 33 observações em calib_fit.

REGRAS DO JITTER (importantes, leia antes de mudar os parâmetros):
  - O ruído gaussiano é aplicado SOMENTE às variáveis meteorológicas
    contínuas (Precipitacao_mm, Temp_max_C, Temp_min_C, Umid_rel_ar,
    Vento_velocidade_ms, Vento_rajada_maxima_ms).
  - NUNCA jitteramos colunas categóricas (pratos, dia da semana etc.) nem as
    colunas de calendário que definem o grupo "transição"
    (dias_desde_ultimas_ferias, dias_ate_ferias) — mexer nelas mudaria a
    própria classificação transição/normal.
  - NUNCA jitteramos o alvo (`total`) — jitterar y contaminaria a medida de
    erro que estamos tentando avaliar.
  - O bloco de TESTE (usado só pra medir MAE/cobertura) nunca é clonado nem
    jitterado — precisa refletir dados reais, senão a avaliação deixa de ser
    honesta.
  - O ruído de cada coluna é escalado pelo desvio-padrão dela
    (ruido = RUIDO_FRAC * std_da_coluna), para não aplicar a mesma
    magnitude de ruído em variáveis com escalas muito diferentes (ex.: mm de
    chuva vs. °C vs. m/s de vento).

Cada cenário roda N_REPETICOES vezes com seeds diferentes, e o resultado
final é a média ± desvio padrão de MAE, margens e cobertura.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor

DATA_DIR = Path(__file__).resolve().parent

ALPHA = 0.05
NIVEL_CONFIANCA = 1 - ALPHA
N_ESTIMATORS = 200
N_REPETICOES = 15
SEEDS = list(range(N_REPETICOES))

# --- Parâmetros do jitter ---
N_CLONES = 5
RUIDO_FRAC = 0.35          # ruído = RUIDO_FRAC * desvio-padrão da coluna
INCLUIR_ORIGINAL = True    # se True, mantém a linha real (sem ruído) além dos N_CLONES
COLUNAS_JITTER = [
    'Precipitacao_mm', 'Temp_max_C', 'Temp_min_C',
    'Umid_rel_ar', 'Vento_velocidade_ms', 'Vento_rajada_maxima_ms',
]


# --------------------------------------------------------------------------
# 1. Carregar e preparar os dados (mesma lógica dos notebooks Previsao_areaX)
# --------------------------------------------------------------------------
def carregar_area_raw(area):
    """Retorna o dataframe cru (antes do one-hot), já filtrado, e a lista de
    colunas categóricas a serem usadas no one-hot encoding."""
    if area == 1:
        data = pd.read_csv(DATA_DIR / 'dataatea1clima.csv', header=0)
        data = data[data['refeicao'] != 'cafe da manha'].copy()
        data = data.dropna()
        data = data[data['total'] != 0]
        onehot_cols = ['Mês', 'Dia_semana', 'Dia_mês', 'prato_principal_1',
                       'prato_principal_2', 'guarnição', 'sobremesa_1', 'refeicao']
    else:
        data = pd.read_csv(DATA_DIR / 'dataarea2clima.csv', header=0)
        onehot_cols = ['Mês', 'Dia_semana', 'Dia_mês', 'prato_principal_1',
                       'prato_principal_2', 'guarnição', 'sobremesa_1']

    data = data.groupby("guarnição").filter(lambda x: len(x) >= 5)
    data = data.groupby("prato_principal_1").filter(lambda x: len(x) >= 5)
    data = data.groupby("prato_principal_2").filter(lambda x: len(x) >= 5)
    data = data.groupby("sobremesa_1").filter(lambda x: len(x) >= 5)

    return data.reset_index(drop=True), onehot_cols


def carregar_area_encoded(area):
    """Versão já com one-hot aplicado (usada pelos cenários A e B, sem jitter)."""
    data_raw, onehot_cols = carregar_area_raw(area)
    data_enc = pd.get_dummies(data_raw, columns=onehot_cols)
    atributos = data_enc.drop(columns=['total']).columns
    X = data_enc[atributos]
    y = data_enc['total']
    return data_raw, X, y


# --------------------------------------------------------------------------
# 2. Jitter: gera clones com ruído gaussiano nas colunas meteorológicas
# --------------------------------------------------------------------------
def gerar_clones(df, colunas_jitter, n_clones, ruido_frac, incluir_original, seed_base):
    """Gera n_clones cópias jitteradas de df (+ o original, se incluir_original)."""
    stds = df[colunas_jitter].std()
    partes = []
    if incluir_original:
        partes.append(df.copy())

    rng = np.random.default_rng(seed_base)
    for _ in range(n_clones):
        clone = df.copy()
        for col in colunas_jitter:
            ruido = rng.normal(0, ruido_frac * stds[col], size=len(clone))
            clone[col] = clone[col] + ruido
        # evita valores fisicamente absurdos após o ruído
        clone['Umid_rel_ar'] = clone['Umid_rel_ar'].clip(0, 100)
        clone['Precipitacao_mm'] = clone['Precipitacao_mm'].clip(lower=0)
        clone['Vento_velocidade_ms'] = clone['Vento_velocidade_ms'].clip(lower=0)
        clone['Vento_rajada_maxima_ms'] = clone['Vento_rajada_maxima_ms'].clip(lower=0)
        partes.append(clone)

    return pd.concat(partes, ignore_index=True)


# --------------------------------------------------------------------------
# 3. Treinar o ensemble (mesma arquitetura dos notebooks)
# --------------------------------------------------------------------------
def treinar_ensemble(X_train, y_train, random_state):
    ensemble = VotingRegressor(
        estimators=[('gb', GradientBoostingRegressor(n_estimators=N_ESTIMATORS, random_state=random_state)),
                    ('rf', RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=random_state))],
        weights=[3, 1]
    )
    ensemble.fit(X_train, y_train)
    return ensemble


# --------------------------------------------------------------------------
# 4. Calibrar (margem conformal) usando calib_fit, avaliar em test
# --------------------------------------------------------------------------
def calibrar_e_avaliar(ensemble, X_calib_fit, y_calib_fit, X_test, y_test):
    y_calib_pred = ensemble.predict(X_calib_fit)
    residuos_calib = np.abs(y_calib_fit.to_numpy() - y_calib_pred)

    mask_trans_calib = ((X_calib_fit['dias_desde_ultimas_ferias'] <= 10) |
                         (X_calib_fit['dias_ate_ferias'] <= 10)).to_numpy()

    residuos_transicao = residuos_calib[mask_trans_calib]
    residuos_normais = residuos_calib[~mask_trans_calib]

    margem_transicao = (np.quantile(residuos_transicao, NIVEL_CONFIANCA, method='higher')
                         if len(residuos_transicao) > 0 else np.nan)
    margem_normal = (np.quantile(residuos_normais, NIVEL_CONFIANCA, method='higher')
                      if len(residuos_normais) > 0 else np.nan)
    margem_total = np.quantile(residuos_calib, NIVEL_CONFIANCA, method='higher')

    # --- Avaliação honesta no bloco de teste (nunca visto, nunca jitterado) ---
    y_test_pred = ensemble.predict(X_test)
    residuos_test = y_test.to_numpy() - y_test_pred
    mae_test = np.mean(np.abs(residuos_test))

    mask_trans_test = ((X_test['dias_desde_ultimas_ferias'] <= 10) |
                        (X_test['dias_ate_ferias'] <= 10)).to_numpy()
    margem_usada_test = np.where(mask_trans_test, margem_transicao, margem_normal)

    dentro_intervalo = np.abs(residuos_test) <= margem_usada_test
    cobertura = dentro_intervalo.mean()

    return {
        'n_calib_fit': len(y_calib_fit),
        'n_test': len(y_test),
        'MAE_test': mae_test,
        'margem_transicao': margem_transicao,
        'margem_normal': margem_normal,
        'margem_geral': margem_total,
        'margem_media_aplicada': np.nanmean(margem_usada_test),
        'cobertura_teste (%)': cobertura * 100,
    }


# --------------------------------------------------------------------------
# 5a. Cenário A (baseline) e B (temporal, sem jitter) — uma execução
# --------------------------------------------------------------------------
def rodar_execucao_sem_jitter(cenario, X, y, X_train_fixo, y_train_fixo,
                               X_calib_pool_fixo, y_calib_pool_fixo, seed):
    if cenario == 'A':
        X_train, X_rest, y_train, y_rest = train_test_split(
            X, y, test_size=0.3, random_state=seed
        )
    else:  # 'B'
        X_train, y_train = X_train_fixo, y_train_fixo
        X_rest, y_rest = X_calib_pool_fixo, y_calib_pool_fixo

    X_calib_fit, X_test, y_calib_fit, y_test = train_test_split(
        X_rest, y_rest, test_size=0.5, random_state=seed
    )

    ens = treinar_ensemble(X_train, y_train, random_state=seed)
    res = calibrar_e_avaliar(ens, X_calib_fit, y_calib_fit, X_test, y_test)
    res['n_train'] = len(y_train)
    res['seed'] = seed
    return res


# --------------------------------------------------------------------------
# 5b. Cenário B' (temporal + jitter) — uma execução
# --------------------------------------------------------------------------
def rodar_execucao_com_jitter(data_raw, onehot_cols, seed):
    raw_2023 = data_raw[data_raw['Ano'] == 2023]
    raw_2024 = data_raw[data_raw['Ano'] == 2024]
    raw_2025 = data_raw[data_raw['Ano'] == 2025]

    # Treino: 5 clones jitterados de 2023 + 5 de 2024 (+ originais, por padrão)
    treino_2023_jit = gerar_clones(raw_2023, COLUNAS_JITTER, N_CLONES, RUIDO_FRAC,
                                    INCLUIR_ORIGINAL, seed_base=seed * 1000 + 1)
    treino_2024_jit = gerar_clones(raw_2024, COLUNAS_JITTER, N_CLONES, RUIDO_FRAC,
                                    INCLUIR_ORIGINAL, seed_base=seed * 1000 + 2)
    treino_raw = pd.concat([treino_2023_jit, treino_2024_jit], ignore_index=True)

    # calib_fit / test: primeiro separa 2025 real em duas metades; só o lado
    # da calibração é clonado/jitterado depois. O teste fica sempre "limpo".
    raw_2025_calib, raw_2025_test = train_test_split(
        raw_2025, test_size=0.5, random_state=seed
    )
    calib_raw_jit = gerar_clones(raw_2025_calib, COLUNAS_JITTER, N_CLONES, RUIDO_FRAC,
                                  INCLUIR_ORIGINAL, seed_base=seed * 1000 + 3)
    test_raw = raw_2025_test.copy()

    # One-hot conjunto para garantir que as colunas fiquem alinhadas entre
    # treino / calibração / teste
    combinado = pd.concat(
        [treino_raw.assign(_bloco='train'),
         calib_raw_jit.assign(_bloco='calib'),
         test_raw.assign(_bloco='test')],
        ignore_index=True
    )
    combinado_enc = pd.get_dummies(combinado, columns=onehot_cols)

    atributos = combinado_enc.drop(columns=['total', '_bloco']).columns
    X_train = combinado_enc.loc[combinado_enc['_bloco'] == 'train', atributos]
    y_train = combinado_enc.loc[combinado_enc['_bloco'] == 'train', 'total']
    X_calib = combinado_enc.loc[combinado_enc['_bloco'] == 'calib', atributos]
    y_calib = combinado_enc.loc[combinado_enc['_bloco'] == 'calib', 'total']
    X_test = combinado_enc.loc[combinado_enc['_bloco'] == 'test', atributos]
    y_test = combinado_enc.loc[combinado_enc['_bloco'] == 'test', 'total']

    ens = treinar_ensemble(X_train, y_train, random_state=seed)
    res = calibrar_e_avaliar(ens, X_calib, y_calib, X_test, y_test)
    res['n_train'] = len(y_train)
    res['seed'] = seed
    return res


# --------------------------------------------------------------------------
# 6. Rodar N_REPETICOES vezes cada cenário e agregar (média ± desvio padrão)
# --------------------------------------------------------------------------
def agregar(execucoes, nome_cenario):
    df_exec = pd.DataFrame(execucoes)
    return {
        'cenario': nome_cenario,
        'n_train': df_exec['n_train'].iloc[0],
        'n_calib_fit (méd.)': df_exec['n_calib_fit'].mean(),
        'n_test (méd.)': df_exec['n_test'].mean(),
        'MAE_test (méd.)': df_exec['MAE_test'].mean(),
        'MAE_test (dp)': df_exec['MAE_test'].std(),
        'margem_geral (méd.)': df_exec['margem_geral'].mean(),
        'margem_geral (dp)': df_exec['margem_geral'].std(),
        'margem_transicao (méd.)': df_exec['margem_transicao'].mean(),
        'margem_normal (méd.)': df_exec['margem_normal'].mean(),
        'cobertura_teste % (méd.)': df_exec['cobertura_teste (%)'].mean(),
        'cobertura_teste % (dp)': df_exec['cobertura_teste (%)'].std(),
        'cobertura_teste % (min)': df_exec['cobertura_teste (%)'].min(),
        'cobertura_teste % (max)': df_exec['cobertura_teste (%)'].max(),
    }


def rodar_cenarios(area):
    data_raw, onehot_cols = carregar_area_raw(area)
    _, X, y = carregar_area_encoded(area)

    idx_train_b = data_raw['Ano'].isin([2023, 2024])
    idx_calib_pool_b = data_raw['Ano'] == 2025
    X_train_b, y_train_b = X[idx_train_b], y[idx_train_b]
    X_calib_pool_b, y_calib_pool_b = X[idx_calib_pool_b], y[idx_calib_pool_b]

    linhas = []

    # --- A) baseline ---
    exec_a = [rodar_execucao_sem_jitter('A', X, y, None, None, None, None, seed)
              for seed in SEEDS]
    linhas.append(agregar(exec_a, 'A) Baseline (aleatório 70/30)'))

    # --- B) temporal sem jitter ---
    exec_b = [rodar_execucao_sem_jitter('B', X, y, X_train_b, y_train_b,
                                         X_calib_pool_b, y_calib_pool_b, seed)
              for seed in SEEDS]
    linhas.append(agregar(exec_b, "B) Temporal: treino 2023-24 / calib 2025"))

    # --- B') temporal com jitter (5 clones 23, 5 clones 24, 5 clones calib 25) ---
    exec_bj = [rodar_execucao_com_jitter(data_raw, onehot_cols, seed) for seed in SEEDS]
    linhas.append(agregar(
        exec_bj,
        f"B') Temporal + jitter ({N_CLONES} clones/ano, ruído={RUIDO_FRAC})"
    ))

    df_res = pd.DataFrame(linhas).set_index('cenario')
    return df_res


if __name__ == '__main__':
    for area in (1, 2):
        print(f"\n{'='*100}\nÁREA {area}  (média de {N_REPETICOES} repetições por cenário)\n{'='*100}")
        df = rodar_cenarios(area)
        with pd.option_context('display.width', 200, 'display.max_columns', None,
                                'display.float_format', '{:.2f}'.format):
            print(df.T)

"""
    ====================================================================================================
ÁREA 1  (média de 15 repetições por cenário)
====================================================================================================
cenario                   A) Baseline (aleatório 70/30)  B) Temporal: treino 2023-24 / calib 2025  B') Temporal + jitter (5 clones/ano, ruído=0.35)
n_train                                          954.00                                    918.00                                           5508.00
n_calib_fit (méd.)                               204.00                                    222.00                                           1332.00
n_test (méd.)                                    205.00                                    223.00                                            223.00
MAE_test (méd.)                                  125.06                                    151.23                                            147.01
MAE_test (dp)                                      9.30                                      4.62                                              4.58
margem_geral (méd.)                              341.13                                    379.51                                            372.04
margem_geral (dp)                                 25.26                                     11.91                                             15.35
margem_transicao (méd.)                          336.04                                    354.57                                            350.06
margem_normal (méd.)                             340.63                                    387.54                                            387.36
cobertura_teste % (méd.)                          95.06                                     93.96                                             94.26
cobertura_teste % (dp)                             2.63                                      1.68                                              1.85
cobertura_teste % (min)                           90.73                                     91.93                                             91.48
cobertura_teste % (max)                           99.51                                     96.86                                             97.76

====================================================================================================
ÁREA 2  (média de 15 repetições por cenário)
====================================================================================================
cenario                   A) Baseline (aleatório 70/30)  B) Temporal: treino 2023-24 / calib 2025  B') Temporal + jitter (5 clones/ano, ruído=0.35)
n_train                                          422.00                                    404.00                                           2424.00
n_calib_fit (méd.)                                90.00                                     99.00                                            594.00
n_test (méd.)                                     91.00                                    100.00                                            100.00
MAE_test (méd.)                                   54.27                                     63.06                                             59.84
MAE_test (dp)                                      6.94                                      3.26                                              2.80
margem_geral (méd.)                              151.43                                    182.17                                            178.33
margem_geral (dp)                                 24.08                                     19.95                                             15.29
margem_transicao (méd.)                          161.47                                    116.48                                            106.21
margem_normal (méd.)                             145.44                                    199.29                                            195.98
cobertura_teste % (méd.)                          93.26                                     93.60                                             93.33
cobertura_teste % (dp)                             3.50                                      2.53                                              2.32
cobertura_teste % (min)                           85.71                                     89.00                                             90.00
cobertura_teste % (max)                           98.90                                     98.00                                             99.00
"""