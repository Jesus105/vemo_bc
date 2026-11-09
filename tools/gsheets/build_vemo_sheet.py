"""Construye el anexo de cálculos (Google Sheet + xlsx) con fórmulas, inputs editables y formato.

Lee los CSV crudos (data/raw) y analysis/out/metrics.json (correr antes analysis/vemo_model.py).
Convención: celdas azules sobre amarillo = supuestos editables; negro = fórmula o dato.

  VEMO_SHEET_ID=<id> ../Clara_DA_BusinessCase/tools/gsheets/.venv/bin/python -I tools/gsheets/build_vemo_sheet.py
Sin VEMO_SHEET_ID solo escribe entregables/Vemo_Anexo_Calculos.xlsx. Se puede correr las veces que sea.
"""
import csv, datetime as dt, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
M = json.loads((ROOT / "analysis" / "out" / "metrics.json").read_text(encoding="utf-8"))

def rd(case, sheet):
    with open(RAW / case / f"{sheet}.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))
def n(x):
    if x in ("", None): return ""
    v = float(x); return int(v) if v.is_integer() else v
def d(s):
    return dt.date.fromisoformat(s) if s else ""
def md(s):  # "2026-05" -> fecha 1-may-2026 (los meses van como fechas reales)
    return dt.date(int(s[:4]), int(s[5:7]), 1)
def DT(s):
    return f"DATE({int(s[:4])},{int(s[5:7])},1)"
def col(i):  # 0 -> A
    s = ""
    i += 1
    while i: i, r = divmod(i - 1, 26); s = chr(65 + r) + s
    return s

# ---------------------------------------------------------------- modelo de pestaña
FMT = {"int": "#,##0", "mxn": "$#,##0", "mxn2": "$#,##0.00", "pct": "0.0%", "dec": "0.0", "date": "yyyy-mm-dd", "x": '0.0"×"', "mon": "mmm yyyy"}
NAVY, TEAL, INPUT_BG, INPUT_FG, GRAY, BAND = "1F2A37", "0F7A5F", "FFF4CC", "1D4ED8", "6B7280", "F4F6F8"

class Tab:
    def __init__(self, title, color, freeze=0, gridlines=True):
        self.title, self.color, self.freeze, self.gridlines = title, color, freeze, gridlines
        self.cells = {}          # (r, c) -> valor
        self.fmt = []            # (r1, c1, r2, c2, numfmt)
        self.styles = []         # (r1, c1, r2, c2, dict)
        self.widths = {}
        self.bands = []          # (r1, c1, r2, c2)
        self.r = 0
    def put(self, r, c, v): self.cells[(r, c)] = v
    def heading(self, text, sub=None):
        self.put(self.r, 0, text); self.styles.append((self.r, 0, self.r, 0, {"bold": True, "size": 14, "fg": NAVY})); self.r += 1
        if sub:
            self.put(self.r, 0, sub); self.styles.append((self.r, 0, self.r, 0, {"italic": True, "fg": GRAY})); self.r += 1
        self.r += 1
    def section(self, text):
        self.put(self.r, 0, text); self.styles.append((self.r, 0, self.r, 0, {"bold": True, "size": 11, "fg": TEAL})); self.r += 1
    def table(self, header, rows, fmts=None, total=None, c0=0):
        """rows: listas de valores; '{r}' en una fórmula se reemplaza por el número de fila (1-based)."""
        top = self.r
        for j, h in enumerate(header): self.put(top, c0 + j, h)
        self.styles.append((top, c0, top, c0 + len(header) - 1, {"bold": True, "bg": NAVY, "fg": "FFFFFF", "wrap": True}))
        for i, row in enumerate(rows):
            rr = top + 1 + i
            for j, v in enumerate(row):
                if isinstance(v, str) and "{r}" in v: v = v.replace("{r}", str(rr + 1))
                self.put(rr, c0 + j, v)
        last = top + len(rows)
        if rows: self.bands.append((top + 1, c0, last, c0 + len(header) - 1))
        for j, f in enumerate(fmts or []):
            if f and rows: self.fmt.append((top + 1, c0 + j, last + (1 if total else 0), c0 + j, FMT[f]))
        if total:
            tr = last + 1
            for j, v in enumerate(total):
                if isinstance(v, str): v = v.replace("{first}", str(top + 2)).replace("{last}", str(last + 1))
                if v != "": self.put(tr, c0 + j, v)
            self.styles.append((tr, c0, tr, c0 + len(header) - 1, {"bold": True, "top": True}))
            last = tr
        self.r = last + 2
        return top + 2, last + 1   # filas 1-based de datos (primera, última)
    def kv(self, rows):
        """Bloque etiqueta / valor / nota. rows: (etiqueta, valor, fmt, es_input, nota). Devuelve {etiqueta: 'B7'}."""
        ref = {}
        for lab, val, f, is_in, note in rows:
            if lab is None: self.r += 1; continue
            self.put(self.r, 0, lab); self.put(self.r, 1, val)
            if note: self.put(self.r, 2, note); self.styles.append((self.r, 2, self.r, 2, {"italic": True, "fg": GRAY}))
            if f: self.fmt.append((self.r, 1, self.r, 1, FMT[f]))
            if is_in: self.styles.append((self.r, 1, self.r, 1, {"bg": INPUT_BG, "fg": INPUT_FG}))
            ref[lab] = f"B{self.r + 1}"; self.r += 1
        self.r += 1
        return ref
    def bold_cell(self, r, c): self.styles.append((r, c, r, c, {"bold": True}))

tabs = []

# ---------------------------------------------------------------- RESUMEN
imp, con, wat = M["impulso"], M["conduce"], M["watts"]
t = Tab("Resumen", "1F2A37", gridlines=False); tabs.append(t)
t.heading("Vemo · Business Case Growth Analyst — Anexo de cálculos",
          "Datos del caso con extracción al 4-nov-2026. Celdas azules sobre amarillo = supuestos que se pueden modificar.")
t.section("Recomendación por case")
t.table(["Case", "Decisión", "Recomendación", "Impacto"], [
    ["Impulso", "Meta de 400 entregas en un mes", "No es viable el próximo mes; realista en marzo 2027. Filtro de requisitos en el agente, reactivar medios, +7 analistas, ~6,000 leads/mes, pedir inventario ya.", "Margen neto de +$6.1 M/mes en el mes de 400"],
    ["Conduce", "$1.5 M adicionales Q1 2027", "Ninguna de las dos propuestas. Reclutamiento cercano al hub en el sur + bono de permanencia en semanas 4 y 12; $0.43 M en reserva condicionada.", "$0.9–1.7 M de contribución en Q1"],
    ["Watts", "Repetir la promo en destination <10%", "No. Medir utilización con conectores instalados, reparar D-04, llevar flota Vemo en horas valle y precio por horario con piso.", "Evita perder $0.19–0.25 M en Q1"],
])
t.section("Pestañas")
t.table(["Pestaña", "Qué contiene"], [
    ["Impulso · Funnel", "Funnel mensual de Dirección con tasas por etapa y saturación de Riesgo"],
    ["Impulso · Cohortes", "Funnel por mes de creación del lead (base de las tasas del modelo)"],
    ["Impulso · Canales", "CPL y CAC por canal, cohortes may–sep (SUMIFS sobre los datos por mes)"],
    ["Impulso · Meta 400", "Modelo de lo que se necesita para 400 entregas; supuestos editables"],
    ["Conduce · Retención", "Retención a 90 días por zona, distancia, turno y horas (COUNTIFS sobre las firmas)"],
    ["Conduce · Cobertura", "Cobertura de turnos por hub y mes, y brecha contra la meta de 92%"],
    ["Conduce · Propuesta", "Comparación de las 3 opciones y presupuesto de la propuesta"],
    ["Watts · Promo agosto", "Sesiones y margen de los 6 hubs de la promo antes, durante y después"],
    ["Watts · Propuesta Q1", "Hubs que entrarían y su margen con descuento; supuestos editables"],
    ["Supuestos del caso", "Economía de cada línea tal como viene en los archivos"],
    ["Calidad de datos", "Problemas encontrados en los datos y cómo se trataron"],
    ["Control de cifras", "Cifras clave calculadas en SQL y en Python, lado a lado"],
    ["Datos · …", "Tablas originales usadas por las fórmulas"],
])
t.widths = {0: 170, 1: 230, 2: 560, 3: 260}

# ---------------------------------------------------------------- IMPULSO · FUNNEL
fm = rd("impulso", "funnel_mensual")
t = Tab("Impulso · Funnel", "0F7A5F", freeze=4); tabs.append(t)
t.heading("Impulso · Funnel mensual (vista de Dirección)", "Eventos del mes calendario. Noviembre incompleto (corte 4-nov). Agente IA desde mayo.")
rows = []
for r in fm:
    rows.append([md(r["mes"]), n(r["leads_creados"]), n(r["contactados"]), n(r["contactados_por_agente_ia"]), n(r["enviados_a_analisis"]),
                 n(r["rechazados_buro"]), n(r["rechazados_riesgo"]), n(r["calificados"]), n(r["visitas_aprobadas"]), n(r["entregas"]), n(r["dias_mediana_analisis"]),
                 "=C{r}/B{r}", "=E{r}/C{r}", "=H{r}/E{r}", "=G{r}/E{r}", "=E{r}-700", "=J{r}/B{r}"])
t.table(["Mes", "Leads", "Contactados", "Contactados por IA", "Enviados a análisis", "Rechazo buró", "Rechazo riesgo", "Calificados", "Visitas aprobadas", "Entregas", "Días de análisis (mediana)",
         "% contacto", "% enviados", "% aprobación", "% rechazo riesgo", "Envíos vs capacidad (700)", "Lead → entrega"], rows,
        ["mon", "int", "int", "int", "int", "int", "int", "int", "int", "int", "dec", "pct", "pct", "pct", "pct", "int", "pct"])
t.widths = {0: 80, **{i: 95 for i in range(1, 17)}}

# ---------------------------------------------------------------- IMPULSO · COHORTES
coh = rd("impulso", "cohortes")
t = Tab("Impulso · Cohortes", "0F7A5F", freeze=4); tabs.append(t)
t.heading("Impulso · Funnel por cohorte de creación", "Avance al 4-nov-2026. Oct y nov siguen abiertas: no se usan para tasas.")
rows = [[md(r["mes_creacion"]), n(r["leads"]), n(r["contactados"]), n(r["enviados_a_analisis"]), n(r["calificados"]), n(r["visitas_aprobadas"]),
         n(r["perdidos_en_visita_por_deposito"]), n(r["perdidos_en_visita_otros_motivos"]), n(r["entregas_acumuladas"]), n(r["dias_mediana_lead_a_entrega"]), n(r["leads_aun_en_proceso"]),
         "=IFERROR(I{r}/B{r},\"\")", "=IFERROR(E{r}/D{r},\"\")", "=IFERROR(I{r}/E{r},\"\")", "=IFERROR(G{r}/F{r},\"\")"] for r in coh]
f1, l1 = t.table(["Mes de creación", "Leads", "Contactados", "Enviados a análisis", "Calificados", "Visitas aprobadas", "Perdidos por depósito", "Perdidos otros motivos",
                  "Entregas", "Días lead → entrega", "Aún en proceso", "Lead → entrega", "% aprobación", "Calificado → entrega", "% visitas perdidas por depósito"], rows,
                 ["mon", "int", "int", "int", "int", "int", "int", "int", "int", "dec", "int", "pct", "pct", "pct", "pct"])
t.section("Cohortes cerradas: antes vs con agente IA")
pre = f"A{f1}:A{l1}"
t.table(["Periodo", "Entregas por mes", "Lead → entrega", "Calificado → entrega", "% perdidos por depósito"], [
    ["Ene–abr (asesores)", f'=AVERAGEIFS(I{f1}:I{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))', f'=SUMIFS(I{f1}:I{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))/SUMIFS(B{f1}:B{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))',
     f'=SUMIFS(I{f1}:I{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))/SUMIFS(E{f1}:E{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))', f'=SUMIFS(G{f1}:G{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))/SUMIFS(F{f1}:F{l1},A{f1}:A{l1},"<"&DATE(2026,5,1))'],
    ["May–sep (agente IA)", f'=AVERAGEIFS(I{f1}:I{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))',
     f'=SUMIFS(I{f1}:I{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))/SUMIFS(B{f1}:B{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))',
     f'=SUMIFS(I{f1}:I{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))/SUMIFS(E{f1}:E{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))',
     f'=SUMIFS(G{f1}:G{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))/SUMIFS(F{f1}:F{l1},A{f1}:A{l1},">="&DATE(2026,5,1),A{f1}:A{l1},"<="&DATE(2026,9,1))'],
], ["", "dec", "pct", "pct", "pct"])
COH_POST = (f1, l1)
t.widths = {0: 150, **{i: 100 for i in range(1, 15)}}

# ---------------------------------------------------------------- DATOS · CANALES + IMPULSO · CANALES
can = rd("impulso", "canales")
dc = Tab("Datos · Canales Impulso", "9CA3AF", freeze=1)
dc.r = 0
cf, cl = dc.table(["Mes de creación", "Canal", "Inversión", "Leads", "Calificados", "Entregas"],
                  [[md(r["mes_creacion"]), r["canal"], n(r["inversion_mxn"]), n(r["leads"]), n(r["calificados"]), n(r["entregas_acumuladas"])] for r in can],
                  ["mon", "", "mxn", "int", "int", "int"])
dc.widths = {0: 120, 1: 100, 2: 110, 3: 80, 4: 90, 5: 80}
t = Tab("Impulso · Canales", "0F7A5F", freeze=0); tabs.append(t)
t.heading("Impulso · Costo por canal (cohortes may–sep)", "Inversión ÷ entregas de la cohorte. Tope de Finanzas: $10,000 por entrega.")
D = "'Datos · Canales Impulso'!"
crit = f'{D}$A${cf}:$A${cl},">="&DATE(2026,5,1),{D}$A${cf}:$A${cl},"<="&DATE(2026,9,1)'
rows = [[ch, f'=SUMIFS({D}$C${cf}:$C${cl},{D}$B${cf}:$B${cl},A{{r}},{crit})', f'=SUMIFS({D}$D${cf}:$D${cl},{D}$B${cf}:$B${cl},A{{r}},{crit})',
         f'=SUMIFS({D}$F${cf}:$F${cl},{D}$B${cf}:$B${cl},A{{r}},{crit})', '=IFERROR(B{r}/C{r},0)', '=IFERROR(B{r}/D{r},0)', "=D{r}/C{r}"]
        for ch in ("Meta", "Google", "TikTok", "Referidos", "Orgánico")]
a, b = t.table(["Canal", "Inversión", "Leads", "Entregas", "CPL", "CAC", "Lead → entrega"], rows, ["", "mxn", "int", "int", "mxn", "mxn", "pct"],
               total=["Total", "=SUM(B{first}:B{last})", "=SUM(C{first}:C{last})", "=SUM(D{first}:D{last})", "=B{last1}/C{last1}", "=B{last1}/D{last1}", "=D{last1}/C{last1}"])
for (rr, cc), v in list(t.cells.items()):
    if isinstance(v, str) and "{last1}" in v: t.cells[(rr, cc)] = v.replace("{last1}", str(b))
CAN_TOTAL_ROW = b
t.section("Inversión mensual en medios")
meses = sorted({r["mes_creacion"] for r in can})
t.table(["Mes", "Inversión", "Leads (todos los canales)"], [[m, f'=SUMIFS({D}$C${cf}:$C${cl},{D}$A${cf}:$A${cl},A{{r}})', f'=SUMIFS({D}$D${cf}:$D${cl},{D}$A${cf}:$A${cl},A{{r}})'] for m in [md(x) for x in meses]], ["mon", "mxn", "int"])
t.widths = {0: 120, 1: 120, 2: 110, 3: 90, 4: 90, 5: 90, 6: 110}

# ---------------------------------------------------------------- IMPULSO · META 400
t = Tab("Impulso · Meta 400", "0F7A5F", gridlines=False); tabs.append(t)
t.heading("Impulso · ¿Qué se necesita para 400 entregas en un mes?", "Tasas de cohortes cerradas may–sep. Cambia los supuestos en amarillo y el modelo se recalcula.")
t.section("Supuestos")
fC, lC = COH_POST
CO = "'Impulso · Cohortes'!"
FU = "'Impulso · Funnel'!"
R = t.kv([
    ("Meta de entregas", 400, "int", True, "Objetivo de Dirección"),
    ("Lead → entrega", f'=SUMIFS({CO}I{fC}:I{lC},{CO}A{fC}:A{lC},">="&DATE(2026,5,1),{CO}A{fC}:A{lC},"<="&DATE(2026,9,1))/SUMIFS({CO}B{fC}:B{lC},{CO}A{fC}:A{lC},">="&DATE(2026,5,1),{CO}A{fC}:A{lC},"<="&DATE(2026,9,1))', "pct", False, "Cohortes may–sep"),
    ("Calificado → entrega", f'=SUMIFS({CO}I{fC}:I{lC},{CO}A{fC}:A{lC},">="&DATE(2026,5,1),{CO}A{fC}:A{lC},"<="&DATE(2026,9,1))/SUMIFS({CO}E{fC}:E{lC},{CO}A{fC}:A{lC},">="&DATE(2026,5,1),{CO}A{fC}:A{lC},"<="&DATE(2026,9,1))', "pct", False, "Cohortes may–sep"),
    ("Aprobación con filtro de requisitos", round(imp["aprob_filtro"], 4), "pct", True, "Calificados ÷ (envíos − exceso de rechazos de riesgo), may–oct"),
    ("Capacidad actual de Riesgo", 700, "int", True, "Análisis por mes"),
    ("Análisis por analista adicional", 150, "int", True, "6 semanas para contratar y capacitar"),
    ("Costo por analista", 35000, "mxn", True, "Mensual"),
    ("Costo por envío a análisis", 180, "mxn", True, "Buró + tiempo del analista"),
    ("Agente de IA", 25000, "mxn", True, "Mensual"),
    ("CPL pagado actual", round(imp["cpl_paid"], 2), "mxn2", True, "Meta + Google + TikTok, may–sep"),
    ("Leads pagados actuales por mes", round(imp["paid_leads_now"]), "int", True, "Promedio may–sep"),
    ("Leads sin costo por mes", round(imp["leads_need"] - imp["paid_leads_need"]), "int", True, "Orgánico + referidos"),
    ("Encarecimiento del CPL incremental", 1.5, "x", True, "Supuesto: sin datos de cómo cambia el CPL al escalar"),
    ("Margen por auto entregado", 30000, "mxn", True, "Contado completo en el mes de entrega"),
    ("Entregas por mes hoy (cohortes may–sep)", round(imp["ent_coh_post"], 1), "dec", True, "Base de comparación"),
    ("Costo mensual de medios hoy", round(imp["cpl_paid"] * imp["paid_leads_now"]), "mxn", True, "Promedio may–sep"),
    ("Envíos a análisis hoy", round(imp["envios_post_avg"]), "int", True, "Promedio may–oct"),
])
t.section("Volumen necesario")
o = t.kv([
    ("Leads necesarios", f"={R['Meta de entregas']}/{R['Lead → entrega']}", "int", False, ""),
    ("Calificados necesarios", f"={R['Meta de entregas']}/{R['Calificado → entrega']}", "int", False, ""),
    ("Análisis necesarios", None, "int", False, ""),
])
t.put(int(o["Análisis necesarios"][1:]) - 1, 1, f"={o['Calificados necesarios']}/{R['Aprobación con filtro de requisitos']}")
t.r -= 1
o2 = t.kv([
    ("Analistas adicionales", f"=MAX(0,ROUNDUP(({o['Análisis necesarios']}-{R['Capacidad actual de Riesgo']})/{R['Análisis por analista adicional']},0))", "int", False, ""),
    ("Leads pagados necesarios", f"={o['Leads necesarios']}-{R['Leads sin costo por mes']}", "int", False, ""),
])
t.r -= 1
t.section("Costo del mes")
c = t.kv([
    ("Medios", f"={R['Leads pagados actuales por mes']}*{R['CPL pagado actual']}+({o2['Leads pagados necesarios']}-{R['Leads pagados actuales por mes']})*{R['CPL pagado actual']}*{R['Encarecimiento del CPL incremental']}", "mxn", False, ""),
    ("Analistas", f"={o2['Analistas adicionales']}*{R['Costo por analista']}", "mxn", False, ""),
    ("Envíos a análisis", f"={o['Análisis necesarios']}*{R['Costo por envío a análisis']}", "mxn", False, ""),
    ("Agente de IA", f"={R['Agente de IA']}", "mxn", False, ""),
])
t.r -= 1
t.section("Margen")
tot = t.kv([
    ("Costo total del mes", f"=SUM({c['Medios']}:{c['Agente de IA']})", "mxn", False, ""),
    ("CAC de medios", f"={c['Medios']}/{R['Meta de entregas']}", "mxn", False, "Tope de Finanzas: $10,000"),
    ("Margen de contribución", f"={R['Meta de entregas']}*{R['Margen por auto entregado']}", "mxn", False, ""),
    ("Margen neto del mes", None, "mxn", False, ""),
    ("Margen neto hoy", f"={R['Entregas por mes hoy (cohortes may–sep)']}*{R['Margen por auto entregado']}-{R['Costo mensual de medios hoy']}-{R['Envíos a análisis hoy']}*{R['Costo por envío a análisis']}-{R['Agente de IA']}", "mxn", False, ""),
    ("Margen incremental vs hoy", None, "mxn", False, ""),
])
t.put(int(tot["Margen neto del mes"][1:]) - 1, 1, f"={tot['Margen de contribución']}-{tot['Costo total del mes']}")
t.put(int(tot["Margen incremental vs hoy"][1:]) - 1, 1, f"={tot['Margen neto del mes']}-{tot['Margen neto hoy']}")
for k in ("Costo total del mes", "Margen incremental vs hoy"):
    rr = int(tot[k][1:]) - 1; t.bold_cell(rr, 0); t.bold_cell(rr, 1)
t.section("Calendario")
t.table(["Cuándo", "Acción", "Por qué ahí"], [
    ["Nov 2026", "Filtro de requisitos en el agente; medios a nivel de junio; pedido de inventario", "Inventario requiere 60 días"],
    ["Dic 2026", "Contratar analistas", "6 semanas para contratar y capacitar"],
    ["Ene 2027", "Escalar medios por canal midiendo el CPL", "Los analistas ya están listos"],
    ["Feb 2027", "~300 entregas", "~31 días de lead a entrega"],
    ["Mar 2027", "400 entregas", "Todo el sistema a capacidad"],
])
IMP_REFS = {"leads": o["Leads necesarios"], "analistas": o2["Analistas adicionales"], "costo": tot["Costo total del mes"], "incremental": tot["Margen incremental vs hoy"], "cac": tot["CAC de medios"]}
t.widths = {0: 290, 1: 150, 2: 420}

# ---------------------------------------------------------------- DATOS · FIRMAS + CONDUCE · RETENCIÓN
cond = rd("conduce", "conductores")
df = Tab("Datos · Firmas Conduce", "9CA3AF", freeze=1)
rows = []
for r in cond:
    rows.append([r["conductor_id"], r["persona_id"], d(r["fecha_firma"]), r["hub"], r["turno"], r["canal"], n(r["distancia_casa_hub_km"]), n(r["horas_semanales_prom"]),
                 n(r["bono_semanal_prom_mxn"]), d(r["fecha_baja"]), r["motivo_baja"],
                 '=IF(LEFT(D{r},7)="Hub Sur","Sur","Resto")', '=IF(G{r}<10,"<10 km","10+ km")',
                 '=IF(AND(C{r}<=DATE(2026,8,6),K{r}<>"Cierre de hub"),1,0)', '=IF(OR(J{r}="",J{r}-C{r}>90),1,0)',
                 '=IF(H{r}<36,"<36 h",IF(H{r}<42,"36–42 h",IF(H{r}<48,"42–48 h","48+ h")))', '=IF(J{r}="","",IF(J{r}-C{r}<=30,1,0))'])
ff, fl = df.table(["Conductor", "Persona", "Fecha de firma", "Hub", "Turno", "Canal", "Distancia casa-hub (km)", "Horas semanales", "Bono semanal", "Fecha de baja", "Motivo de baja",
                   "Zona", "Banda de distancia", "Cuenta para retención", "Sigue a 90 días", "Banda de horas", "Baja en ≤4 semanas"], rows,
                  ["", "", "date", "", "", "", "dec", "dec", "mxn", "date", "", "", "", "int", "int", "", "int"])
df.widths = {i: 105 for i in range(17)}
t = Tab("Conduce · Retención", "B45309", gridlines=False); tabs.append(t)
t.heading("Conduce · Retención a 90 días", "Firmas del 1-ene al 6-ago-2026 (con 90 días de observación). Sin las 43 bajas por cierre de Hub Roma.")
F = "'Datos · Firmas Conduce'!"
rng = lambda c_: f"{F}${c_}${ff}:${c_}${fl}"
def ret_row(label, cond_pairs):
    cc = ",".join(f'{rng(c_)},"{v}"' for c_, v in cond_pairs)
    base = f"{rng('N')},1" + ("," + cc if cc else "")
    return [label, f"=COUNTIFS({base})", f"=COUNTIFS({base},{rng('O')},1)/B{{r}}"]
t.section("Por zona y distancia de la casa al hub")
t.table(["Segmento", "Firmas", "Retención 90 días"], [
    ret_row("Total", []),
    ret_row("Sur · <10 km", [("L", "Sur"), ("M", "<10 km")]), ret_row("Sur · 10+ km", [("L", "Sur"), ("M", "10+ km")]),
    ret_row("Resto · <10 km", [("L", "Resto"), ("M", "<10 km")]), ret_row("Resto · 10+ km", [("L", "Resto"), ("M", "10+ km")]),
], ["", "int", "pct"])
t.section("% de firmas que viven a 10+ km del hub")
t.table(["Zona", "Firmas", "A 10+ km", "%"], [
    [z, f'=COUNTIFS({rng("L")},"{z}")', f'=COUNTIFS({rng("L")},"{z}",{rng("M")},"10+ km")', "=C{r}/B{r}"] for z in ("Sur", "Resto")], ["", "int", "int", "pct"])
t.section("Por turno")
t.table(["Turno", "Firmas", "Retención 90 días"], [ret_row(tu, [("E", tu + "*")]) for tu in ("Mañana", "Tarde", "Noche")], ["", "int", "pct"])
t.section("Por horas semanales (el bono se paga por horas)")
t.table(["Horas", "Firmas", "Retención 90 días", "Bono semanal promedio"],
        [ret_row(h, [("P", h)]) + [f'=AVERAGEIFS({rng("I")},{rng("N")},1,{rng("P")},"{h}")'] for h in ("<36 h", "36–42 h", "42–48 h", "48+ h")], ["", "int", "pct", "mxn"])
t.section("Mismas horas (42–48 h), distinto bono")
med = "MEDIAN(FILTER({I},{N}=1,{P}=\"42–48 h\"))".format(I=rng("I"), N=rng("N"), P=rng("P"))
t.table(["Grupo", "Firmas", "Retención 90 días"], [
    ["Bono ≥ mediana", f'=COUNTIFS({rng("N")},1,{rng("P")},"42–48 h",{rng("I")},">="&{med})', f'=COUNTIFS({rng("N")},1,{rng("P")},"42–48 h",{rng("I")},">="&{med},{rng("O")},1)/B{{r}}'],
    ["Bono < mediana", f'=COUNTIFS({rng("N")},1,{rng("P")},"42–48 h",{rng("I")},"<"&{med})', f'=COUNTIFS({rng("N")},1,{rng("P")},"42–48 h",{rng("I")},"<"&{med},{rng("O")},1)/B{{r}}'],
], ["", "int", "pct"])
t.section("Cuándo se van")
t.kv([("Bajas que ocurren en ≤4 semanas", f'=SUMIFS({rng("Q")},{rng("N")},1)/COUNTIFS({rng("N")},1,{rng("J")},"<>")', "pct", False, "De las firmas que cuentan para retención")])
t.widths = {0: 230, 1: 110, 2: 140, 3: 160}

# ---------------------------------------------------------------- CONDUCE · COBERTURA
hubs = {h["hub"]: h for h in rd("conduce", "hubs")}
cob = rd("conduce", "cobertura_semanal")
dcb = Tab("Datos · Cobertura Conduce", "9CA3AF", freeze=1)
bf, bl = dcb.table(["Semana", "Hub", "Turno", "Turnos disponibles", "Turnos cubiertos", "Mes", "Cuenta (semana desde apertura)"],
                   [[d(r["semana"]), r["hub"], r["turno"], n(r["turnos_disponibles"]), n(r["turnos_cubiertos"]), '=DATE(YEAR(A{r}),MONTH(A{r}),1)',
                     1 if d(r["semana"]) >= d(hubs[r["hub"]]["fecha_apertura"]) else 0] for r in cob],
                   ["date", "", "", "int", "int", "mon", "int"])
dcb.widths = {0: 100, 1: 110, 2: 160, 3: 120, 4: 120, 5: 80, 6: 170}
t = Tab("Conduce · Cobertura", "B45309", freeze=4); tabs.append(t)
t.heading("Conduce · Cobertura de turnos por hub", "Turnos cubiertos ÷ disponibles. Meta: 92% por hub. Excluye la semana del 27-abr de Sur B (abrió el 1-may).")
B = "'Datos · Cobertura Conduce'!"
hub_list = ["Hub Centro", "Hub Poniente", "Hub Norte", "Hub Sur A", "Hub Sur B"]
mlist = [f"2026-{m:02d}" for m in range(1, 11)]
def cobf(h, mcell):
    s = lambda c_: f"SUMIFS({B}${c_}${bf}:${c_}${bl},{B}$B${bf}:$B${bl},\"{h}\",{B}$F${bf}:$F${bl},{mcell},{B}$G${bf}:$G${bl},1)"
    return f'=IFERROR({s("E")}/{s("D")},"")'
t.table(["Mes"] + [h.replace("Hub ", "") for h in hub_list], [[md(m)] + [cobf(h, "$A{r}") for h in hub_list] for m in mlist], ["mon"] + ["pct"] * 5)
t.section("Brecha contra la meta, octubre 2026")
def s_oct(c_, h): return f"SUMIFS({B}${c_}${bf}:${c_}${bl},{B}$B${bf}:$B${bl},\"{h}\",{B}$F${bf}:$F${bl},DATE(2026,10,1),{B}$G${bf}:$G${bl},1)"
gf, gl = t.table(["Hub", "Disponibles", "Cubiertos", "Cobertura", "Turnos bajo la meta", "Contribución perdida al mes"],
                 [[h, "=" + s_oct("D", h), "=" + s_oct("E", h), "=C{r}/B{r}", "=MAX(0,ROUND(0.92*B{r})-C{r})", "=E{r}*1100"] for h in hub_list],
                 ["", "int", "int", "pct", "int", "mxn"], total=["Total", "", "", "", "=SUM(E{first}:E{last})", "=SUM(F{first}:F{last})"])
CON_GAP = f"E{gl}"
t.widths = {0: 130, **{i: 120 for i in range(1, 6)}}

# ---------------------------------------------------------------- CONDUCE · PROPUESTA
t = Tab("Conduce · Propuesta", "B45309", gridlines=False); tabs.append(t)
t.heading("Conduce · ¿Marketing, Operaciones u otra?", "Presupuesto adicional de $1.5 M para Q1 2027 (13 semanas).")
t.section("Opciones")
t.table(["Opción", "Costo Q1", "Qué ataca", "Evidencia", "Decisión"], [
    ["Marketing: $1.5 M en medios para el sur", 1500000, "Volumen de leads", "Sur A tiene 3,882 leads vs 3,915 de Centro; el sur pierde en asistencia a inducción (46% vs 64%) y en retención", "No"],
    ["Operaciones: +30% de bono a todos", "=725*480*0.3*13", "Pago", "Con las mismas horas el bono no cambia la retención; 70% del gasto va a hubs que ya cumplen la meta", "No"],
    ["Sur cercano + permanencia temprana", "=SUM(B{a}:B{b})", "Distancia, inducción y primeras semanas", "Sur <10 km retiene 46% vs 31% a 10+ km; 55% de las bajas en ≤4 semanas", "Sí"],
], ["", "mxn", "", "", ""])
op_row = t.r - 2  # fila 1-based de la opción 3
t.section("Presupuesto de la propuesta")
plan_rows = [[p, v] for p, v in con["plan"]]
pf, pl = t.table(["Partida", "MXN"], plan_rows, ["", "mxn"], total=["Total", "=SUM(B{first}:B{last})"])
t.cells[(op_row, 1)] = f"=SUM(B{pf}:B{pl - 2})"
t.section("Valor estimado en Q1")
v = t.kv([
    ("Turnos bajo la meta en el sur (oct)", f"='Conduce · Cobertura'!{CON_GAP}", "int", False, "Brecha mensual"),
    ("Contribución por turno cubierto", 1100, "mxn", True, ""),
    ("Fracción de la brecha que se cierra (escenario bajo)", 0.5, "pct", True, "Supuesto"),
    ("Rampa Q1 (meses equivalentes)", 1.95, "dec", True, "30% / 65% / 100% del efecto en ene / feb / mar"),
])
v2 = t.kv([
    ("Valor Q1 · escenario bajo", f"={v['Turnos bajo la meta en el sur (oct)']}*{v['Contribución por turno cubierto']}*{v['Fracción de la brecha que se cierra (escenario bajo)']}*{v['Rampa Q1 (meses equivalentes)']}", "mxn", False, ""),
    ("Valor Q1 · escenario base (cierra la brecha)", f"={v['Turnos bajo la meta en el sur (oct)']}*{v['Contribución por turno cubierto']}*{v['Rampa Q1 (meses equivalentes)']}", "mxn", False, "Mezcla de firmas cercanas 50% y asistencia a inducción de 55%"),
    ("Valor mensual una vez cerrada la brecha", f"={v['Turnos bajo la meta en el sur (oct)']}*{v['Contribución por turno cubierto']}", "mxn", False, ""),
])
CON_VAL = v2["Valor Q1 · escenario base (cierra la brecha)"]
t.widths = {0: 340, 1: 140, 2: 250, 3: 520, 4: 80}

# ---------------------------------------------------------------- WATTS
wh = {r["hub_id"]: r for r in rd("watts", "hubs")}
wm = rd("watts", "hub_mensual")
dw = Tab("Datos · Hubs Watts", "9CA3AF", freeze=1)
wf, wl = dw.table(["Mes", "Hub", "Tipo", "Apertura", "Conectores instalados", "Días abierto", "Conectores operativos", "Horas disponibles", "Sesiones", "kWh", "Horas ocupadas",
                   "Ingreso", "Costo de energía", "Margen de energía", "Utilización", "Utilización (instalados)", "Precio efectivo kWh"],
                  [[md(r["mes"]), r["hub_id"], wh[r["hub_id"]]["tipo"], d(wh[r["hub_id"]]["fecha_apertura"]), n(wh[r["hub_id"]]["conectores"]), n(r["dias_abierto"]), n(r["conectores_operativos_prom"]),
                    n(r["horas_conector_disponibles"]), n(r["sesiones"]), n(r["kwh"]), n(r["horas_conector_ocupadas"]), n(r["ingreso_mxn"]), n(r["costo_energia_mxn"]),
                    "=L{r}-M{r}", "=K{r}/H{r}", "=K{r}/(E{r}*24*F{r})", "=IFERROR(L{r}/J{r},\"\")"] for r in wm],
                  ["mon", "", "", "date", "int", "int", "dec", "int", "int", "int", "int", "mxn", "mxn", "mxn", "pct", "pct", "mxn2"])
dw.widths = {i: 100 for i in range(17)}
W = "'Datos · Hubs Watts'!"
wr = lambda c_: f"{W}${c_}${wf}:${c_}${wl}"
t = Tab("Watts · Promo agosto", "1D4ED8", freeze=0); tabs.append(t)
t.heading("Watts · ¿Qué hizo la promoción de agosto?", "6 hubs destination con descuento del 1 al 31 de agosto. D-02 y D-05 llevaban más de 6 meses abiertos; los otros 4 abrieron en jun–jul.")
promo = sorted([k for k, h in wh.items() if h["descuento_promo_agosto"]])
ms = ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
t.section("Sesiones")
t.table(["Hub", "Apertura", "Descuento"] + ms, [[h, d(wh[h]["fecha_apertura"]), n(wh[h]["descuento_promo_agosto"])] +
        [f'=SUMIFS({wr("I")},{wr("B")},$A{{r}},{wr("A")},{DT(m)})' for m in ms] for h in promo], ["", "date", "pct"] + ["int"] * 5,
        total=["Total", "", ""] + [f"=SUM({col(3 + i)}{{first}}:{col(3 + i)}{{last}})" for i in range(5)])
t.section("Margen de energía")
t.table(["Hub", "Apertura", "Descuento"] + ms, [[h, d(wh[h]["fecha_apertura"]), n(wh[h]["descuento_promo_agosto"])] +
        [f'=SUMIFS({wr("N")},{wr("B")},$A{{r}},{wr("A")},{DT(m)})' for m in ms] for h in promo], ["", "date", "pct"] + ["mxn"] * 5,
        total=["Total", "", ""] + [f"=SUM({col(3 + i)}{{first}}:{col(3 + i)}{{last}})" for i in range(5)])
t.section("Alza de sesiones en agosto vs promedio jul–sep")
t.kv([
    ("Hubs maduros con promo (D-02, D-05)", f'=SUMPRODUCT(({wr("B")}="D-02")+({wr("B")}="D-05"),{wr("A")}=DATE(2026,8,1),{wr("I")})/(SUMPRODUCT(({wr("B")}="D-02")+({wr("B")}="D-05"),({wr("A")}=DATE(2026,7,1))+({wr("A")}=DATE(2026,9,1)),{wr("I")})/2)', "x", False, "Regresan a su nivel en septiembre"),
])
t.widths = {0: 260, 1: 100, 2: 90, **{i: 95 for i in range(3, 8)}}

t = Tab("Watts · Propuesta Q1", "1D4ED8", gridlines=False); tabs.append(t)
t.heading("Watts · Repetir la promo en Q1 en destination con utilización <10% en octubre", "Margen de energía con descuento, contra el margen de octubre. Cambia los supuestos en amarillo.")
P = t.kv([
    ("Descuento", 0.25, "pct", True, "Punto medio de 20–30%"),
    ("Alza de volumen con promo", 1.7, "x", True, "La observada en D-02 y D-05; sin canibalización (favorable a Marketing)"),
])
eleg = sorted(wat["eleg"])
oct_ = lambda c_: f'SUMIFS({wr(c_)},{wr("B")},$A{{r}},{wr("A")},DATE(2026,10,1))'
ef, el = t.table(["Hub", "Apertura", "Meses abierto", "Utilización oct", "kWh oct", "Precio efectivo kWh", "Costo energía kWh", "Margen oct", "Margen con promo", "Diferencia al mes", "kWh × para empatar"],
                 [[h, d(wh[h]["fecha_apertura"]), '=DATEDIF(B{r},DATE(2026,10,31),"M")', f"={oct_('K')}/{oct_('H')}", f"={oct_('J')}", f"={oct_('L')}/E{{r}}", n(wh[h]["costo_energia_kwh"]),
                   f"={oct_('N')}", f"=E{{r}}*{P['Alza de volumen con promo']}*(F{{r}}*(1-{P['Descuento']})-G{{r}})", "=I{r}-H{r}",
                   f'=IF(F{{r}}*(1-{P["Descuento"]})<=G{{r}},"No empata",(F{{r}}-G{{r}})/(F{{r}}*(1-{P["Descuento"]})-G{{r}}))'] for h in eleg],
                 ["", "date", "int", "pct", "int", "mxn2", "mxn2", "mxn", "mxn", "mxn", "x"],
                 total=["Total", "", "", "", "", "", "", "=SUM(H{first}:H{last})", "=SUM(I{first}:I{last})", "=SUM(J{first}:J{last})", ""])
t.kv([
    ("Costo de la propuesta en Q1", f"=-3*J{el}", "mxn", False, "Margen que se deja de ganar"),
    ("Hubs con menos de 6 meses", f'=COUNTIF(C{ef}:C{el - 1},"<6")', "int", False, "La meta de 12% aplica a partir del sexto mes"),
    ("Hubs que venderían debajo del costo", f'=COUNTIF(K{ef}:K{el - 1},"No empata")', "int", False, ""),
])
WAT_Q1 = f"J{el}"
t.section("Utilización mal medida: D-04")
t.kv([("D-04 · utilización reportada oct", f'=SUMIFS({wr("O")},{wr("B")},"D-04",{wr("A")},DATE(2026,10,1))', "pct", False, "Sobre conectores operativos (3 de 6)"),
      ("D-04 · utilización con conectores instalados", f'=SUMIFS({wr("P")},{wr("B")},"D-04",{wr("A")},DATE(2026,10,1))', "pct", False, "Quedaría dentro del corte de <10%")])
t.widths = {0: 290, 1: 110, 2: 90, 3: 100, 4: 90, 5: 110, 6: 110, 7: 100, 8: 110, 9: 110, 10: 120}

# ---------------------------------------------------------------- SUPUESTOS / CALIDAD / CONTROL
t = Tab("Supuestos del caso", "6B7280", freeze=1); tabs.append(t)
t.r = 0
t.table(["Línea", "Supuesto", "Valor", "Nota"], [[c_.capitalize(), r["Supuesto"], n(r["Valor"]), r["Nota"]] for c_ in ("impulso", "conduce", "watts") for r in rd(c_, "supuestos")], ["", "", "", ""])
t.widths = {0: 90, 1: 300, 2: 100, 3: 700}

t = Tab("Calidad de datos", "6B7280", gridlines=False); tabs.append(t)
t.heading("Calidad de datos", "Los archivos se cargaron sin cambios; esto es lo que encontré y cómo lo traté.")
t.table(["Línea", "Hallazgo", "Tratamiento"], [
    ["Impulso", "El funnel mensual cuenta eventos del mes sin importar cuándo se creó el lead (nov: 24 entregas con 12 visitas)", "Tasas con cohortes cerradas may–sep"],
    ["Impulso", "Cohortes de oct y nov siguen abiertas (451 y 221 leads en proceso)", "Fuera de las tasas"],
    ["Impulso", "Rechazos de riesgo pasan de 15% a 50% de los envíos desde mayo", "El exceso se atribuye a leads sin requisitos mínimos"],
    ["Conduce", "84 firmas 'Sin canal' no existen en el funnel de reclutamiento (Centro 623 vs 539)", "Se reporta; no cambia la retención"],
    ["Conduce", "Hub Roma cerró el 15-abr: 43 bajas por cierre de hub", "Excluidas de la retención"],
    ["Conduce", "Sur B aparece con una semana sin cobertura antes de abrir (27-abr)", "Excluida de la cobertura"],
    ["Conduce", "Las firmas solo cubren 2026; los 725 activos incluyen contratados antes", "La retención se mide sobre firmas 2026"],
    ["Conduce", "El bono depende de las horas trabajadas", "Retención comparada dentro de la misma banda de horas"],
    ["Watts", "La utilización usa conectores operativos: D-04 con 3 de 6 caídos reporta 14.9%", "Se recalcula con conectores instalados (7.5%)"],
    ["Watts", "El ingreso viene neto de descuentos LTO y promo, sin separar segmentos", "Se usa el precio efectivo por kWh"],
], ["", "", ""])
t.widths = {0: 90, 1: 620, 2: 380}

t = Tab("Control de cifras", "6B7280", gridlines=False); tabs.append(t)
t.heading("Control de cifras", "Cada cifra del deck se calculó en SQL (sql/03_analytical_views.sql) y en Python (analysis/vemo_model.py) desde los archivos originales.")
chk = M.get("checks", [])
LBL = {
    "impulso.exceso_riesgo": "Impulso · rechazos de riesgo por encima de la tasa pre-agente (may–oct)",
    "impulso.costo_exceso": "Impulso · costo de esos envíos a análisis",
    "impulso.entregas cohortes": "Impulso · entregas de las cohortes may–sep",
    "conduce.n observados": "Conduce · firmas que cuentan para retención",
    "conduce.n Sur <10 km": "Conduce · firmas sur a <10 km", "conduce.n Sur 10+ km": "Conduce · firmas sur a 10+ km",
    "conduce.n Resto <10 km": "Conduce · firmas resto a <10 km", "conduce.n Resto 10+ km": "Conduce · firmas resto a 10+ km",
    "conduce.gap oct Sur A": "Conduce · turnos bajo meta Sur A (oct)", "conduce.gap oct Sur B": "Conduce · turnos bajo meta Sur B (oct)",
    "watts.delta mensual": "Watts · diferencia mensual de margen con la promo (SQL redondea el precio a 2 decimales)",
}
lbl = lambda a: next((v for k, v in LBL.items() if a.startswith(k)), a)
t.table(["Cifra", "Python", "SQL", "Coincide"], [[lbl(a), b, c_, "Sí" if ok else "No"] for a, b, c_, ok in chk], ["", "dec", "dec", ""])
t.section("Cifras de este archivo vs Python")
t.table(["Cifra", "Este archivo", "Python"], [
    ["Impulso · leads necesarios", f"='Impulso · Meta 400'!{IMP_REFS['leads']}", round(imp["leads_need"], 1)],
    ["Impulso · analistas adicionales", f"='Impulso · Meta 400'!{IMP_REFS['analistas']}", imp["analistas"]],
    ["Impulso · costo total del mes", f"='Impulso · Meta 400'!{IMP_REFS['costo']}", round(imp["costo_total_400"])],
    ["Impulso · margen incremental vs hoy", f"='Impulso · Meta 400'!{IMP_REFS['incremental']}", round(imp["incremental_neto"])],
    ["Conduce · turnos bajo meta sur (oct)", f"='Conduce · Cobertura'!{CON_GAP}", con["gap_sur_mes"]],
    ["Conduce · valor Q1 escenario base", f"='Conduce · Propuesta'!{CON_VAL}", round(con["valor_q1"])],
    ["Watts · diferencia mensual de la propuesta", f"='Watts · Propuesta Q1'!{WAT_Q1}", round(wat["delta_q1"] / 3)],
], ["", "dec", "dec"])
CONTROL_TAB = t
t.widths = {0: 420, 1: 130, 2: 130, 3: 90}

tabs += [dc, df, dcb, dw]

# ---------------------------------------------------------------- XLSX
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
wb = Workbook(); wb.remove(wb.active)
for tb in tabs:
    ws = wb.create_sheet(tb.title[:31]); ws.sheet_properties.tabColor = tb.color; ws.sheet_view.showGridLines = tb.gridlines
    for (r_, c_), val in tb.cells.items(): ws.cell(r_ + 1, c_ + 1, val)
    for r1, c1, r2, c2, f in tb.fmt:
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1): ws.cell(rr + 1, cc + 1).number_format = f
    for r1, c1, r2, c2, st in tb.styles:
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                cell = ws.cell(rr + 1, cc + 1)
                cell.font = Font(bold=st.get("bold", False), italic=st.get("italic", False), size=st.get("size", 10), color=st.get("fg", "000000"))
                if "bg" in st: cell.fill = PatternFill("solid", fgColor=st["bg"])
                if st.get("wrap"): cell.alignment = Alignment(wrap_text=True, vertical="center")
                if st.get("top"): cell.border = Border(top=Side(style="thin"))
    for c_, w in tb.widths.items(): ws.column_dimensions[get_column_letter(c_ + 1)].width = w / 7
    if tb.freeze: ws.freeze_panes = ws.cell(tb.freeze + 1, 1)
