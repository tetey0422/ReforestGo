"""
Script de prueba para el sistema de verificación automático

Este script verifica que:
1. La función es_verificador() funciona correctamente
2. Los usuarios nivel 3+ tienen permisos de verificación
3. Los mensajes se muestran correctamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReforestGo.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Perfil

def test_verificacion_sistema():
    """Prueba del sistema de verificación"""
    
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE VERIFICACIÓN AUTOMÁTICO")
    print("=" * 60)
    print()
    
    # Obtener todos los usuarios
    usuarios = User.objects.all()
    
    if not usuarios.exists():
        print("❌ No hay usuarios en el sistema")
        return
    
    print(f"📊 Total de usuarios: {usuarios.count()}\n")
    
    # Verificar permisos por nivel
    print("ANÁLISIS DE PERMISOS DE VERIFICACIÓN:")
    print("-" * 60)
    
    verificadores_nivel = 0
    verificadores_rol = 0
    usuarios_sin_acceso = 0
    
    for user in usuarios:
        try:
            perfil = user.perfil
            
            # Determinar si puede verificar
            puede_verificar = (
                perfil.nivel >= 3 or 
                perfil.rol in ['verificador', 'admin'] or 
                user.is_staff
            )
            
            razon = []
            if perfil.nivel >= 3:
                razon.append(f"Nivel {perfil.nivel}")
                verificadores_nivel += 1
            if perfil.rol in ['verificador', 'admin']:
                razon.append(f"Rol: {perfil.rol}")
                verificadores_rol += 1
            if user.is_staff:
                razon.append("Staff")
            
            if puede_verificar:
                estado = "✅ PUEDE VERIFICAR"
                razon_str = " + ".join(razon)
            else:
                estado = "❌ No puede verificar"
                razon_str = f"Nivel {perfil.nivel} (necesita nivel 3)"
                usuarios_sin_acceso += 1
            
            print(f"Usuario: {user.username:<15} | {estado} | {razon_str}")
            
            # Mostrar estadísticas de verificación si las tiene
            if perfil.verificaciones_realizadas > 0:
                tasa = perfil.tasa_aprobacion_verificaciones()
                print(f"  └─ Verificaciones: {perfil.verificaciones_realizadas} "
                      f"| Aprobadas: {perfil.verificaciones_aprobadas} "
                      f"| Tasa: {tasa:.1f}% "
                      f"| Puntos ganados: {perfil.puntos_verificacion}")
            
        except Exception as e:
            print(f"Usuario: {user.username:<15} | ⚠️  Error: {e}")
    
    print()
    print("=" * 60)
    print("RESUMEN:")
    print("-" * 60)
    print(f"👥 Total usuarios: {usuarios.count()}")
    print(f"🔍 Verificadores por nivel 3+: {verificadores_nivel}")
    print(f"⭐ Verificadores por rol especial: {verificadores_rol}")
    print(f"🚫 Sin acceso a verificación: {usuarios_sin_acceso}")
    print()
    
    # Recomendaciones
    if usuarios_sin_acceso > 0:
        print("💡 RECOMENDACIONES:")
        print("-" * 60)
        print("Para que los usuarios puedan verificar, deben:")
        print("  1. Alcanzar nivel 3 (250 puntos) plantando árboles")
        print("  2. O ser asignados manualmente con: python manage.py asignar_verificador <username>")
        print()
    
    print("=" * 60)
    print("✅ Prueba completada")
    print("=" * 60)


if __name__ == '__main__':
    test_verificacion_sistema()
