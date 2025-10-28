# backend/app/modulos/rubros/models.py (CON ALIAS)

from pydantic import BaseModel, Field, AliasChoices
from typing import Optional

class RubroModel(BaseModel):
    """
    Modelo de datos principal para un Rubro.
    Implementa la Doctrina ID Soberano (id de Firestore y codigo de negocio).
    Usa AliasChoices para mapear campos de Firestore a nombres de Pydantic.
    """
    # Usar Field con validation_alias para mapear 'id' de Firestore
    id: Optional[str] = Field(None, validation_alias=AliasChoices('id', '_id')) # Firestore usa 'id' como propiedad, no campo real, pero Pydantic puede mapearlo
    # Usar Field con validation_alias para mapear 'code' a 'codigo'
    codigo: str = Field(..., max_length=3, description="Clave de negocio única", validation_alias=AliasChoices('codigo', 'code'))
    # Usar Field con validation_alias para mapear 'name' a 'nombre'
    nombre: str = Field(..., max_length=30, description="Nombre descriptivo", validation_alias=AliasChoices('nombre', 'name'))
    # baja_logica suele coincidir
    baja_logica: bool = Field(default=False, description="Estado de baja lógica")

    class Config:
        from_attributes = True
        # NUEVO: Permitir population por alias (para que acepte 'code' y 'name')
        populate_by_name = True

class RubroUpdateModel(BaseModel):
    """ Modelo para la actualización parcial (PATCH)... """
    nombre: Optional[str] = Field(None, validation_alias=AliasChoices('nombre', 'name')) # Añadir alias también aquí si es necesario
    baja_logica: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True # Añadir aquí también por consistencia