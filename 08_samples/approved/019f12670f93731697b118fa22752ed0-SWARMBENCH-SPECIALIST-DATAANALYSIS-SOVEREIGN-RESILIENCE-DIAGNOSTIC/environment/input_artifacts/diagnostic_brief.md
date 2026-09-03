Diagnostic brief: Sovereign Resilience Diagnostic

This brief defines the engagement: the fixed country cohort, the exact indicators to pull per domain,
and the scoring method. Use exactly what is defined here so the 20 countries stay comparable.

1. Country cohort (use exactly these 20, no substitutions)

| iso3 | country | region | income_group |
|------|---------|--------|--------------|
| NGA | Nigeria | Sub-Saharan Africa | Lower-middle |
| KEN | Kenya | Sub-Saharan Africa | Lower-middle |
| ETH | Ethiopia | Sub-Saharan Africa | Low |
| GHA | Ghana | Sub-Saharan Africa | Lower-middle |
| ZAF | South Africa | Sub-Saharan Africa | Upper-middle |
| RWA | Rwanda | Sub-Saharan Africa | Low |
| IND | India | South Asia | Lower-middle |
| BGD | Bangladesh | South Asia | Lower-middle |
| PAK | Pakistan | South Asia | Lower-middle |
| IDN | Indonesia | Southeast Asia | Upper-middle |
| VNM | Vietnam | Southeast Asia | Lower-middle |
| PHL | Philippines | Southeast Asia | Lower-middle |
| BRA | Brazil | Latin America | Upper-middle |
| COL | Colombia | Latin America | Upper-middle |
| PER | Peru | Latin America | Upper-middle |
| MEX | Mexico | Latin America | Upper-middle |
| EGY | Egypt | MENA | Lower-middle |
| MAR | Morocco | MENA | Lower-middle |
| UKR | Ukraine | Europe & Central Asia | Upper-middle |
| UZB | Uzbekistan | Europe & Central Asia | Lower-middle |

2. Indicators per domain

`direction` says whether a higher value is better or worse. `wb_source` is the World Bank source
database for the request: 2 is World Development Indicators (the default), 75 is the Worldwide
Governance Indicators database and MUST be passed as `source=75`. Pull the full 2010-2023 series for
every country.

| domain | indicator_code | indicator_name | direction | wb_source |
|--------|----------------|----------------|-----------|-----------|
| macro | NY.GDP.MKTP.KD.ZG | GDP growth (annual %) | higher_better | 2 |
| macro | NY.GDP.PCAP.CD | GDP per capita (current US$) | higher_better | 2 |
| macro | FP.CPI.TOTL.ZG | Inflation, consumer prices (annual %) | lower_better | 2 |
| macro | BN.CAB.XOKA.GD.ZS | Current account balance (% of GDP) | higher_better | 2 |
| macro | GC.DOD.TOTL.GD.ZS | Central government debt, total (% of GDP) | lower_better | 2 |
| health | SP.DYN.LE00.IN | Life expectancy at birth (years) | higher_better | 2 |
| health | SH.DYN.MORT | Under-5 mortality rate (per 1,000) | lower_better | 2 |
| health | SH.STA.MMRT | Maternal mortality ratio (per 100,000) | lower_better | 2 |
| health | SH.XPD.CHEX.GD.ZS | Current health expenditure (% of GDP) | higher_better | 2 |
| health | SH.IMM.MEAS | Measles immunization (% of children 12-23 mo) | higher_better | 2 |
| education | SE.PRM.ENRR | Primary school enrollment (gross %) | higher_better | 2 |
| education | SE.SEC.ENRR | Secondary school enrollment (gross %) | higher_better | 2 |
| education | SE.ADT.LITR.ZS | Adult literacy rate (% ages 15+) | higher_better | 2 |
| education | SE.XPD.TOTL.GD.ZS | Government expenditure on education (% of GDP) | higher_better | 2 |
| poverty | SI.POV.DDAY | Poverty headcount at $2.15/day (%) | lower_better | 2 |
| poverty | SI.POV.GINI | Gini index | lower_better | 2 |
| poverty | SI.DST.FRST.20 | Income share held by lowest 20% | higher_better | 2 |
| poverty | SL.UEM.TOTL.ZS | Unemployment, total (% of labor force, modeled ILO) | lower_better | 2 |
| governance | CC.EST | Control of Corruption (estimate) | higher_better | 75 |
| governance | RL.EST | Rule of Law (estimate) | higher_better | 75 |
| governance | GE.EST | Government Effectiveness (estimate) | higher_better | 75 |
| governance | RQ.EST | Regulatory Quality (estimate) | higher_better | 75 |
| governance | VA.EST | Voice and Accountability (estimate) | higher_better | 75 |
| governance | PV.EST | Political Stability and Absence of Violence (estimate) | higher_better | 75 |
| climate | EN.ATM.CO2E.PC | CO2 emissions per capita (metric tons) | lower_better | 2 |
| climate | EG.FEC.RNEW.ZS | Renewable energy consumption (% of final energy) | higher_better | 2 |
| climate | EG.ELC.ACCS.ZS | Access to electricity (% of population) | higher_better | 2 |
| climate | EN.ATM.PM25.MC.M3 | PM2.5 air pollution, mean annual exposure (ug/m3) | lower_better | 2 |
| climate | AG.LND.FRST.ZS | Forest area (% of land area) | higher_better | 2 |

