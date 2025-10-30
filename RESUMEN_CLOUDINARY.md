# 🎯 Resumen Rápido: Conectar Cloudinary

## ✅ Estado del Proyecto

Tu código **YA ESTÁ CONFIGURADO** para Cloudinary. Solo necesitas agregar las credenciales.

---

## 🚀 Pasos para Activar Cloudinary en Railway

### ⏱️ Tiempo estimado: 5 minutos

### 1️⃣ Obtener Credenciales (2 min)

1. Ve a: [https://cloudinary.com](https://cloudinary.com)
2. Inicia sesión (o crea cuenta gratuita)
3. En el Dashboard, copia:
   - `Cloud name`
   - `API Key`
   - `API Secret`

### 2️⃣ Agregar en Railway (2 min)

1. Ve a tu proyecto en Railway
2. Click en la pestaña **"Variables"**
3. Agrega estas 3 variables:

```
CLOUDINARY_CLOUD_NAME = [tu-cloud-name]
CLOUDINARY_API_KEY = [tu-api-key]
CLOUDINARY_API_SECRET = [tu-api-secret]
```

⚠️ **Sin espacios ni comillas**

### 3️⃣ Probar (1 min)

1. Sube un certificado desde `/formapp/registro/`
2. Verifica en Cloudinary Media Library
3. ¡Listo! ✅

---

## 📋 Variables Necesarias en Railway

```
ALLOWED_HOSTS=*.railway.app
DEBUG=False
SECRET_KEY=tu-clave-secreta

CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

---

## ✅ Configuración en tu Código

Tu código ya tiene todo configurado:

- ✅ `cloudinary` y `django-cloudinary-storage` en requirements.txt
- ✅ Configuración completa en `settings.py`
- ✅ Modelos listos para subir archivos
- ✅ `STORAGES` configurado

**No necesitas cambiar nada en el código.**

---

## 🔍 ¿Cómo Verificar que Funciona?

### Test 1: Logs de Railway
Sin errores de Cloudinary

### Test 2: Subir Archivo
Certificado se sube sin errores

### Test 3: Cloudinary Dashboard
Archivo visible en `/certificados_laborales/`

### Test 4: Ver en la App
Archivo se muestra correctamente

---

## 📚 Guías Completas

- **Guía detallada:** Ver `GUIA_CLOUDINARY.md`
- **Deployment:** Ver `DEPLOYMENT.md`
- **README general:** Ver `README.md`

---

## 🆘 Problemas Comunes

| Problema | Solución |
|----------|----------|
| Archivos no se suben | Verificar 3 variables en Railway |
| Error de autenticación | Verificar API Secret |
| Cloud name no encontrado | Verificar Cloud name |
| Archivos no se ven | Verificar MEDIA_URL en settings |

---

**¿Dudas?** Revisa `GUIA_CLOUDINARY.md` para más detalles.

**© 2025 CHVS**

