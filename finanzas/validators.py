"""
Validadores personalizados para el módulo de finanzas.
"""
from django.core.exceptions import ValidationError
from decimal import Decimal


def validar_presupuesto_positivo(value):
    """
    Valida que un presupuesto sea mayor a cero.
    """
    if value <= Decimal('0.00'):
        raise ValidationError('El presupuesto debe ser mayor a cero.')


def validar_monto_positivo(value):
    """
    Valida que un monto sea mayor a cero.
    """
    if value <= Decimal('0.00'):
        raise ValidationError('El monto debe ser mayor a cero.')


def validar_stock_no_negativo(value):
    """
    Valida que el stock no sea negativo.
    """
    if value < Decimal('0.00'):
        raise ValidationError('El stock no puede ser negativo.')


def validar_fecha_no_futura(value):
    """
    Valida que una fecha no sea en el futuro.
    """
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError('La fecha no puede ser en el futuro.')


def validar_cantidad_movimiento(cantidad, material, tipo_movimiento):
    """
    Valida que haya suficiente stock para un movimiento de salida.
    
    Args:
        cantidad: Cantidad del movimiento
        material: Instancia del Material
        tipo_movimiento: 'ENTRADA' o 'SALIDA'
    
    Raises:
        ValidationError: Si no hay suficiente stock
    """
    if tipo_movimiento == 'SALIDA':
        if cantidad > material.stock_actual:
            raise ValidationError(
                f'Stock insuficiente. Disponible: {material.stock_actual} {material.unidad_medida}, '
                f'Solicitado: {cantidad} {material.unidad_medida}'
            )


def validar_gasto_no_excede_presupuesto(gasto_monto, proyecto):
    """
    Valida que un gasto no exceda el presupuesto del proyecto.
    
    Args:
        gasto_monto: Monto del nuevo gasto
        proyecto: Instancia del Proyecto
    
    Raises:
        ValidationError: Si el gasto excede el presupuesto
    """
    total_con_nuevo_gasto = proyecto.total_gastado + gasto_monto
    if total_con_nuevo_gasto > proyecto.presupuesto_objetivo:
        saldo_disponible = proyecto.saldo_restante
        raise ValidationError(
            f'El gasto excede el presupuesto disponible. '
            f'Saldo disponible: {saldo_disponible} Bs, '
            f'Monto del gasto: {gasto_monto} Bs'
        )
