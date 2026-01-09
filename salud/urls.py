"""
URLs para el módulo de salud.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VacunacionViewSet, TratamientoViewSet,
    MortalidadViewSet, HistorialVeterinarioViewSet
)

router = DefaultRouter()
router.register(r'vacunaciones', VacunacionViewSet, basename='vacunacion')
router.register(r'tratamientos', TratamientoViewSet, basename='tratamiento')
router.register(r'mortalidades', MortalidadViewSet, basename='mortalidad')
router.register(r'historiales', HistorialVeterinarioViewSet, basename='historial-veterinario')

urlpatterns = [
    path('', include(router.urls)),
]
