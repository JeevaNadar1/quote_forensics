#!/usr/bin/env python3
"""Normalize quotes to a common basis and reconcile every stated total.

Usage:
    python3 normalize.py quotes.json [-o normalized.json]

Reads a file conforming to schemas/quote.schema.json. Emits a normalized document
consumed by variance.py, build_xlsx.py and build_pdf.py.

Design rules this file enforces:
  1. Vendor-stated totals are never outputs. Everything is recomputed.
  2. Lines without provenance are rejected, not silently dropped.
  3. Non-firm lines (provisional/optional/allowance) leave the ranked total.
  4. Quarantined value is measured against the quarantine ceiling and reported.
"""

import argparse
import json
import sys
from collections import OrderedDict

QUARANTINE_CEILING = 0.15   # >15% of lowest ranked total blocks ranking
RECONCILE_TOLERANCE = 0.005  # 0.5% before a stated-total mismatch is flagged


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def to_comparison_currency(amount, src_ccy, cfg):
    target = cfg["currency"]
    if not src_ccy or src_ccy == target:
        return amount, 1.0
    rates = cfg.get("fx_rates") or {}
    if src_ccy not in rates:
        fail(f"no fx_rate supplied for {src_ccy} -> {target}; refusing to guess")
    return amount * rates[src_ccy], rates[src_ccy]


def ex_tax(amount, tax_pct, basis):
    """Reduce a line to the ex-tax basis. Tax is added back once, at the end."""
    if basis == "inc_tax" and tax_pct:
        return amount / (1.0 + tax_pct / 100.0)
    return amount


def term_value(quote, ranked_total, cfg):
    """Value of payment terms as a cash-flow cost at the stated cost of capital.

    Returns None when no cost of capital was supplied — an unstated discount rate
    is not a reason to invent one.
    """
    coc = cfg.get("cost_of_capital_pct")
    terms = quote.get("payment_terms")
    if coc is None or not terms:
        return None
    monthly = (coc / 100.0) / 12.0
    npv = 0.0
    for m in terms:
        share = (m.get("pct", 0) / 100.0) * ranked_total
        offset = m.get("month_offset", 0) or 0
        npv += share / ((1.0 + monthly) ** offset)
    # Positive = costs more than paying entirely on completion at the last milestone.
    baseline_offset = max((m.get("month_offset", 0) or 0) for m in terms)
    baseline = ranked_total / ((1.0 + monthly) ** baseline_offset)
    return round(npv - baseline, 2)


