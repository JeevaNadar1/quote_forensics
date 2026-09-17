# Domain: SaaS, licensing, cloud, subscriptions

Load when quotes are software licences, subscriptions, cloud commitments, or renewals.

---

## What differs here

1. **The horizon is the analysis.** Year-one price is close to meaningless. Compare total
   cost over a stated horizon — 3 years is the usual default — with renewal uplift,
   growth in the billable unit, and exit cost all inside it.
2. **The billable unit is where quotes diverge invisibly.** Per seat, per named user, per
   active user, per API call, per GB, per transaction, per core. Two quotes at the same
   headline can differ 3× at real usage. This must be normalized before anything else.
3. **The discount is a loan.** A large year-one discount that steps up at renewal is
   financing, not a price. Model the stepped curve, report the blended rate.
4. **Switching cost is the real lock-in.** Data egress, re-implementation, retraining,
   integration rebuild. A cheaper vendor with a harder exit is not cheaper; it is cheaper
   until the first renewal, at which point you have no leverage. Price the exit.

---

## Checks specific to this domain

1. **Usage projection.** Model low / expected / high. If the ranking flips between them,
   that is the finding. Ask for the user's actual growth assumption; do not invent one.
2. **Renewal uplift cap.** Uncapped renewal is an open cheque. A capped uplift is worth
   real money and is routinely negotiable at first signing — and almost never afterwards.
3. **Tier cliffs.** Which feature you actually need sits in which tier, and what forces an
   upgrade. Vendors price the cliff, not the tier.
4. **Overage rates.** Often several times the committed rate. Check what happens on
   exceeding commitment, and whether unused commitment rolls over.
5. **Implementation and onboarding** — one-off fees, professional services, data migration.
   Frequently excluded from the headline and comparable to a full year of licence.
6. **Support tiers.** Response times, named contacts, escalation paths. Standard support on
   a business-critical system is a risk position, not a saving.
7. **Committed-use discounts** in cloud: only a saving if the commitment is genuinely
   consumed. Price the unused-commitment scenario.
8. **Contract term and termination.** Auto-renewal windows, notice periods, termination for
   convenience. A 90-day notice window missed by a week is a full extra year.
9. **True-up mechanics.** How and when seat growth is billed, and at what rate.
10. **Data portability and exit.** Export format, assistance, retention after termination.
11. **Security, compliance and residency** — if required, a vendor without it is not a
    cheaper option, it is not an option.
12. **Price protection** across the term for added seats. Without it, expansion is at list.

---

## Reporting note

Produce a **year-by-year cost curve** across the horizon, per vendor, not a single total.
The shape of the curve is usually more decision-relevant than its sum, and it is the object
that makes a stepped-discount structure visible to a non-specialist in two seconds.
