# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modulos.rubros.router import router_rubros
from app.modulos.subrubros.router import router_subrubros
from app.modulos.productos.router import router_productos
from app.modulos.unidades_medida.router import router_unidades_medida
# --- INICIO INTEGRACIÓN HITO F1-50 (IVA) ---
from app.modulos.condiciones_iva.router import router_condiciones_iva
# --- FIN INTEGRACIÓN HITO F1-50 (IVA) ---

# --- Configuración de la Aplicación FastAPI ---
app = FastAPI(
    title="Sonido Liquido V4 Core API",
    description="API de Microservicios Core para la gestión de Rubros, SubRubros, Productos y Unidades de Medida.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Configuración de CORS ---
origins = [
    "http://localhost:5173",  # Dirección del frontend en desarrollo
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusión de Routers (Módulos) ---
app.include_router(router_rubros)
app.include_router(router_subrubros)
app.include_router(router_productos)
app.include_router(router_unidades_medida)
# --- INICIO INTEGRACIÓN HITO F1-50 (IVA) ---
app.include_router(router_condiciones_iva)
# --- FIN INTEGRACIÓN HITO F1-50 (IVA) ---

# --- Ruta Base de Salud ---
@app.get("/", tags=["Salud"], summary="Verificar estado de la API")
def read_root():
    """
    Verifica que la API Core esté operativa.
    """
    return {"message": "API Core V4 Operativa. Módulos: Rubros, SubRubros, Productos, Unidades de Medida, Condiciones IVA."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
