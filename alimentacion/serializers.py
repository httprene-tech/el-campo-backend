"""
Serializers para el módulo de alimentación.
"""
from rest_framework import serializers
from .models import ProveedorAlimento, FormulaAlimento, Racion, ConsumoDiario


class ProveedorAlimentoSerializer(serializers.ModelSerializer):
    """Serializer para proveedores de alimento."""
    class Meta:
        model = ProveedorAlimento
        fields = [
            'id', 'nombre', 'contacto', 'telefono', 'direccion', 'activo',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']


class FormulaAlimentoSerializer(serializers.ModelSerializer):
    """Serializer para fórmulas de alimento."""
    cantidad_raciones = serializers.SerializerMethodField()

    class Meta:
        model = FormulaAlimento
        fields = [
            'id', 'nombre', 'descripcion', 'edad_minima_semanas',
            'edad_maxima_semanas', 'activa', 'cantidad_raciones',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_cantidad_raciones(self, obj):
        """Retorna la cantidad de raciones usando esta fórmula."""
        return obj.raciones.filter(eliminado=False).count()


class FormulaAlimentoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de fórmulas."""
    class Meta:
        model = FormulaAlimento
        fields = ['id', 'nombre', 'edad_minima_semanas', 'edad_maxima_semanas', 'activa']


class RacionSerializer(serializers.ModelSerializer):
    """Serializer para raciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    formula_nombre = serializers.ReadOnlyField(source='formula.nombre')
    consumo_por_ave = serializers.ReadOnlyField()
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Racion
        fields = [
            'id', 'lote', 'lote_nombre', 'formula', 'formula_nombre',
            'fecha', 'cantidad_kg', 'consumo_por_ave',
            'registrado_por', 'registrado_por_nombre', 'notas',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_registrado_por_nombre(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.get_full_name() or obj.registrado_por.username
        return None


class RacionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de raciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    formula_nombre = serializers.ReadOnlyField(source='formula.nombre')

    class Meta:
        model = Racion
        fields = ['id', 'lote', 'lote_nombre', 'formula', 'formula_nombre', 'fecha', 'cantidad_kg']


class ConsumoDiarioSerializer(serializers.ModelSerializer):
    """Serializer para consumos diarios."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    material_nombre = serializers.ReadOnlyField(source='material_alimento.nombre')
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ConsumoDiario
        fields = [
            'id', 'lote', 'lote_nombre', 'material_alimento', 'material_nombre',
            'fecha', 'cantidad_kg', 'registrado_por', 'registrado_por_nombre',
            'notas', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_registrado_por_nombre(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.get_full_name() or obj.registrado_por.username
        return None


class ConsumoDiarioListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de consumos."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    material_nombre = serializers.ReadOnlyField(source='material_alimento.nombre')

    class Meta:
        model = ConsumoDiario
        fields = ['id', 'lote', 'lote_nombre', 'material_alimento', 'material_nombre', 'fecha', 'cantidad_kg']
