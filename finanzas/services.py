"""
Servicios de lógica de negocio para el módulo de finanzas.
"""
from decimal import Decimal
from django.db.models import Sum
from .models import Proyecto, Gasto
from .exceptions import PresupuestoExcedidoError


class FinanzasService:
    """Servicio para operaciones financieras."""
    
    @staticmethod
    def calcular_saldo_proyecto(proyecto: Proyecto) -> Decimal:
        """
        Calcula el saldo disponible de un proyecto.
        
        Args:
            proyecto: Instancia de Proyecto
            
        Returns:
            Decimal: Saldo disponible
        """
        total_gastado = proyecto.gastos.filter(eliminado=False).aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')
        
        return proyecto.presupuesto_objetivo - total_gastado
    
    @staticmethod
    def validar_presupuesto_disponible(proyecto: Proyecto, monto_gasto: Decimal) -> bool:
        """
        Valida que haya presupuesto disponible para un gasto.
        
        Args:
            proyecto: Instancia de Proyecto
            monto_gasto: Monto del gasto a validar
            
        Returns:
            bool: True si hay presupuesto disponible
            
        Raises:
            PresupuestoExcedidoError: Si no hay presupuesto suficiente
        """
        saldo_disponible = FinanzasService.calcular_saldo_proyecto(proyecto)
        
        if monto_gasto > saldo_disponible:
            raise PresupuestoExcedidoError(
                proyecto=proyecto,
                monto_gasto=monto_gasto,
                saldo_disponible=saldo_disponible
            )
        
        return True
    
    @staticmethod
    def obtener_resumen_proyecto(proyecto: Proyecto) -> dict:
        """
        Obtiene un resumen completo de un proyecto.
        
        Args:
            proyecto: Instancia de Proyecto
            
        Returns:
            dict: Resumen con totales y porcentajes
        """
        total_gastado = proyecto.gastos.filter(eliminado=False).aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')
        
        saldo_disponible = proyecto.presupuesto_objetivo - total_gastado
        porcentaje_consumido = (total_gastado / proyecto.presupuesto_objetivo * 100) if proyecto.presupuesto_objetivo > 0 else 0
        
        return {
            'proyecto_id': proyecto.id,
            'proyecto_nombre': proyecto.nombre,
            'presupuesto_total': str(proyecto.presupuesto_objetivo),
            'total_gastado': str(total_gastado),
            'saldo_disponible': str(saldo_disponible),
            'porcentaje_consumido': round(float(porcentaje_consumido), 2),
            'cantidad_gastos': proyecto.gastos.filter(eliminado=False).count()
        }
