"""
Views para el módulo de inventario.
"""
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Material, MovimientoInventario
from .serializers import (
    MaterialSerializer, MaterialListSerializer,
    MovimientoInventarioSerializer
)
from core.common.mixins import OptimizedQuerySetMixin, FilterByDateMixin
from core.common.utils import obtener_rango_mes, obtener_mes_anterior

logger = logging.getLogger(__name__)


class MaterialViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar materiales de inventario.
    """
    queryset = Material.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usa serializer ligero para listado."""
        if self.action == 'list':
            return MaterialListSerializer
        return MaterialSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        # No hay relaciones ForeignKey en Material, solo campos directos
        
        # Filtros
        tipo_inventario = self.request.query_params.get('tipo_inventario')
        stock_bajo = self.request.query_params.get('stock_bajo', '').lower() == 'true'
        buscar = self.request.query_params.get('buscar')
        
        if tipo_inventario:
            queryset = queryset.filter(tipo_inventario=tipo_inventario)
        
        if stock_bajo:
            queryset = queryset.filter(
                stock_actual__lte=F('stock_minimo_alerta')
            )
        
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(codigo__icontains=buscar) |
                Q(descripcion__icontains=buscar)
            )
        
        return queryset.order_by('tipo_inventario', 'nombre')

    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        """
        Retorna materiales con stock bajo (stock_actual <= stock_minimo_alerta).
        """
        materiales = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo_alerta')
        )
        serializer = self.get_serializer(materiales, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """
        Retorna el historial de movimientos de un material.
        """
        material = self.get_object()
        movimientos = MovimientoInventario.objects.filter(
            material=material,
            eliminado=False
        ).select_related('usuario', 'gasto', 'gasto__proyecto', 'gasto__categoria').order_by('-fecha', '-creado_en')
        
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)


class MovimientoInventarioViewSet(
    OptimizedQuerySetMixin, 
    FilterByDateMixin, 
    viewsets.ModelViewSet
):
    """
    ViewSet para gestionar movimientos de inventario.
    """
    queryset = MovimientoInventario.objects.filter(eliminado=False)
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        # Optimizar con select_related
        queryset = queryset.select_related(
            'material', 'usuario'
        )
        # Gasto puede ser None, así que solo lo incluimos si existe
        # No podemos usar select_related con relaciones opcionales que pueden ser None
        
        # Filtros adicionales
        material_id = self.request.query_params.get('material')
        tipo = self.request.query_params.get('tipo')
        tipo_inventario = self.request.query_params.get('tipo_inventario')
        
        if material_id:
            queryset = queryset.filter(material_id=material_id)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if tipo_inventario:
            queryset = queryset.filter(material__tipo_inventario=tipo_inventario)
        
        return queryset.order_by('-fecha', '-creado_en')

    def perform_create(self, serializer):
        """Asigna el usuario que registra el movimiento."""
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """
        Retorna un resumen de movimientos agrupado por mes.
        Query params:
            - material: ID del material (opcional)
            - tipo_inventario: Tipo de inventario (opcional)
        """
        queryset = self.get_queryset()
        
        material_id = request.query_params.get('material')
        tipo_inventario = request.query_params.get('tipo_inventario')
        
        if material_id:
            queryset = queryset.filter(material_id=material_id)
        if tipo_inventario:
            queryset = queryset.filter(material__tipo_inventario=tipo_inventario)
        
        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes', 'tipo', 'material__nombre').annotate(
            total_cantidad=Sum('cantidad'),
            cantidad_movimientos=Count('id')
        ).order_by('-mes', 'tipo')
        
        return Response(list(resumen))
