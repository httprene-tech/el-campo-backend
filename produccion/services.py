"""
Servicios de lógica de negocio para el módulo de producción.
"""
from decimal import Decimal
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Lote, Recoleccion, CalidadHuevo


class ProduccionService:
    """Servicio para operaciones de producción."""
    
    @staticmethod
    def calcular_productividad_lote(lote: Lote, dias: int = None) -> dict:
        """
        Calcula la productividad de un lote.
        
        Args:
            lote: Instancia de Lote
            dias: Número de días hacia atrás (default: todos)
            
        Returns:
            dict: Estadísticas de productividad
        """
        recolecciones = lote.recolecciones.filter(eliminado=False)
        
        if dias:
            fecha_limite = timezone.now().date() - timedelta(days=dias)
            recolecciones = recolecciones.filter(fecha__gte=fecha_limite)
        
        total_huevos = recolecciones.aggregate(total=Sum('cantidad_huevos'))['total'] or 0
        promedio_diario = recolecciones.aggregate(promedio=Avg('cantidad_huevos'))['promedio'] or 0
        cantidad_dias = recolecciones.values('fecha').distinct().count()
        
        # Calcular porcentaje de postura
        porcentaje_postura = 0
        if lote.cantidad_aves > 0 and cantidad_dias > 0:
            huevos_esperados = lote.cantidad_aves * cantidad_dias
            porcentaje_postura = (total_huevos / huevos_esperados * 100) if huevos_esperados > 0 else 0
        
        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'total_huevos': total_huevos,
            'promedio_diario': round(float(promedio_diario), 2),
            'cantidad_dias': cantidad_dias,
            'porcentaje_postura': round(float(porcentaje_postura), 2)
        }
    
    @staticmethod
    def calcular_calidad_promedio(lote: Lote) -> dict:
        """
        Calcula la calidad promedio de los huevos de un lote.
        
        Args:
            lote: Instancia de Lote
            
        Returns:
            dict: Estadísticas de calidad
        """
        calidad_huevos = CalidadHuevo.objects.filter(
            recoleccion__lote=lote,
            eliminado=False
        )
        
        total_primera = calidad_huevos.aggregate(total=Sum('cantidad_primera'))['total'] or 0
        total_segunda = calidad_huevos.aggregate(total=Sum('cantidad_segunda'))['total'] or 0
        total_descarte = calidad_huevos.aggregate(total=Sum('cantidad_descarte'))['total'] or 0
        total_evaluado = total_primera + total_segunda + total_descarte
        
        porcentaje_primera = (total_primera / total_evaluado * 100) if total_evaluado > 0 else 0
        porcentaje_segunda = (total_segunda / total_evaluado * 100) if total_evaluado > 0 else 0
        porcentaje_descarte = (total_descarte / total_evaluado * 100) if total_evaluado > 0 else 0
        
        return {
            'total_primera': total_primera,
            'total_segunda': total_segunda,
            'total_descarte': total_descarte,
            'total_evaluado': total_evaluado,
            'porcentaje_primera': round(float(porcentaje_primera), 2),
            'porcentaje_segunda': round(float(porcentaje_segunda), 2),
            'porcentaje_descarte': round(float(porcentaje_descarte), 2)
        }
