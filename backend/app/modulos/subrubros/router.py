# backend/app/modulos/subrubros/router.py (V12.6 - Corrección ASYNC)
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .models import SubRubroModel, SubRubroUpdateModel
from .service import subrubro_service, SubRubroService

router = APIRouter(
    tags=["Sub-Rubros"]
)

# get_service NO es async
def get_service() -> SubRubroService:
    return subrubro_service

@router.post("/", response_model=SubRubroModel, status_code=status.HTTP_201_CREATED)
def crear_subrubro( # <--- 'async' ELIMINADO
    data: SubRubroModel, 
    service: SubRubroService = Depends(get_service)):
    try:
        return service.crear_subrubro(data) # <--- 'await' ELIMINADO
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SubRubroModel])
def listar_subrubros( # <--- 'async' ELIMINADO
    estado: str = 'activos', 
    service: SubRubroService = Depends(get_service)):
    return service.listar_subrubros(estado) # <--- 'await' ELIMINADO

@router.patch("/{subrubro_id}", response_model=SubRubroModel)
async def actualizar_subrubro( # <--- 'async' SE MANTIENE
    subrubro_id: str, 
    data: SubRubroUpdateModel,
    service: SubRubroService = Depends(get_service)):
    subrubro = await service.actualizar_subrubro(subrubro_id, data) # <--- 'await' SE MANTIENE
    if not subrubro:
        raise HTTPException(status_code=404, detail="SubRubro no encontrado")
    return subrubro

@router.delete("/{subrubro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def baja_logica_subrubro( # <--- 'async' SE MANTIENE
    subrubro_id: str, 
    service: SubRubroService = Depends(get_service)):
    if not await service.baja_logica_subrubro(subrubro_id): # <--- 'await' SE MANTIENE
        raise HTTPException(status_code=404, detail="SubRubro no encontrado")
    return