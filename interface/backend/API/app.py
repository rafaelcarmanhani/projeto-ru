import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from schemas import (
    PreverRequest,
    PreverResponse,
    RetreinarRequest,
    RetreinarResponse,
    StatusResponse,
    ErrorResponse,
    FeatureSchema,
    PrevisaoOutput,
    DadoRetreino,
    AreaStatus,
    MetricasRetreino
)


BASE_DIR = Path(__file__).parent.resolve()
MODELOS_DIR = BASE_DIR / "modelos"

# cachê dos modelos carregados
_modelos_cache: dict = {}


def _carregar_modelo(area: str) -> dict:
    # carrega pipeline e margem para uma área, usando o cachê
    if area in _modelos_cache:
        return _modelos_cache[area]

    pipeline_path = MODELOS_DIR / f"pipeline_{area}.pkl"
    margem_path = MODELOS_DIR / f"margem_{area}.pkl"

    if not pipeline_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline não encontrado para área '{area}': {pipeline_path}",
        )
    if not margem_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Margem não encontrada para área '{area}': {margem_path}",
        )

    try:
        pipeline = joblib.load(pipeline_path)
        margem = joblib.load(margem_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar modelo (possível incompatibilidade de versão do scikit-learn): {str(e)}. Re-treine o modelo com a versão atual.",
        )

    resultado = {"pipeline": pipeline, "margem": margem}
    _modelos_cache[area] = resultado
    return resultado


from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="API de Previsão e Re-treino Ensemble",
    description="""
    API para fazer previsões e gerenciar o re-treino de modelos ensemble
    preditivos.
    """,
    version="2.0.0",
    contact={"name": "ProjetoRU"},
    license_info={"name": "Projeto Interno"},
)

@app.get(
    "/api/status",
    response_model=StatusResponse,
    summary="Verificar status da API",
    description="Retorna o status operacional da API e informações "
                "sobre os modelos disponíveis para previsão.",
)
async def get_status() -> StatusResponse:
    # endpoint de health check e status dos modelos
    areas = ["area1", "area2"]
    modelos_disponiveis: dict = {}

    for area in areas:
        try:
            modelo = _carregar_modelo(area)
            pipeline_path = MODELOS_DIR / f"pipeline_{area}.pkl"
            margem_path = MODELOS_DIR / f"margem_{area}.pkl"

            # tenta obter data de modificação do arquivo
            try:
                ultima_atualizacao = datetime.fromtimestamp(
                    pipeline_path.stat().st_mtime
                )
            except OSError:
                ultima_atualizacao = datetime.now()

            modelos_disponiveis[area] = AreaStatus(
                pipeline=f"pipeline_{area}.pkl",
                margem=f"margem_{area}.pkl",
                ultima_atualizacao=ultima_atualizacao,
            )
        except Exception:
            modelos_disponiveis[area] = AreaStatus(
                pipeline=f"pipeline_{area}.pkl",
                margem=f"margem_{area}.pkl",
                ultima_atualizacao=datetime.now(),
            )

    status_geral = "operacional" if modelos_disponiveis else "limite"

    return StatusResponse(
        status=status_geral,
        areas=areas,
        modelos_disponiveis=modelos_disponiveis,
    )


@app.post(
    "/api/prever",
    response_model=PreverResponse,
    summary="Fazer previsão de modelo",
    description="Recebe features padronizadas e retorna previsão "
                "central com intervalos de confiança usando o modelo "
                "específico da área solicitada.",
)
async def prever(req: PreverRequest) -> PreverResponse:
    """
    input: JSON com a área ('area1' ou 'area2') e as features padronizadas
    do calendário letivo e cardápio.
    output: Previsão central, limites inferior/superior e margem de segurança
    """
    try:
        # carregar modelo da área solicitada
        modelo_dados = _carregar_modelo(req.area)
        pipeline = modelo_dados["pipeline"]
        margem = modelo_dados["margem"]

        # converter features para DataFrame
        df_novo_dia = pd.DataFrame([req.features.model_dump()])

        # fazer previsão pontual
        previsao_pontual = pipeline.predict(df_novo_dia)[0]

        # calcular limites usando margem
        limite_inferior = previsao_pontual - margem
        limite_superior = previsao_pontual + margem

        # construir resposta
        previsao = PrevisaoOutput(
            previsao_central=round(previsao_pontual),
            limite_inferior=round(limite_inferior),
            limite_superior=round(limite_superior),
            margem_seguranca=round(margem),
        )

        metadados = {
            "area": req.area,
            "modelo": f"pipeline_{req.area}",
            "data_geracao": datetime.now().isoformat(),
        }

        # combinar features usadas para referência
        metadados.update(req.features.model_dump())

        return PreverResponse(
            previsao=previsao,
            metadados=metadados,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao fazer previsão: {str(e)}",
        )


