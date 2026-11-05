# ------------------------ IMPORTAR BIBLIOTECAS ------------------------

import gurobipy as gp
from gurobipy import GRB, quicksum
import pandas as pd
import calendar
from datetime import date

from relatorio import gerar_relatorio

# ------------------------ CONFIGURAÇÕES INICIAIS ------------------------

# Ler csv
df = pd.read_excel("otimizacao/data/itens_cardapio.xlsx")

# Configurações
ano = 2026
mes = 5

# Dias do mês atual
D = [d for d in range(1, calendar.monthrange(ano, mes)[1] + 1)]

# ------------------------ HISTÓRICO ------------------------

historico = {

    # ---------------- DIA -1 ----------------

    ("banana", "Desjejum", -1): 1,

    ("rúcula", "Almoco", -1): 1,
    ("macarronese", "Almoco", -1): 1,
    ("tabule", "Almoco", -1): 1,
    ("pernil ao molho", "Almoco", -1): 1,
    ("quibe de pvt", "Almoco", -1): 1,
    ("macarrão", "Almoco", -1): 1,
    ("delicia de abacaxi", "Almoco", -1): 1,
    ("mamão", "Almoco", -1): 1,

    ("agrião", "Janta", -1): 1,
    ("beterraba cozida", "Janta", -1): 1,
    ("salada de lentilha", "Janta", -1): 1,
    ("filé de frango ao molho", "Janta", -1): 1,
    ("hambúrguer de lentilha", "Janta", -1): 1,
    ("couve", "Janta", -1): 1,
    ("banoffe", "Janta", -1): 1,
    ("laranja", "Janta", -1): 1,

    # ---------------- DIA -2 ----------------

    ("maçã", "Desjejum", -2): 1,

    ("escarola", "Almoco", -2): 1,
    ("cenoura ralada", "Almoco", -2): 1,
    ("salada de feijão branco", "Almoco", -2): 1,
    ("panqueca de carne", "Almoco", -2): 1,
    ("lasanha de queijo", "Almoco", -2): 1,
    ("purê de batata", "Almoco", -2): 1,
    ("flan de morango", "Almoco", -2): 1,
    ("melão", "Almoco", -2): 1,

    ("acelga crua", "Janta", -2): 1,
    ("brócolis na salada", "Janta", -2): 1,
    ("mista de trigo", "Janta", -2): 1,
    ("coxa de frango assada", "Janta", -2): 1,
    ("lasanha de abobrinha", "Janta", -2): 1,
    ("purê de mandioquinha", "Janta", -2): 1,
    ("delicia de banana", "Janta", -2): 1,
    ("banana", "Janta", -2): 1,

    # ---------------- DIA -3 ----------------

    ("mamão", "Desjejum", -3): 1,

    ("repolho roxo", "Almoco", -3): 1,
    ("couve-flor na salada", "Almoco", -3): 1,
    ("salada de milho", "Almoco", -3): 1,
    ("quibe", "Almoco", -3): 1,
    ("almôndega de aveia", "Almoco", -3): 1,
    ("mandioca", "Almoco", -3): 1,
    ("pudim crocante", "Almoco", -3): 1,
    ("caqui", "Almoco", -3): 1,

    ("couve crua", "Janta", -3): 1,
    ("abobrinha na salada", "Janta", -3): 1,
    ("salada de soja", "Janta", -3): 1,
    ("iscas de frango", "Janta", -3): 1,
    ("curry de legumes", "Janta", -3): 1,
    ("ervilha parmentier", "Janta", -3): 1,
    ("pavê de bombom", "Janta", -3): 1,
    ("melão", "Janta", -3): 1,

    # ---------------- DIA -4 ----------------

    ("melancia", "Desjejum", -4): 1,

    ("alface", "Almoco", -4): 1,
    ("berinjela na salada", "Almoco", -4): 1,
    ("salada de grão de bico", "Almoco", -4): 1,
    ("estrogonofe de carne", "Almoco", -4): 1,
    ("bife de grão de bico", "Almoco", -4): 1,
    ("virado de couve", "Almoco", -4): 1,
    ("alfajor", "Almoco", -4): 1,
    ("goiaba", "Almoco", -4): 1,

    ("chicória", "Janta", -4): 1,
    ("abóbora cabotiá", "Janta", -4): 1,
    ("salada de ervilha seca", "Janta", -4): 1,
    ("frango empanado", "Janta", -4): 1,
    ("omelete", "Janta", -4): 1,
    ("acelga", "Janta", -4): 1,
    ("rocambole de chocolate", "Janta", -4): 1,
    ("tangerina", "Janta", -4): 1,

    # ---------------- DIA -6 ----------------

    ("goiaba", "Desjejum", -6): 1,

    ("almeirão", "Almoco", -6): 1,
    ("quiabo na salada", "Almoco", -6): 1,
    ("salada de feijão fradinho", "Almoco", -6): 1,
    ("carne moída", "Almoco", -6): 1,
    ("hambúrguer de pvt", "Almoco", -6): 1,
    ("batata doce", "Almoco", -6): 1,
    ("doce de goiabada", "Almoco", -6): 1,
    ("abacaxi", "Almoco", -6): 1,

    # ---------------- DIA 7 ----------------

    ("caqui", "Desjejum", -7): 1,

    ("alface", "Almoco", -7): 1,
    ("vagem na salada", "Almoco", -7): 1,
    ("salada de ervilha em conserva", "Almoco", -7): 1,
    ("peixe ao molho", "Almoco", -7): 1,
    ("estrogonofe de pvt", "Almoco", -7): 1,
    ("cenoura", "Almoco", -7): 1,
    ("mousse de chocolate", "Almoco", -7): 1,
    ("melancia", "Almoco", -7): 1,

    ("rúcula", "Janta", -7): 1,
    ("salpicão de legumes", "Janta", -7): 1,
    ("tabule", "Janta", -7): 1,
    ("linguiça suína", "Janta", -7): 1,
    ("grão de bico à indiana", "Janta", -7): 1,
    ("batata sautê", "Janta", -7): 1,
    ("pudim de baunilha", "Janta", -7): 1,
    ("abacaxi", "Janta", -7): 1,
}

# ------------------------ FUNÇÕES AUXILIARES ------------------------

# Dia da semana
def s(d):
    if d < 1:
        return None
    return date(ano, mes, d).weekday()


# Refeições do dia
def R_ds(d):
    # Dias históricos: assume as 3 refeições. Não há problema porque o
    # histórico é lido com .get(..., 0), então dias que não existiram
    # simplesmente contribuem 0 nas janelas.
    if d < 1:
        return ["Desjejum", "Almoco", "Janta"]
    ds = s(d)
    if ds == 5:  # sábado
        return ["Desjejum", "Almoco"]
    elif ds == 6:  # domingo
        return []
    else:
        return ["Desjejum", "Almoco", "Janta"]


# Janela móvel de 7 dias (retroativa: inclui dias históricos quando d <= 6)
def janela7(d):
    return range(d - 6, d + 1)


# ------------------------ SEMANAS DE CALENDÁRIO (W, Dw) ------------------------

# Dw agrupa os dias do horizonte por semana de calendário (segunda a domingo),
# conforme a OBS do relatório na subseção 4.1.7. É diferente da janela
# deslizante janela7(): as restrições de frequência fixa (FF1..FF5) exigem
# igualdade ("exatamente 1x por semana"), o que é infactível numa janela
# deslizante, e por isso precisam de Dw.

Dw = {}
for d in D:
    # isocalendar() = (ano ISO, semana ISO, dia da semana). A semana ISO começa
    # na segunda, que é exatamente a definição de semana usada pelo edital.
    ano_iso, semana_iso, _ = date(ano, mes, d).isocalendar()
    Dw.setdefault((ano_iso, semana_iso), []).append(d)

W = sorted(Dw.keys())

# Semanas completas: as que têm todos os 7 dias dentro do horizonte de
# planejamento. As semanas das bordas do mês ficam truncadas (ex.: maio/2026
# começa numa sexta, então a primeira "semana" tem apenas sex/sáb/dom).
# Aplicar uma restrição de igualdade (FF1..FF5) numa semana truncada torna o
# modelo infactível, porque não há dias úteis suficientes para acomodá-la.
W_completas = [w for w in W if len(Dw[w]) == 7]

# Dias úteis (com almoço / com janta) por semana, úteis para as FF.
def dias_com_refeicao(w, r):
    return [d for d in Dw[w] if r in R_ds(d)]


print(f"Semanas no horizonte: {len(W)} | completas: {len(W_completas)}")
for w in W:
    marca = "completa" if w in W_completas else "PARCIAL"
    print(f"  semana {w[1]}: dias {Dw[w]} ({marca})")

# ------------------------ ORGANIZAR SUBCONJUNTOS ------------------------

P = dict(zip(df["item"], df["P"]))
Categoria = dict(zip(df["item"], df["categoria"]))
TipoCarne = dict(zip(df["item"], df["tipo_carne"]))
Embutido = dict(zip(df["item"], df["embutido"]))
Especificacao = dict(zip(df["item"], df["especificacao"]))
Fritura = dict(zip(df["item"], df["fritura"]))
ABaseDeOvos = dict(zip(df["item"], df["a_base_de_ovos"]))
Produto = dict(zip(df["item"], df["produto"]))
GraoEmConserva = dict(zip(df["item"], df["grao_em_conserva"]))
CremeMaionese = dict(zip(df["item"], df["creme_maionese"]))
Vegetal = dict(zip(df["item"], df["vegetal"]))
Composicao = dict(zip(df["item"], df["composicao"]))

# Categorias de salada, usadas em vários pontos abaixo.
CATEGORIAS_SALADA = ["salada_1", "salada_2", "salada_3"]

# Saladas ATIVAS: a planilha foi populada com os itens do edital (item 5.21 e
# Anexos VII/VIII) via atualizar_planilha.py, então salada_1/2/3 entram
# normalmente no modelo.
#
# Esta lista existe para poder tirar categorias inteiras de escopo. Deixá-la
# vazia é o estado normal; basta acrescentar uma categoria aqui para removê-la
# de I, C e de todos os conjuntos derivados.
CATEGORIAS_IGNORADAS = []

# As saladas entram no modelo apenas para satisfazer as restrições do edital,
# nunca para orientar a escolha. Não existe fonte de score de preferência para
# elas: o DML só cobre pp1, pp2, guarnição e sobremesa_1 (ver BLOCO 3), então
# qualquer P > 0 aqui seria preferência inventada. Com peso neutro, todas as
# saladas factíveis são equivalentes para o otimizador.
#
# A neutralidade fica no código, e não na coluna P da planilha, porque P é dado
# de entrada: os scores do DML já foram aplicados à planilha (BLOCO 3) e serão
# sobrescritos de novo a cada nova rodada do modelo de popularidade.
CATEGORIAS_SEM_SCORE = ["salada_1", "salada_2", "salada_3"]

# Conjuntos
I = [i for i in df["item"] if Categoria[i] not in CATEGORIAS_IGNORADAS]

C = [
    c for c in sorted(df["categoria"].unique())
    if c not in CATEGORIAS_IGNORADAS
]

E = sorted(df["especificacao"].dropna().unique())

# Subconjuntos Ic
Ic = {c: [] for c in C}
for i in I:
    Ic[Categoria[i]].append(i)

# Subconjuntos Ie
Ie = {e: [] for e in E}
for i in I:
    e = Especificacao[i]
    if pd.notna(e):
        Ie[e].append(i)

# Subconjuntos especiais
IBranca   = [i for i in I if TipoCarne[i] == "branca"]
IVermelha = [i for i in I if TipoCarne[i] == "vermelha"]
IEmbutido = [i for i in I if Embutido[i] == 1]

# ISoja: itens à base de soja (PTS / PVT).
# A planilha ainda não tem a coluna "a_base_de_soja" prevista no relatório
# (subseção 4.1.6), mas a especificação já identifica a soja sem ambiguidade,
# então ISoja é derivado dela. Quando a coluna existir, trocar por
# [i for i in I if ABaseDeSoja[i] == 1].
ESPECIFICACOES_SOJA = ["pts moída", "pts em cubos", "massa com pts"]

ISoja = [
    i for i in I
    if pd.notna(Especificacao[i]) and Especificacao[i] in ESPECIFICACOES_SOJA
]

