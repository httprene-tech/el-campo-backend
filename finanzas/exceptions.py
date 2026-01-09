"""
Excepciones personalizadas para el módulo de finanzas.
"""
from core.common.exceptions import NegocioError


class PresupuestoExcedidoError(NegocioError):
    """
    Excepción lanzada cuando un gasto excede el presupuesto disponible del proyecto.
    """
    def __init__(self, proyecto, monto_gasto, saldo_disponible):
        self.proyecto = proyecto
        self.monto_gasto = monto_gasto
        self.saldo_disponible = saldo_disponible
        super().__init__(
            f'El gasto de {monto_gasto} Bs excede el presupuesto disponible de {saldo_disponible} Bs '
            f'para el proyecto "{proyecto.nombre}"',
            detalle={
                'proyecto_id': proyecto.id,
                'proyecto_nombre': proyecto.nombre,
                'monto_gasto': str(monto_gasto),
                'saldo_disponible': str(saldo_disponible),
                'presupuesto_total': str(proyecto.presupuesto_objetivo)
            }
        )