The poverty/inequality and adult-literacy series are sparse; several countries will be missing years.
If an indicator code has been deprecated, resolve the current code via
`https://api.worldbank.org/v2/indicator?format=json`.

3. Scoring method (apply exactly so countries stay comparable)

Indicator values
- For each indicator, use the most recent year in 2010-2023 that has a real (non-null) value for that
  country. Record that year alongside the value.
- If a country has no value for an indicator anywhere in 2010-2023, treat it as missing: log it in the
  gaps list with fallback year "none" and leave it out of that country's sub-score average. Never
  substitute zero and never carry a value across from a different country.

Normalizing each indicator to 0-100
- Normalize each indicator across the 20 cohort countries using min-max scaling on the values that
  exist (ignore missing ones when finding the min and max).
- If the indicator's direction is `higher_better`:
  `normalized = 100 * (value - min) / (max - min)`
- If the direction is `lower_better`, invert it:
  `normalized = 100 * (max - value) / (max - min)`
- If max equals min for an indicator (no spread), give every country with a value 50 for that indicator.

Domain sub-score
- A country's domain sub-score is the simple average of its available normalized indicator values in
  that domain, on a 0-100 scale.
- If a country is missing some indicators in a domain, average only the ones it has, and note how many
  of the domain's indicators were available for that country.

Overall resilience index
- Weight the six domains equally (each contributes one sixth of the index).
- The overall Development Resilience Index for a country is the simple average of its six domain
  sub-scores (macro, health, education, poverty, governance, climate), on a 0-100 scale.
- Every country must have a numeric sub-score in all six domains before ranking; do not leave
  governance_score or any other domain column blank and do not average over fewer than six domains.

Ranking
- Rank countries by the overall index in descending order: rank 1 is the most resilient. Break exact
  ties by the higher governance sub-score.

4. Expected domain CSV row counts (scoring-year rows only)

Each domain CSV must have exactly one row per country-indicator pair for the scoring year.
With all 20 countries present the row counts must be:

| domain file | indicators per country | expected data rows |
|-------------|------------------------|--------------------|
| domain_macro.csv | 5 | 100 |
| domain_health.csv | 5 | 100 |
| domain_education.csv | 4 | 80 |
| domain_poverty.csv | 4 | 80 |
| domain_governance.csv | 6 | 120 |
| domain_climate.csv | 5 | 100 |

5. API URL patterns (use for source_url and source_audit.csv)

Non-governance indicators (wb_source 2), scoring-year pull example:
`https://api.worldbank.org/v2/country/{ISO3}/indicator/{CODE}?date={YEAR}:{YEAR}&format=json`

Governance indicators (wb_source 75), scoring-year pull example:
`https://api.worldbank.org/v2/country/{ISO3}/indicator/{CODE}?date={YEAR}:{YEAR}&format=json&source=75`
(A `GOV_WGI_` prefix in the indicator path is acceptable as long as `source=75` is present.)

The `year` column in each domain CSV row must match the year embedded in that row's source_url
(use `date=YYYY:YYYY`, not a multi-year range like `date=2010:2023`).

6. source_audit.csv

Columns: iso3, domain, indicator_code, year, source_url
Exactly one row per domain CSV row (audit row count must equal the sum of domain CSV rows).

7. data_gaps.csv

Columns: iso3, domain, indicator_code, year_requested, fallback_year
Log missing country-indicator pairs and null years from the 2010-2023 pull. At least 34 rows
are expected. Every country-indicator missing from a domain CSV must appear here. Prefer one
row per missing pair rather than expanding every null panel cell into thousands of rows.

8. Composite index rules

- Columns only: iso3, country, macro_score, health_score, education_score, poverty_score,
  governance_score, climate_score, overall_index, rank, strongest_domain, weakest_domain.
- Every numeric score column uses exactly two decimal places.
- overall_index = simple average of macro_score, health_score, education_score, poverty_score,
  governance_score, and climate_score (equal weights, all six required).
- No blank governance_score or other domain column; do not average over fewer than six domains.
- strongest_domain and weakest_domain use short tokens macro, health, education, poverty,
  governance, climate matching the highest and lowest sub-scores in that row.