# IFritura: itens preparados por fritura (restrição O3).
IFritura = [i for i in I if Fritura[i] == 1]

# IOvos: opções de prato principal 2 à base de ovos (restrições OP2 e OP3).
IOvos = [i for i in I if ABaseDeOvos[i] == 1]

# Tabela 06 do edital (5.23.19): frequência mensal CONTRATADA de cada CORTE
# de carne do prato principal (pp1), por (almoço, jantar), para 26 dias úteis
# (restrição T06).
#
# A chave é a coluna "produto" da planilha, que já registra o corte
# (miolo de alcatra, patinho, lagarto...) — não foi preciso criar coluna
# nova. Os 14 produtos de pp1 batem 1-para-1 com as 14 linhas da Tabela 06.
#
# "Pertences para feijoada" (2x/ano) fica de fora: não é frequência mensal e
# a feijoada não existe como item de pp1 na planilha.
COTA_MENSAL_PRODUTO_CARNE = {
    "filé de merluza": (1, 1),
    "coxão duro": (2, 1),
    "miolo de alcatra": (4, 4),
    "lagarto": (1, 1),
    "patinho": (3, 2),
    "coxão mole": (2, 2),
    "coxa e sobrecoxa": (2, 2),
    "frango industrializado": (2, 1),
    "peito": (2, 2),
    "lombo": (2, 2),
    "bisteca": (1, 1),
    "pernil": (2, 1),
    "linguiça": (1, 1),
    "hambúrguer": (1, 1),
}

# Tabela 07 do edital (5.24.14.1.1): frequência mensal CONTRATADA da opção do
# prato principal (pp2), por (almoço, jantar), para 26 dias úteis (restrição
# T07). Feijoada Vegetariana (2x/ano) fica de fora: não é mensal e o item
# ainda não existe na planilha.
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

# Tabela 08 do edital (5.25.5): frequência mensal CONTRATADA da composição da
# guarnição, por (almoço, jantar), para 26 dias úteis (restrição T08).
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

# Conjunto P (produtos) e subconjuntos Ip, usados pela restrição O2.
# O "produto" é o insumo base do item, e é um vocabulário compartilhado entre
# categorias: é isso que permite detectar que o prato principal 2 e a guarnição
# usam o mesmo ingrediente no mesmo dia.
Pprod = sorted(df["produto"].dropna().unique())

Ip = {p: [] for p in Pprod}
for i in I:
    p = Produto[i]
    if pd.notna(p):
        Ip[p].append(i)

# ---- Subconjuntos das saladas ----

# Itens de salada_1 com regra própria de frequência (1S2/1S3, FF1..FF3): ficam
# de fora da não-repetição genérica 1S1, que vale só para "as demais".
SALADAS_COM_REGRA_PROPRIA = ["alface", "chicória", "almeirão"]

# IGraoConserva: grãos em conserva (3S2 / 3S3).
IGraoConserva = [i for i in I if GraoEmConserva[i] == 1]

# ICremeMaionese: saladas com creme de maionese (FF4 / FF5).
ICremeMaionese = [i for i in I if CremeMaionese[i] == 1]

# Conjunto de vegetais e subconjuntos Iv, usados pela restrição O1. Mesma
# lógica de Pprod/Ip: vocabulário compartilhado entre salada e guarnição.
Veg = sorted(df["vegetal"].dropna().unique())

Iv = {v: [] for v in Veg}
for i in I:
    v = Vegetal[i]
    if pd.notna(v):
        Iv[v].append(i)

# Falha cedo se os atributos novos vierem vazios: sem isso, as restrições que
# dependem deles seriam construídas sem nenhum termo e não teriam efeito algum,
# silenciosamente.
if not IFritura:
    raise SystemExit("IFritura vazio: conferir a coluna 'fritura' da planilha")
if not IOvos:
    raise SystemExit("IOvos vazio: conferir a coluna 'a_base_de_ovos' da planilha")
if "preparo" not in df.columns or df["preparo"].notna().sum() == 0:
    raise SystemExit(
        "coluna 'preparo' ausente ou vazia: rodar "
        "otimizacao/data/atualizar_planilha.py (necessária para a PEN1)"
    )

# As checagens das saladas só valem quando elas estão no modelo: enquanto
# CATEGORIAS_IGNORADAS estiver populada, os conjuntos abaixo são vazios por
# construção e isso é o estado esperado.
if not CATEGORIAS_IGNORADAS:
    if not IGraoConserva:
        raise SystemExit(
            "IGraoConserva vazio: conferir a coluna 'grao_em_conserva'"
        )
    if not ICremeMaionese:
        raise SystemExit(
            "ICremeMaionese vazio: conferir a coluna 'creme_maionese'"
        )
    if not Veg:
        raise SystemExit("Veg vazio: conferir a coluna 'vegetal' da planilha")

    # Mínimo de itens por categoria de salada. E1 exige 1 item de cada
    # categoria em CADA refeição: numa semana completa são 6 almoços + 5
    # jantas = 11 refeições. Como as regras de não-repetição em 7 dias
    # proíbem reaproveitar o mesmo item dentro da janela, uma categoria com
    # menos itens que o número de slots que precisa preencher torna o modelo
    # INFACTÍVEL — e o solver não diz qual restrição causou isso.
    #
    # Contagem por categoria. Numa semana completa há 6 almoços + 5 jantas.
    #
    #   salada_1: 1S1 vale para a semana INTEIRA (11 slots). Alface cobre
    #             2+2, chicória 1+1 e almeirão 1+1 => 8 slots; restam 3,
    #             cada um exigindo 1 item distinto.
    #             3 + alface + chicória + almeirão = 6.
    #   salada_2: 2S1 é POR REFEIÇÃO, então o mesmo conjunto de itens serve
    #             os dois turnos: basta cobrir o turno maior (6 almoços).
    #   salada_3: idem, mas o grão em conserva cobre até 2 almoços;
    #             restam 4 no almoço + os 2 grãos = 6.
    MINIMO_ITENS_SALADA = {"salada_1": 6, "salada_2": 6, "salada_3": 6}

    for c, minimo in MINIMO_ITENS_SALADA.items():
        if len(Ic[c]) < minimo:
            raise SystemExit(
                f"{c} tem {len(Ic[c])} itens, mínimo {minimo}: o modelo "
                f"ficaria infactível (ver BLOCO 1 no fim do arquivo)"
            )

    # Os mínimos acima são NECESSÁRIOS, mas não SUFICIENTES. Uma categoria
    # exatamente no mínimo fica sem nenhum grau de liberdade: todos os seus
    # itens passam a ser obrigatórios em toda semana, e aí as igualdades
    # FF4/FF5 (creme de maionese exatamente 2x por mês em cada refeição) não
    # têm como ser satisfeitas. Verificado: com salada_2 em exatamente 11 o
    # modelo é INFEASIBLE e o IIS acusa E1_salada_2 + 2S1 + FF4/FF5; com 15
    # resolve normalmente.
    FOLGA_RECOMENDADA = 2
    for c, minimo in MINIMO_ITENS_SALADA.items():
        if len(Ic[c]) < minimo + FOLGA_RECOMENDADA:
            print(
                f"AVISO: {c} tem {len(Ic[c])} itens, no limite do mínimo "
                f"({minimo}). Sem folga as igualdades FF podem ficar "
                f"infactíveis; recomendado >= {minimo + FOLGA_RECOMENDADA}."
            )

# ------------------------ MODELO ------------------------

m = gp.Model()

# ------------------------ VARIÁVEIS ------------------------

x = {}
for d in D:
    for r in R_ds(d):
        for i in I:
            x[i, r, d] = m.addVar(
                vtype=GRB.BINARY,
                name=f"x_{i}_{r}_{d}"
            )

m.update()

# ------------------------ FUNÇÃO AUXILIAR ------------------------

# Implementa o x~ (x til) do relatório, subseção 4.1.3: unifica os dados
# históricos (parâmetro H, já conhecido) e as variáveis de decisão do
# horizonte de planejamento.
def valor_x(i, r, d):
    # Histórico
    if d < 1:
        return historico.get((i, r, d), 0)
    # Variável normal
    return x[i, r, d]

# ------------------------ RESTRIÇÕES ------------------------

# ---------------- E1 ----------------

for d in D:
    for r in R_ds(d):
        if r != "Desjejum":
            for c in C:
                m.addConstr(
                    quicksum(
                        x[i, r, d]
                        for i in Ic[c]
                    ) == 1,
                    name=f"E1_{c}_{r}_{d}"
                )

# ---------------- E2 ----------------

for d in D:
    if "Desjejum" in R_ds(d):
        m.addConstr(
            quicksum(
                x[i, "Desjejum", d]
                for i in Ic["sobremesa_2"]
            ) == 1,
            name=f"E2_{d}"
        )

# ---------------- E3 ----------------

for d in D:
    if "Desjejum" in R_ds(d):
        for c in C:
            if c != "sobremesa_2":
                m.addConstr(
                    quicksum(
                        x[i, "Desjejum", d]
                        for i in Ic[c]
                    ) == 0,
                    name=f"E3_{c}_{d}"
                )

# ---------------- PP1 ----------------

for i in Ic["prato_principal_1"]:
    for d in D:
        m.addConstr(
            quicksum(
                valor_x(i, r, k)
                for k in janela7(d)
                for r in R_ds(k)
            ) <= 1,
            name=f"PP1_{i}_{d}"
        )

# ---------------- PP2 / PP3 (SUBSTITUÍDAS POR PP2T) ----------------
#
# O edital (5.23.15) pede alternância BRANCA/VERMELHA entre almoço e jantar
# do mesmo dia. Essa regra é INCOMPATÍVEL com os tetos da Tabela 06 (T06):
# a alternância exige 1 carne branca por dia nos 21 dias que têm almoço e
# jantar (>= 21 brancas no mês), mas a Tabela 06 teta as brancas em 13
# (merluza 2, coxa/sobrecoxa 4, frango industrializado 3, peito 4).
# Confirmado por IIS: famílias T06max + PP2 + PP3 + E1_prato_principal_1.
#
# DECISÃO DO GRUPO: preservar os tetos da Tabela 06 e afrouxar a alternância
# do 5.23.15, trocando-a por uma alternância mais fraca porém bem definida —
# o TIPO de carne (bovina, suína, frango, peixe) não se repete entre o
# almoço e o jantar do mesmo dia (restrição PP2T abaixo).
#
# As variáveis IBranca/IVermelha continuam em uso por PP6 (a carne do jantar
# não pode ser a mesma do almoço do dia seguinte), que não conflita com T06.
#
# Ver DUVIDAS_EDITAL.md para o registro completo desta e das demais
# contradições encontradas no edital.

# ---------------- PP2T ----------------
#
# Alternância por TIPO de carne: o tipo servido no almoço não se repete no
# jantar do mesmo dia. Usa a coluna "especificacao", que já classifica cada
# prato principal em: carne bovina, carne suina, carne de frango, carne de
# peixe e embutidos.
#
# "embutidos" (linguiça, hambúrguer) entra como tipo próprio: é como o
# edital os classifica na Tabela 06, e PP4/PP5 já restringem seu uso a uma
# única refeição por semana.
#
# Formulação: para cada dia com as duas refeições e cada tipo t, no máximo
# uma das duas refeições pode servir t. Como E1 força exatamente 1 prato
# principal por refeição, isso equivale a exigir tipos distintos.

TIPOS_CARNE = sorted(
    Especificacao[i]
    for i in set(Ic["prato_principal_1"])
    if pd.notna(Especificacao[i])
)
TIPOS_CARNE = sorted(set(TIPOS_CARNE))

I_TIPO_CARNE = {
    t: [i for i in Ic["prato_principal_1"] if Especificacao[i] == t]
    for t in TIPOS_CARNE
}

for d in D:
    refeicoes = R_ds(d)
    if "Almoco" in refeicoes and "Janta" in refeicoes:
        for t in TIPOS_CARNE:
            itens = I_TIPO_CARNE[t]
            if not itens:
                continue
            m.addConstr(
                quicksum(x[i, "Almoco", d] for i in itens)
                + quicksum(x[i, "Janta", d] for i in itens)
                <= 1,
                name=f"PP2T_{t}_{d}".replace(" ", "-")
            )

