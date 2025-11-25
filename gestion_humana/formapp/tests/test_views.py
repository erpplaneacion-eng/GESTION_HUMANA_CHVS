"""
Tests para las vistas de la aplicación formapp.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from formapp.models import (
    InformacionBasica,
    ExperienciaLaboral,
    InformacionAcademica,
    CalculoExperiencia,
    DocumentosIdentidad,
    Antecedentes,
)


class PublicFormViewTest(TestCase):
    """Tests para la vista de formulario público"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.url = reverse('formapp:public_form')

    def test_public_form_get(self):
        """Test que la vista GET carga correctamente"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/public_form.html')

    def test_public_form_contiene_formularios(self):
        """Test que la vista contiene todos los formularios necesarios"""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIn('documentos_form', response.context)
        self.assertIn('antecedentes_form', response.context)
        self.assertIn('anexos_form', response.context)
        self.assertIn('experiencia_formset', response.context)
        self.assertIn('academica_formset', response.context)
        self.assertIn('posgrado_formset', response.context)
        self.assertIn('especializacion_formset', response.context)

    def test_public_form_sin_autenticacion(self):
        """Test que el formulario público no requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ApplicantListViewTest(TestCase):
    """Tests para la vista de lista de candidatos"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.url = reverse('formapp:applicant_list')

        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Crear candidatos de prueba
        for i in range(25):
            InformacionBasica.objects.create(
                nombre_completo=f'CANDIDATO {i}',
                cedula=f'100000000{i}',
                genero='Masculino',
                tipo_via='Calle',
                numero_via='1',
                numero_casa='1',
                telefono='3001234567',
                correo=f'candidato{i}@test.com',
            )

    def test_applicant_list_requiere_autenticacion(self):
        """Test que la vista requiere autenticación"""
        response = self.client.get(self.url)
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_applicant_list_get_autenticado(self):
        """Test GET autenticado muestra lista"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/applicant_list.html')

    def test_applicant_list_paginacion(self):
        """Test que la lista está paginada (20 por página)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Debe haber 20 candidatos en la primera página
        self.assertEqual(len(response.context['applicants']), 20)

    def test_applicant_list_busqueda_por_cedula(self):
        """Test búsqueda por cédula"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url, {'search': '1000000001'})
        self.assertEqual(response.status_code, 200)
        applicants = response.context['applicants']
        self.assertEqual(len(applicants), 1)
        self.assertEqual(applicants[0].cedula, '10000000001')

    def test_applicant_list_busqueda_por_nombre(self):
        """Test búsqueda por nombre"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url, {'search': 'CANDIDATO 5'})
        self.assertEqual(response.status_code, 200)
        applicants = list(response.context['applicants'])
        # Debería encontrar CANDIDATO 5, 15, etc.
        self.assertGreater(len(applicants), 0)

    def test_applicant_list_estadisticas(self):
        """Test que muestra estadísticas en el contexto"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertIn('total_personal', response.context)
        self.assertIn('con_experiencia', response.context)
        self.assertIn('profesionales', response.context)
        self.assertIn('con_posgrado', response.context)
        self.assertEqual(response.context['total_personal'], 25)


