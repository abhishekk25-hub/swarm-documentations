I run the carbon border desk at Scheldt Quay Customs Services in Antwerp. We are an indirect
customs representative and we file as the authorised CBAM declarant for twelve importers, which
means the mechanism's obligations land on us before they land on them. The definitive period
started on 1 January 2026 and I need our position for the first half of the year settled now,
while the supplier data can still be fixed. The annual declaration is not due until September
2027, but by then nothing on this file can be changed.

Here is the shape of the problem. Every consignment released for free circulation between
1 January and 30 June sits on a declaration in our file. For each goods line I need to know
whether it is inside the mechanism at all, which country it actually originated in, and what a
tonne of it carries. That last question is the hard one, because a tonne carries the operator's own
verified figure only where the operator's communication is one we are allowed to rely on, and
otherwise it carries whatever the Commission has published for that code and that country. Whether
we are allowed to rely on a communication is never decidable from the communication. The opinion
that settles it is filed under the verification body, and whether that opinion counts at all
depends on an accreditation register that is neither. On top of that, a rolled or ground or
granulated product carries the emissions of the goods consumed to make it, and those goods were
made somewhere else, by an operator whose own communication has its own answer to the same
question.

Then there are the two things that are not properties of any line. Carbon price claims reach
consignments by scheme and period rather than by consignment, so one claim touches several
importers at once and a rebate disclosed in a letter somewhere else takes it away. And the mass
threshold is a property of an importer's whole year, so twelve aggregations that each span the
entire portfolio decide whether groups of lines generate an obligation at all.

Everything is under `/input_artifacts/`. Your working directory is `/workspace`.

Read `/input_artifacts/cbam_desk_reference.md` first. It is the desk manual and it settles every
question of method: what puts a line inside or outside the mechanism, how the country of origin is
settled and when it is not settled at all, the conditions under which an operator's own figures may
be used and the order they are tested in, how specific embedded emissions are derived and how the
three ways a precursor consumption is written are normalised, which sectors carry indirect
emissions, how a published default value is resolved and what happens when the Commission has
published none, how a carbon price claim is tested and converted, the mass threshold and the
certificate arithmetic, and how the remediation programme is ranked and filled. Where it and your
instinct disagree, follow it.

The case file is in six folders. `/input_artifacts/customs_entries/` holds the release
declarations, each with two to four goods lines on it. `/input_artifacts/operator_reports/` holds
the emissions data communications the operators sent us, one per installation, on five different
house layouts. `/input_artifacts/verification_reports/` holds the verification opinions, filed
under the body that signed them rather than under the installation. `/input_artifacts/carbon_price_claims/`
holds the claims operators have lodged for carbon prices paid at home.
`/input_artifacts/supplier_correspondence/` holds the letters, and some of them correct a figure
printed on a communication or disclose something a claim form does not.
`/input_artifacts/proofs_of_origin/` holds the certificates and supplier declarations presented
against particular items, some of which the desk has already marked as defective on their face.

Eleven pinned tables sit in `/input_artifacts/reference/`.
`commission_default_values.csv` and `commission_annex_iv_values.csv` are the Commission's own
published default values for the definitive period, in long form, country by country and code by
code, together with the Annex IV highest values. `covered_goods.csv` says which commodity codes the
mechanism covers. `production_routes.csv` gives, for each code and route, the processes the route
requires inside the boundary and the precursor codes it requires to be reported.
`accreditation_register.csv` carries the verification bodies, their sectors in scope, their
validity dates and any suspension. `importer_register.csv` and `installation_register.csv` are the
desk's registers of who we represent and who supplies them. `fx_reference_rates.csv`,
`desk_parameters.csv`, `remediation_capacity.csv` and `remediation_effort.csv` carry the reference
rates, the phase-in factor and certificate price, the engagement capacity by month and the effort
each kind of remediation costs.

`/input_artifacts/entry_summary_export.json` is our own workbench table. Treat it as an index of
what we think we hold and nothing more. It lists items that were declared and then cancelled, it
omits items that were released, its mass column drifts from the declarations, its origin column
repeats the country of dispatch, its procedure column has been overwritten in places and its
emissions column carries whatever a supplier last sent. The filed document governs, every time.
`/input_artifacts/source_manifest.json` records where each of these came from.

What I need back

