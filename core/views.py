"""
Views actualizadas para ReforestGo con sistema de verificación y oxígeno
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from .models import Perfil, Siembra, Vivero, Zona, Avatar, Verificacion
from django.contrib.auth.models import User


# ========== HELPERS ==========

def es_verificador(user):
    """Verifica si el usuario tiene rol de verificador o admin"""
    return user.perfil.rol in ['verificador', 'admin'] or user.is_staff


# ========== VISTAS PÚBLICAS ==========

def index(request):
    """Página de inicio"""
    # Estadísticas globales
    total_siembras = Siembra.objects.filter(estado='validada').count()
    total_usuarios = User.objects.filter(is_active=True).count()
    viveros_destacados = Vivero.objects.filter(destacado=True)[:3]
    
    # Calcular oxígeno total generado
    oxigeno_total = Siembra.objects.filter(estado='validada').aggregate(
        total=Sum('oxigeno_generado')
    )['total'] or 0
    
    co2_total = Siembra.objects.filter(estado='validada').aggregate(
        total=Sum('co2_absorbido')
    )['total'] or 0
    
    context = {
        'total_siembras': total_siembras,
        'total_usuarios': total_usuarios,
        'viveros_destacados': viveros_destacados,
        'oxigeno_total': round(float(oxigeno_total), 2),
        'co2_total': round(float(co2_total), 2),
    }
    return render(request, 'index.html', context)


def registro(request):
    """Registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('reforest:perfil')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente. 🌱')
            return redirect('reforest:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserCreationForm()
    
    return render(request, 'registro.html', {'form': form})


# ========== PERFIL Y SIEMBRAS ==========

@login_required
def perfil(request):
    """Vista del perfil del usuario"""
    perfil = request.user.perfil
    
    # Estadísticas del usuario
    total_siembras = request.user.siembras.filter(estado='validada').count()
    siembras_pendientes = request.user.siembras.filter(estado='pendiente').count()
    
    # Últimas 6 siembras
    siembras = request.user.siembras.all()[:6]
    
    # Avatares disponibles
    avatares_disponibles = Avatar.objects.filter(nivel_requerido__lte=perfil.nivel)
    
    # Calcular progreso
    try:
        progreso = perfil.progreso_siguiente_nivel()
        if progreso is None:
            progreso = 0
    except Exception:
        progreso = 0

    # Puntos faltantes
    niveles_objetivo = {1: 100, 2: 250, 3: 500, 4: 1000}
    siguiente_objetivo = niveles_objetivo.get(perfil.nivel, 0)
    
    if siguiente_objetivo:
        faltan = max(0, siguiente_objetivo - perfil.puntos)
    else:
        faltan = 0
    
    # Cálculo de impacto ambiental personal
    siembras_validadas = request.user.siembras.filter(estado='validada')
    oxigeno_personal = siembras_validadas.aggregate(total=Sum('oxigeno_generado'))['total'] or 0
    co2_personal = siembras_validadas.aggregate(total=Sum('co2_absorbido'))['total'] or 0
    
    context = {
        'perfil': perfil,
        'total_siembras': total_siembras,
        'siembras_pendientes': siembras_pendientes,
        'siembras': siembras,
        'avatares_disponibles': avatares_disponibles,
        'progreso': progreso,
        'faltan': faltan,
        'oxigeno_personal': round(float(oxigeno_personal), 2),
        'co2_personal': round(float(co2_personal), 2),
    }
    return render(request, 'perfil.html', context)


@login_required
def mis_siembras(request):
    """Lista todas las siembras del usuario"""
    estado_filter = request.GET.get('estado', 'todas')
    
    siembras = request.user.siembras.all()
    
    if estado_filter != 'todas':
        siembras = siembras.filter(estado=estado_filter)
    
    # Paginación
    paginator = Paginator(siembras, 12)
    page_number = request.GET.get('page')
    siembras_page = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': request.user.siembras.count(),
        'validadas': request.user.siembras.filter(estado='validada').count(),
        'pendientes': request.user.siembras.filter(estado='pendiente').count(),
        'en_verificacion': request.user.siembras.filter(estado='en_verificacion').count(),
        'rechazadas': request.user.siembras.filter(estado='rechazada').count(),
    }
    
    context = {
        'siembras': siembras_page,
        'estado_filter': estado_filter,
        'stats': stats,
    }
    return render(request, 'mis_siembras.html', context)


