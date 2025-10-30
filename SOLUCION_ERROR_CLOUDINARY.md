# 🔧 Solución: Error "Invalid Signature" en Cloudinary

## 📋 Problema

Cuando intentas subir un certificado, obtienes este error:

```
Error al guardar el formulario: Invalid Signature 8879a4e9ced60e9bf012256e14d4dc1ec665f4af
```

## ✅ Causa

Este error significa que las **credenciales de Cloudinary están incorrectas** o **no están configuradas** en Railway.

---

## 🚀 Solución: Configurar Credenciales Correctamente

### Paso 1: Obtener tus Credenciales de Cloudinary

1. Ve a [https://cloudinary.com](https://cloudinary.com)
2. Inicia sesión en tu cuenta
3. En el Dashboard, busca la sección **"Account Details"** o ve a **Settings**
4. Copia EXACTAMENTE estos valores:

```
Cloud name: [tu-cloud-name]
API Key: [tu-api-key]
API Secret: [tu-api-secret] ← Click en "Reveal" si está oculto
```

### Paso 2: Configurar en Railway

1. Ve a [https://railway.app](https://railway.app)
2. Selecciona tu proyecto **gestionhumanachvs-production**
3. Click en el servicio web (no la base de datos)
4. Ve a la pestaña **"Variables"**
5. Elimina las variables de Cloudinary que tengas actualmente (si existen)

6. Agrega las 3 variables NUEVAS, UNA POR UNA:

#### Variable 1:
- **Nombre:** `CLOUDINARY_CLOUD_NAME`
- **Valor:** [pega tu cloud-name SIN espacios ni comillas]

#### Variable 2:
- **Nombre:** `CLOUDINARY_API_KEY`
- **Valor:** [pega tu api-key SIN espacios ni comillas]

#### Variable 3:
- **Nombre:** `CLOUDINARY_API_SECRET`
- **Valor:** [pega tu api-secret SIN espacios ni comillas]

### Paso 3: Reiniciar el Servicio

1. Después de agregar las variables, Railway automáticamente reinicia tu servicio
2. Si no se reinicia automáticamente, ve a **"Deployments"** → **"Manual Deploy"**
3. Espera a que termine el despliegue

### Paso 4: Probar

1. Accede a: https://gestionhumanachvs-production.up.railway.app/formapp/registro/
2. Completa el formulario
3. Sube un certificado PDF
4. Envía el formulario

Si sigue el error, verifica en los logs de Railway que las credenciales estén bien.

---

## 🔍 Verificar que Funcionó

### Verificación 1: Logs de Railway

1. En Railway, ve a **"Deployments"**
2. Click en el último deployment
3. Revisa los logs - **NO** debe aparecer el error de "Invalid Signature"

### Verificación 2: Cloudinary Dashboard

1. Ve a tu [Cloudinary Dashboard](https://cloudinary.com/console)
2. Click en **"Media Library"**
3. Deberías ver una carpeta `certificados_laborales`
4. Dentro deberías ver tu archivo PDF subido

### Verificación 3: Tu Aplicación

1. Ve a la lista de personal: `/formapp/lista/`
2. Click en el registro que acabas de crear
3. El certificado debe mostrarse correctamente

---

## ⚠️ Errores Comunes

### Error: Todavía aparece "Invalid Signature"

**Posibles causas:**
1. Las credenciales tienen espacios extras
2. Las credenciales tienen comillas
3. Copiaste mal algún carácter
4. Tu cuenta de Cloudinary no está activa

**Solución:**
- Elimina TODOS los espacios antes y después de los valores
- NO uses comillas en los valores
- Vuelve a copiar las credenciales desde Cloudinary Dashboard
- Verifica que tu cuenta esté activa

### Error: No puedo ver "Reveal" en API Secret

**Solución:**
- El botón "Reveal" está en el Dashboard de Cloudinary
- Si no lo ves, refresh la página
- También puedes regenerar el API Secret en Settings → Security

### Error: Las variables no se guardan en Railway

**Solución:**
- Asegúrate de estar en el servicio WEB (no la base de datos)
- Click en "Save" o "Add" después de cada variable
- Refresca la página para verificar que se guardaron

---

## 📝 Ejemplo Correcto de Variables

**❌ INCORRECTO:**
```
CLOUDINARY_CLOUD_NAME = "mi-cloud-123"
CLOUDINARY_API_KEY = "123456789012345"
CLOUDINARY_API_SECRET = "abc-def-ghi"
```

**✅ CORRECTO:**
```
CLOUDINARY_CLOUD_NAME = mi-cloud-123
CLOUDINARY_API_KEY = 123456789012345
CLOUDINARY_API_SECRET = abc_def_ghi_jkl_mno
```

**Nota:** Sin comillas, sin espacios, exactamente como aparecen en Cloudinary.

---

## 🆘 ¿Aún Tienes Problemas?

1. **Revisa los logs de Railway** para ver errores específicos
2. **Verifica que tu cuenta de Cloudinary esté activa**
3. **Genera un nuevo API Secret** en Cloudinary Dashboard
4. **Contacta al administrador** del sistema

---

## 📚 Recursos Adicionales

- [Documentación de Cloudinary](https://cloudinary.com/documentation)
- [Documentación de django-cloudinary-storage](https://github.com/cloudinary/pycloudinary)
- [GUIA_CLOUDINARY.md](GUIA_CLOUDINARY.md) - Guía completa

---

**© 2025 CHVS - Sistema de Gestión Humana**

