"""
Validadores para el módulo de inventario.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Material, MovimientoInventario


def validar_stock_suficiente(material: Material, cantidad: Decimal):
    """
    Valida que haya stock suficiente para una salida.
    
    Args:
        material: Instancia de Material
        cantidad: Cantidad a validar
        
    Raises:
        ValidationError: Si no hay stock suficiente
    """
    if cantidad > material.stock_actual:
        raise ValidationError(
            f'Stock insuficiente. Disponible: {material.stock_actual} {material.unidad_medida}, '
            f'Solicitado: {cantidad} {material.unidad_medida}'
        )


def validar_cantidad_positiva(cantidad: Decimal):
    """
    Valida que una cantidad sea positiva.
    
    Args:
        cantidad: Cantidad a validar
        
    Raises:
        ValidationError: Si la cantidad no es positiva
    """
    if cantidad <= 0:
        raise ValidationError('La cantidad debe ser mayor a cero.')
