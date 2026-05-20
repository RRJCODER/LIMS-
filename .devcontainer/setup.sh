#!/bin/bash
set -e

echo "========================================"
echo "  Olive Oil LIMS — Configuración inicial"
echo "========================================"

# Fix PATH for pip-installed binaries
export PATH="$HOME/.local/bin:$PATH"

# ── PostgreSQL ──────────────────────────────────────────────────
echo ""
echo "[1/4] Instalando PostgreSQL..."
sudo apt-get update -qq
sudo apt-get install -y -qq postgresql postgresql-client
sudo service postgresql start

# Esperar a que PostgreSQL esté listo
for i in $(seq 1 10); do
  sudo runuser -l postgres -c "pg_isready -q" 2>/dev/null && break
  sleep 1
done

sudo runuser -l postgres -c "psql -c \"CREATE USER lims WITH PASSWORD 'limsdev';\"" 2>/dev/null || echo "  Usuario lims ya existe"
sudo runuser -l postgres -c "psql -c \"CREATE DATABASE olive_lims OWNER lims;\"" 2>/dev/null || echo "  Base de datos ya existe"
sudo runuser -l postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE olive_lims TO lims;\"" 2>/dev/null || true
echo "  ✓ PostgreSQL listo"

# ── Python deps ──────────────────────────────────────────────────
echo ""
echo "[2/4] Instalando dependencias Python..."
cd /workspaces/LIMS-/backend
pip install --quiet \
  pydantic-settings \
  fastapi \
  "sqlalchemy[asyncio]" \
  asyncpg \
  alembic \
  pydantic \
  passlib \
  "bcrypt==4.0.1" \
  uvicorn \
  python-multipart \
  aiofiles \
  email-validator \
  psycopg2-binary
echo "  ✓ Dependencias Python instaladas"

# ── Migraciones y datos iniciales ────────────────────────────────
echo ""
echo "[3/4] Aplicando migraciones y cargando datos..."
export DATABASE_URL="postgresql+asyncpg://lims:limsdev@localhost/olive_lims"
export SYNC_DATABASE_URL="postgresql+psycopg2://lims:limsdev@localhost/olive_lims"
export SECRET_KEY="dev-secret-key-codespaces"
export MEDIA_ROOT="/workspaces/LIMS-/media"
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
mkdir -p /workspaces/LIMS-/media
python3 -m alembic upgrade head
python3 -m app.utils.seed
echo "  ✓ Base de datos lista"

# ── Frontend deps ────────────────────────────────────────────────
echo ""
echo "[4/4] Instalando dependencias Node.js..."
cd /workspaces/LIMS-/frontend
npm install --silent
echo "  ✓ Dependencias frontend instaladas"

echo ""
echo "=========================================="
echo "  ✅ Setup completo! Arrancando servidores..."
echo "=========================================="
