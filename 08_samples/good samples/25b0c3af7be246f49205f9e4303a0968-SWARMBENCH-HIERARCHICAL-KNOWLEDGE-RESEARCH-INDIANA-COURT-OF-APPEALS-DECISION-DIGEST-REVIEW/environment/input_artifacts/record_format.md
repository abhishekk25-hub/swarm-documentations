Use these six labeled parts on every conference slip. Write in your own words and make each part specific to the assigned Indiana Court of Appeals opinion. File the slip on the matching cause drawer and name it from the printed cause number. Each slip needs at least about 200 words of original analysis. A caption restatement is not enough.

1. Matter and procedural posture
   Name the appellant, the trial court, and the complete printed cause number.

2. Claim and question presented
   Identify the Indiana Code, Appellate Rule, or PCR issue the panel actually decided, and what the appellant asked the court to change.

3. Record and material facts
   Reconstruct the trial-record facts the panel relies on.

4. Governing authority and application
   Explain the Indiana Code or Appellate Rule and the sufficiency, harmless-error, or abuse-of-discretion test the panel uses, and how it applies that authority to this record.

5. Findings and disposition
   State whether the panel affirmed, reversed, remanded, or dismissed, and give the decisive reason.

6. Relief and practical consequence
   Explain what transfer or remand does to the judgment or sentence, and what remains for the trial court if anything is left open. Keep that consequence in the panel's nouns so a clerk can tell whether it is a remand, a dismissal, a right upheld, a right rejected, or a monetary award.

Calendar key for transfer_calendar.csv

Write `/logs/agent/output/transfer_calendar.csv` with one row per z-label. The header is report, case_name, docket, issue_family, disposition, penalty_or_remedy, note_status.

penalty_or_remedy is the transfer or leftover clerk work in the panel's nouns, with years, dollars, or Indiana Code findings as printed. A one-word class cell does not ship.

issue_family is exactly one of:
- criminal_sufficiency: Indiana Code title 35 or a merit criminal appeal
- civil_judgment: a plenary civil judgment or summary-judgment appeal
- family_juvenile: CHINS, TPR, or dissolution
- unpublished_nfp: a not-for-publication memorandum
- postconviction: a PC cause or PCR petition
- procedural: an Appellate Rule 46 briefing stop or Rule 9 notice stop

disposition is exactly one of: granted, granted_in_part, denied, dismissed, remanded, other.

note_status is complete only on a finished grounded card.
