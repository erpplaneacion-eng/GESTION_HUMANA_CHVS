# 📋 Datos de Prueba para Formulario con Cloudinary

## Datos Personales

### Información Básica
- **Primer Apellido:** López
- **Segundo Apellido:** Gutiérrez  
- **Primer Nombre:** Carlos
- **Segundo Nombre:** (dejar vacío)
- **Cédula:** 9876543210
- **Género:** Masculino
- **Teléfono:** 3012345678
- **Correo:** carlos.lopez@example.com

### Dirección
- **Tipo de Vía:** Carrera
- **Número de Vía:** 15
- **Número de Casa:** 35-12
- **Complemento:** (dejar vacío)
- **Barrio:** (dejar vacío)

---

## Experiencia Laboral

### Experiencia 1
- **Cargo:** Desarrollador de Software
- **Cargo Anexo 11:** Desarrollador de Software
- **Fecha Inicial:** 2020-01-15
- **Fecha de Terminación:** 2023-06-30
- **Objeto Contractual:** Desarrollo de aplicaciones web
- **Funciones:** Desarrollo de aplicaciones web con Django y React
- **Certificado:** [Subir archivo PDF - usar: formulario_eps_1118283426_1.pdf]

---

## Formación Académica

### Formación 1
- **Profesión:** Ingeniería de Sistemas
- **Universidad:** Universidad Nacional
- **Tarjeta o Resolución:** Tarjeta Profesional
- **N° Tarjeta:** 123456
- **Fecha de Expedición:** 2019-03-15
- **Fecha de Grado:** 2018-12-20
- **Meses de Experiencia por Profesión:** 36

---

## Posgrados

### Posgrado 1
- **Nombre:** Maestría en Desarrollo de Software
- **Universidad:** Universidad de los Andes
- **Fecha de Terminación:** 2023-08-15
- **Meses de Experiencia:** 24

---

## 📁 Archivo para Subir

**Ruta del archivo de prueba:**
```
gestion_humana/media/certificados_laborales/formulario_eps_1118283426_1.pdf
```

---

## ✅ Pasos para Completar

1. Ve a: https://gestionhumanachvs-production.up.railway.app/formapp/registro/
2. Completa los datos personales con la información de arriba
3. Agrega la experiencia laboral con las fechas indicadas
4. **IMPORTANTE:** Sube el archivo PDF desde tu computadora:
   - Click en "Seleccionar archivo" o "Certificado Laboral"
   - Selecciona: `gestion_humana/media/certificados_laborales/formulario_eps_1118283426_1.pdf`
5. Agrega la formación académica
6. Agrega el posgrado
7. Click en "Completar Registro"

---

## 🔍 Verificar que Funciona

Después de enviar:

1. **Mensaje de éxito:** Debe aparecer "¡Formulario enviado con éxito!"
2. **Sin errores:** No debe aparecer el error de "Invalid Signature"
3. **Verificar en Cloudinary:**
   - Ve a: https://cloudinary.com/console
   - Click en "Media Library"
   - Busca la carpeta `certificados_laborales`
   - Debe aparecer tu archivo PDF subido

---

## 🆘 Si Aparece Error

Si todavía aparece el error de "Invalid Signature":

1. Verifica en Railway que las 3 variables estén configuradas
2. Verifica que los valores NO tengan espacios
3. Verifica que Railway haya reiniciado correctamente
4. Revisa los logs de Railway para más detalles

---

**¡Buena suerte con la prueba! 🚀**

