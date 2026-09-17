#!/usr/bin/env python3
"""Variance analysis: what the gap is actually made of.

Usage:
    python3 variance.py normalized.json [-o variance.json]

Produces:
  1. Contribution ranking — which lines create the gap between the cheapest quote
     and each other quote, ranked by rupees contributed, with cumulative coverage.
  2. Rate outliers — lines far from the cross-vendor mean, in both directions.
     Outliers in both directions on one sheet is the unbalanced-bidding signature.
  3. Coverage — what share of the gap the material lines explain. The residual is
     reported, never hidden.
  4. Weighted scores, run at the user's weights and at equal weights. A winner that
     changes between them is weight-driven, not evidence-driven.
"""

import argparse
import json
import statistics
from collections import OrderedDict, defaultdict

OUTLIER_THRESHOLD = 0.35      # 35% from cross-vendor mean
FALLBACK_WEIGHTS = {
    "price": 45, "scope_completeness": 15, "delivery": 10,
    "commercial_risk": 15, "capability": 10, "terms": 5,
}


def materiality(cfg, lowest_total):
    return (cfg.get("materiality_pct", 1.0) / 100.0) * lowest_total


def contribution(base, other, threshold):
    """Line-level decomposition of the gap between two quotes."""
    # Must match the ranked_total basis exactly: firm, non-quarantined lines only.
    # Including provisional or optional scope here produces a phantom residual.
    def ranked(q):
        return {l["map_key"]: l for l in q["lines"]
                if not l["quarantine"] and l.get("kind", "firm") == "firm"}

    bl, ol = ranked(base), ranked(other)

    rows, immaterial = [], 0.0
    for key in set(bl) | set(ol):
        b = bl.get(key, {}).get("value", 0.0)
        o = ol.get(key, {}).get("value", 0.0)
        delta = o - b
        if abs(delta) < threshold:
            immaterial += delta
            continue
        src = ol.get(key) or bl.get(key)
        if key not in bl:
            cause = "present only in " + other["vendor"]
        elif key not in ol:
            cause = "present only in " + base["vendor"]
        else:
            cause = "rate or quantity difference"
        rows.append(OrderedDict(
            map_key=key, cause=cause,
            base_value=round(b, 2), other_value=round(o, 2),
            delta=round(delta, 2),
            category=src.get("category", "Uncategorised"),
            confidence=src.get("confidence", "high"),
            verbatim=src.get("verbatim", ""),
        ))

    rows.sort(key=lambda r: abs(r["delta"]), reverse=True)
    gap = other["ranked_total"] - base["ranked_total"]

    running = 0.0
    for r in rows:
        running += r["delta"]
        r["share_of_gap"] = round(r["delta"] / gap, 4) if gap else None
        r["cumulative_coverage"] = round(running / gap, 4) if gap else None

    explained = sum(r["delta"] for r in rows)
    return OrderedDict(
        vendor=other["vendor"], base=base["vendor"],
        gap=round(gap, 2),
        explained=round(explained, 2),
        immaterial_aggregate=round(immaterial, 2),
        coverage_pct=round(explained / gap * 100, 1) if gap else None,
        unexplained_residual=round(gap - explained - immaterial, 2),
        drivers=rows,
    )


def outliers(quotes):
    by_key = defaultdict(dict)
    for q in quotes:
        for l in q["lines"]:
            if not l["quarantine"] and l.get("rate") is not None:
                by_key[l["map_key"]][q["vendor"]] = l["rate"]

    found = []
    for key, rates in by_key.items():
        if len(rates) < 3:
            continue
        mean = statistics.mean(rates.values())
        if mean == 0:
            continue
        for vendor, rate in rates.items():
            dev = (rate - mean) / mean
            if abs(dev) >= OUTLIER_THRESHOLD:
                found.append(OrderedDict(
                    map_key=key, vendor=vendor, rate=rate,
                    cross_vendor_mean=round(mean, 2),
                    deviation_pct=round(dev * 100, 1),
                    direction="above" if dev > 0 else "below",
                ))
    found.sort(key=lambda r: abs(r["deviation_pct"]), reverse=True)

    per_vendor = defaultdict(lambda: {"above": 0, "below": 0})
    for f in found:
        per_vendor[f["vendor"]][f["direction"]] += 1
    signature = [
        {"vendor": v, **c,
         "note": "outliers in both directions — test for unbalanced bidding"}
        for v, c in per_vendor.items() if c["above"] and c["below"]
    ]
    return {"lines": found, "unbalanced_signature": signature}