# ---------------- PP4 / PP5 ----------------

# Na semana em que um embutido é usado no almoço, é vedado no jantar, e
# vice-versa. Ou seja: numa janela de 7 dias, embutido aparece só no almoço
# ou só no jantar, nunca nos dois.
#
# Linearização com Big-M e variável indicadora binária, conforme a OBS do
# relatório na subseção 4.2.2 (mesma linearização usada em SO2). Substitui a
# formulação quadrática (almoco * janta == 0) usada antes, que não era linear.
#
# M = número máximo de ocorrências possíveis numa janela de 7 dias para uma
# única refeição: no máximo 1 embutido por refeição (E1 fixa exatamente 1 item
# de prato_principal_1) em até 7 dias.
M_EMBUTIDO = 7

for d in D:
    almoco_embutido = quicksum(
        valor_x(i, "Almoco", k)
        for k in janela7(d)
        for i in IEmbutido
        if "Almoco" in R_ds(k)
    )

    janta_embutido = quicksum(
        valor_x(i, "Janta", k)
        for k in janela7(d)
        for i in IEmbutido
        if "Janta" in R_ds(k)
    )

    # u = 1 libera o almoço (e zera o jantar); u = 0 libera o jantar.
    u = m.addVar(vtype=GRB.BINARY, name=f"u_PP4PP5_{d}")

    m.addConstr(
        almoco_embutido <= M_EMBUTIDO * u,
        name=f"PP4_{d}"
    )
    m.addConstr(
        janta_embutido <= M_EMBUTIDO * (1 - u),
        name=f"PP5_{d}"
    )

# ---------------- PP6 ----------------

# A carne (especificação) do jantar de um dia não pode ser a mesma do almoço
# do dia seguinte. Usa valor_x para que o dia 1 do horizonte também seja
# comparado com o jantar do último dia histórico (virada do mês).
for d in D:
    for e in E:
        jantar_espec = quicksum(
            valor_x(i, "Janta", d - 1)
            for i in Ie[e]
            if "Janta" in R_ds(d - 1)
        )

        almoco_espec = quicksum(
            valor_x(i, "Almoco", d)
            for i in Ie[e]
            if "Almoco" in R_ds(d)
        )

        m.addConstr(
            jantar_espec + almoco_espec <= 1,
            name=f"PP6_{e}_{d}"
        )

# ---------------- OP1 ----------------

for i in Ic["prato_principal_2"]:
    for d in D:
        m.addConstr(
            quicksum(
                valor_x(i, r, k)
                for k in janela7(d)
                for r in R_ds(k)
            ) <= 1,
            name=f"OP1_{i}_{d}"
        )

# ---------------- OP4 ----------------

# É vedada a utilização de produto à base de soja no mesmo dia no almoço e no
# jantar. Restrição sobre o mesmo dia, então não usa janela nem histórico.
for d in D:
    refeicoes = R_ds(d)
    if "Almoco" in refeicoes and "Janta" in refeicoes:
        m.addConstr(
            quicksum(
                x[i, "Almoco", d]
                for i in ISoja
            )
            +
            quicksum(
                x[i, "Janta", d]
                for i in ISoja
            )
            <= 1,
            name=f"OP4_{d}"
        )

# ---------------- G1 ----------------

for i in Ic["guarnição"]:
    for d in D:
        m.addConstr(
            quicksum(
                valor_x(i, r, k)
                for k in janela7(d)
                for r in R_ds(k)
            ) <= 1,
            name=f"G1_{i}_{d}"
        )

# ---------------- 1S1 / 2S1 / 3S1 ----------------

# Não-repetição das saladas. O EDITAL usa DUAS formulações diferentes, e a
# distinção importa muito para a factibilidade:
#
#   Tipo I  (1S1) - Tabela 05: "Não podendo se repetir DURANTE A SEMANA".
#         Vale para a semana inteira, somando almoço e jantar. É a versão
#         mais restritiva. Exceto alface, chicória e almeirão, que têm
#         frequência própria (1S2/1S3 e FF1..FF3).
#
#   Tipo II (2S1) e Tipo III (3S1) - Tabela 05: "Não podendo se repetir
#         NO ALMOÇO OU JANTAR da mesma semana". É por REFEIÇÃO: o mesmo
#         item pode aparecer uma vez no almoço e uma vez no jantar da
#         semana, desde que em dias diferentes (5.21.7 cuida do mesmo dia).
#         Mesmo padrão da SO2 das frutas (item 5.26.10).
#
# OBS: o item 5.21.3 diz do Tipo II "Não pode se repetir durante a semana",
# o que contradiz a Tabela 05. Adotada a Tabela 05 (por refeição), que é a
# especificação detalhada da regra. Ver BLOCO 2.
#
# 3S1 exclui os grãos em conserva, que têm regra própria (3S2/3S3).

if "salada_1" in Ic:
    for i in Ic["salada_1"]:
        if i in SALADAS_COM_REGRA_PROPRIA:
            continue
        for d in D:
            m.addConstr(
                quicksum(
                    valor_x(i, r, k)
                    for k in janela7(d)
                    for r in R_ds(k)
                ) <= 1,
                name=f"1S1_{i}_{d}"
            )

for c, nome in [("salada_2", "2S1"), ("salada_3", "3S1")]:
    if c not in Ic:
        continue
    for i in Ic[c]:
        if c == "salada_3" and i in IGraoConserva:
            continue
        for d in D:
            for r in ["Almoco", "Janta"]:
                m.addConstr(
                    quicksum(
                        valor_x(i, r, k)
                        for k in janela7(d)
                        if r in R_ds(k)
                    ) <= 1,
                    name=f"{nome}_{r}_{i}_{d}"
                )

# ---------------- 1S2 / 1S3 ----------------

# Alface: até 2x por semana no almoço (1S2) e até 2x por semana no jantar
# (1S3), separadamente.
#
# OBS R2 do relatório: no texto original as duas diziam "almoço"; o edital
# 5.21.2 confirma 2x no almoço e 2x no jantar.

if "alface" in I:
    for d in D:
        for r, nome in [("Almoco", "1S2"), ("Janta", "1S3")]:
            m.addConstr(
                quicksum(
                    valor_x("alface", r, k)
                    for k in janela7(d)
                    if r in R_ds(k)
                ) <= 2,
                name=f"{nome}_{d}"
            )

# ---------------- 3S2 / 3S3 ----------------

# Grão em conserva: até 2x por semana no almoço (3S2) e no jantar (3S3).
#
# Só constrói se houver itens marcados: sem o guard, o somatório vazio geraria
# 62 restrições vacuosas (0 <= 2) que não mudam a solução mas inflam o modelo.

if IGraoConserva:
    for d in D:
        for r, nome in [("Almoco", "3S2"), ("Janta", "3S3")]:
            m.addConstr(
                quicksum(
                    valor_x(i, r, k)
                    for k in janela7(d)
                    for i in IGraoConserva
                    if r in R_ds(k)
                ) <= 2,
                name=f"{nome}_{d}"
            )

# ---------------- FF1 / FF2 / FF3 ----------------

# Frequências FIXAS (igualdades), por semana de calendário.
#
# ATENÇÃO: usam Dw / W_completas, NÃO janela7. São igualdades ("exatamente 1x
# por semana"), e numa semana truncada da borda do mês elas são infactíveis:
# maio/2026 começa numa sexta, então a semana 18 tem só 3 dias. Por isso as
# restrições valem apenas nas semanas completas.

# O edital 5.21.2.3 é explícito: "A frequência semanal de chicória e almeirão
# será de 1 vez no almoço e 1 vez no jantar, DE CADA UMA". Por isso o almeirão
# tem par no jantar (FF3b), resolvendo a OBS R4 do relatório, que listava
# apenas o almoço.

for w in W_completas:
    for item, r, nome in [
        ("chicória", "Almoco", "FF1"),
        ("chicória", "Janta",  "FF2"),
        ("almeirão", "Almoco", "FF3"),
        ("almeirão", "Janta",  "FF3b"),
    ]:
        if item not in I:
            continue
        m.addConstr(
            quicksum(
                x[item, r, d]
                for d in dias_com_refeicao(w, r)
            ) == 1,
            name=f"{nome}_{w[1]}"
        )

# ---------------- FF4 / FF5 ----------------

# Salada com creme de maionese: 2x no almoço (FF4) e 2x no jantar (FF5), por
# mês. Restrição única sobre todo o horizonte, no mesmo padrão de O3.
#
# Construídas apenas quando há itens marcados: como são IGUALDADES, um
# somatório vazio == 2 tornaria o modelo trivialmente infactível.

if ICremeMaionese:
    for r, nome in [("Almoco", "FF4"), ("Janta", "FF5")]:
        m.addConstr(
            quicksum(
                x[i, r, d]
                for d in D
                for i in ICremeMaionese
                if r in R_ds(d)
            ) == 2,
            name=nome
        )

# ---------------- O1 ----------------

# O vegetal da salada não pode repetir na guarnição do mesmo dia.
#
# Não precisa de Big-M (diferente de O2): é uma soma simples de binárias do
# mesmo dia. Para cada vegetal compartilhado, no máximo 1 item com aquele
# vegetal por refeição, somando salada e guarnição.
#
# Só age nos vegetais que aparecem dos DOIS lados; nos demais a restrição
# seria vacuamente satisfeita e só inflaria o modelo.

IGuarnicao = Ic.get("guarnição", [])

for v in Veg:
    itens_salada = [
        i for i in Iv[v] if Categoria[i] in CATEGORIAS_SALADA
    ]
    itens_guarnicao = [i for i in Iv[v] if i in IGuarnicao]

    if not itens_salada or not itens_guarnicao:
        continue

    for d in D:
        for r in R_ds(d):
            m.addConstr(
                quicksum(
                    x[i, r, d]
                    for i in itens_salada + itens_guarnicao
                ) <= 1,
                name=f"O1_{v}_{r}_{d}"
            )

# ---------------- S4 ----------------

# Edital 5.21.7: "As saladas do almoço não podem ser repetidas no jantar do
# mesmo dia."
#
# Não consta do relatório — veio da leitura direta do edital. É análoga à SO3
# das frutas: cada item de salada aparece no máximo 1x por dia, somando as
# duas refeições.

for c in CATEGORIAS_SALADA:
    if c not in Ic:
        continue
    for i in Ic[c]:
        for d in D:
            refeicoes = [r for r in R_ds(d) if r != "Desjejum"]
            if len(refeicoes) < 2:
                continue
            m.addConstr(
                quicksum(x[i, r, d] for r in refeicoes) <= 1,
                name=f"S4_{i}_{d}"
            )

# ---------------- SO1 ----------------

for i in Ic["sobremesa_1"]:
    for d in D:
        m.addConstr(
            quicksum(
                valor_x(i, r, k)
                for k in janela7(d)
                for r in R_ds(k)
            ) <= 1,
            name=f"SO1_{i}_{d}"
        )

# ---------------- SO3 ----------------

for d in D:
    for i in Ic["sobremesa_2"]:
        m.addConstr(
            quicksum(
                x[i, r, d]
                for r in R_ds(d)
                if (i, r, d) in x
            ) <= 1,
            name=f"SO3_{i}_{d}"
        )

# ---------------- SO4 ----------------

for i in Ic["sobremesa_2"]:
    for d in D:
        m.addConstr(
            quicksum(
                valor_x(i, "Desjejum", k)
                for k in janela7(d)
                if "Desjejum" in R_ds(k)
            ) <= 1,
            name=f"SO4_{i}_{d}"
        )

# ---------------- SO2 ----------------

# A sobremesa 2 (fruta) não se repete na mesma refeição durante a semana.
#
# O relatório apresenta DUAS formulações concorrentes (OBS R5):
#   (a) alternância almoço/jantar, por analogia com PP4/PP5, com Big-M;
#   (b) o que o edital (item 5.26.10) diz literalmente: não repetir na mesma
#       refeição durante a semana.
# Implementada a versão (b), do edital. Se o orientador decidir pela (a), a
# formulação é análoga à de PP4/PP5 acima (indicadora binária + Big-M).
#
# Nota: parcialmente redundante com SO3 (mesma fruta em refeições diferentes
# do mesmo dia) e SO4 (repetição no desjejum), que já estão implementadas.

