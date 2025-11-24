# ✅ Configuración Dual Environment - Resumen

**Fecha**: 2025-11-21
**Objetivo**: Permitir que el proyecto funcione tanto en LOCAL como en PRODUCCIÓN sin conflictos

---

## 📋 Archivos Creados

### Configuración:
- `.env` - Variables locales (NO en git)
- `.env.example` - Plantilla de variables

### Scripts:
- `start_local.sh` - Inicio Linux/Mac/WSL
- `start_local.bat` - Inicio Windows

### Documentación:
- `README_LOCAL.md` - Guía desarrollo local
- `ENVIRONMENTS.md` - Comparación ambientes
- `QUICK_START.md` - Inicio rápido

---

## 🚀 Uso

```bash
# Iniciar servidor local
./start_local.sh    # Linux/Mac/WSL
start_local.bat     # Windows
```

**URL**: http://localhost:8000

---

## 🌍 Ambientes

### LOCAL:
- BD: SQLite
- Archivos: Cloudinary (compartido)
- Email: token.json

### PRODUCCIÓN:
- BD: PostgreSQL
- Archivos: Cloudinary (compartido)
- Email: GMAIL_TOKEN_JSON

---

**Ver documentación completa en README_LOCAL.md**
