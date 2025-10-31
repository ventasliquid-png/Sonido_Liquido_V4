# backend/main.py (V12.4 - Integración Final)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa tus routers aquí (Ambos)
from app.modulos.rubros.router import router as rubros_router
from app.modulos.subrubros.router import router as subrubros_router


app = FastAPI(title="Sonido Líquido V4 API", version="0.1.0")

# --- Configuración CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- FIN CORS ---

# Incluye los routers de tus módulos (Ambos)
app.include_router(rubros_router, prefix="/rubros", tags=["Rubros"])
app.include_router(subrubros_router, prefix="/subrubros", tags=["Sub-Rubros"])


@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Sonido Líquido V4"}