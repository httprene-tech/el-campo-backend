"""
Views para el módulo de producción.
"""
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Galpon, Lote, Recoleccion, CalidadHuevo
from .serializers import (
    GalponSerializer, GalponListSerializer,
    LoteSerializer, LoteListSerializer,
    RecoleccionSerializer, RecoleccionListSerializer,
    CalidadHuevoSerializer
)
from core.common.mixins import OptimizedQuerySetMixin, FilterByDateMixin

logger = logging.getLogger(__name__)


class GalponViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar galpones."""
    queryset = Galpon.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return GalponListSerializer
        return GalponSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('lotes')
        
        activo = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset.order_by('nombre')


class LoteViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar lotes."""
    queryset = Lote.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return LoteListSerializer
        return LoteSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('galpon').prefetch_related(
            'recolecciones',
            'vacunaciones',
            'tratamientos',
            'mortalidades',
            'raciones',
            'consumos_diarios'
        )
        
        galpon_id = self.request.query_params.get('galpon')
        estado = self.request.query_params.get('estado')
        activo = self.request.query_params.get('activo')
        
        if galpon_id:
            queryset = queryset.filter(galpon_id=galpon_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        # Filtro por fecha de ingreso
        fecha_field = 'fecha_ingreso'
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(**{f'{fecha_field}__gte': fecha_inicio})
        if fecha_fin:
            queryset = queryset.filter(**{f'{fecha_field}__lte': fecha_fin})
        
        return queryset.order_by('-fecha_ingreso')

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Retorna estadísticas del lote usando servicios."""
        lote = self.get_object()
        
        # Usar servicios para calcular estadísticas
        productividad = ProduccionService.calcular_productividad_lote(lote)
        calidad = ProduccionService.calcular_calidad_promedio(lote)
        
        return Response({
            **productividad,
            'edad_dias': lote.edad_dias,
            'calidad': calidad
        })


class RecoleccionViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar recolecciones."""
    queryset = Recoleccion.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return RecoleccionListSerializer
        return RecoleccionSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'lote', 'lote__galpon', 'recolectado_por'
        ).prefetch_related('calidad_huevos')
        
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        return queryset.order_by('-fecha', '-hora_recoleccion')

    def perform_create(self, serializer):
        """Asigna el usuario que registra la recolección."""
        serializer.save(recolectado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """Retorna resumen de recolecciones por mes."""
        queryset = self.get_queryset()
        lote_id = request.query_params.get('lote')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes', 'lote__nombre').annotate(
            total_huevos=Sum('cantidad_huevos'),
            cantidad_recolecciones=Count('id')
        ).order_by('-mes')
        
        return Response(list(resumen))


class CalidadHuevoViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar calidad de huevos."""
    queryset = CalidadHuevo.objects.filter(eliminado=False)
    serializer_class = CalidadHuevoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'recoleccion', 'recoleccion__lote', 'evaluado_por'
        )
        
        recoleccion_id = self.request.query_params.get('recoleccion')
        tipo_defecto = self.request.query_params.get('tipo_defecto')
        
        if recoleccion_id:
            queryset = queryset.filter(recoleccion_id=recoleccion_id)
        if tipo_defecto:
            queryset = queryset.filter(tipo_defecto=tipo_defecto)
        
        return queryset.order_by('-recoleccion__fecha')

    def perform_create(self, serializer):
        """Asigna el usuario que evalúa."""
        serializer.save(evaluado_por=self.request.user)
