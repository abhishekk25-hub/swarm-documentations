I am the federal programs director at a state water resources agency and I am getting ready for the next congressional authorization cycle

Our leadership keeps asking me which Army Corps of Engineers recommendations we should be pushing in Washington and which ones are really waiting on something our own local sponsors have to fix first and nobody here can answer that from one place today

I had the twenty most recent signed Chief of Engineers reports pulled from the Corps Planning Community Toolbox and packaged for you so that we are all working from the same documents

Work in /workspace

Everything you need is under /input_artifacts/ where chiefs_reports_manifest.csv gives one row per report unit with its unit_id and its position in the official listing and source_provenance.md records the listing address and the capture date and the twenty signed reports sit in /input_artifacts/chiefs_reports/ as CR-01.pdf through CR-20.pdf

Treat source_provenance.md as authoritative for the capture date and treat those twenty packaged reports as the entire cohort

Build a workbook at /logs/agent/authorization_tracker.xlsx with a sheet named conditions_register and a sheet named sponsor_readiness

conditions_register carries one row for each of the twenty units and no unit_id appears twice

Each register row starts with unit_id and project_name and report_date where report_date is the date the Chief of Engineers signed that report written as YYYY-MM-DD

Then record project_purpose using one of flood_risk_management or coastal_storm_risk_management or navigation or ecosystem_restoration or water_supply or multiple or other or not_stated

Then record nonfederal_sponsor as the report names it and recommended_plan as a short description of what the report actually recommends building or doing

Then record estimated_first_cost as the figure that report gives and cost_price_level as the price level or cost year the report states for that figure and do not convert any cost into a different year

Then record benefit_basis using one of NED or NER or LPP or TNB or non_NED or combined or not_stated

Then record environmental_commitments and implementation_dependencies and authorization_matters as short summaries of what that one report commits to and of what it says has to happen before construction and of what it puts in front of Congress

Close each row with document_relationship set to base or supplemental

Where a row is a supplemental report set related_unit_id to the unit_id of its base report inside this cohort and otherwise set related_unit_id to not_stated

Every row also needs citations

Write each citation as the unit_id then the word page then the page number so that CR-07 page 4 is a valid citation and separate several citations in one cell with the pipe character

The citations cell has to at least support recommended_plan and estimated_first_cost for that row

Where a signed report does not state a value write exactly not_stated rather than filling the cell from another project or from general practice

sponsor_readiness carries one row for the same twenty units with unit_id and sponsor_named and sponsor_obligations and outstanding_dependency and readiness_label and readiness_rationale and supporting_citation

sponsor_named takes yes or no or not_stated

sponsor_obligations records what the report says the nonfederal sponsor has to provide or do and outstanding_dependency records the single item most likely to hold that project up

readiness_label takes sponsor_action or technical_clarification or federal_advocacy or no_action_identified and readiness_rationale explains that label in a sentence or two using evidence already sitting in the same project register row

supporting_citation uses the same citation format

Then write /logs/agent/legislative_briefing.md for me to take into leadership

It has to answer which of the twenty projects need action from a local sponsor before the next authorization cycle and which need technical clarification back from the Corps district and which need us to push federally and what obligations keep showing up across the portfolio

Name every project you discuss with its unit_id and its project_name exactly as they appear in the register and keep the briefing consistent with both sheets

Say plainly where the twenty reports do not settle a question rather than closing the gap with a reasonable sounding guess

Do not put a sponsor obligation or an environmental commitment or an authorization ask into any deliverable unless the signed report for that unit states it

When you are done I should have /logs/agent/authorization_tracker.xlsx with both sheets filled for all twenty units and /logs/agent/legislative_briefing.md ready to read
