"""
Tests para los modelos de la aplicación formapp.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from decimal import Decimal

from formapp.models import (
    InformacionBasica,
    ExperienciaLaboral,
    InformacionAcademica,
    Posgrado,
    Especializacion,
    CalculoExperiencia,
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales,
)


class InformacionBasicaModelTest(TestCase):
    """Tests para el modelo InformacionBasica"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_data = {
            'primer_apellido': 'PEREZ',
            'segundo_apellido': 'GOMEZ',
            'primer_nombre': 'JUAN',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '10',
            'numero_casa': '20-30',
            'telefono': '3001234567',
            'correo': 'juan.perez@example.com',
        }

    def test_crear_informacion_basica_valida(self):
        """Test crear un registro válido de InformacionBasica"""
        info = InformacionBasica.objects.create(**self.valid_data)
        self.assertIsNotNone(info.id)
        self.assertEqual(info.cedula, '1234567890')
        self.assertEqual(info.nombre_completo, 'PEREZ GOMEZ JUAN')

    def test_cedula_unica(self):
        """Test que la cédula debe ser única"""
        InformacionBasica.objects.create(**self.valid_data)

        # Intentar crear otro registro con la misma cédula
        with self.assertRaises(IntegrityError):
            InformacionBasica.objects.create(**self.valid_data)

    def test_campos_obligatorios(self):
        """Test que los campos obligatorios no pueden estar vacíos"""
        # Crear instancia sin cédula
        info = InformacionBasica(
            primer_apellido='TEST',
            segundo_apellido='APELLIDO',
            primer_nombre='NOMBRE',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='10',
            numero_casa='20',
            telefono='3001234567',
            correo='test@test.com',
        )
        # Debe fallar validación por falta de cédula
        with self.assertRaises(ValidationError):
            info.full_clean()

    def test_campos_opcionales(self):
        """Test que los campos opcionales pueden estar vacíos"""
        info = InformacionBasica.objects.create(
            **self.valid_data,
            perfil=None,
            area_del_conocimiento=None,
            profesion=None,
            contrato=None,
            observacion=None,
        )
        self.assertIsNotNone(info.id)
        self.assertIsNone(info.perfil)

    def test_str_method(self):
        """Test del método __str__"""
        info = InformacionBasica.objects.create(**self.valid_data)
        self.assertEqual(str(info), 'PEREZ GOMEZ JUAN')

    def test_genero_choices(self):
        """Test que género acepta valores válidos"""
        for genero_choice in ['Femenino', 'Masculino', 'Otro']:
            data = self.valid_data.copy()
            data['cedula'] = f'123456789{genero_choice[0]}'
            data['genero'] = genero_choice
            info = InformacionBasica.objects.create(**data)
            self.assertEqual(info.genero, genero_choice)


