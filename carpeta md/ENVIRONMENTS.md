# 🌍 Ambientes de Ejecución - Gestión Humana CHVS

Este documento describe las diferencias entre los ambientes de desarrollo local y producción.

---

## 📊 Comparación de Ambientes

| Característica | 💻 LOCAL (Desarrollo) | ☁️ RAILWAY (Producción) |
|----------------|----------------------|-------------------------|
| **Base de Datos** | SQLite (db.sqlite3) | PostgreSQL |
| **Archivos** | Cloudinary (compartido) | Cloudinary (compartido) |
| **Email Token** | token.json (archivo) | GMAIL_TOKEN_JSON (variable) |
| **DEBUG** | True | False |
| **HTTPS** | No requerido | Obligatorio |
| **Servidor** | Django runserver | Gunicorn |
| **Puerto** | 8000 (local) | Asignado por Railway |
| **URL** | localhost:8000 | gestionhumanachvs-production.up.railway.app |
| **Variables** | Archivo .env | Variables de entorno Railway |
| **Logs** | Consola terminal | Railway logs |
| **Backups BD** | Manual | Automático (Railway) |

---

## 💻 Ambiente Local (Desarrollo)

### Características
- **Propósito**: Desarrollo, testing, debugging
- **Base de datos**: SQLite (archivo local, no compartido)
- **Archivos**: Cloudinary (COMPARTIDO con producción)
- **Velocidad**: Rápido para desarrollo
- **Aislamiento**: Cambios no afectan producción (excepto archivos)

### Configuración

```env
# .env (local)
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # Por defecto
CLOUDINARY_CLOUD_NAME=dk7nufqc4
CLOUDINARY_API_KEY=469542484755534
CLOUDINARY_API_SECRET=mq5qysxpTVs9ArnjnR7o-FH4L2M
```

### Ventajas
✅ Desarrollo rápido sin conexión a internet (excepto Cloudinary)
✅ Base de datos propia para experimentar
✅ Sin costos de hosting
✅ Debugging completo con Django debug toolbar

### Desventajas
⚠️ Los archivos subidos van a Cloudinary de producción
⚠️ Base de datos diferente a producción
⚠️ No replica configuración exacta de producción

### Inicio

```bash
# Opción 1: Script automático
./start_local.sh          # Linux/Mac/WSL
start_local.bat           # Windows

# Opción 2: Manual
source venv/bin/activate  # Activar entorno
cd gestion_humana
python manage.py runserver
```

---

## ☁️ Ambiente Producción (Railway)

### Características
- **Propósito**: Sistema en vivo para usuarios finales
- **Base de datos**: PostgreSQL (gestionada por Railway)
- **Archivos**: Cloudinary (compartido con local)
- **Disponibilidad**: 24/7
- **Seguridad**: HTTPS, variables de entorno encriptadas

### Configuración

Variables de entorno en Railway:

```bash
DEBUG=False
SECRET_KEY=f!9f#&^u#06-4^8)_7ri5mui$2t0hyw5ca4k_0&omq9dmx^a)w
ALLOWED_HOSTS=gestionhumanachvs-production.up.railway.app
DATABASE_URL=postgresql://postgres:fVF...@ballast.proxy.rlwy.net:48363/railway
CLOUDINARY_CLOUD_NAME=dk7nufqc4
CLOUDINARY_API_KEY=469542484755534
CLOUDINARY_API_SECRET=mq5qysxpTVs9ArnjnR7o-FH4L2M
DEFAULT_FROM_EMAIL=erp.planeacion@vallesolidario.com
GMAIL_TOKEN_JSON={"token":"ya29...","refresh_token":"1//05..."}
```

### Ventajas
✅ Alta disponibilidad
✅ Backups automáticos
✅ Escalabilidad automática
✅ SSL/HTTPS incluido
✅ PostgreSQL robusto

### Desventajas
⚠️ Debugging limitado (sin DEBUG=True)
⚠️ Cambios requieren deployment
⚠️ Logs en plataforma Railway

### Deployment

```bash
# Automático al hacer push a main
git add .
git commit -m "Descripción cambios"
git push origin main

# Railway detecta el push y despliega automáticamente
```

---

## 🗄️ Gestión de Datos

### Base de Datos

#### Local → Producción

```bash
# 1. Exportar datos de local
python manage.py dumpdata > backup_local.json

# 2. Subir a producción (Railway CLI)
railway run python manage.py loaddata backup_local.json
```

⚠️ **PELIGRO**: Esto sobrescribe la BD de producción

#### Producción → Local

```bash
# 1. Exportar datos de producción
railway run python manage.py dumpdata > backup_prod.json

# 2. Importar en local
python manage.py loaddata backup_prod.json
```

