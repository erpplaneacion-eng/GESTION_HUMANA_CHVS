# CONFIGURACIÓN DE GMAIL PARA RAILWAY

## IMPORTANTE: NO NECESITAS VARIABLES SEPARADAS

Para Railway, debes subir el **archivo completo `token.json` como una variable de entorno**.

---

## 📋 PASOS PARA CONFIGURAR GMAIL EN RAILWAY:

### Paso 1: Preparar el contenido del token.json

Abre el archivo `token.json` en la raíz del proyecto y copia TODO su contenido (es un JSON en una sola línea).

### Paso 2: Ir a Railway

1. Ve a: https://railway.app
2. Inicia sesión
3. Selecciona tu proyecto: **gestionhumanachvs-production**
4. Haz clic en el **servicio web** (no la base de datos)
5. Ve a la pestaña **"Variables"**

### Paso 3: Agregar la variable de entorno

Crea UNA sola variable:

- **Nombre**: `GMAIL_TOKEN_JSON`
- **Valor**: Copia TODO el contenido JSON del archivo `token.json` de tu proyecto (pegarlo sin espacios extra al inicio o final)

⚠️ **IMPORTANTE**: El valor debe ser el JSON completo en una sola línea, exactamente como está en tu archivo local.

### Paso 4: Aplicación automática

El código ya está configurado para:
1. Primero intentar leer de la variable de entorno `GMAIL_TOKEN_JSON` (Railway)
2. Si no existe, buscar el archivo `token.json` en el disco (desarrollo local)

---

## ⚠️ NOTAS IMPORTANTES:

1. **El token tiene fecha de expiración**: Revisa el campo `"expiry"` en tu `token.json`
   - Antes de esa fecha, necesitarás generar un nuevo token
   - El código automáticamente lo refrescará si hay `refresh_token`

2. **Seguridad**: Este token permite enviar correos desde la cuenta de Gmail asociada
   - No lo compartas públicamente
   - No lo subas a GitHub (está en `.gitignore`)

3. **Testing**: Después de configurar, prueba enviando un formulario desde tu aplicación desplegada

---

## 🔄 Para generar un nuevo token (si expira):

Si el token expira, necesitarás:

1. Tener el archivo `credentials.json` original de Google Cloud Console
2. Ejecutar el script de autorización de Google OAuth
3. Obtener un nuevo `token.json`
4. Actualizar la variable `GMAIL_TOKEN_JSON` en Railway con el nuevo contenido

---

## ✅ Checklist:

- [ ] Variable `GMAIL_TOKEN_JSON` creada en Railway
- [ ] Valor JSON copiado correctamente desde `token.json` local (sin espacios extra)
- [ ] Aplicación redesplegada en Railway
- [ ] Probar envío de formulario desde producción

