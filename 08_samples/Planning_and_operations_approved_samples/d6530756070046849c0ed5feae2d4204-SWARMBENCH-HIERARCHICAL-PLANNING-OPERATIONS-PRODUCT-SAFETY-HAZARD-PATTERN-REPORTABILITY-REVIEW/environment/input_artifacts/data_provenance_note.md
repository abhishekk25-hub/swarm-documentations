# Provenance of the incident corpus

## Where the records come from

`incident_reports.csv` holds 204 real consumer product safety incident reports drawn from the
**Publicly Available Consumer Product Safety Information Database** operated by the U.S.
Consumer Product Safety Commission at SaferProducts.gov. The full database is published by
CPSC as a bulk extract (`IncidentReports.csv` inside `https://www.saferproducts.gov/SPDB.zip`);
the extract used here was retrieved on 2026-08-14.

Every field in `incident_reports.csv` is copied from that extract without alteration except
for whitespace normalisation and the column renaming listed below. No text in
`incident_description` or `company_comment` has been reworded, shortened or synthesised.

| Column here | Column in the CPSC extract |
|---|---|
| `report_no` | `Report No.` |
| `report_date` | `Report Date` |
| `product_category` | `Product Category` |
| `product_sub_category` | `Product Sub Category` |
| `product_type` | `Product Type` |
| `brand_as_reported` | `Brand` |
| `model_name_or_number` | `Model Name or Number` |
| `manufacturer_name` | `Manufacturer / Importer / Private Labeler Name` |
| `retailer` | `Retailer` |
| `victim_severity_coded` | `(Primary) Victim Severity` |
| `victim_age_years` | `(Primary) Victim's Age (years)` |
| `incident_location` | `Location` |
| `incident_description` | `Incident Description` |
| `company_comment` | `Company Comments` |

## How this slate was drawn

The 204 reports were selected from reports dated between 2023-01-01 and 2026-06-30 that
concern brand families the group carries, and that describe either a personal injury or a
fire, shock, structural or contamination hazard. That filter is the group's standing
surveillance intake rule, so the slate is deliberately weighted toward reports with a
substantiated hazard and is **not** a random sample of the database. Reports whose narrative
duplicated another report's opening text were dropped so that each row is a distinct account.

## What to keep in mind when reading

- `incident_description` is the consumer's own writing. Length, spelling, punctuation and
  vocabulary vary widely, and CPSC redacts personal details in place.
- `company_comment` is the response filed by the manufacturer, importer or private labeler.
  It is prefixed with the date it was filed and the responding firm's legal name, which is
  often not the brand name on the product. Many responses are house boilerplate reused
  verbatim across unrelated reports; some are specific to the incident.
- Roughly a third of reports carry a company response at all. The absence of a response
  carries no implication either way.
- `brand_as_reported` is entered by the person filing and is inconsistent — casing varies, and
  corporate, sub-brand and parent names are used interchangeably for the same brand family.
- CPSC's own disclaimer applies: the Commission does not guarantee the accuracy, completeness
  or adequacy of the contents of the database, particularly for information submitted by
  people outside CPSC.
