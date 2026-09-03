CONTRACT RESEARCH ORGANIZATION -- CLINICAL OPERATIONS
ADOPTED RISK-BASED MONITORING (RBM) TRIAGE RULEBOOK
(Standard operating method for building the quarterly monitoring plan across the
portfolio; grounded in ICH E6(R2) section 5.0/5.18, the FDA risk-based monitoring
guidance, ICH E8(R1) critical-to-quality thinking, and the TransCelerate RBM
framework. The authorities in sources_to_confirm.md are binding and must be
confirmed and cited each cycle.)

1. Purpose and scope
This rulebook fixes how the clinical-operations lead risk-tiers and schedules
on-site/centralized monitoring visits across the portfolio's trials for the
upcoming 13-week quarter, as of 2026-07-01. Each trial's
monitoring-risk fields are read from its ClinicalTrials.gov study record in
/input_artifacts/trials/. The records are real and vary in format; read each one.

2. In-scope vs out-of-scope (exclusions)
A trial is IN SCOPE for monitoring this quarter only when its Overall Recruitment
Status is one of: Recruiting, Active not recruiting, or Enrolling by invitation.
Every other status is OUT OF SCOPE and is excluded with a reason, not scheduled:
Completed -> completed_closeout; Terminated -> terminated; Withdrawn -> withdrawn;
Suspended -> suspended; Not yet recruiting -> not_yet_enrolling; Unknown ->
status_unknown. Excluded trials are retained on the record with the reason.

3. Status reconciliation (governing value)
A record's Overall Recruitment Status GOVERNS scope. Where one or more of a
trial's individual facility (site) statuses disagree with the overall status, the
overall status governs and the divergence is logged (it does not by itself change
scope). Do not infer scope from a single site's status.

4. Risk score (integer points per in-scope trial)
   Phase (take the highest applicable when multiple phases are listed):
       Early Phase 1 / Phase 1 -> 30; Phase 2 -> 20;
       Phase 3 -> 25; Phase 4 -> 15;
       Not Applicable / none -> 8.
   Study type: Interventional -> 10; Observational -> 0; Expanded access -> 5.
   Enrollment (participant count): >= 500 -> 20; >= 100 -> 12; >= 1 -> 5.
   Number of facilities (sites): >= 10 sites -> 15; >= 2 sites -> 8.
   Data staleness (days since the record was last updated, as of 2026-07-01): >= 365 days -> 15; >= 180 days -> 8.
   Enrollment basis: +5 when enrollment is Estimated (accrual not finalized).
   Regulated intervention: +10 when any intervention is FDA-regulated
       (Drug, Biological, Device, Combination Product, Genetic, Radiation, or Diagnostic Test).
   The risk score is the sum of these terms.

5. Risk tier
   high   when risk score >= 70;
   medium when risk score >= 45 (and < 70);
   low    otherwise.

6. Monitoring hours per in-scope trial
   base 8 h
   + tier adder (high -> 14 h; medium -> 8 h; low -> 4 h)
   + site adder (>= 10 sites -> +8 h; >= 2 sites -> +4 h).

7. Visit-window cadence
   The first monitoring visit must be scheduled within: high tier 10 weeks;
   medium tier 12 weeks; low tier within the 13-week horizon.

8. CRA capacity and the reference schedule
   The portfolio has 48 CRA monitor-hours available each week
   over 13 weeks. Rank in-scope trials by risk score (highest first);
   break ties by the tighter visit window, then larger enrollment, then NCT number.
   Process the ranked list:
     - Assign the trial to the earliest week whose remaining CRA hours can absorb its
       monitoring hours AND whose week number is within the trial's visit window;
       mark it schedule_visit and consume the hours.
     - If no week within the visit window has room but some week in the horizon does,
       mark it window_infeasible (cadence cannot be met this quarter).
     - If no week in the horizon has room, mark it defer_capacity.
   A high-oversight completion is a high-tier trial that is successfully scheduled;
   the count of high-tier trials monitored is the headline metric.

9. Required disposition
   Every trial is carried to a decision (schedule_visit, window_infeasible,
   defer_capacity, or excluded with a reason) with a stated blocker where it is not
   scheduled, and an evidence reference back to the governing record field. Deferred
   and window-infeasible trials are listed with the blocker so the lead can seek
   mitigation (added CRA capacity, centralized/remote monitoring, or re-tiering)
   before an oversight gap occurs.

10. Regulatory confirmation and citation
   The methodology must be confirmed against the live/official authorities in
   sources_to_confirm.md, not paraphrased from memory. For each authority, record the
   requirement or fact it supplies, the official URL actually retrieved, and the
   retrieval date, so the citations are frozen and defensible.
