from django.shortcuts import render
from django.db.models import Q
from .models import PersonalUrl, ExperienciaTotal, ContratoHistorico, ConsolidadoBaseDatos
from django.contrib.auth.decorators import login_required, user_passes_test

def es_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(es_admin)
def buscar_historico(request):
    query = request.GET.get('q')
    context = {
        'query': query,
        'mostrar_resultados': False
    }

    if query:
        # Intentar buscar por cédula (exacta)
        try:
            cedula_query = int(query.strip())
            
            # 1. Resumen Experiencia Total
            context['experiencia_total'] = ExperienciaTotal.objects.filter(cedula=cedula_query).first()
            
            # 2. URL Carpeta
            context['personal_url'] = PersonalUrl.objects.filter(cedula=cedula_query).first()
            
            # 3. Historial de Contratos
            context['contratos'] = ContratoHistorico.objects.filter(cedula=cedula_query).order_by('fecha_inicio')
            
            # 4. Consolidado
            context['consolidado'] = ConsolidadoBaseDatos.objects.filter(cedula=cedula_query).order_by('fecha_firma')
            
            context['mostrar_resultados'] = True
            
        except ValueError:
            # Si no es un número, mostrar error o buscar por nombre (opcional, por ahora solo cédula por seguridad)
            context['error'] = "Por favor ingrese un número de cédula válido (sin puntos ni comas)."

    return render(request, 'basedatosaquicali/busqueda_historica.html', context)