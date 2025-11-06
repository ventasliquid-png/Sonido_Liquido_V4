from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..condiciones_iva.models import CondicionIvaModel, CondicionIvaUpdateModel
from ..condiciones_iva.service import condicion_iva_service, CondicionIvaService

# --- Inyección de Dependencia del Servicio (Patrón Canónico) ---
def get_condicion_iva_service():
    if condicion_iva_service.db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Error crítico: Servicio de base de datos no disponible.")
    return condicion_iva_service
# --- Fin Inyección de Dependencia ---

router_condiciones_iva = APIRouter(
    prefix="/condiciones-iva",
    tags=["Condiciones IVA"],
    responses={404: {"description": "No encontrado"}}
)

@router_condiciones_iva.post("/", 
                             response_model=CondicionIvaModel, 
                             status_code=status.HTTP_201_CREATED,
                             summary="Crear nueva Condición IVA (ABR)")
def crear_iva(
    data: CondicionIvaModel, 
    service: CondicionIvaService = Depends(get_condicion_iva_service)):
    """Crea una nueva condición IVA. Aplica la Doctrina ABR sobre 'codigo_iva'."""
    return service.crear_iva(data)

@router_condiciones_iva.get("/", 
                          response_model=List[CondicionIvaModel],
                          summary="Listar Condiciones IVA (Filtro VIL)")
def listar_ivas(
    estado: str = 'activos', 
    service: CondicionIvaService = Depends(get_condicion_iva_service)):
    """Lista condiciones IVA según la Doctrina VIL (Filtro de Tres Vías)."""
    return service.listar_ivas(estado)

@router_condiciones_iva.patch("/{id}", 
                              response_model=CondicionIvaModel,
                              summary="Actualizar Condición IVA (PATCH)")
def actualizar_iva(
    id: str, 
    data: CondicionIvaUpdateModel, 
    service: CondicionIvaService = Depends(get_condicion_iva_service)):
    """Actualiza parcialmente una condición IVA (nombre, alícuota o baja_logica)."""
    updated = service.actualizar_iva(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Condición IVA no encontrada")
    return updated

@router_condiciones_iva.delete("/{id}", 
                              status_code=status.HTTP_204_NO_CONTENT,
                              summary="Baja Lógica (Doctrina VIL y Anti-Orfandad)")
def baja_logica_iva(
    id: str, 
    service: CondicionIvaService = Depends(get_condicion_iva_service)):
    """Realiza una baja lógica (Doctrina VIL) con Anti-Orfandad."""
    try:
        if not service.baja_logica_iva(id):
            raise HTTPException(status_code=404, detail="Condición IVA no encontrada")
    except HTTPException as e:
        # Re-lanzar la excepción HTTP de Anti-Orfandad
        raise e
    except Exception as e:
        # Capturar otros posibles errores
        raise HTTPException(status_code=500, detail=str(e))
    
    return {} # No content