@login_required
def registrar_siembra(request):
    """Registrar una nueva siembra"""
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        especie = request.POST.get('especie', '')
        descripcion = request.POST.get('descripcion', '')
        
        # Validaciones
        if not foto:
            messages.error(request, 'Debes subir una foto del árbol plantado.')
            return render(request, 'registrar_siembra.html')
        
        if not latitud or not longitud:
            messages.error(request, 'No se pudo obtener tu ubicación GPS.')
            return render(request, 'registrar_siembra.html')
        
        try:
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
                '¡Siembra registrada exitosamente! 🌱 Está pendiente de validación por un administrador.'
            )
            return redirect('reforest:perfil')
            
        except Exception as e:
            messages.error(request, f'Error al registrar la siembra: {str(e)}')
            return render(request, 'registrar_siembra.html')
    
    return render(request, 'registrar_siembra.html')


@login_required
def cambiar_avatar(request, avatar_id):
    """Cambiar el avatar del usuario"""
    avatar = get_object_or_404(Avatar, id=avatar_id)
    perfil = request.user.perfil
    
    if avatar.nivel_requerido > perfil.nivel:
        messages.error(request, f'Debes alcanzar el nivel {avatar.nivel_requerido} para desbloquear este avatar.')
    else:
        perfil.avatar_actual = avatar
        perfil.save()
        messages.success(request, f'Avatar cambiado a {avatar.nombre} {avatar.emoji}')
    
    return redirect('reforest:perfil')


# ========== VERIFICACIÓN ==========

@login_required
@user_passes_test(es_verificador, login_url='reforest:perfil')
def mapa_verificacion(request):
    """Mapa con árboles pendientes de verificación"""
    import json
    
    # Obtener ubicación del usuario (opcional)
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    # Obtener siembras pendientes de verificación
    siembras_pendientes = Siembra.objects.filter(
        estado='pendiente'
    ).select_related('usuario')
    
    # Si hay ubicación, ordenar por cercanía (simplificado)
    if user_lat and user_lng:
        # En producción usarías una query más eficiente con PostGIS
        siembras_pendientes = siembras_pendientes[:50]
    else:
        siembras_pendientes = siembras_pendientes[:50]
    
    # Convertir a JSON para el mapa
    siembras_data = [
        {
            'id': s.id,
            'lat': float(s.latitud),
            'lng': float(s.longitud),
            'especie': s.especie or 'No especificada',
            'usuario': s.usuario.username,
            'fecha': s.fecha_siembra.strftime('%d/%m/%Y'),
            'foto_url': s.foto.url,
        }
        for s in siembras_pendientes
    ]
    
    context = {
        'siembras': json.dumps(siembras_data),
        'total_pendientes': len(siembras_data),
    }
    return render(request, 'mapa_verificacion.html', context)


