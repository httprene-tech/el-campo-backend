"""
Script para poblar tipos de evento en el calendario.
Ejecutar: python manage.py shell < poblar_calendario.py
"""
from calendario.models import TipoEvento

tipos = [
    {'nombre': 'Vacunación', 'descripcion': 'Vacunación de aves', 'color': '#EF4444', 'icono': 'syringe'},
    {'nombre': 'Limpieza', 'descripcion': 'Limpieza de galpón y equipos', 'color': '#22C55E', 'icono': 'broom'},
    {'nombre': 'Mantenimiento', 'descripcion': 'Mantenimiento de instalaciones', 'color': '#F59E0B', 'icono': 'wrench'},
    {'nombre': 'Compra', 'descripcion': 'Compra de materiales o insumos', 'color': '#3B82F6', 'icono': 'shopping-cart'},
    {'nombre': 'Pago', 'descripcion': 'Pago a proveedores o trabajadores', 'color': '#8B5CF6', 'icono': 'dollar-sign'},
    {'nombre': 'Reunión', 'descripcion': 'Reunión familiar o de trabajo', 'color': '#EC4899', 'icono': 'users'},
    {'nombre': 'Construcción', 'descripcion': 'Avance de obra o construcción', 'color': '#F97316', 'icono': 'hammer'},
    {'nombre': 'Recolección', 'descripcion': 'Recolección de huevos', 'color': '#14B8A6', 'icono': 'egg'},
    {'nombre': 'Visita Técnica', 'descripcion': 'Visita de veterinario o técnico', 'color': '#6366F1', 'icono': 'user-check'},
    {'nombre': 'Otro', 'descripcion': 'Otros eventos', 'color': '#64748B', 'icono': 'calendar'},
]

for t in tipos:
    obj, created = TipoEvento.objects.get_or_create(nombre=t['nombre'], defaults=t)
    print(f"[OK] {t['nombre']}" if created else f"[EXISTE] {t['nombre']}")

print(f"\nTotal: {TipoEvento.objects.count()} tipos de evento")
