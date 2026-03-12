# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos esenciales

### Iniciar el servidor de desarrollo
```bash
# Opción rápida (desde la raíz del repo)
./start_local.sh

# Manual
cd gestion_humana
source venv/bin/activate        # Linux/WSL
python manage.py runserver
```

### Migraciones
```bash
cd gestion_humana
python manage.py makemigrations
python manage.py migrate
```

### Ejecutar tests
```bash
cd gestion_humana

# Todos los tests
python manage.py test

# Solo la app formapp
python manage.py test formapp

# Un módulo específico
python manage.py test formapp.tests.test_models

# Una clase específica
python manage.py test formapp.tests.test_models.InformacionBasicaTestCase

# Un test individual
python manage.py test formapp.tests.test_views.ApplicantListViewTest.test_login_required
```

### Comandos de gestión personalizados
```bash
cd gestion_humana

# Recalcular experiencia de todos los candidatos
python manage.py recalcular_experiencias

# Recalcular para una cédula específica (con detalle)
python manage.py recalcular_experiencias --cedula 1234567890 --verbose
```

## Arquitectura general

### Dos aplicaciones Django

1. **`formapp`** — App principal del sistema de gestión de hojas de vida:
   - Registro público de candidatos (sin login) con validaciones estrictas
   - Panel admin para revisar, editar y gestionar candidatos (requiere login)
   - Flujo de corrección: admin solicita correcciones → candidato recibe email con token → actualiza datos
   - Exportación de datos: ZIP individual (PDF certificados + archivos subidos), Excel consolidado
   - Cálculo automático de experiencia laboral (en meses y días)

2. **`basedatosaquicali`** — App de datos históricos de contratos:
   - Almacena contratos históricos cargados desde Excel
   - Se cruza con `formapp` por cédula para enriquecer el cálculo de experiencia
   - Modelos: `ContratoHistorico`, `ConsolidadoBaseDatos`, `ExperienciaTotal`, `PersonalUrl`

### Flujo de experiencia laboral
El cálculo de experiencia total combina dos fuentes:
- Experiencias ingresadas por el candidato en `formapp` (modelo `ExperienciaLaboral`)
- Contratos históricos en `basedatosaquicali` (modelo `ContratoHistorico`)

El modelo `CalculoExperiencia` almacena el resultado consolidado. El servicio `formapp/services.py` contiene la lógica de cálculo; el comando `recalcular_experiencias` lo re-ejecuta en batch.

### Vistas organizadas en módulos
`formapp/views/` está dividido en:
- `views_public.py` — formulario de registro público y actualización por token
- `views_admin.py` — lista, detalle, edición y eliminación de candidatos (login requerido)
- `views_reports.py` — descarga de ZIPs individuales, ZIP masivo, exportación Excel
- `views_public_FIXED.py` — versión legacy (no usar para nuevas funcionalidades)

### Generación de reportes
- `report_generators_pdf.py` — Certificados PDF con ReportLab
- `report_generators_excel.py` — Exportación Excel con openpyxl

### Entornos: desarrollo vs producción
| Aspecto | Desarrollo | Producción (Railway) |
|---|---|---|
| Base de datos | SQLite (`db.sqlite3`) | PostgreSQL (via `DATABASE_URL`) |
| Archivos media | Local (`/media/`) | Cloudinary |
| Email | Puede ser console o Gmail API | Gmail API |
| DEBUG | True | False |

La configuración en `settings.py` detecta automáticamente el entorno por la presencia de `DATABASE_URL`.

### Estados del candidato (`InformacionBasica.estado`)
`RECIBIDO` → `EN_REVISION` → `PENDIENTE_CORRECCION` → `CORREGIDO` → `VERIFICADO` / `RECHAZADO`

El campo `token_correccion` (UUID) se usa para que el candidato acceda a su formulario de actualización sin login, via `/formapp/actualizar-datos/<uuid:token>/`.

## Variables de entorno requeridas (`.env`)
```
SECRET_KEY=
DATABASE_URL=          # Solo en producción; ausente = SQLite
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
```
