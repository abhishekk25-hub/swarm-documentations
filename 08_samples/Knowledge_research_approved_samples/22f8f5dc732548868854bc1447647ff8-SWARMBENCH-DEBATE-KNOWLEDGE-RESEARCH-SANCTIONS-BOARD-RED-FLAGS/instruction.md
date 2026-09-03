I run integrity due diligence at a development finance institution and the screening questions we put to counterparties in the projects we finance have drifted away from what sanctions tribunals actually find
Our risk committee meets in three weeks and I want the refresh grounded in published reasoning rather than in generic vendor red flag lists

Work in /workspace

The evidence is a pinned capture of the World Bank Group Sanctions Board decisions library
/input_artifacts/decisions_index.csv lists the thirty highest numbered public decisions in that capture ordered by decision_number descending with the columns decision_number case_number listing_title decision_date and document_filename
Each document_filename resolves to one fully reasoned decision document under /input_artifacts/decisions/
The library marks a decision that was reissued with a corrigendum by an asterisk in its listing title and the packaged document for such a decision is the reissued version
/input_artifacts/capture_provenance.txt records the capture date and the retrieval address for the index and for every document
Treat that capture date as the as of date for everything you write and work only from the captured material

Write the decision digest to /logs/agent/decision_digest.md with one section for each of the thirty decisions in index order
Open each section with the decision number the case number the decision date and whether the decision carries a corrigendum
Then keep apart three things that blur together easily which are the allegations brought against the respondent the arguments the respondent made in reply and the findings the Sanctions Board itself reached
Record the sanctionable practice or practices the Board found the evidentiary reasoning it relied on the aggravating and mitigating factors it applied and the sanction it imposed
Give a section or paragraph citation from the packaged document for each of those four items
Where a decision does not address one of them write not stated instead of inferring a value
Close each section by saying whether the decision supports a warning sign that a diligence team could observe before contracting and say so plainly when it does not

Write the red flag to evidence matrix to /logs/agent/red_flag_matrix.csv with the columns red_flag_id red_flag decision_number citation basis observable_evidence and diligence_response
Use one row for each pairing of a red flag with a decision that supports it so a flag resting on four decisions gets four rows and carries the same red_flag_id across them
Number red_flag_id from RF-01 upward
basis takes only the values holding or factor or party argument
diligence_response takes only the values routine or enhanced or contractual safeguard or escalate
observable_evidence names the document record or check that a diligence team could actually request before contracting rather than a conclusion that only an investigation would reach
Every decision_number in the matrix must appear in /input_artifacts/decisions_index.csv and in the digest and a red flag that no packaged decision supports does not belong in the matrix at all

Write the risk committee briefing to /logs/agent/risk_committee_briefing.md
It needs to name the reasoning patterns that recur across the thirty decisions and show where a procurement reading and an investigations reading and a legal reading of the same decision point in different directions and how you settled that
Then set out the screening changes and contractual protections you recommend and tie each one to the red_flag_id values it rests on
State plainly that a past sanction is not by itself a reason to exclude a counterparty from a current transaction and say what the committee should do instead
Do not name any party that the packaged decisions do not name

When you are finished /logs/agent/decision_digest.md /logs/agent/red_flag_matrix.csv and /logs/agent/risk_committee_briefing.md should exist and agree with one another
