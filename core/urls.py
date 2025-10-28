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
    
    # API endpoints
    path('api/coordenadas/', views.api_obtener_coordenadas, name='api_coordenadas'),
    path('api/estadisticas/', views.api_estadisticas_usuario, name='api_estadisticas'),
]