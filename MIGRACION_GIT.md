# Guía de Migración a Git en EC2

Esta guía te ayudará a migrar tu proyecto en EC2 a Git sin perder tu configuración de producción.

## ⚠️ IMPORTANTE: Antes de Empezar

1. **Haz backup completo** de tu servidor EC2
2. **Anota tus credenciales** de base de datos RDS
3. **Guarda tu archivo .env** actual
4. **Verifica que tu repositorio Git esté actualizado** con todos los cambios locales

## Opción 1: Migración Segura (Recomendada)

### Paso 1: Preparar en tu EC2

```bash
# Conectarte a EC2
ssh -i elcampo.pem ubuntu@tu-ip-ec2

# Ir al directorio del proyecto
cd /ruta/donde/esta/tu/proyecto

# Hacer backup completo
mkdir -p ~/backups
tar -czf ~/backups/elcampo_backup_$(date +%Y%m%d).tar.gz .
```

### Paso 2: Guardar configuración crítica

```bash
# Guardar .env
cp .env ~/backups/.env.backup

# Guardar archivos de configuración del servidor
cp elcampo.service ~/backups/ 2>/dev/null || true
cp elcampo_nginx ~/backups/ 2>/dev/null || true
```

### Paso 3: Inicializar Git (si no existe)

```bash
# Si el proyecto NO tiene Git
git init
git remote add origin https://github.com/tu-usuario/tu-repo.git
git fetch origin
git checkout -b main origin/main  # o 'master' según tu repo
```

### Paso 4: Restaurar configuración

```bash
# Restaurar .env
cp ~/backups/.env.backup .env

# Verificar que .env tiene tus credenciales de RDS
cat .env | grep DB_
```

### Paso 5: Instalar dependencias y aplicar migraciones

```bash
# Activar venv
source venv/bin/activate  # o: . venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones (NO resetear BD)
python manage.py migrate

# Recolectar estáticos
python manage.py collectstatic --noinput
```

### Paso 6: Reiniciar servicios

```bash
sudo systemctl restart elcampo
sudo systemctl restart nginx

# Verificar que todo funciona
sudo systemctl status elcampo
```

## Opción 2: Usar Script Automático

### Paso 1: Subir script a EC2

```bash
# Desde tu máquina local
scp -i elcampo.pem scripts/deploy_simple.sh ubuntu@tu-ip:/home/ubuntu/
```

### Paso 2: Ejecutar en EC2

```bash
# Conectarte a EC2
ssh -i elcampo.pem ubuntu@tu-ip

# Ir al proyecto
cd /ruta/del/proyecto

# Hacer ejecutable
chmod +x ~/deploy_simple.sh

# Ejecutar
~/deploy_simple.sh
```

## Opción 3: Clonar en Nuevo Directorio (Más Seguro)

Si prefieres no tocar tu proyecto actual:

```bash
# 1. Clonar en nuevo directorio
cd /home/ubuntu
git clone https://github.com/tu-usuario/tu-repo.git elcampo_new

# 2. Copiar configuración del proyecto antiguo
cd elcampo_new
cp ../elcampo/.env .
cp -r ../elcampo/media . 2>/dev/null || true
cp -r ../elcampo/staticfiles . 2>/dev/null || true

# 3. Configurar servicios para apuntar al nuevo directorio
sudo nano /etc/systemd/system/elcampo.service
# Cambiar WorkingDirectory a /home/ubuntu/elcampo_new

# 4. Reiniciar
sudo systemctl daemon-reload
sudo systemctl restart elcampo

# 5. Si todo funciona, eliminar el antiguo
# (Solo después de verificar que todo funciona)
# rm -rf /home/ubuntu/elcampo
```

## Actualizaciones Futuras

Una vez configurado Git, para actualizar:

```bash
# Opción simple
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart elcampo

# O usar el script
./scripts/deploy_simple.sh
```

## Verificación Post-Migración

1. **Verificar que el sitio funciona:**
   ```bash
   curl https://el-campo-back.duckdns.org/admin/
   ```

2. **Verificar logs:**
   ```bash
   sudo journalctl -u elcampo -f
   ```

3. **Verificar base de datos:**
   ```bash
   python manage.py dbshell
   # Luego: \dt (listar tablas)
   ```

4. **Verificar que .env está protegido:**
   ```bash
   # .env NO debe estar en Git
   git status | grep .env  # No debe aparecer nada
   ```

## Troubleshooting

### Error: "no existe la columna X.creado_en"
```bash
python manage.py migrate
```

### Error: "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Permission denied"
```bash
sudo chown -R ubuntu:ubuntu /ruta/del/proyecto
```

### Los archivos no se actualizan
```bash
# Verificar que Git está configurado
git remote -v
git status

# Forzar actualización
git fetch origin
git reset --hard origin/main
```

## Archivos que NUNCA deben estar en Git

- `.env` (credenciales)
- `*.pem` (llaves SSH)
- `venv/` (entorno virtual)
- `__pycache__/` (caché Python)
- `media/` (archivos subidos por usuarios)
- `logs/` (archivos de log)
- `db.sqlite3` (si usas SQLite local)

Todos estos están en `.gitignore`.

## Checklist Final

- [ ] Proyecto clonado/actualizado desde Git
- [ ] `.env` restaurado con credenciales correctas
- [ ] Dependencias instaladas
- [ ] Migraciones aplicadas
- [ ] Archivos estáticos recolectados
- [ ] Servicios reiniciados
- [ ] Sitio web funciona correctamente
- [ ] Base de datos conectada (RDS)
- [ ] HTTPS funcionando
- [ ] Logs sin errores críticos

## Soporte

Si algo sale mal, siempre puedes restaurar desde el backup:
```bash
cd /ruta/del/proyecto
tar -xzf ~/backups/elcampo_backup_YYYYMMDD.tar.gz
```
