#Importar bibliotecas
import gurobipy as gp
from gurobipy import GRB
import calendar
from datetime import date
from gurobipy import quicksum
import pandas as pd

#------------------------CONFIGURAÇÕES INICIAIS------------------------

#Ler csv
df = pd.read_csv("itens_cardapio.csv", sep=";")

#Configurações iniciais
ano = 2026
mes = 1

#Definir os conjuntos
I = list(df["item"])
R = ["Almoco", "Janta"]
D = [d for d in range(1, calendar.monthrange(ano, mes)[1] + 1)]

#função que retorna o dia da semana
def s(d):
    return date(ano, mes, d).weekday()

#função que retorna as refeições em determinado dia
def R_ds(d):
    ds = s(d)

    if ds == 5: #sábado
        return ["Almoco"]
    elif ds == 6: #domingo
        return []
    else:
        return ["Almoco", "Janta"]
    
#------------------------ORGANIZAR SUBCONJUNTOS------------------------

#Parâmetros vindos da planilha
P = dict(zip(df["item"], df["P"]))
Categoria = dict(zip(df["item"], df["categoria"]))
TipoCarne = dict(zip(df["item"], df["tipo_carne"]))
Embutido = dict(zip(df["item"], df["embutido"]))

#Conjunto C
C = sorted(df["categoria"].unique())
print("Categorias:", C)

#Subconjuntos Ic
Ic = {c: [] for c in C}
for i in I:
    Ic[Categoria[i]].append(i)

#Subconjuntos especiais
IBranca   = [i for i in I if TipoCarne[i] == "branca"]
IVermelha = [i for i in I if TipoCarne[i] == "vermelha"]
IEmbutido = [i for i in I if Embutido[i] == 1]

#------------------------VARIÁVEIS------------------------

#Criar modelo
m = gp.Model()    

#Criar variáveis
x = {}
for d in D:
    for r in R_ds(d):
        for i in I:
            x[i, r, d] = m.addVar(
                vtype=GRB.BINARY,
                name=f"x_{i}_{r}_{d}"
            )

m.update()

#Vizualizar
print(len(x)) #número de variáveis

#------------------------RESTRIÇÕES------------------------

#ESTRUTURA 1
for d in D:
    for r in R_ds(d):
        for c in C:
            itens_cat = [i for i in Ic[c] if (i, r, d) in x]
            if not itens_cat:
                continue 

            m.addConstr(
                quicksum(x[i, r, d] for i in itens_cat) == 1,
                name=f"cat_{c}_{r}_{d}"
            )


#PRATO PRINCIPAL 1
for i in Ic["prato_principal_1"]:
    for d in range(1, len(D) - 5):  
        janela_dias = range(d, d + 7)

        m.addConstr(
            quicksum(
                x[i, r, t]
                for t in janela_dias
                for r in R_ds(t)
                if (i, r, t) in x
            ) <= 1,
            name=f"no_repeat7_{i}_{d}"
        )

#------------------------FUNÇÃO OBJETIVO------------------------

#Score temporal por refeição e dia da semana
F = {
    "Almoco": [1.0, 1.0, 1.0, 1.1, 1.2, 1.1, 0.0],
    "Janta":  [0.9, 1.0, 1.0, 1.0, 1.1, 0.0, 0.0]
}

#Score de Preferência
S = {}

for d in D:
    for r in R_ds(d):
        for i in I:
            S[i, r, d] = P[i] * F[r][s(d)]

#Função objetivo
m.setObjective(
    quicksum(S[i, r, d] * x[i, r, d]
             for d in D
             for r in R_ds(d)
             for i in I),
    GRB.MAXIMIZE
)

#Executar
m.optimize()

#Vizualizar

dias_semana = [
    "Segunda", "Terça", "Quarta",
    "Quinta", "Sexta", "Sábado", "Domingo"
]

print("\n")
print("--------------------CARDÁPIO--------------------")
print("\n")

for d in D:
    refeicoes = R_ds(d)
    if not refeicoes:
        continue

    print(f"Dia {d:02d} ({dias_semana[s(d)]}):")
    for r in refeicoes:
        escolhidos = [
            i for i in I
            if (i, r, d) in x and x[i, r, d].X > 0.5
        ]

        if escolhidos:
            print(f"  {r}: {', '.join(escolhidos)}")
        else:
            print(f"  {r}: (nenhum item selecionado)")
    print()
