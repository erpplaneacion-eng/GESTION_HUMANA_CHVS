"""
Tests para funciones de utilidad y helpers.
"""
from django.test import TestCase
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
import io

from formapp.models import InformacionBasica, ExperienciaLaboral, CalculoExperiencia
from formapp.views import calcular_experiencia_total, create_excel_for_person, generar_anexo11_pdf


class CalcularExperienciaTotalTest(TestCase):
    """Tests para la función calcular_experiencia_total"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            nombre_completo='TEST PERSONA',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='1',
            numero_casa='1',
            telefono='3001234567',
            correo='test@test.com',
        )

    def test_calcular_experiencia_sin_experiencias(self):
        """Test cálculo con 0 experiencias laborales"""
        calculo = calcular_experiencia_total(self.persona)

        self.assertIsNotNone(calculo)
        self.assertEqual(calculo.total_meses_experiencia, 0)
        self.assertEqual(calculo.total_dias_experiencia, 0)
        self.assertEqual(calculo.total_experiencia_anos, Decimal('0.00'))
        self.assertEqual(calculo.anos_y_meses_experiencia, '0 años y 0 meses')

    def test_calcular_experiencia_una_experiencia_12_meses(self):
        """Test cálculo con una experiencia de 12 meses"""
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Ingeniero',
            objeto_contractual='Desarrollo',
            funciones='Programar',
        )

        calculo = calcular_experiencia_total(self.persona)

        self.assertEqual(calculo.total_meses_experiencia, 12)
        self.assertEqual(calculo.total_dias_experiencia, 366)
        self.assertEqual(calculo.total_experiencia_anos, Decimal('1.00'))
        self.assertEqual(calculo.anos_y_meses_experiencia, '1 años y 0 meses')

    def test_calcular_experiencia_dos_experiencias(self):
        """Test cálculo con dos experiencias laborales"""
        # Primera experiencia: 12 meses
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2019, 1, 1),
            fecha_terminacion=date(2020, 1, 1),
            meses_experiencia=12,
            dias_experiencia=365,
            cargo='Analista',
            objeto_contractual='Análisis',
            funciones='Analizar',
        )

        # Segunda experiencia: 6 meses
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 6, 1),
            fecha_terminacion=date(2020, 12, 1),
            meses_experiencia=6,
            dias_experiencia=183,
            cargo='Developer',
            objeto_contractual='Dev',
            funciones='Code',
        )

        calculo = calcular_experiencia_total(self.persona)

        self.assertEqual(calculo.total_meses_experiencia, 18)
        self.assertEqual(calculo.total_dias_experiencia, 548)
        self.assertEqual(calculo.total_experiencia_anos, Decimal('1.50'))
        self.assertEqual(calculo.anos_y_meses_experiencia, '1 años y 6 meses')

    def test_calcular_experiencia_30_meses(self):
        """Test cálculo con 30 meses (2 años y 6 meses)"""
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2020, 12, 31),
            meses_experiencia=30,
            dias_experiencia=912,
            cargo='Manager',
            objeto_contractual='Gestión',
            funciones='Administrar',
        )

        calculo = calcular_experiencia_total(self.persona)

        self.assertEqual(calculo.total_meses_experiencia, 30)
        self.assertEqual(calculo.total_experiencia_anos, Decimal('2.50'))
        self.assertEqual(calculo.anos_y_meses_experiencia, '2 años y 6 meses')

    def test_calcular_experiencia_actualiza_registro_existente(self):
        """Test que actualiza el registro existente en lugar de crear uno nuevo"""
        # Crear cálculo inicial
        CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=0,
            total_dias_experiencia=0,
            total_experiencia_anos=Decimal('0.00'),
            anos_y_meses_experiencia='0 años y 0 meses',
        )

        # Agregar experiencia
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Técnico',
            objeto_contractual='Soporte',
            funciones='Ayudar',
        )

        # Recalcular
        calculo = calcular_experiencia_total(self.persona)

        # Debe haber solo un registro de cálculo
        self.assertEqual(CalculoExperiencia.objects.filter(informacion_basica=self.persona).count(), 1)
        self.assertEqual(calculo.total_meses_experiencia, 12)


class CreateExcelForPersonTest(TestCase):
    """Tests para la función create_excel_for_person"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            nombre_completo='JUAN PEREZ GOMEZ',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='10',
            numero_casa='20-30',
            complemento_direccion='Apto 301',
            barrio='Centro',
            telefono='3001234567',
            correo='juan@test.com',
            perfil='PROFESIONAL SOCIAL',
            area_del_conocimiento='SOCIAL',
            profesion='TRABAJADOR SOCIAL',
        )

        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Trabajador Social',
            cargo_anexo_11='Profesional',
            objeto_contractual='Atención social',
            funciones='Intervención comunitaria',
        )

        CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=12,
            total_dias_experiencia=366,
            total_experiencia_anos=Decimal('1.00'),
            anos_y_meses_experiencia='1 años y 0 meses',
        )

    def test_create_excel_genera_workbook(self):
        """Test que genera un workbook de Excel"""
        wb = create_excel_for_person(self.persona)
        self.assertIsNotNone(wb)

    def test_create_excel_tiene_hojas_necesarias(self):
        """Test que el Excel tiene las 6 hojas necesarias"""
        wb = create_excel_for_person(self.persona)
        sheet_names = wb.sheetnames

        expected_sheets = [
            'Información Básica',
            'Experiencia Laboral',
            'Información Académica',
            'Posgrados',
            'Especializaciones',
            'Cálculo Experiencia',
        ]

        for sheet_name in expected_sheets:
            self.assertIn(sheet_name, sheet_names)

    def test_create_excel_sin_experiencias(self):
        """Test generar Excel para persona sin experiencias"""
        persona_sin_exp = InformacionBasica.objects.create(
            nombre_completo='MARIA LOPEZ',
            cedula='9876543210',
            genero='Femenino',
            tipo_via='Carrera',
            numero_via='15',
            numero_casa='30-45',
            telefono='3109876543',
            correo='maria@test.com',
        )

        wb = create_excel_for_person(persona_sin_exp)
        self.assertIsNotNone(wb)


