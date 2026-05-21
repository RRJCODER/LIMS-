#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"
export DATABASE_URL="postgresql+asyncpg://lims:limsdev@localhost/olive_lims"
export SYNC_DATABASE_URL="postgresql+psycopg2://lims:limsdev@localhost/olive_lims"
export SECRET_KEY="dev-secret-key-codespaces"
export MEDIA_ROOT="/workspaces/LIMS-/media"
export CORS_ORIGINS="*"

mkdir -p /workspaces/LIMS-/media

# Backend
pkill -f 'uvicorn app.main' 2>/dev/null || true
cd /workspaces/LIMS-/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
  > /tmp/lims-backend.log 2>&1 &
echo "✓ Backend arrancando (puerto 8000)"

# Frontend
pkill -f 'vite' 2>/dev/null || true
cd /workspaces/LIMS-/frontend
nohup npm run dev -- --host 0.0.0.0 \
  > /tmp/lims-frontend.log 2>&1 &
echo "✓ Frontend arrancando (puerto 5173)"

sleep 5
if curl -s http://localhost:8000/health | grep -q 'ok'; then
  echo "✅ Backend OK — http://localhost:8000"
else
  echo "⚠️  Backend aún iniciando — revisa: tail -f /tmp/lims-backend.log"
fi

echo ""
echo "🌐 Abre la pestaña PORTS y haz clic en el globo del puerto 5173"
echo "   Login: admin@olivelims.local / Admin1234!"
