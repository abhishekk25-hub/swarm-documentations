import argparse
import json
import os
import re
import subprocess
from pathlib import Path

MODEL = os.environ.get(
    "JUDGE_MODEL", "accounts/fireworks/models/kimi-k2p5"
)
BASE_URL = "https://api.fireworks.ai/inference/v1"
LLM_RETRIES = 3
LLM_JUDGE_RUNS = 3
PER_FILE_CHAR_CAP = 20000
REPORT_CHAR_CAP = 120000

AGENT_DIR = Path("/logs/agent")
CHARTS_DIR = AGENT_DIR / "charts"

EXPECTED_ISO3 = [
    "NGA", "KEN", "ETH", "GHA", "ZAF", "RWA", "IND", "BGD", "PAK", "IDN",
    "VNM", "PHL", "BRA", "COL", "PER", "MEX", "EGY", "MAR", "UKR", "UZB",
]

CSV_FILES = [
    "cohort.csv",
    "domain_macro.csv", "domain_health.csv", "domain_education.csv",
    "domain_poverty.csv", "domain_governance.csv", "domain_climate.csv",
    "data_gaps.csv", "source_audit.csv", "composite_index.csv", "summary.csv",
]

DOMAIN_EXPECTED_ROWS = {
    "domain_macro.csv": 100,
    "domain_health.csv": 100,
    "domain_education.csv": 80,
    "domain_poverty.csv": 80,
    "domain_governance.csv": 120,
    "domain_climate.csv": 100,
}

