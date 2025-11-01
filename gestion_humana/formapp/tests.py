from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import InformacionBasica, ExperienciaLaboral, InformacionAcademica, Posgrado, CalculoExperiencia
from .forms import (
    InformacionBasicaPublicForm,
    ExperienciaLaboralForm,
    InformacionAcademicaForm,
    PosgradoForm
)
from datetime import date, timedelta
import tempfile


class InformacionBasicaModelTest(TestCase):
    """Tests para el modelo InformacionBasica"""
    
    def setUp(self):
        self.informacion_basica = InformacionBasica.objects.create(
            nombre_completo='JUAN PEREZ GARCIA',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='45',
            numero_casa='12-34',
            telefono='3001234567',
            correo='juan@example.com'
        )
    
    def test_informacion_basica_creation(self):
        """Test que se puede crear una instancia de InformacionBasica"""
        self.assertIsNotNone(self.informacion_basica)
        self.assertEqual(str(self.informacion_basica), 'JUAN PEREZ GARCIA')
    
    def test_cedula_unique(self):
        """Test que la cédula es única"""
        with self.assertRaises(Exception):
            InformacionBasica.objects.create(
                nombre_completo='MARIA LOPEZ',
                cedula='1234567890',  # Misma cédula
                genero='Femenino',
                tipo_via='Calle',
                numero_via='1',
                numero_casa='1',
                telefono='3012345678',
                correo='maria@example.com'
            )


class FormsTest(TestCase):
    """Tests para los formularios"""
    
    def test_informacion_basica_public_form_valid(self):
        """Test del formulario público con datos válidos"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_informacion_basica_public_form_empty_fields(self):
        """Test que campos obligatorios vacíos muestran errores"""
        form = InformacionBasicaPublicForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('primer_apellido', form.errors)
        self.assertIn('segundo_apellido', form.errors)
        self.assertIn('primer_nombre', form.errors)
        self.assertIn('cedula', form.errors)
        self.assertIn('genero', form.errors)
        self.assertIn('telefono', form.errors)
        self.assertIn('correo', form.errors)
    
    def test_informacion_basica_public_form_error_messages_spanish(self):
        """Test que los mensajes de error están en español"""
        form = InformacionBasicaPublicForm(data={})
        self.assertFalse(form.is_valid())
        
        # Verificar mensajes en español
        self.assertIn('obligatorio', str(form.errors['primer_apellido']))
        self.assertIn('obligatorio', str(form.errors['cedula']))
    
    def test_cedula_validation_digits_only(self):
        """Test validación de cédula solo números"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '12345a7890',  # Con letra
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('solo números', str(form.errors['cedula']))
    
    def test_cedula_validation_length(self):
        """Test validación de longitud de cédula"""
        # Cédula muy corta
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234',  # Solo 4 dígitos
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('entre 5 y 10 dígitos', str(form.errors['cedula']))
    
    def test_telefono_validation(self):
        """Test validación de teléfono"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '12345',  # Muy corto
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('exactamente 10 dígitos', str(form.errors['telefono']))
    
    def test_correo_validation(self):
        """Test validación de correo"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juansinejemplo.com'  # Sin @
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('contener @', str(form.errors['correo']))
    
    def test_save_nombre_completo(self):
        """Test que el método save construye correctamente el nombre completo"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        informacion_basica = form.save()
        self.assertEqual(informacion_basica.nombre_completo, 'GARCÍA LÓPEZ JUAN')
    
    def test_save_nombre_completo_con_segundo_nombre(self):
        """Test que el nombre completo incluye el segundo nombre si está presente"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'segundo_nombre': 'Carlos',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com'
        }
        form = InformacionBasicaPublicForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        informacion_basica = form.save()
        self.assertEqual(informacion_basica.nombre_completo, 'GARCÍA LÓPEZ JUAN CARLOS')


