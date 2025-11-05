from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Perfil, Avatar, Vivero, Zona, Siembra, Verificacion


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'nombre', 'nivel_requerido', 'descripcion']
    list_filter = ['nivel_requerido']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nivel_requerido']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario_display', 'avatar_emoji', 'rol', 'nivel', 'puntos', 
                    'total_siembras', 'stats_verificador', 'fecha_creacion']
    list_filter = ['nivel', 'rol', 'fecha_creacion']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['fecha_creacion', 'total_siembras', 'stats_verificador_detalle']
    ordering = ['-puntos']
    list_editable = ['rol']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'rol', 'avatar_actual', 'bio', 'foto_perfil')
        }),
        ('Gamificación', {
            'fields': ('puntos', 'nivel', 'fecha_creacion')
        }),
        ('Estadísticas', {
            'fields': ('total_siembras', 'stats_verificador_detalle')
        }),
    )
    
    def usuario_display(self, obj):
        return f"{obj.user.get_full_name()} (@{obj.user.username})"
    usuario_display.short_description = 'Usuario'
    
    def avatar_emoji(self, obj):
        if obj.avatar_actual:
            return f"{obj.avatar_actual.emoji} {obj.avatar_actual.nombre}"
        return "Sin avatar"
    avatar_emoji.short_description = 'Avatar'
    
    def total_siembras(self, obj):
        return obj.user.siembras.filter(estado='validada').count()
    total_siembras.short_description = 'Siembras validadas'
    
    def stats_verificador(self, obj):
        if obj.rol in ['verificador', 'admin']:
            return f"✅ {obj.verificaciones_aprobadas}/{obj.verificaciones_realizadas}"
        return "-"
    stats_verificador.short_description = 'Verificaciones'
    
    def stats_verificador_detalle(self, obj):
        if obj.rol in ['verificador', 'admin']:
            return format_html(
                '<strong>Total:</strong> {} | <strong>Aprobadas:</strong> {} | '
                '<strong>Puntos ganados:</strong> {} | <strong>Tasa aprobación:</strong> {:.1f}%',
                obj.verificaciones_realizadas,
                obj.verificaciones_aprobadas,
                obj.puntos_verificacion,
                obj.tasa_aprobacion_verificaciones()
            )
        return "No es verificador"
    stats_verificador_detalle.short_description = 'Estadísticas de verificación'


