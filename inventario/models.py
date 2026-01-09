"""
Modelos de inventario para materiales de construcción e insumos de granja.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE INVENTARIO
# ============================================================================

class Material(BaseModel):
    """
    Materiales con control de inventario.
    Puede ser material de construcción o insumo de granja (alimento, medicinas, etc.).
    """
    
    TIPO_INVENTARIO = [
        ('CONSTRUCCION', 'Material de Construcción'),
        ('GRANJA', 'Insumo de Granja'),
    ]
    
    UNIDADES = [
        ('BOLSA', 'Bolsa'),
        ('PIEZA', 'Pieza / Unidad'),
        ('METRO_CUBICO', 'Metro Cúbico'),
        ('KILO', 'Kilogramo'),
        ('LITRO', 'Litro'),
        ('GLOBAL', 'Global'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    tipo_inventario = models.CharField(
        max_length=20,
        choices=TIPO_INVENTARIO,
        default='CONSTRUCCION',
        db_index=True,
        help_text="Tipo de inventario: construcción o granja"
    )
    unidad_medida = models.CharField(
        max_length=20, 
        choices=UNIDADES, 
        default='BOLSA'
    )
    stock_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    stock_minimo_alerta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=5,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Nivel mínimo antes de alertar stock bajo"
    )
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        help_text="Código interno del material (opcional)"
    )

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['tipo_inventario', 'nombre']
        indexes = [
            models.Index(fields=['tipo_inventario', 'nombre']),
            models.Index(fields=['stock_actual']),
        ]

    @property
    def stock_bajo(self):
        """Indica si el stock está por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo_alerta

    @property
    def porcentaje_stock(self):
        """Calcula el porcentaje de stock disponible (si hay stock mínimo definido)."""
        if self.stock_minimo_alerta == 0:
            return 100.0
        if self.stock_actual == 0:
            return 0.0
        return float((self.stock_actual / (self.stock_minimo_alerta * 2)) * 100)

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad_medida})"

    def __repr__(self):
        return f"<Material: {self.nombre} - Stock: {self.stock_actual}>"


class MovimientoInventario(BaseModel):
    """
    Movimientos de entrada y salida de inventario.
    Actualiza automáticamente el stock del material.
    """
    
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada (Compra/Ingreso)'),
        ('SALIDA', 'Salida (Uso/Consumo)'),
        ('AJUSTE', 'Ajuste de Inventario'),
    ]

    material = models.ForeignKey(
        Material, 
        on_delete=models.CASCADE, 
        related_name='movimientos',
        db_index=True
    )
    tipo = models.CharField(
        max_length=10, 
        choices=TIPO_MOVIMIENTO,
        db_index=True
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    nota = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Ej: Para cimientos del galpón, Consumo diario, etc."
    )
    
    # Vincular la entrada a un gasto real (opcional, solo para materiales de construcción)
    gasto = models.ForeignKey(
        'finanzas.Gasto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimientos_inventario',
        help_text="Gasto asociado (solo para materiales de construcción)"
    )
    
    # Usuario que registró el movimiento
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='movimientos_inventario',
        help_text="Usuario que registró el movimiento"
    )

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha', '-creado_en']
        indexes = [
            models.Index(fields=['material', 'tipo', '-fecha']),
            models.Index(fields=['fecha']),
        ]

    def clean(self):
        """Validación adicional antes de guardar."""
        # Validar que gasto solo se use con materiales de construcción
        if self.gasto and self.material.tipo_inventario != 'CONSTRUCCION':
            raise ValidationError(
                'El gasto solo puede asociarse a materiales de construcción.'
            )
        
        # Validar que ajuste no tenga gasto asociado
        if self.tipo == 'AJUSTE' and self.gasto:
            raise ValidationError(
                'Los ajustes de inventario no pueden tener gasto asociado.'
            )

    def save(self, *args, **kwargs):
        """
        Actualiza el stock automáticamente al guardar un movimiento.
        Usa transacciones atómicas para evitar condiciones de carrera.
        
        Raises:
            ValidationError: Si no hay suficiente stock para una salida.
        """
        from inventario.exceptions import StockInsuficienteError
        
        # Validar antes de guardar
        self.clean()
        
        with transaction.atomic():
            # Bloquear el material para evitar race conditions
            material = Material.objects.select_for_update().get(pk=self.material.pk)
            
            # Calcular nuevo stock según tipo de movimiento
            if self.tipo == 'ENTRADA':
                nuevo_stock = material.stock_actual + self.cantidad
            elif self.tipo == 'SALIDA':
                nuevo_stock = material.stock_actual - self.cantidad
                
                # Validar que no quede stock negativo
                if nuevo_stock < 0:
                    raise ValidationError(
                        f'Stock insuficiente para {material.nombre}. '
                        f'Stock actual: {material.stock_actual} {material.unidad_medida}, '
                        f'Cantidad solicitada: {self.cantidad} {material.unidad_medida}'
                    )
            else:  # AJUSTE
                nuevo_stock = self.cantidad
            
            # Actualizar el stock del material
            material.stock_actual = nuevo_stock
            material.save(update_fields=['stock_actual', 'actualizado_en'])
            
            # Guardar el movimiento
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo}: {self.cantidad} {self.material.unidad_medida} de {self.material.nombre}"

    def __repr__(self):
        return f"<MovimientoInventario: {self.tipo} - {self.material.nombre}>"
