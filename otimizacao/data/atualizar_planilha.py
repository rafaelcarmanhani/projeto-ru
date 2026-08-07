"""
Atualiza itens_cardapio.xlsx com os atributos necessários para as restrições
O3, OP2, OP3 e O2 do modelo de otimização.

O script é IDEMPOTENTE: pode ser rodado várias vezes sem duplicar nada. Ele
preenche apenas o que falta e nunca sobrescreve valores já existentes de
"produto" (os 28 itens de prato_principal_1 já preenchidos ficam intactos).

Rodar da raiz do repositório:
    python otimizacao/data/atualizar_planilha.py
"""

import pandas as pd

CAMINHO = "otimizacao/data/itens_cardapio.xlsx"

# ----------------------------------------------------------------------
# fritura -> habilita O3 (máx. 4 preparações fritas por mês)
#
# ATENÇÃO: esta lista é julgamento culinário, não dado extraído de fonte.
# Precisa de validação da equipe / do edital. Itens empanados e pré-fritos
# industrializados foram incluídos por serem finalizados em fritura.
# ----------------------------------------------------------------------
ITENS_FRITURA = [
    "peixe frito",       # prato_principal_1
    "frango empanado",   # prato_principal_1
    "ovo frito",         # prato_principal_2
    "batata palha",      # guarnição
    "batata corada",     # guarnição
    "batata rústica",    # guarnição
]

# ----------------------------------------------------------------------
# a_base_de_ovos -> habilita OP2 / OP3 (máx. 2x por semana, por refeição)
#
# Só se aplica a prato_principal_2. A coluna "especificacao" já identifica
# estes itens sem ambiguidade, então o preenchimento é mecânico.
# ----------------------------------------------------------------------
ESPECIFICACOES_OVOS = ["ovo cozido", "omelete", "ovo frito"]

# ----------------------------------------------------------------------
# produto para prato_principal_2 -> habilita O2
#
# O2 exige que "produto" seja um vocabulário COMPARTILHADO entre categorias:
# é o que permite detectar que o pp2 e a guarnição usam o mesmo insumo no
# mesmo dia. Os valores abaixo foram escolhidos para casar com itens que já
# existem nas guarnições (brócolis, abobrinha, cenoura, couve).
#
# Também precisa de validação da equipe.
# ----------------------------------------------------------------------
PRODUTO_PP2 = {
    # soja / PTS
    "pvt": "pts",
    "quibe de pvt": "pts",
    "hambúrguer de pvt": "pts",
    "bife de pvt": "pts",
    "estrogonofe de pvt": "pts",
    "xadrez de pvt": "pts",
    "lasanha de pvt": "pts",
    # ovos
    "ovo cozido": "ovo",
    "omelete": "ovo",
    "ovo frito": "ovo",
    # leguminosas
    "grão de bico à indiana": "grão de bico",
    "bife de grão de bico": "grão de bico",
    "hambúrguer de grão de bico": "grão de bico",
    "estrogonofe de grão de bico": "grão de bico",
    "grãos com queijo": "grão de bico",
    "grãos gratinados": "grão de bico",
    "hambúrguer de lentilha": "lentilha",
    "bife de lentilha": "lentilha",
    "bife de feijão": "feijão",
    "cassoulet": "feijão",
    "baião de dois": "feijão",
    # legumes / vegetais
    "curry de legumes": "legumes variados",
    "estrogonofe de legumes": "legumes variados",
    "suflê de legumes": "legumes variados",
    "tomate recheado": "tomate",
    "lasanha de abobrinha": "abobrinha",
    "lasanha de berinjela": "berinjela",
    "canelone de brócolis": "brócolis",
    "quibe de brócolis": "brócolis",
    "quibe de abóbora": "abóbora",
    "moussaka": "berinjela",
    "batata especial": "batata",
    "batatalhoada": "batata",
    # laticínios / massas
    "canelone de ricota": "ricota",
    "almôndega de ricota": "ricota",
    "lasanha de queijo": "queijo",
    "almôndega de aveia": "aveia",
}

