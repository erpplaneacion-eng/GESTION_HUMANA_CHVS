"""
Vista pública de registro de candidatos.
Formulario multi-sección accesible sin autenticación.
Refactorizado desde views.py para mejor organización.
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
        # Usamos InformacionBasicaForm (el mismo del admin) para permitir edición completa
        form = InformacionBasicaForm(request.POST, request.FILES, instance=applicant)
        genero = request.POST.get('genero', applicant.genero)
        documentos_form = DocumentosIdentidadForm(request.POST, request.FILES, instance=documentos_identidad, genero=genero)
        antecedentes_form = AntecedentesForm(request.POST, request.FILES, instance=antecedentes)
        anexos_form = AnexosAdicionalesForm(request.POST, request.FILES, instance=anexos_adicionales)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=applicant)
        basica_formset = EducacionBasicaFormSet(request.POST, request.FILES, instance=applicant)
        superior_formset = EducacionSuperiorFormSet(request.POST, request.FILES, instance=applicant)
        academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES, instance=applicant)
        posgrado_formset = PosgradoFormSet(request.POST, request.FILES, instance=applicant)
        especializacion_formset = EspecializacionFormSet(request.POST, request.FILES, instance=applicant)

        if form.is_valid() and documentos_form.is_valid() and antecedentes_form.is_valid() and \
           anexos_form.is_valid() and experiencia_formset.is_valid() and basica_formset.is_valid() and \
           superior_formset.is_valid() and academica_formset.is_valid() and posgrado_formset.is_valid() and \
           especializacion_formset.is_valid():
            
            try:
                with transaction.atomic():
                    informacion_basica = form.save(commit=False)
                    # Actualizar estado y limpiar token para seguridad (un solo uso)
                    informacion_basica.estado = 'CORREGIDO'
                    informacion_basica.token_correccion = None
                    informacion_basica.token_expiracion = None
                    # Guardar comentarios del candidato sobre las correcciones
                    informacion_basica.comentarios_correccion = request.POST.get('comentarios_correccion', '')
                    informacion_basica.save()

                    documentos = documentos_form.save(commit=False)
                    documentos.informacion_basica = informacion_basica
                    documentos.save()

                    antecedentes_obj = antecedentes_form.save(commit=False)
                    antecedentes_obj.informacion_basica = informacion_basica
                    antecedentes_obj.save()

                    anexos = anexos_form.save(commit=False)
                    anexos.informacion_basica = informacion_basica
                    anexos.save()

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

                    calcular_experiencia_total(informacion_basica)
                    basica_formset.save()
                    superior_formset.save()
                    academica_formset.save()
                    posgrado_formset.save()
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
            messages.error(request, 'Por favor corrige los errores en el formulario.')
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

        # Mapeo de campos a formularios para deshabilitar campos no editables
        # Campos del formulario principal (InformacionBasica)
        campos_info_basica = {
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'cedula', 'genero', 'tipo_via', 'numero_via', 'numero_casa',
            'complemento_direccion', 'barrio', 'telefono', 'correo',
            'poblacion_diferencial', 'acepta_politica'
        }

        # Si hay campos a corregir definidos, deshabilitar todos los demás
        if campos_editables:
            # Deshabilitar campos del formulario principal que NO estén en la lista
            for field_name in form.fields:
                if field_name not in campos_editables:
                    form.fields[field_name].disabled = True
                    form.fields[field_name].widget.attrs['readonly'] = True
                    form.fields[field_name].widget.attrs['class'] = form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'
                    form.fields[field_name].help_text = '🔒 Este campo no está habilitado para corrección'

            # Deshabilitar documentos_identidad si no está en la lista
            if 'documentos_identidad' not in campos_editables:
                for field_name in documentos_form.fields:
                    documentos_form.fields[field_name].disabled = True
                    documentos_form.fields[field_name].widget.attrs['readonly'] = True
                    documentos_form.fields[field_name].widget.attrs['class'] = documentos_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            # Deshabilitar antecedentes si no está en la lista
            if 'antecedentes' not in campos_editables:
                for field_name in antecedentes_form.fields:
                    antecedentes_form.fields[field_name].disabled = True
                    antecedentes_form.fields[field_name].widget.attrs['readonly'] = True
                    antecedentes_form.fields[field_name].widget.attrs['class'] = antecedentes_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            # Deshabilitar anexos_adicionales si no está en la lista
            if 'anexos_adicionales' not in campos_editables:
                for field_name in anexos_form.fields:
                    anexos_form.fields[field_name].disabled = True
                    anexos_form.fields[field_name].widget.attrs['readonly'] = True
                    anexos_form.fields[field_name].widget.attrs['class'] = anexos_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            # Deshabilitar formsets si no están en la lista
            if 'experiencia_laboral' not in campos_editables:
                for exp_form in experiencia_formset:
                    for field_name in exp_form.fields:
                        if field_name != 'DELETE':  # Permitir eliminar
                            exp_form.fields[field_name].disabled = True
                            exp_form.fields[field_name].widget.attrs['readonly'] = True
                            exp_form.fields[field_name].widget.attrs['class'] = exp_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            if 'educacion_basica' not in campos_editables:
                for basica_form in basica_formset:
                    for field_name in basica_form.fields:
                        if field_name != 'DELETE':
                            basica_form.fields[field_name].disabled = True
                            basica_form.fields[field_name].widget.attrs['readonly'] = True
                            basica_form.fields[field_name].widget.attrs['class'] = basica_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            if 'educacion_superior' not in campos_editables:
                for superior_form in superior_formset:
                    for field_name in superior_form.fields:
                        if field_name != 'DELETE':
                            superior_form.fields[field_name].disabled = True
                            superior_form.fields[field_name].widget.attrs['readonly'] = True
                            superior_form.fields[field_name].widget.attrs['class'] = superior_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            if 'formacion_academica' not in campos_editables:
                for academica_form in academica_formset:
                    for field_name in academica_form.fields:
                        if field_name != 'DELETE':
                            academica_form.fields[field_name].disabled = True
                            academica_form.fields[field_name].widget.attrs['readonly'] = True
                            academica_form.fields[field_name].widget.attrs['class'] = academica_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            if 'posgrado' not in campos_editables:
                for posgrado_form in posgrado_formset:
                    for field_name in posgrado_form.fields:
                        if field_name != 'DELETE':
                            posgrado_form.fields[field_name].disabled = True
                            posgrado_form.fields[field_name].widget.attrs['readonly'] = True
                            posgrado_form.fields[field_name].widget.attrs['class'] = posgrado_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

            if 'especializacion' not in campos_editables:
                for especializacion_form in especializacion_formset:
                    for field_name in especializacion_form.fields:
                        if field_name != 'DELETE':
                            especializacion_form.fields[field_name].disabled = True
                            especializacion_form.fields[field_name].widget.attrs['readonly'] = True
                            especializacion_form.fields[field_name].widget.attrs['class'] = especializacion_form.fields[field_name].widget.attrs.get('class', '') + ' bg-light'

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
