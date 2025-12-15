from django.core.exceptions import ValidationError
import os

# Importar magic de manera compatible con Windows y Linux
try:
    # Intenta importar python-magic-bin (Windows)
    import magic
except ImportError:
    try:
        # Si falla, intenta importar python-magic (Linux)
        import magic
    except ImportError:
        # Si ninguno está disponible, magic será None
        magic = None

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

    # IMPORTANTE: Si es un FieldFile existente (ya está en Cloudinary/storage), NO validar
    # Archivos ya subidos ya pasaron validación anteriormente
    if hasattr(value, '_committed') and value._committed:
        return  # Archivo ya existente, omitir validación

    # También verificar si tiene una URL (indica que ya está almacenado)
    if hasattr(value, 'url'):
        try:
            _ = value.url
            return  # Archivo ya existente, omitir validación
        except:
            pass
    
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

    # IMPORTANTE: Si es un FieldFile existente (ya está en Cloudinary/storage), NO validar
    # Esto previene errores al editar registros existentes sin cambiar archivos
    # Un FieldFile existente tiene el atributo 'instance' o '_committed' = True
    if hasattr(value, '_committed') and value._committed:
        return  # Archivo ya existente, omitir validación

    # También verificar si tiene una URL (indica que ya está almacenado)
    if hasattr(value, 'url'):
        try:
            # Si puede obtener URL sin error, es un archivo ya almacenado
            _ = value.url
            return  # Archivo ya existente, omitir validación
        except:
            pass  # No tiene URL válida, continuar validación

    try:
        # Obtener extensión del archivo
        name = str(value.name) if value.name else ''
        if not name:
            return

        # FILTRO 1: Rechazar archivos de metadatos de macOS (._*)
        # Estos son archivos "AppleDouble" que macOS crea automáticamente
        filename_only = os.path.basename(name)
        if filename_only.startswith('._'):
            raise ValidationError(
                'Archivo de metadatos de macOS detectado. '
                'Por favor, sube el archivo original sin comprimir. '
                'Si estás en Mac, evita comprimir archivos o usa "Comprimir" desde la terminal con: '
                'zip -r archivo.zip carpeta/ -x "*/.*" -x ".*"'
            )

        ext = os.path.splitext(name)[1].lower()

        # FILTRO 2: Si es un archivo ya subido a Cloudinary (URL sin extensión)
        # Cloudinary a veces devuelve URLs como: /media/certificados/archivo_xyz123
        # En este caso, confiar que la validación ya se hizo al subir
        if not ext:
            # Si tiene URL de Cloudinary o parece ser un archivo ya subido, permitir
            if 'cloudinary' in name.lower() or '/' in name or len(name) > 50:
                return  # Es un archivo ya subido a Cloudinary, omitir validación

            # Si no tiene extensión y no parece ser de Cloudinary, rechazar
            raise ValidationError(
                'El archivo no tiene extensión válida. '
                'Por favor, asegúrate de subir un archivo con extensión .pdf, .jpg, .jpeg o .png'
            )

        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.heic', '.heif']

        if ext not in valid_extensions:
            raise ValidationError(
                f'Tipo de archivo no permitido. Solo se permiten archivos: PDF, JPG, JPEG, PNG, HEIC (iPhone). '
                f'Extensión detectada: {ext}'
            )
    except (AttributeError, TypeError, ValueError):
        # Si hay algún error al acceder al nombre o procesarlo, no validar (probablemente es un objeto vacío)
        return

