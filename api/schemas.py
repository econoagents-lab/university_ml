from pydantic import BaseModel, Field


class RiesgoCaidaInput(BaseModel):
    proyecto: str = Field(..., description="Nombre del proyecto inmobiliario")
    asesor: str = Field(..., description="Asesor responsable")
    medio_captacion: str = Field(..., description="Medio de captación")
    precio_departamento: float = Field(..., gt=0, description="Precio de la unidad")
    dias_en_tuberia: int = Field(..., ge=0, description="Días desde la separación")
    dormitorios: int = Field(..., ge=0, le=10, description="Número de dormitorios")
    tiene_cuota_inicial: bool = Field(..., description="Indica si registró cuota inicial")
    cambios_unidad: int = Field(0, ge=0, description="Número de cambios de unidad")
    interacciones_ult_7d: int = Field(0, ge=0, description="Interacciones recientes")
    descuento_pct: float = Field(0.0, ge=0, le=1, description="Descuento porcentual")


class RiesgoCaidaOutput(BaseModel):
    riesgo_caida: float
    nivel_riesgo: str
    decision_recomendada: str
    responsable: str
    valor_esperado_en_riesgo: float
    modelo_usado: str


class RiesgoCaidaBatchInput(BaseModel):
    operaciones: list[RiesgoCaidaInput] = Field(..., min_length=1, max_length=500)


class RiesgoCaidaBatchOutput(BaseModel):
    total_operaciones: int
    resultados: list[RiesgoCaidaOutput]



class FeedbackRiesgoCaidaInput(BaseModel):
    codigo_proforma: str
    codigo_unidad: str
    fecha_score: str
    riesgo_caida: float = Field(..., ge=0, le=1)
    nivel_riesgo: str
    ranking_prioridad: int = Field(..., ge=1)
    responsable: str
    accion_tomada: str = Field("pendiente")
    fecha_accion: str = Field("")
    resultado_7d: str = Field("pendiente")
    resultado_30d: str = Field("pendiente")
    caida_real_30d: str = Field("")
    comentario: str = Field("")


class FeedbackRiesgoCaidaOutput(BaseModel):
    status: str
    output_path: str
    rows_written: int
