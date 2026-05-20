#!/bin/bash

echo "🚀 Arrancando servicios LIMS..."

# PostgreSQL
sudo service postgresql start 2>/dev/null || true

# Esperar a que PostgreSQL esté listo
until sudo -u postgres pg_isready -q 2>/dev/null; do
  sleep 1
done

# Crear directorio de media si no existe
mkdir -p /workspaces/LIMS-/media

# Backend
cd /workspaces/LIMS-/backend
pkill -f 'uvicorn app.main' 2>/dev/null || true
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
  > /tmp/lims-backend.log 2>&1 &
echo "  ✓ Backend arrancando (puerto 8000)... log: /tmp/lims-backend.log"

# Frontend
cd /workspaces/LIMS-/frontend
pkill -f 'vite' 2>/dev/null || true
nohup npm run dev -- --host 0.0.0.0 \
  > /tmp/lims-frontend.log 2>&1 &
echo "  ✓ Frontend arrancando (puerto 5173)... log: /tmp/lims-frontend.log"

echo ""
echo "⏳ Espera ~5 segundos y Codespaces abrirá el navegador automáticamente."
echo "   O ve a la pestaña PORTS y haz clic en el globo junto al puerto 5173."
echo ""
echo "   Login: admin@olivelims.local / Admin1234!"
