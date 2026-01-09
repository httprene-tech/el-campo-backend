from django.contrib import admin
from .models import TipoEvento, Evento, Recordatorio


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color', 'icono', 'cantidad_eventos']
    list_filter = ['eliminado']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']

    def cantidad_eventos(self, obj):
        return obj.eventos.filter(eliminado=False).count()
    cantidad_eventos.short_description = 'Eventos'


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'fecha_inicio', 'fecha_fin', 'estado', 'asignado_a', 'todo_el_dia']
    list_filter = ['tipo', 'estado', 'tipo_recurrencia', 'fecha_inicio', 'eliminado']
    search_fields = ['titulo', 'descripcion', 'ubicacion']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha_inicio'


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ['evento', 'fecha_envio', 'enviado', 'metodo']
    list_filter = ['enviado', 'metodo', 'fecha_envio', 'eliminado']
    search_fields = ['evento__titulo', 'notas']
    readonly_fields = ['creado_en', 'actualizado_en']
    date_hierarchy = 'fecha_envio'
