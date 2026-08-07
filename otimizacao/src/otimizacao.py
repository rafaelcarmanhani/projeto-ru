# ------------------------ IMPORTAR BIBLIOTECAS ------------------------

import gurobipy as gp
from gurobipy import GRB, quicksum
import pandas as pd
import calendar
from datetime import date

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

    ("alface", "Almoco", -1): 1,
    ("beterraba", "Almoco", -1): 1,
    ("grao de bico", "Almoco", -1): 1,
    ("pernil ao molho", "Almoco", -1): 1,
    ("quibe de pvt", "Almoco", -1): 1,
    ("macarrão", "Almoco", -1): 1,
    ("delicia de abacaxi", "Almoco", -1): 1,
    ("mamão", "Almoco", -1): 1,

    ("alface", "Janta", -1): 1,
    ("beterraba", "Janta", -1): 1,
    ("grao de bico", "Janta", -1): 1,
    ("filé de frango ao molho", "Janta", -1): 1,
    ("hambúrguer de lentilha", "Janta", -1): 1,
    ("couve", "Janta", -1): 1,
    ("banoffe", "Janta", -1): 1,
    ("laranja", "Janta", -1): 1,

    # ---------------- DIA -2 ----------------

    ("maçã", "Desjejum", -2): 1,

    ("alface", "Almoco", -2): 1,
    ("beterraba", "Almoco", -2): 1,
    ("grao de bico", "Almoco", -2): 1,
    ("panqueca de carne", "Almoco", -2): 1,
    ("lasanha de queijo", "Almoco", -2): 1,
    ("purê de batata", "Almoco", -2): 1,
    ("flan de morango", "Almoco", -2): 1,
    ("melão", "Almoco", -2): 1,

    ("alface", "Janta", -2): 1,
    ("beterraba", "Janta", -2): 1,
    ("grao de bico", "Janta", -2): 1,
    ("coxa de frango assada", "Janta", -2): 1,
    ("lasanha de abobrinha", "Janta", -2): 1,
    ("purê de mandioquinha", "Janta", -2): 1,
    ("delicia de banana", "Janta", -2): 1,
    ("banana", "Janta", -2): 1,

    # ---------------- DIA -3 ----------------

    ("mamão", "Desjejum", -3): 1,

    ("alface", "Almoco", -3): 1,
    ("beterraba", "Almoco", -3): 1,
    ("grao de bico", "Almoco", -3): 1,
    ("quibe", "Almoco", -3): 1,
    ("almôndega de aveia", "Almoco", -3): 1,
    ("mandioca", "Almoco", -3): 1,
    ("pudim crocante", "Almoco", -3): 1,
    ("caqui", "Almoco", -3): 1,

    ("alface", "Janta", -3): 1,
    ("beterraba", "Janta", -3): 1,
    ("grao de bico", "Janta", -3): 1,
    ("iscas de frango", "Janta", -3): 1,
    ("curry de legumes", "Janta", -3): 1,
    ("ervilha parmentier", "Janta", -3): 1,
    ("pavê de bombom", "Janta", -3): 1,
    ("melão", "Janta", -3): 1,

    # ---------------- DIA -4 ----------------

    ("melancia", "Desjejum", -4): 1,

    ("alface", "Almoco", -4): 1,
    ("beterraba", "Almoco", -4): 1,
    ("grao de bico", "Almoco", -4): 1,
    ("estrogonofe de carne", "Almoco", -4): 1,
    ("bife de grão de bico", "Almoco", -4): 1,
    ("virado de couve", "Almoco", -4): 1,
    ("alfajor", "Almoco", -4): 1,
    ("goiaba", "Almoco", -4): 1,

    ("alface", "Janta", -4): 1,
    ("beterraba", "Janta", -4): 1,
    ("grao de bico", "Janta", -4): 1,
    ("frango empanado", "Janta", -4): 1,
    ("omelete", "Janta", -4): 1,
    ("acelga", "Janta", -4): 1,
    ("rocambole de chocolate", "Janta", -4): 1,
    ("tangerina", "Janta", -4): 1,

    # ---------------- DIA -6 ----------------

    ("goiaba", "Desjejum", -6): 1,

    ("alface", "Almoco", -6): 1,
    ("beterraba", "Almoco", -6): 1,
    ("grao de bico", "Almoco", -6): 1,
    ("carne moída", "Almoco", -6): 1,
    ("hambúrguer de pvt", "Almoco", -6): 1,
    ("batata doce", "Almoco", -6): 1,
    ("doce de goiabada", "Almoco", -6): 1,
    ("abacaxi", "Almoco", -6): 1,

    # ---------------- DIA 7 ----------------

    ("caqui", "Desjejum", -7): 1,

    ("alface", "Almoco", -7): 1,
    ("beterraba", "Almoco", -7): 1,
    ("grao de bico", "Almoco", -7): 1,
    ("peixe ao molho", "Almoco", -7): 1,
    ("estrogonofe de pvt", "Almoco", -7): 1,
    ("cenoura", "Almoco", -7): 1,
    ("mousse de chocolate", "Almoco", -7): 1,
    ("melancia", "Almoco", -7): 1,

    ("alface", "Janta", -7): 1,
    ("beterraba", "Janta", -7): 1,
    ("grao de bico", "Janta", -7): 1,
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

