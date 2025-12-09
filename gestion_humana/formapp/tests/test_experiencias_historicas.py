"""
Tests para funcionalidad de experiencias históricas combinadas.
Verifica la integración entre experiencias del formulario y datos históricos.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal

from formapp.models import InformacionBasica, ExperienciaLaboral, CalculoExperiencia
from formapp.services import (
    obtener_experiencias_historicas,
    obtener_resumen_experiencia_historica,
    calcular_experiencia_total
)

# Intentar importar modelo histórico
try:
    from basedatosaquicali.models import ContratoHistorico
    TIENE_HISTORICO = True
except ImportError:
    TIENE_HISTORICO = False
    ContratoHistorico = None


class ObtenerExperienciasHistoricasTest(TestCase):
    """Tests para la función obtener_experiencias_historicas()"""

    def setUp(self):
        """Crear datos de prueba"""
        if TIENE_HISTORICO and ContratoHistorico:
            # Crear contratos históricos de prueba
            self.cedula_test = 12345678

            ContratoHistorico.objects.create(
                cedula=self.cedula_test,
                nombre_contratista='JUAN PEREZ',
                numero_registro=1,
                contrato='CONTRATO-001-2020',
                fecha_inicio=date(2020, 1, 1),
                fecha_fin=date(2020, 6, 30),
                dias_brutos=181,
                traslape='NO',
                explicacion_detallada='Sin traslape',
                dias_reales_contribuidos=181
            )

            ContratoHistorico.objects.create(
                cedula=self.cedula_test,
                nombre_contratista='JUAN PEREZ',
                numero_registro=2,
                contrato='CONTRATO-002-2020',
                fecha_inicio=date(2020, 7, 1),
                fecha_fin=date(2020, 12, 31),
                dias_brutos=184,
                traslape='NO',
                explicacion_detallada='Sin traslape',
                dias_reales_contribuidos=184
            )

    def test_obtener_experiencias_con_datos(self):
        """Debe retornar las experiencias históricas cuando existen"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        experiencias = obtener_experiencias_historicas(self.cedula_test)
        self.assertEqual(len(experiencias), 2)
        self.assertEqual(experiencias[0].contrato, 'CONTRATO-001-2020')
        self.assertEqual(experiencias[1].contrato, 'CONTRATO-002-2020')

    def test_obtener_experiencias_sin_datos(self):
        """Debe retornar lista vacía cuando no hay experiencias históricas"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        experiencias = obtener_experiencias_historicas(99999999)
        self.assertEqual(len(experiencias), 0)

    def test_obtener_experiencias_con_cedula_string(self):
        """Debe funcionar con cédula como string"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        experiencias = obtener_experiencias_historicas(str(self.cedula_test))
        self.assertEqual(len(experiencias), 2)

    def test_obtener_experiencias_ordenadas(self):
        """Las experiencias deben estar ordenadas por fecha_inicio"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        experiencias = obtener_experiencias_historicas(self.cedula_test)
        self.assertTrue(
            experiencias[0].fecha_inicio <= experiencias[1].fecha_inicio
        )


class ObtenerResumenExperienciaHistoricaTest(TestCase):
    """Tests para la función obtener_resumen_experiencia_historica()"""

    def setUp(self):
        """Crear datos de prueba"""
        if TIENE_HISTORICO and ContratoHistorico:
            self.cedula_test = 87654321

            # Crear 3 contratos: 6 meses + 6 meses + 1 año
            ContratoHistorico.objects.create(
                cedula=self.cedula_test,
                nombre_contratista='MARIA LOPEZ',
                numero_registro=1,
                contrato='CONT-A',
                fecha_inicio=date(2019, 1, 1),
                fecha_fin=date(2019, 6, 30),
                dias_brutos=181,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=181
            )

            ContratoHistorico.objects.create(
                cedula=self.cedula_test,
                nombre_contratista='MARIA LOPEZ',
                numero_registro=2,
                contrato='CONT-B',
                fecha_inicio=date(2019, 7, 1),
                fecha_fin=date(2019, 12, 31),
                dias_brutos=184,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=184
            )

            ContratoHistorico.objects.create(
                cedula=self.cedula_test,
                nombre_contratista='MARIA LOPEZ',
                numero_registro=3,
                contrato='CONT-C',
                fecha_inicio=date(2020, 1, 1),
                fecha_fin=date(2020, 12, 31),
                dias_brutos=366,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=366
            )

    def test_resumen_con_datos(self):
        """Debe calcular correctamente el resumen de experiencia histórica"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        resumen = obtener_resumen_experiencia_historica(self.cedula_test)

        self.assertTrue(resumen['tiene_experiencia'])
        self.assertEqual(resumen['total_contratos'], 3)
        self.assertGreater(resumen['total_dias'], 700)  # ~731 días
        self.assertIn('año', resumen['experiencia_texto'])

    def test_resumen_sin_datos(self):
        """Debe retornar resumen vacío cuando no hay experiencias"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        resumen = obtener_resumen_experiencia_historica(99999999)

        self.assertFalse(resumen['tiene_experiencia'])
        self.assertEqual(resumen['total_contratos'], 0)
        self.assertEqual(resumen['total_dias'], 0)
        self.assertEqual(resumen['experiencia_texto'], 'Sin experiencia histórica')

    def test_resumen_formato_texto(self):
        """El texto de experiencia debe tener formato legible"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        resumen = obtener_resumen_experiencia_historica(self.cedula_test)
        texto = resumen['experiencia_texto']

        # Debe contener "años" y "meses"
        self.assertIn('año', texto)
        self.assertIn('mes', texto)


