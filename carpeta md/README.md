# Sistema de Gestión Humana CAVJP

Sistema web completo para la gestión y registro de personal desarrollado con Django. Permite a los candidatos registrarse de forma autónoma y a los administradores gestionar la información del personal, cálculos de experiencia, y exportación de datos.

## 🚀 Características Principales

### Para Candidatos/Usuarios
- ✅ **Formulario de Registro Público**: Interfaz intuitiva y responsiva para registro de datos personales
- ✅ **Experiencia Laboral**: Gestión de múltiples experiencias con certificados digitales
- ✅ **Información Académica**: Registro de títulos profesionales y tarjetas profesionales
- ✅ **Posgrados**: Registro de especializaciones, maestrías y doctorados
- ✅ **Validación en Tiempo Real**: Mensajes de error en español con validaciones robustas
- ✅ **Cálculo Automático**: Sistema calcula automáticamente meses y días de experiencia
- ✅ **Confirmación por Email**: Notificación automática vía Gmail API

### Para Administradores
- 🔐 **Panel de Administración Django**: Gestión completa de registros
- 📊 **Lista de Candidatos**: Vista paginada con búsqueda y filtros
- 📝 **Edición de Registros**: Actualización de información personal y profesional
- 📥 **Exportación de Datos**: 
  - Descarga individual en ZIP con Excel y certificados
  - Descarga consolidada de todo el personal
  - Archivos Excel profesionalmente formateados
- 📈 **Estadísticas**: Conteo de personal, profesionales, posgrados
- 🧮 **Re-cálculo de Experiencia**: Comando de gestión para recalcular

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.7**: Framework web Python
- **PostgreSQL**: Base de datos (en producción)
- **SQLite**: Base de datos de desarrollo
- **Gunicorn**: Servidor WSGI para producción
- **Python 3.13**: Lenguaje de programación

### Frontend
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Iconos vectoriales
- **jQuery**: Manipulación del DOM y AJAX

### Servicios Externos
- **Cloudinary**: Almacenamiento de archivos (certificados)
- **Gmail API**: Envío de correos electrónicos
- **Railway**: Plataforma de despliegue y hosting

### Otros
- **openpyxl**: Generación de archivos Excel
- **Whitenoise**: Servir archivos estáticos

## 📋 Requisitos del Sistema

- Python 3.11 o superior
- PostgreSQL (producción) o SQLite (desarrollo)
- Cuenta de Cloudinary para almacenamiento
- Credenciales de Gmail API para envío de correos
- Railway CLI (opcional para despliegue local)

## 🚀 Instalación y Configuración

> **📘 Para desarrollo local completo**, consulta [README_LOCAL.md](README_LOCAL.md) con instrucciones detalladas.

### Inicio Rápido para Desarrollo Local

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/GESTION_HUMANA_CAVJP.git
cd GESTION_HUMANA_CAVJP

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Ejecutar script de inicio
# En Linux/Mac/WSL:
./start_local.sh

# En Windows:
start_local.bat
```

### Configuración Manual (Alternativa)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/GESTION_HUMANA_CAVJP.git
cd GESTION_HUMANA_CAVJP
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
cd gestion_humana
pip install -r ../requirements.txt
```

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-secret-key-generado
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (desarrollo)
DATABASE_URL=sqlite:///db.sqlite3

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# Gmail API (desarrollo local - JSON completo)
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"..."}
```

### 5. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Usuario Administrador

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://localhost:8000`

## 📁 Estructura del Proyecto

