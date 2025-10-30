# 🔄 Flujo Completo: Cómo Funciona Cloudinary con tu Base de Datos

## 📊 Diagrama del Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESO DE CARGA DE ARCHIVOS                  │
└─────────────────────────────────────────────────────────────────┘

1️⃣ USUARIO SUBE ARCHIVO
   ┌─────────────────────┐
   │  Usuario completa   │
   │  formulario en la   │
   │  aplicación web     │
   │  y selecciona un    │
   │  PDF                │
   └──────────┬──────────┘
              │
              ▼
2️⃣ DJANGO RECIBE EL ARCHIVO
   ┌─────────────────────┐
   │  Tu aplicación      │
   │  Django recibe el   │
   │  formulario y el    │
   │  archivo            │
   └──────────┬──────────┘
              │
              ▼
3️⃣ DJANGO USA LAS CREDENCIALES
   ┌─────────────────────┐
   │  Django lee las     │
   │  variables de       │
   │  Railway:           │
   │  • CLOUD_NAME       │
   │  • API_KEY          │
   │  • API_SECRET       │
   └──────────┬──────────┘
              │
              ▼
4️⃣ SUBE A CLOUDINARY
   ┌─────────────────────┐
   │  Usa las            │
   │  credenciales       │
   │  para autenticarse  │
   │  con Cloudinary     │
   │                     │
   │  Cloudinary recibe  │
   │  el archivo         │
   └──────────┬──────────┘
              │
              ▼
5️⃣ CLOUDINARY RESPUESTA
   ┌─────────────────────┐
   │  Cloudinary guarda  │
   │  el archivo y       │
   │  devuelve una URL:  │
   │                     │
   │  https://res.cloudinary.│
   │  com/dk7nufqc4/     │
   │  media/certificado...│
   └──────────┬──────────┘
              │
              ▼
6️⃣ DJANGO GUARDA LA URL
   ┌─────────────────────┐
   │  Django toma la     │
   │  URL de Cloudinary  │
   │  y la guarda en     │
   │  PostgreSQL         │
   │                     │
   │  Tabla:             │
   │  formapp_           │
   │  experiencialaboral │
   │                     │
   │  Campo:             │
   │  certificado_       │
   │  laboral            │
   └─────────────────────┘
```

---

## 🗄️ Tabla de Base de Datos

En tu base de datos PostgreSQL, la tabla `formapp_experiencialaboral` tiene:

| Campo | Tipo | Contenido |
|-------|------|-----------|
| id | INTEGER | 1 |
| fecha_inicial | DATE | 2020-01-15 |
| fecha_terminacion | DATE | 2023-06-30 |
| cargo | VARCHAR(200) | "Desarrollador de Software" |
| **certificado_laboral** | **VARCHAR(100)** | **"https://res.cloudinary.com/dk7nufqc4/media/certificados_laborales/..."** |
| ... | ... | ... |

**La URL completa del archivo se guarda en la base de datos como texto.**

---

## 🔑 ¿Qué Hacen las Variables?

### Variables de Railway (Configuración)

```
CLOUDINARY_CLOUD_NAME    → Dice a Django a qué cuenta de Cloudinary conectarse
CLOUDINARY_API_KEY       → Credencial para autenticarse
CLOUDINARY_API_SECRET    → Credencial para firmar las peticiones
```

**Equivalente a:**
"Hey Django, cuando subas un archivo, usa estas credenciales para hablar con Cloudinary"

### URL en la Base de Datos (Resultado)

```
certificado_laboral: "https://res.cloudinary.com/dk7nufqc4/image/upload/..."
```

**Equivalente a:**
"Este es el archivo que guardé en Cloudinary"

---

## 📝 Ejemplo Real

### 1. Usuario Sube Archivo

```
Usuario → Selecciona: certificado.pdf
         → Click en "Completar Registro"
```

### 2. Django Procesa

```python
# Django usa las credenciales de Railway
cloud_name = "dk7nufqc4"          # De CLOUDINARY_CLOUD_NAME
api_key = "862119278775475"       # De CLOUDINARY_API_KEY
api_secret = "H29cbSnPJd_..."     # De CLOUDINARY_API_SECRET

# Sube a Cloudinary
upload_result = cloudinary.uploader.upload(
    file,
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# Cloudinary devuelve:
# {"url": "https://res.cloudinary.com/dk7nufqc4/...", "public_id": "..."}
```

### 3. Django Guarda en PostgreSQL

```python
# Guarda en la tabla formapp_experiencialaboral
experiencia = ExperienciaLaboral(
    fecha_inicial="2020-01-15",
    fecha_terminacion="2023-06-30",
    cargo="Desarrollador",
    certificado_laboral="https://res.cloudinary.com/dk7nufqc4/media/..."
)
experiencia.save()

# Ahora en PostgreSQL:
# certificado_laboral = "https://res.cloudinary.com/dk7nufqc4/media/certificado.pdf"
```

### 4. Usuario Ve el Archivo

```python
# Cuando alguien abre el detalle de la experiencia
# Django lee la URL de PostgreSQL
url = experiencia.certificado_laboral
# url = "https://res.cloudinary.com/dk7nufqc4/media/certificado.pdf"

# Y la muestra en el HTML
# <a href="{{ url }}">Ver Certificado</a>
```

---

## 🔍 Verificación en tu Base de Datos

Puedes verificar que funciona conectándote a tu PostgreSQL:

```sql
SELECT 
    id,
    cargo,
    certificado_laboral  -- Aquí verás la URL de Cloudinary
FROM 
    formapp_experiencialaboral;
```

Deberías ver algo como:

```
id | cargo                          | certificado_laboral
1  | Desarrollador de Software      | https://res.cloudinary.com/dk7nufqc4/media/certificados_laborales/formulario_eps_1118283426_1.pdf
```

---

## ⚠️ Si No Configuras las Variables

Sin las credenciales de Cloudinary configuradas en Railway:

1. ❌ Django NO puede autenticarse con Cloudinary
2. ❌ Cloudinary rechaza la subida: "Invalid Signature"
3. ❌ No se devuelve ninguna URL
4. ❌ Django NO puede guardar nada en PostgreSQL
5. ❌ Error: "Error al guardar el formulario"

**Resultado:** No hay archivo en Cloudinary y NO hay URL en la base de datos.

---

## ✅ Con las Variables Configuradas

Con las credenciales correctas en Railway:

1. ✅ Django se autentica con Cloudinary
2. ✅ Cloudinary acepta el archivo
3. ✅ Cloudinary devuelve una URL
4. ✅ Django guarda la URL en PostgreSQL
5. ✅ Éxito: "¡Formulario enviado con éxito!"

**Resultado:** Archivo en Cloudinary Y URL en PostgreSQL.

---

## 📚 Resumen

| Componente | Función | Dónde está |
|------------|---------|------------|
| **Variables de Railway** | Credenciales para autenticarse | Variables de entorno en Railway |
| **Cloudinary** | Almacena el archivo físico | Servidor de Cloudinary |
| **URL en PostgreSQL** | Dirección del archivo en Cloudinary | Campo `certificado_laboral` en la tabla `formapp_experiencialaboral` |
| **Django** | Coordina todo el proceso | Tu aplicación en Railway |

---

**© 2025 CHVS - Sistema de Gestión Humana**

