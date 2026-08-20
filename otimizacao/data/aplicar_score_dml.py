"""
Preenche a coluna P (score de popularidade) de itens_cardapio.xlsx com os
coeficientes estimados pelo Double Machine Learning.

Fluxo:
  1. Le os coeficientes exportados do DML (CSV gerado por exportar_dml.py).
  2. Casa cada item da planilha com seu equivalente no vocabulario historico.
  3. Reescala os coeficientes para a faixa 0.5-1.5 DENTRO de cada categoria.
  4. Grava P (reescalado, usado pelo modelo) e P_bruto (coeficiente original).

Por que reescalar por categoria:
  O coeficiente bruto esta em "alunos a mais/menos" e vai de -455 a +279.
  Como E1 obriga exatamente 1 item de cada categoria por refeicao, uma
  categoria com amplitude maior (prato_principal_1: 734) dominaria o objetivo
  sobre as de amplitude menor (guarnicao: 254), fazendo o solver tratar
  guarnicao como ruido. Reescalar equaliza o peso das categorias e elimina
  os negativos (48% dos coeficientes), mantendo a ORDEM de preferencia.
  P=1.0 vira a media, compativel com o valor neutro usado antes.

Rodar da raiz do repositorio:
    python otimizacao/data/aplicar_score_dml.py [caminho_do_csv]
"""

import re
import sys
import unicodedata

import pandas as pd

PLANILHA = "otimizacao/data/itens_cardapio.xlsx"
CSV_PADRAO = "otimizacao/data/dml_coeficientes.csv"

# Faixa alvo do P reescalado. 1.0 = media (valor neutro usado antes do DML).
P_MIN, P_MAX = 0.5, 1.5

# Categorias que o DML cobre. Sobremesa_2 (frutas) e saladas nao aparecem no
# historico do cardapio, entao ficam com P neutro.
CATEGORIAS_DML = [
    "prato_principal_1",
    "prato_principal_2",
    "guarnição",
    "sobremesa_1",
]

# Itens da planilha cujo equivalente historico tem nome diferente e nao e
# capturado pela normalizacao automatica. Mapeia item da planilha -> nome no
# vocabulario historico (o "item-pai", mais generico).
#
# Ex.: o historico registra apenas "Bife"; a planilha detalha o corte. Ambos
# herdam o mesmo coeficiente, ficando empatados entre si.
MAPA_MANUAL = {
    # prato_principal_1
    "bife (alcatra)": "Bife",
    "bife (coxão mole)": "Bife",
    "iscas de carne (alcatra)": "Isca de carne",
    "iscas de carne (coxão mole)": "Isca de carne",
    "iscas de frango": "Isca de frango",
    "bisteca suína ao molho": "Bisteca",
    "linguiça suína": "Linguiça",
    "pernil ao molho": "Pernil",
    "lombo ao molho": "Lombo",
    "lagarto ao molho": "Lagarto",
    "peixe ao molho": "Filé de peixe",
    "filé de frango ao molho": "Filé de frango",
    "coxa de frango assada": "Filé de coxa",
    "hambúrguer": "Hamburguer",
    # guarnição -- o historico agrupa todas as batatas e virados
    "batata sautê": "Batata",
    "batata corada": "Batata",
    "batata rústica": "Batata",
    "purê de batata": "Purês",
    "purê de mandioquinha": "Purês",
    "virado de cenoura": "Virado",
    "virado de couve": "Virado",
    "virado de abobrinha": "Virado",
    # sobremesa_1
    "romeu e julieta": "Romeu",
    "maria mole": "Pudim de maria mole",
}


def normalizar(texto):
    """Minusculas, sem acento, sem '(...)' e sem sufixo 'ao molho ...'."""
    s = str(texto).strip().lower()
    s = "".join(
        ch for ch in unicodedata.normalize("NFD", s)
        if unicodedata.category(ch) != "Mn"
    )
    s = re.sub(r"\s*\([^)]*\)", "", s)
    s = re.sub(r"\s+(ao|de|com)\s+molho.*$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def reescalar(serie):
    """Mapeia linearmente para [P_MIN, P_MAX]. Serie constante -> 1.0."""
    lo, hi = serie.min(), serie.max()
    if hi == lo:
        return pd.Series(1.0, index=serie.index)
    return P_MIN + (serie - lo) * (P_MAX - P_MIN) / (hi - lo)


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_PADRAO

    coef = pd.read_csv(csv_path)
    df = pd.read_excel(PLANILHA)
    print(f"Coeficientes DML: {len(coef)} | Planilha: {len(df)} itens")

    # Indice (categoria, nome_normalizado) -> coeficiente
    indice = {}
    for _, r in coef.iterrows():
        indice[(r["categoria"], normalizar(r["item_historico"]))] = r["coeficiente"]

    mapa_manual_norm = {normalizar(k): v for k, v in MAPA_MANUAL.items()}

    brutos, origens = [], []
    for _, r in df.iterrows():
        cat, item = r["categoria"], r["item"]
        if cat not in CATEGORIAS_DML:
            brutos.append(None)
            origens.append("fora_do_dml")
            continue

        chave = normalizar(item)
        if (cat, chave) in indice:                       # match direto
            brutos.append(indice[(cat, chave)])
            origens.append("exato")
        elif chave in mapa_manual_norm:                  # herda do item-pai
            pai = normalizar(mapa_manual_norm[chave])
            if (cat, pai) in indice:
                brutos.append(indice[(cat, pai)])
                origens.append("herdado")
            else:
                brutos.append(None)
                origens.append("pai_ausente")
        else:
            brutos.append(None)
            origens.append("sem_dados")

    df["P_bruto"] = brutos
    df["P_origem"] = origens

    # Reescala por categoria e preenche os sem-dados com o neutro 1.0
    df["P"] = 1.0
    for cat in CATEGORIAS_DML:
        m = (df["categoria"] == cat) & df["P_bruto"].notna()
        if m.sum() >= 2:
            df.loc[m, "P"] = reescalar(df.loc[m, "P_bruto"])
    df["P"] = df["P"].round(4)

    # --- Relatorio de cobertura ---
    print("\n=== cobertura por categoria ===")
    for cat in CATEGORIAS_DML:
        sub = df[df["categoria"] == cat]
        com = sub["P_bruto"].notna().sum()
        print(f"  {cat:20s} {com:3d}/{len(sub):3d} com score DML "
              f"({com / len(sub) * 100:3.0f}%)")

    fora = df[~df["categoria"].isin(CATEGORIAS_DML)]
    print(f"  {'(fora do DML)':20s} {len(fora):3d} itens com P neutro = 1.0")

    print("\n=== origem do score ===")
    for k, v in df["P_origem"].value_counts().items():
        print(f"  {k:15s} {v}")

    # --- Validacoes (falham cedo em vez de gerar modelo silenciosamente errado) ---
    if df["P"].isna().any():
        raise SystemExit("ERRO: existem P nulos")
    if (df["P"] <= 0).any():
        raise SystemExit("ERRO: P <= 0 quebraria a funcao objetivo")

    pais_ausentes = df[df["P_origem"] == "pai_ausente"]["item"].tolist()
    if pais_ausentes:
        raise SystemExit(f"ERRO: item-pai do MAPA_MANUAL nao existe no DML: {pais_ausentes}")

    df.to_excel(PLANILHA, index=False)
    print(f"\nSalvo: {PLANILHA}")
    print(f"P varia de {df['P'].min():.4f} a {df['P'].max():.4f}")


if __name__ == "__main__":
    main()
