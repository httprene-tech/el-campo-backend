#!/bin/bash
# Script de despliegue seguro para EC2
# Preserva configuración de producción (.env, media, staticfiles, etc.)

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DESPLIEGUE SEGURO - EL CAMPO ERP${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Variables
PROJECT_DIR="/home/ubuntu/elcampo"  # Ajusta según tu ruta
BACKUP_DIR="/home/ubuntu/backups/elcampo_$(date +%Y%m%d_%H%M%S)"
REPO_URL=""  # Tu URL del repositorio Git

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encontró manage.py. Asegúrate de estar en el directorio del proyecto.${NC}"
    exit 1
fi

# 1. BACKUP de archivos críticos
echo -e "${YELLOW}[1/7] Creando backup de archivos críticos...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup de .env
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    echo -e "${GREEN}  ✓ .env respaldado${NC}"
else
    echo -e "${YELLOW}  ⚠ .env no encontrado (se creará uno nuevo)${NC}"
fi

# Backup de media files
if [ -d "media" ]; then
    cp -r media "$BACKUP_DIR/media_backup"
    echo -e "${GREEN}  ✓ Archivos media respaldados${NC}"
fi

# Backup de staticfiles
if [ -d "staticfiles" ]; then
    cp -r staticfiles "$BACKUP_DIR/staticfiles_backup"
    echo -e "${GREEN}  ✓ Archivos estáticos respaldados${NC}"
fi

# Backup de base de datos (opcional)
echo -e "${YELLOW}  ¿Deseas hacer backup de la base de datos? (s/n)${NC}"
read -r backup_db
if [ "$backup_db" = "s" ] || [ "$backup_db" = "S" ]; then
    source .env 2>/dev/null || true
    if [ -n "$DB_NAME" ] && [ -n "$DB_USER" ]; then
        pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" > "$BACKUP_DIR/db_backup.sql"
        echo -e "${GREEN}  ✓ Base de datos respaldada${NC}"
    else
        echo -e "${YELLOW}  ⚠ Variables de BD no encontradas en .env${NC}"
    fi
fi

echo -e "${GREEN}  Backup guardado en: $BACKUP_DIR${NC}\n"

# 2. Guardar archivos de configuración de producción
echo -e "${YELLOW}[2/7] Guardando archivos de configuración...${NC}"
CONFIG_FILES=()

# Guardar .env si existe
if [ -f ".env" ]; then
    CONFIG_FILES+=(".env")
fi

# Guardar archivos de nginx/systemd si existen
if [ -f "elcampo_nginx" ]; then
    CONFIG_FILES+=("elcampo_nginx")
fi

if [ -f "elcampo.service" ]; then
    CONFIG_FILES+=("elcampo.service")
fi

# Guardar en directorio temporal
TEMP_CONFIG_DIR="/tmp/elcampo_config_$$"
mkdir -p "$TEMP_CONFIG_DIR"
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$TEMP_CONFIG_DIR/"
        echo -e "${GREEN}  ✓ $file guardado${NC}"
    fi
done

# 3. Obtener cambios del repositorio
echo -e "${YELLOW}[3/7] Obteniendo cambios del repositorio...${NC}"

# Si es la primera vez (no hay .git)
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}  Primera vez: clonando repositorio...${NC}"
    if [ -z "$REPO_URL" ]; then
        echo -e "${RED}  Error: REPO_URL no configurado. Edita este script.${NC}"
        exit 1
    fi
    
    # Mover proyecto actual a temporal
    cd ..
    mv elcampo elcampo_old_$(date +%Y%m%d_%H%M%S)
    
    # Clonar repositorio
    git clone "$REPO_URL" elcampo
    cd elcampo
    
    echo -e "${GREEN}  ✓ Repositorio clonado${NC}"
else
    # Actualizar repositorio existente
    git fetch origin
    git reset --hard origin/main  # o 'master' según tu rama principal
    echo -e "${GREEN}  ✓ Código actualizado${NC}"
fi

# 4. Restaurar archivos de configuración
echo -e "${YELLOW}[4/7] Restaurando archivos de configuración...${NC}"
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$TEMP_CONFIG_DIR/$file" ]; then
        cp "$TEMP_CONFIG_DIR/$file" .
        echo -e "${GREEN}  ✓ $file restaurado${NC}"
    fi
done

# Limpiar directorio temporal
rm -rf "$TEMP_CONFIG_DIR"

# 5. Restaurar media y staticfiles
echo -e "${YELLOW}[5/7] Restaurando archivos media y staticfiles...${NC}"
if [ -d "$BACKUP_DIR/media_backup" ]; then
    if [ -d "media" ]; then
        rm -rf media
    fi
    cp -r "$BACKUP_DIR/media_backup" media
    echo -e "${GREEN}  ✓ Archivos media restaurados${NC}"
fi

if [ -d "$BACKUP_DIR/staticfiles_backup" ]; then
    if [ -d "staticfiles" ]; then
        rm -rf staticfiles
    fi
    cp -r "$BACKUP_DIR/staticfiles_backup" staticfiles
    echo -e "${GREEN}  ✓ Archivos estáticos restaurados${NC}"
fi

# 6. Instalar/Actualizar dependencias
echo -e "${YELLOW}[6/7] Instalando dependencias...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}  ✓ Dependencias instaladas${NC}"
else
    echo -e "${YELLOW}  ⚠ venv no encontrado. Creando uno nuevo...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}  ✓ Entorno virtual creado y dependencias instaladas${NC}"
fi

# 7. Aplicar migraciones y recolectar estáticos
echo -e "${YELLOW}[7/7] Aplicando migraciones y recolectando estáticos...${NC}"

# Aplicar migraciones
python manage.py migrate --noinput
echo -e "${GREEN}  ✓ Migraciones aplicadas${NC}"

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
echo -e "${GREEN}  ✓ Archivos estáticos recolectados${NC}"

# Verificar configuración
python manage.py check --deploy
echo -e "${GREEN}  ✓ Verificación de configuración completada${NC}"

# Reiniciar servicios
echo -e "\n${YELLOW}Reiniciando servicios...${NC}"
sudo systemctl daemon-reload
sudo systemctl restart elcampo
sudo systemctl restart nginx

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "Backup guardado en: ${YELLOW}$BACKUP_DIR${NC}"
echo -e "Verifica el estado con: ${YELLOW}sudo systemctl status elcampo${NC}"
echo -e "Ver logs con: ${YELLOW}sudo journalctl -u elcampo -f${NC}\n"
