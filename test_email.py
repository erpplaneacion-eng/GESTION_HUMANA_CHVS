"""
Script de prueba para verificar el envio de correos electronicos con Resend
Ejecutar desde la raiz del proyecto: python test_email.py
"""

import os
import sys
import django

# Agregar el directorio al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gestion_humana'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_humana.settings')
django.setup()

from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
import resend

def test_envio_correo():
    """Prueba el envio de correo con datos de ejemplo usando Resend"""

    print("=" * 60)
    print("PRUEBA DE ENVIO DE CORREOS ELECTRONICOS CON RESEND")
    print("=" * 60)
    print()

    # Verificar configuracion
    print("Configuracion actual:")
    print(f"   RESEND_API_KEY: {'*' * 10 if settings.RESEND_API_KEY else 'NO CONFIGURADO'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

    if not settings.RESEND_API_KEY:
        print(" ERROR: La API key de Resend no esta configurada")
        print("   Por favor configura RESEND_API_KEY en el .env")
        print()
        print(" Pasos para obtener tu API key:")
        print("   1. Registrate en https://resend.com")
        print("   2. Ve a API Keys en el dashboard")
        print("   3. Crea una nueva API key")
        print("   4. Agregala al archivo .env como RESEND_API_KEY=re_...")
        return False

    # Configurar Resend
    resend.api_key = settings.RESEND_API_KEY

    # Datos de prueba
    datos_prueba = {
        'nombre_completo': 'PREZ GMEZ JUAN CARLOS',
        'cedula': '1234567890',
        'correo': 'diegoalgtr1@gmail.com',  # Correo de destino
        'telefono': '3001234567',
        'fecha_registro': datetime.now().strftime('%d/%m/%Y %H:%M'),
    }

    print(" Datos de prueba:")
    for key, value in datos_prueba.items():
        print(f"   {key}: {value}")
    print()

    try:
        print(" Generando template HTML...")

        # Renderizar template HTML
        html_message = render_to_string('formapp/email_confirmacion.html', datos_prueba)

        print(" Template generado correctamente")
        print()
        print(" Enviando correo via Resend API...")
        print(f"   De: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   Para: {datos_prueba['correo']}")
        print(f"   Asunto: [PRUEBA] Confirmacion de Registro - Gestion Humana CHVS")
        print()

        # Enviar correo con Resend
        params = {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [datos_prueba['correo']],
            "subject": "[PRUEBA] Confirmacion de Registro - Gestion Humana CHVS",
            "html": html_message,
        }

        response = resend.Emails.send(params)

        print("=" * 60)
        print(" CORREO ENVIADO EXITOSAMENTE!")
        print("=" * 60)
        print()
        print(f" ID del correo: {response.get('id', 'N/A')}")
        print(f" Revisa la bandeja de entrada de: {datos_prueba['correo']}")
        print("   (Tambien revisa la carpeta de SPAM por si acaso)")
        print()
        print(" La configuracion de correos con Resend esta funcionando correctamente")
        print()
        return True

    except Exception as e:
        print("=" * 60)
        print(" ERROR AL ENVIAR CORREO")
        print("=" * 60)
        print()
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print()
        print(" Posibles causas:")
        print("   1. API key incorrecta o invalida")
        print("   2. El correo remitente no esta verificado en Resend")
        print("   3. Problema de conexion a internet")
        print("   4. Limite de correos alcanzado (3000/mes en plan gratuito)")
        print()
        print(" Nota: El correo remitente debe estar verificado en Resend")
        print("   Ve a tu dashboard de Resend > Domains para verificar tu dominio")
        print()
        return False

if __name__ == '__main__':
    try:
        test_envio_correo()
    except KeyboardInterrupt:
        print("\n\n  Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n\n Error inesperado: {e}")
