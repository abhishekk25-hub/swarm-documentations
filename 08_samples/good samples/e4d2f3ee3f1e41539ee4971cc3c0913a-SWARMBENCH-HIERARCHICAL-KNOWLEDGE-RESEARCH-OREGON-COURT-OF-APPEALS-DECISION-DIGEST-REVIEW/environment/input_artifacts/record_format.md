Use these six labeled parts on every petition-conference slip. Write in your own words and make each part specific to the assigned Oregon Court of Appeals opinion. File the slip on the matching department folio and name it from the printed A-number. Each slip needs substantial original analysis. A caption restatement is not enough.

1. Matter and procedural posture
   Name the appellant, the circuit court or agency, and the complete printed A-number.

2. Claim and question presented
   Identify the ORS or ORAP issue the panel actually decided, and what the appellant asked the court to change.

3. Record and material facts
   Reconstruct the trial-record or agency-record facts the panel relies on.

4. Governing authority and application
   Explain the ORS or ORAP and the sufficiency, harmless-error, or abuse-of-discretion test the panel uses, and how it applies that authority to this record.

5. Findings and disposition
   State whether the panel affirmed, reversed, remanded, or dismissed, and give the decisive reason.

6. Relief and practical consequence
   Explain what a petition for review or remand does to the judgment or sentence, and what remains for the circuit court or agency if anything is left open. Keep that consequence in the panel's nouns so a clerk can tell whether it is a remand, a dismissal, a right upheld, a right rejected, or a monetary award.

Calendar key for petition_calendar.csv

Write `/logs/agent/output/petition_calendar.csv` with one row per v-label. The header is report, case_name, docket, issue_family, disposition, penalty_or_remedy, note_status.

penalty_or_remedy is the petition leftover or remand work in the panel's nouns, with years, dollars, or ORS findings as printed. Write at least three words. A one-word class cell does not ship.

issue_family is exactly one of:
- criminal_sufficiency: ORS Title 16 or a merit criminal appeal
- civil_judgment: a plenary civil judgment or summary-judgment appeal
- family_juvenile: ORS 419B, DHS, or dissolution
- administrative_review: BOLI, PUC, or other agency review
- postconviction: a PCR petition
- procedural: an ORAP 5.45 assignment stop or ORAP 5.05 briefing stop

disposition is exactly one of: granted, granted_in_part, denied, dismissed, remanded, other.

note_status is complete only on a finished grounded card.
