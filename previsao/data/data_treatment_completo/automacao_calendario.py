import pandas as pd

#Criar calendário
df = pd.DataFrame({
    'data': pd.date_range(start='2023-01-01', end='2025-12-31')
})

#Extrair informações de data
df['Ano'] = df['data'].dt.year
df['Mês'] = df['data'].dt.month
df['Dia_mês'] = df['data'].dt.day
df['Dia_semana'] = df['data'].dt.weekday  # 0=segunda, ..., 6=domingo

#Segunda (0) a sábado (5) = letivo, domingo (6) = não letivo
df['letivo'] = df['Dia_semana'] != 6 

#Definir feriados
feriados = [
    ('2023-04-03', '2023-04-08'), #semana santa
    ('2023-04-21', '2023-04-22'), #tiradentes
    '2023-05-01', #dia do trabalho
    ('2023-06-08', '2023-06-10'), #corpus christi
    ('2023-08-14','2023-08-15'), #feriado municipal
    ('2023-09-04', '2023-09-09'), #semana da pátria
    ('2023-10-12', '2023-10-14'), #dia da padroeira do Brasil
    '2023-10-28', #consagração ao funcionário público
    ('2023-11-02', '2023-11-04'), #finados
    '2023-11-15', #proclamação da república

    ('2024-03-25', '2024-03-30'), #semana santa
    '2024-05-01', #dia do trabalho
    ('2024-05-30', '2024-06-01'), #corpus christi
    ('2024-08-15','2024-08-17'), #feriado municipal
    ('2024-09-02', '2024-09-07'), #semana da pátria
    '2024-10-12', #dia da padroeira do Brasil
    '2024-10-28', #consagração ao funcionário público
    '2024-11-02', #finados
    '2024-11-04', #feriado municipal
    ('2024-11-15', '2024-11-16'), #proclamação da república
    '2024-11-20', #dia da consciência negra

    ('2025-03-03', '2025-03-05'), #carnaval + quarta feira de cinzas
    ('2025-04-14', '2025-04-19'), #semana santa
    '2025-04-21', #tiradentes
    ('2025-05-01', '2025-05-03'), #dia do trabalho
    ('2025-06-19', '2025-06-21'), #corpus christi
    ('2025-08-15', '2025-08-16'), #feriado municipal
    ('2025-09-01', '2025-09-06'), #semana da pátria
    ('2025-10-27', '2025-10-28'), #consagração ao funcionário público
    ('2025-11-03', '2025-11-04'), #feriado municipal
    '2025-11-15', #proclamação da república
    ('2025-11-20', '2025-11-22') #dia da consciência negra
]

df['feriado'] = False

for f in feriados:
    if isinstance(f, tuple):  # intervalo
        inicio, fim = f
        df.loc[df['data'].between(inicio, fim), 'feriado'] = True
    else:  # data única
        df.loc[df['data'] == f, 'feriado'] = True

#Definir férias (intervalos)
ferias = [
    ('2023-01-01', '2023-03-12'),
    ('2023-07-15', '2023-08-06'),

    ('2023-12-21', '2024-02-25'),
    ('2024-07-02', '2024-08-04'),

    ('2024-12-12', '2025-02-23'),
    ('2025-07-07', '2025-08-03'),
    ('2025-12-12','2025-12-31')
]

df['ferias'] = False
for inicio, fim in ferias:
    mask = (df['data'] >= inicio) & (df['data'] <= fim)
    df.loc[mask, 'ferias'] = True

# feriado ou férias NÃO são letivos
df.loc[df['feriado'] | df['ferias'], 'letivo'] = False

df['Dia_semana'] = df['Dia_semana'].map({
    0: 'seg',
    1: 'ter',
    2: 'qua',
    3: 'qui',
    4: 'sex',
    5: 'sáb',
    6: 'dom'
})

df['letivo'] = df['letivo'].astype(int)
df['feriado'] = df['feriado'].astype(int)
df['ferias'] = df['ferias'].astype(int)

df = df.drop(columns=['data'])

df.to_csv('previsao\data\data_treatment_completo\dados_brutos\calendario.csv', index=False)