from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado

# Formulario público - solo campos que el usuario puede llenar
class InformacionBasicaPublicForm(forms.ModelForm):
    # Campos separados para el nombre
    primer_apellido = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'})
    )
    segundo_apellido = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido'})
    )
    primer_nombre = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Nombre'})
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
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'base_anexo_11': forms.TextInput(attrs={'class': 'form-control'}),
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
                'required': 'required'
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
            'cargo_anexo_11': {
                'required': 'El cargo anexo 11 es obligatorio.',
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
