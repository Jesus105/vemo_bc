#!/usr/bin/env bash
# Verifica que la carga sea completa: filas en Postgres vs filas en data/raw/manifest.csv.
# Solo valida la CARGA; la calidad de los datos se revisa en el análisis.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
C=vemo-postgres; U="${DB_USER:-postgres}"; D="${DB_NAME:-vemo}"

fail=0
printf "%-28s %8s %8s\n" tabla esperado cargado
while IFS=, read -r case sheet rows cols path; do
  [ "$case" = "case" ] && continue
  t="$case.$(echo "$sheet" | tr '[:upper:]' '[:lower:]')"
  n=$(docker exec "$C" psql -U "$U" -d "$D" -At -c "SELECT count(*) FROM $t")
  mark="OK"; [ "$n" != "$rows" ] && { mark="FALLA"; fail=1; }
  printf "%-28s %8s %8s  %s\n" "$t" "$rows" "$n" "$mark"
done < data/raw/manifest.csv
exit $fail
