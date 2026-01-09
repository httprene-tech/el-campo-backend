# 🚀 Comandos para Ejecutar en EC2

## Conectarse al Servidor

```bash
ssh -i "D:\Escritorio\Software el Campo\elcampo.pem" ubuntu@13.58.39.205
```

## Paso 1: Verificar Estado Actual

```bash
# Ir al directorio del proyecto (ajusta la ruta si es diferente)
cd /home/ubuntu/elcampo

# Ver qué hay actualmente
ls -la

# Verificar si tiene Git
ls -la .git 2>/dev/null && echo "Tiene Git" || echo "NO tiene Git"

# Verificar archivos críticos
[ -f .env ] && echo "✓ .env existe" || echo "✗ .env NO existe"
[ -d venv ] && echo "✓ venv existe" || echo "✗ venv NO existe"
[ -d media ] && echo "✓ media existe" || echo "✗ media NO existe"
```

## Paso 2: Subir Scripts de Migración

**Desde tu Windows PowerShell (en otra terminal):**

```powershell
# Subir el script de migración
scp -i "D:\Escritorio\Software el Campo\elcampo.pem" "D:\Escritorio\Software el Campo\scripts\migrar_a_git.sh" ubuntu@13.58.39.205:/home/ubuntu/

# Subir el script de verificación
scp -i "D:\Escritorio\Software el Campo\scripts\verificar_servidor.sh" ubuntu@13.58.39.205:/home/ubuntu/
```

## Paso 3: Ejecutar Verificación (En EC2)

```bash
# Hacer ejecutables
chmod +x ~/verificar_servidor.sh
chmod +x ~/migrar_a_git.sh

# Ejecutar verificación
~/verificar_servidor.sh
```

## Paso 4: Ejecutar Migración (En EC2)

```bash
# Ir al proyecto
cd /home/ubuntu/elcampo

# Ejecutar migración
~/migrar_a_git.sh
```

El script te preguntará confirmaciones y hará todo automáticamente.

## Alternativa: Migración Manual (Paso a Paso)

Si prefieres hacerlo manualmente:

### 1. Backup de .env

```bash
cd /home/ubuntu/elcampo
cp .env .env.backup
cat .env | grep DB_  # Verificar credenciales de BD
```

### 2. Backup de Media y Staticfiles

```bash
mkdir -p ~/backups
tar -czf ~/backups/media_backup_$(date +%Y%m%d).tar.gz media/ 2>/dev/null || echo "No hay media"
tar -czf ~/backups/staticfiles_backup_$(date +%Y%m%d).tar.gz staticfiles/ 2>/dev/null || echo "No hay staticfiles"
```

### 3. Inicializar Git

```bash
# Si NO tiene Git
git init
git remote add origin https://github.com/httprene-tech/el-campo-backend.git
git fetch origin
git checkout -b main origin/main

# Si YA tiene Git
git remote set-url origin https://github.com/httprene-tech/el-campo-backend.git
git fetch origin
git reset --hard origin/main
```

### 4. Restaurar .env

```bash
cp .env.backup .env
# Verificar que tiene las credenciales correctas
cat .env | grep DB_
```

### 5. Instalar Dependencias

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Aplicar Migraciones

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Reiniciar Servicios

```bash
sudo systemctl restart elcampo
sudo systemctl restart nginx
```

### 8. Verificar

```bash
# Ver estado
sudo systemctl status elcampo

# Ver logs
sudo journalctl -u elcampo -f

# Probar sitio
curl https://el-campo-back.duckdns.org/admin/
```

## Verificación Post-Migración

```bash
# 1. Verificar que Git funciona
cd /home/ubuntu/elcampo
git status
git remote -v

# 2. Verificar que .env está protegido (NO debe estar en Git)
git status | grep .env
# No debe mostrar nada (está en .gitignore)

# 3. Verificar servicios
sudo systemctl status elcampo
sudo systemctl status nginx

# 4. Verificar base de datos
python manage.py dbshell
# Luego ejecutar: \dt (debe mostrar las tablas)
# Salir con: \q
```

## Actualizaciones Futuras

Una vez migrado, para actualizar:

```bash
cd /home/ubuntu/elcampo

# Opción 1: Manual
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart elcampo

# Opción 2: Con script (si lo subes)
./scripts/deploy_simple.sh
```

## Troubleshooting

### Error: "Permission denied"
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/elcampo
```

### Error: "No se encuentra .env"
```bash
# Crear .env desde el backup
cp .env.backup .env
# O crear uno nuevo basado en env.example
nano .env
```

### Error: "Git remote already exists"
```bash
git remote remove origin
git remote add origin https://github.com/httprene-tech/el-campo-backend.git
```

### Error: "venv no encontrado"
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Importante

- ✅ **SIEMPRE** haz backup antes de migrar
- ✅ **VERIFICA** que .env tiene las credenciales de RDS
- ✅ **NO** ejecutes `reset_database.py` en producción
- ✅ **CONFIRMA** que el sitio funciona después de migrar
