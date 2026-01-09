"""
URLs para el módulo de calendario.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoEventoViewSet, EventoViewSet, RecordatorioViewSet

router = DefaultRouter()
router.register(r'tipos', TipoEventoViewSet, basename='tipo-evento')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'recordatorios', RecordatorioViewSet, basename='recordatorio')

urlpatterns = [
    path('', include(router.urls)),
]
