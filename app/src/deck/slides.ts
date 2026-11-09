import type { Slide } from '../types'

// Cifras: sql/03_analytical_views.sql (vía 1) y analysis/vemo_model.py desde CSV crudos (vía 2). Ver analysis/out/metrics.json.
const FUENTE = 'Fuente: Excel del caso (extracción 4-nov-2026) en Postgres `vemo`; vistas en sql/03_analytical_views.sql, recalculado en analysis/vemo_model.py'

export const analysisSlides: Slide[] = [
  {
    kicker: 'Resumen ejecutivo',
    title: 'Tres decisiones, tres recomendaciones',
    headline: 'Las tres propuestas atacan el síntoma visible. Los datos apuntan a otra causa en cada case.',
    table: {
      columns: ['Case', 'Recomendación', 'Impacto en pesos', 'Cuándo'],
      rows: [
        ['Impulso · 400 entregas', 'No es viable "en un mes" hoy. Primero filtrar requisitos en el agente IA y reactivar medios; luego +7 analistas, 3× leads e inventario pedido ya', '+$6.1 M/mes de margen neto al llegar a 400 (costo $2.3 M/mes)', 'Mar 2027 (feb agresivo)'],
        ['Conduce · $1.5 M', 'Ninguna de las dos. Reclutamiento hiperlocal en el sur + bono de permanencia temprana; $0.43 M en reserva condicionada', '$0.9–1.7 M de contribución en Q1 vs $1.07 M comprometido; brecha total $0.86 M/mes', 'Q1 2027'],
        ['Watts · promo Q1', 'No apruebo. Medir utilización bien, arreglar conectores, demanda cautiva de la flota Vemo y precio por horario con piso', 'Evita perder ≈ $0.19–0.25 M de margen en Q1', 'Q1 2027'],
        ['Pregunta final', 'Analizar a fondo Impulso', '$7.9 M/mes en juego vs $0.86 M y $0.07 M', 'Decidir esta semana'],
      ],
    },
    footer: FUENTE,
  },
  {
    kicker: 'Case 1 · Vemo Impulso · insights',
    title: 'El agente IA sí funciona, pero satura a Riesgo con leads que nunca califican',
    headline: 'Entregas por cohorte +69% (81 → 137/mes); el cuello hoy es Riesgo y la caída en medios, no el contacto.',
    kpis: [
      { label: 'Envíos a análisis may–oct', value: '812/mes', sub: 'capacidad 700 · 5 de 6 meses arriba', tone: 'bad' },
      { label: 'Rechazo de Riesgo', value: '15% → 50%', sub: 'de los envíos, pre vs post agente', tone: 'bad' },
      { label: 'Días de análisis', value: '3.9 → 7.9', sub: 'mediana, ene–abr vs oct', tone: 'bad' },
      { label: 'CAC medios', value: '$2.9 k', sub: 'tope Finanzas $10 k', tone: 'good' },
    ],
    chart: {
      id: 'imp-envios',
      title: 'Envíos a análisis por resultado vs capacidad de Riesgo',
      type: 'bar',
      stacked: true,
      x: ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct'],
      series: [
        { name: 'Calificados', values: [133, 147, 167, 163, 242, 299, 293, 260, 256, 235] },
        { name: 'Rechazo buró', values: [80, 87, 90, 95, 101, 128, 144, 125, 128, 121] },
        { name: 'Rechazo riesgo', values: [37, 35, 46, 54, 302, 434, 485, 448, 397, 356] },
      ],
      refLine: { value: 700, label: 'Capacidad 700' },
      note: 'Agente IA desde 1-may. Rechazo de riesgo esperado con la tasa pre-agente (15%): ~130/mes.',
    },
    bullets: [
      '**1. Arriba del funnel el agente ganó.** Contacto 62% → 80% y envíos ×2.8. Las entregas por cohorte pasaron de 81 a 137 al mes.',
      '**2. Manda ~282 leads/mes que no cumplen requisitos.** El exceso de rechazos de Riesgo cuesta $305 k (may–oct) y duplicó los días de análisis.',
      '**3. Hoy el freno es demanda.** Medios −33% jun → oct ($453 k → $304 k) y leads 2,201 → 1,613. CAC $2.9 k: margen enorme vs el tope.',
      '**4. El reporte de Dirección engaña.** Mezcla cohortes (nov: 24 entregas con 12 visitas). Además, 17% de las visitas aprobadas se pierde por el depósito de $15 k.',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Case 1 · Vemo Impulso · estrategia',
    title: '400 entregas: viable en marzo 2027, no "en un mes" desde hoy',
    headline: 'Con la conversión actual (6.7% lead → entrega) se necesitan ~6,000 leads, 823 calificados y 1,650 análisis al mes. Es 3× el volumen actual.',
    table: {
      columns: ['Palanca', 'Qué se necesita', 'Costo/mes', 'Lead time'],
      rows: [
        ['1. Filtro de requisitos en el agente IA', 'Validar ≥6 meses en app y licencia antes de enviar a análisis (envíos 812 → ~530)', '≈ $0 (ahorra $51 k)', '2 semanas'],
        ['2. Más leads', '~6,000 leads/mes; CPL marginal +50% (supuesto)', '$1.75 M medios (CAC $4.4 k)', 'Inmediato, rampa 2 meses'],
        ['3. Capacidad de Riesgo', '+7 analistas (700 → 1,750 análisis)', '$245 k + $297 k de envíos', '6 semanas'],
        ['4. Inventario', 'Pedir 400–450 autos/mes (tope 450)', '—', '60 días'],
        ['5. Depósito', 'Pagar el depósito en 2–3 partes (17% de las visitas se pierde por depósito)', 'Riesgo de cobro', '2–4 semanas'],
      ],
    },
    bullets: [
      '**Costo del mes con 400:** ≈ $2.32 M vs $12.0 M de margen; +$6.1 M/mes neto vs hoy.',
      '**Ruta:** nov: filtro + medios a nivel jun + pedido de inventario · dic: contratar analistas · ene: escalar medios · feb: ~300 · **mar: 400**.',
      '**Por qué no antes:** 60 días de inventario + 6 semanas de contratación + ~31 días de lead a entrega.',
      '**No lo sé con los datos:** el CPL real al triplicar volumen y la capacidad de visitas y entregas físicas.',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Case 2 · Vemo Conduce',
    title: 'Ni medios ni bono: el sur recluta lejos y pierde a la gente en las primeras semanas',
    headline: 'Propuesta: $1.07 M focalizados en el sur + $0.43 M de reserva por resultados. Vale $0.9–1.7 M de contribución en Q1 y ataca una brecha de $0.86 M/mes.',
    kpis: [
      { label: 'Turnos bajo meta en el sur (oct)', value: '785/mes', sub: '× $1,100 = $0.86 M/mes', tone: 'bad' },
      { label: 'Firmas del sur que viven a 10+ km', value: '80%', sub: 'vs 40% en otros hubs', tone: 'bad' },
      { label: 'Asistencia a inducción', value: '46% vs 64%', sub: 'sur vs resto', tone: 'bad' },
      { label: 'Bajas en ≤ 4 semanas', value: '55%', sub: 'antes de que el bono pese' },
    ],
    chart: {
      id: 'con-ret',
      title: 'Retención a 90 días por zona y distancia casa-hub (%)',
      type: 'bar',
      x: ['Sur <10 km', 'Sur 10+ km', 'Resto <10 km', 'Resto 10+ km'],
      series: [{ name: 'Retención 90d', values: [46.1, 30.7, 44.0, 33.9] }],
      unit: '%',
      note: 'Firmas ene–6 ago 2026 (≥90 días de observación); sin bajas por cierre de Hub Roma.',
    },
    bullets: [
      '**Marketing ($1.5 M en medios) no:** el sur ya tiene leads (Sur A 3,882 ≈ Centro 3,915). Más volumen trae más gente lejana: +179 firmas/mes requieren +$0.63 M/mes de inducción y 2 de cada 3 se van antes de 90 días.',
      '**Operaciones (+30% de bono, $1.36 M) no:** en la misma banda de horas (42–48 h), bono alto y bajo retienen igual (36.7% vs 36.8%). Además, 70% del gasto va a hubs que ya cumplen la meta.',
      '**Mi propuesta:** reclutamiento a ≤10 km ($360 k), bono de referido ($200 k), bono de permanencia en las semanas 4 y 12 ($330 k), apoyo para asistir a inducción ($180 k) y reserva de $430 k que se libera si la cobertura sube ≥3 pp en enero.',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Case 3 · Vemo Watts',
    title: 'No apruebo: el "triple" de sesiones fue rampa de hubs nuevos y se vendió debajo del costo',
    headline: 'Repetir la promo en los 12 hubs elegibles costaría ≈ $0.19 M de margen en Q1 aun con +70% de volumen; sin alza de volumen, $0.25 M.',
    kpis: [
      { label: 'Sesiones de los 6 hubs promo', value: '357 → 1,174', sub: 'jul → ago; 4 de 6 abrieron jun–jul' },
      { label: 'Alza real en hubs maduros', value: '×1.67', sub: 'control ×1.03; vuelve a base en sep' },
      { label: 'Margen de energía promo', value: '$12.7 k', sub: 'ago vs $40.3 k sep', tone: 'bad' },
      { label: 'Elegibles con <6 meses', value: '9 de 12', sub: 'la meta de 12% aplica desde el mes 6' },
    ],
    chart: {
      id: 'wat-mg',
      title: 'Margen de energía, hubs maduros de la promo (MXN)',
      type: 'bar',
      x: ['may', 'jun', 'jul', 'ago', 'sep', 'oct'],
      series: [
        { name: 'D-02 (30% desc.)', values: [1145, 1326, 1250, -2247, 1200, 1064] },
        { name: 'D-05 (30% desc.)', values: [1268, 1393, 1112, -3052, 1038, 1101] },
      ],
      note: 'Con 30% de promo + 25% LTO, el precio efectivo ($4.0/kWh) quedó debajo del costo de energía ($5.0–5.1).',
    },
    bullets: [
      '**4 de los 12 elegibles venderían bajo costo** (D-02, D-05, D-07, D-22). En los otros 8, empatar requiere ×2.3–7.4 los kWh, sostenido (la promo dio ×1.67 y se diluyó).',
      '**El corte "<10%" está mal medido:** la utilización usa conectores operativos. D-04 reporta 14.9% con 3 de 6 conectores caídos; con los instalados es 7.5%.',
      '**Qué haría:** (1) medir sobre conectores instalados y sólo hubs con ≥6 meses; (2) reparar D-04; (3) llevar a la flota Vemo (Conduce + LTO) a destination en horas valle, con precio ≥ costo + $1; (4) precio por horario con piso y A/B de 4 semanas vs control; (5) renegociar el fijo o reubicar D-02 y D-05 (spread de $1.1–1.3/kWh vs fijo de $12 k).',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Pregunta final',
    title: 'Si solo pudiera analizar uno a fondo: Impulso',
    headline: 'Es donde más pesos hay en juego, el reloj ya corre (inventario a 60 días, analistas a 6 semanas) y donde más incertidumbre queda.',
    table: {
      columns: ['', 'Impulso', 'Conduce', 'Watts'],
      rows: [
        ['En juego (contribución/mes)', '$7.9 M (263 entregas × $30 k)', '$0.86 M (785 turnos)', '≈ $0.07 M (margen de promo)'],
        ['Urgencia', 'Alta: lo que no se pida en nov no llega en ene', 'Media: el presupuesto es de Q1', 'Baja: basta con no lanzar la promo'],
        ['Lo que no sé', 'CPL al 3×, capacidad de visitas, por qué el agente deja pasar a no elegibles', 'Efecto real del bono de permanencia', 'Elasticidad por horario y canibalización'],
        ['Mientras tanto', '—', 'Arrancar el piloto sur con reserva condicionada', 'Rechazar la promo; reparar D-04; A/B por horario'],
      ],
    },
    bullets: [
      '**A fondo en Impulso:** curva de CPL por canal al escalar, capacidad de visitas y entregas, y pruebas de filtro y depósito en partes.',
      '**Conduce y Watts tienen decisión clara con riesgo acotado:** se ejecutan con métricas semanales y un gate a 4 semanas.',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Supuestos y calidad de datos',
    title: 'Qué supuse, qué corregí y qué no se puede saber',
    twoCol: {
      leftTitle: 'Supuestos y tratamiento de datos',
      left: [
        'Verifiqué 32,740 celdas: los Excel cuadran 1:1 con Postgres. 11 cifras clave cuadran entre SQL y Python.',
        'Impulso: tasas de cohortes cerradas (may–sep); oct/nov abiertas; nov calendario incompleto.',
        'Exceso de rechazos de Riesgo = rechazos arriba de la tasa pre-agente (15%) → leads que no cumplen requisitos.',
        'CPL incremental +50% al escalar (sin datos de escala).',
        'Conduce: retención a 90 días con firmas ≤6-ago; excluyo 43 bajas por cierre de Hub Roma y la semana previa a la apertura de Sur B.',
        '84 firmas "Sin canal" no existen en el funnel (por eso Centro tiene 623 vs 539).',
        'Watts: descuento 25% y volumen ×1.7 (alza de los hubs maduros); sin canibalización (supuesto favorable a Marketing).',
      ],
      rightTitle: 'No se puede saber con estos datos',
      right: [
        'Elasticidad de leads a la inversión al triplicar el gasto.',
        'Capacidad de visitas, citas y entregas físicas de Impulso.',
        'Por qué renuncian (no hay encuesta): distancia es correlación, no causa probada. El piloto con gate lo mide.',
        'El efecto causal del bono de permanencia: se mide con el piloto.',
        'Segmento (B2C, DiDi, LTO) por sesión en Watts: el ingreso viene neto y mezclado.',
        'Canibalización de la promo entre hubs cercanos.',
      ],
    },
    footer: FUENTE,
  },
]

export const aiSlides: Slide[] = [
  {
    kicker: 'Uso de IA · 1/5',
    title: 'Yo dirigí el análisis; la IA lo ejecutó y la verifiqué en cada paso',
    headline: 'Claude Code con un MCP de Postgres de solo lectura, una skill de análisis propia y búsqueda web con Firecrawl.',
    bullets: [
      '**Datos:** Excel → CSV sin limpieza → Postgres en Docker. Las tablas quedan crudas y toda limpieza va en vistas SQL comentadas.',
      '**Skill `vemo-analyst`:** reglas del caso (no confiar en los datos, cohorte vs calendario, pesos y horizonte, segunda vía obligatoria).',
      '**Investigación:** un agente con Firecrawl revisó el sitio de Vemo, el reporte de sustentabilidad y benchmarks (Moove, Kovi, churn de conductores, utilización de cargadores).',
      '**Salida única:** las mismas cifras alimentan el deck, los dashboards, el Google Sheet y el anexo.',
    ],
  },
  {
    kicker: 'Uso de IA · 2/5',
    title: 'Qué delegué y qué decidí yo',
    twoCol: {
      leftTitle: 'La IA ejecutó',
      left: [
        'Carga fiel de los 3 Excel y conteos por hoja.',
        'Queries exploratorias y vistas SQL.',
        'Script de segunda vía en Python desde los CSV.',
        'Scaffold de la app (React + Vite) y export a PDF.',
        'Búsqueda y resumen de fuentes públicas.',
      ],
      rightTitle: 'Yo decidí',
      right: [
        'Usar cohortes cerradas y no el reporte calendario.',
        'Separar hubs maduros vs nuevos en la promo de Watts.',
        'Controlar el bono por horas antes de creerle a la correlación.',
        'Excluir el cierre de Roma y la semana previa a la apertura de Sur B.',
        'Los supuestos de escala (CPL +50%, volumen ×1.7) y presentar rangos, no puntos.',
        'Recomendar "ninguna" en Conduce y "no" en Watts.',
      ],
    },
  },
  {
    kicker: 'Uso de IA · 3/5',
    title: 'Verificación: tres capas antes de que una cifra llegue al deck',
    kpis: [
      { label: 'Celdas Excel vs Postgres', value: '32,740', sub: '16 hojas · 0 diferencias', tone: 'good' },
      { label: 'Cifras SQL vs Python', value: '11/11', sub: 'calculadas por dos vías', tone: 'good' },
      { label: 'Trampas de datos tratadas', value: '8', sub: 'documentadas en el anexo' },
    ],
    bullets: [
      '**Capa 1 · carga:** cada celda del Excel se compara contra la base (números exactos, fechas, vacíos vs NULL).',
      '**Capa 2 · cálculo:** `analysis/vemo_model.py` recalcula desde los CSV crudos y falla si no cuadra con SQL (pestaña Verificación del Sheet).',
      '**Capa 3 · sentido de negocio:** cada número se contrasta con el caso (capacidad 700, CAC ≤ $10 k, meta 92%, meta 12% desde el mes 6).',
    ],
  },
  {
    kicker: 'Uso de IA · 4/5',
    title: 'Dónde tuve que corregir a la IA o a la lectura ingenua',
    table: {
      columns: ['#', 'Lo que salía', 'Cómo lo detecté', 'Corrección'],
      rows: [
        ['1', 'Watts: SQL y Python difieren en $55/mes', 'Chequeo cruzado automático', 'SQL redondeaba el precio a 2 decimales; documentado y con tolerancia explícita'],
        ['2', 'Un chequeo de Conduce era tautológico (se comparaba consigo mismo)', 'Revisé el código del check', 'Lo reemplacé por el valor de SQL (1,531 firmas)'],
        ['3', 'Retención de Hub Roma de 1%', 'Valor imposible vs el resto (~40%)', 'Excluí las 43 bajas por cierre de hub'],
        ['4', '"Más bono = más retención" (34% → 43%)', 'El bono se paga por horas', 'Controlé por horas: el efecto desaparece'],
        ['5', '"La promo triplicó sesiones"', '4 de 6 hubs abrieron en jun–jul', 'Comparé sólo hubs maduros vs control: ×1.67, temporal'],
        ['6', 'D-04 con 14.9% de utilización', 'Conectores operativos 3/6', 'Utilización sobre conectores instalados: 7.5%'],
        ['7', 'Valores de mayo de un chart escritos de memoria y % ×100 (4610%)', 'Revisión de cifras y del PDF', 'Valores tomados de la vista SQL; formato corregido'],
        ['8', 'Modelo de Conduce topado en la meta; web de Vemo contradictoria (141/400+/1,000+ puntos)', 'Sensibilidad y fuentes cruzadas', 'Presento un rango ($0.9–1.7 M); decido sólo con datos del caso'],
      ],
    },
  },
  {
    kicker: 'Uso de IA · 5/5',
    title: 'Límites y siguientes pasos',
    bullets: [
      '**La IA acelera, no decide:** acierta en SQL, pero tiende a tomar correlaciones como causa (bono) y el reporte de Dirección como verdad (calendario).',
      '**Todo es reproducible:** `setup_postgres.sh` → `03_analytical_views.sql` → `vemo_model.py` regenera los JSON, el Sheet y el deck.',
      '**Con más tiempo:** curva de CPL por canal, supervivencia (Kaplan-Meier) por hub y distancia, y diff-in-diff de Watts con más hubs control.',
      '**Lo que pediría a Vemo:** motivo de baja con encuesta, sesiones por segmento en Watts y la capacidad de visitas en Impulso.',
    ],
  },
]
