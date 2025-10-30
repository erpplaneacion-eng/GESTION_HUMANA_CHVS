# 🌩️ Guía Completa: Configuración de Cloudinary en Railway

## 📋 Resumen

Esta guía te ayudará a configurar Cloudinary para subir y almacenar los certificados laborales y archivos PDF del Sistema de Gestión Humana en Railway.

## ✅ Estado Actual de tu Proyecto

Tu proyecto **YA TIENE** configurado Cloudinary:
- ✅ `cloudinary==1.41.0` en `requirements.txt`
- ✅ `django-cloudinary-storage==0.3.0` en `requirements.txt`
- ✅ Configuración completa en `settings.py`
- ✅ Modelos listos para subir archivos

**Solo necesitas agregar las credenciales en Railway.**

---

## 🚀 Paso 1: Obtener Credenciales de Cloudinary

### 1.1 Crear cuenta (si no tienes una)

1. Ve a [https://cloudinary.com](https://cloudinary.com)
2. Click en **"Sign Up for Free"** (Registro Gratuito)
3. Completa el formulario:
   - Email
   - Nombre completo
   - Clave de acceso
4. Verifica tu email

### 1.2 Obtener las credenciales

1. Inicia sesión en [https://cloudinary.com](https://cloudinary.com)
2. Serás redirigido al **Dashboard**
3. En el Dashboard, busca la sección **"Account Details"** o **"Product Environment Credentials"**
4. Encontrarás:

```
Cloud name: [tu-cloud-name]
API Key: [tu-api-key]
API Secret: [tu-api-secret] (click en "Reveal" para verlo)
```

**⚠️ IMPORTANTE:** 
- Copia estos valores EXACTAMENTE como aparecen
- **NUNCA** compartas tu API Secret públicamente
- La cuenta gratuita de Cloudinary es suficiente para tu proyecto

### 1.3 Límites de la cuenta gratuita

La cuenta gratuita incluye:
- ✅ 25 GB de almacenamiento
- ✅ 25 GB de ancho de banda mensual
- ✅ Transformación de imágenes ilimitada
- ✅ Soporte para PDFs

---

## 🔧 Paso 2: Agregar Variables en Railway

### 2.1 Acceder a Railway

1. Ve a [https://railway.app](https://railway.app)
2. Inicia sesión
3. Selecciona tu proyecto **"gestion-humana-chvs"** (o como lo tengas nombrado)

### 2.2 Ir a Variables de Entorno

1. En el dashboard de tu proyecto, busca tu servicio web (no la base de datos)
2. Click en la pestaña **"Variables"**
3. Verás una lista de variables existentes

### 2.3 Agregar las variables de Cloudinary

Click en **"+ New Variable"** y agrega estas tres variables **UNA POR UNA**:

#### Variable 1:
- **Variable name:** `CLOUDINARY_CLOUD_NAME`
- **Value:** `[tu-cloud-name]` (pégalo sin comillas ni espacios)

Click en **"Add"**

#### Variable 2:
- **Variable name:** `CLOUDINARY_API_KEY`
- **Value:** `[tu-api-key]` (pégalo sin comillas ni espacios)

Click en **"Add"**

#### Variable 3:
- **Variable name:** `CLOUDINARY_API_SECRET`
- **Value:** `[tu-api-secret]` (pégalo sin comillas ni espacios)

Click en **"Add"**

### 2.4 Verificar las variables

Tu lista de variables debería verse así:

```
ALLOWED_HOSTS              *.railway.app
CLOUDINARY_API_KEY         123456789012345
CLOUDINARY_API_SECRET      tu-api-secret-secreto
CLOUDINARY_CLOUD_NAME      tu-cloud-name
DATABASE_URL               postgresql://... (automático)
DEBUG                      False
SECRET_KEY                 tu-clave-secreta
```

**⚠️ IMPORTANTE:**
- Los nombres de las variables deben ser **EXACTAMENTE** como se muestran (mayúsculas/minúsculas)
- No agregues espacios antes o después de los valores
- No uses comillas en los valores

---

## 🔄 Paso 3: Reiniciar el Servicio

1. Después de agregar las variables, Railway **automáticamente** reiniciará tu servicio
2. Si no se reinicia automáticamente:
   - Ve a la pestaña **"Deployments"**
   - Click en **"Redeploy"** o **"Manual Deploy"**

---

## ✅ Paso 4: Verificar que Funciona

### 4.1 Verificar en los logs

1. En Railway, ve a **"Deployments"**
2. Click en el último deployment
3. Verifica que no haya errores relacionados con Cloudinary
4. Los logs deberían mostrar que el deployment fue exitoso

### 4.2 Probar subir un archivo

1. Accede a tu aplicación: `https://tu-proyecto.up.railway.app`
2. Ve a: `/formapp/registro/`
3. Completa el formulario
4. En la sección de "Experiencia Laboral", sube un certificado (PDF)
5. Envía el formulario

### 4.3 Verificar en Cloudinary

1. Ve a tu [Dashboard de Cloudinary](https://cloudinary.com/console)
2. Click en **"Media Library"** en el menú lateral
3. Deberías ver una carpeta llamada **"certificados_laborales"**
4. Dentro deberías ver tu archivo PDF subido

### 4.4 Verificar en tu aplicación

1. Ve a la lista de personal: `/formapp/lista/`
2. Click en el registro que acabas de crear
3. Verifica que el certificado se muestre correctamente

---

## 🎯 ¿Qué se almacena en Cloudinary?

Con la configuración actual, estos archivos se suben a Cloudinary:

- ✅ **Certificados laborales** (`certificados_laborales/`)
- ✅ Todos los archivos PDF de experiencia laboral

Los archivos se organizan así en Cloudinary:
```
tu-cloud-name/
  └── certificados_laborales/
      └── formulario_eps_1234567890_1_abc123.pdf
```

---

## 🔍 Cómo Verificar la Configuración en el Código

Tu configuración está en: `gestion_humana/gestion_humana/settings.py`

### Configuración de credenciales (líneas 142-154):

```python
# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Configurar Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)
```

### Configuración de storage (líneas 157-164):

```python
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### Modelo que usa Cloudinary (línea 57):

```python
certificado_laboral = models.FileField(
    upload_to='certificados_laborales/',
    verbose_name='Certificado Laboral o Contractual'
)
```

**✅ Todo está configurado correctamente en tu código.**

---

## 🐛 Solución de Problemas Comunes

### Problema 1: "Archivos no se suben"

**Causa:** Variables de entorno no están configuradas correctamente

**Solución:**
1. Ve a Railway → Variables
2. Verifica que las tres variables existan
3. Verifica que los nombres sean exactos (mayúsculas/minúsculas)
4. Reinicia el servicio

### Problema 2: "Error de autenticación en Cloudinary"

**Causa:** API Secret incorrecto

**Solución:**
1. Ve a tu Dashboard de Cloudinary
2. Copia nuevamente el API Secret
3. Actualiza la variable `CLOUDINARY_API_SECRET` en Railway
4. Reinicia el servicio

### Problema 3: "Cloud name no encontrado"

**Causa:** Cloud name incorrecto

**Solución:**
1. En tu Dashboard de Cloudinary, verifica el Cloud name
2. Actualiza la variable `CLOUDINARY_CLOUD_NAME` en Railway
3. Reinicia el servicio

### Problema 4: "Los archivos se suben pero no se ven"

**Causa:** URL incorrecta o configuración de MEDIA_URL

**Solución:**
1. Verifica que en `settings.py` tengas: `MEDIA_URL = '/media/'`
2. Verifica en Cloudinary Dashboard que los archivos estén ahí
3. Los archivos deberían estar accesibles con la URL completa de Cloudinary

### Problema 5: "Error 413 Request Entity Too Large"

**Causa:** Archivo muy grande

**Solución:**
1. La cuenta gratuita de Cloudinary acepta archivos hasta 10MB
2. Si necesitas archivos más grandes, comprime el PDF
3. O actualiza a un plan pagado de Cloudinary

---

## 📊 Monitorear Uso de Cloudinary

### En el Dashboard de Cloudinary

1. Ve a [https://cloudinary.com/console](https://cloudinary.com/console)
2. Click en **"Usage"** en el menú lateral
3. Verás:
   - **Storage:** Cuánto espacio estás usando
   - **Bandwidth:** Cuánto ancho de banda has consumido
   - **Transformations:** Transformaciones de imágenes

### Límites de la cuenta gratuita

| Recurso | Límite Gratuito |
|---------|----------------|
| Almacenamiento | 25 GB |
| Ancho de banda mensual | 25 GB |
| Transformaciones | Ilimitadas |
| Tamaño máximo por archivo | 10 MB |

---

## 🔒 Seguridad

### Mejores prácticas

✅ **NUNCA** subas tus credenciales a GitHub  
✅ **NUNCA** compartas tu API Secret  
✅ Usa variables de entorno en producción  
✅ La cuenta gratuita es suficiente para empezar  
✅ Monitorea tu uso en el Dashboard  

### Si tus credenciales se filtran

1. Ve a tu Dashboard de Cloudinary
2. Click en **Settings** → **Security**
3. **Regenera** tu API Secret
4. Actualiza la variable en Railway inmediatamente

---

## 📞 ¿Necesitas Ayuda?

### Recursos oficiales

- 📚 [Documentación de Cloudinary](https://cloudinary.com/documentation)
- 📚 [Documentación de django-cloudinary-storage](https://github.com/cloudinary/pycloudinary)
- 📚 [Documentación de Railway](https://docs.railway.app)

### Verificar si Cloudinary está funcionando

Para verificar que todo funciona, puedes probar subiendo un certificado desde:
- Formulario público: `/formapp/registro/`
- Panel de admin: `/admin/formapp/experiencialaboral/add/`

---

## ✅ Checklist Final

- [ ] Cuenta de Cloudinary creada
- [ ] Credenciales obtenidas del Dashboard
- [ ] Variables agregadas en Railway:
  - [ ] `CLOUDINARY_CLOUD_NAME`
  - [ ] `CLOUDINARY_API_KEY`
  - [ ] `CLOUDINARY_API_SECRET`
- [ ] Servicio reiniciado en Railway
- [ ] Archivo de prueba subido exitosamente
- [ ] Archivo visible en Cloudinary Media Library
- [ ] Archivo visible en la aplicación

---

## 🎉 ¡Listo!

Si completaste el checklist, ¡Cloudinary está funcionando perfectamente! 

Todos los certificados laborales que subas se almacenarán automáticamente en Cloudinary y serán accesibles desde cualquier parte del mundo.

**Tu sistema ahora está completamente funcional con:**
- ✅ Base de datos PostgreSQL
- ✅ Almacenamiento de archivos en Cloudinary
- ✅ Archivos estáticos con WhiteNoise
- ✅ HTTPS automático
- ✅ Seguridad configurada

---

**¿Tienes preguntas?** Revisa los logs en Railway o consulta la sección de Solución de Problemas arriba.

**© 2025 CHVS - Sistema de Gestión Humana**

