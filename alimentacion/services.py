"""
Servicios de lógica de negocio para el módulo de alimentación.

Este módulo encapsula toda la lógica de negocio relacionada con:
- Gestión de raciones diarias
- Control de consumo de alimento
- Integración con inventario (CRÍTICO)
- Análisis de eficiencia alimenticia
"""
from decimal import Decimal
from typing import Optional, Dict, List, Any
from datetime import date, timedelta

from django.db import transaction
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import ProveedorAlimento, FormulaAlimento, Racion, ConsumoDiario
from produccion.models import Lote
from inventario.models import Material
from inventario.services import InventarioService


class AlimentacionService:
    """
    Servicio para operaciones de alimentación.
    
    IMPORTANTE: Este servicio integra con InventarioService para
    actualizar el stock cuando se registra consumo de alimento.
    """

    # =========================================================================
    # RACIONES
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def registrar_racion(
        lote: Lote,
        formula: FormulaAlimento,
        cantidad_kg: Decimal,
        usuario: User,
        notas: str = ""
    ) -> Racion:
        """
        Registra una ración diaria de alimento para un lote.

        Args:
            lote: Instancia de Lote
            formula: Fórmula de alimento a usar
            cantidad_kg: Cantidad en kilogramos
            usuario: Usuario que registra
            notas: Notas adicionales

        Returns:
            Racion: Instancia creada

        Raises:
            ValidationError: Si la fórmula no es apropiada para la edad del lote
        """
        # Validar que la fórmula sea apropiada para la edad del lote
        edad_semanas = lote.edad_dias // 7
        
        if formula.edad_minima_semanas > edad_semanas:
            raise ValidationError(
                f"La fórmula '{formula.nombre}' es para aves de al menos "
                f"{formula.edad_minima_semanas} semanas. El lote tiene {edad_semanas} semanas."
            )
        
        if formula.edad_maxima_semanas and formula.edad_maxima_semanas < edad_semanas:
            raise ValidationError(
                f"La fórmula '{formula.nombre}' es para aves de máximo "
                f"{formula.edad_maxima_semanas} semanas. El lote tiene {edad_semanas} semanas."
            )

        racion = Racion.objects.create(
            lote=lote,
            formula=formula,
            fecha=timezone.now().date(),
            cantidad_kg=cantidad_kg,
            registrado_por=usuario,
            notas=notas
        )

        return racion

    @staticmethod
    def obtener_formula_recomendada(lote: Lote) -> Optional[FormulaAlimento]:
        """
        Obtiene la fórmula de alimento recomendada para un lote
        basándose en su edad.

        Args:
            lote: Instancia de Lote

        Returns:
            FormulaAlimento: Fórmula recomendada o None
        """
        edad_semanas = lote.edad_dias // 7

        formula = FormulaAlimento.objects.filter(
            activa=True,
            eliminado=False,
            edad_minima_semanas__lte=edad_semanas
        ).filter(
            # edad_maxima es None (sin límite) o edad_maxima >= edad_semanas
            models.Q(edad_maxima_semanas__isnull=True) | 
            models.Q(edad_maxima_semanas__gte=edad_semanas)
        ).order_by('-edad_minima_semanas').first()

        return formula

    # =========================================================================
    # CONSUMO DIARIO (con integración a Inventario)
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def registrar_consumo_diario(
        lote: Lote,
        material: Material,
        cantidad_kg: Decimal,
        usuario: User,
        notas: str = ""
    ) -> ConsumoDiario:
        """
        Registra el consumo diario de alimento y actualiza el inventario.

        CRÍTICO: Este método integra con InventarioService para generar
        un movimiento de salida automático que actualiza el stock.

        Args:
            lote: Instancia de Lote
            material: Material de alimento del inventario
            cantidad_kg: Cantidad consumida en kilogramos
            usuario: Usuario que registra
            notas: Notas adicionales

        Returns:
            ConsumoDiario: Instancia creada

        Raises:
            ValidationError: Si el material no es de tipo GRANJA
            StockInsuficienteError: Si no hay stock suficiente
        """
        # Validar que el material sea de tipo GRANJA
        if material.tipo_inventario != 'GRANJA':
            raise ValidationError(
                f"El material '{material.nombre}' no es de tipo GRANJA. "
                "Solo se pueden registrar consumos de alimentos."
            )

        # Crear registro de consumo
        consumo = ConsumoDiario.objects.create(
            lote=lote,
            material_alimento=material,
            fecha=timezone.now().date(),
            cantidad_kg=cantidad_kg,
            registrado_por=usuario,
            notas=notas
        )

        # INTEGRACIÓN CON INVENTARIO: Registrar salida de stock
        # Convertir kg a la unidad del material si es necesario
        # Por ahora asumimos que el material está en KILO
        InventarioService.actualizar_stock(
            material=material,
            cantidad=cantidad_kg,
            tipo_movimiento='SALIDA'
        )

        return consumo

    # =========================================================================
    # ANÁLISIS Y ESTADÍSTICAS
    # =========================================================================

    @staticmethod
    def calcular_consumo_por_ave(lote: Lote, dias: int = 7) -> Dict[str, Any]:
        """
        Calcula el consumo de alimento por ave en los últimos N días.

        Args:
            lote: Instancia de Lote
            dias: Número de días a analizar

        Returns:
            dict: Estadísticas de consumo por ave
        """
        fecha_inicio = timezone.now().date() - timedelta(days=dias)

        consumos = ConsumoDiario.objects.filter(
            lote=lote,
            eliminado=False,
            fecha__gte=fecha_inicio
        ).aggregate(
            total_kg=Sum('cantidad_kg'),
            dias_registrados=Count('fecha', distinct=True)
        )

        total_kg = consumos['total_kg'] or Decimal('0')
        dias_registrados = consumos['dias_registrados'] or 0

        # Calcular consumo por ave (en gramos)
        consumo_total_gramos = total_kg * 1000
        consumo_por_ave_dia = Decimal('0')
        
        if lote.cantidad_aves > 0 and dias_registrados > 0:
            consumo_por_ave_dia = consumo_total_gramos / (lote.cantidad_aves * dias_registrados)

        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'periodo_dias': dias,
            'dias_con_registro': dias_registrados,
            'total_consumido_kg': float(total_kg),
            'consumo_por_ave_gramos_dia': round(float(consumo_por_ave_dia), 2),
            'cantidad_aves': lote.cantidad_aves
        }

    @staticmethod
    def obtener_resumen_alimentacion_mensual(
        lote: Optional[Lote] = None,
        año: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de alimentación agrupado por mes.

        Args:
            lote: Opcional, filtrar por lote específico
            año: Opcional, filtrar por año
            mes: Opcional, filtrar por mes

        Returns:
            list: Lista de resúmenes mensuales
        """
        queryset = ConsumoDiario.objects.filter(eliminado=False)

        if lote:
            queryset = queryset.filter(lote=lote)
        if año:
            queryset = queryset.filter(fecha__year=año)
        if mes:
            queryset = queryset.filter(fecha__month=mes)

        resumen = queryset.annotate(
            mes=TruncMonth('fecha')
        ).values('mes', 'material_alimento__nombre').annotate(
            total_kg=Sum('cantidad_kg'),
            cantidad_registros=Count('id')
        ).order_by('-mes')

        return [
            {
                'mes': item['mes'],
                'material': item['material_alimento__nombre'],
                'total_kg': float(item['total_kg'] or 0),
                'cantidad_registros': item['cantidad_registros']
            }
            for item in resumen
        ]

    @staticmethod
    def calcular_eficiencia_alimenticia(lote: Lote, dias: int = 30) -> Dict[str, Any]:
        """
        Calcula la eficiencia alimenticia (conversión alimenticia).
        
        Eficiencia = kg de alimento / docenas de huevos producidas

        Args:
            lote: Instancia de Lote
            dias: Número de días a analizar

        Returns:
            dict: Métricas de eficiencia alimenticia
        """
        from produccion.models import Recoleccion

        fecha_inicio = timezone.now().date() - timedelta(days=dias)

        # Total alimento consumido
        consumo = ConsumoDiario.objects.filter(
            lote=lote,
            eliminado=False,
            fecha__gte=fecha_inicio
        ).aggregate(total_kg=Sum('cantidad_kg'))
        total_alimento_kg = consumo['total_kg'] or Decimal('0')

        # Total huevos producidos
        recolecciones = Recoleccion.objects.filter(
            lote=lote,
            eliminado=False,
            fecha__gte=fecha_inicio
        ).aggregate(total_huevos=Sum('cantidad_huevos'))
        total_huevos = recolecciones['total_huevos'] or 0

        # Calcular conversión (kg alimento / docenas de huevos)
        docenas_producidas = Decimal(str(total_huevos)) / 12
        conversion = Decimal('0')
        if docenas_producidas > 0:
            conversion = total_alimento_kg / docenas_producidas

        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'periodo_dias': dias,
            'total_alimento_kg': float(total_alimento_kg),
            'total_huevos': total_huevos,
            'docenas_producidas': round(float(docenas_producidas), 2),
            'conversion_alimenticia': round(float(conversion), 3),
            'interpretacion': AlimentacionService._interpretar_conversion(float(conversion))
        }

    @staticmethod
    def _interpretar_conversion(conversion: float) -> str:
        """Interpreta el índice de conversión alimenticia."""
        if conversion == 0:
            return "Sin datos suficientes"
        elif conversion < 1.5:
            return "Excelente eficiencia"
        elif conversion < 2.0:
            return "Buena eficiencia"
        elif conversion < 2.5:
            return "Eficiencia aceptable"
        else:
            return "Revisar alimentación - eficiencia baja"
