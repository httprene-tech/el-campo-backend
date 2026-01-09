"""
Modelos de salud para gestión de vacunaciones, tratamientos y mortalidad.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE SALUD
# ============================================================================

class Vacunacion(BaseModel):
    """
    Registro de vacunaciones aplicadas a los lotes.
    """
    lote = models.ForeignKey(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='vacunaciones',
        db_index=True
    )
    fecha = models.DateField(db_index=True)
    tipo_vacuna = models.CharField(
        max_length=150,
        help_text="Tipo de vacuna aplicada (ej: Newcastle, Gumboro)"
    )
    cantidad_aves = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de aves vacunadas"
    )
    metodo_aplicacion = models.CharField(
        max_length=50,
        help_text="Método de aplicación (ej: Inyección, Agua, Spray)"
    )
    aplicado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vacunaciones_aplicadas',
        help_text="Usuario que registró la vacunación"
    )
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Vacunación"
        verbose_name_plural = "Vacunaciones"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['lote', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f"{self.fecha} - {self.lote.nombre}: {self.tipo_vacuna}"

    def __repr__(self):
        return f"<Vacunacion: {self.tipo_vacuna} - Lote #{self.lote.id}>"


class Tratamiento(BaseModel):
    """
    Registro de tratamientos médicos aplicados a los lotes.
    """
    TIPO_TRATAMIENTO = [
        ('ANTIBIOTICO', 'Antibiótico'),
        ('ANTIPARASITARIO', 'Antiparasitario'),
        ('VITAMINAS', 'Vitaminas'),
        ('DESINFECTANTE', 'Desinfectante'),
        ('OTRO', 'Otro'),
    ]

    lote = models.ForeignKey(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='tratamientos',
        db_index=True
    )
    fecha_inicio = models.DateField(db_index=True)
    fecha_fin = models.DateField(null=True, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_TRATAMIENTO,
        default='OTRO',
        db_index=True
    )
    medicamento = models.CharField(
        max_length=200,
        help_text="Nombre del medicamento o tratamiento"
    )
    dosis = models.CharField(
        max_length=100,
        blank=True,
        help_text="Dosis aplicada (ej: 1ml por litro de agua)"
    )
    cantidad_aves = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de aves tratadas"
    )
    motivo = models.TextField(
        help_text="Motivo del tratamiento (síntomas, diagnóstico)"
    )
    aplicado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tratamientos_aplicados'
    )
    resultado = models.TextField(
        blank=True,
        null=True,
        help_text="Resultado del tratamiento"
    )

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['lote', '-fecha_inicio']),
            models.Index(fields=['tipo', '-fecha_inicio']),
        ]

    def clean(self):
        """Validación: fecha_fin debe ser posterior a fecha_inicio."""
        from django.core.exceptions import ValidationError
        if self.fecha_fin and self.fecha_inicio:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin debe ser posterior a la fecha de inicio.'
                )

    def __str__(self):
        return f"{self.fecha_inicio} - {self.lote.nombre}: {self.medicamento}"

    def __repr__(self):
        return f"<Tratamiento: {self.medicamento} - Lote #{self.lote.id}>"


class Mortalidad(BaseModel):
    """
    Registro de mortalidad diaria por lote.
    """
    lote = models.ForeignKey(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='mortalidades',
        db_index=True
    )
    fecha = models.DateField(db_index=True)
    cantidad_aves = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de aves muertas"
    )
    causa = models.CharField(
        max_length=200,
        blank=True,
        help_text="Causa probable de la mortalidad"
    )
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mortalidades_registradas'
    )

    class Meta:
        verbose_name = "Mortalidad"
        verbose_name_plural = "Mortalidades"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['lote', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    @property
    def porcentaje_mortalidad(self):
        """Calcula el porcentaje de mortalidad respecto al lote."""
        if self.lote.cantidad_aves > 0:
            return (self.cantidad_aves / self.lote.cantidad_aves) * 100
        return 0

    def __str__(self):
        return f"{self.fecha} - {self.lote.nombre}: {self.cantidad_aves} aves"

    def __repr__(self):
        return f"<Mortalidad: {self.cantidad_aves} aves - Lote #{self.lote.id}>"


class HistorialVeterinario(BaseModel):
    """
    Historial veterinario completo de un lote.
    Agrupa vacunaciones, tratamientos y mortalidad.
    """
    lote = models.OneToOneField(
        'produccion.Lote',
        on_delete=models.CASCADE,
        related_name='historial_veterinario',
        db_index=True
    )
    notas_generales = models.TextField(
        blank=True,
        null=True,
        help_text="Notas generales sobre la salud del lote"
    )
    veterinario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_veterinario',
        help_text="Veterinario responsable del lote"
    )

    class Meta:
        verbose_name = "Historial Veterinario"
        verbose_name_plural = "Historiales Veterinarios"
        ordering = ['-creado_en']

    @property
    def total_vacunaciones(self):
        """Total de vacunaciones del lote."""
        return self.lote.vacunaciones.filter(eliminado=False).count()

    @property
    def total_tratamientos(self):
        """Total de tratamientos del lote."""
        return self.lote.tratamientos.filter(eliminado=False).count()

    @property
    def total_mortalidad(self):
        """Total de aves muertas del lote."""
        from django.db.models import Sum
        return self.lote.mortalidades.filter(eliminado=False).aggregate(
            total=Sum('cantidad_aves')
        )['total'] or 0

    def __str__(self):
        return f"Historial: {self.lote.nombre}"

    def __repr__(self):
        return f"<HistorialVeterinario: Lote #{self.lote.id}>"