@login_required
@user_passes_test(es_verificador, login_url='reforest:perfil')
def verificar_arbol(request, siembra_id):
    """Formulario para verificar un árbol"""
    siembra = get_object_or_404(Siembra, id=siembra_id)
    
    # Verificar que la siembra esté pendiente
    if siembra.estado != 'pendiente':
        messages.error(request, 'Este árbol ya no está disponible para verificación.')
        return redirect('reforest:mapa_verificacion')
    
    if request.method == 'POST':
        foto_verificacion = request.FILES.get('foto_verificacion')
        foto_ubicacion = request.FILES.get('foto_ubicacion')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        notas = request.POST.get('notas', '')
        
        if not foto_verificacion or not latitud or not longitud:
            messages.error(request, 'Debes subir al menos una foto y compartir tu ubicación.')
            return render(request, 'verificar_arbol.html', {'siembra': siembra})
        
        try:
            verificacion = Verificacion.objects.create(
                siembra=siembra,
                verificador=request.user,
                foto_verificacion=foto_verificacion,
                foto_ubicacion=foto_ubicacion,
                latitud_verificacion=float(latitud),
                longitud_verificacion=float(longitud),
                notas_verificador=notas
            )
            
            # Cambiar estado de la siembra
            siembra.estado = 'en_verificacion'
            siembra.save()
            
            messages.success(
                request,
                f'¡Verificación enviada! Pendiente de aprobación por un administrador. 🎯'
            )
            return redirect('reforest:mapa_verificacion')
            
        except Exception as e:
            messages.error(request, f'Error al enviar la verificación: {str(e)}')
    
    context = {
        'siembra': siembra,
    }
    return render(request, 'verificar_arbol.html', context)


@login_required
@user_passes_test(es_verificador, login_url='reforest:perfil')
def mis_verificaciones(request):
    """Lista de verificaciones realizadas por el usuario"""
    verificaciones = request.user.verificaciones_realizadas.all().select_related('siembra', 'revisada_por')
    
    # Paginación
    paginator = Paginator(verificaciones, 12)
    page_number = request.GET.get('page')
    verificaciones_page = paginator.get_page(page_number)
    
    # Estadísticas
    perfil = request.user.perfil
    stats = {
        'total': perfil.verificaciones_realizadas,
        'aprobadas': perfil.verificaciones_aprobadas,
        'pendientes': verificaciones.filter(estado='pendiente').count(),
        'rechazadas': verificaciones.filter(estado='rechazada').count(),
        'puntos_ganados': perfil.puntos_verificacion,
        'tasa_aprobacion': perfil.tasa_aprobacion_verificaciones(),
    }
    
    context = {
        'verificaciones': verificaciones_page,
        'stats': stats,
    }
    return render(request, 'mis_verificaciones.html', context)


# CONTINÚA EN PARTE 2...

# ========== VISTAS DE ADMINISTRADOR ==========

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(es_admin, login_url='reforest:index')
def admin_verificaciones(request):
    """Panel de administrador para revisar verificaciones"""
    estado_filter = request.GET.get('estado', 'pendiente')
    
    verificaciones = Verificacion.objects.all().select_related(
        'siembra', 'verificador', 'revisada_por'
    )
    
    if estado_filter != 'todas':
        verificaciones = verificaciones.filter(estado=estado_filter)
    
    # Paginación
    paginator = Paginator(verificaciones, 15)
    page_number = request.GET.get('page')
    verificaciones_page = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': Verificacion.objects.count(),
        'pendientes': Verificacion.objects.filter(estado='pendiente').count(),
        'aprobadas': Verificacion.objects.filter(estado='aprobada').count(),
        'rechazadas': Verificacion.objects.filter(estado='rechazada').count(),
    }
    
    context = {
        'verificaciones': verificaciones_page,
        'estado_filter': estado_filter,
        'stats': stats,
    }
    return render(request, 'admin_verificaciones.html', context)


