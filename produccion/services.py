"""
Servicios de lógica de negocio para el módulo de producción.

Este módulo encapsula toda la lógica de negocio relacionada con:
- Cálculo de productividad de lotes
- Estadísticas de recolección
- Calidad de huevos
- Análisis de rendimiento
"""
from decimal import Decimal
from typing import Optional, Dict, List, Any
from datetime import date, timedelta

from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone

from .models import Galpon, Lote, Recoleccion, CalidadHuevo


class ProduccionService:
    """
    Servicio para operaciones de producción.
    Centraliza toda la lógica de negocio del módulo.
    """

    # =========================================================================
    # PRODUCTIVIDAD DE LOTES
    # =========================================================================

    @staticmethod
    def calcular_productividad_lote(lote: Lote) -> Dict[str, Any]:
        """
        Calcula métricas de productividad para un lote.

        Args:
            lote: Instancia de Lote

        Returns:
            dict: Métricas de productividad incluyendo:
                - total_huevos: Total de huevos recolectados
                - promedio_diario: Promedio diario de huevos
                - porcentaje_postura: Porcentaje de postura (huevos/aves*100)
                - dias_produccion: Días que el lote ha estado en producción
        """
        recolecciones = Recoleccion.objects.filter(
            lote=lote,
            eliminado=False
        )

        total_huevos = recolecciones.aggregate(
            total=Sum('cantidad_huevos')
        )['total'] or 0

        dias_con_recoleccion = recolecciones.values('fecha').distinct().count()
        promedio_diario = total_huevos / dias_con_recoleccion if dias_con_recoleccion > 0 else 0

        # Porcentaje de postura: (huevos diarios / cantidad de aves) * 100
        porcentaje_postura = Decimal('0')
        if lote.cantidad_aves > 0 and promedio_diario > 0:
            porcentaje_postura = (Decimal(str(promedio_diario)) / lote.cantidad_aves) * 100

        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'total_huevos': total_huevos,
            'promedio_diario': round(promedio_diario, 2),
            'porcentaje_postura': round(float(porcentaje_postura), 2),
            'dias_produccion': dias_con_recoleccion,
            'cantidad_aves': lote.cantidad_aves,
            'estado': lote.estado
        }

    @staticmethod
    def calcular_calidad_promedio(lote: Lote) -> Dict[str, Any]:
        """
        Calcula estadísticas de calidad de huevos para un lote.

        Args:
            lote: Instancia de Lote

        Returns:
            dict: Estadísticas de calidad incluyendo:
                - total_evaluados: Total de huevos evaluados
                - porcentaje_primera: % de huevos de primera
                - porcentaje_segunda: % de huevos de segunda
                - porcentaje_descarte: % de huevos descartados
        """
        calidades = CalidadHuevo.objects.filter(
            recoleccion__lote=lote,
            eliminado=False
        ).aggregate(
            total_primera=Sum('cantidad_primera'),
            total_segunda=Sum('cantidad_segunda'),
            total_descarte=Sum('cantidad_descarte')
        )

        total_primera = calidades['total_primera'] or 0
        total_segunda = calidades['total_segunda'] or 0
        total_descarte = calidades['total_descarte'] or 0
        total_evaluados = total_primera + total_segunda + total_descarte

        if total_evaluados == 0:
            return {
                'total_evaluados': 0,
                'porcentaje_primera': 0,
                'porcentaje_segunda': 0,
                'porcentaje_descarte': 0
            }

        return {
            'total_evaluados': total_evaluados,
            'porcentaje_primera': round((total_primera / total_evaluados) * 100, 2),
            'porcentaje_segunda': round((total_segunda / total_evaluados) * 100, 2),
            'porcentaje_descarte': round((total_descarte / total_evaluados) * 100, 2)
        }

    # =========================================================================
    # ESTADÍSTICAS DE GALPÓN
    # =========================================================================

    @staticmethod
    def obtener_ocupacion_galpon(galpon: Galpon) -> Dict[str, Any]:
        """
        Calcula la ocupación actual de un galpón.

        Args:
            galpon: Instancia de Galpon

        Returns:
            dict: Información de ocupación
        """
        cantidad_actual = galpon.lotes.filter(
            activo=True,
            eliminado=False
        ).aggregate(total=Sum('cantidad_aves'))['total'] or 0

        porcentaje_ocupacion = Decimal('0')
        if galpon.capacidad_maxima > 0:
            porcentaje_ocupacion = (Decimal(str(cantidad_actual)) / galpon.capacidad_maxima) * 100

        return {
            'galpon_id': galpon.id,
            'galpon_nombre': galpon.nombre,
            'capacidad_maxima': galpon.capacidad_maxima,
            'cantidad_actual': cantidad_actual,
            'espacios_disponibles': galpon.capacidad_maxima - cantidad_actual,
            'porcentaje_ocupacion': round(float(porcentaje_ocupacion), 2)
        }

    # =========================================================================
    # REPORTES Y RESÚMENES
    # =========================================================================

    @staticmethod
    def obtener_resumen_produccion_mensual(
        lote: Optional[Lote] = None,
        año: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de producción agrupado por mes.

        Args:
            lote: Opcional, filtrar por lote específico
            año: Opcional, filtrar por año
            mes: Opcional, filtrar por mes

        Returns:
            list: Lista de resúmenes mensuales
        """
        queryset = Recoleccion.objects.filter(eliminado=False)

        if lote:
            queryset = queryset.filter(lote=lote)
        if año:
            queryset = queryset.filter(fecha__year=año)
        if mes:
            queryset = queryset.filter(fecha__month=mes)

        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes').annotate(
            total_huevos=Sum('cantidad_huevos'),
            cantidad_recolecciones=Count('id'),
            promedio_por_recoleccion=Avg('cantidad_huevos')
        ).order_by('-mes')

        return [
            {
                'mes': item['mes'],
                'total_huevos': item['total_huevos'] or 0,
                'cantidad_recolecciones': item['cantidad_recolecciones'],
                'promedio_por_recoleccion': round(item['promedio_por_recoleccion'] or 0, 2)
            }
            for item in resumen
        ]

    @staticmethod
    def obtener_lotes_activos_con_estadisticas() -> List[Dict[str, Any]]:
        """
        Obtiene todos los lotes activos con sus estadísticas básicas.

        Returns:
            list: Lista de lotes con estadísticas
        """
        lotes = Lote.objects.filter(
            activo=True,
            eliminado=False
        ).select_related('galpon')

        resultados = []
        for lote in lotes:
            productividad = ProduccionService.calcular_productividad_lote(lote)
            resultados.append({
                **productividad,
                'galpon_nombre': lote.galpon.nombre,
                'edad_dias': lote.edad_dias
            })

        return resultados
