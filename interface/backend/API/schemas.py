from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, List
from datetime import datetime


class FeatureSchema(BaseModel):
    # features derivadas do calendário letivo
    Ano: int = Field(..., description="Ano")
    Mês: int = Field(..., description="Mês (1-12)")
    Dia_mês: int = Field(..., description="Dia do mês (1-31)")
    Dia_semana: Literal["seg", "ter", "qua", "qui", "sex", "sáb", "dom"] = Field(
        ..., description="Dia da semana em português"
    )
    letivo: int = Field(..., description="1 se letivo, 0 se não letivo")
    feriado: int = Field(..., description="1 se feriado, 0 se não feriado")
    ferias: int = Field(..., description="1 se férias, 0 se não férias")
    vespera_nao_letivo: int = Field(
        ..., description="1 véspera de dia não letivo"
    )
    pos_nao_letivo: int = Field(
        ..., description="1 dia pós-dia não letivo"
    )
    vespera_feriado: int = Field(
        ..., description="1 véspera de feriado"
    )
    pos_feriado: int = Field(
        ..., description="1 dia pós-feriado"
    )
    dias_desde_inicio_ferias: int = Field(
        ..., description="Dias desde início das férias atuais"
    )
    dias_desde_ultimas_ferias: int = Field(
        ..., description="Dias desde últimas férias"
    )
    dias_ate_ferias: int = Field(
        ..., description="Dias até próxima fériar"
    )
    dias_ate_feriado: int = Field(
        ..., description="Dias até próximo feriado"
    )
    # features relacionadas ao cardápio
    refeicao: str = Field(
        ..., description="Tipo de refeição (almoco/jantar)"
    )
    total: float = Field(
        ..., description="Custo total da refeição"
    )
    prato_principal_1: str = Field(
        ..., description="Prato principal 1"
    )
    prato_principal_2: str = Field(
        ..., description="Prato principal 2"
    )
    guarnição: str = Field(
        ..., description="Guarnição/lateral"
    )
    sobremesa_1: str = Field(
        ..., description="Sobremesa 1"
    )


class PreverRequest(BaseModel):
    # request para endpoint de previsão
    area: Literal["area1", "area2"] = Field(
        ..., description="Área do modelo para previsão"
    )
    features: FeatureSchema = Field(
        ..., description="Features de entrada padronizadas"
    )


class PrevisaoOutput(BaseModel):
    # output da previsão individual
    previsao_central: int = Field(
        ..., description="Valor pontual da previsão"
    )
    limite_inferior: int = Field(
        ..., description="Limite inferior da margem de confiança"
    )
    limite_superior: int = Field(
        ..., description="Limite superior da margem de confiança"
    )
    margem_seguranca: int = Field(
        ..., description="Margem de segurança do modelo"
    )


class PreverResponse(BaseModel):
    # response completo do endpoint de previsão
    sucesso: bool = Field(default=True, description="Indica se a previsão foi bem-sucedida")
    previsao: PrevisaoOutput = Field(..., description="Resultados da previsão")
    metadados: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais da predição"
    )
    timestamp_geracao: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp quando a previsão foi gerada"
    )


class DadoRetreino(BaseModel):
    # registro individual para re-treino
    features: FeatureSchema = Field(..., description="Features de entrada")
    resultado_real: float = Field(
        ..., description="Valor observado/real correspondente"
    )
    data: datetime = Field(
        ..., description="Data do registro"
    )


class RetreinarRequest(BaseModel):
    # request para endpoint de re-treino
    area: Literal["area1", "area2"] = Field(
        ..., description="Área do modelo a ser retrainado"
    )
    novos_dados: List[DadoRetreino] = Field(
        ..., description="Lista de novos registros com features e resultados reais"
    )
    atualizar_modelo: bool = Field(
        default=True,
        description="Se verdadeiro, salva novos modelos treinados"
    )


class MetricasRetreino(BaseModel):
    # métricas após re-treino
    rmse: float = Field(..., description="Root Mean Square Error")
    r2: float = Field(..., description="Coeficiente de determinação")
    mae: float = Field(..., description="Mean Absolute Error")


class RetreinarResponse(BaseModel):
    # response do endpoint de re-treino
    sucesso: bool = Field(default=True, description="Indica se o re-treino foi bem-sucedido")
    mensagem: str = Field(..., description="Mensagem descritiva do resultado")
    modelo_antigo: str = Field(
        ..., description="Caminho do modelo anterior"
    )
    modelo_novo: str = Field(
        ..., description="Caminho do modelo atualizado"
    )
    metricas: MetricasRetreino = Field(
        ..., description="Metricas de desempenho do novo modelo"
    )
    registros_processados: int = Field(
        ..., description="Quantidade de registros usados no retreino"
    )
    timestamp_conclusao: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de conclusão do re-treino"
    )


class AreaStatus(BaseModel):
    # status de uma área de modelo
    pipeline: str = Field(..., description="Arquivo do pipeline")
    margem: str = Field(..., description="Arquivo da margem")
    ultima_atualizacao: datetime = Field(
        ..., description="Última data de atualização"
    )


class StatusResponse(BaseModel):
    # response do endpoint de status
    sucesso: bool = Field(default=True, description="Indica status operacional")
    status: Literal["operacional", "manutenção", "erro"] = Field(
        default="operacional",
        description="Status geral da API"
    )
    areas: List[Literal["area1", "area2"]] = Field(
        default=["area1", "area2"],
        description="Áreas disponíveis"
    )
    modelos_disponiveis: Dict[str, AreaStatus] = Field(
        default_factory=dict,
        description="Status detalhado de cada área"
    )


class ErrorResponse(BaseModel):
    # response padronizado para erros
    sucesso: bool = Field(default=False, description="Indica falha")
    erro: str = Field(..., description="Descrição do erro")
    codigo: str = Field(
        ..., description="Código identificador do erro"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp do erro"
    )