# CBAM desk reference, Scheldt Quay Customs Services NV

This is the desk manual for the carbon border position. It settles every question of method for
the first half of 2026. Where it and your instinct disagree, follow it. Where it is silent, say so
in the deliverable rather than inventing a rule.

The mechanism itself is Regulation (EU) 2023/956 as amended, and the default values are those the
Commission adopted in Implementing Regulation (EU) 2025/2621 as corrected by Implementing
Regulation (EU) 2026/1740. What follows restates those rules in the form the desk works them, with
the arithmetic the desk uses written out. The citations at the end let anyone check a rule against
its published source.

## 1. What the desk is closing

Scheldt Quay is an indirect customs representative and the authorised CBAM declarant for the
twelve importers on `reference/importer_register.csv`. The period is 1 January 2026 to 30 June
2026. Every consignment released for free circulation in that period on one of the declarations in
`customs_entries/` has to be settled: whether it falls inside the mechanism, what its embedded
emissions are, and what obligation the importer it was released for now carries.

The declaration for the year is not due until 30 September 2027 and certificates cannot be bought
before February 2027. This close exists so that the position is known now, while the supplier data
can still be fixed.

## 2. Which lines fall inside the mechanism

A goods line is inside the mechanism only if both of these hold.

**The code is a covered good.** `reference/covered_goods.csv` carries the codes. A line whose
commodity code is marked `no` in that file is outside the mechanism and the scope basis is
`code_not_covered`.

**The customs procedure released the goods.** Only procedures `40 00` and `42 00` release goods
for free circulation. Procedure `51 00` (inward processing), `53 00` (temporary admission) and
`61 00` (re-import of returned goods) leave the goods outside the mechanism, and the scope basis is
`procedure_excluded`. The procedure is the one printed on the item of the declaration. The entry
summary export carries a procedure column and it is not reliable.

The procedure test is applied first. A line that is out of scope for either reason carries no
emissions figure at all: leave the emissions columns empty rather than computing a number that
does not arise, and record its scope basis.

For a line inside the mechanism, the scope basis is `in_scope`.

## 3. Net mass

The net mass that governs is the net mass printed on the item of the declaration, in kilograms.
Convert to tonnes and carry three decimals. The net mass column in the entry summary export drifts
from the declarations and does not govern.

## 4. Country of origin

The country of origin decides which published default values a line may take, and it is settled in
this order.

1. Where a valid proof of origin is on file against that item of that declaration, the country it
   certifies governs and the origin basis is `proof_of_origin`.
2. Where no valid proof displaces it, the country of origin declared on the item governs and the
   origin basis is `entry_declared`. The country of dispatch is not the country of origin, and the
   origin column of the entry summary export repeats the dispatch country.
3. Where a document on the file contradicts the declared origin and no valid proof settles the
   point, the origin is not established. The origin basis is `not_established` and the line takes
   the Annex IV highest default value under section 8, whatever the operator has reported.

A proof of origin is valid unless the desk has recorded a defect on the face of it. The defects
that make a proof incapable of settling origin are: it is unsigned or unsealed by the issuing
authority; it had expired before the date of release; it was issued by a person or body not
competent to certify origin; or it refers to a consignment other than the one released. A proof
carrying one of those defects is retained on the file and the declared origin stands.

## 5. When an operator's own figures may be used

Actual embedded emissions may be used for a good only where the operator's communication for the
installation that produced it is admissible. Admissibility is tested condition by condition in the
order below, and the first condition that fails is the one recorded as the failing condition. If
no condition fails, the report is admissible.

**A1.** An operator communication for that installation and that good is on file, and the
reporting period it states covers the whole of 1 January 2026 to 30 June 2026. A communication
that starts later than 1 January 2026 or ends earlier than 30 June 2026 fails this condition,
whatever else it contains.

**A2.** A verification report for that communication is on file and its opinion is
`verified with reasonable assurance`. An opinion of `verified with qualifications`, `adverse` or
`unable to verify`, and the absence of any verification report, all fail this condition.

**A3.** The accreditation of the verification body was live on the date the opinion was signed.
`reference/accreditation_register.csv` carries the validity dates and any suspension window. A
signature date before `valid_from`, after `valid_to`, or inside a suspension window fails this
condition.

