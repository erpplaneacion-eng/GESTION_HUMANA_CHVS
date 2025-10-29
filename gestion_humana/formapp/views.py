from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from .models import InformacionBasica
from .forms import (
    InformacionBasicaForm,
    ExperienciaLaboralFormSet,
    InformacionAcademicaFormSet,
    PosgradoFormSet,
)

def public_form_view(request):
    if request.method == 'POST':
        form = InformacionBasicaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    informacion_basica = form.save()
                    
                    experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if experiencia_formset.is_valid():
                        experiencia_formset.save()

                    academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if academica_formset.is_valid():
                        academica_formset.save()

                    posgrado_formset = PosgradoFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if posgrado_formset.is_valid():
                        posgrado_formset.save()

                    messages.success(request, '¡Formulario enviado con éxito!')
                    return redirect('formapp:public_form') # Redirect to a success page or the same form
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformacionBasicaForm()
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

class ApplicantDetailView(LoginRequiredMixin, DetailView):
    model = InformacionBasica
    template_name = 'formapp/applicant_detail.html'
    context_object_name = 'applicant'