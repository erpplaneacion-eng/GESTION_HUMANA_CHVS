from django.db import models
from django.core.validators import MinValueValidator
from .validators import validate_file_size, validate_file_extension, validate_file_mime

class InformacionBasica(models.Model):
    # campos datos personales
    
    # campos q son de selecccion multipple, respuestas cerradas    
    GENERO_CHOICES = [
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
    ]
    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre Completo', blank=True, null=True)
    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Cédula',
        error_messages={
            'unique': 'Ya existe un registro con esta cédula. Por favor, verifica el número de cédula.'
        }
    )
    genero = models.CharField(max_length=50, verbose_name='Género', choices=GENERO_CHOICES)
     # Campos de dirección subdivididos
    tipo_via = models.CharField(max_length=50, verbose_name='Tipo de Vía (Calle/Avenida/Carrera)', default='Calle')
    numero_via = models.CharField(max_length=20, verbose_name='Número de Vía', default='')
    numero_casa = models.CharField(max_length=20, verbose_name='Número de Casa/Edificio', default='')
    complemento_direccion = models.CharField(max_length=200, verbose_name='Complemento (Apto, Interior, etc.)', blank=True, null=True)
    barrio = models.CharField(max_length=200, verbose_name='Barrio', blank=True, null=True)

    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    correo = models.EmailField(verbose_name='Correo Electrónico')    
    
    #datos q se deben de cumplir de acuerdo al perfil, y se deben de diligenciar por el personal administrativo
    perfil = models.CharField(max_length=200, verbose_name='Perfil Profesional', blank=True, null=True)
    area_del_conocimiento = models.CharField(max_length=200, verbose_name='Área del Conocimiento', blank=True, null=True)
    profesion = models.CharField(max_length=200, verbose_name='Profesión', blank=True, null=True)
    contrato = models.CharField(max_length=200, verbose_name='Contrato', blank=True, null=True)
    observacion = models.TextField(verbose_name='Observaciones', blank=True, null=True)

    def __str__(self):
        return self.nombre_completo
    
    
    #campos de experiencia laboral
class ExperienciaLaboral(models.Model):
    fecha_inicial = models.DateField(verbose_name='Fecha Inicial')
    fecha_terminacion = models.DateField(verbose_name='Fecha de Terminación')
    
    #campos calculados automaticamente.(estos campos desde el frontend no son editables)
    meses_experiencia = models.IntegerField(verbose_name='Meses de Experiencia')  # Meses completos entre las fechas
    dias_experiencia = models.IntegerField(verbose_name='Días de Experiencia')  # Total de días calendario
    
    cargo = models.CharField(max_length=200, verbose_name='Cargo')
    cargo_anexo_11 = models.CharField(max_length=200, verbose_name='Cargo Anexo 11', blank=True, default='Profesional')
    objeto_contractual = models.TextField(verbose_name='Objeto Contractual')
    funciones = models.TextField(verbose_name='Funciones')     
    
    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='experiencias_laborales')
    certificado_laboral = models.FileField(
        upload_to='certificados_laborales/',
        verbose_name='Certificado Laboral o Contractual',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Formatos permitidos: PDF, JPG, PNG. Tamaño máximo: 10 MB',
        max_length=200,
        blank=False,  # Campo requerido para nuevos registros
        null=False    # No permitir valores NULL en base de datos
    )     
    

    def __str__(self):
        return f'{self.cargo} en {self.informacion_basica.cedula}'

