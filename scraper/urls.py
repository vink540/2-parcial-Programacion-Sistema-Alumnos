from django.urls import path
from . import views


urlpatterns = [
    path('', views.scraper, name='scraper'),
    path('enviar-email/', views.scraper, name='enviar_wikipedia_email'),
]