I help coordinate monitoring visits for our clinical-trial research partners. We have more hospital sites than we can visit this quarter, so I need a risk-based schedule that is practical, easy to defend, and stays within our travel limits. Every partner still needs at least one visit.

Use /input_artifacts/site_roster.csv as the roster. It has the site ID, partner, region, city and state, ClinicalTrials.gov ID, and travel nights for each site.

For each site look for the trial on ClinicalTrials.gov and score it like this:
add 3 points if the trial is suspended, terminated, or withdrawn, add 2 points if it is recruiting but has not been updated since before June 1, 2025; add 2 points if it is completed but has no results posted; add 1 point if the primary completion date is before June 1, 2026 but the trial is still recruiting or active. Keep the score parts separate and then add them into the final risk score.

Also check the site institution against the FDA warning letter list and the HHS OIG exclusions list. Include anything useful in the evidence trail.

Build a schedule with no more than 18 visits and no more than 30 travel nights. Every partner in the roster must have at least one selected visit. Once that minimum coverage is satisfied, use the remaining capacity for the sites that give the most risk coverage per travel night. For ties, choose the site with stronger public evidence first, then the partner with fewer selected visits.

Save the final work under /logs/agent/.

Create monitoring_schedule.csv with the selected sites only. Include site_id, partner_org, region, modality, proposed_month, travel_nights, the risk score parts, total risk_score, objective_contribution, and selection_rank. By modality I mean the trial's study type on ClinicalTrials.gov, such as interventional or observational.

Create audit_trace.csv with one row for every candidate site in the roster. Include the trial fields you checked, FDA and OIG checks, score parts, total risk_score, selected flag, and source URLs.

Create constraint_checks.csv showing the caps used and whether the plan passed each check: visit count, travel nights, partner coverage, one visit per site, and roster coverage.

Create scheduling_rationale.docx as a short 2 page memo explaining how the schedule was chosen, which sites were left out because of the limits, how ties were handled, and what tradeoffs were made so every partner still got covered.