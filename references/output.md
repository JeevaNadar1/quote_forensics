# Output — the three renderers

Ask which the user wants if not stated. Default to **Markdown in chat**; it is the fastest
to iterate against and the other two are one command away.

---

## Common structure

All three carry the same eight blocks, in this order. The order is deliberate: verdict
first for the reader who stops after 20 seconds, evidence after it for the one who does not.

1. **Verdict** — recommendation, confidence, margin over runner-up, conditions
2. **Headline vs normalized** — the table that shows what levelling changed
3. **Gap contribution** — ranked drivers, share of gap, coverage %
4. **Diagnosis** — per-driver, evidence-tagged, with actions
5. **Inclusion ledger** — the scope matrix
6. **Quarantine** — non-comparable scope and the question that releases each item
7. **Assumptions register** — every assumption made to level the quotes
8. **Next actions** — ask-list (buyer) or restructure plan (seller)

Blocks 5–7 are not appendices. They are where a challenged verdict is defended.

---

## 1. Markdown (chat)

1. Lead with a two-line answer before any table. The reader should know the recommendation
   before they scroll.
2. Numbered lists throughout, not bullets.
3. Tables for anything with more than two vendors and two attributes.
4. No callout or note blocks — fold caveats into body text.
5. Keep the headline-vs-normalized table visible without scrolling if at all possible.
   It is the single most persuasive object in the analysis.

---

## 2. Excel model — `scripts/build_xlsx.py`

Sheets, in order:

| Sheet | Contains |
|---|---|
| `Summary` | Verdict, weighted scores, headline vs normalized |
| `Levelled` | Full line-by-line comparison, one column per vendor |
| `Provenance` | Every line's source quote, page/row, verbatim original text |
| `Ledger` | Inclusion/exclusion matrix |
| `Quarantine` | Non-comparable scope + release question |
| `Assumptions` | Assumption register, each with impact if wrong |
| `Sensitivity` | Live weights and rate cells that recalculate |

Rules:

1. **Formulas, not pasted values**, wherever a number is derived. The buyer will change an
   assumption; the model must move.
2. The weights block on `Summary` is input-coloured and drives the score formulas, so the
   user can re-run the decision without re-running the skill.
3. `Provenance` is never omitted to save space. It is the sheet that survives an audit.
4. Freeze panes on header rows. Currency formatting per the source currency.

---

## 3. Print-ready PDF — `scripts/build_pdf.py`

Specification:

1. **A4 portrait**, 20mm margins, print-ready.
2. **Modern Minimalist palette** — light blue `#5DADE2` for headings and primary rules,
   slate gray `#708090` for secondary text and rules, light gray `#D3D3D3` for dividers.
3. **Professional-document typography** — serif body (Times New Roman / Garamond /
   Baskerville family), 12pt body. Headings may run sans for contrast on technical annexes.
4. Numbered lists throughout. No callout or note blocks.
5. No personal name in the footer unless explicitly requested. Footer carries page number
   and document title only.
6. Tables repeat header rows across page breaks. No row split across a page.
7. Evidence tags print as `[E]` / `[I]` / `[U]` with a legend on the first page they appear.

The PDF is the artefact that goes to a committee or a client. It must be defensible
standing alone, without the chat it came from — which is why blocks 5–7 are mandatory in
this renderer even when the user asks for something short.