Eight files, at these exact paths, all under `/logs/agent/`. They are one package and I will read
them against each other, so the figures have to agree.

`/logs/agent/consignment_ledger.csv`, one row per goods line on the declarations, with this header:

```
entry_ref,line_no,importer_code,cn_code,customs_procedure,in_scope,scope_basis,declared_origin,governing_origin,origin_basis,net_mass_t,supplier_installation,emissions_basis,see_direct,see_indirect,see_applied,embedded_emissions_t,evidence_document,evidence_quote
```

`in_scope` is `yes` or `no`. `net_mass_t` is tonnes to three decimals, taken off the item of the
declaration. Write `NONE` in `governing_origin` where the origin is not established. For a line
outside the mechanism leave `see_direct`, `see_indirect`, `see_applied` and `embedded_emissions_t`
empty rather than writing a number that does not arise. `evidence_document` is the identifier of a
document in the file, without its extension, and `evidence_quote` is a passage copied word for word
out of that document, sixty words at most, that names the line it stands behind.

`/logs/agent/installation_dossier.csv`, one row per installation on the register:

```
installation_id,country,sector,cn_code,report_id,reporting_period_start,reporting_period_end,activity_level_t,attributed_direct_t,attributed_indirect_t,own_direct_intensity,precursor_direct_component,see_direct_derived,see_indirect_derived,verification_report,admissibility,failing_condition,evidence_quote
```

`own_direct_intensity` is the attributed direct emissions over the activity level and
`precursor_direct_component` is what the precursors contribute, both to four decimals, and
`see_direct_derived` is their sum. Fill these for every installation, including the ones whose
communication we may not rely on, because the remediation figures are measured against them.
`verification_report` is the opinion that governs, or `NONE`. `failing_condition` is the first
condition that fails, or `NONE`.

`/logs/agent/precursor_chain.csv`, one row per precursor a communication reports:

```
installation_id,cn_code,precursor_installation,precursor_cn_code,precursor_country,consumption_t_per_t,precursor_basis,precursor_see_direct,precursor_contribution,source_document
```

`/logs/agent/carbon_price_schedule.csv`, one row per claim:

```
claim_ref,scheme_type,jurisdiction,period_start,period_end,installations_covered,amount_local,currency,amount_eur,admitted,rejection_condition,deduction_t,importers_affected
```

`admitted` is `yes` or `no`, `rejection_condition` is the first condition that fails or `NONE`, and
`installations_covered` and `importers_affected` are semicolon separated.

`/logs/agent/importer_position.csv`, one row per importer we represent:

```
importer_code,importer_name,lines_in_scope,cumulative_net_mass_t,threshold_status,total_embedded_emissions_t,adjusted_emissions_t,carbon_price_deduction_t,certificates_due,certificates_to_purchase
```

Report the embedded emissions for every importer, including the ones below the threshold, and set
the adjusted emissions, the deduction and the certificates to zero for those.

`/logs/agent/remediation_programme.csv`, one row per installation whose communication we may not
rely on:

```
action_ref,installation_id,failing_condition,action_type,slots_required,earliest_wave,exposure_reduction_t,rank,assigned_wave,status,not_scheduled_reason
```

`earliest_wave` is written `W1` to `W4`. Leave `assigned_wave` empty and give a reason where an
action is not scheduled, and leave the reason empty where it is.

`/logs/agent/position_memo.md`, at least 6,000 characters, for our managing director and for the
national competent authority if they ask. I want the period explained rather than listed: where the
exposure actually sits and why, which importers carry an obligation and which do not and what that
turns on, every installation whose figures we could not use named alongside the condition it failed
and what that costs us, the claims we lost and why, the lines whose origin we could not settle, and
what I should say about the engagement capacity between September and December running out before
the queue does.

`/logs/agent/exposure_exhibit.md`, at least 2,000 characters, ranking the importers by embedded
emissions with the certificate position each one closes at, and the remediation queue in rank order
with the exposure each action would release and where the capacity stops.

How I will read it

A figure that cannot be traced to a filed document should not be written down. Where a
communication may not be relied on, use what the Commission published rather than what the operator
asserted. Where the origin will not settle, say so in the row instead of guessing a country.
Statuses, bases, conditions and action types must be written exactly as the desk reference names
them, and the arithmetic in one file has to agree with the arithmetic in the others.