class ExperienciaLaboralFormTest(TestCase):
    """Tests para el formulario de ExperienciaLaboral"""
    
    def test_experiencia_laboral_form_valid(self):
        """Test formulario de experiencia laboral con datos válidos"""
        fecha_inicio = date(2020, 1, 1)
        fecha_fin = date(2022, 12, 31)
        
        form_data = {
            'cargo': 'Ingeniero de Sistemas',
            'cargo_anexo_11': 'Profesional',
            'fecha_inicial': fecha_inicio,
            'fecha_terminacion': fecha_fin,
            'meses_experiencia': 24,
            'dias_experiencia': 730,
            'objeto_contractual': 'Desarrollo de software',
            'funciones': 'Desarrollo y mantenimiento de aplicaciones web'
        }
        
        file = SimpleUploadedFile("certificado.pdf", b"file_content", content_type="application/pdf")
        form = ExperienciaLaboralForm(data=form_data, files={'certificado_laboral': file})
        
        self.assertTrue(form.is_valid())
    
    def test_experiencia_laboral_form_empty_required_fields(self):
        """Test que campos obligatorios de experiencia están en español"""
        form = ExperienciaLaboralForm(data={})
        self.assertFalse(form.is_valid())
        
        # Verificar que los mensajes de error están en español
        self.assertIn('obligatorio', str(form.errors.get('cargo', '')))
        self.assertIn('obligatorio', str(form.errors.get('fecha_inicial', '')))
        self.assertIn('obligatorio', str(form.errors.get('certificado_laboral', '')))
    
    def test_experiencia_laboral_fecha_inicial_after_terminacion(self):
        """Test que fecha inicial no puede ser mayor que fecha de terminación"""
        form_data = {
            'cargo': 'Ingeniero',
            'cargo_anexo_11': 'Profesional',
            'fecha_inicial': date(2022, 12, 31),
            'fecha_terminacion': date(2020, 1, 1),  # Fecha anterior
            'meses_experiencia': 24,
            'dias_experiencia': 730,
            'objeto_contractual': 'Trabajo',
            'funciones': 'Desarrollo'
        }
        
        file = SimpleUploadedFile("certificado.pdf", b"file_content", content_type="application/pdf")
        form = ExperienciaLaboralForm(data=form_data, files={'certificado_laboral': file})
        
        self.assertFalse(form.is_valid())
        self.assertIn('anterior', str(form.errors))


