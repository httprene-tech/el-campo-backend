"""
Serializers para el módulo de calendario.
"""
from rest_framework import serializers
from .models import TipoEvento, Evento, Recordatorio


class TipoEventoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de evento."""
    cantidad_eventos = serializers.SerializerMethodField()

    class Meta:
        model = TipoEvento
        fields = [
            'id', 'nombre', 'descripcion', 'color', 'icono',
            'cantidad_eventos', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_cantidad_eventos(self, obj):
        """Retorna la cantidad de eventos de este tipo (no eliminados)."""
        return obj.eventos.filter(eliminado=False).count()


class TipoEventoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de tipos de evento."""
    class Meta:
        model = TipoEvento
        fields = ['id', 'nombre', 'color', 'icono']


class EventoSerializer(serializers.ModelSerializer):
    """Serializer para eventos con información relacionada."""
    tipo_nombre = serializers.ReadOnlyField(source='tipo.nombre')
    tipo_color = serializers.ReadOnlyField(source='tipo.color')
    tipo_icono = serializers.ReadOnlyField(source='tipo.icono')
    usuario_nombre = serializers.SerializerMethodField()
    asignado_a_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_recurrencia_display = serializers.CharField(source='get_tipo_recurrencia_display', read_only=True)
    cantidad_recordatorios = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id', 'tipo', 'tipo_nombre', 'tipo_color', 'tipo_icono',
            'usuario', 'usuario_nombre', 'asignado_a', 'asignado_a_nombre',
            'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'todo_el_dia',
            'ubicacion', 'tipo_recurrencia', 'tipo_recurrencia_display',
            'fecha_fin_recurrencia', 'estado', 'estado_display',
            'recordatorio_minutos', 'cantidad_recordatorios',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_usuario_nombre(self, obj):
        """Retorna el nombre del usuario que creó el evento."""
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return None

    def get_asignado_a_nombre(self, obj):
        """Retorna el nombre del usuario asignado."""
        if obj.asignado_a:
            return obj.asignado_a.get_full_name() or obj.asignado_a.username
        return None

    def get_cantidad_recordatorios(self, obj):
        """Retorna la cantidad de recordatorios del evento."""
        return obj.recordatorios.count()


class EventoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de eventos."""
    tipo_nombre = serializers.ReadOnlyField(source='tipo.nombre')
    tipo_color = serializers.ReadOnlyField(source='tipo.color')
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'tipo', 'tipo_nombre', 'tipo_color',
            'fecha_inicio', 'fecha_fin', 'todo_el_dia', 'estado', 'estado_display',
            'asignado_a'
        ]


class RecordatorioSerializer(serializers.ModelSerializer):
    """Serializer para recordatorios."""
    evento_titulo = serializers.ReadOnlyField(source='evento.titulo')
    evento_fecha = serializers.ReadOnlyField(source='evento.fecha_inicio')

    class Meta:
        model = Recordatorio
        fields = [
            'id', 'evento', 'evento_titulo', 'evento_fecha',
            'fecha_envio', 'enviado', 'metodo', 'notas',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']
