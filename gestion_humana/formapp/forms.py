from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from datetime import date
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado, Especializacion, DocumentosIdentidad, Antecedentes, AnexosAdicionales

# Formulario público - solo campos que el usuario puede llenar
class InformacionBasicaPublicForm(forms.ModelForm):
    class Meta:
        model = InformacionBasica
        # Excluir nombre_completo porque se genera automáticamente
        fields = [
            'primer_apellido', 'segundo_apellido', 'primer_nombre', 'segundo_nombre',
            'cedula', 'genero',
            'tipo_via', 'numero_via', 'numero_casa', 'complemento_direccion', 'barrio',
            'telefono', 'correo', 'acepta_politica'
        ]
        widgets = {
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido'}),
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Nombre'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Nombre (Opcional)'}),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'minlength': '5',
                'maxlength': '10',
                'pattern': '[0-9]{5,10}',
                'title': 'La cédula debe tener entre 5 y 10 dígitos'
            }),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'tipo_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle, Avenida, Carrera'}),
            'numero_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 45'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 23-15'}),
            'complemento_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Apto 301'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'minlength': '10',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'El teléfono debe tener exactamente 10 dígitos'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'acepta_politica': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': 'required'
            }),
        }
        error_messages = {
            'primer_apellido': {'required': 'El campo Primer Apellido es obligatorio.'},
            'segundo_apellido': {'required': 'El campo Segundo Apellido es obligatorio.'},
            'primer_nombre': {'required': 'El campo Primer Nombre es obligatorio.'},
            'cedula': {'required': 'El campo Cédula es obligatorio.'},
            'genero': {'required': 'El campo Género es obligatorio.'},
            'tipo_via': {'required': 'El campo Tipo de Vía es obligatorio.'},
            'numero_via': {'required': 'El campo Número de Vía es obligatorio.'},
            'numero_casa': {'required': 'El campo Número de Casa/Edificio es obligatorio.'},
            'telefono': {'required': 'El campo Teléfono es obligatorio.'},
            'correo': {'required': 'El campo Correo Electrónico es obligatorio.'},
            'acepta_politica': {'required': 'Debe aceptar la política de tratamiento de datos para continuar.'},
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit():
            raise forms.ValidationError('La cédula debe contener solo números')
        if len(cedula) < 5 or len(cedula) > 10:
            raise forms.ValidationError('La cédula debe tener entre 5 y 10 dígitos')

        # Validar que la cédula no esté duplicada (solo al crear, no al editar)
        if not self.instance.pk:  # Solo validar si es un nuevo registro
            if InformacionBasica.objects.filter(cedula=cedula).exists():
                raise forms.ValidationError(f'Ya existe un registro con la cédula {cedula}. Por favor, verifica el número de cédula.')

        return cedula

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono debe contener solo números')
        if len(telefono) != 10:
            raise forms.ValidationError('El teléfono debe tener exactamente 10 dígitos')
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if '@' not in correo:
            raise forms.ValidationError('El correo electrónico debe contener @')
        return correo

# Formulario completo para el admin - incluye todos los campos
class InformacionBasicaForm(forms.ModelForm):
    class Meta:
        model = InformacionBasica
        fields = '__all__'
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil': forms.Select(attrs={'class': 'form-control', 'id': 'id_perfil'}),
            'perfil_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique el perfil', 'style': 'text-transform: uppercase;'}),
            'area_del_conocimiento': forms.Select(attrs={'class': 'form-control', 'id': 'id_area_del_conocimiento'}),
            'area_del_conocimiento_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique el área', 'style': 'text-transform: uppercase;'}),
            'profesion': forms.Select(attrs={'class': 'form-control', 'id': 'id_profesion'}),
            'profesion_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique la profesión', 'style': 'text-transform: uppercase;'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'contrato': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle, Avenida, Carrera'}),
            'numero_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 45'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 23-15'}),
            'complemento_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Apto 301'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar opción vacía al inicio de cada select
        empty_choice = [('', '-- Seleccione --')]
        self.fields['perfil'].choices = empty_choice + list(InformacionBasica.PERFIL_CHOICES)
        self.fields['area_del_conocimiento'].choices = empty_choice + list(InformacionBasica.AREA_CONOCIMIENTO_CHOICES)
        self.fields['profesion'].choices = empty_choice + list(InformacionBasica.PROFESION_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        # Convertir campos "otro" a mayúsculas y validar
        
        # Validar Perfil
        perfil = cleaned_data.get('perfil')
        perfil_otro = cleaned_data.get('perfil_otro')
        if perfil == 'OTRO' and not perfil_otro:
            self.add_error('perfil_otro', 'Debe especificar el perfil si seleccionó "OTRO".')
        
        # Validar Área del Conocimiento
        area = cleaned_data.get('area_del_conocimiento')
        area_otro = cleaned_data.get('area_del_conocimiento_otro')
        if area == 'OTRO' and not area_otro:
            self.add_error('area_del_conocimiento_otro', 'Debe especificar el área si seleccionó "OTRO".')
            
        # Validar Profesión
        profesion = cleaned_data.get('profesion')
        profesion_otro = cleaned_data.get('profesion_otro')
        if profesion == 'OTRO' and not profesion_otro:
            self.add_error('profesion_otro', 'Debe especificar la profesión si seleccionó "OTRO".')

        for field in ['perfil_otro', 'area_del_conocimiento_otro', 'profesion_otro']:
            value = cleaned_data.get(field)
            if value:
                cleaned_data[field] = value.upper()
        return cleaned_data

class ExperienciaLaboralForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        exclude = ['informacion_basica']
        widgets = {
            'certificado_laboral': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'meses_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'readonly': 'readonly'}),
            'dias_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'readonly': 'readonly'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniero de Sistemas'}),
            'cargo_anexo_11': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Profesional'}),
            'objeto_contractual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describa el objeto contractual'}),
            'funciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describa las funciones realizadas'}),
            'fecha_inicial': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        error_messages = {
            'fecha_inicial': {
                'required': 'La fecha inicial es obligatoria.',
            },
            'fecha_terminacion': {
                'required': 'La fecha de terminación es obligatoria.',
            },
            'cargo': {
                'required': 'El cargo es obligatorio.',
            },
            'objeto_contractual': {
                'required': 'El objeto contractual es obligatorio.',
            },
            'funciones': {
                'required': 'Las funciones son obligatorias.',
            },
            'certificado_laboral': {
                'required': 'Debe adjuntar el certificado laboral o contractual.',
            },
            'meses_experiencia': {
                'required': 'Los meses de experiencia son obligatorios.',
            },
            'dias_experiencia': {
                'required': 'Los días de experiencia son obligatorios.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo cargo_anexo_11 opcional
        self.fields['cargo_anexo_11'].required = False
        # Establecer valor por defecto si está vacío
        if not self.instance.pk and not self.data:
            self.fields['cargo_anexo_11'].initial = 'Profesional'

        # Agregar textos de ayuda para objeto contractual y funciones
        self.fields['objeto_contractual'].help_text = (
            '⚠️ IMPORTANTE: El certificado laboral que adjunte debe contener esta misma información. '
            'Asegúrese de que el objeto contractual que describe aquí coincida con el que aparece en su certificado. '
            'NOTA: No es necesario adjuntar experiencia relacionada con comedores comunitarios en contrato con la Arquidiócesis de Cali.'
        )
        self.fields['funciones'].help_text = (
            '⚠️ IMPORTANTE: El certificado laboral que adjunte debe contener esta misma información. '
            'Asegúrese de que las funciones que describe aquí coincidan con las que aparecen en su certificado.'
        )

        # Si es una instancia existente (edición), hacer el campo opcional
        if self.instance and self.instance.pk:
            self.fields['certificado_laboral'].required = False
            # Remover el atributo required del widget
            self.fields['certificado_laboral'].widget.attrs.pop('required', None)
            # Remover validadores temporalmente para evitar errores cuando el campo está vacío
            # Los validadores se ejecutarán solo si hay un archivo nuevo en clean_certificado_laboral
            original_validators = self.fields['certificado_laboral'].validators.copy()
            self.fields['certificado_laboral'].validators = []
            # Guardar validadores originales para usarlos en clean_certificado_laboral
            self._original_certificado_validators = original_validators
        else:
            # Si es un nuevo registro, el certificado es obligatorio
            self.fields['certificado_laboral'].required = True
            self._original_certificado_validators = None

    def clean_cargo_anexo_11(self):
        cargo_anexo_11 = self.cleaned_data.get('cargo_anexo_11', '')
        # Si el campo está vacío, establecer valor por defecto
        if not cargo_anexo_11:
            return 'Profesional'
        return cargo_anexo_11

    def clean_certificado_laboral(self):
        certificado = self.cleaned_data.get('certificado_laboral', None)
        
        # Si es una instancia existente (tiene pk) y no se proporciona un nuevo archivo
        # mantener el archivo existente
        if self.instance and self.instance.pk:
            # Si no se proporciona un nuevo certificado
            # En Django, cuando un campo de archivo está vacío en un formset, puede ser None, False, o un objeto vacío
            if not certificado or (hasattr(certificado, 'name') and not certificado.name) or certificado == '':
                # Si ya existe un certificado, mantenerlo
                if hasattr(self.instance, 'certificado_laboral') and self.instance.certificado_laboral:
                    # Retornar el archivo existente sin validarlo nuevamente
                    return self.instance.certificado_laboral
                # Si no hay certificado existente y no se proporciona uno nuevo, retornar None
                return None
        
        # Si se proporciona un nuevo certificado, validarlo con los validadores originales
        if certificado and hasattr(self, '_original_certificado_validators') and self._original_certificado_validators:
            # Ejecutar validadores manualmente solo si hay un archivo nuevo
            for validator in self._original_certificado_validators:
                validator(certificado)
        
        return certificado

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_terminacion = cleaned_data.get('fecha_terminacion')
        today = date.today()

        if fecha_inicial and fecha_inicial > today:
            raise forms.ValidationError('La fecha inicial no puede ser una fecha futura.')
            
        if fecha_terminacion and fecha_terminacion > today:
            raise forms.ValidationError('La fecha de terminación no puede ser una fecha futura.')

        # Validar que la fecha inicial sea menor que la fecha de terminación
        if fecha_inicial and fecha_terminacion:
            if fecha_inicial >= fecha_terminacion:
                raise forms.ValidationError('La fecha inicial debe ser anterior a la fecha de terminación.')

        return cleaned_data

class InformacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = InformacionAcademica
        exclude = ['informacion_basica']
        widgets = {
            'fecha_expedicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tarjeta_profesional': forms.Select(attrs={'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control'}),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_tarjeta_resolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_grado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # FASE 2: Documentos académicos
            'fotocopia_titulo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fotocopia_tarjeta_profesional': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'certificado_vigencia_tarjeta': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_vigencia_tarjeta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_fecha_grado(self):
        fecha = self.cleaned_data.get('fecha_grado')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de grado no puede ser futura.')
        return fecha

class PosgradoForm(forms.ModelForm):
    class Meta:
        model = Posgrado
        exclude = ['informacion_basica']
        widgets = {
            'nombre_posgrado': forms.TextInput(attrs={'class': 'form-control'}),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acta_grado_diploma': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }
    
    def clean_fecha_terminacion(self):
        fecha = self.cleaned_data.get('fecha_terminacion')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de terminación no puede ser futura.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre_posgrado')
        universidad = cleaned_data.get('universidad')
        fecha = cleaned_data.get('fecha_terminacion')
        documento = cleaned_data.get('acta_grado_diploma')
        
        # Si se llenó algún campo de texto, el archivo es obligatorio
        if (nombre or universidad or fecha) and not documento and not self.instance.pk:
            self.add_error('acta_grado_diploma', 'Debe adjuntar el acta de grado o diploma si registra este posgrado.')
            
        return cleaned_data

class EspecializacionForm(forms.ModelForm):
    class Meta:
        model = Especializacion
        exclude = ['informacion_basica']
        widgets = {
            'nombre_especializacion': forms.TextInput(attrs={'class': 'form-control'}),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acta_grado_diploma': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }
        
    def clean_fecha_terminacion(self):
        fecha = self.cleaned_data.get('fecha_terminacion')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de terminación no puede ser futura.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre_especializacion')
        universidad = cleaned_data.get('universidad')
        fecha = cleaned_data.get('fecha_terminacion')
        documento = cleaned_data.get('acta_grado_diploma')
        
        # Si se llenó algún campo de texto, el archivo es obligatorio
        if (nombre or universidad or fecha) and not documento and not self.instance.pk:
            self.add_error('acta_grado_diploma', 'Debe adjuntar el acta de grado o diploma si registra esta especialización.')
            
        return cleaned_data

from .models import EducacionBasica, EducacionSuperior

class EducacionBasicaForm(forms.ModelForm):
    class Meta:
        model = EducacionBasica
        exclude = ['informacion_basica']
        widgets = {
            'institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'anio_grado': forms.NumberInput(attrs={'class': 'form-control', 'min': '1950', 'max': str(date.today().year)}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'acta_grado_diploma': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        institucion = cleaned_data.get('institucion')
        anio_grado = cleaned_data.get('anio_grado')
        acta_grado = cleaned_data.get('acta_grado_diploma')
        
        # Si se llenó algún campo de texto, el archivo es obligatorio (si es un registro nuevo)
        if (institucion or anio_grado) and not acta_grado and not self.instance.pk:
            self.add_error('acta_grado_diploma', 'Debe adjuntar el acta de grado o diploma si registra esta formación.')
            
        return cleaned_data

class EducacionSuperiorForm(forms.ModelForm):
    class Meta:
        model = EducacionSuperior
        exclude = ['informacion_basica']
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_grado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tarjeta_profesional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'documento_soporte': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }
    
    def clean_fecha_grado(self):
        fecha = self.cleaned_data.get('fecha_grado')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de grado no puede ser futura.')
        return fecha
        
    def clean(self):
        cleaned_data = super().clean()
        institucion = cleaned_data.get('institucion')
        titulo = cleaned_data.get('titulo')
        documento = cleaned_data.get('documento_soporte')
        
        # Si se llenó algún campo de texto, el archivo es obligatorio (si es un registro nuevo)
        if (institucion or titulo) and not documento and not self.instance.pk:
            self.add_error('documento_soporte', 'Debe adjuntar el diploma o acta de grado si registra esta formación.')
            
        return cleaned_data

EducacionBasicaFormSet = inlineformset_factory(
    InformacionBasica,
    EducacionBasica,
    form=EducacionBasicaForm,
    extra=1,
    can_delete=True
)

EducacionSuperiorFormSet = inlineformset_factory(
    InformacionBasica,
    EducacionSuperior,
    form=EducacionSuperiorForm,
    extra=1,
    can_delete=True
)

ExperienciaLaboralFormSet = inlineformset_factory(
    InformacionBasica,
    ExperienciaLaboral,
    form=ExperienciaLaboralForm,
    extra=1,
    can_delete=True
)

InformacionAcademicaFormSet = inlineformset_factory(
    InformacionBasica,
    InformacionAcademica,
    form=InformacionAcademicaForm,
    extra=1,
    can_delete=True
)

PosgradoFormSet = inlineformset_factory(
    InformacionBasica,
    Posgrado,
    form=PosgradoForm,
    extra=1,
    can_delete=True
)

EspecializacionFormSet = inlineformset_factory(
    InformacionBasica,
    Especializacion,
    form=EspecializacionForm,
    extra=1,
    can_delete=True
)


# FASE 1: Formulario de Documentos de Identidad y Autorización
class DocumentosIdentidadForm(forms.ModelForm):
    class Meta:
        model = DocumentosIdentidad
        exclude = ['informacion_basica', 'created_at', 'updated_at']
        widgets = {
            'fotocopia_cedula': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'hoja_de_vida': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'libreta_militar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'numero_libreta_militar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 123456789'
            }),
            'distrito_militar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Distrito Militar No. 32'
            }),
            'clase_libreta': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        error_messages = {
            'fotocopia_cedula': {
                'required': 'La fotocopia de la cédula es obligatoria.',
            },
            'hoja_de_vida': {
                'required': 'La hoja de vida es obligatoria.',
            },
        }

    def __init__(self, *args, **kwargs):
        self.genero = kwargs.pop('genero', None)
        super().__init__(*args, **kwargs)

        # Hacer hoja_de_vida obligatoria (aunque el modelo permite null para registros existentes)
        self.fields['hoja_de_vida'].required = True

        # Si es una instancia existente (edición), hacer los campos de archivo opcionales
        if self.instance and self.instance.pk:
            self.fields['fotocopia_cedula'].required = False
            self.fields['hoja_de_vida'].required = False

    def clean(self):
        cleaned_data = super().clean()
        # La libreta militar es ahora opcional para todos los géneros
        # Se mantiene el campo pero sin validación obligatoria
        return cleaned_data


# FASE 3: Formulario de Antecedentes y Verificaciones
class AntecedentesForm(forms.ModelForm):
    class Meta:
        model = Antecedentes
        exclude = ['informacion_basica', 'created_at', 'updated_at']
        widgets = {
            'certificado_procuraduria': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_procuraduria': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificado_contraloria': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_contraloria': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificado_policia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_policia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificado_medidas_correctivas': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_medidas_correctivas': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificado_delitos_sexuales': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_delitos_sexuales': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificado_redam': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fecha_redam': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        error_messages = {
            'certificado_procuraduria': {
                'required': 'El certificado de Procuraduría es obligatorio.',
            },
            'fecha_procuraduria': {
                'required': 'La fecha del certificado de Procuraduría es obligatoria.',
            },
            'certificado_contraloria': {
                'required': 'El certificado de Contraloría es obligatorio.',
            },
            'fecha_contraloria': {
                'required': 'La fecha del certificado de Contraloría es obligatoria.',
            },
            'certificado_policia': {
                'required': 'El certificado de Policía es obligatorio.',
            },
            'fecha_policia': {
                'required': 'La fecha del certificado de Policía es obligatoria.',
            },
            'certificado_medidas_correctivas': {
                'required': 'El certificado de Medidas Correctivas es obligatorio.',
            },
            'fecha_medidas_correctivas': {
                'required': 'La fecha del certificado de Medidas Correctivas es obligatoria.',
            },
            'certificado_delitos_sexuales': {
                'required': 'El certificado de Delitos Sexuales es obligatorio.',
            },
            'fecha_delitos_sexuales': {
                'required': 'La fecha de consulta de Delitos Sexuales es obligatoria.',
            },
            'certificado_redam': {
                'required': 'El certificado REDAM es obligatorio.',
            },
            'fecha_redam': {
                'required': 'La fecha de consulta REDAM es obligatoria.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una instancia existente (edición), hacer los campos de archivo opcionales
        if self.instance and self.instance.pk:
            for field_name in ['certificado_procuraduria', 'certificado_contraloria',
                              'certificado_policia', 'certificado_medidas_correctivas',
                              'certificado_delitos_sexuales', 'certificado_redam']:
                self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        # Validar que las fechas de antecedentes no sean mayores a 30 días
        today = date.today()
        campos_fecha = [
            'fecha_procuraduria', 'fecha_contraloria', 'fecha_policia', 
            'fecha_medidas_correctivas', 'fecha_delitos_sexuales', 'fecha_redam'
        ]
        
        for campo in campos_fecha:
            fecha = cleaned_data.get(campo)
            if fecha:
                dias_diferencia = (today - fecha).days
                if dias_diferencia > 30:
                    self.add_error(campo, 'El certificado no puede tener una vigencia mayor a 30 días.')
                if fecha > today:
                    self.add_error(campo, 'La fecha no puede ser futura.')
        
        return cleaned_data


# FASE 4: Formulario de Anexos Adicionales
class AnexosAdicionalesForm(forms.ModelForm):
    class Meta:
        model = AnexosAdicionales
        exclude = ['informacion_basica', 'created_at', 'updated_at']
        widgets = {
            'anexo_03_datos_personales': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'carta_intencion': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'otros_documentos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'descripcion_otros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describa el contenido del documento adicional'
            }),
        }
        help_texts = {
            'descripcion_otros': '<strong style="color: #ff6b00; font-size: 1.1em;">📋 IMPORTANTE: Población Diferencial</strong><br>Si pertenece a un grupo de población diferencial (indígena, afrodescendiente, víctima del conflicto, persona con discapacidad, etc.), adjunte el certificado y menciónelo aquí.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar nota aclaratoria para población diferencial en el campo de descripción
        self.fields['descripcion_otros'].help_text = '<strong style="color: #ff6b00; font-size: 1.1em;">📋 IMPORTANTE: Población Diferencial</strong><br>Si pertenece a un grupo de población diferencial (indígena, afrodescendiente, víctima del conflicto, persona con discapacidad, etc.), adjunte el certificado y menciónelo aquí.'