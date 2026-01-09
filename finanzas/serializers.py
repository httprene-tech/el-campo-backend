# Django imports
from django.contrib.auth.models import User

# Django REST Framework imports
from rest_framework import serializers

# Local imports
from .models import (
    Proyecto, Categoria, Gasto, Comprobante, Proveedor,
    Socio, Album, FotoAlbum, CarpetaDocumento, Documento
)


# ============================================================================
# SERIALIZERS DE USUARIO Y AUTENTICACIÓN
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User con grupos/roles."""
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'groups']


# ============================================================================
# SERIALIZERS DE SOCIOS/FAMILIA
# ============================================================================

class SocioSerializer(serializers.ModelSerializer):
    """Serializer para socios/familia del proyecto."""
    usuario_detalle = UserSerializer(source='usuario', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)

    class Meta:
        model = Socio
        fields = [
            'id', 'usuario', 'usuario_detalle', 'nombre_completo',
            'rol', 'rol_display', 'telefono', 'parentesco', 
            'activo', 'fecha_registro'
        ]

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username


# ============================================================================
# SERIALIZERS DE CATEGORÍAS Y COMPROBANTES
# ============================================================================

class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorías de gastos."""
    class Meta:
        model = Categoria
        fields = '__all__'


class ComprobanteSerializer(serializers.ModelSerializer):
    """Serializer para comprobantes/fotos de gastos."""
    class Meta:
        model = Comprobante
        fields = ['id', 'imagen', 'subido_en']


# ============================================================================
# SERIALIZERS DE PROVEEDORES
# ============================================================================

class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer para proveedores con cálculos agregados."""
    total_pagado = serializers.ReadOnlyField()
    cantidad_gastos = serializers.SerializerMethodField()

    class Meta:
        model = Proveedor
        fields = '__all__'

    def get_cantidad_gastos(self, obj):
        """Retorna la cantidad de gastos asociados al proveedor."""
        return obj.gastos.filter(eliminado=False).count()


# ============================================================================
# SERIALIZERS DE GASTOS
# ============================================================================

class GastoSerializer(serializers.ModelSerializer):
    """Serializer para gastos con información relacionada."""
    fotos = ComprobanteSerializer(many=True, read_only=True)
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    usuario_detalle = UserSerializer(source='usuario', read_only=True)
    proveedor_detalle = ProveedorSerializer(source='proveedor_rel', read_only=True)

    class Meta:
        model = Gasto
        fields = [
            'id', 'proyecto', 'categoria', 'categoria_nombre', 'usuario', 
            'usuario_detalle', 'monto', 'descripcion', 'fecha', 
            'proveedor_rel', 'proveedor_detalle', 'metodo_pago', 'nro_referencia', 
            'es_retroactivo', 'notas_contexto', 'imagen_comprobante', 'fotos', 'creado_en'
        ]


# ============================================================================
# SERIALIZERS DE PROYECTOS
# ============================================================================

class ProyectoSerializer(serializers.ModelSerializer):
    """Serializer para proyectos con cálculos de presupuesto."""
    total_gastado = serializers.ReadOnlyField()
    saldo_restante = serializers.ReadOnlyField()
    porcentaje_consumido = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = [
            'id', 'nombre', 'presupuesto_objetivo', 'fecha_inicio', 
            'descripcion', 'total_gastado', 'saldo_restante', 'porcentaje_consumido'
        ]

    def get_porcentaje_consumido(self, obj):
        """Calcula el porcentaje del presupuesto consumido."""
        if obj.presupuesto_objetivo > 0:
            porcentaje = (obj.total_gastado / obj.presupuesto_objetivo) * 100
            return round(porcentaje, 2)
        return 0


# ============================================================================
# SERIALIZERS DE GALERÍA
# ============================================================================

class FotoAlbumSerializer(serializers.ModelSerializer):
    """Serializer para fotos de álbumes."""
    subido_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = FotoAlbum
        fields = [
            'id', 'album', 'imagen', 'titulo', 'descripcion',
            'fecha_foto', 'fecha_subida', 'subido_por', 'subido_por_nombre'
        ]

    def get_subido_por_nombre(self, obj):
        if obj.subido_por:
            return obj.subido_por.get_full_name() or obj.subido_por.username
        return None


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer para álbumes con fotos anidadas."""
    fotos = FotoAlbumSerializer(many=True, read_only=True)
    cantidad_fotos = serializers.ReadOnlyField()
    creado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_creacion',
            'creado_por', 'creado_por_nombre', 'cantidad_fotos', 'fotos'
        ]

    def get_creado_por_nombre(self, obj):
        if obj.creado_por:
            return obj.creado_por.get_full_name() or obj.creado_por.username
        return None


class AlbumListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de álbumes (sin fotos anidadas)."""
    cantidad_fotos = serializers.ReadOnlyField()
    portada = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion', 'cantidad_fotos', 'portada']

    def get_portada(self, obj):
        """Retorna la URL de la primera foto como portada."""
        primera_foto = obj.fotos.first()
        if primera_foto:
            return primera_foto.imagen.url
        return None


# ============================================================================
# SERIALIZERS DE DOCUMENTOS
# ============================================================================

class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para documentos."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    subido_por_nombre = serializers.SerializerMethodField()
    carpeta_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            'id', 'carpeta', 'carpeta_nombre', 'tipo', 'tipo_display',
            'nombre', 'archivo', 'descripcion', 'fecha_documento',
            'fecha_subida', 'subido_por', 'subido_por_nombre'
        ]

    def get_subido_por_nombre(self, obj):
        if obj.subido_por:
            return obj.subido_por.get_full_name() or obj.subido_por.username
        return None

    def get_carpeta_nombre(self, obj):
        if obj.carpeta:
            return obj.carpeta.nombre
        return "Sin carpeta"


class CarpetaDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para carpetas de documentos."""
    documentos = DocumentoSerializer(many=True, read_only=True)
    cantidad_documentos = serializers.ReadOnlyField()

    class Meta:
        model = CarpetaDocumento
        fields = [
            'id', 'nombre', 'descripcion', 'icono',
            'fecha_creacion', 'cantidad_documentos', 'documentos'
        ]


class CarpetaDocumentoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de carpetas (sin documentos anidados)."""
    cantidad_documentos = serializers.ReadOnlyField()

    class Meta:
        model = CarpetaDocumento
        fields = ['id', 'nombre', 'descripcion', 'icono', 'cantidad_documentos']