for i in Ic["sobremesa_2"]:
    for d in D:
        for r in ["Almoco", "Janta"]:
            m.addConstr(
                quicksum(
                    valor_x(i, r, k)
                    for k in janela7(d)
                    if r in R_ds(k)
                ) <= 1,
                name=f"SO2_{r}_{i}_{d}"
            )

# ---------------- OP2 / OP3 ----------------

# É vedada a utilização da opção do prato principal 2 à base de ovos mais de
# 2 vezes na semana, no almoço (OP2) e no jantar (OP3), separadamente.

for d in D:
    m.addConstr(
        quicksum(
            valor_x(i, "Almoco", k)
            for k in janela7(d)
            for i in IOvos
            if "Almoco" in R_ds(k)
        ) <= 2,
        name=f"OP2_{d}"
    )
    m.addConstr(
        quicksum(
            valor_x(i, "Janta", k)
            for k in janela7(d)
            for i in IOvos
            if "Janta" in R_ds(k)
        ) <= 2,
        name=f"OP3_{d}"
    )

# ---------------- O2 ----------------

# O ingrediente principal da opção do prato principal (pp2) não pode estar
# presente na composição do cardápio do almoço e do jantar no mesmo dia.
#
# Linearização da implicação lógica do relatório com Big-M e indicadora
# binária, mesma técnica usada em PP4/PP5:
#
#   se algum item de pp2 com produto p é servido no dia
#   -> nenhum item NÃO-pp2 com o mesmo produto p pode ser servido no dia
#
# M = número máximo de itens que podem ser servidos num dia para um mesmo
# produto: no máximo 1 item por categoria (E1) x 8 categorias x 2 refeições.
M_PRODUTO = 16

for p in Pprod:
    itens_pp2 = [i for i in Ip[p] if Categoria[i] == "prato_principal_2"]
    itens_outros = [i for i in Ip[p] if Categoria[i] != "prato_principal_2"]

    # Sem os dois lados a restrição não tem efeito: pular para não poluir o
    # modelo com restrições vazias.
    if not itens_pp2 or not itens_outros:
        continue

    for d in D:
        refeicoes = [r for r in R_ds(d) if r != "Desjejum"]
        if not refeicoes:
            continue

        usa_pp2 = quicksum(
            x[i, r, d]
            for r in refeicoes
            for i in itens_pp2
        )

        usa_outros = quicksum(
            x[i, r, d]
            for r in refeicoes
            for i in itens_outros
        )

        # v = 1 quando o produto p é usado pelo pp2 no dia
        v = m.addVar(vtype=GRB.BINARY, name=f"v_O2_{p}_{d}")

        m.addConstr(usa_pp2 <= M_PRODUTO * v, name=f"O2a_{p}_{d}")
        m.addConstr(usa_outros <= M_PRODUTO * (1 - v), name=f"O2b_{p}_{d}")

# ---------------- O3 ----------------

# A frequência de preparações culinárias utilizando a técnica de fritura será
# permitida no máximo 4 vezes por mês.
# É "por mês", então soma sobre D inteiro: não usa janela nem histórico.

m.addConstr(
    quicksum(
        x[i, r, d]
        for d in D
        for r in R_ds(d)
        for i in IFritura
    ) <= 4,
    name="O3"
)

# ---------------- T06 ----------------

# Tabela 06 do edital (item 5.23.19): "FREQUÊNCIA DE DISTRIBUIÇÃO MENSAL" de
# cada CORTE de carne do prato principal (pp1), por almoço e por jantar.
# Ex.: "Miolo de Alcatra" 4x no almoço e 4x no jantar; "Filé de Merluza" 1x
# em cada; etc.
#
# MOTIVO DA RESTRIÇÃO: sem ela o solver nunca escolhia os cortes de score
# baixo — peixe, lagarto e bisteca saíam 0x no mês inteiro, o que descumpre
# o edital. O objetivo só premia P alto, então os cortes impopulares eram
# simplesmente ignorados.
#
# Agrupa por PRODUTO (o corte), não por item: "bife (alcatra)", "estrogonofe
# de carne" e "iscas de carne (alcatra)" são preparações diferentes do mesmo
# miolo de alcatra, e a cota é do corte, não de cada preparação.
#
# ====================================================================
# POR QUE ESTA RESTRIÇÃO NÃO USA "==" COMO T07/T08
# ====================================================================
#
# A Tabela 06 é MATEMATICAMENTE INCOMPATÍVEL com a alternância branca/
# vermelha do item 5.23.15. Demonstração para maio/2026:
#
#   Cotas da Tabela 06, agregadas por tipo de carne:
#       ALMOÇO   branca  7  | vermelha 19   (total 26)
#       JANTAR   branca  6  | vermelha 16   (total 22)
#
#   (a) A alternância exige 1 carne branca por dia nos 21 dias que têm
#       almoço e jantar, ou seja >= 21 brancas no mês. A Tabela 06 teta as
#       brancas em 13 (merluza 2, coxa/sobrecoxa 4, frango industrializado
#       3, peito 4). Falta de 8.
#
#   (b) Pelo outro lado: das 19 vermelhas exigidas no almoço, no máximo 5
#       cabem nos sábados (sem jantar); as outras 14 exigiriam 14 brancas
#       no jantar, mas a tabela só concede 6.
#
#   Confirmado por IIS nas duas tentativas: com "==" acusa T06 + PP2 + PP3;
#   com piso + teto acusa T06max + PP2 + PP3 + E1_prato_principal_1.
#
# Não é erro de modelagem: é contradição interna do próprio edital, da mesma
# natureza (porém mais grave) que a dos 22 vs. 21 jantares em T07/T08.
#
# DECISÃO DO GRUPO: preservar os TETOS da Tabela 06 (estourar a cota é
# violação inequívoca) e afrouxar a alternância do 5.23.15, substituída pela
# alternância por TIPO de carne (restrição PP2T). Complementarmente, um PISO
# de 1 aparição mensal por corte garante que nenhum corte saia 0x no mês —
# que era o problema original (peixe, lagarto e bisteca nunca apareciam).
#
# O piso é 1, e não a cota cheia, porque a cota cheia é infactível por si:
# no ALMOÇO as cotas somam exatamente 26 (= todos os slots, equivalente a
# "==") e no JANTAR somam 22 contra 21 slots disponíveis.
#
# LIMITAÇÃO CONHECIDA: as quantidades exatas da Tabela 06 não são atingidas
# (ex.: miolo de alcatra pode sair menos que 4x no almoço). Ver
# DUVIDAS_EDITAL.md.

PISO_MENSAL_CORTE = 1

I_PRODUTO_CARNE = {
    p: [i for i in I if Categoria[i] == "prato_principal_1" and Produto[i] == p]
    for p in COTA_MENSAL_PRODUTO_CARNE
}

for p, (cota_almoco, cota_janta) in COTA_MENSAL_PRODUTO_CARNE.items():
    itens = I_PRODUTO_CARNE[p]
    if not itens:
        continue

    # Piso mensal somando as duas refeições: o corte tem de aparecer no mês,
    # mas o solver escolhe em qual refeição encaixá-lo, para não colidir com
    # a alternância branca/vermelha.
    soma_mes = quicksum(
        x[i, r, d]
        for d in D
        for r in R_ds(d)
        if r != "Desjejum"
        for i in itens
    )
    m.addConstr(
        soma_mes >= PISO_MENSAL_CORTE,
        name=f"T06min_{p}".replace(" ", "-")
    )

    # Teto por refeição: continua valendo, porque estourar a cota do edital
    # é violação inequívoca (diferente do piso, que é o que conflita).
    for r, cota in [("Almoco", cota_almoco), ("Janta", cota_janta)]:
        soma = quicksum(
            x[i, r, d]
            for d in D
            if r in R_ds(d)
            for i in itens
        )
        m.addConstr(soma <= cota, name=f"T06max_{p}_{r}".replace(" ", "-"))

# ---------------- T07 ----------------

# Tabela 07 do edital (item 5.24.14.1.1): "FREQUÊNCIA DE DISTRIBUIÇÃO
# MENSAL" de cada tipo de opção do prato principal (pp2), por almoço e por
# jantar. Ex.: "Proteína Texturizada de Soja Moída" 8x no almoço e 5x no
# jantar; "Ovo Cozido" 1x no almoço e 1x no jantar; etc.
#
# "Frequência de distribuição" é a quantidade CONTRATADA, não um teto que a
# contratada pode deixar de atingir — é IGUALDADE (==), não "no máximo".
# Confirmado em rodada anterior: com "<=" o solver zerava itens inteiros
# (ex.: "ovo frito" saiu 0x de uma cota de 2x), o que descumpre o edital.
#
# ALMOÇO: as cotas somam EXATAMENTE 26 (= slots de um mês de 26 dias úteis),
# e E1 já força 1 pp2 por almoço. "==" funciona porque não há folga a
# perder nem a repor.
#
# JANTAR: as cotas somam 22, mas um mês de 26 dias úteis tem só 21 jantas
# (sábado não tem jantar) — o EDITAL tem 1 aparição a mais do que cabe.
# "==" no jantar dá IIS confirmado (família T07 vs. E1_..._Janta). Sem uma
# 12ª linha na Tabela 07 para cortar, a única correção sem inventar dado é
# usar "<=" no jantar — o jantar fica sujeito a não estourar a cota, mas
# não é garantido bater o piso em toda categoria. Documentado como
# LIMITAÇÃO CONHECIDA para o orientador decidir qual linha ceder.
#
# Mesma ressalva vale para janeiro/2026 (27 dias úteis): mesmo o almoço,
# com "==", fica sem folga para o dia 27, e o modelo fica INFEASIBLE
# (testado). Não há correção "certa" sem decisão do orientador — as opções
# são (a) aceitar a violação do edital nesses meses, (b) aumentar a cota do
# item mais frequente proporcionalmente, ou (c) escalar as cotas por
# dias_uteis_reais/26.
#
# Só soma sobre D inteiro (igual O3): é frequência MENSAL, não usa janela
# nem histórico.

I_ESPECIFICACAO = {
    e: [i for i in I if Categoria[i] == "prato_principal_2" and Especificacao[i] == e]
    for e in COTA_MENSAL_ESPECIFICACAO
}

for e, (cota_almoco, cota_janta) in COTA_MENSAL_ESPECIFICACAO.items():
    itens = I_ESPECIFICACAO[e]
    if not itens:
        continue
    for r, cota in [("Almoco", cota_almoco), ("Janta", cota_janta)]:
        soma = quicksum(
            x[i, r, d]
            for d in D
            if r in R_ds(d)
            for i in itens
        )
        expr = (soma == cota) if r == "Almoco" else (soma <= cota)
        m.addConstr(expr, name=f"T07_{e}_{r}".replace(" ", "-"))

# ---------------- T08 ----------------

# Tabela 08 do edital (item 5.25.5): "Frequência" (== quantidade contratada,
# mesma leitura de T07) de cada composição de guarnição, por almoço e por
# jantar. Ex.: "Vegetal C" 4x no almoço e 4x no jantar; "Farinha de
# mandioca" 2x em cada; etc.
#
# Mesma assimetria de T07: ALMOÇO usa "==" (cotas somam exatamente 26,
# sem folga); JANTAR usa "<=" porque as cotas somam 22 e só há 21 jantas —
# 1 aparição a mais do que o mês comporta. Ver a ressalva completa em T07.

I_COMPOSICAO = {
    c: [i for i in I if Categoria[i] == "guarnição" and Composicao[i] == c]
    for c in COTA_MENSAL_COMPOSICAO
}

for c, (cota_almoco, cota_janta) in COTA_MENSAL_COMPOSICAO.items():
    itens = I_COMPOSICAO[c]
    if not itens:
        continue
    for r, cota in [("Almoco", cota_almoco), ("Janta", cota_janta)]:
        soma = quicksum(
            x[i, r, d]
            for d in D
            if r in R_ds(d)
            for i in itens
        )
        expr = (soma == cota) if r == "Almoco" else (soma <= cota)
        m.addConstr(expr, name=f"T08_{c}_{r}".replace(" ", "-"))

