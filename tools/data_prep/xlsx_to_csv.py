"""Exporta cada hoja de los Excel del caso a CSV, SIN limpiar ni transformar nada.

Uso (desde la raíz del repo):
    tools/data_prep/.venv/bin/python -I tools/data_prep/xlsx_to_csv.py

- Fechas -> ISO (YYYY-MM-DD). Celdas vacías -> campo vacío (NULL al cargar en Postgres).
- Números: se escriben con repr() de Python, sin redondear.
- LEEME y supuestos se exportan con todas sus columnas en su posición original.
- Escribe data/raw/manifest.csv con filas/columnas por hoja para verificar la carga.
"""
import csv, datetime as dt, pathlib, sys
import openpyxl

ROOT = pathlib.Path(__file__).resolve().parents[2]
CASES = {
    "impulso": "Vemo_Case1_Impulso_Datos 1.xlsx",
    "conduce": "Vemo_Case2_Conduce_Datos 1.xlsx",
    "watts":   "Vemo_Case3_Watts_Datos 1.xlsx",
}

def fmt(v):
    if v is None:
        return ""
    if isinstance(v, dt.datetime):
        return v.date().isoformat() if v.time() == dt.time(0) else v.isoformat(sep=" ")
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, float):
        return repr(v)
    return str(v)

def main():
    manifest = []
    for case, fname in CASES.items():
        src = ROOT / fname
        if not src.exists():
            sys.exit(f"No encuentro {src}")
        wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
        outdir = ROOT / "data" / "raw" / case
        outdir.mkdir(parents=True, exist_ok=True)
        for ws in wb.worksheets:
            rows = [list(r) for r in ws.iter_rows(values_only=True)]
            # quita filas finales totalmente vacías (artefacto de read_only), nada más
            while rows and all(c is None for c in rows[-1]):
                rows.pop()
            ncols = max((len(r) for r in rows), default=0)
            out = outdir / f"{ws.title}.csv"
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                for r in rows:
                    w.writerow([fmt(c) for c in r] + [""] * (ncols - len(r)))
            data_rows = len(rows) - 1 if ws.title not in ("LEEME",) else len(rows)
            manifest.append((case, ws.title, data_rows, ncols, out.relative_to(ROOT).as_posix()))
            print(f"{case:8s} {ws.title:20s} {data_rows:5d} filas  {ncols:2d} cols -> {out.relative_to(ROOT)}")
    with (ROOT / "data" / "raw" / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "sheet", "data_rows", "cols", "path"])
        w.writerows(manifest)

if __name__ == "__main__":
    main()
