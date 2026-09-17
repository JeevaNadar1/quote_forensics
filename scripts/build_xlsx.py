#!/usr/bin/env python3
"""Build the Excel comparison model.

Usage:
    python3 build_xlsx.py normalized.json variance.json -o comparison.xlsx

Seven sheets: Summary, Levelled, Provenance, Ledger, Quarantine, Assumptions,
Sensitivity. Derived numbers are formulas, not pasted values — the buyer will change
an assumption and the model must move with them.
"""

import argparse
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BLUE, SLATE, LIGHT = "5DADE2", "708090", "D3D3D3"
H_FILL = PatternFill("solid", fgColor=BLUE)
I_FILL = PatternFill("solid", fgColor="FFF4CE")   # input cells
H_FONT = Font(bold=True, color="FFFFFF", size=11)
THIN = Border(bottom=Side(style="thin", color=LIGHT))


def header(ws, row, labels, widths=None):
    for i, label in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=label)
        c.fill, c.font = H_FILL, H_FONT
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 28
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def title(ws, text):
    c = ws.cell(row=1, column=1, value=text)
    c.font = Font(bold=True, size=14, color=BLUE)


def money(ws, col, first, last, fmt):
    for r in range(first, last + 1):
        ws.cell(row=r, column=col).number_format = fmt


def sheet_summary(wb, norm, var):
    ws = wb.create_sheet("Summary")
    ccy = norm["comparison"].get("currency", "")
    fmt = f'#,##0.00'
    title(ws, norm["comparison"].get("title", "Quote comparison"))

    ws.cell(row=2, column=1, value=f"Currency: {ccy}   Basis: "
            f"{norm['comparison'].get('tax_basis', 'ex_tax')}").font = Font(color=SLATE)
    g = norm.get("gate", {})
    ws.cell(row=3, column=1, value=("GATE: RANKABLE — " if g.get("rankable")
                                    else "GATE: BLOCKED — ") + g.get("reason", "")
            ).font = Font(bold=True, color=SLATE if g.get("rankable") else "C0392B")

    header(ws, 5, ["Vendor", "Ranked total", "Quarantined", "Non-firm",
                   "Stated total", "Recon diff", "Score (your weights)",
                   "Score (equal weights)"],
           [26, 16, 14, 14, 16, 14, 20, 20])

    su = {s["vendor"]: s["total"] for s in var["scores_user_weights"]}
    se = {s["vendor"]: s["total"] for s in var["scores_equal_weights"]}

    r = 6
    for q in norm["quotes"]:
        recon = q.get("reconciliation") or {}
        ws.cell(row=r, column=1, value=q["vendor"])
        ws.cell(row=r, column=2, value=q["ranked_total"])
        ws.cell(row=r, column=3, value=q["quarantined_total"])
        ws.cell(row=r, column=4, value=q["non_firm_total"])
        ws.cell(row=r, column=5, value=recon.get("stated"))
        d = ws.cell(row=r, column=6, value=recon.get("difference"))
        if recon.get("status") == "mismatch":
            d.font = Font(bold=True, color="C0392B")
        ws.cell(row=r, column=7, value=su.get(q["vendor"]))
        ws.cell(row=r, column=8, value=se.get(q["vendor"]))
        for c in range(1, 9):
            ws.cell(row=r, column=c).border = THIN
        r += 1
    for col in (2, 3, 4, 5, 6):
        money(ws, col, 6, r - 1, fmt)

    ws.cell(row=r + 1, column=1,
            value=var["weight_sensitivity"]["note"]).font = Font(italic=True, color=SLATE)
    ws.cell(row=r + 3, column=1, value="Weights (editable — Sensitivity sheet recalculates)"
            ).font = Font(bold=True, color=BLUE)
    wr = r + 4
    for k, v in var["weights_used"].items():
        ws.cell(row=wr, column=1, value=k)
        c = ws.cell(row=wr, column=2, value=v)
        c.fill = I_FILL
        wr += 1
    return ws


