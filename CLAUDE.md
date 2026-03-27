# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos esenciales

### Iniciar el servidor de desarrollo
```bash
# Opción rápida (desde la raíz del repo)
./start_local.sh

# Manual
cd gestion_humana
source venv_wsl/bin/activate   # WSL/Linux
# En Windows: venv\Scripts\activate
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

# Cargar datos históricos de contratos desde Excel (basedatosaquicali)
# Requiere el archivo link.xlsx en el directorio de trabajo
python manage.py cargar_historico
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

### Modelos principales de `formapp`
Todos los modelos secundarios tienen FK a `InformacionBasica` (el candidato):
- `ExperienciaLaboral` — experiencias declaradas por el candidato
- `InformacionAcademica` — título profesional universitario
- `EducacionBasica` — bachillerato
- `EducacionSuperior` — técnico / tecnólogo (incluye campo `tiene_tarjeta_profesional`)
- `Posgrado` / `Especializacion` — estudios de posgrado
- `DocumentosIdentidad` — OneToOne: cédula, hoja de vida, libreta militar
- `Antecedentes` — OneToOne: Procuraduría, Contraloría, Policía, RNMC, REDAM, delitos sexuales
- `AnexosAdicionales` — OneToOne: EPS, pensión, RUT, examen ocupacional, etc.
- `CalculoExperiencia` — OneToOne: resultado consolidado del cálculo de experiencia
- `HistorialCorreccion` — registro de solicitudes de corrección del admin y respuestas del candidato

### Flujo de experiencia laboral
`services.calcular_experiencia_total()` combina:
- `ExperienciaLaboral` (declaradas por el candidato)
- `ContratoHistorico` (históricos en `basedatosaquicali`, buscados por cédula numérica)

Usa un **algoritmo de fusión de intervalos** para eliminar traslapes. La base de cálculo es 365 días/año y 30 días/mes. El resultado se guarda en `CalculoExperiencia`.

> **Importante:** `InformacionBasica.cedula` es `CharField`; `ContratoHistorico.cedula` es `BigIntegerField`. La conversión `int(cedula)` ocurre en `services.py` al hacer el cruce.

### Rutas URL clave
- `/formapp/` — formulario público de registro de candidatos
- `/formapp/actualizar-datos/<uuid:token>/` — formulario de corrección por token (sin login)
- `/formapp/admin/applicants/` — lista de candidatos (requiere login)
- `/formapp/admin/applicants/<pk>/` — detalle, edición, eliminación, solicitar corrección
- `/formapp/admin/download-all/` — descarga ZIP masivo de todos los candidatos
- `/formapp/admin/applicants/<pk>/download/` — ZIP individual
- `/historico/buscar/` — búsqueda en base de datos histórica de contratos
- `/admin/` — Django admin

### Vistas organizadas en módulos
`formapp/views/` está dividido en:
- `views_public.py` — formulario de registro público y actualización por token
- `views_admin.py` — lista, detalle, edición y eliminación de candidatos (login requerido)
- `views_reports.py` — descarga de ZIPs individuales, ZIP masivo con descarga paralela (ThreadPoolExecutor)
- `views_public_FIXED.py` — archivo legacy, **no modificar ni usar**

### Generación de reportes
- `report_generators_pdf.py` — Certificados PDF con ReportLab
- `report_generators_excel.py` — Exportación Excel con openpyxl
- `report_generators.py` — wrapper de compatibilidad que re-exporta las dos funciones anteriores; no contiene lógica propia

### Formularios (`forms.py`)
- `InformacionBasicaPublicForm` — campos visibles al candidato en registro público
- `InformacionBasicaAdminForm` — campos adicionales editables por admin
- Formsets via `inlineformset_factory` para `ExperienciaLaboral`, `InformacionAcademica`, `Posgrado`, `Especializacion`, `DocumentosIdentidad`, `Antecedentes`, `AnexosAdicionales`

### Validaciones de archivos
Los `FileField` usan tres validadores en `formapp/validators.py`:
- `validate_file_size` — máximo 10 MB
- `validate_file_extension` — solo PDF, JPG, PNG
- `validate_file_mime` — verifica el tipo MIME real del archivo (requiere `python-magic`; en producción Railway, `nixpacks.toml` instala `libmagic1`)

### Envío de correos
`services.py` usa Gmail API (OAuth2) con `token.json` local o variable de entorno `GMAIL_TOKEN_JSON`. Las funciones de envío son:
- `enviar_correo_confirmacion()` — al registrarse el candidato
- `enviar_correo_solicitud_correccion()` — genera token 48h y envía enlace al candidato
- `enviar_correo_notificacion_admin()` — cuando el candidato completa una corrección
- `enviar_correo_async()` — wrapper que llama a confirmación en un thread daemon

### Entornos: desarrollo vs producción
| Aspecto | Desarrollo | Producción (Railway) |
|---|---|---|
| Base de datos | SQLite (`db.sqlite3`) | PostgreSQL (via `DATABASE_URL`) |
| Archivos media | Local (`/media/`) | Cloudinary |
| Email | Gmail API con `token.json` local | Gmail API con `GMAIL_TOKEN_JSON` env var |
| DEBUG | True | False |

La configuración en `settings.py` detecta automáticamente el entorno por la presencia de `DATABASE_URL`.

La versión de Python es **3.13.0** (definida en `runtime.txt`). WhiteNoise sirve los archivos estáticos en producción. El dominio Railway (`anacavjp.up.railway.app`) está hardcodeado en `CSRF_TRUSTED_ORIGINS` dentro de `settings.py`.

El comando de inicio en producción (definido en `railway.json`):
```
cd gestion_humana && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT --log-file - gestion_humana.wsgi:application
```

### Estados del candidato (`InformacionBasica.estado`)
`RECIBIDO` → `EN_REVISION` → `PENDIENTE_CORRECCION` → `CORREGIDO` → `VERIFICADO` / `RECHAZADO`

El campo `token_correccion` (UUID) expira en 48 horas y permite al candidato acceder a su formulario sin login via `/formapp/actualizar-datos/<uuid:token>/`.

### Suite de tests
Los tests están en `formapp/tests/`:
- `test_models.py` — modelos principales
- `test_models_documents.py` — modelos de documentos
- `test_forms.py` — validaciones de formularios
- `test_views.py` — vistas admin y públicas
- `test_correction_flow.py` — flujo completo de corrección con token
- `test_experiencias_historicas.py` — cálculo de experiencia con datos históricos
- `test_validators.py` — validadores de archivos
- `test_nuevos_campos.py` — campos agregados recientemente

## Variables de entorno requeridas (`.env`)
```
SECRET_KEY=
DATABASE_URL=          # Solo en producción; ausente = SQLite
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
GMAIL_TOKEN_JSON=      # JSON completo del token OAuth2 de Gmail (producción)
ADMIN_EMAIL=           # Email receptor de notificaciones admin
```
