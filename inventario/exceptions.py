"""
Excepciones específicas del módulo de inventario.
"""
from core.common.exceptions import NegocioError


class StockInsuficienteError(NegocioError):
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
            f'Solicitado: {cantidad_solicitada} {material.unidad_medida}',
            detalle={
                'material_id': material.id,
                'material_nombre': material.nombre,
                'cantidad_solicitada': str(cantidad_solicitada),
                'stock_disponible': str(stock_disponible),
                'unidad_medida': material.unidad_medida
            }
        )
