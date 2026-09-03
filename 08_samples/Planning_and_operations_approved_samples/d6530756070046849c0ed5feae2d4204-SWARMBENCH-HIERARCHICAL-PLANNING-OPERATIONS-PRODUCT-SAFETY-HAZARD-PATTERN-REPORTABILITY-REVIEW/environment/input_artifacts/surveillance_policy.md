# Hazard Surveillance and Reportability Method (adopted, binding)

Northbridge Retail Group — Product Safety and Regulatory Affairs
Method revision 4.2. Cycle reference date (**as-of date**): **2026-07-06**.

This document is the method the group has adopted for turning public incident reports into
hazard patterns and reportability determinations. It is binding for this review. Where this
method and a coded field in the source data disagree, this method governs.

---

## 1. Scope

The review covers the incident reports in `/input_artifacts/incident_reports.csv`. Every
report in that file is in scope and must be worked. Reports concern products sold under
brands the group carries; `/input_artifacts/brand_register.csv` maps the brand string as it
was reported to the **brand family** the group tracks. Brand strings in the source are
entered by whoever filed the report and are inconsistent in spelling, casing and corporate
naming; always resolve a report to its brand family through the register rather than by
eyeballing the string.

---

## 2. Failure-mode families

Each incident is assigned exactly one **failure mode**, read from the consumer's own account
in `incident_description`. The coded `product_type` and `product_sub_category` fields
describe what the product *is*, not how it failed, and must not be used to set the failure
mode.

| Failure mode | What the account describes |
|---|---|
| `Ingestion or Choking` | A part, magnet, battery or fragment was swallowed, put in the mouth, or caused choking or aspiration. |
| `Electrical Shock or Arcing` | A person was shocked or an energised part arced, shorted, or was left exposed. |
| `Thermal or Fire` | The product overheated, smoked, smouldered, ignited, melted, scorched, or burned someone by heat. |
| `Mechanical Entrapment or Pinch` | A finger, hand, limb, hair or clothing was caught, pinched, crushed, entangled or amputated by a moving or closing part. |
| `Laceration or Sharp Edge` | A cut, puncture or laceration from a blade, burr, sharp edge, or from glass or ceramic that broke or shattered. |
| `Structural Collapse or Breakage` | A load-bearing element failed — a frame, weld, leg, rail or seam gave way, or the product collapsed, tipped or came apart. |
| `Chemical Exposure or Contamination` | Fumes, gas, chemical residue, mould, rust, or foreign material in or on the product or in food. |
| `Loss of Protective Function` | The product's own safety function failed to operate — an alarm or detector did not sound, a lock, latch, brake, interlock or automatic shut-off did not engage, or the product activated on its own. |
| `Other or Undetermined` | The account does not evidence any of the families above. This is the residual family, not a catch-all for accounts that are merely hard to read. |

**Precedence.** Where one account evidences more than one family, assign the family that
appears **earliest in the table above** (Ingestion or Choking first, Other or Undetermined
last). The order reflects how quickly the hazard can injure someone, not how prominent it is
in the narrative.

