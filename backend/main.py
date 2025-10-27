# backend/main.py (CON CONFIGURACIÓN CORS)

from fastapi import FastAPI
# --- INICIO: Añadir importaciones CORS ---
from fastapi.middleware.cors import CORSMiddleware
# --- FIN: Añadir importaciones CORS ---

# Importa tus routers aquí (asegúrate que la ruta sea correcta)
from app.modulos.rubros import router as rubros_router
# from app.modulos.productos import router as productos_router # Ejemplo si tuvieras más

app = FastAPI(title="Sonido Líquido V4 API", version="0.1.0")

# --- INICIO: Configuración CORS Middleware ---
# Lista de orígenes permitidos. Para desarrollo, localhost:5173 es común.
# En producción, deberías poner la URL real de tu frontend.
# El asterisco '*' permite TODO origen, ÚTIL PARA DESARROLLO, pero INSEGURO para producción.
origins = [
    "http://localhost:5173", # Origen de tu frontend Vite
    "http://127.0.0.1:5173", # A veces el navegador usa esta IP
    # Podrías añadir la URL de producción aquí después:
    # "https://tu-dominio-de-produccion.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Lista de orígenes permitidos
    allow_credentials=True, # Permite cookies (si las usaras)
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Permite todos los encabezados
)
# --- FIN: Configuración CORS Middleware ---

# Incluye los routers de tus módulos
app.include_router(rubros_router.router, prefix="/rubros", tags=["Rubros"])
# app.include_router(productos_router.router, prefix="/productos", tags=["Productos"]) # Ejemplo

# Ruta raíz simple (opcional)
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Sonido Líquido V4"}

# (Puedes tener más configuraciones o lógica aquí si es necesario)