class CalculoExperienciaTotalConHistoricasTest(TestCase):
    """Tests para calcular_experiencia_total() con experiencias históricas"""

    def setUp(self):
        """Crear candidato y experiencias de prueba"""
        # Crear candidato
        self.candidato = InformacionBasica.objects.create(
            cedula='11223344',
            primer_nombre='PEDRO',
            primer_apellido='GARCIA',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='10',
            numero_casa='20',
            telefono='3001234567',
            correo='pedro@test.com'
        )

        # Crear experiencia en el formulario (1 año)
        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2021, 1, 1),
            fecha_terminacion=date(2021, 12, 31),
            meses_experiencia=12,
            dias_experiencia=365,
            cargo='Desarrollador',
            cargo_anexo_11='Profesional',
            objeto_contractual='Desarrollo de software',
            funciones='Programación'
        )

        # Crear experiencias históricas si está disponible
        if TIENE_HISTORICO and ContratoHistorico:
            # Histórica 1: 6 meses
            ContratoHistorico.objects.create(
                cedula=11223344,
                nombre_contratista='PEDRO GARCIA',
                numero_registro=1,
                contrato='HIST-001',
                fecha_inicio=date(2019, 1, 1),
                fecha_fin=date(2019, 6, 30),
                dias_brutos=181,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=181
            )

            # Histórica 2: 6 meses
            ContratoHistorico.objects.create(
                cedula=11223344,
                nombre_contratista='PEDRO GARCIA',
                numero_registro=2,
                contrato='HIST-002',
                fecha_inicio=date(2019, 7, 1),
                fecha_fin=date(2019, 12, 31),
                dias_brutos=184,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=184
            )

    def test_calculo_solo_formulario_sin_historicas(self):
        """Debe calcular correctamente solo con experiencias del formulario"""
        # Crear un candidato diferente SIN experiencias históricas
        candidato_sin_hist = InformacionBasica.objects.create(
            cedula='99999999',  # Cédula que NO está en los datos históricos
            primer_nombre='LAURA',
            primer_apellido='GOMEZ',
            genero='Femenino',
            tipo_via='Calle',
            numero_via='50',
            numero_casa='60',
            telefono='3005555555',
            correo='laura@test.com'
        )

        # Crear solo experiencia del formulario
        ExperienciaLaboral.objects.create(
            informacion_basica=candidato_sin_hist,
            fecha_inicial=date(2023, 1, 1),
            fecha_terminacion=date(2023, 12, 31),
            meses_experiencia=12,
            dias_experiencia=365,
            cargo='Analista',
            cargo_anexo_11='Profesional',
            objeto_contractual='Análisis de datos',
            funciones='Análisis'
        )

        calculo = calcular_experiencia_total(candidato_sin_hist)

        self.assertIsNotNone(calculo)
        self.assertEqual(calculo.total_meses_experiencia, 12)
        self.assertGreaterEqual(calculo.total_dias_experiencia, 365)

    def test_calculo_combinado_formulario_mas_historicas(self):
        """Debe combinar experiencias del formulario + históricas"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        calculo = calcular_experiencia_total(self.candidato)

        # Debe tener más experiencia que solo el formulario
        # Formulario: 1 año + Históricas: 1 año = ~2 años
        self.assertIsNotNone(calculo)
        self.assertGreater(calculo.total_meses_experiencia, 12)
        self.assertGreater(calculo.total_dias_experiencia, 365)
        self.assertGreaterEqual(calculo.total_experiencia_anos, Decimal('1.5'))

    def test_calculo_elimina_traslapes(self):
        """Debe eliminar traslapes entre formulario e históricas"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        # Crear experiencia del formulario que traslapa con histórica
        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2019, 6, 1),  # Traslapa con HIST-001
            fecha_terminacion=date(2019, 8, 31),
            meses_experiencia=3,
            dias_experiencia=92,
            cargo='Consultor',
            cargo_anexo_11='Profesional',
            objeto_contractual='Consultoría',
            funciones='Asesoría'
        )

        calculo = calcular_experiencia_total(self.candidato)

        # El total NO debe ser la suma simple
        # Debe ser menos porque elimina traslapes
        self.assertIsNotNone(calculo)
        # Total sin traslapes < suma de todos los días
        total_dias_simple = 365 + 92 + 181 + 184  # 822 días
        self.assertLess(calculo.total_dias_experiencia, total_dias_simple)

    def test_calculo_actualiza_registro_existente(self):
        """Debe actualizar el registro de CalculoExperiencia si ya existe"""
        # Calcular primera vez
        calculo1 = calcular_experiencia_total(self.candidato)
        id_calculo1 = calculo1.pk

        # Agregar nueva experiencia
        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2022, 1, 1),
            fecha_terminacion=date(2022, 6, 30),
            meses_experiencia=6,
            dias_experiencia=181,
            cargo='Analista',
            cargo_anexo_11='Profesional',
            objeto_contractual='Análisis',
            funciones='Análisis de datos'
        )

        # Calcular segunda vez
        calculo2 = calcular_experiencia_total(self.candidato)

        # Debe ser el mismo registro (update_or_create)
        self.assertEqual(calculo1.pk, calculo2.pk)
        # Pero con más experiencia
        self.assertGreater(calculo2.total_dias_experiencia, calculo1.total_dias_experiencia)


