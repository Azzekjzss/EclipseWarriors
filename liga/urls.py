from django.urls import path
from . import views

urlpatterns = [
    path('', views.ranking, name='ranking'),
    path('registro/', views.registro, name='registro'),
    path('perfil/<int:jugador_id>/', views.public_perfil, name='public_perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('mis-combates/', views.mis_combates, name='mis_combates'),
    path('historial/', views.historial_combates, name='historial'),
    path('salon-fama/', views.salon_fama, name='salon_fama'),
    path('gestionar-combate/<int:combate_id>/<str:accion>/', views.gestionar_combate, name='gestionar_combate'),
    
    # RUTA NUEVA: Para que el botón 'RETAR' funcione
    path('retar/<int:oponente_id>/', views.retar, name='retar'),
]