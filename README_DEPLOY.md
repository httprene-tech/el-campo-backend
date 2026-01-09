# 🚀 Guía Rápida de Despliegue

## Migración a Git en EC2 (Sin Perder Configuración)

### ⚡ Opción Rápida (Recomendada)

```bash
# 1. Conectarte a EC2
ssh -i elcampo.pem ubuntu@tu-ip-ec2

# 2. Ir al proyecto
cd /home/ubuntu/elcampo

# 3. Backup de .env
cp .env .env.backup

# 4. Si NO tienes Git, inicializar:
git init
git remote add origin TU_URL_DEL_REPO
git fetch origin
git checkout -b main origin/main

# 5. Si YA tienes Git, actualizar:
git pull origin main

# 6. Restaurar .env
cp .env.backup .env

# 7. Instalar y migrar
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# 8. Reiniciar
sudo systemctl restart elcampo
sudo systemctl restart nginx
```

### 📋 Checklist de Archivos a Preservar

Estos archivos **NO** deben sobrescribirse:

- ✅ `.env` - Credenciales de BD RDS y configuración
- ✅ `media/` - Archivos subidos por usuarios
- ✅ `staticfiles/` - Archivos estáticos compilados
- ✅ `elcampo.service` - Configuración de systemd
- ✅ `elcampo_nginx` - Configuración de nginx

Todos estos están en `.gitignore` y serán preservados.

### 🔄 Actualizaciones Futuras

```bash
# Usar el script automático
./scripts/deploy_simple.sh

# O manualmente
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart elcampo
```

### ⚠️ Importante

- **NUNCA** ejecutes `reset_database.py` en producción
- **SIEMPRE** haz backup antes de actualizar
- **VERIFICA** que `.env` tiene tus credenciales de RDS

Ver `MIGRACION_GIT.md` para guía completa.
