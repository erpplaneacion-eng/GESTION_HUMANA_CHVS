"""
Vista pública de registro de candidatos.
Formulario multi-sección accesible sin autenticación.
Refactorizado desde views.py para mejor organización.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from ..models import (
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales,
)
from ..forms import (
    InformacionBasicaPublicForm,
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
