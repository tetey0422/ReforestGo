"""
Comando de gestión para asignar rol de verificador manualmente
Uso: python manage.py asignar_verificador <username>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Asigna rol de verificador a un usuario específico'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            perfil = user.perfil
            
            if perfil.rol == 'verificador':
                self.stdout.write(
                    self.style.WARNING(f'⚠️  El usuario {username} ya es verificador')
                )
                return
            
            if perfil.rol == 'admin':
                self.stdout.write(
                    self.style.WARNING(f'⚠️  El usuario {username} ya es admin (tiene permisos superiores)')
                )
                return
            
            # Asignar rol de verificador
            perfil.rol = 'verificador'
            perfil.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Usuario {username} ahora es verificador\n'
                    f'   Nivel actual: {perfil.nivel}\n'
                    f'   Puntos: {perfil.puntos}\n'
                    f'   Nota: Los usuarios nivel 3+ pueden verificar automáticamente.'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuario "{username}" no existe')
            )
            self.stdout.write('\nUsuarios disponibles:')
            for u in User.objects.all()[:10]:
                self.stdout.write(f'  - {u.username} (Nivel {u.perfil.nivel})')