# ======================================================================
#                        RESTRIÇÕES AINDA A FAZER
# ======================================================================
#
# Estado atual: implementadas E1-E3, PP1-PP6, OP1-OP4, G1, SO1-SO4,
# O2, O3, e as de salada (1S1-1S3, 2S1, 3S1-3S3, FF1-FF5, O1). O que falta
# está bloqueado por DADOS que não existem, não por dificuldade de modelagem.
#
# ----------------------------------------------------------------------
# BLOCO 1 - SALADAS: IMPLEMENTADAS E ATIVAS
# ----------------------------------------------------------------------
#
# As saladas foram cadastradas a partir do EDITAL (Pregão 10/2021-PUSP-SC,
# item 5.21 e Anexos VII/VIII) e estão ativas: CATEGORIAS_IGNORADAS = [].
#
# Itens cadastrados via atualizar_planilha.py (dicionários SALADA_1/2/3):
#   salada_1 (Tipo I,   folhosos): 9 itens
#   salada_2 (Tipo II,  cozidas) : 12 itens
#   salada_3 (Tipo III, grãos)   : 10 itens
#
# Restrições implementadas e verificadas contra o cardápio gerado:
#
#   (1S1) Tipo I não repete DURANTE A SEMANA (Tabela 05), exceto alface,
#         chicória e almeirão, que têm frequência própria.
#   (1S2) Alface: até 2x por semana no almoço.   [5.21.2]
#   (1S3) Alface: até 2x por semana no jantar.
#   (2S1) Tipo II não repete NA MESMA REFEIÇÃO da semana.  [Tabela 05]
#   (3S1) Tipo III não repete NA MESMA REFEIÇÃO da semana. [Tabela 05]
#   (3S2) Grão em conserva: até 2x por semana no almoço.  [5.21.4, coluna
#   (3S3) Grão em conserva: até 2x por semana no jantar.   grao_em_conserva]
#
#   (FF1)  Chicória: exatamente 1x no almoço por semana.  [5.21.2.3]
#   (FF2)  Chicória: exatamente 1x no jantar por semana.
#   (FF3)  Almeirão: exatamente 1x no almoço por semana.
#   (FF3b) Almeirão: exatamente 1x no jantar por semana.
#   (FF4)  Salada com creme de maionese: 2x no almoço por mês. [5.21.3.3,
#   (FF5)  Salada com creme de maionese: 2x no jantar por mês.  coluna
#                                                               creme_maionese]
#
#   (O1) O vegetal da salada não repete na guarnição do mesmo dia.
#        [5.21.6 e 5.25.2]. Usa a coluna "vegetal", deliberadamente SEPARADA
#        de "produto" (ver pendência 1 no BLOCO 2): é um vocabulário
#        compartilhado entre salada e guarnição. A coluna "composicao" que já
#        existia não serve — "vegetal A folhoso" é grosso demais e proibiria
#        qualquer folhoso junto de qualquer folhoso.
#
#   (S4) Salada do almoço não repete no jantar do MESMO DIA. [5.21.7]
#        Não constava do relatório; veio da leitura direta do edital.
#
# ----------------------------------------------------------------------
# NOMES DOS ITENS: cuidado com colisão
# ----------------------------------------------------------------------
#
# Vários vegetais existem nas DUAS categorias (acelga, brócolis, couve-flor,
# abobrinha são guarnições). Como todos os dicionários de atributos são
# construídos com dict(zip(df["item"], ...)), nomes repetidos se
# sobrescreveriam SILENCIOSAMENTE, ficando com a categoria da última linha.
# Por isso as saladas levam sufixo: "acelga crua", "brócolis na salada", etc.
# A ligação com a guarnição para o O1 é feita pela coluna "vegetal", não pelo
# nome. atualizar_planilha.py falha se encontrar item duplicado.
#
# ----------------------------------------------------------------------
# QUANTOS ITENS SÃO NECESSÁRIOS
# ----------------------------------------------------------------------
#
# E1 exige 1 item de cada categoria em CADA refeição. Numa semana completa há
# 6 almoços + 5 jantas = 11 refeições (domingo não tem refeição, sábado só
# almoço). Os mínimos dependem de QUAL formulação de não-repetição vale:
#
#   salada_1: >= 6   1S1 vale para a semana inteira (11 slots). Alface cobre
#                    2+2, chicória 1+1 e almeirão 1+1 => 8; restam 3, um item
#                    distinto para cada. 3 + os 3 com regra própria = 6.
#   salada_2: >= 6   2S1 é por REFEIÇÃO, então o mesmo conjunto serve os dois
#                    turnos: basta cobrir o turno maior (6 almoços).
#   salada_3: >= 6   idem, e o grão em conserva cobre até 2 almoços; restam
#                    4 no almoço + os 2 grãos = 6.
#
# Codificados em MINIMO_ITENS_SALADA (topo do arquivo), que falha com mensagem
# clara em vez de deixar o modelo dar INFEASIBLE sem explicação. São mínimos
# NECESSÁRIOS, não suficientes: uma categoria exatamente no mínimo não tem
# folga para as igualdades FF, então o código também emite AVISO abaixo de
# mínimo + 2. Os 9/12/10 cadastrados ficam confortavelmente acima.
#
# ATENÇÃO nas FF: usar Dw / W_completas, NÃO janela7. São igualdades, e numa
# semana truncada da borda do mês (ex.: maio/2026 começa numa sexta, então a
# semana 18 tem só 3 dias) uma igualdade "1x por semana" é infactível.
#
# ATENÇÃO no histórico: o dict `historico` (topo do arquivo) já foi atualizado
# com saladas reais do edital. Ele é um EXEMPLO ilustrativo, não dado medido.
# Se for substituído por histórico real, conferir que respeita 1S1/2S1/3S1 e
# S4 — dados históricos incoerentes tornam o modelo infactível nos primeiros
# dias do horizonte, via janela7. (Foi o que acontecia com os placeholders
# antigos: "beterraba" em todos os dias -1..-7 violava 2S1 já no dia 1.)
#
# ----------------------------------------------------------------------
# BLOCO 2 - decisões que precisam do orientador (não é código)
# ----------------------------------------------------------------------
#
#   (SO2) IMPLEMENTADA na versão do edital (item 5.26.10): a fruta não
#         repete na mesma refeição durante a semana. O relatório traz uma
#         formulação concorrente (OBS R5): alternância almoço/jantar, por
#         analogia com PP4/PP5, com Big-M. CONFIRMAR qual vale. Se for a
#         alternância, trocar o bloco SO2 acima por uma cópia do padrão
#         usado em PP4/PP5.
#
#   (FF3) RESOLVIDA pelo edital. O item 5.21.2.3 é explícito: "A frequência
#         semanal de chicória e almeirão será de 1 vez no almoço e 1 vez no
#         jantar, DE CADA UMA". O relatório listava só almeirão no almoço
#         (OBS R4) — estava incompleto. Implementada a versão do edital,
#         com FF3 (almoço) + FF3b (jantar).
#
#   (2S1) AMBIGUIDADE NO PRÓPRIO EDITAL, decidida a favor da Tabela 05.
#         Para a salada Tipo II há duas redações conflitantes:
#           - Tabela 05: "Não podendo se repetir NO ALMOÇO OU JANTAR da
#             mesma semana"  => por refeição (padrão da SO2).
#           - Item 5.21.3 : "Não pode se repetir durante a semana"
#             => nenhuma repetição, como o Tipo I.
#         Adotada a Tabela 05, que é a especificação detalhada da regra e é
#         coerente com o Tipo III (5.21.4 usa a mesma redação por refeição).
#         IMPACTO: a versão "durante a semana" exigiria 11 itens distintos de
#         salada_2, mais do que o edital lista, e deixaria o modelo
#         infactível. CONFIRMAR com o orientador.
#
#   (1) SALADAS NO O2: a coluna "vegetal" (O1) foi mantida SEPARADA de
#       "produto" (O2) de propósito. Unificá-las faria as saladas entrarem
#       no O2 como efeito colateral: a "salada de grão de bico" passaria a
#       conflitar, no mesmo dia, com os pratos principais 2 de grão de bico.
#       Isso pode até ser desejável — o edital 5.24.8 diz que "o ingrediente
#       principal não pode estar na composição do cardápio do almoço e jantar
#       no mesmo dia, POR EXEMPLO O MESMO TIPO DE GRÃO NA OPÇÃO DO PRATO
#       PRINCIPAL E NA SALADA" — mas isso é uma restrição NOVA (grão da
#       salada vs. grão do pp2), não a O1, e vale por dia inteiro, não por
#       refeição. Para adotar, preencher "produto" nas saladas de grão com o
#       mesmo vocabulário do pp2 ("grão de bico", "lentilha", "feijão") e
#       deixar a O2 agir sobre elas.
#
#   (2) 5.24.7 NÃO IMPLEMENTADA: "É vedada a utilização de qualquer produto
#       que contenha soja na mesma refeição, caso o grão servido na salada
#       seja Feijão tipo Soja." Liga "salada de soja" (salada_3) ao conjunto
#       ISoja dos pratos principais 2. É simples de modelar (soma <= 1 por
#       refeição), mas precisa de confirmação de que "salada de soja" é o
#       item certo do lado da salada.
#
#   Restrições não oficiais mencionadas no relatório, ainda sem modelagem:
#         "segunda a sobremesa é sempre algo já pronto"
#         "estrogonofe geralmente vem com batata palha"
#
#   (PEN1) IMPLEMENTADA, e também não é regra do edital: penalização de
#         proximidade entre pratos de mesmo MODO DE PREPARO (estrogonofe de
#         carne x estrogonofe de frango no mesmo dia, lasanha de pp1 x
#         lasanha de pp2 na mesma refeição). Usa a coluna "preparo", criada
#         para isso. A classificação é julgamento culinário e PRECISA DE
#         VALIDAÇÃO DA NUTRICIONISTA. Ver DUVIDAS_EDITAL.md, item 8.
#
#   Fator de aleatoriedade no score de preferência para dar variabilidade
#   entre meses (subseção 4.1 do relatório, a testar).
#
# ----------------------------------------------------------------------
# BLOCO 3 - SCORE DE PREFERÊNCIA (P): RESOLVIDO
# ----------------------------------------------------------------------
#
# A coluna P foi preenchida com os coeficientes do DML
# (previsao/notebooks/Double_Machine_Learning.ipynb), rodado sobre
# previsao/data/dataarea1.csv. Antes disso P valia 1.0 para todos os itens e
# o objetivo era uma CONSTANTE (271.0): qualquer cardápio factível era ótimo
# e o solver resolvia com 0 iterações de simplex. Agora o objetivo
# discrimina de fato (1403.36, ~3000 iterações).
#
# COMO OS COEFICIENTES VIRARAM P:
#
# O DML estima o efeito de cada item sobre o TOTAL de refeições servidas, e
# os valores brutos vão de -429 a +257. Eles NÃO podem ir direto para P:
# o objetivo é S = P[i] * F[r][s(d)], maximizado, com F > 0. Com P negativo,
# um F maior (sexta-feira, F=1.2) tornaria um item ruim MENOS penalizado,
# invertendo a intenção do fator F.
#
# Por isso os coeficientes foram reescalados linearmente para [1, 10]
# DENTRO DE CADA CATEGORIA. Duas decisões aqui:
#
# (a) POR CATEGORIA, não global. E1 força exatamente 1 item de cada categoria
#     por refeição, então a competição só existe entre itens da MESMA
#     categoria. Uma escala global só faria categorias de coeficiente maior
#     inflarem o objetivo, sem nenhum efeito sobre a escolha.
#
# (b) PISO 1, NÃO 0. Esta é a parte sutil. Com P = 0 o produto S = P * F
#     zera, e o fator F deixa de agir sobre aquele item: o modelo ficaria
#     INDIFERENTE entre servir o pior prato numa segunda (F=1.0) ou numa
#     sexta (F=1.2), perdendo justamente a informação de que sexta tem mais
#     movimento. Pior: P = 0 tornaria o item ruim indistinguível de uma
#     salada, que tem S = 0 por decisão de projeto (ausência de fonte de
#     preferência), não por ser ruim. Com piso 1 a razão entre melhor e pior
#     item é 10:1 e F volta a agir sobre todos.
#
#     O P médio dos itens servidos acompanha o fator F da refeição: o modelo
#     concentra os melhores pratos onde F é maior. Por isso o F também vem
#     do DML (ver FUNÇÃO OBJETIVO); o F antigo, escrito à mão, era maior
#     justamente na sexta, o dia de menor movimento.
#
# ATENÇÃO ao interpretar a escala: o 1 não significa "preferência zero", e o
# 10 não é um teto absoluto. São o pior e o melhor item OBSERVADOS em cada
# categoria. Se um item pior entrar na planilha numa próxima rodada do DML,
# todos os P daquela categoria se deslocam. A escala é ordinal-relativa, não
# cardinal-absoluta.
#
# COBERTURA (142 itens com score, de 183):
#   100 itens - casaram direto com o histórico (após normalizar
#               maiúsculas/acentos: o scrape usa "Bife", a planilha "bife")
#    27 itens - casaram por SINÔNIMO. A planilha detalha o preparo e o
#               histórico não: "bife (alcatra)" e "bife (coxão mole)" são
#               ambos "Bife" no scrape; as 4 variações de batata são só
#               "Batata". O mapeamento está em aplicar_P.py.
#    15 itens - SEM histórico. Recebem P = 5.5, o ponto médio da escala
#               [1, 10], que é o neutro: não são favorecidos nem punidos
#               por falta de dado.
#               (ex.: alfajor, banoffe, canelone de ricota, frango xadrez)
#
# O QUE AINDA NÃO TEM SCORE:
#   sobremesa_2 (frutas, 10 itens) - o DML não cobre esta categoria. Estão
#         com P = 1.0 (piso da escala), o que é INÓCUO hoje: E2 força 1 fruta por
#         refeição, então todas competem entre si com o mesmo peso e o
#         resultado é arbitrário dentro dessa categoria. Para diferenciá-las
#         seria preciso outra fonte de dados.
#   saladas (31 itens) - neutras POR DECISÃO (CATEGORIAS_SEM_SCORE, topo do
#         arquivo). Não é pendência.
#
# RESSALVAS METODOLÓGICAS (para o relatório / orientador):
#   - O DML foi rodado só na AREA 1. A area2 tem outro CSV e pode ter
#     preferências diferentes; hoje o modelo assume as da area 1.
#   - O RandomForestClassifier emitiu warning de propensity score próximo de
#     0/1, o que é esperado com muitas dummies de tratamento e poucas
#     observações por item, mas enfraquece a garantia teórica do DML.
#   - O coeficiente mede efeito sobre DEMANDA TOTAL, que é uma proxy de
#     popularidade — não é medida direta de preferência declarada.
#
# BLOCO 4 - limitação de ambiente
# ----------------------------------------------------------------------
#
# RESOLVIDO: com a licença WLS acadêmica configurada em ~/gurobi.lic o modelo
# resolve normalmente (~11 mil variáveis, ótimo em menos de 1 segundo). A
# limitação anterior era a licença size-limited que vinha junto do pacote pip.
#
# A licença WLS exige conexão com a internet durante o uso e vale 90 dias,
# renováveis em https://license.gurobi.com/. As credenciais são pessoais e
# NÃO devem ser commitadas.
#
# Se der infactível, usar m.computeIIS() + m.write("modelo.ilp").
#
# ----------------------------------------------------------------------
# BLOCO 4b - AUDITORIA DO EDITAL: O QUE AINDA FALTA IMPLEMENTAR
# ----------------------------------------------------------------------
#
# Auditoria completa do Anexo I (Memorial Descritivo) contra o modelo.
# As restrições de SALADA estão 100% cobertas; as lacunas estão nas
# FREQUÊNCIAS MENSAIS das demais categorias.
#
# ====== (A) TABELA 06 - frequência mensal por CORTE DE CARNE (5.23.19)
#
#     IMPLEMENTADA (restrições T06min / T06max).
#
#     Não foi preciso criar coluna nova: a coluna "produto" da planilha já
#     registra o corte, e os 14 produtos de prato_principal_1 batem
#     1-para-1 com as 14 linhas da Tabela 06.
#
#     ATENÇÃO: esta tabela é MATEMATICAMENTE INCOMPATÍVEL com a alternância
#     branca/vermelha do 5.23.15 — a alternância exige >= 21 carnes brancas
#     no mês e a Tabela 06 teta as brancas em 13. Por decisão do grupo, os
#     tetos da Tabela 06 foram preservados e a alternância do 5.23.15 foi
#     substituída pela alternância por TIPO de carne (restrição PP2T, que
#     tomou o lugar de PP2/PP3).
#
#     A cota é aplicada como TETO por refeição + PISO de 1 aparição mensal
#     por corte. As quantidades exatas não são atingidas.
#     Ver DUVIDAS_EDITAL.md, item 1, para a demonstração completa.
#
# ====== (B) TABELA 07 - frequência mensal da OPÇÃO DO PRATO PRINCIPAL
#
#     IMPLEMENTADA (restrição T07). Usa a coluna "especificacao", que já
#     existia. Foi preciso reclassificar 9 itens de pp2 que estavam com
#     especificacao="outro" para uma linha real da Tabela 07 (ver
#     RECLASSIFICACAO_ESPECIFICACAO_PP2 em atualizar_planilha.py); 2 itens
#     (almôndega de ricota, almôndega de aveia) não se encaixam em nenhuma
#     linha e ficam sem cota, de propósito.
#
#     "Frequência de distribuição mensal" é a quantidade CONTRATADA, não um
#     teto: é IGUALDADE, não "no máximo". A primeira versão desta restrição
#     usava "<=" e o solver zerava itens inteiros (ex.: "ovo frito" saía 0x
#     de uma cota de 2x) — bug de interpretação corrigido.
#
#     ALMOÇO usa "==": as cotas somam EXATAMENTE 26 (slots de um mês de 26
#     dias úteis), sem folga. JANTAR usa "<=": as cotas somam 22, mas há só
#     21 jantas no mês — o próprio edital tem 1 aparição a mais do que cabe.
#     Ver a ressalva completa junto à restrição T07 no código.
#
# ====== (C) TABELA 08 - composição das GUARNIÇÕES (5.25.5)
#
#     IMPLEMENTADA (restrição T08). Usa a coluna "composicao", que já
#     existia mas nunca tinha sido carregada num dict do modelo. Foi preciso
#     cadastrar uma guarnição nova ("suflê de guarnição", composicao=
#     "farinha de trigo"): a planilha não tinha nenhum item desse tipo, e
#     sem ele a soma das cotas ficava abaixo dos slots do mês (infactível).
#
#     Mesma leitura de igualdade e mesma assimetria almoço/jantar que T07.
#
# ====== (D) TABELA 09 - frequência mensal das SOBREMESAS (5.26.2)
#
#     NÃO IMPLEMENTADA. Cada tipo de doce tem cota própria (arroz doce 1+1,
#     pudim 2+1, gelatina 2+2, flan 2+2, sorvete 2+1...). Precisa de coluna
#     nova classificando cada sobremesa_1 no tipo da Tabela 09.
#
# ====== (E) TABELA 10 - frequência mensal das FRUTAS (5.26.14)
#
#     NÃO IMPLEMENTADA. Abacaxi 4+4, banana 4+4, laranja 3+2, maçã 3+2,
#     mamão 3+2, melancia 4+4, melão 3+3, tangerina 2+1, e as anuais
#     (caqui 2/ano, goiaba 6+4/ano). Só precisa das cotas, os itens já
#     estão em sobremesa_2.
#
# ====== (F) DESJEJUM (5.20.3 e 5.20.4)
#
#     5.20.3 "Não será permitida a repetição do mesmo tipo de fruta na
#            semana" (no desjejum)                        NÃO IMPLEMENTADA
#     5.20.4 "A fruta servida no desjejum não poderá ser a mesma oferecida
#            no almoço e jantar do dia"                   IMPLEMENTADA (SO3)
#
# ====== (G) REGRAS QUE LIGAM SALADA A PRATO PRINCIPAL
#
#     5.24.7 soja: se a salada Tipo III for feijão soja, nada com soja na
#            mesma refeição.                              NÃO IMPLEMENTADA
#     5.24.8 mesmo grão na salada e no pp2 do mesmo dia.  NÃO IMPLEMENTADA
#            (a coluna "vegetal" foi mantida separada de "produto"
#             justamente para não acoplar isso por acidente — ver BLOCO 2)
#
# ====== (H) REGRAS FORA DO ESCOPO DE UM MODELO DE CARDÁPIO
#
#     Não são restrições de otimização e não devem ser implementadas:
#     porções mínimas em gramas (Tabela 04/06/07), temperatura, higiene,
#     uniformes, transporte, análises microbiológicas, pesquisa de
#     satisfação (5.17.37), cardápios de datas comemorativas (5.18.7),
#     sazonalidade (6.11.3.1). São obrigações operacionais da contratada.
#
# ----------------------------------------------------------------------
# ORDEM SUGERIDA PARA O QUE RESTA (do mais barato ao mais caro)
# ----------------------------------------------------------------------
#   1. Tabela 10 (frutas)     - só as cotas, itens já existem
#   2. 5.20.3 (fruta desjejum não repete na semana) - padrão SO2
#   3. 5.24.7 / 5.24.8        - acoplam salada a pp2
#   4. Tabela 09 (sobremesas) - precisa de coluna "tipo_doce"
#
# As dúvidas e contradições do edital que precisam de decisão do orientador
# estão consolidadas em otimizacao/DUVIDAS_EDITAL.md.
#
# ======================================================================