class ViewTest(TestCase):
    """Tests para las vistas"""
    
    def setUp(self):
        self.client = Client()
        # Crear usuario para pruebas de autenticación
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_public_form_view_get(self):
        """Test que la vista pública del formulario carga correctamente"""
        response = self.client.get(reverse('formapp:public_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/public_form.html')
        self.assertIsInstance(response.context['form'], InformacionBasicaPublicForm)
    
    def test_public_form_view_post_valid(self):
        """Test que un formulario válido se guarda correctamente"""
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com',
            # Experiencia Laboral
            'experiencias_laborales-TOTAL_FORMS': '1',
            'experiencias_laborales-INITIAL_FORMS': '0',
            'experiencias_laborales-MIN_NUM_FORMS': '0',
            'experiencias_laborales-MAX_NUM_FORMS': '1000',
            'experiencias_laborales-0-cargo': 'Ingeniero',
            'experiencias_laborales-0-cargo_anexo_11': 'Profesional',
            'experiencias_laborales-0-fecha_inicial': '2020-01-01',
            'experiencias_laborales-0-fecha_terminacion': '2022-12-31',
            'experiencias_laborales-0-meses_experiencia': '24',
            'experiencias_laborales-0-dias_experiencia': '730',
            'experiencias_laborales-0-objeto_contractual': 'Desarrollo',
            'experiencias_laborales-0-funciones': 'Desarrollar sistemas',
            'experiencias_laborales-0-certificado_laboral': SimpleUploadedFile(
                "certificado.pdf", b"file_content", content_type="application/pdf"
            ),
            # Información Académica
            'formacion_academica-TOTAL_FORMS': '0',
            'formacion_academica-INITIAL_FORMS': '0',
            'formacion_academica-MIN_NUM_FORMS': '0',
            'formacion_academica-MAX_NUM_FORMS': '1000',
            # Posgrados
            'posgrados-TOTAL_FORMS': '0',
            'posgrados-INITIAL_FORMS': '0',
            'posgrados-MIN_NUM_FORMS': '0',
            'posgrados-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(reverse('formapp:public_form'), form_data)
        
        # Debe redirigir al formulario con mensaje de éxito
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InformacionBasica.objects.count(), 1)
    
    def test_public_form_view_post_invalid(self):
        """Test que un formulario inválido muestra errores"""
        form_data = {
            'primer_apellido': '',  # Vacío
            'cedula': 'invalid',  # Inválido
        }
        
        response = self.client.post(reverse('formapp:public_form'), form_data)
        
        # Debe volver a mostrar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_applicant_list_view_requires_login(self):
        """Test que la lista de aplicantes requiere autenticación"""
        response = self.client.get(reverse('formapp:applicant_list'))
        self.assertEqual(response.status_code, 302)  # Redirige al login
    
    def test_applicant_list_view_with_login(self):
        """Test que la lista de aplicantes funciona con login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('formapp:applicant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/applicant_list.html')


class ValidatorTest(TestCase):
    """Tests para los validadores personalizados"""
    
    def test_validate_file_size_valid(self):
        """Test que un archivo pequeño es válido"""
        from .validators import validate_file_size
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Archivo de 1MB (válido)
        file = SimpleUploadedFile("small.pdf", b"x" * 1024 * 1024, content_type="application/pdf")
        
        try:
            validate_file_size(file)
        except Exception:
            self.fail("validate_file_size() raised an exception for a valid file")
    
    def test_validate_file_size_too_large(self):
        """Test que un archivo grande es rechazado"""
        from .validators import validate_file_size
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        
        # Archivo de 11MB (muy grande)
        file = SimpleUploadedFile("large.pdf", b"x" * 11 * 1024 * 1024, content_type="application/pdf")
        
        with self.assertRaises(ValidationError) as context:
            validate_file_size(file)
        
        self.assertIn('10 MB', str(context.exception))
    
    def test_validate_file_extension_valid(self):
        """Test que extensiones válidas son aceptadas"""
        from .validators import validate_file_extension
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        valid_extensions = ['test.pdf', 'test.jpg', 'test.jpeg', 'test.png']
        
        for filename in valid_extensions:
            file = SimpleUploadedFile(filename, b"content", content_type="application/pdf")
            try:
                validate_file_extension(file)
            except Exception:
                self.fail(f"validate_file_extension() raised an exception for valid extension: {filename}")
    
    def test_validate_file_extension_invalid(self):
        """Test que extensiones inválidas son rechazadas"""
        from .validators import validate_file_extension
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        
        invalid_extensions = ['test.exe', 'test.doc', 'test.txt']
        
        for filename in invalid_extensions:
            file = SimpleUploadedFile(filename, b"content", content_type="application/pdf")
            with self.assertRaises(ValidationError):
                validate_file_extension(file)


class CalculoExperienciaTest(TestCase):
    """Tests para el cálculo de experiencia"""
    
    def setUp(self):
        self.informacion_basica = InformacionBasica.objects.create(
            nombre_completo='JUAN PEREZ GARCIA',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='45',
            numero_casa='12-34',
            telefono='3001234567',
            correo='juan@example.com'
        )
    
    def test_calcular_experiencia_total(self):
        """Test que se calcula correctamente la experiencia total"""
        from .views import calcular_experiencia_total
        
        # Crear dos experiencias laborales
        ExperienciaLaboral.objects.create(
            informacion_basica=self.informacion_basica,
            cargo='Ingeniero',
            cargo_anexo_11='Profesional',
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2022, 12, 31),
            meses_experiencia=24,
            dias_experiencia=730,
            objeto_contractual='Desarrollo',
            funciones='Desarrollar',
            certificado_laboral='cert1.pdf'
        )
        
        ExperienciaLaboral.objects.create(
            informacion_basica=self.informacion_basica,
            cargo='Desarrollador',
            cargo_anexo_11='Profesional',
            fecha_inicial=date(2023, 1, 1),
            fecha_terminacion=date(2024, 12, 31),
            meses_experiencia=12,
            dias_experiencia=365,
            objeto_contractual='Desarrollo',
            funciones='Desarrollar',
            certificado_laboral='cert2.pdf'
        )
        
        # Calcular experiencia total
        calculo = calcular_experiencia_total(self.informacion_basica)
        
        self.assertEqual(calculo.total_meses_experiencia, 36)
        self.assertEqual(calculo.total_dias_experiencia, 1095)
        self.assertEqual(calculo.total_experiencia_anos, 3.0)


class IntegrationTest(TestCase):
    """Tests de integración"""
    
    def test_full_registration_flow(self):
        """Test del flujo completo de registro"""
        client = Client()
        
        form_data = {
            'primer_apellido': 'García',
            'segundo_apellido': 'López',
            'primer_nombre': 'Juan',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '45',
            'numero_casa': '12-34',
            'telefono': '3001234567',
            'correo': 'juan@example.com',
            # Experiencia
            'experiencias_laborales-TOTAL_FORMS': '1',
            'experiencias_laborales-INITIAL_FORMS': '0',
            'experiencias_laborales-MIN_NUM_FORMS': '0',
            'experiencias_laborales-MAX_NUM_FORMS': '1000',
            'experiencias_laborales-0-cargo': 'Ingeniero',
            'experiencias_laborales-0-cargo_anexo_11': 'Profesional',
            'experiencias_laborales-0-fecha_inicial': '2020-01-01',
            'experiencias_laborales-0-fecha_terminacion': '2022-12-31',
            'experiencias_laborales-0-meses_experiencia': '24',
            'experiencias_laborales-0-dias_experiencia': '730',
            'experiencias_laborales-0-objeto_contractual': 'Desarrollo',
            'experiencias_laborales-0-funciones': 'Desarrollar sistemas',
            'experiencias_laborales-0-certificado_laboral': SimpleUploadedFile(
                "certificado.pdf", b"file_content", content_type="application/pdf"
            ),
            # Académica
            'formacion_academica-TOTAL_FORMS': '1',
            'formacion_academica-INITIAL_FORMS': '0',
            'formacion_academica-MIN_NUM_FORMS': '0',
            'formacion_academica-MAX_NUM_FORMS': '1000',
            'formacion_academica-0-profesion': 'Ingeniero de Sistemas',
            'formacion_academica-0-universidad': 'Universidad Nacional',
            'formacion_academica-0-tarjeta_profesional': 'Tarjeta Profesional',
            'formacion_academica-0-numero_tarjeta_resolucion': '12345',
            'formacion_academica-0-fecha_expedicion': '2020-01-01',
            'formacion_academica-0-fecha_grado': '2019-12-31',
            'formacion_academica-0-meses_experiencia_profesion': '36',
            # Posgrados
            'posgrados-TOTAL_FORMS': '1',
            'posgrados-INITIAL_FORMS': '0',
            'posgrados-MIN_NUM_FORMS': '0',
            'posgrados-MAX_NUM_FORMS': '1000',
            'posgrados-0-nombre_posgrado': 'Maestría en Ingeniería',
            'posgrados-0-universidad': 'Universidad Nacional',
            'posgrados-0-fecha_terminacion': '2023-12-31',
            'posgrados-0-meses_de_experiencia': '12',
        }
        
        response = client.post(reverse('formapp:public_form'), form_data)
        
        # Verificar que todo se guardó correctamente
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InformacionBasica.objects.count(), 1)
        self.assertEqual(ExperienciaLaboral.objects.count(), 1)
        self.assertEqual(InformacionAcademica.objects.count(), 1)
        self.assertEqual(Posgrado.objects.count(), 1)
        self.assertEqual(CalculoExperiencia.objects.count(), 1)
