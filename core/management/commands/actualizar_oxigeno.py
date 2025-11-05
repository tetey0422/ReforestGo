from django.core.management.base import BaseCommand
from core.models import Siembra
from django.utils import timezone
from django.db.models import Sum
import traceback


class Command(BaseCommand):
    help = 'Actualiza el cálculo de oxígeno generado para todas las siembras validadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del proceso',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)

        self.stdout.write(self.style.SUCCESS('🌿 Iniciando actualización de oxígeno...'))

        # Obtener todas las siembras validadas
        siembras_validadas = Siembra.objects.filter(estado='validada')
        total = siembras_validadas.count()

        self.stdout.write(f'📊 Total de siembras validadas: {total}')

        actualizadas = 0
        errores = 0

        for siembra in siembras_validadas.iterator():
            try:
                oxigeno_anterior = siembra.oxigeno_generado
                # calcular_oxigeno() guarda internamente el objeto
                siembra.calcular_oxigeno()

                if verbose:
                    especie = siembra.especie or 'Sin especie'
                    self.stdout.write(
                        f'  ✓ Siembra #{siembra.id} - {especie}: '
                        f'{oxigeno_anterior} → {siembra.oxigeno_generado} kg O2/año'
                    )

                actualizadas += 1

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error en siembra #{siembra.id}: {str(e)}')
                )
                if verbose:
                    for l in traceback.format_exc().splitlines():
                        self.stdout.write(self.style.ERROR('    ' + l))

        # Estadísticas finales
        self.stdout.write(self.style.SUCCESS('\n📈 Resumen de actualización:'))
        self.stdout.write(f'  ✅ Siembras procesadas: {actualizadas}')
        self.stdout.write(f'  ❌ Errores: {errores}')

        # Calcular total de oxígeno y CO2
        totales = Siembra.objects.filter(estado='validada').aggregate(
            oxigeno_total=Sum('oxigeno_generado'),
            co2_total=Sum('co2_absorbido')
        )

        oxigeno_total = float(totales['oxigeno_total'] or 0)
        co2_total = float(totales['co2_total'] or 0)

        self.stdout.write(f'\n🌍 Impacto ambiental total:')
        self.stdout.write(f'  💨 Oxígeno generado: {oxigeno_total:.2f} kg/año')
        self.stdout.write(f'  🌿 CO2 absorbido: {co2_total:.2f} kg/año')
        # Aproximación: 4600 kg CO2 = emisiones anuales promedio de un auto
        equivalentes = (co2_total / 4600) if co2_total else 0
        self.stdout.write(f'  🚗 Equivalente a: {equivalentes:.2f} autos fuera de circulación')

        self.stdout.write(self.style.SUCCESS('\n✨ Actualización completada exitosamente!'))
