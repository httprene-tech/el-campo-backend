"""
Modelos de alimentación para gestión de raciones, consumo y fórmulas.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE ALIMENTACIÓN
# ============================================================================

class ProveedorAlimento(BaseModel):
    """
    Proveedores de alimento para las aves.
    """
    nombre = models.CharField(max_length=150, unique=True, db_index=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si el proveedor está activo"
    )

    class Meta:
        verbose_name = "Proveedor de Alimento"
        verbose_name_plural = "Proveedores de Alimento"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['activo', 'nombre']),
        ]

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<ProveedorAlimento: {self.nombre}>"


class FormulaAlimento(BaseModel):
    """
    Fórmulas o tipos de alimento (ej: Inicio, Desarrollo, Postura).
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    edad_minima_semanas = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Edad mínima en semanas para usar esta fórmula"
    )
    edad_maxima_semanas = models.IntegerField(
        null=True,
        blank=True,
        help_text="Edad máxima en semanas para usar esta fórmula"
    )
    activa = models.BooleanField(
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = "Fórmula de Alimento"
        verbose_name_plural = "Fórmulas de Alimento"
        ordering = ['edad_minima_semanas', 'nombre']
        indexes = [
            models.Index(fields=['activa', 'edad_minima_semanas']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.edad_minima_semanas}-{self.edad_maxima_semanas or '∞'} semanas)"

    def __repr__(self):
        return f"<FormulaAlimento: {self.nombre}>"


class Racion(BaseModel):
    """
    Raciones diarias de alimento asignadas a lotes.
    """
    lote = models.ForeignKey(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='raciones',
        db_index=True
    )
    formula = models.ForeignKey(
        FormulaAlimento,
        on_delete=models.PROTECT,
        related_name='raciones',
        db_index=True
    )
    fecha = models.DateField(db_index=True)
    cantidad_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cantidad de alimento en kilogramos"
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='raciones_registradas'
    )
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Ración"
        verbose_name_plural = "Raciones"
        ordering = ['-fecha']
        unique_together = [['lote', 'fecha']]
        indexes = [
            models.Index(fields=['lote', '-fecha']),
            models.Index(fields=['formula', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    @property
    def consumo_por_ave(self):
        """Calcula el consumo por ave en gramos."""
        if self.lote.cantidad_aves > 0:
            return (self.cantidad_kg * 1000) / self.lote.cantidad_aves
        return 0

    def __str__(self):
        return f"{self.fecha} - {self.lote.nombre}: {self.cantidad_kg} kg"

    def __repr__(self):
        return f"<Racion: {self.cantidad_kg} kg - Lote #{self.lote.id}>"


class ConsumoDiario(BaseModel):
    """
    Registro de consumo diario de alimento por lote.
    Relacionado con el inventario de alimento.
    """
    lote = models.ForeignKey(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='consumos_diarios',
        db_index=True
    )
    material_alimento = models.ForeignKey(
        'inventario.Material',
        on_delete=models.PROTECT,
        related_name='consumos_diarios',
        limit_choices_to={'tipo_inventario': 'GRANJA'},
        db_index=True,
        help_text="Material de alimento del inventario"
    )
    fecha = models.DateField(db_index=True)
    cantidad_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cantidad consumida en kilogramos"
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consumos_registrados'
    )
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Consumo Diario"
        verbose_name_plural = "Consumos Diarios"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['lote', '-fecha']),
            models.Index(fields=['material_alimento', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    def clean(self):
        """Validación: el material debe ser de tipo GRANJA."""
        from django.core.exceptions import ValidationError
        if self.material_alimento.tipo_inventario != 'GRANJA':
            raise ValidationError(
                'El material debe ser de tipo GRANJA (alimento).'
            )

    def __str__(self):
        return f"{self.fecha} - {self.lote.nombre}: {self.cantidad_kg} kg de {self.material_alimento.nombre}"

    def __repr__(self):
        return f"<ConsumoDiario: {self.cantidad_kg} kg - Lote #{self.lote.id}>"
