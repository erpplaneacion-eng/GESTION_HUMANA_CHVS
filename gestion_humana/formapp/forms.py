from django import forms
from django.forms import inlineformset_factory
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado

# Formulario público - solo campos que el usuario puede llenar
class InformacionBasicaPublicForm(forms.ModelForm):
    class Meta:
        model = InformacionBasica
        # Excluir campos administrativos que solo el personal administrativo debe llenar
        fields = [
            'nombre_completo', 'cedula', 'genero',
            'tipo_via', 'numero_via', 'numero_casa', 'complemento_direccion', 'barrio',
            'telefono', 'correo'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'tipo_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle, Avenida, Carrera'}),
            'numero_via': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 45'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 23-15'}),
            'complemento_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Apto 301'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

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
            'certificado_laboral': forms.FileInput(attrs={'class': 'form-control'}),
            'meses_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'readonly': 'readonly'}),
            'dias_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'readonly': 'readonly'}),
            'dias_residual_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_anexo_11': forms.TextInput(attrs={'class': 'form-control'}),
            'objeto_contractual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'funciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fecha_inicial': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_terminacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

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
