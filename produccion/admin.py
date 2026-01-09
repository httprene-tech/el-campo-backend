from django.contrib import admin
from .models import Galpon, Lote, Recoleccion, CalidadHuevo


@admin.register(Galpon)
class GalponAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_maxima', 'cantidad_aves_actual', 'activo']
    list_filter = ['activo', 'eliminado']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'galpon', 'fecha_ingreso', 'cantidad_aves', 'estado', 'activo']
    list_filter = ['estado', 'activo', 'galpon', 'fecha_ingreso', 'eliminado']
    search_fields = ['nombre', 'raza', 'notas']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha_ingreso'


@admin.register(Recoleccion)
class RecoleccionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'cantidad_huevos', 'recolectado_por']
    list_filter = ['fecha', 'lote', 'lote__galpon', 'eliminado']
    search_fields = ['lote__nombre', 'notas']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'


@admin.register(CalidadHuevo)
class CalidadHuevoAdmin(admin.ModelAdmin):
    list_display = ['recoleccion', 'cantidad_primera', 'cantidad_segunda', 'cantidad_descarte', 'tipo_defecto']
    list_filter = ['tipo_defecto', 'recoleccion__fecha', 'eliminado']
    search_fields = ['observaciones', 'recoleccion__lote__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
