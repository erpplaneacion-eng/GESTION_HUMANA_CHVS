from django.contrib import admin
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado, Especializacion, CalculoExperiencia

class ExperienciaLaboralInline(admin.TabularInline):
    model = ExperienciaLaboral
    extra = 1
    fields = (
        'fecha_inicial', 'fecha_terminacion', 'cargo', 'cargo_anexo_11',
        'meses_experiencia', 'dias_experiencia',
        'objeto_contractual', 'funciones', 'certificado_laboral'
    )
    readonly_fields = ('meses_experiencia', 'dias_experiencia')

class InformacionAcademicaInline(admin.TabularInline):
    model = InformacionAcademica
    extra = 1
    fields = (
        'profesion', 'universidad', 'fecha_grado', 'tarjeta_profesional',
        'numero_tarjeta_resolucion', 'fecha_expedicion', 'meses_experiencia_profesion'
    )

class PosgradoInline(admin.TabularInline):
    model = Posgrado
    extra = 1
    fields = ('nombre_posgrado', 'universidad', 'fecha_terminacion', 'meses_de_experiencia')

class EspecializacionInline(admin.TabularInline):
    model = Especializacion
    extra = 1
    fields = ('nombre_especializacion', 'universidad', 'fecha_terminacion', 'meses_de_experiencia')

class CalculoExperienciaInline(admin.StackedInline):
    model = CalculoExperiencia
    can_delete = False
    readonly_fields = (
        'total_meses_experiencia', 'total_dias_experiencia',
        'total_experiencia_anos', 'anos_y_meses_experiencia'
    )
    fields = readonly_fields

@admin.register(InformacionBasica)
class InformacionBasicaAdmin(admin.ModelAdmin):
    list_display = (
        'cedula', 'nombre_completo', 'genero', 'profesion',
        'area_conocimiento', 'telefono', 'correo'
    )
    list_filter = ('genero', 'area_conocimiento', 'tipo_perfil')
    search_fields = ('cedula', 'nombre_completo', 'correo', 'profesion')

    fieldsets = (
        ('Información Personal', {
            'fields': (
                'nombre_completo', 'cedula', 'genero',
                ('tipo_via', 'numero_via', 'numero_casa'),
                ('complemento_direccion', 'barrio'),
                'telefono', 'correo'
            )
        }),
        ('Perfil Profesional (Administrativo)', {
            'fields': (
                'perfil', 'area_conocimiento', 'area_del_conocimiento',
                'tipo_perfil', 'profesion', 'experiencia',
                'tiempo_experiencia', 'cantidad', 'organizacion',
                'contrato', 'observacion'
            ),
            'description': 'Estos campos deben ser completados por el personal administrativo'
        }),
    )

    inlines = [
        ExperienciaLaboralInline,
        InformacionAcademicaInline,
        PosgradoInline,
        EspecializacionInline,
        CalculoExperienciaInline
    ]

    def save_model(self, request, obj, form, change):
        """Guarda el modelo y recalcula la experiencia"""
        super().save_model(request, obj, form, change)
        # Importar aquí para evitar importación circular
        from .views import calcular_experiencia_total
        if obj.experiencias_laborales.exists():
            calcular_experiencia_total(obj)

    def save_formset(self, request, form, formset, change):
        """Guarda los formsets y recalcula la experiencia si es necesario"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()

        # Recalcular experiencia después de guardar experiencias laborales
        if formset.model == ExperienciaLaboral:
            from .views import calcular_experiencia_total
            obj = form.instance
            if obj.experiencias_laborales.exists():
                calcular_experiencia_total(obj)

@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'cargo', 'fecha_inicial',
        'fecha_terminacion', 'meses_experiencia'
    )
    list_filter = ('cargo_anexo_11',)
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'cargo')
    readonly_fields = ('meses_experiencia', 'dias_experiencia')

@admin.register(InformacionAcademica)
class InformacionAcademicaAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'profesion', 'universidad',
        'fecha_grado', 'tarjeta_profesional'
    )
    list_filter = ('tarjeta_profesional',)
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'profesion')

@admin.register(Posgrado)
class PosgradoAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'nombre_posgrado', 'universidad',
        'fecha_terminacion', 'meses_de_experiencia'
    )
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'nombre_posgrado')

@admin.register(Especializacion)
class EspecializacionAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'nombre_especializacion', 'universidad',
        'fecha_terminacion', 'meses_de_experiencia'
    )
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'nombre_especializacion')

@admin.register(CalculoExperiencia)
class CalculoExperienciaAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'total_meses_experiencia',
        'total_experiencia_anos', 'anos_y_meses_experiencia'
    )
    readonly_fields = (
        'total_meses_experiencia', 'total_dias_experiencia',
        'total_experiencia_anos', 'anos_y_meses_experiencia'
    )
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula')
