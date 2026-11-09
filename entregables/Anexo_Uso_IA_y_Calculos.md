# Anexo · Cálculos y uso de IA — Business Case Growth Analyst Vemo

## Dónde están los cálculos
| Qué | Dónde |
|---|---|
| Google Sheet del anexo: tasas y modelos con fórmulas, supuestos editables (azul sobre amarillo) y pestañas de datos | https://docs.google.com/spreadsheets/d/1FK5lK3L-FRlHqhxH8Y-Vezhyul2obZITFUhgZcq9e-A/edit |
| Mismo contenido en Excel | `entregables/Vemo_Anexo_Calculos.xlsx` |
| SQL: carga fiel y vistas analíticas comentadas | [`sql/03_analytical_views.sql`](https://github.com/Jesus105/vemo_bc/blob/main/sql/03_analytical_views.sql), [`01_schema`](https://github.com/Jesus105/vemo_bc/blob/main/sql/01_schema.sql), [`02_load_data`](https://github.com/Jesus105/vemo_bc/blob/main/sql/02_load_data.sql) |
| Python: segunda vía desde los CSV crudos, modelos y exports | `analysis/vemo_model.py` → `analysis/out/metrics.json` |
| Verificación de la carga (Excel vs Postgres, celda por celda) | `scripts/verify_xlsx_vs_db.py` |
| Investigación pública (Vemo, competencia, benchmarks) | `docs/investigacion_mercado.md` |
| Deck y dashboards | `entregables/Vemo_Deck_Analisis.pdf`, `entregables/Vemo_Deck_IA.pdf`, `app/` |

Para reproducir todo: `./scripts/setup_postgres.sh` → `psql < sql/03_analytical_views.sql` → `python -I analysis/vemo_model.py` → `python -I tools/gsheets/build_vemo_sheet.py` → `node tools/pdf/build_deck_pdfs.mjs`.

## Cómo usé IA
Usé Claude Code como analista ejecutor, con estas herramientas:
- Un MCP de Postgres de solo lectura sobre los datos del caso.
- Una skill propia (`vemo-analyst`) con las reglas del caso: no confiar en los datos, cohorte vs calendario, todo en pesos y con horizonte, y segunda vía obligatoria.
- Un agente con Firecrawl para la investigación pública. No le pasé ningún dato del caso.

**Qué hizo la IA:**
- La carga de los datos.
- Las queries y las vistas.
- El script de verificación.
- El scaffold de la app y el export a PDF.

**Qué decidí yo:**
- El encuadre de cada case.
- Qué datos no creerle al reporte.
- Los supuestos de escala.
- Las recomendaciones.

### Cómo verifiqué
1. **Carga:** 32,740 celdas de las 16 hojas comparadas contra Postgres, con 0 diferencias.
2. **Cálculo:** 11 cifras clave calculadas por dos vías (vistas SQL y Python sobre los CSV). El script falla si no cuadran.
3. **Negocio:** cada número contrastado con las restricciones del caso: capacidad de Riesgo 700, CAC ≤ $10 k, meta de cobertura 92% y meta de 12% desde el mes 6.

### Dónde tuve que corregir a la IA o a la lectura ingenua
| # | Lo que salió | Cómo lo detecté | Corrección |
|---|---|---|---|
| 1 | Watts: SQL y Python difieren en $55/mes | Chequeo cruzado automático | La vista redondeaba el precio efectivo a 2 decimales. Lo documenté y dejé una tolerancia explícita. |
| 2 | Un chequeo de Conduce estaba escrito de forma que siempre pasaba (comparaba el valor consigo mismo) | Revisé el código del chequeo | Lo reemplacé por el valor que da SQL (1,531 firmas). |
| 3 | Valores del chart de margen de Watts para mayo escritos de memoria (no venían de una query) | Revisión de las cifras del deck contra la base | Los reemplacé por los valores de `watts.v_hub_mes`. |
| 4 | El componente de gráficas multiplicaba los % por 100 (salía "4610%") | Revisión visual del PDF | Corregí el formato a puntos porcentuales y los ticks del eje. |
| 5 | Retención de Hub Roma de 1% | Valor imposible frente al resto (~40%) | Excluí las 43 bajas por cierre de hub. |
| 6 | "Más bono = más retención" (34% → 43%) | El bono se paga por horas trabajadas | Controlé por banda de horas y el efecto desaparece (36.7% vs 36.8%). |
| 7 | "La promo triplicó sesiones" | 4 de 6 hubs abrieron en jun–jul | Comparé solo los hubs maduros contra un grupo control: ×1.67, y el efecto fue temporal. |
| 8 | D-04 con 14.9% de utilización | Tenía 3 de 6 conectores operativos | Recalculé sobre conectores instalados: 7.5%. |
| 9 | El modelo de Conduce topaba el resultado en la meta, lo que da un punto optimista | Análisis de sensibilidad | Presento un rango ($0.9–1.7 M) y una reserva condicionada. |
| 10 | La web de Vemo reporta 141, 400+ o 1,000+ puntos de carga, y requisitos de Impulso distintos a los del caso | Fuentes contradictorias | Decidí solo con los datos del caso. La web la usé como contexto. |

## Supuestos principales
- **Impulso:**
  - Uso tasas de cohortes cerradas (may–sep).
  - El exceso de rechazos de Riesgo, por encima de la tasa pre-agente de 15%, lo atribuyo a leads que no cumplen los requisitos mínimos.
  - Supongo que el CPL incremental cuesta +50% al escalar.
- **Conduce:**
  - Retención a 90 días calculada con firmas hasta el 6-ago.
  - El costo marginal de una firma por medios es el doble del promedio ($2,800).
  - El impacto de la propuesta se modela con una mezcla de 50% de firmas cercanas y una asistencia a inducción de 55%, con rampa de 30/65/100% y tope en la meta.
- **Watts:**
  - Descuento de 25%.
  - Volumen ×1.7.
  - Sin canibalización, un supuesto favorable a Marketing.
