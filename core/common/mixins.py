"""
Mixins para ViewSets que optimizan queries y proporcionan funcionalidad común.
"""
from rest_framework.response import Response
from django.db.models import Q


class OptimizedQuerySetMixin:
    """
    Mixin que optimiza los querysets con select_related y prefetch_related.
    Debe ser usado en ViewSets que necesiten optimización de queries.
    """
    def get_queryset(self):
        """
        Retorna un queryset optimizado.
        Debe ser sobrescrito en cada ViewSet para especificar las relaciones.
        """
        return super().get_queryset()


class FilterByDateMixin:
    """
    Mixin que agrega filtros por rango de fechas.
    Requiere que el modelo tenga un campo 'fecha' o 'creado_en'.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        # Determinar campo de fecha
        fecha_field = 'fecha' if hasattr(queryset.model, 'fecha') else 'creado_en'
        
        if fecha_inicio:
            queryset = queryset.filter(**{f'{fecha_field}__gte': fecha_inicio})
        if fecha_fin:
            queryset = queryset.filter(**{f'{fecha_field}__lte': fecha_fin})
        
        return queryset


class SoftDeleteMixin:
    """
    Mixin que filtra objetos eliminados por defecto.
    Requiere que el modelo herede de SoftDeleteModel.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Por defecto, excluir objetos eliminados
        incluir_eliminados = self.request.query_params.get('incluir_eliminados', '').lower() == 'true'
        
        if not incluir_eliminados:
            queryset = queryset.filter(eliminado=False)
        
        return queryset