@login_required
@user_passes_test(es_admin, login_url='reforest:index')
def revisar_verificacion(request, verificacion_id):
    """Aprobar o rechazar una verificación"""
    verificacion = get_object_or_404(Verificacion, id=verificacion_id)
    
    if verificacion.estado != 'pendiente':
        messages.warning(request, 'Esta verificación ya fue revisada.')
        return redirect('reforest:admin_verificaciones')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        notas = request.POST.get('notas', '')
        
        if accion == 'aprobar':
            verificacion.aprobar(request.user)
            messages.success(
                request,
                f'✅ Verificación aprobada. {verificacion.puntos_otorgados} puntos otorgados a {verificacion.verificador.username}'
            )
        elif accion == 'rechazar':
            verificacion.rechazar(request.user, notas)
            messages.info(request, f'❌ Verificación rechazada.')
        
        return redirect('reforest:admin_verificaciones')
    
    # Calcular distancia entre siembra y verificación
    distancia = verificacion.calcular_distancia()
    # Calcular puntos que se otorgarán (entero)
    puntos = verificacion.calcular_puntos()
    
    context = {
        'verificacion': verificacion,
        'distancia': distancia,
        'puntos': puntos,
    }
    return render(request, 'revisar_verificacion.html', context)


# ========== ESTADÍSTICAS DE OXÍGENO ==========

@login_required
def estadisticas_oxigeno(request):
    """Dashboard de impacto ambiental"""
    # Actualizar oxígeno de todas las siembras validadas del usuario
    siembras_validadas = request.user.siembras.filter(estado='validada')
    
    for siembra in siembras_validadas:
        siembra.calcular_oxigeno()
    
    # Obtener datos actualizados
    oxigeno_data = siembras_validadas.aggregate(
        total_oxigeno=Sum('oxigeno_generado'),
        total_co2=Sum('co2_absorbido')
    )
    
    oxigeno_total = float(oxigeno_data['total_oxigeno'] or 0)
    co2_total = float(oxigeno_data['total_co2'] or 0)
    
    # Calcular equivalencias
    equivalencias = {
        'autos_año': round(co2_total / 4600, 2),  # 1 auto = ~4.6 ton CO2/año
        'telefonos_cargados': int(oxigeno_total * 120),
        'arboles_equivalentes': siembras_validadas.count(),
        'personas_oxigeno': int(oxigeno_total / 365),  # 1 persona = ~1 kg O2/día
    }
    
    # Datos por especie
    por_especie = siembras_validadas.values('especie').annotate(
        total_oxigeno=Sum('oxigeno_generado'),
        cantidad=Count('id')
    ).order_by('-total_oxigeno')[:10]
    
    # Datos para gráfico temporal (últimos 12 meses)
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    
    hace_12_meses = datetime.now() - timedelta(days=365)
    
    por_mes = siembras_validadas.filter(
        fecha_siembra__gte=hace_12_meses
    ).annotate(
        mes=TruncMonth('fecha_siembra')
    ).values('mes').annotate(
        cantidad=Count('id'),
        oxigeno=Sum('oxigeno_generado')
    ).order_by('mes')
    
    context = {
        'oxigeno_total': round(oxigeno_total, 2),
        'co2_total': round(co2_total, 2),
        'equivalencias': equivalencias,
        'siembras_count': siembras_validadas.count(),
        'por_especie': list(por_especie),
        'por_mes': list(por_mes),
    }
    return render(request, 'estadisticas_oxigeno.html', context)


# ========== MAPA Y RANKING (actualizados) ==========

def mapa(request):
    """Mapa interactivo con viveros y zonas de siembra"""
    import json
    
    viveros = Vivero.objects.all()
    zonas = Zona.objects.filter(activa=True)
    
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
        'viveros': json.dumps(viveros_data),
        'zonas': json.dumps(zonas_data),
    }
    return render(request, 'mapa.html', context)


def ranking(request):
    """Ranking de usuarios por puntos"""
    perfiles = Perfil.objects.select_related('user', 'avatar_actual')\
        .filter(user__is_staff=False, user__is_superuser=False)\
        .order_by('-puntos')[:50]
    
    # Añadir posición y datos
    for index, perfil in enumerate(perfiles, start=1):
        perfil.posicion = index
        perfil.siembras_validadas = perfil.user.siembras.filter(estado='validada').count()
    
    # Posición del usuario actual
    usuario_posicion = None
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        try:
            usuarios_por_encima = Perfil.objects.filter(
                puntos__gt=request.user.perfil.puntos,
                user__is_staff=False,
                user__is_superuser=False
            ).count()
            usuario_posicion = usuarios_por_encima + 1
        except:
            usuario_posicion = None
    
    context = {
        'perfiles': perfiles,
        'usuario_posicion': usuario_posicion,
    }
    return render(request, 'ranking.html', context)


