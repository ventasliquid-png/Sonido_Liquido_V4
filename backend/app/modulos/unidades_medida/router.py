# backend/app/modulos/unidades_medida/router.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .models import UnidadMedidaModel, UnidadMedidaUpdateModel
from .service import unidad_medida_service, UnidadMedidaService

# --- Adherencia V12: Inyección de Dependencia del Servicio ---
def get_unidad_medida_service():
    if unidad_medida_service.db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Error crítico: Servicio de base de datos no disponible.")
    return unidad_medida_service
# --- Fin Adherencia V12 ---

router_unidades_medida = APIRouter(
    prefix="/unidades-medida",
    tags=["Unidades de Medida"],
    responses={404: {"description": "No encontrado"}}
)

@router_unidades_medida.post("/", 
                           response_model=UnidadMedidaModel, 
                           status_code=status.HTTP_201_CREATED,
                           summary="Crear nueva Unidad de Medida (ABR V12)")
def crear_unidad(
    data: UnidadMedidaModel, 
    service: UnidadMedidaService = Depends(get_unidad_medida_service)
):
    """
    Crea una nueva unidad de medida.
    Aplica la Doctrina ABR V12 (Anti-Duplicados) sobre `codigo_unidad`.
    """
    return service.crear_unidad(data)

@router_unidades_medida.get("/", 
                          response_model=List[UnidadMedidaModel],
                          summary="Listar Unidades (Filtro VIL)")
def listar_unidades(
    estado: str = 'activos', 
    service: UnidadMedidaService = Depends(get_unidad_medida_service)
):
    """
    Lista unidades de medida según la Doctrina VIL (Filtro de Tres Vías).
    - 'activos' (default): Solo baja_logica = false
    - 'inactivos': Solo baja_logica = true
    - 'todos': Todos los registros
    """
    return service.listar_unidades(estado)

@router_unidades_medida.patch("/{id}", 
                             response_model=UnidadMedidaModel,
                             summary="Actualizar Unidad (PATCH)")
def actualizar_unidad(
    id: str, 
    data: UnidadMedidaUpdateModel, 
    service: UnidadMedidaService = Depends(get_unidad_medida_service)
):
    """
    Actualiza parcialmente una unidad de medida (nombre o baja_logica).
    """
    updated = service.actualizar_unidad(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return updated

@router_unidades_medida.delete("/{id}", 
                              status_code=status.HTTP_204_NO_CONTENT,
                              summary="Baja Lógica (Doctrina VIL)")
def baja_logica_unidad(
    id: str, 
    service: UnidadMedidaService = Depends(get_unidad_medida_service)
):
    """
    Realiza una baja lógica (Doctrina VIL) de la unidad.
    Establece baja_logica = true.
    """
    if not service.baja_logica_unidad(id):
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return {} # No content