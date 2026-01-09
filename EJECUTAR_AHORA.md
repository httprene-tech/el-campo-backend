# ⚡ EJECUTA ESTO AHORA EN TU EC2

Estás conectado al servidor. Sigue estos pasos **en orden**:

## 🔍 PASO 1: Verificar Estado Actual

Ejecuta estos comandos para ver qué tienes:

```bash
# Ver dónde estás
pwd

# Buscar el proyecto
find /home -name "manage.py" -type f 2>/dev/null

# Si encontraste el proyecto, ir ahí
cd /ruta/del/proyecto  # Reemplaza con la ruta que encontraste

# Ver qué hay
ls -la

# Verificar archivos críticos
[ -f .env ] && echo "✓ .env existe" || echo "✗ .env NO existe"
[ -d venv ] && echo "✓ venv existe" || echo "✗ venv NO existe"
[ -d .git ] && echo "✓ Git existe" || echo "✗ NO tiene Git"
```

## 📤 PASO 2: Subir Scripts (Desde Windows PowerShell)

**Abre OTRA terminal de PowerShell** (no cierres la SSH) y ejecuta:

```powershell
# Subir script de migración
scp -i "D:\Escritorio\Software el Campo\elcampo.pem" "D:\Escritorio\Software el Campo\scripts\migrar_a_git.sh" ubuntu@13.58.39.205:/home/ubuntu/

# Subir script de verificación
scp -i "D:\Escritorio\Software el Campo\elcampo.pem" "D:\Escritorio\Software el Campo\scripts\verificar_servidor.sh" ubuntu@13.58.39.205:/home/ubuntu/
```

## 🚀 PASO 3: Ejecutar Migración (En la terminal SSH)

Vuelve a tu terminal SSH y ejecuta:

```bash
# Hacer ejecutables
chmod +x ~/migrar_a_git.sh
chmod +x ~/verificar_servidor.sh

# Primero verificar
~/verificar_servidor.sh

# Luego migrar (esto hará TODO automáticamente)
cd /home/ubuntu/elcampo  # Ajusta la ruta según lo que encontraste
~/migrar_a_git.sh
```

## ✅ PASO 4: Verificar que Funciona

```bash
# Ver estado del servicio
sudo systemctl status elcampo

# Ver logs
sudo journalctl -u elcampo -n 20

# Probar el sitio
curl -I https://el-campo-back.duckdns.org/admin/
```

## 🆘 Si Algo Sale Mal

```bash
# Ver el backup (está en ~/backups/)
ls -la ~/backups/

# Restaurar .env desde backup
cp ~/backups/elcampo_*/env.backup /home/ubuntu/elcampo/.env
```

---

## 📋 Alternativa: Migración Manual (Si prefieres control total)

Si no quieres usar el script automático, ejecuta estos comandos **uno por uno**:

```bash
# 1. Ir al proyecto
cd /home/ubuntu/elcampo  # Ajusta la ruta

# 2. Backup de .env (CRÍTICO)
cp .env .env.backup
cat .env | grep DB_  # Verificar que tiene credenciales

# 3. Backup de media y staticfiles
mkdir -p ~/backups
[ -d media ] && tar -czf ~/backups/media_backup.tar.gz media/
[ -d staticfiles ] && tar -czf ~/backups/staticfiles_backup.tar.gz staticfiles/

# 4. Inicializar Git
git init
git remote add origin https://github.com/httprene-tech/el-campo-backend.git
git fetch origin
git checkout -b main origin/main

# 5. Restaurar .env
cp .env.backup .env

# 6. Instalar dependencias
source venv/bin/activate
pip install -r requirements.txt

# 7. Migraciones
python manage.py migrate
python manage.py collectstatic --noinput

# 8. Reiniciar
sudo systemctl restart elcampo
sudo systemctl restart nginx

# 9. Verificar
sudo systemctl status elcampo
```

---

## ⚠️ IMPORTANTE

- ✅ El script **preserva** tu `.env` con las credenciales de RDS
- ✅ El script **preserva** tus archivos `media/` y `staticfiles/`
- ✅ El script **hace backup** de todo antes de cambiar algo
- ✅ **NO** se perderá tu configuración de producción

**¿Listo? Empieza con el PASO 1** 👆
