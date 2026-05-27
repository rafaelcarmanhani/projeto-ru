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
    ("laranja", "Janta", -2): 1,

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
    ("mamão", "Almoco", -4): 1,

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
    ("caqui", "Almoco", -6): 1,

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

    if d < 1:
        return ["Desjejum", "Almoco", "Janta"]

    ds = s(d)

    if ds == 5:  # sábado
        return ["Desjejum", "Almoco"]

    elif ds == 6:  # domingo
        return []

    else:
        return ["Desjejum", "Almoco", "Janta"]


# Janela móvel de 7 dias
def janela7(d):
    return range(d - 6, d + 1)


# ------------------------ ORGANIZAR SUBCONJUNTOS ------------------------

P = dict(zip(df["item"], df["P"]))
Categoria = dict(zip(df["item"], df["categoria"]))
TipoCarne = dict(zip(df["item"], df["tipo_carne"]))
Embutido = dict(zip(df["item"], df["embutido"]))
Especificacao = dict(zip(df["item"], df["especificacao"]))

# Conjuntos
I = list(df["item"])

C = sorted(df["categoria"].unique())
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

# ---------------- PP4 ----------------

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

    # NÃO pode existir almoço e janta na mesma janela
    m.addConstr(
        almoco_embutido * janta_embutido == 0,
        name=f"PP4_PP5_{d}"
    )

# ---------------- PP6 ----------------

for d in D:

    if d + 1 <= max(D):

        for e in E:

            jantar_espec = quicksum(

                x[i, "Janta", d]

                for i in Ie[e]

                if (i, "Janta", d) in x

            )

            almoco_espec = quicksum(

                x[i, "Almoco", d + 1]

                for i in Ie[e]

                if (i, "Almoco", d + 1) in x

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