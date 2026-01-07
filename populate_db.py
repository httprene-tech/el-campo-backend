import os
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finanzas.models import Categoria

# 2. Lista de categorías a crear
cats = [
    "Infraestructura y Tinglado", "Materiales de Obra Bruta",
    "Mano de Obra", "Instalaciones", "Transporte",
    "Equipamiento Avícola", "Administrativo", "Gasto Inicial / Ajuste"
]

print("Iniciando población de categorías...")

# 3. Crear registros
for nombre in cats:
    obj, created = Categoria.objects.get_or_create(nombre=nombre)
    if created:
        print(f"[NUEVO] Categoría creada: {obj.nombre}")
    else:
        print(f"[EXISTE] Categoría ya existente: {obj.nombre}")

print("¡Proceso completado con éxito!")
