# backend/app/modulos/productos/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal # <--- DOCTRINA V2.0 APLICADA

# --- Sub-modelos ---
class UnidadMinimaEmpaqueModel(BaseModel):
    descripcion: str
    unidades: float

class StockDepositoModel(BaseModel):
    deposito_id: str
    stock_real: float

class ComponenteKitModel(BaseModel):
    producto_id: str
    cantidad: float

# --- Modelo Principal v2.0: El Canon Corregido ---
class ProductoModel(BaseModel):
    # 1. Identificación y Datos Maestros
    id: Optional[str] = None
    sku: str = Field(..., max_length=8)
    nombre: str = Field(..., max_length=30)
    codigo_bas: Optional[str] = Field(None, max_length=8)
    observaciones: Optional[str] = Field(None, max_length=60)
    baja_logica: bool = False

    # 2. Costos y Precios (CORREGIDO V2.0)
    precio_costo: Decimal # <-- CONFORME A DOCTRINA
    moneda_costo: str
    precio_base_venta: Decimal # <-- CONFORME A DOCTRINA

    # 3. Gestión y Logística (Unidades)
    unidad_medida: str
    unidad_minima_pedido: float
    unidad_minima_empaque: UnidadMinimaEmpaqueModel

    # 4. Gestión de Stock (Multi-Depósito - SEMILLA)
    stock_minimo_pedido: float
    stock_depositos: List[StockDepositoModel] = []
    stock_comprometido: float
    stock_entrante: float

    # 5. Kits (Conjuntos - SEMILLA)
    es_kit: bool = False
    componentes_kit: List[ComponenteKitModel] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True # <-- Requerido para Decimal

# --- Modelo de Actualización v2.0 (Para Enmienda PATCH) ---
class ProductoUpdateModel(BaseModel):
    # Modelo para actualizaciones parciales (PATCH)
    sku: Optional[str] = Field(None, max_length=8)
    nombre: Optional[str] = Field(None, max_length=30)
    codigo_bas: Optional[str] = Field(None, max_length=8)
    observaciones: Optional[str] = Field(None, max_length=60)
    baja_logica: Optional[bool] = None

    # --- CORREGIDO V2.0 ---
    precio_costo: Optional[Decimal] = None
    moneda_costo: Optional[str] = None
    precio_base_venta: Optional[Decimal] = None
    # -----------------------

    unidad_medida: Optional[str] = None
    unidad_minima_pedido: Optional[float] = None
    unidad_minima_empaque: Optional[UnidadMinimaEmpaqueModel] = None
    stock_minimo_pedido: Optional[float] = None
    stock_depositos: Optional[List[StockDepositoModel]] = None
    stock_comprometido: Optional[float] = None
    stock_entrante: Optional[float] = None
    es_kit: Optional[bool] = None
    componentes_kit: Optional[List[ComponenteKitModel]] = None