#!/bin/bash

# ====================================
# Script de inicio para desarrollo local
# Sistema de Gestión Humana CHVS
# ====================================

echo "========================================"
echo "🚀 Iniciando Sistema de Gestión Humana"
echo "========================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ ERROR: No se encontró el archivo .env${NC}"
    echo ""
    echo "Por favor, crea el archivo .env basándote en .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Luego edita .env y completa las credenciales de Cloudinary"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env encontrado${NC}"

# 2. Activar entorno virtual
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Activando entorno virtual...${NC}"
    source venv/bin/activate
elif [ -d "gestion_humana/venv_wsl" ]; then
    echo -e "${GREEN}✅ Activando entorno virtual (venv_wsl)...${NC}"
    source gestion_humana/venv_wsl/bin/activate
else
    echo -e "${YELLOW}⚠️  No se encontró entorno virtual${NC}"
    echo ""
    echo "Creando nuevo entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate

    echo "Instalando dependencias..."
    pip install -r requirements.txt
fi

echo ""

# 3. Verificar dependencias
echo "📦 Verificando dependencias..."
pip list | grep -E "Django|cloudinary|psycopg2" > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Instalando dependencias faltantes...${NC}"
    pip install -r requirements.txt
fi

echo ""

# 4. Verificar token.json para Gmail
if [ ! -f "token.json" ]; then
    echo -e "${YELLOW}⚠️  WARNING: No se encontró token.json${NC}"
    echo "El envío de emails podría no funcionar en local"
    echo "Consulta README_LOCAL.md para configurar Gmail API"
else
    echo -e "${GREEN}✅ Token de Gmail encontrado${NC}"
fi

echo ""

# 5. Aplicar migraciones pendientes
echo "🔄 Verificando migraciones..."
cd gestion_humana
python manage.py migrate --check 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Aplicando migraciones pendientes...${NC}"
    python manage.py migrate
else
    echo -e "${GREEN}✅ Base de datos actualizada${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ Sistema listo para desarrollo local${NC}"
echo "========================================"
echo ""
echo "🌐 Iniciando servidor en http://localhost:8000"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

# 6. Iniciar servidor de desarrollo
python manage.py runserver