# BLOCO 5 - RESSALVAS SOBRE OS CARDÁPIOS GERADOS HOJE
# ----------------------------------------------------------------------
#
# O modelo resolve em OPTIMAL e respeita todas as restrições implementadas,
# mas o cardápio que ele produz AINDA NÃO É ENTREGÁVEL. Os números abaixo
# são de maio/2026 (26 almoços + 21 jantas = 47 refeições principais).
#
# (1) BAIXA DIVERSIDADE — o problema mais visível
#
#     Itens do catálogo efetivamente usados no mês:
#       prato_principal_1   11/28  (39%)   -> 17 itens nunca aparecem
#       prato_principal_2   12/37  (32%)   -> 25 nunca aparecem
#       guarnição           11/28  (39%)   -> 17 nunca aparecem
#       sobremesa_1         11/49  (22%)   -> 38 nunca aparecem
#       saladas             31/31 (100%)   <- contraste revelador
#
#     A CAUSA é estrutural, não um bug. E1 exige 47 itens por categoria no
#     mês; as regras de não-repetição (PP1/OP1/G1/SO1) permitem cada item
#     ~4-5x. Logo 11 itens no teto de repetição já cobrem os 47 slots. Como
#     o objetivo só premia P alto, o solver escolhe os 11 melhores e os
#     repete até o limite — não há nada no modelo que valorize variedade.
#     O padrão de uso é literalmente [5,5,5,4,4,4,4,4,4,4,4].
#
#     As saladas usam 100% do catálogo justamente porque têm peso neutro:
#     sem gradiente de score, o solver não tem motivo para concentrar.
#
# (2) COTAS DO EDITAL — SITUAÇÃO ATUAL
#
#     As Tabelas 06, 07 e 08 estão implementadas e o cardápio gerado
#     respeita todos os seus tetos (verificado em maio/2026).
#
#     A Tabela 06 foi o que corrigiu a maior distorção: antes dela, os
#     cortes de score baixo saíam 0x no mês inteiro — peixe, lagarto e
#     bisteca nunca apareciam, o que descumpre o edital de forma óbvia.
#     Hoje todos os 14 cortes aparecem pelo menos 1x.
#
#     Isso também atacou o problema (1) de diversidade pela raiz: forçar
#     distribuição entre cortes/composições impede o otimizador de
#     concentrar nos poucos itens de P alto. Em prato_principal_1 o uso do
#     catálogo subiu de 11/28 para 15/28 itens.
#
#     LIMITAÇÃO: as quantidades EXATAS da Tabela 06 não são atingidas,
#     porque são incompatíveis com a alternância do 5.23.15.
#     Ver DUVIDAS_EDITAL.md, item 1.
#
# (3) O SCORE É UMA PROXY, NÃO PREFERÊNCIA DECLARADA
#
#     O coeficiente do DML mede efeito sobre a DEMANDA TOTAL do RU. Um prato
#     com coeficiente alto pode indicar popularidade, mas também que ele foi
#     servido em dias de movimento naturalmente maior. O DML controla
#     covariáveis (clima, calendário letivo, dia da semana), o que mitiga
#     isso, mas não elimina. Ver ressalvas metodológicas no BLOCO 3.
#
# (4) NÃO HÁ RESTRIÇÃO NUTRICIONAL
#
#     O modelo não conhece caloria, proteína, sódio ou custo. O edital exige
#     "alimentação balanceada" (item 1.1) e a Tabela 04 define porções, mas
#     nada disso está no modelo. Um cardápio pode ser ótimo para o objetivo
#     e desequilibrado nutricionalmente.
#
# (5) SEM CUSTO
#
#     O contrato é por preço unitário de refeição. Maximizar popularidade
#     sem restrição orçamentária tende a puxar para os itens mais caros
#     (carnes nobres, sobremesas elaboradas). Falta a dimensão de custo.
#
# ----------------------------------------------------------------------
# O QUE MELHORARIA MAIS, EM ORDEM DE CUSTO-BENEFÍCIO
# ----------------------------------------------------------------------
#
# (a) Implementar a Tabela 08 (cotas de composição da guarnição). Os dados
#     JÁ EXISTEM na coluna "composicao". É a maior melhoria por menor
#     esforço: corrige violação do edital E aumenta diversidade.
#
# (b) Implementar a Tabela 06 (frequência por corte). Precisa de uma coluna
#     nova mapeando prato -> corte de carne.
#
# (c) Termo de diversidade no objetivo. Alternativas:
#       - limite de aparições por item no mês (mais simples);
#       - penalizar concentração via variável de "item usado" com custo fixo;
#       - maximizar o número de itens distintos como objetivo secundário.
#     Vale discutir com o orientador se diversidade é objetivo ou restrição.
#
# (d) Restrições nutricionais e/ou de custo, se houver dados. Exigiria
#     colunas novas na planilha.
#
# (e) Rodar o DML também na área 2 e comparar. Hoje o P vem só da área 1.
#
# ======================================================================

