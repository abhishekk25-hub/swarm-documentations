# Maternal & newborn health data pack — board meeting

There is a board meeting coming next week for funding cycle. we want to fetch the real time data from the open source urls to provide out our analysis, prepare a deck and short document for our next meeting.

I have provided you 100 countries at the bottom, split into four regions. Let us keep them in that order — I've already sorted them the way I want them to appear.

For each country I need the latest value from the World Bank API for three things: maternal mortality ratio, skilled birth attendance, and current health spending as a % of GDP. Below are the source endpoints.

- MMR: "https://api.worldbank.org/v2/country/{ISO2}/indicator/SH.STA.MMRT?format=json&mrv=5"
- Skilled birth attendance: "https://api.worldbank.org/v2/country/{ISO2}/indicator/SH.STA.BRTC.ZS?format=json&mrv=5"
- Health expenditure: "https://api.worldbank.org/v2/country/{ISO2}/indicator/SH.XPD.CHEX.GD.ZS?format=json&mrv=5"

Then check the WHO country profile for each one — "https://www.who.int/countries/{iso3-lowercase}" — and write one short line giving useful context on the country's health system or situation. Just a sentence.

Put everything under /logs/agent/maternal-health-board folder:

- data.csv — country details, the latest World Bank values and their years, the WHO note, and all the source URLs.
- mmr_trend.csv — the MMR trend values the World Bank returns.
- source_audit.csv — Original links from where data is fetched.

For the board deck, make dashboard.pptx with exactly six slides — no title or cover slide. Slide 1 = Africa table, Slide 2 = Asia table, Slide 3 = Americas table, Slide 4 = Europe & Oceania table, Slide 5 = a horizontal bar chart titled "Global MMR Comparison", Slide 6 = a scatter plot titled "MMR vs Health Expenditure."

On the table slides keep country order as i provided and only show the below fields: Country, ISO3, MMR, MMR Year, Skilled Birth Att %, Health Exp % GDP.

Sort the bar chart highest to lowest MMR. Colour the bars by region — Africa red, Asia orange, Americas blue, Europe & Oceania green. For the scatter, health spending on the x-axis, MMR on the y, label the dots with ISO3, and use the same region colours.

Finally a short summary.docx I can read. Cover:
- The average MMR across all 100 countries
- The top 3 highest and lowest burden countries by MMR
- The average MMR per region and the biggest gap between regions
- Which countries are missing MMR data
- Countries where skilled birth attendance is below 50%
- Fifteen investment candidates ranked by a priority score (MMR divided by health expenditure — higher means more impact per dollar)
- Whether MMR is improving or worsening for countries that have multi-year trend data

Real names and numbers — if data is missing, leave it missing.


- Country list:

Africa (35): Nigeria (NG/NGA), Sierra Leone (SL/SLE), Chad (TD/TCD), South Sudan (SS/SSD), DR Congo (CD/COD), Kenya (KE/KEN), Ethiopia (ET/ETH), Ghana (GH/GHA), Rwanda (RW/RWA), South Africa (ZA/ZAF), Mali (ML/MLI), Niger (NE/NER), Angola (AO/AGO), Mozambique (MZ/MOZ), Tanzania (TZ/TZA), Uganda (UG/UGA), Zambia (ZM/ZMB), Zimbabwe (ZW/ZWE), Burkina Faso (BF/BFA), Guinea (GN/GIN), Cameroon (CM/CMR), Senegal (SN/SEN), Côte d'Ivoire (CI/CIV), Madagascar (MG/MDG), Malawi (MW/MWI), Somalia (SO/SOM), Sudan (SD/SDN), Eritrea (ER/ERI), Liberia (LR/LBR), Togo (TG/TGO), Benin (BJ/BEN), Congo (CG/COG), Central African Republic (CF/CAF), Gambia (GM/GMB), Mauritania (MR/MRT).

Asia (25): India (IN/IND), Pakistan (PK/PAK), Bangladesh (BD/BGD), Myanmar (MM/MMR), Cambodia (KH/KHM), Nepal (NP/NPL), Indonesia (ID/IDN), Philippines (PH/PHL), Afghanistan (AF/AFG), Vietnam (VN/VNM), Laos (LA/LAO), Timor-Leste (TL/TLS), Papua New Guinea (PG/PNG), Sri Lanka (LK/LKA), Thailand (TH/THA), Yemen (YE/YEM), Bhutan (BT/BTN), Kyrgyzstan (KG/KGZ), Tajikistan (TJ/TJK), Uzbekistan (UZ/UZB), Azerbaijan (AZ/AZE), Mongolia (MN/MNG), Armenia (AM/ARM), Turkmenistan (TM/TKM), Georgia (GE/GEO).

Americas (20): Haiti (HT/HTI), Bolivia (BO/BOL), Brazil (BR/BRA), Mexico (MX/MEX), United States (US/USA), Peru (PE/PER), Colombia (CO/COL), Venezuela (VE/VEN), Guatemala (GT/GTM), Honduras (HN/HND), Nicaragua (NI/NIC), El Salvador (SV/SLV), Paraguay (PY/PRY), Ecuador (EC/ECU), Dominican Republic (DO/DOM), Cuba (CU/CUB), Jamaica (JM/JAM), Trinidad and Tobago (TT/TTO), Guyana (GY/GUY), Suriname (SR/SUR).

Europe & Oceania (20): Sweden (SE/SWE), United Kingdom (GB/GBR), France (FR/FRA), Germany (DE/DEU), Russia (RU/RUS), Ukraine (UA/UKR), Romania (RO/ROU), Greece (GR/GRC), Turkey (TR/TUR), Australia (AU/AUS), Poland (PL/POL), Italy (IT/ITA), Spain (ES/ESP), Portugal (PT/PRT), Netherlands (NL/NLD), Hungary (HU/HUN), Bulgaria (BG/BGR), Albania (AL/ALB), New Zealand (NZ/NZL), Norway (NO/NOR).
