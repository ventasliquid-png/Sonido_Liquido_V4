@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE BACKEND (FASTAPI)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%~dp0\.."

ECHO Ubicado en la raiz del proyecto.
ECHO Entrando a la carpeta del backend...
cd backend

ECHO Activando entorno virtual de Python...
IF EXIST venv\Scripts\activate (
    call venv\Scripts\activate
) ELSE (
    ECHO [ERROR] Entorno virtual 'venv' no encontrado.
    pause
    exit /b
)

ECHO Estableciendo ruta de credenciales de Google...
REM Asegúrate que esta ruta sea correcta para tu PC actual
set GOOGLE_APPLICATION_CREDENTIALS="C:\dev\Sonido_Liquido_V4\service-account-v4.json"
ECHO Variable GOOGLE_APPLICATION_CREDENTIALS establecida.

ECHO Iniciando servidor FastAPI con Uvicorn...
uvicorn main:app --reload

ECHO Servidor detenido.
pause