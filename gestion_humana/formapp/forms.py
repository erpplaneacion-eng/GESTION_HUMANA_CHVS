from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado, Especializacion

# Formulario público - solo campos que el usuario puede llenar
class InformacionBasicaPublicForm(forms.ModelForm):
    # Campos separados para el nombre
    primer_apellido = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'}),
        error_messages={'required': 'El campo Primer Apellido es obligatorio.'}
    )
    segundo_apellido = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido'}),
        error_messages={'required': 'El campo Segundo Apellido es obligatorio.'}
    )
    primer_nombre = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Nombre'}),
        error_messages={'required': 'El campo Primer Nombre es obligatorio.'}
    )
    segundo_nombre = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Nombre (Opcional)'})
    )

    class Meta:
        model = InformacionBasica
        # Excluir nombre_completo porque lo construiremos a partir de los campos separados
        fields = [
            'cedula', 'genero',
            'tipo_via', 'numero_via', 'numero_casa', 'complemento_direccion', 'barrio',
            'telefono', 'correo'
        ]
        widgets = {
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
        }
        error_messages = {
            'cedula': {
                'required': 'El campo Cédula es obligatorio.',
            },
            'genero': {
                'required': 'El campo Género es obligatorio.',
            },
            'tipo_via': {
                'required': 'El campo Tipo de Vía es obligatorio.',
            },
            'numero_via': {
                'required': 'El campo Número de Vía es obligatorio.',
            },
            'numero_casa': {
                'required': 'El campo Número de Casa/Edificio es obligatorio.',
            },
            'telefono': {
                'required': 'El campo Teléfono es obligatorio.',
            },
            'correo': {
                'required': 'El campo Correo Electrónico es obligatorio.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando, dividir el nombre completo
        if self.instance and self.instance.nombre_completo:
            partes = self.instance.nombre_completo.split()
            if len(partes) >= 3:
                self.initial['primer_apellido'] = partes[0] if len(partes) > 0 else ''
                self.initial['segundo_apellido'] = partes[1] if len(partes) > 1 else ''
                self.initial['primer_nombre'] = partes[2] if len(partes) > 2 else ''
                self.initial['segundo_nombre'] = ' '.join(partes[3:]) if len(partes) > 3 else ''

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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Construir nombre completo concatenando los campos
        primer_apellido = self.cleaned_data.get('primer_apellido', '').strip()
        segundo_apellido = self.cleaned_data.get('segundo_apellido', '').strip()
        primer_nombre = self.cleaned_data.get('primer_nombre', '').strip()
        segundo_nombre = self.cleaned_data.get('segundo_nombre', '').strip()

        # Concatenar y convertir a mayúsculas
        partes_nombre = [primer_apellido, segundo_apellido, primer_nombre]
        if segundo_nombre:
            partes_nombre.append(segundo_nombre)

        instance.nombre_completo = ' '.join(partes_nombre).upper()

        if commit:
            instance.save()
        return instance

# Formulario completo para el admin - incluye todos los campos
class InformacionBasicaForm(forms.ModelForm):
    class Meta:
        model = InformacionBasica
        fields = '__all__'
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil': forms.TextInput(attrs={'class': 'form-control'}),
            'area_conocimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'area_del_conocimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_perfil': forms.TextInput(attrs={'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control'}),
            'experiencia': forms.TextInput(attrs={'class': 'form-control'}),
            'tiempo_experiencia': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'organizacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            'Asegúrese de que el objeto contractual que describe aquí coincida con el que aparece en su certificado.'
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
            'meses_experiencia_profesion': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class PosgradoForm(forms.ModelForm):
    class Meta:
        model = Posgrado
        exclude = ['informacion_basica']
        widgets = {
            'nombre_posgrado': forms.TextInput(attrs={'class': 'form-control'}),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meses_de_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class EspecializacionForm(forms.ModelForm):
    class Meta:
        model = Especializacion
        exclude = ['informacion_basica']
        widgets = {
            'nombre_especializacion': forms.TextInput(attrs={'class': 'form-control'}),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meses_de_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

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