```
GESTION_HUMANA_CAVJP/
├── gestion_humana/                # Directorio del proyecto Django
│   ├── formapp/                   # Aplicación principal
│   │   ├── models.py              # Modelos de datos
│   │   ├── views.py               # Vistas y lógica de negocio
│   │   ├── forms.py               # Formularios y validaciones
│   │   ├── admin.py               # Configuración del admin
│   │   ├── validators.py          # Validadores personalizados
│   │   ├── tests.py               # Tests automatizados
│   │   ├── urls.py                # URLs de la app
│   │   ├── templates/             # Plantillas HTML
│   │   │   └── formapp/
│   │   │       ├── public_form.html          # Formulario público
│   │   │       ├── applicant_list.html       # Lista de candidatos
│   │   │       ├── applicant_detail.html     # Detalle de candidato
│   │   │       ├── applicant_edit.html       # Edición
│   │   │       └── email_confirmacion.html   # Template de email
│   │   └── management/
│   │       └── commands/
│   │           └── recalcular_experiencia.py # Comando de gestión
│   ├── gestion_humana/            # Configuración del proyecto
│   │   ├── settings.py            # Configuración Django
│   │   ├── urls.py                # URLs principales
│   │   └── wsgi.py                # WSGI para producción
│   ├── static/                    # Archivos estáticos
│   │   └── css/
│   │       └── style.css          # Estilos personalizados
│   ├── templates/                 # Plantillas base
│   │   ├── base.html              # Template base
│   │   └── registration/
│   │       ├── login.html
│   │       └── logout.html
│   ├── media/                     # Archivos subidos (desarrollo)
│   └── manage.py
├── requirements.txt               # Dependencias Python
├── Procfile                      # Configuración Railway
├── railway.json                  # Configuración de despliegue
└── README.md                     # Este archivo
```

## 🗄️ Modelos de Datos

### InformacionBasica
Modelo principal que almacena datos personales y profesionales del candidato:
- Información personal (nombre, cédula, género, contacto, dirección)
- Perfil profesional (completado por admin)
- Relaciones: ExperienciaLaboral, InformacionAcademica, Posgrado

### ExperienciaLaboral
Registro de experiencia laboral:
- Cargo y objeto contractual
- Fechas de inicio y fin
- Cálculo automático de meses y días
- Certificado laboral (PDF/JPG/PNG hasta 10MB)
- Validación de fechas (inicial < terminación)

### InformacionAcademica
Títulos profesionales:
- Profesión y universidad
- Tarjeta profesional o resolución
- Fecha de grado y expedición
- Meses de experiencia por profesión

### Posgrado
Especializaciones, maestrías y doctorados:
- Nombre del posgrado
- Universidad
- Fecha de terminación
- Meses de experiencia

### CalculoExperiencia
Cálculos automáticos de experiencia total:
- Total de meses y días
- Conversión a años
- Formato legible "X años y Y meses"

## 🧪 Testing

El proyecto incluye una suite completa de tests automatizados:

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test formapp

# Ejecutar tests con cobertura (requiere coverage.py)
coverage run --source='.' manage.py test
coverage report
```

### Tests Incluidos
- ✅ Validación de modelos
- ✅ Validación de formularios
- ✅ Mensajes de error en español
- ✅ Validadores personalizados
- ✅ Vistas y autenticación
- ✅ Cálculo de experiencia
- ✅ Integración completa

## 🚢 Despliegue en Producción

### Despliegue en Railway

1. **Conectar el Repositorio**
   - Iniciar sesión en Railway.app
   - Nuevo proyecto desde GitHub

2. **Configurar Variables de Entorno**
   
   En la sección "Variables" de Railway, configurar:
   
   ```
   SECRET_KEY=<generar-secret-key-seguro>
   DEBUG=False
   ALLOWED_HOSTS=gestionhumanacavjp-production.up.railway.app
   
   # PostgreSQL (automático con Railway PostgreSQL)
   DATABASE_URL=<auto-configurado-por-railway>
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=<tu-cloud-name>
   CLOUDINARY_API_KEY=<tu-api-key>
   CLOUDINARY_API_SECRET=<tu-api-secret>
   
   # Gmail API
   GMAIL_TOKEN_JSON=<json-completo-de-token>
   ```

3. **Despliegue Automático**
   - Railway detecta el `railway.json` automáticamente
   - Ejecuta migraciones en cada despliegue
   - Recolecta archivos estáticos
   - Inicia Gunicorn

### Variables de Entorno en Railway

```bash
# Python
SECRET_KEY=tu-secret-key-super-seguro
DEBUG=False
ALLOWED_HOSTS=*.railway.app,tu-dominio.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# Gmail API (JSON completo como string)
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"..."}

# Base de datos (auto-configurado por Railway)
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 👥 Usuarios y Permisos

### Perfiles de Usuario

1. **Usuarios Públicos (Sin registro)**
   - Acceso: `/formapp/registro/`
   - Funcionalidad: Completar formulario de registro
   - Sin autenticación requerida

2. **Personal Administrativo (Autenticado)**
   - Acceso: `/formapp/lista/`
   - Funcionalidad: Ver, editar, eliminar registros
   - Requiere inicio de sesión