def validate_file_mime(value):
    """
    Valida que el archivo sea realmente un PDF, JPG o PNG basándose en su contenido MIME type,
    no solo en la extensión del archivo. Esto previene que archivos maliciosos sean disfrazados
    con extensiones válidas (ej: malware.exe renombrado como certificado.pdf)
    """
    # Si no hay archivo (None, False, o cadena vacía), no validar
    if not value or value == '':
        return

    # Si el archivo no tiene nombre, no validar
    if not hasattr(value, 'name'):
        return

    # Si el nombre está vacío o es None, no validar
    if not value.name or value.name == '':
        return

    # Si el archivo parece ser un objeto vacío (típico en formsets cuando no se envía archivo)
    if hasattr(value, 'size') and value.size == 0:
        return

    # IMPORTANTE: Si es un FieldFile existente (ya está en Cloudinary/storage), NO validar
    # Esto previene errores al editar registros existentes sin cambiar archivos
    if hasattr(value, '_committed') and value._committed:
        return  # Archivo ya existente, omitir validación

    # También verificar si tiene una URL (indica que ya está almacenado)
    if hasattr(value, 'url'):
        try:
            _ = value.url
            return  # Archivo ya existente, omitir validación
        except:
            pass

    # Filtrar archivos de metadatos de macOS (._*)
    name = str(value.name) if value.name else ''
    filename_only = os.path.basename(name)
    if filename_only.startswith('._'):
        # Ya se rechazó en validate_file_extension, no validar MIME
        return

    # Si es un archivo ya subido a Cloudinary (URL sin extensión), omitir validación MIME
    if name and ('cloudinary' in name.lower() or len(name) > 50):
        return

    # Si magic no está disponible, solo validar por magic bytes básicos
    if magic is None:
        return _validate_file_magic_bytes(value)

    try:
        # Leer primeros 2048 bytes para detectar tipo MIME
        # Guardar posición actual del cursor
        original_position = value.tell() if hasattr(value, 'tell') else 0

        # Leer encabezado del archivo
        file_header = value.read(2048)

        # Restaurar posición del cursor al inicio para no afectar procesamiento posterior
        if hasattr(value, 'seek'):
            value.seek(original_position)

        # Detectar MIME type real del archivo
        mime = magic.from_buffer(file_header, mime=True)

        # Lista de MIME types permitidos
        allowed_mimes = [
            'application/pdf',           # PDF
            'image/jpeg',                # JPEG/JPG
            'image/png',                 # PNG
            'image/heic',                # HEIC (iPhone iOS 11+)
            'image/heif',                # HEIF (variante de HEIC)
            'image/heic-sequence',       # HEIC secuencia (Live Photos)
            'image/heif-sequence',       # HEIF secuencia
        ]

        if mime not in allowed_mimes:
            raise ValidationError(
                f'Tipo de archivo no válido. '
                f'Se esperaba: PDF, JPG o PNG. '
                f'Se detectó: {mime}. '
                f'Por favor, asegúrese de que el archivo no haya sido renombrado y sea realmente un documento válido.'
            )

    except (AttributeError, TypeError, ValueError, IOError) as e:
        # Si hay algún error al leer el archivo, no validar (probablemente es un objeto vacío)
        # Nota: En producción esto podría ser más estricto
        return

def _validate_file_magic_bytes(value):
    """
    Validación básica usando magic bytes cuando python-magic no está disponible
    """
    try:
        # Guardar posición actual del cursor
        original_position = value.tell() if hasattr(value, 'tell') else 0

        # Leer primeros bytes del archivo
        file_header = value.read(32)

        # Restaurar posición del cursor
        if hasattr(value, 'seek'):
            value.seek(original_position)

        # Verificar magic bytes conocidos
        is_pdf = file_header.startswith(b'%PDF')
        is_png = file_header.startswith(b'\x89PNG\r\n\x1a\n')
        is_jpeg = file_header.startswith(b'\xff\xd8\xff')
        # HEIC/HEIF: Buscar 'ftyp' en los primeros 32 bytes (offset 4-8)
        # HEIC típicamente tiene 'ftypheic' o 'ftypheif' o 'ftypmif1'
        is_heic = b'ftyp' in file_header[0:32] and (
            b'heic' in file_header[0:32] or
            b'heif' in file_header[0:32] or
            b'mif1' in file_header[0:32]
        )

        if not (is_pdf or is_png or is_jpeg or is_heic):
            raise ValidationError(
                'Tipo de archivo no válido. '
                'Se esperaba: PDF, JPG, PNG o HEIC (iPhone). '
                'Por favor, asegúrese de que el archivo sea realmente un documento válido.'
            )

    except (AttributeError, TypeError, ValueError, IOError):
        # Si hay error al leer, permitir que pase (será validado por extensión)
        return
