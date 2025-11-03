# backend/app/modulos/rubros/router.py (V12.9 - Sincronización Total)
from fastapi import APIRouter, HTTPException, status
from typing import List
from .models import RubroModel, RubroUpdateModel
# --- CORREGIDO: Se importa el servicio directo, se elimina 'Depends' ---
from .service import rubro_service

router = APIRouter(
    # prefix="/rubros", <-- ¡ERROR DOCTRINAL ELIMINADO! (Se aplica Doctrina V12.9)
    tags=["Rubros"]
)

# --- CORREGIDO: Se elimina 'Depends' y 'async def', se usa 'def' ---
@router.post("/", response_model=RubroModel, status_code=status.HTTP_201_CREATED)
def crear_rubro(data: RubroModel):
    try:
        return rubro_service.crear_rubro(data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CORREGIDO: Se elimina 'Depends' y 'async def', se usa 'def' ---
@router.get("/", response_model=List[RubroModel])
def listar_rubros(estado: str = 'activos'):
    try:
        return rubro_service.listar_rubros(estado)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en router al listar: {e}")

# --- CORREGIDO: Se elimina 'Depends' y 'async def', se usa 'def' ---
@router.patch("/{rubro_id}", response_model=RubroModel)
def actualizar_rubro(rubro_id: str, data: RubroUpdateModel):
    rubro = rubro_service.actualizar_rubro(rubro_id, data)
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return rubro

# --- CORREGIDO: Se elimina 'Depends' y 'async def', se usa 'def' ---
# --- Se cambia la respuesta a un 'dict' (como SubRubros) en vez de 204 ---
@router.delete("/{rubro_id}", response_model=dict)
def baja_logica_rubro(rubro_id: str):
    success = rubro_service.baja_logica_rubro(rubro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rubro no encontrado al intentar dar de baja")
    # Devolvemos un JSON que el frontend pueda entender
    return {"id": rubro_id, "baja_logica": True, "status": "ok"}