RUBRIC_ITEMS = [
    ("cohort_complete",
     "cohort.csv exists and lists all 20 required countries (NGA, KEN, ETH, GHA, ZAF, RWA, IND, BGD, PAK, IDN, VNM, PHL, BRA, COL, PER, MEX, EGY, MAR, UKR, UZB), each with a region and an income group."),
    ("cohort_matches_brief",
     "cohort.csv region and income_group values match the cohort table in the diagnostic brief exactly for all 20 countries (not generic region labels)."),
    ("macro_complete",
     "domain_macro.csv exists and contains exactly 100 scoring-year indicator rows (five indicators for each of the 20 countries)."),
    ("health_complete",
     "domain_health.csv exists and contains exactly 100 scoring-year indicator rows (five indicators for each of the 20 countries)."),
    ("education_complete",
     "domain_education.csv exists and contains exactly 80 scoring-year indicator rows (four indicators for each of the 20 countries)."),
    ("poverty_complete",
     "domain_poverty.csv exists and contains exactly 80 scoring-year indicator rows (four indicators for each of the 20 countries)."),
    ("governance_complete",
     "domain_governance.csv exists with exactly 120 scoring-year indicator rows (six WGI indicators for each of the 20 countries), brief WGI codes in indicator_code, and source=75 present in every api.worldbank.org source_url."),
    ("climate_complete",
     "domain_climate.csv exists and contains exactly 100 scoring-year indicator rows (five indicators for each of the 20 countries)."),
    ("traceability",
     "In the domain CSVs, each indicator value is accompanied by its indicator code, the year of the value, and a World Bank (api.worldbank.org) source URL whose date parameter matches that year; every domain_governance.csv row must include source=75 in its source_url."),
    ("url_full_format",
     "Every source_url in the domain CSVs is a full URL beginning with https://api.worldbank.org/v2/ (not a relative path like country/...)."),
    ("url_scoring_year_matches_row",
     "In every domain CSV row, the source_url date parameter matches the scoring year in the year column (for example date=2023:2023 when year is 2023; a multi-year range like date=2010:2023 on every row does not count)."),
    ("governance_wgi_source75",
     "domain_governance.csv uses the brief's WGI codes (CC.EST, RL.EST, GE.EST, RQ.EST, VA.EST, PV.EST) in the indicator_code column and includes source=75 in every api.worldbank.org URL (a GOV_WGI_ prefix in the URL path is acceptable)."),
    ("subscores_in_range",
     "Each domain CSV reports a 0-100 sub-score per country, and all reported sub-scores fall within the 0-100 range."),
    ("domain_scoring_year_rows",
     "Each domain_*.csv contains one row per country-indicator pair for the scoring year only (not a full 2010-2023 panel of rows per indicator)."),
    ("domain_row_counts_match_brief",
     "Each domain CSV has the expected scoring-year row count from the diagnostic brief: domain_macro.csv 100, domain_health.csv 100, domain_education.csv 80, domain_poverty.csv 80, domain_governance.csv 120, domain_climate.csv 100 (use FILE EVIDENCE row counts)."),
    ("brief_indicator_codes",
     "Every indicator_code in the six domain CSVs appears in the indicator table in the diagnostic brief (no substituted or invented codes)."),
    ("gaps_logged",
     "data_gaps.csv exists with at least 34 data rows logging genuinely missing indicator/country/year cells with fallback_year none when no value exists; missing values are not replaced with zeros or invented numbers."),
    ("gaps_schema",
     "data_gaps.csv uses the required columns iso3, domain, indicator_code, year_requested, fallback_year."),
    ("gaps_domain_tokens",
     "Every domain value in data_gaps.csv is one of the short tokens macro, health, education, poverty, governance, or climate (not longer labels such as macro-fiscal)."),
    ("gaps_thorough",
     "data_gaps.csv contains at least 34 rows documenting real sparse-series gaps (one row per missing country-indicator pair or missing year; collapsed summaries are not sufficient)."),
    ("gaps_reconcile_domain_shortfalls",
     "Every country-indicator pair missing from a domain CSV (relative to the brief's expected row counts) appears in data_gaps.csv; for example the ten missing GC.DOD.TOTL.GD.ZS macro rows must each have a gap row."),
    ("source_audit_complete",
     "source_audit.csv exists with columns iso3, domain, indicator_code, year, source_url and at least as many data rows as the total indicator rows across all six domain_*.csv files."),
    ("source_audit_row_count_exact",
     "source_audit.csv has exactly one row per domain CSV row (FILE EVIDENCE audit row count equals domain total row count, not merely greater than)."),
    ("composite_covers_20",
     "composite_index.csv exists and contains rows covering all 20 required countries."),
    ("composite_columns",
     "composite_index.csv contains only the required columns iso3, country, macro_score, health_score, education_score, poverty_score, governance_score, climate_score, overall_index, rank, strongest_domain, weakest_domain (no extra columns such as region, income_group, percentile, or gap_count)."),
    ("composite_all_six_domains_populated",
     "Every row in composite_index.csv has non-empty numeric values in all six domain score columns (macro_score through climate_score); blank or missing governance_score or any other domain column means this item is not satisfied."),
    ("composite_overall_six_domain_mean",
     "For every country, overall_index equals the simple average of the six domain sub-scores (equal one-sixth weights per the brief); averaging over fewer than six domains does not count."),
    ("composite_two_decimal_format",
     "Every numeric score column in composite_index.csv (macro_score through overall_index) uses exactly two decimal places for every country (for example 90.80, not 90.8); if FILE EVIDENCE composite two-decimal hint lists any score with fewer than two decimal places, this item is not satisfied."),
    ("index_in_range",
     "The overall index values in composite_index.csv are all within the 0-100 range."),
    ("rank_consistent",
     "The rank column is a complete 1..20 ordering with no duplicates, strictly descending by overall index (rank 1 = highest index), with ties broken by the higher governance sub-score per the brief."),
    ("composite_strongest_weakest_accurate",
     "For every country in composite_index.csv, strongest_domain names the domain with the highest sub-score and weakest_domain names the domain with the lowest sub-score in that row (using the short tokens macro, health, education, poverty, governance, climate)."),
    ("composite_matches_domain_subscores",
     "For each country, the six domain score columns in composite_index.csv equal the simple average of normalized_score values in the corresponding domain_*.csv for that country, formatted to exactly two decimal places; any mismatch or one-decimal composite value means this item is not satisfied."),
    ("summary_schema",
     "summary.csv uses only metric,value columns (no description or other columns) and includes countries_scored=20, domains_covered=6, indicators_pulled equal to the total rows across the six domain CSVs, and total_gaps equal to the row count of data_gaps.csv with total_gaps at least 34."),
    ("summary_indicators_pulled",
     "summary.csv includes an indicators_pulled row whose value exactly equals the total number of indicator rows across all six domain_*.csv files (not an approximate count)."),
    ("summary_domains_covered",
     "summary.csv includes a domains_covered row with value 6."),
    ("ranking_chart",
     "charts/resilience_ranking.png exists, is a valid PNG that ranks the countries by overall index, and is at least 1800 pixels wide and 1800 pixels tall (use the EVIDENCE for validity/size/dimensions)."),
    ("ranking_chart_matches_index",
     "The country order in charts/resilience_ranking.png matches composite_index.csv rank order 1 through 20 (rank 1 highest overall index at the top)."),
    ("heatmap_chart",
     "charts/domain_heatmap.png exists, is a valid PNG representing a 20-countries by 6-domains sub-score heatmap, and is at least 1800 pixels wide and 1800 pixels tall (use the EVIDENCE for validity/size/dimensions)."),
    ("heatmap_matches_domain_csvs",
     "The sub-scores shown in charts/domain_heatmap.png align with the per-country domain averages computed from normalized_score in the six domain_*.csv files (within reasonable rounding to two decimal places)."),
    ("animation",
     "resilience_race.mp4 exists, is at least 10 seconds long per ffprobe EVIDENCE, has at least 24 frames per ffprobe EVIDENCE, and is genuinely animated across many frames rather than a single static frame."),
    ("animation_yearly_frames",
     "resilience_race.mp4 animates across the 2010-2023 window with a substantial frame count consistent with year-by-year motion (use ffprobe EVIDENCE: not satisfied if frame_count is below 24)."),
    ("mp4_measure_documented",
     "diagnostic_report.md names the indicator or index series that resilience_race.mp4 animates in a paragraph directly under the ## Methodology heading (a ### subsection alone does not count), and the animated values are consistent with that series in the CSVs; if FILE EVIDENCE shows MP4 series named in Methodology = no, this item is not satisfied."),
    ("report_substantial",
     "diagnostic_report.md exists and is at least 4000 words of substantial prose, not a stub or placeholder."),
    ("report_country_headings",
     "The report contains a dedicated section for each of the 20 countries starting with a markdown heading exactly of the form ## ISO3 - Country Name (for example ## BRA - Brazil)."),
    ("report_sections_in_rank_order",
     "The 20 country sections in diagnostic_report.md (each starting with ## ISO3 - Country Name) appear in composite_index.csv rank order (rank 1 country first through rank 20 last)."),
    ("report_six_domain_scores_per_country",
     "Under each of the 20 ## ISO3 - Country Name headings, the report includes plain labeled lines using the exact column names macro_score, health_score, education_score, poverty_score, governance_score, and climate_score with values identical to composite_index.csv for that country formatted to exactly two decimal places; if FILE EVIDENCE composite two-decimal hint is NOT CLEAN or report labeled score two-decimal hint is NOT CLEAN, this item is not satisfied."),
    ("report_strongest_weakest_labeled",
     "Under each of the 20 ## ISO3 - Country Name headings, the report includes plain labeled lines strongest_domain and weakest_domain with the exact tokens from composite_index.csv for that country (for example strongest_domain: health)."),
    ("report_coverage",
     "The report covers methodology, headline cross-country findings, at least 120 words of strengths-and-vulnerabilities prose under each ## ISO3 - Country Name heading (substitute ### headings or narrative blocks without the required ## format do not count), explicit data-coverage caveats, and recommendations."),
    ("report_caveats_heading",
     "diagnostic_report.md includes a dedicated section whose markdown heading is exactly ## Data Coverage Caveats (a ### subheading does not count)."),
    ("report_cites_composite_scores",
     "Under each of the 20 ## ISO3 - Country Name headings, the report includes plain labeled lines overall_index and rank with values identical to composite_index.csv for that country, with overall_index formatted to exactly two decimal places; if FILE EVIDENCE composite two-decimal hint is not clean, this item is not satisfied."),
    ("report_caveats_cites_gaps",
     "The ## Data Coverage Caveats section names at least five specific iso3, indicator_code, and year_requested combinations that appear as rows in data_gaps.csv (not generic statements about sparsity alone)."),
    ("report_grounded",
     "The figures and claims in the report and the visuals are consistent with the numbers in the CSVs and grounded in the World Bank data, with no fabricated values or contradictions across the package; if FILE EVIDENCE shows domain row MISMATCH, fewer than 34 data_gaps rows, composite two-decimal problems, or chart/animation contradictions, this item is not satisfied."),
]


