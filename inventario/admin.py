from django.contrib import admin
from .models import Material, MovimientoInventario


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'tipo_inventario', 'unidad_medida', 'stock_actual', 'stock_minimo_alerta', 'stock_bajo']
    list_filter = ['tipo_inventario', 'unidad_medida', 'eliminado']
    search_fields = ['nombre', 'codigo', 'descripcion']
    readonly_fields = ['stock_actual', 'creado_en', 'actualizado_en']


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['material', 'tipo', 'cantidad', 'fecha', 'usuario', 'gasto']
    list_filter = ['tipo', 'fecha', 'material__tipo_inventario', 'eliminado']
    search_fields = ['material__nombre', 'nota']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'
