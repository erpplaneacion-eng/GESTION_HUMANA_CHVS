"""
Vista pública de registro de candidatos.
Formulario multi-sección accesible sin autenticación.
VERSIÓN CORREGIDA CON FIXES PARA FLUJO DE CORRECCIÓN
"""
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
    """Vista pública de registro - SIN CAMBIOS"""
    if request.method == 'POST':
        form = InformacionBasicaPublicForm(request.POST, request.FILES)
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

        if form.is_valid():
            documentos_valid = documentos_form.is_valid()
            antecedentes_valid = antecedentes_form.is_valid()
            anexos_valid = anexos_form.is_valid()
            experiencia_valid = experiencia_formset.is_valid()
            basica_valid = basica_formset.is_valid()
            superior_valid = superior_formset.is_valid()
            academica_valid = academica_formset.is_valid()
            posgrado_valid = posgrado_formset.is_valid()
            especializacion_valid = especializacion_formset.is_valid()

            if documentos_valid and antecedentes_valid and anexos_valid and experiencia_valid and basica_valid and superior_valid and academica_valid and posgrado_valid and especializacion_valid:
                try:
                    with transaction.atomic():
                        informacion_basica = form.save()

                        documentos = documentos_form.save(commit=False)
                        documentos.informacion_basica = informacion_basica
                        documentos.save()

                        antecedentes = antecedentes_form.save(commit=False)
                        antecedentes.informacion_basica = informacion_basica
                        antecedentes.save()

                        anexos = anexos_form.save(commit=False)
                        anexos.informacion_basica = informacion_basica
                        anexos.save()

                        experiencia_formset.instance = informacion_basica
                        experiencia_formset.save()
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

                        enviar_correo_async(informacion_basica)

                        messages.success(request, '¡Formulario enviado con éxito! Recibirás un correo de confirmación en los próximos minutos.')
                        return redirect('formapp:public_form')
                except Exception as e:
                    messages.error(request, f'Error al guardar el formulario: {str(e)}')
            else:
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
    VERSIÓN CORREGIDA - Maneja correctamente campos disabled y validaciones.
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

    # Obtener campos editables
    campos_editables = set(applicant.campos_a_corregir or [])

    if request.method == 'POST':
        # ==============================================
        # FIX #1: RESTAURAR VALORES DE CAMPOS DISABLED
        # ==============================================
        # Los campos disabled no se envían en POST, debemos restaurar sus valores
        # desde la instancia de BD para que las validaciones funcionen
        
        post_data = request.POST.copy()  # Hacer copia mutable
        
        # Restaurar campos del formulario principal que NO están editables
        for field_name in InformacionBasicaForm.base_fields.keys():
            if field_name not in campos_editables:
                # Obtener valor actual de la BD
                current_value = getattr(applicant, field_name, None)
                if current_value is not None:
                    # Restaurar en POST data
                    if isinstance(current_value, bool):
                        post_data[field_name] = 'on' if current_value else ''
                    else:
                        post_data[field_name] = str(current_value)
        
        # Crear formularios con POST data restaurado
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

        # ==============================================
        # FIX #2: HACER OPCIONALES CAMPOS NO EDITABLES
        # ==============================================
        # Para evitar errores de validación, hacer que campos no editables sean opcionales
        if campos_editables:
            for field_name in form.fields:
                if field_name not in campos_editables:
                    form.fields[field_name].required = False
            
            # Hacer opcionales formsets que no están en campos editables
            if 'documentos_identidad' not in campos_editables:
                for field in documentos_form.fields.values():
                    field.required = False
            
            if 'antecedentes' not in campos_editables:
                for field in antecedentes_form.fields.values():
                    field.required = False
            
            if 'anexos_adicionales' not in campos_editables:
                for field in anexos_form.fields.values():
                    field.required = False
            
            if 'experiencia_laboral' not in campos_editables:
                for form_exp in experiencia_formset.forms:
                    for field in form_exp.fields.values():
                        field.required = False
            
            if 'educacion_basica' not in campos_editables:
                for form_bas in basica_formset.forms:
                    for field in form_bas.fields.values():
                        field.required = False
            
            if 'educacion_superior' not in campos_editables:
                for form_sup in superior_formset.forms:
                    for field in form_sup.fields.values():
                        field.required = False
            
            if 'formacion_academica' not in campos_editables:
                for form_aca in academica_formset.forms:
                    for field in form_aca.fields.values():
                        field.required = False
            
            if 'posgrado' not in campos_editables:
                for form_pos in posgrado_formset.forms:
                    for field in form_pos.fields.values():
                        field.required = False
            
            if 'especializacion' not in campos_editables:
                for form_esp in especializacion_formset.forms:
                    for field in form_esp.fields.values():
                        field.required = False

        # Validar todos los formularios
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

        # ==============================================
        # FIX #3: LOGGING DETALLADO DE ERRORES
        # ==============================================
        if not form_valid:
            logger.error(f'Errores en formulario principal: {form.errors}')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
        
        if not documentos_valid:
            logger.error(f'Errores en documentos: {documentos_form.errors}')
            for field, errors in documentos_form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en Documentos - {field}: {error}')
        
        if not antecedentes_valid:
            logger.error(f'Errores en antecedentes: {antecedentes_form.errors}')
        
        if not experiencia_valid:
            logger.error(f'Errores en experiencia: {experiencia_formset.errors}')

        # Validar que TODOS sean válidos
        if form_valid and documentos_valid and antecedentes_valid and anexos_valid and \
           experiencia_valid and basica_valid and superior_valid and academica_valid and \
           posgrado_valid and especializacion_valid:
            
            try:
                with transaction.atomic():
                    # ==============================================
                    # FIX #4: GUARDAR SIN update_fields
                    # ==============================================
                    # Simplemente guardamos normalmente, Django maneja qué campos cambiar
                    informacion_basica = form.save(commit=False)
                    informacion_basica.estado = 'CORREGIDO'
                    informacion_basica.token_correccion = None
                    informacion_basica.token_expiracion = None
                    informacion_basica.comentarios_correccion = request.POST.get('comentarios_correccion', '')
                    informacion_basica.save()  # Guardar TODOS los campos

                    # Guardar formsets solo si están en campos editables
                    if 'documentos_identidad' in campos_editables:
                        documentos = documentos_form.save(commit=False)
                        documentos.informacion_basica = informacion_basica
                        documentos.save()

                    if 'antecedentes' in campos_editables:
                        antecedentes_obj = antecedentes_form.save(commit=False)
                        antecedentes_obj.informacion_basica = informacion_basica
                        antecedentes_obj.save()

                    if 'anexos_adicionales' in campos_editables:
                        anexos = anexos_form.save(commit=False)
                        anexos.informacion_basica = informacion_basica
                        anexos.save()

                    if 'experiencia_laboral' in campos_editables:
                        experiencia_formset.save()
                        calcular_experiencia_total(informacion_basica)

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

                    # Actualizar historial
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
                logger.error(f'Error al guardar correcciones: {str(e)}', exc_info=True)
                messages.error(request, f'Error al guardar las correcciones: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores mostrados en el formulario.')
            logger.warning(f'Validación fallida para {applicant.cedula}. Campos editables: {campos_editables}')

    else:  # GET request
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

        # ==============================================
        # FIX #5: USAR readonly EN VEZ DE disabled
        # ==============================================
        # disabled no envía datos en POST, readonly sí pero no permite edición
        if campos_editables:
            def aplicar_estilo_editable(form_fields):
                for field_name in form_fields:
                    current_class = form_fields[field_name].widget.attrs.get('class', '')
                    form_fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                    form_fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'

            def aplicar_estilo_bloqueado(form_fields):
                for field_name in form_fields:
                    # USAR readonly EN VEZ DE disabled
                    form_fields[field_name].widget.attrs['readonly'] = 'readonly'
                    current_class = form_fields[field_name].widget.attrs.get('class', '')
                    form_fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                    form_fields[field_name].widget.attrs['style'] = 'pointer-events: none; cursor: not-allowed;'

            # Aplicar estilos al formulario principal
            for field_name in form.fields:
                if field_name in campos_editables:
                    current_class = form.fields[field_name].widget.attrs.get('class', '')
                    form.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3 campo-editable'
                    form.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'
                    form.fields[field_name].help_text = '<span style="color: #dc3545; font-weight: bold;">✏️ CORRIJA ESTE CAMPO</span>'
                else:
                    form.fields[field_name].widget.attrs['readonly'] = 'readonly'
                    current_class = form.fields[field_name].widget.attrs.get('class', '')
                    form.fields[field_name].widget.attrs['class'] = current_class + ' bg-light campo-bloqueado'
                    form.fields[field_name].widget.attrs['style'] = 'pointer-events: none; cursor: not-allowed;'

            # Aplicar a documentos
            if 'documentos_identidad' in campos_editables:
                aplicar_estilo_editable(documentos_form.fields)
            else:
                aplicar_estilo_bloqueado(documentos_form.fields)

            # Aplicar a antecedentes
            if 'antecedentes' in campos_editables:
                aplicar_estilo_editable(antecedentes_form.fields)
            else:
                aplicar_estilo_bloqueado(antecedentes_form.fields)

            # Aplicar a anexos
            if 'anexos_adicionales' in campos_editables:
                aplicar_estilo_editable(anexos_form.fields)
            else:
                aplicar_estilo_bloqueado(anexos_form.fields)

            # Aplicar a formsets
            def aplicar_estilos_formset(formset, editable):
                for form_item in formset.forms:
                    for field_name in form_item.fields:
                        if field_name not in ['DELETE', 'id']:
                            if editable:
                                current_class = form_item.fields[field_name].widget.attrs.get('class', '')
                                form_item.fields[field_name].widget.attrs['class'] = current_class + ' border border-danger border-3'
                                form_item.fields[field_name].widget.attrs['style'] = 'background-color: #fff5f5;'
                            else:
                                form_item.fields[field_name].widget.attrs['readonly'] = 'readonly'
                                current_class = form_item.fields[field_name].widget.attrs.get('class', '')
                                form_item.fields[field_name].widget.attrs['class'] = current_class + ' bg-light'
                                form_item.fields[field_name].widget.attrs['style'] = 'pointer-events: none;'

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
        'is_public_correction': True,
        'campos_editables': list(campos_editables),  # Para mostrar en template
    }
    return render(request, 'formapp/applicant_edit.html', context)

