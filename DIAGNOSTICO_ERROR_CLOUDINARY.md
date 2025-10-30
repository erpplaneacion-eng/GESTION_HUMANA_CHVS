# 🔍 Diagnóstico Detallado: Error "Invalid Signature"

## ⚠️ ERROR ACTUAL

```
Error al guardar el formulario: Invalid Signature e717cfc498e49c10d77844ffd6157601a7d7479e
String to sign - 'folder=media/certificados_laborales&tags=media&timestamp=1761840442&use_filename=1'
```

---

## 🔬 ANÁLISIS DETALLADO

### ✅ Lo que está BIEN

1. **Credenciales configuradas** - Las 3 variables están en Railway
2. **Código correcto** - La configuración en settings.py es correcta
3. **Cloudinary intenta subir** - El error viene de Cloudinary, no de Django

### ❌ Posibles CAUSAS

#### Causa 1: API_SECRET Tiene un Carácter Incorrecto ⚠️

**TÚ TENDRÍAS QUE VERIFICAR:**

En Railway, el valor del `CLOUDINARY_API_SECRET` que mostraste era:
```
H29cbSnPJd_SYlFxOv039mc_wZE
```

Pero en el mensaje original me pasaste:
```
H29cbSnPJd_SYlFxOv039mc_wZE
```

**Puede haber:**
- Un espacio al inicio o al final
- Un carácter especial que no se ve
- Una diferencia sutil

#### Causa 2: Railway No Reinició Correctamente

**SÍNTOMA:** Variables actualizadas pero el servicio usa valores antiguos

**SOLUCIÓN:**
1. En Railway, elimina TODAS las variables de Cloudinary
2. Guarda (debe reiniciar)
3. Vuelve a agregarlas UNA POR UNA
4. Guarda después de cada una

#### Causa 3: Problema con django-cloudinary-storage 0.3.0

**POSIBLE SOLUCIÓN:** Actualizar la versión

#### Causa 4: Desincronización de Timestamp

**SÍNTOMA:** El timestamp que genera Django no coincide con Cloudinary

**SOLUCIÓN:** Verificar en los logs de Railway la hora del sistema

---

## 🎯 SOLUCIONES A PROBAR (EN ORDEN)

### Solución 1: Verificar que NO haya Espacios

1. Ve a Railway → Variables
2. Click en cada variable de Cloudinary
3. Verifica que al INICIO y al FINAL no haya espacios
4. Si hay espacios, edita y quítalos
5. Guarda

### Solución 2: Eliminar y Recrear Variables

1. Ve a Railway → Variables
2. Elimina:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Guarda (espera a que reinicie)
4. Agrega de nuevo:
   ```
   CLOUDINARY_CLOUD_NAME=dk7nufqc4
   ```
   Guarda y espera
   
   ```
   CLOUDINARY_API_KEY=862119278775475
   ```
   Guarda y espera
   
   ```
   CLOUDINARY_API_SECRET=H29cbSnPJd_SYlFxOv039mc_wZE
   ```
   Guarda y espera

### Solución 3: Actualizar django-cloudinary-storage

```bash
pip install --upgrade django-cloudinary-storage
```

Actualiza en `requirements.txt`:
```txt
django-cloudinary-storage==0.3.2
```

### Solución 4: Agregar Configuración Manual en settings.py

Actualiza `gestion_humana/gestion_humana/settings.py`:

```python
# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# IMPORTANTE: Configurar Cloudinary explícitamente
import cloudinary

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME', default=''),
    api_key=config('CLOUDINARY_API_KEY', default=''),
    api_secret=config('CLOUDINARY_API_SECRET', default=''),
    secure=True
)

# Configuración de STORAGE (Cloudinary para media, WhiteNoise para estáticos)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Agregar esto
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Solución 5: Verificar en Cloudinary Dashboard

1. Ve a https://cloudinary.com/console
2. Verifica que tu cuenta esté activa
3. Ve a Settings → Security
4. Verifica que el API Secret sea el correcto
5. Si sospechas, regenera el API Secret y úsalo en Railway

---

## 🔍 VERIFICACIÓN EN LOGS DE RAILWAY

1. Ve a Railway → Deployments
2. Click en el último deployment
3. Click en "View Logs"
4. Busca errores relacionados con Cloudinary
5. Verifica que las variables estén siendo leídas

**Busca mensajes como:**
- "Cloudinary configured successfully"
- "Invalid API credentials"
- Cualquier error relacionado con Cloudinary

---

## 📊 CHECKLIST DE DIAGNÓSTICO

- [ ] Variables están en el servicio WEB (no PostgreSQL)
- [ ] Nombre exacto: `CLOUDINARY_CLOUD_NAME` (no otro nombre)
- [ ] Nombre exacto: `CLOUDINARY_API_KEY`
- [ ] Nombre exacto: `CLOUDINARY_API_SECRET`
- [ ] Cloud name es: `dk7nufqc4`
- [ ] API Key es: `862119278775475`
- [ ] API Secret es: `H29cbSnPJd_SYlFxOv039mc_wZE`
- [ ] NO hay espacios al inicio
- [ ] NO hay espacios al final
- [ ] Railway reinició después de guardar
- [ ] Logs de Railway no muestran errores

---

## 🆘 PRÓXIMOS PASOS

1. **PRIMERO:** Verifica que NO haya espacios en las credenciales
2. **SEGUNDO:** Elimina y recrea las variables
3. **TERCERO:** Revisa los logs de Railway para más información
4. **CUARTO:** Si nada funciona, prueba actualizar django-cloudinary-storage

---

## 📞 Información para Debugging

Si el problema persiste, necesitaría:

1. Screenshot de las variables en Railway (puedes ocultar los valores)
2. Logs de Railway del deployment más reciente
3. Confirmación de que eliminaste y recreaste las variables

---

**© 2025 CHVS - Sistema de Gestión Humana**

