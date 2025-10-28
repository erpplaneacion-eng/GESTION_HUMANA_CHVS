# GESTIÓN HUMANA - Sistema de Documentación del Personal

## Descripción del Proyecto

Este proyecto implementa un sistema de gestión humana basado en Django que maneja la documentación completa del personal de una organización. El sistema está diseñado para almacenar información detallada sobre empleados, incluyendo datos personales, experiencia laboral, formación académica y certificaciones profesionales.

## Análisis del Archivo Excel

### Archivo Fuente
- **Nombre**: `registros_personal_documentacion.xlsx`
- **Ubicación**: `archivos excel/`
- **Contenido**: Documentación completa del personal con más de 100 columnas de información

### Columnas Principales Identificadas

#### 1. Información Básica
- `ID_REGISRTO`: Número de identificación del registro (Integer)
- `Perfil`: Tipo de perfil profesional (String)
- `Area del conocimiento`: Área de especialización (String)
- `Tipo de perfil`: Clasificación del perfil (String)
- `Area de conocimiento`: Detalle del área (String)
- `Profesion`: Profesión principal (String)
- `Experiencia`: Tipo de experiencia (String)
- `Tiempo de experiencia`: Duración de experiencia (String)
- `Cantidad`: Número de registros (Integer)
- `CEDULA`: Número de identificación único (String)
- `DESCRIPCIÓN`: Descripción del cargo (Text)
- `GENERO`: Género de la persona (String)
- `BASE ANEXO 11`: Referencia administrativa (String)
- `DIRECCION`: Dirección residencial (Text)
- `TELEFONO`: Número de teléfono (String)
- `CORREO`: Correo electrónico (Email)
- `OBSERVACION`: Observaciones adicionales (Text)

#### 2. Registros de Experiencia Laboral (1-6)
- `ID_EXPERIENCIA`: Identificador único de la experiencia (Integer, Clave Primaria)
- `ID_REGISRTO`: Clave foránea para enlazar con la tabla de Información Básica (Integer)
Cada sección incluye:
- `CERTIFICADOS LABORALES O CONTRACTUALES`: Descripción del certificado (Text)
- `MESES EXPERIENCIA`: Meses de experiencia (Integer)
- `DIAS EXPERIENCIA`: Días de experiencia (Integer)
- `DIAS RESIDUAL EXPERIENCIA`: Días residuales (Integer)
- `CARGO`: Cargo desempeñado (String)
- `CARGO ANEXO 11`: Cargo administrativo (String)
- `OBJETO CONTRACTUAL`: Objeto del contrato (Text)
- `FUNCIONES`: Funciones desempeñadas (Text)
`FECHA INICIAL`: Fecha de inicio del contrato (Date)
- `FECHA DE TERMINACION`: Fecha de finalización (Date)
- 

#### 3. Información Profesional y Académica
- `ID_FORMACION`: Identificador único de la formación (Integer, Clave Primaria)
- `ID_REGISRTO`: Clave foránea para enlazar con la tabla de Información Básica (Integer)
- `FECHA EXPEDICION`: Fecha de expedición de tarjeta profesional (Date)
- `TARJETA O RESOLUCIÓN PROFESIONAL`: Número de tarjeta (String)
- `PROFESION 1/2`: Profesiones registradas (String)
- `UNIVERSIDAD`: Institución educativa (String)
- `N° TARJETA O RESOLUCION`: Número de resolución (String)
- `FECHA DE GRADO`: Fecha de graduación (Date)
- `PROFESION X-MESES DE EXPERIENCIA`: Meses de experiencia por profesión (Integer)


#### 3.1. Información de Posgrados
- `ID_POSGRADO`: Identificador único del posgrado (Integer, Clave Primaria)
- `ID_REGISRTO`: Clave foránea para enlazar con la tabla de Información Básica (Integer)
- `NOMBRE_POSGRADO`: Nombre del posgrado (Especialización, Maestría, etc.) (String)
- `UNIVERSIDAD`: Institución educativa donde se cursó (String)
- `FECHA_TERMINACION`: Fecha de terminación o graduación del posgrado (Date)

#### 4. Cálculos de Experiencia Total
- `ID_CALCULO`: Identificador único del cálculo (Integer, Clave Primaria)
- `ID_REGISRTO`: Clave foránea para enlazar con la tabla de Información Básica (Integer)
- `TOTAL MESES EXPERIENCIA CERTIFICADA`: Total meses certificados (Integer)
- `TOTAL DIAS EXPERIENCIA CERTIFICADA`: Total días certificados (Integer)
- `TOTAL DIAS RESIDUA EXPERIENCIA CERTIFICADA`: Días residuales totales (Integer)
- `TOTAL EXPERIENCIA EN AÑOS`: Experiencia en años (Decimal)
- `AÑOS Y MESES DE EXPERIENCIA`: Experiencia formateada (String)

## Diseño de Base de Datos

### Esquema Relacional para PostgreSQL

Se diseñó un esquema relacional único con una tabla principal `Personal` que consolida toda la información. Esta aproximación se tomó considerando:

- **Ventajas**:
  - Simplicidad en consultas
  - Menos joins complejos
  - Fácil mantenimiento
  - Adecuado para datos mayoritariamente opcionales

