"""
Tests específicos para los nuevos campos de archivo en Posgrado y Especialización.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from formapp.forms import PosgradoForm, EspecializacionForm
from formapp.models import InformacionBasica, Posgrado, Especializacion


class NuevosCamposPosgradoTest(TestCase):
    """Tests para verificar que los nuevos campos de archivo funcionan en Posgrado"""

    def test_posgrado_con_archivo_valido(self):
        """Test que el campo acta_grado_diploma acepta archivos válidos"""
        diploma_pdf = SimpleUploadedFile(
            'diploma_maestria.pdf',
            b'%PDF-1.4 contenido del diploma',
            content_type='application/pdf'
        )

        form = PosgradoForm(
            data={
                'nombre_posgrado': 'Maestría en Ingeniería de Software',
                'universidad': 'Universidad de los Andes',
                'fecha_terminacion': date(2023, 6, 15),
            },
            files={'acta_grado_diploma': diploma_pdf}
        )

        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_posgrado_sin_archivo_con_datos_falla(self):
        """Test que el archivo es obligatorio cuando se llenan otros campos"""
        form = PosgradoForm(
            data={
                'nombre_posgrado': 'Maestría en Ingeniería',
                'universidad': 'Universidad Nacional',
                'fecha_terminacion': date(2023, 6, 15),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('acta_grado_diploma', form.errors)

    def test_posgrado_con_imagen_jpg_valida(self):
        """Test que acepta archivos JPG válidos"""
        diploma_jpg = SimpleUploadedFile(
            'diploma.jpg',
            b'\xff\xd8\xff\xe0\x00\x10JFIF contenido',
            content_type='image/jpeg'
        )

        form = PosgradoForm(
            data={
                'nombre_posgrado': 'Doctorado en Computación',
                'universidad': 'MIT',
                'fecha_terminacion': date(2024, 5, 20),
            },
            files={'acta_grado_diploma': diploma_jpg}
        )

        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_guardar_posgrado_con_archivo(self):
        """Test que se puede guardar un posgrado con archivo en la base de datos"""
        persona = InformacionBasica.objects.create(
            primer_apellido='GARCIA',
            segundo_apellido='LOPEZ',
            primer_nombre='PEDRO',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='10',
            numero_casa='20-30',
            telefono='3001234567',
            correo='pedro@test.com',
        )

        diploma_pdf = SimpleUploadedFile(
            'diploma_posgrado.pdf',
            b'%PDF-1.4 test content',
            content_type='application/pdf'
        )

        posgrado = Posgrado.objects.create(
            informacion_basica=persona,
            nombre_posgrado='MBA',
            universidad='Harvard',
            fecha_terminacion=date(2022, 12, 1),
            acta_grado_diploma=diploma_pdf
        )

        self.assertIsNotNone(posgrado.id)
        self.assertTrue(posgrado.acta_grado_diploma)


class NuevosCamposEspecializacionTest(TestCase):
    """Tests para verificar que los nuevos campos de archivo funcionan en Especialización"""

    def test_especializacion_con_archivo_valido(self):
        """Test que el campo acta_grado_diploma acepta archivos válidos"""
        diploma_pdf = SimpleUploadedFile(
            'diploma_especializacion.pdf',
            b'%PDF-1.4 contenido del diploma',
            content_type='application/pdf'
        )

        form = EspecializacionForm(
            data={
                'nombre_especializacion': 'Especialización en Gerencia de Proyectos',
                'universidad': 'Universidad Javeriana',
                'fecha_terminacion': date(2023, 11, 30),
            },
            files={'acta_grado_diploma': diploma_pdf}
        )

        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_especializacion_sin_archivo_con_datos_falla(self):
        """Test que el archivo es obligatorio cuando se llenan otros campos"""
        form = EspecializacionForm(
            data={
                'nombre_especializacion': 'Especialización en Marketing',
                'universidad': 'Universidad del Rosario',
                'fecha_terminacion': date(2023, 8, 15),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('acta_grado_diploma', form.errors)

    def test_especializacion_con_imagen_png_valida(self):
        """Test que acepta archivos PNG válidos"""
        diploma_png = SimpleUploadedFile(
            'diploma.png',
            b'\x89PNG\r\n\x1a\n contenido',
            content_type='image/png'
        )

        form = EspecializacionForm(
            data={
                'nombre_especializacion': 'Especialización en Finanzas',
                'universidad': 'EAFIT',
                'fecha_terminacion': date(2024, 3, 15),
            },
            files={'acta_grado_diploma': diploma_png}
        )

        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_guardar_especializacion_con_archivo(self):
        """Test que se puede guardar una especialización con archivo en la base de datos"""
        persona = InformacionBasica.objects.create(
            primer_apellido='MARTINEZ',
            segundo_apellido='RODRIGUEZ',
            primer_nombre='ANA',
            cedula='9876543210',
            genero='Femenino',
            tipo_via='Carrera',
            numero_via='15',
            numero_casa='30-45',
            telefono='3109876543',
            correo='ana@test.com',
        )

        diploma_pdf = SimpleUploadedFile(
            'diploma_especializacion.pdf',
            b'%PDF-1.4 test content',
            content_type='application/pdf'
        )

        especializacion = Especializacion.objects.create(
            informacion_basica=persona,
            nombre_especializacion='Especialización en Derecho Laboral',
            universidad='Universidad Externado',
            fecha_terminacion=date(2023, 7, 20),
            acta_grado_diploma=diploma_pdf
        )

        self.assertIsNotNone(especializacion.id)
        self.assertTrue(especializacion.acta_grado_diploma)
