#!/usr/bin/env python
"""
Script para verificar que Cloudinary está configurado correctamente
Ejecutar: python verificar_cloudinary.py
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'gestion_humana'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_humana.settings')

import django
django.setup()

from django.conf import settings
import cloudinary

def verificar_cloudinary():
    """Verifica la configuración de Cloudinary"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE CLOUDINARY")
    print("=" * 60)
    print()
    
    # Verificar imports
    print("1️⃣ Verificando imports...")
    try:
        import cloudinary
        import cloudinary_storage
        print("   ✅ cloudinary importado correctamente")
        print("   ✅ cloudinary_storage importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando: {e}")
        return False
    print()
    
    # Verificar installed apps
    print("2️⃣ Verificando INSTALLED_APPS...")
    if 'cloudinary_storage' in settings.INSTALLED_APPS:
        print("   ✅ cloudinary_storage en INSTALLED_APPS")
    else:
        print("   ❌ cloudinary_storage NO está en INSTALLED_APPS")
        return False
    
    if 'cloudinary' in settings.INSTALLED_APPS:
        print("   ✅ cloudinary en INSTALLED_APPS")
    else:
        print("   ❌ cloudinary NO está en INSTALLED_APPS")
        return False
    print()
    
    # Verificar configuración de CLOUDINARY_STORAGE
    print("3️⃣ Verificando configuración de credenciales...")
    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
    api_key = settings.CLOUDINARY_STORAGE.get('API_KEY', '')
    api_secret = settings.CLOUDINARY_STORAGE.get('API_SECRET', '')
    
    if cloud_name:
        print(f"   ✅ Cloud Name: {cloud_name[:10]}...")
    else:
        print("   ⚠️  Cloud Name: NO configurado")
    
    if api_key:
        print(f"   ✅ API Key: {api_key[:10]}...")
    else:
        print("   ⚠️  API Key: NO configurado")
    
    if api_secret:
        print(f"   ✅ API Secret: Configurado (oculto por seguridad)")
    else:
        print("   ⚠️  API Secret: NO configurado")
    
    if not (cloud_name and api_key and api_secret):
        print()
        print("   ⚠️  ADVERTENCIA: Faltan credenciales de Cloudinary")
        print("   📝 Ve a Railway y configura las variables:")
        print("      - CLOUDINARY_CLOUD_NAME")
        print("      - CLOUDINARY_API_KEY")
        print("      - CLOUDINARY_API_SECRET")
        print()
        print("   💡 Ver GUIA_CLOUDINARY.md para más información")
        print()
    print()
    
    # Verificar configuración de STORAGES
    print("4️⃣ Verificando configuración de STORAGES...")
    default_backend = settings.STORAGES.get('default', {}).get('BACKEND', '')
    if 'cloudinary' in default_backend.lower():
        print(f"   ✅ Default storage: {default_backend}")
    else:
        print(f"   ❌ Default storage NO usa Cloudinary: {default_backend}")
        return False
    
    staticfiles_backend = settings.STORAGES.get('staticfiles', {}).get('BACKEND', '')
    if 'whitenoise' in staticfiles_backend.lower():
        print(f"   ✅ Static files: {staticfiles_backend}")
    else:
        print(f"   ⚠️  Static files: {staticfiles_backend}")
    print()
    
    # Verificar configuración de MEDIA
    print("5️⃣ Verificando configuración de MEDIA...")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print()
    
    # Verificar si Cloudinary está configurado
    print("6️⃣ Verificando conexión con Cloudinary...")
    if cloud_name and api_key and api_secret:
        try:
            # Probar configuración de cloudinary
            config = cloudinary.config()
            if config.cloud_name:
                print(f"   ✅ Cloudinary configurado: {config.cloud_name}")
                print("   ✅ Credenciales válidas")
            else:
                print("   ❌ Cloudinary no está configurado")
                return False
        except Exception as e:
            print(f"   ⚠️  Error verificando Cloudinary: {e}")
            print("   💡 Esto puede ser normal si las credenciales no están configuradas")
    else:
        print("   ⚠️  No se puede verificar conexión sin credenciales")
    print()
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print()
    
    has_credentials = cloud_name and api_key and api_secret
    
    if has_credentials:
        print("✅ Cloudinary está CONFIGURADO y LISTO")
        print()
        print("📝 Próximos pasos:")
        print("   1. Reinicia tu aplicación en Railway")
        print("   2. Prueba subir un certificado desde /formapp/registro/")
        print("   3. Verifica en Cloudinary Dashboard que el archivo aparezca")
    else:
        print("⚠️  Cloudinary está configurado pero FALTAN CREDENCIALES")
        print()
        print("📝 Pasos siguientes:")
        print("   1. Ve a tu Railway Dashboard")
        print("   2. Agrega las 3 variables de entorno de Cloudinary")
        print("   3. Reinicia el servicio")
        print("   4. Ejecuta este script nuevamente para verificar")
    print()
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        verificar_cloudinary()
    except Exception as e:
        print(f"❌ Error ejecutando verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

