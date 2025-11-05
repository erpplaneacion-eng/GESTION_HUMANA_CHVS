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
    # Si no hay archivo (None, False, o cadena vacía), no validar
    # Esto permite que el campo esté vacío en edición
    if not value or value == '':
        return
    
    # Si el archivo no tiene nombre, no validar
    if not hasattr(value, 'name'):
        return
    
    # Si el nombre está vacío o es None, no validar
    if not value.name or value.name == '':
        return
    
    # Si el archivo parece ser un objeto vacío (típico en formsets cuando no se envía archivo)
    # Verificar si realmente tiene contenido
    if hasattr(value, 'size') and value.size == 0:
        return
    
    try:
        # Obtener extensión del archivo
        name = str(value.name) if value.name else ''
        if not name:
            return
        
        ext = os.path.splitext(name)[1].lower()
        
        # Si la extensión está vacía, no validar (probablemente es un objeto vacío)
        if not ext:
            return
        
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']

        if ext not in valid_extensions:
            raise ValidationError(
                f'Tipo de archivo no permitido. Solo se permiten archivos: PDF, JPG, JPEG, PNG. '
                f'Archivo actual: {ext}'
            )
    except (AttributeError, TypeError, ValueError):
        # Si hay algún error al acceder al nombre o procesarlo, no validar (probablemente es un objeto vacío)
        return
