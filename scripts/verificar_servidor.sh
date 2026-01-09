#!/bin/bash
# Script para verificar el estado actual del servidor EC2

echo "=========================================="
echo "  VERIFICACION DEL SERVIDOR EC2"
echo "=========================================="
echo ""

# Verificar directorio del proyecto
echo "[1] Verificando directorio del proyecto..."
if [ -d "/home/ubuntu/elcampo" ]; then
    echo "  ✓ Proyecto encontrado en: /home/ubuntu/elcampo"
    cd /home/ubuntu/elcampo
    echo "  ✓ Directorio actual: $(pwd)"
else
    echo "  ✗ Proyecto NO encontrado en /home/ubuntu/elcampo"
    echo "  Buscando en otros lugares..."
    find /home -name "manage.py" -type f 2>/dev/null | head -5
fi

echo ""

# Verificar archivos críticos
if [ -f "manage.py" ]; then
    echo "[2] Archivos críticos encontrados:"
    [ -f ".env" ] && echo "  ✓ .env existe" || echo "  ✗ .env NO existe"
    [ -d "venv" ] && echo "  ✓ venv existe" || echo "  ✗ venv NO existe"
    [ -d "media" ] && echo "  ✓ media/ existe" || echo "  ⚠ media/ NO existe"
    [ -d "staticfiles" ] && echo "  ✓ staticfiles/ existe" || echo "  ⚠ staticfiles/ NO existe"
    [ -d ".git" ] && echo "  ✓ .git existe (ya tiene Git)" || echo "  ✗ .git NO existe (sin Git)"
fi

echo ""

# Verificar servicios
echo "[3] Estado de servicios:"
sudo systemctl status elcampo --no-pager | head -10 || echo "  ⚠ Servicio elcampo no encontrado"
echo ""
sudo systemctl status nginx --no-pager | head -10 || echo "  ⚠ Nginx no encontrado"

echo ""

# Verificar configuración de BD
if [ -f ".env" ]; then
    echo "[4] Variables de BD en .env:"
    grep "DB_" .env | sed 's/=.*/=***/' || echo "  ⚠ No se encontraron variables DB_"
else
    echo "[4] ⚠ .env no existe, no se puede verificar BD"
fi

echo ""

# Verificar espacio en disco
echo "[5] Espacio en disco:"
df -h / | tail -1

echo ""
echo "=========================================="
echo "  VERIFICACION COMPLETADA"
echo "=========================================="
