#!/bin/bash
set -e

export PATH="$HOME/.local/bin:$PATH"

echo "================================================"
echo "  Olive Oil LIMS — Configuración inicial"
echo "================================================"

# ── PostgreSQL (ya instalado por el feature) ──────────────
echo ""
echo "[1/4] Configurando base de datos..."
# El feature postgresql ya arrancó PostgreSQL y creó el usuario postgres
psql -U postgres -c "CREATE USER lims WITH PASSWORD 'limsdev';" 2>/dev/null || echo "  Usuario lims ya existe"
psql -U postgres -c "CREATE DATABASE olive_lims OWNER lims;" 2>/dev/null || echo "  BD ya existe"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE olive_lims TO lims;" 2>/dev/null || true
echo "  ✓ PostgreSQL listo"

# ── Python deps ───────────────────────────────────────────
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
  psycopg2-binary \
  numpy \
  scipy \
  jinja2 \
  weasyprint \
  pillow \
  python-barcode \
  qrcode
echo "  ✓ Python deps OK"

# ── Migraciones y seed ────────────────────────────────────
echo ""
echo "[3/4] Aplicando migraciones y cargando datos..."
python3 -m alembic upgrade head
python3 -m app.utils.seed
echo "  ✓ Base de datos OK"

# ── Frontend ──────────────────────────────────────────────
echo ""
echo "[4/4] Instalando dependencias Node.js..."
cd /workspaces/LIMS-/frontend
npm install --silent
echo "  ✓ Frontend deps OK"

echo ""
echo "================================================"
echo "  ✅ Setup completo — arrancando servidores..."
echo "================================================"
