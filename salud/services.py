"""
Servicios de lógica de negocio para el módulo de salud.

Este módulo encapsula toda la lógica de negocio relacionada con:
- Gestión de vacunaciones
- Control de tratamientos
- Registro y análisis de mortalidad
- Historial veterinario
"""
from decimal import Decimal
from typing import Optional, Dict, List, Any
from datetime import date, timedelta

from django.db import transaction
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Vacunacion, Tratamiento, Mortalidad, HistorialVeterinario
from produccion.models import Lote


class SaludService:
    """
    Servicio para operaciones de salud animal.
    Centraliza toda la lógica de negocio del módulo.
    """

    # =========================================================================
    # VACUNACIONES
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def registrar_vacunacion(
        lote: Lote,
        tipo_vacuna: str,
        cantidad_aves: int,
        metodo_aplicacion: str,
        usuario: User,
        observaciones: str = ""
    ) -> Vacunacion:
        """
        Registra una vacunación para un lote.

        Args:
            lote: Instancia de Lote
            tipo_vacuna: Tipo de vacuna aplicada
            cantidad_aves: Cantidad de aves vacunadas
            metodo_aplicacion: Método de aplicación
            usuario: Usuario que registra
            observaciones: Observaciones adicionales

        Returns:
            Vacunacion: Instancia creada
        """
        vacunacion = Vacunacion.objects.create(
            lote=lote,
            fecha=timezone.now().date(),
            tipo_vacuna=tipo_vacuna,
            cantidad_aves=cantidad_aves,
            metodo_aplicacion=metodo_aplicacion,
            aplicado_por=usuario,
            observaciones=observaciones
        )

        # Asegurar que existe historial veterinario
        HistorialVeterinario.objects.get_or_create(lote=lote)

        return vacunacion

    @staticmethod
    def obtener_vacunaciones_pendientes(lote: Lote) -> List[Dict[str, Any]]:
        """
        Obtiene las vacunaciones que podrían estar pendientes
        basándose en la edad del lote y vacunas típicas.

        Args:
            lote: Instancia de Lote

        Returns:
            list: Lista de vacunaciones sugeridas
        """
        edad_semanas = lote.edad_dias // 7
        vacunas_aplicadas = set(
            Vacunacion.objects.filter(
                lote=lote,
                eliminado=False
            ).values_list('tipo_vacuna', flat=True)
        )

        # Calendario típico de vacunación (personalizable)
        calendario = [
            {'semana': 1, 'vacuna': 'Marek', 'metodo': 'Inyección'},
            {'semana': 2, 'vacuna': 'Newcastle + Bronquitis', 'metodo': 'Spray'},
            {'semana': 3, 'vacuna': 'Gumboro', 'metodo': 'Agua'},
            {'semana': 6, 'vacuna': 'Viruela Aviar', 'metodo': 'Punción alar'},
            {'semana': 10, 'vacuna': 'Newcastle (refuerzo)', 'metodo': 'Agua'},
        ]

        pendientes = []
        for item in calendario:
            if edad_semanas >= item['semana'] and item['vacuna'] not in vacunas_aplicadas:
                pendientes.append({
                    'vacuna': item['vacuna'],
                    'metodo_sugerido': item['metodo'],
                    'semana_recomendada': item['semana'],
                    'semanas_atrasada': edad_semanas - item['semana']
                })

        return pendientes

    # =========================================================================
    # TRATAMIENTOS
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def registrar_tratamiento(
        lote: Lote,
        tipo: str,
        medicamento: str,
        dosis: str,
        cantidad_aves: int,
        motivo: str,
        usuario: User,
        fecha_fin: Optional[date] = None
    ) -> Tratamiento:
        """
        Registra un tratamiento médico para un lote.

        Args:
            lote: Instancia de Lote
            tipo: Tipo de tratamiento (ANTIBIOTICO, ANTIPARASITARIO, etc.)
            medicamento: Nombre del medicamento
            dosis: Dosis aplicada
            cantidad_aves: Cantidad de aves tratadas
            motivo: Motivo del tratamiento
            usuario: Usuario que registra
            fecha_fin: Fecha estimada de fin del tratamiento

        Returns:
            Tratamiento: Instancia creada
        """
        tratamiento = Tratamiento.objects.create(
            lote=lote,
            fecha_inicio=timezone.now().date(),
            fecha_fin=fecha_fin,
            tipo=tipo,
            medicamento=medicamento,
            dosis=dosis,
            cantidad_aves=cantidad_aves,
            motivo=motivo,
            aplicado_por=usuario
        )

        # Asegurar que existe historial veterinario
        HistorialVeterinario.objects.get_or_create(lote=lote)

        return tratamiento

    @staticmethod
    def obtener_tratamientos_activos(lote: Optional[Lote] = None) -> List[Tratamiento]:
        """
        Obtiene tratamientos que están actualmente en curso.

        Args:
            lote: Opcional, filtrar por lote específico

        Returns:
            list: Lista de tratamientos activos
        """
        hoy = timezone.now().date()
        queryset = Tratamiento.objects.filter(
            eliminado=False,
            fecha_inicio__lte=hoy
        ).filter(
            # fecha_fin es None (en curso) o fecha_fin >= hoy
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=hoy)
        ).select_related('lote', 'lote__galpon', 'aplicado_por')

        if lote:
            queryset = queryset.filter(lote=lote)

        return list(queryset)

    # =========================================================================
    # MORTALIDAD
    # =========================================================================

    @staticmethod
    @transaction.atomic
    def registrar_mortalidad(
        lote: Lote,
        cantidad_aves: int,
        causa: str,
        usuario: User,
        observaciones: str = ""
    ) -> Mortalidad:
        """
        Registra mortalidad en un lote y actualiza la cantidad de aves.

        Args:
            lote: Instancia de Lote
            cantidad_aves: Cantidad de aves muertas
            causa: Causa probable de la mortalidad
            usuario: Usuario que registra
            observaciones: Observaciones adicionales

        Returns:
            Mortalidad: Instancia creada
        """
        mortalidad = Mortalidad.objects.create(
            lote=lote,
            fecha=timezone.now().date(),
            cantidad_aves=cantidad_aves,
            causa=causa,
            observaciones=observaciones,
            registrado_por=usuario
        )

        # Actualizar cantidad de aves en el lote
        lote.cantidad_aves = max(0, lote.cantidad_aves - cantidad_aves)
        lote.save(update_fields=['cantidad_aves', 'actualizado_en'])

        # Asegurar que existe historial veterinario
        HistorialVeterinario.objects.get_or_create(lote=lote)

        return mortalidad

    @staticmethod
    def obtener_mortalidad_acumulada(lote: Lote) -> Dict[str, Any]:
        """
        Obtiene estadísticas de mortalidad acumulada de un lote.

        Args:
            lote: Instancia de Lote

        Returns:
            dict: Estadísticas de mortalidad
        """
        mortalidades = Mortalidad.objects.filter(
            lote=lote,
            eliminado=False
        )

        total_muertos = mortalidades.aggregate(
            total=Sum('cantidad_aves')
        )['total'] or 0

        # Cantidad inicial (actual + muertos)
        cantidad_inicial = lote.cantidad_aves + total_muertos
        porcentaje_mortalidad = Decimal('0')
        if cantidad_inicial > 0:
            porcentaje_mortalidad = (Decimal(str(total_muertos)) / cantidad_inicial) * 100

        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'cantidad_inicial': cantidad_inicial,
            'cantidad_actual': lote.cantidad_aves,
            'total_mortalidad': total_muertos,
            'porcentaje_mortalidad': round(float(porcentaje_mortalidad), 2),
            'registros_mortalidad': mortalidades.count()
        }

    # =========================================================================
    # HISTORIAL VETERINARIO
    # =========================================================================

    @staticmethod
    def obtener_resumen_salud_lote(lote: Lote) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de la salud de un lote.

        Args:
            lote: Instancia de Lote

        Returns:
            dict: Resumen de salud completo
        """
        mortalidad_data = SaludService.obtener_mortalidad_acumulada(lote)
        vacunaciones_pendientes = SaludService.obtener_vacunaciones_pendientes(lote)

        total_vacunaciones = Vacunacion.objects.filter(
            lote=lote,
            eliminado=False
        ).count()

        total_tratamientos = Tratamiento.objects.filter(
            lote=lote,
            eliminado=False
        ).count()

        tratamientos_activos = len(SaludService.obtener_tratamientos_activos(lote))

        return {
            'lote_id': lote.id,
            'lote_nombre': lote.nombre,
            'edad_dias': lote.edad_dias,
            'total_vacunaciones': total_vacunaciones,
            'vacunaciones_pendientes': len(vacunaciones_pendientes),
            'detalle_pendientes': vacunaciones_pendientes,
            'total_tratamientos': total_tratamientos,
            'tratamientos_activos': tratamientos_activos,
            **mortalidad_data
        }
