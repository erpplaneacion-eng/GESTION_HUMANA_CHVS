# 📋 Ejemplo de Uso: Sistema con Especializaciones y Posgrados Separados

## 🎯 Caso de Uso: Registro de un Profesional

### **Ejemplo: Dra. María González - Médica con Especialización y Maestría**

---

## 📝 PASO 1: Formulario Público de Registro

### **Datos Personales Básicos:**
- **Nombre Completo:** María González Pérez
- **Cédula:** 1234567890
- **Género:** Femenino
- **Teléfono:** 3001234567
- **Correo:** maria.gonzalez@email.com

### **SECCIÓN 4: Posgrados (Maestrías, Doctorados)**

El usuario puede agregar **POSGRADOS** (Maestrías, Doctorados, PhD):

**Posgrado 1:**
- **Nombre del Posgrado:** Maestría en Salud Pública
- **Universidad:** Universidad Nacional de Colombia
- **Fecha de Terminación:** 15/06/2020
- **Meses de Experiencia:** 12

**Posgrado 2:**
- **Nombre del Posgrado:** Doctorado en Medicina
- **Universidad:** Universidad del Valle
- **Fecha de Terminación:** 20/12/2022
- **Meses de Experiencia:** 24

### **SECCIÓN 5: Especializaciones**

El usuario puede agregar **ESPECIALIZACIONES** por separado:

**Especialización 1:**
- **Nombre de la Especialización:** Especialización en Medicina Interna
- **Universidad:** Universidad Javeriana
- **Fecha de Terminación:** 10/05/2018
- **Meses de Experiencia:** 36

**Especialización 2:**
- **Nombre de la Especialización:** Especialización en Cardiología
- **Universidad:** Universidad CES
- **Fecha de Terminación:** 05/08/2019
- **Meses de Experiencia:** 24

---

## 💾 PASO 2: Almacenamiento en Base de Datos

### **Tabla: `InformacionBasica`**
```python
{
    'id': 1,
    'nombre_completo': 'MARÍA GONZÁLEZ PÉREZ',
    'cedula': '1234567890',
    'correo': 'maria.gonzalez@email.com',
    ...
}
```

### **Tabla: `Posgrado`** (RELACIONADA)
```python
[
    {
        'id': 1,
        'informacion_basica_id': 1,
        'nombre_posgrado': 'Maestría en Salud Pública',
        'universidad': 'Universidad Nacional de Colombia',
        'fecha_terminacion': '2020-06-15',
        'meses_de_experiencia': 12
    },
    {
        'id': 2,
        'informacion_basica_id': 1,
        'nombre_posgrado': 'Doctorado en Medicina',
        'universidad': 'Universidad del Valle',
        'fecha_terminacion': '2022-12-20',
        'meses_de_experiencia': 24
    }
]
```

### **Tabla: `Especializacion`** (NUEVA - RELACIONADA)
```python
[
    {
        'id': 1,
        'informacion_basica_id': 1,
        'nombre_especializacion': 'Especialización en Medicina Interna',
        'universidad': 'Universidad Javeriana',
        'fecha_terminacion': '2018-05-10',
        'meses_de_experiencia': 36
    },
    {
        'id': 2,
        'informacion_basica_id': 1,
        'nombre_especializacion': 'Especialización en Cardiología',
        'universidad': 'Universidad CES',
        'fecha_terminacion': '2019-08-05',
        'meses_de_experiencia': 24
    }
]
```

---

## 👁️ PASO 3: Vista de Detalle del Administrador

### **Antes (Sistema Anterior):**
```
📋 Posgrados y Especializaciones
├── Maestría en Salud Pública
├── Doctorado en Medicina
├── Especialización en Medicina Interna
└── Especialización en Cardiología
```

### **Ahora (Sistema Actual):**

**📘 Posgrados (Maestrías, Doctorados)**
```
┌─────────────────────────────────────┐
│ 🏆 Maestría en Salud Pública         │
│ Universidad Nacional de Colombia     │
│ Terminación: 15/06/2020              │
│ Experiencia: 12 meses                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏆 Doctorado en Medicina             │
│ Universidad del Valle                │
│ Terminación: 20/12/2022              │
│ Experiencia: 24 meses                │
└─────────────────────────────────────┘
```

**📜 Especializaciones**
```
┌─────────────────────────────────────┐
│ 📜 Especialización en Medicina      │
│    Interna                           │
│ Universidad Javeriana                 │
│ Terminación: 10/05/2018              │
│ Experiencia: 36 meses                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📜 Especialización en Cardiología    │
│ Universidad CES                      │
│ Terminación: 05/08/2019              │
│ Experiencia: 24 meses                │
└─────────────────────────────────────┘
```

---

## 📊 PASO 4: Exportación a Excel

