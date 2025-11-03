# backend/app/modulos/subrubros/router.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .models import SubRubroModel, SubRubroUpdateModel
from .service import subrubro_service, SubRubroService

# --- Adherencia V12: Inyección de Dependencia del Servicio ---
def get_subrubro_service():
    if subrubro_service.db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Error crítico: Servicio de base de datos no disponible.")
    return subrubro_service
# --- Fin Adherencia V12 ---

router_subrubros = APIRouter(
    prefix="/subrubros",
    tags=["SubRubros"],
    responses={404: {"description": "No encontrado"}}
)

@router_subrubros.post("/", 
                        response_model=SubRubroModel, 
                        status_code=status.HTTP_201_CREATED,
                        summary="Crear nuevo SubRubro (ABR V12)")
def crear_subrubro(
    data: SubRubroModel, 
    service: SubRubroService = Depends(get_subrubro_service)
):
    """
    Crea un nuevo subrubro.
    Aplica la Doctrina ABR V12 (Anti-Duplicados) sobre `codigo_subrubro` y la gestión de contadores.
    """
    return service.crear_subrubro(data)

@router_subrubros.get("/", 
                      response_model=List[SubRubroModel],
                      summary="Listar SubRubros (Filtro VIL)")
def listar_subrubros(
    estado: str = 'activos', 
    rubro_id: str = None, 
    service: SubRubroService = Depends(get_subrubro_service)
):
    """
    Lista subrubros según la Doctrina VIL (Filtro de Tres Vías).
    - 'activos' (default): Solo baja_logica = false
    - 'inactivos': Solo baja_logica = true
    - 'todos': Todos los registros
    """
    return service.listar_subrubros(estado=estado, rubro_id=rubro_id)

@router_subrubros.get("/codigo/next", 
                      summary="Obtener próximo código de SubRubro (Operación Contadores)",
                      response_model=int)
def obtener_siguiente_codigo(
    service: SubRubroService = Depends(get_subrubro_service)
):
    """
    Genera y reserva el próximo código numérico para un nuevo subrubro.
    """
    return service.obtener_siguiente_codigo()

@router_subrubros.patch("/{id}", 
                        response_model=SubRubroModel,
                        summary="Actualizar SubRubro (PATCH)")
def actualizar_subrubro(
    id: str, 
    data: SubRubroUpdateModel, 
    service: SubRubroService = Depends(get_subrubro_service)
):
    """
    Actualiza parcialmente un subrubro (nombre o baja_logica).
    """
    updated = service.actualizar_subrubro(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="SubRubro no encontrado")
    return updated

@router_subrubros.delete("/{id}", 
                         status_code=status.HTTP_204_NO_CONTENT,
                         summary="Baja Lógica (Doctrina VIL)")
def baja_logica_subrubro(
    id: str, 
    service: SubRubroService = Depends(get_subrubro_service)
):
    """
    Realiza una baja lógica (Doctrina VIL) del subrubro.
    Establece baja_logica = true.
    """
    if not service.baja_logica_subrubro(id):
        raise HTTPException(status_code=404, detail="SubRubro no encontrado")
    return {}