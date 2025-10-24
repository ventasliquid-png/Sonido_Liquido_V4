# backend/app/modulos/productos/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .models import ProductoModel, ProductoUpdateModel # <-- Importa modelos v2.0
from .service import producto_service, ProductoService # <-- Importa servicio v2.0

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# Inyección de Dependencia del Servicio
async def get_service() -> ProductoService:
    return producto_service

@router.post("/", response_model=ProductoModel, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    producto_data: ProductoModel, # <-- Pydantic v2.0 valida Decimal
    service: ProductoService = Depends(get_service)):
    sku_existente = await service.obtener_producto_por_sku(producto_data.sku)
    if sku_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El SKU {producto_data.sku} ya existe."
        )
    return await service.crear_producto(producto_data)

@router.get("/", response_model=List[ProductoModel])
async def listar_productos(
    activos: bool = True, 
    service: ProductoService = Depends(get_service)):
    return await service.listar_productos(activos)

@router.get("/id/{producto_id}", response_model=ProductoModel)
async def obtener_producto_por_id(
    producto_id: str, 
    service: ProductoService = Depends(get_service)):
    producto = await service.obtener_producto_por_id(producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.get("/sku/{sku}", response_model=ProductoModel)
async def obtener_producto_por_sku(
    sku: str, 
    service: ProductoService = Depends(get_service)):
    producto = await service.obtener_producto_por_sku(sku)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.patch("/{producto_id}", response_model=ProductoModel)
async def actualizar_producto(
    producto_id: str, 
    producto_data: ProductoUpdateModel, # <-- Pydantic v2.0 valida Decimal
    service: ProductoService = Depends(get_service)):
    producto = await service.actualizar_producto(producto_id, producto_data)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def baja_logica_producto(
    producto_id: str, 
    service: ProductoService = Depends(get_service)):
    exito = await service.baja_logica_producto(producto_id)
    if not exito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return