@admin.register(Vivero)
class ViveroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'coordenadas', 'telefono', 'destacado', 'fecha_registro']
    list_filter = ['destacado', 'fecha_registro']
    search_fields = ['nombre', 'direccion', 'especies_disponibles']
    list_editable = ['destacado']
    ordering = ['-destacado', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'direccion', 'telefono', 'horario')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud')
        }),
        ('Especies y Destacados', {
            'fields': ('especies_disponibles', 'destacado')
        }),
    )
    
    def coordenadas(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank">{}, {}</a>',
            obj.latitud, obj.longitud, obj.latitud, obj.longitud
        )
    coordenadas.short_description = 'Coordenadas'


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_terreno', 'coordenadas', 'activa', 'fecha_creacion']
    list_filter = ['tipo_terreno', 'activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'recomendaciones']
    list_editable = ['activa']
    ordering = ['-activa', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo_terreno', 'descripcion', 'recomendaciones')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    def coordenadas(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank">{}, {}</a>',
            obj.latitud, obj.longitud, obj.latitud, obj.longitud
        )
    coordenadas.short_description = 'Coordenadas'


@admin.register(Siembra)
class SiembraAdmin(admin.ModelAdmin):
    list_display = ['usuario_nombre', 'miniatura', 'especie', 'estado', 'puntos_otorgados',
                    'oxigeno_info', 'edad_arbol', 'fecha_siembra', 'acciones_rapidas']
    list_filter = ['estado', 'fecha_siembra', 'especie']
    search_fields = ['usuario__username', 'especie', 'descripcion']
    readonly_fields = ['usuario', 'foto_preview', 'fecha_siembra', 'ubicacion_mapa', 
                       'oxigeno_detalle', 'edad_arbol']
    ordering = ['-fecha_siembra']
    actions = ['validar_siembras', 'rechazar_siembras', 'actualizar_oxigeno']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'fecha_siembra', 'edad_arbol')
        }),
        ('Detalles de la Siembra', {
            'fields': ('foto_preview', 'especie', 'descripcion')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud', 'ubicacion_mapa')
        }),
        ('Impacto Ambiental', {
            'fields': ('oxigeno_detalle',)
        }),
        ('Validación', {
            'fields': ('estado', 'puntos_otorgados', 'validada_por', 'fecha_validacion', 'notas_admin')
        }),
    )
    
    def usuario_nombre(self, obj):
        return f"{obj.usuario.get_full_name()} (@{obj.usuario.username})"
    usuario_nombre.short_description = 'Usuario'
    
    def miniatura(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sin foto"
    miniatura.short_description = 'Foto'
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 10px;" />',
                obj.foto.url
            )
        return "Sin foto"
    foto_preview.short_description = 'Foto de la siembra'
    
    def ubicacion_mapa(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank" class="button">'
            '📍 Ver en Google Maps</a>',
            obj.latitud, obj.longitud
        )
    ubicacion_mapa.short_description = 'Ubicación'
    
    def oxigeno_info(self, obj):
        if obj.estado == 'validada':
            return format_html(
                '🌿 {} kg O2/año<br>💨 {} kg CO2/año',
                obj.oxigeno_generado, obj.co2_absorbido
            )
        return "-"
    oxigeno_info.short_description = 'Oxígeno'
    
    def oxigeno_detalle(self, obj):
        if obj.estado == 'validada':
            return format_html(
                '<div style="padding: 15px; background: #e8f5e9; border-radius: 5px;">'
                '<strong>Oxígeno generado:</strong> {} kg/año<br>'
                '<strong>CO2 absorbido:</strong> {} kg/año<br>'
                '<strong>Edad del árbol:</strong> {}<br>'
                '<strong>Última actualización:</strong> {}'
                '</div>',
                obj.oxigeno_generado,
                obj.co2_absorbido,
                obj.edad_arbol_texto(),
                obj.ultima_actualizacion_oxigeno.strftime('%d/%m/%Y %H:%M')
            )
        return "El árbol debe estar validado para calcular oxígeno"
    oxigeno_detalle.short_description = 'Impacto Ambiental'
    
    def edad_arbol(self, obj):
        return obj.edad_arbol_texto()
    edad_arbol.short_description = 'Edad'
    
    def acciones_rapidas(self, obj):
        if obj.estado == 'pendiente':
            return format_html(
                '<a class="button" href="/admin/core/siembra/{}/change/">✅ Revisar</a>',
                obj.pk
            )
        elif obj.estado == 'validada':
            return format_html('<span style="color: green;">✓ Validada</span>')
        elif obj.estado == 'en_verificacion':
            return format_html('<span style="color: orange;">⏳ En verificación</span>')
        else:
            return format_html('<span style="color: red;">✗ Rechazada</span>')
    acciones_rapidas.short_description = 'Acciones'
    
    def validar_siembras(self, request, queryset):
        """Acción para validar múltiples siembras"""
        count = 0
        usuarios_nivel3 = []
        
        for siembra in queryset.filter(estado='pendiente'):
            nivel_anterior = siembra.usuario.perfil.nivel
            subio_nivel = siembra.validar(request.user)
            
            # Verificar si alcanzó nivel 3
            if subio_nivel and siembra.usuario.perfil.nivel == 3:
                usuarios_nivel3.append(siembra.usuario.username)
            
            count += 1
        
        mensaje = f'{count} siembra(s) validada(s) exitosamente.'
        
        # Agregar mensaje sobre nuevos verificadores
        if usuarios_nivel3:
            mensaje += f' 🎉 ¡{", ".join(usuarios_nivel3)} alcanzó nivel 3 y ahora puede verificar árboles!'
        
        self.message_user(request, mensaje)
    validar_siembras.short_description = "✅ Validar siembras seleccionadas"
    
    def rechazar_siembras(self, request, queryset):
        """Acción para rechazar múltiples siembras"""
        count = queryset.filter(estado='pendiente').update(
            estado='rechazada',
            validada_por=request.user,
            fecha_validacion=timezone.now()
        )
        self.message_user(request, f'{count} siembra(s) rechazada(s).')
    rechazar_siembras.short_description = "❌ Rechazar siembras seleccionadas"
    
    def actualizar_oxigeno(self, request, queryset):
        """Actualiza el cálculo de oxígeno de las siembras validadas"""
        count = 0
        for siembra in queryset.filter(estado='validada'):
            siembra.calcular_oxigeno()
            count += 1
        
        self.message_user(request, f'Oxígeno actualizado para {count} siembra(s).')
    actualizar_oxigeno.short_description = "🌿 Actualizar cálculo de oxígeno"
    
    def save_model(self, request, obj, form, change):
        """Override para manejar la validación automática"""
        if change:
            try:
                original = Siembra.objects.get(pk=obj.pk)
                
                if original.estado == 'pendiente' and obj.estado == 'validada':
                    obj.validada_por = request.user
                    obj.fecha_validacion = timezone.now()
                    super().save_model(request, obj, form, change)
                    
                    # Calcular oxígeno
                    obj.calcular_oxigeno()
                    
                    if not obj.usuario.is_staff and not obj.usuario.is_superuser:
                        perfil = obj.usuario.perfil
                        perfil.sumar_puntos(obj.puntos_otorgados)
                        self.message_user(request, f'✅ Siembra validada. {obj.puntos_otorgados} puntos otorgados')
                    else:
                        self.message_user(request, f'✅ Siembra validada (usuario admin - sin puntos)')
                    return
                
                elif original.estado == 'pendiente' and obj.estado == 'rechazada':
                    obj.validada_por = request.user
                    obj.fecha_validacion = timezone.now()
                    self.message_user(request, f'❌ Siembra rechazada')
            
            except Siembra.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)


