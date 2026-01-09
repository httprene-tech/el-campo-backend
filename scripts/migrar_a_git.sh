#!/bin/bash
# Script de migración segura a Git para EC2
# Preserva toda la configuración de producción

set -e  # Salir si hay errores

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  MIGRACION A GIT - EL CAMPO ERP${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Variables
REPO_URL="https://github.com/httprene-tech/el-campo-backend.git"
PROJECT_DIR="/home/ubuntu/elcampo"
BACKUP_DIR="/home/ubuntu/backups/elcampo_$(date +%Y%m%d_%H%M%S)"

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encontró manage.py${NC}"
    echo -e "${YELLOW}Ejecuta este script desde el directorio del proyecto${NC}"
    exit 1
fi

echo -e "${YELLOW}[PASO 1/8] Creando backup completo...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup de .env (CRÍTICO)
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    echo -e "${GREEN}  ✓ .env respaldado${NC}"
else
    echo -e "${RED}  ✗ .env NO encontrado - CRÍTICO${NC}"
    echo -e "${YELLOW}  ¿Continuar sin .env? (s/n)${NC}"
    read -r respuesta
    if [ "$respuesta" != "s" ] && [ "$respuesta" != "S" ]; then
        exit 1
    fi
fi

# Backup de media
if [ -d "media" ]; then
    tar -czf "$BACKUP_DIR/media_backup.tar.gz" media/
    echo -e "${GREEN}  ✓ media/ respaldado${NC}"
fi

# Backup de staticfiles
if [ -d "staticfiles" ]; then
    tar -czf "$BACKUP_DIR/staticfiles_backup.tar.gz" staticfiles/
    echo -e "${GREEN}  ✓ staticfiles/ respaldado${NC}"
fi

# Backup de archivos de configuración
[ -f "elcampo.service" ] && cp elcampo.service "$BACKUP_DIR/" && echo -e "${GREEN}  ✓ elcampo.service respaldado${NC}"
[ -f "elcampo_nginx" ] && cp elcampo_nginx "$BACKUP_DIR/" && echo -e "${GREEN}  ✓ elcampo_nginx respaldado${NC}"

echo -e "${GREEN}  Backup guardado en: $BACKUP_DIR${NC}\n"

echo -e "${YELLOW}[PASO 2/8] Verificando Git...${NC}"
if [ -d ".git" ]; then
    echo -e "${GREEN}  ✓ Git ya está inicializado${NC}"
    git remote -v
    echo -e "${YELLOW}  ¿Actualizar remoto? (s/n)${NC}"
    read -r respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        git remote set-url origin "$REPO_URL"
        echo -e "${GREEN}  ✓ Remoto actualizado${NC}"
    fi
else
    echo -e "${YELLOW}  Inicializando Git...${NC}"
    git init
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}  ✓ Git inicializado${NC}"
fi

echo -e "\n${YELLOW}[PASO 3/8] Obteniendo código del repositorio...${NC}"
git fetch origin

# Verificar si hay cambios locales
if [ -d ".git" ] && [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo -e "${YELLOW}  ⚠ Hay cambios locales no guardados${NC}"
    echo -e "${YELLOW}  ¿Deseas guardarlos en un commit? (s/n)${NC}"
    read -r respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        git add .
        git commit -m "Backup antes de migración - $(date +%Y%m%d_%H%M%S)"
    fi
fi

# Hacer checkout del código
echo -e "${YELLOW}  Obteniendo código de main...${NC}"
git checkout -B main origin/main 2>/dev/null || git checkout main
echo -e "${GREEN}  ✓ Código actualizado${NC}"

echo -e "\n${YELLOW}[PASO 4/8] Restaurando archivos de configuración...${NC}"
if [ -f "$BACKUP_DIR/.env.backup" ]; then
    cp "$BACKUP_DIR/.env.backup" .env
    echo -e "${GREEN}  ✓ .env restaurado${NC}"
else
    echo -e "${RED}  ✗ No se pudo restaurar .env${NC}"
    echo -e "${YELLOW}  Debes crear .env manualmente con tus credenciales de RDS${NC}"
fi

# Restaurar media
if [ -f "$BACKUP_DIR/media_backup.tar.gz" ]; then
    if [ -d "media" ]; then
        rm -rf media
    fi
    tar -xzf "$BACKUP_DIR/media_backup.tar.gz"
    echo -e "${GREEN}  ✓ media/ restaurado${NC}"
fi

# Restaurar staticfiles
if [ -f "$BACKUP_DIR/staticfiles_backup.tar.gz" ]; then
    if [ -d "staticfiles" ]; then
        rm -rf staticfiles
    fi
    tar -xzf "$BACKUP_DIR/staticfiles_backup.tar.gz"
    echo -e "${GREEN}  ✓ staticfiles/ restaurado${NC}"
fi

echo -e "\n${YELLOW}[PASO 5/8] Verificando entorno virtual...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}  ✓ venv existe${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}  Creando venv...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}  ✓ venv creado${NC}"
fi

echo -e "\n${YELLOW}[PASO 6/8] Instalando dependencias...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}  ✓ Dependencias instaladas${NC}"

echo -e "\n${YELLOW}[PASO 7/8] Aplicando migraciones y recolectando estáticos...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}  ✓ Migraciones aplicadas${NC}"

python manage.py collectstatic --noinput
echo -e "${GREEN}  ✓ Archivos estáticos recolectados${NC}"

# Verificar configuración
python manage.py check --deploy
echo -e "${GREEN}  ✓ Verificación de configuración OK${NC}"

echo -e "\n${YELLOW}[PASO 8/8] Reiniciando servicios...${NC}"
sudo systemctl daemon-reload
sudo systemctl restart elcampo
sleep 2
sudo systemctl restart nginx
echo -e "${GREEN}  ✓ Servicios reiniciados${NC}"

# Verificar estado
echo -e "\n${YELLOW}Verificando estado de servicios...${NC}"
sudo systemctl status elcampo --no-pager | head -5
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  MIGRACION COMPLETADA EXITOSAMENTE${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "Backup guardado en: ${YELLOW}$BACKUP_DIR${NC}"
echo -e "\nVerifica que todo funciona:"
echo -e "  ${YELLOW}sudo systemctl status elcampo${NC}"
echo -e "  ${YELLOW}sudo journalctl -u elcampo -f${NC}"
echo -e "  ${YELLOW}curl https://el-campo-back.duckdns.org/admin/${NC}\n"
