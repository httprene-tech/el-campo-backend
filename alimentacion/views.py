"""
Views para el módulo de alimentación.
"""
import logging
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import ProveedorAlimento, FormulaAlimento, Racion, ConsumoDiario
from .serializers import (
    ProveedorAlimentoSerializer,
    FormulaAlimentoSerializer, FormulaAlimentoListSerializer,
    RacionSerializer, RacionListSerializer,
    ConsumoDiarioSerializer, ConsumoDiarioListSerializer
)
from core.common.mixins import OptimizedQuerySetMixin, FilterByDateMixin

logger = logging.getLogger(__name__)


class ProveedorAlimentoViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar proveedores de alimento."""
    queryset = ProveedorAlimento.objects.filter(eliminado=False)
    serializer_class = ProveedorAlimentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        activo = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset.order_by('nombre')


class FormulaAlimentoViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar fórmulas de alimento."""
    queryset = FormulaAlimento.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return FormulaAlimentoListSerializer
        return FormulaAlimentoSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        activa = self.request.query_params.get('activa')
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        return queryset.order_by('edad_minima_semanas', 'nombre')


class RacionViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar raciones."""
    queryset = Racion.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return RacionListSerializer
        return RacionSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('lote', 'formula', 'registrado_por')
        
        lote_id = self.request.query_params.get('lote')
        formula_id = self.request.query_params.get('formula')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        if formula_id:
            queryset = queryset.filter(formula_id=formula_id)
        
        return queryset.order_by('-fecha')

    def perform_create(self, serializer):
        """Asigna el usuario que registra la ración."""
        serializer.save(registrado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """Retorna resumen de raciones por mes."""
        queryset = self.get_queryset()
        lote_id = request.query_params.get('lote')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes', 'lote__nombre', 'formula__nombre').annotate(
            total_kg=Sum('cantidad_kg'),
            promedio_kg=Avg('cantidad_kg'),
            cantidad_raciones=Count('id')
        ).order_by('-mes')
        
        return Response(list(resumen))


class ConsumoDiarioViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar consumos diarios."""
    queryset = ConsumoDiario.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsumoDiarioListSerializer
        return ConsumoDiarioSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'lote', 'material_alimento', 'registrado_por'
        )
        
        lote_id = self.request.query_params.get('lote')
        material_id = self.request.query_params.get('material')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        if material_id:
            queryset = queryset.filter(material_alimento_id=material_id)
        
        return queryset.order_by('-fecha')

    def perform_create(self, serializer):
        """Asigna el usuario que registra el consumo."""
        serializer.save(registrado_por=self.request.user)
