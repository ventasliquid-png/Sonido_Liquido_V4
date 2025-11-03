# backend/app/modulos/subrubros/router.py (V12.9 - Corrección de Prefijo)
from fastapi import APIRouter, HTTPException, status
from typing import List
from .models import SubRubroModel, SubRubroUpdateModel
from .service import subrubro_service

# --- INICIO: CORRECCIÓN V12.9 ---
# Eliminamos el 'prefix' de aquí. main.py ya lo define.
router = APIRouter(
    tags=["Sub-Rubros"]
)
# --- FIN: CORRECCIÓN V12.9 ---


# --- Endpoint de CREAR (POST) ---
@router.post("/", response_model=SubRubroModel, status_code=status.HTTP_201_CREATED)
def crear_subrubro(data: SubRubroModel):
    """
    Crea un nuevo sub-rubro.
    Verifica duplicados activos o inactivos antes de crear.
    """
    try:
        # La lógica de negocio (transacción, duplicados) está en el servicio
        return subrubro_service.crear_subrubro(data)
    except HTTPException as e:
        # Si el servicio lanza una excepción HTTP (ej. 409 Conflict), la reenviamos
        raise e
    except Exception as e:
        # Captura cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"Error en router al crear: {e}")

# --- Endpoint de LISTAR (GET) ---
@router.get("/", response_model=List[SubRubroModel])
def listar_subrubros(estado: str = 'activos'):
    """
    Lista todos los sub-rubros.
    Filtra por estado: 'activos' (default), 'inactivos', o 'todos'.
    """
    try:
        return subrubro_service.listar_subrubros(estado)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en router al listar: {e}")

# --- Endpoint de ACTUALIZAR (PATCH) ---
@router.patch("/{id}", response_model=SubRubroModel)
def actualizar_subrubro(id: str, data: SubRubroUpdateModel):
    """
    Actualiza un sub-rubro existente por su ID.
    Solo actualiza los campos enviados en el body.
    """
    try:
        actualizado = subrubro_service.actualizar_subrubro(id, data)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="SubRubro no encontrado")
        return actualizado
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en router al actualizar: {e}")


# --- Endpoint de BAJA (DELETE) ---
@router.delete("/{id}", response_model=dict)
def baja_logica_subrubro(id: str):
    """
    Realiza una baja lógica de un sub-rubro por su ID.
    Establece 'baja_logica' = True.
    """
    try:
        success = subrubro_service.baja_logica_subrubro(id)
        if not success:
            raise HTTPException(status_code=404, detail="SubRubro no encontrado al intentar dar de baja")
        return {"id": id, "baja_logica": True, "status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en router al dar de baja: {e}")