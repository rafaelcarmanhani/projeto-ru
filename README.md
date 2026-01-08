# Projeto RU USP São Carlos
Projeto de previsão e otimização do restaurante universitário da USP de São Carlos

## Estrutura do repositório

```text
projeto-ru/
├── previsao/             # Módulo de Previsão (Python)
│   ├── data/             # Datasets brutos e processados
│   ├── notebooks/        # Notebooks para exploração e treino
│   ├── scripts/          # Scripts de treino e inferência (.py)
│   └── requirements.txt  # Dependências (pandas, scikit-learn, etc)
│
├── otimizacao/           # Módulo de Otimização (Python + Gurobi)
│   ├── data/             # CSVs de entrada (itens_cardapio.csv)
│   ├── src/              # Código fonte do modelo (gurobi_codigo.py)
│   ├── results/          # Saídas geradas (cardapios_otimizados.json)
│   └── requirements.txt  # Dependências (gurobipy, pandas)
│
├── interface/            # Interface
│   ├── backend/          # API Express
│   └── frontend/         # App React
│
├── .gitignore            # Arquivos para o Git ignorar
└── README.md             # Documentação principal do projeto
