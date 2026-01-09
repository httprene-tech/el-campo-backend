from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Categoria, Proyecto, Gasto, Comprobante, Proveedor,
    Socio, Album, FotoAlbum, CarpetaDocumento, Documento
)


# ============================================================================
# INLINES
# ============================================================================

class ComprobanteInline(admin.TabularInline):
    """Permite subir múltiples fotos dentro de la misma pantalla de Gasto"""
    model = Comprobante
    extra = 1
    readonly_fields = ('ver_imagen',)

    def ver_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" />', obj.imagen.url)
        return "Sin imagen"
    ver_imagen.short_description = "Vista Previa"


class FotoAlbumInline(admin.TabularInline):
    """Permite subir múltiples fotos dentro del álbum"""
    model = FotoAlbum
    extra = 1
    readonly_fields = ('ver_miniatura',)
    fields = ('imagen', 'titulo', 'descripcion', 'fecha_foto', 'ver_miniatura')

    def ver_miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px;" />', obj.imagen.url)
        return "Sin imagen"
    ver_miniatura.short_description = "Miniatura"


class DocumentoInline(admin.TabularInline):
    """Permite ver documentos dentro de la carpeta"""
    model = Documento
    extra = 0
    readonly_fields = ('ver_archivo', 'creado_en', 'subido_por')
    fields = ('nombre', 'tipo', 'archivo', 'fecha_documento', 'ver_archivo')

    def ver_archivo(self, obj):
        if obj.archivo:
            return format_html('<a href="{}" target="_blank">📄 Ver</a>', obj.archivo.url)
        return "-"
    ver_archivo.short_description = "Archivo"


# ============================================================================
# ADMIN DE SOCIOS/FAMILIA
# ============================================================================

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'parentesco', 'rol', 'telefono', 'activo', 'creado_en')
    list_filter = ('rol', 'activo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'parentesco')
    list_editable = ('activo',)
    readonly_fields = ('creado_en', 'actualizado_en')
    
    def nombre_completo(self, obj):
        nombre = obj.usuario.get_full_name() or obj.usuario.username
        return format_html('<strong>{}</strong>', nombre)
    nombre_completo.short_description = "Nombre"


# ============================================================================
# ADMIN DE PROYECTOS Y GASTOS
# ============================================================================

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'presupuesto_objetivo', 'total_gastado_format', 'saldo_restante_format', 'fecha_inicio')
    readonly_fields = ('total_gastado_format', 'saldo_restante_format', 'creado_en', 'actualizado_en')
    search_fields = ('nombre',)

    def total_gastado_format(self, obj):
        try:
            val = float(obj.total_gastado)
            return format_html('<b>{:,.2f} Bs</b>', val)
        except (ValueError, TypeError):
            return format_html('<b>{} Bs</b>', obj.total_gastado)
    total_gastado_format.short_description = "Total Gastado"

    def saldo_restante_format(self, obj):
        try:
            val = float(obj.saldo_restante)
            color = "green" if val > 0 else "red"
            return format_html('<b style="color: {};">{:,.2f} Bs</b>', color, val)
        except (ValueError, TypeError):
             return format_html('<b>{} Bs</b>', obj.saldo_restante)
    saldo_restante_format.short_description = "Saldo Disponible"


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'descripcion', 'monto_format', 'categoria', 'metodo_pago', 'es_retroactivo', 'usuario')
    list_filter = ('categoria', 'metodo_pago', 'es_retroactivo', 'fecha', 'proyecto')
    search_fields = ('descripcion', 'proveedor_rel__nombre', 'nro_referencia', 'notas_contexto')
    autocomplete_fields = ['categoria', 'proyecto', 'proveedor_rel']
    inlines = [ComprobanteInline]
    readonly_fields = ('creado_en', 'actualizado_en')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('proyecto', 'categoria', 'monto', 'descripcion', 'fecha')
        }),
        ('Detalles de Pago', {
            'fields': ('proveedor_rel', 'metodo_pago', 'nro_referencia')
        }),
        ('Información Adicional', {
            'fields': ('es_retroactivo', 'notas_contexto'),
            'classes': ('collapse',)
        }),
    )

    def monto_format(self, obj):
        return format_html('<b>{:,.2f} Bs</b>', obj.monto)
    monto_format.short_description = "Monto"
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ('nombre', 'descripcion', 'cantidad_gastos')
    readonly_fields = ('creado_en', 'actualizado_en')
    
    def cantidad_gastos(self, obj):
        return obj.gastos.filter(eliminado=False).count()
    cantidad_gastos.short_description = "Gastos Registrados"


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('gasto', 'creado_en', 'ver_foto')
    list_filter = ('creado_en',)
    readonly_fields = ('creado_en', 'actualizado_en')
    
    def ver_foto(self, obj):
        return format_html('<a href="{}" target="_blank">Ver Imagen</a>', obj.imagen.url)
    ver_foto.short_description = "Comprobante"


# ============================================================================
# ADMIN DE PROVEEDORES
# ============================================================================

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'especialidad', 'total_pagado_format', 'cantidad_gastos')
    search_fields = ('nombre', 'especialidad')
    readonly_fields = ('total_pagado_format', 'creado_en', 'actualizado_en')
    
    def total_pagado_format(self, obj):
        return format_html('<b>{:,.2f} Bs</b>', obj.total_pagado)
    total_pagado_format.short_description = "Total Pagado"
    
    def cantidad_gastos(self, obj):
        return obj.gastos.filter(eliminado=False).count()
    cantidad_gastos.short_description = "Cantidad de Gastos"


# ============================================================================
# ADMIN DE GALERÍA
# ============================================================================

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_fotos_display', 'creado_en', 'creado_por')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('cantidad_fotos_display', 'creado_en', 'actualizado_en')
    inlines = [FotoAlbumInline]
    
    def cantidad_fotos_display(self, obj):
        return format_html('<b>{}</b> fotos', obj.cantidad_fotos)
    cantidad_fotos_display.short_description = "Cantidad"
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(FotoAlbum)
class FotoAlbumAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'titulo', 'album', 'fecha_foto', 'creado_en', 'subido_por')
    list_filter = ('album', 'creado_en')
    search_fields = ('titulo', 'descripcion', 'album__nombre')
    readonly_fields = ('creado_en', 'actualizado_en')
    
    def miniatura(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    miniatura.short_description = "Foto"
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# ADMIN DE DOCUMENTOS
# ============================================================================

@admin.register(CarpetaDocumento)
class CarpetaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('icono_nombre', 'cantidad_docs', 'creado_en')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('cantidad_docs', 'creado_en', 'actualizado_en')
    inlines = [DocumentoInline]
    
    def icono_nombre(self, obj):
        return format_html('📁 <b>{}</b>', obj.nombre)
    icono_nombre.short_description = "Carpeta"
    
    def cantidad_docs(self, obj):
        return format_html('<b>{}</b> documentos', obj.cantidad_documentos)
    cantidad_docs.short_description = "Contenido"


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'carpeta', 'fecha_documento', 'ver_archivo', 'subido_por')
    list_filter = ('tipo', 'carpeta', 'fecha_documento')
    search_fields = ('nombre', 'descripcion')
    autocomplete_fields = ['carpeta']
    date_hierarchy = 'fecha_documento'
    
    def ver_archivo(self, obj):
        if obj.archivo:
            return format_html('<a href="{}" target="_blank">📄 Descargar</a>', obj.archivo.url)
        return "-"
    ver_archivo.short_description = "Archivo"
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)
