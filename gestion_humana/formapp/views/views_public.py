"""
Vista pública de registro de candidatos.
Formulario multi-sección accesible sin autenticación.
Refactorizado desde views.py para mejor organización.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from ..models import (
    InformacionBasica,
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales,
)
from ..forms import (
    InformacionBasicaPublicForm,
    InformacionBasicaForm,
    ExperienciaLaboralFormSet,
    InformacionAcademicaFormSet,
    PosgradoFormSet,
    EspecializacionFormSet,
    EducacionBasicaFormSet,
    EducacionSuperiorFormSet,
    DocumentosIdentidadForm,
    AntecedentesForm,
    AnexosAdicionalesForm,
)
from ..services import calcular_experiencia_total, enviar_correo_async

import logging

logger = logging.getLogger(__name__)


def public_form_view(request):
    if request.method == 'POST':
        form = InformacionBasicaPublicForm(request.POST, request.FILES)
        # Obtener género para pasarlo al formulario de documentos
        genero = request.POST.get('genero', '')
        documentos_form = DocumentosIdentidadForm(request.POST, request.FILES, genero=genero)
        antecedentes_form = AntecedentesForm(request.POST, request.FILES)
        anexos_form = AnexosAdicionalesForm(request.POST, request.FILES)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES)
        basica_formset = EducacionBasicaFormSet(request.POST, request.FILES)
        superior_formset = EducacionSuperiorFormSet(request.POST, request.FILES)
        academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES)
        posgrado_formset = PosgradoFormSet(request.POST, request.FILES)
        especializacion_formset = EspecializacionFormSet(request.POST, request.FILES)

        # CRÍTICO: Validar TODOS los formularios ANTES de guardar cualquier cosa
        if form.is_valid():
            # Validar todos los formsets y formularios primero
            documentos_valid = documentos_form.is_valid()
            antecedentes_valid = antecedentes_form.is_valid()
            anexos_valid = anexos_form.is_valid()
            experiencia_valid = experiencia_formset.is_valid()
            basica_valid = basica_formset.is_valid()
            superior_valid = superior_formset.is_valid()
            academica_valid = academica_formset.is_valid()
            posgrado_valid = posgrado_formset.is_valid()
            especializacion_valid = especializacion_formset.is_valid()

            # Solo proceder si TODO es válido
            if documentos_valid and antecedentes_valid and anexos_valid and experiencia_valid and basica_valid and superior_valid and academica_valid and posgrado_valid and especializacion_valid:
                try:
                    with transaction.atomic():
                        informacion_basica = form.save()

                        # Guardar documentos de identidad
                        documentos = documentos_form.save(commit=False)
                        documentos.informacion_basica = informacion_basica
                        documentos.save()

                        # Guardar antecedentes
                        antecedentes = antecedentes_form.save(commit=False)
                        antecedentes.informacion_basica = informacion_basica
                        antecedentes.save()

                        # Guardar anexos adicionales (opcional)
                        anexos = anexos_form.save(commit=False)
                        anexos.informacion_basica = informacion_basica
                        anexos.save()

                        # Asociar formsets con la instancia guardada y guardar
                        experiencia_formset.instance = informacion_basica
                        experiencia_formset.save()
                        # Calcular experiencia automáticamente
                        calcular_experiencia_total(informacion_basica)

                        basica_formset.instance = informacion_basica
                        basica_formset.save()

                        superior_formset.instance = informacion_basica
                        superior_formset.save()

                        academica_formset.instance = informacion_basica
                        academica_formset.save()

                        posgrado_formset.instance = informacion_basica
                        posgrado_formset.save()

                        especializacion_formset.instance = informacion_basica
                        especializacion_formset.save()

                        # Enviar correo de confirmación al usuario de manera asíncrona
                        enviar_correo_async(informacion_basica)

                        messages.success(request, '¡Formulario enviado con éxito! Recibirás un correo de confirmación en los próximos minutos.')
                        return redirect('formapp:public_form')
                except Exception as e:
                    messages.error(request, f'Error al guardar el formulario: {str(e)}')
            else:
                # Mostrar errores específicos de cada formulario/formset que falló
                if not documentos_valid:
                    for field, error_list in documentos_form.errors.items():
                        for error in error_list:
                            messages.error(request, f'Error en Documentos de Identidad - {field}: {error}')

                if not antecedentes_valid:
                    for field, error_list in antecedentes_form.errors.items():
                        for error in error_list:
                            messages.error(request, f'Error en Antecedentes - {field}: {error}')

                if not experiencia_valid:
                    for i, form_errors in enumerate(experiencia_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Experiencia Laboral #{i+1} - {field}: {error}')

                if not basica_valid:
                    for i, form_errors in enumerate(basica_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Educación Básica #{i+1} - {field}: {error}')

                if not superior_valid:
                    for i, form_errors in enumerate(superior_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Educación Superior (Técnico/Tecnólogo) #{i+1} - {field}: {error}')

                if not academica_valid:
                    for i, form_errors in enumerate(academica_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Información Académica #{i+1} - {field}: {error}')

                if not posgrado_valid:
                    for i, form_errors in enumerate(posgrado_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Posgrado #{i+1} - {field}: {error}')

                if not especializacion_valid:
                    for i, form_errors in enumerate(especializacion_formset.errors):
                        if form_errors:
                            for field, error_list in form_errors.items():
                                for error in error_list:
                                    messages.error(request, f'Error en Especialización #{i+1} - {field}: {error}')

                messages.warning(request, 'Por favor corrija los errores en el formulario antes de enviarlo.')
        else:
            messages.warning(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformacionBasicaPublicForm()
        documentos_form = DocumentosIdentidadForm()
        antecedentes_form = AntecedentesForm()
        anexos_form = AnexosAdicionalesForm()
        experiencia_formset = ExperienciaLaboralFormSet()
        basica_formset = EducacionBasicaFormSet()
        superior_formset = EducacionSuperiorFormSet()
        academica_formset = InformacionAcademicaFormSet()
        posgrado_formset = PosgradoFormSet()
        especializacion_formset = EspecializacionFormSet()

    context = {
        'form': form,
        'documentos_form': documentos_form,
        'antecedentes_form': antecedentes_form,
        'anexos_form': anexos_form,
        'experiencia_formset': experiencia_formset,
        'basica_formset': basica_formset,
        'superior_formset': superior_formset,
        'academica_formset': academica_formset,
        'posgrado_formset': posgrado_formset,
        'especializacion_formset': especializacion_formset,
    }
    return render(request, 'formapp/public_form.html', context)


def public_update_view(request, token):
    """
    Vista pública para corregir información mediante token seguro.
    """
    # 1. Validar existencia del token
    try:
        applicant = InformacionBasica.objects.get(token_correccion=token)
    except InformacionBasica.DoesNotExist:
        messages.error(request, 'El enlace de corrección no es válido o no existe.')
        return redirect('formapp:public_form')

    # 2. Validar expiración del token
    if not applicant.token_expiracion or applicant.token_expiracion < timezone.now():
        messages.error(request, 'Este enlace de corrección ha expirado. Por favor comunícate con Gestión Humana.')
        return redirect('formapp:public_form')

    # Obtener instancias relacionadas
    try:
        documentos_identidad = applicant.documentos_identidad
    except DocumentosIdentidad.DoesNotExist:
        documentos_identidad = None

    try:
        antecedentes = applicant.antecedentes
    except Antecedentes.DoesNotExist:
        antecedentes = None

    try:
        anexos_adicionales = applicant.anexos_adicionales
    except AnexosAdicionales.DoesNotExist:
        anexos_adicionales = None

    if request.method == 'POST':
        # Obtener campos editables para validación selectiva
        campos_editables = set(applicant.campos_a_corregir or [])

        # ==============================================================
        # FIX CRÍTICO: Restaurar valores de campos disabled antes de validar
        # Los campos disabled no se envían en POST, causando errores de validación
        # ==============================================================
        post_data = request.POST.copy()  # Hacer copia mutable del POST
        
        # Restaurar valores desde la BD para campos que NO están editables
        # Lista de campos internos del sistema que NO deben restaurarse
        campos_excluir = ['campos_a_corregir', 'token_correccion', 'token_expiracion', 
                          'comentarios_correccion', 'estado']
        
        for field_name in InformacionBasicaForm.base_fields.keys():
            if field_name not in campos_editables and field_name not in campos_excluir:
                current_value = getattr(applicant, field_name, None)
                if current_value is not None:
                    if isinstance(current_value, bool):
                        post_data[field_name] = 'on' if current_value else ''
                    elif isinstance(current_value, (list, dict)):
                        # Para JSONField, convertir a JSON string válido
                        post_data[field_name] = json.dumps(current_value)
                    else:
                        post_data[field_name] = str(current_value)
        
        # Crear formularios con POST DATA RESTAURADO
        form = InformacionBasicaForm(post_data, request.FILES, instance=applicant)
        genero = post_data.get('genero', applicant.genero)
        documentos_form = DocumentosIdentidadForm(post_data, request.FILES, instance=documentos_identidad, genero=genero)
        antecedentes_form = AntecedentesForm(post_data, request.FILES, instance=antecedentes)
        anexos_form = AnexosAdicionalesForm(post_data, request.FILES, instance=anexos_adicionales)
        experiencia_formset = ExperienciaLaboralFormSet(post_data, request.FILES, instance=applicant)
        basica_formset = EducacionBasicaFormSet(post_data, request.FILES, instance=applicant)
        superior_formset = EducacionSuperiorFormSet(post_data, request.FILES, instance=applicant)
        academica_formset = InformacionAcademicaFormSet(post_data, request.FILES, instance=applicant)
        posgrado_formset = PosgradoFormSet(post_data, request.FILES, instance=applicant)
        especializacion_formset = EspecializacionFormSet(post_data, request.FILES, instance=applicant)

        # Remover validaciones de campos que NO están editables
        # Los campos deshabilitados no se envían en POST, así que debemos hacer campos no editables opcionales
        if campos_editables:
            # Hacer que campos NO editables sean opcionales para validación
            for field_name in form.fields:
                if field_name not in campos_editables:
                    form.fields[field_name].required = False

            # Validar solo formsets que están en campos editables
            validar_documentos = 'documentos_identidad' in campos_editables
            validar_antecedentes = 'antecedentes' in campos_editables
            validar_anexos = 'anexos_adicionales' in campos_editables
            validar_experiencia = 'experiencia_laboral' in campos_editables
            validar_basica = 'educacion_basica' in campos_editables
            validar_superior = 'educacion_superior' in campos_editables
            validar_academica = 'formacion_academica' in campos_editables
            validar_posgrado = 'posgrado' in campos_editables
            validar_especializacion = 'especializacion' in campos_editables

            # Si un formset NO está editable, hacer todos sus campos opcionales
            if not validar_documentos:
                for field in documentos_form.fields.values():
                    field.required = False
            if not validar_antecedentes:
                for field in antecedentes_form.fields.values():
                    field.required = False
            if not validar_anexos:
                for field in anexos_form.fields.values():
                    field.required = False
            if not validar_experiencia:
                for form_exp in experiencia_formset.forms:
                    for field in form_exp.fields.values():
                        field.required = False
            if not validar_basica:
                for form_bas in basica_formset.forms:
                    for field in form_bas.fields.values():
                        field.required = False
            if not validar_superior:
                for form_sup in superior_formset.forms:
                    for field in form_sup.fields.values():
                        field.required = False
            if not validar_academica:
                for form_aca in academica_formset.forms:
                    for field in form_aca.fields.values():
                        field.required = False
            if not validar_posgrado:
                for form_pos in posgrado_formset.forms:
                    for field in form_pos.fields.values():
                        field.required = False
            if not validar_especializacion:
                for form_esp in especializacion_formset.forms:
                    for field in form_esp.fields.values():
                        field.required = False

        # Ahora validar todos los formularios
        # Hacer opcionales los campos no editables para evitar errores de validación
        if campos_editables:
            for field_name in form.fields:
                if field_name not in campos_editables:
                    form.fields[field_name].required = False
        
        # Validar formularios
        form_valid = form.is_valid()
        documentos_valid = documentos_form.is_valid()
        antecedentes_valid = antecedentes_form.is_valid()
        anexos_valid = anexos_form.is_valid()
        experiencia_valid = experiencia_formset.is_valid()
        basica_valid = basica_formset.is_valid()
        superior_valid = superior_formset.is_valid()
        academica_valid = academica_formset.is_valid()
        posgrado_valid = posgrado_formset.is_valid()
        especializacion_valid = especializacion_formset.is_valid()
        
        # FIX: Logging detallado de errores para debugging
        if not form_valid:
            logger.error(f'[CORRECCIÓN] Errores formulario principal para {applicant.cedula}: {form.errors}')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
        
        if not documentos_valid:
            logger.error(f'[CORRECCIÓN] Errores documentos: {documentos_form.errors}')
        
        if not experiencia_valid:
            logger.error(f'[CORRECCIÓN] Errores experiencia: {experiencia_formset.errors}')
        
        if form_valid and documentos_valid and antecedentes_valid and anexos_valid and \
           experiencia_valid and basica_valid and superior_valid and academica_valid and \
           posgrado_valid and especializacion_valid:
            
            try:
                with transaction.atomic():
                    # GUARDAR SOLO LOS CAMPOS EDITABLES
                    # Los campos no editables mantienen sus valores actuales de la BD

                    # Guardar formulario principal (solo actualiza campos que vinieron en POST)
                    informacion_basica = form.save(commit=False)

                    # Actualizar estado y limpiar token para seguridad (un solo uso)
                    informacion_basica.estado = 'CORREGIDO'
                    informacion_basica.token_correccion = None
                    informacion_basica.token_expiracion = None

                    # Guardar comentarios del candidato sobre las correcciones
                    informacion_basica.comentarios_correccion = request.POST.get('comentarios_correccion', '')

                    # FIX #4: Guardar sin update_fields para evitar problemas con campos calculados
                    # Django automáticamente solo actualiza los campos que cambiaron
                    informacion_basica.save()
                    
                    logger.info(f'[CORRECCIÓN] Información guardada exitosamente para {applicant.cedula}. Estado: CORREGIDO')

                    # Guardar formsets solo si están en campos editables (completos o parciales)
                    campos_documentos = ['fotocopia_cedula', 'hoja_de_vida', 'libreta_militar', 
                                       'numero_libreta_militar', 'distrito_militar', 'clase_libreta']
                    if 'documentos_identidad' in campos_editables or any(c in campos_editables for c in campos_documentos):
                        documentos = documentos_form.save(commit=False)
                        documentos.informacion_basica = informacion_basica
                        documentos.save()

                    campos_antecedentes = ['certificado_procuraduria', 'fecha_procuraduria', 
                                         'certificado_contraloria', 'fecha_contraloria',
                                         'certificado_policia', 'fecha_policia',
                                         'certificado_medidas_correctivas', 'fecha_medidas_correctivas',
                                         'certificado_delitos_sexuales', 'fecha_delitos_sexuales']
                    if 'antecedentes' in campos_editables or any(c in campos_editables for c in campos_antecedentes):
                        antecedentes_obj = antecedentes_form.save(commit=False)
                        antecedentes_obj.informacion_basica = informacion_basica
                        antecedentes_obj.save()

                    campos_anexos = ['anexo_03_datos_personales', 'carta_intencion', 
                                   'otros_documentos', 'descripcion_otros']
                    if 'anexos_adicionales' in campos_editables or any(c in campos_editables for c in campos_anexos):
                        anexos = anexos_form.save(commit=False)
                        anexos.informacion_basica = informacion_basica
                        anexos.save()

                    if 'experiencia_laboral' in campos_editables:
                        experiencia_formset.save()
                    
                    # Recalcular experiencia (lógica idéntica a admin)
                    from datetime import datetime as dt
                    experiencias_modificadas = []
                    for form_exp in experiencia_formset:
                        if form_exp.instance.pk and not form_exp.cleaned_data.get('DELETE', False):
                            if form_exp.has_changed() and ('fecha_inicial' in form_exp.changed_data or 'fecha_terminacion' in form_exp.changed_data):
                                experiencia = form_exp.instance
                                if experiencia.fecha_inicial and experiencia.fecha_terminacion:
                                    fecha_inicio = dt.combine(experiencia.fecha_inicial, dt.min.time())
                                    fecha_fin = dt.combine(experiencia.fecha_terminacion, dt.min.time())
                                    delta = fecha_fin - fecha_inicio
                                    total_dias = delta.days
                                    anos = fecha_fin.year - fecha_inicio.year
                                    meses = fecha_fin.month - fecha_inicio.month
                                    dias = fecha_fin.day - fecha_inicio.day
                                    if dias < 0:
                                        meses -= 1
                                        if fecha_inicio.month == 1:
                                            ultimo_dia = dt(fecha_inicio.year - 1, 12, 31).day
                                        else:
                                            ultimo_dia = dt(fecha_inicio.year, fecha_inicio.month - 1, 1).day
                                        dias += ultimo_dia
                                    if meses < 0:
                                        anos -= 1
                                        meses += 12
                                    total_meses = (anos * 12) + meses
                                    experiencia.meses_experiencia = total_meses
                                    experiencia.dias_experiencia = total_dias
                                    experiencias_modificadas.append(experiencia)
                    
                        if experiencias_modificadas:
                            from ..models import ExperienciaLaboral
                            ExperienciaLaboral.objects.bulk_update(experiencias_modificadas, ['meses_experiencia', 'dias_experiencia'])

                        # Recalcular experiencia total solo si se modificó experiencia
                        calcular_experiencia_total(informacion_basica)

                    # Guardar otros formsets solo si están en campos editables
                    if 'educacion_basica' in campos_editables:
                        basica_formset.save()

                    if 'educacion_superior' in campos_editables:
                        superior_formset.save()

                    if 'formacion_academica' in campos_editables:
                        academica_formset.save()

                    if 'posgrado' in campos_editables:
                        posgrado_formset.save()

                    if 'especializacion' in campos_editables:
                        especializacion_formset.save()

                    # Actualizar el registro en historial de correcciones
                    from ..models import HistorialCorreccion
                    historial = HistorialCorreccion.objects.filter(
                        informacion_basica=informacion_basica
                    ).order_by('-fecha_solicitud').first()

                    if historial:
                        historial.fecha_correccion = timezone.now()
                        historial.comentarios_candidato = informacion_basica.comentarios_correccion
                        historial.save()

                    # Enviar notificación al administrador
                    from ..services import enviar_correo_notificacion_admin
                    enviar_correo_notificacion_admin(informacion_basica, informacion_basica.comentarios_correccion)

                    messages.success(request, '¡Información corregida y enviada exitosamente! Gracias por tu gestión.')
                    return redirect('formapp:public_form')

            except Exception as e:
                messages.error(request, f'Error al guardar las correcciones: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores mostrados en el formulario.')
            logger.warning(f'[CORRECCIÓN] Validación fallida para {applicant.cedula}. Campos editables: {list(campos_editables)}')
    else:
        form = InformacionBasicaForm(instance=applicant)
        documentos_form = DocumentosIdentidadForm(instance=documentos_identidad, genero=applicant.genero)
        antecedentes_form = AntecedentesForm(instance=antecedentes)
        anexos_form = AnexosAdicionalesForm(instance=anexos_adicionales)
        experiencia_formset = ExperienciaLaboralFormSet(instance=applicant)
        basica_formset = EducacionBasicaFormSet(instance=applicant)
        superior_formset = EducacionSuperiorFormSet(instance=applicant)
        academica_formset = InformacionAcademicaFormSet(instance=applicant)
        posgrado_formset = PosgradoFormSet(instance=applicant)
        especializacion_formset = EspecializacionFormSet(instance=applicant)

        # RESTRICCIÓN DE CAMPOS: Solo permitir editar campos seleccionados por el admin
        campos_editables = set(applicant.campos_a_corregir or [])

        # Si hay campos a corregir definidos, aplicar restricciones
        if campos_editables:
            # LÓGICA INVERTIDA: Deshabilitar TODOS los campos y resaltar solo los EDITABLES

            # 1. Procesar campos del formulario principal
            for field_name in form.fields:
                if field_name in campos_editables:
                    # Campo EDITABLE: Resaltar en rojo con borde grueso
                    current_class = form.fields[field_name].widget.attrs.get('class', '')
                    form.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                    form.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5; border-width: 3px !important;'
                    form.fields[field_name].help_text = '<span style="color: #dc3545; font-weight: bold;">✏️ CORRIJA ESTE CAMPO</span>'
                else:
                    # Campo BLOQUEADO: Usar readonly en vez de disabled
                    # FIX: disabled no envía datos en POST, readonly sí pero no permite edición
                    form.fields[field_name].widget.attrs['readonly'] = 'readonly'
                    current_class = form.fields[field_name].widget.attrs.get('class', '')
                    form.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                    form.fields[field_name].widget.attrs['style'] = 'pointer-events: none; cursor: not-allowed;'

            # Función auxiliar para aplicar estilos a formularios
            def aplicar_estilo_editable(form_fields):
                """Aplica estilo rojo a campos editables"""
                for field_name in form_fields:
                    current_class = form_fields[field_name].widget.attrs.get('class', '')
                    form_fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                    form_fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5; border-width: 3px !important;'

            def aplicar_estilo_bloqueado(form_fields):
                """Aplica estilo gris y deshabilita campos"""
                # FIX: Usar readonly en vez de disabled
                for field_name in form_fields:
                    form_fields[field_name].widget.attrs['readonly'] = 'readonly'
                    current_class = form_fields[field_name].widget.attrs.get('class', '')
                    form_fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                    form_fields[field_name].widget.attrs['style'] = 'pointer-events: none; cursor: not-allowed;'

            # 2. Procesar documentos_identidad (formset completo o campos individuales)
            campos_documentos = ['fotocopia_cedula', 'hoja_de_vida', 'libreta_militar', 
                               'numero_libreta_militar', 'distrito_militar', 'clase_libreta']
            
            # Verificar si algún campo específico de documentos está en campos_editables
            campos_doc_editables = [c for c in campos_documentos if c in campos_editables]
            
            if 'documentos_identidad' in campos_editables:
                # Marcar TODO el formset
                aplicar_estilo_editable(documentos_form.fields)
            elif campos_doc_editables:
                # Marcar solo campos específicos
                for field_name in documentos_form.fields:
                    if field_name in campos_doc_editables:
                        current_class = documentos_form.fields[field_name].widget.attrs.get('class', '')
                        documentos_form.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                        documentos_form.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'
                    else:
                        documentos_form.fields[field_name].widget.attrs['readonly'] = 'readonly'
                        current_class = documentos_form.fields[field_name].widget.attrs.get('class', '')
                        documentos_form.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                        documentos_form.fields[field_name].widget.attrs['style'] = 'pointer-events: none;'
            else:
                # Bloquear todo
                aplicar_estilo_bloqueado(documentos_form.fields)

            # 3. Procesar antecedentes (formset completo o campos individuales)
            campos_antecedentes = ['certificado_procuraduria', 'fecha_procuraduria', 
                                 'certificado_contraloria', 'fecha_contraloria',
                                 'certificado_policia', 'fecha_policia',
                                 'certificado_medidas_correctivas', 'fecha_medidas_correctivas',
                                 'certificado_delitos_sexuales', 'fecha_delitos_sexuales']
            
            campos_ant_editables = [c for c in campos_antecedentes if c in campos_editables]
            
            if 'antecedentes' in campos_editables:
                # Marcar TODO el formset
                aplicar_estilo_editable(antecedentes_form.fields)
            elif campos_ant_editables:
                # Marcar solo campos específicos
                for field_name in antecedentes_form.fields:
                    if field_name in campos_ant_editables:
                        current_class = antecedentes_form.fields[field_name].widget.attrs.get('class', '')
                        antecedentes_form.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                        antecedentes_form.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'
                    else:
                        antecedentes_form.fields[field_name].widget.attrs['readonly'] = 'readonly'
                        current_class = antecedentes_form.fields[field_name].widget.attrs.get('class', '')
                        antecedentes_form.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                        antecedentes_form.fields[field_name].widget.attrs['style'] = 'pointer-events: none;'
            else:
                # Bloquear todo
                aplicar_estilo_bloqueado(antecedentes_form.fields)

            # 4. Procesar anexos_adicionales (formset completo o campos individuales)
            campos_anexos = ['anexo_03_datos_personales', 'carta_intencion', 
                           'otros_documentos', 'descripcion_otros']
            
            campos_anx_editables = [c for c in campos_anexos if c in campos_editables]
            
            if 'anexos_adicionales' in campos_editables:
                # Marcar TODO el formset
                aplicar_estilo_editable(anexos_form.fields)
            elif campos_anx_editables:
                # Marcar solo campos específicos
                for field_name in anexos_form.fields:
                    if field_name in campos_anx_editables:
                        current_class = anexos_form.fields[field_name].widget.attrs.get('class', '')
                        anexos_form.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                        anexos_form.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'
                    else:
                        anexos_form.fields[field_name].widget.attrs['readonly'] = 'readonly'
                        current_class = anexos_form.fields[field_name].widget.attrs.get('class', '')
                        anexos_form.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                        anexos_form.fields[field_name].widget.attrs['style'] = 'pointer-events: none;'
            else:
                # Bloquear todo
                aplicar_estilo_bloqueado(anexos_form.fields)

            # 5. Procesar formsets - CRÍTICO: Iterar sobre TODAS las formas del formset
            def aplicar_estilos_formset(formset, editable):
                """Aplica estilos a todos los campos de todas las formas en un formset"""
                for form_item in formset.forms:
                    for field_name in form_item.fields:
                        if field_name not in ['DELETE', 'id']:
                            if editable:
                                current_class = form_item.fields[field_name].widget.attrs.get('class', '')
                                form_item.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                                form_item.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5; border-width: 3px !important;'
                            else:
                                # FIX: Usar readonly en vez de disabled
                                form_item.fields[field_name].widget.attrs['readonly'] = 'readonly'
                                current_class = form_item.fields[field_name].widget.attrs.get('class', '')
                                form_item.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                                form_item.fields[field_name].widget.attrs['style'] = 'pointer-events: none; cursor: not-allowed;'

            # Aplicar estilos a cada formset
            aplicar_estilos_formset(experiencia_formset, 'experiencia_laboral' in campos_editables)
            aplicar_estilos_formset(basica_formset, 'educacion_basica' in campos_editables)
            aplicar_estilos_formset(superior_formset, 'educacion_superior' in campos_editables)
            aplicar_estilos_formset(academica_formset, 'formacion_academica' in campos_editables)
            aplicar_estilos_formset(posgrado_formset, 'posgrado' in campos_editables)
            aplicar_estilos_formset(especializacion_formset, 'especializacion' in campos_editables)

    context = {
        'form': form,
        'documentos_form': documentos_form,
        'antecedentes_form': antecedentes_form,
        'anexos_form': anexos_form,
        'experiencia_formset': experiencia_formset,
        'basica_formset': basica_formset,
        'superior_formset': superior_formset,
        'academica_formset': academica_formset,
        'posgrado_formset': posgrado_formset,
        'especializacion_formset': especializacion_formset,
        'applicant': applicant,
        'is_public_correction': True, # Flag para ajustar el template
    }
    return render(request, 'formapp/applicant_edit.html', context)
