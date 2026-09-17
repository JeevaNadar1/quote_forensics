# Buyer mode — award and negotiate

Read at stages 6–7 when the user is choosing a vendor.

---

## The award verdict

Never a bare "pick B". Required shape:

```
RECOMMENDATION: [Vendor] at [normalized total]
Confidence: [high / medium / low] — [what would change it]
Margin over runner-up: [amount, % — and whether that exceeds the noise floor]

Conditional on:
1. [the assumption that, if wrong, flips the answer]
2. [the quarantined item that must be resolved first]
```

Rules:

1. **State the noise floor.** If the gap between first and second is smaller than the
   assumptions you made to level them, there is no winner on price. Say that. It is the
   honest and more useful answer, and it moves the decision to non-price criteria where it
   belongs.
2. **Run the flip test.** Name the single assumption that, if reversed, changes the
   recommendation. If none exists, the verdict is robust — say so, it is worth knowing.
3. **Separate price rank from value rank.** They diverge often. When they do, that
   divergence *is* the analysis.
4. **Include "award nothing yet"** as a live option whenever quarantine exceeds 5% or the
   spec was loose enough that vendors priced different things.

---

## Scoring beyond price

Weighted scoring only where the user sets weights, or with a visible fallback:

| Criterion | Fallback weight | Notes |
|---|---|---|
| Normalized price | 45% | After levelling, never headline |
| Scope completeness | 15% | Exclusion count and value |
| Delivery / lead time | 10% | Against the user's actual date |
| Commercial risk | 15% | Payment exposure, liability caps, LDs |
| Vendor capability | 10% | Only from evidence supplied |
| Terms quality | 5% | Warranty, escalation, validity |

1. Print the weights. Unprinted weights are a hidden thesis.
2. Run the result at the user's weights **and** at equal weights. If the winner changes,
   the answer is weight-driven, not evidence-driven — that is a finding, report it.
3. Never score vendor capability from general impressions of the company. Evidence in the
   documents, or no score.

---

## Negotiation levers — ranked by winnability

Do not hand over twenty asks. Hand over the four that move money.

| Lever | Typical yield | Winnability | Use when |
|---|---|---|---|
| Scope clarification on excluded items | Very high | High | Anything quarantined |
| Price match on the 3 worst line items | High | High | Unbalanced rates visible |
| Payment terms shift | Medium | High | Advance-heavy quote |
| Warranty extension in lieu of discount | Medium | High | Vendor guards headline price |
| Volume or term commitment for rate | High | Medium | You can actually commit |
| Escalation cap / validity extension | Medium | Medium | Long delivery window |
| Headline percentage discount | Low | Low | Last resort — invites padding next time |

**The core rule: negotiate line items, not totals.** "Can you do better?" yields 3% and
teaches the vendor to inflate next time. "Your rate on item 14 is 40% above the other two
quotes — explain or match" yields more and is hard to refuse without disclosure.

Target the **three lines that contribute most to the gap**, from the contribution ranking.
Not the three largest lines. Not forty lines.

---

## The ask-list

One table, vendor-ready, each row actionable:

| # | Item | Ask | Why it is defensible |
|---|---|---|---|
| 1 | Line 14, ducting | Rate justification or match to ₹X | 40% above both other quotes on identical spec |
| 2 | Commissioning | Confirm in scope, or price it | Ambiguous wording on p.3 |
| 3 | Payment | 30% advance → 15% | Market norm for this contract size |

Every ask carries its justification. An unjustified ask is a haggle; a justified one is
hard to refuse in writing.

---

## The redline

When rewriting the received quote into a counter-position:

1. **Preserve the vendor's own line structure and wording.** Changing their format makes
   comparison of their response impossible and signals you rewrote their offer.
2. Mark every change: `[AMENDED]`, `[ADDED — needs pricing]`, `[QUERY]`, `[DELETED]`.
3. Never delete a line silently. Strike it with a reason.
4. Attach the assumption register — every assumption you made while levelling. This is how
   the vendor corrects you cheaply instead of expensively.
5. State validity: how long your counter stands.

---

## The negotiation email

Short. Specific. Never adversarial — vendors who feel ambushed price risk into round two.

1. Thank, confirm receipt, state the decision timeline.
2. State that quotes are being levelled to a common basis (this alone changes vendor
   behaviour — it signals the exclusions trick will not work).
3. List the specific queries, numbered, with the line references.
4. Give a deadline and a format for the response.
5. Do not reveal other vendors' prices. It is bad practice, it is often contractually
   restricted, and it converts a negotiation into a race to the bottom on quality.

---

## Ethics floor

1. Do not fabricate a competing quote for leverage.
2. Do not share one vendor's pricing with another.
3. Do not solicit a bid from a vendor with no chance of winning purely to create pressure.

These are not decorative. They also fail commercially — vendors talk, and a buyer known for
this gets priced accordingly.
