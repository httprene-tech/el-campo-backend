"""
Views para el módulo de calendario.
"""
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import TipoEvento, Evento, Recordatorio
from .serializers import (
    TipoEventoSerializer, TipoEventoListSerializer,
    EventoSerializer, EventoListSerializer,
    RecordatorioSerializer
)
from core.common.mixins import OptimizedQuerySetMixin, FilterByDateMixin

logger = logging.getLogger(__name__)


class TipoEventoViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de evento.
    """
    queryset = TipoEvento.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usa serializer ligero para listado."""
        if self.action == 'list':
            return TipoEventoListSerializer
        return TipoEventoSerializer

    def get_queryset(self):
        """Optimiza queries."""
        return super().get_queryset().order_by('nombre')


class EventoViewSet(OptimizedQuerySetMixin, FilterByDateMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar eventos del calendario.
    """
    queryset = Evento.objects.filter(eliminado=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usa serializer ligero para listado."""
        if self.action == 'list':
            return EventoListSerializer
        return EventoSerializer

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        # Optimizar con select_related
        queryset = queryset.select_related(
            'tipo', 'usuario', 'asignado_a'
        ).prefetch_related('recordatorios')
        
        # Filtros adicionales
        tipo_id = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        asignado_a = self.request.query_params.get('asignado_a')
        buscar = self.request.query_params.get('buscar')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if asignado_a:
            queryset = queryset.filter(asignado_a_id=asignado_a)
        
        if buscar:
            queryset = queryset.filter(
                Q(titulo__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(ubicacion__icontains=buscar)
            )
        
        # Filtro por rango de fechas (sobrescribe el de FilterByDateMixin)
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)
        
        return queryset.order_by('fecha_inicio', 'titulo')

    def perform_create(self, serializer):
        """Asigna el usuario que crea el evento."""
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """
        Retorna eventos próximos (fecha_inicio >= hoy).
        Query params:
            - dias: Número de días hacia adelante (default: 7)
        """
        dias = int(request.query_params.get('dias', 7))
        fecha_limite = timezone.now() + timedelta(days=dias)
        
        eventos = self.get_queryset().filter(
            fecha_inicio__gte=timezone.now(),
            fecha_inicio__lte=fecha_limite,
            estado__in=['PENDIENTE', 'EN_PROCESO'],
            eliminado=False
        )
        
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        """Retorna eventos del día de hoy."""
        hoy_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = hoy_inicio + timedelta(days=1)
        
        eventos = self.get_queryset().filter(
            fecha_inicio__gte=hoy_inicio,
            fecha_inicio__lt=hoy_fin,
            eliminado=False
        )
        
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca un evento como completado."""
        evento = self.get_object()
        evento.estado = 'COMPLETADO'
        evento.save()
        
        serializer = self.get_serializer(evento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Marca un evento como cancelado."""
        evento = self.get_object()
        evento.estado = 'CANCELADO'
        evento.save()
        
        serializer = self.get_serializer(evento)
        return Response(serializer.data)


class RecordatorioViewSet(OptimizedQuerySetMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar recordatorios.
    """
    queryset = Recordatorio.objects.filter(eliminado=False)
    serializer_class = RecordatorioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimiza queries y permite filtros."""
        queryset = super().get_queryset()
        
        # Optimizar con select_related
        queryset = queryset.select_related('evento', 'evento__tipo', 'evento__asignado_a')
        
        # Filtros
        evento_id = self.request.query_params.get('evento')
        enviado = self.request.query_params.get('enviado')
        
        if evento_id:
            queryset = queryset.filter(evento_id=evento_id)
        
        if enviado is not None:
            queryset = queryset.filter(enviado=enviado.lower() == 'true')
        
        return queryset.order_by('-fecha_envio', '-creado_en')
