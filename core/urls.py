from django.urls import path
from . import views

app_name = 'reforest'

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('siembras/', views.mis_siembras, name='mis_siembras'),
    path('registrar-siembra/', views.registrar_siembra, name='registrar_siembra'),
    path('cambiar-avatar/<int:avatar_id>/', views.cambiar_avatar, name='cambiar_avatar'),
    path('mapa/', views.mapa, name='mapa'),
    path('ranking/', views.ranking, name='ranking'),
]
