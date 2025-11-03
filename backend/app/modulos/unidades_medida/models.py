# backend/app/modulos/unidades_medida/models.py
from pydantic import BaseModel, Field
from typing import Optional

class UnidadMedidaModel(BaseModel):
    """
    Vestimenta Canónica (Hito F1-50) para Unidades de Medida.
    """
    id: Optional[str] = None
    codigo_unidad: str = Field(..., max_length=4, description="Clave de negocio única (ej: KG, UN)")
    nombre: str = Field(..., max_length=30, description="Nombre descriptivo (ej: Kilogramos)")
    baja_logica: bool = Field(default=False, description="Estado de baja lógica (Doctrina VIL)")

    class Config:
        from_attributes = True # Reemplaza orm_mode
        populate_by_name = True # Permite mapeo si los nombres difieren (aunque aquí no)

class UnidadMedidaUpdateModel(BaseModel):
    """ Modelo para la actualización parcial (PATCH). Adhiere a VIL. """
    nombre: Optional[str] = Field(None, max_length=30)
    baja_logica: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True