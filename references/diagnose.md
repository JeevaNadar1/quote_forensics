# Diagnose — why the number is what it is

Read at stage 5. This is the stage the user actually wanted when they said "don't just
compare numbers".

**The job:** for each material delta, name the driver, tag the evidence, quantify the
share, and say what could be done about it.

---

## Method

1. Take the contribution-ranked deltas from `scripts/variance.py`.
2. Work top-down. Stop when reported drivers explain **≥80% of the total gap**, then state
   the coverage figure explicitly.
3. For each: driver → evidence tag → quantum → actionability.
4. Aggregate everything below materiality into one line. Do not itemise noise.

---

## The 14 drivers

Test in this order. The first four explain most real-world gaps.

### 1. Scope inclusion delta
Cheaper quote excludes something. **Most common driver by a wide margin.** Evidence:
inclusion ledger. Action: get it priced, or accept the buyer carries it.

### 2. Specification tier
Different grade, brand, model, or service tier behind an identically-worded line. Evidence:
make/model/grade in the quote. Where a quote says only "as per spec", that is **[U]** — the
single highest-yield question you can ask a vendor. Action: re-tender on a locked spec.

### 3. Quantity and break pricing
Rates conditional on volume that may not materialise. Evidence: stated break tables.
Action: confirm the rate holds at real volume, in writing.

### 4. Unit-of-measure or basis mismatch
Same number, different denominator. Evidence: normalization conversion log. If this driver
appears, the gap was partly an illusion — say so plainly.

### 5. Tax and duty treatment
Inclusive vs exclusive, rate differences, credit availability, import duty. Evidence: tax
lines. Usually collapses a gap rather than explaining one.

### 6. Labour vs material split
Two quotes at the same total can carry very different exposure. A material-heavy quote is
exposed to commodity movement; a labour-heavy one to availability and productivity.
Evidence: split where given, **[U]** where lump-summed. Action: ask for the split — refusal
is itself information.

### 7. Freight, packing, insurance, incoterms
Who carries goods and risk to site. Evidence: incoterm or delivery clause. A quote with no
delivery term is incomplete, not cheap.

### 8. Installation and commissioning
Frequently unstated, frequently the largest single omission. Evidence: explicit scope.
Action: never assume included.

### 9. Warranty, SLA and support depth
Duration, response time, parts vs labour, on-site vs remote, exclusions. Price the
difference over the horizon where the buyer would otherwise buy the cover. Evidence:
warranty clause.

### 10. Payment terms
Advance-heavy quotes carry a real cash cost and real counterparty exposure. Evidence:
payment schedule. Quantify at stated cost of capital; report the risk separately.

### 11. Escalation and validity
A firm price for 30 days is not the same product as a firm price for the contract term.
Evidence: validity and escalation clauses. A short validity on a long procurement is a
repricing option the vendor holds against you.

### 12. Overhead, contingency and margin loading
Visible as preliminaries, P&OH, contingency, or as uniform loading across lines. Evidence:
stated percentages, or **[I]** from rate patterns against `benchmarks.csv`. Without
benchmarks, a claim that margin is "high" is **[U]** — you cannot see their cost base.

### 13. Risk transfer
Liquidated damages, retention, indemnity caps, performance security, force majeure breadth,
termination rights. A quote that caps liability at fee value is cheaper because it is
selling less protection. Evidence: the clauses. Report as commercial risk, not legal advice.

### 14. Lead time and delivery premium
Speed costs money; delay costs more. Evidence: stated lead times. Action: where the buyer
has a hard date, price the slower quote's delay exposure into the comparison.

---

## Pattern signals worth naming

These are **[I]** unless the documents evidence them. Say so. Never state one as fact.

1. **Unbalanced bidding** — some rates far below market, others far above, total looks
   competitive. Exposure sits in whichever lines grow. Test by re-running the total against
   a plausible quantity variation; if the ranking flips, that is the finding.
2. **Loss-leader front loading** — cheap year one, expensive renewal or consumables. Test
   by extending the horizon.
3. **Under-scoping to win** — the cheapest quote is cheapest because it excludes the most.
   Test: count exclusions. Correlate with price rank. It is often a straight line.
4. **Round-number pricing** — suggests an estimate, not a build-up. Ask for the build-up.
5. **Copy-paste scope** — boilerplate not matched to the actual brief. Signals the vendor
   has not engaged; a change order is coming.
6. **Stated-total mismatch** — vendor's arithmetic disagrees with yours. Report the
   direction, the size, and which line causes it. Always raise this; it changes the
   conversation entirely.

---

## Writing a diagnosis line

Required shape:

> **[Driver]** — *[E/I/U]* — explains **₹X (N% of gap)**. *Evidence or question.*
> **Action:** what to do about it.

Worked examples:

> **Scope inclusion** — *[E]* — explains **₹4.2L (38% of gap)**. Vendor B excludes
> installation and commissioning ("Erection & commissioning in scope of client", p.3);
> Vendors A and C include it. **Action:** obtain B's price for it, or budget it separately.
> Until then B is not ₹4.2L cheaper.

> **Margin loading** — *[U]* — cannot be determined. No cost build-up supplied by any
> vendor and no benchmark file provided. **Action:** request rate analysis for the top 5
> lines by value. Refusal is itself a signal.

> **Specification tier** — *[I], medium confidence* — likely explains **₹1.1L (10%)**.
> A specifies a named premium brand; B and C say "equivalent make". Inference from the
> price pattern across three comparable lines, not from a stated spec. **Action:** lock the
> make in the tender and re-price.

---

## Prohibited moves

1. Asserting a cost structure you cannot see. You do not know their margin.
2. Converting an **[I]** into an **[E]** by writing it more confidently.
3. Explaining 100% of a gap. You will not have evidence for all of it. Report the
   unexplained residual as a number — it is one of the more useful outputs on the page.
4. Ranking drivers by how interesting they are rather than by rupees contributed.
