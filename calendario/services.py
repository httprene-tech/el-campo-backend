"""
Servicios de lógica de negocio para el módulo de calendario.

Este módulo encapsula toda la lógica de negocio relacionada con:
- Gestión de eventos y recordatorios
- Generación de eventos automáticos desde otros módulos
- Análisis de eventos próximos y pendientes
"""
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta, date

from django.db import transaction
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.utils import timezone

from .models import TipoEvento, Evento, Recordatorio


class CalendarioService:
    """
    Servicio para operaciones de calendario.
    Centraliza toda la lógica de negocio del módulo.
    """

    # =========================================================================
    # GESTIÓN DE EVENTOS
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def crear_evento(
        titulo: str,
        tipo: TipoEvento,
        fecha_inicio: datetime,
        usuario: User,
        descripcion: str = "",
        fecha_fin: Optional[datetime] = None,
        asignado_a: Optional[User] = None,
        ubicacion: str = "",
        todo_el_dia: bool = False,
        recordatorio_minutos: Optional[int] = None
    ) -> Evento:
        """
        Crea un evento en el calendario.

        Args:
            titulo: Título del evento
            tipo: TipoEvento asociado
            fecha_inicio: Fecha y hora de inicio
            usuario: Usuario que crea el evento
            descripcion: Descripción del evento
            fecha_fin: Fecha y hora de fin (opcional)
            asignado_a: Usuario asignado al evento
            ubicacion: Ubicación del evento
            todo_el_dia: Si el evento dura todo el día
            recordatorio_minutos: Minutos antes para recordatorio

        Returns:
            Evento: Instancia creada
        """
        evento = Evento.objects.create(
            titulo=titulo,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            usuario=usuario,
            asignado_a=asignado_a,
            descripcion=descripcion,
            ubicacion=ubicacion,
            todo_el_dia=todo_el_dia,
            recordatorio_minutos=recordatorio_minutos
        )

        return evento

    @staticmethod
    @transaction.atomic
    def crear_evento_desde_vacunacion(
        lote_nombre: str,
        tipo_vacuna: str,
        fecha: date,
        usuario: User
    ) -> Evento:
        """
        Crea un evento de calendario desde una vacunación programada.
        
        SINERGIA: Este método conecta el módulo de salud con el calendario.

        Args:
            lote_nombre: Nombre del lote a vacunar
            tipo_vacuna: Tipo de vacuna
            fecha: Fecha de la vacunación
            usuario: Usuario que programa

        Returns:
            Evento: Evento de vacunación creado
        """
        # Obtener o crear tipo de evento de vacunación
        tipo_evento, _ = TipoEvento.objects.get_or_create(
            nombre='Vacunación',
            defaults={
                'descripcion': 'Eventos de vacunación de aves',
                'color': '#DC2626',  # Rojo
                'icono': 'syringe'
            }
        )

        fecha_inicio = timezone.make_aware(
            datetime.combine(fecha, datetime.min.time().replace(hour=8))
        )

        return CalendarioService.crear_evento(
            titulo=f"Vacunación: {tipo_vacuna} - {lote_nombre}",
            tipo=tipo_evento,
            fecha_inicio=fecha_inicio,
            usuario=usuario,
            descripcion=f"Aplicar vacuna {tipo_vacuna} al lote {lote_nombre}",
            ubicacion="Galpón",
            recordatorio_minutos=1440  # 1 día antes
        )

    @staticmethod
    @transaction.atomic
    def crear_evento_desde_pago(
        descripcion_pago: str,
        monto: str,
        fecha: date,
        usuario: User
    ) -> Evento:
        """
        Crea un evento de calendario desde un pago programado.
        
        SINERGIA: Este método conecta el módulo de finanzas con el calendario.

        Args:
            descripcion_pago: Descripción del pago
            monto: Monto del pago
            fecha: Fecha del pago
            usuario: Usuario que programa

        Returns:
            Evento: Evento de pago creado
        """
        # Obtener o crear tipo de evento de pago
        tipo_evento, _ = TipoEvento.objects.get_or_create(
            nombre='Pago',
            defaults={
                'descripcion': 'Pagos programados',
                'color': '#059669',  # Verde
                'icono': 'dollar-sign'
            }
        )

        fecha_inicio = timezone.make_aware(
            datetime.combine(fecha, datetime.min.time().replace(hour=9))
        )

        return CalendarioService.crear_evento(
            titulo=f"Pago: {descripcion_pago}",
            tipo=tipo_evento,
            fecha_inicio=fecha_inicio,
            usuario=usuario,
            descripcion=f"Realizar pago de {monto} Bs - {descripcion_pago}",
            recordatorio_minutos=1440  # 1 día antes
        )

    # =========================================================================
    # CAMBIO DE ESTADO
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def marcar_completado(evento: Evento, usuario: User) -> Evento:
        """
        Marca un evento como completado.

        Args:
            evento: Instancia de Evento
            usuario: Usuario que completa

        Returns:
            Evento: Evento actualizado
        """
        evento.estado = 'COMPLETADO'
        evento.save(update_fields=['estado', 'actualizado_en'])
        return evento

    @staticmethod
    @transaction.atomic
    def marcar_cancelado(evento: Evento, usuario: User) -> Evento:
        """
        Marca un evento como cancelado.

        Args:
            evento: Instancia de Evento
            usuario: Usuario que cancela

        Returns:
            Evento: Evento actualizado
        """
        evento.estado = 'CANCELADO'
        evento.save(update_fields=['estado', 'actualizado_en'])
        return evento

    # =========================================================================
    # CONSULTAS Y ANÁLISIS
    # =========================================================================

    @staticmethod
    def obtener_eventos_proximos(
        dias: int = 7,
        usuario: Optional[User] = None
    ) -> List[Evento]:
        """
        Obtiene eventos próximos en los siguientes N días.

        Args:
            dias: Número de días hacia adelante
            usuario: Opcional, filtrar por usuario asignado

        Returns:
            list: Lista de eventos próximos
        """
        ahora = timezone.now()
        fecha_limite = ahora + timedelta(days=dias)

        queryset = Evento.objects.filter(
            eliminado=False,
            fecha_inicio__gte=ahora,
            fecha_inicio__lte=fecha_limite,
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).select_related('tipo', 'usuario', 'asignado_a')

        if usuario:
            queryset = queryset.filter(
                Q(asignado_a=usuario) | Q(usuario=usuario)
            )

        return list(queryset.order_by('fecha_inicio'))

    @staticmethod
    def obtener_eventos_hoy(usuario: Optional[User] = None) -> List[Evento]:
        """
        Obtiene eventos del día de hoy.

        Args:
            usuario: Opcional, filtrar por usuario

        Returns:
            list: Lista de eventos de hoy
        """
        ahora = timezone.now()
        inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)

        queryset = Evento.objects.filter(
            eliminado=False,
            fecha_inicio__gte=inicio_dia,
            fecha_inicio__lt=fin_dia
        ).select_related('tipo', 'usuario', 'asignado_a')

        if usuario:
            queryset = queryset.filter(
                Q(asignado_a=usuario) | Q(usuario=usuario)
            )

        return list(queryset.order_by('fecha_inicio'))

    @staticmethod
    def obtener_resumen_estado() -> Dict[str, int]:
        """
        Obtiene un resumen de eventos por estado.

        Returns:
            dict: Conteo de eventos por estado
        """
        resumen = Evento.objects.filter(
            eliminado=False
        ).values('estado').annotate(
            cantidad=Count('id')
        )

        return {
            item['estado']: item['cantidad']
            for item in resumen
        }

    @staticmethod
    def obtener_eventos_vencidos() -> List[Evento]:
        """
        Obtiene eventos que ya pasaron pero siguen pendientes.

        Returns:
            list: Lista de eventos vencidos
        """
        ahora = timezone.now()

        return list(Evento.objects.filter(
            eliminado=False,
            fecha_inicio__lt=ahora,
            estado='PENDIENTE'
        ).select_related('tipo', 'usuario', 'asignado_a').order_by('fecha_inicio'))

    # =========================================================================
    # RECORDATORIOS
    # =========================================================================

    @staticmethod
    def obtener_eventos_para_recordatorio() -> List[Evento]:
        """
        Obtiene eventos que necesitan enviar recordatorio.
        
        Los eventos se seleccionan si:
        - Tienen recordatorio_minutos configurado
        - La fecha actual está dentro del rango de recordatorio
        - No se ha enviado recordatorio aún

        Returns:
            list: Lista de eventos que necesitan recordatorio
        """
        ahora = timezone.now()

        eventos = Evento.objects.filter(
            eliminado=False,
            estado='PENDIENTE',
            recordatorio_minutos__isnull=False
        ).select_related('tipo').prefetch_related('recordatorios')

        eventos_para_recordar = []
        for evento in eventos:
            # Verificar si ya se envió recordatorio
            if evento.recordatorios.filter(enviado=True).exists():
                continue

            # Calcular momento del recordatorio
            momento_recordatorio = evento.fecha_inicio - timedelta(
                minutes=evento.recordatorio_minutos
            )

            # Si ya pasó el momento del recordatorio pero el evento aún no ocurre
            if momento_recordatorio <= ahora < evento.fecha_inicio:
                eventos_para_recordar.append(evento)

        return eventos_para_recordar

    @staticmethod
    @transaction.atomic
    def registrar_recordatorio_enviado(evento: Evento, metodo: str = 'SISTEMA') -> Recordatorio:
        """
        Registra que se envió un recordatorio para un evento.

        Args:
            evento: Instancia de Evento
            metodo: Método de envío

        Returns:
            Recordatorio: Instancia creada
        """
        return Recordatorio.objects.create(
            evento=evento,
            enviado=True,
            metodo=metodo
        )
