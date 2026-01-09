"""
Modelos de producción para gestión de lotes, recolección y calidad de huevos.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE PRODUCCIÓN
# ============================================================================

class Galpon(BaseModel):
    """
    Galpones o naves donde se crían las gallinas.
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    capacidad_maxima = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Capacidad máxima de aves en el galpón"
    )
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si el galpón está en uso"
    )

    class Meta:
        verbose_name = "Galpón"
        verbose_name_plural = "Galpones"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['activo', 'nombre']),
        ]

    @property
    def cantidad_aves_actual(self):
        """Calcula la cantidad actual de aves en el galpón."""
        from django.db.models import Sum
        return self.lotes.filter(activo=True, eliminado=False).aggregate(
            total=Sum('cantidad_aves')
        )['total'] or 0

    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad_maxima})"

    def __repr__(self):
        return f"<Galpon: {self.nombre}>"


class Lote(BaseModel):
    """
    Lotes de gallinas ponedoras.
    Cada lote representa un grupo de aves que ingresan juntas al galpón.
    """
    ESTADO = [
        ('CRECIMIENTO', 'Crecimiento'),
        ('PRODUCCION', 'En Producción'),
        ('MUDAS', 'En Mudas'),
        ('FINALIZADO', 'Finalizado'),
    ]

    nombre = models.CharField(max_length=150, db_index=True)
    galpon = models.ForeignKey(
        Galpon,
        on_delete=models.PROTECT,
        related_name='lotes',
        db_index=True
    )
    fecha_ingreso = models.DateField(db_index=True)
    fecha_salida = models.DateField(null=True, blank=True)
    cantidad_aves = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad inicial de aves en el lote"
    )
    raza = models.CharField(
        max_length=100,
        blank=True,
        help_text="Raza de las gallinas (ej: Lohmann Brown, Hy-Line)"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='CRECIMIENTO',
        db_index=True
    )
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si el lote está activo"
    )
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['galpon', 'estado', '-fecha_ingreso']),
            models.Index(fields=['activo', '-fecha_ingreso']),
            models.Index(fields=['estado']),
        ]

    @property
    def edad_dias(self):
        """Calcula la edad del lote en días."""
        from django.utils import timezone
        fecha_fin = self.fecha_salida or timezone.now().date()
        return (fecha_fin - self.fecha_ingreso).days

    @property
    def total_huevos_recolectados(self):
        """Total de huevos recolectados del lote."""
        from django.db.models import Sum
        return self.recolecciones.filter(eliminado=False).aggregate(
            total=Sum('cantidad_huevos')
        )['total'] or 0

    @property
    def promedio_diario_huevos(self):
        """Promedio diario de huevos si hay recolecciones."""
        recolecciones = self.recolecciones.filter(eliminado=False)
        if recolecciones.exists():
            dias_con_recoleccion = recolecciones.values('fecha').distinct().count()
            if dias_con_recoleccion > 0:
                return self.total_huevos_recolectados / dias_con_recoleccion
        return 0

    def __str__(self):
        return f"{self.nombre} - {self.galpon.nombre} ({self.cantidad_aves} aves)"

    def __repr__(self):
        return f"<Lote: {self.nombre} - Estado: {self.estado}>"


class Recoleccion(BaseModel):
    """
    Registro diario de recolección de huevos por lote.
    """
    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name='recolecciones',
        db_index=True
    )
    fecha = models.DateField(db_index=True)
    cantidad_huevos = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Cantidad de huevos recolectados"
    )
    hora_recoleccion = models.TimeField(
        null=True,
        blank=True,
        help_text="Hora aproximada de recolección"
    )
    recolectado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recolecciones_realizadas',
        help_text="Usuario que registró la recolección"
    )
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Recolección"
        verbose_name_plural = "Recolecciones"
        ordering = ['-fecha', '-hora_recoleccion']
        unique_together = [['lote', 'fecha']]
        indexes = [
            models.Index(fields=['lote', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f"{self.fecha} - {self.lote.nombre}: {self.cantidad_huevos} huevos"

    def __repr__(self):
        return f"<Recoleccion: Lote #{self.lote.id} - {self.cantidad_huevos} huevos>"


class CalidadHuevo(BaseModel):
    """
    Control de calidad de los huevos recolectados.
    """
    TIPO_DEFECTO = [
        ('NINGUNO', 'Sin defectos'),
        ('CASCARON_DEBIL', 'Cáscara débil'),
        ('CASCARON_ROTO', 'Cáscara rota'),
        ('SUCIO', 'Huevo sucio'),
        ('FORMA_IRREGULAR', 'Forma irregular'),
        ('TAMAÑO_PEQUENO', 'Tamaño pequeño'),
        ('OTRO', 'Otro'),
    ]

    recoleccion = models.ForeignKey(
        Recoleccion,
        on_delete=models.CASCADE,
        related_name='calidad_huevos',
        db_index=True
    )
    cantidad_primera = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad de huevos de primera calidad"
    )
    cantidad_segunda = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad de huevos de segunda calidad"
    )
    cantidad_descarte = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad de huevos descartados"
    )
    tipo_defecto = models.CharField(
        max_length=20,
        choices=TIPO_DEFECTO,
        default='NINGUNO',
        db_index=True
    )
    observaciones = models.TextField(blank=True, null=True)
    evaluado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='huevos_evaluados'
    )

    class Meta:
        verbose_name = "Calidad de Huevo"
        verbose_name_plural = "Calidades de Huevo"
        ordering = ['-recoleccion__fecha']
        indexes = [
            models.Index(fields=['recoleccion', 'tipo_defecto']),
        ]

    @property
    def total_huevos(self):
        """Total de huevos evaluados."""
        return self.cantidad_primera + self.cantidad_segunda + self.cantidad_descarte

    @property
    def porcentaje_primera(self):
        """Porcentaje de huevos de primera calidad."""
        if self.total_huevos > 0:
            return (self.cantidad_primera / self.total_huevos) * 100
        return 0

    def clean(self):
        """Validación: la suma debe coincidir con la recolección."""
        from django.core.exceptions import ValidationError
        if self.total_huevos != self.recoleccion.cantidad_huevos:
            raise ValidationError(
                f'La suma de huevos evaluados ({self.total_huevos}) debe coincidir '
                f'con la cantidad recolectada ({self.recoleccion.cantidad_huevos}).'
            )

    def __str__(self):
        return f"Calidad: {self.recoleccion.fecha} - 1ra: {self.cantidad_primera}, 2da: {self.cantidad_segunda}"

    def __repr__(self):
        return f"<CalidadHuevo: {self.total_huevos} huevos evaluados>"
