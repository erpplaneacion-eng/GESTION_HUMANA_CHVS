from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from ..validators import validate_file_size, validate_file_extension, validate_file_mime

class ValidateFileSizeTest(TestCase):
    def test_valid_file_size(self):
        # 1MB file
        file = SimpleUploadedFile("test.pdf", b"content" * 1024 * 1024)
        # Should not raise ValidationError
        try:
            validate_file_size(file)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError unexpectedly for 1MB file")

    def test_invalid_file_size(self):
        # 11MB file (10MB limit)
        # Create a mock file object to avoid creating a huge string in memory
        class MockFile:
            def __init__(self, size):
                self.size = size
                self.name = "large.pdf"
        
        file = MockFile(11 * 1024 * 1024)
        
        with self.assertRaises(ValidationError) as cm:
            validate_file_size(file)
        self.assertIn('no puede superar los 10 MB', str(cm.exception))

    def test_exact_limit_file_size(self):
        # 10MB file
        class MockFile:
            def __init__(self, size):
                self.size = size
                self.name = "limit.pdf"
        
        file = MockFile(10 * 1024 * 1024)
        try:
            validate_file_size(file)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError unexpectedly for 10MB file")

    def test_none_or_empty_file(self):
        # None check
        try:
            validate_file_size(None)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError for None")
            
        # Empty object check
        class EmptyFile:
            pass
        try:
            validate_file_size(EmptyFile())
        except ValidationError:
            self.fail("validate_file_size raised ValidationError for empty object")

class ValidateFileExtensionTest(TestCase):
    def test_valid_extensions(self):
        valid_extensions = ['test.pdf', 'test.jpg', 'test.jpeg', 'test.png', 'TEST.PDF', 'TEST.JPG']
        for filename in valid_extensions:
            file = SimpleUploadedFile(filename, b"content")
            try:
                validate_file_extension(file)
            except ValidationError:
                self.fail(f"validate_file_extension raised ValidationError for valid extension: {filename}")

    def test_invalid_extensions(self):
        invalid_extensions = ['test.txt', 'test.exe', 'test.gif', 'test.doc', 'test.docx']
        for filename in invalid_extensions:
            file = SimpleUploadedFile(filename, b"content")
            with self.assertRaises(ValidationError, msg=f"Should raise error for {filename}"):
                validate_file_extension(file)

    def test_no_extension(self):
        # Based on current code logic: "if not ext: return"
        # This means files without extension are allowed by this specific validator
        file = SimpleUploadedFile("readme", b"content")
        try:
            validate_file_extension(file)
        except ValidationError:
            self.fail("validate_file_extension raised ValidationError for file without extension")

class ValidateFileMimeTest(TestCase):
    def test_valid_pdf_mime(self):
        # PDF Header: %PDF
        content = b'%PDF-1.4 content'
        file = SimpleUploadedFile("test.pdf", content, content_type="application/pdf")
        try:
            validate_file_mime(file)
        except ValidationError:
            self.fail("validate_file_mime raised ValidationError for valid PDF")

    def test_valid_jpg_mime(self):
        # JPEG Header: \xff\xd8\xff
        content = b'\xff\xd8\xff\xe0\x00\x10JFIF content'
        file = SimpleUploadedFile("test.jpg", content, content_type="image/jpeg")
        try:
            validate_file_mime(file)
        except ValidationError:
            self.fail("validate_file_mime raised ValidationError for valid JPG")

    def test_valid_png_mime(self):
        # PNG Header: \x89PNG\r\n\x1a\n
        content = b'\x89PNG\r\n\x1a\n content'
        file = SimpleUploadedFile("test.png", content, content_type="image/png")
        try:
            validate_file_mime(file)
        except ValidationError:
            self.fail("validate_file_mime raised ValidationError for valid PNG")

    def test_invalid_content_renamed_extension(self):
        # Text file renamed to .pdf
        content = b'This is a text file, not a PDF'
        file = SimpleUploadedFile("fake.pdf", content, content_type="application/pdf")
        
        with self.assertRaises(ValidationError):
            validate_file_mime(file)

    def test_exe_renamed_to_jpg(self):
        # EXE header usually starts with MZ
        content = b'MZ\x90\x00\x03\x00\x00\x00'
        file = SimpleUploadedFile("malware.jpg", content, content_type="image/jpeg")
        
        with self.assertRaises(ValidationError):
            validate_file_mime(file)