def score(quotes, weights):
    """Price scored on normalized ranked total; other criteria only where evidenced."""
    lowest = min(q["ranked_total"] for q in quotes)
    max_excl = max(len(q["exclusions"]) for q in quotes) or 1
    leads = [q["lead_time_days"] for q in quotes if q.get("lead_time_days")]
    max_lead = max(leads) if leads else None

    out = []
    for q in quotes:
        s, basis = {}, {}
        s["price"] = lowest / q["ranked_total"] * 100 if q["ranked_total"] else 0
        basis["price"] = "normalized ranked total"

        s["scope_completeness"] = (1 - len(q["exclusions"]) / max_excl) * 100
        basis["scope_completeness"] = f"{len(q['exclusions'])} stated exclusions"

        if max_lead and q.get("lead_time_days"):
            s["delivery"] = (1 - (q["lead_time_days"] - min(leads)) /
                             max(1, max_lead - min(leads))) * 100
            basis["delivery"] = f"{q['lead_time_days']} days"
        else:
            basis["delivery"] = "not evidenced — unscored"

        adv = sum(m.get("pct", 0) for m in q.get("payment_terms", [])
                  if (m.get("month_offset", 0) or 0) == 0)
        s["commercial_risk"] = max(0.0, 100 - adv)
        basis["commercial_risk"] = f"{adv:.0f}% payable at/before start"

        w = q.get("risk_terms", {}).get("warranty_months")
        if w is not None:
            best = max((x.get("risk_terms", {}).get("warranty_months") or 0)
                       for x in quotes) or 1
            s["terms"] = w / best * 100
            basis["terms"] = f"{w} month warranty"
        else:
            basis["terms"] = "not evidenced — unscored"

        basis["capability"] = "not evidenced in documents — unscored"

        active = {k: v for k, v in weights.items() if k in s}
        wsum = sum(active.values())
        total = sum(s[k] * active[k] for k in active) / wsum if wsum else 0
        out.append(OrderedDict(
            vendor=q["vendor"], total=round(total, 1),
            components={k: round(v, 1) for k, v in s.items()},
            basis=basis,
            unscored=[k for k in weights if k not in s],
        ))
    out.sort(key=lambda r: r["total"], reverse=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="variance.json")
    args = ap.parse_args()

    with open(args.input) as f:
        doc = json.load(f)

    cfg, quotes = doc["comparison"], doc["quotes"]
    quotes = [q for q in quotes if q["ranked_total"] > 0]
    base = min(quotes, key=lambda q: q["ranked_total"])
    thr = materiality(cfg, base["ranked_total"])

    user_w = cfg.get("weights") or FALLBACK_WEIGHTS
    equal_w = {k: 100 / len(user_w) for k in user_w}
    s_user, s_equal = score(quotes, user_w), score(quotes, equal_w)
    flip = s_user[0]["vendor"] != s_equal[0]["vendor"]

    result = OrderedDict(
        base_vendor=base["vendor"],
        materiality_threshold=round(thr, 2),
        gate=doc.get("gate"),
        contributions=[contribution(base, q, thr)
                       for q in quotes if q["vendor"] != base["vendor"]],
        outliers=outliers(quotes),
        scores_user_weights=s_user,
        scores_equal_weights=s_equal,
        weight_sensitivity={
            "winner_changes": flip,
            "note": ("Winner changes between your weights and equal weights — the result "
                     "is weight-driven, not evidence-driven. Report this.") if flip else
                    "Winner holds at both your weights and equal weights.",
        },
        weights_used=user_w,
    )

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"base (lowest ranked): {base['vendor']}  materiality {thr:,.2f}")
    for c in result["contributions"]:
        print(f"\n  vs {c['vendor']}: gap {c['gap']:+,.2f}  "
              f"coverage {c['coverage_pct']}%  residual {c['unexplained_residual']:+,.2f}")
        for d in c["drivers"][:5]:
            print(f"    {d['delta']:+14,.2f}  {d['share_of_gap']:>7.1%}  "
                  f"{d['map_key'][:44]}  [{d['cause']}]")
    if result["outliers"]["unbalanced_signature"]:
        print("\n  !! unbalanced-bidding signature:",
              result["outliers"]["unbalanced_signature"])
    print(f"\n  weight sensitivity: {result['weight_sensitivity']['note']}")
    print(f"  written -> {args.output}")


if __name__ == "__main__":
    main()
