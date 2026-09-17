#!/usr/bin/env python3
"""Build the A4 print-ready comparison report.

Usage:
    python3 build_pdf.py normalized.json variance.json -o comparison.pdf \
        [--verdict verdict.json]

Style: A4 portrait, 20mm margins, Modern Minimalist palette (#5DADE2 primary,
#708090 secondary, #D3D3D3 dividers), serif body at 12pt, numbered lists, no
callout blocks, no personal name in the footer.

verdict.json is optional and carries the written analysis:
    {"recommendation": "...", "confidence": "medium",
     "conditions": ["..."], "diagnosis": [{"driver": "...", "tag": "E",
     "quantum": "...", "evidence": "...", "action": "..."}],
     "next_actions": ["..."]}
"""

import argparse
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

BLUE = colors.HexColor("#5DADE2")
SLATE = colors.HexColor("#708090")
LIGHT = colors.HexColor("#D3D3D3")
RED = colors.HexColor("#C0392B")

BODY_FONT = "Times-Roman"
BODY_BOLD = "Times-Bold"
BODY_ITAL = "Times-Italic"
HEAD_FONT = "Helvetica-Bold"   # sans headings against serif body


def styles():
    s = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=s["Normal"], fontName=HEAD_FONT, fontSize=20,
                                textColor=BLUE, leading=24, spaceAfter=4),
        "sub": ParagraphStyle("sb", parent=s["Normal"], fontName=BODY_ITAL, fontSize=10,
                              textColor=SLATE, leading=13, spaceAfter=14),
        "h1": ParagraphStyle("h1", parent=s["Normal"], fontName=HEAD_FONT, fontSize=13,
                             textColor=BLUE, leading=16, spaceBefore=14, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=s["Normal"], fontName=HEAD_FONT, fontSize=11,
                             textColor=SLATE, leading=14, spaceBefore=9, spaceAfter=4),
        "body": ParagraphStyle("b", parent=s["Normal"], fontName=BODY_FONT, fontSize=12,
                               leading=16, alignment=TA_LEFT, spaceAfter=7),
        "num": ParagraphStyle("n", parent=s["Normal"], fontName=BODY_FONT, fontSize=12,
                              leading=16, leftIndent=14, spaceAfter=5),
        "small": ParagraphStyle("s", parent=s["Normal"], fontName=BODY_FONT, fontSize=9,
                                textColor=SLATE, leading=12),
        "cell": ParagraphStyle("c", parent=s["Normal"], fontName=BODY_FONT, fontSize=9,
                               leading=11.5),
        "cellh": ParagraphStyle("ch", parent=s["Normal"], fontName=HEAD_FONT, fontSize=9,
                                textColor=colors.white, leading=11.5),
    }


def numbered(items, st):
    return [Paragraph(f"{i}. {t}", st["num"]) for i, t in enumerate(items, 1)]