def write_reward(path, reward, justification, error=None):
    reward = max(0.0, min(1.0, float(reward)))
    Path(os.path.dirname(path) or ".").mkdir(parents=True, exist_ok=True)
    payload = {"reward": reward}
    if error:
        payload["error"] = str(error)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    for jpath in ("/logs/agent/judge_justification.txt", "/logs/verifier/judge_justification.txt"):
        try:
            Path(os.path.dirname(jpath)).mkdir(parents=True, exist_ok=True)
            with open(jpath, "w", encoding="utf-8") as f:
                f.write(f"Score: {reward}\n\n{justification}\n")
        except Exception:
            pass
    print(f"Score: {reward}")
    print(justification)


def extract_json(text):
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    m = re.search(r"\{[\s\S]*\}", text)
    return m.group(0) if m else text


def read_text(path, cap):
    try:
        return Path(path).read_text(encoding="utf-8-sig", errors="ignore")[:cap]
    except Exception as e:
        return f"<<could not read {path}: {type(e).__name__}: {e}>>"


def png_evidence(path):
    p = Path(path)
    if not p.is_file():
        return f"{path.name}: MISSING"
    size = p.stat().st_size
    try:
        with open(p, "rb") as f:
            valid = f.read(8) == b"\x89PNG\r\n\x1a\n"
    except Exception:
        valid = False
    dims = "unknown"
    try:
        from PIL import Image
        with Image.open(p) as im:
            dims = f"{im.width}x{im.height}"
    except Exception:
        pass
    return f"{path.name}: present, {size} bytes, valid_png={valid}, dimensions={dims}"


