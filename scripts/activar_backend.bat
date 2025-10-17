@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE BACKEND (FASTAPI)
ECHO ===============================================

REM Navega al directorio raíz del proyecto, sin importar desde dónde se llame al script
cd /d "%~dp0\.."

ECHO Ubicado en la raiz del proyecto. Entrando a la carpeta del backend...
cd backend

ECHO Activando entorno virtual de Python...
IF EXIST venv\Scripts\activate (
    call venv\Scripts\activate
) ELSE (
    ECHO [ERROR] Entorno virtual 'venv' no encontrado.
    ECHO Asegurate que la carpeta 'venv' existe dentro de 'backend'.
    pause
    exit /b
)

ECHO Iniciando servidor FastAPI con Uvicorn...
uvicorn main:app --reload

ECHO Servidor detenido.
pause