class InformacionAcademica(models.Model):
    TIPO_TARJETA_CHOICES = [
        ('Tarjeta Profesional', 'Tarjeta Profesional'),
        ('Resolución', 'Resolución'),
        ('No Aplica', 'No Aplica'),
    ]

    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='formacion_academica')
    fecha_expedicion = models.DateField(verbose_name='Fecha de Expedición', blank=True, null=True)
    tarjeta_profesional = models.CharField(
        max_length=200,
        verbose_name='Tarjeta o Resolución Profesional',
        choices=TIPO_TARJETA_CHOICES,
        default='No Aplica'
    )
    profesion = models.CharField(max_length=200, verbose_name='Profesión')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    numero_tarjeta_resolucion = models.CharField(max_length=200, verbose_name='N° Tarjeta o Resolución', blank=True, null=True)
    fecha_grado = models.DateField(verbose_name='Fecha de Grado')

    # FASE 2: Documentos académicos
    fotocopia_titulo = models.FileField(
        upload_to='titulos_academicos/',
        verbose_name='Fotocopia del Título/Diploma',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Acta de grado o diploma. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )
    fotocopia_tarjeta_profesional = models.FileField(
        upload_to='tarjetas_profesionales/',
        verbose_name='Fotocopia Tarjeta Profesional',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Solo si aplica. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )
    certificado_vigencia_tarjeta = models.FileField(
        upload_to='certificados_vigencia/',
        verbose_name='Certificado de Vigencia',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Certificado de vigencia de tarjeta profesional. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )
    fecha_vigencia_tarjeta = models.DateField(
        verbose_name='Fecha de Vigencia del Certificado',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.profesion} de {self.informacion_basica.cedula}'

from django.core.validators import MinValueValidator
class Posgrado(models.Model):
    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='posgrados')
    nombre_posgrado = models.CharField(max_length=200, verbose_name='Nombre del Posgrado')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    fecha_terminacion = models.DateField(verbose_name='Fecha de Terminación')


    def __str__(self):
        return f'{self.nombre_posgrado} de {self.informacion_basica.cedula}'

class Especializacion(models.Model):
    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='especializaciones')
    nombre_especializacion = models.CharField(max_length=200, verbose_name='Nombre de la Especialización')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    fecha_terminacion = models.DateField(verbose_name='Fecha de Terminación')


    def __str__(self):
        return f'{self.nombre_especializacion} de {self.informacion_basica.cedula}'

class CalculoExperiencia(models.Model):
    informacion_basica = models.OneToOneField(InformacionBasica, on_delete=models.CASCADE, related_name='calculo_experiencia')
    total_meses_experiencia = models.IntegerField(verbose_name='Total Meses Experiencia Certificada')
    total_dias_experiencia = models.IntegerField(verbose_name='Total Días Experiencia Certificada')
    total_experiencia_anos = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Total Experiencia en Años')
    anos_y_meses_experiencia = models.CharField(max_length=200, verbose_name='Años y Meses de Experiencia')

    def __str__(self):
        return f'Cálculo de experiencia para {self.informacion_basica.cedula}'