El archivo Excel ahora incluye **6 hojas**:

### **Hoja 1: Información Básica**
- Datos personales y profesionales

### **Hoja 2: Experiencia Laboral**
- Experiencias registradas

### **Hoja 3: Información Académica**
- Títulos profesionales

### **Hoja 4: Posgrados** ⭐
| Nombre Posgrado | Universidad | Fecha Terminación | Meses Experiencia |
|----------------|-------------|-------------------|-------------------|
| Maestría en Salud Pública | Universidad Nacional de Colombia | 2020-06-15 | 12 |
| Doctorado en Medicina | Universidad del Valle | 2022-12-20 | 24 |

### **Hoja 5: Especializaciones** ⭐ **NUEVA**
| Nombre Especialización | Universidad | Fecha Terminación | Meses Experiencia |
|------------------------|-------------|-------------------|-------------------|
| Especialización en Medicina Interna | Universidad Javeriana | 2018-05-10 | 36 |
| Especialización en Cardiología | Universidad CES | 2019-08-05 | 24 |

### **Hoja 6: Cálculo Experiencia**
- Totales de experiencia

---

## 📄 PASO 5: Exportación a PDF (ANEXO 11)

En el PDF del ANEXO 11, la tabla de estudios ahora muestra:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ESTUDIOS REALIZADOS                              │
├──────────────┬──────────────┬──────────────┬──────────────┬───────────┤
│ DESCRIPCIÓN  │UNIVERSITARIOS│ESPECIALIZACIÓN│    OTROS      │           │
├──────────────┼──────────────┼──────────────┼───────────────┼───────────┤
│ TÍTULO       │ Medicina     │Especialización│Maestría en    │           │
│ OBTENIDO     │              │en Medicina   │Salud Pública  │           │
│              │              │Interna       │               │           │
├──────────────┼──────────────┼──────────────┼───────────────┼───────────┤
│ INSTITUCIÓN  │Universidad   │Universidad   │Universidad    │           │
│              │Javeriana     │Javeriana     │Nacional       │           │
├──────────────┼──────────────┼──────────────┼───────────────┼───────────┤
│ FECHA GRADO  │10/05/2015    │10/05/2018    │15/06/2020     │           │
└──────────────┴──────────────┴──────────────┴───────────────┴───────────┘
```

---

## 🔧 PASO 6: Acceso desde Django Admin

En el panel de administración de Django:

### **Antes:**
- Solo se veía una sección "Posgrados" que incluía todo

### **Ahora:**
- **Sección "Posgrados":** Para maestrías, doctorados, PhD
- **Sección "Especializaciones":** Para especializaciones profesionales separadas

Ambas secciones aparecen como **inlines** en el registro de la persona.

---

## ✅ Ventajas del Nuevo Sistema

1. **✅ Separación Clara:** Los usuarios pueden distinguir entre posgrados académicos y especializaciones profesionales
2. **✅ Mejor Organización:** Los datos se almacenan en tablas separadas
3. **✅ Exportación Mejorada:** Excel y PDF muestran ambas categorías por separado
4. **✅ Flexibilidad:** El usuario puede agregar solo posgrados, solo especializaciones, o ambos
5. **✅ Búsqueda Mejorada:** Los administradores pueden filtrar y buscar por tipo de estudio

---

## 🎬 Flujo Completo del Usuario

```
1. Usuario accede a /formapp/registro/
   ↓
2. Completa información personal
   ↓
3. Agrega experiencia laboral
   ↓
4. Agrega formación académica
   ↓
5. SECCIÓN 4: Agrega POSGRADOS (Maestrías, Doctorados)
   - Puede agregar múltiples posgrados
   - Cada uno con su universidad y fecha
   ↓
6. SECCIÓN 5: Agrega ESPECIALIZACIONES (Separadas)
   - Puede agregar múltiples especializaciones
   - Cada una con su universidad y fecha
   ↓
7. Envía el formulario
   ↓
8. Sistema guarda en tablas separadas:
   - Posgrados → tabla `Posgrado`
   - Especializaciones → tabla `Especializacion`
   ↓
9. Administrador puede ver ambas secciones separadas
   ↓
10. Al exportar, Excel y PDF muestran ambas categorías
```

---

## 📝 Notas Importantes

- **Posgrados** = Maestrías, Doctorados, PhD (nivel académico superior)
- **Especializaciones** = Especializaciones profesionales, cursos de especialización (nivel profesional)
- Ambos pueden tener múltiples registros por persona
- Ambos contribuyen a los meses de experiencia
- Se muestran por separado en todas las vistas y exportaciones

---

**Ejemplo creado el:** 2025-01-27
**Versión del sistema:** 1.1.0 (con especializaciones separadas)

