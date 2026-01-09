from django.contrib import admin
from .models import ProveedorAlimento, FormulaAlimento, Racion, ConsumoDiario


@admin.register(ProveedorAlimento)
class ProveedorAlimentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'activo']
    list_filter = ['activo', 'eliminado']
    search_fields = ['nombre', 'contacto', 'telefono']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(FormulaAlimento)
class FormulaAlimentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edad_minima_semanas', 'edad_maxima_semanas', 'activa']
    list_filter = ['activa', 'eliminado']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(Racion)
class RacionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'formula', 'cantidad_kg', 'registrado_por']
    list_filter = ['fecha', 'lote', 'formula', 'eliminado']
    search_fields = ['lote__nombre', 'notas']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'


@admin.register(ConsumoDiario)
class ConsumoDiarioAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'material_alimento', 'cantidad_kg', 'registrado_por']
    list_filter = ['fecha', 'lote', 'material_alimento', 'eliminado']
    search_fields = ['lote__nombre', 'notas']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'