def mp4_evidence(path):
    p = Path(path)
    if not p.is_file():
        return f"{path.name}: MISSING"
    dur = frames = "unknown"
    try:
        dur = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
            stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        pass
    try:
        frames = subprocess.check_output(
            ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
            stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        pass
    return f"{path.name}: present, duration_sec={dur}, frame_count={frames}"


def gather_evidence():
    lines = ["EXPECTED 20 ISO3: " + ", ".join(EXPECTED_ISO3), "", "FILE EVIDENCE:"]
    domain_row_total = 0
    for name in CSV_FILES:
        p = AGENT_DIR / name
        if p.is_file():
            try:
                rows = max(0, sum(1 for _ in open(p, encoding="utf-8-sig", errors="ignore")) - 1)
            except Exception:
                rows = "?"
            if name in DOMAIN_EXPECTED_ROWS:
                domain_row_total += rows if isinstance(rows, int) else 0
                exp = DOMAIN_EXPECTED_ROWS[name]
                ok = rows == exp if isinstance(rows, int) else False
                lines.append(f"  {name}: present, ~{rows} data rows (expected {exp}) {'OK' if ok else 'MISMATCH'}")
            else:
                lines.append(f"  {name}: present, ~{rows} data rows")
        else:
            if name in DOMAIN_EXPECTED_ROWS:
                lines.append(f"  {name}: MISSING (expected {DOMAIN_EXPECTED_ROWS[name]} rows)")
            else:
                lines.append(f"  {name}: MISSING")
    audit = AGENT_DIR / "source_audit.csv"
    if audit.is_file() and domain_row_total:
        try:
            audit_rows = max(0, sum(1 for _ in open(audit, encoding="utf-8-sig", errors="ignore")) - 1)
        except Exception:
            audit_rows = "?"
        lines.append(
            f"  source_audit.csv vs domain rows hint: audit ~{audit_rows} rows, domain total ~{domain_row_total}"
        )
    gaps_p = AGENT_DIR / "data_gaps.csv"
    if gaps_p.is_file():
        try:
            gap_rows = max(0, sum(1 for _ in open(gaps_p, encoding="utf-8-sig", errors="ignore")) - 1)
        except Exception:
            gap_rows = "?"
        lines.append(f"  data_gaps.csv row hint: ~{gap_rows} data rows (expected at least 34)")
    lines.append("  " + png_evidence(CHARTS_DIR / "resilience_ranking.png"))
    lines.append("  " + png_evidence(CHARTS_DIR / "domain_heatmap.png"))
    lines.append("  " + mp4_evidence(AGENT_DIR / "resilience_race.mp4"))

    url_range_count = 0
    url_year_mismatch = 0
    url_rows_checked = 0
    for dname in DOMAIN_EXPECTED_ROWS:
        dp = AGENT_DIR / dname
        if not dp.is_file():
            continue
        try:
            text = read_text(dp, PER_FILE_CHAR_CAP)
            for ln in text.splitlines()[1:51]:
                if "source_url" in ln.lower() or not ln.strip():
                    continue
                parts = ln.split(",")
                if len(parts) < 6:
                    continue
                year_val = parts[3].strip()
                url = parts[5] if len(parts) > 5 else ""
                url_rows_checked += 1
                if re.search(r"date=2010:2023", url):
                    url_range_count += 1
                elif year_val.isdigit() and f"date={year_val}:{year_val}" not in url:
                    url_year_mismatch += 1
        except Exception:
            pass
    lines.append(
        f"  URL HINTS (sample of domain rows): checked ~{url_rows_checked}, "
        f"date=2010:2023 ranges ~{url_range_count}, year/url mismatches ~{url_year_mismatch}"
    )

    rp = AGENT_DIR / "diagnostic_report.md"
    if rp.is_file():
        report_text = read_text(rp, 10_000_000)
        word_count = len(report_text.split())
        lines.append(f"  diagnostic_report.md: present, ~{word_count} words")
        label_patterns = [
            ("overall_index:", r"^overall_index:\s*[\d.]+"),
            ("rank:", r"^rank:\s*\d+"),
            ("macro_score:", r"^macro_score:\s*[\d.]+"),
            ("strongest_domain:", r"^strongest_domain:\s*\w+"),
            ("weakest_domain:", r"^weakest_domain:\s*\w+"),
        ]
        lines.append("  REPORT LABEL HINTS (LLM uses these as evidence, not automatic scoring):")
        for label, pat in label_patterns:
            count = len(re.findall(pat, report_text, flags=re.MULTILINE | re.IGNORECASE))
            lines.append(f"    {label} line count = {count} (expected 20 per country section)")
        bad_report_decimals = []
        for m in re.finditer(
            r"^(overall_index|macro_score|health_score|education_score|poverty_score|governance_score|climate_score):\s*([\d.]+)",
            report_text,
            flags=re.MULTILINE | re.IGNORECASE,
        ):
            val = m.group(2)
            if "." not in val or len(val.split(".")[1]) != 2:
                bad_report_decimals.append(f"{m.group(1)}:{val}")
        lines.append(
            f"    report labeled score two-decimal hint: "
            f"{'CLEAN' if not bad_report_decimals else f'NOT CLEAN - {len(bad_report_decimals)} labels use fewer than 2 decimals (e.g. {bad_report_decimals[:4]})'}"
        )
        lines.append(
            f"    exact heading '## Data Coverage Caveats' present = "
            f"{'yes' if '## Data Coverage Caveats' in report_text else 'no'}"
        )
        meth = re.search(r"^## Methodology\s*$([\s\S]*?)(?=^## |\Z)", report_text, flags=re.MULTILINE)
        meth_body = (meth.group(1) if meth else "").strip()
        before_subheading = re.split(r"^###\s", meth_body, maxsplit=1, flags=re.MULTILINE)[0]
        anim_named_in_methodology = bool(
            re.search(r"resilience_race\.mp4|SP\.DYN\.LE00\.IN|life expectancy", before_subheading, re.I)
        )
        lines.append(
            f"    MP4 series named in ## Methodology before any ### subsection: "
            f"{'yes' if anim_named_in_methodology else 'no'}"
        )
        comp = AGENT_DIR / "composite_index.csv"
        if comp.is_file():
            comp_lines = [
                ln.strip() for ln in read_text(comp, PER_FILE_CHAR_CAP).splitlines()
                if ln.strip() and not ln.lower().startswith("iso3")
            ]
            bad_precision = []
            blank_gov = 0
            for ln in comp_lines:
                parts = ln.split(",")
                if len(parts) < 10:
                    continue
                if not parts[6].strip():
                    blank_gov += 1
                for val in parts[2:9]:
                    if "." in val and len(val.split(".")[1]) != 2:
                        bad_precision.append(val)
            lines.append(
                f"    composite_index.csv two-decimal hint: "
                f"{'CLEAN - all score fields use 2 decimals' if not bad_precision else f'NOT CLEAN - {len(bad_precision)} score values use fewer than 2 decimal places (e.g. {bad_precision[:3]})'}"
            )
            lines.append(
                f"    composite_index.csv blank governance_score rows: {blank_gov} (expected 0)"
            )
    else:
        lines.append("  diagnostic_report.md: MISSING")
    return "\n".join(lines)


def gather_deliverables():
    parts = []
    for name in CSV_FILES:
        p = AGENT_DIR / name
        if p.is_file():
            parts.append(f"=== {name} ===\n{read_text(p, PER_FILE_CHAR_CAP)}")
    rp = AGENT_DIR / "diagnostic_report.md"
    if rp.is_file():
        parts.append(f"=== diagnostic_report.md ===\n{read_text(rp, REPORT_CHAR_CAP)}")
    return "\n\n".join(parts)


def build_prompt(brief, evidence, deliverables):
    ids = [cid for cid, _ in RUBRIC_ITEMS]
    rubric = "\n".join(f'  - "{cid}": {desc}' for cid, desc in RUBRIC_ITEMS)
    return f"""You are a meticulous, independent data-analysis reviewer grading a cross-country
"Sovereign Development Resilience Diagnostic". Evaluate the submission below ONLY on the evidence
provided. Do not use outside knowledge to fill gaps, and do not reward vague or generic work.

Grade each rubric item as a BINARY result: 1 if the item is fully satisfied by the submission,
0 if it is not (absent, incomplete, wrong, or fabricated). Do not give partial fractions; each
item is worth exactly one point. Judge each item independently of the others.

Use the FILE EVIDENCE section as factual ground truth for row counts, PNG/MP4 validity, URL hints,
and two-decimal hints. When a rubric item says "if FILE EVIDENCE ... this item is not satisfied",
you must score 0 when that evidence condition is met even if the prose deliverables look acceptable.
Do not give credit for report labeled lines that use one-decimal values when composite_index.csv
uses one-decimal scores. Do not pass gap or summary items when data_gaps.csv has fewer than 34 rows.

Use the FILE EVIDENCE section to decide items about file existence, chart validity, and the
animation (duration and frame count). Use the TEXT DELIVERABLES for content and numeric items.

RUBRIC ITEMS:
{rubric}

Respond with ONLY this JSON (one entry per item id, score is 0 or 1):
{{"items": {{ {", ".join(f'"{i}": {{"score": 0 or 1, "note": "<short reason>"}}' for i in ids)} }}}}

=== TASK BRIEF (the rules the work had to follow) ===
{brief}

=== FILE EVIDENCE ===
{evidence}

=== TEXT DELIVERABLES ===
{deliverables}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-dir", default="/logs/agent")
    parser.add_argument("--brief", default="/input_artifacts/diagnostic_brief.md")
    parser.add_argument("--reward-out", default="/logs/verifier/reward.json")
    args = parser.parse_args()

    global AGENT_DIR, CHARTS_DIR
    AGENT_DIR = Path(args.agent_dir)
    CHARTS_DIR = AGENT_DIR / "charts"

    if not AGENT_DIR.is_dir() or not any(AGENT_DIR.iterdir()):
        write_reward(args.reward_out, 0.0,
                     f"No agent output under {AGENT_DIR} (fail-closed).",
                     error="no_agent_output")
        return

    try:
        from openai import OpenAI
    except Exception as e:
        write_reward(args.reward_out, 0.0,
                     f"LLM judge dependency unavailable (fail-closed): {type(e).__name__}: {e}",
                     error="judge_dependency_unavailable")
        return

    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        write_reward(args.reward_out, 0.0,
                     "LLM judge could not run because FIREWORKS_API_KEY is not set (fail-closed).",
                     error="missing_api_key")
        return

    brief = read_text(args.brief, 40000)
    evidence = gather_evidence()
    deliverables = gather_deliverables()
    if not deliverables.strip():
        deliverables = "(No CSV or report text could be read from /logs/agent/.)"

    prompt = build_prompt(brief, evidence, deliverables)
    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    run_item_scores = []
    last_err = None
    for _ in range(LLM_JUDGE_RUNS):
        parsed = None
        for _ in range(LLM_RETRIES):
            try:
                resp = client.chat.completions.create(
                    model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0)
                parsed = json.loads(extract_json(resp.choices[0].message.content or ""))
                break
            except Exception as e:
                last_err = e
        if parsed is None:
            continue
        items = parsed.get("items", parsed)
        scores = {}
        for cid, _ in RUBRIC_ITEMS:
            v = items.get(cid)
            if isinstance(v, dict):
                raw = v.get("score", 0)
            else:
                raw = v if v is not None else 0
            try:
                scores[cid] = 1 if float(raw) >= 0.5 else 0
            except Exception:
                scores[cid] = 0
        run_item_scores.append(scores)

    if not run_item_scores:
        write_reward(args.reward_out, 0.0,
                     f"LLM judge error (fail-closed): {last_err}\n\n{evidence}",
                     error="llm_judge_failed")
        return

    results = []
    for cid, _ in RUBRIC_ITEMS:
        run_scores = [run[cid] for run in run_item_scores]
        avg = sum(run_scores) / len(run_scores)
        passed = 1 if avg >= 0.5 else 0
        results.append((cid, passed, f"avg={avg:.2f} over {len(run_item_scores)} judge runs"))

    total = len(results)
    satisfied = sum(p for _, p, _ in results)
    reward = satisfied / total if total else 0.0

    lines = [
        f"Rubric score: {satisfied}/{total} binary items satisfied = {round(reward, 4)}",
        f"(reward = items satisfied / total items; averaged over {len(run_item_scores)} LLM judge runs)",
        "",
        "FILE EVIDENCE:",
        evidence,
        "",
        "PER-ITEM RESULTS:",
    ]
    for cid, passed, note in results:
        lines.append(f"  [{'PASS' if passed else 'FAIL'}] {cid}: {note}")

    write_reward(args.reward_out, reward, "\n".join(lines))


if __name__ == "__main__":
    main()
