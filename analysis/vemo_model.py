"""Vemo BC · segunda vía de cálculo + modelos + exports.

Lee los CSV crudos (data/raw), NO la base, y recalcula cada cifra que va al deck.
Compara contra los valores obtenidos por SQL (sql/03_analytical_views.sql) y falla si no cuadran.
Escribe:
  - app/public/data/{impulso,conduce,watts}.json  (dashboards)
  - analysis/out/metrics.json                       (cifras del deck)
  - entregables/Vemo_Anexo_Calculos.xlsx            (anexo; base del Google Sheet)
Uso: tools/data_prep/.venv/bin/python -I analysis/vemo_model.py
"""
import csv, json, math, pathlib, datetime as dt
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "analysis" / "out"; OUT.mkdir(parents=True, exist_ok=True)
APPDATA = ROOT / "app" / "public" / "data"; APPDATA.mkdir(parents=True, exist_ok=True)
ENT = ROOT / "entregables"; ENT.mkdir(exist_ok=True)

def rd(case, sheet):
    with open(RAW / case / f"{sheet}.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))
def num(x):
    return None if x in ("", None) else float(x)
def D(s):
    return dt.date.fromisoformat(s) if s else None
MESES = {"01":"ene","02":"feb","03":"mar","04":"abr","05":"may","06":"jun","07":"jul","08":"ago","09":"sep","10":"oct","11":"nov","12":"dic"}
lab = lambda m: MESES[m[5:7]]
checks = []
def check(name, got, expected, tol=0.5):
    ok = abs(got - expected) <= tol
    checks.append((name, got, expected, ok))
def mxn(x):
    return f"${x/1e6:,.2f} M" if abs(x) >= 1e6 else f"${x/1e3:,.0f} k"

# ============================================================ IMPULSO
fm = rd("impulso", "funnel_mensual"); coh = rd("impulso", "cohortes"); can = rd("impulso", "canales")
for r in fm:
    for k in r:
        if k != "mes": r[k] = num(r[k])
for r in coh:
    for k in r:
        if k != "mes_creacion": r[k] = num(r[k])
for r in can:
    for k in ("inversion_mxn", "leads", "calificados", "entregas_acumuladas"): r[k] = num(r[k])

pre = [r for r in fm if r["mes"] < "2026-05"]
post = [r for r in fm if "2026-05" <= r["mes"] <= "2026-10"]
s = lambda rows, k: sum(r[k] for r in rows)
tasa_riesgo_pre = s(pre, "rechazados_riesgo") / s(pre, "enviados_a_analisis")
exceso = sum(r["rechazados_riesgo"] - round(r["enviados_a_analisis"] * tasa_riesgo_pre) for r in post)
check("impulso.exceso_riesgo may-oct (SQL v_exceso_riesgo)", exceso, 1692)
check("impulso.costo_exceso (SQL)", exceso * 180, 304560)
envios_post_avg = s(post, "enviados_a_analisis") / len(post)
meses_sobre_cap = sum(1 for r in post if r["enviados_a_analisis"] > 700)
aprob_pre = s(pre, "calificados") / s(pre, "enviados_a_analisis")
aprob_post = s(post, "calificados") / s(post, "enviados_a_analisis")
dias_pre = sum(r["dias_mediana_analisis"] for r in pre) / len(pre)
dias_oct = next(r for r in fm if r["mes"] == "2026-10")["dias_mediana_analisis"]

# cohortes cerradas
c_pre = [r for r in coh if r["mes_creacion"] < "2026-05"]
c_post = [r for r in coh if "2026-05" <= r["mes_creacion"] <= "2026-09"]
l2e_pre = s(c_pre, "entregas_acumuladas") / s(c_pre, "leads")
l2e_post = s(c_post, "entregas_acumuladas") / s(c_post, "leads")
cal2e_post = s(c_post, "entregas_acumuladas") / s(c_post, "calificados")
ent_coh_pre = s(c_pre, "entregas_acumuladas") / len(c_pre)
ent_coh_post = s(c_post, "entregas_acumuladas") / len(c_post)
perd_dep_post = s(c_post, "perdidos_en_visita_por_deposito") / s(c_post, "visitas_aprobadas")
vis2e_post = s(c_post, "entregas_acumuladas") / s(c_post, "visitas_aprobadas")
check("impulso.entregas cohortes may-sep", s(c_post, "entregas_acumuladas"), 684)

# consistencia: canales vs cohortes
dq_impulso = []
for r in coh:
    m = r["mes_creacion"]
    sl = sum(c["leads"] for c in can if c["mes_creacion"] == m)
    se = sum(c["entregas_acumuladas"] for c in can if c["mes_creacion"] == m)
    if sl != r["leads"] or se != r["entregas_acumuladas"]:
        dq_impulso.append(f"{m}: canales {sl:.0f} leads/{se:.0f} entregas vs cohortes {r['leads']:.0f}/{r['entregas_acumuladas']:.0f}")
for r in fm:
    c = next(x for x in coh if x["mes_creacion"] == r["mes"])
    if r["leads_creados"] != c["leads"]:
        dq_impulso.append(f"{r['mes']}: leads funnel {r['leads_creados']:.0f} vs cohortes {c['leads']:.0f}")

# canales (cohortes cerradas may-sep)
canal = defaultdict(lambda: defaultdict(float))
for r in can:
    if "2026-05" <= r["mes_creacion"] <= "2026-09":
        for k in ("inversion_mxn", "leads", "entregas_acumuladas"): canal[r["canal"]][k] += r[k]
cac = {k: (v["inversion_mxn"] / v["entregas_acumuladas"]) for k, v in canal.items()}
cpl = {k: (v["inversion_mxn"] / v["leads"]) for k, v in canal.items()}
inv_mes = defaultdict(float)
for r in can: inv_mes[r["mes_creacion"]] += r["inversion_mxn"]
paid = ("Meta", "Google", "TikTok")
paid_leads_post = sum(canal[c]["leads"] for c in paid)
paid_inv_post = sum(canal[c]["inversion_mxn"] for c in paid)
cpl_paid = paid_inv_post / paid_leads_post
free_leads_mes = sum(canal[c]["leads"] for c in ("Orgánico", "Referidos")) / 5
cac_blend_post = paid_inv_post / sum(canal[c]["entregas_acumuladas"] for c in canal)

# ---- modelo 400
META = 400
calif_need = META / cal2e_post
# Aprobación con filtro de requisitos en el agente: quitar el exceso de rechazos de Riesgo
aprob_filtro = s(post, "calificados") / (s(post, "enviados_a_analisis") - exceso)
analisis_need = calif_need / aprob_filtro
analistas = max(0, math.ceil((analisis_need - 700) / 150))
leads_need = META / l2e_post
paid_leads_need = leads_need - free_leads_mes
paid_leads_now = paid_leads_post / 5
CPL_MARGINAL_MULT = 1.5   # supuesto: el CPL incremental cuesta 50% más (saturación de audiencias)
media_total = paid_leads_now * cpl_paid + (paid_leads_need - paid_leads_now) * cpl_paid * CPL_MARGINAL_MULT
cac_400 = media_total / META
costo_envios = analisis_need * 180
costo_analistas = analistas * 35000
costo_total_400 = media_total + costo_envios + costo_analistas + 25000
base_ent = ent_coh_post  # ~137/mes
margen_400 = META * 30000
margen_base = base_ent * 30000
# costo base (mes típico post agente)
costo_base = paid_inv_post / 5 + envios_post_avg * 180 + 25000
incremental_neto = (margen_400 - costo_total_400) - (margen_base - costo_base)
# palanca 0: filtro solo → envíos bajo capacidad
envios_con_filtro = envios_post_avg - exceso / len(post)
imp = dict(
    tasa_riesgo_pre=tasa_riesgo_pre, exceso_riesgo=exceso, costo_exceso=exceso * 180,
    exceso_mes=exceso / len(post), envios_post_avg=envios_post_avg, meses_sobre_cap=meses_sobre_cap,
    aprob_pre=aprob_pre, aprob_post=aprob_post, dias_pre=dias_pre, dias_oct=dias_oct,
    l2e_pre=l2e_pre, l2e_post=l2e_post, cal2e_post=cal2e_post, ent_coh_pre=ent_coh_pre, ent_coh_post=ent_coh_post,
    perd_dep_post=perd_dep_post, vis2e_post=vis2e_post, cac=cac, cpl=cpl, cpl_paid=cpl_paid, cac_blend_post=cac_blend_post,
    inv_jun=inv_mes["2026-06"], inv_oct=inv_mes["2026-10"],
    calif_need=calif_need, aprob_filtro=aprob_filtro, analisis_need=analisis_need, analistas=analistas,
    leads_need=leads_need, paid_leads_need=paid_leads_need, paid_leads_now=paid_leads_now, media_total=media_total,
    cac_400=cac_400, costo_envios=costo_envios, costo_analistas=costo_analistas, costo_total_400=costo_total_400,
    margen_400=margen_400, incremental_neto=incremental_neto, envios_con_filtro=envios_con_filtro, dq=dq_impulso,
)

# ============================================================ CONDUCE
cond = rd("conduce", "conductores"); hubs = rd("conduce", "hubs"); cob = rd("conduce", "cobertura_semanal")
fun = rd("conduce", "funnel_mensual"); inv = rd("conduce", "inversion_mensual")
CORTE = dt.date(2026, 8, 6)
obs = [r for r in cond if D(r["fecha_firma"]) <= CORTE and r["motivo_baja"] != "Cierre de hub"]
def ret(r):
    b = D(r["fecha_baja"]); return b is None or b > D(r["fecha_firma"]) + dt.timedelta(days=90)
def rate(rows): return sum(ret(r) for r in rows) / len(rows) if rows else None
ret_total = rate(obs)
check("conduce.n observados (SQL: 1574 firmas ≤6-ago − 43 cierre de hub)", len(obs), 1531, 0)
sur = lambda r: r["hub"].startswith("Hub Sur")
near = lambda r: float(r["distancia_casa_hub_km"]) < 10
ret_seg = {
    "Sur <10 km": rate([r for r in obs if sur(r) and near(r)]), "Sur 10+ km": rate([r for r in obs if sur(r) and not near(r)]),
    "Resto <10 km": rate([r for r in obs if not sur(r) and near(r)]), "Resto 10+ km": rate([r for r in obs if not sur(r) and not near(r)]),
}
n_seg = {"Sur <10 km": 102, "Sur 10+ km": 375, "Resto <10 km": 632, "Resto 10+ km": 422}
for k, v in n_seg.items():
    got = len([r for r in obs if (sur(r) == k.startswith("Sur")) and (near(r) == ("<10" in k))])
    check(f"conduce.n {k} (SQL v_retencion90)", got, v, 0)
share_lejos_sur = sum(1 for r in cond if sur(r) and not near(r)) / sum(1 for r in cond if sur(r))
share_lejos_resto = sum(1 for r in cond if not sur(r) and not near(r)) / sum(1 for r in cond if not sur(r))
bajas = [r for r in obs if r["fecha_baja"]]
baja_2sem = sum(1 for r in bajas if (D(r["fecha_baja"]) - D(r["fecha_firma"])).days <= 14) / len(bajas)
baja_4sem = sum(1 for r in bajas if (D(r["fecha_baja"]) - D(r["fecha_firma"])).days <= 30) / len(bajas)
def hb(r):
    h = float(r["horas_semanales_prom"])
    return "<36 h" if h < 36 else "36–42 h" if h < 42 else "42–48 h" if h < 48 else "48+ h"
ret_horas = {k: rate([r for r in obs if hb(r) == k]) for k in ("<36 h", "36–42 h", "42–48 h", "48+ h")}
bono_horas = {k: sum(float(r["bono_semanal_prom_mxn"]) for r in obs if hb(r) == k) / len([r for r in obs if hb(r) == k]) for k in ret_horas}
# bono dentro de la misma banda de horas (42–48 h): ¿más bono = más retención?
band = [r for r in obs if hb(r) == "42–48 h"]
med = sorted(float(r["bono_semanal_prom_mxn"]) for r in band)[len(band) // 2]
ret_bono_alto = rate([r for r in band if float(r["bono_semanal_prom_mxn"]) >= med])
ret_bono_bajo = rate([r for r in band if float(r["bono_semanal_prom_mxn"]) < med])
ret_turno = {}
for r in obs: ret_turno.setdefault(r["turno"].split(" ")[0], []).append(r)
ret_turno = {k: rate(v) for k, v in ret_turno.items()}
ret_hub = {}
for r in obs: ret_hub.setdefault(r["hub"], []).append(r)
ret_hub = {k: rate(v) for k, v in ret_hub.items() if k != "Hub Roma"}

# cobertura
apert = {h["hub"]: D(h["fecha_apertura"]) for h in hubs}
cobm = defaultdict(lambda: [0, 0])
for r in cob:
    if D(r["semana"]) < apert[r["hub"]]: continue  # semana que empieza antes de la apertura (Sur B, 27-abr)
    k = (r["semana"][:7], r["hub"]); cobm[k][0] += int(r["turnos_disponibles"]); cobm[k][1] += int(r["turnos_cubiertos"])
meses_c = sorted({k[0] for k in cobm if k[0] >= "2026-01"})
hubs_act = ["Hub Centro", "Hub Poniente", "Hub Norte", "Hub Sur A", "Hub Sur B"]
cob_series = {h: [round(cobm[(m, h)][1] / cobm[(m, h)][0] * 100, 1) if cobm[(m, h)][0] else None for m in meses_c] for h in hubs_act}
gap_oct = {h: max(round(0.92 * cobm[("2026-10", h)][0]) - cobm[("2026-10", h)][1], 0) for h in hubs_act}
check("conduce.gap oct Sur A (SQL)", gap_oct["Hub Sur A"], 481, 0); check("conduce.gap oct Sur B (SQL)", gap_oct["Hub Sur B"], 304, 0)
gap_sur_mes = gap_oct["Hub Sur A"] + gap_oct["Hub Sur B"]
valor_gap_mes = gap_sur_mes * 1100
perdidos_sur_oct = sum(cobm[("2026-10", h)][0] - cobm[("2026-10", h)][1] for h in ("Hub Sur A", "Hub Sur B"))
# funnel
fh = defaultdict(lambda: defaultdict(int))
for r in fun:
    for k in ("leads", "citados_induccion", "asistieron_induccion", "firmas"): fh[r["hub"]][k] += int(r[k])
show = {h: fh[h]["asistieron_induccion"] / fh[h]["citados_induccion"] for h in fh}
leads_h = {h: fh[h]["leads"] for h in fh}
sin_lead = sum(1 for r in cond if r["canal"] == "Sin canal")
firmas_sur_mes = sum(1 for r in cond if sur(r) and "2026-07-01" <= r["fecha_firma"] < "2026-11-01") / 4
# --- propuestas
bono_ops = 725 * 480 * 0.30 * 13
dif_bono_turno = ret_bono_alto - ret_bono_bajo
# Marketing: $500k/mes extra; firmas extra al costo marginal (supuesto 2× el promedio de $1,400 por saturación)
firmas_mkt_mes = 500000 / (1400 * 2)
ret_sur_actual = rate([r for r in obs if sur(r)])
# Nuestra propuesta (Q1): presupuesto
plan = [
    ("Reclutamiento hiperlocal sur (radio ≤10 km: geo-segmentación Meta/Indeed, ferias y volanteo en colonias)", 360000),
    ("Bono de referido sur: $2,000 al llegar el referido a la semana 4 (~100 referidos)", 200000),
    ("Bono de permanencia sur para nuevos: $1,000 en semana 4 + $1,500 en semana 12 (~240 firmas)", 330000),
    ("Asistencia a inducción: recordatorios WhatsApp + apoyo de transporte $300 el día de inducción (~600 citados)", 180000),
    ("Reserva condicionada a resultados del mes 1 (se libera si la cobertura sur sube ≥3 pp)", 430000),
]
plan_total = sum(v for _, v in plan)
assert plan_total == 1500000, plan_total
# Impacto estimado: subir mezcla de firmas cercanas del sur de 21% a 50% y show-rate del sur de 46% a 55%.
mix_now = 1 - share_lejos_sur
mix_new = 0.50
ret_sur_new = mix_new * ret_seg["Sur <10 km"] + (1 - mix_new) * ret_seg["Sur 10+ km"]
ret_sur_now = mix_now * ret_seg["Sur <10 km"] + (1 - mix_now) * ret_seg["Sur 10+ km"]
lift_ret = ret_sur_new / ret_sur_now - 1
show_lift = 0.55 / show["Hub Sur A"] - 1
# Activos sur ∝ firmas × permanencia. Turnos cubiertos sur oct:
cub_sur_oct = sum(cobm[("2026-10", h)][1] for h in ("Hub Sur A", "Hub Sur B"))
disp_sur_oct = sum(cobm[("2026-10", h)][0] for h in ("Hub Sur A", "Hub Sur B"))
# Solo la fracción de cubiertos que rota (conductores firmados en 2026) responde; supuesto: 100% en estado estable,
# rampa Q1: 30% / 65% / 100% del efecto pleno.
pleno = min(cub_sur_oct * ((1 + lift_ret) * (1 + show_lift) - 1), 0.92 * disp_sur_oct - cub_sur_oct)
turnos_q1 = pleno * (0.30 + 0.65 + 1.0)
valor_q1 = turnos_q1 * 1100
con = dict(
    ret_total=ret_total, ret_seg=ret_seg, share_lejos_sur=share_lejos_sur, share_lejos_resto=share_lejos_resto,
    baja_2sem=baja_2sem, baja_4sem=baja_4sem, ret_horas=ret_horas, bono_horas=bono_horas,
    ret_bono_alto=ret_bono_alto, ret_bono_bajo=ret_bono_bajo, ret_turno=ret_turno, ret_hub=ret_hub,
    gap_oct=gap_oct, gap_sur_mes=gap_sur_mes, valor_gap_mes=valor_gap_mes, valor_gap_q1=valor_gap_mes * 3,
    perdidos_sur_oct=perdidos_sur_oct, show=show, leads_h=leads_h, sin_lead=sin_lead, firmas_sur_mes=firmas_sur_mes,
    bono_ops=bono_ops, firmas_mkt_mes=firmas_mkt_mes, ret_sur_actual=ret_sur_actual,
    plan=plan, lift_ret=lift_ret, show_lift=show_lift, pleno_mes=pleno, turnos_q1=turnos_q1, valor_q1=valor_q1,
    cob_oct={h: cobm[("2026-10", h)][1] / cobm[("2026-10", h)][0] for h in hubs_act},
)

# ============================================================ WATTS
wh = {r["hub_id"]: r for r in rd("watts", "hubs")}
wm = rd("watts", "hub_mensual")
for r in wm:
    h = wh[r["hub_id"]]
    for k in ("dias_abierto", "conectores_operativos_prom", "horas_conector_disponibles", "sesiones", "kwh", "horas_conector_ocupadas", "ingreso_mxn", "costo_energia_mxn"):
        r[k] = float(r[k])
    r["u"] = r["horas_conector_ocupadas"] / r["horas_conector_disponibles"]
    r["u_inst"] = r["horas_conector_ocupadas"] / (float(h["conectores"]) * 24 * r["dias_abierto"])
    r["mg"] = r["ingreso_mxn"] - r["costo_energia_mxn"]
    r["eff"] = r["ingreso_mxn"] / r["kwh"] if r["kwh"] else None
W = {(r["hub_id"], r["mes"]): r for r in wm}
promo = [k for k, h in wh.items() if h["descuento_promo_agosto"]]
ses = lambda hub, m: W[(hub, m)]["sesiones"] if (hub, m) in W else 0
mg = lambda hub, m: W[(hub, m)]["mg"] if (hub, m) in W else 0
ses_jul = sum(ses(h, "2026-07") for h in promo); ses_ago = sum(ses(h, "2026-08") for h in promo)
ses_sep = sum(ses(h, "2026-09") for h in promo); ses_oct = sum(ses(h, "2026-10") for h in promo)
mg_jul = sum(mg(h, "2026-07") for h in promo); mg_ago = sum(mg(h, "2026-08") for h in promo); mg_sep = sum(mg(h, "2026-09") for h in promo)
maduros = [h for h in promo if D(wh[h]["fecha_apertura"]) < dt.date(2026, 2, 1)]  # ≥6 meses en ago
nuevos = [h for h in promo if h not in maduros]
uplift_maduros = sum(ses(h, "2026-08") for h in maduros) / sum((ses(h, "2026-07") + ses(h, "2026-09")) / 2 for h in maduros)
# control: destination sin promo abiertos antes de jun
ctrl = [k for k, h in wh.items() if h["tipo"] == "Destination" and not h["descuento_promo_agosto"] and D(h["fecha_apertura"]) < dt.date(2026, 6, 1)]
uplift_ctrl = sum(ses(h, "2026-08") for h in ctrl) / sum((ses(h, "2026-07") + ses(h, "2026-09")) / 2 for h in ctrl)
# propuesta Q1
eleg = [k for k, h in wh.items() if h["tipo"] == "Destination" and (k, "2026-10") in W and W[(k, "2026-10")]["u"] < 0.10]
UPLIFT, DESC = 1.7, 0.25
def delta(k, up=UPLIFT, d=DESC):
    o = W[(k, "2026-10")]; c = float(wh[k]["costo_energia_kwh"])
    return o["kwh"] * up * (o["eff"] * (1 - d) - c) - o["mg"]
delta_mes = sum(delta(k) for k in eleg)
check("watts.delta mensual propuesta (SQL v_propuesta_q1; SQL redondea precio efectivo a 2 dec.)", delta_mes, -64902, 100)
delta_sin_uplift = sum(delta(k, 1.0) for k in eleg)
def meses_abiertos(k, ref=dt.date(2026, 10, 31)):
    a = D(wh[k]["fecha_apertura"]); return (ref.year - a.year) * 12 + ref.month - a.month - (1 if ref.day < a.day else 0)
eleg_jovenes = [k for k in eleg if meses_abiertos(k) < 6]
debajo_costo = [k for k in eleg if W[(k, "2026-10")]["eff"] * (1 - DESC) <= float(wh[k]["costo_energia_kwh"])]
def breakeven(k):
    o = W[(k, "2026-10")]; c = float(wh[k]["costo_energia_kwh"])
    den = o["eff"] * (1 - DESC) - c
    return None if den <= 0 else (o["eff"] - c) / den
be = {k: breakeven(k) for k in eleg}
# D-04 conectores caídos
d04 = W[("D-04", "2026-10")]
dest_oct = [k for k, h in wh.items() if h["tipo"] == "Destination" and (k, "2026-10") in W]
fijo_dest = sum(float(wh[k]["costo_fijo_mensual_mxn"]) for k in dest_oct)
mg_dest_oct = sum(W[(k, "2026-10")]["mg"] for k in dest_oct)
neg_tras_fijo_maduros = [k for k in dest_oct if meses_abiertos(k) >= 6 and W[(k, "2026-10")]["mg"] < float(wh[k]["costo_fijo_mensual_mxn"])]
spread = {k: float(wh[k]["precio_publico_kwh"]) - float(wh[k]["costo_energia_kwh"]) for k in wh}
wat = dict(
    promo=promo, ses_jul=ses_jul, ses_ago=ses_ago, ses_sep=ses_sep, ses_oct=ses_oct, mg_jul=mg_jul, mg_ago=mg_ago, mg_sep=mg_sep,
    maduros=maduros, nuevos=nuevos, uplift_maduros=uplift_maduros, uplift_ctrl=uplift_ctrl,
    eleg=eleg, eleg_jovenes=eleg_jovenes, debajo_costo=debajo_costo, breakeven=be,
    delta_mes=delta_mes, delta_q1=delta_mes * 3, delta_sin_uplift_q1=delta_sin_uplift * 3,
    d04_u=d04["u"], d04_u_inst=d04["u_inst"], d04_ses_jun=ses("D-04", "2026-06"), d04_ses_oct=ses("D-04", "2026-10"),
    fijo_dest=fijo_dest, mg_dest_oct=mg_dest_oct, neg_tras_fijo_maduros=neg_tras_fijo_maduros,
)

# ============================================================ OUTPUT JSON (dashboards)
pct = lambda x, d=0: f"{x*100:.{d}f}%"
meses_i = [r["mes"] for r in fm if r["mes"] <= "2026-10"]
impulso_json = {
    "title": "Vemo Impulso · funnel de arrendamiento",
    "answer": f"El agente de IA sí subió las entregas (+{ent_coh_post/ent_coh_pre-1:.0%} por cohorte), pero manda ~{exceso/len(post):.0f} leads/mes que no cumplen requisitos y satura a Riesgo; 400 en un mes es viable hasta marzo 2027, no antes.",
    "kpis": [
        {"label": "Entregas por cohorte (may–sep)", "value": f"{ent_coh_post:.0f}/mes", "sub": f"vs {ent_coh_pre:.0f} pre-agente"},
        {"label": "Envíos a análisis (may–oct)", "value": f"{envios_post_avg:.0f}/mes", "sub": f"capacidad 700 · {meses_sobre_cap} de 6 meses arriba", "tone": "bad"},
        {"label": "Aprobación buró+riesgo", "value": pct(aprob_post), "sub": f"vs {pct(aprob_pre)} pre-agente", "tone": "bad"},
        {"label": "Días de análisis (mediana)", "value": f"{dias_oct:.1f}", "sub": f"vs {dias_pre:.1f} pre-agente", "tone": "bad"},
        {"label": "CAC medios (may–sep)", "value": f"${cac_blend_post:,.0f}", "sub": "tope Finanzas $10,000", "tone": "good"},
        {"label": "Inversión medios oct vs jun", "value": f"{inv_mes['2026-10']/inv_mes['2026-06']-1:+.0%}", "sub": f"{mxn(inv_mes['2026-06'])} → {mxn(inv_mes['2026-10'])}", "tone": "bad"},
    ],
    "charts": [
        {"id": "envios", "title": "Envíos a análisis vs capacidad de Riesgo", "type": "bar", "x": [lab(m) for m in meses_i],
         "series": [{"name": "Calificados", "values": [r["calificados"] for r in fm if r["mes"] <= "2026-10"]},
                    {"name": "Rechazo buró", "values": [r["rechazados_buro"] for r in fm if r["mes"] <= "2026-10"]},
                    {"name": "Rechazo riesgo", "values": [r["rechazados_riesgo"] for r in fm if r["mes"] <= "2026-10"]}],
         "stacked": True, "refLine": {"value": 700, "label": "Capacidad 700"}},
        {"id": "dias", "title": "Días de análisis (mediana)", "type": "line", "x": [lab(r["mes"]) for r in fm],
         "series": [{"name": "Días", "values": [r["dias_mediana_analisis"] for r in fm]}], "note": "Nov incompleto (extracción 4-nov)."},
        {"id": "cohortes", "title": "Entregas por cohorte de creación", "type": "bar", "x": [lab(r["mes_creacion"]) for r in coh if r["mes_creacion"] <= "2026-09"],
         "series": [{"name": "Entregas", "values": [r["entregas_acumuladas"] for r in coh if r["mes_creacion"] <= "2026-09"]}], "note": "Oct/nov siguen abiertas."},
        {"id": "inversion", "title": "Inversión en medios por mes (MXN miles)", "type": "line", "x": [lab(m) for m in meses_i],
         "series": [{"name": "Inversión", "values": [round(inv_mes[m] / 1000) for m in meses_i]}, {"name": "Leads", "values": [r["leads_creados"] for r in fm if r["mes"] <= "2026-10"]}]},
        {"id": "cac", "title": "CAC por canal (may–sep, MXN)", "type": "hbar", "x": list(paid),
         "series": [{"name": "CAC", "values": [round(cac[c]) for c in paid]}], "refLine": {"value": 10000, "label": "Tope $10k"}},
    ],
    "tables": [{"title": "Modelo para 400 entregas en un mes", "columns": ["Concepto", "Valor"], "rows": [
        ["Conversión lead→entrega (cohortes may–sep)", pct(l2e_post, 2)],
        ["Leads necesarios", f"{leads_need:,.0f} /mes"],
        ["Calificados necesarios", f"{calif_need:,.0f} /mes"],
        ["Aprobación con filtro de requisitos en el agente", pct(aprob_filtro)],
        ["Análisis necesarios", f"{analisis_need:,.0f} /mes → {analistas} analistas extra"],
        ["Medios", mxn(media_total) + f" (CAC {cac_400:,.0f})"],
        ["Costo total del mes", mxn(costo_total_400)],
        ["Margen de contribución (400 × $30k)", mxn(margen_400)],
        ["Margen incremental neto vs hoy", mxn(incremental_neto) + " /mes"],
    ]}],
    "notes": [
        "funnel_mensual (Dirección) mezcla cohortes: nov marca 24 entregas con 12 visitas. Usamos cohortes cerradas (may–sep) para tasas.",
        f"Exceso de rechazos de riesgo = rechazos por encima de la tasa pre-agente ({pct(tasa_riesgo_pre)}); supuesto: son leads que no cumplen requisitos mínimos.",
        "Supuesto: CPL incremental 50% más caro que el actual por saturación (no hay datos de escala).",
    ] + [f"Calidad de datos: {x}" for x in dq_impulso[:3]],
}
conduce_json = {
    "title": "Vemo Conduce · retención y cobertura",
    "answer": f"Ninguna de las dos: el sur sí tiene leads; el problema es que 79% de sus firmas viven a 10+ km y se van en las primeras semanas. Propuesta focalizada en el sur: $0.9–{mxn(valor_q1)} de contribución en Q1 con $1.07 M comprometidos.",
    "kpis": [
        {"label": "Retención a 90 días", "value": pct(ret_total), "sub": "firmas ene–6 ago, sin cierre de Roma", "tone": "bad"},
        {"label": "Cobertura oct Sur A / Sur B", "value": f"{con['cob_oct']['Hub Sur A']*100:.0f}% / {con['cob_oct']['Hub Sur B']*100:.0f}%", "sub": "meta 92%", "tone": "bad"},
        {"label": "Turnos bajo meta sur (oct)", "value": f"{gap_sur_mes:,}", "sub": f"= {mxn(valor_gap_mes)}/mes de contribución", "tone": "bad"},
        {"label": "Firmas sur que viven a 10+ km", "value": pct(share_lejos_sur), "sub": f"vs {pct(share_lejos_resto)} en otros hubs"},
        {"label": "Bajas en ≤4 semanas", "value": pct(baja_4sem), "sub": "antes de que el bono pese"},
        {"label": "Asistencia a inducción sur", "value": pct(show['Hub Sur A']), "sub": f"vs {pct(show['Hub Centro'])} Centro", "tone": "bad"},
    ],
    "charts": [
        {"id": "cob", "title": "Cobertura de turnos por hub (%)", "type": "line", "x": [lab(m) for m in meses_c],
         "series": [{"name": h.replace("Hub ", ""), "values": cob_series[h]} for h in hubs_act], "unit": "%", "refLine": {"value": 92, "label": "Meta 92%"}},
        {"id": "ret_dist", "title": "Retención a 90 días por zona y distancia casa-hub (%)", "type": "bar", "x": list(ret_seg),
         "series": [{"name": "Retención 90d", "values": [round(v * 100, 1) for v in ret_seg.values()]}], "unit": "%"},
        {"id": "ret_horas", "title": "Retención 90d por horas semanales (el bono sigue a las horas)", "type": "bar", "x": list(ret_horas),
         "series": [{"name": "Retención 90d %", "values": [round(v * 100, 1) for v in ret_horas.values()]}, {"name": "Bono prom. $/100", "values": [round(v / 100, 1) for v in bono_horas.values()]}]},
        {"id": "funnel", "title": "Leads y asistencia a inducción por hub", "type": "bar", "x": [h.replace("Hub ", "") for h in hubs_act],
         "series": [{"name": "Leads (ene–nov)", "values": [leads_h[h] for h in hubs_act]}, {"name": "Firmas", "values": [fh[h]["firmas"] for h in hubs_act]}]},
    ],
    "tables": [{"title": "Propuestas evaluadas (Q1 2027)", "columns": ["Opción", "Costo", "Qué ataca", "Veredicto"], "rows": [
        ["Marketing: $1.5 M medios sur", "$1.50 M", f"Más leads (sur ya tiene {leads_h['Hub Sur A']:,} leads, ≈ Centro)", "No"],
        ["Operaciones: +30% bono a todos", mxn(bono_ops), f"Bono; pero {pct(baja_2sem)} de bajas ocurre en ≤2 semanas", "No"],
        ["Propuesta: sur hiperlocal + permanencia temprana", "$1.07 M + $0.43 M reserva", "Distancia, inducción y primeras semanas", "Sí"],
    ]}],
    "notes": [
        f"{sin_lead} firmas 'Sin canal' no existen en funnel_mensual (por eso Centro tiene 623 firmas vs 539).",
        "Hub Roma cerró 15-abr: 43 bajas por 'Cierre de hub' se excluyen de la retención.",
        "Semana de Hub Sur B anterior a su apertura (1-may) se excluye de cobertura.",
        "Bono y horas: el bono se paga por horas → correlación con retención no es causal.",
        "conductores sólo trae firmas 2026; los 725 activos incluyen contratados antes.",
    ],
}
meses_w = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
watts_json = {
    "title": "Vemo Watts · utilización y margen",
    "answer": f"No apruebo: la promo no se sostuvo y en los hubs maduros vendió debajo del costo; en Q1 costaría ≈ {mxn(-wat['delta_q1'])} de margen aun con +70% de volumen. Mejor: demanda cautiva de la flota Vemo, precio por horario con piso y arreglar conectores.",
    "kpis": [
        {"label": "Sesiones promo jul → ago", "value": f"{ses_jul:.0f} → {ses_ago:.0f}", "sub": f"×{ses_ago/ses_jul:.1f}, pero 4 de 6 hubs abrieron en jun–jul"},
        {"label": "Margen de energía promo ago", "value": mxn(mg_ago), "sub": f"vs {mxn(mg_jul)} jul y {mxn(mg_sep)} sep", "tone": "bad"},
        {"label": "Alza real en hubs maduros", "value": f"×{uplift_maduros:.2f}", "sub": f"control ×{uplift_ctrl:.2f}; vuelve a base en sep"},
        {"label": "Hubs elegibles (<10% oct)", "value": f"{len(eleg)}", "sub": f"{len(eleg_jovenes)} con <6 meses (meta aún no aplica)"},
        {"label": "Costo propuesta Q1", "value": mxn(-wat['delta_q1']), "sub": f"{mxn(-wat['delta_sin_uplift_q1'])} sin alza de volumen", "tone": "bad"},
        {"label": "D-04 utilización reportada vs instalada", "value": f"{d04['u']*100:.1f}% vs {d04['u_inst']*100:.1f}%", "sub": "3 de 6 conectores caídos desde ago", "tone": "bad"},
    ],
    "charts": [
        {"id": "ses_promo", "title": "Sesiones en los 6 hubs de la promo", "type": "bar", "x": [lab(m) for m in meses_w],
         "series": [{"name": "Maduros (D-02, D-05)", "values": [sum(ses(h, m) for h in maduros) for m in meses_w]},
                    {"name": "Nuevos (abiertos jun–jul)", "values": [sum(ses(h, m) for h in nuevos) for m in meses_w]}], "stacked": True},
        {"id": "mg_promo", "title": "Margen de energía hubs maduros de la promo (MXN)", "type": "bar", "x": [lab(m) for m in meses_w],
         "series": [{"name": h, "values": [round(mg(h, m)) for m in meses_w]} for h in maduros]},
        {"id": "util_oct", "title": "Utilización oct-2026, destination (%)", "type": "hbar", "x": sorted(dest_oct, key=lambda k: W[(k, '2026-10')]['u']),
         "series": [{"name": "Utilización", "values": [round(W[(k, '2026-10')]['u'] * 100, 1) for k in sorted(dest_oct, key=lambda k: W[(k, '2026-10')]['u'])]}], "unit": "%", "refLine": {"value": 10, "label": "Corte 10%"}},
    ],
    "tables": [{"title": "Hubs que entrarían a la promo (oct < 10%)", "columns": ["Hub", "Meses abierto", "Utilización oct", "Margen oct", "Δ margen/mes con promo", "kWh × para empatar"],
                "rows": [[k, meses_abiertos(k), pct(W[(k, '2026-10')]['u'], 1), f"${W[(k, '2026-10')]['mg']:,.0f}", (f"-${-delta(k):,.0f}" if delta(k) < 0 else f"${delta(k):,.0f}"), ("imposible" if be[k] is None else f"×{be[k]:.1f}")] for k in sorted(eleg)]}],
    "notes": [
        "Utilización con conectores operativos: si se caen conectores la utilización 'sube' (D-04). El corte <10% debe usar conectores instalados.",
        f"Supuestos: descuento 25% (punto medio), alza de volumen ×{UPLIFT} (la observada en hubs maduros), sin canibalización (optimista para Marketing).",
        "Ingreso ya neto de LTO 25% + promo: en D-02/D-05 el precio efectivo con promo quedó debajo del costo de energía.",
        "Hubs <6 meses todavía están en rampa natural: el 'triple' de sesiones mezcla rampa y promo.",
    ],
}
for name, obj in (("impulso", impulso_json), ("conduce", conduce_json), ("watts", watts_json)):
    (APPDATA / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
(OUT / "metrics.json").write_text(json.dumps({"impulso": imp, "conduce": con, "watts": wat}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

# ============================================================ XLSX anexo
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
wb = Workbook(); ws = wb.active; ws.title = "README"
for row in [
    ["Vemo · Business Case Growth Analyst · Anexo de cálculos"],
    ["Fuente: Excel del caso (extracción 4-nov-2026) cargados sin cambios en Postgres; vistas en sql/03_analytical_views.sql."],
    ["Segunda vía: analysis/vemo_model.py recalcula desde CSV crudos y compara contra SQL (pestaña Verificacion)."],
    ["Pestañas: Conclusiones · Impulso_* · Conduce_* · Watts_* · Supuestos · Calidad_datos · Verificacion"],
]: ws.append(row)
ws["A1"].font = Font(bold=True, size=14)
def sheet(title, header, rows):
    s = wb.create_sheet(title); s.append(header)
    for c in s[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0F8A6A")
    for r in rows: s.append(r)
    for col in s.columns: s.column_dimensions[col[0].column_letter].width = max(12, min(60, max(len(str(c.value or "")) for c in col) + 2))
    return s
sheet("Conclusiones", ["Case", "Respuesta"], [["Impulso", impulso_json["answer"]], ["Conduce", conduce_json["answer"]], ["Watts", watts_json["answer"]]])
s = sheet("Impulso_funnel", list(fm[0].keys()) + ["tasa_aprobacion", "envios_sobre_capacidad"], [])
for i, r in enumerate(fm, start=2):
    s.append(list(r.values()) + [f"=H{i}/E{i}", f"=E{i}-700"])
sheet("Impulso_cohortes", list(coh[0].keys()), [list(r.values()) for r in coh])
sheet("Impulso_canales_cac", ["canal", "inversion_may_sep", "leads", "entregas", "CPL", "CAC"],
      [[k, v["inversion_mxn"], v["leads"], v["entregas_acumuladas"], cpl[k], cac.get(k)] for k, v in canal.items()])
sheet("Impulso_modelo_400", ["Concepto", "Valor"], [[a, b] for a, b in impulso_json["tables"][0]["rows"]] + [
    ["Supuesto CPL marginal ×", CPL_MARGINAL_MULT], ["Analistas: costo/mes", costo_analistas], ["Envíos: costo/mes", costo_envios], ["Medios: costo/mes", media_total]])
sheet("Conduce_retencion", ["Segmento", "Retención 90d"], [[k, v] for k, v in {**ret_seg, **{f"Horas {k}": v for k, v in ret_horas.items()}, **{f"Turno {k}": v for k, v in ret_turno.items()}, **ret_hub}.items()])
sheet("Conduce_cobertura", ["mes"] + hubs_act, [[m] + [cob_series[h][i] for h in hubs_act] for i, m in enumerate(meses_c)])
sheet("Conduce_propuesta", ["Partida", "MXN"], plan + [["Total", plan_total], ["Valor estimado Q1 (contribución turnos)", valor_q1], ["Bono Operaciones (+30%)", bono_ops]])
sheet("Watts_promo", ["hub_id", "mes", "sesiones", "kwh", "ingreso", "costo_energia", "margen_energia", "utilizacion", "utilizacion_instalada"],
      [[r["hub_id"], r["mes"], r["sesiones"], r["kwh"], r["ingreso_mxn"], r["costo_energia_mxn"], r["mg"], r["u"], r["u_inst"]] for r in wm if r["hub_id"] in promo])
sheet("Watts_propuesta_Q1", watts_json["tables"][0]["columns"], watts_json["tables"][0]["rows"])
sup = []
for case in ("impulso", "conduce", "watts"):
    for r in rd(case, "supuestos"): sup.append([case, r["Supuesto"], r["Valor"], r["Nota"]])
sheet("Supuestos", ["case", "supuesto", "valor", "nota"], sup)
sheet("Calidad_datos", ["case", "hallazgo"], [["impulso", x] for x in dq_impulso] + [["conduce", n] for n in conduce_json["notes"]] + [["watts", n] for n in watts_json["notes"][:1]])
sheet("Verificacion", ["chequeo", "python (CSV)", "SQL", "ok"], [[a, b, c, "OK" if d else "FALLA"] for a, b, c, d in checks])
wb.save(ENT / "Vemo_Anexo_Calculos.xlsx")

for a, b, c, d in checks: print(f"{'OK ' if d else 'FAIL'} {a}: {b:,.1f} vs {c:,.1f}")
assert all(d for *_, d in checks), "verificación falló"
print(json.dumps({"impulso": {k: imp[k] for k in ("exceso_mes","ent_coh_pre","ent_coh_post","l2e_post","cal2e_post","aprob_filtro","analisis_need","analistas","leads_need","media_total","cac_400","costo_total_400","incremental_neto","envios_con_filtro","perd_dep_post","vis2e_post","cpl_paid")},
                  "conduce": {k: con[k] for k in ("ret_total","ret_seg","baja_2sem","baja_4sem","ret_bono_alto","ret_bono_bajo","ret_turno","gap_sur_mes","valor_gap_mes","bono_ops","firmas_mkt_mes","firmas_sur_mes","lift_ret","show_lift","pleno_mes","valor_q1","show")},
                  "watts": {k: wat[k] for k in ("ses_jul","ses_ago","ses_sep","mg_jul","mg_ago","mg_sep","uplift_maduros","uplift_ctrl","eleg","eleg_jovenes","debajo_costo","delta_q1","delta_sin_uplift_q1","fijo_dest","mg_dest_oct","neg_tras_fijo_maduros")}},
                 default=str, indent=1, ensure_ascii=False))
