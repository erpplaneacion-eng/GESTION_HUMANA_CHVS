@echo off
REM ====================================
REM Script de inicio para desarrollo local (Windows)
REM Sistema de Gestión Humana CHVS
REM ====================================

echo ========================================
echo 🚀 Iniciando Sistema de Gestión Humana
echo ========================================
echo.

REM 1. Verificar que existe .env
if not exist ".env" (
    echo ❌ ERROR: No se encontró el archivo .env
    echo.
    echo Por favor, crea el archivo .env basándote en .env.example:
    echo   copy .env.example .env
    echo.
    echo Luego edita .env y completa las credenciales de Cloudinary
    pause
    exit /b 1
)

echo ✅ Archivo .env encontrado

REM 2. Activar entorno virtual
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No se encontró entorno virtual
    echo.
    echo Creando nuevo entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat

    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo.

REM 3. Verificar token.json para Gmail
if not exist "token.json" (
    echo ⚠️  WARNING: No se encontró token.json
    echo El envío de emails podría no funcionar en local
    echo Consulta README_LOCAL.md para configurar Gmail API
) else (
    echo ✅ Token de Gmail encontrado
)

echo.

REM 4. Aplicar migraciones pendientes
echo 🔄 Verificando migraciones...
cd gestion_humana
python manage.py migrate

echo.
echo ========================================
echo ✅ Sistema listo para desarrollo local
echo ========================================
echo.
echo 🌐 Iniciando servidor en http://localhost:8000
echo.
echo Para detener el servidor, presiona Ctrl+C
echo.

REM 5. Iniciar servidor de desarrollo
python manage.py runserver
