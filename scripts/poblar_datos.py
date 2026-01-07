"""
Script de población de datos para la Granja Avícola El Campo.
Ejecutar con: python manage.py shell < scripts/poblar_datos.py
O desde el shell de Django.
"""
import os
import django

# Configurar Django si no está configurado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from finanzas.models import Proyecto, Categoria, Socio, Proveedor


def crear_usuarios():
    """Crear usuarios de la familia"""
    
    usuarios = [
        {
            'username': 'admin',
            'password': 'admin',
            'first_name': 'Administrador',
            'last_name': '',
            'is_superuser': True,
            'is_staff': True,
            'email': 'admin@elcampo.local',
            'rol': 'ADMINISTRADOR',
            'parentesco': 'Administrador'
        },
        {
            'username': 'nelly',
            'password': 'nelly',
            'first_name': 'Nelly',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'nelly@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
        {
            'username': 'julio',
            'password': 'julio',
            'first_name': 'Julio',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'julio@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
        {
            'username': 'paola',
            'password': 'paola',
            'first_name': 'Paola',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'paola@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
        {
            'username': 'pablo',
            'password': 'pablo',
            'first_name': 'Pablo',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'pablo@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
        {
            'username': 'luisa',
            'password': 'luisa',
            'first_name': 'Luisa',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'luisa@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
        {
            'username': 'rene',
            'password': 'rene',
            'first_name': 'René',
            'last_name': '',
            'is_superuser': False,
            'is_staff': False,
            'email': 'rene@elcampo.local',
            'rol': 'REGISTRADOR',
            'parentesco': 'Familiar'
        },
    ]
    
    for datos in usuarios:
        user, created = User.objects.get_or_create(
            username=datos['username'],
            defaults={
                'first_name': datos['first_name'],
                'last_name': datos['last_name'],
                'email': datos['email'],
                'is_superuser': datos['is_superuser'],
                'is_staff': datos['is_staff'],
            }
        )
        
        if created:
            user.set_password(datos['password'])
            user.save()
            print(f"✓ Usuario creado: {datos['username']}")
        else:
            print(f"→ Usuario ya existe: {datos['username']}")
        
        # Crear perfil de socio
        Socio.objects.get_or_create(
            usuario=user,
            defaults={
                'rol': datos['rol'],
                'parentesco': datos['parentesco'],
                'activo': True
            }
        )


def crear_categorias():
    """Crear categorías de gastos"""
    
    categorias = [
        {'nombre': 'Materiales', 'descripcion': 'Cemento, arena, fierros, ladrillos, etc.'},
        {'nombre': 'Mano de Obra', 'descripcion': 'Pago a albañiles, plomeros, electricistas'},
        {'nombre': 'Transporte', 'descripcion': 'Fletes, combustible, viáticos'},
        {'nombre': 'Equipamiento', 'descripcion': 'Herramientas, maquinaria, equipos'},
        {'nombre': 'Alimentación', 'descripcion': 'Comida para trabajadores'},
        {'nombre': 'Servicios', 'descripcion': 'Agua, luz, trámites'},
        {'nombre': 'Animales', 'descripcion': 'Compra de gallinas, pollos'},
        {'nombre': 'Medicamentos', 'descripcion': 'Vacunas, vitaminas, medicinas para aves'},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios no categorizados'},
    ]
    
    for datos in categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=datos['nombre'],
            defaults={'descripcion': datos['descripcion']}
        )
        if created:
            print(f"✓ Categoría creada: {datos['nombre']}")
        else:
            print(f"→ Categoría ya existe: {datos['nombre']}")


def crear_proyecto_inicial():
    """Crear el proyecto principal"""
    from datetime import date
    
    proyecto, created = Proyecto.objects.get_or_create(
        nombre='Construcción Galpón Ponedoras',
        defaults={
            'presupuesto_objetivo': 100000.00,
            'fecha_inicio': date.today(),
            'descripcion': 'Construcción del galpón para 500 gallinas ponedoras. Financiado con crédito bancario.',
        }
    )
    
    if created:
        print(f"✓ Proyecto creado: {proyecto.nombre}")
    else:
        print(f"→ Proyecto ya existe: {proyecto.nombre}")
    
    return proyecto


def crear_proveedores():
    """Crear proveedores de ejemplo"""
    
    proveedores = [
        {'nombre': 'Ferretería Central', 'especialidad': 'Materiales de construcción', 'telefono': '70001111'},
        {'nombre': 'Materiales Don Pepe', 'especialidad': 'Arena, grava, cemento', 'telefono': '70002222'},
        {'nombre': 'Soldaduras JM', 'especialidad': 'Estructuras metálicas', 'telefono': '70003333'},
    ]
    
    for datos in proveedores:
        prov, created = Proveedor.objects.get_or_create(
            nombre=datos['nombre'],
            defaults={
                'especialidad': datos['especialidad'],
                'telefono': datos.get('telefono', '')
            }
        )
        if created:
            print(f"✓ Proveedor creado: {datos['nombre']}")
        else:
            print(f"→ Proveedor ya existe: {datos['nombre']}")


def main():
    print("\n" + "="*50)
    print("POBLANDO BASE DE DATOS - EL CAMPO")
    print("="*50 + "\n")
    
    print("📁 Creando usuarios...")
    crear_usuarios()
    
    print("\n📂 Creando categorías...")
    crear_categorias()
    
    print("\n🏗️ Creando proyecto inicial...")
    crear_proyecto_inicial()
    
    print("\n🏪 Creando proveedores...")
    crear_proveedores()
    
    print("\n" + "="*50)
    print("✅ POBLACIÓN COMPLETADA")
    print("="*50)
    print("\nUsuarios creados:")
    print("  admin / admin (Administrador)")
    print("  nelly / nelly")
    print("  julio / julio")
    print("  paola / paola")
    print("  pablo / pablo")
    print("  luisa / luisa")
    print("  rene / rene")
    print("\n")


if __name__ == '__main__':
    main()