# ------------------------ FUNÇÃO OBJETIVO ------------------------

# Fator temporal F[r][dia da semana]: peso de cada refeição no objetivo.
#
# Vem do DML, igual ao P dos pratos: a última seção de
# previsao/notebooks/Double_Machine_Learning.ipynb estima o efeito de cada
# combinação dia da semana x refeição sobre a demanda total, controlando
# pratos, clima e calendário, e exporta os coeficientes para o CSV abaixo.
#
# Antes o F era escrito à mão e estava INVERTIDO em relação aos dados: dava
# o maior peso à sexta (almoço 1.2, jantar 1.1), que é o dia de MENOR
# movimento, e o menor ao jantar de segunda (0.9), um dos mais cheios. Como
# o objetivo P x F leva os maiores P para os maiores F, os melhores pratos
# iam para os piores dias.
#
# Reescala dos coeficientes, mesma lógica do P (ver BLOCO 3):
#   - linear, para [F_MIN, F_MAX]; a ordem dos coeficientes é preservada;
#   - escala ÚNICA para almoço e jantar (e não por refeição), porque o F
#     compara refeições entre si: é isso que decide onde vão os melhores
#     pratos;
#   - piso 1, não 0: com F = 0 a refeição mais vazia deixaria de ter
#     preferência entre os pratos (S = P x 0);
#   - teto 2: a razão entre a refeição mais cheia e a mais vazia na demanda
#     observada é ~1.7 (ter almoço x sex jantar), então [1, 2] mantém o F
#     na mesma ordem de grandeza da diferença real de público.
#
# O desjejum fica fora do DML (o notebook remove o café da manhã) e mantém
# F = 1.0; hoje isso é inócuo, porque todas as frutas têm o mesmo P.
CAMINHO_COEF_TEMPORAL = "otimizacao/data/coef_dml_temporal_area1.csv"
F_MIN, F_MAX = 1.0, 2.0

coef_temporal = pd.read_csv(
    CAMINHO_COEF_TEMPORAL, index_col="dia_refeicao"
)["coef"]
coef_min, coef_max = coef_temporal.min(), coef_temporal.max()

# Nomes usados no CSV do DML (colunas Dia_semana e refeicao dos dados).
DIAS_DML = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
REFEICOES_DML = {"Almoco": "almoco", "Janta": "jantar"}

F = {
    "Desjejum": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
    "Almoco":   [0.0] * 7,
    "Janta":    [0.0] * 7,
}

for r, r_dml in REFEICOES_DML.items():
    for ds, dia_dml in enumerate(DIAS_DML):
        chave = f"{dia_dml}_{r_dml}"
        if chave in coef_temporal.index:
            F[r][ds] = F_MIN + (F_MAX - F_MIN) * (
                (coef_temporal[chave] - coef_min) / (coef_max - coef_min)
            )

# Falha cedo se alguma refeição servida no horizonte ficou sem coeficiente:
# ela entraria no objetivo com F = 0, e o solver passaria a ser indiferente
# aos pratos daquela refeição, silenciosamente.
for d in D:
    for r in R_ds(d):
        if F[r][s(d)] <= 0:
            raise SystemExit(
                f"F[{r}][{DIAS_DML[s(d)]}] sem coeficiente em "
                f"{CAMINHO_COEF_TEMPORAL}"
            )

print("\nFator temporal F (do DML):")
for r in ["Almoco", "Janta"]:
    print(f"  {r:7s}", "  ".join(
        f"{DIAS_DML[ds]} {F[r][ds]:.2f}" for ds in range(6) if F[r][ds] > 0
    ))

S = {}
for d in D:
    for r in R_ds(d):
        for i in I:
            # Saladas com peso neutro: participam das restrições, mas não
            # somam nada ao objetivo (ver CATEGORIAS_SEM_SCORE no topo).
            if Categoria[i] in CATEGORIAS_SEM_SCORE:
                S[i, r, d] = 0.0
            else:
                S[i, r, d] = P[i] * F[r][s(d)]

# ---------------- PEN1: penalização de proximidade por MODO DE PREPARO ----
#
# PROBLEMA: pratos de preparo igual mas ingrediente diferente apareciam
# colados — "estrogonofe de carne" no almoço e "estrogonofe de frango" no
# jantar do mesmo dia, ou "lasanha bolonhesa" (pp1) e "lasanha de pvt"
# (pp2) na MESMA refeição. Para o modelo eles eram maximamente distintos
# (espécies e cortes diferentes, passam por PP2T/PP6), mas para quem come
# são o mesmo prato. Medido no cardápio de maio/2026 ANTES desta
# penalização: 10 colisões no mesmo dia e 12 em refeições consecutivas.
#
# NÃO É REGRA DO EDITAL. É critério de qualidade do cardápio, decidido
# pelo grupo. Ver DUVIDAS_EDITAL.md, item 8.
#
# POR QUE PENALIZAÇÃO E NÃO RESTRIÇÃO: uma proibição rígida ("no máximo 1
# estrogonofe por dia") é cega à distância — trataria igual um par colado
# no mesmo dia e um par separado por duas semanas, e pode tornar o modelo
# infactível quando combinada com as cotas fixas da Tabela 07 (lasanha
# aparece em "massa com queijo" E "massa com pts", ambas com cota mensal).
# A penalização deixa o solver decidir: ele aceita a colisão só quando o
# ganho de popularidade compensa, e o custo cresce quanto mais perto.
#
# FORMULAÇÃO: trabalha em SLOTS (a sequência cronológica de refeições
# principais), não em dias. Almoço -> jantar do mesmo dia é distância 1,
# que é justamente o caso mais visível. Para cada par de slots (a, b) com
# a < b e distância k = b - a <= ALCANCE_PEN, e cada preparo q, cria-se
# uma variável de colisão z[q,a,b] >= 0 com:
#
#     z[q,a,b] >= (itens de q no slot a) + (itens de q no slot b) - 1
#
# z só é forçada a 1 quando o preparo q aparece nos DOIS slots; caso
# contrário o lado direito é <= 0 e o solver deixa z em 0, porque a
# penalização é negativa no objetivo (maximização). Não precisa ser
# binária nem ter restrição de teto: a própria maximização empurra z para
# baixo. Isso mantém a relaxação linear apertada e o modelo rápido.
#
# O PESO DECAI COM A DISTÂNCIA: peso(k) = PESO_PEN_BASE / k. A distância 0
# (mesma refeição) é tratada à parte, com o dobro do peso da distância 1,
# EXCETO o par pp1 + pp2 de mesmo preparo, que passou a ser DESEJADO e
# recebe bônus (BON1, abaixo). A distância 0 continua pegando os outros
# casos, ex.: "ovo frito" (pp2) com "batata corada" (guarnição, frito).
#
# PRESENÇA, NÃO CONTAGEM: nos pares a distância k >= 1, cada slot entra
# com y[q,slot] = "o preparo q aparece no slot", e não com a soma dos
# itens. Com a soma, um slot com estrogonofe no pp1 E no pp2 (2 itens)
# ativaria z >= 2 + 0 - 1 = 1 contra TODOS os vizinhos, mesmo sem nenhum
# estrogonofe neles — e o bônus BON1 nunca compensaria. y é contínua em
# [0, 1] com y >= x[i] para cada item de q: a maximização empurra y para
# baixo, então y = max(x[i]), sem precisar ser binária.
#
# CALIBRAÇÃO DO PESO: o maior S possível é ~20 (P=10 no melhor slot,
# F=2.0). Com PESO_PEN_BASE = 25, uma colisão em slots adjacentes custa 25
# — mais que o ganho máximo de trocar um prato por outro dentro da mesma
# categoria, então o solver só colide quando não há alternativa factível.
# A distâncias maiores o custo cai (12.5 a 2 slots, 8.3 a 3...), virando
# um desempate suave em vez de uma proibição.

ALCANCE_PEN = 4      # até quantos slots de distância a penalização age
PESO_PEN_BASE = 25.0  # custo de uma colisão em slots adjacentes (k = 1)

Preparo = dict(zip(df["item"], df["preparo"]))

# Preparos com 2+ itens: com 1 item só, a não-repetição em 7 dias
# (PP1/OP1/G1) já impede a proximidade, e a penalização seria inócua.
PREPAROS = sorted({
    p for p in df["preparo"].dropna().unique()
    if len([i for i in I if Preparo.get(i) == p]) >= 2
})

I_PREPARO = {q: [i for i in I if Preparo.get(i) == q] for q in PREPAROS}

# Slots = refeições principais em ordem cronológica. O desjejum fica fora:
# só tem fruta, que não tem preparo.
slots = [
    (d, r)
    for d in D
    for r in ["Almoco", "Janta"]
    if r in R_ds(d)
]

penalidades = []
bonus = []

# ---------------- BON1: bônus para pp1 e pp2 do MESMO PREPARO -------------
#
# Pedido do grupo: é desejável que a opção vegetariana "acompanhe" o prato
# principal — estrogonofe de frango + estrogonofe de pvt, lasanha
# bolonhesa + lasanha de berinjela. Para o comensal, pp1 e pp2 viram duas
# versões do mesmo prato. NÃO É REGRA DO EDITAL; ver DUVIDAS_EDITAL.md,
# item 9.
#
# FORMULAÇÃO: para cada slot e preparo q, b[q,slot] em [0, 1] com
#
#     b <= (itens pp1 de q no slot)   e   b <= (itens pp2 de q no slot)
#
# Como E1 força exatamente 1 pp1 e 1 pp2 por refeição, os dois lados são
# 0/1 e b só pode valer 1 quando os dois pratos são de q. O bônus é
# positivo no objetivo, então a maximização empurra b para cima até esse
# teto: não precisa ser binária.
#
# CALIBRAÇÃO: PESO_BON1 = 5 é ~1/4 do maior S (~20) e ~1/5 do custo de uma
# colisão adjacente do PEN1. Serve de desempate forte entre pp2 de score
# parecido, mas não faz o solver trocar um pp2 bom por um ruim só para
# casar o preparo. O próprio PEN1 (distância k >= 1) e OP1/PP1 limitam
# quantas vezes cada preparo pode casar no mês.
PESO_BON1 = 5.0

IPP1 = set(Ic["prato_principal_1"])
IPP2 = set(Ic["prato_principal_2"])

