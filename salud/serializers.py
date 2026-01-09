"""
Serializers para el módulo de salud.
"""
from rest_framework import serializers
from .models import Vacunacion, Tratamiento, Mortalidad, HistorialVeterinario


class VacunacionSerializer(serializers.ModelSerializer):
    """Serializer para vacunaciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    lote_galpon = serializers.ReadOnlyField(source='lote.galpon.nombre')
    aplicado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Vacunacion
        fields = [
            'id', 'lote', 'lote_nombre', 'lote_galpon', 'fecha',
            'tipo_vacuna', 'cantidad_aves', 'metodo_aplicacion',
            'aplicado_por', 'aplicado_por_nombre', 'observaciones',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_aplicado_por_nombre(self, obj):
        if obj.aplicado_por:
            return obj.aplicado_por.get_full_name() or obj.aplicado_por.username
        return None


class VacunacionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de vacunaciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')

    class Meta:
        model = Vacunacion
        fields = ['id', 'lote', 'lote_nombre', 'fecha', 'tipo_vacuna', 'cantidad_aves']


class TratamientoSerializer(serializers.ModelSerializer):
    """Serializer para tratamientos."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    aplicado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Tratamiento
        fields = [
            'id', 'lote', 'lote_nombre', 'fecha_inicio', 'fecha_fin',
            'tipo', 'tipo_display', 'medicamento', 'dosis', 'cantidad_aves',
            'motivo', 'aplicado_por', 'aplicado_por_nombre', 'resultado',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_aplicado_por_nombre(self, obj):
        if obj.aplicado_por:
            return obj.aplicado_por.get_full_name() or obj.aplicado_por.username
        return None


class TratamientoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de tratamientos."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Tratamiento
        fields = ['id', 'lote', 'lote_nombre', 'fecha_inicio', 'tipo', 'tipo_display', 'medicamento']


class MortalidadSerializer(serializers.ModelSerializer):
    """Serializer para mortalidad."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    porcentaje_mortalidad = serializers.ReadOnlyField()
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Mortalidad
        fields = [
            'id', 'lote', 'lote_nombre', 'fecha', 'cantidad_aves',
            'porcentaje_mortalidad', 'causa', 'observaciones',
            'registrado_por', 'registrado_por_nombre',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_registrado_por_nombre(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.get_full_name() or obj.registrado_por.username
        return None


class MortalidadListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de mortalidad."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')

    class Meta:
        model = Mortalidad
        fields = ['id', 'lote', 'lote_nombre', 'fecha', 'cantidad_aves', 'causa']


class HistorialVeterinarioSerializer(serializers.ModelSerializer):
    """Serializer para historial veterinario."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    total_vacunaciones = serializers.ReadOnlyField()
    total_tratamientos = serializers.ReadOnlyField()
    total_mortalidad = serializers.ReadOnlyField()
    veterinario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialVeterinario
        fields = [
            'id', 'lote', 'lote_nombre', 'notas_generales',
            'veterinario_responsable', 'veterinario_nombre',
            'total_vacunaciones', 'total_tratamientos', 'total_mortalidad',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_veterinario_nombre(self, obj):
        if obj.veterinario_responsable:
            return obj.veterinario_responsable.get_full_name() or obj.veterinario_responsable.username
        return None
