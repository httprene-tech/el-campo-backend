"""
Validadores para el módulo de finanzas.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Proyecto, Gasto
from .services import FinanzasService


def validar_presupuesto_proyecto(proyecto: Proyecto, monto: Decimal):
    """
    Valida que un gasto no exceda el presupuesto del proyecto.
    
    Args:
        proyecto: Instancia de Proyecto
        monto: Monto del gasto a validar
        
    Raises:
        ValidationError: Si el gasto excede el presupuesto
    """
    try:
        FinanzasService.validar_presupuesto_disponible(proyecto, monto)
    except Exception as e:
        raise ValidationError(str(e))


def validar_monto_positivo(monto: Decimal):
    """
    Valida que un monto sea positivo.
    
    Args:
        monto: Monto a validar
        
    Raises:
        ValidationError: Si el monto no es positivo
    """
    if monto <= 0:
        raise ValidationError('El monto debe ser mayor a cero.')