wb.save(ROOT / "entregables" / "Vemo_Anexo_Calculos.xlsx")
print("xlsx ok")

# ---------------------------------------------------------------- GOOGLE SHEET
SID = os.environ.get("VEMO_SHEET_ID")
if not SID: sys.exit(0)
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gsheets_client as g
svc = g.service()
def rgb(h): return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}
def run(reqs):
    for i in range(0, len(reqs), 400):
        chunk = reqs[i:i + 400]
        g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": chunk}).execute())
meta = svc.spreadsheets().get(spreadsheetId=SID).execute()
run([{"updateSpreadsheetProperties": {"properties": {"title": "Vemo · Business Case Growth Analyst · Anexo de cálculos", "locale": "en_US", "timeZone": "America/Mexico_City"},
                                      "fields": "title,locale,timeZone"}},
     {"addSheet": {"properties": {"title": "_tmp"}}}])
meta = svc.spreadsheets().get(spreadsheetId=SID).execute()
run([{"deleteSheet": {"sheetId": s["properties"]["sheetId"]}} for s in meta["sheets"] if s["properties"]["title"] != "_tmp"])
res = g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
    {"addSheet": {"properties": {"title": tb.title, "index": i, "tabColorStyle": {"rgbColor": rgb(tb.color)},
                                 "gridProperties": {"frozenRowCount": tb.freeze, "hideGridlines": not tb.gridlines,
                                                    "rowCount": max(r_ for r_, _ in tb.cells) + 20, "columnCount": max(c_ for _, c_ in tb.cells) + 3}}}} for i, tb in enumerate(tabs)]}).execute())
