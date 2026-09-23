
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)

CSV_PATH = "projeto-ru\previsao\data\dataarea1.csv"

# Colunas climáticas que não são usadas na previsão (mesmo critério do notebook original)
COLUNAS_CLIMA = [
    "Precipitacao_mm", "Temp_max_C", "Temp_min_C",
    "Umid_rel_ar", "Vento_velocidade_ms", "Vento_rajada_maxima_ms",
]

COLUNAS_ONEHOT = [
    "Mês", "Dia_semana", "Dia_mês", "prato_principal_1",
    "prato_principal_2", "guarnição", "sobremesa_1", "refeicao",
]


# ---------------------------------------------------------------------------
# Carregamento e preparação dos dados
# ---------------------------------------------------------------------------

def carregar_e_preparar_dados(csv_path: str = CSV_PATH):
    """
    Carrega o CSV da área 1, aplica as mesmas limpezas do notebook original
    e retorna:
      - X, y: atributos e alvo (após one-hot encoding)
      - atributos: lista de colunas de X (usada para reindexar novas observações)
      - colunas_base: colunas do dataset ANTES do one-hot (usadas para validar nova_obs)
    """
    data = pd.read_csv(csv_path, header=0)

    # Remover o Café da Manhã
    data = data[data["refeicao"] != "cafe da manha"].copy()

    data = data.dropna()
    data = data[data["total"] != 0]

    # Não utilizar variáveis climáticas na previsão
    data = data.drop(columns=COLUNAS_CLIMA, errors="ignore")

    # Descartar observações com valores que aparecem menos de 5 vezes
    data = data.groupby("guarnição").filter(lambda x: len(x) >= 5)
    data = data.groupby("prato_principal_1").filter(lambda x: len(x) >= 5)
    data = data.groupby("prato_principal_2").filter(lambda x: len(x) >= 5)
    data = data.groupby("sobremesa_1").filter(lambda x: len(x) >= 5)

    # Colunas do dataset ANTES do one-hot — usadas para validar nova_obs mais adiante
    colunas_base = data.drop(columns=["total"]).columns

    # Aplicando One Hot Encoding nas variáveis categóricas
    data = pd.get_dummies(data, columns=COLUNAS_ONEHOT)

    atributos = data.drop(columns=["total"]).columns
    X = data[atributos]   # DataFrame (preserva feature names)
    y = data["total"]     # Series

    return X, y, atributos, colunas_base


# ---------------------------------------------------------------------------
# Treino do ensemble com Conformal Prediction
# ---------------------------------------------------------------------------

def treinar_ensemble_conformal(X, y, alpha: float = 0.05, test_size: float = 0.3,
                                random_state: int = 42):

    nivel_confianca = 1 - alpha

    X_train, X_calib, y_train, y_calib = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    print(f"Treino: {len(X_train)} observações | Calibração: {len(X_calib)} observações")

    # 1. Ensemble de calibração
    ensemble_conformal = VotingRegressor(
        estimators=[("gb", GradientBoostingRegressor(n_estimators=200, random_state=random_state)),
                    ("rf", RandomForestRegressor(n_estimators=200, random_state=random_state))],
        weights=[3, 1],
    )
    ensemble_conformal.fit(X_train, y_train)

    y_calib_pred = ensemble_conformal.predict(X_calib)
    residuos_calib = np.abs(y_calib - y_calib_pred)

    # Dias de transição: primeiros ou últimos 10 dias de semestre
    mascara_transicao = (X_calib["dias_desde_ultimas_ferias"] <= 10) | (X_calib["dias_ate_ferias"] <= 10)
    residuos_transicao = residuos_calib[mascara_transicao]
    residuos_normais = residuos_calib[~mascara_transicao]

    margem_transicao = np.quantile(residuos_transicao, nivel_confianca, method="higher")
    margem_normal = np.quantile(residuos_normais, nivel_confianca, method="higher")
    margem_total = np.quantile(residuos_calib, nivel_confianca, method="higher")

    # 2. Ensemble final, treinado em 100% dos dados
    ensemble = VotingRegressor(
        estimators=[("gb", GradientBoostingRegressor(n_estimators=200, random_state=random_state)),
                    ("rf", RandomForestRegressor(n_estimators=200, random_state=random_state))],
        weights=[3, 1],
    )
    ensemble.fit(X, y)

    print("\nCONFORMAL PREDICTION - VALIDAÇÃO:")
    print(f"Margem para Dias de Transição (Início/Fim): ±{margem_transicao:.1f} pessoas "
          f"({len(residuos_transicao)} dias analisados)")
    print(f"Margem para Dias Normais: ±{margem_normal:.1f} pessoas ({len(residuos_normais)} dias analisados)")
    print(f"Margem GERAL (sem distinção): ±{margem_total:.1f} pessoas ({len(residuos_calib)} dias analisados)")
    print(f"Mediana GERAL dos resíduos: {np.median(residuos_calib):.1f} pessoas")
    print(f"Média GERAL dos resíduos: {np.mean(residuos_calib):.1f} pessoas")

    return {
        "ensemble": ensemble,
        "ensemble_conformal": ensemble_conformal,
        "X_calib": X_calib,
        "y_calib": y_calib,
        "y_calib_pred": y_calib_pred,
        "margem_transicao": margem_transicao,
        "margem_normal": margem_normal,
        "margem_total": margem_total,
        "nivel_confianca": nivel_confianca,
        "alpha": alpha,
    }