- **Estructura de la Tabla**:
  - **Clave Primaria**: ID automático de Django
  - **Clave Única**: `cedula` (número de identificación)
  - **Campos Obligatorios**: Ninguno (todos nullable para flexibilidad)
  - **Relaciones**: Se introduce una relación de uno a muchos entre la tabla principal de personal y la nueva tabla de posgrados.

### Tipos de Datos Utilizados

| Tipo Django | Tipo PostgreSQL | Uso |
|-------------|-----------------|-----|
| `IntegerField` | `INTEGER` | Números enteros (meses, días, cantidades) |
| `CharField` | `VARCHAR` | Textos cortos (nombres, profesiones) |
| `TextField` | `TEXT` | Textos largos (descripciones, funciones) |
| `EmailField` | `VARCHAR` | Correos electrónicos |
| `DateField` | `DATE` | Fechas |
| `DecimalField` | `DECIMAL` | Números decimales (años de experiencia) |

## Implementación en Django

### Modelos Implementados

### Modelo Personal

```python
class Personal(models.Model):
    # Información básica, experiencia laboral (1-6), formación académica
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    # ... (todos los campos definidos)

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"

    def __str__(self):
        return f"{self.cedula} - {self.descripcion}"
```

### Características del Modelo

- **Campos Nullables**: Todos los campos permiten valores nulos para manejar datos incompletos
- **Validaciones**: Campo `correo` con validación de email
- **Índices**: Clave única en `cedula` para integridad de datos
- **Nombres Descriptivos**: Campos nombrados en español para consistencia

## Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Django 4.0+
- PostgreSQL 12+
- Dependencias del proyecto

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd GESTION_HUMANA_CHVS
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**:
   - Crear base de datos PostgreSQL
   - Actualizar configuración en `settings.py`

5. **Ejecutar migraciones**:
   ```bash
   cd gestion_humana
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crear superusuario** (opcional):
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar servidor**:
   ```bash
   python manage.py runserver
   ```

## Uso del Sistema

### Carga de Datos

Para cargar datos desde el archivo Excel, se puede implementar un comando de gestión personalizado:

```python
# En formapp/management/commands/import_excel.py
import pandas as pd
from django.core.management.base import BaseCommand
from formapp.models import Personal

class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_excel('archivos excel/registros_personal_documentacion.xlsx')
        for index, row in df.iterrows():
            Personal.objects.create(
                cedula=row['CEDULA'],
                descripcion=row['DESCRIPCIÓN'],
                # ... mapear todos los campos
            )
```

### Consultas Comunes

```python
# Buscar personal por cédula
persona = Personal.objects.get(cedula='123456789')

# Filtrar por profesión
profesionales = Personal.objects.filter(profesion='Ingeniero')

# Obtener experiencia total
experiencia_total = Personal.objects.aggregate(
    total_meses=models.Sum('total_meses_experiencia_certificada')
)

# Filtrar por formación académica
especialistas = Personal.objects.filter(especializacion_1__isnull=False)

# Obtener experiencia total
experiencia_total = Personal.objects.aggregate(
    total_meses=models.Sum('total_meses_experiencia_certificada')
)
```

## Estructura del Proyecto

```
GESTION_HUMANA_CHVS/
├── archivos excel/
│   └── registros_personal_documentacion.xlsx
├── gestion_humana/
│   ├── formapp/
│   │   ├── models.py          # Modelo Personal
│   │   ├── views.py           # Vistas de la aplicación
│   │   ├── admin.py           # Configuración del admin
│   │   ├── apps.py            # Configuración de la app
│   │   ├── tests.py           # Tests
│   │   └── migrations/        # Migraciones de BD
│   ├── gestion_humana/
│   │   ├── settings.py        # Configuración global
│   │   ├── urls.py            # URLs principales
│   │   ├── wsgi.py            # Configuración WSGI
│   │   └── asgi.py            # Configuración ASGI
│   └── manage.py              # Script de gestión
└── README.md                  # Este archivo
```

## Consideraciones Técnicas

### Rendimiento
- La tabla única puede crecer significativamente
- Considerar índices en campos de búsqueda frecuente (`cedula`, `profesion`)
- Implementar paginación en consultas grandes

### Seguridad
- Validar entrada de datos
- Implementar permisos de usuario
- Proteger información sensible

### Mantenimiento
- Realizar backups regulares
- Monitorear crecimiento de la base de datos
- Actualizar migraciones cuando se modifiquen modelos

## Próximas Mejoras

1. **Normalización**: Dividir en tablas relacionadas (Direcciones, Experiencias, Formaciones)
2. **API REST**: Implementar API para integración con otros sistemas
3. **Interfaz Web**: Crear formularios y vistas para gestión
4. **Reportes**: Generar reportes automáticos
5. **Importación Automática**: Comando para importar datos del Excel periódicamente

## Soporte

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo.

---

**Nota**: Este sistema está diseñado específicamente para manejar la documentación del personal según el formato del archivo Excel proporcionado. Cualquier modificación en la estructura de datos requerirá ajustes en el modelo y migraciones correspondientes.