# ----------------------------------------------------------------------
# produto para guarnição -> é o OUTRO LADO da restrição O2
#
# Sem isto, O2 não tem efeito NENHUM: ela só age quando um mesmo valor de
# "produto" aparece tanto no prato_principal_2 quanto em outra categoria, e
# as guarnições estavam todas com produto vazio (só tinham "composicao",
# que é o tipo de vegetal, granularidade grossa demais para O2).
#
# Os valores abaixo casam de propósito com os de PRODUTO_PP2, para que o
# modelo detecte, por exemplo, "canelone de brócolis" (pp2) junto de
# "brócolis" (guarnição) no mesmo dia.
#
# Guarnições sem contraparte no pp2 (farofa, polenta, cuscuz, nhoque,
# macarrão, creme de milho) ficam sem produto de propósito.
# ----------------------------------------------------------------------
PRODUTO_GUARNICAO = {
    "brócolis": "brócolis",
    "abobrinha": "abobrinha",
    "virado de abobrinha": "abobrinha",
    "cenoura": "cenoura",
    "virado de cenoura": "cenoura",
    "couve": "couve",
    "virado de couve": "couve",
    "batata sautê": "batata",
    "batata corada": "batata",
    "batata rústica": "batata",
    "batata palha": "batata",
    "purê de batata": "batata",
    "batata doce": "batata doce",
    "mandioca": "mandioca",
    "purê de mandioquinha": "mandioquinha",
    "chuchu": "chuchu",
    "vagem": "vagem",
    "couve-flor": "couve-flor",
    "acelga": "acelga",
    "repolho": "repolho",
    "legumes": "legumes variados",
    "ervilha parmentier": "ervilha",
}


def main():
    df = pd.read_excel(CAMINHO)
    print(f"Lido: {df.shape[0]} itens, {df.shape[1]} colunas")

    # ---- 2d. Normalizar espaços em branco nas colunas de texto ----
    # Bug encontrado: existia 'massa ' (com espaço no fim) separado de 'massas',
    # tratados como dois valores distintos.
    for col in ["item", "categoria", "especificacao", "produto", "composicao"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda v: v.strip() if isinstance(v, str) else v
            )

    # Unificar 'massa' e 'massas' numa única composição
    df["composicao"] = df["composicao"].replace({"massa": "massas"})
    print("Espaços normalizados; 'massa' unificado com 'massas'")

    # ---- 2a. Coluna fritura ----
    df["fritura"] = df["item"].isin(ITENS_FRITURA).astype(int)

    encontrados = set(df.loc[df["fritura"] == 1, "item"])
    faltando = set(ITENS_FRITURA) - encontrados
    if faltando:
        raise SystemExit(f"ERRO: itens de fritura não encontrados: {faltando}")
    print(f"fritura: {df['fritura'].sum()} itens marcados")

    # ---- 2b. Coluna a_base_de_ovos ----
    df["a_base_de_ovos"] = (
        (df["categoria"] == "prato_principal_2")
        & (df["especificacao"].isin(ESPECIFICACOES_OVOS))
    ).astype(int)
    print(f"a_base_de_ovos: {df['a_base_de_ovos'].sum()} itens marcados")

    # ---- 2c. produto para prato_principal_2 ----
    # Preenche APENAS onde está vazio, para não sobrescrever pp1.
    antes = df["produto"].notna().sum()

    mapa_produto = {**PRODUTO_PP2, **PRODUTO_GUARNICAO}

    mask_vazio = df["produto"].isna()
    df.loc[mask_vazio, "produto"] = df.loc[mask_vazio, "item"].map(mapa_produto)

    depois = df["produto"].notna().sum()
    print(f"produto: {antes} -> {depois} preenchidos")

    # Conferir se as chaves dos mapas existem mesmo na planilha (um typo aqui
    # faria O2 perder um lado silenciosamente).
    itens = set(df["item"])
    typos = [k for k in mapa_produto if k not in itens]
    if typos:
        raise SystemExit(f"ERRO: itens inexistentes no mapa de produto: {typos}")

    # O2 só tem efeito onde um produto aparece no pp2 E em outra categoria.
    pp2 = set(df[df["categoria"] == "prato_principal_2"]["produto"].dropna())
    outros = set(df[df["categoria"] != "prato_principal_2"]["produto"].dropna())
    compartilhados = sorted(pp2 & outros)
    print(f"produtos compartilhados pp2 <-> outras categorias (O2 age): "
          f"{compartilhados}")

    # Conferir se algum pp2 ficou sem produto (quebraria O2 silenciosamente)
    pp2_sem = df[
        (df["categoria"] == "prato_principal_2") & (df["produto"].isna())
    ]["item"].tolist()
    if pp2_sem:
        raise SystemExit(f"ERRO: prato_principal_2 sem produto: {pp2_sem}")

    df.to_excel(CAMINHO, index=False)
    print(f"\nSalvo: {CAMINHO} ({df.shape[1]} colunas)")


if __name__ == "__main__":
    main()