**A4.** The accreditation of that verification body covers the sector of the installation. The
sectors in scope are on the same register.

**A5.** The declared boundary is complete for the route the installation says it operates.
`reference/production_routes.csv` gives, for each code and route, the processes the route requires
inside the boundary and the precursor codes the route requires to be reported. A communication
that omits one of those processes from its boundary, or that reports no consumption of a precursor
code the route requires, fails this condition.

**A6.** The verification report records no material misstatement that was left unresolved at the
date it was issued.

Where two verification reports are on file for the same communication, the later one governs in
full and the earlier one is spent.

An inadmissible communication is not discarded. Its figures are still read, because the exposure
that a remediation would release is measured against them under section 12.

## 6. Deriving specific embedded emissions

For an installation whose communication is admissible, the specific embedded emissions of its good
are

    SEE_direct = attributed direct emissions / activity level + sum over precursors of
                 (SEE_direct of the precursor x tonnes of precursor per tonne of product)

and the same expression with the indirect figures for SEE_indirect. Carry four decimals.

A precursor carries the derived figure of the installation that made it where that installation's
own communication is admissible, and the published default value for its own code and its own
country where it is not. An inadmissible link takes the default for that link alone. It does not
push the good that consumed it onto defaults.

Precursor consumption is reported three ways and all three mean the same thing once normalised.
A specific consumption is already tonnes per tonne of product. A total quantity consumed in the
period is divided by the activity level for the period. A percentage of the mass of product is
divided by one hundred.

The figure an operator prints for its own specific embedded emissions is its own arithmetic on its
own direct emissions and its own production. It does not carry the precursors and it is not the
figure the desk uses.

## 7. Indirect emissions

Indirect emissions are carried for cement and fertilisers. They are not carried for iron and
steel, for aluminium or for hydrogen, and the Commission prints `N/A` in the indirect column for
those sectors. For a good in a sector that does not carry indirect emissions, the applied indirect
figure is zero, whatever the operator's communication states.

The applied figure for a line is the direct figure plus the indirect figure.

## 8. Resolving a default value

Where actual figures may not be used, the line takes a published default value, resolved in this
order against `reference/commission_default_values.csv` and
`reference/commission_annex_iv_values.csv`.

- The origin is not established: the Annex IV highest default value, basis `default_annex_iv`.
- The origin is a country that has rows in the default value file: the row for that country and
  that code, basis `default_country`.
- The origin is a country with no rows in that file at all: the row for
  `Other Countries and Territories` and that code, basis `default_other_countries`.
- The country has rows but not for that code, or the row for that code carries `-` rather than a
  figure: the Annex IV highest default value, basis `default_annex_iv`.

Where the Annex IV value is used for a good in a sector that carries indirect emissions, the
highest default value is the direct figure and the same figure is carried again as the indirect
figure, because the published Annex IV column is a single total for the good.

Where actual figures are used, the basis is `actual`.

## 9. Embedded emissions of a line

    embedded emissions in tonnes CO2e = applied specific embedded emissions x net mass in tonnes

Carry three decimals.

## 10. Carbon price paid in the country of production

A claim in `carbon_price_claims/` reduces the obligation only where every condition below holds.
The first condition that fails is the one recorded.

**P1.** An attestation by an independent person is on file with the claim.

**P2.** No rebate, refund or other compensation was received for the amount claimed. A rebate
disclosed anywhere on the file removes the claim, whatever the claim form itself says.

**P3.** The period the payment relates to overlaps the reporting period.

**P4.** At least one installation the claim names is the supplier installation of a line that is
inside the mechanism and was released for an importer above the mass threshold of section 11.

**P5.** The charge is an explicit carbon price. An emissions trading system and a carbon tax are
explicit carbon prices. An energy excise and a production levy are not.

An admitted claim is converted at the reference rate on `reference/fx_reference_rates.csv`, which
carries units of the local currency per euro, and then expressed in tonnes:

    deduction in tonnes = amount in euro / certificate price assumption x phase-in factor

Round to three decimals. The claim is then allocated across the importers whose counted
consignments it covers, pro rata by the embedded emissions of those consignments.

A claim covering an importer that is below the mass threshold of section 11 allocates nothing to
that importer, because that importer carries no obligation to reduce.

## 11. The mass threshold and the certificate position