class ApplicantDetailViewConHistoricasTest(TestCase):
    """Tests para la vista de detalle con experiencias históricas"""

    def setUp(self):
        """Crear usuario, candidato y datos de prueba"""
        # Crear usuario admin
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )

        # Crear candidato
        self.candidato = InformacionBasica.objects.create(
            cedula='55667788',
            primer_nombre='ANA',
            primer_apellido='MARTINEZ',
            genero='Femenino',
            tipo_via='Carrera',
            numero_via='15',
            numero_casa='30',
            telefono='3009876543',
            correo='ana@test.com'
        )

        # Crear experiencias históricas si está disponible
        if TIENE_HISTORICO and ContratoHistorico:
            ContratoHistorico.objects.create(
                cedula=55667788,
                nombre_contratista='ANA MARTINEZ',
                numero_registro=1,
                contrato='HIST-2020-001',
                fecha_inicio=date(2020, 1, 1),
                fecha_fin=date(2020, 12, 31),
                dias_brutos=366,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=366
            )

        self.client = Client()

    def test_vista_requiere_autenticacion(self):
        """La vista de detalle debe requerir autenticación"""
        response = self.client.get(f'/formapp/admin/applicants/{self.candidato.pk}/')
        self.assertEqual(response.status_code, 302)  # Redirect a login

    def test_vista_con_usuario_autenticado(self):
        """La vista debe cargar correctamente con usuario autenticado"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/formapp/admin/applicants/{self.candidato.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_contexto_contiene_experiencias_historicas(self):
        """El contexto debe incluir experiencias_historicas"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/formapp/admin/applicants/{self.candidato.pk}/')

        self.assertIn('experiencias_historicas', response.context)
        experiencias = response.context['experiencias_historicas']
        self.assertEqual(len(experiencias), 1)

    def test_contexto_contiene_resumen_historico(self):
        """El contexto debe incluir resumen_historico"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/formapp/admin/applicants/{self.candidato.pk}/')

        self.assertIn('resumen_historico', response.context)
        resumen = response.context['resumen_historico']
        self.assertEqual(resumen['total_contratos'], 1)
        self.assertTrue(resumen['tiene_experiencia'])

    def test_template_muestra_seccion_historica(self):
        """El template debe renderizar la sección de experiencias históricas"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/formapp/admin/applicants/{self.candidato.pk}/')

        self.assertContains(response, 'Experiencia Histórica')
        self.assertContains(response, 'HIST-2020-001')
        self.assertContains(response, 'Contratos 2017-2025')


