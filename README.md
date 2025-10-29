# Sistema de Gestión Humana - CHVS

Sistema web para la gestión de información del personal, registro de experiencia laboral, formación académica y posgrados.

## 🚀 Características

- ✅ Registro público de personal
- ✅ Gestión de experiencia laboral con cálculo automático
- ✅ Registro de formación académica
- ✅ Gestión de posgrados
- ✅ Panel administrativo para personal autorizado
- ✅ Búsqueda y filtrado de personal
- ✅ Exportación de certificados laborales
- ✅ Base de datos PostgreSQL

## 🛠️ Tecnologías

- **Backend:** Django 5.2.7
- **Base de Datos:** PostgreSQL
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Servidor:** Gunicorn
- **Despliegue:** Railway

## 📋 Requisitos

- Python 3.13.0
- PostgreSQL
- pip

## 🔧 Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/gestion-humana-chvs.git
cd gestion-humana-chvs
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` dentro de la carpeta `gestion_humana/`:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Ejecutar migraciones

```bash
cd gestion_humana
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Accede a: `http://localhost:8000`

## 🌐 Despliegue en Railway

Ver [DEPLOYMENT.md](gestion_humana/DEPLOYMENT.md) para instrucciones detalladas.

### Resumen rápido:

1. **Subir a GitHub**
2. **Conectar con Railway**
3. **Agregar PostgreSQL**
4. **Configurar variables de entorno:**
   ```
   SECRET_KEY=tu-clave-secreta-produccion
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   ```

## 📁 Estructura del Proyecto

```
GESTION_HUMANA_CHVS/
├── gestion_humana/           # Proyecto Django
│   ├── gestion_humana/       # Configuración del proyecto
│   │   ├── settings.py       # Configuraciones
│   │   ├── urls.py          # URLs principales
│   │   └── wsgi.py          # WSGI application
│   ├── formapp/             # App principal
│   │   ├── models.py        # Modelos de base de datos
│   │   ├── views.py         # Vistas
│   │   ├── forms.py         # Formularios
│   │   ├── admin.py         # Configuración admin
│   │   └── templates/       # Templates HTML
│   ├── static/              # Archivos estáticos
│   ├── media/               # Archivos subidos
│   ├── templates/           # Templates base
│   └── manage.py            # Django CLI
├── requirements.txt         # Dependencias Python
├── runtime.txt             # Versión de Python
├── Procfile               # Comando de inicio
├── railway.json           # Configuración Railway
└── README.md             # Este archivo
```

## 🔐 Credenciales por Defecto

**Panel de Administración:** `/admin/`
- Usuario: `admin`
- Contraseña: `admin123`

**⚠️ IMPORTANTE:** Cambia estas credenciales en producción.

## 📝 Uso

### Para Usuarios (Público)

1. Accede a `/formapp/registro/`
2. Completa el formulario con tus datos personales
3. Agrega experiencia laboral (con certificados)
4. Agrega formación académica
5. Agrega posgrados (opcional)
6. Envía el formulario

### Para Administradores

1. Inicia sesión en `/admin/`
2. Gestiona registros de personal
3. Completa información administrativa
4. Revisa y edita registros
5. Exporta reportes

## 🎯 Funcionalidades Principales

### 1. Registro de Personal
- Información personal (nombre, cédula, dirección, contacto)
- Validaciones automáticas (cédula, teléfono, email)

### 2. Experiencia Laboral
- Fechas de inicio y fin
- Cálculo automático de meses y días
- Carga de certificados laborales
- Funciones y objeto contractual

### 3. Formación Académica
- Profesión y universidad
- Tarjeta profesional
- Fecha de grado
- Meses de experiencia por profesión

### 4. Posgrados
- Nombre del posgrado
- Universidad
- Fecha de terminación
- Meses de experiencia

### 5. Panel Administrativo
- Campos administrativos resaltados
- Perfil profesional
- Área de conocimiento
- Observaciones

## 🔒 Seguridad

- ✅ SECRET_KEY única y segura
- ✅ DEBUG=False en producción
- ✅ HTTPS obligatorio
- ✅ Cookies seguras
- ✅ Protección CSRF
- ✅ Validación de datos
- ✅ Autenticación requerida para admin

## 📊 Base de Datos

### Modelos Principales:

- **InformacionBasica**: Datos personales y profesionales
- **ExperienciaLaboral**: Historial laboral
- **InformacionAcademica**: Formación académica
- **Posgrado**: Estudios de posgrado
- **CalculoExperiencia**: Cálculos automáticos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia privada para uso de CHVS.

## 👥 Autor

Desarrollado para CHVS - Sistema de Gestión Humana

## 📞 Soporte

Para soporte técnico o consultas, contacta al administrador del sistema.

---

**© 2025 CHVS - Todos los derechos reservados**
