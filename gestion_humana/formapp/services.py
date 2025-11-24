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
    Implementa algoritmo de fusión de intervalos para descontar traslapes de fechas.

    Args:
        informacion_basica: Instancia de InformacionBasica

    Returns:
        CalculoExperiencia: Registro con el cálculo consolidado
    """
    experiencias = informacion_basica.experiencias_laborales.all().order_by('fecha_inicial')

    if not experiencias:
        total_dias = 0
        total_meses = 0
    else:
        # Algoritmo de fusión de intervalos para eliminar traslapes
        intervalos = []
        for exp in experiencias:
            if exp.fecha_inicial and exp.fecha_terminacion:
                intervalos.append((exp.fecha_inicial, exp.fecha_terminacion))
        
        if not intervalos:
            total_dias = 0
        else:
            # Ordenar por fecha de inicio (ya ordenado por query, pero aseguramos)
            intervalos.sort(key=lambda x: x[0])
            
            merged = []
            if intervalos:
                curr_start, curr_end = intervalos[0]
                
                for i in range(1, len(intervalos)):
                    next_start, next_end = intervalos[i]
                    
                    if next_start <= curr_end:  # Hay traslape
                        # Extender el final del intervalo actual si el siguiente termina después
                        curr_end = max(curr_end, next_end)
                    else:
                        # No hay traslape, guardar intervalo actual e iniciar uno nuevo
                        merged.append((curr_start, curr_end))
                        curr_start, curr_end = next_start, next_end
                
                merged.append((curr_start, curr_end))
            
            # Calcular días totales sumando los intervalos fusionados
            total_dias = 0
            for start, end in merged:
                # Sumar 1 porque la resta de fechas da la diferencia, pero ambos días cuentan (inclusivo)
                # Ejemplo: 1 al 2 de enero = 2 días, pero 2-1 = 1.
                dias_intervalo = (end - start).days
                # Ajuste lógico para cálculos laborales: aproximación de 30 días por mes
                # Sin embargo, para precisión usamos días calendario.
                # Si queremos ser consistentes con el cálculo individual anterior (dias_experiencia)
                # debemos usar la misma lógica. El modelo usa (fin-inicio).days en views o donde se guarde.
                # Aquí usaremos days + 1 si queremos inclusivo, o days si queremos diferencia exacta.
                # La lógica estándar laboral suele ser días calendario.
                # Si fecha_terminacion es el último día trabajado:
                total_dias += dias_intervalo + 1

        # Aproximación de meses (30 días) para consistencia general
        total_meses = int(total_dias / 30)

    # Convertir a años (considerando 360 días por año laboral estándar o 12 meses)
    total_anos = round(total_meses / 12, 2)

    # Calcular años y meses para formato legible
    anos = total_meses // 12
    meses_restantes = total_meses % 12
    dias_restantes = total_dias % 30 # Aproximado
    
    if dias_restantes > 0:
        # Si sobran días que no completan un mes
        anos_y_meses = f"{anos} años, {meses_restantes} meses y {dias_restantes} días"
    else:
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
