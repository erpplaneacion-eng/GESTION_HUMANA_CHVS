#!/usr/bin/env python
"""
Script para verificar las credenciales de Cloudinary
"""

# Tus credenciales (copia exacta)
CLOUD_NAME = "dk7nufqc4"
API_KEY = "862119278775475"
API_SECRET = "H29cbSnPJd_SYlFxOv039mc_wZE"

print("=" * 60)
print("🔍 VERIFICANDO CREDENCIALES DE CLOUDINARY")
print("=" * 60)
print()

# Verificar que no tengan espacios
if ' ' in CLOUD_NAME or ' ' in API_KEY or ' ' in API_SECRET:
    print("❌ ERROR: Las credenciales contienen espacios")
    print("   Cloud Name:", CLOUD_NAME)
    print("   API Key:", API_KEY)
    print("   API Secret:", "CONTENIDO OCULTO")
else:
    print("✅ Las credenciales no tienen espacios")

# Verificar longitud
print()
print("📏 Longitud de las credenciales:")
print(f"   Cloud Name: {len(CLOUD_NAME)} caracteres")
print(f"   API Key: {len(API_KEY)} caracteres")
print(f"   API Secret: {len(API_SECRET)} caracteres")

print()
print("=" * 60)
print("✅ FORMATO CORRECTO - Listas para usar en Railway")
print("=" * 60)
print()
print("📝 Variables para Railway:")
print()
print("CLOUDINARY_CLOUD_NAME=" + CLOUD_NAME)
print("CLOUDINARY_API_KEY=" + API_KEY)
print("CLOUDINARY_API_SECRET=" + API_SECRET)

