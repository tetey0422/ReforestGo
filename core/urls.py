from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'reforest'

urlpatterns = [
    # Páginas principales
    path('', views.index, name='index'),
    path('mapa/', views.mapa, name='mapa'),
    path('ranking/', views.ranking, name='ranking'),
    
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Perfil y siembras (requieren login)
    path('perfil/', views.perfil, name='perfil'),
    path('siembras/', views.mis_siembras, name='mis_siembras'),
    path('registrar-siembra/', views.registrar_siembra, name='registrar_siembra'),
    path('cambiar-avatar/<int:avatar_id>/', views.cambiar_avatar, name='cambiar_avatar'),
    
    # Estadísticas de oxígeno
    path('oxigeno/', views.estadisticas_oxigeno, name='estadisticas_oxigeno'),
    
    # Sistema de verificación (requieren rol verificador)
    path('verificacion/mapa/', views.mapa_verificacion, name='mapa_verificacion'),
    path('verificacion/arbol/<int:siembra_id>/', views.verificar_arbol, name='verificar_arbol'),
    path('verificacion/mis-verificaciones/', views.mis_verificaciones, name='mis_verificaciones'),
    
    # Panel de administrador
    path('admin/verificaciones/', views.admin_verificaciones, name='admin_verificaciones'),
    path('admin/verificacion/<int:verificacion_id>/', views.revisar_verificacion, name='revisar_verificacion'),
    
    # API endpoints
    path('api/coordenadas/', views.api_obtener_coordenadas, name='api_coordenadas'),
    path('api/estadisticas/', views.api_estadisticas_usuario, name='api_estadisticas'),
    path('api/siembras-cercanas/', views.api_siembras_cercanas, name='api_siembras_cercanas'),
]