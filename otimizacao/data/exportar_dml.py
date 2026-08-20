"""Roda o Double Machine Learning e exporta os coeficientes de popularidade em CSV.

Replica a logica do notebook previsao/notebooks/Double_Machine_Learning.ipynb,
que calcula os coeficientes mas so salva graficos (savefig) -- nunca exporta os
numeros. Este script fecha essa lacuna para alimentar a coluna P da planilha.

Requer o venv com doubleml: previsao/notebooks/venv/bin/python
Rodar da raiz:  previsao/notebooks/venv/bin/python otimizacao/data/exportar_dml.py area1
"""
from doubleml.plm import DoubleMLPLR
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

np.random.seed(42)
N_ESTIMATORS, N_FOLDS, RANDOM_STATE = 100, 5, 42
AREA = sys.argv[1] if len(sys.argv)>1 else 'area1'

CFG = {
 'area1': dict(csv='previsao/data/dataarea1.csv',
   onehot=['Mês','Dia_semana','Dia_mês','prato_principal_1','prato_principal_2','guarnição','sobremesa_1','refeicao'],
   rm_cafe=True, rm_erro=True, rm_zero=True, dropna=True),
 'area2': dict(csv='previsao/data/dataarea2.csv',
   onehot=['Mês','Dia_semana','Dia_mês','prato_principal_1','prato_principal_2','guarnição','sobremesa_1'],
   rm_cafe=False, rm_erro=False, rm_zero=False, dropna=False),
}[AREA]
Y='total'

data = pd.read_csv(CFG['csv'], header=0)
if CFG['rm_cafe']: data = data[data['refeicao']!='cafe da manha'].copy()
if CFG['rm_erro']: data = data[data['guarnição']!='Erro de leitura']
data = data[~((data['Ano']==2023)&(data['Mês']==10)&(data['Dia_mês']==11))]
if CFG['dropna']: data = data.dropna()
if CFG['rm_zero']: data = data[data[Y]!=0]
for c in ['guarnição','prato_principal_1','prato_principal_2','sobremesa_1']:
    data = data.groupby(c).filter(lambda x: len(x)>=5)
data = pd.get_dummies(data, columns=CFG['onehot'])
print(f'[{AREA}] shape apos preparo: {data.shape}', flush=True)

GROUPS = {'prato_principal_1_':'prato_principal_1','prato_principal_2_':'prato_principal_2',
          'guarnição_':'guarnição','sobremesa_1_':'sobremesa_1'}
rows=[]
for prefix, cat in GROUPS.items():
    d_cols=[c for c in data.columns if c.startswith(prefix)]
    x_cols=[c for c in data.columns if c not in d_cols+[Y]]
    print(f'  rodando {prefix} ({len(d_cols)} tratamentos)...', flush=True)
    dml = DoubleMLPLR(DoubleMLData(data, y_col=Y, d_cols=d_cols, x_cols=x_cols),
        ml_m=RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE),
        ml_l=RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE),
        n_folds=N_FOLDS)
    dml.fit()
    for nome, coef, se in zip(d_cols, dml.coef, dml.se):
        rows.append(dict(area=AREA, categoria=cat,
                         item_historico=nome[len(prefix):], coeficiente=coef, erro_padrao=se))

out=pd.DataFrame(rows).sort_values(['categoria','coeficiente'], ascending=[True,False])
dest=f'otimizacao/data/dml_coeficientes.csv' if AREA=='area1' else f'otimizacao/data/dml_coeficientes_{AREA}.csv'
out.to_csv(dest, index=False)
print(f'salvo: {dest}  ({len(out)} coeficientes)')
