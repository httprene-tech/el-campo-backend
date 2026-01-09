"""
Serializers para el módulo de producción.
"""
from rest_framework import serializers
from .models import Galpon, Lote, Recoleccion, CalidadHuevo


class GalponSerializer(serializers.ModelSerializer):
    """Serializer para galpones."""
    cantidad_aves_actual = serializers.ReadOnlyField()
    cantidad_lotes_activos = serializers.SerializerMethodField()

    class Meta:
        model = Galpon
        fields = [
            'id', 'nombre', 'capacidad_maxima', 'descripcion', 'activo',
            'cantidad_aves_actual', 'cantidad_lotes_activos',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_cantidad_lotes_activos(self, obj):
        """Retorna la cantidad de lotes activos en el galpón."""
        return obj.lotes.filter(activo=True, eliminado=False).count()


class GalponListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de galpones."""
    cantidad_aves_actual = serializers.ReadOnlyField()

    class Meta:
        model = Galpon
        fields = ['id', 'nombre', 'capacidad_maxima', 'activo', 'cantidad_aves_actual']


class LoteSerializer(serializers.ModelSerializer):
    """Serializer para lotes."""
    galpon_nombre = serializers.ReadOnlyField(source='galpon.nombre')
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    edad_dias = serializers.ReadOnlyField()
    total_huevos_recolectados = serializers.ReadOnlyField()
    promedio_diario_huevos = serializers.ReadOnlyField()
    cantidad_recolecciones = serializers.SerializerMethodField()

    class Meta:
        model = Lote
        fields = [
            'id', 'nombre', 'galpon', 'galpon_nombre', 'fecha_ingreso', 'fecha_salida',
            'cantidad_aves', 'raza', 'estado', 'estado_display', 'activo',
            'edad_dias', 'total_huevos_recolectados', 'promedio_diario_huevos',
            'cantidad_recolecciones', 'notas', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_cantidad_recolecciones(self, obj):
        """Retorna la cantidad de recolecciones del lote."""
        return obj.recolecciones.filter(eliminado=False).count()


class LoteListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de lotes."""
    galpon_nombre = serializers.ReadOnlyField(source='galpon.nombre')
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    edad_dias = serializers.ReadOnlyField()

    class Meta:
        model = Lote
        fields = [
            'id', 'nombre', 'galpon', 'galpon_nombre', 'fecha_ingreso',
            'cantidad_aves', 'estado', 'estado_display', 'activo', 'edad_dias'
        ]


class RecoleccionSerializer(serializers.ModelSerializer):
    """Serializer para recolecciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    lote_galpon = serializers.ReadOnlyField(source='lote.galpon.nombre')
    recolectado_por_nombre = serializers.SerializerMethodField()
    tiene_calidad = serializers.SerializerMethodField()

    class Meta:
        model = Recoleccion
        fields = [
            'id', 'lote', 'lote_nombre', 'lote_galpon', 'fecha', 'cantidad_huevos',
            'hora_recoleccion', 'recolectado_por', 'recolectado_por_nombre',
            'tiene_calidad', 'notas', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_recolectado_por_nombre(self, obj):
        """Retorna el nombre del usuario que registró la recolección."""
        if obj.recolectado_por:
            return obj.recolectado_por.get_full_name() or obj.recolectado_por.username
        return None

    def get_tiene_calidad(self, obj):
        """Indica si la recolección tiene evaluación de calidad."""
        return obj.calidad_huevos.exists()


class RecoleccionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de recolecciones."""
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')

    class Meta:
        model = Recoleccion
        fields = ['id', 'lote', 'lote_nombre', 'fecha', 'cantidad_huevos']


class CalidadHuevoSerializer(serializers.ModelSerializer):
    """Serializer para calidad de huevos."""
    recoleccion_fecha = serializers.ReadOnlyField(source='recoleccion.fecha')
    recoleccion_lote = serializers.ReadOnlyField(source='recoleccion.lote.nombre')
    tipo_defecto_display = serializers.CharField(source='get_tipo_defecto_display', read_only=True)
    total_huevos = serializers.ReadOnlyField()
    porcentaje_primera = serializers.ReadOnlyField()
    evaluado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = CalidadHuevo
        fields = [
            'id', 'recoleccion', 'recoleccion_fecha', 'recoleccion_lote',
            'cantidad_primera', 'cantidad_segunda', 'cantidad_descarte',
            'total_huevos', 'porcentaje_primera', 'tipo_defecto', 'tipo_defecto_display',
            'observaciones', 'evaluado_por', 'evaluado_por_nombre',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_evaluado_por_nombre(self, obj):
        """Retorna el nombre del usuario que evaluó."""
        if obj.evaluado_por:
            return obj.evaluado_por.get_full_name() or obj.evaluado_por.username
        return None
