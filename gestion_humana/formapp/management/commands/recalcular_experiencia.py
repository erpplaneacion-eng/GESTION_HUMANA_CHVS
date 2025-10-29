from django.core.management.base import BaseCommand
from formapp.models import InformacionBasica
from formapp.views import calcular_experiencia_total


class Command(BaseCommand):
    help = 'Recalcula la experiencia total para todos los registros existentes'

    def handle(self, *args, **options):
        personas = InformacionBasica.objects.all()
        total = personas.count()
        procesados = 0
        con_experiencia = 0

        self.stdout.write(self.style.SUCCESS(f'Iniciando recálculo de experiencia para {total} personas...'))

        for persona in personas:
            if persona.experiencias_laborales.exists():
                calcular_experiencia_total(persona)
                con_experiencia += 1
                self.stdout.write(f'  OK - {persona.nombre_completo} ({persona.cedula})')
            procesados += 1

        self.stdout.write(self.style.SUCCESS(f'\n¡Proceso completado!'))
        self.stdout.write(f'  Total procesados: {procesados}')
        self.stdout.write(f'  Con experiencia laboral: {con_experiencia}')
        self.stdout.write(f'  Sin experiencia laboral: {procesados - con_experiencia}')
