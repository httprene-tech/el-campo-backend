"""
URLs para el módulo de inventario.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r'materiales', MaterialViewSet, basename='material')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

urlpatterns = [
    path('', include(router.urls)),
]
