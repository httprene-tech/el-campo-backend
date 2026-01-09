from django.contrib import admin
from .models import Vacunacion, Tratamiento, Mortalidad, HistorialVeterinario


@admin.register(Vacunacion)
class VacunacionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'tipo_vacuna', 'cantidad_aves', 'aplicado_por']
    list_filter = ['fecha', 'lote', 'lote__galpon', 'eliminado']
    search_fields = ['tipo_vacuna', 'observaciones', 'lote__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['fecha_inicio', 'lote', 'tipo', 'medicamento', 'cantidad_aves']
    list_filter = ['tipo', 'fecha_inicio', 'lote', 'eliminado']
    search_fields = ['medicamento', 'motivo', 'lote__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha_inicio'


@admin.register(Mortalidad)
class MortalidadAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'cantidad_aves', 'causa', 'registrado_por']
    list_filter = ['fecha', 'lote', 'lote__galpon', 'eliminado']
    search_fields = ['causa', 'observaciones', 'lote__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha'


@admin.register(HistorialVeterinario)
class HistorialVeterinarioAdmin(admin.ModelAdmin):
    list_display = ['lote', 'veterinario_responsable', 'total_vacunaciones', 'total_tratamientos']
    list_filter = ['lote__galpon', 'eliminado']
    search_fields = ['lote__nombre', 'notas_generales']
    readonly_fields = ['creado_en', 'actualizado_en']
