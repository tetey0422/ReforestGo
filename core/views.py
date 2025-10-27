"""
Views para la aplicación ReforestGo
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Perfil, Siembra, Vivero, Zona, Avatar
from django.contrib.auth.models import User


def index(request):
    """Página de inicio"""
    # Obtener estadísticas globales
    total_siembras = Siembra.objects.filter(estado='validada').count()
    total_usuarios = User.objects.filter(is_active=True).count()
    viveros_destacados = Vivero.objects.filter(destacado=True)
    
    context = {
        'total_siembras': total_siembras,
        'total_usuarios': total_usuarios,
        'viveros_destacados': viveros_destacados,
    }
    return render(request, 'reforest/index.html', context)


def registro(request):
    """Registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('reforest:perfil')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # El perfil se crea automáticamente por la señal post_save
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('reforest:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserCreationForm()
    
    return render(request, 'reforest/registro.html', {'form': form})


@login_required
def perfil(request):
    """Vista del perfil del usuario"""
    perfil = request.user.perfil
    
    # Obtener estadísticas del usuario
    total_siembras = request.user.siembras.filter(estado='validada').count()
    siembras_pendientes = request.user.siembras.filter(estado='pendiente').count()
    
    # Últimas 6 siembras
    siembras = request.user.siembras.all()[:6]
    
    # Avatares disponibles (desbloqueados según nivel)
    avatares_disponibles = Avatar.objects.filter(nivel_requerido__lte=perfil.nivel)
    
    # Calcular progreso hacia el siguiente nivel
    progreso = perfil.progreso_siguiente_nivel()

    # Calcular puntos faltantes hacia el siguiente nivel
    # Definir objetivos por nivel
    niveles_objetivo = {1: 100, 2: 250, 3: 500, 4: 1000}
    siguiente_objetivo = niveles_objetivo.get(perfil.nivel)
    if siguiente_objetivo:
        faltan = max(0, siguiente_objetivo - perfil.puntos)
    else:
        faltan = 0
    
    context = {
        'perfil': perfil,
        'total_siembras': total_siembras,
        'siembras_pendientes': siembras_pendientes,
        'siembras': siembras,
        'avatares_disponibles': avatares_disponibles,
        'progreso': progreso,
        'faltan': faltan,
    }
    return render(request, 'reforest/perfil.html', context)


@login_required
def mis_siembras(request):
    """Lista todas las siembras del usuario"""
    # Obtener filtros
    estado_filter = request.GET.get('estado', 'todas')
    
    # Filtrar siembras
    siembras = request.user.siembras.all()
    
    if estado_filter != 'todas':
        siembras = siembras.filter(estado=estado_filter)
    
    # Paginación
    paginator = Paginator(siembras, 12)  # 12 siembras por página
    page_number = request.GET.get('page')
    siembras_page = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': request.user.siembras.count(),
        'validadas': request.user.siembras.filter(estado='validada').count(),
        'pendientes': request.user.siembras.filter(estado='pendiente').count(),
        'rechazadas': request.user.siembras.filter(estado='rechazada').count(),
    }
    
    context = {
        'siembras': siembras_page,
        'estado_filter': estado_filter,
        'stats': stats,
    }
    return render(request, 'reforest/mis_siembras.html', context)


@login_required
def registrar_siembra(request):
    """Registrar una nueva siembra"""
    if request.method == 'POST':
        # Obtener datos del formulario
        foto = request.FILES.get('foto')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        especie = request.POST.get('especie', '')
        descripcion = request.POST.get('descripcion', '')
        
        # Validaciones
        if not foto:
            messages.error(request, 'Debes subir una foto del árbol plantado.')
            return render(request, 'reforest/registrar_siembra.html')
        
        if not latitud or not longitud:
            messages.error(request, 'No se pudo obtener tu ubicación GPS.')
            return render(request, 'reforest/registrar_siembra.html')
        
        try:
            # Crear la siembra
            siembra = Siembra.objects.create(
                usuario=request.user,
                foto=foto,
                latitud=float(latitud),
                longitud=float(longitud),
                especie=especie,
                descripcion=descripcion
            )
            
            messages.success(
                request,
                '¡Siembra registrada exitosamente! Está pendiente de validación por un administrador.'
            )
            return redirect('reforest:perfil')
            
        except Exception as e:
            messages.error(request, f'Error al registrar la siembra: {str(e)}')
            return render(request, 'reforest/registrar_siembra.html')
    
    return render(request, 'reforest/registrar_siembra.html')