@admin.register(Verificacion)
class VerificacionAdmin(admin.ModelAdmin):
    list_display = ['verificador_nombre', 'siembra_info', 'estado', 'distancia_precision',
                    'puntos_otorgados', 'fecha_verificacion', 'acciones']
    list_filter = ['estado', 'fecha_verificacion']
    search_fields = ['verificador__username', 'siembra__especie']
    readonly_fields = ['fecha_verificacion', 'siembra', 'verificador', 'fotos_preview',
                       'mapa_comparacion', 'distancia_calculada']
    ordering = ['-fecha_verificacion']
    actions = ['aprobar_verificaciones', 'rechazar_verificaciones']
    
    fieldsets = (
        ('Verificación', {
            'fields': ('siembra', 'verificador', 'fecha_verificacion', 'estado')
        }),
        ('Fotos de Verificación', {
            'fields': ('fotos_preview',)
        }),
        ('Ubicación y Precisión', {
            'fields': ('latitud_verificacion', 'longitud_verificacion', 
                      'distancia_calculada', 'mapa_comparacion')
        }),
        ('Notas', {
            'fields': ('notas_verificador', 'notas_admin')
        }),
        ('Revisión', {
            'fields': ('revisada_por', 'fecha_revision', 'puntos_otorgados')
        }),
    )
    
    def verificador_nombre(self, obj):
        return f"{obj.verificador.get_full_name()} (@{obj.verificador.username})"
    verificador_nombre.short_description = 'Verificador'
    
    def siembra_info(self, obj):
        return format_html(
            'Siembra #{}<br>Por: {}',
            obj.siembra.id,
            obj.siembra.usuario.username
        )
    siembra_info.short_description = 'Siembra'
    
    def distancia_precision(self, obj):
        dist = obj.calcular_distancia()
        color = 'green' if dist < 20 else 'orange' if dist < 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f} m</span>',
            color, dist
        )
    distancia_precision.short_description = 'Distancia'
    
    def fotos_preview(self, obj):
        html = '<div style="display: flex; gap: 10px;">'
        if obj.foto_verificacion:
            html += f'<div><p><strong>Foto principal:</strong></p><img src="{obj.foto_verificacion.url}" style="max-width: 300px; border-radius: 5px;"></div>'
        if obj.foto_ubicacion:
            html += f'<div><p><strong>Foto ubicación:</strong></p><img src="{obj.foto_ubicacion.url}" style="max-width: 300px; border-radius: 5px;"></div>'
        html += '</div>'
        return format_html(html)
    fotos_preview.short_description = 'Fotos de verificación'
    
    def distancia_calculada(self, obj):
        dist = obj.calcular_distancia()
        return format_html(
            '<strong>Distancia:</strong> {:.2f} metros<br>'
            '<strong>Precisión:</strong> {}',
            dist,
            'Excelente ✅' if dist < 20 else 'Buena ⚠️' if dist < 50 else 'Revisar ❌'
        )
    distancia_calculada.short_description = 'Análisis de precisión'
    
    def mapa_comparacion(self, obj):
        return format_html(
            '<div style="display: flex; gap: 20px;">'
            '<div>'
            '<strong>Ubicación Original:</strong><br>'
            '<a href="https://www.google.com/maps?q={},{}" target="_blank" class="button">'
            '📍 Ver siembra original</a><br>'
            'Lat: {}, Lng: {}'
            '</div>'
            '<div>'
            '<strong>Ubicación Verificación:</strong><br>'
            '<a href="https://www.google.com/maps?q={},{}" target="_blank" class="button">'
            '📍 Ver verificación</a><br>'
            'Lat: {}, Lng: {}'
            '</div>'
            '</div>',
            obj.siembra.latitud, obj.siembra.longitud,
            obj.siembra.latitud, obj.siembra.longitud,
            obj.latitud_verificacion, obj.longitud_verificacion,
            obj.latitud_verificacion, obj.longitud_verificacion
        )
    mapa_comparacion.short_description = 'Comparación de ubicaciones'
    
    def acciones(self, obj):
        if obj.estado == 'pendiente':
            return format_html(
                '<a class="button" href="/admin/core/verificacion/{}/change/">📋 Revisar</a>',
                obj.pk
            )
        elif obj.estado == 'aprobada':
            return format_html(
                '<span style="color: green;">✅ Aprobada<br>{} pts otorgados</span>',
                obj.puntos_otorgados
            )
        else:
            return format_html('<span style="color: red;">❌ Rechazada</span>')
    acciones.short_description = 'Estado'
    
    def aprobar_verificaciones(self, request, queryset):
        """Aprobar múltiples verificaciones"""
        count = 0
        for verificacion in queryset.filter(estado='pendiente'):
            verificacion.aprobar(request.user)
            count += 1
        
        self.message_user(request, f'{count} verificación(es) aprobada(s).')
    aprobar_verificaciones.short_description = "✅ Aprobar verificaciones"
    
    def rechazar_verificaciones(self, request, queryset):
        """Rechazar múltiples verificaciones"""
        count = 0
        for verificacion in queryset.filter(estado='pendiente'):
            verificacion.rechazar(request.user, 'Rechazado desde el admin')
            count += 1
        
        self.message_user(request, f'{count} verificación(es) rechazada(s).')
    rechazar_verificaciones.short_description = "❌ Rechazar verificaciones"
    
    def save_model(self, request, obj, form, change):
        """Override para manejar aprobación/rechazo"""
        if change:
            try:
                original = Verificacion.objects.get(pk=obj.pk)
                
                if original.estado == 'pendiente' and obj.estado == 'aprobada':
                    obj.aprobar(request.user)
                    self.message_user(request, f'✅ Verificación aprobada. {obj.puntos_otorgados} puntos otorgados')
                    return
                elif original.estado == 'pendiente' and obj.estado == 'rechazada':
                    obj.rechazar(request.user, obj.notas_admin)
                    self.message_user(request, '❌ Verificación rechazada')
                    return
            except Verificacion.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)