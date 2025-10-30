# 🔐 Solución: Error HTTP 401 al Abrir PDFs en Cloudinary

## ⚠️ PROBLEMA

Cuando intentas abrir un certificado PDF desde tu aplicación, ves:

```
Esta página no funciona
HTTP ERROR 401
```

La URL que genera es:
```
https://res.cloudinary.com/dk7nufqc4/image/upload/v1/media/certificados_laborales/...
```

---

## ✅ SOLUCIÓN

**Cloudinary bloquea la entrega de PDFs por defecto en cuentas gratuitas.**

Necesitas **habilitar manualmente** la entrega de archivos PDF.

---

## 🚀 PASOS PARA RESOLVERLO

### Paso 1: Acceder a Cloudinary

1. Ve a [https://cloudinary.com](https://cloudinary.com)
2. Inicia sesión con tu cuenta
3. Serás redirigido al Dashboard

### Paso 2: Ir a Settings

1. En el menú lateral izquierdo, busca **"Settings"** (Configuración)
2. Click en **"Settings"**

### Paso 3: Ir a Security

1. En las pestañas de Settings, busca **"Security"**
2. Click en **"Security"**

### Paso 4: Habilitar Entrega de PDF y ZIP

1. Desplázate hacia abajo hasta encontrar la sección **"Upload presets"** o **"Security"**
2. Busca la opción: **"PDF and ZIP files delivery"**
3. Verás una casilla: **"Allow delivery of PDF and ZIP files"**
4. **Marca esta casilla** ✅
5. Click en **"Save"** (Guardar)

**Nota:** Puede tomar 1-2 minutos para que los cambios surtan efecto.

### Paso 5: Probar

1. Vuelve a tu aplicación
2. Intenta abrir un certificado PDF
3. Debería funcionar correctamente

---

## 📸 ¿Dónde Está la Opción?

La ubicación exacta es:

```
Cloudinary Dashboard
  └── Settings (menú lateral izquierdo)
      └── Security (pestaña)
          └── Scroll hacia abajo
              └── "PDF and ZIP files delivery"
                  └── ☑️ Allow delivery of PDF and ZIP files
```

---

## 🔍 Verificación

Después de habilitar la opción, puedes verificar:

1. **En Cloudinary Dashboard:**
   - Settings → Security
   - La casilla debe estar marcada

2. **En tu aplicación:**
   - Abre un certificado PDF
   - Debe abrirse sin error 401

3. **URL funcionando:**
   - La URL debe ser accesible
   - El PDF debe descargarse o mostrarse correctamente

---

## ⏱️ Timeout de Cache

**IMPORTANTE:** Después de habilitar la opción, puede tomar:
- **1-2 minutos** para que Cloudinary actualice la configuración
- **5-10 minutos** para que la cache del CDN se limpie

**Si todavía no funciona después de 5 minutos:**
1. Espera un poco más
2. Limpia la cache de tu navegador
3. Intenta en modo incógnito
4. Verifica que la casilla esté guardada en Cloudinary

---

## 🎯 Por Qué Pasa Esto

Cloudinary, por razones de seguridad, bloquea por defecto la entrega pública de:
- Archivos PDF
- Archivos ZIP
- Archivos ejecutables

Esto aplica **especialmente a cuentas gratuitas**.

Debes habilitar manualmente esta opción en Settings → Security.

---

## ✅ Una Vez Habilitado

Después de habilitar esta opción:

- ✅ Todos los PDFs subidos **anteriormente** se volverán accesibles
- ✅ Todos los PDFs subidos **en el futuro** serán accesibles automáticamente
- ✅ Los archivos ZIP también funcionarán
- ✅ No necesitas hacer ningún cambio en el código

---

## 🆘 Si No Encuentras la Opción

Si no encuentras "PDF and ZIP files delivery" en Settings:

### Alternativa 1: Buscar en "Upload"

1. Settings → **"Upload"**
2. Busca "Moderation" o "Security"
3. Busca opciones relacionadas con PDF/ZIP

### Alternativa 2: Verificar Plan

1. Verifica que estés en el plan correcto
2. Si estás en plan gratuito, la opción debe estar disponible
3. Si estás en trial, puede que la opción esté en otra ubicación

### Alternativa 3: Contactar Soporte

1. Si no encuentras la opción en ningún lado
2. Contacta a soporte de Cloudinary
3. Pide específicamente "Enable PDF and ZIP delivery"

---

## 📚 Referencia

- [Documentación oficial de Cloudinary sobre PDFs](https://cloudinary.com/documentation)
- [Soporte de Cloudinary sobre error 401](https://support.cloudinary.com/hc/en-us/articles/360016480179)

---

## ✅ Checklist

- [ ] Entré a Settings → Security en Cloudinary
- [ ] Encontré la opción "PDF and ZIP files delivery"
- [ ] Marqué la casilla "Allow delivery of PDF and ZIP files"
- [ ] Guardé los cambios
- [ ] Esperé 2-5 minutos
- [ ] Probé abrir un PDF desde la aplicación
- [ ] Funciona correctamente

---

**¡Después de este paso, tus PDFs deberían funcionar perfectamente! 🎉**

---

**© 2025 CHVS - Sistema de Gestión Humana**

