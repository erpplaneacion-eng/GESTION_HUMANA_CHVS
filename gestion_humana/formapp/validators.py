from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    """
    Valida que el archivo no supere los 10 MB (límite de Cloudinary plan gratuito)
    """
    # Si no hay archivo (None o False), no validar
    if not value:
        return
    
    # Si el archivo no tiene tamaño, no validar
    if not hasattr(value, 'size') or not value.size:
        return
    
    filesize = value.size
    max_size_mb = 10
    max_size_bytes = max_size_mb * 1024 * 1024  # 10 MB en bytes

    if filesize > max_size_bytes:
        raise ValidationError(f'El archivo no puede superar los {max_size_mb} MB. Tamaño actual: {filesize / (1024 * 1024):.2f} MB')

def validate_file_extension(value):
    """
    Valida que el archivo sea PDF, JPG, PNG o JPEG
    """
    # Si no hay archivo (None o False), no validar
    if not value:
        return
    
    # Si el archivo no tiene nombre, no validar
    if not hasattr(value, 'name') or not value.name:
        return
    
    ext = os.path.splitext(value.name)[1].lower()  # Obtener extensión del archivo
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']

    if ext not in valid_extensions:
        raise ValidationError(
            f'Tipo de archivo no permitido. Solo se permiten archivos: PDF, JPG, JPEG, PNG. '
            f'Archivo actual: {ext}'
        )