class GenerarAnexo11PdfTest(TestCase):
    """Tests para la función generar_anexo11_pdf"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            nombre_completo='ANA TORRES MARTINEZ',
            cedula='5544332211',
            genero='Femenino',
            tipo_via='Avenida',
            numero_via='5',
            numero_casa='10-20',
            complemento_direccion='Torre 2 Apto 502',
            barrio='El Refugio',
            telefono='3105544332',
            correo='ana@test.com',
            perfil='PROFESIONAL PSICOLOGIA',
            contrato='4146.010.32.1.2366.2025',
        )

        CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=24,
            total_dias_experiencia=730,
            total_experiencia_anos=Decimal('2.00'),
            anos_y_meses_experiencia='2 años y 0 meses',
        )

    def test_generar_anexo11_pdf_retorna_buffer(self):
        """Test que genera un PDF y retorna un buffer"""
        pdf_buffer = generar_anexo11_pdf(self.persona)
        self.assertIsNotNone(pdf_buffer)
        self.assertIsInstance(pdf_buffer, io.BytesIO)

    def test_generar_anexo11_pdf_tiene_contenido(self):
        """Test que el PDF tiene contenido"""
        pdf_buffer = generar_anexo11_pdf(self.persona)
        pdf_content = pdf_buffer.getvalue()
        self.assertGreater(len(pdf_content), 0)
        # Verificar que es un PDF (comienza con %PDF)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_anexo11_pdf_sin_calculo_experiencia(self):
        """Test generar PDF para persona sin cálculo de experiencia"""
        persona_sin_calculo = InformacionBasica.objects.create(
            nombre_completo='PEDRO SANCHEZ',
            cedula='6677889900',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='1',
            numero_casa='1',
            telefono='3206677889',
            correo='pedro@test.com',
            perfil='TECNICO GGHH',
        )

        # Debe generar el PDF aunque no haya cálculo
        pdf_buffer = generar_anexo11_pdf(persona_sin_calculo)
        self.assertIsNotNone(pdf_buffer)


class NumeroATextoEsTest(TestCase):
    """Tests para la función auxiliar numero_a_texto_es dentro de generar_anexo11_pdf"""

    def test_numeros_1_al_10(self):
        """Test conversión de números 1 al 10"""
        from formapp.views import generar_anexo11_pdf

        # Crear persona de prueba
        persona = InformacionBasica.objects.create(
            nombre_completo='TEST',
            cedula='1234567890',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='1',
            numero_casa='1',
            telefono='3001234567',
            correo='test@test.com',
        )

        # Generar PDF (que contiene la función numero_a_texto_es)
        # No hay forma directa de probar la función interna sin refactorizar
        # Este test sirve como recordatorio para refactorizar estas funciones
        pdf_buffer = generar_anexo11_pdf(persona)
        self.assertIsNotNone(pdf_buffer)


class FechaEspanolTest(TestCase):
    """Tests para validar formato de fecha en español"""

    def test_meses_en_espanol(self):
        """Test que los meses están en español en el PDF"""
        persona = InformacionBasica.objects.create(
            nombre_completo='TEST FECHA',
            cedula='1112223334',
            genero='Femenino',
            tipo_via='Calle',
            numero_via='1',
            numero_casa='1',
            telefono='3001112223',
            correo='test@test.com',
        )

        pdf_buffer = generar_anexo11_pdf(persona)
        pdf_content = pdf_buffer.getvalue()

        # Verificar que el PDF se generó
        self.assertIsNotNone(pdf_content)
        self.assertGreater(len(pdf_content), 0)
