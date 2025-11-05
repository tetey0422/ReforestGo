"""
Comando de gestión para generar zonas automáticas a partir de siembras existentes
Uso: python manage.py generar_zonas_automaticas
"""
from django.core.management.base import BaseCommand
from core.models import Siembra, Zona
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2


class Command(BaseCommand):
    help = 'Genera zonas automáticas donde hay más de 10 árboles en un radio de 1km'

    def add_arguments(self, parser):
        parser.add_argument(
            '--radio',
            type=float,
            default=1.0,
            help='Radio de búsqueda en kilómetros (por defecto: 1.0)'
        )
        parser.add_argument(
            '--minimo',
            type=int,
            default=10,
            help='Número mínimo de árboles para crear zona (por defecto: 10)'
        )

    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula distancia en km usando Haversine"""
        R = 6371
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def handle(self, *args, **options):
        radio_busqueda = options['radio']
        minimo_arboles = options['minimo']
        
        self.stdout.write(self.style.SUCCESS('🔍 Analizando siembras validadas...'))
        
        # Obtener todas las siembras validadas
        siembras = Siembra.objects.filter(estado='validada')
        total_siembras = siembras.count()
        
        if total_siembras == 0:
            self.stdout.write(self.style.WARNING('❌ No hay siembras validadas'))
            return
        
        self.stdout.write(f'📊 Total de siembras validadas: {total_siembras}')
        
        # Agrupar siembras por cercanía
        grupos = []
        siembras_procesadas = set()
        
        for siembra in siembras:
            if siembra.id in siembras_procesadas:
                continue
            
            # Buscar siembras cercanas
            grupo = [siembra]
            siembras_procesadas.add(siembra.id)
            
            for otra_siembra in siembras:
                if otra_siembra.id in siembras_procesadas:
                    continue
                
                distancia = self.calcular_distancia(
                    float(siembra.latitud), float(siembra.longitud),
                    float(otra_siembra.latitud), float(otra_siembra.longitud)
                )
                
                if distancia <= radio_busqueda:
                    grupo.append(otra_siembra)
                    siembras_procesadas.add(otra_siembra.id)
            
            if len(grupo) >= minimo_arboles:
                grupos.append(grupo)
        
        self.stdout.write(f'\n🌳 Grupos encontrados con {minimo_arboles}+ árboles: {len(grupos)}')
        
        if len(grupos) == 0:
            self.stdout.write(self.style.WARNING(
                f'\n❌ No se encontraron grupos con al menos {minimo_arboles} árboles en {radio_busqueda}km'
            ))
            return
        
        # Crear zonas para cada grupo
        zonas_creadas = 0
        zonas_actualizadas = 0
        
        for i, grupo in enumerate(grupos, 1):
            # Calcular centro de masa
            lat_promedio = sum(float(s.latitud) for s in grupo) / len(grupo)
            lng_promedio = sum(float(s.longitud) for s in grupo) / len(grupo)
            
            # Verificar si ya existe una zona en esta área
            zona_existente = None
            for zona in Zona.objects.filter(activa=True):
                distancia = self.calcular_distancia(
                    lat_promedio, lng_promedio,
                    float(zona.latitud), float(zona.longitud)
                )
                if distancia <= 1.5:  # 1.5 km de tolerancia
                    zona_existente = zona
                    break
            
            if zona_existente:
                # Actualizar zona existente
                zona_existente.total_siembras = len(grupo)
                zona_existente.save()
                zonas_actualizadas += 1
                self.stdout.write(
                    f'  {i}. ✏️  Actualizada: {zona_existente.nombre} ({len(grupo)} árboles)'
                )
            else:
                # Determinar especie predominante
                especies = {}
                for siembra in grupo:
                    if siembra.especie:
                        especies[siembra.especie] = especies.get(siembra.especie, 0) + 1
                
                especie_comun = 'árboles'
                if especies:
                    especie_comun = max(especies.items(), key=lambda x: x[1])[0]
                
                # Crear nueva zona
                nueva_zona = Zona.objects.create(
                    nombre=f"Zona de Reforestación - {len(grupo)} {especie_comun}",
                    latitud=lat_promedio,
                    longitud=lng_promedio,
                    tipo_terreno='urbano',
                    descripcion=f"Zona generada automáticamente con {len(grupo)} árboles plantados. Especie predominante: {especie_comun}.",
                    recomendaciones=f"Esta zona tiene una buena concentración de árboles. Se recomienda continuar plantando especies similares.",
                    activa=True,
                    auto_generada=True,
                    radio_km=radio_busqueda,
                    total_siembras=len(grupo)
                )
                zonas_creadas += 1
                
                self.stdout.write(
                    f'  {i}. ✅ Creada: {nueva_zona.nombre} '
                    f'({lat_promedio:.4f}, {lng_promedio:.4f})'
                )
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✅ Proceso completado'))
        self.stdout.write(f'📍 Zonas creadas: {zonas_creadas}')
        self.stdout.write(f'✏️  Zonas actualizadas: {zonas_actualizadas}')
        self.stdout.write(f'🌳 Total de árboles agrupados: {sum(len(g) for g in grupos)}')
        self.stdout.write('=' * 60)
