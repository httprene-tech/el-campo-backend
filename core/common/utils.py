"""
Utilidades comunes para todos los módulos.
"""
from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta


def calcular_porcentaje(parte, total):
    """
    Calcula el porcentaje de parte sobre total.
    
    Args:
        parte: Valor parcial
        total: Valor total
        
    Returns:
        float: Porcentaje redondeado a 2 decimales
    """
    if total == 0:
        return 0.0
    return round((parte / total) * 100, 2)


def formatear_moneda(monto, simbolo='Bs'):
    """
    Formatea un monto como moneda.
    
    Args:
        monto: Decimal o float
        simbolo: Símbolo de moneda (default: 'Bs')
        
    Returns:
        str: Monto formateado
    """
    if isinstance(monto, Decimal):
        return f"{monto:,.2f} {simbolo}"
    return f"{float(monto):,.2f} {simbolo}"


def obtener_rango_mes(fecha=None):
    """
    Obtiene el primer y último día del mes de una fecha.
    
    Args:
        fecha: datetime o date (default: hoy)
        
    Returns:
        tuple: (primer_dia, ultimo_dia)
    """
    if fecha is None:
        fecha = timezone.now()
    
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    primer_dia = fecha.replace(day=1)
    
    # Calcular último día del mes
    if fecha.month == 12:
        ultimo_dia = fecha.replace(year=fecha.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)
    
    return primer_dia, ultimo_dia


def obtener_mes_anterior():
    """
    Obtiene el primer y último día del mes anterior.
    
    Returns:
        tuple: (primer_dia, ultimo_dia)
    """
    hoy = timezone.now().date()
    primer_dia_mes_actual = hoy.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
    
    return primer_dia_mes_anterior, ultimo_dia_mes_anterior


def validar_rango_fechas(fecha_inicio, fecha_fin):
    """
    Valida que fecha_inicio sea anterior a fecha_fin.
    
    Args:
        fecha_inicio: datetime o date
        fecha_fin: datetime o date
        
    Returns:
        bool: True si el rango es válido
        
    Raises:
        ValueError: Si fecha_inicio > fecha_fin
    """
    if fecha_inicio and fecha_fin:
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.fromisoformat(fecha_inicio).date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.fromisoformat(fecha_fin).date()
        
        if fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    return True
