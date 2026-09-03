# Source provenance

The source of record for current recommendation status is GAO-25-108032, published May 7, 2025: https://www.gao.gov/products/gao-25-108032.

Each selected recommendation is paired with the text of its originating GAO report. Official product URLs are recorded per unit in `source_manifest.csv`. Because the GAO asset host rejected automated downloads from this build environment, report text was extracted from the official public PDF or product page through `https://r.jina.ai/http://www.gao.gov/...` on 2026-08-29. The `URL Source` header preserved in each report file identifies the official GAO URL used by the extraction service.

The 24 originating reports contain 423,346 measured words. The current status letter contains 11,756 measured words. Unique source material therefore totals 435,102 words. Including the per-unit status excerpts supplied for bounded reading, the input-artifact files contain 442,937 words before manifest and roster metadata.

The corpus is intentionally frozen and must not be supplemented with live status. A missing target date or completion date in a unit's supplied status excerpt is a genuine source gap and must remain `unknown`; it must not be filled from later web updates.

## Runtime access note

The input image also provides the content-neutral `source-window` command for optional bounded access to the frozen text corpus. It can inventory files, locate literal or regular-expression matches, and return exact character slices of at most 12,000 characters. It performs no recommendation selection, classification, planning, or scoring. Run `source-window --help` for its command syntax.
