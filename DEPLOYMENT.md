# Guía de Despliegue en Producción

## Requisitos Previos

- Python 3.12+
- PostgreSQL 12+
- Virtual environment activado
- Variables de entorno configuradas

## Pasos para Desplegar en Producción (EC2)

### 1. Conectarse al servidor

```bash
ssh -i elcampo.pem usuario@tu-ip-ec2
```

### 2. Clonar/Actualizar el código

```bash
cd /ruta/del/proyecto
git pull origin main  # o la rama que uses
```

### 3. Activar el entorno virtual

```bash
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

### 4. Instalar/Actualizar dependencias

```bash
pip install -r requirements.txt
```

### 5. Aplicar Migraciones

**IMPORTANTE**: En producción, NUNCA ejecutes `reset_database.py`. Solo aplica migraciones:

```bash
python manage.py migrate
```

Si necesitas resetear la base de datos (solo en desarrollo local):
```bash
python reset_database.py  # SOLO EN DESARROLLO
```

### 6. Recolectar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 7. Crear superusuario (si es necesario)

```bash
python manage.py createsuperuser
```

### 8. Poblar datos iniciales (opcional)

```bash
python manage.py poblar_datos
```

### 9. Reiniciar el servidor

```bash
# Con systemd
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# O con supervisor
sudo supervisorctl restart elcampo
```

## Comandos Útiles

### Verificar estado de migraciones

```bash
python manage.py showmigrations
```

### Crear nuevas migraciones (solo en desarrollo)

```bash
python manage.py makemigrations
```

### Verificar configuración

```bash
python manage.py check --deploy
```

## Variables de Entorno Necesarias

Asegúrate de tener configurado en tu servidor (archivo `.env` o variables del sistema):

```env
SECRET_KEY=tu-secret-key-super-segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,tu-ip-ec2
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_bd
```

## Notas Importantes

1. **NUNCA ejecutes `reset_database.py` en producción** - Esto eliminará TODOS los datos
2. **Siempre haz backup antes de migraciones** en producción
3. **Usa `--noinput` en producción** para evitar prompts interactivos
4. **Configura `DEBUG=False`** en producción
5. **Usa un servidor WSGI** (Gunicorn, uWSGI) en lugar del servidor de desarrollo

## Backup de Base de Datos

```bash
# Backup
pg_dump -U usuario nombre_bd > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar
psql -U usuario nombre_bd < backup_archivo.sql
```

## Estructura de Archivos en Producción

```
proyecto/
├── core/
│   ├── settings.py
│   └── ...
├── finanzas/
├── inventario/
├── produccion/
├── salud/
├── alimentacion/
├── calendario/
├── core/
│   └── management/
│       └── commands/
│           └── poblar_datos.py  # Comando para poblar datos
├── manage.py
├── requirements.txt
└── .env  # NO subir a git
```

## Troubleshooting

### Error: "no existe la columna X.creado_en"

Esto significa que las migraciones no están aplicadas. Ejecuta:
```bash
python manage.py migrate
```

### Error: "ModuleNotFoundError: No module named 'core'"

Asegúrate de estar en el directorio raíz del proyecto y que el entorno virtual esté activado.

### Error: "ProgrammingError: relation does not exist"

Las tablas no existen. Aplica las migraciones:
```bash
python manage.py migrate
```
