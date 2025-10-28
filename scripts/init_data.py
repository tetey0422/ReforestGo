"""
Script para inicializar datos de ejemplo en la base de datos
Ejecutar con: python manage.py shell < scripts/init_data.py
"""

from core.models import Avatar, Vivero, Zona
from django.contrib.auth.models import User

print("🌱 Iniciando creación de datos de ejemplo...")

# Crear avatares si no existen
avatares_data = [
    {"nombre": "Semilla", "emoji": "🌱", "nivel_requerido": 1, "descripcion": "El inicio de todo"},
    {"nombre": "Brote", "emoji": "🌿", "nivel_requerido": 2, "descripcion": "Estás creciendo"},
    {"nombre": "Arbusto", "emoji": "🌳", "nivel_requerido": 3, "descripcion": "Ya eres fuerte"},
    {"nombre": "Árbol", "emoji": "🌲", "nivel_requerido": 4, "descripcion": "Majestuoso y firme"},
    {"nombre": "Bosque", "emoji": "🌴", "nivel_requerido": 5, "descripcion": "Leyenda viviente"},
]

print("\n📸 Creando avatares...")
for avatar_data in avatares_data:
    avatar, created = Avatar.objects.get_or_create(
        nivel_requerido=avatar_data['nivel_requerido'],
        defaults=avatar_data
    )
    if created:
        print(f"  ✅ Avatar creado: {avatar.emoji} {avatar.nombre}")
    else:
        print(f"  ⏭️  Avatar ya existe: {avatar.emoji} {avatar.nombre}")

# Crear viveros de ejemplo
viveros_data = [
    {
        "nombre": "Vivero El Jardín Verde",
        "direccion": "Calle 45 #23-15, Barrancabermeja",
        "latitud": 7.0653,
        "longitud": -73.8534,
        "telefono": "+57 (607) 622-1234",
        "horario": "Lunes a Sábado 7am-6pm",
        "especies_disponibles": "Ceiba, Guayacán, Roble, Samán, Caracolí, Ocobo",
        "destacado": True
    },
    {
        "nombre": "Vivero Naturaleza Viva",
        "direccion": "Carrera 12 #67-89, Barrancabermeja",
        "latitud": 7.0720,
        "longitud": -73.8600,
        "telefono": "+57 (607) 622-5678",
        "horario": "Lunes a Viernes 8am-5pm",
        "especies_disponibles": "Cedro, Nogal, Almendro, Guamo, Arrayán",
        "destacado": False
    },
    {
        "nombre": "Vivero Eco Vida",
        "direccion": "Avenida del Río #34-56, Barrancabermeja",
        "latitud": 7.0580,
        "longitud": -73.8480,
        "telefono": "+57 (607) 622-9012",
        "horario": "Martes a Domingo 8am-6pm",
        "especies_disponibles": "Palma, Bambú, Caucho, Yarumo, Matarratón",
        "destacado": True
    },
]

print("\n🏪 Creando viveros...")
for vivero_data in viveros_data:
    vivero, created = Vivero.objects.get_or_create(
        nombre=vivero_data['nombre'],
        defaults=vivero_data
    )
    if created:
        print(f"  ✅ Vivero creado: {vivero.nombre}")
    else:
        print(f"  ⏭️  Vivero ya existe: {vivero.nombre}")

# Crear zonas de siembra
zonas_data = [
    {
        "nombre": "Parque Central Barrancabermeja",
        "latitud": 7.0650,
        "longitud": -73.8520,
        "tipo_terreno": "parque",
        "descripcion": "Parque público ideal para siembra de árboles ornamentales y de sombra.",
        "recomendaciones": "Especies recomendadas: Samán, Ocobo, Guayacán. Plantar en época de lluvias.",
        "activa": True
    },
    {
        "nombre": "Ribera del Río Magdalena",
        "latitud": 7.0700,
        "longitud": -73.8700,
        "tipo_terreno": "ribera",
        "descripcion": "Zona ribereña perfecta para especies que protegen contra la erosión.",
        "recomendaciones": "Especies: Sauce, Ceiba, Guadua. Importante para control de erosión.",
        "activa": True
    },
    {
        "nombre": "Zona Rural El Carmen",
        "latitud": 7.0800,
        "longitud": -73.8800,
        "tipo_terreno": "rural",
        "descripcion": "Área rural con suelo fértil para reforestación extensiva.",
        "recomendaciones": "Especies nativas: Roble, Cedro, Nogal. Ideal para plantaciones grandes.",
        "activa": True
    },
    {
        "nombre": "Cerro La Paz",
        "latitud": 7.0500,
        "longitud": -73.8400,
        "tipo_terreno": "montaña",
        "descripcion": "Zona montañosa que requiere reforestación para prevenir deslizamientos.",
        "recomendaciones": "Especies de raíz profunda: Pino, Eucalipto (con precaución), Arrayán.",
        "activa": True
    },
]

print("\n🗺️  Creando zonas de siembra...")
for zona_data in zonas_data:
    zona, created = Zona.objects.get_or_create(
        nombre=zona_data['nombre'],
        defaults=zona_data
    )
    if created:
        print(f"  ✅ Zona creada: {zona.nombre}")
    else:
        print(f"  ⏭️  Zona ya existe: {zona.nombre}")

# Crear usuario administrador si no existe
print("\n👤 Verificando usuario administrador...")
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@reforestgo.com',
        password='admin123',
        first_name='Administrador',
        last_name='ReforestGo'
    )
    print("  ✅ Usuario admin creado (usuario: admin, contraseña: admin123)")
else:
    print("  ⏭️  Usuario admin ya existe")

print("\n✨ ¡Datos de ejemplo creados exitosamente!")
print("\n📝 Resumen:")
print(f"  • Avatares: {Avatar.objects.count()}")
print(f"  • Viveros: {Vivero.objects.count()}")
print(f"  • Zonas: {Zona.objects.count()}")
print(f"  • Usuarios: {User.objects.count()}")
print("\n🚀 Ya puedes iniciar el servidor con: python manage.py runserver")