# FASE 1: Documentos de Identidad y Autorización
class DocumentosIdentidad(models.Model):
    informacion_basica = models.OneToOneField(
        InformacionBasica,
        on_delete=models.CASCADE,
        related_name='documentos_identidad'
    )

    # Fotocopia cédula de ciudadanía
    fotocopia_cedula = models.FileField(
        upload_to='documentos_identidad/cedulas/',
        verbose_name='Fotocopia Cédula de Ciudadanía',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Formatos permitidos: PDF, JPG, PNG. Tamaño máximo: 10 MB',
        max_length=200
    )

    # Hoja de vida
    hoja_de_vida = models.FileField(
        upload_to='documentos_identidad/hojas_de_vida/',
        verbose_name='Hoja de Vida',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Formatos permitidos: PDF, JPG, PNG. Tamaño máximo: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )

    # Libreta militar (opcional)
    libreta_militar = models.FileField(
        upload_to='documentos_identidad/libretas_militares/',
        verbose_name='Libreta Militar',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Opcional. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )
    numero_libreta_militar = models.CharField(
        max_length=50,
        verbose_name='Número de Libreta Militar',
        blank=True,
        null=True
    )
    distrito_militar = models.CharField(
        max_length=200,
        verbose_name='Distrito Militar',
        blank=True,
        null=True
    )
    clase_libreta = models.CharField(
        max_length=50,
        verbose_name='Clase de Libreta',
        choices=[
            ('Primera', 'Primera Clase'),
            ('Segunda', 'Segunda Clase'),
        ],
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Documentos de Identidad'
        verbose_name_plural = 'Documentos de Identidad'

    def __str__(self):
        return f'Documentos de {self.informacion_basica.nombre_completo}'


# FASE 3: Antecedentes y Verificaciones
class Antecedentes(models.Model):
    informacion_basica = models.OneToOneField(
        InformacionBasica,
        on_delete=models.CASCADE,
        related_name='antecedentes'
    )

    # Antecedentes disciplinarios (Procuraduría General de la Nación)
    certificado_procuraduria = models.FileField(
        upload_to='antecedentes/procuraduria/',
        verbose_name='Certificado de Antecedentes Disciplinarios',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Procuraduría General de la Nación. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200
    )
    fecha_procuraduria = models.DateField(
        verbose_name='Fecha de Expedición Procuraduría'
    )

    # Antecedentes fiscales (Contraloría General de la República)
    certificado_contraloria = models.FileField(
        upload_to='antecedentes/contraloria/',
        verbose_name='Certificado de Antecedentes Fiscales',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Contraloría General de la República. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200
    )
    fecha_contraloria = models.DateField(
        verbose_name='Fecha de Expedición Contraloría'
    )

    # Antecedentes judiciales (Policía Nacional)
    certificado_policia = models.FileField(
        upload_to='antecedentes/policia/',
        verbose_name='Certificado de Antecedentes Judiciales',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Policía Nacional de Colombia. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200
    )
    fecha_policia = models.DateField(
        verbose_name='Fecha de Expedición Policía'
    )

    # Registro Nacional de Medidas Correctivas (RNMC)
    certificado_medidas_correctivas = models.FileField(
        upload_to='antecedentes/medidas_correctivas/',
        verbose_name='Registro de Medidas Correctivas',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='RNMC - Policía Nacional. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200
    )
    fecha_medidas_correctivas = models.DateField(
        verbose_name='Fecha de Expedición RNMC'
    )

    # Consulta de inhabilidades por delitos sexuales contra menores
    certificado_delitos_sexuales = models.FileField(
        upload_to='antecedentes/delitos_sexuales/',
        verbose_name='Consulta Inhabilidades Delitos Sexuales',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Ley 1918 de 2018. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200
    )
    fecha_delitos_sexuales = models.DateField(
        verbose_name='Fecha de Consulta'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Antecedentes'
        verbose_name_plural = 'Antecedentes'

    def __str__(self):
        return f'Antecedentes de {self.informacion_basica.nombre_completo}'


# FASE 4: Anexos Adicionales
class AnexosAdicionales(models.Model):
    informacion_basica = models.OneToOneField(
        InformacionBasica,
        on_delete=models.CASCADE,
        related_name='anexos_adicionales'
    )

    # ANEXO 03 - Datos Personales
    anexo_03_datos_personales = models.FileField(
        upload_to='anexos/anexo_03/',
        verbose_name='ANEXO 03 - Datos Personales',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Formato de datos personales vigente. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )

    # Carta de intención o contrato
    carta_intencion = models.FileField(
        upload_to='anexos/cartas_intencion/',
        verbose_name='Carta de Intención o Contrato',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Carta de intención firmada. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )

    # Otros documentos opcionales
    otros_documentos = models.FileField(
        upload_to='anexos/otros/',
        verbose_name='Otros Documentos',
        validators=[validate_file_size, validate_file_extension, validate_file_mime],
        help_text='Documentos adicionales. Formatos: PDF, JPG, PNG. Máx: 10 MB',
        max_length=200,
        blank=True,
        null=True
    )
    descripcion_otros = models.TextField(
        verbose_name='Descripción de Otros Documentos',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Anexos Adicionales'
        verbose_name_plural = 'Anexos Adicionales'

    def __str__(self):
        return f'Anexos de {self.informacion_basica.nombre_completo}'