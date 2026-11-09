"""Sube entregables/Vemo_Anexo_Calculos.xlsx a un Google Sheet existente (una pestaña por hoja, fórmulas incluidas).

La service account no puede crear archivos en Drive: crea un Sheet vacío, compártelo como Editor con
tasknest-sheets-bot@hermes-495507.iam.gserviceaccount.com y corre:
  VEMO_SHEET_ID=<id> ../Clara_DA_BusinessCase/tools/gsheets/.venv/bin/python -I tools/gsheets/build_vemo_sheet.py
Se puede correr de nuevo sin problema: borra y recrea las pestañas.
"""
import os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import openpyxl
import gsheets_client as g

ROOT = pathlib.Path(__file__).resolve().parents[2]
SID = os.environ["VEMO_SHEET_ID"]
wb = openpyxl.load_workbook(ROOT / "entregables" / "Vemo_Anexo_Calculos.xlsx")  # fórmulas como texto '=...'
svc = g.service()
meta = svc.spreadsheets().get(spreadsheetId=SID).execute()
old = [s["properties"]["sheetId"] for s in meta["sheets"]]
# 1) pestaña temporal, 2) borrar todas las anteriores, 3) crear las nuevas, 4) borrar la temporal
tmp = g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [{"addSheet": {"properties": {"title": "_tmp"}}}]}).execute())["replies"][0]["addSheet"]["properties"]["sheetId"]
g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [{"deleteSheet": {"sheetId": i}} for i in old]}).execute())
reqs = [{"addSheet": {"properties": {"title": ws.title, "gridProperties": {"frozenRowCount": 1}}}} for ws in wb.worksheets]
res = g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": reqs}).execute())
g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [{"deleteSheet": {"sheetId": tmp}}]}).execute())
data = []
for ws in wb.worksheets:
    rows = [["" if c is None else c for c in r] for r in ws.iter_rows(values_only=True)]
    data.append({"range": f"'{ws.title}'!A1", "values": rows})
g.with_retry(lambda: svc.spreadsheets().values().batchUpdate(spreadsheetId=SID, body={"valueInputOption": "USER_ENTERED", "data": data}).execute())
fmt = [{"repeatCell": {"range": {"sheetId": r["addSheet"]["properties"]["sheetId"], "startRowIndex": 0, "endRowIndex": 1},
        "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                                       "backgroundColor": {"red": 0.06, "green": 0.54, "blue": 0.42}}},
        "fields": "userEnteredFormat(textFormat,backgroundColor)"}} for r in res["replies"][1:]]
fmt += [{"autoResizeDimensions": {"dimensions": {"sheetId": r["addSheet"]["properties"]["sheetId"], "dimension": "COLUMNS"}}} for r in res["replies"]]
g.with_retry(lambda: svc.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": fmt}).execute())
# verificación: el número de filas por pestaña coincide con el xlsx
got = svc.spreadsheets().values().batchGet(spreadsheetId=SID, ranges=[f"'{ws.title}'!A:A" for ws in wb.worksheets]).execute()
for ws, vr in zip(wb.worksheets, got["valueRanges"]):
    n = len(vr.get("values", []))
    print(f"{'OK ' if n == ws.max_row else 'DIF'} {ws.title}: sheet {n} / xlsx {ws.max_row}")
print(f"https://docs.google.com/spreadsheets/d/{SID}/edit")
