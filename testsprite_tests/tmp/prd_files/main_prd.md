# Product Requirements Document (PRD)
## Sistema de Gestión Humana CHVS

### 1. Overview
**Producto:** Sistema de Gestión de Recursos Humanos para la Secretaría de Bienestar Social de Cali
**Cliente:** UNIÓN TEMPORAL COMISIÓN ARQUIDIOCESANA VIDA JUSTICIA Y PAZ 25-2
**Versión:** 1.0
**Fecha:** Noviembre 2024

### 2. Objetivos del Producto
- Digitalizar y centralizar el proceso de registro de candidatos para contratos con la Secretaría de Bienestar Social
- Automatizar el cálculo de experiencia laboral y la generación de documentos oficiales (ANEXO 11)
- Facilitar la gestión y verificación de documentación de candidatos (antecedentes, títulos, certificados)
- Generar reportes consolidados en Excel y descargas masivas de documentación

### 3. Usuarios Objetivo
1. **Candidatos (Público):** Profesionales que aplican a contratos públicos
2. **Personal Administrativo (Staff):** Gestores de RRHH que revisan y procesan aplicaciones
3. **Representante Legal:** Firma digital de documentos ANEXO 11

### 4. Características Principales

#### 4.1 Registro Público de Candidatos
**Descripción:** Formulario web público multi-sección para registro de información personal y profesional

**Requerimientos Funcionales:**
- Validación de cédula única (5-10 dígitos numéricos)
- Validación de teléfono (10 dígitos)
- Validación de correo electrónico
- Formulario dividido en 8 secciones:
  1. Datos personales básicos
  2. Documentos de identidad
  3. Experiencia laboral (múltiples entradas)
  4. Información académica (múltiples entradas)
  5. Posgrados (múltiples entradas)
  6. Especializaciones (múltiples entradas)
  7. Antecedentes legales (5 certificados obligatorios)
  8. Anexos adicionales (opcionales)

**Validaciones:**
- Archivos: máximo 10MB, formatos PDF/JPG/PNG, validación MIME type
- Fechas: fecha inicial debe ser anterior a fecha final en experiencia laboral
- Campos obligatorios según sección
- Libreta militar condicional según género (opcional para todos)

**Comportamiento:**
- Envío de correo de confirmación automático al registrarse
- Mensaje de éxito/error claro
- Rollback completo si cualquier sección falla validación

#### 4.2 Gestión de Experiencia Laboral
**Descripción:** Registro de experiencia laboral con cálculo automático de tiempo acumulado

**Requerimientos Funcionales:**
- Cálculo automático de meses y días entre fecha inicial y final
- Suma total de todas las experiencias laborales
- Conversión a años (formato decimal y "X años Y meses")
- Adjuntar certificado laboral por cada experiencia

**Reglas de Negocio:**
- Meses completos: diferencia de meses considerando día
- Días totales: diferencia calendario
- Total años: meses totales / 12 (2 decimales)
- Certificado obligatorio en registro inicial, opcional en edición

#### 4.3 Panel Administrativo
**Descripción:** Interfaz para personal administrativo con gestión completa de candidatos

**Requerimientos Funcionales:**
- Lista de candidatos con paginación (20 por página)
- Búsqueda por cédula o nombre
- Ver detalle completo de candidato
- Editar información y documentos
- Eliminar registro
- Estadísticas en dashboard:
  - Total de personal
  - Personal con experiencia
  - Profesionales titulados
  - Personal con posgrado

**Autenticación:**
- Login requerido para acceso
- Django authentication system

#### 4.4 Generación de Reportes Excel
**Descripción:** Exportación de datos a formato Excel estructurado

**Tipos de Reportes:**
1. **Excel Individual (6 hojas):**
   - Información Básica (datos personales y profesionales)
   - Experiencia Laboral (tabla con todas las experiencias)
   - Información Académica (títulos y universidades)
   - Posgrados (lista de posgrados)
   - Especializaciones (lista de especializaciones)
   - Cálculo de Experiencia (resumen consolidado)

2. **Excel Consolidado:**
   - Lista completa de todo el personal en una tabla
   - Columnas: Cédula, Nombre, Género, Teléfono, Correo, Perfil, Área, Profesión, Contrato, Observaciones

