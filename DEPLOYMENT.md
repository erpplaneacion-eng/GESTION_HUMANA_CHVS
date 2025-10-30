# Guía de Despliegue - Sistema de Gestión Humana

## 📋 Requisitos Previos

- Cuenta en GitHub
- Cuenta en Railway (https://railway.app)
- Git instalado localmente

## 🚀 Paso 1: Subir el Proyecto a GitHub

### 1.1 Inicializar repositorio Git

```bash
git init
git add .
git commit -m "Initial commit: Sistema de Gestión Humana"
```

### 1.2 Crear repositorio en GitHub

1. Ve a https://github.com y crea un nuevo repositorio
2. Nombre sugerido: `gestion-humana-chvs`
3. NO inicialices con README, .gitignore o licencia (ya los tienes)

### 1.3 Conectar y subir

```bash
git remote add origin https://github.com/TU_USUARIO/gestion-humana-chvs.git
git branch -M main
git push -u origin main
```

## 🚂 Paso 2: Desplegar en Railway

### 2.1 Crear Proyecto en Railway

1. Inicia sesión en Railway (https://railway.app)
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona el repositorio `gestion-humana-chvs`

### 2.2 Agregar Base de Datos PostgreSQL

1. En tu proyecto de Railway, click en "+ New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway creará automáticamente la base de datos

### 2.3 Configurar Variables de Entorno

En la pestaña "Variables" de tu servicio web, agrega:

```
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiala
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

**IMPORTANTE**: Railway automáticamente inyecta `DATABASE_URL` desde PostgreSQL, no necesitas configurarla manualmente.

#### 2.3.1 Configurar Cloudinary (Para Certificados y Archivos)

Para que los certificados laborales y archivos se suban a Cloudinary, agrega estas tres variables:

```
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

**¿Dónde obtener estas credenciales?**
1. Ve a [https://cloudinary.com](https://cloudinary.com)
2. Inicia sesión o crea una cuenta gratuita
3. En el Dashboard, verás tu **Cloud Name**, **API Key** y **API Secret**
4. Cópialos exactamente como aparecen

**Nota:** No incluyas espacios ni comillas alrededor de los valores.

### 2.4 Generar una SECRET_KEY Segura

Puedes generar una clave secreta segura con Python:

```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 2.5 Deployment

Railway detectará automáticamente:
- `runtime.txt` - Versión de Python
- `requirements.txt` - Dependencias
- `Procfile` - Comando de inicio
- `railway.json` - Configuración de despliegue

El despliegue ejecutará automáticamente:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn gestion_humana.wsgi
```

## 🔧 Paso 3: Post-Despliegue

### 3.1 Crear Superusuario

Desde el panel de Railway, ve a la pestaña "Deploy" y abre la consola:

```bash
python manage.py createsuperuser
```

### 3.2 Verificar el Sitio

Railway te proporcionará una URL como: `https://tu-proyecto.up.railway.app`

Accede a:
- Panel de administración: `https://tu-proyecto.up.railway.app/admin/`
- Registro público: `https://tu-proyecto.up.railway.app/formapp/registro/`
- Login: `https://tu-proyecto.up.railway.app/login/`

## 📁 Estructura de Archivos para Despliegue

```
gestion_humana/
├── .env                    # Variables de entorno (NO subir a GitHub)
├── .env.example            # Plantilla de variables de entorno
├── .gitignore             # Archivos a ignorar en Git
├── requirements.txt        # Dependencias de Python
├── runtime.txt            # Versión de Python
├── Procfile               # Comando de inicio para Railway
├── railway.json           # Configuración de Railway
├── manage.py
├── db.sqlite3             # Base de datos local (NO va a producción)
├── gestion_humana/
│   ├── settings.py        # Configurado para producción
│   ├── urls.py
│   └── wsgi.py
├── formapp/
├── static/
├── staticfiles/           # Archivos estáticos compilados
├── media/                 # Archivos subidos por usuarios
└── templates/
```

## 🔒 Seguridad

### En Producción (Railway):
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` único y seguro
- ✅ `ALLOWED_HOSTS` configurado correctamente
- ✅ Base de datos PostgreSQL
- ✅ HTTPS automático

### En Desarrollo Local:
- ✅ `.env` con `DEBUG=True`
- ✅ SQLite para desarrollo
- ✅ No compartir `.env`

## 🐛 Solución de Problemas

### Error: "DisallowedHost at /"
- Verifica que `ALLOWED_HOSTS` incluya `*.railway.app`
- Reinicia el servicio en Railway

### Error de Migración
- Ejecuta manualmente desde la consola de Railway:
```bash
python manage.py migrate
```

### Archivos Estáticos No Cargan
- Verifica que WhiteNoise esté en `MIDDLEWARE`
- Ejecuta: `python manage.py collectstatic --noinput`

### Base de Datos No Conecta
- Verifica que el servicio PostgreSQL esté corriendo
- Railway debe inyectar automáticamente `DATABASE_URL`

### Errores con Cloudinary / Archivos No Se Suben
- Verifica que las tres variables de Cloudinary estén configuradas:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- Revisa que los valores NO tengan espacios ni comillas
- Si los archivos no se suben, revisa los logs en Railway
- Verifica que tu cuenta de Cloudinary esté activa (cuenta gratuita funciona)

### Archivos No Se Visualizan después de Subirlos
- Los archivos se almacenan en Cloudinary con prefijo `/media/`
- Verifica que `MEDIA_URL = '/media/'` esté en settings.py
- Revisa la URL del archivo en Cloudinary Dashboard

## 📊 Monitoreo

En Railway puedes ver:
- **Logs**: Pestaña "Deployments" → Click en despliegue → "View Logs"
- **Métricas**: CPU, Memoria, Red
- **Variables**: Todas las variables de entorno configuradas

## 🔄 Actualizaciones

Para actualizar tu aplicación:

```bash
git add .
git commit -m "Descripción de cambios"
git push origin main
```

Railway desplegará automáticamente los cambios.

## 📝 Notas Importantes

1. **No subas el archivo `.env` a GitHub** - Contiene información sensible
2. **Usa `.env.example`** como plantilla para otros desarrolladores
3. **La base de datos PostgreSQL** en Railway es automática
4. **Railway ofrece $5 de crédito gratis** mensualmente
5. **Guarda tu `SECRET_KEY`** en un lugar seguro

## 🆘 Soporte

Si tienes problemas:
- Revisa los logs en Railway
- Verifica las variables de entorno
- Consulta la documentación de Railway: https://docs.railway.app
- Revisa la configuración de `settings.py`

---

**¡Buena suerte con tu despliegue! 🚀**
