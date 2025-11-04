#!/usr/bin/env python
"""
Script de prueba para generar un PDF ANEXO 11 de ejemplo
"""
import os
import sys
import django

# Configurar Django
# Añadir el directorio gestion_humana al path
gestion_humana_dir = os.path.join(os.path.dirname(__file__), 'gestion_humana')
sys.path.insert(0, gestion_humana_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_humana.settings')
django.setup()

from formapp.models import InformacionBasica
from formapp.views import generar_anexo11_pdf

def main():
    """Genera un PDF ANEXO 11 de prueba"""

    # Verificar si hay registros en la base de datos
    total_registros = InformacionBasica.objects.count()

    print(f"\n{'='*60}")
    print(f"   GENERADOR DE PDF ANEXO 11 - PRUEBA")
    print(f"{'='*60}")
    print(f"\nTotal de registros en la base de datos: {total_registros}")

    if total_registros == 0:
        print("\n[!] No hay registros en la base de datos.")
        print("\nCreando un registro de ejemplo...")

        # Crear un registro de ejemplo
        from datetime import date
        from formapp.models import ExperienciaLaboral, InformacionAcademica, CalculoExperiencia

        # Crear información básica
        ejemplo = InformacionBasica.objects.create(
            nombre_completo="Juan Carlos Pérez González",
            cedula="1234567890",
            genero="Masculino",
            tipo_via="Calle",
            numero_via="45",
            numero_casa="23-15",
            complemento_direccion="Apto 301",
            barrio="Centro",
            telefono="3001234567",
            correo="juan.perez@example.com",
            base_anexo_11="PROFESIONAL PSICOSOCIAL",
            perfil="Profesional en Trabajo Social",
            area_conocimiento="Ciencias Sociales",
            profesion="Trabajador Social",
            observacion="Excelente desempeño en proyectos sociales"
        )

        # Crear experiencia laboral
        exp1 = ExperienciaLaboral.objects.create(
            informacion_basica=ejemplo,
            fecha_inicial=date(2020, 1, 15),
            fecha_terminacion=date(2022, 6, 30),
            cargo="Trabajador Social",
            cargo_anexo_11="PROFESIONAL PSICOSOCIAL",
            objeto_contractual="Atención psicosocial a familias vulnerables",
            funciones="Realizar visitas domiciliarias, elaborar diagnósticos sociales, diseñar planes de intervención",
            meses_experiencia=29,
            dias_experiencia=897
        )

        exp2 = ExperienciaLaboral.objects.create(
            informacion_basica=ejemplo,
            fecha_inicial=date(2022, 8, 1),
            fecha_terminacion=date(2024, 10, 31),
            cargo="Coordinador de Programas Sociales",
            cargo_anexo_11="COORDINADOR PSICOSOCIAL",
            objeto_contractual="Coordinación de programas de seguridad alimentaria",
            funciones="Coordinar equipos de trabajo, supervisar ejecución de proyectos, elaborar informes",
            meses_experiencia=27,
            dias_experiencia=822
        )

        # Crear información académica
        InformacionAcademica.objects.create(
            informacion_basica=ejemplo,
            profesion="Trabajo Social",
            universidad="Universidad del Valle",
            tarjeta_profesional="Tarjeta Profesional",
            numero_tarjeta_resolucion="TS-12345",
            fecha_grado=date(2019, 12, 15),
            fecha_expedicion=date(2020, 1, 20),
            meses_experiencia_profesion=60
        )

        # Calcular experiencia total
        CalculoExperiencia.objects.create(
            informacion_basica=ejemplo,
            total_meses_experiencia=56,
            total_dias_experiencia=1719,
            total_experiencia_anos=4.67,
            anos_y_meses_experiencia="4 años y 8 meses"
        )

        print(f"[OK] Registro de ejemplo creado: {ejemplo.nombre_completo}")

    else:
        # Usar el primer registro disponible
        ejemplo = InformacionBasica.objects.first()
        print(f"\n[OK] Usando registro existente: {ejemplo.nombre_completo}")

    print(f"\n{'='*60}")
    print(f"   DATOS DEL REGISTRO")
    print(f"{'='*60}")
    print(f"Nombre: {ejemplo.nombre_completo}")
    print(f"Cédula: {ejemplo.cedula}")
    print(f"Correo: {ejemplo.correo}")
    print(f"Cargo Anexo 11: {ejemplo.base_anexo_11 or 'No especificado'}")

    # Contar relaciones
    experiencias = ejemplo.experiencias_laborales.count()
    academica = ejemplo.formacion_academica.count()
    posgrados = ejemplo.posgrados.count()

    print(f"\nExperiencias laborales: {experiencias}")
    print(f"Formación académica: {academica}")
    print(f"Posgrados: {posgrados}")

    # Generar PDF
    print(f"\n{'='*60}")
    print(f"   GENERANDO PDF ANEXO 11")
    print(f"{'='*60}")

    try:
        pdf_buffer = generar_anexo11_pdf(ejemplo)

        # Guardar el PDF en el directorio actual
        output_filename = f"ANEXO_11_{ejemplo.nombre_completo.replace(' ', '_')}_EJEMPLO.pdf"
        output_path = os.path.join(os.path.dirname(__file__), output_filename)

        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        print(f"\n[OK] PDF generado exitosamente!")
        print(f"[*] Archivo guardado en: {output_path}")
        print(f"[*] Tamano: {len(pdf_buffer.getvalue())} bytes")

    except Exception as e:
        print(f"\n[ERROR] Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    print(f"\n{'='*60}")
    print(f"   PRUEBA COMPLETADA")
    print(f"{'='*60}\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
