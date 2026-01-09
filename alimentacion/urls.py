"""
URLs para el módulo de alimentación.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProveedorAlimentoViewSet, FormulaAlimentoViewSet,
    RacionViewSet, ConsumoDiarioViewSet
)

router = DefaultRouter()
router.register(r'proveedores', ProveedorAlimentoViewSet, basename='proveedor-alimento')
router.register(r'formulas', FormulaAlimentoViewSet, basename='formula-alimento')
router.register(r'raciones', RacionViewSet, basename='racion')
router.register(r'consumos', ConsumoDiarioViewSet, basename='consumo-diario')

urlpatterns = [
    path('', include(router.urls)),
]
