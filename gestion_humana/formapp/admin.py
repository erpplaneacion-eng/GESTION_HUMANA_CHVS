from django.contrib import admin
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado, Especializacion, CalculoExperiencia, DocumentosIdentidad, Antecedentes, AnexosAdicionales

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
        'numero_tarjeta_resolucion', 'fecha_expedicion',
        'fotocopia_titulo', 'fotocopia_tarjeta_profesional',
        'certificado_vigencia_tarjeta', 'fecha_vigencia_tarjeta'
    )

class PosgradoInline(admin.TabularInline):
    model = Posgrado
    extra = 1
    fields = ('nombre_posgrado', 'universidad', 'fecha_terminacion')

class EspecializacionInline(admin.TabularInline):
    model = Especializacion
    extra = 1
    fields = ('nombre_especializacion', 'universidad', 'fecha_terminacion')

class CalculoExperienciaInline(admin.StackedInline):
    model = CalculoExperiencia
    can_delete = False
    readonly_fields = (
        'total_meses_experiencia', 'total_dias_experiencia',
        'total_experiencia_anos', 'anos_y_meses_experiencia'
    )
    fields = readonly_fields

class DocumentosIdentidadInline(admin.StackedInline):
    model = DocumentosIdentidad
    can_delete = False
    extra = 0
    fieldsets = (
        ('Documento de Identidad', {
            'fields': ('fotocopia_cedula', 'hoja_de_vida')
        }),
        ('Situación Militar (Opcional)', {
            'fields': (
                'libreta_militar', 'numero_libreta_militar',
                'distrito_militar', 'clase_libreta'
            ),
            'classes': ('collapse',)
        }),
    )

class AntecedentesInline(admin.StackedInline):
    model = Antecedentes
    can_delete = False
    extra = 0
    fieldsets = (
        ('Antecedentes Disciplinarios - Procuraduría', {
            'fields': ('certificado_procuraduria', 'fecha_procuraduria')
        }),
        ('Antecedentes Fiscales - Contraloría', {
            'fields': ('certificado_contraloria', 'fecha_contraloria')
        }),
        ('Antecedentes Judiciales - Policía', {
            'fields': ('certificado_policia', 'fecha_policia')
        }),
        ('Medidas Correctivas - RNMC', {
            'fields': ('certificado_medidas_correctivas', 'fecha_medidas_correctivas')
        }),
        ('Inhabilidades por Delitos Sexuales', {
            'fields': ('certificado_delitos_sexuales', 'fecha_delitos_sexuales')
        }),
    )

class AnexosAdicionalesInline(admin.StackedInline):
    model = AnexosAdicionales
    can_delete = False
    extra = 0
    fieldsets = (
        ('ANEXO 03', {
            'fields': ('anexo_03_datos_personales',)
        }),
        ('Carta de Intención', {
            'fields': ('carta_intencion',)
        }),
        ('Otros Documentos', {
            'fields': ('otros_documentos', 'descripcion_otros'),
            'classes': ('collapse',)
        }),
    )