@login_required
def cambiar_avatar(request, avatar_id):
    """Cambiar el avatar del usuario"""
    avatar = get_object_or_404(Avatar, id=avatar_id)
    perfil = request.user.perfil
    
    # Verificar que el avatar esté desbloqueado
    if avatar.nivel_requerido > perfil.nivel:
        messages.error(request, f'Debes alcanzar el nivel {avatar.nivel_requerido} para desbloquear este avatar.')
    else:
        perfil.avatar_actual = avatar
        perfil.save()
        messages.success(request, f'Avatar cambiado a {avatar.nombre} {avatar.emoji}')
    
    return redirect('reforest:perfil')


def mapa(request):
    """Mapa interactivo con viveros y zonas de siembra"""
    viveros = Vivero.objects.all()
    zonas = Zona.objects.filter(activa=True)
    
    # Convertir a formato JSON para el mapa
    viveros_data = [
        {
            'nombre': v.nombre,
            'lat': float(v.latitud),
            'lng': float(v.longitud),
            'direccion': v.direccion,
            'telefono': v.telefono,
            'horario': v.horario,
            'especies': v.especies_disponibles,
            'destacado': v.destacado,
        }
        for v in viveros
    ]
    
    zonas_data = [
        {
            'nombre': z.nombre,
            'lat': float(z.latitud),
            'lng': float(z.longitud),
            'tipo': z.tipo_terreno,
            'descripcion': z.descripcion,
            'recomendaciones': z.recomendaciones,
        }
        for z in zonas
    ]
    
    context = {
        'viveros': viveros_data,
        'zonas': zonas_data,
    }
    return render(request, 'reforest/mapa.html', context)


def ranking(request):
    """Ranking de usuarios por puntos"""
    # Top 50 usuarios
    perfiles = Perfil.objects.select_related('user', 'avatar_actual').order_by('-puntos')[:50]
    
    # Añadir posición en el ranking
    for index, perfil in enumerate(perfiles, start=1):
        perfil.posicion = index
        perfil.siembras_validadas = perfil.user.siembras.filter(estado='validada').count()
    
    # Posición del usuario actual si está autenticado
    usuario_posicion = None
    if request.user.is_authenticated:
        try:
            usuarios_por_encima = Perfil.objects.filter(
                puntos__gt=request.user.perfil.puntos
            ).count()
            usuario_posicion = usuarios_por_encima + 1
        except:
            usuario_posicion = None
    
    context = {
        'perfiles': perfiles,
        'usuario_posicion': usuario_posicion,
    }
    return render(request, 'reforest/ranking.html', context)


# =========================
# API ENDPOINTS
# =========================

def api_obtener_coordenadas(request):
    """API para obtener viveros y zonas en formato JSON"""
    tipo = request.GET.get('tipo', 'todos')  # viveros, zonas, todos
    
    data = {}
    
    if tipo in ['viveros', 'todos']:
        viveros = Vivero.objects.all()
        data['viveros'] = [
            {
                'id': v.id,
                'nombre': v.nombre,
                'lat': float(v.latitud),
                'lng': float(v.longitud),
                'direccion': v.direccion,
                'telefono': v.telefono,
                'especies': v.especies_disponibles,
                'destacado': v.destacado,
            }
            for v in viveros
        ]
    
    if tipo in ['zonas', 'todos']:
        zonas = Zona.objects.filter(activa=True)
        data['zonas'] = [
            {
                'id': z.id,
                'nombre': z.nombre,
                'lat': float(z.latitud),
                'lng': float(z.longitud),
                'tipo': z.tipo_terreno,
                'descripcion': z.descripcion,
                'recomendaciones': z.recomendaciones,
            }
            for z in zonas
        ]
    
    return JsonResponse(data)


@login_required
def api_estadisticas_usuario(request):
    """API para obtener estadísticas del usuario"""
    perfil = request.user.perfil
    
    data = {
        'usuario': request.user.username,
        'nombre_completo': request.user.get_full_name(),
        'nivel': perfil.nivel,
        'puntos': perfil.puntos,
        'avatar': {
            'emoji': perfil.avatar_actual.emoji if perfil.avatar_actual else '🌱',
            'nombre': perfil.avatar_actual.nombre if perfil.avatar_actual else 'Semilla',
        },
        'siembras': {
            'total': request.user.siembras.count(),
            'validadas': request.user.siembras.filter(estado='validada').count(),
            'pendientes': request.user.siembras.filter(estado='pendiente').count(),
            'rechazadas': request.user.siembras.filter(estado='rechazada').count(),
        },
        'progreso_nivel': perfil.progreso_siguiente_nivel(),
    }
    
    return JsonResponse(data)