### Archivos (Cloudinary)

**Automáticamente compartidos** entre ambos ambientes si usan las mismas credenciales:

```
LOCAL                    CLOUDINARY                 PRODUCCIÓN
  ↓                          ↓                          ↓
Subir archivo  →  dk7nufqc4/certificados/  ←  Ver archivo
```

✅ No requiere sincronización manual
⚠️ Borrar en uno = borrar en ambos

---

## 🔒 Seguridad

### Local
- DEBUG=True (muestra errores completos)
- Sin HTTPS (HTTP plano)
- Credenciales en .env (archivo local)
- SQLite sin contraseña

### Producción
- DEBUG=False (oculta errores sensibles)
- HTTPS obligatorio
- Credenciales en variables encriptadas
- PostgreSQL con autenticación

---

## 🧪 Testing

### Local (Recomendado)

```bash
# Ejecutar tests
python manage.py test

# Tests con coverage
coverage run --source='.' manage.py test
coverage report

# Tests de un modelo específico
python manage.py test formapp.tests.TestExperienciaLaboral
```

### Producción (NO Recomendado)

⚠️ **No ejecutar tests en producción** - puede afectar datos reales

---

## 📝 Mejores Prácticas

### Desarrollo Local

1. **Siempre trabajar en rama separada**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Probar localmente antes de push**
   ```bash
   python manage.py test
   python manage.py check
   ```

3. **No modificar .env en Git**
   - .env está en .gitignore
   - Usar .env.example como plantilla

4. **Cuidado con archivos Cloudinary**
   - Archivos subidos en local van a producción
   - Usar prefijos de prueba si es necesario

### Deployment a Producción

1. **Verificar cambios**
   ```bash
   git status
   git diff
   ```

2. **Commit descriptivo**
   ```bash
   git commit -m "feat: Descripción clara del cambio"
   ```

3. **Push a main**
   ```bash
   git push origin main
   ```

4. **Verificar deployment en Railway**
   - Railway → Deployments
   - Revisar logs
   - Probar en la URL de producción

5. **Rollback si hay problemas**
   ```bash
   # En Railway dashboard: Redeploy versión anterior
   ```

---

## 🔍 Debugging

### Local
```python
# En views.py
import pdb; pdb.set_trace()  # Breakpoint

# O usar print()
print(f"DEBUG: {variable}")
```

### Producción
```bash
# Ver logs en tiempo real (Railway CLI)
railway logs

# Buscar error específico
railway logs | grep ERROR
```

---

## 📊 Monitoreo

### Local
- Consola del servidor Django
- Navegador (DevTools F12)

### Producción
- Railway Dashboard → Metrics
- Railway Logs
- Cloudinary Dashboard → Media Library
- Gmail API → Quota monitoring

---

## ⚙️ Migraciones de Base de Datos

### Local

```bash
# 1. Crear migración
python manage.py makemigrations

# 2. Revisar SQL generado
python manage.py sqlmigrate formapp 0001

# 3. Aplicar
python manage.py migrate
```

### Producción

```bash
# Automático en deployment (railway.json)
# O manual:
railway run python manage.py migrate
```

---

## 🚨 Escenarios Comunes

### Agregar Nuevo Campo al Modelo

```bash
# 1. LOCAL: Modificar models.py
# 2. LOCAL: Crear migración
python manage.py makemigrations

# 3. LOCAL: Probar migración
python manage.py migrate

# 4. LOCAL: Probar funcionalidad
python manage.py runserver

# 5. GIT: Commit y push
git add .
git commit -m "feat: Agregar campo X al modelo Y"
git push origin main

# 6. RAILWAY: Deployment automático
# Railway ejecuta migrate automáticamente
```

### Actualizar Dependencia

```bash
# 1. LOCAL: Actualizar requirements.txt
pip install paquete==nueva-version
pip freeze > requirements.txt

# 2. LOCAL: Probar
pip install -r requirements.txt
python manage.py check

# 3. GIT: Push
git add requirements.txt
git commit -m "chore: Actualizar paquete a version X"
git push origin main

# 4. RAILWAY: Deployment automático
```

### Cambiar Variables de Entorno

**Local:**
```bash
# Editar .env
nano .env

# Reiniciar servidor
Ctrl+C
python manage.py runserver
```

**Producción:**
```bash
# 1. Railway Dashboard → Variables
# 2. Editar variable
# 3. Redeploy automático
```

---

## 📚 Recursos

- [Django Settings Best Practices](https://docs.djangoproject.com/en/5.2/topics/settings/)
- [Railway Documentation](https://docs.railway.app/)
- [Cloudinary Django Integration](https://cloudinary.com/documentation/django_integration)

---

**Última actualización: 2025-11-21**
