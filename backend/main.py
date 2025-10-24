# backend/main.py
from fastapi import FastAPI

# 1. Importar el router del nuevo módulo de productos
#    Asegúrate de que la ruta 'app.modulos.productos.router' es correcta
#    según la estructura que creamos.
from app.modulos.productos.router import router as productos_router

# Crear la instancia de la aplicación FastAPI
app = FastAPI()

# 2. Registrar (incluir) el router de productos en la aplicación principal
#    Esto hace que todos los endpoints definidos en productos_router
#    estén disponibles bajo el prefijo "/productos" (definido en el router).
app.include_router(productos_router)

# Endpoint raíz de ejemplo (puedes mantenerlo o quitarlo según necesites)
@app.get("/")
def read_root():
    """
    Endpoint raíz para verificar que el backend está operativo.
    """
    return {"message": "TAX-2 Backend v4: Operativo y Listo"}

# Aquí podrías añadir más routers de otros módulos en el futuro
# app.include_router(otro_modulo_router)