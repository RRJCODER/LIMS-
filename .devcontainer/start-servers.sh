#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"
export DATABASE_URL="postgresql+asyncpg://lims:limsdev@localhost/olive_lims"
export SYNC_DATABASE_URL="postgresql+psycopg2://lims:limsdev@localhost/olive_lims"
export SECRET_KEY="dev-secret-key-codespaces"
export MEDIA_ROOT="/workspaces/LIMS-/media"
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

echo "🚀 Arrancando servicios LIMS..."

# PostgreSQL
sudo service postgresql start 2>/dev/null || true
for i in $(seq 1 10); do
  sudo runuser -l postgres -c "pg_isready -q" 2>/dev/null && break
  sleep 1
done

mkdir -p /workspaces/LIMS-/media

# Backend
pkill -f 'uvicorn app.main' 2>/dev/null || true
cd /workspaces/LIMS-/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
  > /tmp/lims-backend.log 2>&1 &
echo "  ✓ Backend en puerto 8000 (log: /tmp/lims-backend.log)"

# Frontend
pkill -f 'vite' 2>/dev/null || true
cd /workspaces/LIMS-/frontend
nohup npm run dev -- --host 0.0.0.0 \
  > /tmp/lims-frontend.log 2>&1 &
echo "  ✓ Frontend en puerto 5173 (log: /tmp/lims-frontend.log)"

sleep 4
echo ""
if curl -s http://localhost:8000/health | grep -q 'ok'; then
  echo "  ✅ Backend OK"
else
  echo "  ⚠️  Backend aún arrancando — revisa /tmp/lims-backend.log"
fi

echo ""
echo "  🌐 Abre la pestaña PORTS y haz clic en el globo del puerto 5173"
echo "  Login: admin@olivelims.local / Admin1234!"
