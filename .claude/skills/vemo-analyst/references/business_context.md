# Contexto de negocio (del caso y de las hojas supuestos)

El enunciado completo está en `Business_Case_Vemo.md` (raíz del repo). Aquí solo está la economía que da el archivo. **No hay conclusiones todavía.**

## Impulso (case 1): arrendamiento de autos eléctricos a conductores DiDi/Uber
- Funnel: lead creado → contactado (agente IA de WhatsApp desde 1-may-2026 o asesor) → enviado a análisis → calificado (buró + riesgo) → visita aprobada → entrega (pagó depósito).
- Hoy: 120–160 entregas/mes. Meta de Dirección: **400 entregas en un mes**.
- Supuestos (`impulso.supuestos`): margen de contribución $30,000 por auto entregado (todo en el mes de entrega); CAC máx. $10,000 de medios por entrega (política de Finanzas); capacidad de Riesgo 700 análisis/mes (analista extra: $35,000/mes, +150 análisis/mes, 6 semanas para contratar y capacitar); $180 por envío a análisis; agente IA $25,000/mes; requisitos mínimos: ≥6 meses en DiDi/Uber y licencia vigente; depósito $15,000; inventario tope 450 autos/mes (hoy se piden ~150; aumentos con 60 días de anticipación).

## Conduce (case 2): conductores asalariados, 3 turnos por auto
- De cada 10 que firman, a los 3 meses quedan < 4. Hubs del sur no llenan turnos.
- Supuestos (`conduce.supuestos`): $1,100 de contribución por turno cubierto; $3,500 de inducción por firma (presupuesto operativo, fuera de los $1.5 M); sueldo fijo $3,200/semana + bono; 725 conductores activos promedio jul–sep 2026; bono promedio $480/semana; meta de cobertura 92% por hub; **presupuesto extra $1.5 M** (una vez, Q1 2027); medios actuales para el sur ~$110,000/mes (~41% del total, ~$1,400 por firma).
- Propuesta Marketing: $1.5 M en medios para el sur (~$500k extra/mes). Propuesta Operaciones: +30% de bono a todos durante 13 semanas.

## Watts (case 3): red de carga
- Hubs anchored (carga rápida) y destination. Segmentos B2C, DiDi independiente y LTO (clientes Impulso, 25% de descuento acumulable con promociones).
- Promo agosto 2026: descuento en 6 hubs destination (`watts.hubs.descuento_promo_agosto`).
- Supuestos (`watts.supuestos`): utilización = horas-conector ocupadas ÷ (conectores operativos × 24 h); meta destination 12% a partir del 6.º mes; margen de energía = ingreso − costo de energía (sin costo fijo).
- Propuesta Marketing: repetir la promo (20–30%) todo Q1 2027 en todos los destination con utilización < 10% en octubre 2026.