# Saladas fora de escopo: não aparecem no cardápio publicado do RU e não existem
# em nenhuma fonte de dados do projeto (o scrape histórico não tem coluna de
# salada; chicória e almeirão não aparecem em lugar nenhum). A planilha tem
# apenas 1 item placeholder por categoria de salada.
#
# É obrigatório filtrar aqui: E1 exige exatamente 1 item de CADA categoria em
# cada refeição, então sem esse filtro os 3 placeholders (alface, beterraba,
# grao de bico) seriam forçados em todas as refeições do mês.
#
# Para reativar as saladas no futuro: esvaziar esta lista e popular a planilha
# (ver bloco RESTRIÇÕES AINDA A FAZER no fim do arquivo).
CATEGORIAS_IGNORADAS = ["salada_1", "salada_2", "salada_3"]

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

# Falha cedo se os atributos novos vierem vazios: sem isso, as restrições que
# dependem deles seriam construídas sem nenhum termo e não teriam efeito algum,
# silenciosamente.
if not IFritura:
    raise SystemExit("IFritura vazio: conferir a coluna 'fritura' da planilha")
if not IOvos:
    raise SystemExit("IOvos vazio: conferir a coluna 'a_base_de_ovos' da planilha")

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

# ---------------- PP2 ----------------

for d in D:
    refeicoes = R_ds(d)
    if "Almoco" in refeicoes and "Janta" in refeicoes:
        m.addConstr(
            quicksum(
                x[i, "Almoco", d]
                for i in IBranca
            )
            ==
            quicksum(
                x[i, "Janta", d]
                for i in IVermelha
            ),
            name=f"PP2_{d}"
        )

# ---------------- PP3 ----------------

