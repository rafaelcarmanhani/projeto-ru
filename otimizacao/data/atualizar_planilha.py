"""
Atualiza itens_cardapio.xlsx com os atributos necessários para as restrições
O3, OP2, OP3, O2, T07, T08 e (saladas) 3S2/3S3, FF4/FF5 e O1 do modelo de
otimização.

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


# ----------------------------------------------------------------------
# especificacao (reclassificação) -> habilita T07 (Tabela 07: frequência
# mensal da opção do prato principal, item 5.24.14.1.1)
#
# 11 itens de prato_principal_2 estão com especificacao="outro", porque não
# foram classificados nas linhas da Tabela 07 quando a coluna foi criada
# (fase anterior, para O2/OP2/OP3). A Tabela 07 exige a classificação para
# TODOS os itens: suas cotas mensais somam EXATAMENTE aos slots do mês
# (26 almoços em maio/2026), então "outro" sem cota tornaria o modelo
# infactível se T07 virar restrição de igualdade.
#
# Dois itens (almôndega de ricota, almôndega de aveia) não se encaixam em
# nenhuma linha da Tabela 07 — não são PVT, ovo, legume nem massa com
# queijo — e permanecem como "outro", SEM cota mensal (T07 não os limita).
# ----------------------------------------------------------------------
RECLASSIFICACAO_ESPECIFICACAO_PP2 = {
    "lasanha de abobrinha": "massa com queijo",
    "lasanha de berinjela": "massa com queijo",
    "canelone de brócolis": "massa com queijo",
    "moussaka": "legume gratinado",
    "batata especial": "legume",
    "batatalhoada": "legume gratinado",
    "suflê de legumes": "legume gratinado",
    "quibe de brócolis": "legume",
    "quibe de abóbora": "legume",
}

# ----------------------------------------------------------------------
# Tabela 07 do edital (5.24.14.1.1) -> frequência mensal MÁXIMA da opção
# do prato principal, por (almoço, jantar), considerando 26 dias úteis.
#
# Feijoada Vegetariana (2x/ano) fica de fora: não é mensal e o item ainda
# não existe na planilha.
# ----------------------------------------------------------------------
COTA_MENSAL_ESPECIFICACAO = {
    "pts moída": (8, 5),
    "pts em cubos": (4, 3),
    "ovo cozido": (1, 1),
    "omelete": (1, 1),
    "ovo frito": (2, 2),
    "legume gratinado": (3, 3),
    "legume com queijo": (1, 1),
    "legume": (2, 2),
    "leguminosa": (2, 2),
    "massa com queijo": (1, 1),
    "massa com pts": (1, 1),
}

# ----------------------------------------------------------------------
# Guarnição faltante para a Tabela 08 (5.25.5): a planilha não tinha
# nenhuma guarnição "à base de farinha de trigo" (torta com legumes,
# suflê). Sem ela, a soma das cotas da Tabela 08 (24 almoços) fica abaixo
# dos 26 slots do mês, e o modelo fica infactível.
# ----------------------------------------------------------------------
GUARNICAO_FARINHA_TRIGO = "suflê de guarnição"

# ----------------------------------------------------------------------
# Tabela 08 do edital (5.25.5) -> frequência mensal MÁXIMA da composição
# da guarnição, por (almoço, jantar), considerando 26 dias úteis.
# ----------------------------------------------------------------------
COTA_MENSAL_COMPOSICAO = {
    "farinha de mandioca": (2, 2),
    "vegetal C": (4, 4),
    "vegetal A folhoso": (2, 2),
    "vegetal não folhoso": (7, 6),
    "creme espessado": (3, 2),
    "massas": (4, 3),
    "farinha de milho e fubá": (2, 2),
    "farinha de trigo": (2, 1),
}

# ----------------------------------------------------------------------
# preparo -> habilita PEN1 (penalização de proximidade entre pratos do
# mesmo MODO DE PREPARO), no modelo de otimização.
#
# MOTIVO: a planilha descreve INGREDIENTE ("produto") e TIPO DE CARNE
# ("especificacao"), mas nada sobre COMO o prato é feito. Para o modelo,
# "estrogonofe de carne" e "estrogonofe de frango" são maximamente
# diferentes (espécies e cortes distintos), e passam por PP2T/PP6 sem
# problema — mas para quem come são o mesmo prato. O resultado eram
# estrogonofes no almoço e no jantar do mesmo dia, ou lasanha de pp1 e
# lasanha de pp2 na MESMA refeição.
#
# ATENÇÃO: esta classificação é julgamento culinário, não dado extraído de
# fonte — mesma natureza da lista ITENS_FRITURA. PRECISA DE VALIDAÇÃO DA
# NUTRICIONISTA / DA EQUIPE.
#
# DECISÕES TOMADAS (a revisar):
#
#   - "ao molho" NÃO é preparo. Por decisão do grupo, o molho é só um
#     detalhe do prato e não caracteriza semelhança: "lagarto ao molho" e
#     "lombo ao molho" são pratos diferentes. Se fosse considerado,
#     agruparia 7 itens de pp1 e travaria o modelo sem necessidade.
#
#   - Itens sem família clara ficam FORA (não aparecem no dicionário):
#     "pvt", "legumes", "farofa", "polenta", "cuscuz", "macarrão",
#     "nhoque", "creme de milho", as guarnições de vegetal puro e as de
#     batata sem preparo próprio. Sem preparo, ficam sem penalização —
#     mesmo padrão dos itens sem cota na Tabela 07.
#
#   - "bife" agrupa os bifes de carne e os bifes vegetarianos (bife de
#     pvt, de grão de bico, de lentilha, de feijão): o formato do prato é
#     o mesmo, que é o que o comensal percebe.
#
#   - "assado" ficou só com "coxa de frango assada": é o único item cujo
#     nome declara o preparo. Vários outros provavelmente são assados na
#     prática — CONFIRMAR com a nutricionista se vale classificá-los.
# ----------------------------------------------------------------------
PREPARO = {
    # ---- prato_principal_1 ----
    "bife (alcatra)": "bife",
    "bife (coxão mole)": "bife",
    "carne de panela": "cozido",
    "carne em cubos": "cubos",
    "carne louca": "desfiado",
    "carne moída": "moída",
    "coxa de frango assada": "assado",
    "estrogonofe de carne": "estrogonofe",
    "estrogonofe de frango": "estrogonofe",
    "frango cremoso": "cremoso",
    "frango empanado": "empanado",
    "frango xadrez": "xadrez",
    "fricassê de frango": "gratinado",
    "hambúrguer": "hambúrguer",
    "iscas de carne (alcatra)": "iscas",
    "iscas de carne (coxão mole)": "iscas",
    "iscas de frango": "iscas",
    "lasanha bolonhesa": "lasanha",
    "panqueca de carne": "panqueca",
    "peixe frito": "frito",
    "quibe": "quibe",

    # ---- prato_principal_2 ----
    "almôndega de aveia": "almôndega",
    "almôndega de ricota": "almôndega",
    "baião de dois": "cozido",
    "batatalhoada": "gratinado",
    "bife de feijão": "bife",
    "bife de grão de bico": "bife",
    "bife de lentilha": "bife",
    "bife de pvt": "bife",
    "canelone de brócolis": "canelone",
    "canelone de ricota": "canelone",
    "cassoulet": "cozido",
    "curry de legumes": "curry",
    "estrogonofe de grão de bico": "estrogonofe",
    "estrogonofe de legumes": "estrogonofe",
    "estrogonofe de pvt": "estrogonofe",
    "grão de bico à indiana": "curry",
    "grãos com queijo": "gratinado",
    "grãos gratinados": "gratinado",
    "hambúrguer de grão de bico": "hambúrguer",
    "hambúrguer de lentilha": "hambúrguer",
    "hambúrguer de pvt": "hambúrguer",
    "lasanha de abobrinha": "lasanha",
    "lasanha de berinjela": "lasanha",
    "lasanha de pvt": "lasanha",
    "lasanha de queijo": "lasanha",
    "moussaka": "gratinado",
    "omelete": "omelete",
    "ovo frito": "frito",
    "quibe de abóbora": "quibe",
    "quibe de brócolis": "quibe",
    "quibe de pvt": "quibe",
    "suflê de legumes": "suflê",
    "tomate recheado": "recheado",
    "xadrez de pvt": "xadrez",

    # ---- guarnição ----
    "batata corada": "frito",
    "batata palha": "frito",
    "batata rústica": "frito",
    "purê de batata": "purê",
    "purê de mandioquinha": "purê",
    "suflê de guarnição": "suflê",
    "virado de abobrinha": "virado",
    "virado de cenoura": "virado",
    "virado de couve": "virado",
}

# ----------------------------------------------------------------------
# ITENS DE SALADA (edital 5.21 e Anexos VII/VIII)
#
# Tipo I  = salada_1: folhosos (5.21.2)
# Tipo II = salada_2: cozida, vegetal A/B/C, massa, maionese (5.21.3)
# Tipo III= salada_3: grãos (5.21.4)
#
# ATENÇÃO aos nomes: vários vegetais já existem na planilha como GUARNIÇÃO
# (acelga, brócolis, couve-flor, abobrinha). Como os dicionários de atributos
# são construídos com dict(zip(item, ...)), nomes iguais se sobrescreveriam
# silenciosamente. Por isso as saladas levam sufixo ("acelga crua", "brócolis
# na salada", ...). A ligação com a guarnição para a restrição O1 é feita pela
# coluna "vegetal", não pelo nome.
# ----------------------------------------------------------------------

# Tipo I - folhosos. Anexo VII lista: alface (crespa/americana/roxa), almeirão
# Pão de Açúcar, chicória (escarola), rúcula, acelga, couve manteiga,
# repolho liso e roxo, agrião.
SALADA_1 = {
    "alface": None,                 # regra própria 1S2/1S3
    "chicória": None,               # regra própria FF1/FF2
    "almeirão": None,               # regra própria FF3/FF3b
    "rúcula": None,
    "agrião": None,
    "escarola": None,
    "acelga crua": "acelga",
    "repolho roxo": "repolho",
    "couve crua": "couve",
}

# Tipo II - cozidas / com maionese / com massa. Exemplos do próprio 5.21.3
# ("macarronese, maionese de legumes, brócolis, couve-flor, abobrinha,
# berinjela, abóbora, quiabo") e do Anexo VIII (saladas elaboradas).
SALADA_2 = {
    "macarronese": None,
    "maionese de legumes": "legumes variados",
    "brócolis na salada": "brócolis",
    "couve-flor na salada": "couve-flor",
    "abobrinha na salada": "abobrinha",
    "berinjela na salada": "berinjela",
    "abóbora cabotiá": "abóbora",
    "quiabo na salada": None,
    "beterraba cozida": "beterraba",
    "cenoura ralada": "cenoura",
    "salpicão de legumes": "legumes variados",
    "vagem na salada": "vagem",
}

# Tipo III - grãos (5.21.4): "feijão tipo soja, feijão tipo branco, feijão
# tipo fradinho, lentilha, milho, ervilha seca, ervilha em conserva, grão de
# bico". Mais tabule e mista de trigo do Anexo VIII.
SALADA_3 = {
    "salada de feijão branco": None,
    "salada de feijão fradinho": None,
    "salada de soja": None,
    "salada de lentilha": None,
    "salada de ervilha seca": None,
    "salada de grão de bico": None,
    "tabule": None,
    "mista de trigo": None,
    "salada de milho": None,          # em conserva
    "salada de ervilha em conserva": None,   # em conserva
}

# ----------------------------------------------------------------------
# grao_em_conserva -> habilita 3S2 / 3S3 (grão em conserva até 2x por semana,
# no almoço e no jantar separadamente), conforme 5.21.4.
# ----------------------------------------------------------------------
ITENS_GRAO_CONSERVA = [
    "salada de milho",
    "salada de ervilha em conserva",
]

# ----------------------------------------------------------------------
# creme_maionese -> habilita FF4 / FF5 (5.21.3.3: "A frequência mensal de
# salada com creme de maionese será de 2 vezes no jantar e 2 vezes no
# almoço"). São as saladas Tipo II que levam creme de maionese.
# ----------------------------------------------------------------------
ITENS_CREME_MAIONESE = [
    "maionese de legumes",
    "salpicão de legumes",
]

# ----------------------------------------------------------------------
# vegetal -> habilita O1 (o vegetal da salada não repete na guarnição do
# mesmo dia).
#
# É um vocabulário COMPARTILHADO entre salada_* e guarnição, na mesma lógica
# que "produto" é compartilhado entre prato_principal_2 e guarnição para O2.
# Sem interseção entre os dois lados, O1 não tem efeito nenhum.
#
# DELIBERADAMENTE SEPARADO DE "produto": reusar "produto" acoplaria as saladas
# à restrição O2 como efeito colateral (ex.: "grão de bico" salada_3 passaria a
# conflitar com os pp2 de grão de bico). Essa é uma decisão em aberto para o
# orientador — ver bloco de comentários de otimizacao.py.
#
# As guarnições já têm "produto" preenchido com nomes de vegetais, então o
# lado da guarnição parte desses mesmos valores.
# ----------------------------------------------------------------------
VEGETAL_GUARNICAO = {
    "brócolis": "brócolis",
    "abobrinha": "abobrinha",
    "virado de abobrinha": "abobrinha",
    "cenoura": "cenoura",
    "virado de cenoura": "cenoura",
    "couve": "couve",
    "virado de couve": "couve",
    "chuchu": "chuchu",
    "vagem": "vagem",
    "couve-flor": "couve-flor",
    "acelga": "acelga",
    "repolho": "repolho",
}

# Vegetal das saladas: vem dos próprios dicionários SALADA_1/2/3 acima, onde
# o valor de cada item é o vegetal (ou None quando não há contraparte possível
# na guarnição, como nas saladas de grão).
VEGETAL_SALADA = {
    item: veg
    for grupo in (SALADA_1, SALADA_2, SALADA_3)
    for item, veg in grupo.items()
    if veg is not None
}


def cadastrar_saladas(df):
    """Substitui as saladas da planilha pelos itens do edital.

    Idempotente: remove todas as linhas de salada_1/2/3 e reinsere a partir
    dos dicionários acima, então rodar duas vezes dá o mesmo resultado.
    """
    antes = (df["categoria"].isin(["salada_1", "salada_2", "salada_3"])).sum()
    df = df[~df["categoria"].isin(["salada_1", "salada_2", "salada_3"])]

    novas = []
    for categoria, grupo in [
        ("salada_1", SALADA_1),
        ("salada_2", SALADA_2),
        ("salada_3", SALADA_3),
    ]:
        for item in grupo:
            novas.append({
                "item": item,
                "categoria": categoria,
                # P neutro: as saladas existem para satisfazer as restrições
                # do edital, não para orientar a escolha. O peso efetivo é
                # zerado em CATEGORIAS_SEM_SCORE (otimizacao.py).
                "P": 1,
                "embutido": 0,
                "fritura": 0,
                "a_base_de_ovos": 0,
            })

    df = pd.concat([df, pd.DataFrame(novas)], ignore_index=True)
    print(f"saladas: {antes} placeholder(s) -> {len(novas)} itens do edital "
          f"({len(SALADA_1)} + {len(SALADA_2)} + {len(SALADA_3)})")

    # Nomes duplicados colapsariam silenciosamente em dict(zip(...)).
    dups = df["item"][df["item"].duplicated()].tolist()
    if dups:
        raise SystemExit(f"ERRO: itens com nome duplicado na planilha: {dups}")

    return df


def cadastrar_guarnicao_farinha_trigo(df):
    """Acrescenta a guarnição "à base de farinha de trigo" que faltava
    para a Tabela 08 (5.25.5) ter itens suficientes. Idempotente.
    """
    if (df["item"] == GUARNICAO_FARINHA_TRIGO).any():
        return df

    nova = pd.DataFrame([{
        "item": GUARNICAO_FARINHA_TRIGO,
        "categoria": "guarnição",
        "P": 1,
        "embutido": 0,
        "fritura": 0,
        "a_base_de_ovos": 0,
        "composicao": "farinha de trigo",
    }])
    print(f"guarnição: acrescentado '{GUARNICAO_FARINHA_TRIGO}' "
          f"(Tabela 08 não tinha item de farinha de trigo)")
    return pd.concat([df, nova], ignore_index=True)


def main():
    df = pd.read_excel(CAMINHO)
    print(f"Lido: {df.shape[0]} itens, {df.shape[1]} colunas")

    # ---- 1. Cadastrar as saladas do edital ----
    df = cadastrar_saladas(df)

    # ---- 1b. Acrescentar guarnição de farinha de trigo (Tabela 08) ----
    df = cadastrar_guarnicao_farinha_trigo(df)

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

    # ---- 2h. Reclassificar especificacao de pp2 para a Tabela 07 (T07) ----
    # Os 11 itens "outro" precisam cair numa linha da tabela, senão T07 (que
    # é uma restrição de IGUALDADE — ver otimizacao.py) fica infactível.
    mask_reclass = df["item"].isin(RECLASSIFICACAO_ESPECIFICACAO_PP2)
    df.loc[mask_reclass, "especificacao"] = df.loc[mask_reclass, "item"].map(
        RECLASSIFICACAO_ESPECIFICACAO_PP2
    )
    typos = [k for k in RECLASSIFICACAO_ESPECIFICACAO_PP2 if k not in set(df["item"])]
    if typos:
        raise SystemExit(f"ERRO: itens inexistentes em RECLASSIFICACAO_ESPECIFICACAO_PP2: {typos}")
    print(f"especificacao: {mask_reclass.sum()} itens de pp2 reclassificados para a Tabela 07")

    ainda_outro = df[(df["categoria"] == "prato_principal_2") & (df["especificacao"] == "outro")]
    if len(ainda_outro):
        print(f"  AVISO: {len(ainda_outro)} itens de pp2 seguem como 'outro' "
              f"(sem cota T07, item não se encaixa na Tabela 07): "
              f"{sorted(ainda_outro['item'])}")

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

    # ---- 2e. Coluna grao_em_conserva (3S2 / 3S3) ----
    df["grao_em_conserva"] = df["item"].isin(ITENS_GRAO_CONSERVA).astype(int)
    print(f"grao_em_conserva: {df['grao_em_conserva'].sum()} itens marcados")

    # ---- 2f. Coluna creme_maionese (FF4 / FF5) ----
    df["creme_maionese"] = df["item"].isin(ITENS_CREME_MAIONESE).astype(int)
    print(f"creme_maionese: {df['creme_maionese'].sum()} itens marcados")

    # ---- 2g. Coluna vegetal (O1) ----
    mapa_vegetal = {**VEGETAL_GUARNICAO, **VEGETAL_SALADA}
    df["vegetal"] = df["item"].map(mapa_vegetal)
    print(f"vegetal: {df['vegetal'].notna().sum()} itens preenchidos")

    # Mesmas checagens de typo que já são feitas para "produto": uma chave
    # inexistente aqui faria O1 perder um lado silenciosamente.
    for nome, lista in [
        ("grao_em_conserva", ITENS_GRAO_CONSERVA),
        ("creme_maionese", ITENS_CREME_MAIONESE),
        ("vegetal", list(mapa_vegetal)),
        ("preparo", list(PREPARO)),
    ]:
        typos = [k for k in lista if k not in itens]
        if typos:
            raise SystemExit(f"ERRO: itens inexistentes em {nome}: {typos}")

    # ---- 2i. Coluna preparo (PEN1 - penalização de proximidade) ----
    df["preparo"] = df["item"].map(PREPARO)
    n_prep = df["preparo"].notna().sum()
    print(f"preparo: {n_prep} itens classificados")

    # A penalização só age em preparos com 2+ itens: com 1 item só, a
    # não-repetição em 7 dias (PP1/OP1/G1) já resolve, e a penalização
    # seria inócua.
    contagem = df["preparo"].value_counts()
    ativos = contagem[contagem >= 2]
    print(f"  preparos com 2+ itens (PEN1 age): {dict(ativos)}")
    inocuos = sorted(contagem[contagem < 2].index)
    if inocuos:
        print(f"  preparos com 1 item só (sem efeito prático): {inocuos}")

    # Itens de pp1/pp2/guarnição que ficaram sem preparo: é esperado para
    # os que não têm família clara (pvt, legumes, farofa...), mas convém
    # revisar a lista, porque um item sem preparo não é penalizado nunca.
    cat_penalizadas = ["prato_principal_1", "prato_principal_2", "guarnição"]
    sem_preparo = sorted(
        df[df["categoria"].isin(cat_penalizadas) & df["preparo"].isna()]["item"]
    )
    print(f"  {len(sem_preparo)} itens sem preparo (fora da PEN1): {sem_preparo}")

    # O1 só age onde um vegetal aparece numa salada E numa guarnição.
    cat_salada = df["categoria"].str.startswith("salada_", na=False)
    veg_salada = set(df[cat_salada]["vegetal"].dropna())
    veg_guarnicao = set(
        df[df["categoria"] == "guarnição"]["vegetal"].dropna()
    )
    veg_comuns = sorted(veg_salada & veg_guarnicao)
    print(f"vegetais compartilhados salada <-> guarnição (O1 age): {veg_comuns}")
    if not veg_comuns:
        print("  AVISO: sem interseção, O1 não terá efeito. Esperado enquanto "
              "as saladas do edital não forem cadastradas (Fase 2).")

    # ---- 3. Conferir factibilidade das Tabelas 07 e 08 ----
    # T07/T08 são restrições de IGUALDADE por refeição (ver otimizacao.py):
    # a soma das cotas mensais precisa cobrir EXATAMENTE os slots do mês.
    # Falha aqui em vez de deixar o Gurobi dar INFEASIBLE sem explicação.
    import calendar
    from datetime import date
    ANO_TESTE, MES_TESTE = 2026, 5
    dias = calendar.monthrange(ANO_TESTE, MES_TESTE)[1]
    almocos = sum(1 for d in range(1, dias + 1) if date(ANO_TESTE, MES_TESTE, d).weekday() != 6)
    jantas = sum(1 for d in range(1, dias + 1) if date(ANO_TESTE, MES_TESTE, d).weekday() not in (5, 6))

    for nome, coluna, cotas, categoria in [
        ("T07 (Tabela 07)", "especificacao", COTA_MENSAL_ESPECIFICACAO, "prato_principal_2"),
        ("T08 (Tabela 08)", "composicao", COTA_MENSAL_COMPOSICAO, "guarnição"),
    ]:
        sub = df[df["categoria"] == categoria]
        sa = sum(a for a, _ in cotas.values())
        sj = sum(j for _, j in cotas.values())
        print(f"{nome}: soma das cotas almoço={sa} (slots={almocos}), "
              f"jantar={sj} (slots={jantas})")
        if sa < almocos or sj < jantas:
            raise SystemExit(
                f"ERRO: {nome} tem cota insuficiente para cobrir o mês de "
                f"referência ({MES_TESTE}/{ANO_TESTE}): "
                f"almoço {sa} < {almocos} ou jantar {sj} < {jantas}. "
                f"Cadastrar mais itens ou revisar as cotas."
            )
        sem_cota = sub[~sub[coluna].isin(cotas)]
        if len(sem_cota):
            print(f"  {len(sem_cota)} itens de {categoria} sem cota em {nome} "
                  f"(ficam de fora da restrição): {sorted(sem_cota['item'])}")

    df.to_excel(CAMINHO, index=False)
    print(f"\nSalvo: {CAMINHO} ({df.shape[1]} colunas)")


if __name__ == "__main__":
    main()