def table(rows, widths, st, align_right=()):
    data = [[Paragraph(str(c), st["cellh"]) for c in rows[0]]]
    data += [[Paragraph(str(c), st["cell"]) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FA")]),
    ]
    for c in align_right:
        cmds.append(("ALIGN", (c, 1), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(cmds))
    return t


def fmt(v, ccy=""):
    if v is None:
        return "—"
    try:
        return (f"{ccy} {v:,.2f}" if ccy else f"{v:,.2f}").strip()
    except (TypeError, ValueError):
        return str(v)


def build(norm, var, verdict, out):
    st = styles()
    cfg = norm["comparison"]
    ccy = cfg.get("currency", "")
    doc_title = cfg.get("title", "Quote comparison")

    def page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
        canvas.setFont(BODY_FONT, 8)
        canvas.setFillColor(SLATE)
        canvas.drawString(20 * mm, 10 * mm, doc_title)
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    d = BaseDocTemplate(out, pagesize=A4, topMargin=20 * mm, bottomMargin=22 * mm,
                        leftMargin=20 * mm, rightMargin=20 * mm, title=doc_title)
    frame = Frame(20 * mm, 22 * mm, A4[0] - 40 * mm, A4[1] - 42 * mm, id="f")
    d.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=page)])
    W = A4[0] - 40 * mm

    f = []
    f.append(Paragraph(doc_title, st["title"]))
    f.append(Paragraph(
        f"Comparison currency {ccy} · basis {cfg.get('tax_basis', 'ex_tax')} · "
        f"{len(norm['quotes'])} quotes levelled to a common scope. "
        f"Evidence tags: [E] evidenced in the documents, [I] inferred with stated "
        f"reasoning, [U] not determinable — question listed.", st["sub"]))

    gate = norm.get("gate", {})
    if not gate.get("rankable"):
        f.append(Paragraph("Ranking withheld", st["h1"]))
        f.append(Paragraph(gate.get("reason", ""), st["body"]))
    elif verdict.get("recommendation"):
        f.append(Paragraph("Recommendation", st["h1"]))
        f.append(Paragraph(verdict["recommendation"], st["body"]))
        if verdict.get("confidence"):
            f.append(Paragraph(f"Confidence: {verdict['confidence']}.", st["body"]))
        if verdict.get("conditions"):
            f.append(Paragraph("Conditional on:", st["h2"]))
            f += numbered(verdict["conditions"], st)
        if gate.get("reason"):
            f.append(Paragraph(gate["reason"], st["small"]))

    # Headline vs normalized
    f.append(Paragraph("Headline against normalized", st["h1"]))
    rows = [["Vendor", "Stated total", "Ranked (levelled)", "Quarantined",
             "Non-firm", "Reconciliation"]]
    for q in norm["quotes"]:
        r = q.get("reconciliation") or {}
        note = "—"
        if r.get("status") == "mismatch":
            note = f"mismatch {r['difference']:+,.2f}"
        elif r.get("status") == "ok":
            note = "ties"
        elif r.get("status") == "not_comparable":
            note = "not comparable"
        rows.append([q["vendor"], fmt(r.get("stated")), fmt(q["ranked_total"]),
                     fmt(q["quarantined_total"]), fmt(q["non_firm_total"]), note])
    f.append(table(rows, [W * .21, W * .16, W * .17, W * .15, W * .14, W * .17],
                   st, align_right=(1, 2, 3, 4)))
    f.append(Spacer(1, 4))
    f.append(Paragraph("Ranked totals exclude quarantined and non-firm scope. "
                       "Stated totals are the vendors' own figures, shown only for "
                       "reconciliation.", st["small"]))

    # Gap contribution
    for c in var.get("contributions", []):
        f.append(Paragraph(f"What the gap to {c['vendor']} is made of", st["h1"]))
        f.append(Paragraph(
            f"Gap against {c['base']}: {fmt(c['gap'], ccy)}. The drivers below explain "
            f"{c['coverage_pct']}% of it; unexplained residual {fmt(c['unexplained_residual'], ccy)}.",
            st["body"]))
        rows = [["Scope item", "Cause", "Delta", "Share", "Cum."]]
        for drv in c["drivers"][:10]:
            rows.append([drv["map_key"], drv["cause"], fmt(drv["delta"]),
                         f"{drv['share_of_gap']:.1%}" if drv["share_of_gap"] else "—",
                         f"{drv['cumulative_coverage']:.1%}" if drv["cumulative_coverage"] else "—"])
        f.append(table(rows, [W * .34, W * .24, W * .17, W * .12, W * .13],
                       st, align_right=(2, 3, 4)))

    # Diagnosis
    if verdict.get("diagnosis"):
        f.append(Paragraph("Diagnosis — why the numbers differ", st["h1"]))
        for i, dg in enumerate(verdict["diagnosis"], 1):
            block = [Paragraph(
                f"{i}. <b>{dg.get('driver', '')}</b> — [{dg.get('tag', 'U')}] — "
                f"{dg.get('quantum', '')}", st["num"])]
            if dg.get("evidence"):
                block.append(Paragraph(dg["evidence"], st["small"]))
            if dg.get("action"):
                block.append(Paragraph(f"<b>Action:</b> {dg['action']}", st["small"]))
            block.append(Spacer(1, 5))
            f.append(KeepTogether(block))

    # Outliers
    ol = var.get("outliers", {})
    if ol.get("lines"):
        f.append(Paragraph("Rate outliers", st["h1"]))
        rows = [["Scope item", "Vendor", "Rate", "Cross-vendor mean", "Deviation"]]
        for o in ol["lines"][:12]:
            rows.append([o["map_key"], o["vendor"], fmt(o["rate"]),
                         fmt(o["cross_vendor_mean"]), f"{o['deviation_pct']:+.1f}%"])
        f.append(table(rows, [W * .34, W * .18, W * .16, W * .18, W * .14],
                       st, align_right=(2, 3, 4)))
        if ol.get("unbalanced_signature"):
            names = ", ".join(s["vendor"] for s in ol["unbalanced_signature"])
            f.append(Spacer(1, 4))
            f.append(Paragraph(
                f"{names} carries outliers in both directions on the same sheet. That is "
                f"the unbalanced-bidding signature: rates set low where quantities may "
                f"shrink and high where they may grow. Re-test the ranking against "
                f"plausible quantity variation before awarding.", st["body"]))

    # Ledger
    f.append(Paragraph("Inclusion ledger", st["h1"]))
    elements = []
    for q in norm["quotes"]:
        for e in q.get("inclusions", []) + q.get("exclusions", []):
            if e not in elements:
                elements.append(e)
    if elements:
        rows = [["Scope element"] + [q["vendor"] for q in norm["quotes"]]]
        for e in elements:
            row = [e]
            for q in norm["quotes"]:
                row.append("Included" if e in q.get("inclusions", [])
                           else "EXCLUDED" if e in q.get("exclusions", [])
                           else "not stated")
            rows.append(row)
        vw = (W * .58) / max(1, len(norm["quotes"]))
        f.append(table(rows, [W * .42] + [vw] * len(norm["quotes"]), st))
    else:
        f.append(Paragraph("No inclusions or exclusions were stated in any quote. That is "
                           "itself a finding — request an explicit scope statement from "
                           "every vendor before awarding.", st["body"]))

    # Quarantine
    qlines = [(q["vendor"], l) for q in norm["quotes"] for l in q["lines"] if l["quarantine"]]
    if qlines:
        f.append(Paragraph("Quarantined scope", st["h1"]))
        f.append(Paragraph(
            f"Excluded from ranked totals because it could not be levelled. "
            f"Quarantine ratio {norm.get('quarantine_ratio', 0):.1%}.", st["body"]))
        rows = [["Vendor", "Scope item", "Value", "Reason"]]
        for v, l in qlines:
            rows.append([v, l["map_key"], fmt(l["value"]), l.get("quarantine_reason") or "—"])
        f.append(table(rows, [W * .2, W * .34, W * .16, W * .30], st, align_right=(2,)))

    # Assumptions
    f.append(Paragraph("Assumption register", st["h1"]))
    if norm.get("assumptions"):
        rows = [["#", "Assumption", "Impact if wrong"]]
        for i, a in enumerate(norm["assumptions"], 1):
            rows.append([i, a.get("text", ""), a.get("impact_if_wrong", "—")])
        f.append(table(rows, [W * .06, W * .54, W * .40], st))
    else:
        f.append(Paragraph("No assumptions recorded.", st["body"]))

    if verdict.get("next_actions"):
        f.append(Paragraph("Next actions", st["h1"]))
        f += numbered(verdict["next_actions"], st)

    d.build(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("normalized")
    ap.add_argument("variance")
    ap.add_argument("--verdict", default=None)
    ap.add_argument("-o", "--output", default="comparison.pdf")
    args = ap.parse_args()

    norm = json.load(open(args.normalized))
    var = json.load(open(args.variance))
    verdict = json.load(open(args.verdict)) if args.verdict else {}
    build(norm, var, verdict, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
