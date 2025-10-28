from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    puntos = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)
    avatar_actual = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(max_length=500, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    
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
        
        # Si ya está en el nivel máximo
        if self.nivel >= 5:
            return 100.0
        
        try:
            puntos_necesarios = niveles[self.nivel]
            puntos_nivel_anterior = niveles.get(self.nivel - 1, 0)
            
            # Evitar división por cero
            if puntos_necesarios == puntos_nivel_anterior:
                return 100.0
            
            progreso = ((self.puntos - puntos_nivel_anterior) / (puntos_necesarios - puntos_nivel_anterior)) * 100
            return max(0.0, min(progreso, 100.0))  # Asegurar que esté entre 0 y 100
        except Exception:
            return 0.0


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
    
    class Meta:
        verbose_name = 'Zona de Siembra'
        verbose_name_plural = 'Zonas de Siembra'
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo_terreno})"


class Siembra(models.Model):
    """Registro de siembras realizadas por usuarios"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
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
    
    class Meta:
        ordering = ['-fecha_siembra']
        verbose_name = 'Siembra'
        verbose_name_plural = 'Siembras'
    
    def __str__(self):
        return f"Siembra de {self.usuario.username} - {self.fecha_siembra.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        """Optimizar imagen antes de guardar"""
        super().save(*args, **kwargs)
        
        if self.foto:
            try:
                img = Image.open(self.foto.path)
                
                # Convertir RGBA a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Redimensionar si es muy grande
                if img.height > 1200 or img.width > 1200:
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    img.save(self.foto.path, quality=85, optimize=True)
            except Exception as e:
                # Si hay error al procesar la imagen, continuar sin optimizar
                pass
    
    def validar(self, admin_user):
            """Valida la siembra y otorga puntos al usuario"""
            from django.utils import timezone
        
            print(f"🔍 DEBUG - Validando siembra de: {self.usuario.username}")
            print(f"🔍 DEBUG - ¿Es staff? {self.usuario.is_staff}")
            print(f"🔍 DEBUG - ¿Es superuser? {self.usuario.is_superuser}")
        
            self.estado = 'validada'
            self.validada_por = admin_user
            self.fecha_validacion = timezone.now()
            self.save()
        
            # NO otorgar puntos si el usuario es staff o superuser
            if self.usuario.is_staff or self.usuario.is_superuser:
                print(f"❌ DEBUG - NO se otorgan puntos porque el usuario es admin/staff")
                return False
        
            # Otorgar puntos solo a usuarios normales
            print(f"✅ DEBUG - Usuario normal, otorgando {self.puntos_otorgados} puntos")
        
            perfil = self.usuario.perfil
            puntos_antes = perfil.puntos
            nivel_antes = perfil.nivel
        
            print(f"📊 DEBUG - Antes: {puntos_antes} puntos, Nivel {nivel_antes}")
        
            subio_nivel = perfil.sumar_puntos(self.puntos_otorgados)
        
            print(f"📊 DEBUG - Después: {perfil.puntos} puntos, Nivel {perfil.nivel}")
            print(f"🎉 DEBUG - ¿Subió de nivel? {subio_nivel}")
        
            return subio_nivel


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