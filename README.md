# Vemo · Business Case de Growth Analyst

Tres decisiones de Dirección, una por línea de negocio: **Impulso** (meta de 400 entregas), **Conduce** (retención y los $1.5 M de Q1 2027) y **Watts** (promoción en hubs destination).
Entrega: **lunes 9-nov-2026, 5 pm** · máx. 7 láminas + anexo (cálculos + uso de IA).

> Estado: **datos preparados, análisis sin empezar.**

## Por dónde empezar

| # | Documento | Para qué |
|---|---|---|
| 1 | `Business_Case_Vemo.md` (+ `Business_Case_Growth_Analyst_Vemo 2.pdf`) | El caso tal como se entregó |
| 2 | `instrucciones.md` | Correo del reclutador con entregables y fecha |
| 3 | `.claude/skills/vemo-analyst/references/` | Contexto de negocio y modelo de datos |
| 4 | `Reporte Sustentabilidad Vemo.pdf` | Contexto opcional de la empresa |

## Estructura

```
.
├── Vemo_Case{1,2,3}_*_Datos 1.xlsx   Datos originales (no se modifican)
├── data/raw/<case>/<hoja>.csv        Cada hoja exportada tal cual + manifest.csv (conteos)
├── tools/data_prep/xlsx_to_csv.py    Excel → CSV (sin limpieza)
├── docker-compose.yml                PostgreSQL 16 (puerto 5433) con data/raw montado
├── sql/                              01 schema · 02 carga · 03 vistas analíticas (vacío)
├── scripts/                          setup_postgres.sh · verify_db.sh
├── .mcp.json                         MCP postgres-vemo para Claude Code
├── .claude/skills/vemo-analyst/      Skill de análisis (SKILL.md + references/)
└── app/                              Sitio (React 19 + Vite + Tailwind) para Vercel, ver app/README.md
```

## Quickstart

Requisitos: Docker (o Colima), Python 3, Node.

```bash
# 1. (solo si cambian los Excel) regenerar los CSV
python3 -m venv tools/data_prep/.venv && tools/data_prep/.venv/bin/pip install openpyxl
tools/data_prep/.venv/bin/python -I tools/data_prep/xlsx_to_csv.py

# 2. Base de datos
./scripts/setup_postgres.sh   # levanta Postgres, crea schemas impulso/conduce/watts y carga los CSV
./scripts/verify_db.sh        # compara filas cargadas vs data/raw/manifest.csv (16 tablas)
```

Conexión: `postgresql://postgres:postgrespassword@localhost:5433/vemo` (credenciales locales de demo, ver `.env.example`).
Resetear: `docker compose down -v && ./scripts/setup_postgres.sh`.

**Carga fiel a propósito:** las tablas no tienen PK/FK/CHECK, para no rechazar ni corregir filas. Los LEEME advierten que los datos salen "tal como los exportan los sistemas"; la validación es parte del análisis y va en vistas (`sql/03_analytical_views.sql`).

## Claude Code

Abre `claude` en la raíz, aprueba `postgres-vemo` del `.mcp.json` (requiere `npx`). La skill `vemo-analyst` se carga desde `.claude/skills/`.
