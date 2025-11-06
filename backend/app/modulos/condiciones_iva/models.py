from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class CondicionIvaModel(BaseModel):
    id: Optional[str] = None
    codigo_iva: str = Field(..., max_length=4, description="Clave de negocio única (ej: EXE, GRA)")
    nombre: str = Field(..., max_length=30, description="Nombre descriptivo (ej: Exento, Gravado)")
    alicuota: Decimal = Field(..., description="Valor porcentual (ej: 21.00)")
    baja_logica: bool = Field(default=False, description="Estado de baja lógica (Doctrina VIL)")

    class Config:
        from_attributes = True 
        populate_by_name = True 

class CondicionIvaUpdateModel(BaseModel):
    nombre: Optional[str] = Field(None, max_length=30)
    alicuota: Optional[Decimal] = Field(None, description="Valor porcentual")
    baja_logica: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True
