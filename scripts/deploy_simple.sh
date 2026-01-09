#!/bin/bash
# Script simplificado para actualizar desde Git sin perder configuración
# Uso: ./scripts/deploy_simple.sh

set -e

echo "=========================================="
echo "  ACTUALIZACION DESDE GIT - EL CAMPO"
echo "=========================================="
echo ""

# 1. Backup de .env
if [ -f ".env" ]; then
    cp .env .env.backup
    echo "[OK] .env respaldado"
fi

# 2. Guardar media si existe
if [ -d "media" ]; then
    mv media media_backup_temp
    echo "[OK] Media guardado temporalmente"
fi

# 3. Actualizar desde Git
if [ -d ".git" ]; then
    echo "Actualizando desde Git..."
    git fetch origin
    git reset --hard origin/main  # Cambia 'main' por tu rama
    echo "[OK] Código actualizado"
else
    echo "Error: No es un repositorio Git. Ejecuta primero: git init && git remote add origin TU_URL"
    exit 1
fi

# 4. Restaurar .env
if [ -f ".env.backup" ]; then
    mv .env.backup .env
    echo "[OK] .env restaurado"
fi

# 5. Restaurar media
if [ -d "media_backup_temp" ]; then
    if [ -d "media" ]; then
        rm -rf media
    fi
    mv media_backup_temp media
    echo "[OK] Media restaurado"
fi

# 6. Instalar dependencias
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "[OK] Dependencias actualizadas"
fi

# 7. Migraciones y estáticos
python manage.py migrate --noinput
python manage.py collectstatic --noinput
echo "[OK] Migraciones y estáticos aplicados"

# 8. Reiniciar
sudo systemctl restart elcampo
sudo systemctl restart nginx
echo "[OK] Servicios reiniciados"

echo ""
echo "=========================================="
echo "  ACTUALIZACION COMPLETADA"
echo "=========================================="
