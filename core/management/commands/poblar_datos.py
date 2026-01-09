"""
Comando de Django para poblar la base de datos con datos iniciales.
Ejecutar: python manage.py poblar_datos
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from finanzas.models import Proyecto, Categoria, Socio, Proveedor
from datetime import date


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos iniciales (usuarios, categorías, proyecto, proveedores)'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*50)
        self.stdout.write("POBLANDO BASE DE DATOS - EL CAMPO")
        self.stdout.write("="*50 + "\n")
        
        # Crear usuarios
        self.stdout.write("Creando usuarios...")
        self._crear_usuarios()
        
        # Crear categorías
        self.stdout.write("\nCreando categorías...")
        self._crear_categorias()
        
        # Crear proyecto inicial
        self.stdout.write("\nCreando proyecto inicial...")
        self._crear_proyecto_inicial()
        
        # Crear proveedores
        self.stdout.write("\nCreando proveedores...")
        self._crear_proveedores()
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("POBLACION COMPLETADA"))
        self.stdout.write("="*50)
        self.stdout.write("\nUsuarios creados:")
        self.stdout.write("  admin / admin (Administrador)")
        self.stdout.write("  nelly / nelly")
        self.stdout.write("  julio / julio")
        self.stdout.write("  paola / paola")
        self.stdout.write("  pablo / pablo")
        self.stdout.write("  luisa / luisa")
        self.stdout.write("  rene / rene")
        self.stdout.write("\n")

    def _crear_usuarios(self):
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
                self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario creado: {datos['username']}"))
            else:
                self.stdout.write(f"  [EXISTE] Usuario ya existe: {datos['username']}")
            
            # Crear perfil de socio
            Socio.objects.get_or_create(
                usuario=user,
                defaults={
                    'rol': datos['rol'],
                    'parentesco': datos['parentesco'],
                    'activo': True
                }
            )

    def _crear_categorias(self):
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
                self.stdout.write(self.style.SUCCESS(f"  [OK] Categoria creada: {datos['nombre']}"))
            else:
                self.stdout.write(f"  [EXISTE] Categoria ya existe: {datos['nombre']}")

    def _crear_proyecto_inicial(self):
        """Crear el proyecto principal"""
        proyecto, created = Proyecto.objects.get_or_create(
            nombre='Construcción Galpón Ponedoras',
            defaults={
                'presupuesto_objetivo': 100000.00,
                'fecha_inicio': date.today(),
                'descripcion': 'Construcción del galpón para 500 gallinas ponedoras. Financiado con crédito bancario.',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"  [OK] Proyecto creado: {proyecto.nombre}"))
        else:
            self.stdout.write(f"  [EXISTE] Proyecto ya existe: {proyecto.nombre}")

    def _crear_proveedores(self):
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
                self.stdout.write(self.style.SUCCESS(f"  [OK] Proveedor creado: {datos['nombre']}"))
            else:
                self.stdout.write(f"  [EXISTE] Proveedor ya existe: {datos['nombre']}")
