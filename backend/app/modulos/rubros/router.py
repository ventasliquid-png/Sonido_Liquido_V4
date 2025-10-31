# backend/app/modulos/rubros/router.py (V12.5 - Prefijo Corregido)
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .models import RubroModel, RubroUpdateModel
from .service import rubro_service, RubroService

router = APIRouter(
    # prefix="/rubros", <-- ¡ERROR DOCTRINAL ELIMINADO!
    tags=["Rubros"]
)

async def get_service() -> RubroService:
# ... (el resto del archivo es idéntico) ...
    return rubro_service

@router.post("/", response_model=RubroModel, status_code=status.HTTP_201_CREATED)
async def crear_rubro(
    data: RubroModel, 
    service: RubroService = Depends(get_service)):
    try:
        return await service.crear_rubro(data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[RubroModel])
async def listar_rubros(
    estado: str = 'activos', 
    service: RubroService = Depends(get_service)):
    return await service.listar_rubros(estado)

@router.patch("/{rubro_id}", response_model=RubroModel)
async def actualizar_rubro(
    rubro_id: str, 
    data: RubroUpdateModel,
    service: RubroService = Depends(get_service)):
    rubro = await service.actualizar_rubro(rubro_id, data)
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return rubro

@router.delete("/{rubro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def baja_logica_rubro(
    rubro_id: str, 
    service: RubroService = Depends(get_service)):
    if not await service.baja_logica_rubro(rubro_id):
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return