@admin.register(InformacionBasica)
class InformacionBasicaAdmin(admin.ModelAdmin):
    list_display = (
        'cedula', 'nombre_completo', 'genero', 'profesion',
        'area_del_conocimiento', 'telefono', 'correo'
    )
    list_filter = ('genero', 'area_del_conocimiento', 'contrato')
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
                'perfil', 'area_del_conocimiento', 'profesion',
                'contrato', 'observacion'
            ),
            'description': 'Estos campos deben ser completados por el personal administrativo'
        }),
    )

    inlines = [
        DocumentosIdentidadInline,
        AntecedentesInline,
        AnexosAdicionalesInline,
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
        'fecha_grado', 'tarjeta_profesional', 'tiene_titulo', 'tiene_tarjeta'
    )
    list_filter = ('tarjeta_profesional',)
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'profesion')

    fieldsets = (
        ('Información del Aspirante', {
            'fields': ('informacion_basica',)
        }),
        ('Formación Académica', {
            'fields': (
                'profesion', 'universidad', 'fecha_grado'
            )
        }),
        ('Tarjeta Profesional', {
            'fields': (
                'tarjeta_profesional', 'numero_tarjeta_resolucion',
                'fecha_expedicion'
            )
        }),
        ('Documentos Académicos', {
            'fields': (
                'fotocopia_titulo', 'fotocopia_tarjeta_profesional',
                'certificado_vigencia_tarjeta', 'fecha_vigencia_tarjeta'
            )
        }),
    )

    def tiene_titulo(self, obj):
        return bool(obj.fotocopia_titulo)
    tiene_titulo.boolean = True
    tiene_titulo.short_description = 'Título'

    def tiene_tarjeta(self, obj):
        return bool(obj.fotocopia_tarjeta_profesional)
    tiene_tarjeta.boolean = True
    tiene_tarjeta.short_description = 'Tarjeta Prof.'

@admin.register(Posgrado)
class PosgradoAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'nombre_posgrado', 'universidad',
        'fecha_terminacion'
    )
    search_fields = ('informacion_basica__nombre_completo', 'informacion_basica__cedula', 'nombre_posgrado')

@admin.register(Especializacion)
class EspecializacionAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'nombre_especializacion', 'universidad',
        'fecha_terminacion'
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

@admin.register(DocumentosIdentidad)
class DocumentosIdentidadAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica',
        'tiene_libreta_militar', 'created_at'
    )
    list_filter = ('clase_libreta',)
    search_fields = (
        'informacion_basica__nombre_completo',
        'informacion_basica__cedula',
        'numero_libreta_militar'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información del Aspirante', {
            'fields': ('informacion_basica',)
        }),
        ('Documento de Identidad', {
            'fields': ('fotocopia_cedula', 'hoja_de_vida')
        }),
        ('Situación Militar (Opcional)', {
            'fields': (
                'libreta_militar', 'numero_libreta_militar',
                'distrito_militar', 'clase_libreta'
            )
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tiene_libreta_militar(self, obj):
        return bool(obj.libreta_militar)
    tiene_libreta_militar.boolean = True
    tiene_libreta_militar.short_description = 'Libreta Militar'

@admin.register(Antecedentes)
class AntecedentesAdmin(admin.ModelAdmin):
    list_display = (
        'informacion_basica', 'fecha_procuraduria', 'fecha_contraloria',
        'fecha_policia', 'tiene_todos_certificados', 'created_at'
    )
    list_filter = ('fecha_procuraduria', 'fecha_contraloria', 'fecha_policia')
    search_fields = (
        'informacion_basica__nombre_completo',
        'informacion_basica__cedula'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información del Aspirante', {
            'fields': ('informacion_basica',)
        }),
        ('Antecedentes Disciplinarios - Procuraduría', {
            'fields': ('certificado_procuraduria', 'fecha_procuraduria')
        }),
        ('Antecedentes Fiscales - Contraloría', {
            'fields': ('certificado_contraloria', 'fecha_contraloria')
        }),
        ('Antecedentes Judiciales - Policía', {
            'fields': ('certificado_policia', 'fecha_policia')
        }),
        ('Medidas Correctivas - RNMC', {
            'fields': ('certificado_medidas_correctivas', 'fecha_medidas_correctivas')
        }),
        ('Inhabilidades por Delitos Sexuales', {
            'fields': ('certificado_delitos_sexuales', 'fecha_delitos_sexuales')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tiene_todos_certificados(self, obj):
        return all([
            obj.certificado_procuraduria,
            obj.certificado_contraloria,
            obj.certificado_policia,
            obj.certificado_medidas_correctivas,
            obj.certificado_delitos_sexuales
        ])
    tiene_todos_certificados.boolean = True
    tiene_todos_certificados.short_description = 'Completo'
