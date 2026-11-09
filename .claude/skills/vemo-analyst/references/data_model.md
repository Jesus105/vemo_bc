# Modelo de datos (base `vemo`, Postgres 16 en localhost:5433)

Tablas = hojas de Excel con los mismos nombres de columna. Sin PK/FK a propósito (carga fiel, sin rechazar filas).
Origen: `data/raw/<case>/<hoja>.csv`, exportados con `tools/data_prep/xlsx_to_csv.py`. Conteos esperados en `data/raw/manifest.csv`.

| Tabla | Filas | Grano | Notas del LEEME |
|---|---:|---|---|
| impulso.funnel_mensual | 11 | mes calendario del evento (2026-01 → 2026-11) | Vista de Dirección. Cuenta eventos del mes sin importar cuándo se creó el lead (incluye leads de fines de 2025). Noviembre incompleto (extracción 4-nov). `dias_mediana_analisis` = envío → aprobación. |
| impulso.cohortes | 11 | mes de creación del lead | Avance hasta 4-nov-2026. Totales no cuadran exacto con funnel_mensual. `leads_aun_en_proceso` = ni entregados ni perdidos. |
| impulso.canales | 55 | mes de creación × canal | Referidos y Orgánico sin inversión en medios. |
| conduce.conductores | 2,245 | una fila por firma | `persona_id` se repite si recontratan. `fecha_baja` NULL = activo. Horas y bono = promedio semanal mientras estuvo activo. |
| conduce.hubs | 6 | hub | Hub Roma cerró 15-abr-2026; sus autos y conductores pasaron a Hub Centro (80 autos desde entonces). |
| conduce.cobertura_semanal | 657 | semana × hub × turno | Incluye conductores contratados antes de 2026. Primera semana y semanas de apertura/cierre tienen < 7 días. |
| conduce.funnel_mensual | 165 | mes × hub × turno | `centro_de_carga` = filtro automático (NO es carga eléctrica). |
| conduce.inversion_mensual | 55 | mes × canal | No separa por hub. Website, Otros y Sin canal no tienen inversión. |
| watts.hubs | 31 | hub | Precio público y costo de energía por kWh, costo fijo mensual, descuento de la promo de agosto. |
| watts.hub_mensual | 207 | mes × hub (2026-01 → 2026-10) | Horas disponibles = conectores_operativos_prom × 24 × días abierto. Ingreso ya neto de descuentos LTO y promo; no separa segmentos. |
| */leeme, */supuestos | — | — | `supuestos.valor` es texto; `valor_num` es numérico cuando aplica. |

Meses: texto `'YYYY-MM'`. Fechas: `DATE`.
