# backend/app/modulos/rubros/router.py (PREFIJO ELIMINADO)

from fastapi import APIRouter, Depends, status, Query, Response
from typing import List, Optional
from .models import RubroModel, RubroUpdateModel
from .service import RubroService

# --- CORRECCIÓN: Eliminar el 'prefix="/rubros"' de aquí ---
router = APIRouter(
    # prefix="/rubros", # <--- ELIMINADO
    tags=["Rubros"],
    responses={404: {"description": "No encontrado"}}
)

# --- Dependencia ---
def get_rubro_service():
    """Dependencia para inyectar el servicio de rubros."""
    # En una app real, podrías manejar dependencias más complejas aquí
    # o usar un framework de inyección de dependencias.
    # Por ahora, simplemente instanciarlo está bien.
    try:
        return RubroService()
    except RuntimeError as e:
        # Captura el error de inicialización de Firestore y lo reporta
        raise HTTPException(status_code=503, detail=f"Error al conectar con la base de datos: {e}")


@router.post(
    "/", # Ahora esta ruta será POST /rubros (correcto)
    response_model=RubroModel,
    status_code=status.HTTP_201_CREATED,
    summary="Crear o Reactivar un Rubro (Doctrina ABR)"
)
def crear_rubro(
    rubro: RubroModel,
    response: Response,
    service: RubroService = Depends(get_rubro_service)
):
    """
    Crea un nuevo rubro.
    - Si el 'codigo' ya existe y está inactivo (baja_logica: True),
      lo reactiva y devuelve 200 OK (Doctrina ABR).
    - Si el 'codigo' ya existe y está activo, devuelve 409 Conflict.
    - Si es nuevo, lo crea (y el contador asociado) y devuelve 201 Created.
    """
    rubro_creado, estado = service.crear_rubro(rubro)

    if estado == "reactivated":
        response.status_code = status.HTTP_200_OK

    return rubro_creado

@router.get(
    "/", # Ahora esta ruta será GET /rubros (correcto)
    response_model=List[RubroModel],
    summary="Listar Rubros"
)
def listar_rubros(
    activos: Optional[bool] = Query(None, description="Filtrar por estado (True=activos, False=inactivos)"),
    service: RubroService = Depends(get_rubro_service)
):
    """Obtiene una lista de rubros, con filtro opcional de estado."""
    return service.listar_rubros(activos)

@router.get(
    "/{id}", # Ahora esta ruta será GET /rubros/{id} (correcto)
    response_model=RubroModel,
    summary="Obtener Rubro por ID"
)
def obtener_rubro_por_id(
    id: str,
    service: RubroService = Depends(get_rubro_service)
):
    """Obtiene un rubro por su ID de Firestore."""
    return service.obtener_rubro_por_id(id)

@router.get(
    "/codigo/{codigo}", # Ahora esta ruta será GET /rubros/codigo/{codigo} (correcto)
    response_model=RubroModel,
    summary="Obtener Rubro por Código de Negocio"
)
def obtener_rubro_por_codigo(
    codigo: str,
    service: RubroService = Depends(get_rubro_service)
):
    """Obtiene un rubro por su 'codigo' de negocio (ID Soberano)."""
    return service.obtener_rubro_por_codigo(codigo)

@router.patch(
    "/{id}", # Ahora esta ruta será PATCH /rubros/{id} (correcto)
    response_model=RubroModel,
    summary="Actualizar un Rubro"
)
def actualizar_rubro(
    id: str,
    rubro_update: RubroUpdateModel,
    service: RubroService = Depends(get_rubro_service)
):
    """Actualiza parcialmente el 'nombre' o 'baja_logica' de un rubro."""
    return service.actualizar_rubro(id, rubro_update)

@router.delete(
    "/{id}", # Ahora esta ruta será DELETE /rubros/{id} (correcto)
    response_model=RubroModel,
    summary="Baja Lógica de un Rubro"
)
def baja_logica_rubro(
    id: str,
    service: RubroService = Depends(get_rubro_service)
):
    """Realiza la baja lógica (soft-delete) de un rubro."""
    return service.baja_logica_rubro(id)