class ExperienciaLaboralModelTest(TestCase):
    """Tests para el modelo ExperienciaLaboral y cálculos automáticos"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            primer_apellido='LOPEZ',
            segundo_apellido='GARCIA',
            primer_nombre='MARIA',
            cedula='9876543210',
            genero='Femenino',
            tipo_via='Carrera',
            numero_via='15',
            numero_casa='30-45',
            telefono='3109876543',
            correo='maria.lopez@example.com',
        )

    def test_crear_experiencia_laboral(self):
        """Test crear experiencia laboral"""
        exp = ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Ingeniero',
            objeto_contractual='Desarrollo de software',
            funciones='Programación y diseño',
        )
        self.assertIsNotNone(exp.id)
        self.assertEqual(exp.cargo, 'Ingeniero')

    def test_calculo_meses_12_meses_exactos(self):
        """Test cálculo de experiencia: 12 meses exactos"""
        fecha_inicial = date(2020, 1, 1)
        fecha_terminacion = date(2021, 1, 1)

        # Calcular manualmente
        anos = fecha_terminacion.year - fecha_inicial.year
        meses = fecha_terminacion.month - fecha_inicial.month
        dias = fecha_terminacion.day - fecha_inicial.day

        if dias < 0:
            meses -= 1
        if meses < 0:
            anos -= 1
            meses += 12

        total_meses_esperado = (anos * 12) + meses
        self.assertEqual(total_meses_esperado, 12)

    def test_calculo_meses_6_meses_exactos(self):
        """Test cálculo de experiencia: 6 meses exactos"""
        fecha_inicial = date(2020, 1, 1)
        fecha_terminacion = date(2020, 7, 1)

        anos = fecha_terminacion.year - fecha_inicial.year
        meses = fecha_terminacion.month - fecha_inicial.month
        total_meses_esperado = (anos * 12) + meses

        self.assertEqual(total_meses_esperado, 6)

    def test_calculo_dias_totales(self):
        """Test cálculo de días totales calendario"""
        fecha_inicial = date(2020, 1, 1)
        fecha_terminacion = date(2020, 1, 31)

        delta = fecha_terminacion - fecha_inicial
        dias_esperados = delta.days

        self.assertEqual(dias_esperados, 30)

    def test_cargo_anexo_11_default(self):
        """Test que cargo_anexo_11 tiene valor por defecto"""
        exp = ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2020, 6, 1),
            meses_experiencia=5,
            dias_experiencia=152,
            cargo='Técnico',
            objeto_contractual='Soporte técnico',
            funciones='Mantenimiento',
        )
        self.assertEqual(exp.cargo_anexo_11, 'Profesional')

    def test_relacion_con_informacion_basica(self):
        """Test relación ForeignKey con InformacionBasica"""
        ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2019, 1, 1),
            fecha_terminacion=date(2020, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Analista',
            objeto_contractual='Análisis de datos',
            funciones='Reportes',
        )

        self.assertEqual(self.persona.experiencias_laborales.count(), 1)

    def test_str_method(self):
        """Test del método __str__"""
        exp = ExperienciaLaboral.objects.create(
            informacion_basica=self.persona,
            fecha_inicial=date(2020, 1, 1),
            fecha_terminacion=date(2021, 1, 1),
            meses_experiencia=12,
            dias_experiencia=366,
            cargo='Developer',
            objeto_contractual='Dev',
            funciones='Code',
        )
        self.assertEqual(str(exp), 'Developer en 9876543210')


class CalculoExperienciaModelTest(TestCase):
    """Tests para el modelo CalculoExperiencia"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            primer_apellido='RUIZ',
            segundo_apellido='MARTINEZ',
            primer_nombre='CARLOS',
            cedula='1122334455',
            genero='Masculino',
            tipo_via='Avenida',
            numero_via='5',
            numero_casa='10-20',
            telefono='3201122334',
            correo='carlos.ruiz@example.com',
        )

    def test_crear_calculo_experiencia(self):
        """Test crear registro de cálculo de experiencia"""
        calculo = CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=24,
            total_dias_experiencia=730,
            total_experiencia_anos=Decimal('2.00'),
            anos_y_meses_experiencia='2 años y 0 meses',
        )
        self.assertIsNotNone(calculo.id)
        self.assertEqual(calculo.total_meses_experiencia, 24)

    def test_relacion_one_to_one(self):
        """Test que la relación es 1-1 con InformacionBasica"""
        CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=12,
            total_dias_experiencia=365,
            total_experiencia_anos=Decimal('1.00'),
            anos_y_meses_experiencia='1 años y 0 meses',
        )

        # Intentar crear otro cálculo para la misma persona
        with self.assertRaises(IntegrityError):
            CalculoExperiencia.objects.create(
                informacion_basica=self.persona,
                total_meses_experiencia=24,
                total_dias_experiencia=730,
                total_experiencia_anos=Decimal('2.00'),
                anos_y_meses_experiencia='2 años y 0 meses',
            )

    def test_conversion_meses_a_anos(self):
        """Test conversión de meses a años (decimal)"""
        meses = 30  # 2.5 años
        anos_decimal = round(meses / 12, 2)
        self.assertEqual(anos_decimal, Decimal('2.50'))

    def test_formato_anos_y_meses(self):
        """Test formato legible de años y meses"""
        total_meses = 29
        anos = total_meses // 12
        meses_restantes = total_meses % 12
        texto = f"{anos} años y {meses_restantes} meses"

        self.assertEqual(texto, "2 años y 5 meses")

    def test_str_method(self):
        """Test del método __str__"""
        calculo = CalculoExperiencia.objects.create(
            informacion_basica=self.persona,
            total_meses_experiencia=12,
            total_dias_experiencia=365,
            total_experiencia_anos=Decimal('1.00'),
            anos_y_meses_experiencia='1 años y 0 meses',
        )
        self.assertEqual(str(calculo), 'Cálculo de experiencia para 1122334455')


