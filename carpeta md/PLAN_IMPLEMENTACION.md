# Plan de Implementacion - Documentos Faltantes

## Resumen del Proyecto

Este plan detalla la implementacion de los documentos y requisitos faltantes en el sistema de Gestion Humana CAVJP, siguiendo las normativas colombianas para contratacion de personal.

---

## Estado Actual vs Requerimientos

### Implementado
- Certificaciones de experiencia laboral (obligatorio)
- Informacion de tarjeta profesional (numero, tipo, fecha)
- Generacion de ANEXO 11 (PDF)
- Datos personales basicos

### Por Implementar
- Documentos de identidad y autorizacion
- Documentos academicos
- Antecedentes y verificaciones
- Anexos adicionales

---

## FASE 1: Documentos de Identidad y Autorizacion

### Objetivo
Agregar campos para documentos de identificacion personal y autorizaciones legales.

### Modelos a Crear/Modificar

#### 1.1 Nuevo Modelo: `DocumentosIdentidad`
```python
class DocumentosIdentidad(models.Model):
    informacion_basica = models.OneToOneField(InformacionBasica, on_delete=models.CASCADE)

    # Fotocopia cedula
    fotocopia_cedula = models.FileField(upload_to='documentos_identidad/')

    # Libreta militar (solo hombres)
    libreta_militar = models.FileField(upload_to='documentos_identidad/', blank=True, null=True)
    numero_libreta_militar = models.CharField(max_length=50, blank=True, null=True)
    distrito_militar = models.CharField(max_length=100, blank=True, null=True)

    # Carta autorizacion datos personales
    carta_autorizacion_datos = models.FileField(upload_to='autorizaciones/')
    fecha_autorizacion = models.DateField()
```

### Tareas
- [ ] Crear modelo DocumentosIdentidad
- [ ] Crear migracion
- [ ] Crear formulario DocumentosIdentidadForm
- [ ] Agregar al template de registro
- [ ] Agregar al admin
- [ ] Probar funcionalidad

### Archivos a Modificar
- `formapp/models.py`
- `formapp/forms.py`
- `formapp/views.py`
- `formapp/admin.py`
- `formapp/templates/formapp/public_form.html`

---

## FASE 2: Documentos Academicos

### Objetivo
Agregar campos para subir documentos academicos que respalden la informacion registrada.

### Modelos a Modificar

#### 2.1 Modificar Modelo: `InformacionAcademica`
Agregar campos:
```python
# Fotocopia del titulo/diploma
fotocopia_titulo = models.FileField(upload_to='titulos_academicos/')

# Fotocopia tarjeta profesional
fotocopia_tarjeta_profesional = models.FileField(upload_to='tarjetas_profesionales/', blank=True, null=True)

# Certificado de vigencia de tarjeta profesional
certificado_vigencia_tarjeta = models.FileField(upload_to='certificados_vigencia/', blank=True, null=True)
fecha_vigencia_tarjeta = models.DateField(blank=True, null=True)
```

### Tareas
- [ ] Modificar modelo InformacionAcademica
- [ ] Crear migracion
- [ ] Actualizar InformacionAcademicaForm
- [ ] Actualizar template
- [ ] Actualizar admin
- [ ] Probar funcionalidad

### Archivos a Modificar
- `formapp/models.py`
- `formapp/forms.py`
- `formapp/admin.py`
- `formapp/templates/formapp/public_form.html`

---

## FASE 3: Antecedentes y Verificaciones

### Objetivo
Agregar campos para todos los certificados de antecedentes requeridos por ley.

### Modelos a Crear

