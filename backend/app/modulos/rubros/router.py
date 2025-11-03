# backend/app/modulos/rubros/router.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .models import RubroModel, RubroUpdateModel
from .service import rubro_service, RubroService

# --- Adherencia V12: Inyección de Dependencia del Servicio ---
def get_rubro_service():
    # Asume que RubroService ya maneja la conexión a la base de datos o levanta una excepción.
    if rubro_service.db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Error crítico: Servicio de base de datos no disponible.")
    return rubro_service
# --- Fin Adherencia V12 ---

router_rubros = APIRouter(
    prefix="/rubros",
    tags=["Rubros"],
    responses={404: {"description": "No encontrado"}}
)

@router_rubros.post("/", 
                     response_model=RubroModel, 
                     status_code=status.HTTP_201_CREATED,
                     summary="Crear nuevo Rubro (ABR V12)")
def crear_rubro(
    data: RubroModel, 
    service: RubroService = Depends(get_rubro_service)
):
    """
    Crea un nuevo rubro.
    Aplica la Doctrina ABR V12 (Anti-Duplicados) sobre `codigo_rubro` y la gestión de contadores.
    """
    return service.crear_rubro(data)

@router_rubros.get("/", 
                   response_model=List[RubroModel],
                   summary="Listar Rubros (Filtro VIL)")
def listar_rubros(
    estado: str = 'activos', 
    service: RubroService = Depends(get_rubro_service)
):
    """
    Lista rubros según la Doctrina VIL (Filtro de Tres Vías).
    - 'activos' (default): Solo baja_logica = false
    - 'inactivos': Solo baja_logica = true
    - 'todos': Todos los registros
    """
    return service.listar_rubros(estado)

@router_rubros.get("/codigo/next", 
                    summary="Obtener próximo código de Rubro (Operación Contadores)",
                    response_model=int)
def obtener_siguiente_codigo(
    service: RubroService = Depends(get_rubro_service)
):
    """
    Genera y reserva el próximo código numérico para un nuevo rubro.
    """
    return service.obtener_siguiente_codigo()

@router_rubros.patch("/{id}", 
                      response_model=RubroModel,
                      summary="Actualizar Rubro (PATCH)")
def actualizar_rubro(
    id: str, 
    data: RubroUpdateModel, 
    service: RubroService = Depends(get_rubro_service)
):
    """
    Actualiza parcialmente un rubro (nombre o baja_logica).
    """
    updated = service.actualizar_rubro(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return updated

@router_rubros.delete("/{id}", 
                      status_code=status.HTTP_204_NO_CONTENT,
                      summary="Baja Lógica (Doctrina VIL)")
def baja_logica_rubro(
    id: str, 
    service: RubroService = Depends(get_rubro_service)
):
    """
    Realiza una baja lógica (Doctrina VIL) del rubro.
    Establece baja_logica = true.
    """
    if not service.baja_logica_rubro(id):
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return {} # No content