class InformacionAcademicaModelTest(TestCase):
    """Tests para el modelo InformacionAcademica"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            primer_apellido='TORRES',
            segundo_apellido='MARTINEZ',
            primer_nombre='ANA',
            cedula='5544332211',
            genero='Femenino',
            tipo_via='Calle',
            numero_via='20',
            numero_casa='15-30',
            telefono='3105544332',
            correo='ana.torres@example.com',
        )

    def test_crear_informacion_academica(self):
        """Test crear información académica"""
        academica = InformacionAcademica.objects.create(
            informacion_basica=self.persona,
            tarjeta_profesional='Tarjeta Profesional',
            profesion='Ingeniera de Sistemas',
            universidad='Universidad Nacional',
            numero_tarjeta_resolucion='12345',
            fecha_grado=date(2015, 12, 15),
        )
        self.assertIsNotNone(academica.id)
        self.assertEqual(academica.profesion, 'Ingeniera de Sistemas')

    def test_tarjeta_profesional_choices(self):
        """Test choices de tarjeta profesional"""
        choices = ['Tarjeta Profesional', 'Resolución', 'No Aplica']
        for choice in choices:
            academica = InformacionAcademica.objects.create(
                informacion_basica=self.persona,
                tarjeta_profesional=choice,
                profesion=f'Profesion {choice}',
                universidad='Universidad',
                fecha_grado=date(2015, 1, 1),
            )
            self.assertEqual(academica.tarjeta_profesional, choice)

    def test_relacion_con_informacion_basica(self):
        """Test relación ForeignKey con InformacionBasica"""
        InformacionAcademica.objects.create(
            informacion_basica=self.persona,
            tarjeta_profesional='No Aplica',
            profesion='Técnico',
            universidad='SENA',
            fecha_grado=date(2010, 6, 1),
        )

        self.assertEqual(self.persona.formacion_academica.count(), 1)

    def test_str_method(self):
        """Test del método __str__"""
        academica = InformacionAcademica.objects.create(
            informacion_basica=self.persona,
            tarjeta_profesional='Tarjeta Profesional',
            profesion='Abogada',
            universidad='Universidad de Cali',
            fecha_grado=date(2018, 12, 1),
        )
        self.assertEqual(str(academica), 'Abogada de 5544332211')


class PosgradoModelTest(TestCase):
    """Tests para el modelo Posgrado"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            primer_apellido='SANCHEZ',
            segundo_apellido='RODRIGUEZ',
            primer_nombre='PEDRO',
            cedula='6677889900',
            genero='Masculino',
            tipo_via='Carrera',
            numero_via='50',
            numero_casa='100-20',
            telefono='3206677889',
            correo='pedro.sanchez@example.com',
        )

    def test_crear_posgrado(self):
        """Test crear posgrado"""
        posgrado = Posgrado.objects.create(
            informacion_basica=self.persona,
            nombre_posgrado='Maestría en Ingeniería',
            universidad='Universidad de los Andes',
            fecha_terminacion=date(2020, 6, 15),
        )
        self.assertIsNotNone(posgrado.id)
        self.assertEqual(posgrado.nombre_posgrado, 'Maestría en Ingeniería')

    def test_multiple_posgrados(self):
        """Test que una persona puede tener múltiples posgrados"""
        Posgrado.objects.create(
            informacion_basica=self.persona,
            nombre_posgrado='Maestría en Admin',
            universidad='Universidad 1',
            fecha_terminacion=date(2018, 1, 1),
        )
        Posgrado.objects.create(
            informacion_basica=self.persona,
            nombre_posgrado='Doctorado en Física',
            universidad='Universidad 2',
            fecha_terminacion=date(2022, 1, 1),
        )

        self.assertEqual(self.persona.posgrados.count(), 2)

    def test_str_method(self):
        """Test del método __str__"""
        posgrado = Posgrado.objects.create(
            informacion_basica=self.persona,
            nombre_posgrado='MBA',
            universidad='Harvard',
            fecha_terminacion=date(2019, 5, 1),
        )
        self.assertEqual(str(posgrado), 'MBA de 6677889900')


class EspecializacionModelTest(TestCase):
    """Tests para el modelo Especializacion"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            primer_apellido='MARTINEZ',
            segundo_apellido='GONZALEZ',
            primer_nombre='LAURA',
            cedula='9988776655',
            genero='Femenino',
            tipo_via='Avenida',
            numero_via='30',
            numero_casa='50-60',
            telefono='3109988776',
            correo='laura.martinez@example.com',
        )

    def test_crear_especializacion(self):
        """Test crear especialización"""
        esp = Especializacion.objects.create(
            informacion_basica=self.persona,
            nombre_especializacion='Especialización en Gerencia',
            universidad='Universidad Javeriana',
            fecha_terminacion=date(2021, 11, 30),
        )
        self.assertIsNotNone(esp.id)
        self.assertEqual(esp.nombre_especializacion, 'Especialización en Gerencia')

    def test_multiple_especializaciones(self):
        """Test múltiples especializaciones"""
        Especializacion.objects.create(
            informacion_basica=self.persona,
            nombre_especializacion='Esp 1',
            universidad='Uni 1',
            fecha_terminacion=date(2020, 1, 1),
        )
        Especializacion.objects.create(
            informacion_basica=self.persona,
            nombre_especializacion='Esp 2',
            universidad='Uni 2',
            fecha_terminacion=date(2021, 1, 1),
        )

        self.assertEqual(self.persona.especializaciones.count(), 2)

    def test_str_method(self):
        """Test del método __str__"""
        esp = Especializacion.objects.create(
            informacion_basica=self.persona,
            nombre_especializacion='Esp Marketing',
            universidad='ICESI',
            fecha_terminacion=date(2022, 6, 1),
        )
        self.assertEqual(str(esp), 'Esp Marketing de 9988776655')