# ========== API ENDPOINTS ==========

def api_obtener_coordenadas(request):
    """API para obtener viveros y zonas en formato JSON"""
    tipo = request.GET.get('tipo', 'todos')
    
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
    
    # Actualizar oxígeno
    siembras_validadas = request.user.siembras.filter(estado='validada')
    for siembra in siembras_validadas:
        siembra.calcular_oxigeno()
    
    # Obtener datos actualizados
    oxigeno_data = siembras_validadas.aggregate(
        total_oxigeno=Sum('oxigeno_generado'),
        total_co2=Sum('co2_absorbido')
    )
    
    data = {
        'usuario': request.user.username,
        'nombre_completo': request.user.get_full_name(),
        'nivel': perfil.nivel,
        'puntos': perfil.puntos,
        'rol': perfil.rol,
        'avatar': {
            'emoji': perfil.avatar_actual.emoji if perfil.avatar_actual else '🌱',
            'nombre': perfil.avatar_actual.nombre if perfil.avatar_actual else 'Semilla',
        },
        'siembras': {
            'total': request.user.siembras.count(),
            'validadas': siembras_validadas.count(),
            'pendientes': request.user.siembras.filter(estado='pendiente').count(),
            'en_verificacion': request.user.siembras.filter(estado='en_verificacion').count(),
            'rechazadas': request.user.siembras.filter(estado='rechazada').count(),
        },
        'verificaciones': {
            'realizadas': perfil.verificaciones_realizadas,
            'aprobadas': perfil.verificaciones_aprobadas,
            'puntos_ganados': perfil.puntos_verificacion,
            'tasa_aprobacion': perfil.tasa_aprobacion_verificaciones(),
        } if perfil.rol in ['verificador', 'admin'] else None,
        'impacto_ambiental': {
            'oxigeno_generado': float(oxigeno_data['total_oxigeno'] or 0),
            'co2_absorbido': float(oxigeno_data['total_co2'] or 0),
        },
        'progreso_nivel': perfil.progreso_siguiente_nivel(),
    }
    
    return JsonResponse(data)


@login_required
def api_siembras_cercanas(request):
    """API para obtener siembras pendientes cercanas al usuario"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radio_km = int(request.GET.get('radio', 10))
    
    if not lat or not lng:
        return JsonResponse({'error': 'Se requiere latitud y longitud'}, status=400)
    
    # Obtener siembras pendientes
    siembras = Siembra.objects.filter(estado='pendiente').select_related('usuario')
    
    # Filtrar por distancia (simplificado - en producción usar PostGIS)
    siembras_data = []
    for siembra in siembras[:100]:  # Limitar para performance
        # Cálculo simplificado de distancia
        import math
        R = 6371  # Radio de la Tierra en km
        
        lat1 = math.radians(float(lat))
        lon1 = math.radians(float(lng))
        lat2 = math.radians(float(siembra.latitud))
        lon2 = math.radians(float(siembra.longitud))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distancia = R * c
        
        if distancia <= radio_km:
            siembras_data.append({
                'id': siembra.id,
                'lat': float(siembra.latitud),
                'lng': float(siembra.longitud),
                'especie': siembra.especie or 'No especificada',
                'usuario': siembra.usuario.username,
                'fecha': siembra.fecha_siembra.strftime('%d/%m/%Y'),
                'foto_url': siembra.foto.url,
                'distancia_km': round(distancia, 2),
            })
    
    # Ordenar por distancia
    siembras_data.sort(key=lambda x: x['distancia_km'])
    
    return JsonResponse({
        'siembras': siembras_data,
        'total': len(siembras_data)
    })