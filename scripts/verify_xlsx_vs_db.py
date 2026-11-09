"""Compara celda por celda los 3 Excel originales contra las tablas de Postgres (vemo).
Uso: tools/data_prep/.venv/bin/python -I scripts/verify_xlsx_vs_db.py   (requiere el contenedor vemo-postgres)
Números exactos (Decimal), fechas ISO, vacíos = NULL; multiconjunto de filas (sin PK); LEEME en orden por línea.
"""
import openpyxl, subprocess, csv, io, sys, datetime as dt, pathlib
from decimal import Decimal
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = {"impulso": "Vemo_Case1_Impulso_Datos 1.xlsx", "conduce": "Vemo_Case2_Conduce_Datos 1.xlsx", "watts": "Vemo_Case3_Watts_Datos 1.xlsx"}
def db(sql):
    out = subprocess.run(["docker", "exec", "vemo-postgres", "psql", "-U", "postgres", "-d", "vemo", "-c", f"COPY ({sql}) TO STDOUT WITH CSV HEADER"], capture_output=True, text=True, check=True).stdout
    r = list(csv.reader(io.StringIO(out))); return r[0], r[1:]
def nx(v):
    if v is None: return None
    if isinstance(v, dt.datetime): return v.date().isoformat() if v.time() == dt.time(0) else v.isoformat(sep=" ")
    if isinstance(v, dt.date): return v.isoformat()
    if isinstance(v, (int, float)) and not isinstance(v, bool): return Decimal(repr(v)).normalize()
    return str(v)
def nd(s, isnum):
    if s == "": return None
    if isnum:
        try: return Decimal(s).normalize()
        except Exception: return s
    return s
def sn(s):
    if s == "": return None
    try: return str(Decimal(s).normalize())
    except Exception: return s
cells, bad = 0, []
for case, f in CASES.items():
    for ws in openpyxl.load_workbook(ROOT / f, data_only=True, read_only=True).worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        while rows and all(c is None for c in rows[-1]): rows.pop()
        t = ws.title.lower(); name = f"{case}.{t}"
        if ws.title == "LEEME":
            x = ["" if r[0] is None else str(r[0]) for r in rows]
            d = [r[0] for r in db(f"SELECT coalesce(texto,'') FROM {name} ORDER BY linea")[1]]
            ok = x == d; cells += len(x)
        elif ws.title == "supuestos":
            data = rows[1:]
            xs = Counter(tuple(None if c is None else (str(nx(c)) if isinstance(c, (int, float)) else nx(c)) for c in r[:3]) for r in data)
            ds = Counter(tuple(sn(c) for c in r) for r in db(f"SELECT supuesto,valor,nota FROM {name}")[1])
            vn = db(f"SELECT valor,valor_num FROM {name}")[1]
            ok = xs == ds and all(Decimal(a) == Decimal(b) for a, b in vn if a and b); cells += sum(len(r) for r in data)
        else:
            hdr = [str(h) for h in rows[0]]; data = rows[1:]
            types = dict(db(f"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='{case}' AND table_name='{t}'")[1])
            isnum = [types[c] in ("numeric", "integer", "bigint") for c in hdr]
            xs = Counter(tuple(nx(c) for c in r) for r in data)
            ds = Counter(tuple(nd(c, n) for c, n in zip(r, isnum)) for r in db(f"SELECT {', '.join(hdr)} FROM {name}")[1])
            ok = set(hdr) == set(types) and xs == ds; cells += sum(len(r) for r in data)
        print(f"{'OK  ' if ok else 'DIFF'} {name}")
        if not ok: bad.append(name)
print(f"celdas comparadas: {cells:,} · diferencias: {len(bad)}")
sys.exit(1 if bad else 0)