def sheet_levelled(wb, norm):
    ws = wb.create_sheet("Levelled")
    title(ws, "Levelled comparison — one row per mapped scope item")
    vendors = [q["vendor"] for q in norm["quotes"]]
    header(ws, 3, ["Scope item", "Category", "UoM", "Map", "Confidence"] + vendors
           + ["Min", "Max", "Spread %"],
           [42, 18, 10, 14, 12] + [16] * len(vendors) + [14, 14, 12])

    keys, meta = [], {}
    for q in norm["quotes"]:
        for l in q["lines"]:
            if l["map_key"] not in meta:
                keys.append(l["map_key"])
                meta[l["map_key"]] = l
    idx = {v: i for i, v in enumerate(vendors)}

    r = 4
    for key in keys:
        m = meta[key]
        ws.cell(row=r, column=1, value=key)
        ws.cell(row=r, column=2, value=m.get("category"))
        ws.cell(row=r, column=3, value=m.get("uom"))
        ws.cell(row=r, column=4, value=m.get("map_type"))
        cc = ws.cell(row=r, column=5, value=m.get("confidence"))
        if m.get("confidence") == "low":
            cc.font = Font(bold=True, color="C0392B")
        for q in norm["quotes"]:
            hit = next((l for l in q["lines"] if l["map_key"] == key), None)
            col = 6 + idx[q["vendor"]]
            if hit:
                c = ws.cell(row=r, column=col, value=hit["value"])
                if hit["quarantine"]:
                    c.font = Font(italic=True, color=SLATE)
            else:
                ws.cell(row=r, column=col, value="—").font = Font(color="C0392B")
        first, last = get_column_letter(6), get_column_letter(5 + len(vendors))
        rng = f"{first}{r}:{last}{r}"
        ws.cell(row=r, column=6 + len(vendors), value=f"=IFERROR(MIN({rng}),\"\")")
        ws.cell(row=r, column=7 + len(vendors), value=f"=IFERROR(MAX({rng}),\"\")")
        mn = f"{get_column_letter(6 + len(vendors))}{r}"
        mx = f"{get_column_letter(7 + len(vendors))}{r}"
        ws.cell(row=r, column=8 + len(vendors),
                value=f'=IFERROR(({mx}-{mn})/{mn},"")').number_format = "0.0%"
        r += 1

    tot = r
    ws.cell(row=tot, column=1, value="TOTAL (all rows incl. quarantined)").font = Font(bold=True)
    for i, _ in enumerate(vendors):
        col = get_column_letter(6 + i)
        c = ws.cell(row=tot, column=6 + i, value=f"=SUM({col}4:{col}{r - 1})")
        c.font = Font(bold=True)
    for i in range(len(vendors)):
        money(ws, 6 + i, 4, tot, "#,##0.00")
    return ws


def sheet_provenance(wb, norm):
    ws = wb.create_sheet("Provenance")
    title(ws, "Provenance — every compared line traced to its source text")
    header(ws, 3, ["Vendor", "Scope item", "Source file / ref", "Page", "Row",
                   "Verbatim original text"], [22, 34, 24, 10, 10, 80])
    r = 4
    for q in norm["quotes"]:
        for l in q["lines"]:
            ws.cell(row=r, column=1, value=q["vendor"])
            ws.cell(row=r, column=2, value=l["map_key"])
            ws.cell(row=r, column=3, value=q.get("quote_ref"))
            ws.cell(row=r, column=4, value=l.get("page"))
            ws.cell(row=r, column=5, value=l.get("row"))
            c = ws.cell(row=r, column=6, value=l.get("verbatim"))
            c.alignment = Alignment(wrap_text=True, vertical="top")
            r += 1
    return ws


def sheet_ledger(wb, norm):
    ws = wb.create_sheet("Ledger")
    title(ws, "Inclusion / exclusion ledger")
    vendors = [q["vendor"] for q in norm["quotes"]]
    header(ws, 3, ["Scope element"] + vendors, [46] + [26] * len(vendors))

    elements = []
    for q in norm["quotes"]:
        for e in q.get("inclusions", []) + q.get("exclusions", []):
            if e not in elements:
                elements.append(e)
    r = 4
    for e in elements:
        ws.cell(row=r, column=1, value=e).alignment = Alignment(wrap_text=True)
        for i, q in enumerate(norm["quotes"]):
            if e in q.get("inclusions", []):
                v, colr = "Included", "1E8449"
            elif e in q.get("exclusions", []):
                v, colr = "EXCLUDED", "C0392B"
            else:
                v, colr = "not stated — ask", SLATE
            c = ws.cell(row=r, column=2 + i, value=v)
            c.font = Font(color=colr, bold=(v == "EXCLUDED"))
        r += 1
    return ws


