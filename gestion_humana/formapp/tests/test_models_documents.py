from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from datetime import date
from unittest.mock import patch, MagicMock

from formapp.models import (
    InformacionBasica,
    DocumentosIdentidad,
    Antecedentes,
    AnexosAdicionales
)

# Mock return value for Cloudinary upload
MOCK_CLOUDINARY_RESPONSE = {
    'public_id': 'test_id',
    'version': '123456',
    'signature': 'abcdef',
    'format': 'pdf',
    'resource_type': 'raw'
}

@patch('cloudinary.uploader.upload', return_value=MOCK_CLOUDINARY_RESPONSE)
class DocumentosIdentidadModelTest(TestCase):
    def setUp(self):
        self.info_basica = InformacionBasica.objects.create(
            primer_apellido="PEREZ",
            segundo_apellido="GARCIA",
            primer_nombre="JUAN",
            cedula="12345",
            correo="juan@example.com",
            telefono="3001234567",
            genero="Masculino",
            tipo_via="Calle",
            numero_via="123",
            numero_casa="45-67",
            barrio="Centro"
        )
        self.archivo_dummy = SimpleUploadedFile("test.pdf", b"%PDF-1.4 content here", content_type="application/pdf")

    def test_crear_documentos_identidad_minimo(self, mock_upload):
        """Test creating with only required fields"""
        docs = DocumentosIdentidad.objects.create(
            informacion_basica=self.info_basica,
            fotocopia_cedula=self.archivo_dummy
        )
        self.assertEqual(docs.informacion_basica, self.info_basica)
        self.assertTrue(docs.fotocopia_cedula)
        self.assertFalse(docs.hoja_de_vida) # Optional
        self.assertFalse(docs.libreta_militar) # Optional

    def test_crear_documentos_identidad_completo(self, mock_upload):
        """Test creating with all fields"""
        docs = DocumentosIdentidad.objects.create(
            informacion_basica=self.info_basica,
            fotocopia_cedula=self.archivo_dummy,
            hoja_de_vida=self.archivo_dummy,
            libreta_militar=self.archivo_dummy,
            numero_libreta_militar="123456789",
            distrito_militar="Distrito 1",
            clase_libreta="Primera"
        )
        self.assertTrue(docs.hoja_de_vida)
        self.assertTrue(docs.libreta_militar)
        self.assertEqual(docs.numero_libreta_militar, "123456789")

    def test_one_to_one_relationship(self, mock_upload):
        """Test that one InformacionBasica can have only one DocumentosIdentidad"""
        DocumentosIdentidad.objects.create(
            informacion_basica=self.info_basica,
            fotocopia_cedula=self.archivo_dummy
        )
        with self.assertRaises(IntegrityError):
            DocumentosIdentidad.objects.create(
                informacion_basica=self.info_basica,
                fotocopia_cedula=self.archivo_dummy
            )

@patch('cloudinary.uploader.upload', return_value=MOCK_CLOUDINARY_RESPONSE)
class AntecedentesModelTest(TestCase):
    def setUp(self):
        self.info_basica = InformacionBasica.objects.create(
            primer_apellido="GOMEZ",
            segundo_apellido="MARTINEZ",
            primer_nombre="MARIA",
            cedula="67890",
            correo="maria@example.com",
            telefono="3009876543",
            genero="Femenino",
            tipo_via="Carrera",
            numero_via="45",
            numero_casa="12-34",
            barrio="Poblado"
        )
        self.archivo_dummy = SimpleUploadedFile("antecedente.pdf", b"%PDF-1.4 content here", content_type="application/pdf")
        self.fecha_dummy = date(2025, 1, 1)

    def test_crear_antecedentes_completo(self, mock_upload):
        """Test creating Antecedentes with all required fields"""
        antecedentes = Antecedentes.objects.create(
            informacion_basica=self.info_basica,
            certificado_procuraduria=self.archivo_dummy,
            fecha_procuraduria=self.fecha_dummy,
            certificado_contraloria=self.archivo_dummy,
            fecha_contraloria=self.fecha_dummy,
            certificado_policia=self.archivo_dummy,
            fecha_policia=self.fecha_dummy,
            certificado_medidas_correctivas=self.archivo_dummy,
            fecha_medidas_correctivas=self.fecha_dummy,
            certificado_delitos_sexuales=self.archivo_dummy,
            fecha_delitos_sexuales=self.fecha_dummy
        )
        self.assertEqual(antecedentes.informacion_basica, self.info_basica)
        self.assertTrue(antecedentes.certificado_procuraduria)
        self.assertEqual(antecedentes.fecha_procuraduria, self.fecha_dummy)

    def test_str_method(self, mock_upload):
        antecedentes = Antecedentes.objects.create(
            informacion_basica=self.info_basica,
            certificado_procuraduria=self.archivo_dummy,
            fecha_procuraduria=self.fecha_dummy,
            certificado_contraloria=self.archivo_dummy,
            fecha_contraloria=self.fecha_dummy,
            certificado_policia=self.archivo_dummy,
            fecha_policia=self.fecha_dummy,
            certificado_medidas_correctivas=self.archivo_dummy,
            fecha_medidas_correctivas=self.fecha_dummy,
            certificado_delitos_sexuales=self.archivo_dummy,
            fecha_delitos_sexuales=self.fecha_dummy
        )
        self.assertIn("Antecedentes de GOMEZ MARTINEZ MARIA", str(antecedentes))

@patch('cloudinary.uploader.upload', return_value=MOCK_CLOUDINARY_RESPONSE)
class AnexosAdicionalesModelTest(TestCase):
    def setUp(self):
        self.info_basica = InformacionBasica.objects.create(
            primer_apellido="RODRIGUEZ",
            segundo_apellido="LOPEZ",
            primer_nombre="PEDRO",
            cedula="54321",
            correo="pedro@example.com",
            telefono="3005556666",
            genero="Masculino",
            tipo_via="Avenida",
            numero_via="789",
            numero_casa="01-02",
            barrio="Norte"
        )
        self.archivo_dummy = SimpleUploadedFile("anexo.pdf", b"%PDF-1.4 content here", content_type="application/pdf")

    def test_crear_anexos_opcionales(self, mock_upload):
        """Test that AnexosAdicionales can be created even if empty (all fields optional)"""
        anexos = AnexosAdicionales.objects.create(
            informacion_basica=self.info_basica
        )
        self.assertEqual(anexos.informacion_basica, self.info_basica)
        self.assertFalse(anexos.anexo_03_datos_personales)

    def test_crear_anexos_con_datos(self, mock_upload):
        anexos = AnexosAdicionales.objects.create(
            informacion_basica=self.info_basica,
            anexo_03_datos_personales=self.archivo_dummy,
            carta_intencion=self.archivo_dummy,
            otros_documentos=self.archivo_dummy,
            descripcion_otros="Documentos extra"
        )
        self.assertTrue(anexos.anexo_03_datos_personales)
        self.assertEqual(anexos.descripcion_otros, "Documentos extra")
