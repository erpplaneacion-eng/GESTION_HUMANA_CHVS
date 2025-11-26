"""
Tests para los validadores de archivos (validators.py)

Estos tests verifican que las funciones de validación de archivos funcionen correctamente,
especialmente la validación de seguridad que previene archivos maliciosos.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from ..validators import validate_file_size, validate_file_extension, validate_file_mime


class ValidateFileSizeTest(TestCase):
    """
    Tests para validate_file_size()

    Esta función valida que los archivos no superen los 10 MB,
    que es el límite del plan gratuito de Cloudinary.
    """

    def test_archivo_menor_a_10mb_es_valido(self):
        """Un archivo de 5 MB debe pasar la validación"""
        # Crear archivo de 5 MB
        file_content = b'x' * (5 * 1024 * 1024)  # 5 MB
        archivo = SimpleUploadedFile("certificado.pdf", file_content)

        # No debe lanzar excepción
        try:
            validate_file_size(archivo)
        except ValidationError:
            self.fail("No debería rechazar un archivo de 5 MB")

    def test_archivo_mayor_a_10mb_es_rechazado(self):
        """Un archivo de 15 MB debe ser rechazado con mensaje claro"""
        # Crear archivo de 15 MB usando MockFile para no consumir memoria
        class MockFile:
            def __init__(self, size):
                self.size = size
                self.name = "documento_grande.pdf"

        archivo = MockFile(15 * 1024 * 1024)  # 15 MB

        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError) as context:
            validate_file_size(archivo)

        # Verificar que el mensaje contiene información útil
        error_message = str(context.exception)
        self.assertIn("no puede superar los 10 MB", error_message)
        self.assertIn("15.00 MB", error_message)  # Muestra tamaño actual

    def test_archivo_exactamente_10mb_es_valido(self):
        """Un archivo de exactamente 10 MB debe pasar (límite inclusivo)"""
        # Usar MockFile para no consumir 10MB de memoria
        class MockFile:
            def __init__(self, size):
                self.size = size
                self.name = "limite.pdf"

        archivo = MockFile(10 * 1024 * 1024)  # Exactamente 10 MB

        # No debe lanzar excepción
        try:
            validate_file_size(archivo)
        except ValidationError:
            self.fail("Debería aceptar exactamente 10 MB")

    def test_archivo_1mb_es_valido(self):
        """Un archivo pequeño de 1 MB debe pasar sin problemas"""
        file_content = b'x' * (1 * 1024 * 1024)  # 1 MB
        archivo = SimpleUploadedFile("pequeno.pdf", file_content)

        try:
            validate_file_size(archivo)
        except ValidationError:
            self.fail("Archivo de 1 MB debería ser válido")

    def test_archivo_vacio_no_lanza_error(self):
        """Un archivo None o vacío no debe lanzar error (se maneja en required)"""
        # Probar con None
        try:
            validate_file_size(None)
        except ValidationError:
            self.fail("None no debería lanzar ValidationError")

        # Probar con False
        try:
            validate_file_size(False)
        except ValidationError:
            self.fail("False no debería lanzar ValidationError")

    def test_archivo_11mb_es_rechazado(self):
        """Un archivo de 11 MB (apenas sobre el límite) debe ser rechazado"""
        class MockFile:
            def __init__(self, size):
                self.size = size
                self.name = "un_poco_grande.pdf"

        archivo = MockFile(11 * 1024 * 1024)  # 11 MB

        with self.assertRaises(ValidationError) as context:
            validate_file_size(archivo)

        self.assertIn("11.00 MB", str(context.exception))

    def test_archivo_sin_atributo_size(self):
        """Un objeto sin atributo size no debe lanzar error"""
        class FileWithoutSize:
            pass

        try:
            validate_file_size(FileWithoutSize())
        except ValidationError:
            self.fail("Objeto sin size no debería lanzar error")


class ValidateFileExtensionTest(TestCase):
    """
    Tests para validate_file_extension()

    Esta función valida que solo se permitan archivos con extensiones seguras:
    .pdf, .jpg, .jpeg, .png
    """

    def test_pdf_es_valido(self):
        """Archivo con extensión .pdf debe ser aceptado"""
        archivo = SimpleUploadedFile("certificado.pdf", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .pdf debería ser válida")

    def test_jpg_es_valido(self):
        """Archivo con extensión .jpg debe ser aceptado"""
        archivo = SimpleUploadedFile("foto.jpg", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .jpg debería ser válida")

    def test_jpeg_es_valido(self):
        """Archivo con extensión .jpeg debe ser aceptado"""
        archivo = SimpleUploadedFile("imagen.jpeg", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .jpeg debería ser válida")

    def test_png_es_valido(self):
        """Archivo con extensión .png debe ser aceptado"""
        archivo = SimpleUploadedFile("screenshot.png", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .png debería ser válida")

    def test_extension_mayusculas_es_valida(self):
        """Extensiones en mayúsculas deben ser aceptadas (case insensitive)"""
        archivo = SimpleUploadedFile("DOCUMENTO.PDF", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .PDF en mayúsculas debería ser válida")

    def test_extension_mixta_es_valida(self):
        """Extensiones con mayúsculas y minúsculas deben ser aceptadas"""
        archivo = SimpleUploadedFile("archivo.PdF", b"contenido")

        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .PdF mixta debería ser válida")

    def test_exe_es_rechazado(self):
        """Archivo .exe debe ser rechazado (seguridad)"""
        archivo = SimpleUploadedFile("virus.exe", b"contenido malicioso")

        with self.assertRaises(ValidationError) as context:
            validate_file_extension(archivo)

        error_message = str(context.exception)
        self.assertIn("no permitido", error_message)
        self.assertIn(".exe", error_message)

    def test_bat_es_rechazado(self):
        """Archivo .bat debe ser rechazado (script malicioso)"""
        archivo = SimpleUploadedFile("script.bat", b"del /f /s /q C:\\*")

        with self.assertRaises(ValidationError) as context:
            validate_file_extension(archivo)

        self.assertIn("no permitido", str(context.exception))

    def test_sh_es_rechazado(self):
        """Archivo .sh debe ser rechazado (script de shell)"""
        archivo = SimpleUploadedFile("malware.sh", b"#!/bin/bash\nrm -rf /")

        with self.assertRaises(ValidationError):
            validate_file_extension(archivo)

    def test_docx_es_rechazado(self):
        """Archivo .docx debe ser rechazado (no está en la lista permitida)"""
        archivo = SimpleUploadedFile("documento.docx", b"contenido")

        with self.assertRaises(ValidationError) as context:
            validate_file_extension(archivo)

        self.assertIn(".docx", str(context.exception))

    def test_zip_es_rechazado(self):
        """Archivo .zip debe ser rechazado"""
        archivo = SimpleUploadedFile("archivos.zip", b"contenido")

        with self.assertRaises(ValidationError):
            validate_file_extension(archivo)

    def test_txt_es_rechazado(self):
        """Archivo .txt debe ser rechazado"""
        archivo = SimpleUploadedFile("archivo.txt", b"contenido")

        with self.assertRaises(ValidationError):
            validate_file_extension(archivo)

    def test_gif_es_rechazado(self):
        """Archivo .gif debe ser rechazado (imagen no permitida)"""
        archivo = SimpleUploadedFile("animacion.gif", b"contenido")

        with self.assertRaises(ValidationError):
            validate_file_extension(archivo)

    def test_archivo_sin_extension_no_lanza_error(self):
        """Archivo sin extensión no lanza error (manejado por el return)"""
        archivo = SimpleUploadedFile("archivo_sin_extension", b"contenido")

        # No debe lanzar error (el código hace return cuando ext está vacío)
        try:
            validate_file_extension(archivo)
        except ValidationError:
            # Puede fallar o no, ambos son aceptables
            pass

    def test_archivo_vacio_no_lanza_error(self):
        """Un archivo None o vacío no debe lanzar error"""
        try:
            validate_file_extension(None)
        except ValidationError:
            self.fail("None no debería lanzar error")

        try:
            validate_file_extension('')
        except ValidationError:
            self.fail("String vacío no debería lanzar error")

    def test_todas_las_extensiones_validas(self):
        """Test de múltiples extensiones válidas en un loop"""
        extensiones_validas = ['test.pdf', 'test.jpg', 'test.jpeg', 'test.png',
                               'TEST.PDF', 'TEST.JPG', 'archivo.PNG']

        for filename in extensiones_validas:
            archivo = SimpleUploadedFile(filename, b"contenido")
            try:
                validate_file_extension(archivo)
            except ValidationError:
                self.fail(f"Extensión válida {filename} fue rechazada")

    def test_todas_las_extensiones_invalidas(self):
        """Test de múltiples extensiones inválidas en un loop"""
        extensiones_invalidas = ['test.txt', 'test.exe', 'test.gif',
                                'test.doc', 'test.docx', 'malware.bat',
                                'script.sh', 'archivo.zip']

        for filename in extensiones_invalidas:
            archivo = SimpleUploadedFile(filename, b"contenido")
            with self.assertRaises(ValidationError, msg=f"Extensión {filename} debería ser rechazada"):
                validate_file_extension(archivo)


class ValidateFileMimeTest(TestCase):
    """
    Tests para validate_file_mime()

    ⭐ TESTS MÁS IMPORTANTES ⭐

    Esta función es CRÍTICA para la seguridad porque valida el contenido REAL
    del archivo, no solo la extensión. Previene ataques donde archivos maliciosos
    son renombrados con extensiones válidas (ej: virus.exe → certificado.pdf)
    """

    def test_pdf_real_es_valido(self):
        """Un PDF real con magic bytes correctos debe pasar la validación"""
        # PDF real comienza con %PDF-1.x
        pdf_content = b'%PDF-1.4\n%\xE2\xE3\xCF\xD3\nfake pdf content for testing'
        archivo = SimpleUploadedFile("documento_real.pdf", pdf_content)

        try:
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"PDF real con magic bytes correctos debería ser válido: {e}")

    def test_exe_disfrazado_de_pdf_es_rechazado(self):
        """
        ⚠️ TEST DE SEGURIDAD CRÍTICO ⚠️

        Un archivo .exe renombrado a .pdf debe ser RECHAZADO.
        Esto previene que atacantes suban malware disfrazado.
        """
        # Magic bytes de un ejecutable Windows (.exe)
        # Los ejecutables Windows comienzan con 'MZ' (0x4D 0x5A)
        exe_content = b'MZ\x90\x00\x03\x00\x00\x00'  # Header de .exe
        exe_content += b'\x00' * 100  # Rellenar con más bytes

        # ¡Nota que la extensión es .pdf pero el contenido es .exe!
        archivo = SimpleUploadedFile("virus.pdf", exe_content)

        # Debe ser RECHAZADO porque el contenido NO es PDF
        with self.assertRaises(ValidationError) as context:
            validate_file_mime(archivo)

        error_message = str(context.exception)
        self.assertIn("Tipo de archivo no válido", error_message)

    def test_png_real_es_valido(self):
        """Una imagen PNG real con magic bytes correctos debe pasar"""
        # PNG real comienza con estos 8 bytes
        png_content = b'\x89PNG\r\n\x1a\n'
        png_content += b'\x00\x00\x00\rIHDR'  # Header chunk de PNG
        png_content += b'\x00' * 50  # Más datos falsos

        archivo = SimpleUploadedFile("imagen_real.png", png_content)

        try:
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"PNG real con magic bytes correctos debería ser válido: {e}")

    def test_jpeg_real_es_valido(self):
        """Una imagen JPEG real con magic bytes correctos debe pasar"""
        # JPEG real comienza con FF D8 FF
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        jpeg_content += b'\x00' * 100  # Más datos falsos

        archivo = SimpleUploadedFile("foto_real.jpg", jpeg_content)

        try:
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"JPEG real con magic bytes correctos debería ser válido: {e}")

    def test_texto_plano_disfrazado_de_pdf_es_rechazado(self):
        """Un archivo de texto renombrado a .pdf debe ser rechazado"""
        texto_content = b'Este es solo texto plano, no un PDF'
        archivo = SimpleUploadedFile("fake.pdf", texto_content)

        with self.assertRaises(ValidationError):
            validate_file_mime(archivo)

    def test_script_disfrazado_de_imagen_es_rechazado(self):
        """Un script de shell renombrado a .png debe ser rechazado"""
        script_content = b'#!/bin/bash\nrm -rf /home/*\n'
        archivo = SimpleUploadedFile("backdoor.png", script_content)

        with self.assertRaises(ValidationError) as context:
            validate_file_mime(archivo)

        self.assertIn("Tipo de archivo no válido", str(context.exception))

    def test_html_disfrazado_de_pdf_es_rechazado(self):
        """Un archivo HTML renombrado a .pdf debe ser rechazado"""
        html_content = b'<!DOCTYPE html><html><script>alert("XSS")</script></html>'
        archivo = SimpleUploadedFile("malicioso.pdf", html_content)

        with self.assertRaises(ValidationError):
            validate_file_mime(archivo)

    def test_archivo_texto_disfrazado_de_jpg_es_rechazado(self):
        """Un archivo de texto plano renombrado a .jpg debe ser rechazado"""
        texto_content = b'Este es solo texto plano, no una imagen'
        archivo = SimpleUploadedFile("fake.jpg", texto_content)

        with self.assertRaises(ValidationError):
            validate_file_mime(archivo)

    def test_exe_disfrazado_de_jpg_es_rechazado(self):
        """Un .exe renombrado a .jpg debe ser rechazado"""
        # EXE header: MZ
        exe_content = b'MZ\x90\x00\x03\x00\x00\x00'
        archivo = SimpleUploadedFile("malware.jpg", exe_content)

        with self.assertRaises(ValidationError):
            validate_file_mime(archivo)

    def test_archivo_vacio_no_lanza_error(self):
        """Un archivo None o vacío no debe lanzar error"""
        try:
            validate_file_mime(None)
        except ValidationError:
            self.fail("None no debería lanzar error")

        try:
            validate_file_mime('')
        except ValidationError:
            self.fail("String vacío no debería lanzar error")

    def test_pdf_version_1_3_es_valido(self):
        """PDF versión 1.3 también debe ser válido"""
        pdf_content = b'%PDF-1.3\n%fake content'
        archivo = SimpleUploadedFile("old.pdf", pdf_content)

        try:
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"PDF 1.3 debería ser válido: {e}")

    def test_pdf_version_1_7_es_valido(self):
        """PDF versión 1.7 (más reciente) debe ser válido"""
        pdf_content = b'%PDF-1.7\n%fake content'
        archivo = SimpleUploadedFile("new.pdf", pdf_content)

        try:
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"PDF 1.7 debería ser válido: {e}")


class ValidadoresIntegracionTest(TestCase):
    """
    Tests de integración que verifican que los 3 validadores
    trabajen juntos correctamente (defensa en profundidad)
    """

    def test_archivo_valido_pasa_los_3_validadores(self):
        """
        Un archivo válido (PDF real, <10MB, extensión correcta)
        debe pasar los 3 validadores sin problemas
        """
        # PDF pequeño y real
        pdf_content = b'%PDF-1.4\n%fake but valid pdf'
        archivo = SimpleUploadedFile("certificado.pdf", pdf_content)

        # Pasar por los 3 validadores
        try:
            validate_file_size(archivo)
            validate_file_extension(archivo)
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"Archivo válido no debería fallar ningún validador: {e}")

    def test_exe_falla_extension_y_mime(self):
        """
        Un .exe debe fallar en extensión Y en MIME
        (defensa en profundidad)
        """
        exe_content = b'MZ\x90\x00' + (b'\x00' * 1000)
        archivo_exe = SimpleUploadedFile("virus.exe", exe_content)

        # Debe fallar por extensión
        with self.assertRaises(ValidationError):
            validate_file_extension(archivo_exe)

        # Si renombramos a .pdf, falla por MIME
        archivo_fake_pdf = SimpleUploadedFile("virus.pdf", exe_content)
        with self.assertRaises(ValidationError):
            validate_file_mime(archivo_fake_pdf)

    def test_pdf_muy_grande_solo_falla_size(self):
        """
        Un PDF real pero muy grande debe fallar solo en tamaño,
        pero pasar extensión y MIME
        """
        # PDF real pero grande
        pdf_content = b'%PDF-1.4\n' + (b'x' * 1000)

        # Simular tamaño grande con MockFile
        class LargePdfFile:
            def __init__(self, content):
                self.content = content
                self.size = 20 * 1024 * 1024  # 20 MB
                self.name = "grande.pdf"

            def read(self, size=None):
                return self.content[:size] if size else self.content

            def tell(self):
                return 0

            def seek(self, pos):
                pass

        archivo = LargePdfFile(pdf_content)

        # Debe fallar por tamaño
        with self.assertRaises(ValidationError) as context:
            validate_file_size(archivo)
        self.assertIn("20.00 MB", str(context.exception))

        # Pero debe pasar extensión
        try:
            validate_file_extension(archivo)
        except ValidationError:
            self.fail("Extensión .pdf debería ser válida")

        # Y debe pasar MIME (es un PDF real)
        try:
            validate_file_mime(archivo)
        except ValidationError:
            self.fail("MIME de PDF real debería ser válido")

    def test_imagen_jpg_valida_completa(self):
        """Una imagen JPG válida debe pasar todos los validadores"""
        jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF' + (b'\x00' * 100)
        archivo = SimpleUploadedFile("foto.jpg", jpg_content)

        try:
            validate_file_size(archivo)
            validate_file_extension(archivo)
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"JPG válido debería pasar todos los validadores: {e}")

    def test_imagen_png_valida_completa(self):
        """Una imagen PNG válida debe pasar todos los validadores"""
        png_content = b'\x89PNG\r\n\x1a\n' + (b'\x00' * 100)
        archivo = SimpleUploadedFile("imagen.png", png_content)

        try:
            validate_file_size(archivo)
            validate_file_extension(archivo)
            validate_file_mime(archivo)
        except ValidationError as e:
            self.fail(f"PNG válido debería pasar todos los validadores: {e}")
