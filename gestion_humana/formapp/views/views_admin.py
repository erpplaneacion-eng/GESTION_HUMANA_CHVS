"""
Vistas administrativas para gestión de candidatos.
Panel de administración con lista, detalle, edición y eliminación.
Refactorizado desde views.py para mejor organización.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from datetime import datetime as dt

from ..models import (
    InformacionBasica,
    ExperienciaLaboral,
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales,
)
from ..forms import (
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
from ..services import calcular_experiencia_total, enviar_correo_solicitud_correccion

import logging
import traceback

logger = logging.getLogger(__name__)


class ApplicantListView(LoginRequiredMixin, ListView):
    model = InformacionBasica
    template_name = 'formapp/applicant_list.html'
    context_object_name = 'applicants'
    ordering = ['-id']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Búsqueda por cédula o nombre
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(cedula__icontains=search_query) |
                Q(nombre_completo__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estadísticas correctamente calculadas
        context['total_personal'] = InformacionBasica.objects.count()
        context['con_experiencia'] = InformacionBasica.objects.filter(
            experiencias_laborales__isnull=False
        ).distinct().count()
        context['profesionales'] = InformacionBasica.objects.filter(
            formacion_academica__isnull=False
        ).distinct().count()
        context['con_posgrado'] = InformacionBasica.objects.filter(
            posgrados__isnull=False
        ).distinct().count()
        # Mantener el valor de búsqueda en el contexto
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ApplicantDetailView(LoginRequiredMixin, DetailView):
    model = InformacionBasica
    template_name = 'formapp/applicant_detail.html'
    context_object_name = 'applicant'

@login_required
def applicant_edit_view(request, pk):
    """Vista para editar un registro existente"""
    applicant = get_object_or_404(InformacionBasica, pk=pk)

    # Obtener o crear instancias relacionadas
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

        # Validar todos los formsets antes de guardar
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

        if form_valid and documentos_valid and antecedentes_valid and anexos_valid and experiencia_valid and basica_valid and superior_valid and academica_valid and posgrado_valid and especializacion_valid:
            try:
                with transaction.atomic():
                    informacion_basica = form.save()

                    # Guardar documentos de identidad
                    documentos = documentos_form.save(commit=False)
                    documentos.informacion_basica = informacion_basica
                    documentos.save()

                    # Guardar antecedentes
                    antecedentes_obj = antecedentes_form.save(commit=False)
                    antecedentes_obj.informacion_basica = informacion_basica
                    antecedentes_obj.save()

                    # Guardar anexos adicionales
                    anexos = anexos_form.save(commit=False)
                    anexos.informacion_basica = informacion_basica
                    anexos.save()

                    # Guardar todos los formsets
                    # Guardar experiencia laboral - usar save() que maneja automáticamente todo
                    experiencia_formset.save()

                    # Recalcular meses y días SOLO para experiencias que cambiaron sus fechas
                    from datetime import datetime as dt
                    experiencias_modificadas = []

                    for form_exp in experiencia_formset:
                        # Solo procesar si el formulario tiene una instancia guardada (no eliminada)
                        if form_exp.instance.pk and not form_exp.cleaned_data.get('DELETE', False):
                            # Verificar si cambió alguna de las fechas
                            if form_exp.has_changed() and ('fecha_inicial' in form_exp.changed_data or 'fecha_terminacion' in form_exp.changed_data):
                                experiencia = form_exp.instance
                                if experiencia.fecha_inicial and experiencia.fecha_terminacion:
                                    fecha_inicio = dt.combine(experiencia.fecha_inicial, dt.min.time())
                                    fecha_fin = dt.combine(experiencia.fecha_terminacion, dt.min.time())

                                    # Calcular diferencia
                                    delta = fecha_fin - fecha_inicio
                                    total_dias = delta.days

                                    # Calcular meses
                                    anos = fecha_fin.year - fecha_inicio.year
                                    meses = fecha_fin.month - fecha_inicio.month
                                    dias = fecha_fin.day - fecha_inicio.day

                                    if dias < 0:
                                        meses -= 1
                                        # Obtener días del mes anterior
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

                    # Guardar solo las experiencias que se modificaron (bulk update)
                    if experiencias_modificadas:
                        from formapp.models import ExperienciaLaboral
                        ExperienciaLaboral.objects.bulk_update(
                            experiencias_modificadas,
                            ['meses_experiencia', 'dias_experiencia']
                        )
                    
                    # Calcular experiencia total automáticamente
                    calcular_experiencia_total(informacion_basica)

                    # Guardar los demás formsets
                    basica_formset.save()
                    superior_formset.save()
                    academica_formset.save()
                    posgrado_formset.save()
                    especializacion_formset.save()

                    messages.success(request, f'Registro de {informacion_basica.nombre_completo} actualizado con éxito!')
                    return redirect('formapp:applicant_detail', pk=informacion_basica.pk)
            except Exception as e:
                import traceback
                messages.error(request, f'Error al actualizar el registro: {str(e)}')
                logger.error(f'Error guardando experiencia laboral: {str(e)}\n{traceback.format_exc()}')
        else:
            # Si hay errores, mostrar mensajes específicos
            if not form_valid:
                messages.error(request, 'Por favor corrija los errores en el formulario principal.')
                # Mostrar errores específicos del formulario principal
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
            
            if not experiencia_valid:
                error_msg = experiencia_formset.non_form_errors()
                if error_msg:
                    messages.error(request, f'Error en Experiencia Laboral: {error_msg}')
                for idx, form_exp in enumerate(experiencia_formset, 1):
                    if form_exp.errors:
                        messages.error(request, f'Experiencia {idx}: {form_exp.errors}')
            if not basica_valid:
                messages.error(request, 'Por favor corrija los errores en Educación Básica.')
            if not superior_valid:
                messages.error(request, 'Por favor corrija los errores en Educación Superior.')
            if not academica_valid:
                messages.error(request, 'Por favor corrija los errores en Formación Académica.')
            if not posgrado_valid:
                messages.error(request, 'Por favor corrija los errores en Posgrados.')
            if not especializacion_valid:
                messages.error(request, 'Por favor corrija los errores en Especializaciones.')
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
    }
    return render(request, 'formapp/applicant_edit.html', context)

@login_required
def applicant_delete_view(request, pk):
    """Vista para eliminar un registro"""
    applicant = get_object_or_404(InformacionBasica, pk=pk)

    if request.method == 'POST':
        nombre = applicant.nombre_completo
        try:
            applicant.delete()
            messages.success(request, f'Registro de {nombre} eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el registro: {str(e)}')
        return redirect('formapp:applicant_list')

    # Si no es POST, redirigir a la lista
    return redirect('formapp:applicant_list')

@login_required
def solicitar_correccion_view(request, pk):
    """
    Procesa la solicitud de corrección del administrador.
    Genera token y envía correo.
    """
    if request.method != 'POST':
        return redirect('formapp:applicant_detail', pk=pk)

    applicant = get_object_or_404(InformacionBasica, pk=pk)
    mensaje = request.POST.get('mensaje_observacion')

    if not mensaje:
        messages.error(request, 'Debes ingresar una observación para el candidato.')
        return redirect('formapp:applicant_detail', pk=pk)

    # Enviar correo y actualizar estado
    if enviar_correo_solicitud_correccion(applicant, mensaje, request):
        messages.success(request, f'Se ha enviado la solicitud de corrección a {applicant.nombre_completo}.')
    else:
        messages.error(request, 'Hubo un error al enviar el correo. Por favor verifica la configuración.')

    return redirect('formapp:applicant_detail', pk=pk)