#### 3.1 Nuevo Modelo: `Antecedentes`
```python
class Antecedentes(models.Model):
    informacion_basica = models.OneToOneField(InformacionBasica, on_delete=models.CASCADE)

    # Antecedentes disciplinarios (Procuraduria)
    certificado_procuraduria = models.FileField(upload_to='antecedentes/')
    fecha_procuraduria = models.DateField()

    # Antecedentes fiscales (Contraloria)
    certificado_contraloria = models.FileField(upload_to='antecedentes/')
    fecha_contraloria = models.DateField()

    # Antecedentes judiciales (Policia)
    certificado_policia = models.FileField(upload_to='antecedentes/')
    fecha_policia = models.DateField()

    # Registro de medidas correctivas
    certificado_medidas_correctivas = models.FileField(upload_to='antecedentes/')
    fecha_medidas_correctivas = models.DateField()

    # Inhabilidades por delitos sexuales
    certificado_delitos_sexuales = models.FileField(upload_to='antecedentes/')
    fecha_delitos_sexuales = models.DateField()
```

### Tareas
- [ ] Crear modelo Antecedentes
- [ ] Crear migracion
- [ ] Crear formulario AntecedentesForm
- [ ] Agregar al template de registro
- [ ] Agregar al admin
- [ ] Probar funcionalidad

### Archivos a Modificar
- `formapp/models.py`
- `formapp/forms.py`
- `formapp/views.py`
- `formapp/admin.py`
- `formapp/templates/formapp/public_form.html`

---

## FASE 4: Anexos Adicionales

### Objetivo
Agregar campos para anexos especificos requeridos.

### Modelos a Crear

#### 4.1 Nuevo Modelo: `AnexosAdicionales`
```python
class AnexosAdicionales(models.Model):
    informacion_basica = models.OneToOneField(InformacionBasica, on_delete=models.CASCADE)

    # ANEXO 03 - Datos Personales
    anexo_03_datos_personales = models.FileField(upload_to='anexos/', blank=True, null=True)

    # Carta de intencion o contrato
    carta_intencion = models.FileField(upload_to='anexos/', blank=True, null=True)

    # Otros documentos opcionales
    otros_documentos = models.FileField(upload_to='anexos/', blank=True, null=True)
    descripcion_otros = models.TextField(blank=True, null=True)
```

### Tareas
- [ ] Crear modelo AnexosAdicionales
- [ ] Crear migracion
- [ ] Crear formulario AnexosAdicionalesForm
- [ ] Agregar al template de registro
- [ ] Agregar al admin
- [ ] Probar funcionalidad

---

## FASE 5: Actualizacion del Backend

### Objetivo
Actualizar vistas, validadores y logica de negocio.

### Tareas

#### 5.1 Actualizar Views
- [ ] Modificar `public_form_view` para manejar nuevos formularios
- [ ] Actualizar logica de guardado atomico
- [ ] Agregar validaciones adicionales

#### 5.2 Actualizar Exportaciones
- [ ] Actualizar `create_excel_for_person` para incluir nuevos documentos
- [ ] Actualizar `download_individual_zip` para incluir todos los archivos
- [ ] Actualizar `download_all_zip`

#### 5.3 Actualizar Email
- [ ] Actualizar template de confirmacion si es necesario

### Archivos a Modificar
- `formapp/views.py`
- `formapp/validators.py`

---

## FASE 6: Actualizacion del Frontend

### Objetivo
Actualizar templates para mostrar y capturar los nuevos campos.

### Tareas

#### 6.1 Template de Registro Publico
- [ ] Agregar seccion "Documentos de Identidad"
- [ ] Agregar campos de documentos academicos
- [ ] Agregar seccion "Antecedentes"
- [ ] Agregar seccion "Anexos Adicionales"
- [ ] Agregar validaciones JavaScript
- [ ] Mantener UX consistente

#### 6.2 Template de Detalle
- [ ] Mostrar todos los nuevos documentos
- [ ] Links de descarga para cada archivo

#### 6.3 Template de Edicion
- [ ] Permitir editar/reemplazar documentos

### Archivos a Modificar
- `formapp/templates/formapp/public_form.html`
- `formapp/templates/formapp/applicant_detail.html`
- `formapp/templates/formapp/applicant_edit.html`

