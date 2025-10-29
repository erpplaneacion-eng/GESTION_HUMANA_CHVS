from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.db.models import Q, Count
from .models import InformacionBasica, CalculoExperiencia
from .forms import (
    InformacionBasicaPublicForm,
    ExperienciaLaboralFormSet,
    InformacionAcademicaFormSet,
    PosgradoFormSet,
)

def calcular_experiencia_total(informacion_basica):
    """Calcula automáticamente la experiencia total de una persona"""
    experiencias = informacion_basica.experiencias_laborales.all()

    total_meses = sum(exp.meses_experiencia for exp in experiencias)
    total_dias = sum(exp.dias_experiencia for exp in experiencias)
    total_dias_residual = sum(exp.dias_residual_experiencia for exp in experiencias)

    # Convertir a años (considerando 12 meses por año)
    total_anos = round(total_meses / 12, 2)

    # Calcular años y meses para formato legible
    anos = total_meses // 12
    meses_restantes = total_meses % 12
    anos_y_meses = f"{anos} años y {meses_restantes} meses"

    # Crear o actualizar el registro de cálculo
    calculo, created = CalculoExperiencia.objects.update_or_create(
        informacion_basica=informacion_basica,
        defaults={
            'total_meses_experiencia': total_meses,
            'total_dias_experiencia': total_dias,
            'total_dias_residual_experiencia': total_dias_residual,
            'total_experiencia_anos': total_anos,
            'anos_y_meses_experiencia': anos_y_meses,
        }
    )
    return calculo

def public_form_view(request):
    if request.method == 'POST':
        form = InformacionBasicaPublicForm(request.POST, request.FILES)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES)
        academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES)
        posgrado_formset = PosgradoFormSet(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    informacion_basica = form.save()

                    experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if experiencia_formset.is_valid():
                        experiencia_formset.save()
                        # Calcular experiencia automáticamente
                        calcular_experiencia_total(informacion_basica)

                    academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if academica_formset.is_valid():
                        academica_formset.save()

                    posgrado_formset = PosgradoFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if posgrado_formset.is_valid():
                        posgrado_formset.save()

                    messages.success(request, '¡Formulario enviado con éxito!')
                    return redirect('formapp:public_form')
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformacionBasicaPublicForm()
        experiencia_formset = ExperienciaLaboralFormSet()
        academica_formset = InformacionAcademicaFormSet()
        posgrado_formset = PosgradoFormSet()

    context = {
        'form': form,
        'experiencia_formset': experiencia_formset,
        'academica_formset': academica_formset,
        'posgrado_formset': posgrado_formset,
    }
    return render(request, 'formapp/public_form.html', context)

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