**Formato:**
- Headers azules (#366092) con texto blanco
- Bordes en todas las celdas
- Texto centrado en headers
- Anchos de columna ajustados
- Título principal en negrita

#### 4.5 Generación de PDF ANEXO 11
**Descripción:** Documento oficial "Carta de Compromiso Personal" en formato PDF

**Estructura del Documento:**
- **Página 1:** Carta de compromiso
  - Fecha actual en español (día, mes, año)
  - Destinatario: Secretaría de Bienestar Social
  - Número de proceso (campo contrato)
  - Texto de compromiso con datos del candidato
  - Firmas: Profesional y Representante Legal

- **Página 2:** Relación de experiencia profesional
  - Tabla de datos personales (7 filas)
  - Tabla de estudios realizados (4 columnas: Universitarios, Especialización, Otros)
  - Consolidación de todos los títulos académicos
  - Total de experiencia en años

**Formato:**
- Tamaño carta (letter)
- Márgenes: 0.75" laterales, 0.5" superior/inferior
- Fuente: Helvetica
- Títulos en negrita, centrados
- Tablas con bordes y fondo gris en headers

#### 4.6 Descarga de Archivos ZIP
**Descripción:** Empaquetado de toda la documentación en archivo comprimido

**Tipos de ZIP:**
1. **ZIP Individual:**
   - Excel individual
   - PDF ANEXO 11
   - Todos los documentos adjuntos organizados en carpetas:
     - Documentos_Identidad/
     - Certificados_Laborales/
     - Documentos_Academicos/
     - Antecedentes/
     - Anexos/

2. **ZIP Completo (Todo el Personal):**
   - Excel consolidado
   - Por cada candidato:
     - Carpeta Personal/{nombre}/
     - Excel individual
     - PDF ANEXO 11
     - Todos los documentos organizados en subcarpetas

**Manejo de Archivos:**
- Detección automática de extensión (PDF/JPG/PNG)
- Fallback a extensión .pdf si no se puede determinar
- Nombres de archivo sanitizados (sin espacios ni caracteres especiales)
- Logging de errores por archivo individual (continúa si uno falla)

#### 4.7 Envío de Correos de Confirmación
**Descripción:** Email automático al completar registro exitosamente

**Requerimientos Funcionales:**
- Envío mediante Gmail API
- Template HTML personalizado
- Información incluida:
  - Nombre completo del candidato
  - Cédula
  - Correo
  - Teléfono
  - Fecha y hora de registro (zona horaria Colombia)

**Comportamiento:**
- Envío en thread separado (no bloquea respuesta del formulario)
- Logging de éxito/error
- Soporte para Railway (variable GMAIL_TOKEN_JSON) y desarrollo local (token.json)
- Refresh automático de token si ha expirado

### 5. Modelos de Datos

#### 5.1 InformacionBasica
- Datos personales (nombre, cédula, género, dirección, teléfono, correo)
- Datos profesionales (perfil, área, profesión, contrato, observaciones)
- Relaciones: 1-N con experiencias/formación, 1-1 con documentos/antecedentes

#### 5.2 ExperienciaLaboral
- Fechas (inicial, terminación)
- Cálculos (meses, días - auto calculados)
- Descripción (cargo, objeto contractual, funciones)
- Certificado laboral (archivo adjunto)

#### 5.3 InformacionAcademica
- Título profesional
- Universidad
- Tarjeta profesional (tipo, número)
- Fechas (expedición, grado)
- Documentos adjuntos (título, tarjeta, certificado vigencia)

#### 5.4 Posgrado / Especializacion
- Nombre del estudio
- Universidad
- Fecha de terminación

#### 5.5 CalculoExperiencia
- Total meses
- Total días
- Total años (decimal)
- Texto legible (X años Y meses)

#### 5.6 DocumentosIdentidad
- Cédula (obligatorio, al 150%)
- Hoja de vida (obligatorio)
- Libreta militar (opcional)
- Datos libreta (número, distrito, clase)

#### 5.7 Antecedentes
- 5 certificados obligatorios:
  - Procuraduría + fecha
  - Contraloría + fecha
  - Policía + fecha
  - Medidas Correctivas + fecha
  - Delitos Sexuales + fecha

#### 5.8 AnexosAdicionales
- ANEXO 03 (opcional)
- Carta de intención (opcional)
- Otros documentos (opcional) + descripción

### 6. Reglas de Negocio

#### 6.1 Validaciones
1. Cédula debe ser única en el sistema
2. Teléfono debe tener exactamente 10 dígitos
3. Correo debe ser válido (contener @)
4. Archivos adjuntos:
   - Tamaño máximo: 10 MB
   - Formatos permitidos: PDF, JPG, JPEG, PNG
   - Validación MIME type (no solo extensión)
5. Fechas de experiencia: fecha inicial < fecha terminación
6. Certificados laborales obligatorios en registro inicial

#### 6.2 Cálculos Automáticos
1. **Experiencia por periodo:**
   - Meses completos = (años × 12) + meses + ajuste por días
   - Días totales = diferencia calendario

2. **Experiencia total:**
   - Suma de todos los meses de experiencia
   - Suma de todos los días de experiencia
   - Conversión a años: meses / 12 (2 decimales)
   - Texto: "X años y Y meses"

3. **Nombre completo:**
   - Concatenación: Apellido1 Apellido2 Nombre1 Nombre2
   - Conversión automática a MAYÚSCULAS

#### 6.3 Transacciones
- Uso de `transaction.atomic()` para operaciones críticas
- Rollback completo si falla cualquier parte del guardado
- Validación de TODOS los formsets antes de guardar

#### 6.4 Archivos en Edición
- Al editar: archivos existentes son opcionales (mantener si no se sube nuevo)
- Al crear: archivos críticos son obligatorios
- Validadores solo se ejecutan si se sube un archivo nuevo

### 7. Integraciones

#### 7.1 Gmail API
- Autenticación OAuth 2.0
- Credenciales desde variable de entorno (Railway) o archivo local
- Refresh automático de token
- Envío de emails HTML

#### 7.2 Cloudinary
- Almacenamiento de archivos adjuntos
- CDN para servir archivos

#### 7.3 PostgreSQL (Producción)
- Base de datos principal en Railway
- Configuración via DATABASE_URL

#### 7.4 SQLite (Desarrollo)
- Base de datos local para desarrollo

### 8. Seguridad

#### 8.1 Autenticación y Autorización
- LoginRequiredMixin para vistas administrativas
- Formulario público sin autenticación (por diseño)

#### 8.2 Validación de Archivos
- Validación de tamaño (10 MB máx)
- Validación de extensión
- Validación de MIME type con python-magic
- Prevención de inyección de archivos maliciosos

#### 8.3 Validación de Datos
- Validación de formato en frontend (HTML5)
- Validación en backend (Django forms)
- Prevención de duplicados (cédula única)

### 9. Rendimiento

#### 9.1 Paginación
- Lista de candidatos: 20 por página
- Carga bajo demanda

#### 9.2 Generación Asíncrona
- Envío de correos en thread separado
- No bloquea respuesta del formulario

#### 9.3 Optimizaciones
- WhiteNoise para archivos estáticos
- Cloudinary CDN para media
- Índices en base de datos (cédula)

### 10. Despliegue

#### 10.1 Entornos
- **Desarrollo:** SQLite, token.json local, DEBUG=True
- **Producción (Railway):** PostgreSQL, GMAIL_TOKEN_JSON env var, DEBUG=False

#### 10.2 Servidor
- Gunicorn como WSGI server
- WhiteNoise para archivos estáticos
- Configuración via variables de entorno

#### 10.3 Variables de Entorno
- DATABASE_URL
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- GMAIL_TOKEN_JSON
- Cloudinary credentials (CLOUD_NAME, API_KEY, API_SECRET)

### 11. Limitaciones Conocidas

1. **Escalabilidad:** ZIP completo carga todos los candidatos en memoria
2. **Email:** No hay cola de reintentos si falla envío
3. **Concurrencia:** No hay manejo de ediciones simultáneas
4. **Testing:** No hay tests automatizados implementados
5. **Internacionalización:** Solo español
6. **Móvil:** No hay versión móvil optimizada

### 12. Trabajo Futuro

1. Implementar suite completa de tests (unitarios, integración, E2E)
2. Refactorizar views.py en múltiples archivos
3. Implementar procesamiento asíncrono con Celery
4. Agregar cola de emails con reintentos
5. Optimizar generación de ZIP completo (streaming)
6. Implementar rate limiting en formulario público
7. Agregar logging estructurado y monitoreo
8. Implementar versión móvil responsive

### 13. Criterios de Éxito

1. **Funcionalidad:**
   - 100% de registros exitosos se envían con correo de confirmación
   - 0% de pérdida de datos en formularios validados
   - Generación exitosa de reportes Excel y PDF

2. **Usabilidad:**
   - Tiempo promedio de llenado de formulario: < 15 minutos
   - Claridad de mensajes de error: 90%+ comprensión

3. **Rendimiento:**
   - Tiempo de carga de lista: < 2 segundos
   - Tiempo de generación de ZIP individual: < 10 segundos
   - Disponibilidad: 99%+

4. **Seguridad:**
   - 0 vulnerabilidades críticas
   - 100% de validación de archivos adjuntos
