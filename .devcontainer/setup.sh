#!/bin/bash
set -e
export PATH="/usr/lib/postgresql/13/bin:$HOME/.local/bin:$PATH"

echo "================================================"
echo "  Olive Oil LIMS — Setup inicial (una sola vez)"
echo "================================================"

# ── Instalar PostgreSQL ─────────────────────────────────
echo "[1/5] Instalando PostgreSQL..."
sudo apt-get update -qq
sudo apt-get install -y -qq postgresql postgresql-client
echo "  ✓ PostgreSQL instalado"

# ── Inicializar cluster propio (sin permisos de sistema) ─────
echo "[2/5] Inicializando base de datos..."
mkdir -p ~/pgsocket
if [ ! -f ~/pgdata/PG_VERSION ]; then
  initdb -D ~/pgdata --auth-local trust --auth-host trust
fi
pg_ctl -D ~/pgdata -o "-p 5433 -k /home/vscode/pgsocket" -l ~/pgdata/logfile start
sleep 3
createdb -h localhost -p 5433 olive_lims 2>/dev/null || true
psql -h localhost -p 5433 -d olive_lims -c "CREATE USER lims WITH PASSWORD 'limsdev';" 2>/dev/null || true
psql -h localhost -p 5433 -d olive_lims -c "GRANT ALL PRIVILEGES ON DATABASE olive_lims TO lims;" 2>/dev/null || true
echo "  ✓ Base de datos lista"

# ── Python deps ───────────────────────────────────────
echo "[3/5] Instalando dependencias Python..."
cd /workspaces/LIMS-/backend
pip install --quiet \
  pydantic-settings fastapi "sqlalchemy[asyncio]" asyncpg alembic \
  pydantic passlib "bcrypt==4.0.1" uvicorn python-multipart aiofiles \
  email-validator psycopg2-binary numpy scipy jinja2 weasyprint pillow \
  python-barcode qrcode
echo "  ✓ Python deps OK"

# ── Migraciones y seed ────────────────────────────────
echo "[4/5] Aplicando migraciones y cargando datos..."
export DATABASE_URL="postgresql+asyncpg://lims:limsdev@localhost:5433/olive_lims"
export SYNC_DATABASE_URL="postgresql+psycopg2://lims:limsdev@localhost:5433/olive_lims"
export SECRET_KEY="dev-secret"
export MEDIA_ROOT="/workspaces/LIMS-/media"
export CORS_ORIGINS="*"
mkdir -p /workspaces/LIMS-/media
python3 -m alembic upgrade head
python3 -m app.utils.seed
echo "  ✓ Datos cargados"

# ── Frontend deps ────────────────────────────────────
echo "[5/5] Instalando dependencias frontend..."
cd /workspaces/LIMS-/frontend
npm install --silent
echo "  ✓ Frontend deps OK"

pg_ctl -D ~/pgdata -o "-p 5433 -k /home/vscode/pgsocket" stop 2>/dev/null || true

echo ""
echo "================================================"
echo "  ✅ Setup completo"
echo "================================================"
