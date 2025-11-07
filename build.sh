#!/usr/bin/env bash
# Script de build recomendado para Render.com
set -euo pipefail

echo "Actualizando pip e instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Build completo."
