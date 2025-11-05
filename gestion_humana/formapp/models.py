from django.db import models
from django.core.validators import MinValueValidator
from .validators import validate_file_size, validate_file_extension

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
    complemento_direccion = models.CharField(max_length=100, verbose_name='Complemento (Apto, Interior, etc.)', blank=True, null=True)
    barrio = models.CharField(max_length=100, verbose_name='Barrio', blank=True, null=True)

    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    correo = models.EmailField(verbose_name='Correo Electrónico')    
    
    #datos q se deben de cumplir de acuerdo al perfil, y se deben de diligenciar por el personal administrativo
    perfil = models.CharField(max_length=200, verbose_name='Perfil Profesional', blank=True, null=True)
    area_conocimiento = models.CharField(max_length=200, verbose_name='Área de Conocimiento', blank=True, null=True)
    area_del_conocimiento = models.CharField(max_length=200, verbose_name='Área del Conocimiento', blank=True, null=True)
    tipo_perfil = models.CharField(max_length=200, verbose_name='Tipo de Perfil', blank=True, null=True)
    profesion = models.CharField(max_length=200, verbose_name='Profesión', blank=True, null=True)
    experiencia = models.CharField(max_length=200, verbose_name='Tipo de Experiencia', blank=True, null=True)
    tiempo_experiencia = models.CharField(max_length=200, verbose_name='Tiempo de Experiencia', blank=True, null=True)
    cantidad = models.IntegerField(verbose_name='Cantidad', blank=True, null=True)
    organizacion = models.TextField(verbose_name='Organización', blank=True, null=True)
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
        validators=[validate_file_size, validate_file_extension],
        help_text='Formatos permitidos: PDF, JPG, PNG. Tamaño máximo: 10 MB',
        blank=True  # Permitir que el campo esté vacío en edición
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
        max_length=100,
        verbose_name='Tarjeta o Resolución Profesional',
        choices=TIPO_TARJETA_CHOICES,
        default='No Aplica'
    )
    profesion = models.CharField(max_length=200, verbose_name='Profesión')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    numero_tarjeta_resolucion = models.CharField(max_length=100, verbose_name='N° Tarjeta o Resolución', blank=True, null=True)
    fecha_grado = models.DateField(verbose_name='Fecha de Grado')
    meses_experiencia_profesion = models.IntegerField(verbose_name='Meses de Experiencia por Profesión', default=0)

    def __str__(self):
        return f'{self.profesion} de {self.informacion_basica.cedula}'

from django.core.validators import MinValueValidator
class Posgrado(models.Model):
    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='posgrados')
    nombre_posgrado = models.CharField(max_length=200, verbose_name='Nombre del Posgrado')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    fecha_terminacion = models.DateField(verbose_name='Fecha de Terminación')
    meses_de_experiencia = models.IntegerField(verbose_name='Meses de Experiencia', validators=[MinValueValidator(0)])
    

    def __str__(self):
        return f'{self.nombre_posgrado} de {self.informacion_basica.cedula}'

class Especializacion(models.Model):
    informacion_basica = models.ForeignKey(InformacionBasica, on_delete=models.CASCADE, related_name='especializaciones')
    nombre_especializacion = models.CharField(max_length=200, verbose_name='Nombre de la Especialización')
    universidad = models.CharField(max_length=200, verbose_name='Universidad')
    fecha_terminacion = models.DateField(verbose_name='Fecha de Terminación')
    meses_de_experiencia = models.IntegerField(verbose_name='Meses de Experiencia', validators=[MinValueValidator(0)])
    

    def __str__(self):
        return f'{self.nombre_especializacion} de {self.informacion_basica.cedula}'

class CalculoExperiencia(models.Model):
    informacion_basica = models.OneToOneField(InformacionBasica, on_delete=models.CASCADE, related_name='calculo_experiencia')
    total_meses_experiencia = models.IntegerField(verbose_name='Total Meses Experiencia Certificada')
    total_dias_experiencia = models.IntegerField(verbose_name='Total Días Experiencia Certificada')
    total_experiencia_anos = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Total Experiencia en Años')
    anos_y_meses_experiencia = models.CharField(max_length=100, verbose_name='Años y Meses de Experiencia')

    def __str__(self):
        return f'Cálculo de experiencia para {self.informacion_basica.cedula}'