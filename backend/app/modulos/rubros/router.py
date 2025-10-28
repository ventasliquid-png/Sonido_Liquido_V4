# backend/app/modulos/rubros/router.py (VERIFICAR IMPORT HTTPException)

from fastapi import APIRouter, Depends, status, Query, Response, HTTPException # <-- ASEGURAR HTTPException AQUÍ
from typing import List, Optional
from .models import RubroModel, RubroUpdateModel
from .service import RubroService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Rubros"],
    responses={404: {"description": "No encontrado"}}
)

def get_rubro_service():
    try:
        return RubroService()
    except RuntimeError as e:
        # Esta línea necesita HTTPException importado en ESTE archivo
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error al conectar con la base de datos: {e}")

@router.get(
    "/",
    response_model=List[RubroModel],
    summary="Listar Rubros"
)
def listar_rubros(
    activos: Optional[bool] = Query(None, description="Filtrar por estado (True=activos, False=inactivos)"),
    service: RubroService = Depends(get_rubro_service)
):
    """Obtiene una lista de rubros, con filtro opcional de estado."""
    logger.info(f"Router: Received GET /rubros request with activos={activos}")
    try:
        result = service.listar_rubros(activos)
        logger.info(f"Router: Service returned {len(result)} rubros.")
        return result
    except HTTPException as http_exc:
        logger.error(f"Router: HTTPException from service: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Router: Unexpected error calling service.listar_rubros: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno al listar rubros: {e}")

# ... (Resto de las rutas POST, GET/{id}, PATCH, DELETE sin cambios...) ...
@router.post( "/", response_model=RubroModel, status_code=status.HTTP_201_CREATED, summary="Crear o Reactivar un Rubro (Doctrina ABR)")
def crear_rubro( rubro: RubroModel, response: Response, service: RubroService = Depends(get_rubro_service)):
    rubro_creado, estado = service.crear_rubro(rubro)
    if estado == "reactivated": response.status_code = status.HTTP_200_OK
    return rubro_creado

@router.get( "/{id}", response_model=RubroModel, summary="Obtener Rubro por ID")
def obtener_rubro_por_id( id: str, service: RubroService = Depends(get_rubro_service)):
    return service.obtener_rubro_por_id(id)

@router.get( "/codigo/{codigo}", response_model=RubroModel, summary="Obtener Rubro por Código de Negocio")
def obtener_rubro_por_codigo( codigo: str, service: RubroService = Depends(get_rubro_service)):
    return service.obtener_rubro_por_codigo(codigo)

@router.patch( "/{id}", response_model=RubroModel, summary="Actualizar un Rubro")
def actualizar_rubro( id: str, rubro_update: RubroUpdateModel, service: RubroService = Depends(get_rubro_service)):
    return service.actualizar_rubro(id, rubro_update)

@router.delete( "/{id}", response_model=RubroModel, summary="Baja Lógica de un Rubro")
def baja_logica_rubro( id: str, service: RubroService = Depends(get_rubro_service)):
    return service.baja_logica_rubro(id)