class IntegracionExperienciasTest(TestCase):
    """Tests de integración end-to-end"""

    def setUp(self):
        """Crear escenario completo de prueba"""
        # Crear candidato
        self.candidato = InformacionBasica.objects.create(
            cedula='99887766',
            primer_nombre='CARLOS',
            primer_apellido='RODRIGUEZ',
            genero='Masculino',
            tipo_via='Avenida',
            numero_via='20',
            numero_casa='40',
            telefono='3007654321',
            correo='carlos@test.com'
        )

        # Experiencia formulario: 2 contratos de 6 meses cada uno (2021)
        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2021, 1, 1),
            fecha_terminacion=date(2021, 6, 30),
            meses_experiencia=6,
            dias_experiencia=181,
            cargo='Desarrollador Junior',
            cargo_anexo_11='Profesional',
            objeto_contractual='Desarrollo',
            funciones='Programación'
        )

        ExperienciaLaboral.objects.create(
            informacion_basica=self.candidato,
            fecha_inicial=date(2021, 7, 1),
            fecha_terminacion=date(2021, 12, 31),
            meses_experiencia=6,
            dias_experiencia=184,
            cargo='Desarrollador',
            cargo_anexo_11='Profesional',
            objeto_contractual='Desarrollo',
            funciones='Programación'
        )

        # Experiencias históricas: 2 contratos de 1 año cada uno (2019-2020)
        if TIENE_HISTORICO and ContratoHistorico:
            ContratoHistorico.objects.create(
                cedula=99887766,
                nombre_contratista='CARLOS RODRIGUEZ',
                numero_registro=1,
                contrato='HIST-2019',
                fecha_inicio=date(2019, 1, 1),
                fecha_fin=date(2019, 12, 31),
                dias_brutos=365,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=365
            )

            ContratoHistorico.objects.create(
                cedula=99887766,
                nombre_contratista='CARLOS RODRIGUEZ',
                numero_registro=2,
                contrato='HIST-2020',
                fecha_inicio=date(2020, 1, 1),
                fecha_fin=date(2020, 12, 31),
                dias_brutos=366,
                traslape='NO',
                explicacion_detallada='',
                dias_reales_contribuidos=366
            )

    def test_integracion_completa(self):
        """Test de integración completa del flujo"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        # 1. Verificar experiencias del formulario
        exp_formulario = self.candidato.experiencias_laborales.all()
        self.assertEqual(exp_formulario.count(), 2)

        # 2. Verificar experiencias históricas
        exp_historicas = obtener_experiencias_historicas(self.candidato.cedula)
        self.assertEqual(len(exp_historicas), 2)

        # 3. Calcular experiencia total combinada
        calculo = calcular_experiencia_total(self.candidato)

        # 4. Verificar que el cálculo combina correctamente
        # Formulario: 1 año (2021) + Históricas: 2 años (2019-2020) = 3 años totales
        self.assertIsNotNone(calculo)
        self.assertGreaterEqual(calculo.total_experiencia_anos, Decimal('2.9'))  # ~3 años
        self.assertGreaterEqual(calculo.total_meses_experiencia, 35)  # ~36 meses
        self.assertIn('año', calculo.anos_y_meses_experiencia)

        # 5. Verificar que no hay traslapes (todos son secuenciales)
        dias_esperados = 365 + 366 + 181 + 184  # ~1096 días
        # Puede variar ligeramente por la fórmula de cálculo
        self.assertGreaterEqual(calculo.total_dias_experiencia, dias_esperados - 10)
        self.assertLessEqual(calculo.total_dias_experiencia, dias_esperados + 10)

    def test_resumen_experiencia_historica_completo(self):
        """Verificar resumen de experiencia histórica"""
        if not TIENE_HISTORICO:
            self.skipTest("basedatosaquicali no está disponible")

        resumen = obtener_resumen_experiencia_historica(self.candidato.cedula)

        self.assertTrue(resumen['tiene_experiencia'])
        self.assertEqual(resumen['total_contratos'], 2)
        self.assertGreaterEqual(resumen['total_dias'], 730)  # ~2 años
        self.assertIn('año', resumen['experiencia_texto'])
