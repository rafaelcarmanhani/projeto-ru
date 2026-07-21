"""
Gera o arquivo calendario.csv usado pelo pipeline de tratamento de dados.
"""

from pathlib import Path

from calendario_utils import gerar_calendario

# Caminho de saída construído com pathlib (portátil entre Windows/Linux/Mac,
# ao contrário da string com barras invertidas usada anteriormente, que só
# "funcionava" porque nenhuma das sequências de escape era válida).
#
# Usa __file__ como referência em vez de um caminho relativo ao diretório de
# execução, para que o resultado não dependa de onde o comando
# `python automacao_calendario.py` é chamado. Este script e
# calendario_utils.py ficam na mesma pasta (data_treatment_completo/), então
# o CSV é salvo ali também — no mesmo nível dos demais dados brutos lidos
# pelo Tratamento_dos_dados.ipynb.
OUTPUT_PATH = Path(__file__).resolve().parent / "calendario.csv"

if __name__ == "__main__":
    df = gerar_calendario()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Calendário salvo em: {OUTPUT_PATH.resolve()} ({len(df)} linhas)")