**Negated harm.** Accounts frequently say a harm did *not* occur ("thankfully no one was
injured", "there was no fire"). A negated mention is not evidence of that family.

---

## 3. Substantiated harm level

Each incident is assigned a **harm level** read from `incident_description`:

| Level | Meaning |
|---|---|
| `H0` | No personal harm described. Property damage alone is `H0`. |
| `H1` | Harm described but no professional treatment: redness, a mark, a minor burn, blister, bruise, scratch, soreness, or self-administered first aid. |
| `H2` | Treatment by a professional short of emergency care: urgent care, a doctor, clinic, dentist, stitches, sutures, a prescription, or an X-ray. |
| `H3` | Emergency or severe outcome: emergency department, ambulance, hospital admission, surgery, fracture, third-degree burn, loss of consciousness, or death. |

**The coded severity field is not authoritative.** `victim_severity_coded` is entered by the
person filing the report and is routinely wrong in both directions — reports describing an
emergency-room visit are filed as "Incident, No Injury", and reports describing no harm at
all are filed under a treatment category. Read the account and let it govern.

For the purpose of recording disagreement, the coded field maps onto these bands:

| `victim_severity_coded` | Band |
|---|---|
| `No Incident, No Injury` | H0 |
| `Incident, No Injury` | H0 |
| `Injury, No First Aid or Medical Attention Received` | H1 |
| `Injury, First Aid Received by Non-Medical Professional` | H1 |
| `Injury, Seen by Medical Professional` | H2 |
| `Injury, Emergency Department Treatment Received` | H3 |
| `Injury, Hospital Admission` | H3 |
| `Death` | H3 |
| `Injury, Level of care not known` | not comparable |
| `Unspecified` | not comparable |

An incident is flagged `severity_conflict = true` when the coded value maps to a band and the
harm level read from the account is a **different** band. Where the coded value is not
comparable, `severity_conflict` is `false`.

---

## 4. Company posture

Where `company_comment` is populated, the responding firm's filed response is read and
assigned exactly one **posture**. Where the field is empty the posture is `None`.

| Posture | What the response does |
|---|---|
| `Recall or Corrective Action Cited` | Points to a recall, corrective action, retrofit, stop-sale, or a warning/replacement/repair programme. |
| `Remedy Offered` | States that this consumer was or will be given a refund, replacement, repair, credit or equivalent, at no cost. |
| `Disputes or Deflects` | Attributes the incident to misuse, modification, assembly error or failure to follow the manual; or disputes that the product is the firm's, is genuine, or can be identified; or asserts the product performed as designed and no defect was found. |
| `Standards Assurance Only` | Asserts only that the product meets or exceeds applicable standards, is rigorously tested, or is built with multiple layers of protection — taking no position on this incident. |
| `Acknowledged Under Review` | Acknowledges receipt, thanks the reporter, or says the matter has been shared or is being reviewed, and nothing more. |
| `None` | No response was filed. |

**Precedence.** Responses routinely do several of these at once — a firm will recite its
standards compliance and then offer a replacement in the same paragraph. Where a response
supports more than one posture, assign the posture that appears **earliest in the table
above**.

---

## 5. Evidence grade

The evidence grade follows from the posture and the harm level:

| Condition | Grade |
|---|---|
| Posture is `Recall or Corrective Action Cited` or `Remedy Offered` | `Corroborated` |
| Posture is `Disputes or Deflects` | `Contested` |
| Otherwise, and harm level is `H1`, `H2` or `H3` | `Uncontested` |
| Otherwise (harm level `H0`) | `Insufficient` |

An incident is **countable** if its grade is `Corroborated` or `Uncontested`. `Contested` and
`Insufficient` incidents remain on the register and are reported, but they do not count
toward any reportability trigger.

---

## 6. Hazard patterns

A **hazard pattern** is the set of all in-scope incidents sharing the same
(`brand_family`, `failure_mode`) pair. Every incident belongs to exactly one pattern, and
every distinct pair observed in the corpus forms a pattern, including pairs with a single
incident.

Patterns are **not** confined to one product category. The same brand family and failure mode
recur across different categories of goods, and those incidents form one pattern. Reconciling
a pattern across the categories its incidents came from is part of the work.

---

## 7. Reportability trigger

A pattern is **triggered** when any of the following first becomes true. Only countable
incidents are considered.

- **Rule A** — at least **3** countable incidents fall within any rolling **365-day** window.
- **Rule B** — at least **2** countable incidents at harm level `H2` or higher fall within any
  rolling **540-day** window.
- **Rule C** — the pattern contains at least one countable incident at harm level `H3` **and**
  at least **2** countable incidents in total.

The **trigger date** is the earliest `report_date` at which a rule is satisfied — that is, the
report date of the incident whose arrival completes the rule. Where more than one rule is
satisfied, the trigger date is the earliest of their dates, and the recorded
**trigger rule** is the rule producing that earliest date (breaking a tie in the order A, B,
C). A pattern satisfying no rule has no trigger date and no trigger rule.

**Filing deadline** = trigger date + **10 calendar days**.

**Exposure days** = the number of days from the filing deadline to the as-of date, or `0` if
the deadline has not yet passed.

---

## 8. Review board docket

Every triggered pattern requires a dossier heard by the Product Safety Review Board before
anything is filed. The board sits on **business days** (Monday to Friday) and hears at most
**2** dossiers per sitting day. This cycle covers the **10** business days beginning on the
as-of date, so the cycle holds **20** board slots.

Triggered patterns are seated in this order:

1. **exposure days, descending** — the longest-standing obligations are heard first;
2. then **trigger date, ascending**;
3. then **pattern id, ascending**.

The first 20 patterns in that order are seated, two per business day, in order — slots 1 and 2
on the first business day, slots 3 and 4 on the second, and so on. Triggered patterns beyond
the twentieth are **not** seated this cycle.

---

## 9. Disposition

| Condition | Disposition |
|---|---|
| Triggered and seated in a board slot this cycle | `Board Docketed` |
| Triggered but beyond the cycle's board capacity | `Board Backlog` |
| Not triggered, and 2 or more countable incidents | `Monitor` |
| Not triggered, and fewer than 2 countable incidents | `Close No Action` |

The board capacity is a real constraint and it is not assumed to be sufficient. Where the
triggered inventory exceeds the slots the cycle holds, the shortfall is a finding of the
review and must be reported as such, with the patterns that go unheard named.
