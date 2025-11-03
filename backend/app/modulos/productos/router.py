# backend/app/modulos/productos/router.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .models import ProductoModel, ProductoUpdateModel
from .service import producto_service, ProductoService

# --- Adherencia V12: Inyección de Dependencia del Servicio ---
def get_producto_service():
    if producto_service.db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Error crítico: Servicio de base de datos no disponible.")
    return producto_service
# --- Fin Adherencia V12 ---

router_productos = APIRouter(
    prefix="/productos",
    tags=["Productos"],
    responses={404: {"description": "No encontrado"}}
)

@router_productos.post("/", 
                        response_model=ProductoModel, 
                        status_code=status.HTTP_201_CREATED,
                        summary="Crear nuevo Producto (ABR V12)")
def crear_producto(
    data: ProductoModel, 
    service: ProductoService = Depends(get_producto_service)
):
    """
    Crea un nuevo producto.
    Aplica la Doctrina ABR V12 (Anti-Duplicados) sobre `codigo_producto` y la gestión de contadores.
    """
    return service.crear_producto(data)

@router_productos.get("/", 
                      response_model=List[ProductoModel],
                      summary="Listar Productos (Filtro VIL)")
def listar_productos(
    estado: str = 'activos', 
    rubro_id: str = None,
    subrubro_id: str = None,
    service: ProductoService = Depends(get_producto_service)
):
    """
    Lista productos según la Doctrina VIL (Filtro de Tres Vías).
    - 'activos' (default): Solo baja_logica = false
    - 'inactivos': Solo baja_logica = true
    - 'todos': Todos los registros
    """
    return service.listar_productos(estado=estado, rubro_id=rubro_id, subrubro_id=subrubro_id)

@router_productos.get("/codigo/next", 
                      summary="Obtener próximo código de Producto (Operación Contadores)",
                      response_model=int)
def obtener_siguiente_codigo(
    service: ProductoService = Depends(get_producto_service)
):
    """
    Genera y reserva el próximo código numérico para un nuevo producto.
    """
    return service.obtener_siguiente_codigo()

@router_productos.patch("/{id}", 
                        response_model=ProductoModel,
                        summary="Actualizar Producto (PATCH)")
def actualizar_producto(
    id: str, 
    data: ProductoUpdateModel, 
    service: ProductoService = Depends(get_producto_service)
):
    """
    Actualiza parcialmente un producto (nombre, descripcion, etc.).
    """
    updated = service.actualizar_producto(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return updated

@router_productos.delete("/{id}", 
                         status_code=status.HTTP_204_NO_CONTENT,
                         summary="Baja Lógica (Doctrina VIL)")
def baja_logica_producto(
    id: str, 
    service: ProductoService = Depends(get_producto_service)
):
    """
    Realiza una baja lógica (Doctrina VIL) del producto.
    Establece baja_logica = true.
    """
    if not service.baja_logica_producto(id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {}