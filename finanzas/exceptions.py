"""
Excepciones personalizadas para el módulo de finanzas.
"""


class PresupuestoExcedidoError(Exception):
    """
    Excepción lanzada cuando un gasto excede el presupuesto disponible del proyecto.
    """
    def __init__(self, proyecto, monto_gasto, saldo_disponible):
        self.proyecto = proyecto
        self.monto_gasto = monto_gasto
        self.saldo_disponible = saldo_disponible
        super().__init__(
            f'El gasto de {monto_gasto} Bs excede el presupuesto disponible de {saldo_disponible} Bs '
            f'para el proyecto "{proyecto.nombre}"'
        )


class StockInsuficienteError(Exception):
    """
    Excepción lanzada cuando no hay suficiente stock para realizar un movimiento de salida.
    """
    def __init__(self, material, cantidad_solicitada, stock_disponible):
        self.material = material
        self.cantidad_solicitada = cantidad_solicitada
        self.stock_disponible = stock_disponible
        super().__init__(
            f'Stock insuficiente de {material.nombre}. '
            f'Disponible: {stock_disponible} {material.unidad_medida}, '
            f'Solicitado: {cantidad_solicitada} {material.unidad_medida}'
        )


class FechaInvalidaError(Exception):
    """
    Excepción lanzada cuando una fecha no cumple con las reglas de negocio.
    """
    pass
