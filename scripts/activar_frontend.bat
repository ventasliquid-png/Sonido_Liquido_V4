@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE FRONTEND (VUE.JS)
ECHO ===============================================

REM Navega al directorio raíz del proyecto, sin importar desde dónde se llame al script
cd /d "%~dp0\.."

ECHO Ubicado en la raiz del proyecto. Entrando a la carpeta del frontend...
cd frontend

ECHO Iniciando servidor de desarrollo de Vite...
npm run dev

pause