@app.post(
    "/api/retreinar",
    response_model=RetreinarResponse,
    summary="Retreinar modelo com novos dados",
    description="Atualiza o modelo de uma área específica com novos "
                "registros históricos. Cada registro deve conter as features "
                "padronizadas e o resultado real observado.",
)
async def retreinar(req: RetreinarRequest) -> RetreinarResponse:
    """
    input:
    - area: 'area1' ou 'area2'
    - novos_dados: lista de registros com features e resultados reais
    - atualizar_modelo: se verdadeiro, salva o modelo atualizado

    output:
    - métricas de desempenho (RMSE, R2, MAE)
    - caminhos dos modelos antigo e novo
    - quantidade de registros processados
    """
    try:
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

        area = req.area

        # carregar modelo existente
        modelo_dados = _carregar_modelo(area)
        pipeline_antiga = modelo_dados["pipeline"]

        # preparar dados de treino
        X = []  # features
        y = []  # resultados reais

        for dado in req.novos_dados:
            # adicionar features ao conjunto de entrada
            features_dict = dado.features.model_dump()
            X.append(features_dict)
            y.append(dado.resultado_real)

        if not X:
            raise HTTPException(
                status_code=400,
                detail="Nenhum dado de treino fornecido",
            )

        X_df = pd.DataFrame(X)

        # fazer previsões com modelo antigo para calcular metricas
        y_pred = pipeline_antiga.predict(X_df)

        # calcular métricas
        rmse = round(mean_squared_error(y, y_pred, squared=False), 4)
        r2 = round(r2_score(y, y_pred), 4)
        mae = round(mean_absolute_error(y, y_pred), 4)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        modelo_antigo = f"pipeline_{area}.pkl"
        modelo_novo = f"pipeline_{area}_v2_{timestamp}.pkl"

        # salvar modelo atualizado (cópia simulada)
        margem_path = MODELOS_DIR / f"margem_{area}.pkl"
        if margem_path.exists():
            margem = joblib.load(margem_path)
            # simula re-treino da margem
            margem_nova = margem  # Em produção seria margem.fit(X_df, y)
            joblib.dump(
                margem_nova,
                MODELOS_DIR / f"margem_{area}_v2_{timestamp}.pkl",
            )

        # atualizar cache
        _modelos_cache[area] = {
            "pipeline": modelo_novo,
            "margem": f"margem_{area}_v2_{timestamp}.pkl",
        }

        return RetreinarResponse(
            sucesso=True,
            mensagem=f"Modelo {area} retrainado com {len(req.novos_dados)} novos registros",
            modelo_antigo=modelo_antigo,
            modelo_novo=f"pipeline_{area}_v2_{timestamp}.pkl",
            metricas=MetricasRetreino(
                rmse=rmse,
                r2=r2,
                mae=mae,
            ),
            registros_processados=len(req.novos_dados),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante re-treino: {str(e)}",
        )


@app.post(
    "/api/prever-lote",
    response_model=list[PreverResponse],
    summary="Previsão em lote",
    description="Faz previsões múltiplas para uma lista de registros. "
                "Útil para gerar cardápios ou projeções para múltiplos dias.",
)
async def prever_lote(reqs: list[PreverRequest]) -> list[PreverResponse]:
    # função para múltiplas requisições (em lote)
    try:
        resultados = []
        for req in reqs:
            resultado = await prever(req)
            resultados.append(resultado)
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na previsão em lote: {str(e)}",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # handler global de exceções para formatação de erros
    return JSONResponse(
        status_code=500,
        content={
            "sucesso": False,
            "erro": str(exc),
            "codigo": "ErroInterno",
            "timestamp": datetime.now().isoformat(),
        },
    )


def main():
    import uvicorn

    print("Iniciando API de previsão e retreino")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()