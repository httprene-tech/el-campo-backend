"""
Modelos base compartidos para todos los módulos.
"""
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Modelo abstracto que agrega campos de timestamp automáticos.
    """
    creado_en = models.DateTimeField(auto_now_add=True, db_index=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-creado_en']


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que implementa soft delete (eliminación lógica).
    """
    eliminado = models.BooleanField(default=False, db_index=True)
    eliminado_en = models.DateTimeField(null=True, blank=True)
    eliminado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_eliminados'
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Marca el objeto como eliminado sin borrarlo físicamente."""
        self.eliminado = True
        self.eliminado_en = timezone.now()
        if user:
            self.eliminado_por = user
        self.save()

    def restore(self):
        """Restaura un objeto eliminado."""
        self.eliminado = False
        self.eliminado_en = None
        self.eliminado_por = None
        self.save()


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamps y soft delete.
    Usar este modelo como base para todos los modelos del sistema.
    """
    class Meta:
        abstract = True
