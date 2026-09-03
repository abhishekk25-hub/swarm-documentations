# Causal pattern taxonomy

These are the eight causal patterns you must classify every disaster against. They are drawn from
real accident-investigation and safety-science literature. A pattern name is a category of
underlying MECHANISM, not a severity label or a synonym for "something went wrong" - use the
worked examples below to judge whether a specific disaster's real history genuinely shows the
mechanism, not just a superficially similar outcome.

## REGULATORY_CAPTURE_OR_WEAK_OVERSIGHT
The body responsible for inspecting, licensing, or enforcing safety standards had the authority to
prevent the failure but did not exercise it effectively - because it was under-resourced,
deferred to the operator's own self-reporting, was structurally too close to the industry it
regulated, or had jurisdictional gaps that let the actual hazard fall between agencies. This is
about the REGULATOR's failure, not the operator's. Example mechanism: an inspection agency relies
on the operator's own safety filings rather than independent verification, and those filings
understate a known hazard.

## MAINTENANCE_DEFERRAL_OR_NEGLECT
A known piece of equipment, structure, or system was allowed to degrade past a safe threshold
because inspection, repair, or replacement was postponed, skipped, or done to a lower standard
than required - typically for cost or scheduling reasons. This is about a SPECIFIC physical asset
whose condition was allowed to worsen, not about safety culture in general.

## DESIGN_OR_ENGINEERING_FLAW
The failure traces to how something was originally designed, engineered, or specified - an
inadequate safety margin, a load case or failure mode the design never accounted for, a materials
choice that could not survive real operating conditions, or a design that violated (or exploited a
gap in) the engineering standards of its time. This is about the original design decision, not
about how the thing was later maintained or operated.

## OPERATOR_OR_HUMAN_ERROR
A person actually operating, piloting, or directly controlling the system made a decision or took
an action (or failed to take one) in the moment that directly triggered or failed to prevent the
failure - a misjudgment, a missed procedure step, a miscommunication in the control loop. This
does NOT include failures better explained by inadequate training or an unsafe culture that set
the operator up to fail (see INADEQUATE_SAFETY_CULTURE_OR_TRAINING below) - the distinguishing
question is whether a reasonably trained, reasonably supported person in that role could still
plausibly have made the same specific error, versus whether the organization had made that error
close to inevitable.

## COST_CUTTING_UNDER_COMMERCIAL_PRESSURE
A specific decision that increased risk - cutting a corner, choosing a cheaper option, delaying an
expenditure, understaffing, or overriding a safety recommendation - is documented as having been
made explicitly to save money, meet a deadline, or protect a commercial or competitive position.
This requires the source to actually connect the risky decision to a commercial motive, not just
note that the organization was a business.

## CASCADING_OR_COMMON_MODE_FAILURE
A single initiating failure propagated through a system because supposedly independent
safeguards, backups, or barriers turned out to share a common weakness or were not actually
independent of each other, so one failure took out several protections at once rather than being
caught by the next layer of defense. This is about the STRUCTURE of how the failure spread, not
about what initially caused it.

## IGNORED_PRIOR_WARNINGS_OR_TESTS
Before the disaster, a specific real warning existed - a prior near-miss, a whistleblower report,
an internal test result, an external audit finding, or a documented recommendation - and the
organization responsible had that warning in hand and did not act on it in time. This requires a
real, specific, documented prior warning event, not just hindsight that the risk was "foreseeable"
in the abstract.

## INADEQUATE_SAFETY_CULTURE_OR_TRAINING
The organization's normal way of operating - not a single decision, but an ongoing pattern -
normalized unsafe practices, under-trained staff for the real risks of the role, discouraged
reporting of hazards, or treated safety procedures as optional under production pressure. This is
about a sustained organizational pattern documented across multiple points in the source, not a
single bad decision (see COST_CUTTING_UNDER_COMMERCIAL_PRESSURE) or a single person's in-the-
moment error (see OPERATOR_OR_HUMAN_ERROR).

---

# Deliverable contract

Full detail is in instruction.md; this section is the exact schema reference.

## Per-disaster record: /logs/agent/records/<slug>.md
Five sections in order: `# <disaster_name>`, `## Identity`, `## Causal chain` (five labeled
parts: Root cause, Contributing factors, Failure point, Consequence, Reform triggered),
`## Causal pattern classification` (each applicable pattern with a real supporting quote).

## /logs/agent/causal_pattern_register.csv
Columns, exactly in this order: entry_id, disaster_slug, disaster_name, industry_domain,
real_date, causal_pattern, key_finding, supporting_quote, cross_industry_link. causal_pattern
must be exactly one of the eight category names above (all-caps, exact spelling).
cross_industry_link is either NONE or another row's entry_id from a DIFFERENT industry_domain
whose underlying mechanism is genuinely the same, not merely the same category label.

## /logs/agent/cross_industry_synthesis.md
At least 900 words, organized by causal pattern (not by industry), citing specific entry_ids and
direct quotes from your own register for every claim.

## /logs/agent/pattern_taxonomy.json
A JSON object with exactly the eight category names above as keys, each mapped to an array of the
entry_ids from causal_pattern_register.csv that carry that pattern. Must agree exactly with the
register: every entry_id in the register appears under its own pattern's array here, and no
entry_id appears that is not a real register row.