def sheet_quarantine(wb, norm):
    ws = wb.create_sheet("Quarantine")
    title(ws, "Quarantined scope — excluded from ranked totals")
    ws.cell(row=2, column=1,
            value=f"Quarantine ratio: {norm.get('quarantine_ratio', 0):.1%}   "
                  f"{norm.get('gate', {}).get('reason', '')}").font = Font(color=SLATE)
    header(ws, 4, ["Vendor", "Scope item", "Value", "Reason", "Question that releases it"],
           [22, 38, 16, 34, 48])
    r = 5
    for q in norm["quotes"]:
        for l in q["lines"]:
            if l["quarantine"]:
                ws.cell(row=r, column=1, value=q["vendor"])
                ws.cell(row=r, column=2, value=l["map_key"])
                ws.cell(row=r, column=3, value=l["value"]).number_format = "#,##0.00"
                ws.cell(row=r, column=4, value=l.get("quarantine_reason"))
                ws.cell(row=r, column=5, value="")
                r += 1
    return ws


def sheet_assumptions(wb, norm):
    ws = wb.create_sheet("Assumptions")
    title(ws, "Assumption register — every assumption made to level these quotes")
    header(ws, 3, ["#", "Assumption", "Impact if wrong", "Affects"], [6, 60, 50, 30])
    r = 4
    for i, a in enumerate(norm.get("assumptions", []), 1):
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=a.get("text")).alignment = Alignment(wrap_text=True)
        ws.cell(row=r, column=3, value=a.get("impact_if_wrong")).alignment = Alignment(wrap_text=True)
        ws.cell(row=r, column=4, value=", ".join(a.get("affects", [])))
        r += 1
    if r == 4:
        ws.cell(row=4, column=2,
                value="None recorded. If this is truly empty, the levelling was trivial — "
                      "verify that, because it usually is not.").font = Font(italic=True, color=SLATE)
    return ws


def sheet_sensitivity(wb, norm, var):
    ws = wb.create_sheet("Sensitivity")
    title(ws, "Sensitivity — change a weight, the ranking moves")
    header(ws, 3, ["Vendor"] + list(var["weights_used"].keys()) + ["Weighted score"],
           [26] + [18] * len(var["weights_used"]) + [18])

    wrow = 4 + len(var["scores_user_weights"]) + 2
    ws.cell(row=wrow - 1, column=1, value="Weights (edit these)").font = Font(bold=True, color=BLUE)
    for i, (k, v) in enumerate(var["weights_used"].items()):
        ws.cell(row=wrow, column=1 + i, value=k).font = Font(color=SLATE)
        c = ws.cell(row=wrow + 1, column=1 + i, value=v)
        c.fill = I_FILL
    keys = list(var["weights_used"].keys())

    r = 4
    for s in var["scores_user_weights"]:
        ws.cell(row=r, column=1, value=s["vendor"])
        for i, k in enumerate(keys):
            ws.cell(row=r, column=2 + i, value=s["components"].get(k))
        parts = [f"{get_column_letter(2 + i)}{r}*{get_column_letter(1 + i)}${wrow + 1}"
                 for i, k in enumerate(keys) if k in s["components"]]
        wsum = "+".join(f"{get_column_letter(1 + i)}${wrow + 1}"
                        for i, k in enumerate(keys) if k in s["components"])
        ws.cell(row=r, column=2 + len(keys),
                value=f"=IFERROR(({'+'.join(parts)})/({wsum}),\"\")"
                ).font = Font(bold=True)
        r += 1
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("normalized")
    ap.add_argument("variance")
    ap.add_argument("-o", "--output", default="comparison.xlsx")
    args = ap.parse_args()

    norm = json.load(open(args.normalized))
    var = json.load(open(args.variance))

    wb = Workbook()
    wb.remove(wb.active)
    sheet_summary(wb, norm, var)
    sheet_levelled(wb, norm)
    sheet_provenance(wb, norm)
    sheet_ledger(wb, norm)
    sheet_quarantine(wb, norm)
    sheet_assumptions(wb, norm)
    sheet_sensitivity(wb, norm, var)
    wb.save(args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
