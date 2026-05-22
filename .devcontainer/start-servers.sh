#!/bin/bash
export PATH="/usr/lib/postgresql/13/bin:$HOME/.local/bin:$PATH"
export DATABASE_URL="postgresql+asyncpg://lims:limsdev@localhost:5433/olive_lims"
export SYNC_DATABASE_URL="postgresql+psycopg2://lims:limsdev@localhost:5433/olive_lims"
export SECRET_KEY="dev-secret"
export MEDIA_ROOT="/workspaces/LIMS-/media"
export CORS_ORIGINS="*"

mkdir -p ~/pgsocket /workspaces/LIMS-/media

# Arrancar PostgreSQL
pg_ctl -D ~/pgdata -o "-p 5433 -k /home/vscode/pgsocket" -l ~/pgdata/logfile start 2>/dev/null || true
sleep 2

# Backend
pkill -f 'uvicorn app.main' 2>/dev/null || true
cd /workspaces/LIMS-/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  > /tmp/backend.log 2>&1 &
echo "✓ Backend arrancando (puerto 8000)"

# Frontend
pkill -f vite 2>/dev/null || true
cd /workspaces/LIMS-/frontend
nohup npm run dev -- --host 0.0.0.0 \
  > /tmp/frontend.log 2>&1 &
echo "✓ Frontend arrancando (puerto 5173)"

sleep 5
if curl -s http://localhost:8000/health | grep -q 'ok'; then
  echo "✅ Todo listo — abre el puerto 5173"
  echo "   Login: admin@olivelims.local / Admin1234!"
else
  echo "⚠️  Revisando logs: tail -f /tmp/backend.log"
fi
