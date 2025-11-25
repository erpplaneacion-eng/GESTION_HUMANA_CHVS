from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import uuid
import shutil
import tempfile
from unittest.mock import patch, MagicMock

from ..models import (
    InformacionBasica,
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales
)

# Crear directorio temporal para media
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
    MEDIA_ROOT=TEMP_MEDIA_ROOT
)
class CorrectionFlowTests(TestCase):
    def setUp(self):
        # Crear usuario admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        self.client = Client()
        
        # Crear un postulante de prueba
        self.applicant = InformacionBasica.objects.create(
            primer_apellido='TEST',
            primer_nombre='USER',
            cedula='123456789',
            correo='test@example.com',
            telefono='3001234567',
            genero='Masculino',
            estado='RECIBIDO'
        )

        # Crear dummy file para los campos FileField requeridos
        # Usar contenido válido de un archivo de texto plano o PDF dummy mínimo si fuera validado estrictamente
        dummy_file = SimpleUploadedFile("file.txt", b"contenido de prueba", content_type="text/plain")

        # Crear instancias relacionadas
        DocumentosIdentidad.objects.create(
            informacion_basica=self.applicant,
            fotocopia_cedula=dummy_file
        )
        Antecedentes.objects.create(
            informacion_basica=self.applicant,
            certificado_procuraduria=dummy_file,
            fecha_procuraduria=timezone.now().date(),
            certificado_contraloria=dummy_file,
            fecha_contraloria=timezone.now().date(),
            certificado_policia=dummy_file,
            fecha_policia=timezone.now().date(),
            certificado_medidas_correctivas=dummy_file,
            fecha_medidas_correctivas=timezone.now().date(),
            certificado_delitos_sexuales=dummy_file,
            fecha_delitos_sexuales=timezone.now().date(),
        )
        AnexosAdicionales.objects.create(
            informacion_basica=self.applicant
        )
        
        self.detail_url = reverse('formapp:applicant_detail', kwargs={'pk': self.applicant.pk})
        self.correction_url = reverse('formapp:solicitar_correccion', kwargs={'pk': self.applicant.pk})

    def tearDown(self):
        # Limpiar directorio temporal
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @patch('formapp.services.get_gmail_service')
    def test_admin_request_correction(self, mock_get_service):
        """Prueba que el admin puede solicitar corrección y se actualiza el estado"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        self.client.login(username='admin', password='adminpassword')
        
        # Enviar solicitud POST
        response = self.client.post(self.correction_url, {
            'mensaje_observacion': 'Corregir cédula ilegible'
        }, follow=True)
        
        # Verificar redirección y mensaje
        self.assertRedirects(response, self.detail_url)
        self.assertContains(response, 'Se ha enviado la solicitud de corrección')
        
        # Verificar actualización del modelo
        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.estado, 'PENDIENTE_CORRECCION')
        self.assertIsNotNone(self.applicant.token_correccion)
        self.assertIsNotNone(self.applicant.token_expiracion)
        
        # Verificar que la expiración es futura
        future = timezone.now() + timedelta(hours=47)
        self.assertTrue(self.applicant.token_expiracion > future)

    def test_public_access_with_valid_token(self):
        """Prueba el acceso a la vista pública con un token válido"""
        token = uuid.uuid4()
        self.applicant.token_correccion = token
        self.applicant.token_expiracion = timezone.now() + timedelta(hours=48)
        self.applicant.estado = 'PENDIENTE_CORRECCION'
        self.applicant.save()
        
        url = reverse('formapp:public_update', kwargs={'token': token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/applicant_edit.html')
        self.assertContains(response, self.applicant.nombre_completo)

    def test_public_access_with_invalid_token(self):
        """Prueba que un token inexistente redirige al inicio"""
        invalid_token = uuid.uuid4()
        url = reverse('formapp:public_update', kwargs={'token': invalid_token})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse('formapp:public_form'))

    def test_public_access_with_expired_token(self):
        """Prueba que un token expirado no permite el acceso"""
        token = uuid.uuid4()
        self.applicant.token_correccion = token
        self.applicant.token_expiracion = timezone.now() - timedelta(hours=1)
        self.applicant.save()
        
        url = reverse('formapp:public_update', kwargs={'token': token})
        response = self.client.get(url)
        
        self.assertRedirects(response, reverse('formapp:public_form'))

    def test_successful_correction_submission(self):
        """Prueba el flujo completo: usuario envía corrección y se actualiza estado"""
        token = uuid.uuid4()
        self.applicant.token_correccion = token
        self.applicant.token_expiracion = timezone.now() + timedelta(hours=24)
        self.applicant.estado = 'PENDIENTE_CORRECCION'
        self.applicant.save()
        
        url = reverse('formapp:public_update', kwargs={'token': token})
        
        # Datos mínimos requeridos para el formulario
        data = {
            'primer_apellido': 'TEST_UPDATED',
            'primer_nombre': 'USER',
            'cedula': '123456789',
            'correo': 'test@example.com',
            'telefono': '3001234567',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'acepta_politica': 'on',
            
            # Campos requeridos de antecedentes
            'fecha_procuraduria': timezone.now().date(),
            'fecha_contraloria': timezone.now().date(),
            'fecha_policia': timezone.now().date(),
            'fecha_medidas_correctivas': timezone.now().date(),
            'fecha_delitos_sexuales': timezone.now().date(),

            # Formsets management
            'experiencias_laborales-TOTAL_FORMS': '0',
            'experiencias_laborales-INITIAL_FORMS': '0',
            'formacion_academica-TOTAL_FORMS': '0',
            'formacion_academica-INITIAL_FORMS': '0',
            'posgrados-TOTAL_FORMS': '0',
            'posgrados-INITIAL_FORMS': '0',
            'especializaciones-TOTAL_FORMS': '0',
            'especializaciones-INITIAL_FORMS': '0',
            'educacion_basica-TOTAL_FORMS': '0',
            'educacion_basica-INITIAL_FORMS': '0',
            'educacion_superior-TOTAL_FORMS': '0',
            'educacion_superior-INITIAL_FORMS': '0',
        }
        
        response = self.client.post(url, data)
        
        self.assertRedirects(response, reverse('formapp:public_form'))
        
        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.primer_apellido, 'TEST_UPDATED')
        self.assertEqual(self.applicant.estado, 'CORREGIDO')
        self.assertIsNone(self.applicant.token_correccion)
