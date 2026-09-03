I run a data-storytelling studio and I need a set of short animated **data-story reels** built
from live World Bank figures — one per topic — plus a manifest indexing them. Each reel isn't
just a chart: it has to *tell the story of the data* faithfully. This needs network access;
there's no local copy of the numbers, so you fetch each series yourself.

There are sixteen topics. Each is a country + indicator, paired with a **peer country** to
compare against. The same list is on disk at `/input_artifacts/sections.json`.

| section_id   | country_code | indicator_code        | country        | indicator                     | peer (country_code) |
|--------------|--------------|-----------------------|----------------|-------------------------------|---------------------|
| pop_de       | DE           | SP.POP.TOTL           | Germany        | Total population              | France (FR)         |
| gdppc_jp     | JP           | NY.GDP.PCAP.CD        | Japan          | GDP per capita (USD)          | South Korea (KR)    |
| life_br      | BR           | SP.DYN.LE00.IN        | Brazil         | Life expectancy at birth      | Argentina (AR)      |
| elec_ng      | NG           | EG.ELC.ACCS.ZS        | Nigeria        | Access to electricity (%)     | Kenya (KE)          |
| internet_id  | ID           | IT.NET.USER.ZS        | Indonesia      | Internet users (%)            | Philippines (PH)    |
| urban_mx     | MX           | SP.URB.TOTL.IN.ZS     | Mexico         | Urban population (%)          | Colombia (CO)       |
| co2pc_us     | US           | EN.GHG.CO2.PC.CE.AR5  | United States  | CO2 emissions per capita      | China (CN)          |
| gdpgr_in     | IN           | NY.GDP.MKTP.KD.ZG     | India          | GDP growth (%)                | China (CN)          |
| infl_tr      | TR           | FP.CPI.TOTL.ZG        | Turkey         | Inflation (%)                 | Brazil (BR)         |
| unemp_es     | ES           | SL.UEM.TOTL.ZS        | Spain          | Unemployment (%)              | Germany (DE)        |
| fert_eg      | EG           | SP.DYN.TFRT.IN        | Egypt          | Fertility rate                | India (IN)          |
| prim_et      | ET           | SE.PRM.ENRR           | Ethiopia       | Primary school enrollment (%) | Kenya (KE)          |
| mort_in      | IN           | SH.DYN.MORT           | India          | Under-5 mortality rate        | Bangladesh (BD)     |
| rural_cn     | CN           | SP.RUR.TOTL.ZS        | China          | Rural population (%)          | India (IN)          |
| renew_de     | DE           | EG.FEC.RNEW.ZS        | Germany        | Renewable energy (%)          | France (FR)         |
| milit_us     | US           | MS.MIL.XPND.GD.ZS     | United States  | Military expenditure (% GDP)  | Russia (RU)         |

Fetch the data live

For each topic, pull the 2000–2022 series for BOTH the country and its peer from:

```
https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&date=2000:2022&per_page=100
```

The response is `[meta, data]`; points are in `response[1]`, each `{"date":"YYYY","value":<number|null>}`.
Use the non-null points. From the country's own series work out, for real:

- **latest_value** and **latest_year** — the most recent non-null point;
- **peak_year** — the year with the highest value; **trough_year** — the year with the lowest value;
- **trend_direction** — `"rising"`, `"falling"`, or `"flat"` (compare the latest value to the earliest:
  rising if it grew more than ~2%, falling if it fell more than ~2%, otherwise flat);
- **peer_comparison** — fetch the peer's latest value for the SAME indicator and say whether the
  country's latest is `"higher"` or `"lower"` than the peer's.

Don't guess any of these — derive them from the data you fetch.

What to produce (exact paths)

For each topic, write a faithful **data story** and render it as a reel.

1. One MP4 per topic at `/logs/agent/reels/<section_id>.mp4`. Each: 7.0–9.0s, an mp4, at least 320px on
   the short side, and **genuinely animated** (the chart draws/grows over the 2000–2022 span — not one
   frame held for 8s). On screen, large and legible, show the country, the indicator, the latest value,
   and the story beats (the trend, the peak/trough year, the peer comparison).

2. `/logs/agent/manifest.json`, a JSON **array** with one record per topic:
   ```json
   {"section_id":"pop_de","country":"Germany","indicator":"Total population",
    "latest_value":83177813,"latest_year":2022,"trend_direction":"flat",
    "peak_year":2021,"trough_year":2011,"peer_country":"France","peer_comparison":"higher",
    "narrative":"<150-250 word data story, see below>","reel":"reels/pop_de.mp4"}
   ```

3. `/logs/agent/output.json` = `{"sections":[ ...the same sixteen records... ]}`.

The **narrative** is the heart of it: 150–250 words of clear prose that faithfully tells THIS series'
story — where it started and ended, the overall trend, what happened at the peak and trough years, and
how the country compares to its peer — using the real numbers you fetched. It must be specific to this
series (real years and values), not generic filler, and must not state anything the data doesn't show.
`latest_value` is the raw number (no comma formatting).

Where the effort pays off

A reel only counts when it's the real thing: built from data you actually fetched, the right length,
genuinely animated, with the country and indicator legible on screen. The story carries the most weight —
each narrative is judged on whether it faithfully and specifically tells that series' real story (correct
trend, the actual peak/trough years, the right peer comparison, the real numbers) and reads clearly. A
generic, vague, or fabricated story — or one that gets the turning points or comparison wrong — earns
little, no matter how pretty the chart. Sixteen shallow stories lose to sixteen faithful ones.

One last thing: always leave something behind. Write `/logs/agent/output.json` and the manifest and
render whatever reels you finished, even if you only got partway through the sixteen topics.
