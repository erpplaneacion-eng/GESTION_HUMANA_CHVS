"""
Servicios de lógica de negocio para formapp.
Extracción de funciones de utilidad y lógica de negocio desde views.py
"""
import os
import json
import base64
import logging
import threading
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
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


def get_gmail_service():
    """Helper para obtener servicio autenticado de Gmail"""
    try:
        token_data = None
        gmail_token_json = os.getenv('GMAIL_TOKEN_JSON')
        
        if gmail_token_json:
            try:
                token_data = json.loads(gmail_token_json)
            except json.JSONDecodeError:
                return None

        if not token_data:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            token_path = os.path.join(BASE_DIR, 'token.json')
            if os.path.exists(token_path):
                with open(token_path, 'r') as token_file:
                    token_data = json.load(token_file)
            else:
                return None

        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes', SCOPES)
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        logger.error(f'Error obteniendo servicio Gmail: {str(e)}')
        return None


def enviar_correo_confirmacion(informacion_basica):
    """
    Envía correo de confirmación al usuario que completó el formulario usando Gmail API.
    """
    try:
        service = get_gmail_service()
        if not service:
            logger.error("No se pudo inicializar el servicio de Gmail")
            return False

        fecha_colombia = datetime.now(COLOMBIA_TZ)
        context = {
            'nombre_completo': informacion_basica.nombre_completo,
            'cedula': informacion_basica.cedula,
            'correo': informacion_basica.correo,
            'telefono': informacion_basica.telefono,
            'fecha_registro': fecha_colombia.strftime('%d/%m/%Y %H:%M'),
        }

        html_message = render_to_string('formapp/email_confirmacion.html', context)

        message = MIMEMultipart('alternative')
        message['To'] = informacion_basica.correo
        message['From'] = f'Gestión Humana CAVJP <{settings.DEFAULT_FROM_EMAIL}>'
        message['Subject'] = 'Confirmación de Registro - Gestión Humana CAVJP'
        html_part = MIMEText(html_message, 'html', 'utf-8')
        message.attach(html_part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}

        service.users().messages().send(userId='me', body=send_message).execute()
        logger.info(f'Correo enviado exitosamente a {informacion_basica.correo}')
        return True

    except Exception as e:
        logger.error(f'Error al enviar correo a {informacion_basica.correo}: {str(e)}')
        return False


def enviar_correo_solicitud_correccion(informacion_basica, mensaje_observacion, request=None):
    """
    Genera un token, actualiza el estado y envía correo solicitando corrección.
    
    Args:
        informacion_basica: Instancia del modelo
        mensaje_observacion: Texto con las instrucciones de corrección
        request: Objeto request para construir la URL absoluta
    """
    try:
        # 1. Generar token y expiración (48 horas)
        token = uuid.uuid4()
        expiracion = timezone.now() + timedelta(hours=48)
        
        # 2. Actualizar registro
        informacion_basica.token_correccion = token
        informacion_basica.token_expiracion = expiracion
        informacion_basica.estado = 'PENDIENTE_CORRECCION'
        informacion_basica.save(update_fields=['token_correccion', 'token_expiracion', 'estado'])
        
        # 3. Construir enlace
        if request:
            scheme = request.scheme
            host = request.get_host()
            enlace = f"{scheme}://{host}/formapp/actualizar-datos/{token}/"
        else:
            # Fallback si no hay request (ej. tarea programada)
            enlace = f"https://gestionhumanacavijup.up.railway.app/formapp/actualizar-datos/{token}/"

        # 4. Enviar correo
        service = get_gmail_service()
        if not service:
            return False

        context = {
            'nombre_completo': informacion_basica.nombre_completo,
            'mensaje_observacion': mensaje_observacion,
            'enlace_correccion': enlace,
        }

        html_message = render_to_string('formapp/email_solicitud_correccion.html', context)

        message = MIMEMultipart('alternative')
        message['To'] = informacion_basica.correo
        message['From'] = f'Gestión Humana CAVJP <{settings.DEFAULT_FROM_EMAIL}>'
        message['Subject'] = 'Solicitud de Corrección - Gestión Humana CAVJP'
        html_part = MIMEText(html_message, 'html', 'utf-8')
        message.attach(html_part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}

        service.users().messages().send(userId='me', body=send_message).execute()
        logger.info(f'Correo de corrección enviado a {informacion_basica.correo}')
        return True

    except Exception as e:
        logger.error(f'Error enviando solicitud de corrección: {str(e)}')
        return False


def enviar_correo_notificacion_admin(informacion_basica, comentarios_candidato=''):
    """
    Envía notificación al administrador cuando el candidato corrige su información.

    Args:
        informacion_basica: Instancia del modelo
        comentarios_candidato: Comentarios del candidato sobre las correcciones
    """
    try:
        service = get_gmail_service()
        if not service:
            logger.error("No se pudo inicializar el servicio de Gmail")
            return False

        # Email del administrador (desde settings o configuración)
        admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)

        context = {
            'nombre_completo': informacion_basica.nombre_completo,
            'cedula': informacion_basica.cedula,
            'correo': informacion_basica.correo,
            'comentarios_candidato': comentarios_candidato,
            'enlace_revision': f'https://gestionhumanacavijup.up.railway.app/formapp/admin/applicants/{informacion_basica.pk}/',
        }

        html_message = render_to_string('formapp/email_notificacion_admin.html', context)

        message = MIMEMultipart('alternative')
        message['To'] = admin_email
        message['From'] = f'Sistema Gestión Humana <{settings.DEFAULT_FROM_EMAIL}>'
        message['Subject'] = f'Corrección Completada - {informacion_basica.nombre_completo}'
        html_part = MIMEText(html_message, 'html', 'utf-8')
        message.attach(html_part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}

        service.users().messages().send(userId='me', body=send_message).execute()
        logger.info(f'Notificación enviada al admin sobre corrección de {informacion_basica.nombre_completo}')
        return True

    except Exception as e:
        logger.error(f'Error enviando notificación al admin: {str(e)}')
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