# ---------------------------------------------------------------------------
# Previsão para uma nova observação
# ---------------------------------------------------------------------------

def validar_nova_obs(nova_obs_dict, colunas_base):
    """
    Confere se as chaves de nova_obs batem com as colunas reais do dataset
    (antes do one-hot encoding).
    """
    colunas_base_set = set(colunas_base)
    chaves = set(nova_obs_dict.keys())

    invalidas = sorted(chaves - colunas_base_set)
    faltando = sorted(colunas_base_set - chaves)

    if invalidas:
        raise ValueError(
            "As seguintes colunas em nova_obs não existem no dataset (confira nomes/typos): "
            f"{invalidas}\n\nColunas válidas disponíveis: {sorted(colunas_base_set)}"
        )

    if faltando:
        print(f"Atenção: colunas do dataset não informadas em nova_obs "
              f"(serão preenchidas com 0 no one-hot): {faltando}")

    return True


def prever_intervalo(nova_obs_dict, resultado_treino, colunas_base, atributos, y):

    validar_nova_obs(nova_obs_dict, colunas_base)

    nova_obs = pd.DataFrame(nova_obs_dict)
    nova_obs_processed = pd.get_dummies(nova_obs).reindex(columns=atributos, fill_value=0)

    ensemble = resultado_treino["ensemble"]
    margem_transicao = resultado_treino["margem_transicao"]
    margem_normal = resultado_treino["margem_normal"]
    nivel_confianca = resultado_treino["nivel_confianca"]

    # Mesmo critério usado em treinar_ensemble_conformal para separar os resíduos
    dias_desde_ultimas_ferias = nova_obs_dict["dias_desde_ultimas_ferias"][0]
    dias_ate_ferias = nova_obs_dict["dias_ate_ferias"][0]
    is_transicao = (dias_desde_ultimas_ferias <= 10) or (dias_ate_ferias <= 10)

    if is_transicao:
        margem_usada = margem_transicao
        tipo_dia = "Transição (início/fim de férias)"
    else:
        margem_usada = margem_normal
        tipo_dia = "Normal"

    pred_central = ensemble.predict(nova_obs_processed)[0]
    limite_inf = max(y.min(), pred_central - margem_usada)
    limite_sup = pred_central + margem_usada

    print(f"\nPrevisão Central: {int(round(pred_central))} pessoas esperadas")
    print(f"\nTipo de dia (para escolha da margem): {tipo_dia}")
    print(f"\nIntervalo de Confiança ({nivel_confianca * 100:.1f}%):")
    print(f"  Limite Inferior: {int(round(limite_inf))} pessoas")
    print(f"  Previsão: {int(round(pred_central))} pessoas")
    print(f"  Limite Superior: {int(round(limite_sup))} pessoas")
    print(f"\n  Amplitude: {int(round(limite_sup - limite_inf))} pessoas")
    print(f"  Margem usada: ±{int(round(margem_usada))} pessoas")
    print("\nGarantias Estatísticas:")
    print(f"  Nível de Confiança: {nivel_confianca * 100:.1f}%")
    print(f"  Calibração: {len(resultado_treino['y_calib'])} observações")

    return {
        "pred_central": pred_central,
        "limite_inf": limite_inf,
        "limite_sup": limite_sup,
        "tipo_dia": tipo_dia,
        "margem_usada": margem_usada,
    }


# ---------------------------------------------------------------------------
# Execução direta do script: treina o modelo e roda uma previsão de exemplo
# ---------------------------------------------------------------------------

def main():
    X, y, atributos, colunas_base = carregar_e_preparar_dados()
    print(f"{len(X)} observações, {len(atributos)} atributos")

    resultado_treino = treinar_ensemble_conformal(X, y, alpha=0.05)

    # Exemplo de nova observação — ajuste os valores conforme a previsão desejada
    nova_obs_dict = {
        "Ano": [2025],
        "Dia_mês": [25],
        "Dia_semana": ["ter"],
        "Mês": [5],
        "prato_principal_1": ["Estrogonofe de carne"],
        "prato_principal_2": ["curry de legumes"],
        "guarnição": ["legumes sauté"],
        "sobremesa_1": ["goiabada"],
        "refeicao": ["jantar"],
        "letivo": [1],
        "vespera_nao_letivo": [0],
        "pos_nao_letivo": [0],
        "dias_desde_ultimas_ferias": [90],
        "dias_ate_ferias": [90],
        "feriado": [0],
        "ferias": [0],
        "vespera_feriado": [0],
        "pos_feriado": [0],
        "dias_desde_inicio_ferias": [0],
        "dias_ate_feriado": [90],
    }

    prever_intervalo(nova_obs_dict, resultado_treino, colunas_base, atributos, y)


if __name__ == "__main__":
    main()