# Só preparos que existem nas duas categorias podem casar.
PREPAROS_BON1 = [
    q for q in PREPAROS
    if IPP1 & set(I_PREPARO[q]) and IPP2 & set(I_PREPARO[q])
]

b_BON1 = {}
for q in PREPAROS_BON1:
    pp1_q = [i for i in I_PREPARO[q] if i in IPP1]
    pp2_q = [i for i in I_PREPARO[q] if i in IPP2]
    for d, r in slots:
        nome = f"{q}_{d}_{r}".replace(" ", "-")
        bq = m.addVar(lb=0.0, ub=1.0, name=f"b_BON1_{nome}")
        m.addConstr(bq <= quicksum(x[i, r, d] for i in pp1_q), name=f"BON1a_{nome}")
        m.addConstr(bq <= quicksum(x[i, r, d] for i in pp2_q), name=f"BON1b_{nome}")
        b_BON1[q, d, r] = bq
        bonus.append(PESO_BON1 * bq)

print(f"\nBON1: {len(PREPAROS_BON1)} preparos podem casar pp1/pp2 "
      f"({', '.join(PREPAROS_BON1)}), peso {PESO_BON1}")

for q in PREPAROS:
    itens_q = I_PREPARO[q]

    # ---- distância 0: mesma refeição ----
    # Peso dobrado em relação à distância 1: é o caso mais visível. O par
    # pp1 + pp2 casado pelo BON1 é descontado (- b), então só colide o que
    # sobrar além dele (ex.: pp1, pp2 e guarnição todos "frito").
    for d, r in slots:
        ocorrencias = quicksum(x[i, r, d] for i in itens_q)
        casado = b_BON1.get((q, d, r), 0)
        z = m.addVar(lb=0.0, name=f"z_PEN1_{q}_{d}_{r}".replace(" ", "-"))
        m.addConstr(z >= ocorrencias - 1 - casado, name=f"PEN1_0_{q}_{d}_{r}".replace(" ", "-"))
        penalidades.append(2.0 * PESO_PEN_BASE * z)

    # ---- presença do preparo em cada slot (ver "PRESENÇA, NÃO CONTAGEM") ----
    y = {}
    for d, r in slots:
        nome = f"{q}_{d}_{r}".replace(" ", "-")
        y[d, r] = m.addVar(lb=0.0, ub=1.0, name=f"y_PEN1_{nome}")
        for i in itens_q:
            m.addConstr(y[d, r] >= x[i, r, d], name=f"PEN1y_{nome}_{i}".replace(" ", "-"))

    # ---- distância k >= 1: pares de slots próximos ----
    for a in range(len(slots)):
        for b in range(a + 1, min(a + 1 + ALCANCE_PEN, len(slots))):
            k = b - a
            da, ra = slots[a]
            db, rb = slots[b]

            z = m.addVar(lb=0.0, name=f"z_PEN1_{q}_{da}{ra[:3]}_{db}{rb[:3]}".replace(" ", "-"))
            m.addConstr(
                z >= y[da, ra] + y[db, rb] - 1,
                name=f"PEN1_{k}_{q}_{da}{ra[:3]}_{db}{rb[:3]}".replace(" ", "-")
            )
            penalidades.append((PESO_PEN_BASE / k) * z)

print(f"\nPEN1: {len(PREPAROS)} preparos penalizados, "
      f"{len(penalidades)} termos (alcance {ALCANCE_PEN} slots, "
      f"peso base {PESO_PEN_BASE})")

# ---------------- PEN2: pp2 mais atrativo que o pp1 ----------------------
#
# Pedido do grupo: o prato principal 2 (vegetariano) não deve ofuscar o
# prato principal 1. Nunca deveria sair, por exemplo, o MELHOR pp2 junto
# do PIOR pp1. NÃO É REGRA DO EDITAL; ver DUVIDAS_EDITAL.md, item 9.
#
# COMPARAR P ENTRE CATEGORIAS FAZ SENTIDO AQUI: o P é reescalado para
# [1, 10] DENTRO de cada categoria (BLOCO 3), então P = 10 é "o melhor da
# categoria" e P = 1 "o pior". P_pp2 > P_pp1 lê-se como "o pp2 está mais
# alto no ranking dele do que o pp1 no dele", que é a noção de "mais
# atrativo" pedida — e não uma comparação de demanda absoluta.
#
# FORMULAÇÃO: penalidade linear por refeição (hinge), com folga:
#
#     v[slot] >= P(pp2 do slot) - P(pp1 do slot) - FOLGA_PEN2,   v >= 0
#
# Como E1 força exatamente 1 item de cada, as somas abaixo são o P do
# prato escolhido. A penalização é negativa no objetivo, então v fica em
# max(0, excesso) sem precisar de binária.
#
# CALIBRAÇÃO ("não tão severa"):
#   - FOLGA_PEN2 = 1.0: inversões pequenas (pp2 até 1 ponto acima) são de
#     graça. Pratos de P parecido não travam o modelo.
#   - PESO_PEN2 = 1.0 por ponto de excesso. O pior caso (pp2 = 10 com
#     pp1 = 1) custa 8, menos da metade do maior S e bem abaixo de uma
#     colisão do PEN1. É o suficiente para o solver redistribuir os pares
#     (o pp2 forte vai para o dia do pp1 forte), mas não para abrir mão de
#     popularidade de verdade.
FOLGA_PEN2 = 1.0
PESO_PEN2 = 1.0

v_PEN2 = {}
for d, r in slots:
    v = m.addVar(lb=0.0, name=f"v_PEN2_{d}_{r}")
    m.addConstr(
        v >= quicksum(P[i] * x[i, r, d] for i in IPP2)
           - quicksum(P[i] * x[i, r, d] for i in IPP1)
           - FOLGA_PEN2,
        name=f"PEN2_{d}_{r}"
    )
    v_PEN2[d, r] = v
    penalidades.append(PESO_PEN2 * v)

print(f"PEN2: {len(v_PEN2)} termos (folga {FOLGA_PEN2}, peso {PESO_PEN2})")

# ---------------- PEN3: mesmo prato na mesma refeição, semana seguinte ----
#
# Pedido do grupo: variedade. Lasanha no almoço de uma terça e de novo no
# almoço da terça seguinte é o tipo de repetição que o aluno mais percebe.
# NÃO É REGRA DO EDITAL; ver DUVIDAS_EDITAL.md, item 9.
#
# POR QUE O PEN1 NÃO COBRE: ele age até ALCANCE_PEN slots (~2 dias), e a
# mesma refeição da semana seguinte fica a ~11 slots. As regras PP1/OP1 já
# impedem o mesmo item DUAS vezes na janela de 7 dias, mas d e d + 7 ficam
# em janelas diferentes, então essa repetição é permitida.
#
# FORMULAÇÃO: para cada item i de pp1 ou pp2 (prato EXATO, não preparo) e
# cada par (d, r), (d + 7, r) existente:
#
#     z >= x[i,r,d] + x[i,r,d+7] - 1,   z >= 0
#
# Mesmo raciocínio do PEN1: z só é forçada a 1 se o item aparece nos dois;
# a penalização é negativa no objetivo, então z fica em 0 nos demais casos.
#
# CALIBRAÇÃO ("leve"): PESO_PEN3 = 6, ~30% do maior S (~20) e ~1/4 de uma
# colisão adjacente do PEN1. Desempata entre pratos de score parecido, mas
# o solver ainda repete um prato muito popular quando a alternativa é cara.
PESO_PEN3 = 6.0

I_PEN3 = sorted(IPP1 | IPP2)

z_PEN3 = {}
for d in D:
    if d + 7 not in D:
        continue
    for r in R_ds(d):
        if r not in ("Almoco", "Janta") or r not in R_ds(d + 7):
            continue
        for i in I_PEN3:
            z = m.addVar(lb=0.0, name=f"z_PEN3_{i}_{d}_{r}".replace(" ", "-"))
            m.addConstr(
                z >= x[i, r, d] + x[i, r, d + 7] - 1,
                name=f"PEN3_{i}_{d}_{r}".replace(" ", "-")
            )
            z_PEN3[i, d, r] = z
            penalidades.append(PESO_PEN3 * z)

print(f"PEN3: {len(z_PEN3)} termos (peso {PESO_PEN3})")

# Objetivo: popularidade, mais o bônus de preparo casado (BON1), menos as
# colisões de preparo (PEN1) e as inversões pp2 > pp1 (PEN2).
m.setObjective(
    quicksum(
        S[i, r, d] * x[i, r, d]
        for d in D
        for r in R_ds(d)
        for i in I
    )
    + quicksum(bonus)
    - quicksum(penalidades),
    GRB.MAXIMIZE
)

# ------------------------ EXECUTAR ------------------------

m.optimize()

# ------------------------ VISUALIZAR ------------------------

dias_semana = [
    "Segunda", "Terça", "Quarta",
    "Quinta", "Sexta", "Sábado", "Domingo"
]

print("\n")
print("-------------------- CARDÁPIO --------------------")
print("\n")

for d in D:
    refeicoes = R_ds(d)
    if not refeicoes:
        continue

    print(f"Dia {d:02d} ({dias_semana[s(d)]}):")
    for r in refeicoes:
        escolhidos = [
            i for i in I
            if (i, r, d) in x
            and x[i, r, d].X > 0.5
        ]
        if escolhidos:
            # Mostra o score de cada item junto do nome, para auditar se o
            # cardápio está de fato concentrando os itens de P alto nos
            # slots de F alto (ver FUNÇÃO OBJETIVO). Saladas aparecem com
            # (0.0): é o peso neutro de CATEGORIAS_SEM_SCORE, não um bug.
            itens_com_score = ", ".join(
                f"{i} ({S[i, r, d]:.1f})" for i in escolhidos
            )
            print(f"  {r} (F={F[r][s(d)]:.2f}): {itens_com_score}")
        else:
            print(f"  {r}: (nenhum item selecionado)")

    print()

# ------------------------ RELATÓRIO VISUAL ------------------------

# Página HTML com o cardápio em calendário, para apresentar ao time (ver
# relatorio.py). Fica em otimizacao/results/, junto de um JSON com os mesmos
# dados, e abre sozinha no navegador. Para só gerar o arquivo, sem abrir,
# troque ABRIR_NO_NAVEGADOR para False.
ABRIR_NO_NAVEGADOR = True

STATUS_SOLVER = {
    GRB.OPTIMAL: "ótima",
    GRB.TIME_LIMIT: "interrompida (limite de tempo)",
    GRB.SUBOPTIMAL: "subótima",
}

if m.SolCount > 0:
    resultado = {
        "ano": ano,
        "mes": mes,
        "dias_no_mes": calendar.monthrange(ano, mes)[1],
        "primeiro_dia_semana": s(1),
        "solver": {
            "status": STATUS_SOLVER.get(m.Status, f"status {m.Status}"),
            "tempo_s": round(m.Runtime, 1),
            "objetivo": round(m.ObjVal, 1),
        },
        "parametros": {
            "PESO_PEN_BASE": PESO_PEN_BASE,
            "ALCANCE_PEN": ALCANCE_PEN,
            "PESO_BON1": PESO_BON1,
            "FOLGA_PEN2": FOLGA_PEN2,
            "PESO_PEN2": PESO_PEN2,
            "PESO_PEN3": PESO_PEN3,
        },
        "preparos_penalizados": PREPAROS,
        "dias": [
            {
                "dia": d,
                "dia_semana": s(d),
                "refeicoes": [
                    {
                        "refeicao": r,
                        "F": round(F[r][s(d)], 3),
                        "itens": [
                            {
                                "nome": i,
                                "categoria": Categoria[i],
                                "P": round(float(P[i]), 3),
                                "S": round(float(S[i, r, d]), 3),
                                # NaN na planilha = item sem preparo.
                                "preparo": Preparo[i] if isinstance(Preparo.get(i), str) else None,
                            }
                            for i in I
                            if x[i, r, d].X > 0.5
                        ],
                    }
                    for r in R_ds(d)
                ],
            }
            for d in D
            if R_ds(d)
        ],
    }

    caminho = gerar_relatorio(
        resultado, "otimizacao/results", abrir=ABRIR_NO_NAVEGADOR
    )
    print(f"Relatório salvo em {caminho}")
else:
    print("Sem solução factível: relatório não gerado.")
