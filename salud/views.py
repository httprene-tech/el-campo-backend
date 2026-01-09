"""
Views para el módulo de salud.
"""
import logging
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Vacunacion, Tratamiento, Mortalidad, HistorialVeterinario
from .serializers import (
    VacunacionSerializer, VacunacionListSerializer,
    TratamientoSerializer, TratamientoListSerializer,
    MortalidadSerializer, MortalidadListSerializer,
    HistorialVeterinarioSerializer
)
from core.common.mixins import OptimizedQuerySetMixin, FilterByDateMixin

logger = logging.getLogger(__name__)


class VacunacionViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar vacunaciones."""
    queryset = Vacunacion.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return VacunacionListSerializer
        return VacunacionSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('lote', 'lote__galpon', 'aplicado_por')
        
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        return queryset.order_by('-fecha')

    def perform_create(self, serializer):
        """Asigna el usuario que registra la vacunación."""
        serializer.save(aplicado_por=self.request.user)


class TratamientoViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar tratamientos."""
    queryset = Tratamiento.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return TratamientoListSerializer
        return TratamientoSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('lote', 'aplicado_por')
        
        lote_id = self.request.query_params.get('lote')
        tipo = self.request.query_params.get('tipo')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por fecha_inicio
        fecha_field = 'fecha_inicio'
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(**{f'{fecha_field}__gte': fecha_inicio})
        if fecha_fin:
            queryset = queryset.filter(**{f'{fecha_field}__lte': fecha_fin})
        
        return queryset.order_by('-fecha_inicio')

    def perform_create(self, serializer):
        """Asigna el usuario que registra el tratamiento."""
        serializer.save(aplicado_por=self.request.user)


class MortalidadViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar mortalidad."""
    queryset = Mortalidad.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MortalidadListSerializer
        return MortalidadSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('lote', 'registrado_por')
        
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        return queryset.order_by('-fecha')

    def perform_create(self, serializer):
        """Asigna el usuario que registra la mortalidad."""
        serializer.save(registrado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """Retorna resumen de mortalidad por mes."""
        queryset = self.get_queryset()
        lote_id = request.query_params.get('lote')
        
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes', 'lote__nombre').annotate(
            total_aves=Sum('cantidad_aves')
        ).order_by('-mes')
        
        return Response(list(resumen))


class HistorialVeterinarioViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar historiales veterinarios."""
    queryset = HistorialVeterinario.objects.filter(eliminado=False)
    serializer_class = HistorialVeterinarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimiza queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'lote', 'lote__galpon', 'veterinario_responsable'
        ).prefetch_related(
            'lote__vacunaciones',
            'lote__tratamientos',
            'lote__mortalidades'
        )
        
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        return queryset.order_by('-creado_en')
