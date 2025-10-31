from pydantic import BaseModel, Field
from typing import Optional

class SubRubroModel(BaseModel):
    id: Optional[str] = None
    codigo_subrubro: str = Field(..., max_length=10) # Identificador de negocio único
    nombre: str = Field(..., max_length=50)
    baja_logica: bool = False

    class Config:
        orm_mode = True

class SubRubroUpdateModel(BaseModel):
    codigo_subrubro: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=50)
    baja_logica: Optional[bool] = None