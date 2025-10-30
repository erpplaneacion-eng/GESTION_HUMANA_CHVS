# 🔐 Acceso Administrativo

## 📋 Credenciales de Acceso

- **URL:** https://gestionhumanachvs-production.up.railway.app/login/
- **Usuario:** admin
- **Contraseña:** admin123

---

## 🔍 Una vez dentro del panel administrativo

Puedes:

1. **Ver lista de personal registrado**
   - Ve a: `/formapp/lista/`
   - Verás todas las personas registradas
   - Estadísticas: total personal, con experiencia, profesionales, con posgrados

2. **Ver detalles de cada registro**
   - Click en el botón "Ver Detalle" (ícono de ojo)
   - Verás toda la información completa

3. **Editar registros**
   - Click en el botón "Editar" (ícono de lápiz)
   - Puedes completar campos administrativos
   - Ver experiencia laboral con certificados
   - Agregar información profesional

4. **Eliminar registros**
   - Click en el botón "Eliminar" (ícono de basura)
   - Confirmar eliminación

5. **Subir certificados (con Cloudinary configurado)**
   - Al editar un registro
   - Puedes subir certificados laborales
   - Los certificados se almacenan en Cloudinary

---

## 🎯 Verificar que Cloudinary Funciona

Desde el panel administrativo, puedes verificar:

1. **Ver certificados subidos**
   - En el detalle de un registro con experiencia laboral
   - Debe aparecer el link al certificado
   - El certificado debe abrirse correctamente

2. **Subir un certificado de prueba**
   - Ve a "Editar" en cualquier registro
   - En la sección "Experiencia Laboral"
   - Sube un certificado PDF
   - Guarda
   - Verifica que no aparezca error "Invalid Signature"

---

## 📊 Funcionalidades del Panel

### Estadísticas
- Total de personal registrado
- Cantidad con experiencia laboral
- Cantidad de profesionales
- Cantidad con posgrados

### Búsqueda
- Buscar por cédula o nombre
- Resultados en tiempo real

### Filtros
- Por género
- Por área de conocimiento
- Por tipo de perfil

### Exportación (si implementas)
- Exportar reportes Excel
- Generar certificados laborales
- Imprimir reportes

---

## 🆘 Si No Puedes Entrar

### Problema 1: "Usuario o contraseña incorrectos"
- Verifica que escribiste "admin" en usuario
- Verifica que escribiste "admin123" en contraseña
- Respeta mayúsculas/minúsculas

### Problema 2: No existe el usuario
- Debes crear el superusuario en Railway
- Ve a Deployments → Console
- Ejecuta: `python manage.py createsuperuser`
- Sigue las instrucciones

### Problema 3: Error de conexión
- Verifica que el servidor esté corriendo
- Verifica que Railway esté activo
- Revisa los logs de Railway

---

**© 2025 CHVS - Sistema de Gestión Humana**

