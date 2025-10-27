from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Perfil, Avatar, Vivero, Zona, Siembra


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'nombre', 'nivel_requerido', 'descripcion']
    list_filter = ['nivel_requerido']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nivel_requerido']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario_display', 'avatar_emoji', 'nivel', 'puntos', 'total_siembras', 'fecha_creacion']
    list_filter = ['nivel', 'fecha_creacion']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['fecha_creacion', 'total_siembras']
    ordering = ['-puntos']
    
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
                    'fecha_siembra', 'acciones_rapidas']
    list_filter = ['estado', 'fecha_siembra', 'especie']
    search_fields = ['usuario__username', 'especie', 'descripcion']
    readonly_fields = ['usuario', 'foto_preview', 'fecha_siembra', 'ubicacion_mapa']
    list_editable = ['estado']
    ordering = ['-fecha_siembra']
    actions = ['validar_siembras', 'rechazar_siembras']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'fecha_siembra')
        }),
        ('Detalles de la Siembra', {
            'fields': ('foto_preview', 'especie', 'descripcion')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud', 'ubicacion_mapa')
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
    
    def acciones_rapidas(self, obj):
        if obj.estado == 'pendiente':
            return format_html(
                '<a class="button" href="/admin/reforest/siembra/{}/change/">✅ Revisar</a>',
                obj.pk
            )
        elif obj.estado == 'validada':
            return format_html('<span style="color: green;">✓ Validada</span>')
        else:
            return format_html('<span style="color: red;">✗ Rechazada</span>')
    acciones_rapidas.short_description = 'Acciones'
    
    def validar_siembras(self, request, queryset):
        """Acción para validar múltiples siembras"""
        count = 0
        for siembra in queryset.filter(estado='pendiente'):
            siembra.validar(request.user)
            count += 1
        
        self.message_user(request, f'{count} siembra(s) validada(s) exitosamente.')
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