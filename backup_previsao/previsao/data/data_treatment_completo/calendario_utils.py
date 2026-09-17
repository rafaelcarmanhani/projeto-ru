"""
Geração do calendário letivo (feriados, férias, dias letivos e variáveis
derivadas de proximidade).
"""

from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Definições de feriados e férias.
# Cada item pode ser uma data única (str) ou um intervalo (tupla de duas str).
# ---------------------------------------------------------------------------

FERIADOS: list[str | tuple[str, str]] = [
    ("2023-04-03", "2023-04-08"),  # semana santa
    ("2023-04-21", "2023-04-22"),  # tiradentes
    "2023-05-01",  # dia do trabalho
    ("2023-06-08", "2023-06-10"),  # corpus christi
    ("2023-08-14", "2023-08-15"),  # feriado municipal
    ("2023-09-04", "2023-09-09"),  # semana da pátria
    ("2023-10-12", "2023-10-14"),  # dia da padroeira do Brasil
    "2023-10-28",  # consagração ao funcionário público
    ("2023-11-02", "2023-11-04"),  # finados
    "2023-11-15",  # proclamação da república

    ("2024-03-25", "2024-03-30"),  # semana santa
    "2024-05-01",  # dia do trabalho
    ("2024-05-30", "2024-06-01"),  # corpus christi
    ("2024-08-15", "2024-08-17"),  # feriado municipal
    ("2024-09-02", "2024-09-07"),  # semana da pátria
    "2024-10-12",  # dia da padroeira do Brasil
    "2024-10-28",  # consagração ao funcionário público
    "2024-11-02",  # finados
    "2024-11-04",  # feriado municipal
    ("2024-11-15", "2024-11-16"),  # proclamação da república
    "2024-11-20",  # dia da consciência negra

    ("2025-03-03", "2025-03-05"),  # carnaval + quarta-feira de cinzas
    ("2025-04-14", "2025-04-19"),  # semana santa
    "2025-04-21",  # tiradentes
    ("2025-05-01", "2025-05-03"),  # dia do trabalho
    ("2025-06-19", "2025-06-21"),  # corpus christi
    ("2025-08-15", "2025-08-16"),  # feriado municipal
    ("2025-09-01", "2025-09-06"),  # semana da pátria
    ("2025-10-27", "2025-10-28"),  # consagração ao funcionário público
    ("2025-11-03", "2025-11-04"),  # feriado municipal
    "2025-11-15",  # proclamação da república
    ("2025-11-20", "2025-11-22"),  # dia da consciência negra
]

FERIAS: list[tuple[str, str]] = [
    ("2023-01-01", "2023-03-12"),
    ("2023-07-15", "2023-08-06"),
    ("2023-12-21", "2024-02-25"),
    ("2024-07-02", "2024-08-04"),
    ("2024-12-12", "2025-02-23"),
    ("2025-07-07", "2025-08-03"),
    ("2025-12-12", "2025-12-31"),
]

_DIA_SEMANA_MAP = {0: "seg", 1: "ter", 2: "qua", 3: "qui", 4: "sex", 5: "sáb", 6: "dom"}


