"""
Comando para recalcular la experiencia total de todos los candidatos.
Combina experiencias del formulario + experiencias históricas.
"""
from django.core.management.base import BaseCommand
from formapp.models import InformacionBasica
from formapp.services import calcular_experiencia_total, obtener_experiencias_historicas


class Command(BaseCommand):
    help = 'Recalcula la experiencia total de todos los candidatos (formulario + histórico)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cedula',
            type=str,
            help='Recalcular solo para una cédula específica'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )

    def handle(self, *args, **options):
        cedula_especifica = options.get('cedula')
        verbose = options.get('verbose', False)

        # Filtrar candidatos
        if cedula_especifica:
            candidatos = InformacionBasica.objects.filter(cedula=cedula_especifica)
            if not candidatos.exists():
                self.stdout.write(self.style.ERROR(f'No se encontró candidato con cédula {cedula_especifica}'))
                return
        else:
            candidatos = InformacionBasica.objects.all()

        total = candidatos.count()
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Recalculando experiencia para {total} candidato(s)...\n'))

        procesados = 0
        con_historico = 0
        sin_historico = 0
        errores = 0

        for candidato in candidatos:
            try:
                # Obtener información previa
                exp_formulario = candidato.experiencias_laborales.count()
                exp_historicas = obtener_experiencias_historicas(candidato.cedula)
                count_historicas = len(exp_historicas)

                # Recalcular
                calculo = calcular_experiencia_total(candidato)

                # Estadísticas
                procesados += 1
                if count_historicas > 0:
                    con_historico += 1

                    if verbose:
                        self.stdout.write(
                            f'✅ {candidato.nombre_completo} (Cédula: {candidato.cedula})\n'
                            f'   📝 Formulario: {exp_formulario} exp | '
                            f'💾 Histórico: {count_historicas} exp | '
                            f'📊 Total: {calculo.anos_y_meses_experiencia}'
                        )
                else:
                    sin_historico += 1
                    if verbose:
                        self.stdout.write(
                            f'✅ {candidato.nombre_completo} (Cédula: {candidato.cedula})\n'
                            f'   📝 Solo formulario: {exp_formulario} exp | '
                            f'📊 Total: {calculo.anos_y_meses_experiencia}'
                        )

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error con {candidato.nombre_completo} (Cédula: {candidato.cedula}): {str(e)}'
                    )
                )

        # Resumen final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('\n📊 RESUMEN DE RECÁLCULO:\n'))
        self.stdout.write(f'   Total procesados: {procesados}/{total}')
        self.stdout.write(f'   ✅ Con experiencia histórica: {con_historico}')
        self.stdout.write(f'   📝 Solo formulario: {sin_historico}')
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'   ❌ Errores: {errores}'))
        self.stdout.write('\n' + '='*70)

        if errores == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ Recálculo completado exitosamente!\n'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️ Recálculo completado con algunos errores.\n'))
