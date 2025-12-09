"""
Script para verificar experiencias de la cédula 862272
Muestra experiencias del formulario, históricas y el total combinado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_humana.settings')
django.setup()

from formapp.models import InformacionBasica, ExperienciaLaboral
from basedatosaquicali.models import ContratoHistorico
from datetime import date

# Buscar candidato
cedula = '862272'

try:
    candidato = InformacionBasica.objects.get(cedula=cedula)
    print(f'\n📋 CANDIDATO: {candidato.nombre_completo}')
    print(f'📧 Cédula: {cedula}')
    print('='*70)

    # ========================================================================
    # 1. EXPERIENCIAS DEL FORMULARIO
    # ========================================================================
    print('\n🔵 EXPERIENCIAS DEL FORMULARIO (formapp_experiencialaboral):')
    print('-'*70)
    exp_formulario = ExperienciaLaboral.objects.filter(informacion_basica=candidato)

    if exp_formulario.exists():
        total_dias_formulario = 0
        print(f'Total de registros: {exp_formulario.count()}')
        print()

        for idx, exp in enumerate(exp_formulario, 1):
            dias = (exp.fecha_terminacion - exp.fecha_inicial).days + 1
            total_dias_formulario += dias
            print(f'{idx}. {exp.cargo}')
            print(f'   Desde: {exp.fecha_inicial.strftime("%d/%m/%Y")} hasta {exp.fecha_terminacion.strftime("%d/%m/%Y")}')
            print(f'   Días: {dias}')
            print()

        anos_form = total_dias_formulario // 365
        meses_form = (total_dias_formulario % 365) // 30
        dias_form = (total_dias_formulario % 365) % 30

        print(f'📊 SUBTOTAL FORMULARIO:')
        print(f'  - Total días: {total_dias_formulario}')
        print(f'  - Equivalente: {anos_form} años, {meses_form} meses, {dias_form} días')
    else:
        print('❌ No hay experiencias en el formulario')
        total_dias_formulario = 0

    print('\n' + '='*70)

    # ========================================================================
    # 2. EXPERIENCIAS HISTÓRICAS
    # ========================================================================
    print('\n🟠 EXPERIENCIAS HISTÓRICAS (basedatosaquicali_contratohistorico):')
    print('-'*70)

    exp_historicas = ContratoHistorico.objects.filter(cedula=int(cedula)).order_by('fecha_inicio')

    if exp_historicas.exists():
        print(f'Total de registros: {exp_historicas.count()}')
        print()

        total_dias_historico_bruto = 0
        total_dias_historico_real = 0

        for idx, exp in enumerate(exp_historicas, 1):
            print(f'{idx}. {exp.contrato}')
            print(f'   Desde: {exp.fecha_inicio.strftime("%d/%m/%Y")} hasta {exp.fecha_fin.strftime("%d/%m/%Y")}')
            print(f'   Días brutos: {exp.dias_brutos}')
            print(f'   Días reales (sin traslape): {exp.dias_reales_contribuidos}')
            print(f'   Traslape: {exp.traslape}')

            total_dias_historico_bruto += exp.dias_brutos
            total_dias_historico_real += exp.dias_reales_contribuidos

        anos_hist = total_dias_historico_real // 365
        meses_hist = (total_dias_historico_real % 365) // 30
        dias_hist = (total_dias_historico_real % 365) % 30

        print(f'\n📊 SUBTOTAL HISTÓRICO:')
        print(f'  - Total días brutos: {total_dias_historico_bruto}')
        print(f'  - Total días reales (sin traslapes históricos): {total_dias_historico_real}')
        print(f'  - Equivalente: {anos_hist} años, {meses_hist} meses, {dias_hist} días')
    else:
        print('❌ No hay experiencias históricas')
        total_dias_historico_real = 0

    print('\n' + '='*70)

    # ========================================================================
    # 3. SUMA SIMPLE (SIN VERIFICAR TRASLAPES ENTRE FORMULARIO E HISTÓRICO)
    # ========================================================================
    print('\n🔢 SUMA SIMPLE (Formulario + Histórico, sin verificar traslapes entre ellos):')
    print('-'*70)
    total_simple = total_dias_formulario + total_dias_historico_real
    anos_simple = total_simple // 365
    meses_simple = (total_simple % 365) // 30
    dias_simple = (total_simple % 365) % 30

    print(f'Formulario: {total_dias_formulario:,} días')
    print(f'Histórico:  {total_dias_historico_real:,} días (ya sin traslapes internos)')
    print(f'-'*40)
    print(f'SUMA TOTAL: {total_simple:,} días')
    print(f'Equivalente: {anos_simple} años, {meses_simple} meses, {dias_simple} días')

    print('\n' + '='*70)

    # ========================================================================
    # 4. TOTAL EN LA BASE DE DATOS (CON FUSIÓN DE INTERVALOS COMPLETA)
    # ========================================================================
    print('\n✅ TOTAL GUARDADO EN BD (formapp_calculoexperiencia):')
    print('   (Combina formulario + histórico y elimina TODOS los traslapes)')
    print('-'*70)

    if hasattr(candidato, 'calculo_experiencia') and candidato.calculo_experiencia:
        calc = candidato.calculo_experiencia
        print(f'Total días:  {calc.total_dias_experiencia:,}')
        print(f'Total meses: {calc.total_meses_experiencia}')
        print(f'Total años:  {calc.total_experiencia_anos}')
        print(f'Formato:     {calc.anos_y_meses_experiencia}')

        print('\n' + '='*70)

        # Comparación
        print('\n📈 COMPARACIÓN:')
        print('-'*70)
        print(f'Suma simple:     {total_simple:,} días')
        print(f'Total BD (real): {calc.total_dias_experiencia:,} días')
        diferencia = total_simple - calc.total_dias_experiencia
        if diferencia > 0:
            print(f'Diferencia:      {diferencia} días eliminados por traslapes')
        elif diferencia < 0:
            print(f'Diferencia:      {abs(diferencia)} días adicionales (posible ajuste de cálculo)')
        else:
            print(f'Diferencia:      0 días (sin traslapes)')
    else:
        print('❌ No hay cálculo guardado en la BD')
        print('💡 Ejecuta: python manage.py recalcular_experiencias --cedula 862272')

    print('\n' + '='*70)
    print('\n✅ Consulta completada\n')

except InformacionBasica.DoesNotExist:
    print(f'\n❌ No se encontró candidato con cédula {cedula}\n')
except Exception as e:
    print(f'\n❌ Error: {e}\n')
    import traceback
    traceback.print_exc()