def gerar_calendario(
    data_inicio: str = "2023-01-01",
    data_fim: str = "2025-12-31",
    feriados: list | None = None,
    ferias: list | None = None,
) -> pd.DataFrame:
    """
    Gera o calendário diário com as colunas:
    Ano, Mês, Dia_mês, Dia_semana, letivo, feriado, ferias,
    vespera_nao_letivo, pos_nao_letivo, vespera_feriado, pos_feriado,
    dias_desde_inicio_ferias, dias_desde_ultimas_ferias,
    dias_ate_ferias, dias_ate_feriado.

    `Mês` e `Dia_mês` são retornados como int (ver observação sobre tipos
    no notebook de tratamento: a padronização de tipo é feita uma única vez
    aqui para evitar divergências quando o calendário é unido a outras
    tabelas ou usado para prever novas observações).
    """
    feriados = FERIADOS if feriados is None else feriados
    ferias = FERIAS if ferias is None else ferias

    df = pd.DataFrame({"data": pd.date_range(start=data_inicio, end=data_fim)})

    df["Ano"] = df["data"].dt.year
    df["Mês"] = df["data"].dt.month
    df["Dia_mês"] = df["data"].dt.day
    df["_dia_semana_num"] = df["data"].dt.weekday  # 0=segunda ... 6=domingo

    # Segunda (0) a sábado (5) = letivo, domingo (6) = não letivo
    df["letivo"] = df["_dia_semana_num"] != 6

    # --- Feriados ---
    df["feriado"] = False
    for f in feriados:
        if isinstance(f, tuple):
            inicio, fim = f
            df.loc[df["data"].between(inicio, fim), "feriado"] = True
        else:
            df.loc[df["data"] == f, "feriado"] = True

    # --- Férias ---
    df["ferias"] = False
    for inicio, fim in ferias:
        mask = (df["data"] >= inicio) & (df["data"] <= fim)
        df.loc[mask, "ferias"] = True

    # Feriado ou férias => não letivo
    df.loc[df["feriado"] | df["ferias"], "letivo"] = False

    df["Dia_semana"] = df["_dia_semana_num"].map(_DIA_SEMANA_MAP)
    df = df.drop(columns=["_dia_semana_num"])

    df["letivo"] = df["letivo"].astype(int)
    df["feriado"] = df["feriado"].astype(int)
    df["ferias"] = df["ferias"].astype(int)

    # --- Variáveis derivadas de proximidade (vésperas, pós, contagens) ---
    df = df.sort_values("data").reset_index(drop=True)

    df["vespera_nao_letivo"] = (df["letivo"].shift(-1) == 0).astype(int)
    df["pos_nao_letivo"] = (df["letivo"].shift(1) == 0).astype(int)
    df["vespera_feriado"] = (df["feriado"].shift(-1) == 1).astype(int)
    df["pos_feriado"] = (df["feriado"].shift(1) == 1).astype(int)

    inicio_ferias_mask = (df["ferias"] == 1) & (df["ferias"].shift(1, fill_value=0) == 0)
    retorno_aulas_mask = (df["ferias"] == 0) & (df["ferias"].shift(1) == 1)

    df["_dt_start_current"] = df.where(inicio_ferias_mask)["data"].ffill()
    df["dias_desde_inicio_ferias"] = (
        (df["data"] - df["_dt_start_current"]).dt.days.fillna(0).astype(int)
    )
    df.loc[df["ferias"] == 0, "dias_desde_inicio_ferias"] = 0

    df["_dt_last_end"] = df.where(retorno_aulas_mask)["data"].ffill()
    df["dias_desde_ultimas_ferias"] = (
        (df["data"] - df["_dt_last_end"]).dt.days.fillna(0).astype(int)
    )
    df.loc[df["ferias"] == 1, "dias_desde_ultimas_ferias"] = 0

    df["_dt_next_start"] = df.where(inicio_ferias_mask)["data"].bfill()
    df["dias_ate_ferias"] = (
        (df["_dt_next_start"] - df["data"]).dt.days.fillna(0).astype(int)
    )
    df.loc[df["ferias"] == 1, "dias_ate_ferias"] = 0

    inicio_feriado_mask = (df["feriado"] == 1) & (df["feriado"].shift(1, fill_value=0) == 0)
    df["_dt_next_feriado"] = df.where(inicio_feriado_mask)["data"].bfill()
    df["dias_ate_feriado"] = (
        (df["_dt_next_feriado"] - df["data"]).dt.days.fillna(0).astype(int)
    )
    df.loc[df["feriado"] == 1, "dias_ate_feriado"] = 0

    df = df.drop(columns=[
        "_dt_start_current", "_dt_last_end", "_dt_next_start", "_dt_next_feriado",
    ])

    df = df.drop(columns=["data"])

    colunas_ordenadas = [
        "Ano", "Mês", "Dia_mês", "Dia_semana", "letivo", "feriado", "ferias",
        "vespera_nao_letivo", "pos_nao_letivo", "vespera_feriado", "pos_feriado",
        "dias_desde_inicio_ferias", "dias_desde_ultimas_ferias",
        "dias_ate_ferias", "dias_ate_feriado",
    ]
    return df[colunas_ordenadas]
