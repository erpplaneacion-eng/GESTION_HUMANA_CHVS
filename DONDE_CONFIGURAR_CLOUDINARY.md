# 📍 ¿Dónde Configurar las Variables de Cloudinary en Railway?

## ✅ RESPUESTA CORRECTA

Las variables de Cloudinary se configuran en la **APLICACIÓN WEB**, NO en la base de datos.

---

## 🎯 Diagrama del Proyecto en Railway

```
┌─────────────────────────────────────────────────────┐
│              TU PROYECTO EN RAILWAY                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  📊 BASE DE DATOS (PostgreSQL)              │  │
│  │  ──────────────────────────────────────────  │  │
│  │  • DATABASE_URL (automático)                │  │
│  │  • No necesitas tocar nada aquí             │  │
│  │                                              │  │
│  │  ❌ NO pongas las variables de Cloudinary   │  │
│  │     aquí                                     │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  🌐 APLICACIÓN WEB (Django)                  │  │
│  │  ──────────────────────────────────────────  │  │
│  │  • SECRET_KEY                                │  │
│  │  • DEBUG                                     │  │
│  │  • ALLOWED_HOSTS                             │  │
│  │  • DATABASE_URL (automático de PostgreSQL)  │  │
│  │                                              │  │
│  │  ✅ PON AQUÍ las variables de Cloudinary:   │  │
│  │     - CLOUDINARY_CLOUD_NAME                  │  │
│  │     - CLOUDINARY_API_KEY                     │  │
│  │     - CLOUDINARY_API_SECRET                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Pasos Detallados

### Paso 1: Identificar el Servicio Correcto

En tu dashboard de Railway deberías ver algo como esto:

```
gestionhumanachvs-production
├── 📊 PostgreSQL (Base de datos)
└── 🌐 Web Service (Tu aplicación Django)
    ↑
    ESTA ES LA QUE NECESITAS
```

### Paso 2: Click en el Servicio Web

**NO hagas click en PostgreSQL**, haz click en el servicio que tiene el nombre de tu aplicación (probablemente "Web Service" o "gestionhumanachvs").

### Paso 3: Ir a la Pestaña "Variables"

Una vez dentro del servicio web, verás varias pestañas:
- **"Deployments"** ← Shows deployments
- **"Settings"** ← Configuración
- **"Variables"** ← ¡ESTA ES LA QUE NECESITAS!
- **"Metrics"** ← Métricas
- **"Logs"** ← Logs

Click en **"Variables"**.

### Paso 4: Agregar las Variables

Aquí verás una lista de variables ya configuradas, algo como:

```
ALLOWED_HOSTS              *.railway.app
DEBUG                      False
SECRET_KEY                 tu-clave-secreta
DATABASE_URL               postgresql://... (automático)
```

Click en **"+ New Variable"** y agrega:

```
CLOUDINARY_CLOUD_NAME      dk7nufqc4
CLOUDINARY_API_KEY         862119278775475
CLOUDINARY_API_SECRET      H29cbSnPJd_SYlFxOv039mc_wZE
```

### Paso 5: Verificar

Después de agregar las variables, tu lista debería verse así:

```
ALLOWED_HOSTS              *.railway.app
CLOUDINARY_API_KEY         862119278775475
CLOUDINARY_API_SECRET      H29cbSnPJd_SYlFxOv039mc_wZE
CLOUDINARY_CLOUD_NAME      dk7nufqc4
DATABASE_URL               postgresql://... (automático)
DEBUG                      False
SECRET_KEY                 tu-clave-secreta
```

---

## ⚠️ Errores Comunes

### Error 1: "Configuré en PostgreSQL y no funciona"

**Problema:** Pusiste las variables en el servicio de PostgreSQL  
**Solución:** Las variables van en el servicio WEB, no en la base de datos

### Error 2: "No sé cuál es mi aplicación web"

**Solución:** En Railway, tu aplicación web es el servicio que tiene el código Django.  
Suele tener un ícono de 🌐 o estar marcado como "Web Service"

### Error 3: "No veo la pestaña Variables"

**Solución:** Asegúrate de estar en el servicio web, no en PostgreSQL.  
La pestaña "Variables" solo aparece en servicios que pueden ejecutar código.

---

## 🎯 Resumen Visual

En el dashboard de Railway:

1. ✅ **Click en:** `Web Service` o `gestionhumanachvs-production` (tu app)
2. ❌ **NO click en:** `PostgreSQL` (la base de datos)
3. ✅ **Click en:** Pestaña `Variables`
4. ✅ **Click en:** `+ New Variable`
5. ✅ **Agrega:** Las 3 variables de Cloudinary

---

## 📚 Verificación

Después de configurar, verifica que:

1. ✅ Las variables estén en el servicio WEB
2. ✅ Los nombres sean EXACTOS (mayúsculas/minúsculas)
3. ✅ Los valores NO tengan espacios ni comillas
4. ✅ Railway haya reiniciado automáticamente el servicio

---

## 🆘 ¿Todavía Confundido?

**Pregúntate:**
- ¿Dónde corre mi código Django? → Esa es tu aplicación web
- ¿Dónde están las otras variables como SECRET_KEY? → Ahí van las de Cloudinary

**Nunca pongas las variables en PostgreSQL**, siempre en la aplicación web.

---

**© 2025 CHVS - Sistema de Gestión Humana**

