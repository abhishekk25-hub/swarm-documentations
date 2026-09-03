# Export-Control Screening Rulebook

This rulebook is binding for `/logs/agent/export_screening_matrix.csv` and related
deliverables. Closed lists and arithmetic below are the only values the matrix may use.

## 1. What a row is

One row = one `claim_id` from `/input_artifacts/claim_catalog.json`. Every catalog claim
must appear exactly once. Do not invent claim IDs. Do not relabel `jurisdiction_id` or
`control_theme` away from the catalog assignment for that claim_id.

## 2. Columns (exact order)

```
claim_id,jurisdiction_id,control_theme,section_locator,obligation_paraphrase,evidence_quote,control_class,duty_actor,licence_posture,enduse_sensitivity,control_tightness_score,crosswalk_group_id,note
```

## 3. Closed vocabularies

### control_class (exactly one)
- `AUTHORIZATION_REQUIRED` - a licence/authorization is required before the transfer
- `EXCEPTION_AVAILABLE` - a published exception, OGEL, or simplified path may apply
- `SCREENING_DUTY` - end-user / denied-party / end-use screening is required
- `DESTINATION_RESTRICTED` - destination or country-based restriction applies
- `CATCHALL_TRIGGER` - catch-all / unlisted-tech trigger language
- `PROCEDURAL_DUTY` - recordkeeping, reporting, application process, or ICP duty
- `PROHIBITION` - an outright ban or criminal offence framing
- `NOT_FOUND` - the theme cannot be grounded in the fetched instrument; use sparingly

### duty_actor (exactly one)
- `EXPORTER` - the exporting company / applicant
- `BROKER` - broker / arranger of the transfer
- `END_USER` - named end-user obligations
- `LICENSING_AUTHORITY` - the government authority itself
- `INTERNAL_COMPLIANCE` - compliance officer / ICP inside the firm
- `UNSPECIFIED`

### licence_posture (exactly one)
- `INDIVIDUAL_LICENCE` - case-by-case licence
- `GENERAL_LICENCE` - open/general/simplified licence path
- `NO_LICENCE_IF_EXCEPTION` - exception can remove the need
- `PROHIBITED` - no licence path
- `NOT_APPLICABLE` - theme is not a licensing decision (e.g. pure recordkeeping)
- `UNKNOWN_NOT_FOUND` - paired with NOT_FOUND

### enduse_sensitivity (exactly one)
- `WMD_MILITARY` - WMD / military end-use red flags
- `GOVERNMENT_SECURE` - government or security-service end use
- `CIVILIAN_DUAL` - civilian / dual-use framing
- `UNSPECIFIED`
- `NOT_APPLICABLE`

## 4. Substantive paraphrase (anti-padding)

`obligation_paraphrase` must be a real sentence in the analyst's own words:
- at least 25 characters and 6 words
- NOT identical to, and NOT a contiguous slice of, `evidence_quote`
- NOT a section heading (title-case capital ratio under 0.60)
- Contains a duty verb (shall / must / require / prohibit / authorise / authorize / licence / license / screen / report / retain / apply / notify)
- `evidence_quote` is 12-60 words, copied verbatim from the fetched instrument

The full normalised quote (not merely a 12-word window) must appear in the instrument text.

## 5. control_tightness_score (0-10 integer)

Sum these four terms (each 0-3, then clamp to 10):

1. **Class weight** - EXCEPTION_AVAILABLE=0, PROCEDURAL_DUTY=1, SCREENING_DUTY=2,
   AUTHORIZATION_REQUIRED=2, DESTINATION_RESTRICTED=2, CATCHALL_TRIGGER=2, PROHIBITION=3,
   NOT_FOUND=0
2. **Licence weight** - NO_LICENCE_IF_EXCEPTION=0, GENERAL_LICENCE=1, INDIVIDUAL_LICENCE=2,
   PROHIBITED=3, NOT_APPLICABLE=0, UNKNOWN_NOT_FOUND=0
3. **End-use weight** - CIVILIAN_DUAL=0, UNSPECIFIED=1, GOVERNMENT_SECURE=2, WMD_MILITARY=3,
   NOT_APPLICABLE=0
4. **Actor clarity** - duty_actor is not UNSPECIFIED = 1; else 0; NOT_FOUND = 0

`control_tightness_score = min(10, class + licence + enduse + actor)`

## 6. Crosswalk groups

`crosswalk_group_id` is `XW-####` shared by claims that address the same control theme
across different jurisdictions. A group must contain at least 2 jurisdictions. Singleton
claims use `XW-NONE`.

## 7. Exception / conflict ledger

Columns (exact order):
```
conflict_id,claim_id_a,claim_id_b,control_theme,class_a,class_b,why_it_matters,evidence_quote_a,evidence_quote_b
```

A row is a real conflict only when `class_a` differs from `class_b` and the two claim_ids
are distinct catalog claims. Do not pad with agreeing pairs.

## 8. Charts

Four PNGs, series also in `chart_data.json`:
- `control_class_distribution.png`
- `tightness_score_histogram.png`
- `theme_coverage_by_jurisdiction.png`
- `conflict_density.png`

Numbers must equal the matrix. Each PNG must draw its own series.
