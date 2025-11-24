"""
Servicios de lógica de negocio para formapp.
Extracción de funciones de utilidad y lógica de negocio desde views.py
"""
import os
import json
import base64
import logging
import threading
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz

from .models import CalculoExperiencia

logger = logging.getLogger(__name__)

# Zona horaria de Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def calcular_experiencia_total(informacion_basica):
    """
    Calcula automáticamente la experiencia total de una persona.

    Args:
        informacion_basica: Instancia de InformacionBasica

    Returns:
        CalculoExperiencia: Registro con el cálculo consolidado

    Esta función suma todos los meses y días de experiencia laboral,
    convierte a años y genera un formato legible.
    """
    experiencias = informacion_basica.experiencias_laborales.all()

    total_meses = sum(exp.meses_experiencia for exp in experiencias)
    total_dias = sum(exp.dias_experiencia for exp in experiencias)

    # Convertir a años (considerando 12 meses por año)
    total_anos = round(total_meses / 12, 2)

    # Calcular años y meses para formato legible
    anos = total_meses // 12
    meses_restantes = total_meses % 12
    anos_y_meses = f"{anos} años y {meses_restantes} meses"

    # Crear o actualizar el registro de cálculo
    calculo, created = CalculoExperiencia.objects.update_or_create(
        informacion_basica=informacion_basica,
        defaults={
            'total_meses_experiencia': total_meses,
            'total_dias_experiencia': total_dias,
            'total_experiencia_anos': total_anos,
            'anos_y_meses_experiencia': anos_y_meses,
        }
    )
    return calculo


def enviar_correo_confirmacion(informacion_basica):
    """
    Envía correo de confirmación al usuario que completó el formulario usando Gmail API.

    Args:
        informacion_basica: Instancia de InformacionBasica

    Returns:
        bool: True si el correo se envió exitosamente, False si falló

    Esta función:
    1. Carga credenciales desde variable de entorno (Railway) o archivo local
    2. Renderiza un template HTML personalizado
    3. Envía el correo mediante Gmail API
    4. Maneja el refresh automático de tokens
    """
    try:
        # Cargar credenciales: primero de variable de entorno (Railway) o archivo (desarrollo local)
        token_data = None

        # Intentar cargar desde variable de entorno (Railway)
        gmail_token_json = os.getenv('GMAIL_TOKEN_JSON')
        if gmail_token_json:
            try:
                token_data = json.loads(gmail_token_json)
                logger.info('Credenciales de Gmail cargadas desde variable de entorno')
            except json.JSONDecodeError as e:
                logger.error(f'Error parseando GMAIL_TOKEN_JSON: {str(e)}')
                return False

        # Si no hay variable de entorno, intentar cargar desde archivo (desarrollo local)
        if not token_data:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            token_path = os.path.join(BASE_DIR, 'token.json')

            if os.path.exists(token_path):
                try:
                    with open(token_path, 'r') as token_file:
                        token_data = json.load(token_file)
                    logger.info(f'Credenciales de Gmail cargadas desde {token_path}')
                except Exception as e:
                    logger.error(f'Error leyendo token.json: {str(e)}')
                    return False
            else:
                logger.error(f'No se encontró token.json en {token_path} ni variable GMAIL_TOKEN_JSON')
                return False

        # Crear credenciales desde el token
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes', SCOPES)
        )

        # Refrescar el token si es necesario
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Construir el servicio de Gmail
        service = build('gmail', 'v1', credentials=creds)

        # Preparar contexto para el template - usar zona horaria de Colombia
        fecha_colombia = datetime.now(COLOMBIA_TZ)
        context = {
            'nombre_completo': informacion_basica.nombre_completo,
            'cedula': informacion_basica.cedula,
            'correo': informacion_basica.correo,
            'telefono': informacion_basica.telefono,
            'fecha_registro': fecha_colombia.strftime('%d/%m/%Y %H:%M'),
        }

        # Renderizar template HTML
        html_message = render_to_string('formapp/email_confirmacion.html', context)

        # Crear mensaje de correo con nombre del remitente
        message = MIMEMultipart('alternative')
        message['To'] = informacion_basica.correo
        message['From'] = f'Gestión Humana CHVS <{settings.DEFAULT_FROM_EMAIL}>'
        message['Subject'] = 'Confirmación de Registro - Gestión Humana CHVS'

        # Adjuntar contenido HTML
        html_part = MIMEText(html_message, 'html', 'utf-8')
        message.attach(html_part)

        # Codificar el mensaje en base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}

        # Enviar correo
        service.users().messages().send(userId='me', body=send_message).execute()

        logger.info(f'Correo enviado exitosamente a {informacion_basica.correo} vía Gmail API')
        return True

    except Exception as e:
        logger.error(f'Error al enviar correo a {informacion_basica.correo}: {str(e)}')
        return False


def enviar_correo_async(informacion_basica):
    """
    Envía correo de confirmación de manera asíncrona en un thread separado.

    Args:
        informacion_basica: Instancia de InformacionBasica

    Esta función no bloquea la respuesta del formulario.
    Los errores se logean pero no detienen el proceso principal.
    """
    def enviar_correo_thread():
        try:
            enviar_correo_confirmacion(informacion_basica)
        except Exception as e:
            logger.error(f'Error en thread de correo: {str(e)}')

    thread = threading.Thread(target=enviar_correo_thread)
    thread.daemon = True
    thread.start()
