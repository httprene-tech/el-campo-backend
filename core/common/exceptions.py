"""
Excepciones compartidas para todos los módulos.
"""


class ERPBaseException(Exception):
    """Excepción base para todas las excepciones del ERP."""
    def __init__(self, message, detalle=None):
        self.message = message
        self.detalle = detalle or {}
        super().__init__(self.message)


class ValidacionError(ERPBaseException):
    """Excepción para errores de validación."""
    pass


class NegocioError(ERPBaseException):
    """Excepción para errores de lógica de negocio."""
    pass


class RecursoNoEncontradoError(ERPBaseException):
    """Excepción cuando un recurso no se encuentra."""
    pass
