"""
URLs para el módulo de producción.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalponViewSet, LoteViewSet, RecoleccionViewSet, CalidadHuevoViewSet

router = DefaultRouter()
router.register(r'galpones', GalponViewSet, basename='galpon')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'recolecciones', RecoleccionViewSet, basename='recoleccion')
router.register(r'calidad-huevos', CalidadHuevoViewSet, basename='calidad-huevo')

urlpatterns = [
    path('', include(router.urls)),
]
