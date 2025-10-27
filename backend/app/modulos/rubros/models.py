from pydantic import BaseModel, Field
from typing import Optional

class RubroModel(BaseModel):
    """
    Modelo de datos principal para un Rubro.
    Implementa la Doctrina ID Soberano (id de Firestore y codigo de negocio).
    """
    id: Optional[str] = None  # ID de Firestore
    codigo: str = Field(..., max_length=3, description="Clave de negocio única, visible al usuario")
    nombre: str = Field(..., max_length=30, description="Nombre descriptivo del rubro")
    baja_logica: bool = Field(default=False, description="Estado de baja lógica (ABR)")

    class Config:
        # Permite que el modelo se cree a partir de atributos de objeto (como los de Firestore)
        from_attributes = True

class RubroUpdateModel(BaseModel):
    """
    Modelo para la actualización parcial (PATCH) de un Rubro.
    El 'codigo' no es modificable.
    """
    nombre: Optional[str] = None
    baja_logica: Optional[bool] = None

    class Config:
        from_attributes = True