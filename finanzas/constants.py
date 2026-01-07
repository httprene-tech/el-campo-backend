"""
Constantes utilizadas en el módulo de finanzas.
"""
from decimal import Decimal


# ============================================================================
# LÍMITES Y CONFIGURACIÓN
# ============================================================================

# Límite máximo de presupuesto para un proyecto (en Bs)
MAX_PRESUPUESTO_PROYECTO = Decimal('10000000.00')  # 10 millones de Bs

# Límite máximo para un gasto individual (en Bs)
MAX_MONTO_GASTO = Decimal('1000000.00')  # 1 millón de Bs

# Porcentaje de alerta cuando el presupuesto está cerca de agotarse
PORCENTAJE_ALERTA_PRESUPUESTO = 90  # 90%

# Stock mínimo por defecto para materiales
STOCK_MINIMO_DEFAULT = Decimal('5.00')


# ============================================================================
# MENSAJES DE ERROR ESTANDARIZADOS
# ============================================================================

ERROR_PRESUPUESTO_EXCEDIDO = "Atención: Este gasto excede el presupuesto total del proyecto."
ERROR_STOCK_INSUFICIENTE = "No hay suficiente stock disponible para completar esta operación."
ERROR_FECHA_FUTURA = "La fecha no puede estar en el futuro."
ERROR_MONTO_INVALIDO = "El monto debe ser mayor a cero."
ERROR_PROYECTO_INACTIVO = "No se pueden registrar gastos en un proyecto inactivo."


# ============================================================================
# MENSAJES DE ÉXITO
# ============================================================================

EXITO_GASTO_CREADO = "Gasto registrado exitosamente."
EXITO_PROYECTO_CREADO = "Proyecto creado exitosamente."
EXITO_MOVIMIENTO_CREADO = "Movimiento de inventario registrado exitosamente."


# ============================================================================
# MENSAJES DE ADVERTENCIA
# ============================================================================

ADVERTENCIA_PRESUPUESTO_BAJO = "Advertencia: El presupuesto del proyecto está por debajo del {porcentaje}%."
ADVERTENCIA_STOCK_BAJO = "Advertencia: El stock de {material} está por debajo del nivel mínimo."
ADVERTENCIA_GASTO_RETROACTIVO = "Este gasto se está registrando con fecha anterior a hoy."


# ============================================================================
# CONFIGURACIÓN DE REPORTES
# ============================================================================

# Colores para reportes PDF (en formato RGB)
COLOR_HEADER_PDF = (0, 128, 0)  # Verde
COLOR_ALERTA_PDF = (255, 0, 0)  # Rojo
COLOR_OK_PDF = (0, 128, 0)  # Verde

# Límite de descripción en reportes PDF
MAX_DESCRIPCION_PDF = 30
MAX_PROVEEDOR_PDF = 20
