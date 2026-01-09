"""
Serializers para el módulo de inventario.
"""
from rest_framework import serializers
from .models import Material, MovimientoInventario


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer para materiales con información calculada."""
    stock_bajo = serializers.ReadOnlyField()
    porcentaje_stock = serializers.ReadOnlyField()
    tipo_inventario_display = serializers.CharField(source='get_tipo_inventario_display', read_only=True)
    unidad_medida_display = serializers.CharField(source='get_unidad_medida_display', read_only=True)
    cantidad_movimientos = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = [
            'id', 'nombre', 'codigo', 'tipo_inventario', 'tipo_inventario_display',
            'unidad_medida', 'unidad_medida_display', 'stock_actual', 
            'stock_minimo_alerta', 'stock_bajo', 'porcentaje_stock',
            'descripcion', 'cantidad_movimientos', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['stock_actual', 'creado_en', 'actualizado_en']

    def get_cantidad_movimientos(self, obj):
        """Retorna la cantidad de movimientos del material."""
        return obj.movimientos.filter(eliminado=False).count()


class MaterialListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de materiales."""
    stock_bajo = serializers.ReadOnlyField()
    tipo_inventario_display = serializers.CharField(source='get_tipo_inventario_display', read_only=True)

    class Meta:
        model = Material
        fields = [
            'id', 'nombre', 'codigo', 'tipo_inventario', 'tipo_inventario_display',
            'unidad_medida', 'stock_actual', 'stock_minimo_alerta', 'stock_bajo'
        ]


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de inventario."""
    material_nombre = serializers.ReadOnlyField(source='material.nombre')
    material_unidad = serializers.ReadOnlyField(source='material.unidad_medida')
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    gasto_detalle = serializers.SerializerMethodField()

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'material', 'material_nombre', 'material_unidad',
            'tipo', 'tipo_display', 'cantidad', 'fecha', 'nota',
            'gasto', 'gasto_detalle', 'usuario', 'usuario_nombre',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_usuario_nombre(self, obj):
        """Retorna el nombre del usuario que registró el movimiento."""
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return None

    def get_gasto_detalle(self, obj):
        """Retorna información del gasto asociado si existe."""
        if obj.gasto:
            return {
                'id': obj.gasto.id,
                'monto': str(obj.gasto.monto),
                'descripcion': obj.gasto.descripcion,
                'fecha': obj.gasto.fecha
            }
        return None
