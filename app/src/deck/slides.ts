import type { Slide } from '../types'

// Cifras: sql/03_analytical_views.sql (vía 1) y analysis/vemo_model.py desde CSV crudos (vía 2). Ver analysis/out/metrics.json.
const FUENTE = 'Fuente: Excel del caso (extracción 4-nov-2026) en Postgres `vemo`; vistas en sql/03_analytical_views.sql, recalculado en analysis/vemo_model.py'

export const analysisSlides: Slide[] = [
  {
    kicker: 'Resumen ejecutivo',
    title: 'Las tres propuestas atacan el síntoma, no la causa',
    cards: [
      {
        tag: 'Impulso · ¿400 entregas en un mes?',
        title: 'Sí, pero en **marzo 2027**, no el mes que entra',
        big: '+$6.1 M/mes',
        tone: 'good',
        body: 'El agente de IA atasca a Riesgo con gente que no califica. Hay que filtrar, invertir más en anuncios y contratar analistas. Autos y analistas tardan 2 meses en llegar.',
      },
      {
        tag: 'Conduce · ¿Medios o bono?',
        title: '**Ninguna.** El sur contrata gente que vive lejos y se va en el primer mes',
        big: '$0.9–1.7 M',
        tone: 'good',
        body: 'Contratar cerca del hub y premiar quedarse el 1er y 3er mes, con parte del dinero condicionado a resultados.',
      },
      {
        tag: 'Watts · ¿Repetir la promo?',
        title: '**No.** Las sesiones subieron porque los hubs eran nuevos, y se vendió debajo del costo',
        big: '−$0.2 M',
        tone: 'bad',
        body: 'Eso costaría repetirla en Q1. Mejor: arreglar cargadores, mandar a la flota de Vemo y bajar precio solo en horas vacías.',
      },
    ],
    takeaway: 'Si solo pudiera profundizar en uno: **Impulso**. Hay **$23.7 M en juego en el trimestre** ($7.9 M al mes) y el reloj ya corre.',
    footer: FUENTE,
  },
  {
    kicker: 'Case 1 · Vemo Impulso · qué está pasando',
    title: 'El agente de IA trae más gente, pero manda a Riesgo a quien ni siquiera califica',
    chart: {
      id: 'imp-envios',
      title: 'Solicitudes enviadas a Riesgo cada mes, por resultado',
      type: 'bar',
      stacked: true,
      x: ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct'],
      series: [
        { name: 'Aprobados', values: [133, 147, 167, 163, 242, 299, 293, 260, 256, 235] },
        { name: 'Rechazo buró', values: [80, 87, 90, 95, 101, 128, 144, 125, 128, 121] },
        { name: 'Rechazo riesgo', values: [37, 35, 46, 54, 302, 434, 485, 448, 397, 356] },
      ],
      refLine: { value: 700, label: 'Riesgo puede revisar 700' },
      note: 'El agente de IA arrancó en mayo. La barra azul es lo que explotó.',
    },
    bullets: [
      '**1. Sí funciona:** las entregas pasaron de **81 a 137 al mes** desde que llegó el agente.',
      '**2. Pero filtra mal:** manda 3 veces más solicitudes (~810/mes), y Riesgo solo revisa 700. **La mitad se rechaza**, cuando antes era 15%: son personas sin los 6 meses en DiDi/Uber o sin licencia.',
      '**3. Eso cuesta:** $180 por solicitud inútil (~$50 k al mes) y la revisión tarda el doble, **de 4 a 8 días**.',
      '**4. Se recortaron anuncios:** −33% desde junio, y los leads cayeron. Cada entrega cuesta $2.9 k en anuncios contra $10 k permitidos: **hay espacio para invertir.**',
    ],
    method: 'comparé cada etapa del funnel antes y después de mayo; para las tasas usé el mes en que se creó el lead, no el mes del reporte de Dirección (que mezcla leads viejos y nuevos).',
    footer: FUENTE,
  },
  {
    kicker: 'Case 1 · Vemo Impulso · cómo llegar a 400',
    title: 'Para 400 entregas hay que triplicar el funnel, y eso es posible hasta marzo',
    chart: {
      id: 'imp-400',
      title: 'Lo que se necesita cada mes: hoy vs para 400 entregas',
      type: 'bar',
      x: ['Leads', 'Revisiones de Riesgo', 'Aprobados', 'Entregas'],
      series: [
        { name: 'Hoy (prom. may–oct)', values: [2049, 812, 264, 137] },
        { name: 'Para 400', values: [5992, 1652, 823, 400] },
      ],
      note: 'De cada 100 leads hoy se entregan ~7 autos. Esa tasa es la base del cálculo.',
    },
    bullets: [
      '**Nov:** filtrar requisitos en el agente (gratis), regresar anuncios al nivel de junio y **pedir autos** (tardan 60 días).',
      '**Dic:** contratar **7 analistas** de Riesgo (tardan 6 semanas en estar listos).',
      '**Ene–feb:** subir anuncios a ~$1.75 M/mes. Sigue debajo del tope: $4.4 k por entrega. Llegamos a ~300.',
      '**Mar 2027: 400 entregas.** Cuesta $2.3 M al mes y deja $12 M de margen: **+$6.1 M vs hoy.**',
    ],
    method: 'partí de 400 y fui hacia atrás con las tasas reales de cada etapa. Supuse que conseguir más leads cuesta 50% más caro (no hay datos de cómo sube el costo al escalar).',
    footer: FUENTE,
  },
  {
    kicker: 'Case 2 · Vemo Conduce',
    title: 'Ni más anuncios ni más bono: el sur contrata gente que vive lejos y se va en el primer mes',
    chart: {
      id: 'con-ret',
      title: 'De cada 100 conductores que firman, ¿cuántos siguen a los 3 meses?',
      type: 'bar',
      x: ['Sur · vive a <10 km', 'Sur · vive a 10+ km', 'Otros hubs · <10 km', 'Otros hubs · 10+ km'],
      series: [{ name: 'Siguen a los 90 días', values: [46.1, 30.7, 44.0, 33.9] }],
      unit: '%',
      note: 'En el sur, 8 de cada 10 contratados viven a más de 10 km (en otros hubs, 4 de cada 10).',
    },
    bullets: [
      '**Marketing dice "no nos conocen":** falso. El sur recibe **tantas solicitudes como Centro** (3,882 vs 3,915). El problema es que solo la mitad llega a la inducción y quienes firman viven lejos.',
      '**Operaciones dice "ganan poco":** entre conductores que trabajan **las mismas horas**, los de bono alto y los de bono bajo se quedan igual (**37% vs 37%**). Además, **55% se va en el primer mes**, antes de que el bono importe.',
      '**El costo:** el sur deja **785 turnos vacíos al mes** = $0.86 M de contribución perdida.',
    ],
    takeaway: 'Usar los $1.5 M en el sur: anuncios solo a ≤10 km del hub, bono de referido y **bono por quedarse** en la semana 4 y 12 ($1.07 M). Los otros $0.43 M se liberan solo si en enero la cobertura sube. Vale **$0.9–1.7 M en Q1**.',
    method: 'retención a 90 días de quienes firmaron hasta agosto, cruzada por distancia casa-hub, turno y horas trabajadas (el bono se paga por horas, por eso comparé con las mismas horas).',
    footer: FUENTE,
  },
  {
    kicker: 'Case 3 · Vemo Watts',
    title: 'La promo no funcionó: las sesiones subieron porque los hubs eran nuevos, y cada carga se vendió con pérdida',
    chart: {
      id: 'wat-mg',
      title: 'Ganancia por energía en los 2 hubs viejos de la promo (MXN al mes)',
      type: 'bar',
      x: ['may', 'jun', 'jul', 'ago (promo)', 'sep', 'oct'],
      series: [
        { name: 'D-02', values: [1145, 1326, 1250, -2247, 1200, 1064] },
        { name: 'D-05', values: [1268, 1393, 1112, -3052, 1038, 1101] },
      ],
      note: 'Promo 30% + descuento de clientes Impulso 25% = cobramos $4.0 por kWh que nos cuesta $5.0.',
    },
    bullets: [
      '**"Se triplicaron" es engañoso:** 4 de los 6 hubs llevaban 1–2 meses abiertos, así que iban a crecer de todos modos.',
      '**En los 2 hubs viejos** las sesiones subieron 67% en agosto y **en septiembre regresaron** a lo de siempre.',
      '**Repetirla en Q1** (12 hubs) costaría **~$195 k** de ganancia. 9 de esos hubs tienen menos de 6 meses: todavía no deberían medirse contra la meta.',
      '**La medición falla:** D-04 tiene la mitad de sus cargadores descompuestos y por eso parece usado al 15%; en realidad está al 7.5%.',
    ],
    takeaway: '**No aprobar.** Arreglar cargadores, mandar a la flota de Vemo (Conduce e Impulso) a estos hubs en horas vacías y bajar precio solo en esas horas, nunca debajo del costo. Probarlo 4 semanas contra hubs sin cambio.',
    method: 'comparé los hubs con promo contra hubs similares sin promo, separando los que ya tenían más de 6 meses de los recién abiertos.',
    footer: FUENTE,
  },
  {
    kicker: 'Pregunta final',
    title: 'Si solo pudiera analizar uno a fondo: Impulso',
    chart: {
      id: 'fin-stakes',
      title: 'Dinero en juego en un trimestre (MXN millones)',
      type: 'hbar',
      x: ['Impulso', 'Conduce', 'Watts'],
      series: [{ name: 'En juego', values: [23.7, 2.6, 0.19] }],
      note: 'Impulso: 263 entregas faltantes × $30 k × 3 meses. Conduce: 785 turnos vacíos × $1,100 × 3. Watts: margen que se perdería con la promo en Q1.',
    },
    bullets: [
      '**Más dinero:** faltan 263 entregas al mes para 400, a $30 k cada una: **$23.7 M en el trimestre**, 9 veces lo de Conduce.',
      '**Más urgente:** lo que no se pida en noviembre (autos, analistas) no llega en enero.',
      '**Más incertidumbre:** no sé cuánto sube el costo de los anuncios al triplicar, ni si alcanza la capacidad de visitas y entregas.',
      '**Mientras tanto:** en Conduce arrancar el piloto del sur con el dinero condicionado; en Watts no lanzar la promo y reparar D-04.',
    ],
    footer: FUENTE,
  },
  {
    kicker: 'Cómo hice el análisis',
    title: 'Cuatro pasos antes de creerle a cualquier número',
    cards: [
      { tag: 'Paso 1', title: 'Revisar que los datos estén completos', body: 'Cargué los 3 Excel tal cual a una base SQL y comparé **celda por celda** (32,740) contra el original: 0 diferencias. Luego busqué trampas: hubs cerrados, semanas incompletas, meses abiertos.' },
      { tag: 'Paso 2', title: 'No creerle al número "bonito"', body: 'Separé lo que se ve en el reporte de lo que realmente pasó: **cohortes** en Impulso, **mismas horas** en Conduce, **hubs viejos vs nuevos** en Watts.' },
      { tag: 'Paso 3', title: 'Pasarlo a pesos', body: 'Cada recomendación con costo, beneficio y mes, usando la economía que dio Vemo. Cuando faltó un dato, escribí el supuesto (p. ej. +50% en costo de anuncios).' },
      { tag: 'Paso 4', title: 'Calcular todo dos veces', body: 'Cada cifra del deck sale igual en **SQL, Python y el Google Sheet**. El Sheet tiene las fórmulas y los supuestos editables.' },
    ],
    takeawayLabel: 'Lo que no se puede saber',
    takeaway: 'Con estos datos no se sabe cuánto sube el costo de los anuncios al escalar, **por qué** renuncian los conductores (no hay encuesta) y cuánto le quita una promo a otros hubs.',
    footer: 'SQL: github.com/Jesus105/vemo_bc · Cálculos: Google Sheet del anexo · Detalle paso a paso: docs/BRIEF_PROYECTO.md',
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
      '**Capa 2 · cálculo:** `analysis/vemo_model.py` recalcula desde los CSV crudos y falla si no cuadra con SQL (pestaña "Control de cifras" del Sheet).',
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