3. **Superusuario (Django Admin)**
   - Acceso: `/admin/`
   - Funcionalidad: Gestión completa del sistema
   - Creado con `createsuperuser`

## 🔒 Seguridad

- ✅ Autenticación de usuarios con Django Auth
- ✅ Validación de archivos (tipo y tamaño)
- ✅ Protección CSRF en todos los formularios
- ✅ Cédula única por registro
- ✅ Secret Key en variables de entorno
- ✅ DEBUG=False en producción
- ✅ Archivos sensibles en .gitignore
- ✅ HTTPS habilitado en producción

## 📧 Configuración de Email

El sistema utiliza Gmail API para envío de correos:

1. **Crear Proyecto en Google Cloud Console**
2. **Habilitar Gmail API**
3. **Crear Credenciales OAuth 2.0**
4. **Autorizar Dominio o Usuario**
5. **Exportar Token JSON**

Documentación completa: https://developers.google.com/gmail/api/quickstart/python

## 📊 Exportación de Datos

### Formato Individual
```
[Usuario]_Completo.zip
├── [Usuario]_Informacion.xlsx
│   ├── Información Básica
│   ├── Experiencia Laboral
│   ├── Información Académica
│   ├── Posgrados
│   └── Cálculo Experiencia
└── Certificados/
    ├── 1_[Cargo].pdf
    ├── 2_[Cargo].pdf
    └── ...
```

### Formato Consolidado
```
Personal_Completo_[timestamp].zip
├── Personal_Completo.xlsx
└── Personal/
    └── [Usuario_1]/
        ├── [Usuario]_Informacion.xlsx
        └── Certificados/
            └── ...
```

## 🔧 Comandos de Gestión

### Recalcular Experiencia

Si necesitas recalcular la experiencia de todos los registros:

```bash
python manage.py recalcular_experiencia
```

## 🐛 Solución de Problemas

### Error: "No module named 'gestion_humana'"
```bash
# Asegúrate de estar en el directorio correcto
cd gestion_humana
python manage.py [comando]
```

### Error: Archivos estáticos no cargan
```bash
python manage.py collectstatic --noinput
```

### Error: Migraciones pendientes
```bash
python manage.py migrate
```

### Error: Gmail API no envía correos
- Verificar que `GMAIL_TOKEN_JSON` esté configurado
- Verificar permisos de Gmail API
- Revisar logs: `logger.error()` en consola de Railway

## 📝 Validaciones Implementadas

### Información Personal
- ✅ Cédula: 5-10 dígitos, solo números, única
- ✅ Teléfono: Exactamente 10 dígitos, solo números
- ✅ Correo: Formato email válido, debe contener @
- ✅ Género: Selección obligatoria
- ✅ Dirección: Campos obligatorios vs opcionales

### Experiencia Laboral
- ✅ Fecha inicial < fecha terminación
- ✅ Certificado: PDF, JPG, PNG, máximo 10MB
- ✅ Campos obligatorios: cargo, fechas, funciones

### Formularios
- ✅ Validación HTML5 deshabilitada (`novalidate`)
- ✅ Validación Django con mensajes en español
- ✅ Mensajes de error personalizados por campo

## 🔄 Versionado

- **Versión Actual**: 1.0.0
- **Última Actualización**: 2025
- **Django**: 5.2.7
- **Python**: 3.13

## 👨‍💻 Contribuidores

- Desarrollo: Sistema de Gestión Humana CAVJP
- Despliegue: Railway.app
- Almacenamiento: Cloudinary
- Email: Gmail API

## 📞 Soporte

Para soporte técnico o consultas:
- Revisar logs en Railway
- Consultar documentación de Django
- Verificar configuración de variables de entorno

## 📄 Licencia

Este proyecto es de uso interno para Gestión Humana CAVJP.

## 🎯 Roadmap

- [ ] Implementar notificaciones push
- [ ] Panel de estadísticas avanzado
- [ ] Integración con otros sistemas RH
- [ ] App móvil complementaria
- [ ] API REST para integraciones

## ✅ Checklist de Producción

- [x] Tests automatizados completos
- [x] Validaciones de seguridad
- [x] Manejo de errores robusto
- [x] Logs estructurados
- [x] Variables de entorno configuradas
- [x] Archivos estáticos servidos correctamente
- [x] Base de datos optimizada
- [x] Documentación completa
- [x] Backup automático configurado
- [x] Monitoreo de errores

---

**Desarrollado con ❤️ usando Django**