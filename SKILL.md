---
name: quote-forensics
description: Compare, diagnose and rewrite commercial quotations, bids, tenders, estimates and vendor proposals. Use this skill whenever the user has two or more quotes, bids, rate cards, BOQs, SOW pricing sheets, renewal offers or supplier proposals and wants to know which is better, why one is cheaper or dearer, what a price gap is actually made of, whether a quote is padded or under-scoped, what to negotiate, or how to restructure a quote they are issuing. Triggers on "compare these quotes", "which vendor should I pick", "is this quote fair", "why is this so expensive", "level these bids", "review this quotation", "help me negotiate this price", "make my quote more competitive", and on any message where two or more priced offers are pasted, uploaded or attached. Works buyer-side (award a contract) and seller-side (win one). Do NOT use for pure financial modelling, invoice reconciliation, or accounting close.
---

# Quote Forensics

Levels offers to a common basis, recomputes every number, explains
each material gap with traceable evidence, then awards or restructures.

**The governing principle:** most apparent price differences are scope differences.
A comparison that skips normalization is not a fast comparison — it is a wrong one.

---

## Mode switch (decide first, one line, say which)

| Mode | User is | Terminal output |
|---|---|---|
| **BUYER** | Receiving quotes, choosing a vendor | Award verdict + negotiation ask-list + redline |
| **SELLER** | Issuing quotes, competing for work | Competitiveness read + restructured quote |
| **AUDIT** | Reviewing one quote alone, no comparator | Padding/gap findings + questions to ask |

If unclear, ask once. Never blend BUYER and SELLER output in one response.

---

## Pipeline

```
INTAKE → NORMALIZE → RECONCILE → COMPARE → DIAGNOSE → RECOMMEND → REWRITE
```

Stages 1–5 always run. Stage 6 runs on request or when a decision is clearly wanted.
Stage 7 is gated — offer it, build it when asked.

| Stage | Does | Read |
|---|---|---|
| 1 INTAKE | Extract every line to schema, **verbatim** wording preserved | `schemas/quote.schema.json` |
| 2 NORMALIZE | Common basis: tax, UoM, currency, inclusions, horizon | `references/normalize.md` |
| 3 RECONCILE | Recompute all arithmetic, diff against vendor's stated totals | `scripts/normalize.py` |
| 4 COMPARE | Variance + **contribution ranking** of the gap | `scripts/variance.py` |
| 5 DIAGNOSE | Attribute each material delta to a driver, with evidence tier | `references/diagnose.md` |
| 6 RECOMMEND | Award logic / positioning | `references/buyer.md` or `references/seller.md` |
| 7 REWRITE | Counter-quote redline, ask-list, or restructured quote | same |

Domain packs, load only on match: `references/domains/boq.md` (construction, civil,
fit-out, MEP), `saas.md` (software, licences, subscriptions, cloud),
`goods.md` (equipment, materials, manufacturing, distribution).

Renderers: `references/output.md`.

---

## Context preservation — the non-negotiable

Every normalized line carries **provenance**: source quote, page or row, and the
vendor's original wording, unparaphrased.

1. Never restate a line in your own words and then reason from your restatement.
2. Never merge two vendor lines into one comparison row without recording both source strings.
3. When a verdict is challenged, you must be able to produce the sentence it came from.

Paraphrase is where context dies. The quote's own language is the primary source; your
summary is a view over it, never a replacement for it.

---

## Evidence tiering — the anti-hallucination rule

Every causal claim about *why* a price is what it is gets exactly one tag:

| Tag | Means | Requirement |
|---|---|---|
| **[E] Evidenced** | Traceable to text or arithmetic in the documents | Cite the line or quote the phrase |
| **[I] Inferred** | Derived from patterns in the data | State the inference chain and confidence |
| **[U] Unknown** | Not determinable from what was supplied | State the exact question to ask the vendor |

**[U] is a correct, frequent, valuable answer.** A price gap with no visible cause is a
finding — it is the single most common signal of undisclosed scope or padding. Never
manufacture a plausible reason to avoid writing [U]. An invented rationale in a
procurement decision is worse than no rationale, because it gets acted on.

Untagged causal claims are a defect. Fix them before shipping the response.

---

## Hard stops

1. **No comparison before normalization.** If scope cannot be levelled, say so and stop.
2. **No total you did not recompute.** Vendor-stated totals are inputs, never outputs.
3. **Quarantine ceiling.** If non-comparable scope exceeds **15% of the lowest normalized
   total**, refuse to rank. Report what must be obtained from vendors first. A ranking
   built on 30% unmatched scope is noise wearing a table.
4. **No live market pricing.** You have no access to current market rates unless the user
   supplies `benchmarks.csv`. Say "no benchmark" rather than guessing a fair price.
5. **No legal opinion.** Flag risky clauses as commercial risk; do not opine on
   enforceability.
6. **Arithmetic is computed, not read.** Run the scripts. Eyeballed cross-vendor
   multiplication is a known error source.

---

## Materiality

Default threshold: a delta is material at **≥1% of the lowest normalized comparable
total**, or **≥15% of that line's own cross-vendor mean**, whichever is smaller.
Below threshold, aggregate into "immaterial variance" and move on.

Rationale: a 40-line diagnosis reads as noise. Five ranked drivers covering 80% of the
gap gets acted on. Always report what share of the total gap the reported drivers explain.

---

## Refusals and honesty

1. If the quotes are for genuinely different things, say they are not comparable and
   explain what is actually being asked — that is a scoping decision, not a price decision.
2. If a document is illegible or truncated, list what you could not read before analysing.
   Never silently drop a line item.
3. If the recommendation is close, say it is close. Manufactured decisiveness on a 2%
   gap is false precision.
