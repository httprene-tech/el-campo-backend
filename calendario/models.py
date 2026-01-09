"""
Modelos de calendario para eventos y recordatorios.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, time
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE CALENDARIO
# ============================================================================

class TipoEvento(BaseModel):
    """
    Tipos de eventos para categorizar los eventos del calendario.
    Ej: Vacunación, Limpieza, Mantenimiento, Pago, Reunión, etc.
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Color en formato hexadecimal (ej: #3B82F6)"
    )
    icono = models.CharField(
        max_length=50,
        default='calendar',
        help_text="Nombre del ícono para el frontend"
    )

    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Evento"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<TipoEvento: {self.nombre}>"


class Evento(BaseModel):
    """
    Eventos del calendario.
    Pueden ser eventos únicos o recurrentes.
    """
    TIPO_RECURRENCIA = [
        ('NINGUNA', 'Sin recurrencia'),
        ('DIARIA', 'Diaria'),
        ('SEMANAL', 'Semanal'),
        ('MENSUAL', 'Mensual'),
        ('ANUAL', 'Anual'),
    ]

    ESTADO = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    # Relaciones
    tipo = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
        related_name='eventos',
        db_index=True
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_creados',
        help_text="Usuario que creó el evento"
    )
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_asignados',
        help_text="Usuario asignado al evento"
    )

    # Información del evento
    titulo = models.CharField(max_length=200, db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(db_index=True)
    fecha_fin = models.DateTimeField(null=True, blank=True, db_index=True)
    todo_el_dia = models.BooleanField(
        default=False,
        help_text="Si es True, el evento dura todo el día"
    )
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    # Recurrencia
    tipo_recurrencia = models.CharField(
        max_length=20,
        choices=TIPO_RECURRENCIA,
        default='NINGUNA',
        db_index=True
    )
    fecha_fin_recurrencia = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha hasta la cual se repite el evento"
    )

    # Estado y recordatorios
    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='PENDIENTE',
        db_index=True
    )
    recordatorio_minutos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutos antes del evento para enviar recordatorio (ej: 30, 60, 1440)"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['fecha_inicio', 'titulo']
        indexes = [
            models.Index(fields=['fecha_inicio', 'estado']),
            models.Index(fields=['tipo', 'fecha_inicio']),
            models.Index(fields=['asignado_a', 'fecha_inicio']),
            models.Index(fields=['estado']),
        ]

    def clean(self):
        """Validación adicional antes de guardar."""
        # Validar que fecha_fin sea posterior a fecha_inicio
        if self.fecha_fin and self.fecha_inicio:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin debe ser posterior a la fecha de inicio.'
                )
        
        # Validar recurrencia
        if self.tipo_recurrencia != 'NINGUNA' and not self.fecha_fin_recurrencia:
            raise ValidationError(
                'Si el evento es recurrente, debe especificar una fecha de fin de recurrencia.'
            )

    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"

    def __repr__(self):
        return f"<Evento: {self.titulo} - {self.estado}>"


class Recordatorio(BaseModel):
    """
    Recordatorios enviados para eventos.
    Permite rastrear qué recordatorios se han enviado.
    """
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='recordatorios',
        db_index=True
    )
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    enviado = models.BooleanField(default=False)
    metodo = models.CharField(
        max_length=20,
        default='SISTEMA',
        help_text="Método de envío: SISTEMA, EMAIL, SMS, etc."
    )
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Recordatorio"
        verbose_name_plural = "Recordatorios"
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['evento', '-fecha_envio']),
            models.Index(fields=['enviado']),
        ]

    def __str__(self):
        return f"Recordatorio: {self.evento.titulo} - {self.fecha_envio}"

    def __repr__(self):
        return f"<Recordatorio: Evento #{self.evento.id} - Enviado: {self.enviado}>"