ids = {tb.title: r["addSheet"]["properties"]["sheetId"] for tb, r in zip(tabs, res["replies"])}
run([{"deleteSheet": {"sheetId": s["properties"]["sheetId"]}} for s in svc.spreadsheets().get(spreadsheetId=SID).execute()["sheets"] if s["properties"]["title"] == "_tmp"])
def val(v):
    if isinstance(v, dt.date): return f"=DATE({v.year},{v.month},{v.day})"
    return v
data = []
for tb in tabs:
    R_ = max(r_ for r_, _ in tb.cells) + 1; C_ = max(c_ for _, c_ in tb.cells) + 1
    grid = [[""] * C_ for _ in range(R_)]
    for (r_, c_), v_ in tb.cells.items(): grid[r_][c_] = val(v_)
    data.append({"range": f"'{tb.title}'!A1", "values": grid})
for i in range(0, len(data), 4):
    chunk = data[i:i + 4]
    g.with_retry(lambda: svc.spreadsheets().values().batchUpdate(spreadsheetId=SID, body={"valueInputOption": "USER_ENTERED", "data": chunk}).execute())
reqs = []
for tb in tabs:
    sid = ids[tb.title]
    rng_ = lambda r1, c1, r2, c2: {"sheetId": sid, "startRowIndex": r1, "endRowIndex": r2 + 1, "startColumnIndex": c1, "endColumnIndex": c2 + 1}
    R_ = max(r_ for r_, _ in tb.cells) + 1; C_ = max(c_ for _, c_ in tb.cells) + 1
    reqs.append({"repeatCell": {"range": rng_(0, 0, R_ + 5, C_ + 1), "cell": {"userEnteredFormat": {"textFormat": {"fontFamily": "Roboto", "fontSize": 10}, "verticalAlignment": "MIDDLE"}},
                                "fields": "userEnteredFormat(textFormat,verticalAlignment)"}})
    for r1, c1, r2, c2 in tb.bands:
        reqs.append({"addBanding": {"bandedRange": {"range": rng_(r1, c1, r2, c2), "rowProperties": {"firstBandColorStyle": {"rgbColor": rgb("FFFFFF")}, "secondBandColorStyle": {"rgbColor": rgb(BAND)}}}}})
    for r1, c1, r2, c2, f in tb.fmt:
        typ = "DATE" if f in (FMT["date"], FMT["mon"]) else "NUMBER"
        reqs.append({"repeatCell": {"range": rng_(r1, c1, r2, c2), "cell": {"userEnteredFormat": {"numberFormat": {"type": typ, "pattern": f}}}, "fields": "userEnteredFormat.numberFormat"}})
    for r1, c1, r2, c2, st in tb.styles:
        fmt = {"textFormat": {"bold": st.get("bold", False), "italic": st.get("italic", False), "fontSize": st.get("size", 10), "fontFamily": "Roboto",
                              "foregroundColorStyle": {"rgbColor": rgb(st.get("fg", "111827"))}}}
        fields = ["textFormat"]
        if "bg" in st: fmt["backgroundColorStyle"] = {"rgbColor": rgb(st["bg"])}; fields.append("backgroundColorStyle")
        if st.get("wrap"): fmt["wrapStrategy"] = "WRAP"; fields.append("wrapStrategy")
        reqs.append({"repeatCell": {"range": rng_(r1, c1, r2, c2), "cell": {"userEnteredFormat": fmt}, "fields": "userEnteredFormat(" + ",".join(fields) + ")"}})
        if st.get("top"):
            reqs.append({"updateBorders": {"range": rng_(r1, c1, r2, c2), "top": {"style": "SOLID", "colorStyle": {"rgbColor": rgb(NAVY)}}}})
    for c_, w in tb.widths.items():
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": c_, "endIndex": c_ + 1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    # columnas de texto largo con ajuste de línea
    # títulos y notas desbordan a la derecha; sólo las celdas de tablas ajustan línea
    reqs.append({"repeatCell": {"range": rng_(0, 0, R_, C_), "cell": {"userEnteredFormat": {"wrapStrategy": "OVERFLOW_CELL"}}, "fields": "userEnteredFormat.wrapStrategy"}})
    if not tb.title.startswith("Datos"):
        for r1, c1, r2, c2 in tb.bands:
            reqs.append({"repeatCell": {"range": rng_(r1, c1, r2, c2), "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat.wrapStrategy"}})
    for r1, c1, r2, c2, st in tb.styles:
        if st.get("wrap"):
            reqs.append({"repeatCell": {"range": rng_(r1, c1, r2, c2), "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat.wrapStrategy"}})