---

## FASE 7: Panel de Administracion

### Objetivo
Actualizar el admin de Django para gestionar todos los nuevos campos.

### Tareas
- [ ] Agregar inlines para nuevos modelos
- [ ] Configurar list_display, list_filter, search_fields
- [ ] Agregar acciones personalizadas si es necesario

### Archivos a Modificar
- `formapp/admin.py`

---

## Consideraciones Tecnicas

### Validaciones de Archivos
Todos los nuevos campos de archivo usaran los mismos validadores existentes:
- `validate_file_size` (max 10MB)
- `validate_file_extension` (pdf, jpg, png)
- `validate_file_mime`

### Almacenamiento
- Todos los archivos se almacenaran en Cloudinary
- Organizados en carpetas por tipo de documento

### Migraciones
- Cada fase incluye sus propias migraciones
- Se ejecutaran en orden para mantener integridad
- Campos nuevos seran opcionales inicialmente para no romper registros existentes

### Compatibilidad
- No se modificaran campos existentes
- Solo se agregaran nuevos campos/modelos
- El sistema actual seguira funcionando sin cambios

---

## Orden de Ejecucion

1. **Fase 1** - Documentos de Identidad (ACTUAL)
2. **Fase 2** - Documentos Academicos
3. **Fase 3** - Antecedentes
4. **Fase 4** - Anexos Adicionales
5. **Fase 5** - Backend
6. **Fase 6** - Frontend
7. **Fase 7** - Admin

---

## Notas Importantes

1. **Backup**: Realizar backup de la base de datos antes de cada fase
2. **Testing**: Probar cada fase en desarrollo antes de produccion
3. **Rollback**: Cada migracion puede revertirse si es necesario
4. **Documentacion**: Actualizar este README al completar cada fase

---

## Progreso

| Fase | Estado | Migracion | Descripcion |
|------|--------|-----------|-------------|
| Fase 1 | COMPLETADA | 0014_documentos_identidad.py | Documentos de Identidad y Autorizacion |
| Fase 2 | COMPLETADA | 0015_documentos_academicos.py | Documentos Academicos |
| Fase 3 | COMPLETADA | 0016_antecedentes.py | Antecedentes y Verificaciones |
| Fase 4 | COMPLETADA | 0017_anexos_adicionales.py | Anexos Adicionales |
| Fase 5 | COMPLETADA | - | Backend (Views, Forms) |
| Fase 6 | COMPLETADA | - | Frontend (Templates) |
| Fase 7 | COMPLETADA | - | Admin |

---

## Resumen de Implementacion

### Modelos Nuevos Creados:
1. **DocumentosIdentidad** - Cedula, libreta militar, autorizacion datos
2. **Antecedentes** - Procuraduria, Contraloria, Policia, RNMC, Delitos sexuales
3. **AnexosAdicionales** - ANEXO 03, Carta intencion, Otros documentos

### Modelos Modificados:
1. **InformacionAcademica** - Agregados campos para fotocopia titulo, tarjeta profesional, certificado vigencia

### Total de Campos de Archivo Agregados: 19
- Fotocopia cedula
- Libreta militar
- Carta autorizacion datos
- Fotocopia titulo (por cada formacion)
- Fotocopia tarjeta profesional (por cada formacion)
- Certificado vigencia tarjeta (por cada formacion)
- Certificado Procuraduria
- Certificado Contraloria
- Certificado Policia
- Certificado Medidas Correctivas
- Certificado Delitos Sexuales
- ANEXO 03
- Carta de intencion
- Otros documentos

---

## Contacto

Para dudas o sugerencias sobre este plan, contactar al equipo de desarrollo.

---

*Documento creado: 2025-11-18*
*Ultima actualizacion: 2025-11-18*
*Estado: IMPLEMENTACION COMPLETADA*