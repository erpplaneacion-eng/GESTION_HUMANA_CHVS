# ✅ Checklist Final: Resolver Error "Invalid Signature"

## ⚠️ URGENTE: Verificar en Railway

### Paso 1: Verificar Variables en Railway

1. Ve a https://railway.app
2. Click en tu proyecto
3. Click en el servicio WEB (no PostgreSQL)
4. Click en Variables

### Paso 2: Verificar NO Haya Espacios

Para **CADA UNA** de estas variables:

**CLOUDINARY_CLOUD_NAME**
- ✅ Click en "..." (tres puntos)
- ✅ Click en "Edit"
- ✅ VERIFICA que sea exactamente: `dk7nufqc4`
- ✅ No debe tener espacios al inicio
- ✅ No debe tener espacios al final
- ✅ Si tiene espacios, elimínalos y guarda

**CLOUDINARY_API_KEY**
- ✅ Click en "..." (tres puntos)
- ✅ Click en "Edit"
- ✅ VERIFICA que sea exactamente: `862119278775475`
- ✅ No debe tener espacios
- ✅ Guarda

**CLOUDINARY_API_SECRET** ⚠️ ESTA ES LA MÁS IMPORTANTE
- ✅ Click en "..." (tres puntos)
- ✅ Click en "Edit"
- ✅ **COPIA el valor exacto**
- ✅ Vuelve a Cloudinary Dashboard
- ✅ En Settings → Security
- ✅ **COPIA nuevamente el API Secret**
- ✅ **COMPARA** los dos valores carácter por carácter
- ✅ Si NO coinciden, pega el valor correcto de Cloudinary
- ✅ Guarda

### Paso 3: Eliminar y Recrear

Si las variables tienen el formato correcto:

1. **ELIMINA las 3 variables** de Cloudinary
2. Guarda (espera a que reinicie)
3. Vuelve a agregarlas UNA POR UNA
4. Guarda después de cada una
5. Espera a que Railway despliegue

### Paso 4: Esperar el Deploy

1. Ve a Deployments
2. Espera a que termine el deployment más reciente
3. Debe estar en "Active" o "Running"

### Paso 5: Probar

1. Ve a: https://gestionhumanachvs-production.up.railway.app/formapp/registro/
2. Completa el formulario
3. Sube un certificado PDF
4. Envía

---

## ❌ Si TODAVÍA Aparece el Error

### Opción A: Verificar en Cloudinary

1. Ve a https://cloudinary.com/console
2. Settings → Security
3. **Regenera el API Secret**
4. Copia el nuevo valor
5. Actualiza en Railway

### Opción B: Revisar Logs

1. En Railway → Deployments
2. Click en el último deployment
3. Click en "View Logs"
4. Busca errores relacionados con Cloudinary
5. Copia el error completo

### Opción C: Contactar Soporte

Si NADA funciona, necesitarías:

1. Screenshot de las variables en Railway (ocultando valores)
2. Logs de Railway
3. Confirmación de que regeneraste el API Secret

---

## ✅ SI FUNCIONA

Cuando funcione, deberías ver:

1. ✅ "¡Formulario enviado con éxito!"
2. ✅ El archivo en Cloudinary Dashboard
3. ✅ La URL guardada en PostgreSQL

---

**🎉 ¡Buena suerte!**

