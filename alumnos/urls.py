from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear/', views.crear_alumno, name='crear_alumno'),
    path('editar/<int:pk>/', views.editar_alumno, name='editar_alumno'),
    path('eliminar/<int:pk>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('enviar-pdf/<int:alumno_id>/', views.enviar_pdf, name='enviar_pdf'),
]