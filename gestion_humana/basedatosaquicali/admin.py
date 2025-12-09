from django.contrib import admin
from .models import PersonalUrl, ExperienciaTotal, ContratoHistorico, ConsolidadoBaseDatos

@admin.register(PersonalUrl)
class PersonalUrlAdmin(admin.ModelAdmin):
    list_display = ('contratista', 'cedula', 'area', 'enlace_carpeta')
    search_fields = ('contratista', 'cedula', 'area')
    list_filter = ('area',)

@admin.register(ExperienciaTotal)
class ExperienciaTotalAdmin(admin.ModelAdmin):
    list_display = ('nombre_contratista', 'cedula', 'experiencia_neta_texto', 'experiencia_neta_dias')
    search_fields = ('nombre_contratista', 'cedula')

@admin.register(ContratoHistorico)
class ContratoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'nombre_contratista', 'cedula', 'fecha_inicio', 'fecha_fin', 'dias_reales_contribuidos')
    search_fields = ('contrato', 'nombre_contratista', 'cedula')
    list_filter = ('traslape',)

@admin.register(ConsolidadoBaseDatos)
class ConsolidadoBaseDatosAdmin(admin.ModelAdmin):
    list_display = ('numero_contrato_otrosi', 'nombre_contratista', 'cedula', 'fecha_firma', 'fecha_final', 'estado')
    search_fields = ('numero_contrato_otrosi', 'nombre_contratista', 'cedula')
    list_filter = ('estado', 'area', 'tipo_documento')