from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from .models import SubRubroModel, SubRubroUpdateModel
from .service import subrubro_service, SubRubroService

# [INICIO Patrón Singleton V3 (Backend)]
# Instancia del servicio (importada desde service.py)
def get_subrubro_service():
    return subrubro_service
# [FIN Patrón Singleton V3]

router_subrubros = APIRouter(
    prefix="/subrubros",
    tags=["SubRubros"]
)

@router_subrubros.post("/", response_model=SubRubroModel, status_code=status.HTTP_201_CREATED)
def crear_subrubro(data: SubRubroModel, service: SubRubroService = Depends(get_subrubro_service)):
    try:
        return service.crear_subrubro(data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al crear subrubro: {e}")

@router_subrubros.get("/lista", response_model=List[SubRubroModel])
def listar_subrubros(estado: str = 'activos', service: SubRubroService = Depends(get_subrubro_service)):
    # --- LÍNEA CORREGIDA (Sin rubro_id) ---
    return service.listar_subrubros(estado=estado)

@router_subrubros.put("/{id}", response_model=SubRubroModel)
def actualizar_subrubro(id: str, data: SubRubroUpdateModel, service: SubRubroService = Depends(get_subrubro_service)):
    try:
        actualizado = service.actualizar_subrubro(id, data)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="SubRubro no encontrado")
        return actualizado
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al actualizar subrubro: {e}")

@router_subrubros.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def baja_logica_subrubro(id: str, service: SubRubroService = Depends(get_subrubro_service)):
    try:
        if not service.baja_logica_subrubro(id):
            raise HTTPException(status_code=404, detail="SubRubro no encontrado")
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al dar de baja subrubro: {e}")
