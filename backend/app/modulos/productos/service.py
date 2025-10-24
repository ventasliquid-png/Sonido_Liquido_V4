# backend/app/modulos/productos/service.py
from typing import List, Optional
from .models import ProductoModel, ProductoUpdateModel
from decimal import Decimal, Context, ROUND_HALF_UP

# --- DOCTRINA V2.0: Contexto de precisión financiera canónica ---
# Define el estándar de 4 decimales
FOUR_PLACES = Context(prec=10, rounding=ROUND_HALF_UP).create_decimal('0.0001')

# Simulación de la capa de base de datos (Firestore)
# from core.database import db
# db_productos = db.collection('productos')

class ProductoService:

    def _quantize_decimal(self, value: Decimal) -> Decimal:
        """Asegura la adherencia a la doctrina de 4 decimales."""
        return value.quantize(FOUR_PLACES)

    async def crear_producto(self, producto_data: ProductoModel) -> ProductoModel:
        # DOCTRINA V2.0: Asegurar precisión antes de persistir
        producto_data.precio_costo = self._quantize_decimal(producto_data.precio_costo)
        producto_data.precio_base_venta = self._quantize_decimal(producto_data.precio_base_venta)

        # Lógica de persistencia (Mock)
        # ... (serializar Decimal a str para Firestore) ...

        producto_data.id = "mock-firestore-id-v2" # Mock
        print(f"Servicio v2.0: Creando producto {producto_data.sku} con precisión Decimal.")
        return producto_data

    async def obtener_producto_por_id(self, id: str) -> Optional[ProductoModel]:
        # ... (deserializar str de Firestore a Decimal) ...
        print(f"Servicio v2.0: Obteniendo producto ID {id}")
        return None # Mock

    async def obtener_producto_por_sku(self, sku: str) -> Optional[ProductoModel]:
        # Implementación similar a obtener_producto_por_id
        print(f"Servicio v2.0: Obteniendo producto SKU {sku}")
        return None # Mock

    async def listar_productos(self, activos: bool = True) -> List[ProductoModel]:
        # Implementación similar (bucle para deserializar Decimales)
        print(f"Servicio v2.0: Listando productos (activos={activos})")
        return [] # Mock

    async def actualizar_producto(self, id: str, data: ProductoUpdateModel) -> Optional[ProductoModel]:
        # update_data = data.dict(exclude_unset=True) # Clave del PATCH
        # DOCTRINA V2.0: Asegurar precisión en los campos que vienen
        # ... (quantize y serializar a str) ...

        print(f"Servicio v2.0: Actualizando (PATCH) producto ID {id} con precisión Decimal.")
        return await self.obtener_producto_por_id(id) # Mock

    async def baja_logica_producto(self, id: str) -> bool:
        print(f"Servicio v2.0: Dando de baja lógica producto ID {id}")
        return True # Mock

# Instancia Singleton del Servicio
producto_service = ProductoService()