class ApplicantDetailViewTest(TestCase):
    """Tests para la vista de detalle de candidato"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.candidato = InformacionBasica.objects.create(
            nombre_completo='JUAN PEREZ',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='10',
            numero_casa='20-30',
            telefono='3001234567',
            correo='juan@test.com',
        )

        self.url = reverse('formapp:applicant_detail', kwargs={'pk': self.candidato.pk})

    def test_applicant_detail_requiere_autenticacion(self):
        """Test que requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_applicant_detail_get_autenticado(self):
        """Test GET autenticado muestra detalle"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/applicant_detail.html')
        self.assertEqual(response.context['applicant'], self.candidato)

    def test_applicant_detail_candidato_no_existe(self):
        """Test detalle de candidato que no existe"""
        self.client.login(username='testuser', password='testpass123')
        url_invalido = reverse('formapp:applicant_detail', kwargs={'pk': 99999})
        response = self.client.get(url_invalido)
        self.assertEqual(response.status_code, 404)


class ApplicantEditViewTest(TestCase):
    """Tests para la vista de edición de candidato"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.candidato = InformacionBasica.objects.create(
            nombre_completo='MARIA LOPEZ',
            cedula='9876543210',
            genero='Femenino',
            tipo_via='Carrera',
            numero_via='15',
            numero_casa='30-45',
            telefono='3109876543',
            correo='maria@test.com',
        )

        self.url = reverse('formapp:applicant_edit', kwargs={'pk': self.candidato.pk})

    def test_applicant_edit_requiere_autenticacion(self):
        """Test que requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_applicant_edit_get_autenticado(self):
        """Test GET muestra formulario de edición"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formapp/applicant_edit.html')
        self.assertEqual(response.context['applicant'], self.candidato)


class ApplicantDeleteViewTest(TestCase):
    """Tests para la vista de eliminación de candidato"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.candidato = InformacionBasica.objects.create(
            nombre_completo='CARLOS RUIZ',
            cedula='1122334455',
            genero='Masculino',
            tipo_via='Avenida',
            numero_via='5',
            numero_casa='10-20',
            telefono='3201122334',
            correo='carlos@test.com',
        )

        self.url = reverse('formapp:applicant_delete', kwargs={'pk': self.candidato.pk})

    def test_applicant_delete_requiere_autenticacion(self):
        """Test que requiere autenticación"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_applicant_delete_post_elimina_candidato(self):
        """Test POST elimina el candidato"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url)

        # Debe redirigir a la lista
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('formapp:applicant_list'))

        # El candidato no debe existir
        self.assertFalse(
            InformacionBasica.objects.filter(pk=self.candidato.pk).exists()
        )

    def test_applicant_delete_get_redirige_a_lista(self):
        """Test GET redirige a la lista (no muestra formulario de confirmación)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('formapp:applicant_list'))


class DownloadIndividualZipViewTest(TestCase):
    """Tests para la descarga de ZIP individual"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.candidato = InformacionBasica.objects.create(
            nombre_completo='ANA TORRES',
            cedula='5544332211',
            genero='Femenino',
            tipo_via='Calle',
            numero_via='20',
            numero_casa='15-30',
            telefono='3105544332',
            correo='ana@test.com',
        )

        # Agregar experiencia laboral
        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Analista',
            objeto_contractual='Análisis de datos',
            funciones='Reportes y análisis',
        )

        # Crear cálculo de experiencia
        CalculoExperiencia.objects.create(
            informacion_basica=self.candidato,
            total_meses_experiencia=12,
            total_dias_experiencia=366,
            total_experiencia_anos=1.00,
            anos_y_meses_experiencia='1 años y 0 meses',
        )

        self.url = reverse('formapp:download_individual', kwargs={'pk': self.candidato.pk})

    def test_download_individual_requiere_autenticacion(self):
        """Test que requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_download_individual_retorna_zip(self):
        """Test que retorna un archivo ZIP"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment', response['Content-Disposition'])


class DownloadAllZipViewTest(TestCase):
    """Tests para la descarga de ZIP completo"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Crear varios candidatos
        for i in range(3):
            candidato = InformacionBasica.objects.create(
                nombre_completo=f'CANDIDATO {i}',
                cedula=f'100000000{i}',
                genero='Masculino',
                tipo_via='Calle',
                numero_via='1',
                numero_casa='1',
                telefono='3001234567',
                correo=f'candidato{i}@test.com',
            )

        self.url = reverse('formapp:download_all')

    def test_download_all_requiere_autenticacion(self):
        """Test que requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_download_all_retorna_zip(self):
        """Test que retorna un archivo ZIP"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('Personal_Completo', response['Content-Disposition'])
