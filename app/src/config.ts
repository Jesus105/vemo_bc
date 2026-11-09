// URL del Google Sheet del anexo (vista publicada o compartida). Vacío = "pendiente".
export const SHEET_URL: string = 'https://docs.google.com/spreadsheets/d/1FK5lK3L-FRlHqhxH8Y-Vezhyul2obZITFUhgZcq9e-A/edit?usp=sharing'
export const REPO_URL = 'https://github.com/Jesus105/vemo_bc'
const blob = (f: string) => `${REPO_URL}/blob/main/${f}`

// Archivos de cálculo enlazados en el anexo (rama main en GitHub)
export const SQL_FILES: { file: string; desc: string; url: string }[] = [
  { file: 'sql/03_analytical_views.sql', desc: 'Vistas de análisis por case: funnel, cohortes, CAC, retención, cobertura, margen de hubs y propuesta de Q1', url: blob('sql/03_analytical_views.sql') },
  { file: 'sql/01_schema.sql', desc: 'Tablas tal como vienen en los Excel (sin llaves para no rechazar filas)', url: blob('sql/01_schema.sql') },
  { file: 'sql/02_load_data.sql', desc: 'Carga de los CSV exportados de los Excel', url: blob('sql/02_load_data.sql') },
]
export const CODE_FILES: { file: string; desc: string; url: string }[] = [
  { file: 'analysis/vemo_model.py', desc: 'Recalcula cada cifra desde los CSV, modelos (400 entregas, Conduce, Watts) y control contra SQL', url: blob('analysis/vemo_model.py') },
  { file: 'scripts/verify_xlsx_vs_db.py', desc: 'Compara celda por celda los Excel contra la base', url: blob('scripts/verify_xlsx_vs_db.py') },
]
