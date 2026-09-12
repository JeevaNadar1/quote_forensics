# Quote Forensics

A Claude Skill for comparing, diagnosing and rewriting commercial quotations, bids,
tenders and vendor proposals.

Most quote comparisons fail the same way: someone lines up three totals, picks the
smallest, and discovers six months later that it was the smallest because it excluded the
most. This skill exists to stop that.

**Governing principle: most apparent price differences are scope differences.** A
comparison that skips normalization is not a fast comparison, it is a wrong one.

---

## What it does

1. **Levels** quotes to a common basis across seven axes — tax, unit of measure, currency,
   scope inclusions, time horizon, payment terms, quantity basis.
2. **Recomputes** every number and reconciles it against the vendor's own stated total.
   Mismatches between the two are reported as findings, because they usually are one.
3. **Ranks the gap by contribution** — which specific lines create the difference, and what
   share each contributes. You negotiate the three lines that matter, not forty.
4. **Diagnoses** each material delta against 14 price drivers, with every causal claim
   tagged as evidenced, inferred, or unknown.
5. **Recommends** — an award verdict with a stated confidence and a flip test (buyer), or a
   competitiveness read and restructuring plan (seller).
6. **Rewrites** — a counter-quote redline and vendor ask-list, or a restructured quote that
   wins without gutting margin.

---

## Why it doesn't hallucinate reasons

The failure mode of any LLM asked "why is this quote expensive" is a fluent, plausible,
invented answer. Three structural defences:

1. **Mandatory provenance.** Every compared line carries the vendor's verbatim original
   wording, its page and its row. The skill never reasons from its own paraphrase. Any
   verdict can be traced back to the sentence it came from.
2. **Evidence tiering.** Every causal claim is tagged `[E]` evidenced, `[I]` inferred with
   a stated inference chain, or `[U]` unknown with the exact question to ask the vendor.
   `[U]` is a correct and frequent output — a price gap with no visible cause is itself one
   of the strongest signals of undisclosed scope.
3. **Reported residual.** The skill explains what it can and prints the unexplained
   remainder as a number. It never manufactures coverage to reach 100%.

Plus a quarantine ceiling: if non-comparable scope exceeds 15% of the lowest normalized
total, the skill **refuses to rank** and issues a question list instead. A ranking built on
30% unmatched scope is a coin flip that will be believed.

---

## Install

**Claude.ai / Claude Desktop** — upload `quote-forensics.skill` in Settings → Capabilities → Skills.

**Claude Code** — clone into your skills directory:

```bash
git clone https://github.com/<you>/quote-forensics.git ~/.claude/skills/quote-forensics
```

**Standalone** — the scripts run without Claude:

```bash
pip install openpyxl reportlab
python3 scripts/normalize.py  examples/sample_quotes.json -o normalized.json
python3 scripts/variance.py   normalized.json             -o variance.json
python3 scripts/build_xlsx.py normalized.json variance.json -o comparison.xlsx
python3 scripts/build_pdf.py  normalized.json variance.json --verdict verdict.json -o comparison.pdf
```

---

## Usage

Paste, upload or attach two or more quotes and say what you want:

```
Compare these three HVAC quotes and tell me which to award.
Why is vendor B 18% cheaper?
Level these bids — I think one of them is under-scoped.
Make my quote more competitive without dropping the price.
Review this single quote, I have nothing to compare it against.
```

Three modes, chosen at the top of every run:

| Mode | You are | Output |
|---|---|---|
| **Buyer** | Receiving quotes | Award verdict, negotiation ask-list, redline |
| **Seller** | Issuing quotes | Competitiveness read, restructured quote |
| **Audit** | Reviewing one quote alone | Padding and gap findings, questions to ask |

---

## Structure

```
quote-forensics/
├── SKILL.md                      core protocol, mode switch, hard stops
├── references/
│   ├── normalize.md              the seven levelling axes, mapping, quarantine
│   ├── diagnose.md               14 price drivers, evidence discipline
│   ├── buyer.md                  award logic, negotiation levers, redline
│   ├── seller.md                 9 restructuring moves before discounting
│   ├── output.md                 the three renderers
│   └── domains/
│       ├── boq.md                construction, fit-out, MEP, unbalanced bidding
│       ├── saas.md               licences, subscriptions, cloud, horizon modelling
│       └── goods.md              equipment, materials, landed and life-cycle cost
├── schemas/quote.schema.json     strict intake schema, provenance mandatory
├── scripts/
│   ├── normalize.py              levelling + arithmetic reconciliation
│   ├── variance.py               contribution ranking, outliers, weighted scoring
│   ├── build_xlsx.py             7-sheet Excel model with live formulas
│   └── build_pdf.py              A4 print-ready report
└── examples/                     worked 3-vendor comparison, end to end
```

Progressive disclosure: `SKILL.md` is the only file always loaded. References load on
demand, domain packs only on domain match.

---

## Outputs

1. **Markdown** — analysis in chat, fastest to iterate against.
2. **Excel** — seven sheets including a Provenance sheet and a live Sensitivity sheet, so
   the recipient can change a weight and watch the ranking move. Derived numbers are
   formulas, not pasted values.
3. **PDF** — A4 print-ready, for a committee or a client. Carries the ledger, quarantine
   and assumption register regardless of length, because it has to be defensible standing
   alone.

---

## Worked example

`examples/` contains a real-shaped three-vendor HVAC comparison. Running it surfaces:

1. The cheapest headline quote is **not** the cheapest offer — 70.6% of its apparent
   advantage is installation scope it excluded.
2. **Two vendors' own grand totals disagree with the sum of their own line items**
   (+INR 78,000 and −INR 110,000). Recomputation catches what eyeballing does not.
3. A vendor low on equipment and high on piping — a rate pattern worth a question.
4. A margin claim the skill **refuses to make**, because no cost build-up was supplied.

---

## Limits, stated plainly

1. No live market pricing. Supply `benchmarks.csv` or accept that "is this a fair price"
   is answered from the documents only.
2. No legal opinion. Risky clauses are flagged as commercial risk, not adjudicated.
3. It cannot see a vendor's cost base. Any claim about their margin is `[I]` at best and
   usually `[U]`.
4. Extraction quality bounds everything. Garbage intake, garbage verdict — which is why
   intake defects are reported rather than silently dropped.

---

## License

MIT.
