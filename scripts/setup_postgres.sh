#!/usr/bin/env bash
# Levanta Postgres, crea el esquema, carga los CSV (data/raw) y crea las vistas.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
C=vemo-postgres; U="${DB_USER:-postgres}"; D="${DB_NAME:-vemo}"

echo "== Vemo · PostgreSQL setup"
if ! docker info > /dev/null 2>&1; then
  echo "Docker no está corriendo; intento con Colima..."
  colima start
fi

if [ ! -f data/raw/manifest.csv ]; then
  echo "Faltan los CSV; exportando desde los Excel..."
  tools/data_prep/.venv/bin/python -I tools/data_prep/xlsx_to_csv.py
fi

docker compose up -d
until docker exec "$C" pg_isready -U "$U" -d "$D" > /dev/null 2>&1; do sleep 1; done

for f in 01_schema 02_load_data 03_analytical_views; do
  echo "-> sql/$f.sql"
  docker exec -i "$C" psql -v ON_ERROR_STOP=1 -q -U "$U" -d "$D" -f "/sql/$f.sql" > /dev/null
done

echo "== Listo: postgresql://$U:postgrespassword@localhost:${DB_PORT:-5433}/$D"
