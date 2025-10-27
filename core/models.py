from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

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
            return 100
        puntos_necesarios = niveles[self.nivel]
        puntos_nivel_anterior = niveles.get(self.nivel - 1, 0)
        progreso = ((self.puntos - puntos_nivel_anterior) / (puntos_necesarios - puntos_nivel_anterior)) * 100
        return min(progreso, 100)


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
    
    def validar(self, admin_user):
        """Valida la siembra y otorga puntos al usuario"""
        from django.utils import timezone
        self.estado = 'validada'
        self.validada_por = admin_user
        self.fecha_validacion = timezone.now()
        self.save()
        
        # Otorgar puntos al usuario
        perfil = self.usuario.perfil
        subio_nivel = perfil.sumar_puntos(self.puntos_otorgados)
        
        return subio_nivel


# Señales para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se registra un usuario"""
    if created:
        avatar_inicial = Avatar.objects.filter(nivel_requerido=1).first()
        Perfil.objects.create(user=instance, avatar_actual=avatar_inicial)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()