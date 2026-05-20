#!/bin/bash
set -e

echo "========================================"
echo "  Olive Oil LIMS — Configuración inicial"
echo "========================================"

# ── PostgreSQL ───────────────────────────────────────────
echo ""
echo "[1/4] Instalando y configurando PostgreSQL..."
sudo apt-get update -qq
sudo apt-get install -y -qq postgresql postgresql-client
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER lims WITH PASSWORD 'limsdev';" 2>/dev/null || echo "  Usuario lims ya existe"
sudo -u postgres psql -c "CREATE DATABASE olive_lims OWNER lims;" 2>/dev/null || echo "  Base de datos ya existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE olive_lims TO lims;" 2>/dev/null || true
echo "  ✓ PostgreSQL listo"

# ── Python deps ──────────────────────────────────────────
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

# ── Migraciones y datos iniciales ────────────────────────
echo ""
echo "[3/4] Aplicando migraciones y cargando datos..."
alembic upgrade head
python -m app.utils.seed
echo "  ✓ Base de datos lista"

# ── Frontend deps ────────────────────────────────────────
echo ""
echo "[4/4] Instalando dependencias Node.js..."
cd /workspaces/LIMS-/frontend
npm install --silent
echo "  ✓ Dependencias frontend instaladas"

echo ""
echo "=========================================="
echo "  ✅ Setup completo!"
echo "  Los servidores arrancarán automáticamente."
echo "  Frontend → puerto 5173"
echo "  Backend  → puerto 8000"
echo "=========================================="
