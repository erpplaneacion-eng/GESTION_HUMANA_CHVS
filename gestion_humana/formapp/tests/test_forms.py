"""
Tests para los formularios de la aplicación formapp.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
import io

from formapp.forms import (
    InformacionBasicaPublicForm,
    InformacionBasicaForm,
    ExperienciaLaboralForm,
    InformacionAcademicaForm,
    PosgradoForm,
    EspecializacionForm,
    DocumentosIdentidadForm,
    AntecedentesForm,
    AnexosAdicionalesForm,
)
from formapp.models import InformacionBasica, ExperienciaLaboral


class InformacionBasicaPublicFormTest(TestCase):
    """Tests para InformacionBasicaPublicForm"""

    def setUp(self):
        """Configuración inicial"""
        self.valid_data = {
            'primer_apellido': 'GOMEZ',
            'segundo_apellido': 'LOPEZ',
            'primer_nombre': 'JUAN',
            'segundo_nombre': 'CARLOS',
            'cedula': '1234567890',
            'genero': 'Masculino',
            'tipo_via': 'Calle',
            'numero_via': '10',
            'numero_casa': '20-30',
            'telefono': '3001234567',
            'correo': 'juan.gomez@example.com',
        }

    def test_formulario_valido(self):
        """Test formulario con datos válidos"""
        form = InformacionBasicaPublicForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_nombre_completo_se_genera_automaticamente(self):
        """Test que nombre_completo se genera automáticamente en mayúsculas"""
        form = InformacionBasicaPublicForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.nombre_completo, 'GOMEZ LOPEZ JUAN CARLOS')

    def test_nombre_completo_mayusculas(self):
        """Test que el nombre se convierte a mayúsculas"""
        data = self.valid_data.copy()
        data['primer_apellido'] = 'gomez'
        data['primer_nombre'] = 'juan'
        form = InformacionBasicaPublicForm(data=data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.nombre_completo, 'GOMEZ LOPEZ JUAN CARLOS')

    def test_cedula_debe_ser_numerica(self):
        """Test que cédula debe contener solo números"""
        data = self.valid_data.copy()
        data['cedula'] = '123ABC456'
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)

    def test_cedula_longitud_minima(self):
        """Test que cédula debe tener al menos 5 dígitos"""
        data = self.valid_data.copy()
        data['cedula'] = '1234'
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)

    def test_cedula_longitud_maxima(self):
        """Test que cédula debe tener máximo 10 dígitos"""
        data = self.valid_data.copy()
        data['cedula'] = '12345678901'  # 11 dígitos
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)

    def test_cedula_duplicada(self):
        """Test que no se puede crear registro con cédula duplicada"""
        # Crear primer registro
        form1 = InformacionBasicaPublicForm(data=self.valid_data)
        self.assertTrue(form1.is_valid())
        form1.save()

        # Intentar crear segundo registro con misma cédula
        data2 = self.valid_data.copy()
        data2['correo'] = 'otro@example.com'
        form2 = InformacionBasicaPublicForm(data=data2)
        self.assertFalse(form2.is_valid())
        self.assertIn('cedula', form2.errors)

    def test_telefono_debe_ser_numerico(self):
        """Test que teléfono debe contener solo números"""
        data = self.valid_data.copy()
        data['telefono'] = '300-123-4567'
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    def test_telefono_debe_tener_10_digitos(self):
        """Test que teléfono debe tener exactamente 10 dígitos"""
        data = self.valid_data.copy()
        data['telefono'] = '300123456'  # 9 dígitos
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    def test_correo_debe_contener_arroba(self):
        """Test que correo debe tener @"""
        data = self.valid_data.copy()
        data['correo'] = 'juangomez.com'
        form = InformacionBasicaPublicForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)

    def test_segundo_nombre_opcional(self):
        """Test que segundo nombre es opcional"""
        data = self.valid_data.copy()
        data['segundo_nombre'] = ''
        form = InformacionBasicaPublicForm(data=data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.nombre_completo, 'GOMEZ LOPEZ JUAN')

    def test_campos_obligatorios(self):
        """Test que los campos obligatorios no pueden estar vacíos"""
        required_fields = [
            'primer_apellido',
            'segundo_apellido',
            'primer_nombre',
            'cedula',
            'genero',
            'tipo_via',
            'numero_via',
            'numero_casa',
            'telefono',
            'correo',
        ]

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            form = InformacionBasicaPublicForm(data=data)
            self.assertFalse(form.is_valid(), f"Campo {field} debería ser obligatorio")
            self.assertIn(field, form.errors, f"Debería haber error en campo {field}")


class ExperienciaLaboralFormTest(TestCase):
    """Tests para ExperienciaLaboralForm"""

    def setUp(self):
        """Configuración inicial"""
        self.persona = InformacionBasica.objects.create(
            nombre_completo='TEST PERSONA',
            cedula='1122334455',
            genero='Masculino',
            tipo_via='Calle',
            numero_via='1',
            numero_casa='1',
            telefono='3001112233',
            correo='test@test.com',
        )

        # Crear un archivo PDF de prueba con cabecera válida
        self.test_pdf = SimpleUploadedFile(
            "certificado.pdf",
            b"%PDF-1.4 content",
            content_type="application/pdf"
        )

        self.valid_data = {
            'fecha_inicial': date(2020, 1, 1),
            'fecha_terminacion': date(2021, 1, 1),
            'meses_experiencia': 12,
            'dias_experiencia': 366,
            'cargo': 'Ingeniero de Software',
            'cargo_anexo_11': 'Profesional',
            'objeto_contractual': 'Desarrollo de aplicaciones web',
            'funciones': 'Programación, diseño y testing',
        }

    def test_formulario_valido_con_certificado(self):
        """Test formulario válido con certificado"""
        form = ExperienciaLaboralForm(
            data=self.valid_data,
            files={'certificado_laboral': self.test_pdf}
        )
        self.assertTrue(form.is_valid())

    def test_fecha_inicial_debe_ser_anterior_a_fecha_terminacion(self):
        """Test que fecha inicial debe ser anterior a fecha terminación"""
        data = self.valid_data.copy()
        data['fecha_inicial'] = date(2021, 1, 1)
        data['fecha_terminacion'] = date(2020, 1, 1)
        form = ExperienciaLaboralForm(
            data=data,
            files={'certificado_laboral': self.test_pdf}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_cargo_anexo_11_tiene_valor_por_defecto(self):
        """Test que cargo_anexo_11 tiene 'Profesional' como default"""
        data = self.valid_data.copy()
        data['cargo_anexo_11'] = ''
        form = ExperienciaLaboralForm(
            data=data,
            files={'certificado_laboral': self.test_pdf}
        )
        self.assertTrue(form.is_valid())
        # El método clean_cargo_anexo_11 debería establecer 'Profesional'
        self.assertEqual(form.cleaned_data['cargo_anexo_11'], 'Profesional')

    def test_certificado_laboral_obligatorio_en_creacion(self):
        """Test que certificado es obligatorio para nuevo registro"""
        form = ExperienciaLaboralForm(data=self.valid_data)
        # Sin archivos
        self.assertFalse(form.is_valid())
        self.assertIn('certificado_laboral', form.errors)

    def test_certificado_laboral_opcional_en_edicion(self):
        """Test que certificado es opcional al editar"""
        # Mock de Cloudinary para evitar error en save()
        from unittest.mock import patch
        with patch('cloudinary.uploader.upload', return_value={'public_id': 'test', 'format': 'pdf', 'resource_type': 'raw'}):
            # Primero crear una experiencia con certificado
            exp = ExperienciaLaboral.objects.create(
                informacion_basica=self.persona,
                **self.valid_data,
                certificado_laboral=self.test_pdf
            )

        # Editar sin proporcionar nuevo certificado
        data = self.valid_data.copy()
        form = ExperienciaLaboralForm(data=data, instance=exp)
        # En edición, el certificado debería ser opcional
        self.assertTrue(form.is_valid())

    def test_campos_obligatorios(self):
        """Test campos obligatorios"""
        required_fields = [
            'fecha_inicial',
            'fecha_terminacion',
            'cargo',
            'objeto_contractual',
            'funciones',
            'meses_experiencia',
            'dias_experiencia',
        ]

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            form = ExperienciaLaboralForm(
                data=data,
                files={'certificado_laboral': self.test_pdf}
            )
            self.assertFalse(form.is_valid(), f"Campo {field} debería ser obligatorio")


class DocumentosIdentidadFormTest(TestCase):
    """Tests para DocumentosIdentidadForm"""

    def setUp(self):
        """Configuración inicial"""
        self.test_pdf = SimpleUploadedFile(
            "cedula.pdf",
            b"%PDF-1.4 content",
            content_type="application/pdf"
        )
        self.test_pdf_hv = SimpleUploadedFile(
            "hoja_vida.pdf",
            b"%PDF-1.4 content",
            content_type="application/pdf"
        )

    def test_formulario_valido_sin_libreta_militar(self):
        """Test que libreta militar es opcional"""
        form = DocumentosIdentidadForm(
            data={},
            files={
                'fotocopia_cedula': self.test_pdf,
                'hoja_de_vida': self.test_pdf_hv,
            },
            genero='Femenino'
        )
        self.assertTrue(form.is_valid())

    def test_fotocopia_cedula_obligatoria(self):
        """Test que fotocopia de cédula es obligatoria"""
        form = DocumentosIdentidadForm(
            data={},
            files={'hoja_de_vida': self.test_pdf_hv},
            genero='Masculino'
        )
        self.assertFalse(form.is_valid())
        self.assertIn('fotocopia_cedula', form.errors)

    def test_hoja_de_vida_obligatoria(self):
        """Test que hoja de vida es obligatoria"""
        form = DocumentosIdentidadForm(
            data={},
            files={'fotocopia_cedula': self.test_pdf},
            genero='Femenino'
        )
        self.assertFalse(form.is_valid())
        self.assertIn('hoja_de_vida', form.errors)


class AntecedentesFormTest(TestCase):
    """Tests para AntecedentesForm"""

    def setUp(self):
        """Configuración inicial"""
        self.create_test_files()

    def create_test_files(self):
        """Crear archivos de prueba"""
        self.cert_procuraduria = SimpleUploadedFile(
            "procuraduria.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )
        self.cert_contraloria = SimpleUploadedFile(
            "contraloria.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )
        self.cert_policia = SimpleUploadedFile(
            "policia.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )
        self.cert_medidas = SimpleUploadedFile(
            "medidas.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )
        self.cert_delitos = SimpleUploadedFile(
            "delitos.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )

    def test_formulario_valido_con_todos_los_certificados(self):
        """Test formulario válido con todos los certificados"""
        form = AntecedentesForm(
            data={
                'fecha_procuraduria': date(2024, 1, 1),
                'fecha_contraloria': date(2024, 1, 1),
                'fecha_policia': date(2024, 1, 1),
                'fecha_medidas_correctivas': date(2024, 1, 1),
                'fecha_delitos_sexuales': date(2024, 1, 1),
            },
            files={
                'certificado_procuraduria': self.cert_procuraduria,
                'certificado_contraloria': self.cert_contraloria,
                'certificado_policia': self.cert_policia,
                'certificado_medidas_correctivas': self.cert_medidas,
                'certificado_delitos_sexuales': self.cert_delitos,
            }
        )
        self.assertTrue(form.is_valid())

    def test_todos_los_certificados_son_obligatorios(self):
        """Test que todos los 5 certificados son obligatorios"""
        required_files = [
            'certificado_procuraduria',
            'certificado_contraloria',
            'certificado_policia',
            'certificado_medidas_correctivas',
            'certificado_delitos_sexuales',
        ]

        for cert_field in required_files:
            self.create_test_files()  # Recrear archivos
            files = {
                'certificado_procuraduria': self.cert_procuraduria,
                'certificado_contraloria': self.cert_contraloria,
                'certificado_policia': self.cert_policia,
                'certificado_medidas_correctivas': self.cert_medidas,
                'certificado_delitos_sexuales': self.cert_delitos,
            }
            # Remover el certificado a probar
            del files[cert_field]

            form = AntecedentesForm(
                data={
                    'fecha_procuraduria': date(2024, 1, 1),
                    'fecha_contraloria': date(2024, 1, 1),
                    'fecha_policia': date(2024, 1, 1),
                    'fecha_medidas_correctivas': date(2024, 1, 1),
                    'fecha_delitos_sexuales': date(2024, 1, 1),
                },
                files=files
            )
            self.assertFalse(form.is_valid(), f"{cert_field} debería ser obligatorio")

    def test_todas_las_fechas_son_obligatorias(self):
        """Test que todas las fechas son obligatorias"""
        required_dates = [
            'fecha_procuraduria',
            'fecha_contraloria',
            'fecha_policia',
            'fecha_medidas_correctivas',
            'fecha_delitos_sexuales',
        ]

        for date_field in required_dates:
            self.create_test_files()
            data = {
                'fecha_procuraduria': date(2024, 1, 1),
                'fecha_contraloria': date(2024, 1, 1),
                'fecha_policia': date(2024, 1, 1),
                'fecha_medidas_correctivas': date(2024, 1, 1),
                'fecha_delitos_sexuales': date(2024, 1, 1),
            }
            # Remover la fecha a probar
            del data[date_field]

            form = AntecedentesForm(
                data=data,
                files={
                    'certificado_procuraduria': self.cert_procuraduria,
                    'certificado_contraloria': self.cert_contraloria,
                    'certificado_policia': self.cert_policia,
                    'certificado_medidas_correctivas': self.cert_medidas,
                    'certificado_delitos_sexuales': self.cert_delitos,
                }
            )
            self.assertFalse(form.is_valid(), f"{date_field} debería ser obligatorio")


class AnexosAdicionalesFormTest(TestCase):
    """Tests para AnexosAdicionalesForm"""

    def test_todos_los_campos_son_opcionales(self):
        """Test que todos los anexos adicionales son opcionales"""
        form = AnexosAdicionalesForm(data={}, files={})
        self.assertTrue(form.is_valid())

    def test_formulario_valido_con_anexos(self):
        """Test formulario válido con anexos"""
        anexo_pdf = SimpleUploadedFile(
            "anexo.pdf", b"%PDF-1.4 content", content_type="application/pdf"
        )
        form = AnexosAdicionalesForm(
            data={'descripcion_otros': 'Certificado de idiomas'},
            files={'anexo_03_datos_personales': anexo_pdf}
        )
        self.assertTrue(form.is_valid())


class PosgradoFormTest(TestCase):
    """Tests para PosgradoForm"""

    def test_formulario_valido(self):
        """Test formulario válido de posgrado"""
        form = PosgradoForm(data={
            'nombre_posgrado': 'Maestría en Ingeniería',
            'universidad': 'Universidad Nacional',
            'fecha_terminacion': date(2022, 6, 1),
        })
        self.assertTrue(form.is_valid())

    def test_campos_obligatorios(self):
        """Test campos obligatorios"""
        form = PosgradoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_posgrado', form.errors)
        self.assertIn('universidad', form.errors)
        self.assertIn('fecha_terminacion', form.errors)


class EspecializacionFormTest(TestCase):
    """Tests para EspecializacionForm"""

    def test_formulario_valido(self):
        """Test formulario válido de especialización"""
        form = EspecializacionForm(data={
            'nombre_especializacion': 'Especialización en Gerencia',
            'universidad': 'Universidad Javeriana',
            'fecha_terminacion': date(2021, 12, 1),
        })
        self.assertTrue(form.is_valid())

    def test_campos_obligatorios(self):
        """Test campos obligatorios"""
        form = EspecializacionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_especializacion', form.errors)
        self.assertIn('universidad', form.errors)
        self.assertIn('fecha_terminacion', form.errors)


class InformacionAcademicaFormTest(TestCase):
    """Tests para InformacionAcademicaForm"""

    def test_formulario_valido_minimo(self):
        """Test formulario válido con campos mínimos requeridos"""
        form = InformacionAcademicaForm(data={
            'profesion': 'Ingeniero de Sistemas',
            'universidad': 'Universidad Nacional',
            'fecha_grado': date(2020, 12, 1),
            'tarjeta_profesional': 'No Aplica',
        })
        self.assertTrue(form.is_valid())

    def test_formulario_valido_completo(self):
        """Test formulario válido con todos los campos"""
        form = InformacionAcademicaForm(data={
            'profesion': 'Abogado',
            'universidad': 'Universidad Libre',
            'fecha_grado': date(2019, 6, 1),
            'tarjeta_profesional': 'Tarjeta Profesional',
            'numero_tarjeta_resolucion': 'TP-123456',
            'fecha_expedicion': date(2019, 7, 1),
            'fecha_vigencia_tarjeta': date(2029, 7, 1),
        })
        self.assertTrue(form.is_valid())

    def test_campos_obligatorios(self):
        """Test campos obligatorios"""
        form = InformacionAcademicaForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('profesion', form.errors)
        self.assertIn('universidad', form.errors)
        self.assertIn('fecha_grado', form.errors)

    def test_archivos_opcionales(self):
        """Test que los archivos son opcionales en el formulario"""
        # El modelo define estos campos como blank=True, null=True
        form = InformacionAcademicaForm(data={
            'profesion': 'Ingeniero',
            'universidad': 'U. Andes',
            'fecha_grado': date(2020, 1, 1),
            'tarjeta_profesional': 'No Aplica',
        })
        self.assertTrue(form.is_valid())
        # Verificar que no hay errores relacionados con archivos
        self.assertNotIn('fotocopia_titulo', form.errors)