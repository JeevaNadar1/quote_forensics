# Normalize — scope levelling

Read at stage 2. This is the stage that makes every later stage valid. Nothing downstream
survives a normalization error.

---

## The seven axes

Level every quote on all seven before any number is compared. Skipping one silently is
how a "20% cheaper" vendor turns out to be 8% dearer.

### 1. Tax basis

1. Reduce everything to **ex-tax** as the comparison basis. Tax is added back once, at the
   end, at the applicable rate per line.
2. Flag mixed-rate situations: goods and services in one quote can attract different
   rates, and a vendor quoting a single blended rate may be wrong.
3. Where input credit is available to the buyer, tax is not a cost — it is a cash-flow
   timing item. Say which treatment you applied. Never switch silently mid-analysis.
4. A vendor who quotes inclusive and one who quotes exclusive are not 18% apart; they are
   0% apart. This is the most common false delta in existence.

### 2. Unit of measure

1. Convert to a single UoM per comparison row. Record the conversion factor used.
2. Where conversion is lossy or contested (sqft of finished area vs carpet area, per-seat
   vs per-user, per-tonne vs per-piece), do **not** convert. Quarantine and ask.
3. Watch for the same UoM meaning different things: "per day" at 8 hours vs 9 hours is a
   12.5% rate difference hiding inside an identical-looking number.

### 3. Currency

1. Convert at a single stated rate, with the date. Print the rate in the output.
2. Never silently absorb FX. A quote in foreign currency carries FX risk that the local
   quote does not — that risk is a real cost and belongs in the risk column, not the price.
3. If the contract will be paid over time, note that the rate applies at payment, not award.

### 4. Scope inclusions and exclusions

The **inclusion ledger** is the centrepiece of this stage. Build it as a matrix:

| Scope element | Vendor A | Vendor B | Vendor C | Treatment |
|---|---|---|---|---|
| Freight to site | Included | Excluded, ₹— | Included | Add B's estimate or quarantine |
| Installation | Included | Included | Excluded | Add C or quarantine |
| Warranty | 24 mo | 12 mo | 24 mo | Price the 12-month gap or flag |

1. Read the exclusions list before the price list. Exclusions are where quotes are won.
2. Every element present in one quote and absent in another gets an explicit treatment:
   **added** (with a sourced figure), **deducted** (from the richer quote), or
   **quarantined** (non-comparable, excluded from the ranked total and reported separately).
3. Never treat an absent line as free. Absent means "someone will pay for this later",
   and that someone is the buyer.
4. "As per standard practice", "as required", "to be finalised" and provisional sums are
   **not** scope. They are open-ended exposure. Quarantine and list as a question.

### 5. Time horizon

1. Compare over the same period. A 3-year subscription against a perpetual licence needs
   a stated horizon — pick one, justify it, run the alternative if the verdict flips.
2. Include renewal, escalation and refresh inside the horizon. A cheap year one with a
   contractual uplift is a financing structure, not a discount.
3. Where horizons differ irreconcilably, report both and say which horizon changes the answer.

### 6. Payment terms

1. Terms have quantifiable value. Discount cash flows at the user's stated cost of capital;
   if none is stated, use a clearly-labelled placeholder and show sensitivity.
2. Advance payment is both a cost and a **risk transfer** — money paid before delivery is
   exposure, not just timing. Report it in the risk column as well.
3. Retention, milestone gates and payment-on-acceptance are buyer protections with real
   value. A quote that waives them is more expensive than it looks.

### 7. Quantity basis

1. Confirm all vendors priced the same quantities. Quantity drift between quotes is common
   and is usually an error, not a strategy — but occasionally it is a strategy.
2. Where quantities differ, rebase to unit rates and compare those. Report the quantity
   discrepancy separately as an intake defect.
3. Where a vendor priced a break quantity you did not ask for, that rate is conditional.
   Mark it. It evaporates at the real volume.

---

## Line mapping

Vendors never use the same line structure. Map with these rules:

1. **One-to-one** — same scope, different words. Map, keep both source strings.
2. **Many-to-one** — one vendor itemises what another bundles. Roll the itemised side up
   to the bundled level. **Never** split a bundled price by assumption — that invents data.
3. **One-to-none** — present in one quote only. This is the inclusion ledger's job. It is
   never a rounding detail.
4. **Fuzzy** — plausibly the same scope, wording ambiguous. Map it, tag the row
   `confidence: low`, and list it in the questions output. Do not hide the ambiguity in a
   confident-looking table.

Never force a map to make the table tidy. An honest "unmatched" row is more valuable than
a tidy wrong one.

---

## The quarantine rule

Quarantined value is scope that cannot be levelled. It is excluded from ranked totals and
reported as its own block, with the specific question that would release it.

Compute `quarantine_ratio = quarantined_value / lowest_normalized_total`.

1. **< 5%** — proceed, footnote it.
2. **5–15%** — proceed, but state that the verdict is conditional and name the condition.
3. **> 15%** — **stop**. Do not rank. Issue the question list instead. Ranking here would
   be a coin-flip dressed as analysis, and it will be believed.

---

## Output of this stage

A levelled sheet where every row has: comparison label, per-vendor normalized value,
per-vendor original verbatim string, map type, confidence, and treatment applied. Plus the
inclusion ledger, the quarantine block, and every assumption made, listed — not buried.

If you made an assumption to make two numbers comparable, that assumption is a finding.
Print it.