for d in D:
    refeicoes = R_ds(d)
    if "Almoco" in refeicoes and "Janta" in refeicoes:
        m.addConstr(
            quicksum(
                x[i, "Almoco", d]
                for i in IVermelha
            )
            ==
            quicksum(
                x[i, "Janta", d]
                for i in IBranca
            ),
            name=f"PP3_{d}"
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

# ======================================================================
#                        RESTRIÇÕES AINDA A FAZER
# ======================================================================
#
# Estado atual: implementadas E1-E3, PP1-PP6, OP1-OP4, G1, SO1-SO4,
# O2, O3. O que falta está bloqueado por DADOS que não existem, não por
# dificuldade de modelagem.
#
# ----------------------------------------------------------------------
# BLOCO 1 - SALADAS: fora de escopo por decisão do projeto
# ----------------------------------------------------------------------
#
# As saladas não aparecem no cardápio publicado do RU e não existem em
# nenhuma fonte de dados: o scrape histórico (previsao/.../cardapio.txt e
# dataarea1.csv) não tem coluna de salada, e "chicória"/"almeirão" não
# aparecem em lugar nenhum do repositório. A planilha tem apenas 1 item
# placeholder por categoria.
#
# Por isso salada_1/2/3 estão em CATEGORIAS_IGNORADAS (topo do arquivo) e
# as restrições abaixo NÃO foram implementadas:
#
#   (1S1) Salada 1 não repete em 7 dias, exceto alface, chicória, almeirão.
#   (1S2) Alface: até 2x por semana no almoço.
#   (1S3) Alface: até 2x por semana no jantar.
#         (OBS R2 do relatório: no texto original as duas diziam "almoço";
#          o edital 5.21.2 confirma 2x almoço e 2x jantar.)
#   (2S1) Salada 2 não repete em 7 dias.
#   (3S1) Salada 3 não repete em 7 dias.
#   (3S2) Grão em conserva: até 2x por semana no almoço.  [+ coluna
#   (3S3) Grão em conserva: até 2x por semana no jantar.   grao_em_conserva]
#
#   (FF1) Chicória: exatamente 1x no almoço por semana.
#   (FF2) Chicória: exatamente 1x no jantar por semana.
#   (FF3) Almeirão: exatamente 1x no almoço por semana.
#   (FF4) Salada com creme de maionese: 2x no almoço por mês. [+ coluna
#   (FF5) Salada com creme de maionese: 2x no jantar por mês.  creme_maionese]
#
# PARA REATIVAR: esvaziar CATEGORIAS_IGNORADAS e popular a planilha com os
# itens de salada do edital (mínimo ~7 por categoria; com menos que isso as
# restrições de não-repetição em 7 dias ficam INFACTÍVEIS, porque E1 exige
# 1 item de cada categoria em cada refeição).
#
# ATENÇÃO nas FF: usar Dw / W_completas (já implementados no topo do
# arquivo), NÃO janela7. São igualdades, e numa semana truncada da borda do
# mês (ex.: maio/2026 começa numa sexta) uma igualdade "1x por semana" é
# infactível.
#
#   (O1) O vegetal da salada não pode repetir na guarnição do mesmo dia.
#        Depende de salada + de um atributo de vegetal. Hoje as guarnições
#        têm "composicao" (vegetal A folhoso / vegetal C / não folhoso),
#        granularidade grossa demais: proibiria qualquer folhoso junto de
#        qualquer folhoso. Precisa de um atributo mais fino, ou reusar
#        "produto", que já foi preenchido nas guarnições para O2.
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
#   (FF3) O edital 5.21.2.3 prevê chicória E almeirão 1x no almoço e 1x no
#         jantar, cada um. A lista do relatório tem só almeirão no almoço
#         (OBS R4). Confirmar se é intencional.
#
#   Restrições não oficiais mencionadas no relatório, ainda sem modelagem:
#         "segunda a sobremesa é sempre algo já pronto"
#         "estrogonofe geralmente vem com batata palha"
#
#   Fator de aleatoriedade no score de preferência para dar variabilidade
#   entre meses (subseção 4.1 do relatório, a testar).
#
# ----------------------------------------------------------------------
# BLOCO 3 - PENDÊNCIA CRÍTICA: a função objetivo está achatada
# ----------------------------------------------------------------------
#
# A coluna P vale 1.0 para TODOS os itens da planilha. Como o objetivo é
# maximizar sum(P[i] * F[r][s(d)] * x), o modelo hoje não tem preferência
# real entre itens: qualquer cardápio factível é ótimo, e o que sai é
# arbitrário dentro do espaço factível.
#
# O notebook previsao/notebooks/Double_Machine_Learning.ipynb calcula os
# coeficientes de popularidade (theta do DML), mas só faz savefig dos
# gráficos: nunca exporta os valores (não há to_csv nem to_excel). Por isso
# eles nunca chegaram na planilha.
#
# ENQUANTO ISSO NÃO FOR RESOLVIDO, não faz sentido avaliar se o cardápio
# gerado "está bom": o resultado não reflete preferência nenhuma.
#
# O DML só produz P para 4 categorias (pp1, pp2, guarnição, sobremesa_1).
# Sobremesa_2 (frutas) e saladas precisariam de outra fonte de score.
#
# ----------------------------------------------------------------------
# BLOCO 4 - limitação de ambiente
# ----------------------------------------------------------------------
#
# A licença Gurobi da .venv é size-limited e recusa este modelo (~11 mil
# variáveis), inclusive com o horizonte reduzido a poucos dias. Dá para
# CONSTRUIR o modelo e inspecionar as restrições, mas não para resolvê-lo.
# Validar factibilidade exige licença acadêmica completa.
# Se der infactível, usar m.computeIIS() + m.write("modelo.ilp").
#
# ======================================================================

# ------------------------ FUNÇÃO OBJETIVO ------------------------

F = {
    "Desjejum": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
    "Almoco":   [1.0, 1.0, 1.0, 1.1, 1.2, 1.1, 0.0],
    "Janta":    [0.9, 1.0, 1.0, 1.0, 1.1, 0.0, 0.0]
}

S = {}
for d in D:
    for r in R_ds(d):
        for i in I:
            S[i, r, d] = P[i] * F[r][s(d)]

# Objetivo
m.setObjective(
    quicksum(
        S[i, r, d] * x[i, r, d]
        for d in D
        for r in R_ds(d)
        for i in I
    ),
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
            print(f"  {r}: {', '.join(escolhidos)}")
        else:
            print(f"  {r}: (nenhum item selecionado)")

    print()
