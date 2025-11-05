# core/models.py - VERSIÓN ACTUALIZADA CON VERIFICACIÓN Y OXÍGENO

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from datetime import datetime, timedelta
from decimal import Decimal
import os


class Avatar(models.Model):
    """Avatares desbloqueables según nivel"""
    nombre = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10, default="🌱")
    imagen = models.ImageField(upload_to='avatares/', null=True, blank=True)
    nivel_requerido = models.IntegerField(default=1)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        ordering = ['nivel_requerido']
        verbose_name = 'Avatar'
        verbose_name_plural = 'Avatares'
    
    def __str__(self):
        return f"{self.emoji} {self.nombre} (Nivel {self.nivel_requerido})"


class Perfil(models.Model):
    """Perfil extendido del usuario con gamificación"""
    ROLES = [
        ('usuario', 'Usuario'),
        ('verificador', 'Verificador'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    puntos = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)
    avatar_actual = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(max_length=500, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    
    # Nuevo campo para el rol
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    
    # Estadísticas de verificador
    verificaciones_realizadas = models.IntegerField(default=0)
    verificaciones_aprobadas = models.IntegerField(default=0)
    puntos_verificacion = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
    
    def __str__(self):
        return f"{self.user.username} - Nivel {self.nivel} ({self.puntos} pts)"
    
    def sumar_puntos(self, puntos):
        """Suma puntos y actualiza nivel automáticamente"""
        self.puntos += puntos
        nivel_anterior = self.nivel
        
        # Sistema de niveles
        if self.puntos >= 1000:
            self.nivel = 5
        elif self.puntos >= 500:
            self.nivel = 4
        elif self.puntos >= 250:
            self.nivel = 3
        elif self.puntos >= 100:
            self.nivel = 2
        else:
            self.nivel = 1
        
        # Actualizar avatar si subió de nivel
        if self.nivel > nivel_anterior:
            nuevo_avatar = Avatar.objects.filter(nivel_requerido=self.nivel).first()
            if nuevo_avatar:
                self.avatar_actual = nuevo_avatar
        
        self.save()
        return self.nivel > nivel_anterior  # Retorna True si subió de nivel
    
    def progreso_siguiente_nivel(self):
        """Calcula el progreso hacia el siguiente nivel"""
        niveles = {1: 100, 2: 250, 3: 500, 4: 1000, 5: float('inf')}
        
        if self.nivel >= 5:
            return 100.0
        
        try:
            puntos_necesarios = niveles[self.nivel]
            puntos_nivel_anterior = niveles.get(self.nivel - 1, 0)
            
            if puntos_necesarios == puntos_nivel_anterior:
                return 100.0
            
            progreso = ((self.puntos - puntos_nivel_anterior) / (puntos_necesarios - puntos_nivel_anterior)) * 100
            return max(0.0, min(progreso, 100.0))
        except Exception:
            return 0.0
    
    def tasa_aprobacion_verificaciones(self):
        """Calcula el porcentaje de verificaciones aprobadas"""
        if self.verificaciones_realizadas == 0:
            return 100.0
        return (self.verificaciones_aprobadas / self.verificaciones_realizadas) * 100


# Datos de oxígeno por especie (kg O2/año según edad)
OXYGEN_RATES = {
    'ceiba': {'joven': 12, 'maduro': 30, 'viejo': 25},
    'guayacan': {'joven': 10, 'maduro': 25, 'viejo': 22},
    'roble': {'joven': 15, 'maduro': 35, 'viejo': 30},
    'saman': {'joven': 18, 'maduro': 40, 'viejo': 35},
    'caracoli': {'joven': 11, 'maduro': 28, 'viejo': 24},
    'pino': {'joven': 10, 'maduro': 22, 'viejo': 18},
    'default': {'joven': 12, 'maduro': 28, 'viejo': 25}
}


class Siembra(models.Model):
    """Registro de siembras realizadas por usuarios"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_verificacion', 'En Verificación'),
        ('validada', 'Validada'),
        ('rechazada', 'Rechazada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siembras')
    foto = models.ImageField(upload_to='siembras/%Y/%m/')
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    especie = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)
    puntos_otorgados = models.IntegerField(default=20)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_siembra = models.DateTimeField(auto_now_add=True)
    validada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validaciones')
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    notas_admin = models.TextField(blank=True)
    
    # Nuevos campos para oxígeno
    oxigeno_generado = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="kg O2/año")
    co2_absorbido = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="kg CO2/año")
    ultima_actualizacion_oxigeno = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_siembra']
        verbose_name = 'Siembra'
        verbose_name_plural = 'Siembras'
    
    def __str__(self):
        return f"Siembra de {self.usuario.username} - {self.fecha_siembra.strftime('%d/%m/%Y')}"
    
    def calcular_oxigeno(self):
        """Calcula el oxígeno generado según especie y edad del árbol"""
        if self.estado != 'validada':
            self.oxigeno_generado = 0
            self.co2_absorbido = 0
            return
        
        # Calcular años desde plantación
        dias_plantado = (datetime.now().date() - self.fecha_siembra.date()).days
        years = dias_plantado / 365.25
        
        # Determinar etapa del árbol
        if years < 2:
            stage = 'joven'
        elif years < 10:
            stage = 'maduro'
        else:
            stage = 'viejo'
        
        # Obtener tasa de oxígeno según especie
        especie_lower = self.especie.lower().strip() if self.especie else 'default'
        rate_data = OXYGEN_RATES.get(especie_lower, OXYGEN_RATES['default'])
        rate = rate_data[stage]
        
        # Calcular oxígeno (más edad = más oxígeno hasta cierto punto)
        factor_edad = min(years / 10, 1.0)  # Alcanza máximo en 10 años
        self.oxigeno_generado = Decimal(rate * factor_edad).quantize(Decimal('0.01'))
        
        # CO2 absorbido (aproximadamente 1.5 kg CO2 por cada kg O2)
        self.co2_absorbido = (self.oxigeno_generado * Decimal('1.5')).quantize(Decimal('0.01'))
        self.ultima_actualizacion_oxigeno = datetime.now()
        self.save()
    
    def edad_arbol_dias(self):
        """Retorna la edad del árbol en días"""
        return (datetime.now().date() - self.fecha_siembra.date()).days
    
    def edad_arbol_texto(self):
        """Retorna la edad del árbol en formato legible"""
        dias = self.edad_arbol_dias()
        if dias < 30:
            return f"{dias} días"
        elif dias < 365:
            meses = dias // 30
            return f"{meses} mes{'es' if meses > 1 else ''}"
        else:
            years = dias // 365
            return f"{years} año{'s' if years > 1 else ''}"
    
    def save(self, *args, **kwargs):
        """Optimizar imagen antes de guardar"""
        super().save(*args, **kwargs)
        
        if self.foto:
            try:
                img = Image.open(self.foto.path)
                
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                if img.height > 1200 or img.width > 1200:
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    img.save(self.foto.path, quality=85, optimize=True)
            except Exception as e:
                pass
    
    def validar(self, admin_user):
        """Valida la siembra y otorga puntos al usuario"""
        from django.utils import timezone
        
        self.estado = 'validada'
        self.validada_por = admin_user
        self.fecha_validacion = timezone.now()
        self.save()
        
        # Calcular oxígeno después de validar
        self.calcular_oxigeno()
        
        # Verificar si se debe crear una zona automática
        self.verificar_crear_zona_automatica()
        
        # NO otorgar puntos si el usuario es staff o superuser
        if self.usuario.is_staff or self.usuario.is_superuser:
            return False
        
        perfil = self.usuario.perfil
        subio_nivel = perfil.sumar_puntos(self.puntos_otorgados)
        
        return subio_nivel
    
    def verificar_crear_zona_automatica(self):
        """Verifica si hay más de 10 árboles en el área y crea una zona automática"""
        from math import radians, sin, cos, sqrt, atan2
        
        radio_busqueda = 1.0  # 1 km de radio
        
        # Contar siembras validadas cercanas (incluida esta)
        siembras_cercanas = Siembra.objects.filter(estado='validada')
        
        arboles_en_area = []
        for siembra in siembras_cercanas:
            distancia = self.calcular_distancia_entre_puntos(
                float(self.latitud), float(self.longitud),
                float(siembra.latitud), float(siembra.longitud)
            )
            if distancia <= radio_busqueda:
                arboles_en_area.append(siembra)
        
        # Si hay más de 10 árboles, crear zona automática
        if len(arboles_en_area) >= 10:
            # Verificar si ya existe una zona en esta área
            from .models import Zona
            zona_existente = False
            
            for zona in Zona.objects.filter(activa=True):
                distancia_zona = self.calcular_distancia_entre_puntos(
                    float(self.latitud), float(self.longitud),
                    float(zona.latitud), float(zona.longitud)
                )
                if distancia_zona <= 1.5:  # 1.5 km de tolerancia
                    zona_existente = True
                    # Actualizar contador de la zona existente
                    zona.contar_siembras()
                    break
            
            # Si no existe, crear nueva zona
            if not zona_existente:
                # Calcular centro de masa de los árboles
                lat_promedio = sum(float(s.latitud) for s in arboles_en_area) / len(arboles_en_area)
                lng_promedio = sum(float(s.longitud) for s in arboles_en_area) / len(arboles_en_area)
                
                # Determinar tipo de terreno predominante
                especies_comunes = {}
                for siembra in arboles_en_area:
                    if siembra.especie:
                        especies_comunes[siembra.especie] = especies_comunes.get(siembra.especie, 0) + 1
                
                especie_comun = max(especies_comunes.items(), key=lambda x: x[1])[0] if especies_comunes else "árboles"
                
                # Crear zona automática
                nueva_zona = Zona.objects.create(
                    nombre=f"Zona de Reforestación - {len(arboles_en_area)} árboles",
                    latitud=lat_promedio,
                    longitud=lng_promedio,
                    tipo_terreno='urbano',  # Por defecto, se puede mejorar con geolocalización
                    descripcion=f"Zona generada automáticamente con {len(arboles_en_area)} árboles plantados. Especie predominante: {especie_comun}.",
                    recomendaciones=f"Esta zona tiene una buena concentración de árboles. Se recomienda continuar plantando especies similares a {especie_comun}.",
                    activa=True,
                    auto_generada=True,
                    radio_km=radio_busqueda,
                    total_siembras=len(arboles_en_area)
                )
    
    def calcular_distancia_entre_puntos(self, lat1, lon1, lat2, lon2):
        """Calcula la distancia en km entre dos puntos usando fórmula de Haversine"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c


class Verificacion(models.Model):
    """Verificaciones realizadas por verificadores"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE, related_name='verificaciones')
    verificador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verificaciones_realizadas')
    
    # Fotos de verificación
    foto_verificacion = models.ImageField(upload_to='verificaciones/%Y/%m/')
    foto_ubicacion = models.ImageField(upload_to='verificaciones/%Y/%m/', null=True, blank=True)
    
    # Ubicación de la verificación
    latitud_verificacion = models.DecimalField(max_digits=9, decimal_places=6)
    longitud_verificacion = models.DecimalField(max_digits=9, decimal_places=6)
    
    notas_verificador = models.TextField(max_length=500, blank=True)
    fecha_verificacion = models.DateTimeField(auto_now_add=True)
    
    # Estado de la verificación
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Revisión por admin
    revisada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verificaciones_revisadas')
    fecha_revision = models.DateTimeField(null=True, blank=True)
    notas_admin = models.TextField(blank=True)
    
    # Puntos otorgados
    puntos_otorgados = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Verificación'
        verbose_name_plural = 'Verificaciones'
        ordering = ['-fecha_verificacion']
    
    def __str__(self):
        return f"Verificación de {self.verificador.username} - Siembra #{self.siembra.id}"
    
    def calcular_distancia(self):
        """Calcula la distancia entre la siembra y la verificación en metros"""
        from math import radians, sin, cos, sqrt, atan2
        
        # Radio de la Tierra en metros
        R = 6371000
        
        lat1 = radians(float(self.siembra.latitud))
        lon1 = radians(float(self.siembra.longitud))
        lat2 = radians(float(self.latitud_verificacion))
        lon2 = radians(float(self.longitud_verificacion))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return round(distance, 2)
    
    def calcular_puntos(self):
        """Calcula los puntos a otorgar según calidad de verificación"""
        PUNTOS_BASE = 50
        BONUS_PRECISION = 30  # Bonus por estar cerca
        BONUS_FOTOS_EXTRA = 20  # Bonus por foto adicional
        
        puntos = PUNTOS_BASE
        
        # Bonus por precisión de ubicación (< 20 metros)
        distancia = self.calcular_distancia()
        if distancia < 20:
            puntos += BONUS_PRECISION
        
        # Bonus por foto adicional de ubicación
        if self.foto_ubicacion:
            puntos += BONUS_FOTOS_EXTRA
        
        return puntos
    
    def aprobar(self, admin_user):
        """Aprueba la verificación y otorga puntos"""
        from django.utils import timezone
        
        self.estado = 'aprobada'
        self.revisada_por = admin_user
        self.fecha_revision = timezone.now()
        
        # Calcular y otorgar puntos
        self.puntos_otorgados = self.calcular_puntos()
        
        # Actualizar perfil del verificador
        perfil = self.verificador.perfil
        perfil.verificaciones_realizadas += 1
        perfil.verificaciones_aprobadas += 1
        perfil.puntos_verificacion += self.puntos_otorgados
        
        # Sumar puntos y verificar si subió de nivel
        subio_nivel = perfil.sumar_puntos(self.puntos_otorgados)
        
        # Guardar información sobre si alcanzó nivel 3 (desbloqueó verificación)
        self.desbloqueo_verificacion = (perfil.nivel == 3 and subio_nivel)
        
        # Cambiar estado de la siembra
        self.siembra.estado = 'en_verificacion'
        self.siembra.save()
        
        self.save()
    
    def rechazar(self, admin_user, razon=''):
        """Rechaza la verificación"""
        from django.utils import timezone
        
        self.estado = 'rechazada'
        self.revisada_por = admin_user
        self.fecha_revision = timezone.now()
        self.notas_admin = razon
        
        # Actualizar estadísticas del verificador
        perfil = self.verificador.perfil
        perfil.verificaciones_realizadas += 1
        perfil.save()
        
        # La siembra vuelve a pendiente
        self.siembra.estado = 'pendiente'
        self.siembra.save()
        
        self.save()


class Vivero(models.Model):
    """Viveros disponibles en el mapa"""
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    telefono = models.CharField(max_length=20, blank=True)
    horario = models.CharField(max_length=200, default="Lunes a Viernes 8am-5pm")
    especies_disponibles = models.TextField(help_text="Lista de especies separadas por comas")
    destacado = models.BooleanField(default=False, help_text="Viveros patrocinadores")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vivero'
        verbose_name_plural = 'Viveros'
    
    def __str__(self):
        return self.nombre


class Zona(models.Model):
    """Zonas de siembra recomendadas"""
    TIPO_TERRENO = [
        ('urbano', 'Urbano'),
        ('rural', 'Rural'),
        ('montaña', 'Montaña'),
        ('ribera', 'Ribera'),
        ('parque', 'Parque'),
    ]
    
    nombre = models.CharField(max_length=200)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    tipo_terreno = models.CharField(max_length=20, choices=TIPO_TERRENO)
    descripcion = models.TextField()
    recomendaciones = models.TextField(help_text="Especies recomendadas y consejos")
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    auto_generada = models.BooleanField(default=False, help_text="Zona generada automáticamente por concentración de siembras")
    radio_km = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Radio de cobertura en kilómetros")
    total_siembras = models.IntegerField(default=0, help_text="Total de siembras en esta zona")
    
    class Meta:
        verbose_name = 'Zona de Siembra'
        verbose_name_plural = 'Zonas de Siembra'
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo_terreno})"
    
    def contar_siembras(self):
        """Cuenta las siembras validadas en el radio de esta zona"""
        from math import radians, sin, cos, sqrt, atan2
        
        count = 0
        siembras = Siembra.objects.filter(estado='validada')
        
        for siembra in siembras:
            distancia = self.calcular_distancia(float(siembra.latitud), float(siembra.longitud))
            if distancia <= float(self.radio_km):
                count += 1
        
        self.total_siembras = count
        self.save()
        return count
    
    def calcular_distancia(self, lat2, lon2):
        """Calcula la distancia en km usando fórmula de Haversine"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1 = radians(float(self.latitud))
        lon1 = radians(float(self.longitud))
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c


# Señal para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se registra un usuario"""
    if created:
        avatar_inicial = Avatar.objects.filter(nivel_requerido=1).first()
        Perfil.objects.create(user=instance, avatar_actual=avatar_inicial)
    else:
        # Asegurar que el perfil existe
        if not hasattr(instance, 'perfil'):
            avatar_inicial = Avatar.objects.filter(nivel_requerido=1).first()
            Perfil.objects.create(user=instance, avatar_actual=avatar_inicial)