def normalize_quote(quote, cfg):
    basis = cfg.get("tax_basis", "ex_tax")
    src_ccy = quote.get("currency") or cfg["currency"]

    lines, defects, fx_used = [], [], 1.0
    ranked = quarantined = non_firm = 0.0

    for idx, ln in enumerate(quote.get("lines", [])):
        prov = ln.get("provenance") or {}
        if not prov.get("verbatim"):
            defects.append(
                f"line {idx + 1} ('{ln.get('description', '?')[:40]}') has no provenance "
                f"— excluded from comparison, must be re-extracted"
            )
            continue

        # Recompute. The vendor's own amount is an input to reconcile, never a result.
        qty, rate = ln.get("qty"), ln.get("rate")
        if qty is not None and rate is not None:
            computed = qty * rate
        elif ln.get("amount") is not None:
            computed = float(ln["amount"])
        else:
            defects.append(f"line {idx + 1} has neither qty*rate nor amount")
            continue

        stated = ln.get("amount")
        line_mismatch = None
        if stated is not None and qty is not None and rate is not None:
            if abs(computed - stated) > max(1.0, abs(stated) * RECONCILE_TOLERANCE):
                line_mismatch = round(computed - stated, 2)

        value = ex_tax(computed, ln.get("tax_pct"), basis)
        value, fx_used = to_comparison_currency(value, src_ccy, cfg)
        value = round(value, 2)

        kind = ln.get("kind", "firm")
        is_q = bool(ln.get("quarantine"))
        if is_q:
            quarantined += value
        elif kind != "firm":
            non_firm += value
        else:
            ranked += value

        lines.append(OrderedDict(
            map_key=ln.get("map_key") or ln.get("description", "")[:60],
            description=ln.get("description", ""),
            category=ln.get("category", "Uncategorised"),
            qty=qty, uom=ln.get("uom"), rate=rate,
            value=value,
            kind=kind,
            quarantine=is_q,
            quarantine_reason=ln.get("quarantine_reason"),
            map_type=ln.get("map_type", "one_to_one"),
            confidence=ln.get("confidence", "high"),
            line_mismatch=line_mismatch,
            verbatim=prov["verbatim"],
            page=prov.get("page"),
            row=prov.get("row"),
        ))

    # Reconcile against the vendor's stated grand total.
    recon = None
    if quote.get("stated_total") is not None:
        stated_basis = quote.get("stated_total_basis", basis)
        st = float(quote["stated_total"])
        if stated_basis == "inc_tax" and basis == "ex_tax":
            rates = [l.get("tax_pct") for l in quote.get("lines", []) if l.get("tax_pct")]
            if len(set(rates)) == 1:
                st = st / (1.0 + rates[0] / 100.0)
            else:
                recon = {"status": "not_comparable",
                         "note": "stated total is tax-inclusive across mixed tax rates; "
                                 "cannot be reduced to ex-tax without the vendor's breakdown"}
        if recon is None:
            st, _ = to_comparison_currency(st, src_ccy, cfg)
            computed_all = ranked + quarantined + non_firm
            diff = round(computed_all - st, 2)
            flagged = abs(diff) > max(1.0, abs(st) * RECONCILE_TOLERANCE)
            recon = {
                "status": "mismatch" if flagged else "ok",
                "stated": round(st, 2),
                "computed": round(computed_all, 2),
                "difference": diff,
                "note": ("Vendor's total disagrees with the sum of their own lines. "
                         "Raise this before negotiating anything else.") if flagged else None,
            }

    out = OrderedDict(
        vendor=quote["vendor"],
        quote_ref=quote.get("quote_ref"),
        quote_date=quote.get("quote_date"),
        validity_days=quote.get("validity_days"),
        source_currency=src_ccy,
        fx_rate_applied=fx_used,
        lead_time_days=quote.get("lead_time_days"),
        incoterm=quote.get("incoterm"),
        ranked_total=round(ranked, 2),
        quarantined_total=round(quarantined, 2),
        non_firm_total=round(non_firm, 2),
        inclusions=quote.get("inclusions", []),
        exclusions=quote.get("exclusions", []),
        risk_terms=quote.get("risk_terms", {}),
        payment_terms=quote.get("payment_terms", []),
        reconciliation=recon,
        intake_defects=defects,
        lines=lines,
    )
    out["payment_term_cost"] = term_value(quote, out["ranked_total"], cfg)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="normalized.json")
    args = ap.parse_args()

    with open(args.input) as f:
        doc = json.load(f)

    cfg = doc.get("comparison") or fail("missing 'comparison' block")
    if not cfg.get("currency"):
        fail("comparison.currency is required")

    quotes = [normalize_quote(q, cfg) for q in doc.get("quotes", [])]
    if not quotes:
        fail("no quotes supplied")

    lowest = min(q["ranked_total"] for q in quotes if q["ranked_total"] > 0)
    total_q = sum(q["quarantined_total"] for q in quotes)
    ratio = total_q / lowest if lowest else 0.0

    if ratio > QUARANTINE_CEILING:
        gate = {"rankable": False, "reason": (
            f"Quarantined scope is {ratio:.1%} of the lowest ranked total, above the "
            f"{QUARANTINE_CEILING:.0%} ceiling. Ranking is not reportable. Resolve the "
            f"quarantine block with the vendors first.")}
    elif ratio > 0.05:
        gate = {"rankable": True, "reason": (
            f"Quarantined scope is {ratio:.1%} of the lowest ranked total. Verdict is "
            f"conditional on the quarantine block being resolved.")}
    else:
        gate = {"rankable": True, "reason": f"Quarantined scope {ratio:.1%} — immaterial."}

    result = OrderedDict(
        comparison=cfg,
        gate=gate,
        quarantine_ratio=round(ratio, 4),
        assumptions=doc.get("assumptions", []),
        quotes=quotes,
    )

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"normalized {len(quotes)} quotes -> {args.output}")
    for q in quotes:
        print(f"  {q['vendor']:<24} ranked {q['ranked_total']:>14,.2f}  "
              f"quarantined {q['quarantined_total']:>12,.2f}")
        r = q.get("reconciliation")
        if r and r.get("status") == "mismatch":
            print(f"    !! stated-total mismatch: {r['difference']:+,.2f}")
        for d in q["intake_defects"]:
            print(f"    !! {d}")
    print(f"  gate: {'RANKABLE' if gate['rankable'] else 'BLOCKED'} — {gate['reason']}")


if __name__ == "__main__":
    main()