run(reqs)
# lectura de control: errores de fórmula y comparación con Python
out = svc.spreadsheets().values().batchGet(spreadsheetId=SID, ranges=[f"'{tb.title}'!A1:Z200" for tb in tabs if not tb.title.startswith("Datos")], valueRenderOption="UNFORMATTED_VALUE").execute()
errs = []
for vr in out["valueRanges"]:
    for i, row in enumerate(vr.get("values", [])):
        for j, v_ in enumerate(row):
            if isinstance(v_, str) and v_.startswith("#"): errs.append(f"{vr['range']} {col(j)}{i + 1}: {v_}")
print("errores de fórmula:", errs[:15] or "ninguno")
ctl = svc.spreadsheets().values().get(spreadsheetId=SID, range="'Control de cifras'!A1:C60", valueRenderOption="UNFORMATTED_VALUE").execute()["values"]
for row in ctl:
    if len(row) == 3 and isinstance(row[1], (int, float)) and isinstance(row[2], (int, float)):
        ok = abs(row[1] - row[2]) <= max(1, abs(row[2]) * 0.002)
        print(("OK  " if ok else "DIF ") + f"{row[0]}: sheet {row[1]:,.1f} vs python {row[2]:,.1f}")
print(f"https://docs.google.com/spreadsheets/d/{SID}/edit")