The threshold is a property of the importer, not of a line. For each importer, add the net mass of
every line released for that importer inside the mechanism in the calendar year. An importer whose
cumulative net mass is fifty tonnes or less is below the threshold and carries no obligation:
report its emissions but set its adjusted emissions, its deduction and its certificates to zero.
Lines outside the mechanism are not counted towards the threshold.

For an importer above the threshold:

    adjusted emissions   = total embedded emissions x 0.025
    certificates due     = adjusted emissions - the deduction allocated to that importer,
                           and never less than zero
    certificates to buy  = certificates due rounded up to the next whole certificate

`reference/desk_parameters.csv` carries the phase-in factor, the certificate price assumption and
the threshold.

## 12. The remediation programme

Every installation whose communication was inadmissible is a candidate for one remediation action,
referenced `REM-` followed by the numeric part of the installation identifier.

The action type follows the failing condition, and the effort it costs in engagement slots is on
`reference/remediation_effort.csv`.

The exposure a remediation would release is the difference the action would make to this position:
the embedded emissions the affected lines carry now, less the embedded emissions the same lines
would carry if that one communication became admissible and nothing else changed. Only lines
inside the mechanism, released for an importer above the threshold, and whose figure depends on
that installation, are affected. A line depends on an installation when the installation produced
its good, or when the installation made a precursor that a chain of admissible communications
carries into that good. Round to three decimals. The figure can be negative, and a negative
figure means the actual data is worse than the published default.

Actions are ranked by exposure released per engagement slot, highest first, and ties are broken by
installation identifier ascending.

There are four monthly waves on `reference/remediation_capacity.csv`, each with its own slot
capacity. Take the actions in rank order and place each one in the earliest wave that is not
earlier than the wave the supplier has said it can engage in, and that still has enough free slots
for the whole action. An action that cannot be placed is not scheduled, with the reason
`capacity_exhausted` where a wave existed but had no room, and `no_wave_after_availability` where
no wave falls after the supplier's earliest date. Where a supplier has stated an earliest month in
its correspondence, that month is the earliest wave; where it has said nothing, the earliest wave
is the first.

An action is never split across waves and a wave is never overfilled.

## 13. Conventions

Write dates as `YYYY-MM-DD`. Write the four decimal places on specific emissions and three on
emissions, masses and deductions. Write country names as the default value file writes them.
Write codes with the spacing the declarations use.

The controlled vocabularies are:

- scope basis: `in_scope`, `procedure_excluded`, `code_not_covered`
- origin basis: `entry_declared`, `proof_of_origin`, `not_established`
- emissions basis: `actual`, `default_country`, `default_other_countries`, `default_annex_iv`,
  `not_applicable`
- admissibility: `admissible`, `not_admissible`
- failing condition: `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `NONE`
- precursor basis: `actual`, `default_country`, `default_other_countries`, `default_annex_iv`
- threshold status: `above_threshold`, `below_threshold`
- action type: `obtain_report`, `reverification`, `accredited_reverification`,
  `boundary_completion`, `misstatement_resolution`
- remediation status: `scheduled`, `not_scheduled`
- not scheduled reason: `capacity_exhausted`, `no_wave_after_availability`

## 14. What governs

The filed document governs. `entry_summary_export.json` is the desk's own workbench table, kept by
hand, and it is an index of what we think we hold and nothing more. It lists items that were
declared and then cancelled before release, it omits items that were released, its mass column
drifts, its origin column repeats the country of dispatch, its procedure column has been
overwritten in places, and its emissions column carries whatever figure a supplier last sent
rather than anything the desk has derived. It records nothing that was verified.

Where a later letter from an operator corrects a figure in a communication it names, the
correction governs that figure and nothing else on that communication changes.

## 15. Sources

- Regulation (EU) 2023/956 establishing a carbon border adjustment mechanism:
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023R0956
- Commission Implementing Regulation (EU) 2025/2621 on default values, Annexes I to IV:
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ%3AL_202502621
- The Commission's published default value workbook for the definitive period, from which
  `reference/commission_default_values.csv` and `reference/commission_annex_iv_values.csv` were
  taken: https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/cbam-definitive-regime_en
- Commission guidance for the definitive period, introduction to CBAM concepts:
  https://taxation-customs.ec.europa.eu/document/download/031abf60-21a9-4822-b258-ac8b111d8358_en
