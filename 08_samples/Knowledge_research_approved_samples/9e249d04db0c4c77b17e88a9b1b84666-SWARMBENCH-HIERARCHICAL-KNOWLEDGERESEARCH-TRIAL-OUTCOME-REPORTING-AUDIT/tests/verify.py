import csv
import json
import os
import re
import sys
import traceback

AGENT_DIR = "/logs/agent"
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_DIR = os.path.join(TESTS_DIR, "test_logic", "key")
SRC_DIR = os.path.join(TESTS_DIR, "test_logic", "corpus")
LEDGER = os.path.join(AGENT_DIR, "outcome_ledger.csv")
BASIS = os.path.join(AGENT_DIR, "prespecification_basis.csv")

LEDGER_COLUMNS = [
    "nct", "unit_type", "registry_measure", "registry_role", "registry_timeframe",
    "reported", "reporting_document", "reported_label", "reported_instrument",
    "reported_role", "role_evidence_quote", "result_quote",
]

NUMERIC = re.compile(r"\d+\.\d+|\d+\s*%|[Pp]\s*[=<>]\s*\.?\d|95%\s*CI|\bn\s*=\s*\d+|\b\d+\b")
CAPTION = re.compile(r"^\s*(?:Table|Figure|Fig\.?|Appendix|Supplementary|Panel|Exhibit)\s*[0-9IVX]", re.I)
FILLER = {"this", "that", "these", "those", "here", "there", "such", "same", "above", "below", "following"}
NOT_A_RESULT = re.compile(
    r"\bwill be (?:measured|assessed|collected|recorded|calculated|analysed|analyzed)\b"
    r"|\b(?:is|are) defined as\b|\bwill be the\b|\bwe will\b"
    r"|\b(?:outcomes?|endpoints?) (?:will be|are to be)\b",
    re.I,
)
WORD = re.compile(r"[a-z0-9]+")
STOP = set(
    "the a an of and or in on for to with by from as at is are was were be been will shall score "
    "scores total item items scale questionnaire index inventory measure measured measures "
    "assessment assessed change changes baseline follow up week weeks month months day days year "
    "years patient patients participant participants group groups study trial number percentage "
    "proportion mean median rate time point points visit visits".split()
)

KEY = {}
DOCS = {}
ROWS = []
BASIS_ROWS = {}
BY_TRIAL = {}
MATCH = {}


def toks(text):
    return {w for w in WORD.findall((text or "").lower()) if w not in STOP and len(w) > 2}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def norm_id(value):
    return (value or "").strip().upper().replace(".TXT", "")


def load():
    for name in sorted(os.listdir(KEY_DIR)):
        if name.endswith(".json"):
            k = json.load(open(os.path.join(KEY_DIR, name)))
            KEY[k["nct"]] = k
            for pmcid in k["publications"]:
                path = os.path.join(SRC_DIR, "trials", k["nct"], "publications", pmcid + ".txt")
                DOCS[(k["nct"], pmcid)] = open(path).read() if os.path.exists(path) else ""
    if os.path.exists(LEDGER):
        with open(LEDGER, newline="") as fh:
            for row in csv.DictReader(fh):
                clean = {c: (row.get(c) or "").strip() for c in LEDGER_COLUMNS}
                clean["_nct"] = norm_id(clean["nct"])
                ROWS.append(clean)
    for row in ROWS:
        BY_TRIAL.setdefault(row["_nct"], []).append(row)
    if os.path.exists(BASIS):
        with open(BASIS, newline="") as fh:
            for row in csv.DictReader(fh):
                BASIS_ROWS[norm_id(row.get("nct"))] = row
    for nct, key in KEY.items():
        rows = [r for r in BY_TRIAL.get(nct, []) if r["unit_type"].lower().startswith("prespec")]
        used = set()
        for unit in key["prespecified_units"]:
            want = toks(unit["measure"])
            best, best_row = 0.0, None
            for i, r in enumerate(rows):
                if i in used:
                    continue
                s = jaccard(want, toks(r["registry_measure"]))
                if s > best:
                    best, best_row = s, i
            if best_row is not None and best >= 0.6:
                used.add(best_row)
                MATCH[(nct, unit["uid"])] = rows[best_row]


def says_yes(value):
    return (value or "").strip().lower() in {"yes", "y", "true", "1"}


def authored(nct, row):
    if row is None:
        return False
    quote = row["result_quote"].strip()
    if len(quote.split()) < 6:
        return False
    blob = DOCS.get((nct, norm_id(row["reporting_document"])), "")
    if not blob or quote not in blob:
        return False
    if NOT_A_RESULT.search(quote) or CAPTION.match(quote):
        return False
    claimed = toks(row["reported_label"]) or toks(row["registry_measure"])
    if not (claimed & toks(quote)):
        return False
    concept = {t for t in claimed if len(t) > 3}
    low = blob.lower()
    return all(t in low for t in concept)


def squash(text):
    return " ".join((text or "").split()).strip().lower()


def registry_grounded(nct, unit, row):
    if row is None:
        return False
    if squash(row["registry_measure"]) != squash(unit["measure"]):
        return False
    return squash(row["registry_role"]) == squash(unit["role"])


def ratio(num, den):
    return (num / den) if den else 0.0


def expected_evidence_units(nct):
    key = KEY[nct]
    out = []
    for u in key["prespecified_units"]:
        if u["reported"]:
            out.append(("prespecified", u["uid"], u))
    for i, a in enumerate(key["additional_units"]):
        out.append(("additional", i, a))
    return out


ADDITIONAL_CLAIM = {}


def additional_assignment(nct):
    if nct in ADDITIONAL_CLAIM:
        return ADDITIONAL_CLAIM[nct]
    key = KEY[nct]
    rows = [r for r in BY_TRIAL.get(nct, []) if r["unit_type"].lower().startswith("addition")]
    taken = set()
    assign = {}
    for idx, unit in enumerate(key["additional_units"]):
        want = toks(unit["reported_label"])
        doc = unit["reporting_document"]
        for i, r in enumerate(rows):
            if i in taken:
                continue
            if norm_id(r["reporting_document"]) != doc:
                continue
            if jaccard(want, toks(r["reported_label"])) >= 0.5:
                taken.add(i)
                assign[idx] = r
                break
    ADDITIONAL_CLAIM[nct] = assign
    return assign


def row_for_evidence_unit(nct, kind, ident, unit):
    if kind == "prespecified":
        return MATCH.get((nct, ident))
    return additional_assignment(nct).get(ident)


def grounded_units(nct):
    found = []
    for kind, ident, unit in expected_evidence_units(nct):
        row = row_for_evidence_unit(nct, kind, ident, unit)
        if row is not None and authored(nct, row):
            found.append((kind, ident, unit, row))
    return found


def authorship_share(nct):
    units = expected_evidence_units(nct)
    return ratio(len(grounded_units(nct)), len(units))


def static_coverage(nct):
    key = KEY[nct]
    grounded_ids = {ident for kind, ident, _, _ in grounded_units(nct) if kind == "prespecified"}
    earned = 0
    for u in key["prespecified_units"]:
        row = MATCH.get((nct, u["uid"]))
        if row is None:
            continue
        if u["reported"]:
            if u["uid"] in grounded_ids:
                earned += 1
        elif registry_grounded(nct, u, row) and not row["reporting_document"].strip():
            earned += 1
    return ratio(earned, len(key["prespecified_units"])), []


def static_basis(nct):
    key = KEY[nct]
    row = BASIS_ROWS.get(nct)
    if not row:
        return 0.0, [nct + ": no prespecification_basis row"]
    fields = [
        str(row.get("registry_version_used", "")).strip() == str(key["prespecification_version"]),
        str(row.get("version_date", "")).strip() == key["prespecification_date"],
        str(row.get("prespecified_outcome_count", "")).strip() == str(len(key["prespecified_units"])),
    ]
    earned = sum(1 for f in fields if f) if grounded_units(nct) else 0
    return ratio(earned, len(fields)), []


def rh_result_quote_verbatim(nct):
    return authorship_share(nct), []


def rh_result_quote_numeric(nct):
    units = expected_evidence_units(nct)
    ok = sum(1 for _, _, _, row in grounded_units(nct) if NUMERIC.search(row["result_quote"]))
    return ratio(ok, len(units)), []


def rh_role_quote_verbatim(nct):
    units = expected_evidence_units(nct)
    ok = 0
    for _, _, _, row in grounded_units(nct):
        quote = row["role_evidence_quote"].strip()
        if len(quote.split()) < 2 or not (toks(quote) - FILLER):
            continue
        if " ".join(quote.split()) == " ".join(row["result_quote"].split()):
            continue
        blob = DOCS.get((nct, norm_id(row["reporting_document"])), "")
        if quote and blob and quote in blob:
            ok += 1
    return ratio(ok, len(units)), []


def rh_negative_rows_clean(nct):
    key = KEY[nct]
    if not grounded_units(nct):
        return 0.0, []
    expected = [u for u in key["prespecified_units"] if not u["reported"]]
    ok = 0
    for u in expected:
        row = MATCH.get((nct, u["uid"]))
        if row is None or says_yes(row["reported"]):
            continue
        if not registry_grounded(nct, u, row):
            continue
        if not row["reporting_document"].strip() and not row["result_quote"].strip():
            ok += 1
    return ratio(ok, len(expected)), []


def rh_additional_within_bound(nct):
    key = KEY[nct]
    found = grounded_units(nct)
    if not found:
        return 0.0, []
    submitted = sum(1 for r in BY_TRIAL.get(nct, []) if r["unit_type"].lower().startswith("addition"))
    allowed = len(key["additional_units"]) + 10
    if submitted == 0:
        return 0.0, []
    if submitted <= allowed:
        return 1.0, []
    return ratio(allowed, submitted), []


def rh_distinct_result_quotes(nct):
    units = expected_evidence_units(nct)
    seen = set()
    for _, _, _, row in grounded_units(nct):
        seen.add(" ".join(row["result_quote"].split()))
    return ratio(len(seen), len(units)), []


def po_basis_derived(nct):
    key = KEY[nct]
    row = BASIS_ROWS.get(nct)
    if row is None or not grounded_units(nct):
        return 0.0, []
    fields = [
        str(row.get("registry_version_used", "")).strip() == str(key["prespecification_version"]),
        str(row.get("version_date", "")).strip() == key["prespecification_date"],
        str(row.get("prespecified_outcome_count", "")).strip() == str(len(key["prespecified_units"])),
    ]
    return ratio(sum(1 for f in fields if f), len(fields)), []


def static_registry_fields(nct, uid):
    key = KEY[nct]
    unit = next(u for u in key["prespecified_units"] if u["uid"] == uid)
    row = MATCH.get((nct, uid))
    if row is None or not grounded_units(nct):
        return 0.0, []
    fields = [
        squash(row["registry_measure"]) == squash(unit["measure"]),
        squash(row["registry_role"]) == squash(unit["role"]),
        squash(row["registry_timeframe"]) == squash(unit["timeframe"]),
    ]
    return ratio(sum(1 for f in fields if f), len(fields)), []


def rh_row_shape_rules(nct):
    key = KEY[nct]
    rows = BY_TRIAL.get(nct, [])
    if not rows or not grounded_units(nct):
        return 0.0, []
    ok = 0
    for r in rows:
        if r["unit_type"].lower().startswith("addition"):
            clean = not any(r[c].strip() for c in
                            ("registry_measure", "registry_role", "registry_timeframe"))
        elif says_yes(r["reported"]):
            clean = bool(r["reporting_document"].strip()) and bool(r["reported_label"].strip())
        else:
            clean = not any(r[c].strip() for c in
                            ("reporting_document", "reported_label", "reported_instrument",
                             "reported_role", "role_evidence_quote", "result_quote"))
        if clean:
            ok += 1
    return ratio(ok, len(rows)), []


def po_reported(nct, uid):
    key = KEY[nct]
    unit = next(u for u in key["prespecified_units"] if u["uid"] == uid)
    row = MATCH.get((nct, uid))
    if row is None:
        return 0.0, []
    if says_yes(row["reported"]) != unit["reported"]:
        return 0.0, []
    earned = authored(nct, row) if unit["reported"] else registry_grounded(nct, unit, row)
    return (1.0 if earned else 0.0), []


def po_field(nct, uid, field):
    key = KEY[nct]
    unit = next(u for u in key["prespecified_units"] if u["uid"] == uid)
    row = MATCH.get((nct, uid))
    if row is None or not authored(nct, row):
        return 0.0, []
    if field == "document":
        return (1.0 if norm_id(row["reporting_document"]) == unit["reporting_document"] else 0.0), []
    if field == "role":
        quote = row["role_evidence_quote"].strip()
        blob = DOCS.get((nct, norm_id(row["reporting_document"])), "")
        content = toks(quote) - FILLER
        if len(quote.split()) < 2 or not content or not blob or quote not in blob:
            return 0.0, []
        if " ".join(quote.split()) == " ".join(row["result_quote"].split()):
            return 0.0, []
        return (1.0 if row["reported_role"].strip().lower() == unit["reported_role"].lower() else 0.0), []
    want = unit["reported_label"] if field == "label" else unit["reported_instrument"]
    got = row["reported_label"] if field == "label" else row["reported_instrument"]
    if not want:
        return (1.0 if not got.strip() else 0.0), []
    return (1.0 if jaccard(toks(want), toks(got)) >= 0.5 else 0.0), []


def po_additional(nct, idx):
    row = additional_assignment(nct).get(idx)
    if row is None or not authored(nct, row):
        return 0.0, []
    return 1.0, []


def check_static_nct02048007_coverage():
    return static_coverage("NCT02048007")

def check_static_nct02048007_basis():
    return static_basis("NCT02048007")

def check_reward_hacking_nct02048007_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02048007")

def check_reward_hacking_nct02048007_result_quote_numeric():
    return rh_result_quote_numeric("NCT02048007")

def check_reward_hacking_nct02048007_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02048007")

def check_reward_hacking_nct02048007_negative_rows_clean():
    return rh_negative_rows_clean("NCT02048007")

def check_reward_hacking_nct02048007_additional_within_bound():
    return rh_additional_within_bound("NCT02048007")

def check_reward_hacking_nct02048007_row_shape_rules():
    return rh_row_shape_rules("NCT02048007")

def check_reward_hacking_nct02048007_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02048007")

def check_po_nct02048007_basis_derived():
    return po_basis_derived("NCT02048007")

def check_static_nct02048007_pri1_registry_fields():
    return static_registry_fields("NCT02048007", "pri1")

def check_po_nct02048007_pri1_reported():
    return po_reported("NCT02048007", "pri1")

def check_po_nct02048007_pri1_document():
    return po_field("NCT02048007", "pri1", "document")

def check_po_nct02048007_pri1_label():
    return po_field("NCT02048007", "pri1", "label")

def check_po_nct02048007_pri1_instrument():
    return po_field("NCT02048007", "pri1", "instrument")

def check_po_nct02048007_pri1_role():
    return po_field("NCT02048007", "pri1", "role")

def check_static_nct02048007_pri2_registry_fields():
    return static_registry_fields("NCT02048007", "pri2")

def check_po_nct02048007_pri2_reported():
    return po_reported("NCT02048007", "pri2")

def check_po_nct02048007_pri2_document():
    return po_field("NCT02048007", "pri2", "document")

def check_po_nct02048007_pri2_label():
    return po_field("NCT02048007", "pri2", "label")

def check_po_nct02048007_pri2_instrument():
    return po_field("NCT02048007", "pri2", "instrument")

def check_po_nct02048007_pri2_role():
    return po_field("NCT02048007", "pri2", "role")

def check_static_nct02048007_pri5_registry_fields():
    return static_registry_fields("NCT02048007", "pri5")

def check_po_nct02048007_pri5_reported():
    return po_reported("NCT02048007", "pri5")

def check_static_nct02048007_pri6_registry_fields():
    return static_registry_fields("NCT02048007", "pri6")

def check_po_nct02048007_pri6_reported():
    return po_reported("NCT02048007", "pri6")

def check_po_nct02048007_pri6_document():
    return po_field("NCT02048007", "pri6", "document")

def check_po_nct02048007_pri6_label():
    return po_field("NCT02048007", "pri6", "label")

def check_po_nct02048007_pri6_instrument():
    return po_field("NCT02048007", "pri6", "instrument")

def check_po_nct02048007_pri6_role():
    return po_field("NCT02048007", "pri6", "role")

def check_static_nct02048007_pri7_registry_fields():
    return static_registry_fields("NCT02048007", "pri7")

def check_po_nct02048007_pri7_reported():
    return po_reported("NCT02048007", "pri7")

def check_po_nct02048007_pri7_document():
    return po_field("NCT02048007", "pri7", "document")

def check_po_nct02048007_pri7_label():
    return po_field("NCT02048007", "pri7", "label")

def check_po_nct02048007_pri7_role():
    return po_field("NCT02048007", "pri7", "role")

def check_static_nct02048007_sec1_registry_fields():
    return static_registry_fields("NCT02048007", "sec1")

def check_po_nct02048007_sec1_reported():
    return po_reported("NCT02048007", "sec1")

def check_static_nct02048007_sec2_registry_fields():
    return static_registry_fields("NCT02048007", "sec2")

def check_po_nct02048007_sec2_reported():
    return po_reported("NCT02048007", "sec2")

def check_po_nct02048007_sec2_document():
    return po_field("NCT02048007", "sec2", "document")

def check_po_nct02048007_sec2_label():
    return po_field("NCT02048007", "sec2", "label")

def check_po_nct02048007_sec2_instrument():
    return po_field("NCT02048007", "sec2", "instrument")

def check_po_nct02048007_sec2_role():
    return po_field("NCT02048007", "sec2", "role")

def check_static_nct02048007_sec3_registry_fields():
    return static_registry_fields("NCT02048007", "sec3")

def check_po_nct02048007_sec3_reported():
    return po_reported("NCT02048007", "sec3")

def check_po_nct02048007_sec3_document():
    return po_field("NCT02048007", "sec3", "document")

def check_po_nct02048007_sec3_label():
    return po_field("NCT02048007", "sec3", "label")

def check_po_nct02048007_sec3_instrument():
    return po_field("NCT02048007", "sec3", "instrument")

def check_po_nct02048007_sec3_role():
    return po_field("NCT02048007", "sec3", "role")

def check_static_nct02048007_sec5_registry_fields():
    return static_registry_fields("NCT02048007", "sec5")

def check_po_nct02048007_sec5_reported():
    return po_reported("NCT02048007", "sec5")

def check_static_nct02048007_sec6_registry_fields():
    return static_registry_fields("NCT02048007", "sec6")

def check_po_nct02048007_sec6_reported():
    return po_reported("NCT02048007", "sec6")

def check_static_nct02048007_sec10_registry_fields():
    return static_registry_fields("NCT02048007", "sec10")

def check_po_nct02048007_sec10_reported():
    return po_reported("NCT02048007", "sec10")

def check_static_nct02048007_sec14_registry_fields():
    return static_registry_fields("NCT02048007", "sec14")

def check_po_nct02048007_sec14_reported():
    return po_reported("NCT02048007", "sec14")

def check_static_nct02048007_sec15_registry_fields():
    return static_registry_fields("NCT02048007", "sec15")

def check_po_nct02048007_sec15_reported():
    return po_reported("NCT02048007", "sec15")

def check_static_nct02048007_sec16_registry_fields():
    return static_registry_fields("NCT02048007", "sec16")

def check_po_nct02048007_sec16_reported():
    return po_reported("NCT02048007", "sec16")

def check_static_nct02048007_sec17_registry_fields():
    return static_registry_fields("NCT02048007", "sec17")

def check_po_nct02048007_sec17_reported():
    return po_reported("NCT02048007", "sec17")

def check_static_nct02048007_sec20_registry_fields():
    return static_registry_fields("NCT02048007", "sec20")

def check_po_nct02048007_sec20_reported():
    return po_reported("NCT02048007", "sec20")

def check_static_nct02048007_sec21_registry_fields():
    return static_registry_fields("NCT02048007", "sec21")

def check_po_nct02048007_sec21_reported():
    return po_reported("NCT02048007", "sec21")

def check_static_nct02048007_sec22_registry_fields():
    return static_registry_fields("NCT02048007", "sec22")

def check_po_nct02048007_sec22_reported():
    return po_reported("NCT02048007", "sec22")

def check_static_nct02048007_sec23_registry_fields():
    return static_registry_fields("NCT02048007", "sec23")

def check_po_nct02048007_sec23_reported():
    return po_reported("NCT02048007", "sec23")

def check_static_nct02048007_sec24_registry_fields():
    return static_registry_fields("NCT02048007", "sec24")

def check_po_nct02048007_sec24_reported():
    return po_reported("NCT02048007", "sec24")

def check_static_nct02048007_sec25_registry_fields():
    return static_registry_fields("NCT02048007", "sec25")

def check_po_nct02048007_sec25_reported():
    return po_reported("NCT02048007", "sec25")

def check_static_nct02048007_sec27_registry_fields():
    return static_registry_fields("NCT02048007", "sec27")

def check_po_nct02048007_sec27_reported():
    return po_reported("NCT02048007", "sec27")

def check_static_nct02048007_sec28_registry_fields():
    return static_registry_fields("NCT02048007", "sec28")

def check_po_nct02048007_sec28_reported():
    return po_reported("NCT02048007", "sec28")

def check_static_nct02048007_sec29_registry_fields():
    return static_registry_fields("NCT02048007", "sec29")

def check_po_nct02048007_sec29_reported():
    return po_reported("NCT02048007", "sec29")

def check_po_nct02048007_add0_found():
    return po_additional("NCT02048007", 0)

def check_po_nct02048007_add1_found():
    return po_additional("NCT02048007", 1)

def check_po_nct02048007_add2_found():
    return po_additional("NCT02048007", 2)

def check_po_nct02048007_add3_found():
    return po_additional("NCT02048007", 3)

def check_po_nct02048007_add4_found():
    return po_additional("NCT02048007", 4)

def check_po_nct02048007_add5_found():
    return po_additional("NCT02048007", 5)

def check_po_nct02048007_add6_found():
    return po_additional("NCT02048007", 6)

def check_po_nct02048007_add7_found():
    return po_additional("NCT02048007", 7)

def check_po_nct02048007_add8_found():
    return po_additional("NCT02048007", 8)

def check_po_nct02048007_add9_found():
    return po_additional("NCT02048007", 9)

def check_po_nct02048007_add10_found():
    return po_additional("NCT02048007", 10)

def check_po_nct02048007_add11_found():
    return po_additional("NCT02048007", 11)

def check_po_nct02048007_add12_found():
    return po_additional("NCT02048007", 12)

def check_po_nct02048007_add13_found():
    return po_additional("NCT02048007", 13)

def check_po_nct02048007_add14_found():
    return po_additional("NCT02048007", 14)

def check_po_nct02048007_add15_found():
    return po_additional("NCT02048007", 15)

def check_po_nct02048007_add16_found():
    return po_additional("NCT02048007", 16)

def check_po_nct02048007_add17_found():
    return po_additional("NCT02048007", 17)

def check_po_nct02048007_add18_found():
    return po_additional("NCT02048007", 18)

def check_po_nct02048007_add19_found():
    return po_additional("NCT02048007", 19)

def check_po_nct02048007_add20_found():
    return po_additional("NCT02048007", 20)

def check_po_nct02048007_add21_found():
    return po_additional("NCT02048007", 21)

def check_po_nct02048007_add22_found():
    return po_additional("NCT02048007", 22)

def check_po_nct02048007_add23_found():
    return po_additional("NCT02048007", 23)

def check_po_nct02048007_add24_found():
    return po_additional("NCT02048007", 24)

def check_po_nct02048007_add25_found():
    return po_additional("NCT02048007", 25)

def check_po_nct02048007_add26_found():
    return po_additional("NCT02048007", 26)

def check_po_nct02048007_add27_found():
    return po_additional("NCT02048007", 27)

def check_po_nct02048007_add28_found():
    return po_additional("NCT02048007", 28)

def check_po_nct02048007_add29_found():
    return po_additional("NCT02048007", 29)

def check_po_nct02048007_add30_found():
    return po_additional("NCT02048007", 30)

def check_po_nct02048007_add31_found():
    return po_additional("NCT02048007", 31)

def check_po_nct02048007_add32_found():
    return po_additional("NCT02048007", 32)

def check_po_nct02048007_add33_found():
    return po_additional("NCT02048007", 33)

def check_po_nct02048007_add34_found():
    return po_additional("NCT02048007", 34)

def check_po_nct02048007_add35_found():
    return po_additional("NCT02048007", 35)

def check_po_nct02048007_add36_found():
    return po_additional("NCT02048007", 36)

def check_po_nct02048007_add37_found():
    return po_additional("NCT02048007", 37)

def check_po_nct02048007_add38_found():
    return po_additional("NCT02048007", 38)

def check_po_nct02048007_add39_found():
    return po_additional("NCT02048007", 39)

def check_po_nct02048007_add40_found():
    return po_additional("NCT02048007", 40)

def check_po_nct02048007_add41_found():
    return po_additional("NCT02048007", 41)

def check_po_nct02048007_add42_found():
    return po_additional("NCT02048007", 42)

def check_po_nct02048007_add43_found():
    return po_additional("NCT02048007", 43)

def check_po_nct02048007_add44_found():
    return po_additional("NCT02048007", 44)

def check_po_nct02048007_add45_found():
    return po_additional("NCT02048007", 45)

def check_po_nct02048007_add46_found():
    return po_additional("NCT02048007", 46)

def check_po_nct02048007_add47_found():
    return po_additional("NCT02048007", 47)

def check_po_nct02048007_add48_found():
    return po_additional("NCT02048007", 48)

def check_po_nct02048007_add49_found():
    return po_additional("NCT02048007", 49)

def check_po_nct02048007_add50_found():
    return po_additional("NCT02048007", 50)

def check_po_nct02048007_add51_found():
    return po_additional("NCT02048007", 51)

def check_po_nct02048007_add52_found():
    return po_additional("NCT02048007", 52)

def check_po_nct02048007_add53_found():
    return po_additional("NCT02048007", 53)

def check_po_nct02048007_add54_found():
    return po_additional("NCT02048007", 54)

def check_po_nct02048007_add55_found():
    return po_additional("NCT02048007", 55)

def check_po_nct02048007_add56_found():
    return po_additional("NCT02048007", 56)

def check_po_nct02048007_add57_found():
    return po_additional("NCT02048007", 57)

def check_po_nct02048007_add58_found():
    return po_additional("NCT02048007", 58)

def check_po_nct02048007_add59_found():
    return po_additional("NCT02048007", 59)

def check_po_nct02048007_add60_found():
    return po_additional("NCT02048007", 60)

def check_po_nct02048007_add61_found():
    return po_additional("NCT02048007", 61)

def check_po_nct02048007_add62_found():
    return po_additional("NCT02048007", 62)

def check_po_nct02048007_add63_found():
    return po_additional("NCT02048007", 63)

def check_po_nct02048007_add64_found():
    return po_additional("NCT02048007", 64)

def check_po_nct02048007_add65_found():
    return po_additional("NCT02048007", 65)

def check_po_nct02048007_add66_found():
    return po_additional("NCT02048007", 66)

def check_po_nct02048007_add67_found():
    return po_additional("NCT02048007", 67)

def check_po_nct02048007_add68_found():
    return po_additional("NCT02048007", 68)

def check_po_nct02048007_add69_found():
    return po_additional("NCT02048007", 69)

def check_po_nct02048007_add70_found():
    return po_additional("NCT02048007", 70)

def check_po_nct02048007_add71_found():
    return po_additional("NCT02048007", 71)

def check_po_nct02048007_add72_found():
    return po_additional("NCT02048007", 72)

def check_po_nct02048007_add73_found():
    return po_additional("NCT02048007", 73)

def check_po_nct02048007_add74_found():
    return po_additional("NCT02048007", 74)

def check_po_nct02048007_add75_found():
    return po_additional("NCT02048007", 75)

def check_po_nct02048007_add76_found():
    return po_additional("NCT02048007", 76)

def check_po_nct02048007_add77_found():
    return po_additional("NCT02048007", 77)

def check_po_nct02048007_add78_found():
    return po_additional("NCT02048007", 78)

def check_po_nct02048007_add79_found():
    return po_additional("NCT02048007", 79)

def check_po_nct02048007_add80_found():
    return po_additional("NCT02048007", 80)

def check_po_nct02048007_add81_found():
    return po_additional("NCT02048007", 81)

def check_po_nct02048007_add82_found():
    return po_additional("NCT02048007", 82)

def check_po_nct02048007_add83_found():
    return po_additional("NCT02048007", 83)

def check_po_nct02048007_add84_found():
    return po_additional("NCT02048007", 84)

def check_po_nct02048007_add85_found():
    return po_additional("NCT02048007", 85)

def check_po_nct02048007_add86_found():
    return po_additional("NCT02048007", 86)

def check_po_nct02048007_add87_found():
    return po_additional("NCT02048007", 87)

def check_po_nct02048007_add88_found():
    return po_additional("NCT02048007", 88)

def check_po_nct02048007_add89_found():
    return po_additional("NCT02048007", 89)

def check_po_nct02048007_add90_found():
    return po_additional("NCT02048007", 90)

def check_po_nct02048007_add91_found():
    return po_additional("NCT02048007", 91)

def check_po_nct02048007_add92_found():
    return po_additional("NCT02048007", 92)

def check_po_nct02048007_add93_found():
    return po_additional("NCT02048007", 93)

def check_po_nct02048007_add94_found():
    return po_additional("NCT02048007", 94)

def check_po_nct02048007_add95_found():
    return po_additional("NCT02048007", 95)

def check_po_nct02048007_add96_found():
    return po_additional("NCT02048007", 96)

def check_po_nct02048007_add97_found():
    return po_additional("NCT02048007", 97)

def check_po_nct02048007_add98_found():
    return po_additional("NCT02048007", 98)

def check_po_nct02048007_add99_found():
    return po_additional("NCT02048007", 99)

def check_po_nct02048007_add100_found():
    return po_additional("NCT02048007", 100)

def check_po_nct02048007_add101_found():
    return po_additional("NCT02048007", 101)

def check_po_nct02048007_add102_found():
    return po_additional("NCT02048007", 102)

def check_po_nct02048007_add103_found():
    return po_additional("NCT02048007", 103)

def check_po_nct02048007_add104_found():
    return po_additional("NCT02048007", 104)

def check_po_nct02048007_add105_found():
    return po_additional("NCT02048007", 105)

def check_po_nct02048007_add106_found():
    return po_additional("NCT02048007", 106)

def check_po_nct02048007_add107_found():
    return po_additional("NCT02048007", 107)

def check_po_nct02048007_add108_found():
    return po_additional("NCT02048007", 108)

def check_po_nct02048007_add109_found():
    return po_additional("NCT02048007", 109)

def check_po_nct02048007_add110_found():
    return po_additional("NCT02048007", 110)

def check_po_nct02048007_add111_found():
    return po_additional("NCT02048007", 111)

def check_po_nct02048007_add112_found():
    return po_additional("NCT02048007", 112)

def check_po_nct02048007_add113_found():
    return po_additional("NCT02048007", 113)

def check_po_nct02048007_add114_found():
    return po_additional("NCT02048007", 114)

def check_po_nct02048007_add115_found():
    return po_additional("NCT02048007", 115)

def check_po_nct02048007_add116_found():
    return po_additional("NCT02048007", 116)

def check_po_nct02048007_add117_found():
    return po_additional("NCT02048007", 117)

def check_po_nct02048007_add118_found():
    return po_additional("NCT02048007", 118)

def check_po_nct02048007_add119_found():
    return po_additional("NCT02048007", 119)

def check_po_nct02048007_add120_found():
    return po_additional("NCT02048007", 120)

def check_po_nct02048007_add121_found():
    return po_additional("NCT02048007", 121)

def check_po_nct02048007_add122_found():
    return po_additional("NCT02048007", 122)

def check_po_nct02048007_add123_found():
    return po_additional("NCT02048007", 123)

def check_po_nct02048007_add124_found():
    return po_additional("NCT02048007", 124)

def check_po_nct02048007_add125_found():
    return po_additional("NCT02048007", 125)

def check_po_nct02048007_add126_found():
    return po_additional("NCT02048007", 126)

def check_po_nct02048007_add127_found():
    return po_additional("NCT02048007", 127)

def check_po_nct02048007_add128_found():
    return po_additional("NCT02048007", 128)

def check_po_nct02048007_add129_found():
    return po_additional("NCT02048007", 129)

def check_po_nct02048007_add130_found():
    return po_additional("NCT02048007", 130)

def check_po_nct02048007_add131_found():
    return po_additional("NCT02048007", 131)

def check_po_nct02048007_add132_found():
    return po_additional("NCT02048007", 132)

def check_po_nct02048007_add133_found():
    return po_additional("NCT02048007", 133)

def check_po_nct02048007_add134_found():
    return po_additional("NCT02048007", 134)

def check_po_nct02048007_add135_found():
    return po_additional("NCT02048007", 135)

def check_po_nct02048007_add136_found():
    return po_additional("NCT02048007", 136)

def check_po_nct02048007_add137_found():
    return po_additional("NCT02048007", 137)

def check_po_nct02048007_add138_found():
    return po_additional("NCT02048007", 138)

def check_po_nct02048007_add139_found():
    return po_additional("NCT02048007", 139)

def check_po_nct02048007_add140_found():
    return po_additional("NCT02048007", 140)

def check_po_nct02048007_add141_found():
    return po_additional("NCT02048007", 141)

def check_po_nct02048007_add142_found():
    return po_additional("NCT02048007", 142)

def check_po_nct02048007_add143_found():
    return po_additional("NCT02048007", 143)

def check_po_nct02048007_add144_found():
    return po_additional("NCT02048007", 144)

def check_po_nct02048007_add145_found():
    return po_additional("NCT02048007", 145)

def check_po_nct02048007_add146_found():
    return po_additional("NCT02048007", 146)

def check_po_nct02048007_add147_found():
    return po_additional("NCT02048007", 147)

def check_po_nct02048007_add148_found():
    return po_additional("NCT02048007", 148)

def check_po_nct02048007_add149_found():
    return po_additional("NCT02048007", 149)

def check_po_nct02048007_add150_found():
    return po_additional("NCT02048007", 150)

def check_po_nct02048007_add151_found():
    return po_additional("NCT02048007", 151)

def check_po_nct02048007_add152_found():
    return po_additional("NCT02048007", 152)

def check_po_nct02048007_add153_found():
    return po_additional("NCT02048007", 153)

def check_po_nct02048007_add154_found():
    return po_additional("NCT02048007", 154)

def check_po_nct02048007_add155_found():
    return po_additional("NCT02048007", 155)

def check_po_nct02048007_add156_found():
    return po_additional("NCT02048007", 156)

def check_po_nct02048007_add157_found():
    return po_additional("NCT02048007", 157)

def check_po_nct02048007_add158_found():
    return po_additional("NCT02048007", 158)

def check_po_nct02048007_add159_found():
    return po_additional("NCT02048007", 159)

def check_po_nct02048007_add160_found():
    return po_additional("NCT02048007", 160)

def check_po_nct02048007_add161_found():
    return po_additional("NCT02048007", 161)

def check_po_nct02048007_add162_found():
    return po_additional("NCT02048007", 162)

def check_po_nct02048007_add163_found():
    return po_additional("NCT02048007", 163)

def check_po_nct02048007_add164_found():
    return po_additional("NCT02048007", 164)

def check_po_nct02048007_add165_found():
    return po_additional("NCT02048007", 165)

def check_static_nct02391337_coverage():
    return static_coverage("NCT02391337")

def check_static_nct02391337_basis():
    return static_basis("NCT02391337")

def check_reward_hacking_nct02391337_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02391337")

def check_reward_hacking_nct02391337_result_quote_numeric():
    return rh_result_quote_numeric("NCT02391337")

def check_reward_hacking_nct02391337_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02391337")

def check_reward_hacking_nct02391337_negative_rows_clean():
    return rh_negative_rows_clean("NCT02391337")

def check_reward_hacking_nct02391337_additional_within_bound():
    return rh_additional_within_bound("NCT02391337")

def check_reward_hacking_nct02391337_row_shape_rules():
    return rh_row_shape_rules("NCT02391337")

def check_reward_hacking_nct02391337_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02391337")

def check_po_nct02391337_basis_derived():
    return po_basis_derived("NCT02391337")

def check_static_nct02391337_sec1_registry_fields():
    return static_registry_fields("NCT02391337", "sec1")

def check_po_nct02391337_sec1_reported():
    return po_reported("NCT02391337", "sec1")

def check_static_nct02391337_sec2_registry_fields():
    return static_registry_fields("NCT02391337", "sec2")

def check_po_nct02391337_sec2_reported():
    return po_reported("NCT02391337", "sec2")

def check_static_nct02391337_sec4_registry_fields():
    return static_registry_fields("NCT02391337", "sec4")

def check_po_nct02391337_sec4_reported():
    return po_reported("NCT02391337", "sec4")

def check_static_nct02391337_sec8_registry_fields():
    return static_registry_fields("NCT02391337", "sec8")

def check_po_nct02391337_sec8_reported():
    return po_reported("NCT02391337", "sec8")

def check_po_nct02391337_sec8_document():
    return po_field("NCT02391337", "sec8", "document")

def check_po_nct02391337_sec8_label():
    return po_field("NCT02391337", "sec8", "label")

def check_po_nct02391337_sec8_instrument():
    return po_field("NCT02391337", "sec8", "instrument")

def check_po_nct02391337_sec8_role():
    return po_field("NCT02391337", "sec8", "role")

def check_static_nct02391337_oth2_registry_fields():
    return static_registry_fields("NCT02391337", "oth2")

def check_po_nct02391337_oth2_reported():
    return po_reported("NCT02391337", "oth2")

def check_static_nct02391337_oth3_registry_fields():
    return static_registry_fields("NCT02391337", "oth3")

def check_po_nct02391337_oth3_reported():
    return po_reported("NCT02391337", "oth3")

def check_po_nct02391337_oth3_document():
    return po_field("NCT02391337", "oth3", "document")

def check_po_nct02391337_oth3_label():
    return po_field("NCT02391337", "oth3", "label")

def check_po_nct02391337_oth3_role():
    return po_field("NCT02391337", "oth3", "role")

def check_static_nct02391337_oth4_registry_fields():
    return static_registry_fields("NCT02391337", "oth4")

def check_po_nct02391337_oth4_reported():
    return po_reported("NCT02391337", "oth4")

def check_static_nct02391337_oth5_registry_fields():
    return static_registry_fields("NCT02391337", "oth5")

def check_po_nct02391337_oth5_reported():
    return po_reported("NCT02391337", "oth5")

def check_static_nct02391337_oth6_registry_fields():
    return static_registry_fields("NCT02391337", "oth6")

def check_po_nct02391337_oth6_reported():
    return po_reported("NCT02391337", "oth6")

def check_static_nct02391337_oth7_registry_fields():
    return static_registry_fields("NCT02391337", "oth7")

def check_po_nct02391337_oth7_reported():
    return po_reported("NCT02391337", "oth7")

def check_static_nct02391337_oth8_registry_fields():
    return static_registry_fields("NCT02391337", "oth8")

def check_po_nct02391337_oth8_reported():
    return po_reported("NCT02391337", "oth8")

def check_static_nct02391337_oth9_registry_fields():
    return static_registry_fields("NCT02391337", "oth9")

def check_po_nct02391337_oth9_reported():
    return po_reported("NCT02391337", "oth9")

def check_static_nct02391337_oth10_registry_fields():
    return static_registry_fields("NCT02391337", "oth10")

def check_po_nct02391337_oth10_reported():
    return po_reported("NCT02391337", "oth10")

def check_static_nct02391337_oth11_registry_fields():
    return static_registry_fields("NCT02391337", "oth11")

def check_po_nct02391337_oth11_reported():
    return po_reported("NCT02391337", "oth11")

def check_po_nct02391337_add0_found():
    return po_additional("NCT02391337", 0)

def check_po_nct02391337_add1_found():
    return po_additional("NCT02391337", 1)

def check_po_nct02391337_add2_found():
    return po_additional("NCT02391337", 2)

def check_po_nct02391337_add3_found():
    return po_additional("NCT02391337", 3)

def check_po_nct02391337_add4_found():
    return po_additional("NCT02391337", 4)

def check_po_nct02391337_add5_found():
    return po_additional("NCT02391337", 5)

def check_po_nct02391337_add6_found():
    return po_additional("NCT02391337", 6)

def check_po_nct02391337_add7_found():
    return po_additional("NCT02391337", 7)

def check_po_nct02391337_add8_found():
    return po_additional("NCT02391337", 8)

def check_po_nct02391337_add9_found():
    return po_additional("NCT02391337", 9)

def check_po_nct02391337_add10_found():
    return po_additional("NCT02391337", 10)

def check_po_nct02391337_add11_found():
    return po_additional("NCT02391337", 11)

def check_po_nct02391337_add12_found():
    return po_additional("NCT02391337", 12)

def check_po_nct02391337_add13_found():
    return po_additional("NCT02391337", 13)

def check_po_nct02391337_add14_found():
    return po_additional("NCT02391337", 14)

def check_po_nct02391337_add15_found():
    return po_additional("NCT02391337", 15)

def check_po_nct02391337_add16_found():
    return po_additional("NCT02391337", 16)

def check_po_nct02391337_add17_found():
    return po_additional("NCT02391337", 17)

def check_po_nct02391337_add18_found():
    return po_additional("NCT02391337", 18)

def check_po_nct02391337_add19_found():
    return po_additional("NCT02391337", 19)

def check_po_nct02391337_add20_found():
    return po_additional("NCT02391337", 20)

def check_po_nct02391337_add21_found():
    return po_additional("NCT02391337", 21)

def check_po_nct02391337_add22_found():
    return po_additional("NCT02391337", 22)

def check_po_nct02391337_add23_found():
    return po_additional("NCT02391337", 23)

def check_po_nct02391337_add24_found():
    return po_additional("NCT02391337", 24)

def check_po_nct02391337_add25_found():
    return po_additional("NCT02391337", 25)

def check_po_nct02391337_add26_found():
    return po_additional("NCT02391337", 26)

def check_po_nct02391337_add27_found():
    return po_additional("NCT02391337", 27)

def check_po_nct02391337_add28_found():
    return po_additional("NCT02391337", 28)

def check_po_nct02391337_add29_found():
    return po_additional("NCT02391337", 29)

def check_po_nct02391337_add30_found():
    return po_additional("NCT02391337", 30)

def check_po_nct02391337_add31_found():
    return po_additional("NCT02391337", 31)

def check_po_nct02391337_add32_found():
    return po_additional("NCT02391337", 32)

def check_po_nct02391337_add33_found():
    return po_additional("NCT02391337", 33)

def check_po_nct02391337_add34_found():
    return po_additional("NCT02391337", 34)

def check_po_nct02391337_add35_found():
    return po_additional("NCT02391337", 35)

def check_po_nct02391337_add36_found():
    return po_additional("NCT02391337", 36)

def check_po_nct02391337_add37_found():
    return po_additional("NCT02391337", 37)

def check_po_nct02391337_add38_found():
    return po_additional("NCT02391337", 38)

def check_po_nct02391337_add39_found():
    return po_additional("NCT02391337", 39)

def check_po_nct02391337_add40_found():
    return po_additional("NCT02391337", 40)

def check_po_nct02391337_add41_found():
    return po_additional("NCT02391337", 41)

def check_po_nct02391337_add42_found():
    return po_additional("NCT02391337", 42)

def check_po_nct02391337_add43_found():
    return po_additional("NCT02391337", 43)

def check_po_nct02391337_add44_found():
    return po_additional("NCT02391337", 44)

def check_po_nct02391337_add45_found():
    return po_additional("NCT02391337", 45)

def check_po_nct02391337_add46_found():
    return po_additional("NCT02391337", 46)

def check_po_nct02391337_add47_found():
    return po_additional("NCT02391337", 47)

def check_po_nct02391337_add48_found():
    return po_additional("NCT02391337", 48)

def check_po_nct02391337_add49_found():
    return po_additional("NCT02391337", 49)

def check_po_nct02391337_add50_found():
    return po_additional("NCT02391337", 50)

def check_po_nct02391337_add51_found():
    return po_additional("NCT02391337", 51)

def check_po_nct02391337_add52_found():
    return po_additional("NCT02391337", 52)

def check_po_nct02391337_add53_found():
    return po_additional("NCT02391337", 53)

def check_po_nct02391337_add54_found():
    return po_additional("NCT02391337", 54)

def check_po_nct02391337_add55_found():
    return po_additional("NCT02391337", 55)

def check_po_nct02391337_add56_found():
    return po_additional("NCT02391337", 56)

def check_po_nct02391337_add57_found():
    return po_additional("NCT02391337", 57)

def check_po_nct02391337_add58_found():
    return po_additional("NCT02391337", 58)

def check_po_nct02391337_add59_found():
    return po_additional("NCT02391337", 59)

def check_po_nct02391337_add60_found():
    return po_additional("NCT02391337", 60)

def check_po_nct02391337_add61_found():
    return po_additional("NCT02391337", 61)

def check_po_nct02391337_add62_found():
    return po_additional("NCT02391337", 62)

def check_po_nct02391337_add63_found():
    return po_additional("NCT02391337", 63)

def check_po_nct02391337_add64_found():
    return po_additional("NCT02391337", 64)

def check_po_nct02391337_add65_found():
    return po_additional("NCT02391337", 65)

def check_po_nct02391337_add66_found():
    return po_additional("NCT02391337", 66)

def check_po_nct02391337_add67_found():
    return po_additional("NCT02391337", 67)

def check_po_nct02391337_add68_found():
    return po_additional("NCT02391337", 68)

def check_po_nct02391337_add69_found():
    return po_additional("NCT02391337", 69)

def check_po_nct02391337_add70_found():
    return po_additional("NCT02391337", 70)

def check_po_nct02391337_add71_found():
    return po_additional("NCT02391337", 71)

def check_po_nct02391337_add72_found():
    return po_additional("NCT02391337", 72)

def check_po_nct02391337_add73_found():
    return po_additional("NCT02391337", 73)

def check_po_nct02391337_add74_found():
    return po_additional("NCT02391337", 74)

def check_po_nct02391337_add75_found():
    return po_additional("NCT02391337", 75)

def check_po_nct02391337_add76_found():
    return po_additional("NCT02391337", 76)

def check_po_nct02391337_add77_found():
    return po_additional("NCT02391337", 77)

def check_po_nct02391337_add78_found():
    return po_additional("NCT02391337", 78)

def check_po_nct02391337_add79_found():
    return po_additional("NCT02391337", 79)

def check_po_nct02391337_add80_found():
    return po_additional("NCT02391337", 80)

def check_po_nct02391337_add81_found():
    return po_additional("NCT02391337", 81)

def check_po_nct02391337_add82_found():
    return po_additional("NCT02391337", 82)

def check_po_nct02391337_add83_found():
    return po_additional("NCT02391337", 83)

def check_po_nct02391337_add84_found():
    return po_additional("NCT02391337", 84)

def check_po_nct02391337_add85_found():
    return po_additional("NCT02391337", 85)

def check_po_nct02391337_add86_found():
    return po_additional("NCT02391337", 86)

def check_po_nct02391337_add87_found():
    return po_additional("NCT02391337", 87)

def check_po_nct02391337_add88_found():
    return po_additional("NCT02391337", 88)

def check_po_nct02391337_add89_found():
    return po_additional("NCT02391337", 89)

def check_po_nct02391337_add90_found():
    return po_additional("NCT02391337", 90)

def check_po_nct02391337_add91_found():
    return po_additional("NCT02391337", 91)

def check_po_nct02391337_add92_found():
    return po_additional("NCT02391337", 92)

def check_static_nct02409680_coverage():
    return static_coverage("NCT02409680")

def check_static_nct02409680_basis():
    return static_basis("NCT02409680")

def check_reward_hacking_nct02409680_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02409680")

def check_reward_hacking_nct02409680_result_quote_numeric():
    return rh_result_quote_numeric("NCT02409680")

def check_reward_hacking_nct02409680_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02409680")

def check_reward_hacking_nct02409680_negative_rows_clean():
    return rh_negative_rows_clean("NCT02409680")

def check_reward_hacking_nct02409680_additional_within_bound():
    return rh_additional_within_bound("NCT02409680")

def check_reward_hacking_nct02409680_row_shape_rules():
    return rh_row_shape_rules("NCT02409680")

def check_reward_hacking_nct02409680_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02409680")

def check_po_nct02409680_basis_derived():
    return po_basis_derived("NCT02409680")

def check_static_nct02409680_pri1_registry_fields():
    return static_registry_fields("NCT02409680", "pri1")

def check_po_nct02409680_pri1_reported():
    return po_reported("NCT02409680", "pri1")

def check_po_nct02409680_pri1_document():
    return po_field("NCT02409680", "pri1", "document")

def check_po_nct02409680_pri1_label():
    return po_field("NCT02409680", "pri1", "label")

def check_po_nct02409680_pri1_instrument():
    return po_field("NCT02409680", "pri1", "instrument")

def check_po_nct02409680_pri1_role():
    return po_field("NCT02409680", "pri1", "role")

def check_static_nct02409680_sec2_registry_fields():
    return static_registry_fields("NCT02409680", "sec2")

def check_po_nct02409680_sec2_reported():
    return po_reported("NCT02409680", "sec2")

def check_po_nct02409680_sec2_document():
    return po_field("NCT02409680", "sec2", "document")

def check_po_nct02409680_sec2_label():
    return po_field("NCT02409680", "sec2", "label")

def check_po_nct02409680_sec2_instrument():
    return po_field("NCT02409680", "sec2", "instrument")

def check_po_nct02409680_sec2_role():
    return po_field("NCT02409680", "sec2", "role")

def check_static_nct02409680_sec3_registry_fields():
    return static_registry_fields("NCT02409680", "sec3")

def check_po_nct02409680_sec3_reported():
    return po_reported("NCT02409680", "sec3")

def check_po_nct02409680_sec3_document():
    return po_field("NCT02409680", "sec3", "document")

def check_po_nct02409680_sec3_label():
    return po_field("NCT02409680", "sec3", "label")

def check_po_nct02409680_sec3_role():
    return po_field("NCT02409680", "sec3", "role")

def check_static_nct02409680_oth12_registry_fields():
    return static_registry_fields("NCT02409680", "oth12")

def check_po_nct02409680_oth12_reported():
    return po_reported("NCT02409680", "oth12")

def check_po_nct02409680_add0_found():
    return po_additional("NCT02409680", 0)

def check_po_nct02409680_add1_found():
    return po_additional("NCT02409680", 1)

def check_po_nct02409680_add2_found():
    return po_additional("NCT02409680", 2)

def check_po_nct02409680_add3_found():
    return po_additional("NCT02409680", 3)

def check_po_nct02409680_add4_found():
    return po_additional("NCT02409680", 4)

def check_po_nct02409680_add5_found():
    return po_additional("NCT02409680", 5)

def check_po_nct02409680_add6_found():
    return po_additional("NCT02409680", 6)

def check_po_nct02409680_add7_found():
    return po_additional("NCT02409680", 7)

def check_po_nct02409680_add8_found():
    return po_additional("NCT02409680", 8)

def check_po_nct02409680_add9_found():
    return po_additional("NCT02409680", 9)

def check_po_nct02409680_add10_found():
    return po_additional("NCT02409680", 10)

def check_po_nct02409680_add11_found():
    return po_additional("NCT02409680", 11)

def check_po_nct02409680_add12_found():
    return po_additional("NCT02409680", 12)

def check_po_nct02409680_add13_found():
    return po_additional("NCT02409680", 13)

def check_po_nct02409680_add14_found():
    return po_additional("NCT02409680", 14)

def check_po_nct02409680_add15_found():
    return po_additional("NCT02409680", 15)

def check_po_nct02409680_add16_found():
    return po_additional("NCT02409680", 16)

def check_po_nct02409680_add17_found():
    return po_additional("NCT02409680", 17)

def check_po_nct02409680_add18_found():
    return po_additional("NCT02409680", 18)

def check_po_nct02409680_add19_found():
    return po_additional("NCT02409680", 19)

def check_po_nct02409680_add20_found():
    return po_additional("NCT02409680", 20)

def check_po_nct02409680_add21_found():
    return po_additional("NCT02409680", 21)

def check_po_nct02409680_add22_found():
    return po_additional("NCT02409680", 22)

def check_po_nct02409680_add23_found():
    return po_additional("NCT02409680", 23)

def check_po_nct02409680_add24_found():
    return po_additional("NCT02409680", 24)

def check_po_nct02409680_add25_found():
    return po_additional("NCT02409680", 25)

def check_po_nct02409680_add26_found():
    return po_additional("NCT02409680", 26)

def check_po_nct02409680_add27_found():
    return po_additional("NCT02409680", 27)

def check_po_nct02409680_add28_found():
    return po_additional("NCT02409680", 28)

def check_po_nct02409680_add29_found():
    return po_additional("NCT02409680", 29)

def check_po_nct02409680_add30_found():
    return po_additional("NCT02409680", 30)

def check_po_nct02409680_add31_found():
    return po_additional("NCT02409680", 31)

def check_po_nct02409680_add32_found():
    return po_additional("NCT02409680", 32)

def check_po_nct02409680_add33_found():
    return po_additional("NCT02409680", 33)

def check_po_nct02409680_add34_found():
    return po_additional("NCT02409680", 34)

def check_po_nct02409680_add35_found():
    return po_additional("NCT02409680", 35)

def check_po_nct02409680_add36_found():
    return po_additional("NCT02409680", 36)

def check_po_nct02409680_add37_found():
    return po_additional("NCT02409680", 37)

def check_po_nct02409680_add38_found():
    return po_additional("NCT02409680", 38)

def check_po_nct02409680_add39_found():
    return po_additional("NCT02409680", 39)

def check_po_nct02409680_add40_found():
    return po_additional("NCT02409680", 40)

def check_po_nct02409680_add41_found():
    return po_additional("NCT02409680", 41)

def check_po_nct02409680_add42_found():
    return po_additional("NCT02409680", 42)

def check_po_nct02409680_add43_found():
    return po_additional("NCT02409680", 43)

def check_po_nct02409680_add44_found():
    return po_additional("NCT02409680", 44)

def check_po_nct02409680_add45_found():
    return po_additional("NCT02409680", 45)

def check_po_nct02409680_add46_found():
    return po_additional("NCT02409680", 46)

def check_po_nct02409680_add47_found():
    return po_additional("NCT02409680", 47)

def check_po_nct02409680_add48_found():
    return po_additional("NCT02409680", 48)

def check_po_nct02409680_add49_found():
    return po_additional("NCT02409680", 49)

def check_po_nct02409680_add50_found():
    return po_additional("NCT02409680", 50)

def check_po_nct02409680_add51_found():
    return po_additional("NCT02409680", 51)

def check_po_nct02409680_add52_found():
    return po_additional("NCT02409680", 52)

def check_po_nct02409680_add53_found():
    return po_additional("NCT02409680", 53)

def check_po_nct02409680_add54_found():
    return po_additional("NCT02409680", 54)

def check_po_nct02409680_add55_found():
    return po_additional("NCT02409680", 55)

def check_po_nct02409680_add56_found():
    return po_additional("NCT02409680", 56)

def check_po_nct02409680_add57_found():
    return po_additional("NCT02409680", 57)

def check_po_nct02409680_add58_found():
    return po_additional("NCT02409680", 58)

def check_static_nct02429180_coverage():
    return static_coverage("NCT02429180")

def check_static_nct02429180_basis():
    return static_basis("NCT02429180")

def check_reward_hacking_nct02429180_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02429180")

def check_reward_hacking_nct02429180_result_quote_numeric():
    return rh_result_quote_numeric("NCT02429180")

def check_reward_hacking_nct02429180_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02429180")

def check_reward_hacking_nct02429180_negative_rows_clean():
    return rh_negative_rows_clean("NCT02429180")

def check_reward_hacking_nct02429180_additional_within_bound():
    return rh_additional_within_bound("NCT02429180")

def check_reward_hacking_nct02429180_row_shape_rules():
    return rh_row_shape_rules("NCT02429180")

def check_reward_hacking_nct02429180_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02429180")

def check_po_nct02429180_basis_derived():
    return po_basis_derived("NCT02429180")

def check_static_nct02429180_pri1_registry_fields():
    return static_registry_fields("NCT02429180", "pri1")

def check_po_nct02429180_pri1_reported():
    return po_reported("NCT02429180", "pri1")

def check_po_nct02429180_pri1_document():
    return po_field("NCT02429180", "pri1", "document")

def check_po_nct02429180_pri1_label():
    return po_field("NCT02429180", "pri1", "label")

def check_po_nct02429180_pri1_instrument():
    return po_field("NCT02429180", "pri1", "instrument")

def check_po_nct02429180_pri1_role():
    return po_field("NCT02429180", "pri1", "role")

def check_static_nct02429180_pri2_registry_fields():
    return static_registry_fields("NCT02429180", "pri2")

def check_po_nct02429180_pri2_reported():
    return po_reported("NCT02429180", "pri2")

def check_po_nct02429180_pri2_document():
    return po_field("NCT02429180", "pri2", "document")

def check_po_nct02429180_pri2_label():
    return po_field("NCT02429180", "pri2", "label")

def check_po_nct02429180_pri2_instrument():
    return po_field("NCT02429180", "pri2", "instrument")

def check_po_nct02429180_pri2_role():
    return po_field("NCT02429180", "pri2", "role")

def check_static_nct02429180_pri3_registry_fields():
    return static_registry_fields("NCT02429180", "pri3")

def check_po_nct02429180_pri3_reported():
    return po_reported("NCT02429180", "pri3")

def check_po_nct02429180_pri3_document():
    return po_field("NCT02429180", "pri3", "document")

def check_po_nct02429180_pri3_label():
    return po_field("NCT02429180", "pri3", "label")

def check_po_nct02429180_pri3_instrument():
    return po_field("NCT02429180", "pri3", "instrument")

def check_po_nct02429180_pri3_role():
    return po_field("NCT02429180", "pri3", "role")

def check_static_nct02429180_pri4_registry_fields():
    return static_registry_fields("NCT02429180", "pri4")

def check_po_nct02429180_pri4_reported():
    return po_reported("NCT02429180", "pri4")

def check_po_nct02429180_pri4_document():
    return po_field("NCT02429180", "pri4", "document")

def check_po_nct02429180_pri4_label():
    return po_field("NCT02429180", "pri4", "label")

def check_po_nct02429180_pri4_instrument():
    return po_field("NCT02429180", "pri4", "instrument")

def check_po_nct02429180_pri4_role():
    return po_field("NCT02429180", "pri4", "role")

def check_static_nct02429180_pri5_registry_fields():
    return static_registry_fields("NCT02429180", "pri5")

def check_po_nct02429180_pri5_reported():
    return po_reported("NCT02429180", "pri5")

def check_po_nct02429180_pri5_document():
    return po_field("NCT02429180", "pri5", "document")

def check_po_nct02429180_pri5_label():
    return po_field("NCT02429180", "pri5", "label")

def check_po_nct02429180_pri5_instrument():
    return po_field("NCT02429180", "pri5", "instrument")

def check_po_nct02429180_pri5_role():
    return po_field("NCT02429180", "pri5", "role")

def check_static_nct02429180_sec1_registry_fields():
    return static_registry_fields("NCT02429180", "sec1")

def check_po_nct02429180_sec1_reported():
    return po_reported("NCT02429180", "sec1")

def check_po_nct02429180_sec1_document():
    return po_field("NCT02429180", "sec1", "document")

def check_po_nct02429180_sec1_label():
    return po_field("NCT02429180", "sec1", "label")

def check_po_nct02429180_sec1_instrument():
    return po_field("NCT02429180", "sec1", "instrument")

def check_po_nct02429180_sec1_role():
    return po_field("NCT02429180", "sec1", "role")

def check_static_nct02429180_sec2_registry_fields():
    return static_registry_fields("NCT02429180", "sec2")

def check_po_nct02429180_sec2_reported():
    return po_reported("NCT02429180", "sec2")

def check_po_nct02429180_sec2_document():
    return po_field("NCT02429180", "sec2", "document")

def check_po_nct02429180_sec2_label():
    return po_field("NCT02429180", "sec2", "label")

def check_po_nct02429180_sec2_instrument():
    return po_field("NCT02429180", "sec2", "instrument")

def check_po_nct02429180_sec2_role():
    return po_field("NCT02429180", "sec2", "role")

def check_static_nct02429180_sec3_registry_fields():
    return static_registry_fields("NCT02429180", "sec3")

def check_po_nct02429180_sec3_reported():
    return po_reported("NCT02429180", "sec3")

def check_po_nct02429180_sec3_document():
    return po_field("NCT02429180", "sec3", "document")

def check_po_nct02429180_sec3_label():
    return po_field("NCT02429180", "sec3", "label")

def check_po_nct02429180_sec3_instrument():
    return po_field("NCT02429180", "sec3", "instrument")

def check_po_nct02429180_sec3_role():
    return po_field("NCT02429180", "sec3", "role")

def check_static_nct02429180_sec4_registry_fields():
    return static_registry_fields("NCT02429180", "sec4")

def check_po_nct02429180_sec4_reported():
    return po_reported("NCT02429180", "sec4")

def check_po_nct02429180_sec4_document():
    return po_field("NCT02429180", "sec4", "document")

def check_po_nct02429180_sec4_label():
    return po_field("NCT02429180", "sec4", "label")

def check_po_nct02429180_sec4_instrument():
    return po_field("NCT02429180", "sec4", "instrument")

def check_po_nct02429180_sec4_role():
    return po_field("NCT02429180", "sec4", "role")

def check_static_nct02429180_sec5_registry_fields():
    return static_registry_fields("NCT02429180", "sec5")

def check_po_nct02429180_sec5_reported():
    return po_reported("NCT02429180", "sec5")

def check_po_nct02429180_sec5_document():
    return po_field("NCT02429180", "sec5", "document")

def check_po_nct02429180_sec5_label():
    return po_field("NCT02429180", "sec5", "label")

def check_po_nct02429180_sec5_instrument():
    return po_field("NCT02429180", "sec5", "instrument")

def check_po_nct02429180_sec5_role():
    return po_field("NCT02429180", "sec5", "role")

def check_static_nct02429180_sec6_registry_fields():
    return static_registry_fields("NCT02429180", "sec6")

def check_po_nct02429180_sec6_reported():
    return po_reported("NCT02429180", "sec6")

def check_po_nct02429180_sec6_document():
    return po_field("NCT02429180", "sec6", "document")

def check_po_nct02429180_sec6_label():
    return po_field("NCT02429180", "sec6", "label")

def check_po_nct02429180_sec6_instrument():
    return po_field("NCT02429180", "sec6", "instrument")

def check_po_nct02429180_sec6_role():
    return po_field("NCT02429180", "sec6", "role")

def check_static_nct02429180_sec8_registry_fields():
    return static_registry_fields("NCT02429180", "sec8")

def check_po_nct02429180_sec8_reported():
    return po_reported("NCT02429180", "sec8")

def check_po_nct02429180_sec8_document():
    return po_field("NCT02429180", "sec8", "document")

def check_po_nct02429180_sec8_label():
    return po_field("NCT02429180", "sec8", "label")

def check_po_nct02429180_sec8_instrument():
    return po_field("NCT02429180", "sec8", "instrument")

def check_po_nct02429180_sec8_role():
    return po_field("NCT02429180", "sec8", "role")

def check_static_nct02429180_sec9_registry_fields():
    return static_registry_fields("NCT02429180", "sec9")

def check_po_nct02429180_sec9_reported():
    return po_reported("NCT02429180", "sec9")

def check_po_nct02429180_sec9_document():
    return po_field("NCT02429180", "sec9", "document")

def check_po_nct02429180_sec9_label():
    return po_field("NCT02429180", "sec9", "label")

def check_po_nct02429180_sec9_instrument():
    return po_field("NCT02429180", "sec9", "instrument")

def check_po_nct02429180_sec9_role():
    return po_field("NCT02429180", "sec9", "role")

def check_static_nct02429180_sec10_registry_fields():
    return static_registry_fields("NCT02429180", "sec10")

def check_po_nct02429180_sec10_reported():
    return po_reported("NCT02429180", "sec10")

def check_po_nct02429180_sec10_document():
    return po_field("NCT02429180", "sec10", "document")

def check_po_nct02429180_sec10_label():
    return po_field("NCT02429180", "sec10", "label")

def check_po_nct02429180_sec10_role():
    return po_field("NCT02429180", "sec10", "role")

def check_static_nct02429180_oth1_registry_fields():
    return static_registry_fields("NCT02429180", "oth1")

def check_po_nct02429180_oth1_reported():
    return po_reported("NCT02429180", "oth1")

def check_po_nct02429180_oth1_document():
    return po_field("NCT02429180", "oth1", "document")

def check_po_nct02429180_oth1_label():
    return po_field("NCT02429180", "oth1", "label")

def check_po_nct02429180_oth1_instrument():
    return po_field("NCT02429180", "oth1", "instrument")

def check_po_nct02429180_oth1_role():
    return po_field("NCT02429180", "oth1", "role")

def check_po_nct02429180_add0_found():
    return po_additional("NCT02429180", 0)

def check_po_nct02429180_add1_found():
    return po_additional("NCT02429180", 1)

def check_po_nct02429180_add2_found():
    return po_additional("NCT02429180", 2)

def check_po_nct02429180_add3_found():
    return po_additional("NCT02429180", 3)

def check_po_nct02429180_add4_found():
    return po_additional("NCT02429180", 4)

def check_po_nct02429180_add5_found():
    return po_additional("NCT02429180", 5)

def check_po_nct02429180_add6_found():
    return po_additional("NCT02429180", 6)

def check_po_nct02429180_add7_found():
    return po_additional("NCT02429180", 7)

def check_po_nct02429180_add8_found():
    return po_additional("NCT02429180", 8)

def check_po_nct02429180_add9_found():
    return po_additional("NCT02429180", 9)

def check_po_nct02429180_add10_found():
    return po_additional("NCT02429180", 10)

def check_po_nct02429180_add11_found():
    return po_additional("NCT02429180", 11)

def check_po_nct02429180_add12_found():
    return po_additional("NCT02429180", 12)

def check_po_nct02429180_add13_found():
    return po_additional("NCT02429180", 13)

def check_po_nct02429180_add14_found():
    return po_additional("NCT02429180", 14)

def check_po_nct02429180_add15_found():
    return po_additional("NCT02429180", 15)

def check_po_nct02429180_add16_found():
    return po_additional("NCT02429180", 16)

def check_po_nct02429180_add17_found():
    return po_additional("NCT02429180", 17)

def check_po_nct02429180_add18_found():
    return po_additional("NCT02429180", 18)

def check_po_nct02429180_add19_found():
    return po_additional("NCT02429180", 19)

def check_po_nct02429180_add20_found():
    return po_additional("NCT02429180", 20)

def check_po_nct02429180_add21_found():
    return po_additional("NCT02429180", 21)

def check_po_nct02429180_add22_found():
    return po_additional("NCT02429180", 22)

def check_po_nct02429180_add23_found():
    return po_additional("NCT02429180", 23)

def check_po_nct02429180_add24_found():
    return po_additional("NCT02429180", 24)

def check_po_nct02429180_add25_found():
    return po_additional("NCT02429180", 25)

def check_po_nct02429180_add26_found():
    return po_additional("NCT02429180", 26)

def check_po_nct02429180_add27_found():
    return po_additional("NCT02429180", 27)

def check_po_nct02429180_add28_found():
    return po_additional("NCT02429180", 28)

def check_po_nct02429180_add29_found():
    return po_additional("NCT02429180", 29)

def check_po_nct02429180_add30_found():
    return po_additional("NCT02429180", 30)

def check_po_nct02429180_add31_found():
    return po_additional("NCT02429180", 31)

def check_po_nct02429180_add32_found():
    return po_additional("NCT02429180", 32)

def check_po_nct02429180_add33_found():
    return po_additional("NCT02429180", 33)

def check_po_nct02429180_add34_found():
    return po_additional("NCT02429180", 34)

def check_po_nct02429180_add35_found():
    return po_additional("NCT02429180", 35)

def check_po_nct02429180_add36_found():
    return po_additional("NCT02429180", 36)

def check_po_nct02429180_add37_found():
    return po_additional("NCT02429180", 37)

def check_po_nct02429180_add38_found():
    return po_additional("NCT02429180", 38)

def check_po_nct02429180_add39_found():
    return po_additional("NCT02429180", 39)

def check_po_nct02429180_add40_found():
    return po_additional("NCT02429180", 40)

def check_po_nct02429180_add41_found():
    return po_additional("NCT02429180", 41)

def check_po_nct02429180_add42_found():
    return po_additional("NCT02429180", 42)

def check_po_nct02429180_add43_found():
    return po_additional("NCT02429180", 43)

def check_po_nct02429180_add44_found():
    return po_additional("NCT02429180", 44)

def check_po_nct02429180_add45_found():
    return po_additional("NCT02429180", 45)

def check_po_nct02429180_add46_found():
    return po_additional("NCT02429180", 46)

def check_po_nct02429180_add47_found():
    return po_additional("NCT02429180", 47)

def check_po_nct02429180_add48_found():
    return po_additional("NCT02429180", 48)

def check_po_nct02429180_add49_found():
    return po_additional("NCT02429180", 49)

def check_po_nct02429180_add50_found():
    return po_additional("NCT02429180", 50)

def check_po_nct02429180_add51_found():
    return po_additional("NCT02429180", 51)

def check_po_nct02429180_add52_found():
    return po_additional("NCT02429180", 52)

def check_po_nct02429180_add53_found():
    return po_additional("NCT02429180", 53)

def check_po_nct02429180_add54_found():
    return po_additional("NCT02429180", 54)

def check_po_nct02429180_add55_found():
    return po_additional("NCT02429180", 55)

def check_po_nct02429180_add56_found():
    return po_additional("NCT02429180", 56)

def check_po_nct02429180_add57_found():
    return po_additional("NCT02429180", 57)

def check_po_nct02429180_add58_found():
    return po_additional("NCT02429180", 58)

def check_po_nct02429180_add59_found():
    return po_additional("NCT02429180", 59)

def check_po_nct02429180_add60_found():
    return po_additional("NCT02429180", 60)

def check_po_nct02429180_add61_found():
    return po_additional("NCT02429180", 61)

def check_static_nct02584283_coverage():
    return static_coverage("NCT02584283")

def check_static_nct02584283_basis():
    return static_basis("NCT02584283")

def check_reward_hacking_nct02584283_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02584283")

def check_reward_hacking_nct02584283_result_quote_numeric():
    return rh_result_quote_numeric("NCT02584283")

def check_reward_hacking_nct02584283_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02584283")

def check_reward_hacking_nct02584283_negative_rows_clean():
    return rh_negative_rows_clean("NCT02584283")

def check_reward_hacking_nct02584283_additional_within_bound():
    return rh_additional_within_bound("NCT02584283")

def check_reward_hacking_nct02584283_row_shape_rules():
    return rh_row_shape_rules("NCT02584283")

def check_reward_hacking_nct02584283_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02584283")

def check_po_nct02584283_basis_derived():
    return po_basis_derived("NCT02584283")

def check_static_nct02584283_pri1_registry_fields():
    return static_registry_fields("NCT02584283", "pri1")

def check_po_nct02584283_pri1_reported():
    return po_reported("NCT02584283", "pri1")

def check_po_nct02584283_pri1_document():
    return po_field("NCT02584283", "pri1", "document")

def check_po_nct02584283_pri1_label():
    return po_field("NCT02584283", "pri1", "label")

def check_po_nct02584283_pri1_role():
    return po_field("NCT02584283", "pri1", "role")

def check_static_nct02584283_sec1_registry_fields():
    return static_registry_fields("NCT02584283", "sec1")

def check_po_nct02584283_sec1_reported():
    return po_reported("NCT02584283", "sec1")

def check_po_nct02584283_sec1_document():
    return po_field("NCT02584283", "sec1", "document")

def check_po_nct02584283_sec1_label():
    return po_field("NCT02584283", "sec1", "label")

def check_po_nct02584283_sec1_instrument():
    return po_field("NCT02584283", "sec1", "instrument")

def check_po_nct02584283_sec1_role():
    return po_field("NCT02584283", "sec1", "role")

def check_static_nct02584283_sec4_registry_fields():
    return static_registry_fields("NCT02584283", "sec4")

def check_po_nct02584283_sec4_reported():
    return po_reported("NCT02584283", "sec4")

def check_po_nct02584283_sec4_document():
    return po_field("NCT02584283", "sec4", "document")

def check_po_nct02584283_sec4_label():
    return po_field("NCT02584283", "sec4", "label")

def check_po_nct02584283_sec4_role():
    return po_field("NCT02584283", "sec4", "role")

def check_static_nct02584283_sec5_registry_fields():
    return static_registry_fields("NCT02584283", "sec5")

def check_po_nct02584283_sec5_reported():
    return po_reported("NCT02584283", "sec5")

def check_po_nct02584283_sec5_document():
    return po_field("NCT02584283", "sec5", "document")

def check_po_nct02584283_sec5_label():
    return po_field("NCT02584283", "sec5", "label")

def check_po_nct02584283_sec5_role():
    return po_field("NCT02584283", "sec5", "role")

def check_static_nct02584283_sec7_registry_fields():
    return static_registry_fields("NCT02584283", "sec7")

def check_po_nct02584283_sec7_reported():
    return po_reported("NCT02584283", "sec7")

def check_static_nct02584283_sec8_registry_fields():
    return static_registry_fields("NCT02584283", "sec8")

def check_po_nct02584283_sec8_reported():
    return po_reported("NCT02584283", "sec8")

def check_static_nct02584283_sec9_registry_fields():
    return static_registry_fields("NCT02584283", "sec9")

def check_po_nct02584283_sec9_reported():
    return po_reported("NCT02584283", "sec9")

def check_static_nct02584283_sec10_registry_fields():
    return static_registry_fields("NCT02584283", "sec10")

def check_po_nct02584283_sec10_reported():
    return po_reported("NCT02584283", "sec10")

def check_static_nct02584283_sec13_registry_fields():
    return static_registry_fields("NCT02584283", "sec13")

def check_po_nct02584283_sec13_reported():
    return po_reported("NCT02584283", "sec13")

def check_static_nct02584283_sec14_registry_fields():
    return static_registry_fields("NCT02584283", "sec14")

def check_po_nct02584283_sec14_reported():
    return po_reported("NCT02584283", "sec14")

def check_static_nct02584283_sec15_registry_fields():
    return static_registry_fields("NCT02584283", "sec15")

def check_po_nct02584283_sec15_reported():
    return po_reported("NCT02584283", "sec15")

def check_static_nct02584283_sec16_registry_fields():
    return static_registry_fields("NCT02584283", "sec16")

def check_po_nct02584283_sec16_reported():
    return po_reported("NCT02584283", "sec16")

def check_static_nct02584283_sec17_registry_fields():
    return static_registry_fields("NCT02584283", "sec17")

def check_po_nct02584283_sec17_reported():
    return po_reported("NCT02584283", "sec17")

def check_static_nct02584283_sec18_registry_fields():
    return static_registry_fields("NCT02584283", "sec18")

def check_po_nct02584283_sec18_reported():
    return po_reported("NCT02584283", "sec18")

def check_static_nct02584283_sec19_registry_fields():
    return static_registry_fields("NCT02584283", "sec19")

def check_po_nct02584283_sec19_reported():
    return po_reported("NCT02584283", "sec19")

def check_static_nct02584283_sec20_registry_fields():
    return static_registry_fields("NCT02584283", "sec20")

def check_po_nct02584283_sec20_reported():
    return po_reported("NCT02584283", "sec20")

def check_static_nct02584283_sec21_registry_fields():
    return static_registry_fields("NCT02584283", "sec21")

def check_po_nct02584283_sec21_reported():
    return po_reported("NCT02584283", "sec21")

def check_static_nct02584283_sec22_registry_fields():
    return static_registry_fields("NCT02584283", "sec22")

def check_po_nct02584283_sec22_reported():
    return po_reported("NCT02584283", "sec22")

def check_static_nct02584283_sec23_registry_fields():
    return static_registry_fields("NCT02584283", "sec23")

def check_po_nct02584283_sec23_reported():
    return po_reported("NCT02584283", "sec23")

def check_static_nct02584283_sec24_registry_fields():
    return static_registry_fields("NCT02584283", "sec24")

def check_po_nct02584283_sec24_reported():
    return po_reported("NCT02584283", "sec24")

def check_static_nct02584283_sec25_registry_fields():
    return static_registry_fields("NCT02584283", "sec25")

def check_po_nct02584283_sec25_reported():
    return po_reported("NCT02584283", "sec25")

def check_static_nct02584283_sec26_registry_fields():
    return static_registry_fields("NCT02584283", "sec26")

def check_po_nct02584283_sec26_reported():
    return po_reported("NCT02584283", "sec26")

def check_static_nct02584283_sec27_registry_fields():
    return static_registry_fields("NCT02584283", "sec27")

def check_po_nct02584283_sec27_reported():
    return po_reported("NCT02584283", "sec27")

def check_static_nct02584283_sec28_registry_fields():
    return static_registry_fields("NCT02584283", "sec28")

def check_po_nct02584283_sec28_reported():
    return po_reported("NCT02584283", "sec28")

def check_static_nct02584283_sec29_registry_fields():
    return static_registry_fields("NCT02584283", "sec29")

def check_po_nct02584283_sec29_reported():
    return po_reported("NCT02584283", "sec29")

def check_static_nct02584283_sec30_registry_fields():
    return static_registry_fields("NCT02584283", "sec30")

def check_po_nct02584283_sec30_reported():
    return po_reported("NCT02584283", "sec30")

def check_static_nct02584283_sec31_registry_fields():
    return static_registry_fields("NCT02584283", "sec31")

def check_po_nct02584283_sec31_reported():
    return po_reported("NCT02584283", "sec31")

def check_static_nct02584283_sec32_registry_fields():
    return static_registry_fields("NCT02584283", "sec32")

def check_po_nct02584283_sec32_reported():
    return po_reported("NCT02584283", "sec32")

def check_static_nct02584283_sec33_registry_fields():
    return static_registry_fields("NCT02584283", "sec33")

def check_po_nct02584283_sec33_reported():
    return po_reported("NCT02584283", "sec33")

def check_static_nct02584283_sec34_registry_fields():
    return static_registry_fields("NCT02584283", "sec34")

def check_po_nct02584283_sec34_reported():
    return po_reported("NCT02584283", "sec34")

def check_static_nct02584283_sec35_registry_fields():
    return static_registry_fields("NCT02584283", "sec35")

def check_po_nct02584283_sec35_reported():
    return po_reported("NCT02584283", "sec35")

def check_static_nct02584283_sec36_registry_fields():
    return static_registry_fields("NCT02584283", "sec36")

def check_po_nct02584283_sec36_reported():
    return po_reported("NCT02584283", "sec36")

def check_static_nct02584283_sec39_registry_fields():
    return static_registry_fields("NCT02584283", "sec39")

def check_po_nct02584283_sec39_reported():
    return po_reported("NCT02584283", "sec39")

def check_po_nct02584283_add0_found():
    return po_additional("NCT02584283", 0)

def check_po_nct02584283_add1_found():
    return po_additional("NCT02584283", 1)

def check_po_nct02584283_add2_found():
    return po_additional("NCT02584283", 2)

def check_po_nct02584283_add3_found():
    return po_additional("NCT02584283", 3)

def check_po_nct02584283_add4_found():
    return po_additional("NCT02584283", 4)

def check_po_nct02584283_add5_found():
    return po_additional("NCT02584283", 5)

def check_po_nct02584283_add6_found():
    return po_additional("NCT02584283", 6)

def check_po_nct02584283_add7_found():
    return po_additional("NCT02584283", 7)

def check_po_nct02584283_add8_found():
    return po_additional("NCT02584283", 8)

def check_po_nct02584283_add9_found():
    return po_additional("NCT02584283", 9)

def check_po_nct02584283_add10_found():
    return po_additional("NCT02584283", 10)

def check_po_nct02584283_add11_found():
    return po_additional("NCT02584283", 11)

def check_po_nct02584283_add12_found():
    return po_additional("NCT02584283", 12)

def check_po_nct02584283_add13_found():
    return po_additional("NCT02584283", 13)

def check_po_nct02584283_add14_found():
    return po_additional("NCT02584283", 14)

def check_po_nct02584283_add15_found():
    return po_additional("NCT02584283", 15)

def check_po_nct02584283_add16_found():
    return po_additional("NCT02584283", 16)

def check_po_nct02584283_add17_found():
    return po_additional("NCT02584283", 17)

def check_po_nct02584283_add18_found():
    return po_additional("NCT02584283", 18)

def check_po_nct02584283_add19_found():
    return po_additional("NCT02584283", 19)

def check_po_nct02584283_add20_found():
    return po_additional("NCT02584283", 20)

def check_po_nct02584283_add21_found():
    return po_additional("NCT02584283", 21)

def check_po_nct02584283_add22_found():
    return po_additional("NCT02584283", 22)

def check_po_nct02584283_add23_found():
    return po_additional("NCT02584283", 23)

def check_po_nct02584283_add24_found():
    return po_additional("NCT02584283", 24)

def check_po_nct02584283_add25_found():
    return po_additional("NCT02584283", 25)

def check_po_nct02584283_add26_found():
    return po_additional("NCT02584283", 26)

def check_po_nct02584283_add27_found():
    return po_additional("NCT02584283", 27)

def check_po_nct02584283_add28_found():
    return po_additional("NCT02584283", 28)

def check_po_nct02584283_add29_found():
    return po_additional("NCT02584283", 29)

def check_po_nct02584283_add30_found():
    return po_additional("NCT02584283", 30)

def check_po_nct02584283_add31_found():
    return po_additional("NCT02584283", 31)

def check_po_nct02584283_add32_found():
    return po_additional("NCT02584283", 32)

def check_po_nct02584283_add33_found():
    return po_additional("NCT02584283", 33)

def check_po_nct02584283_add34_found():
    return po_additional("NCT02584283", 34)

def check_po_nct02584283_add35_found():
    return po_additional("NCT02584283", 35)

def check_po_nct02584283_add36_found():
    return po_additional("NCT02584283", 36)

def check_po_nct02584283_add37_found():
    return po_additional("NCT02584283", 37)

def check_po_nct02584283_add38_found():
    return po_additional("NCT02584283", 38)

def check_po_nct02584283_add39_found():
    return po_additional("NCT02584283", 39)

def check_po_nct02584283_add40_found():
    return po_additional("NCT02584283", 40)

def check_po_nct02584283_add41_found():
    return po_additional("NCT02584283", 41)

def check_po_nct02584283_add42_found():
    return po_additional("NCT02584283", 42)

def check_po_nct02584283_add43_found():
    return po_additional("NCT02584283", 43)

def check_po_nct02584283_add44_found():
    return po_additional("NCT02584283", 44)

def check_po_nct02584283_add45_found():
    return po_additional("NCT02584283", 45)

def check_po_nct02584283_add46_found():
    return po_additional("NCT02584283", 46)

def check_po_nct02584283_add47_found():
    return po_additional("NCT02584283", 47)

def check_po_nct02584283_add48_found():
    return po_additional("NCT02584283", 48)

def check_po_nct02584283_add49_found():
    return po_additional("NCT02584283", 49)

def check_po_nct02584283_add50_found():
    return po_additional("NCT02584283", 50)

def check_po_nct02584283_add51_found():
    return po_additional("NCT02584283", 51)

def check_po_nct02584283_add52_found():
    return po_additional("NCT02584283", 52)

def check_po_nct02584283_add53_found():
    return po_additional("NCT02584283", 53)

def check_po_nct02584283_add54_found():
    return po_additional("NCT02584283", 54)

def check_po_nct02584283_add55_found():
    return po_additional("NCT02584283", 55)

def check_po_nct02584283_add56_found():
    return po_additional("NCT02584283", 56)

def check_po_nct02584283_add57_found():
    return po_additional("NCT02584283", 57)

def check_po_nct02584283_add58_found():
    return po_additional("NCT02584283", 58)

def check_po_nct02584283_add59_found():
    return po_additional("NCT02584283", 59)

def check_po_nct02584283_add60_found():
    return po_additional("NCT02584283", 60)

def check_po_nct02584283_add61_found():
    return po_additional("NCT02584283", 61)

def check_po_nct02584283_add62_found():
    return po_additional("NCT02584283", 62)

def check_po_nct02584283_add63_found():
    return po_additional("NCT02584283", 63)

def check_po_nct02584283_add64_found():
    return po_additional("NCT02584283", 64)

def check_po_nct02584283_add65_found():
    return po_additional("NCT02584283", 65)

def check_po_nct02584283_add66_found():
    return po_additional("NCT02584283", 66)

def check_po_nct02584283_add67_found():
    return po_additional("NCT02584283", 67)

def check_po_nct02584283_add68_found():
    return po_additional("NCT02584283", 68)

def check_po_nct02584283_add69_found():
    return po_additional("NCT02584283", 69)

def check_po_nct02584283_add70_found():
    return po_additional("NCT02584283", 70)

def check_po_nct02584283_add71_found():
    return po_additional("NCT02584283", 71)

def check_po_nct02584283_add72_found():
    return po_additional("NCT02584283", 72)

def check_po_nct02584283_add73_found():
    return po_additional("NCT02584283", 73)

def check_static_nct02747927_coverage():
    return static_coverage("NCT02747927")

def check_static_nct02747927_basis():
    return static_basis("NCT02747927")

def check_reward_hacking_nct02747927_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02747927")

def check_reward_hacking_nct02747927_result_quote_numeric():
    return rh_result_quote_numeric("NCT02747927")

def check_reward_hacking_nct02747927_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02747927")

def check_reward_hacking_nct02747927_negative_rows_clean():
    return rh_negative_rows_clean("NCT02747927")

def check_reward_hacking_nct02747927_additional_within_bound():
    return rh_additional_within_bound("NCT02747927")

def check_reward_hacking_nct02747927_row_shape_rules():
    return rh_row_shape_rules("NCT02747927")

def check_reward_hacking_nct02747927_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02747927")

def check_po_nct02747927_basis_derived():
    return po_basis_derived("NCT02747927")

def check_static_nct02747927_pri1_registry_fields():
    return static_registry_fields("NCT02747927", "pri1")

def check_po_nct02747927_pri1_reported():
    return po_reported("NCT02747927", "pri1")

def check_po_nct02747927_pri1_document():
    return po_field("NCT02747927", "pri1", "document")

def check_po_nct02747927_pri1_label():
    return po_field("NCT02747927", "pri1", "label")

def check_po_nct02747927_pri1_instrument():
    return po_field("NCT02747927", "pri1", "instrument")

def check_po_nct02747927_pri1_role():
    return po_field("NCT02747927", "pri1", "role")

def check_static_nct02747927_sec4_registry_fields():
    return static_registry_fields("NCT02747927", "sec4")

def check_po_nct02747927_sec4_reported():
    return po_reported("NCT02747927", "sec4")

def check_po_nct02747927_sec4_document():
    return po_field("NCT02747927", "sec4", "document")

def check_po_nct02747927_sec4_label():
    return po_field("NCT02747927", "sec4", "label")

def check_po_nct02747927_sec4_instrument():
    return po_field("NCT02747927", "sec4", "instrument")

def check_po_nct02747927_sec4_role():
    return po_field("NCT02747927", "sec4", "role")

def check_static_nct02747927_sec6_registry_fields():
    return static_registry_fields("NCT02747927", "sec6")

def check_po_nct02747927_sec6_reported():
    return po_reported("NCT02747927", "sec6")

def check_static_nct02747927_sec7_registry_fields():
    return static_registry_fields("NCT02747927", "sec7")

def check_po_nct02747927_sec7_reported():
    return po_reported("NCT02747927", "sec7")

def check_static_nct02747927_sec8_registry_fields():
    return static_registry_fields("NCT02747927", "sec8")

def check_po_nct02747927_sec8_reported():
    return po_reported("NCT02747927", "sec8")

def check_static_nct02747927_sec9_registry_fields():
    return static_registry_fields("NCT02747927", "sec9")

def check_po_nct02747927_sec9_reported():
    return po_reported("NCT02747927", "sec9")

def check_static_nct02747927_sec11_registry_fields():
    return static_registry_fields("NCT02747927", "sec11")

def check_po_nct02747927_sec11_reported():
    return po_reported("NCT02747927", "sec11")

def check_po_nct02747927_sec11_document():
    return po_field("NCT02747927", "sec11", "document")

def check_po_nct02747927_sec11_label():
    return po_field("NCT02747927", "sec11", "label")

def check_po_nct02747927_sec11_role():
    return po_field("NCT02747927", "sec11", "role")

def check_static_nct02747927_sec15_registry_fields():
    return static_registry_fields("NCT02747927", "sec15")

def check_po_nct02747927_sec15_reported():
    return po_reported("NCT02747927", "sec15")

def check_po_nct02747927_add0_found():
    return po_additional("NCT02747927", 0)

def check_po_nct02747927_add1_found():
    return po_additional("NCT02747927", 1)

def check_po_nct02747927_add2_found():
    return po_additional("NCT02747927", 2)

def check_po_nct02747927_add3_found():
    return po_additional("NCT02747927", 3)

def check_po_nct02747927_add4_found():
    return po_additional("NCT02747927", 4)

def check_po_nct02747927_add5_found():
    return po_additional("NCT02747927", 5)

def check_po_nct02747927_add6_found():
    return po_additional("NCT02747927", 6)

def check_po_nct02747927_add7_found():
    return po_additional("NCT02747927", 7)

def check_po_nct02747927_add8_found():
    return po_additional("NCT02747927", 8)

def check_po_nct02747927_add9_found():
    return po_additional("NCT02747927", 9)

def check_po_nct02747927_add10_found():
    return po_additional("NCT02747927", 10)

def check_po_nct02747927_add11_found():
    return po_additional("NCT02747927", 11)

def check_po_nct02747927_add12_found():
    return po_additional("NCT02747927", 12)

def check_po_nct02747927_add13_found():
    return po_additional("NCT02747927", 13)

def check_po_nct02747927_add14_found():
    return po_additional("NCT02747927", 14)

def check_po_nct02747927_add15_found():
    return po_additional("NCT02747927", 15)

def check_po_nct02747927_add16_found():
    return po_additional("NCT02747927", 16)

def check_po_nct02747927_add17_found():
    return po_additional("NCT02747927", 17)

def check_po_nct02747927_add18_found():
    return po_additional("NCT02747927", 18)

def check_po_nct02747927_add19_found():
    return po_additional("NCT02747927", 19)

def check_po_nct02747927_add20_found():
    return po_additional("NCT02747927", 20)

def check_po_nct02747927_add21_found():
    return po_additional("NCT02747927", 21)

def check_po_nct02747927_add22_found():
    return po_additional("NCT02747927", 22)

def check_po_nct02747927_add23_found():
    return po_additional("NCT02747927", 23)

def check_po_nct02747927_add24_found():
    return po_additional("NCT02747927", 24)

def check_po_nct02747927_add25_found():
    return po_additional("NCT02747927", 25)

def check_po_nct02747927_add26_found():
    return po_additional("NCT02747927", 26)

def check_po_nct02747927_add27_found():
    return po_additional("NCT02747927", 27)

def check_po_nct02747927_add28_found():
    return po_additional("NCT02747927", 28)

def check_po_nct02747927_add29_found():
    return po_additional("NCT02747927", 29)

def check_po_nct02747927_add30_found():
    return po_additional("NCT02747927", 30)

def check_po_nct02747927_add31_found():
    return po_additional("NCT02747927", 31)

def check_po_nct02747927_add32_found():
    return po_additional("NCT02747927", 32)

def check_po_nct02747927_add33_found():
    return po_additional("NCT02747927", 33)

def check_po_nct02747927_add34_found():
    return po_additional("NCT02747927", 34)

def check_po_nct02747927_add35_found():
    return po_additional("NCT02747927", 35)

def check_po_nct02747927_add36_found():
    return po_additional("NCT02747927", 36)

def check_po_nct02747927_add37_found():
    return po_additional("NCT02747927", 37)

def check_po_nct02747927_add38_found():
    return po_additional("NCT02747927", 38)

def check_po_nct02747927_add39_found():
    return po_additional("NCT02747927", 39)

def check_po_nct02747927_add40_found():
    return po_additional("NCT02747927", 40)

def check_po_nct02747927_add41_found():
    return po_additional("NCT02747927", 41)

def check_po_nct02747927_add42_found():
    return po_additional("NCT02747927", 42)

def check_po_nct02747927_add43_found():
    return po_additional("NCT02747927", 43)

def check_po_nct02747927_add44_found():
    return po_additional("NCT02747927", 44)

def check_po_nct02747927_add45_found():
    return po_additional("NCT02747927", 45)

def check_po_nct02747927_add46_found():
    return po_additional("NCT02747927", 46)

def check_po_nct02747927_add47_found():
    return po_additional("NCT02747927", 47)

def check_po_nct02747927_add48_found():
    return po_additional("NCT02747927", 48)

def check_po_nct02747927_add49_found():
    return po_additional("NCT02747927", 49)

def check_po_nct02747927_add50_found():
    return po_additional("NCT02747927", 50)

def check_po_nct02747927_add51_found():
    return po_additional("NCT02747927", 51)

def check_po_nct02747927_add52_found():
    return po_additional("NCT02747927", 52)

def check_po_nct02747927_add53_found():
    return po_additional("NCT02747927", 53)

def check_po_nct02747927_add54_found():
    return po_additional("NCT02747927", 54)

def check_po_nct02747927_add55_found():
    return po_additional("NCT02747927", 55)

def check_po_nct02747927_add56_found():
    return po_additional("NCT02747927", 56)

def check_po_nct02747927_add57_found():
    return po_additional("NCT02747927", 57)

def check_po_nct02747927_add58_found():
    return po_additional("NCT02747927", 58)

def check_po_nct02747927_add59_found():
    return po_additional("NCT02747927", 59)

def check_po_nct02747927_add60_found():
    return po_additional("NCT02747927", 60)

def check_po_nct02747927_add61_found():
    return po_additional("NCT02747927", 61)

def check_po_nct02747927_add62_found():
    return po_additional("NCT02747927", 62)

def check_po_nct02747927_add63_found():
    return po_additional("NCT02747927", 63)

def check_po_nct02747927_add64_found():
    return po_additional("NCT02747927", 64)

def check_po_nct02747927_add65_found():
    return po_additional("NCT02747927", 65)

def check_po_nct02747927_add66_found():
    return po_additional("NCT02747927", 66)

def check_po_nct02747927_add67_found():
    return po_additional("NCT02747927", 67)

def check_po_nct02747927_add68_found():
    return po_additional("NCT02747927", 68)

def check_po_nct02747927_add69_found():
    return po_additional("NCT02747927", 69)

def check_po_nct02747927_add70_found():
    return po_additional("NCT02747927", 70)

def check_po_nct02747927_add71_found():
    return po_additional("NCT02747927", 71)

def check_po_nct02747927_add72_found():
    return po_additional("NCT02747927", 72)

def check_po_nct02747927_add73_found():
    return po_additional("NCT02747927", 73)

def check_po_nct02747927_add74_found():
    return po_additional("NCT02747927", 74)

def check_po_nct02747927_add75_found():
    return po_additional("NCT02747927", 75)

def check_po_nct02747927_add76_found():
    return po_additional("NCT02747927", 76)

def check_po_nct02747927_add77_found():
    return po_additional("NCT02747927", 77)

def check_po_nct02747927_add78_found():
    return po_additional("NCT02747927", 78)

def check_po_nct02747927_add79_found():
    return po_additional("NCT02747927", 79)

def check_po_nct02747927_add80_found():
    return po_additional("NCT02747927", 80)

def check_po_nct02747927_add81_found():
    return po_additional("NCT02747927", 81)

def check_po_nct02747927_add82_found():
    return po_additional("NCT02747927", 82)

def check_po_nct02747927_add83_found():
    return po_additional("NCT02747927", 83)

def check_po_nct02747927_add84_found():
    return po_additional("NCT02747927", 84)

def check_po_nct02747927_add85_found():
    return po_additional("NCT02747927", 85)

def check_po_nct02747927_add86_found():
    return po_additional("NCT02747927", 86)

def check_po_nct02747927_add87_found():
    return po_additional("NCT02747927", 87)

def check_po_nct02747927_add88_found():
    return po_additional("NCT02747927", 88)

def check_po_nct02747927_add89_found():
    return po_additional("NCT02747927", 89)

def check_po_nct02747927_add90_found():
    return po_additional("NCT02747927", 90)

def check_po_nct02747927_add91_found():
    return po_additional("NCT02747927", 91)

def check_po_nct02747927_add92_found():
    return po_additional("NCT02747927", 92)

def check_po_nct02747927_add93_found():
    return po_additional("NCT02747927", 93)

def check_po_nct02747927_add94_found():
    return po_additional("NCT02747927", 94)

def check_po_nct02747927_add95_found():
    return po_additional("NCT02747927", 95)

def check_po_nct02747927_add96_found():
    return po_additional("NCT02747927", 96)

def check_po_nct02747927_add97_found():
    return po_additional("NCT02747927", 97)

def check_po_nct02747927_add98_found():
    return po_additional("NCT02747927", 98)

def check_po_nct02747927_add99_found():
    return po_additional("NCT02747927", 99)

def check_po_nct02747927_add100_found():
    return po_additional("NCT02747927", 100)

def check_po_nct02747927_add101_found():
    return po_additional("NCT02747927", 101)

def check_po_nct02747927_add102_found():
    return po_additional("NCT02747927", 102)

def check_po_nct02747927_add103_found():
    return po_additional("NCT02747927", 103)

def check_po_nct02747927_add104_found():
    return po_additional("NCT02747927", 104)

def check_po_nct02747927_add105_found():
    return po_additional("NCT02747927", 105)

def check_po_nct02747927_add106_found():
    return po_additional("NCT02747927", 106)

def check_po_nct02747927_add107_found():
    return po_additional("NCT02747927", 107)

def check_po_nct02747927_add108_found():
    return po_additional("NCT02747927", 108)

def check_po_nct02747927_add109_found():
    return po_additional("NCT02747927", 109)

def check_po_nct02747927_add110_found():
    return po_additional("NCT02747927", 110)

def check_po_nct02747927_add111_found():
    return po_additional("NCT02747927", 111)

def check_po_nct02747927_add112_found():
    return po_additional("NCT02747927", 112)

def check_po_nct02747927_add113_found():
    return po_additional("NCT02747927", 113)

def check_po_nct02747927_add114_found():
    return po_additional("NCT02747927", 114)

def check_po_nct02747927_add115_found():
    return po_additional("NCT02747927", 115)

def check_po_nct02747927_add116_found():
    return po_additional("NCT02747927", 116)

def check_po_nct02747927_add117_found():
    return po_additional("NCT02747927", 117)

def check_po_nct02747927_add118_found():
    return po_additional("NCT02747927", 118)

def check_static_nct02944682_coverage():
    return static_coverage("NCT02944682")

def check_static_nct02944682_basis():
    return static_basis("NCT02944682")

def check_reward_hacking_nct02944682_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT02944682")

def check_reward_hacking_nct02944682_result_quote_numeric():
    return rh_result_quote_numeric("NCT02944682")

def check_reward_hacking_nct02944682_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT02944682")

def check_reward_hacking_nct02944682_negative_rows_clean():
    return rh_negative_rows_clean("NCT02944682")

def check_reward_hacking_nct02944682_additional_within_bound():
    return rh_additional_within_bound("NCT02944682")

def check_reward_hacking_nct02944682_row_shape_rules():
    return rh_row_shape_rules("NCT02944682")

def check_reward_hacking_nct02944682_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT02944682")

def check_po_nct02944682_basis_derived():
    return po_basis_derived("NCT02944682")

def check_static_nct02944682_pri1_registry_fields():
    return static_registry_fields("NCT02944682", "pri1")

def check_po_nct02944682_pri1_reported():
    return po_reported("NCT02944682", "pri1")

def check_po_nct02944682_pri1_document():
    return po_field("NCT02944682", "pri1", "document")

def check_po_nct02944682_pri1_label():
    return po_field("NCT02944682", "pri1", "label")

def check_po_nct02944682_pri1_instrument():
    return po_field("NCT02944682", "pri1", "instrument")

def check_po_nct02944682_pri1_role():
    return po_field("NCT02944682", "pri1", "role")

def check_static_nct02944682_pri3_registry_fields():
    return static_registry_fields("NCT02944682", "pri3")

def check_po_nct02944682_pri3_reported():
    return po_reported("NCT02944682", "pri3")

def check_po_nct02944682_pri3_document():
    return po_field("NCT02944682", "pri3", "document")

def check_po_nct02944682_pri3_label():
    return po_field("NCT02944682", "pri3", "label")

def check_po_nct02944682_pri3_instrument():
    return po_field("NCT02944682", "pri3", "instrument")

def check_po_nct02944682_pri3_role():
    return po_field("NCT02944682", "pri3", "role")

def check_static_nct02944682_pri4_registry_fields():
    return static_registry_fields("NCT02944682", "pri4")

def check_po_nct02944682_pri4_reported():
    return po_reported("NCT02944682", "pri4")

def check_po_nct02944682_pri4_document():
    return po_field("NCT02944682", "pri4", "document")

def check_po_nct02944682_pri4_label():
    return po_field("NCT02944682", "pri4", "label")

def check_po_nct02944682_pri4_instrument():
    return po_field("NCT02944682", "pri4", "instrument")

def check_po_nct02944682_pri4_role():
    return po_field("NCT02944682", "pri4", "role")

def check_static_nct02944682_sec2_registry_fields():
    return static_registry_fields("NCT02944682", "sec2")

def check_po_nct02944682_sec2_reported():
    return po_reported("NCT02944682", "sec2")

def check_po_nct02944682_sec2_document():
    return po_field("NCT02944682", "sec2", "document")

def check_po_nct02944682_sec2_label():
    return po_field("NCT02944682", "sec2", "label")

def check_po_nct02944682_sec2_instrument():
    return po_field("NCT02944682", "sec2", "instrument")

def check_po_nct02944682_sec2_role():
    return po_field("NCT02944682", "sec2", "role")

def check_static_nct02944682_sec4_registry_fields():
    return static_registry_fields("NCT02944682", "sec4")

def check_po_nct02944682_sec4_reported():
    return po_reported("NCT02944682", "sec4")

def check_static_nct02944682_sec5_registry_fields():
    return static_registry_fields("NCT02944682", "sec5")

def check_po_nct02944682_sec5_reported():
    return po_reported("NCT02944682", "sec5")

def check_static_nct02944682_sec6_registry_fields():
    return static_registry_fields("NCT02944682", "sec6")

def check_po_nct02944682_sec6_reported():
    return po_reported("NCT02944682", "sec6")

def check_static_nct02944682_sec7_registry_fields():
    return static_registry_fields("NCT02944682", "sec7")

def check_po_nct02944682_sec7_reported():
    return po_reported("NCT02944682", "sec7")

def check_static_nct02944682_oth2_registry_fields():
    return static_registry_fields("NCT02944682", "oth2")

def check_po_nct02944682_oth2_reported():
    return po_reported("NCT02944682", "oth2")

def check_po_nct02944682_oth2_document():
    return po_field("NCT02944682", "oth2", "document")

def check_po_nct02944682_oth2_label():
    return po_field("NCT02944682", "oth2", "label")

def check_po_nct02944682_oth2_instrument():
    return po_field("NCT02944682", "oth2", "instrument")

def check_po_nct02944682_oth2_role():
    return po_field("NCT02944682", "oth2", "role")

def check_static_nct02944682_oth3_registry_fields():
    return static_registry_fields("NCT02944682", "oth3")

def check_po_nct02944682_oth3_reported():
    return po_reported("NCT02944682", "oth3")

def check_po_nct02944682_oth3_document():
    return po_field("NCT02944682", "oth3", "document")

def check_po_nct02944682_oth3_label():
    return po_field("NCT02944682", "oth3", "label")

def check_po_nct02944682_oth3_instrument():
    return po_field("NCT02944682", "oth3", "instrument")

def check_po_nct02944682_oth3_role():
    return po_field("NCT02944682", "oth3", "role")

def check_po_nct02944682_add0_found():
    return po_additional("NCT02944682", 0)

def check_po_nct02944682_add1_found():
    return po_additional("NCT02944682", 1)

def check_po_nct02944682_add2_found():
    return po_additional("NCT02944682", 2)

def check_po_nct02944682_add3_found():
    return po_additional("NCT02944682", 3)

def check_po_nct02944682_add4_found():
    return po_additional("NCT02944682", 4)

def check_po_nct02944682_add5_found():
    return po_additional("NCT02944682", 5)

def check_po_nct02944682_add6_found():
    return po_additional("NCT02944682", 6)

def check_po_nct02944682_add7_found():
    return po_additional("NCT02944682", 7)

def check_po_nct02944682_add8_found():
    return po_additional("NCT02944682", 8)

def check_po_nct02944682_add9_found():
    return po_additional("NCT02944682", 9)

def check_po_nct02944682_add10_found():
    return po_additional("NCT02944682", 10)

def check_po_nct02944682_add11_found():
    return po_additional("NCT02944682", 11)

def check_po_nct02944682_add12_found():
    return po_additional("NCT02944682", 12)

def check_po_nct02944682_add13_found():
    return po_additional("NCT02944682", 13)

def check_po_nct02944682_add14_found():
    return po_additional("NCT02944682", 14)

def check_po_nct02944682_add15_found():
    return po_additional("NCT02944682", 15)

def check_po_nct02944682_add16_found():
    return po_additional("NCT02944682", 16)

def check_po_nct02944682_add17_found():
    return po_additional("NCT02944682", 17)

def check_po_nct02944682_add18_found():
    return po_additional("NCT02944682", 18)

def check_po_nct02944682_add19_found():
    return po_additional("NCT02944682", 19)

def check_po_nct02944682_add20_found():
    return po_additional("NCT02944682", 20)

def check_po_nct02944682_add21_found():
    return po_additional("NCT02944682", 21)

def check_po_nct02944682_add22_found():
    return po_additional("NCT02944682", 22)

def check_po_nct02944682_add23_found():
    return po_additional("NCT02944682", 23)

def check_po_nct02944682_add24_found():
    return po_additional("NCT02944682", 24)

def check_po_nct02944682_add25_found():
    return po_additional("NCT02944682", 25)

def check_po_nct02944682_add26_found():
    return po_additional("NCT02944682", 26)

def check_po_nct02944682_add27_found():
    return po_additional("NCT02944682", 27)

def check_po_nct02944682_add28_found():
    return po_additional("NCT02944682", 28)

def check_po_nct02944682_add29_found():
    return po_additional("NCT02944682", 29)

def check_po_nct02944682_add30_found():
    return po_additional("NCT02944682", 30)

def check_po_nct02944682_add31_found():
    return po_additional("NCT02944682", 31)

def check_po_nct02944682_add32_found():
    return po_additional("NCT02944682", 32)

def check_po_nct02944682_add33_found():
    return po_additional("NCT02944682", 33)

def check_po_nct02944682_add34_found():
    return po_additional("NCT02944682", 34)

def check_po_nct02944682_add35_found():
    return po_additional("NCT02944682", 35)

def check_po_nct02944682_add36_found():
    return po_additional("NCT02944682", 36)

def check_po_nct02944682_add37_found():
    return po_additional("NCT02944682", 37)

def check_po_nct02944682_add38_found():
    return po_additional("NCT02944682", 38)

def check_po_nct02944682_add39_found():
    return po_additional("NCT02944682", 39)

def check_po_nct02944682_add40_found():
    return po_additional("NCT02944682", 40)

def check_po_nct02944682_add41_found():
    return po_additional("NCT02944682", 41)

def check_po_nct02944682_add42_found():
    return po_additional("NCT02944682", 42)

def check_po_nct02944682_add43_found():
    return po_additional("NCT02944682", 43)

def check_po_nct02944682_add44_found():
    return po_additional("NCT02944682", 44)

def check_po_nct02944682_add45_found():
    return po_additional("NCT02944682", 45)

def check_po_nct02944682_add46_found():
    return po_additional("NCT02944682", 46)

def check_po_nct02944682_add47_found():
    return po_additional("NCT02944682", 47)

def check_po_nct02944682_add48_found():
    return po_additional("NCT02944682", 48)

def check_po_nct02944682_add49_found():
    return po_additional("NCT02944682", 49)

def check_po_nct02944682_add50_found():
    return po_additional("NCT02944682", 50)

def check_po_nct02944682_add51_found():
    return po_additional("NCT02944682", 51)

def check_po_nct02944682_add52_found():
    return po_additional("NCT02944682", 52)

def check_po_nct02944682_add53_found():
    return po_additional("NCT02944682", 53)

def check_po_nct02944682_add54_found():
    return po_additional("NCT02944682", 54)

def check_po_nct02944682_add55_found():
    return po_additional("NCT02944682", 55)

def check_po_nct02944682_add56_found():
    return po_additional("NCT02944682", 56)

def check_po_nct02944682_add57_found():
    return po_additional("NCT02944682", 57)

def check_po_nct02944682_add58_found():
    return po_additional("NCT02944682", 58)

def check_po_nct02944682_add59_found():
    return po_additional("NCT02944682", 59)

def check_po_nct02944682_add60_found():
    return po_additional("NCT02944682", 60)

def check_po_nct02944682_add61_found():
    return po_additional("NCT02944682", 61)

def check_po_nct02944682_add62_found():
    return po_additional("NCT02944682", 62)

def check_po_nct02944682_add63_found():
    return po_additional("NCT02944682", 63)

def check_po_nct02944682_add64_found():
    return po_additional("NCT02944682", 64)

def check_po_nct02944682_add65_found():
    return po_additional("NCT02944682", 65)

def check_po_nct02944682_add66_found():
    return po_additional("NCT02944682", 66)

def check_po_nct02944682_add67_found():
    return po_additional("NCT02944682", 67)

def check_po_nct02944682_add68_found():
    return po_additional("NCT02944682", 68)

def check_po_nct02944682_add69_found():
    return po_additional("NCT02944682", 69)

def check_po_nct02944682_add70_found():
    return po_additional("NCT02944682", 70)

def check_po_nct02944682_add71_found():
    return po_additional("NCT02944682", 71)

def check_po_nct02944682_add72_found():
    return po_additional("NCT02944682", 72)

def check_po_nct02944682_add73_found():
    return po_additional("NCT02944682", 73)

def check_po_nct02944682_add74_found():
    return po_additional("NCT02944682", 74)

def check_po_nct02944682_add75_found():
    return po_additional("NCT02944682", 75)

def check_po_nct02944682_add76_found():
    return po_additional("NCT02944682", 76)

def check_po_nct02944682_add77_found():
    return po_additional("NCT02944682", 77)

def check_po_nct02944682_add78_found():
    return po_additional("NCT02944682", 78)

def check_po_nct02944682_add79_found():
    return po_additional("NCT02944682", 79)

def check_po_nct02944682_add80_found():
    return po_additional("NCT02944682", 80)

def check_po_nct02944682_add81_found():
    return po_additional("NCT02944682", 81)

def check_po_nct02944682_add82_found():
    return po_additional("NCT02944682", 82)

def check_po_nct02944682_add83_found():
    return po_additional("NCT02944682", 83)

def check_po_nct02944682_add84_found():
    return po_additional("NCT02944682", 84)

def check_po_nct02944682_add85_found():
    return po_additional("NCT02944682", 85)

def check_po_nct02944682_add86_found():
    return po_additional("NCT02944682", 86)

def check_po_nct02944682_add87_found():
    return po_additional("NCT02944682", 87)

def check_po_nct02944682_add88_found():
    return po_additional("NCT02944682", 88)

def check_po_nct02944682_add89_found():
    return po_additional("NCT02944682", 89)

def check_po_nct02944682_add90_found():
    return po_additional("NCT02944682", 90)

def check_po_nct02944682_add91_found():
    return po_additional("NCT02944682", 91)

def check_po_nct02944682_add92_found():
    return po_additional("NCT02944682", 92)

def check_po_nct02944682_add93_found():
    return po_additional("NCT02944682", 93)

def check_po_nct02944682_add94_found():
    return po_additional("NCT02944682", 94)

def check_po_nct02944682_add95_found():
    return po_additional("NCT02944682", 95)

def check_po_nct02944682_add96_found():
    return po_additional("NCT02944682", 96)

def check_po_nct02944682_add97_found():
    return po_additional("NCT02944682", 97)

def check_po_nct02944682_add98_found():
    return po_additional("NCT02944682", 98)

def check_po_nct02944682_add99_found():
    return po_additional("NCT02944682", 99)

def check_po_nct02944682_add100_found():
    return po_additional("NCT02944682", 100)

def check_po_nct02944682_add101_found():
    return po_additional("NCT02944682", 101)

def check_po_nct02944682_add102_found():
    return po_additional("NCT02944682", 102)

def check_po_nct02944682_add103_found():
    return po_additional("NCT02944682", 103)

def check_po_nct02944682_add104_found():
    return po_additional("NCT02944682", 104)

def check_po_nct02944682_add105_found():
    return po_additional("NCT02944682", 105)

def check_po_nct02944682_add106_found():
    return po_additional("NCT02944682", 106)

def check_po_nct02944682_add107_found():
    return po_additional("NCT02944682", 107)

def check_po_nct02944682_add108_found():
    return po_additional("NCT02944682", 108)

def check_po_nct02944682_add109_found():
    return po_additional("NCT02944682", 109)

def check_po_nct02944682_add110_found():
    return po_additional("NCT02944682", 110)

def check_po_nct02944682_add111_found():
    return po_additional("NCT02944682", 111)

def check_po_nct02944682_add112_found():
    return po_additional("NCT02944682", 112)

def check_po_nct02944682_add113_found():
    return po_additional("NCT02944682", 113)

def check_po_nct02944682_add114_found():
    return po_additional("NCT02944682", 114)

def check_po_nct02944682_add115_found():
    return po_additional("NCT02944682", 115)

def check_po_nct02944682_add116_found():
    return po_additional("NCT02944682", 116)

def check_po_nct02944682_add117_found():
    return po_additional("NCT02944682", 117)

def check_po_nct02944682_add118_found():
    return po_additional("NCT02944682", 118)

def check_po_nct02944682_add119_found():
    return po_additional("NCT02944682", 119)

def check_po_nct02944682_add120_found():
    return po_additional("NCT02944682", 120)

def check_po_nct02944682_add121_found():
    return po_additional("NCT02944682", 121)

def check_po_nct02944682_add122_found():
    return po_additional("NCT02944682", 122)

def check_po_nct02944682_add123_found():
    return po_additional("NCT02944682", 123)

def check_po_nct02944682_add124_found():
    return po_additional("NCT02944682", 124)

def check_po_nct02944682_add125_found():
    return po_additional("NCT02944682", 125)

def check_po_nct02944682_add126_found():
    return po_additional("NCT02944682", 126)

def check_po_nct02944682_add127_found():
    return po_additional("NCT02944682", 127)

def check_po_nct02944682_add128_found():
    return po_additional("NCT02944682", 128)

def check_po_nct02944682_add129_found():
    return po_additional("NCT02944682", 129)

def check_po_nct02944682_add130_found():
    return po_additional("NCT02944682", 130)

def check_po_nct02944682_add131_found():
    return po_additional("NCT02944682", 131)

def check_po_nct02944682_add132_found():
    return po_additional("NCT02944682", 132)

def check_po_nct02944682_add133_found():
    return po_additional("NCT02944682", 133)

def check_po_nct02944682_add134_found():
    return po_additional("NCT02944682", 134)

def check_po_nct02944682_add135_found():
    return po_additional("NCT02944682", 135)

def check_po_nct02944682_add136_found():
    return po_additional("NCT02944682", 136)

def check_po_nct02944682_add137_found():
    return po_additional("NCT02944682", 137)

def check_po_nct02944682_add138_found():
    return po_additional("NCT02944682", 138)

def check_po_nct02944682_add139_found():
    return po_additional("NCT02944682", 139)

def check_po_nct02944682_add140_found():
    return po_additional("NCT02944682", 140)

def check_po_nct02944682_add141_found():
    return po_additional("NCT02944682", 141)

def check_po_nct02944682_add142_found():
    return po_additional("NCT02944682", 142)

def check_po_nct02944682_add143_found():
    return po_additional("NCT02944682", 143)

def check_po_nct02944682_add144_found():
    return po_additional("NCT02944682", 144)

def check_po_nct02944682_add145_found():
    return po_additional("NCT02944682", 145)

def check_po_nct02944682_add146_found():
    return po_additional("NCT02944682", 146)

def check_po_nct02944682_add147_found():
    return po_additional("NCT02944682", 147)

def check_po_nct02944682_add148_found():
    return po_additional("NCT02944682", 148)

def check_po_nct02944682_add149_found():
    return po_additional("NCT02944682", 149)

def check_po_nct02944682_add150_found():
    return po_additional("NCT02944682", 150)

def check_po_nct02944682_add151_found():
    return po_additional("NCT02944682", 151)

def check_po_nct02944682_add152_found():
    return po_additional("NCT02944682", 152)

def check_po_nct02944682_add153_found():
    return po_additional("NCT02944682", 153)

def check_po_nct02944682_add154_found():
    return po_additional("NCT02944682", 154)

def check_po_nct02944682_add155_found():
    return po_additional("NCT02944682", 155)

def check_po_nct02944682_add156_found():
    return po_additional("NCT02944682", 156)

def check_po_nct02944682_add157_found():
    return po_additional("NCT02944682", 157)

def check_po_nct02944682_add158_found():
    return po_additional("NCT02944682", 158)

def check_po_nct02944682_add159_found():
    return po_additional("NCT02944682", 159)

def check_po_nct02944682_add160_found():
    return po_additional("NCT02944682", 160)

def check_po_nct02944682_add161_found():
    return po_additional("NCT02944682", 161)

def check_po_nct02944682_add162_found():
    return po_additional("NCT02944682", 162)

def check_po_nct02944682_add163_found():
    return po_additional("NCT02944682", 163)

def check_po_nct02944682_add164_found():
    return po_additional("NCT02944682", 164)

def check_po_nct02944682_add165_found():
    return po_additional("NCT02944682", 165)

def check_po_nct02944682_add166_found():
    return po_additional("NCT02944682", 166)

def check_po_nct02944682_add167_found():
    return po_additional("NCT02944682", 167)

def check_po_nct02944682_add168_found():
    return po_additional("NCT02944682", 168)

def check_po_nct02944682_add169_found():
    return po_additional("NCT02944682", 169)

def check_po_nct02944682_add170_found():
    return po_additional("NCT02944682", 170)

def check_po_nct02944682_add171_found():
    return po_additional("NCT02944682", 171)

def check_po_nct02944682_add172_found():
    return po_additional("NCT02944682", 172)

def check_po_nct02944682_add173_found():
    return po_additional("NCT02944682", 173)

def check_po_nct02944682_add174_found():
    return po_additional("NCT02944682", 174)

def check_po_nct02944682_add175_found():
    return po_additional("NCT02944682", 175)

def check_po_nct02944682_add176_found():
    return po_additional("NCT02944682", 176)

def check_po_nct02944682_add177_found():
    return po_additional("NCT02944682", 177)

def check_po_nct02944682_add178_found():
    return po_additional("NCT02944682", 178)

def check_po_nct02944682_add179_found():
    return po_additional("NCT02944682", 179)

def check_po_nct02944682_add180_found():
    return po_additional("NCT02944682", 180)

def check_po_nct02944682_add181_found():
    return po_additional("NCT02944682", 181)

def check_po_nct02944682_add182_found():
    return po_additional("NCT02944682", 182)

def check_po_nct02944682_add183_found():
    return po_additional("NCT02944682", 183)

def check_static_nct03114917_coverage():
    return static_coverage("NCT03114917")

def check_static_nct03114917_basis():
    return static_basis("NCT03114917")

def check_reward_hacking_nct03114917_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03114917")

def check_reward_hacking_nct03114917_result_quote_numeric():
    return rh_result_quote_numeric("NCT03114917")

def check_reward_hacking_nct03114917_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03114917")

def check_reward_hacking_nct03114917_negative_rows_clean():
    return rh_negative_rows_clean("NCT03114917")

def check_reward_hacking_nct03114917_additional_within_bound():
    return rh_additional_within_bound("NCT03114917")

def check_reward_hacking_nct03114917_row_shape_rules():
    return rh_row_shape_rules("NCT03114917")

def check_reward_hacking_nct03114917_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03114917")

def check_po_nct03114917_basis_derived():
    return po_basis_derived("NCT03114917")

def check_static_nct03114917_pri1_registry_fields():
    return static_registry_fields("NCT03114917", "pri1")

def check_po_nct03114917_pri1_reported():
    return po_reported("NCT03114917", "pri1")

def check_static_nct03114917_sec3_registry_fields():
    return static_registry_fields("NCT03114917", "sec3")

def check_po_nct03114917_sec3_reported():
    return po_reported("NCT03114917", "sec3")

def check_static_nct03114917_sec4_registry_fields():
    return static_registry_fields("NCT03114917", "sec4")

def check_po_nct03114917_sec4_reported():
    return po_reported("NCT03114917", "sec4")

def check_static_nct03114917_oth1_registry_fields():
    return static_registry_fields("NCT03114917", "oth1")

def check_po_nct03114917_oth1_reported():
    return po_reported("NCT03114917", "oth1")

def check_static_nct03114917_oth2_registry_fields():
    return static_registry_fields("NCT03114917", "oth2")

def check_po_nct03114917_oth2_reported():
    return po_reported("NCT03114917", "oth2")

def check_static_nct03114917_oth3_registry_fields():
    return static_registry_fields("NCT03114917", "oth3")

def check_po_nct03114917_oth3_reported():
    return po_reported("NCT03114917", "oth3")

def check_static_nct03114917_oth5_registry_fields():
    return static_registry_fields("NCT03114917", "oth5")

def check_po_nct03114917_oth5_reported():
    return po_reported("NCT03114917", "oth5")

def check_static_nct03114917_oth6_registry_fields():
    return static_registry_fields("NCT03114917", "oth6")

def check_po_nct03114917_oth6_reported():
    return po_reported("NCT03114917", "oth6")

def check_static_nct03114917_oth7_registry_fields():
    return static_registry_fields("NCT03114917", "oth7")

def check_po_nct03114917_oth7_reported():
    return po_reported("NCT03114917", "oth7")

def check_static_nct03114917_oth8_registry_fields():
    return static_registry_fields("NCT03114917", "oth8")

def check_po_nct03114917_oth8_reported():
    return po_reported("NCT03114917", "oth8")

def check_static_nct03114917_oth9_registry_fields():
    return static_registry_fields("NCT03114917", "oth9")

def check_po_nct03114917_oth9_reported():
    return po_reported("NCT03114917", "oth9")

def check_static_nct03114917_oth10_registry_fields():
    return static_registry_fields("NCT03114917", "oth10")

def check_po_nct03114917_oth10_reported():
    return po_reported("NCT03114917", "oth10")

def check_static_nct03114917_oth11_registry_fields():
    return static_registry_fields("NCT03114917", "oth11")

def check_po_nct03114917_oth11_reported():
    return po_reported("NCT03114917", "oth11")

def check_static_nct03114917_oth12_registry_fields():
    return static_registry_fields("NCT03114917", "oth12")

def check_po_nct03114917_oth12_reported():
    return po_reported("NCT03114917", "oth12")

def check_static_nct03114917_oth13_registry_fields():
    return static_registry_fields("NCT03114917", "oth13")

def check_po_nct03114917_oth13_reported():
    return po_reported("NCT03114917", "oth13")

def check_static_nct03114917_oth14_registry_fields():
    return static_registry_fields("NCT03114917", "oth14")

def check_po_nct03114917_oth14_reported():
    return po_reported("NCT03114917", "oth14")

def check_static_nct03114917_oth15_registry_fields():
    return static_registry_fields("NCT03114917", "oth15")

def check_po_nct03114917_oth15_reported():
    return po_reported("NCT03114917", "oth15")

def check_static_nct03114917_oth16_registry_fields():
    return static_registry_fields("NCT03114917", "oth16")

def check_po_nct03114917_oth16_reported():
    return po_reported("NCT03114917", "oth16")

def check_static_nct03114917_oth17_registry_fields():
    return static_registry_fields("NCT03114917", "oth17")

def check_po_nct03114917_oth17_reported():
    return po_reported("NCT03114917", "oth17")

def check_static_nct03114917_oth18_registry_fields():
    return static_registry_fields("NCT03114917", "oth18")

def check_po_nct03114917_oth18_reported():
    return po_reported("NCT03114917", "oth18")

def check_po_nct03114917_add0_found():
    return po_additional("NCT03114917", 0)

def check_po_nct03114917_add1_found():
    return po_additional("NCT03114917", 1)

def check_po_nct03114917_add2_found():
    return po_additional("NCT03114917", 2)

def check_static_nct03148457_coverage():
    return static_coverage("NCT03148457")

def check_static_nct03148457_basis():
    return static_basis("NCT03148457")

def check_reward_hacking_nct03148457_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03148457")

def check_reward_hacking_nct03148457_result_quote_numeric():
    return rh_result_quote_numeric("NCT03148457")

def check_reward_hacking_nct03148457_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03148457")

def check_reward_hacking_nct03148457_negative_rows_clean():
    return rh_negative_rows_clean("NCT03148457")

def check_reward_hacking_nct03148457_additional_within_bound():
    return rh_additional_within_bound("NCT03148457")

def check_reward_hacking_nct03148457_row_shape_rules():
    return rh_row_shape_rules("NCT03148457")

def check_reward_hacking_nct03148457_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03148457")

def check_po_nct03148457_basis_derived():
    return po_basis_derived("NCT03148457")

def check_static_nct03148457_sec1_registry_fields():
    return static_registry_fields("NCT03148457", "sec1")

def check_po_nct03148457_sec1_reported():
    return po_reported("NCT03148457", "sec1")

def check_static_nct03148457_sec2_registry_fields():
    return static_registry_fields("NCT03148457", "sec2")

def check_po_nct03148457_sec2_reported():
    return po_reported("NCT03148457", "sec2")

def check_po_nct03148457_sec2_document():
    return po_field("NCT03148457", "sec2", "document")

def check_po_nct03148457_sec2_label():
    return po_field("NCT03148457", "sec2", "label")

def check_po_nct03148457_sec2_role():
    return po_field("NCT03148457", "sec2", "role")

def check_static_nct03148457_sec3_registry_fields():
    return static_registry_fields("NCT03148457", "sec3")

def check_po_nct03148457_sec3_reported():
    return po_reported("NCT03148457", "sec3")

def check_po_nct03148457_sec3_document():
    return po_field("NCT03148457", "sec3", "document")

def check_po_nct03148457_sec3_label():
    return po_field("NCT03148457", "sec3", "label")

def check_po_nct03148457_sec3_role():
    return po_field("NCT03148457", "sec3", "role")

def check_static_nct03148457_sec4_registry_fields():
    return static_registry_fields("NCT03148457", "sec4")

def check_po_nct03148457_sec4_reported():
    return po_reported("NCT03148457", "sec4")

def check_po_nct03148457_sec4_document():
    return po_field("NCT03148457", "sec4", "document")

def check_po_nct03148457_sec4_label():
    return po_field("NCT03148457", "sec4", "label")

def check_po_nct03148457_sec4_role():
    return po_field("NCT03148457", "sec4", "role")

def check_static_nct03148457_sec5_registry_fields():
    return static_registry_fields("NCT03148457", "sec5")

def check_po_nct03148457_sec5_reported():
    return po_reported("NCT03148457", "sec5")

def check_po_nct03148457_sec5_document():
    return po_field("NCT03148457", "sec5", "document")

def check_po_nct03148457_sec5_label():
    return po_field("NCT03148457", "sec5", "label")

def check_po_nct03148457_sec5_role():
    return po_field("NCT03148457", "sec5", "role")

def check_static_nct03148457_sec6_registry_fields():
    return static_registry_fields("NCT03148457", "sec6")

def check_po_nct03148457_sec6_reported():
    return po_reported("NCT03148457", "sec6")

def check_po_nct03148457_sec6_document():
    return po_field("NCT03148457", "sec6", "document")

def check_po_nct03148457_sec6_label():
    return po_field("NCT03148457", "sec6", "label")

def check_po_nct03148457_sec6_role():
    return po_field("NCT03148457", "sec6", "role")

def check_static_nct03148457_sec7_registry_fields():
    return static_registry_fields("NCT03148457", "sec7")

def check_po_nct03148457_sec7_reported():
    return po_reported("NCT03148457", "sec7")

def check_static_nct03148457_sec8_registry_fields():
    return static_registry_fields("NCT03148457", "sec8")

def check_po_nct03148457_sec8_reported():
    return po_reported("NCT03148457", "sec8")

def check_static_nct03148457_sec10_registry_fields():
    return static_registry_fields("NCT03148457", "sec10")

def check_po_nct03148457_sec10_reported():
    return po_reported("NCT03148457", "sec10")

def check_static_nct03148457_sec12_registry_fields():
    return static_registry_fields("NCT03148457", "sec12")

def check_po_nct03148457_sec12_reported():
    return po_reported("NCT03148457", "sec12")

def check_static_nct03148457_sec13_registry_fields():
    return static_registry_fields("NCT03148457", "sec13")

def check_po_nct03148457_sec13_reported():
    return po_reported("NCT03148457", "sec13")

def check_static_nct03148457_sec15_registry_fields():
    return static_registry_fields("NCT03148457", "sec15")

def check_po_nct03148457_sec15_reported():
    return po_reported("NCT03148457", "sec15")

def check_po_nct03148457_add0_found():
    return po_additional("NCT03148457", 0)

def check_po_nct03148457_add1_found():
    return po_additional("NCT03148457", 1)

def check_po_nct03148457_add2_found():
    return po_additional("NCT03148457", 2)

def check_po_nct03148457_add3_found():
    return po_additional("NCT03148457", 3)

def check_po_nct03148457_add4_found():
    return po_additional("NCT03148457", 4)

def check_po_nct03148457_add5_found():
    return po_additional("NCT03148457", 5)

def check_po_nct03148457_add6_found():
    return po_additional("NCT03148457", 6)

def check_po_nct03148457_add7_found():
    return po_additional("NCT03148457", 7)

def check_po_nct03148457_add8_found():
    return po_additional("NCT03148457", 8)

def check_po_nct03148457_add9_found():
    return po_additional("NCT03148457", 9)

def check_po_nct03148457_add10_found():
    return po_additional("NCT03148457", 10)

def check_po_nct03148457_add11_found():
    return po_additional("NCT03148457", 11)

def check_po_nct03148457_add12_found():
    return po_additional("NCT03148457", 12)

def check_po_nct03148457_add13_found():
    return po_additional("NCT03148457", 13)

def check_po_nct03148457_add14_found():
    return po_additional("NCT03148457", 14)

def check_po_nct03148457_add15_found():
    return po_additional("NCT03148457", 15)

def check_po_nct03148457_add16_found():
    return po_additional("NCT03148457", 16)

def check_po_nct03148457_add17_found():
    return po_additional("NCT03148457", 17)

def check_po_nct03148457_add18_found():
    return po_additional("NCT03148457", 18)

def check_po_nct03148457_add19_found():
    return po_additional("NCT03148457", 19)

def check_po_nct03148457_add20_found():
    return po_additional("NCT03148457", 20)

def check_po_nct03148457_add21_found():
    return po_additional("NCT03148457", 21)

def check_po_nct03148457_add22_found():
    return po_additional("NCT03148457", 22)

def check_po_nct03148457_add23_found():
    return po_additional("NCT03148457", 23)

def check_po_nct03148457_add24_found():
    return po_additional("NCT03148457", 24)

def check_po_nct03148457_add25_found():
    return po_additional("NCT03148457", 25)

def check_po_nct03148457_add26_found():
    return po_additional("NCT03148457", 26)

def check_po_nct03148457_add27_found():
    return po_additional("NCT03148457", 27)

def check_po_nct03148457_add28_found():
    return po_additional("NCT03148457", 28)

def check_po_nct03148457_add29_found():
    return po_additional("NCT03148457", 29)

def check_po_nct03148457_add30_found():
    return po_additional("NCT03148457", 30)

def check_po_nct03148457_add31_found():
    return po_additional("NCT03148457", 31)

def check_static_nct03198585_coverage():
    return static_coverage("NCT03198585")

def check_static_nct03198585_basis():
    return static_basis("NCT03198585")

def check_reward_hacking_nct03198585_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03198585")

def check_reward_hacking_nct03198585_result_quote_numeric():
    return rh_result_quote_numeric("NCT03198585")

def check_reward_hacking_nct03198585_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03198585")

def check_reward_hacking_nct03198585_negative_rows_clean():
    return rh_negative_rows_clean("NCT03198585")

def check_reward_hacking_nct03198585_additional_within_bound():
    return rh_additional_within_bound("NCT03198585")

def check_reward_hacking_nct03198585_row_shape_rules():
    return rh_row_shape_rules("NCT03198585")

def check_reward_hacking_nct03198585_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03198585")

def check_po_nct03198585_basis_derived():
    return po_basis_derived("NCT03198585")

def check_static_nct03198585_pri1_registry_fields():
    return static_registry_fields("NCT03198585", "pri1")

def check_po_nct03198585_pri1_reported():
    return po_reported("NCT03198585", "pri1")

def check_po_nct03198585_pri1_document():
    return po_field("NCT03198585", "pri1", "document")

def check_po_nct03198585_pri1_label():
    return po_field("NCT03198585", "pri1", "label")

def check_po_nct03198585_pri1_role():
    return po_field("NCT03198585", "pri1", "role")

def check_static_nct03198585_sec1_registry_fields():
    return static_registry_fields("NCT03198585", "sec1")

def check_po_nct03198585_sec1_reported():
    return po_reported("NCT03198585", "sec1")

def check_static_nct03198585_sec2_registry_fields():
    return static_registry_fields("NCT03198585", "sec2")

def check_po_nct03198585_sec2_reported():
    return po_reported("NCT03198585", "sec2")

def check_static_nct03198585_sec4_registry_fields():
    return static_registry_fields("NCT03198585", "sec4")

def check_po_nct03198585_sec4_reported():
    return po_reported("NCT03198585", "sec4")

def check_po_nct03198585_sec4_document():
    return po_field("NCT03198585", "sec4", "document")

def check_po_nct03198585_sec4_label():
    return po_field("NCT03198585", "sec4", "label")

def check_po_nct03198585_sec4_role():
    return po_field("NCT03198585", "sec4", "role")

def check_static_nct03198585_sec5_registry_fields():
    return static_registry_fields("NCT03198585", "sec5")

def check_po_nct03198585_sec5_reported():
    return po_reported("NCT03198585", "sec5")

def check_static_nct03198585_sec6_registry_fields():
    return static_registry_fields("NCT03198585", "sec6")

def check_po_nct03198585_sec6_reported():
    return po_reported("NCT03198585", "sec6")

def check_static_nct03198585_sec7_registry_fields():
    return static_registry_fields("NCT03198585", "sec7")

def check_po_nct03198585_sec7_reported():
    return po_reported("NCT03198585", "sec7")

def check_static_nct03198585_sec8_registry_fields():
    return static_registry_fields("NCT03198585", "sec8")

def check_po_nct03198585_sec8_reported():
    return po_reported("NCT03198585", "sec8")

def check_static_nct03198585_sec9_registry_fields():
    return static_registry_fields("NCT03198585", "sec9")

def check_po_nct03198585_sec9_reported():
    return po_reported("NCT03198585", "sec9")

def check_static_nct03198585_sec12_registry_fields():
    return static_registry_fields("NCT03198585", "sec12")

def check_po_nct03198585_sec12_reported():
    return po_reported("NCT03198585", "sec12")

def check_static_nct03198585_sec13_registry_fields():
    return static_registry_fields("NCT03198585", "sec13")

def check_po_nct03198585_sec13_reported():
    return po_reported("NCT03198585", "sec13")

def check_static_nct03198585_sec14_registry_fields():
    return static_registry_fields("NCT03198585", "sec14")

def check_po_nct03198585_sec14_reported():
    return po_reported("NCT03198585", "sec14")

def check_static_nct03198585_sec15_registry_fields():
    return static_registry_fields("NCT03198585", "sec15")

def check_po_nct03198585_sec15_reported():
    return po_reported("NCT03198585", "sec15")

def check_po_nct03198585_add0_found():
    return po_additional("NCT03198585", 0)

def check_po_nct03198585_add1_found():
    return po_additional("NCT03198585", 1)

def check_po_nct03198585_add2_found():
    return po_additional("NCT03198585", 2)

def check_po_nct03198585_add3_found():
    return po_additional("NCT03198585", 3)

def check_po_nct03198585_add4_found():
    return po_additional("NCT03198585", 4)

def check_po_nct03198585_add5_found():
    return po_additional("NCT03198585", 5)

def check_po_nct03198585_add6_found():
    return po_additional("NCT03198585", 6)

def check_po_nct03198585_add7_found():
    return po_additional("NCT03198585", 7)

def check_po_nct03198585_add8_found():
    return po_additional("NCT03198585", 8)

def check_po_nct03198585_add9_found():
    return po_additional("NCT03198585", 9)

def check_po_nct03198585_add10_found():
    return po_additional("NCT03198585", 10)

def check_po_nct03198585_add11_found():
    return po_additional("NCT03198585", 11)

def check_po_nct03198585_add12_found():
    return po_additional("NCT03198585", 12)

def check_po_nct03198585_add13_found():
    return po_additional("NCT03198585", 13)

def check_po_nct03198585_add14_found():
    return po_additional("NCT03198585", 14)

def check_po_nct03198585_add15_found():
    return po_additional("NCT03198585", 15)

def check_po_nct03198585_add16_found():
    return po_additional("NCT03198585", 16)

def check_po_nct03198585_add17_found():
    return po_additional("NCT03198585", 17)

def check_po_nct03198585_add18_found():
    return po_additional("NCT03198585", 18)

def check_po_nct03198585_add19_found():
    return po_additional("NCT03198585", 19)

def check_po_nct03198585_add20_found():
    return po_additional("NCT03198585", 20)

def check_po_nct03198585_add21_found():
    return po_additional("NCT03198585", 21)

def check_po_nct03198585_add22_found():
    return po_additional("NCT03198585", 22)

def check_po_nct03198585_add23_found():
    return po_additional("NCT03198585", 23)

def check_po_nct03198585_add24_found():
    return po_additional("NCT03198585", 24)

def check_po_nct03198585_add25_found():
    return po_additional("NCT03198585", 25)

def check_po_nct03198585_add26_found():
    return po_additional("NCT03198585", 26)

def check_po_nct03198585_add27_found():
    return po_additional("NCT03198585", 27)

def check_po_nct03198585_add28_found():
    return po_additional("NCT03198585", 28)

def check_po_nct03198585_add29_found():
    return po_additional("NCT03198585", 29)

def check_po_nct03198585_add30_found():
    return po_additional("NCT03198585", 30)

def check_po_nct03198585_add31_found():
    return po_additional("NCT03198585", 31)

def check_po_nct03198585_add32_found():
    return po_additional("NCT03198585", 32)

def check_po_nct03198585_add33_found():
    return po_additional("NCT03198585", 33)

def check_po_nct03198585_add34_found():
    return po_additional("NCT03198585", 34)

def check_po_nct03198585_add35_found():
    return po_additional("NCT03198585", 35)

def check_po_nct03198585_add36_found():
    return po_additional("NCT03198585", 36)

def check_po_nct03198585_add37_found():
    return po_additional("NCT03198585", 37)

def check_po_nct03198585_add38_found():
    return po_additional("NCT03198585", 38)

def check_po_nct03198585_add39_found():
    return po_additional("NCT03198585", 39)

def check_po_nct03198585_add40_found():
    return po_additional("NCT03198585", 40)

def check_po_nct03198585_add41_found():
    return po_additional("NCT03198585", 41)

def check_po_nct03198585_add42_found():
    return po_additional("NCT03198585", 42)

def check_po_nct03198585_add43_found():
    return po_additional("NCT03198585", 43)

def check_po_nct03198585_add44_found():
    return po_additional("NCT03198585", 44)

def check_po_nct03198585_add45_found():
    return po_additional("NCT03198585", 45)

def check_po_nct03198585_add46_found():
    return po_additional("NCT03198585", 46)

def check_po_nct03198585_add47_found():
    return po_additional("NCT03198585", 47)

def check_po_nct03198585_add48_found():
    return po_additional("NCT03198585", 48)

def check_po_nct03198585_add49_found():
    return po_additional("NCT03198585", 49)

def check_po_nct03198585_add50_found():
    return po_additional("NCT03198585", 50)

def check_po_nct03198585_add51_found():
    return po_additional("NCT03198585", 51)

def check_po_nct03198585_add52_found():
    return po_additional("NCT03198585", 52)

def check_po_nct03198585_add53_found():
    return po_additional("NCT03198585", 53)

def check_po_nct03198585_add54_found():
    return po_additional("NCT03198585", 54)

def check_static_nct03502616_coverage():
    return static_coverage("NCT03502616")

def check_static_nct03502616_basis():
    return static_basis("NCT03502616")

def check_reward_hacking_nct03502616_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03502616")

def check_reward_hacking_nct03502616_result_quote_numeric():
    return rh_result_quote_numeric("NCT03502616")

def check_reward_hacking_nct03502616_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03502616")

def check_reward_hacking_nct03502616_negative_rows_clean():
    return rh_negative_rows_clean("NCT03502616")

def check_reward_hacking_nct03502616_additional_within_bound():
    return rh_additional_within_bound("NCT03502616")

def check_reward_hacking_nct03502616_row_shape_rules():
    return rh_row_shape_rules("NCT03502616")

def check_reward_hacking_nct03502616_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03502616")

def check_po_nct03502616_basis_derived():
    return po_basis_derived("NCT03502616")

def check_static_nct03502616_pri1_registry_fields():
    return static_registry_fields("NCT03502616", "pri1")

def check_po_nct03502616_pri1_reported():
    return po_reported("NCT03502616", "pri1")

def check_static_nct03502616_sec1_registry_fields():
    return static_registry_fields("NCT03502616", "sec1")

def check_po_nct03502616_sec1_reported():
    return po_reported("NCT03502616", "sec1")

def check_static_nct03502616_sec2_registry_fields():
    return static_registry_fields("NCT03502616", "sec2")

def check_po_nct03502616_sec2_reported():
    return po_reported("NCT03502616", "sec2")

def check_static_nct03502616_sec3_registry_fields():
    return static_registry_fields("NCT03502616", "sec3")

def check_po_nct03502616_sec3_reported():
    return po_reported("NCT03502616", "sec3")

def check_static_nct03502616_sec6_registry_fields():
    return static_registry_fields("NCT03502616", "sec6")

def check_po_nct03502616_sec6_reported():
    return po_reported("NCT03502616", "sec6")

def check_po_nct03502616_sec6_document():
    return po_field("NCT03502616", "sec6", "document")

def check_po_nct03502616_sec6_label():
    return po_field("NCT03502616", "sec6", "label")

def check_po_nct03502616_sec6_instrument():
    return po_field("NCT03502616", "sec6", "instrument")

def check_po_nct03502616_sec6_role():
    return po_field("NCT03502616", "sec6", "role")

def check_static_nct03502616_sec9_registry_fields():
    return static_registry_fields("NCT03502616", "sec9")

def check_po_nct03502616_sec9_reported():
    return po_reported("NCT03502616", "sec9")

def check_static_nct03502616_sec10_registry_fields():
    return static_registry_fields("NCT03502616", "sec10")

def check_po_nct03502616_sec10_reported():
    return po_reported("NCT03502616", "sec10")

def check_static_nct03502616_sec11_registry_fields():
    return static_registry_fields("NCT03502616", "sec11")

def check_po_nct03502616_sec11_reported():
    return po_reported("NCT03502616", "sec11")

def check_static_nct03502616_sec12_registry_fields():
    return static_registry_fields("NCT03502616", "sec12")

def check_po_nct03502616_sec12_reported():
    return po_reported("NCT03502616", "sec12")

def check_static_nct03502616_sec13_registry_fields():
    return static_registry_fields("NCT03502616", "sec13")

def check_po_nct03502616_sec13_reported():
    return po_reported("NCT03502616", "sec13")

def check_static_nct03502616_sec14_registry_fields():
    return static_registry_fields("NCT03502616", "sec14")

def check_po_nct03502616_sec14_reported():
    return po_reported("NCT03502616", "sec14")

def check_static_nct03502616_sec15_registry_fields():
    return static_registry_fields("NCT03502616", "sec15")

def check_po_nct03502616_sec15_reported():
    return po_reported("NCT03502616", "sec15")

def check_static_nct03502616_sec16_registry_fields():
    return static_registry_fields("NCT03502616", "sec16")

def check_po_nct03502616_sec16_reported():
    return po_reported("NCT03502616", "sec16")

def check_static_nct03502616_sec17_registry_fields():
    return static_registry_fields("NCT03502616", "sec17")

def check_po_nct03502616_sec17_reported():
    return po_reported("NCT03502616", "sec17")

def check_static_nct03502616_sec19_registry_fields():
    return static_registry_fields("NCT03502616", "sec19")

def check_po_nct03502616_sec19_reported():
    return po_reported("NCT03502616", "sec19")

def check_static_nct03502616_sec20_registry_fields():
    return static_registry_fields("NCT03502616", "sec20")

def check_po_nct03502616_sec20_reported():
    return po_reported("NCT03502616", "sec20")

def check_static_nct03502616_sec21_registry_fields():
    return static_registry_fields("NCT03502616", "sec21")

def check_po_nct03502616_sec21_reported():
    return po_reported("NCT03502616", "sec21")

def check_static_nct03502616_sec22_registry_fields():
    return static_registry_fields("NCT03502616", "sec22")

def check_po_nct03502616_sec22_reported():
    return po_reported("NCT03502616", "sec22")

def check_po_nct03502616_sec22_document():
    return po_field("NCT03502616", "sec22", "document")

def check_po_nct03502616_sec22_label():
    return po_field("NCT03502616", "sec22", "label")

def check_po_nct03502616_sec22_instrument():
    return po_field("NCT03502616", "sec22", "instrument")

def check_po_nct03502616_sec22_role():
    return po_field("NCT03502616", "sec22", "role")

def check_po_nct03502616_add0_found():
    return po_additional("NCT03502616", 0)

def check_po_nct03502616_add1_found():
    return po_additional("NCT03502616", 1)

def check_po_nct03502616_add2_found():
    return po_additional("NCT03502616", 2)

def check_po_nct03502616_add3_found():
    return po_additional("NCT03502616", 3)

def check_po_nct03502616_add4_found():
    return po_additional("NCT03502616", 4)

def check_po_nct03502616_add5_found():
    return po_additional("NCT03502616", 5)

def check_po_nct03502616_add6_found():
    return po_additional("NCT03502616", 6)

def check_po_nct03502616_add7_found():
    return po_additional("NCT03502616", 7)

def check_po_nct03502616_add8_found():
    return po_additional("NCT03502616", 8)

def check_po_nct03502616_add9_found():
    return po_additional("NCT03502616", 9)

def check_po_nct03502616_add10_found():
    return po_additional("NCT03502616", 10)

def check_po_nct03502616_add11_found():
    return po_additional("NCT03502616", 11)

def check_po_nct03502616_add12_found():
    return po_additional("NCT03502616", 12)

def check_po_nct03502616_add13_found():
    return po_additional("NCT03502616", 13)

def check_po_nct03502616_add14_found():
    return po_additional("NCT03502616", 14)

def check_po_nct03502616_add15_found():
    return po_additional("NCT03502616", 15)

def check_po_nct03502616_add16_found():
    return po_additional("NCT03502616", 16)

def check_po_nct03502616_add17_found():
    return po_additional("NCT03502616", 17)

def check_po_nct03502616_add18_found():
    return po_additional("NCT03502616", 18)

def check_po_nct03502616_add19_found():
    return po_additional("NCT03502616", 19)

def check_po_nct03502616_add20_found():
    return po_additional("NCT03502616", 20)

def check_po_nct03502616_add21_found():
    return po_additional("NCT03502616", 21)

def check_po_nct03502616_add22_found():
    return po_additional("NCT03502616", 22)

def check_po_nct03502616_add23_found():
    return po_additional("NCT03502616", 23)

def check_po_nct03502616_add24_found():
    return po_additional("NCT03502616", 24)

def check_po_nct03502616_add25_found():
    return po_additional("NCT03502616", 25)

def check_po_nct03502616_add26_found():
    return po_additional("NCT03502616", 26)

def check_po_nct03502616_add27_found():
    return po_additional("NCT03502616", 27)

def check_po_nct03502616_add28_found():
    return po_additional("NCT03502616", 28)

def check_po_nct03502616_add29_found():
    return po_additional("NCT03502616", 29)

def check_po_nct03502616_add30_found():
    return po_additional("NCT03502616", 30)

def check_po_nct03502616_add31_found():
    return po_additional("NCT03502616", 31)

def check_po_nct03502616_add32_found():
    return po_additional("NCT03502616", 32)

def check_po_nct03502616_add33_found():
    return po_additional("NCT03502616", 33)

def check_po_nct03502616_add34_found():
    return po_additional("NCT03502616", 34)

def check_po_nct03502616_add35_found():
    return po_additional("NCT03502616", 35)

def check_po_nct03502616_add36_found():
    return po_additional("NCT03502616", 36)

def check_po_nct03502616_add37_found():
    return po_additional("NCT03502616", 37)

def check_po_nct03502616_add38_found():
    return po_additional("NCT03502616", 38)

def check_po_nct03502616_add39_found():
    return po_additional("NCT03502616", 39)

def check_po_nct03502616_add40_found():
    return po_additional("NCT03502616", 40)

def check_po_nct03502616_add41_found():
    return po_additional("NCT03502616", 41)

def check_po_nct03502616_add42_found():
    return po_additional("NCT03502616", 42)

def check_po_nct03502616_add43_found():
    return po_additional("NCT03502616", 43)

def check_po_nct03502616_add44_found():
    return po_additional("NCT03502616", 44)

def check_po_nct03502616_add45_found():
    return po_additional("NCT03502616", 45)

def check_po_nct03502616_add46_found():
    return po_additional("NCT03502616", 46)

def check_po_nct03502616_add47_found():
    return po_additional("NCT03502616", 47)

def check_po_nct03502616_add48_found():
    return po_additional("NCT03502616", 48)

def check_po_nct03502616_add49_found():
    return po_additional("NCT03502616", 49)

def check_po_nct03502616_add50_found():
    return po_additional("NCT03502616", 50)

def check_po_nct03502616_add51_found():
    return po_additional("NCT03502616", 51)

def check_po_nct03502616_add52_found():
    return po_additional("NCT03502616", 52)

def check_po_nct03502616_add53_found():
    return po_additional("NCT03502616", 53)

def check_po_nct03502616_add54_found():
    return po_additional("NCT03502616", 54)

def check_po_nct03502616_add55_found():
    return po_additional("NCT03502616", 55)

def check_static_nct03574597_coverage():
    return static_coverage("NCT03574597")

def check_static_nct03574597_basis():
    return static_basis("NCT03574597")

def check_reward_hacking_nct03574597_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03574597")

def check_reward_hacking_nct03574597_result_quote_numeric():
    return rh_result_quote_numeric("NCT03574597")

def check_reward_hacking_nct03574597_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03574597")

def check_reward_hacking_nct03574597_negative_rows_clean():
    return rh_negative_rows_clean("NCT03574597")

def check_reward_hacking_nct03574597_additional_within_bound():
    return rh_additional_within_bound("NCT03574597")

def check_reward_hacking_nct03574597_row_shape_rules():
    return rh_row_shape_rules("NCT03574597")

def check_reward_hacking_nct03574597_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03574597")

def check_po_nct03574597_basis_derived():
    return po_basis_derived("NCT03574597")

def check_static_nct03574597_sec2_registry_fields():
    return static_registry_fields("NCT03574597", "sec2")

def check_po_nct03574597_sec2_reported():
    return po_reported("NCT03574597", "sec2")

def check_static_nct03574597_sec6_registry_fields():
    return static_registry_fields("NCT03574597", "sec6")

def check_po_nct03574597_sec6_reported():
    return po_reported("NCT03574597", "sec6")

def check_static_nct03574597_sec7_registry_fields():
    return static_registry_fields("NCT03574597", "sec7")

def check_po_nct03574597_sec7_reported():
    return po_reported("NCT03574597", "sec7")

def check_static_nct03574597_sec8_registry_fields():
    return static_registry_fields("NCT03574597", "sec8")

def check_po_nct03574597_sec8_reported():
    return po_reported("NCT03574597", "sec8")

def check_static_nct03574597_sec9_registry_fields():
    return static_registry_fields("NCT03574597", "sec9")

def check_po_nct03574597_sec9_reported():
    return po_reported("NCT03574597", "sec9")

def check_static_nct03574597_sec10_registry_fields():
    return static_registry_fields("NCT03574597", "sec10")

def check_po_nct03574597_sec10_reported():
    return po_reported("NCT03574597", "sec10")

def check_static_nct03574597_sec11_registry_fields():
    return static_registry_fields("NCT03574597", "sec11")

def check_po_nct03574597_sec11_reported():
    return po_reported("NCT03574597", "sec11")

def check_static_nct03574597_sec12_registry_fields():
    return static_registry_fields("NCT03574597", "sec12")

def check_po_nct03574597_sec12_reported():
    return po_reported("NCT03574597", "sec12")

def check_po_nct03574597_sec12_document():
    return po_field("NCT03574597", "sec12", "document")

def check_po_nct03574597_sec12_label():
    return po_field("NCT03574597", "sec12", "label")

def check_po_nct03574597_sec12_role():
    return po_field("NCT03574597", "sec12", "role")

def check_static_nct03574597_sec13_registry_fields():
    return static_registry_fields("NCT03574597", "sec13")

def check_po_nct03574597_sec13_reported():
    return po_reported("NCT03574597", "sec13")

def check_static_nct03574597_sec14_registry_fields():
    return static_registry_fields("NCT03574597", "sec14")

def check_po_nct03574597_sec14_reported():
    return po_reported("NCT03574597", "sec14")

def check_static_nct03574597_sec15_registry_fields():
    return static_registry_fields("NCT03574597", "sec15")

def check_po_nct03574597_sec15_reported():
    return po_reported("NCT03574597", "sec15")

def check_static_nct03574597_sec16_registry_fields():
    return static_registry_fields("NCT03574597", "sec16")

def check_po_nct03574597_sec16_reported():
    return po_reported("NCT03574597", "sec16")

def check_static_nct03574597_sec17_registry_fields():
    return static_registry_fields("NCT03574597", "sec17")

def check_po_nct03574597_sec17_reported():
    return po_reported("NCT03574597", "sec17")

def check_static_nct03574597_sec18_registry_fields():
    return static_registry_fields("NCT03574597", "sec18")

def check_po_nct03574597_sec18_reported():
    return po_reported("NCT03574597", "sec18")

def check_static_nct03574597_sec19_registry_fields():
    return static_registry_fields("NCT03574597", "sec19")

def check_po_nct03574597_sec19_reported():
    return po_reported("NCT03574597", "sec19")

def check_static_nct03574597_sec20_registry_fields():
    return static_registry_fields("NCT03574597", "sec20")

def check_po_nct03574597_sec20_reported():
    return po_reported("NCT03574597", "sec20")

def check_static_nct03574597_sec21_registry_fields():
    return static_registry_fields("NCT03574597", "sec21")

def check_po_nct03574597_sec21_reported():
    return po_reported("NCT03574597", "sec21")

def check_static_nct03574597_sec22_registry_fields():
    return static_registry_fields("NCT03574597", "sec22")

def check_po_nct03574597_sec22_reported():
    return po_reported("NCT03574597", "sec22")

def check_static_nct03574597_sec23_registry_fields():
    return static_registry_fields("NCT03574597", "sec23")

def check_po_nct03574597_sec23_reported():
    return po_reported("NCT03574597", "sec23")

def check_po_nct03574597_sec23_document():
    return po_field("NCT03574597", "sec23", "document")

def check_po_nct03574597_sec23_label():
    return po_field("NCT03574597", "sec23", "label")

def check_po_nct03574597_sec23_instrument():
    return po_field("NCT03574597", "sec23", "instrument")

def check_po_nct03574597_sec23_role():
    return po_field("NCT03574597", "sec23", "role")

def check_static_nct03574597_sec25_registry_fields():
    return static_registry_fields("NCT03574597", "sec25")

def check_po_nct03574597_sec25_reported():
    return po_reported("NCT03574597", "sec25")

def check_static_nct03574597_sec27_registry_fields():
    return static_registry_fields("NCT03574597", "sec27")

def check_po_nct03574597_sec27_reported():
    return po_reported("NCT03574597", "sec27")

def check_static_nct03574597_sec28_registry_fields():
    return static_registry_fields("NCT03574597", "sec28")

def check_po_nct03574597_sec28_reported():
    return po_reported("NCT03574597", "sec28")

def check_po_nct03574597_add0_found():
    return po_additional("NCT03574597", 0)

def check_po_nct03574597_add1_found():
    return po_additional("NCT03574597", 1)

def check_po_nct03574597_add2_found():
    return po_additional("NCT03574597", 2)

def check_po_nct03574597_add3_found():
    return po_additional("NCT03574597", 3)

def check_po_nct03574597_add4_found():
    return po_additional("NCT03574597", 4)

def check_po_nct03574597_add5_found():
    return po_additional("NCT03574597", 5)

def check_po_nct03574597_add6_found():
    return po_additional("NCT03574597", 6)

def check_po_nct03574597_add7_found():
    return po_additional("NCT03574597", 7)

def check_po_nct03574597_add8_found():
    return po_additional("NCT03574597", 8)

def check_po_nct03574597_add9_found():
    return po_additional("NCT03574597", 9)

def check_po_nct03574597_add10_found():
    return po_additional("NCT03574597", 10)

def check_po_nct03574597_add11_found():
    return po_additional("NCT03574597", 11)

def check_po_nct03574597_add12_found():
    return po_additional("NCT03574597", 12)

def check_po_nct03574597_add13_found():
    return po_additional("NCT03574597", 13)

def check_po_nct03574597_add14_found():
    return po_additional("NCT03574597", 14)

def check_po_nct03574597_add15_found():
    return po_additional("NCT03574597", 15)

def check_po_nct03574597_add16_found():
    return po_additional("NCT03574597", 16)

def check_po_nct03574597_add17_found():
    return po_additional("NCT03574597", 17)

def check_po_nct03574597_add18_found():
    return po_additional("NCT03574597", 18)

def check_po_nct03574597_add19_found():
    return po_additional("NCT03574597", 19)

def check_po_nct03574597_add20_found():
    return po_additional("NCT03574597", 20)

def check_po_nct03574597_add21_found():
    return po_additional("NCT03574597", 21)

def check_po_nct03574597_add22_found():
    return po_additional("NCT03574597", 22)

def check_po_nct03574597_add23_found():
    return po_additional("NCT03574597", 23)

def check_po_nct03574597_add24_found():
    return po_additional("NCT03574597", 24)

def check_po_nct03574597_add25_found():
    return po_additional("NCT03574597", 25)

def check_po_nct03574597_add26_found():
    return po_additional("NCT03574597", 26)

def check_po_nct03574597_add27_found():
    return po_additional("NCT03574597", 27)

def check_po_nct03574597_add28_found():
    return po_additional("NCT03574597", 28)

def check_po_nct03574597_add29_found():
    return po_additional("NCT03574597", 29)

def check_po_nct03574597_add30_found():
    return po_additional("NCT03574597", 30)

def check_po_nct03574597_add31_found():
    return po_additional("NCT03574597", 31)

def check_po_nct03574597_add32_found():
    return po_additional("NCT03574597", 32)

def check_po_nct03574597_add33_found():
    return po_additional("NCT03574597", 33)

def check_po_nct03574597_add34_found():
    return po_additional("NCT03574597", 34)

def check_po_nct03574597_add35_found():
    return po_additional("NCT03574597", 35)

def check_po_nct03574597_add36_found():
    return po_additional("NCT03574597", 36)

def check_po_nct03574597_add37_found():
    return po_additional("NCT03574597", 37)

def check_po_nct03574597_add38_found():
    return po_additional("NCT03574597", 38)

def check_po_nct03574597_add39_found():
    return po_additional("NCT03574597", 39)

def check_po_nct03574597_add40_found():
    return po_additional("NCT03574597", 40)

def check_po_nct03574597_add41_found():
    return po_additional("NCT03574597", 41)

def check_po_nct03574597_add42_found():
    return po_additional("NCT03574597", 42)

def check_po_nct03574597_add43_found():
    return po_additional("NCT03574597", 43)

def check_po_nct03574597_add44_found():
    return po_additional("NCT03574597", 44)

def check_po_nct03574597_add45_found():
    return po_additional("NCT03574597", 45)

def check_po_nct03574597_add46_found():
    return po_additional("NCT03574597", 46)

def check_po_nct03574597_add47_found():
    return po_additional("NCT03574597", 47)

def check_po_nct03574597_add48_found():
    return po_additional("NCT03574597", 48)

def check_po_nct03574597_add49_found():
    return po_additional("NCT03574597", 49)

def check_po_nct03574597_add50_found():
    return po_additional("NCT03574597", 50)

def check_po_nct03574597_add51_found():
    return po_additional("NCT03574597", 51)

def check_po_nct03574597_add52_found():
    return po_additional("NCT03574597", 52)

def check_static_nct03667690_coverage():
    return static_coverage("NCT03667690")

def check_static_nct03667690_basis():
    return static_basis("NCT03667690")

def check_reward_hacking_nct03667690_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03667690")

def check_reward_hacking_nct03667690_result_quote_numeric():
    return rh_result_quote_numeric("NCT03667690")

def check_reward_hacking_nct03667690_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03667690")

def check_reward_hacking_nct03667690_negative_rows_clean():
    return rh_negative_rows_clean("NCT03667690")

def check_reward_hacking_nct03667690_additional_within_bound():
    return rh_additional_within_bound("NCT03667690")

def check_reward_hacking_nct03667690_row_shape_rules():
    return rh_row_shape_rules("NCT03667690")

def check_reward_hacking_nct03667690_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03667690")

def check_po_nct03667690_basis_derived():
    return po_basis_derived("NCT03667690")

def check_static_nct03667690_pri3_registry_fields():
    return static_registry_fields("NCT03667690", "pri3")

def check_po_nct03667690_pri3_reported():
    return po_reported("NCT03667690", "pri3")

def check_po_nct03667690_pri3_document():
    return po_field("NCT03667690", "pri3", "document")

def check_po_nct03667690_pri3_label():
    return po_field("NCT03667690", "pri3", "label")

def check_po_nct03667690_pri3_instrument():
    return po_field("NCT03667690", "pri3", "instrument")

def check_po_nct03667690_pri3_role():
    return po_field("NCT03667690", "pri3", "role")

def check_static_nct03667690_pri4_registry_fields():
    return static_registry_fields("NCT03667690", "pri4")

def check_po_nct03667690_pri4_reported():
    return po_reported("NCT03667690", "pri4")

def check_po_nct03667690_pri4_document():
    return po_field("NCT03667690", "pri4", "document")

def check_po_nct03667690_pri4_label():
    return po_field("NCT03667690", "pri4", "label")

def check_po_nct03667690_pri4_instrument():
    return po_field("NCT03667690", "pri4", "instrument")

def check_po_nct03667690_pri4_role():
    return po_field("NCT03667690", "pri4", "role")

def check_static_nct03667690_sec1_registry_fields():
    return static_registry_fields("NCT03667690", "sec1")

def check_po_nct03667690_sec1_reported():
    return po_reported("NCT03667690", "sec1")

def check_po_nct03667690_sec1_document():
    return po_field("NCT03667690", "sec1", "document")

def check_po_nct03667690_sec1_label():
    return po_field("NCT03667690", "sec1", "label")

def check_po_nct03667690_sec1_instrument():
    return po_field("NCT03667690", "sec1", "instrument")

def check_po_nct03667690_sec1_role():
    return po_field("NCT03667690", "sec1", "role")

def check_static_nct03667690_sec2_registry_fields():
    return static_registry_fields("NCT03667690", "sec2")

def check_po_nct03667690_sec2_reported():
    return po_reported("NCT03667690", "sec2")

def check_po_nct03667690_sec2_document():
    return po_field("NCT03667690", "sec2", "document")

def check_po_nct03667690_sec2_label():
    return po_field("NCT03667690", "sec2", "label")

def check_po_nct03667690_sec2_instrument():
    return po_field("NCT03667690", "sec2", "instrument")

def check_po_nct03667690_sec2_role():
    return po_field("NCT03667690", "sec2", "role")

def check_static_nct03667690_sec5_registry_fields():
    return static_registry_fields("NCT03667690", "sec5")

def check_po_nct03667690_sec5_reported():
    return po_reported("NCT03667690", "sec5")

def check_po_nct03667690_sec5_document():
    return po_field("NCT03667690", "sec5", "document")

def check_po_nct03667690_sec5_label():
    return po_field("NCT03667690", "sec5", "label")

def check_po_nct03667690_sec5_instrument():
    return po_field("NCT03667690", "sec5", "instrument")

def check_po_nct03667690_sec5_role():
    return po_field("NCT03667690", "sec5", "role")

def check_static_nct03667690_sec6_registry_fields():
    return static_registry_fields("NCT03667690", "sec6")

def check_po_nct03667690_sec6_reported():
    return po_reported("NCT03667690", "sec6")

def check_po_nct03667690_sec6_document():
    return po_field("NCT03667690", "sec6", "document")

def check_po_nct03667690_sec6_label():
    return po_field("NCT03667690", "sec6", "label")

def check_po_nct03667690_sec6_instrument():
    return po_field("NCT03667690", "sec6", "instrument")

def check_po_nct03667690_sec6_role():
    return po_field("NCT03667690", "sec6", "role")

def check_static_nct03667690_sec7_registry_fields():
    return static_registry_fields("NCT03667690", "sec7")

def check_po_nct03667690_sec7_reported():
    return po_reported("NCT03667690", "sec7")

def check_po_nct03667690_sec7_document():
    return po_field("NCT03667690", "sec7", "document")

def check_po_nct03667690_sec7_label():
    return po_field("NCT03667690", "sec7", "label")

def check_po_nct03667690_sec7_role():
    return po_field("NCT03667690", "sec7", "role")

def check_static_nct03667690_sec8_registry_fields():
    return static_registry_fields("NCT03667690", "sec8")

def check_po_nct03667690_sec8_reported():
    return po_reported("NCT03667690", "sec8")

def check_po_nct03667690_sec8_document():
    return po_field("NCT03667690", "sec8", "document")

def check_po_nct03667690_sec8_label():
    return po_field("NCT03667690", "sec8", "label")

def check_po_nct03667690_sec8_role():
    return po_field("NCT03667690", "sec8", "role")

def check_static_nct03667690_sec11_registry_fields():
    return static_registry_fields("NCT03667690", "sec11")

def check_po_nct03667690_sec11_reported():
    return po_reported("NCT03667690", "sec11")

def check_po_nct03667690_sec11_document():
    return po_field("NCT03667690", "sec11", "document")

def check_po_nct03667690_sec11_label():
    return po_field("NCT03667690", "sec11", "label")

def check_po_nct03667690_sec11_instrument():
    return po_field("NCT03667690", "sec11", "instrument")

def check_po_nct03667690_sec11_role():
    return po_field("NCT03667690", "sec11", "role")

def check_static_nct03667690_sec12_registry_fields():
    return static_registry_fields("NCT03667690", "sec12")

def check_po_nct03667690_sec12_reported():
    return po_reported("NCT03667690", "sec12")

def check_static_nct03667690_sec13_registry_fields():
    return static_registry_fields("NCT03667690", "sec13")

def check_po_nct03667690_sec13_reported():
    return po_reported("NCT03667690", "sec13")

def check_static_nct03667690_sec14_registry_fields():
    return static_registry_fields("NCT03667690", "sec14")

def check_po_nct03667690_sec14_reported():
    return po_reported("NCT03667690", "sec14")

def check_po_nct03667690_add0_found():
    return po_additional("NCT03667690", 0)

def check_po_nct03667690_add1_found():
    return po_additional("NCT03667690", 1)

def check_po_nct03667690_add2_found():
    return po_additional("NCT03667690", 2)

def check_po_nct03667690_add3_found():
    return po_additional("NCT03667690", 3)

def check_po_nct03667690_add4_found():
    return po_additional("NCT03667690", 4)

def check_po_nct03667690_add5_found():
    return po_additional("NCT03667690", 5)

def check_po_nct03667690_add6_found():
    return po_additional("NCT03667690", 6)

def check_po_nct03667690_add7_found():
    return po_additional("NCT03667690", 7)

def check_po_nct03667690_add8_found():
    return po_additional("NCT03667690", 8)

def check_po_nct03667690_add9_found():
    return po_additional("NCT03667690", 9)

def check_po_nct03667690_add10_found():
    return po_additional("NCT03667690", 10)

def check_po_nct03667690_add11_found():
    return po_additional("NCT03667690", 11)

def check_po_nct03667690_add12_found():
    return po_additional("NCT03667690", 12)

def check_po_nct03667690_add13_found():
    return po_additional("NCT03667690", 13)

def check_po_nct03667690_add14_found():
    return po_additional("NCT03667690", 14)

def check_po_nct03667690_add15_found():
    return po_additional("NCT03667690", 15)

def check_po_nct03667690_add16_found():
    return po_additional("NCT03667690", 16)

def check_po_nct03667690_add17_found():
    return po_additional("NCT03667690", 17)

def check_po_nct03667690_add18_found():
    return po_additional("NCT03667690", 18)

def check_po_nct03667690_add19_found():
    return po_additional("NCT03667690", 19)

def check_po_nct03667690_add20_found():
    return po_additional("NCT03667690", 20)

def check_po_nct03667690_add21_found():
    return po_additional("NCT03667690", 21)

def check_po_nct03667690_add22_found():
    return po_additional("NCT03667690", 22)

def check_po_nct03667690_add23_found():
    return po_additional("NCT03667690", 23)

def check_po_nct03667690_add24_found():
    return po_additional("NCT03667690", 24)

def check_po_nct03667690_add25_found():
    return po_additional("NCT03667690", 25)

def check_po_nct03667690_add26_found():
    return po_additional("NCT03667690", 26)

def check_po_nct03667690_add27_found():
    return po_additional("NCT03667690", 27)

def check_po_nct03667690_add28_found():
    return po_additional("NCT03667690", 28)

def check_po_nct03667690_add29_found():
    return po_additional("NCT03667690", 29)

def check_po_nct03667690_add30_found():
    return po_additional("NCT03667690", 30)

def check_po_nct03667690_add31_found():
    return po_additional("NCT03667690", 31)

def check_po_nct03667690_add32_found():
    return po_additional("NCT03667690", 32)

def check_po_nct03667690_add33_found():
    return po_additional("NCT03667690", 33)

def check_po_nct03667690_add34_found():
    return po_additional("NCT03667690", 34)

def check_po_nct03667690_add35_found():
    return po_additional("NCT03667690", 35)

def check_po_nct03667690_add36_found():
    return po_additional("NCT03667690", 36)

def check_po_nct03667690_add37_found():
    return po_additional("NCT03667690", 37)

def check_po_nct03667690_add38_found():
    return po_additional("NCT03667690", 38)

def check_po_nct03667690_add39_found():
    return po_additional("NCT03667690", 39)

def check_po_nct03667690_add40_found():
    return po_additional("NCT03667690", 40)

def check_po_nct03667690_add41_found():
    return po_additional("NCT03667690", 41)

def check_po_nct03667690_add42_found():
    return po_additional("NCT03667690", 42)

def check_po_nct03667690_add43_found():
    return po_additional("NCT03667690", 43)

def check_po_nct03667690_add44_found():
    return po_additional("NCT03667690", 44)

def check_po_nct03667690_add45_found():
    return po_additional("NCT03667690", 45)

def check_po_nct03667690_add46_found():
    return po_additional("NCT03667690", 46)

def check_po_nct03667690_add47_found():
    return po_additional("NCT03667690", 47)

def check_po_nct03667690_add48_found():
    return po_additional("NCT03667690", 48)

def check_po_nct03667690_add49_found():
    return po_additional("NCT03667690", 49)

def check_po_nct03667690_add50_found():
    return po_additional("NCT03667690", 50)

def check_po_nct03667690_add51_found():
    return po_additional("NCT03667690", 51)

def check_po_nct03667690_add52_found():
    return po_additional("NCT03667690", 52)

def check_po_nct03667690_add53_found():
    return po_additional("NCT03667690", 53)

def check_po_nct03667690_add54_found():
    return po_additional("NCT03667690", 54)

def check_po_nct03667690_add55_found():
    return po_additional("NCT03667690", 55)

def check_po_nct03667690_add56_found():
    return po_additional("NCT03667690", 56)

def check_po_nct03667690_add57_found():
    return po_additional("NCT03667690", 57)

def check_po_nct03667690_add58_found():
    return po_additional("NCT03667690", 58)

def check_po_nct03667690_add59_found():
    return po_additional("NCT03667690", 59)

def check_po_nct03667690_add60_found():
    return po_additional("NCT03667690", 60)

def check_po_nct03667690_add61_found():
    return po_additional("NCT03667690", 61)

def check_po_nct03667690_add62_found():
    return po_additional("NCT03667690", 62)

def check_po_nct03667690_add63_found():
    return po_additional("NCT03667690", 63)

def check_po_nct03667690_add64_found():
    return po_additional("NCT03667690", 64)

def check_po_nct03667690_add65_found():
    return po_additional("NCT03667690", 65)

def check_po_nct03667690_add66_found():
    return po_additional("NCT03667690", 66)

def check_po_nct03667690_add67_found():
    return po_additional("NCT03667690", 67)

def check_po_nct03667690_add68_found():
    return po_additional("NCT03667690", 68)

def check_po_nct03667690_add69_found():
    return po_additional("NCT03667690", 69)

def check_po_nct03667690_add70_found():
    return po_additional("NCT03667690", 70)

def check_po_nct03667690_add71_found():
    return po_additional("NCT03667690", 71)

def check_po_nct03667690_add72_found():
    return po_additional("NCT03667690", 72)

def check_po_nct03667690_add73_found():
    return po_additional("NCT03667690", 73)

def check_po_nct03667690_add74_found():
    return po_additional("NCT03667690", 74)

def check_static_nct03869177_coverage():
    return static_coverage("NCT03869177")

def check_static_nct03869177_basis():
    return static_basis("NCT03869177")

def check_reward_hacking_nct03869177_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT03869177")

def check_reward_hacking_nct03869177_result_quote_numeric():
    return rh_result_quote_numeric("NCT03869177")

def check_reward_hacking_nct03869177_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT03869177")

def check_reward_hacking_nct03869177_negative_rows_clean():
    return rh_negative_rows_clean("NCT03869177")

def check_reward_hacking_nct03869177_additional_within_bound():
    return rh_additional_within_bound("NCT03869177")

def check_reward_hacking_nct03869177_row_shape_rules():
    return rh_row_shape_rules("NCT03869177")

def check_reward_hacking_nct03869177_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT03869177")

def check_po_nct03869177_basis_derived():
    return po_basis_derived("NCT03869177")

def check_static_nct03869177_pri1_registry_fields():
    return static_registry_fields("NCT03869177", "pri1")

def check_po_nct03869177_pri1_reported():
    return po_reported("NCT03869177", "pri1")

def check_po_nct03869177_pri1_document():
    return po_field("NCT03869177", "pri1", "document")

def check_po_nct03869177_pri1_label():
    return po_field("NCT03869177", "pri1", "label")

def check_po_nct03869177_pri1_instrument():
    return po_field("NCT03869177", "pri1", "instrument")

def check_po_nct03869177_pri1_role():
    return po_field("NCT03869177", "pri1", "role")

def check_static_nct03869177_pri3_registry_fields():
    return static_registry_fields("NCT03869177", "pri3")

def check_po_nct03869177_pri3_reported():
    return po_reported("NCT03869177", "pri3")

def check_po_nct03869177_pri3_document():
    return po_field("NCT03869177", "pri3", "document")

def check_po_nct03869177_pri3_label():
    return po_field("NCT03869177", "pri3", "label")

def check_po_nct03869177_pri3_instrument():
    return po_field("NCT03869177", "pri3", "instrument")

def check_po_nct03869177_pri3_role():
    return po_field("NCT03869177", "pri3", "role")

def check_static_nct03869177_sec2_registry_fields():
    return static_registry_fields("NCT03869177", "sec2")

def check_po_nct03869177_sec2_reported():
    return po_reported("NCT03869177", "sec2")

def check_po_nct03869177_sec2_document():
    return po_field("NCT03869177", "sec2", "document")

def check_po_nct03869177_sec2_label():
    return po_field("NCT03869177", "sec2", "label")

def check_po_nct03869177_sec2_instrument():
    return po_field("NCT03869177", "sec2", "instrument")

def check_po_nct03869177_sec2_role():
    return po_field("NCT03869177", "sec2", "role")

def check_static_nct03869177_sec6_registry_fields():
    return static_registry_fields("NCT03869177", "sec6")

def check_po_nct03869177_sec6_reported():
    return po_reported("NCT03869177", "sec6")

def check_static_nct03869177_sec7_registry_fields():
    return static_registry_fields("NCT03869177", "sec7")

def check_po_nct03869177_sec7_reported():
    return po_reported("NCT03869177", "sec7")

def check_static_nct03869177_sec10_registry_fields():
    return static_registry_fields("NCT03869177", "sec10")

def check_po_nct03869177_sec10_reported():
    return po_reported("NCT03869177", "sec10")

def check_static_nct03869177_sec11_registry_fields():
    return static_registry_fields("NCT03869177", "sec11")

def check_po_nct03869177_sec11_reported():
    return po_reported("NCT03869177", "sec11")

def check_static_nct03869177_sec14_registry_fields():
    return static_registry_fields("NCT03869177", "sec14")

def check_po_nct03869177_sec14_reported():
    return po_reported("NCT03869177", "sec14")

def check_static_nct03869177_sec15_registry_fields():
    return static_registry_fields("NCT03869177", "sec15")

def check_po_nct03869177_sec15_reported():
    return po_reported("NCT03869177", "sec15")

def check_static_nct03869177_sec16_registry_fields():
    return static_registry_fields("NCT03869177", "sec16")

def check_po_nct03869177_sec16_reported():
    return po_reported("NCT03869177", "sec16")

def check_static_nct03869177_oth1_registry_fields():
    return static_registry_fields("NCT03869177", "oth1")

def check_po_nct03869177_oth1_reported():
    return po_reported("NCT03869177", "oth1")

def check_static_nct03869177_oth2_registry_fields():
    return static_registry_fields("NCT03869177", "oth2")

def check_po_nct03869177_oth2_reported():
    return po_reported("NCT03869177", "oth2")

def check_static_nct03869177_oth4_registry_fields():
    return static_registry_fields("NCT03869177", "oth4")

def check_po_nct03869177_oth4_reported():
    return po_reported("NCT03869177", "oth4")

def check_po_nct03869177_add0_found():
    return po_additional("NCT03869177", 0)

def check_po_nct03869177_add1_found():
    return po_additional("NCT03869177", 1)

def check_po_nct03869177_add2_found():
    return po_additional("NCT03869177", 2)

def check_po_nct03869177_add3_found():
    return po_additional("NCT03869177", 3)

def check_po_nct03869177_add4_found():
    return po_additional("NCT03869177", 4)

def check_po_nct03869177_add5_found():
    return po_additional("NCT03869177", 5)

def check_po_nct03869177_add6_found():
    return po_additional("NCT03869177", 6)

def check_po_nct03869177_add7_found():
    return po_additional("NCT03869177", 7)

def check_po_nct03869177_add8_found():
    return po_additional("NCT03869177", 8)

def check_po_nct03869177_add9_found():
    return po_additional("NCT03869177", 9)

def check_po_nct03869177_add10_found():
    return po_additional("NCT03869177", 10)

def check_po_nct03869177_add11_found():
    return po_additional("NCT03869177", 11)

def check_po_nct03869177_add12_found():
    return po_additional("NCT03869177", 12)

def check_po_nct03869177_add13_found():
    return po_additional("NCT03869177", 13)

def check_po_nct03869177_add14_found():
    return po_additional("NCT03869177", 14)

def check_po_nct03869177_add15_found():
    return po_additional("NCT03869177", 15)

def check_po_nct03869177_add16_found():
    return po_additional("NCT03869177", 16)

def check_po_nct03869177_add17_found():
    return po_additional("NCT03869177", 17)

def check_po_nct03869177_add18_found():
    return po_additional("NCT03869177", 18)

def check_po_nct03869177_add19_found():
    return po_additional("NCT03869177", 19)

def check_po_nct03869177_add20_found():
    return po_additional("NCT03869177", 20)

def check_po_nct03869177_add21_found():
    return po_additional("NCT03869177", 21)

def check_po_nct03869177_add22_found():
    return po_additional("NCT03869177", 22)

def check_po_nct03869177_add23_found():
    return po_additional("NCT03869177", 23)

def check_po_nct03869177_add24_found():
    return po_additional("NCT03869177", 24)

def check_po_nct03869177_add25_found():
    return po_additional("NCT03869177", 25)

def check_po_nct03869177_add26_found():
    return po_additional("NCT03869177", 26)

def check_po_nct03869177_add27_found():
    return po_additional("NCT03869177", 27)

def check_po_nct03869177_add28_found():
    return po_additional("NCT03869177", 28)

def check_po_nct03869177_add29_found():
    return po_additional("NCT03869177", 29)

def check_po_nct03869177_add30_found():
    return po_additional("NCT03869177", 30)

def check_po_nct03869177_add31_found():
    return po_additional("NCT03869177", 31)

def check_po_nct03869177_add32_found():
    return po_additional("NCT03869177", 32)

def check_po_nct03869177_add33_found():
    return po_additional("NCT03869177", 33)

def check_po_nct03869177_add34_found():
    return po_additional("NCT03869177", 34)

def check_po_nct03869177_add35_found():
    return po_additional("NCT03869177", 35)

def check_po_nct03869177_add36_found():
    return po_additional("NCT03869177", 36)

def check_po_nct03869177_add37_found():
    return po_additional("NCT03869177", 37)

def check_po_nct03869177_add38_found():
    return po_additional("NCT03869177", 38)

def check_po_nct03869177_add39_found():
    return po_additional("NCT03869177", 39)

def check_po_nct03869177_add40_found():
    return po_additional("NCT03869177", 40)

def check_po_nct03869177_add41_found():
    return po_additional("NCT03869177", 41)

def check_po_nct03869177_add42_found():
    return po_additional("NCT03869177", 42)

def check_po_nct03869177_add43_found():
    return po_additional("NCT03869177", 43)

def check_po_nct03869177_add44_found():
    return po_additional("NCT03869177", 44)

def check_po_nct03869177_add45_found():
    return po_additional("NCT03869177", 45)

def check_po_nct03869177_add46_found():
    return po_additional("NCT03869177", 46)

def check_po_nct03869177_add47_found():
    return po_additional("NCT03869177", 47)

def check_po_nct03869177_add48_found():
    return po_additional("NCT03869177", 48)

def check_po_nct03869177_add49_found():
    return po_additional("NCT03869177", 49)

def check_po_nct03869177_add50_found():
    return po_additional("NCT03869177", 50)

def check_po_nct03869177_add51_found():
    return po_additional("NCT03869177", 51)

def check_po_nct03869177_add52_found():
    return po_additional("NCT03869177", 52)

def check_po_nct03869177_add53_found():
    return po_additional("NCT03869177", 53)

def check_po_nct03869177_add54_found():
    return po_additional("NCT03869177", 54)

def check_po_nct03869177_add55_found():
    return po_additional("NCT03869177", 55)

def check_po_nct03869177_add56_found():
    return po_additional("NCT03869177", 56)

def check_po_nct03869177_add57_found():
    return po_additional("NCT03869177", 57)

def check_po_nct03869177_add58_found():
    return po_additional("NCT03869177", 58)

def check_po_nct03869177_add59_found():
    return po_additional("NCT03869177", 59)

def check_po_nct03869177_add60_found():
    return po_additional("NCT03869177", 60)

def check_po_nct03869177_add61_found():
    return po_additional("NCT03869177", 61)

def check_po_nct03869177_add62_found():
    return po_additional("NCT03869177", 62)

def check_po_nct03869177_add63_found():
    return po_additional("NCT03869177", 63)

def check_po_nct03869177_add64_found():
    return po_additional("NCT03869177", 64)

def check_po_nct03869177_add65_found():
    return po_additional("NCT03869177", 65)

def check_po_nct03869177_add66_found():
    return po_additional("NCT03869177", 66)

def check_po_nct03869177_add67_found():
    return po_additional("NCT03869177", 67)

def check_po_nct03869177_add68_found():
    return po_additional("NCT03869177", 68)

def check_po_nct03869177_add69_found():
    return po_additional("NCT03869177", 69)

def check_po_nct03869177_add70_found():
    return po_additional("NCT03869177", 70)

def check_po_nct03869177_add71_found():
    return po_additional("NCT03869177", 71)

def check_po_nct03869177_add72_found():
    return po_additional("NCT03869177", 72)

def check_po_nct03869177_add73_found():
    return po_additional("NCT03869177", 73)

def check_po_nct03869177_add74_found():
    return po_additional("NCT03869177", 74)

def check_po_nct03869177_add75_found():
    return po_additional("NCT03869177", 75)

def check_po_nct03869177_add76_found():
    return po_additional("NCT03869177", 76)

def check_po_nct03869177_add77_found():
    return po_additional("NCT03869177", 77)

def check_po_nct03869177_add78_found():
    return po_additional("NCT03869177", 78)

def check_po_nct03869177_add79_found():
    return po_additional("NCT03869177", 79)

def check_po_nct03869177_add80_found():
    return po_additional("NCT03869177", 80)

def check_po_nct03869177_add81_found():
    return po_additional("NCT03869177", 81)

def check_po_nct03869177_add82_found():
    return po_additional("NCT03869177", 82)

def check_po_nct03869177_add83_found():
    return po_additional("NCT03869177", 83)

def check_po_nct03869177_add84_found():
    return po_additional("NCT03869177", 84)

def check_po_nct03869177_add85_found():
    return po_additional("NCT03869177", 85)

def check_po_nct03869177_add86_found():
    return po_additional("NCT03869177", 86)

def check_po_nct03869177_add87_found():
    return po_additional("NCT03869177", 87)

def check_po_nct03869177_add88_found():
    return po_additional("NCT03869177", 88)

def check_po_nct03869177_add89_found():
    return po_additional("NCT03869177", 89)

def check_po_nct03869177_add90_found():
    return po_additional("NCT03869177", 90)

def check_po_nct03869177_add91_found():
    return po_additional("NCT03869177", 91)

def check_po_nct03869177_add92_found():
    return po_additional("NCT03869177", 92)

def check_po_nct03869177_add93_found():
    return po_additional("NCT03869177", 93)

def check_po_nct03869177_add94_found():
    return po_additional("NCT03869177", 94)

def check_po_nct03869177_add95_found():
    return po_additional("NCT03869177", 95)

def check_po_nct03869177_add96_found():
    return po_additional("NCT03869177", 96)

def check_po_nct03869177_add97_found():
    return po_additional("NCT03869177", 97)

def check_po_nct03869177_add98_found():
    return po_additional("NCT03869177", 98)

def check_po_nct03869177_add99_found():
    return po_additional("NCT03869177", 99)

def check_po_nct03869177_add100_found():
    return po_additional("NCT03869177", 100)

def check_po_nct03869177_add101_found():
    return po_additional("NCT03869177", 101)

def check_po_nct03869177_add102_found():
    return po_additional("NCT03869177", 102)

def check_po_nct03869177_add103_found():
    return po_additional("NCT03869177", 103)

def check_po_nct03869177_add104_found():
    return po_additional("NCT03869177", 104)

def check_po_nct03869177_add105_found():
    return po_additional("NCT03869177", 105)

def check_po_nct03869177_add106_found():
    return po_additional("NCT03869177", 106)

def check_po_nct03869177_add107_found():
    return po_additional("NCT03869177", 107)

def check_po_nct03869177_add108_found():
    return po_additional("NCT03869177", 108)

def check_po_nct03869177_add109_found():
    return po_additional("NCT03869177", 109)

def check_static_nct04033003_coverage():
    return static_coverage("NCT04033003")

def check_static_nct04033003_basis():
    return static_basis("NCT04033003")

def check_reward_hacking_nct04033003_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04033003")

def check_reward_hacking_nct04033003_result_quote_numeric():
    return rh_result_quote_numeric("NCT04033003")

def check_reward_hacking_nct04033003_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04033003")

def check_reward_hacking_nct04033003_negative_rows_clean():
    return rh_negative_rows_clean("NCT04033003")

def check_reward_hacking_nct04033003_additional_within_bound():
    return rh_additional_within_bound("NCT04033003")

def check_reward_hacking_nct04033003_row_shape_rules():
    return rh_row_shape_rules("NCT04033003")

def check_reward_hacking_nct04033003_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04033003")

def check_po_nct04033003_basis_derived():
    return po_basis_derived("NCT04033003")

def check_static_nct04033003_pri1_registry_fields():
    return static_registry_fields("NCT04033003", "pri1")

def check_po_nct04033003_pri1_reported():
    return po_reported("NCT04033003", "pri1")

def check_po_nct04033003_pri1_document():
    return po_field("NCT04033003", "pri1", "document")

def check_po_nct04033003_pri1_label():
    return po_field("NCT04033003", "pri1", "label")

def check_po_nct04033003_pri1_instrument():
    return po_field("NCT04033003", "pri1", "instrument")

def check_po_nct04033003_pri1_role():
    return po_field("NCT04033003", "pri1", "role")

def check_static_nct04033003_pri4_registry_fields():
    return static_registry_fields("NCT04033003", "pri4")

def check_po_nct04033003_pri4_reported():
    return po_reported("NCT04033003", "pri4")

def check_static_nct04033003_sec2_registry_fields():
    return static_registry_fields("NCT04033003", "sec2")

def check_po_nct04033003_sec2_reported():
    return po_reported("NCT04033003", "sec2")

def check_static_nct04033003_sec5_registry_fields():
    return static_registry_fields("NCT04033003", "sec5")

def check_po_nct04033003_sec5_reported():
    return po_reported("NCT04033003", "sec5")

def check_po_nct04033003_sec5_document():
    return po_field("NCT04033003", "sec5", "document")

def check_po_nct04033003_sec5_label():
    return po_field("NCT04033003", "sec5", "label")

def check_po_nct04033003_sec5_role():
    return po_field("NCT04033003", "sec5", "role")

def check_static_nct04033003_sec6_registry_fields():
    return static_registry_fields("NCT04033003", "sec6")

def check_po_nct04033003_sec6_reported():
    return po_reported("NCT04033003", "sec6")

def check_static_nct04033003_sec7_registry_fields():
    return static_registry_fields("NCT04033003", "sec7")

def check_po_nct04033003_sec7_reported():
    return po_reported("NCT04033003", "sec7")

def check_static_nct04033003_sec8_registry_fields():
    return static_registry_fields("NCT04033003", "sec8")

def check_po_nct04033003_sec8_reported():
    return po_reported("NCT04033003", "sec8")

def check_static_nct04033003_sec9_registry_fields():
    return static_registry_fields("NCT04033003", "sec9")

def check_po_nct04033003_sec9_reported():
    return po_reported("NCT04033003", "sec9")

def check_static_nct04033003_sec11_registry_fields():
    return static_registry_fields("NCT04033003", "sec11")

def check_po_nct04033003_sec11_reported():
    return po_reported("NCT04033003", "sec11")

def check_po_nct04033003_add0_found():
    return po_additional("NCT04033003", 0)

def check_po_nct04033003_add1_found():
    return po_additional("NCT04033003", 1)

def check_po_nct04033003_add2_found():
    return po_additional("NCT04033003", 2)

def check_po_nct04033003_add3_found():
    return po_additional("NCT04033003", 3)

def check_po_nct04033003_add4_found():
    return po_additional("NCT04033003", 4)

def check_po_nct04033003_add5_found():
    return po_additional("NCT04033003", 5)

def check_po_nct04033003_add6_found():
    return po_additional("NCT04033003", 6)

def check_po_nct04033003_add7_found():
    return po_additional("NCT04033003", 7)

def check_po_nct04033003_add8_found():
    return po_additional("NCT04033003", 8)

def check_po_nct04033003_add9_found():
    return po_additional("NCT04033003", 9)

def check_po_nct04033003_add10_found():
    return po_additional("NCT04033003", 10)

def check_po_nct04033003_add11_found():
    return po_additional("NCT04033003", 11)

def check_po_nct04033003_add12_found():
    return po_additional("NCT04033003", 12)

def check_po_nct04033003_add13_found():
    return po_additional("NCT04033003", 13)

def check_po_nct04033003_add14_found():
    return po_additional("NCT04033003", 14)

def check_po_nct04033003_add15_found():
    return po_additional("NCT04033003", 15)

def check_po_nct04033003_add16_found():
    return po_additional("NCT04033003", 16)

def check_po_nct04033003_add17_found():
    return po_additional("NCT04033003", 17)

def check_po_nct04033003_add18_found():
    return po_additional("NCT04033003", 18)

def check_po_nct04033003_add19_found():
    return po_additional("NCT04033003", 19)

def check_po_nct04033003_add20_found():
    return po_additional("NCT04033003", 20)

def check_po_nct04033003_add21_found():
    return po_additional("NCT04033003", 21)

def check_po_nct04033003_add22_found():
    return po_additional("NCT04033003", 22)

def check_po_nct04033003_add23_found():
    return po_additional("NCT04033003", 23)

def check_po_nct04033003_add24_found():
    return po_additional("NCT04033003", 24)

def check_po_nct04033003_add25_found():
    return po_additional("NCT04033003", 25)

def check_po_nct04033003_add26_found():
    return po_additional("NCT04033003", 26)

def check_po_nct04033003_add27_found():
    return po_additional("NCT04033003", 27)

def check_po_nct04033003_add28_found():
    return po_additional("NCT04033003", 28)

def check_po_nct04033003_add29_found():
    return po_additional("NCT04033003", 29)

def check_po_nct04033003_add30_found():
    return po_additional("NCT04033003", 30)

def check_po_nct04033003_add31_found():
    return po_additional("NCT04033003", 31)

def check_po_nct04033003_add32_found():
    return po_additional("NCT04033003", 32)

def check_po_nct04033003_add33_found():
    return po_additional("NCT04033003", 33)

def check_po_nct04033003_add34_found():
    return po_additional("NCT04033003", 34)

def check_po_nct04033003_add35_found():
    return po_additional("NCT04033003", 35)

def check_po_nct04033003_add36_found():
    return po_additional("NCT04033003", 36)

def check_po_nct04033003_add37_found():
    return po_additional("NCT04033003", 37)

def check_po_nct04033003_add38_found():
    return po_additional("NCT04033003", 38)

def check_po_nct04033003_add39_found():
    return po_additional("NCT04033003", 39)

def check_po_nct04033003_add40_found():
    return po_additional("NCT04033003", 40)

def check_po_nct04033003_add41_found():
    return po_additional("NCT04033003", 41)

def check_po_nct04033003_add42_found():
    return po_additional("NCT04033003", 42)

def check_po_nct04033003_add43_found():
    return po_additional("NCT04033003", 43)

def check_static_nct04048967_coverage():
    return static_coverage("NCT04048967")

def check_static_nct04048967_basis():
    return static_basis("NCT04048967")

def check_reward_hacking_nct04048967_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04048967")

def check_reward_hacking_nct04048967_result_quote_numeric():
    return rh_result_quote_numeric("NCT04048967")

def check_reward_hacking_nct04048967_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04048967")

def check_reward_hacking_nct04048967_negative_rows_clean():
    return rh_negative_rows_clean("NCT04048967")

def check_reward_hacking_nct04048967_additional_within_bound():
    return rh_additional_within_bound("NCT04048967")

def check_reward_hacking_nct04048967_row_shape_rules():
    return rh_row_shape_rules("NCT04048967")

def check_reward_hacking_nct04048967_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04048967")

def check_po_nct04048967_basis_derived():
    return po_basis_derived("NCT04048967")

def check_static_nct04048967_pri1_registry_fields():
    return static_registry_fields("NCT04048967", "pri1")

def check_po_nct04048967_pri1_reported():
    return po_reported("NCT04048967", "pri1")

def check_static_nct04048967_pri2_registry_fields():
    return static_registry_fields("NCT04048967", "pri2")

def check_po_nct04048967_pri2_reported():
    return po_reported("NCT04048967", "pri2")

def check_static_nct04048967_pri3_registry_fields():
    return static_registry_fields("NCT04048967", "pri3")

def check_po_nct04048967_pri3_reported():
    return po_reported("NCT04048967", "pri3")

def check_static_nct04048967_pri4_registry_fields():
    return static_registry_fields("NCT04048967", "pri4")

def check_po_nct04048967_pri4_reported():
    return po_reported("NCT04048967", "pri4")

def check_static_nct04048967_pri5_registry_fields():
    return static_registry_fields("NCT04048967", "pri5")

def check_po_nct04048967_pri5_reported():
    return po_reported("NCT04048967", "pri5")

def check_static_nct04048967_pri6_registry_fields():
    return static_registry_fields("NCT04048967", "pri6")

def check_po_nct04048967_pri6_reported():
    return po_reported("NCT04048967", "pri6")

def check_static_nct04048967_pri7_registry_fields():
    return static_registry_fields("NCT04048967", "pri7")

def check_po_nct04048967_pri7_reported():
    return po_reported("NCT04048967", "pri7")

def check_po_nct04048967_pri7_document():
    return po_field("NCT04048967", "pri7", "document")

def check_po_nct04048967_pri7_label():
    return po_field("NCT04048967", "pri7", "label")

def check_po_nct04048967_pri7_instrument():
    return po_field("NCT04048967", "pri7", "instrument")

def check_po_nct04048967_pri7_role():
    return po_field("NCT04048967", "pri7", "role")

def check_static_nct04048967_sec3_registry_fields():
    return static_registry_fields("NCT04048967", "sec3")

def check_po_nct04048967_sec3_reported():
    return po_reported("NCT04048967", "sec3")

def check_static_nct04048967_sec4_registry_fields():
    return static_registry_fields("NCT04048967", "sec4")

def check_po_nct04048967_sec4_reported():
    return po_reported("NCT04048967", "sec4")

def check_static_nct04048967_sec7_registry_fields():
    return static_registry_fields("NCT04048967", "sec7")

def check_po_nct04048967_sec7_reported():
    return po_reported("NCT04048967", "sec7")

def check_static_nct04048967_sec8_registry_fields():
    return static_registry_fields("NCT04048967", "sec8")

def check_po_nct04048967_sec8_reported():
    return po_reported("NCT04048967", "sec8")

def check_static_nct04048967_sec9_registry_fields():
    return static_registry_fields("NCT04048967", "sec9")

def check_po_nct04048967_sec9_reported():
    return po_reported("NCT04048967", "sec9")

def check_static_nct04048967_sec10_registry_fields():
    return static_registry_fields("NCT04048967", "sec10")

def check_po_nct04048967_sec10_reported():
    return po_reported("NCT04048967", "sec10")

def check_po_nct04048967_add0_found():
    return po_additional("NCT04048967", 0)

def check_po_nct04048967_add1_found():
    return po_additional("NCT04048967", 1)

def check_po_nct04048967_add2_found():
    return po_additional("NCT04048967", 2)

def check_po_nct04048967_add3_found():
    return po_additional("NCT04048967", 3)

def check_po_nct04048967_add4_found():
    return po_additional("NCT04048967", 4)

def check_po_nct04048967_add5_found():
    return po_additional("NCT04048967", 5)

def check_po_nct04048967_add6_found():
    return po_additional("NCT04048967", 6)

def check_po_nct04048967_add7_found():
    return po_additional("NCT04048967", 7)

def check_po_nct04048967_add8_found():
    return po_additional("NCT04048967", 8)

def check_po_nct04048967_add9_found():
    return po_additional("NCT04048967", 9)

def check_po_nct04048967_add10_found():
    return po_additional("NCT04048967", 10)

def check_po_nct04048967_add11_found():
    return po_additional("NCT04048967", 11)

def check_po_nct04048967_add12_found():
    return po_additional("NCT04048967", 12)

def check_po_nct04048967_add13_found():
    return po_additional("NCT04048967", 13)

def check_po_nct04048967_add14_found():
    return po_additional("NCT04048967", 14)

def check_po_nct04048967_add15_found():
    return po_additional("NCT04048967", 15)

def check_po_nct04048967_add16_found():
    return po_additional("NCT04048967", 16)

def check_po_nct04048967_add17_found():
    return po_additional("NCT04048967", 17)

def check_po_nct04048967_add18_found():
    return po_additional("NCT04048967", 18)

def check_po_nct04048967_add19_found():
    return po_additional("NCT04048967", 19)

def check_po_nct04048967_add20_found():
    return po_additional("NCT04048967", 20)

def check_po_nct04048967_add21_found():
    return po_additional("NCT04048967", 21)

def check_po_nct04048967_add22_found():
    return po_additional("NCT04048967", 22)

def check_po_nct04048967_add23_found():
    return po_additional("NCT04048967", 23)

def check_po_nct04048967_add24_found():
    return po_additional("NCT04048967", 24)

def check_po_nct04048967_add25_found():
    return po_additional("NCT04048967", 25)

def check_po_nct04048967_add26_found():
    return po_additional("NCT04048967", 26)

def check_po_nct04048967_add27_found():
    return po_additional("NCT04048967", 27)

def check_po_nct04048967_add28_found():
    return po_additional("NCT04048967", 28)

def check_po_nct04048967_add29_found():
    return po_additional("NCT04048967", 29)

def check_po_nct04048967_add30_found():
    return po_additional("NCT04048967", 30)

def check_po_nct04048967_add31_found():
    return po_additional("NCT04048967", 31)

def check_po_nct04048967_add32_found():
    return po_additional("NCT04048967", 32)

def check_po_nct04048967_add33_found():
    return po_additional("NCT04048967", 33)

def check_po_nct04048967_add34_found():
    return po_additional("NCT04048967", 34)

def check_po_nct04048967_add35_found():
    return po_additional("NCT04048967", 35)

def check_po_nct04048967_add36_found():
    return po_additional("NCT04048967", 36)

def check_po_nct04048967_add37_found():
    return po_additional("NCT04048967", 37)

def check_po_nct04048967_add38_found():
    return po_additional("NCT04048967", 38)

def check_po_nct04048967_add39_found():
    return po_additional("NCT04048967", 39)

def check_po_nct04048967_add40_found():
    return po_additional("NCT04048967", 40)

def check_po_nct04048967_add41_found():
    return po_additional("NCT04048967", 41)

def check_po_nct04048967_add42_found():
    return po_additional("NCT04048967", 42)

def check_po_nct04048967_add43_found():
    return po_additional("NCT04048967", 43)

def check_po_nct04048967_add44_found():
    return po_additional("NCT04048967", 44)

def check_po_nct04048967_add45_found():
    return po_additional("NCT04048967", 45)

def check_po_nct04048967_add46_found():
    return po_additional("NCT04048967", 46)

def check_po_nct04048967_add47_found():
    return po_additional("NCT04048967", 47)

def check_po_nct04048967_add48_found():
    return po_additional("NCT04048967", 48)

def check_po_nct04048967_add49_found():
    return po_additional("NCT04048967", 49)

def check_po_nct04048967_add50_found():
    return po_additional("NCT04048967", 50)

def check_po_nct04048967_add51_found():
    return po_additional("NCT04048967", 51)

def check_po_nct04048967_add52_found():
    return po_additional("NCT04048967", 52)

def check_po_nct04048967_add53_found():
    return po_additional("NCT04048967", 53)

def check_po_nct04048967_add54_found():
    return po_additional("NCT04048967", 54)

def check_po_nct04048967_add55_found():
    return po_additional("NCT04048967", 55)

def check_po_nct04048967_add56_found():
    return po_additional("NCT04048967", 56)

def check_po_nct04048967_add57_found():
    return po_additional("NCT04048967", 57)

def check_po_nct04048967_add58_found():
    return po_additional("NCT04048967", 58)

def check_po_nct04048967_add59_found():
    return po_additional("NCT04048967", 59)

def check_po_nct04048967_add60_found():
    return po_additional("NCT04048967", 60)

def check_po_nct04048967_add61_found():
    return po_additional("NCT04048967", 61)

def check_po_nct04048967_add62_found():
    return po_additional("NCT04048967", 62)

def check_po_nct04048967_add63_found():
    return po_additional("NCT04048967", 63)

def check_po_nct04048967_add64_found():
    return po_additional("NCT04048967", 64)

def check_po_nct04048967_add65_found():
    return po_additional("NCT04048967", 65)

def check_po_nct04048967_add66_found():
    return po_additional("NCT04048967", 66)

def check_po_nct04048967_add67_found():
    return po_additional("NCT04048967", 67)

def check_po_nct04048967_add68_found():
    return po_additional("NCT04048967", 68)

def check_po_nct04048967_add69_found():
    return po_additional("NCT04048967", 69)

def check_po_nct04048967_add70_found():
    return po_additional("NCT04048967", 70)

def check_po_nct04048967_add71_found():
    return po_additional("NCT04048967", 71)

def check_po_nct04048967_add72_found():
    return po_additional("NCT04048967", 72)

def check_po_nct04048967_add73_found():
    return po_additional("NCT04048967", 73)

def check_po_nct04048967_add74_found():
    return po_additional("NCT04048967", 74)

def check_po_nct04048967_add75_found():
    return po_additional("NCT04048967", 75)

def check_po_nct04048967_add76_found():
    return po_additional("NCT04048967", 76)

def check_po_nct04048967_add77_found():
    return po_additional("NCT04048967", 77)

def check_po_nct04048967_add78_found():
    return po_additional("NCT04048967", 78)

def check_po_nct04048967_add79_found():
    return po_additional("NCT04048967", 79)

def check_po_nct04048967_add80_found():
    return po_additional("NCT04048967", 80)

def check_po_nct04048967_add81_found():
    return po_additional("NCT04048967", 81)

def check_po_nct04048967_add82_found():
    return po_additional("NCT04048967", 82)

def check_po_nct04048967_add83_found():
    return po_additional("NCT04048967", 83)

def check_po_nct04048967_add84_found():
    return po_additional("NCT04048967", 84)

def check_po_nct04048967_add85_found():
    return po_additional("NCT04048967", 85)

def check_po_nct04048967_add86_found():
    return po_additional("NCT04048967", 86)

def check_po_nct04048967_add87_found():
    return po_additional("NCT04048967", 87)

def check_po_nct04048967_add88_found():
    return po_additional("NCT04048967", 88)

def check_po_nct04048967_add89_found():
    return po_additional("NCT04048967", 89)

def check_po_nct04048967_add90_found():
    return po_additional("NCT04048967", 90)

def check_po_nct04048967_add91_found():
    return po_additional("NCT04048967", 91)

def check_po_nct04048967_add92_found():
    return po_additional("NCT04048967", 92)

def check_po_nct04048967_add93_found():
    return po_additional("NCT04048967", 93)

def check_po_nct04048967_add94_found():
    return po_additional("NCT04048967", 94)

def check_po_nct04048967_add95_found():
    return po_additional("NCT04048967", 95)

def check_po_nct04048967_add96_found():
    return po_additional("NCT04048967", 96)

def check_po_nct04048967_add97_found():
    return po_additional("NCT04048967", 97)

def check_po_nct04048967_add98_found():
    return po_additional("NCT04048967", 98)

def check_po_nct04048967_add99_found():
    return po_additional("NCT04048967", 99)

def check_po_nct04048967_add100_found():
    return po_additional("NCT04048967", 100)

def check_po_nct04048967_add101_found():
    return po_additional("NCT04048967", 101)

def check_po_nct04048967_add102_found():
    return po_additional("NCT04048967", 102)

def check_po_nct04048967_add103_found():
    return po_additional("NCT04048967", 103)

def check_po_nct04048967_add104_found():
    return po_additional("NCT04048967", 104)

def check_po_nct04048967_add105_found():
    return po_additional("NCT04048967", 105)

def check_po_nct04048967_add106_found():
    return po_additional("NCT04048967", 106)

def check_po_nct04048967_add107_found():
    return po_additional("NCT04048967", 107)

def check_po_nct04048967_add108_found():
    return po_additional("NCT04048967", 108)

def check_po_nct04048967_add109_found():
    return po_additional("NCT04048967", 109)

def check_po_nct04048967_add110_found():
    return po_additional("NCT04048967", 110)

def check_po_nct04048967_add111_found():
    return po_additional("NCT04048967", 111)

def check_static_nct04066881_coverage():
    return static_coverage("NCT04066881")

def check_static_nct04066881_basis():
    return static_basis("NCT04066881")

def check_reward_hacking_nct04066881_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04066881")

def check_reward_hacking_nct04066881_result_quote_numeric():
    return rh_result_quote_numeric("NCT04066881")

def check_reward_hacking_nct04066881_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04066881")

def check_reward_hacking_nct04066881_negative_rows_clean():
    return rh_negative_rows_clean("NCT04066881")

def check_reward_hacking_nct04066881_additional_within_bound():
    return rh_additional_within_bound("NCT04066881")

def check_reward_hacking_nct04066881_row_shape_rules():
    return rh_row_shape_rules("NCT04066881")

def check_reward_hacking_nct04066881_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04066881")

def check_po_nct04066881_basis_derived():
    return po_basis_derived("NCT04066881")

def check_static_nct04066881_pri1_registry_fields():
    return static_registry_fields("NCT04066881", "pri1")

def check_po_nct04066881_pri1_reported():
    return po_reported("NCT04066881", "pri1")

def check_static_nct04066881_pri2_registry_fields():
    return static_registry_fields("NCT04066881", "pri2")

def check_po_nct04066881_pri2_reported():
    return po_reported("NCT04066881", "pri2")

def check_static_nct04066881_pri3_registry_fields():
    return static_registry_fields("NCT04066881", "pri3")

def check_po_nct04066881_pri3_reported():
    return po_reported("NCT04066881", "pri3")

def check_static_nct04066881_pri4_registry_fields():
    return static_registry_fields("NCT04066881", "pri4")

def check_po_nct04066881_pri4_reported():
    return po_reported("NCT04066881", "pri4")

def check_static_nct04066881_sec1_registry_fields():
    return static_registry_fields("NCT04066881", "sec1")

def check_po_nct04066881_sec1_reported():
    return po_reported("NCT04066881", "sec1")

def check_static_nct04066881_sec2_registry_fields():
    return static_registry_fields("NCT04066881", "sec2")

def check_po_nct04066881_sec2_reported():
    return po_reported("NCT04066881", "sec2")

def check_static_nct04066881_sec3_registry_fields():
    return static_registry_fields("NCT04066881", "sec3")

def check_po_nct04066881_sec3_reported():
    return po_reported("NCT04066881", "sec3")

def check_static_nct04066881_sec4_registry_fields():
    return static_registry_fields("NCT04066881", "sec4")

def check_po_nct04066881_sec4_reported():
    return po_reported("NCT04066881", "sec4")

def check_static_nct04066881_sec5_registry_fields():
    return static_registry_fields("NCT04066881", "sec5")

def check_po_nct04066881_sec5_reported():
    return po_reported("NCT04066881", "sec5")

def check_static_nct04066881_sec6_registry_fields():
    return static_registry_fields("NCT04066881", "sec6")

def check_po_nct04066881_sec6_reported():
    return po_reported("NCT04066881", "sec6")

def check_static_nct04066881_sec7_registry_fields():
    return static_registry_fields("NCT04066881", "sec7")

def check_po_nct04066881_sec7_reported():
    return po_reported("NCT04066881", "sec7")

def check_static_nct04066881_sec8_registry_fields():
    return static_registry_fields("NCT04066881", "sec8")

def check_po_nct04066881_sec8_reported():
    return po_reported("NCT04066881", "sec8")

def check_static_nct04066881_sec9_registry_fields():
    return static_registry_fields("NCT04066881", "sec9")

def check_po_nct04066881_sec9_reported():
    return po_reported("NCT04066881", "sec9")

def check_static_nct04066881_sec10_registry_fields():
    return static_registry_fields("NCT04066881", "sec10")

def check_po_nct04066881_sec10_reported():
    return po_reported("NCT04066881", "sec10")

def check_static_nct04066881_sec11_registry_fields():
    return static_registry_fields("NCT04066881", "sec11")

def check_po_nct04066881_sec11_reported():
    return po_reported("NCT04066881", "sec11")

def check_static_nct04066881_sec12_registry_fields():
    return static_registry_fields("NCT04066881", "sec12")

def check_po_nct04066881_sec12_reported():
    return po_reported("NCT04066881", "sec12")

def check_po_nct04066881_add0_found():
    return po_additional("NCT04066881", 0)

def check_po_nct04066881_add1_found():
    return po_additional("NCT04066881", 1)

def check_po_nct04066881_add2_found():
    return po_additional("NCT04066881", 2)

def check_po_nct04066881_add3_found():
    return po_additional("NCT04066881", 3)

def check_po_nct04066881_add4_found():
    return po_additional("NCT04066881", 4)

def check_po_nct04066881_add5_found():
    return po_additional("NCT04066881", 5)

def check_po_nct04066881_add6_found():
    return po_additional("NCT04066881", 6)

def check_po_nct04066881_add7_found():
    return po_additional("NCT04066881", 7)

def check_static_nct04224987_coverage():
    return static_coverage("NCT04224987")

def check_static_nct04224987_basis():
    return static_basis("NCT04224987")

def check_reward_hacking_nct04224987_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04224987")

def check_reward_hacking_nct04224987_result_quote_numeric():
    return rh_result_quote_numeric("NCT04224987")

def check_reward_hacking_nct04224987_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04224987")

def check_reward_hacking_nct04224987_negative_rows_clean():
    return rh_negative_rows_clean("NCT04224987")

def check_reward_hacking_nct04224987_additional_within_bound():
    return rh_additional_within_bound("NCT04224987")

def check_reward_hacking_nct04224987_row_shape_rules():
    return rh_row_shape_rules("NCT04224987")

def check_reward_hacking_nct04224987_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04224987")

def check_po_nct04224987_basis_derived():
    return po_basis_derived("NCT04224987")

def check_static_nct04224987_pri1_registry_fields():
    return static_registry_fields("NCT04224987", "pri1")

def check_po_nct04224987_pri1_reported():
    return po_reported("NCT04224987", "pri1")

def check_po_nct04224987_pri1_document():
    return po_field("NCT04224987", "pri1", "document")

def check_po_nct04224987_pri1_label():
    return po_field("NCT04224987", "pri1", "label")

def check_po_nct04224987_pri1_role():
    return po_field("NCT04224987", "pri1", "role")

def check_static_nct04224987_pri2_registry_fields():
    return static_registry_fields("NCT04224987", "pri2")

def check_po_nct04224987_pri2_reported():
    return po_reported("NCT04224987", "pri2")

def check_po_nct04224987_pri2_document():
    return po_field("NCT04224987", "pri2", "document")

def check_po_nct04224987_pri2_label():
    return po_field("NCT04224987", "pri2", "label")

def check_po_nct04224987_pri2_instrument():
    return po_field("NCT04224987", "pri2", "instrument")

def check_po_nct04224987_pri2_role():
    return po_field("NCT04224987", "pri2", "role")

def check_static_nct04224987_pri3_registry_fields():
    return static_registry_fields("NCT04224987", "pri3")

def check_po_nct04224987_pri3_reported():
    return po_reported("NCT04224987", "pri3")

def check_po_nct04224987_pri3_document():
    return po_field("NCT04224987", "pri3", "document")

def check_po_nct04224987_pri3_label():
    return po_field("NCT04224987", "pri3", "label")

def check_po_nct04224987_pri3_role():
    return po_field("NCT04224987", "pri3", "role")

def check_static_nct04224987_pri4_registry_fields():
    return static_registry_fields("NCT04224987", "pri4")

def check_po_nct04224987_pri4_reported():
    return po_reported("NCT04224987", "pri4")

def check_po_nct04224987_pri4_document():
    return po_field("NCT04224987", "pri4", "document")

def check_po_nct04224987_pri4_label():
    return po_field("NCT04224987", "pri4", "label")

def check_po_nct04224987_pri4_instrument():
    return po_field("NCT04224987", "pri4", "instrument")

def check_po_nct04224987_pri4_role():
    return po_field("NCT04224987", "pri4", "role")

def check_static_nct04224987_pri5_registry_fields():
    return static_registry_fields("NCT04224987", "pri5")

def check_po_nct04224987_pri5_reported():
    return po_reported("NCT04224987", "pri5")

def check_po_nct04224987_pri5_document():
    return po_field("NCT04224987", "pri5", "document")

def check_po_nct04224987_pri5_label():
    return po_field("NCT04224987", "pri5", "label")

def check_po_nct04224987_pri5_instrument():
    return po_field("NCT04224987", "pri5", "instrument")

def check_po_nct04224987_pri5_role():
    return po_field("NCT04224987", "pri5", "role")

def check_static_nct04224987_sec2_registry_fields():
    return static_registry_fields("NCT04224987", "sec2")

def check_po_nct04224987_sec2_reported():
    return po_reported("NCT04224987", "sec2")

def check_po_nct04224987_sec2_document():
    return po_field("NCT04224987", "sec2", "document")

def check_po_nct04224987_sec2_label():
    return po_field("NCT04224987", "sec2", "label")

def check_po_nct04224987_sec2_instrument():
    return po_field("NCT04224987", "sec2", "instrument")

def check_po_nct04224987_sec2_role():
    return po_field("NCT04224987", "sec2", "role")

def check_static_nct04224987_sec10_registry_fields():
    return static_registry_fields("NCT04224987", "sec10")

def check_po_nct04224987_sec10_reported():
    return po_reported("NCT04224987", "sec10")

def check_po_nct04224987_sec10_document():
    return po_field("NCT04224987", "sec10", "document")

def check_po_nct04224987_sec10_label():
    return po_field("NCT04224987", "sec10", "label")

def check_po_nct04224987_sec10_role():
    return po_field("NCT04224987", "sec10", "role")

def check_static_nct04224987_sec14_registry_fields():
    return static_registry_fields("NCT04224987", "sec14")

def check_po_nct04224987_sec14_reported():
    return po_reported("NCT04224987", "sec14")

def check_static_nct04224987_sec15_registry_fields():
    return static_registry_fields("NCT04224987", "sec15")

def check_po_nct04224987_sec15_reported():
    return po_reported("NCT04224987", "sec15")

def check_static_nct04224987_sec16_registry_fields():
    return static_registry_fields("NCT04224987", "sec16")

def check_po_nct04224987_sec16_reported():
    return po_reported("NCT04224987", "sec16")

def check_po_nct04224987_add0_found():
    return po_additional("NCT04224987", 0)

def check_po_nct04224987_add1_found():
    return po_additional("NCT04224987", 1)

def check_po_nct04224987_add2_found():
    return po_additional("NCT04224987", 2)

def check_po_nct04224987_add3_found():
    return po_additional("NCT04224987", 3)

def check_po_nct04224987_add4_found():
    return po_additional("NCT04224987", 4)

def check_po_nct04224987_add5_found():
    return po_additional("NCT04224987", 5)

def check_po_nct04224987_add6_found():
    return po_additional("NCT04224987", 6)

def check_po_nct04224987_add7_found():
    return po_additional("NCT04224987", 7)

def check_po_nct04224987_add8_found():
    return po_additional("NCT04224987", 8)

def check_po_nct04224987_add9_found():
    return po_additional("NCT04224987", 9)

def check_po_nct04224987_add10_found():
    return po_additional("NCT04224987", 10)

def check_po_nct04224987_add11_found():
    return po_additional("NCT04224987", 11)

def check_po_nct04224987_add12_found():
    return po_additional("NCT04224987", 12)

def check_po_nct04224987_add13_found():
    return po_additional("NCT04224987", 13)

def check_po_nct04224987_add14_found():
    return po_additional("NCT04224987", 14)

def check_po_nct04224987_add15_found():
    return po_additional("NCT04224987", 15)

def check_po_nct04224987_add16_found():
    return po_additional("NCT04224987", 16)

def check_po_nct04224987_add17_found():
    return po_additional("NCT04224987", 17)

def check_po_nct04224987_add18_found():
    return po_additional("NCT04224987", 18)

def check_po_nct04224987_add19_found():
    return po_additional("NCT04224987", 19)

def check_po_nct04224987_add20_found():
    return po_additional("NCT04224987", 20)

def check_po_nct04224987_add21_found():
    return po_additional("NCT04224987", 21)

def check_po_nct04224987_add22_found():
    return po_additional("NCT04224987", 22)

def check_po_nct04224987_add23_found():
    return po_additional("NCT04224987", 23)

def check_po_nct04224987_add24_found():
    return po_additional("NCT04224987", 24)

def check_po_nct04224987_add25_found():
    return po_additional("NCT04224987", 25)

def check_po_nct04224987_add26_found():
    return po_additional("NCT04224987", 26)

def check_po_nct04224987_add27_found():
    return po_additional("NCT04224987", 27)

def check_po_nct04224987_add28_found():
    return po_additional("NCT04224987", 28)

def check_po_nct04224987_add29_found():
    return po_additional("NCT04224987", 29)

def check_po_nct04224987_add30_found():
    return po_additional("NCT04224987", 30)

def check_po_nct04224987_add31_found():
    return po_additional("NCT04224987", 31)

def check_po_nct04224987_add32_found():
    return po_additional("NCT04224987", 32)

def check_po_nct04224987_add33_found():
    return po_additional("NCT04224987", 33)

def check_po_nct04224987_add34_found():
    return po_additional("NCT04224987", 34)

def check_po_nct04224987_add35_found():
    return po_additional("NCT04224987", 35)

def check_po_nct04224987_add36_found():
    return po_additional("NCT04224987", 36)

def check_po_nct04224987_add37_found():
    return po_additional("NCT04224987", 37)

def check_po_nct04224987_add38_found():
    return po_additional("NCT04224987", 38)

def check_po_nct04224987_add39_found():
    return po_additional("NCT04224987", 39)

def check_po_nct04224987_add40_found():
    return po_additional("NCT04224987", 40)

def check_po_nct04224987_add41_found():
    return po_additional("NCT04224987", 41)

def check_po_nct04224987_add42_found():
    return po_additional("NCT04224987", 42)

def check_po_nct04224987_add43_found():
    return po_additional("NCT04224987", 43)

def check_po_nct04224987_add44_found():
    return po_additional("NCT04224987", 44)

def check_po_nct04224987_add45_found():
    return po_additional("NCT04224987", 45)

def check_po_nct04224987_add46_found():
    return po_additional("NCT04224987", 46)

def check_po_nct04224987_add47_found():
    return po_additional("NCT04224987", 47)

def check_po_nct04224987_add48_found():
    return po_additional("NCT04224987", 48)

def check_po_nct04224987_add49_found():
    return po_additional("NCT04224987", 49)

def check_po_nct04224987_add50_found():
    return po_additional("NCT04224987", 50)

def check_po_nct04224987_add51_found():
    return po_additional("NCT04224987", 51)

def check_po_nct04224987_add52_found():
    return po_additional("NCT04224987", 52)

def check_po_nct04224987_add53_found():
    return po_additional("NCT04224987", 53)

def check_po_nct04224987_add54_found():
    return po_additional("NCT04224987", 54)

def check_po_nct04224987_add55_found():
    return po_additional("NCT04224987", 55)

def check_po_nct04224987_add56_found():
    return po_additional("NCT04224987", 56)

def check_po_nct04224987_add57_found():
    return po_additional("NCT04224987", 57)

def check_po_nct04224987_add58_found():
    return po_additional("NCT04224987", 58)

def check_po_nct04224987_add59_found():
    return po_additional("NCT04224987", 59)

def check_po_nct04224987_add60_found():
    return po_additional("NCT04224987", 60)

def check_po_nct04224987_add61_found():
    return po_additional("NCT04224987", 61)

def check_static_nct04247009_coverage():
    return static_coverage("NCT04247009")

def check_static_nct04247009_basis():
    return static_basis("NCT04247009")

def check_reward_hacking_nct04247009_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04247009")

def check_reward_hacking_nct04247009_result_quote_numeric():
    return rh_result_quote_numeric("NCT04247009")

def check_reward_hacking_nct04247009_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04247009")

def check_reward_hacking_nct04247009_negative_rows_clean():
    return rh_negative_rows_clean("NCT04247009")

def check_reward_hacking_nct04247009_additional_within_bound():
    return rh_additional_within_bound("NCT04247009")

def check_reward_hacking_nct04247009_row_shape_rules():
    return rh_row_shape_rules("NCT04247009")

def check_reward_hacking_nct04247009_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04247009")

def check_po_nct04247009_basis_derived():
    return po_basis_derived("NCT04247009")

def check_static_nct04247009_pri2_registry_fields():
    return static_registry_fields("NCT04247009", "pri2")

def check_po_nct04247009_pri2_reported():
    return po_reported("NCT04247009", "pri2")

def check_static_nct04247009_pri4_registry_fields():
    return static_registry_fields("NCT04247009", "pri4")

def check_po_nct04247009_pri4_reported():
    return po_reported("NCT04247009", "pri4")

def check_static_nct04247009_pri6_registry_fields():
    return static_registry_fields("NCT04247009", "pri6")

def check_po_nct04247009_pri6_reported():
    return po_reported("NCT04247009", "pri6")

def check_static_nct04247009_sec1_registry_fields():
    return static_registry_fields("NCT04247009", "sec1")

def check_po_nct04247009_sec1_reported():
    return po_reported("NCT04247009", "sec1")

def check_static_nct04247009_sec2_registry_fields():
    return static_registry_fields("NCT04247009", "sec2")

def check_po_nct04247009_sec2_reported():
    return po_reported("NCT04247009", "sec2")

def check_static_nct04247009_sec3_registry_fields():
    return static_registry_fields("NCT04247009", "sec3")

def check_po_nct04247009_sec3_reported():
    return po_reported("NCT04247009", "sec3")

def check_static_nct04247009_sec5_registry_fields():
    return static_registry_fields("NCT04247009", "sec5")

def check_po_nct04247009_sec5_reported():
    return po_reported("NCT04247009", "sec5")

def check_static_nct04247009_sec6_registry_fields():
    return static_registry_fields("NCT04247009", "sec6")

def check_po_nct04247009_sec6_reported():
    return po_reported("NCT04247009", "sec6")

def check_static_nct04247009_sec8_registry_fields():
    return static_registry_fields("NCT04247009", "sec8")

def check_po_nct04247009_sec8_reported():
    return po_reported("NCT04247009", "sec8")

def check_static_nct04247009_sec9_registry_fields():
    return static_registry_fields("NCT04247009", "sec9")

def check_po_nct04247009_sec9_reported():
    return po_reported("NCT04247009", "sec9")

def check_static_nct04247009_sec10_registry_fields():
    return static_registry_fields("NCT04247009", "sec10")

def check_po_nct04247009_sec10_reported():
    return po_reported("NCT04247009", "sec10")

def check_po_nct04247009_add0_found():
    return po_additional("NCT04247009", 0)

def check_po_nct04247009_add1_found():
    return po_additional("NCT04247009", 1)

def check_po_nct04247009_add2_found():
    return po_additional("NCT04247009", 2)

def check_po_nct04247009_add3_found():
    return po_additional("NCT04247009", 3)

def check_po_nct04247009_add4_found():
    return po_additional("NCT04247009", 4)

def check_po_nct04247009_add5_found():
    return po_additional("NCT04247009", 5)

def check_po_nct04247009_add6_found():
    return po_additional("NCT04247009", 6)

def check_po_nct04247009_add7_found():
    return po_additional("NCT04247009", 7)

def check_po_nct04247009_add8_found():
    return po_additional("NCT04247009", 8)

def check_po_nct04247009_add9_found():
    return po_additional("NCT04247009", 9)

def check_po_nct04247009_add10_found():
    return po_additional("NCT04247009", 10)

def check_po_nct04247009_add11_found():
    return po_additional("NCT04247009", 11)

def check_po_nct04247009_add12_found():
    return po_additional("NCT04247009", 12)

def check_po_nct04247009_add13_found():
    return po_additional("NCT04247009", 13)

def check_po_nct04247009_add14_found():
    return po_additional("NCT04247009", 14)

def check_po_nct04247009_add15_found():
    return po_additional("NCT04247009", 15)

def check_po_nct04247009_add16_found():
    return po_additional("NCT04247009", 16)

def check_po_nct04247009_add17_found():
    return po_additional("NCT04247009", 17)

def check_po_nct04247009_add18_found():
    return po_additional("NCT04247009", 18)

def check_po_nct04247009_add19_found():
    return po_additional("NCT04247009", 19)

def check_po_nct04247009_add20_found():
    return po_additional("NCT04247009", 20)

def check_po_nct04247009_add21_found():
    return po_additional("NCT04247009", 21)

def check_po_nct04247009_add22_found():
    return po_additional("NCT04247009", 22)

def check_po_nct04247009_add23_found():
    return po_additional("NCT04247009", 23)

def check_po_nct04247009_add24_found():
    return po_additional("NCT04247009", 24)

def check_po_nct04247009_add25_found():
    return po_additional("NCT04247009", 25)

def check_po_nct04247009_add26_found():
    return po_additional("NCT04247009", 26)

def check_po_nct04247009_add27_found():
    return po_additional("NCT04247009", 27)

def check_po_nct04247009_add28_found():
    return po_additional("NCT04247009", 28)

def check_po_nct04247009_add29_found():
    return po_additional("NCT04247009", 29)

def check_po_nct04247009_add30_found():
    return po_additional("NCT04247009", 30)

def check_po_nct04247009_add31_found():
    return po_additional("NCT04247009", 31)

def check_po_nct04247009_add32_found():
    return po_additional("NCT04247009", 32)

def check_po_nct04247009_add33_found():
    return po_additional("NCT04247009", 33)

def check_po_nct04247009_add34_found():
    return po_additional("NCT04247009", 34)

def check_po_nct04247009_add35_found():
    return po_additional("NCT04247009", 35)

def check_po_nct04247009_add36_found():
    return po_additional("NCT04247009", 36)

def check_po_nct04247009_add37_found():
    return po_additional("NCT04247009", 37)

def check_po_nct04247009_add38_found():
    return po_additional("NCT04247009", 38)

def check_po_nct04247009_add39_found():
    return po_additional("NCT04247009", 39)

def check_po_nct04247009_add40_found():
    return po_additional("NCT04247009", 40)

def check_po_nct04247009_add41_found():
    return po_additional("NCT04247009", 41)

def check_po_nct04247009_add42_found():
    return po_additional("NCT04247009", 42)

def check_po_nct04247009_add43_found():
    return po_additional("NCT04247009", 43)

def check_po_nct04247009_add44_found():
    return po_additional("NCT04247009", 44)

def check_po_nct04247009_add45_found():
    return po_additional("NCT04247009", 45)

def check_po_nct04247009_add46_found():
    return po_additional("NCT04247009", 46)

def check_po_nct04247009_add47_found():
    return po_additional("NCT04247009", 47)

def check_po_nct04247009_add48_found():
    return po_additional("NCT04247009", 48)

def check_po_nct04247009_add49_found():
    return po_additional("NCT04247009", 49)

def check_po_nct04247009_add50_found():
    return po_additional("NCT04247009", 50)

def check_po_nct04247009_add51_found():
    return po_additional("NCT04247009", 51)

def check_po_nct04247009_add52_found():
    return po_additional("NCT04247009", 52)

def check_po_nct04247009_add53_found():
    return po_additional("NCT04247009", 53)

def check_po_nct04247009_add54_found():
    return po_additional("NCT04247009", 54)

def check_po_nct04247009_add55_found():
    return po_additional("NCT04247009", 55)

def check_po_nct04247009_add56_found():
    return po_additional("NCT04247009", 56)

def check_po_nct04247009_add57_found():
    return po_additional("NCT04247009", 57)

def check_po_nct04247009_add58_found():
    return po_additional("NCT04247009", 58)

def check_po_nct04247009_add59_found():
    return po_additional("NCT04247009", 59)

def check_po_nct04247009_add60_found():
    return po_additional("NCT04247009", 60)

def check_po_nct04247009_add61_found():
    return po_additional("NCT04247009", 61)

def check_po_nct04247009_add62_found():
    return po_additional("NCT04247009", 62)

def check_static_nct04369326_coverage():
    return static_coverage("NCT04369326")

def check_static_nct04369326_basis():
    return static_basis("NCT04369326")

def check_reward_hacking_nct04369326_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04369326")

def check_reward_hacking_nct04369326_result_quote_numeric():
    return rh_result_quote_numeric("NCT04369326")

def check_reward_hacking_nct04369326_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04369326")

def check_reward_hacking_nct04369326_negative_rows_clean():
    return rh_negative_rows_clean("NCT04369326")

def check_reward_hacking_nct04369326_additional_within_bound():
    return rh_additional_within_bound("NCT04369326")

def check_reward_hacking_nct04369326_row_shape_rules():
    return rh_row_shape_rules("NCT04369326")

def check_reward_hacking_nct04369326_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04369326")

def check_po_nct04369326_basis_derived():
    return po_basis_derived("NCT04369326")

def check_static_nct04369326_sec1_registry_fields():
    return static_registry_fields("NCT04369326", "sec1")

def check_po_nct04369326_sec1_reported():
    return po_reported("NCT04369326", "sec1")

def check_po_nct04369326_sec1_document():
    return po_field("NCT04369326", "sec1", "document")

def check_po_nct04369326_sec1_label():
    return po_field("NCT04369326", "sec1", "label")

def check_po_nct04369326_sec1_role():
    return po_field("NCT04369326", "sec1", "role")

def check_static_nct04369326_sec7_registry_fields():
    return static_registry_fields("NCT04369326", "sec7")

def check_po_nct04369326_sec7_reported():
    return po_reported("NCT04369326", "sec7")

def check_po_nct04369326_sec7_document():
    return po_field("NCT04369326", "sec7", "document")

def check_po_nct04369326_sec7_label():
    return po_field("NCT04369326", "sec7", "label")

def check_po_nct04369326_sec7_role():
    return po_field("NCT04369326", "sec7", "role")

def check_static_nct04369326_sec14_registry_fields():
    return static_registry_fields("NCT04369326", "sec14")

def check_po_nct04369326_sec14_reported():
    return po_reported("NCT04369326", "sec14")

def check_static_nct04369326_sec15_registry_fields():
    return static_registry_fields("NCT04369326", "sec15")

def check_po_nct04369326_sec15_reported():
    return po_reported("NCT04369326", "sec15")

def check_static_nct04369326_sec16_registry_fields():
    return static_registry_fields("NCT04369326", "sec16")

def check_po_nct04369326_sec16_reported():
    return po_reported("NCT04369326", "sec16")

def check_po_nct04369326_add0_found():
    return po_additional("NCT04369326", 0)

def check_po_nct04369326_add1_found():
    return po_additional("NCT04369326", 1)

def check_po_nct04369326_add2_found():
    return po_additional("NCT04369326", 2)

def check_po_nct04369326_add3_found():
    return po_additional("NCT04369326", 3)

def check_po_nct04369326_add4_found():
    return po_additional("NCT04369326", 4)

def check_po_nct04369326_add5_found():
    return po_additional("NCT04369326", 5)

def check_po_nct04369326_add6_found():
    return po_additional("NCT04369326", 6)

def check_po_nct04369326_add7_found():
    return po_additional("NCT04369326", 7)

def check_po_nct04369326_add8_found():
    return po_additional("NCT04369326", 8)

def check_po_nct04369326_add9_found():
    return po_additional("NCT04369326", 9)

def check_po_nct04369326_add10_found():
    return po_additional("NCT04369326", 10)

def check_po_nct04369326_add11_found():
    return po_additional("NCT04369326", 11)

def check_po_nct04369326_add12_found():
    return po_additional("NCT04369326", 12)

def check_po_nct04369326_add13_found():
    return po_additional("NCT04369326", 13)

def check_po_nct04369326_add14_found():
    return po_additional("NCT04369326", 14)

def check_po_nct04369326_add15_found():
    return po_additional("NCT04369326", 15)

def check_po_nct04369326_add16_found():
    return po_additional("NCT04369326", 16)

def check_po_nct04369326_add17_found():
    return po_additional("NCT04369326", 17)

def check_po_nct04369326_add18_found():
    return po_additional("NCT04369326", 18)

def check_po_nct04369326_add19_found():
    return po_additional("NCT04369326", 19)

def check_static_nct04424511_coverage():
    return static_coverage("NCT04424511")

def check_static_nct04424511_basis():
    return static_basis("NCT04424511")

def check_reward_hacking_nct04424511_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT04424511")

def check_reward_hacking_nct04424511_result_quote_numeric():
    return rh_result_quote_numeric("NCT04424511")

def check_reward_hacking_nct04424511_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT04424511")

def check_reward_hacking_nct04424511_negative_rows_clean():
    return rh_negative_rows_clean("NCT04424511")

def check_reward_hacking_nct04424511_additional_within_bound():
    return rh_additional_within_bound("NCT04424511")

def check_reward_hacking_nct04424511_row_shape_rules():
    return rh_row_shape_rules("NCT04424511")

def check_reward_hacking_nct04424511_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT04424511")

def check_po_nct04424511_basis_derived():
    return po_basis_derived("NCT04424511")

def check_static_nct04424511_pri1_registry_fields():
    return static_registry_fields("NCT04424511", "pri1")

def check_po_nct04424511_pri1_reported():
    return po_reported("NCT04424511", "pri1")

def check_static_nct04424511_sec1_registry_fields():
    return static_registry_fields("NCT04424511", "sec1")

def check_po_nct04424511_sec1_reported():
    return po_reported("NCT04424511", "sec1")

def check_static_nct04424511_sec5_registry_fields():
    return static_registry_fields("NCT04424511", "sec5")

def check_po_nct04424511_sec5_reported():
    return po_reported("NCT04424511", "sec5")

def check_static_nct04424511_sec8_registry_fields():
    return static_registry_fields("NCT04424511", "sec8")

def check_po_nct04424511_sec8_reported():
    return po_reported("NCT04424511", "sec8")

def check_static_nct04424511_sec9_registry_fields():
    return static_registry_fields("NCT04424511", "sec9")

def check_po_nct04424511_sec9_reported():
    return po_reported("NCT04424511", "sec9")

def check_static_nct04424511_sec10_registry_fields():
    return static_registry_fields("NCT04424511", "sec10")

def check_po_nct04424511_sec10_reported():
    return po_reported("NCT04424511", "sec10")

def check_static_nct04424511_sec11_registry_fields():
    return static_registry_fields("NCT04424511", "sec11")

def check_po_nct04424511_sec11_reported():
    return po_reported("NCT04424511", "sec11")

def check_static_nct04424511_sec12_registry_fields():
    return static_registry_fields("NCT04424511", "sec12")

def check_po_nct04424511_sec12_reported():
    return po_reported("NCT04424511", "sec12")

def check_static_nct04424511_sec13_registry_fields():
    return static_registry_fields("NCT04424511", "sec13")

def check_po_nct04424511_sec13_reported():
    return po_reported("NCT04424511", "sec13")

def check_static_nct04424511_sec14_registry_fields():
    return static_registry_fields("NCT04424511", "sec14")

def check_po_nct04424511_sec14_reported():
    return po_reported("NCT04424511", "sec14")

def check_static_nct04424511_sec15_registry_fields():
    return static_registry_fields("NCT04424511", "sec15")

def check_po_nct04424511_sec15_reported():
    return po_reported("NCT04424511", "sec15")

def check_static_nct04424511_sec16_registry_fields():
    return static_registry_fields("NCT04424511", "sec16")

def check_po_nct04424511_sec16_reported():
    return po_reported("NCT04424511", "sec16")

def check_static_nct04424511_sec17_registry_fields():
    return static_registry_fields("NCT04424511", "sec17")

def check_po_nct04424511_sec17_reported():
    return po_reported("NCT04424511", "sec17")

def check_static_nct04424511_sec18_registry_fields():
    return static_registry_fields("NCT04424511", "sec18")

def check_po_nct04424511_sec18_reported():
    return po_reported("NCT04424511", "sec18")

def check_static_nct04424511_sec19_registry_fields():
    return static_registry_fields("NCT04424511", "sec19")

def check_po_nct04424511_sec19_reported():
    return po_reported("NCT04424511", "sec19")

def check_po_nct04424511_add0_found():
    return po_additional("NCT04424511", 0)

def check_po_nct04424511_add1_found():
    return po_additional("NCT04424511", 1)

def check_po_nct04424511_add2_found():
    return po_additional("NCT04424511", 2)

def check_po_nct04424511_add3_found():
    return po_additional("NCT04424511", 3)

def check_po_nct04424511_add4_found():
    return po_additional("NCT04424511", 4)

def check_po_nct04424511_add5_found():
    return po_additional("NCT04424511", 5)

def check_po_nct04424511_add6_found():
    return po_additional("NCT04424511", 6)

def check_po_nct04424511_add7_found():
    return po_additional("NCT04424511", 7)

def check_po_nct04424511_add8_found():
    return po_additional("NCT04424511", 8)

def check_po_nct04424511_add9_found():
    return po_additional("NCT04424511", 9)

def check_po_nct04424511_add10_found():
    return po_additional("NCT04424511", 10)

def check_po_nct04424511_add11_found():
    return po_additional("NCT04424511", 11)

def check_po_nct04424511_add12_found():
    return po_additional("NCT04424511", 12)

def check_po_nct04424511_add13_found():
    return po_additional("NCT04424511", 13)

def check_po_nct04424511_add14_found():
    return po_additional("NCT04424511", 14)

def check_po_nct04424511_add15_found():
    return po_additional("NCT04424511", 15)

def check_static_nct05254002_coverage():
    return static_coverage("NCT05254002")

def check_static_nct05254002_basis():
    return static_basis("NCT05254002")

def check_reward_hacking_nct05254002_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT05254002")

def check_reward_hacking_nct05254002_result_quote_numeric():
    return rh_result_quote_numeric("NCT05254002")

def check_reward_hacking_nct05254002_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT05254002")

def check_reward_hacking_nct05254002_negative_rows_clean():
    return rh_negative_rows_clean("NCT05254002")

def check_reward_hacking_nct05254002_additional_within_bound():
    return rh_additional_within_bound("NCT05254002")

def check_reward_hacking_nct05254002_row_shape_rules():
    return rh_row_shape_rules("NCT05254002")

def check_reward_hacking_nct05254002_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT05254002")

def check_po_nct05254002_basis_derived():
    return po_basis_derived("NCT05254002")

def check_static_nct05254002_pri1_registry_fields():
    return static_registry_fields("NCT05254002", "pri1")

def check_po_nct05254002_pri1_reported():
    return po_reported("NCT05254002", "pri1")

def check_po_nct05254002_pri1_document():
    return po_field("NCT05254002", "pri1", "document")

def check_po_nct05254002_pri1_label():
    return po_field("NCT05254002", "pri1", "label")

def check_po_nct05254002_pri1_instrument():
    return po_field("NCT05254002", "pri1", "instrument")

def check_po_nct05254002_pri1_role():
    return po_field("NCT05254002", "pri1", "role")

def check_static_nct05254002_pri2_registry_fields():
    return static_registry_fields("NCT05254002", "pri2")

def check_po_nct05254002_pri2_reported():
    return po_reported("NCT05254002", "pri2")

def check_po_nct05254002_pri2_document():
    return po_field("NCT05254002", "pri2", "document")

def check_po_nct05254002_pri2_label():
    return po_field("NCT05254002", "pri2", "label")

def check_po_nct05254002_pri2_instrument():
    return po_field("NCT05254002", "pri2", "instrument")

def check_po_nct05254002_pri2_role():
    return po_field("NCT05254002", "pri2", "role")

def check_static_nct05254002_sec3_registry_fields():
    return static_registry_fields("NCT05254002", "sec3")

def check_po_nct05254002_sec3_reported():
    return po_reported("NCT05254002", "sec3")

def check_po_nct05254002_sec3_document():
    return po_field("NCT05254002", "sec3", "document")

def check_po_nct05254002_sec3_label():
    return po_field("NCT05254002", "sec3", "label")

def check_po_nct05254002_sec3_instrument():
    return po_field("NCT05254002", "sec3", "instrument")

def check_po_nct05254002_sec3_role():
    return po_field("NCT05254002", "sec3", "role")

def check_static_nct05254002_sec5_registry_fields():
    return static_registry_fields("NCT05254002", "sec5")

def check_po_nct05254002_sec5_reported():
    return po_reported("NCT05254002", "sec5")

def check_po_nct05254002_sec5_document():
    return po_field("NCT05254002", "sec5", "document")

def check_po_nct05254002_sec5_label():
    return po_field("NCT05254002", "sec5", "label")

def check_po_nct05254002_sec5_instrument():
    return po_field("NCT05254002", "sec5", "instrument")

def check_po_nct05254002_sec5_role():
    return po_field("NCT05254002", "sec5", "role")

def check_static_nct05254002_sec7_registry_fields():
    return static_registry_fields("NCT05254002", "sec7")

def check_po_nct05254002_sec7_reported():
    return po_reported("NCT05254002", "sec7")

def check_po_nct05254002_sec7_document():
    return po_field("NCT05254002", "sec7", "document")

def check_po_nct05254002_sec7_label():
    return po_field("NCT05254002", "sec7", "label")

def check_po_nct05254002_sec7_role():
    return po_field("NCT05254002", "sec7", "role")

def check_static_nct05254002_sec8_registry_fields():
    return static_registry_fields("NCT05254002", "sec8")

def check_po_nct05254002_sec8_reported():
    return po_reported("NCT05254002", "sec8")

def check_static_nct05254002_sec9_registry_fields():
    return static_registry_fields("NCT05254002", "sec9")

def check_po_nct05254002_sec9_reported():
    return po_reported("NCT05254002", "sec9")

def check_po_nct05254002_sec9_document():
    return po_field("NCT05254002", "sec9", "document")

def check_po_nct05254002_sec9_label():
    return po_field("NCT05254002", "sec9", "label")

def check_po_nct05254002_sec9_role():
    return po_field("NCT05254002", "sec9", "role")

def check_static_nct05254002_sec11_registry_fields():
    return static_registry_fields("NCT05254002", "sec11")

def check_po_nct05254002_sec11_reported():
    return po_reported("NCT05254002", "sec11")

def check_static_nct05254002_sec14_registry_fields():
    return static_registry_fields("NCT05254002", "sec14")

def check_po_nct05254002_sec14_reported():
    return po_reported("NCT05254002", "sec14")

def check_po_nct05254002_sec14_document():
    return po_field("NCT05254002", "sec14", "document")

def check_po_nct05254002_sec14_label():
    return po_field("NCT05254002", "sec14", "label")

def check_po_nct05254002_sec14_role():
    return po_field("NCT05254002", "sec14", "role")

def check_static_nct05254002_sec16_registry_fields():
    return static_registry_fields("NCT05254002", "sec16")

def check_po_nct05254002_sec16_reported():
    return po_reported("NCT05254002", "sec16")

def check_po_nct05254002_sec16_document():
    return po_field("NCT05254002", "sec16", "document")

def check_po_nct05254002_sec16_label():
    return po_field("NCT05254002", "sec16", "label")

def check_po_nct05254002_sec16_role():
    return po_field("NCT05254002", "sec16", "role")

def check_static_nct05254002_sec18_registry_fields():
    return static_registry_fields("NCT05254002", "sec18")

def check_po_nct05254002_sec18_reported():
    return po_reported("NCT05254002", "sec18")

def check_static_nct05254002_sec19_registry_fields():
    return static_registry_fields("NCT05254002", "sec19")

def check_po_nct05254002_sec19_reported():
    return po_reported("NCT05254002", "sec19")

def check_static_nct05254002_sec20_registry_fields():
    return static_registry_fields("NCT05254002", "sec20")

def check_po_nct05254002_sec20_reported():
    return po_reported("NCT05254002", "sec20")

def check_static_nct05254002_sec21_registry_fields():
    return static_registry_fields("NCT05254002", "sec21")

def check_po_nct05254002_sec21_reported():
    return po_reported("NCT05254002", "sec21")

def check_static_nct05254002_sec22_registry_fields():
    return static_registry_fields("NCT05254002", "sec22")

def check_po_nct05254002_sec22_reported():
    return po_reported("NCT05254002", "sec22")

def check_po_nct05254002_sec22_document():
    return po_field("NCT05254002", "sec22", "document")

def check_po_nct05254002_sec22_label():
    return po_field("NCT05254002", "sec22", "label")

def check_po_nct05254002_sec22_role():
    return po_field("NCT05254002", "sec22", "role")

def check_po_nct05254002_add0_found():
    return po_additional("NCT05254002", 0)

def check_po_nct05254002_add1_found():
    return po_additional("NCT05254002", 1)

def check_po_nct05254002_add2_found():
    return po_additional("NCT05254002", 2)

def check_po_nct05254002_add3_found():
    return po_additional("NCT05254002", 3)

def check_po_nct05254002_add4_found():
    return po_additional("NCT05254002", 4)

def check_po_nct05254002_add5_found():
    return po_additional("NCT05254002", 5)

def check_po_nct05254002_add6_found():
    return po_additional("NCT05254002", 6)

def check_po_nct05254002_add7_found():
    return po_additional("NCT05254002", 7)

def check_po_nct05254002_add8_found():
    return po_additional("NCT05254002", 8)

def check_po_nct05254002_add9_found():
    return po_additional("NCT05254002", 9)

def check_po_nct05254002_add10_found():
    return po_additional("NCT05254002", 10)

def check_po_nct05254002_add11_found():
    return po_additional("NCT05254002", 11)

def check_po_nct05254002_add12_found():
    return po_additional("NCT05254002", 12)

def check_po_nct05254002_add13_found():
    return po_additional("NCT05254002", 13)

def check_po_nct05254002_add14_found():
    return po_additional("NCT05254002", 14)

def check_po_nct05254002_add15_found():
    return po_additional("NCT05254002", 15)

def check_po_nct05254002_add16_found():
    return po_additional("NCT05254002", 16)

def check_po_nct05254002_add17_found():
    return po_additional("NCT05254002", 17)

def check_po_nct05254002_add18_found():
    return po_additional("NCT05254002", 18)

def check_static_nct05485402_coverage():
    return static_coverage("NCT05485402")

def check_static_nct05485402_basis():
    return static_basis("NCT05485402")

def check_reward_hacking_nct05485402_result_quote_verbatim():
    return rh_result_quote_verbatim("NCT05485402")

def check_reward_hacking_nct05485402_result_quote_numeric():
    return rh_result_quote_numeric("NCT05485402")

def check_reward_hacking_nct05485402_role_quote_verbatim():
    return rh_role_quote_verbatim("NCT05485402")

def check_reward_hacking_nct05485402_negative_rows_clean():
    return rh_negative_rows_clean("NCT05485402")

def check_reward_hacking_nct05485402_additional_within_bound():
    return rh_additional_within_bound("NCT05485402")

def check_reward_hacking_nct05485402_row_shape_rules():
    return rh_row_shape_rules("NCT05485402")

def check_reward_hacking_nct05485402_distinct_result_quotes():
    return rh_distinct_result_quotes("NCT05485402")

def check_po_nct05485402_basis_derived():
    return po_basis_derived("NCT05485402")

def check_static_nct05485402_pri1_registry_fields():
    return static_registry_fields("NCT05485402", "pri1")

def check_po_nct05485402_pri1_reported():
    return po_reported("NCT05485402", "pri1")

def check_po_nct05485402_pri1_document():
    return po_field("NCT05485402", "pri1", "document")

def check_po_nct05485402_pri1_label():
    return po_field("NCT05485402", "pri1", "label")

def check_po_nct05485402_pri1_instrument():
    return po_field("NCT05485402", "pri1", "instrument")

def check_po_nct05485402_pri1_role():
    return po_field("NCT05485402", "pri1", "role")

def check_static_nct05485402_sec1_registry_fields():
    return static_registry_fields("NCT05485402", "sec1")

def check_po_nct05485402_sec1_reported():
    return po_reported("NCT05485402", "sec1")

def check_po_nct05485402_sec1_document():
    return po_field("NCT05485402", "sec1", "document")

def check_po_nct05485402_sec1_label():
    return po_field("NCT05485402", "sec1", "label")

def check_po_nct05485402_sec1_instrument():
    return po_field("NCT05485402", "sec1", "instrument")

def check_po_nct05485402_sec1_role():
    return po_field("NCT05485402", "sec1", "role")

def check_static_nct05485402_sec2_registry_fields():
    return static_registry_fields("NCT05485402", "sec2")

def check_po_nct05485402_sec2_reported():
    return po_reported("NCT05485402", "sec2")

def check_static_nct05485402_sec3_registry_fields():
    return static_registry_fields("NCT05485402", "sec3")

def check_po_nct05485402_sec3_reported():
    return po_reported("NCT05485402", "sec3")

def check_po_nct05485402_sec3_document():
    return po_field("NCT05485402", "sec3", "document")

def check_po_nct05485402_sec3_label():
    return po_field("NCT05485402", "sec3", "label")

def check_po_nct05485402_sec3_instrument():
    return po_field("NCT05485402", "sec3", "instrument")

def check_po_nct05485402_sec3_role():
    return po_field("NCT05485402", "sec3", "role")

def check_static_nct05485402_sec4_registry_fields():
    return static_registry_fields("NCT05485402", "sec4")

def check_po_nct05485402_sec4_reported():
    return po_reported("NCT05485402", "sec4")

def check_po_nct05485402_sec4_document():
    return po_field("NCT05485402", "sec4", "document")

def check_po_nct05485402_sec4_label():
    return po_field("NCT05485402", "sec4", "label")

def check_po_nct05485402_sec4_instrument():
    return po_field("NCT05485402", "sec4", "instrument")

def check_po_nct05485402_sec4_role():
    return po_field("NCT05485402", "sec4", "role")

def check_static_nct05485402_sec5_registry_fields():
    return static_registry_fields("NCT05485402", "sec5")

def check_po_nct05485402_sec5_reported():
    return po_reported("NCT05485402", "sec5")

def check_static_nct05485402_sec7_registry_fields():
    return static_registry_fields("NCT05485402", "sec7")

def check_po_nct05485402_sec7_reported():
    return po_reported("NCT05485402", "sec7")

def check_po_nct05485402_sec7_document():
    return po_field("NCT05485402", "sec7", "document")

def check_po_nct05485402_sec7_label():
    return po_field("NCT05485402", "sec7", "label")

def check_po_nct05485402_sec7_instrument():
    return po_field("NCT05485402", "sec7", "instrument")

def check_po_nct05485402_sec7_role():
    return po_field("NCT05485402", "sec7", "role")

def check_static_nct05485402_sec9_registry_fields():
    return static_registry_fields("NCT05485402", "sec9")

def check_po_nct05485402_sec9_reported():
    return po_reported("NCT05485402", "sec9")

def check_po_nct05485402_sec9_document():
    return po_field("NCT05485402", "sec9", "document")

def check_po_nct05485402_sec9_label():
    return po_field("NCT05485402", "sec9", "label")

def check_po_nct05485402_sec9_instrument():
    return po_field("NCT05485402", "sec9", "instrument")

def check_po_nct05485402_sec9_role():
    return po_field("NCT05485402", "sec9", "role")

def check_static_nct05485402_sec10_registry_fields():
    return static_registry_fields("NCT05485402", "sec10")

def check_po_nct05485402_sec10_reported():
    return po_reported("NCT05485402", "sec10")

def check_static_nct05485402_sec11_registry_fields():
    return static_registry_fields("NCT05485402", "sec11")

def check_po_nct05485402_sec11_reported():
    return po_reported("NCT05485402", "sec11")

def check_static_nct05485402_sec12_registry_fields():
    return static_registry_fields("NCT05485402", "sec12")

def check_po_nct05485402_sec12_reported():
    return po_reported("NCT05485402", "sec12")

def check_static_nct05485402_sec13_registry_fields():
    return static_registry_fields("NCT05485402", "sec13")

def check_po_nct05485402_sec13_reported():
    return po_reported("NCT05485402", "sec13")

def check_static_nct05485402_sec15_registry_fields():
    return static_registry_fields("NCT05485402", "sec15")

def check_po_nct05485402_sec15_reported():
    return po_reported("NCT05485402", "sec15")

def check_static_nct05485402_sec16_registry_fields():
    return static_registry_fields("NCT05485402", "sec16")

def check_po_nct05485402_sec16_reported():
    return po_reported("NCT05485402", "sec16")

def check_static_nct05485402_sec17_registry_fields():
    return static_registry_fields("NCT05485402", "sec17")

def check_po_nct05485402_sec17_reported():
    return po_reported("NCT05485402", "sec17")

def check_static_nct05485402_sec18_registry_fields():
    return static_registry_fields("NCT05485402", "sec18")

def check_po_nct05485402_sec18_reported():
    return po_reported("NCT05485402", "sec18")

def check_static_nct05485402_sec19_registry_fields():
    return static_registry_fields("NCT05485402", "sec19")

def check_po_nct05485402_sec19_reported():
    return po_reported("NCT05485402", "sec19")

def check_static_nct05485402_sec20_registry_fields():
    return static_registry_fields("NCT05485402", "sec20")

def check_po_nct05485402_sec20_reported():
    return po_reported("NCT05485402", "sec20")

def check_static_nct05485402_sec21_registry_fields():
    return static_registry_fields("NCT05485402", "sec21")

def check_po_nct05485402_sec21_reported():
    return po_reported("NCT05485402", "sec21")

def check_static_nct05485402_sec23_registry_fields():
    return static_registry_fields("NCT05485402", "sec23")

def check_po_nct05485402_sec23_reported():
    return po_reported("NCT05485402", "sec23")

def check_static_nct05485402_sec24_registry_fields():
    return static_registry_fields("NCT05485402", "sec24")

def check_po_nct05485402_sec24_reported():
    return po_reported("NCT05485402", "sec24")

def check_static_nct05485402_sec25_registry_fields():
    return static_registry_fields("NCT05485402", "sec25")

def check_po_nct05485402_sec25_reported():
    return po_reported("NCT05485402", "sec25")

def check_static_nct05485402_sec26_registry_fields():
    return static_registry_fields("NCT05485402", "sec26")

def check_po_nct05485402_sec26_reported():
    return po_reported("NCT05485402", "sec26")

def check_static_nct05485402_sec27_registry_fields():
    return static_registry_fields("NCT05485402", "sec27")

def check_po_nct05485402_sec27_reported():
    return po_reported("NCT05485402", "sec27")

def check_static_nct05485402_sec28_registry_fields():
    return static_registry_fields("NCT05485402", "sec28")

def check_po_nct05485402_sec28_reported():
    return po_reported("NCT05485402", "sec28")

def check_static_nct05485402_sec29_registry_fields():
    return static_registry_fields("NCT05485402", "sec29")

def check_po_nct05485402_sec29_reported():
    return po_reported("NCT05485402", "sec29")

def check_static_nct05485402_sec31_registry_fields():
    return static_registry_fields("NCT05485402", "sec31")

def check_po_nct05485402_sec31_reported():
    return po_reported("NCT05485402", "sec31")

def check_static_nct05485402_sec32_registry_fields():
    return static_registry_fields("NCT05485402", "sec32")

def check_po_nct05485402_sec32_reported():
    return po_reported("NCT05485402", "sec32")

def check_static_nct05485402_sec33_registry_fields():
    return static_registry_fields("NCT05485402", "sec33")

def check_po_nct05485402_sec33_reported():
    return po_reported("NCT05485402", "sec33")

def check_po_nct05485402_sec33_document():
    return po_field("NCT05485402", "sec33", "document")

def check_po_nct05485402_sec33_label():
    return po_field("NCT05485402", "sec33", "label")

def check_po_nct05485402_sec33_role():
    return po_field("NCT05485402", "sec33", "role")

def check_static_nct05485402_sec34_registry_fields():
    return static_registry_fields("NCT05485402", "sec34")

def check_po_nct05485402_sec34_reported():
    return po_reported("NCT05485402", "sec34")

def check_static_nct05485402_sec36_registry_fields():
    return static_registry_fields("NCT05485402", "sec36")

def check_po_nct05485402_sec36_reported():
    return po_reported("NCT05485402", "sec36")

def check_static_nct05485402_sec37_registry_fields():
    return static_registry_fields("NCT05485402", "sec37")

def check_po_nct05485402_sec37_reported():
    return po_reported("NCT05485402", "sec37")

def check_static_nct05485402_sec38_registry_fields():
    return static_registry_fields("NCT05485402", "sec38")

def check_po_nct05485402_sec38_reported():
    return po_reported("NCT05485402", "sec38")

def check_po_nct05485402_add0_found():
    return po_additional("NCT05485402", 0)

def check_po_nct05485402_add1_found():
    return po_additional("NCT05485402", 1)

def check_po_nct05485402_add2_found():
    return po_additional("NCT05485402", 2)

def check_po_nct05485402_add3_found():
    return po_additional("NCT05485402", 3)

def check_po_nct05485402_add4_found():
    return po_additional("NCT05485402", 4)

def check_po_nct05485402_add5_found():
    return po_additional("NCT05485402", 5)

def check_po_nct05485402_add6_found():
    return po_additional("NCT05485402", 6)

def check_po_nct05485402_add7_found():
    return po_additional("NCT05485402", 7)

def check_po_nct05485402_add8_found():
    return po_additional("NCT05485402", 8)

def check_po_nct05485402_add9_found():
    return po_additional("NCT05485402", 9)

def check_po_nct05485402_add10_found():
    return po_additional("NCT05485402", 10)

def check_po_nct05485402_add11_found():
    return po_additional("NCT05485402", 11)

def check_po_nct05485402_add12_found():
    return po_additional("NCT05485402", 12)

def check_po_nct05485402_add13_found():
    return po_additional("NCT05485402", 13)

def check_po_nct05485402_add14_found():
    return po_additional("NCT05485402", 14)

def check_po_nct05485402_add15_found():
    return po_additional("NCT05485402", 15)

def check_po_nct05485402_add16_found():
    return po_additional("NCT05485402", 16)

def check_po_nct05485402_add17_found():
    return po_additional("NCT05485402", 17)

def check_po_nct05485402_add18_found():
    return po_additional("NCT05485402", 18)

def check_po_nct05485402_add19_found():
    return po_additional("NCT05485402", 19)

def check_po_nct05485402_add20_found():
    return po_additional("NCT05485402", 20)

def check_po_nct05485402_add21_found():
    return po_additional("NCT05485402", 21)

def check_po_nct05485402_add22_found():
    return po_additional("NCT05485402", 22)

def check_po_nct05485402_add23_found():
    return po_additional("NCT05485402", 23)

def check_po_nct05485402_add24_found():
    return po_additional("NCT05485402", 24)

def check_po_nct05485402_add25_found():
    return po_additional("NCT05485402", 25)

def check_po_nct05485402_add26_found():
    return po_additional("NCT05485402", 26)

def check_po_nct05485402_add27_found():
    return po_additional("NCT05485402", 27)

def check_po_nct05485402_add28_found():
    return po_additional("NCT05485402", 28)

def check_po_nct05485402_add29_found():
    return po_additional("NCT05485402", 29)

def check_po_nct05485402_add30_found():
    return po_additional("NCT05485402", 30)

def check_po_nct05485402_add31_found():
    return po_additional("NCT05485402", 31)

def check_po_nct05485402_add32_found():
    return po_additional("NCT05485402", 32)

def check_po_nct05485402_add33_found():
    return po_additional("NCT05485402", 33)

def check_po_nct05485402_add34_found():
    return po_additional("NCT05485402", 34)

def check_po_nct05485402_add35_found():
    return po_additional("NCT05485402", 35)

def check_po_nct05485402_add36_found():
    return po_additional("NCT05485402", 36)

def check_po_nct05485402_add37_found():
    return po_additional("NCT05485402", 37)

def check_po_nct05485402_add38_found():
    return po_additional("NCT05485402", 38)

def check_po_nct05485402_add39_found():
    return po_additional("NCT05485402", 39)

def check_po_nct05485402_add40_found():
    return po_additional("NCT05485402", 40)

def check_po_nct05485402_add41_found():
    return po_additional("NCT05485402", 41)

def check_po_nct05485402_add42_found():
    return po_additional("NCT05485402", 42)

def check_po_nct05485402_add43_found():
    return po_additional("NCT05485402", 43)

def check_po_nct05485402_add44_found():
    return po_additional("NCT05485402", 44)

def check_po_nct05485402_add45_found():
    return po_additional("NCT05485402", 45)

def check_po_nct05485402_add46_found():
    return po_additional("NCT05485402", 46)

def check_po_nct05485402_add47_found():
    return po_additional("NCT05485402", 47)

def check_po_nct05485402_add48_found():
    return po_additional("NCT05485402", 48)

def check_po_nct05485402_add49_found():
    return po_additional("NCT05485402", 49)

def check_po_nct05485402_add50_found():
    return po_additional("NCT05485402", 50)

def check_po_nct05485402_add51_found():
    return po_additional("NCT05485402", 51)

def check_po_nct05485402_add52_found():
    return po_additional("NCT05485402", 52)

def check_po_nct05485402_add53_found():
    return po_additional("NCT05485402", 53)

def check_po_nct05485402_add54_found():
    return po_additional("NCT05485402", 54)

def check_po_nct05485402_add55_found():
    return po_additional("NCT05485402", 55)

def check_po_nct05485402_add56_found():
    return po_additional("NCT05485402", 56)

def check_po_nct05485402_add57_found():
    return po_additional("NCT05485402", 57)

def check_po_nct05485402_add58_found():
    return po_additional("NCT05485402", 58)

def check_po_nct05485402_add59_found():
    return po_additional("NCT05485402", 59)

def check_po_nct05485402_add60_found():
    return po_additional("NCT05485402", 60)

def check_po_nct05485402_add61_found():
    return po_additional("NCT05485402", 61)

def check_po_nct05485402_add62_found():
    return po_additional("NCT05485402", 62)

def check_po_nct05485402_add63_found():
    return po_additional("NCT05485402", 63)

def check_po_nct05485402_add64_found():
    return po_additional("NCT05485402", 64)

def check_po_nct05485402_add65_found():
    return po_additional("NCT05485402", 65)

def check_po_nct05485402_add66_found():
    return po_additional("NCT05485402", 66)

def check_po_nct05485402_add67_found():
    return po_additional("NCT05485402", 67)

def check_po_nct05485402_add68_found():
    return po_additional("NCT05485402", 68)

def check_po_nct05485402_add69_found():
    return po_additional("NCT05485402", 69)

def check_po_nct05485402_add70_found():
    return po_additional("NCT05485402", 70)

def check_po_nct05485402_add71_found():
    return po_additional("NCT05485402", 71)

def check_po_nct05485402_add72_found():
    return po_additional("NCT05485402", 72)

def check_po_nct05485402_add73_found():
    return po_additional("NCT05485402", 73)

def check_po_nct05485402_add74_found():
    return po_additional("NCT05485402", 74)

def check_po_nct05485402_add75_found():
    return po_additional("NCT05485402", 75)

def check_po_nct05485402_add76_found():
    return po_additional("NCT05485402", 76)

def check_po_nct05485402_add77_found():
    return po_additional("NCT05485402", 77)

def check_po_nct05485402_add78_found():
    return po_additional("NCT05485402", 78)

def check_po_nct05485402_add79_found():
    return po_additional("NCT05485402", 79)

def check_po_nct05485402_add80_found():
    return po_additional("NCT05485402", 80)

def check_po_nct05485402_add81_found():
    return po_additional("NCT05485402", 81)

def check_po_nct05485402_add82_found():
    return po_additional("NCT05485402", 82)

def check_po_nct05485402_add83_found():
    return po_additional("NCT05485402", 83)

def check_po_nct05485402_add84_found():
    return po_additional("NCT05485402", 84)

def check_po_nct05485402_add85_found():
    return po_additional("NCT05485402", 85)

def check_po_nct05485402_add86_found():
    return po_additional("NCT05485402", 86)

def check_po_nct05485402_add87_found():
    return po_additional("NCT05485402", 87)

def check_po_nct05485402_add88_found():
    return po_additional("NCT05485402", 88)

def check_po_nct05485402_add89_found():
    return po_additional("NCT05485402", 89)

def check_po_nct05485402_add90_found():
    return po_additional("NCT05485402", 90)

def check_po_nct05485402_add91_found():
    return po_additional("NCT05485402", 91)

def check_po_nct05485402_add92_found():
    return po_additional("NCT05485402", 92)

def check_po_nct05485402_add93_found():
    return po_additional("NCT05485402", 93)

def check_po_nct05485402_add94_found():
    return po_additional("NCT05485402", 94)

def check_po_nct05485402_add95_found():
    return po_additional("NCT05485402", 95)

def check_po_nct05485402_add96_found():
    return po_additional("NCT05485402", 96)

def check_po_nct05485402_add97_found():
    return po_additional("NCT05485402", 97)

def check_po_nct05485402_add98_found():
    return po_additional("NCT05485402", 98)

def check_po_nct05485402_add99_found():
    return po_additional("NCT05485402", 99)

STATIC_CHECKS = [
    check_static_nct02048007_coverage,
    check_static_nct02048007_basis,
    check_static_nct02048007_pri1_registry_fields,
    check_static_nct02048007_pri2_registry_fields,
    check_static_nct02048007_pri5_registry_fields,
    check_static_nct02048007_pri6_registry_fields,
    check_static_nct02048007_pri7_registry_fields,
    check_static_nct02048007_sec1_registry_fields,
    check_static_nct02048007_sec2_registry_fields,
    check_static_nct02048007_sec3_registry_fields,
    check_static_nct02048007_sec5_registry_fields,
    check_static_nct02048007_sec6_registry_fields,
    check_static_nct02048007_sec10_registry_fields,
    check_static_nct02048007_sec14_registry_fields,
    check_static_nct02048007_sec15_registry_fields,
    check_static_nct02048007_sec16_registry_fields,
    check_static_nct02048007_sec17_registry_fields,
    check_static_nct02048007_sec20_registry_fields,
    check_static_nct02048007_sec21_registry_fields,
    check_static_nct02048007_sec22_registry_fields,
    check_static_nct02048007_sec23_registry_fields,
    check_static_nct02048007_sec24_registry_fields,
    check_static_nct02048007_sec25_registry_fields,
    check_static_nct02048007_sec27_registry_fields,
    check_static_nct02048007_sec28_registry_fields,
    check_static_nct02048007_sec29_registry_fields,
    check_static_nct02391337_coverage,
    check_static_nct02391337_basis,
    check_static_nct02391337_sec1_registry_fields,
    check_static_nct02391337_sec2_registry_fields,
    check_static_nct02391337_sec4_registry_fields,
    check_static_nct02391337_sec8_registry_fields,
    check_static_nct02391337_oth2_registry_fields,
    check_static_nct02391337_oth3_registry_fields,
    check_static_nct02391337_oth4_registry_fields,
    check_static_nct02391337_oth5_registry_fields,
    check_static_nct02391337_oth6_registry_fields,
    check_static_nct02391337_oth7_registry_fields,
    check_static_nct02391337_oth8_registry_fields,
    check_static_nct02391337_oth9_registry_fields,
    check_static_nct02391337_oth10_registry_fields,
    check_static_nct02391337_oth11_registry_fields,
    check_static_nct02409680_coverage,
    check_static_nct02409680_basis,
    check_static_nct02409680_pri1_registry_fields,
    check_static_nct02409680_sec2_registry_fields,
    check_static_nct02409680_sec3_registry_fields,
    check_static_nct02409680_oth12_registry_fields,
    check_static_nct02429180_coverage,
    check_static_nct02429180_basis,
    check_static_nct02429180_pri1_registry_fields,
    check_static_nct02429180_pri2_registry_fields,
    check_static_nct02429180_pri3_registry_fields,
    check_static_nct02429180_pri4_registry_fields,
    check_static_nct02429180_pri5_registry_fields,
    check_static_nct02429180_sec1_registry_fields,
    check_static_nct02429180_sec2_registry_fields,
    check_static_nct02429180_sec3_registry_fields,
    check_static_nct02429180_sec4_registry_fields,
    check_static_nct02429180_sec5_registry_fields,
    check_static_nct02429180_sec6_registry_fields,
    check_static_nct02429180_sec8_registry_fields,
    check_static_nct02429180_sec9_registry_fields,
    check_static_nct02429180_sec10_registry_fields,
    check_static_nct02429180_oth1_registry_fields,
    check_static_nct02584283_coverage,
    check_static_nct02584283_basis,
    check_static_nct02584283_pri1_registry_fields,
    check_static_nct02584283_sec1_registry_fields,
    check_static_nct02584283_sec4_registry_fields,
    check_static_nct02584283_sec5_registry_fields,
    check_static_nct02584283_sec7_registry_fields,
    check_static_nct02584283_sec8_registry_fields,
    check_static_nct02584283_sec9_registry_fields,
    check_static_nct02584283_sec10_registry_fields,
    check_static_nct02584283_sec13_registry_fields,
    check_static_nct02584283_sec14_registry_fields,
    check_static_nct02584283_sec15_registry_fields,
    check_static_nct02584283_sec16_registry_fields,
    check_static_nct02584283_sec17_registry_fields,
    check_static_nct02584283_sec18_registry_fields,
    check_static_nct02584283_sec19_registry_fields,
    check_static_nct02584283_sec20_registry_fields,
    check_static_nct02584283_sec21_registry_fields,
    check_static_nct02584283_sec22_registry_fields,
    check_static_nct02584283_sec23_registry_fields,
    check_static_nct02584283_sec24_registry_fields,
    check_static_nct02584283_sec25_registry_fields,
    check_static_nct02584283_sec26_registry_fields,
    check_static_nct02584283_sec27_registry_fields,
    check_static_nct02584283_sec28_registry_fields,
    check_static_nct02584283_sec29_registry_fields,
    check_static_nct02584283_sec30_registry_fields,
    check_static_nct02584283_sec31_registry_fields,
    check_static_nct02584283_sec32_registry_fields,
    check_static_nct02584283_sec33_registry_fields,
    check_static_nct02584283_sec34_registry_fields,
    check_static_nct02584283_sec35_registry_fields,
    check_static_nct02584283_sec36_registry_fields,
    check_static_nct02584283_sec39_registry_fields,
    check_static_nct02747927_coverage,
    check_static_nct02747927_basis,
    check_static_nct02747927_pri1_registry_fields,
    check_static_nct02747927_sec4_registry_fields,
    check_static_nct02747927_sec6_registry_fields,
    check_static_nct02747927_sec7_registry_fields,
    check_static_nct02747927_sec8_registry_fields,
    check_static_nct02747927_sec9_registry_fields,
    check_static_nct02747927_sec11_registry_fields,
    check_static_nct02747927_sec15_registry_fields,
    check_static_nct02944682_coverage,
    check_static_nct02944682_basis,
    check_static_nct02944682_pri1_registry_fields,
    check_static_nct02944682_pri3_registry_fields,
    check_static_nct02944682_pri4_registry_fields,
    check_static_nct02944682_sec2_registry_fields,
    check_static_nct02944682_sec4_registry_fields,
    check_static_nct02944682_sec5_registry_fields,
    check_static_nct02944682_sec6_registry_fields,
    check_static_nct02944682_sec7_registry_fields,
    check_static_nct02944682_oth2_registry_fields,
    check_static_nct02944682_oth3_registry_fields,
    check_static_nct03114917_coverage,
    check_static_nct03114917_basis,
    check_static_nct03114917_pri1_registry_fields,
    check_static_nct03114917_sec3_registry_fields,
    check_static_nct03114917_sec4_registry_fields,
    check_static_nct03114917_oth1_registry_fields,
    check_static_nct03114917_oth2_registry_fields,
    check_static_nct03114917_oth3_registry_fields,
    check_static_nct03114917_oth5_registry_fields,
    check_static_nct03114917_oth6_registry_fields,
    check_static_nct03114917_oth7_registry_fields,
    check_static_nct03114917_oth8_registry_fields,
    check_static_nct03114917_oth9_registry_fields,
    check_static_nct03114917_oth10_registry_fields,
    check_static_nct03114917_oth11_registry_fields,
    check_static_nct03114917_oth12_registry_fields,
    check_static_nct03114917_oth13_registry_fields,
    check_static_nct03114917_oth14_registry_fields,
    check_static_nct03114917_oth15_registry_fields,
    check_static_nct03114917_oth16_registry_fields,
    check_static_nct03114917_oth17_registry_fields,
    check_static_nct03114917_oth18_registry_fields,
    check_static_nct03148457_coverage,
    check_static_nct03148457_basis,
    check_static_nct03148457_sec1_registry_fields,
    check_static_nct03148457_sec2_registry_fields,
    check_static_nct03148457_sec3_registry_fields,
    check_static_nct03148457_sec4_registry_fields,
    check_static_nct03148457_sec5_registry_fields,
    check_static_nct03148457_sec6_registry_fields,
    check_static_nct03148457_sec7_registry_fields,
    check_static_nct03148457_sec8_registry_fields,
    check_static_nct03148457_sec10_registry_fields,
    check_static_nct03148457_sec12_registry_fields,
    check_static_nct03148457_sec13_registry_fields,
    check_static_nct03148457_sec15_registry_fields,
    check_static_nct03198585_coverage,
    check_static_nct03198585_basis,
    check_static_nct03198585_pri1_registry_fields,
    check_static_nct03198585_sec1_registry_fields,
    check_static_nct03198585_sec2_registry_fields,
    check_static_nct03198585_sec4_registry_fields,
    check_static_nct03198585_sec5_registry_fields,
    check_static_nct03198585_sec6_registry_fields,
    check_static_nct03198585_sec7_registry_fields,
    check_static_nct03198585_sec8_registry_fields,
    check_static_nct03198585_sec9_registry_fields,
    check_static_nct03198585_sec12_registry_fields,
    check_static_nct03198585_sec13_registry_fields,
    check_static_nct03198585_sec14_registry_fields,
    check_static_nct03198585_sec15_registry_fields,
    check_static_nct03502616_coverage,
    check_static_nct03502616_basis,
    check_static_nct03502616_pri1_registry_fields,
    check_static_nct03502616_sec1_registry_fields,
    check_static_nct03502616_sec2_registry_fields,
    check_static_nct03502616_sec3_registry_fields,
    check_static_nct03502616_sec6_registry_fields,
    check_static_nct03502616_sec9_registry_fields,
    check_static_nct03502616_sec10_registry_fields,
    check_static_nct03502616_sec11_registry_fields,
    check_static_nct03502616_sec12_registry_fields,
    check_static_nct03502616_sec13_registry_fields,
    check_static_nct03502616_sec14_registry_fields,
    check_static_nct03502616_sec15_registry_fields,
    check_static_nct03502616_sec16_registry_fields,
    check_static_nct03502616_sec17_registry_fields,
    check_static_nct03502616_sec19_registry_fields,
    check_static_nct03502616_sec20_registry_fields,
    check_static_nct03502616_sec21_registry_fields,
    check_static_nct03502616_sec22_registry_fields,
    check_static_nct03574597_coverage,
    check_static_nct03574597_basis,
    check_static_nct03574597_sec2_registry_fields,
    check_static_nct03574597_sec6_registry_fields,
    check_static_nct03574597_sec7_registry_fields,
    check_static_nct03574597_sec8_registry_fields,
    check_static_nct03574597_sec9_registry_fields,
    check_static_nct03574597_sec10_registry_fields,
    check_static_nct03574597_sec11_registry_fields,
    check_static_nct03574597_sec12_registry_fields,
    check_static_nct03574597_sec13_registry_fields,
    check_static_nct03574597_sec14_registry_fields,
    check_static_nct03574597_sec15_registry_fields,
    check_static_nct03574597_sec16_registry_fields,
    check_static_nct03574597_sec17_registry_fields,
    check_static_nct03574597_sec18_registry_fields,
    check_static_nct03574597_sec19_registry_fields,
    check_static_nct03574597_sec20_registry_fields,
    check_static_nct03574597_sec21_registry_fields,
    check_static_nct03574597_sec22_registry_fields,
    check_static_nct03574597_sec23_registry_fields,
    check_static_nct03574597_sec25_registry_fields,
    check_static_nct03574597_sec27_registry_fields,
    check_static_nct03574597_sec28_registry_fields,
    check_static_nct03667690_coverage,
    check_static_nct03667690_basis,
    check_static_nct03667690_pri3_registry_fields,
    check_static_nct03667690_pri4_registry_fields,
    check_static_nct03667690_sec1_registry_fields,
    check_static_nct03667690_sec2_registry_fields,
    check_static_nct03667690_sec5_registry_fields,
    check_static_nct03667690_sec6_registry_fields,
    check_static_nct03667690_sec7_registry_fields,
    check_static_nct03667690_sec8_registry_fields,
    check_static_nct03667690_sec11_registry_fields,
    check_static_nct03667690_sec12_registry_fields,
    check_static_nct03667690_sec13_registry_fields,
    check_static_nct03667690_sec14_registry_fields,
    check_static_nct03869177_coverage,
    check_static_nct03869177_basis,
    check_static_nct03869177_pri1_registry_fields,
    check_static_nct03869177_pri3_registry_fields,
    check_static_nct03869177_sec2_registry_fields,
    check_static_nct03869177_sec6_registry_fields,
    check_static_nct03869177_sec7_registry_fields,
    check_static_nct03869177_sec10_registry_fields,
    check_static_nct03869177_sec11_registry_fields,
    check_static_nct03869177_sec14_registry_fields,
    check_static_nct03869177_sec15_registry_fields,
    check_static_nct03869177_sec16_registry_fields,
    check_static_nct03869177_oth1_registry_fields,
    check_static_nct03869177_oth2_registry_fields,
    check_static_nct03869177_oth4_registry_fields,
    check_static_nct04033003_coverage,
    check_static_nct04033003_basis,
    check_static_nct04033003_pri1_registry_fields,
    check_static_nct04033003_pri4_registry_fields,
    check_static_nct04033003_sec2_registry_fields,
    check_static_nct04033003_sec5_registry_fields,
    check_static_nct04033003_sec6_registry_fields,
    check_static_nct04033003_sec7_registry_fields,
    check_static_nct04033003_sec8_registry_fields,
    check_static_nct04033003_sec9_registry_fields,
    check_static_nct04033003_sec11_registry_fields,
    check_static_nct04048967_coverage,
    check_static_nct04048967_basis,
    check_static_nct04048967_pri1_registry_fields,
    check_static_nct04048967_pri2_registry_fields,
    check_static_nct04048967_pri3_registry_fields,
    check_static_nct04048967_pri4_registry_fields,
    check_static_nct04048967_pri5_registry_fields,
    check_static_nct04048967_pri6_registry_fields,
    check_static_nct04048967_pri7_registry_fields,
    check_static_nct04048967_sec3_registry_fields,
    check_static_nct04048967_sec4_registry_fields,
    check_static_nct04048967_sec7_registry_fields,
    check_static_nct04048967_sec8_registry_fields,
    check_static_nct04048967_sec9_registry_fields,
    check_static_nct04048967_sec10_registry_fields,
    check_static_nct04066881_coverage,
    check_static_nct04066881_basis,
    check_static_nct04066881_pri1_registry_fields,
    check_static_nct04066881_pri2_registry_fields,
    check_static_nct04066881_pri3_registry_fields,
    check_static_nct04066881_pri4_registry_fields,
    check_static_nct04066881_sec1_registry_fields,
    check_static_nct04066881_sec2_registry_fields,
    check_static_nct04066881_sec3_registry_fields,
    check_static_nct04066881_sec4_registry_fields,
    check_static_nct04066881_sec5_registry_fields,
    check_static_nct04066881_sec6_registry_fields,
    check_static_nct04066881_sec7_registry_fields,
    check_static_nct04066881_sec8_registry_fields,
    check_static_nct04066881_sec9_registry_fields,
    check_static_nct04066881_sec10_registry_fields,
    check_static_nct04066881_sec11_registry_fields,
    check_static_nct04066881_sec12_registry_fields,
    check_static_nct04224987_coverage,
    check_static_nct04224987_basis,
    check_static_nct04224987_pri1_registry_fields,
    check_static_nct04224987_pri2_registry_fields,
    check_static_nct04224987_pri3_registry_fields,
    check_static_nct04224987_pri4_registry_fields,
    check_static_nct04224987_pri5_registry_fields,
    check_static_nct04224987_sec2_registry_fields,
    check_static_nct04224987_sec10_registry_fields,
    check_static_nct04224987_sec14_registry_fields,
    check_static_nct04224987_sec15_registry_fields,
    check_static_nct04224987_sec16_registry_fields,
    check_static_nct04247009_coverage,
    check_static_nct04247009_basis,
    check_static_nct04247009_pri2_registry_fields,
    check_static_nct04247009_pri4_registry_fields,
    check_static_nct04247009_pri6_registry_fields,
    check_static_nct04247009_sec1_registry_fields,
    check_static_nct04247009_sec2_registry_fields,
    check_static_nct04247009_sec3_registry_fields,
    check_static_nct04247009_sec5_registry_fields,
    check_static_nct04247009_sec6_registry_fields,
    check_static_nct04247009_sec8_registry_fields,
    check_static_nct04247009_sec9_registry_fields,
    check_static_nct04247009_sec10_registry_fields,
    check_static_nct04369326_coverage,
    check_static_nct04369326_basis,
    check_static_nct04369326_sec1_registry_fields,
    check_static_nct04369326_sec7_registry_fields,
    check_static_nct04369326_sec14_registry_fields,
    check_static_nct04369326_sec15_registry_fields,
    check_static_nct04369326_sec16_registry_fields,
    check_static_nct04424511_coverage,
    check_static_nct04424511_basis,
    check_static_nct04424511_pri1_registry_fields,
    check_static_nct04424511_sec1_registry_fields,
    check_static_nct04424511_sec5_registry_fields,
    check_static_nct04424511_sec8_registry_fields,
    check_static_nct04424511_sec9_registry_fields,
    check_static_nct04424511_sec10_registry_fields,
    check_static_nct04424511_sec11_registry_fields,
    check_static_nct04424511_sec12_registry_fields,
    check_static_nct04424511_sec13_registry_fields,
    check_static_nct04424511_sec14_registry_fields,
    check_static_nct04424511_sec15_registry_fields,
    check_static_nct04424511_sec16_registry_fields,
    check_static_nct04424511_sec17_registry_fields,
    check_static_nct04424511_sec18_registry_fields,
    check_static_nct04424511_sec19_registry_fields,
    check_static_nct05254002_coverage,
    check_static_nct05254002_basis,
    check_static_nct05254002_pri1_registry_fields,
    check_static_nct05254002_pri2_registry_fields,
    check_static_nct05254002_sec3_registry_fields,
    check_static_nct05254002_sec5_registry_fields,
    check_static_nct05254002_sec7_registry_fields,
    check_static_nct05254002_sec8_registry_fields,
    check_static_nct05254002_sec9_registry_fields,
    check_static_nct05254002_sec11_registry_fields,
    check_static_nct05254002_sec14_registry_fields,
    check_static_nct05254002_sec16_registry_fields,
    check_static_nct05254002_sec18_registry_fields,
    check_static_nct05254002_sec19_registry_fields,
    check_static_nct05254002_sec20_registry_fields,
    check_static_nct05254002_sec21_registry_fields,
    check_static_nct05254002_sec22_registry_fields,
    check_static_nct05485402_coverage,
    check_static_nct05485402_basis,
    check_static_nct05485402_pri1_registry_fields,
    check_static_nct05485402_sec1_registry_fields,
    check_static_nct05485402_sec2_registry_fields,
    check_static_nct05485402_sec3_registry_fields,
    check_static_nct05485402_sec4_registry_fields,
    check_static_nct05485402_sec5_registry_fields,
    check_static_nct05485402_sec7_registry_fields,
    check_static_nct05485402_sec9_registry_fields,
    check_static_nct05485402_sec10_registry_fields,
    check_static_nct05485402_sec11_registry_fields,
    check_static_nct05485402_sec12_registry_fields,
    check_static_nct05485402_sec13_registry_fields,
    check_static_nct05485402_sec15_registry_fields,
    check_static_nct05485402_sec16_registry_fields,
    check_static_nct05485402_sec17_registry_fields,
    check_static_nct05485402_sec18_registry_fields,
    check_static_nct05485402_sec19_registry_fields,
    check_static_nct05485402_sec20_registry_fields,
    check_static_nct05485402_sec21_registry_fields,
    check_static_nct05485402_sec23_registry_fields,
    check_static_nct05485402_sec24_registry_fields,
    check_static_nct05485402_sec25_registry_fields,
    check_static_nct05485402_sec26_registry_fields,
    check_static_nct05485402_sec27_registry_fields,
    check_static_nct05485402_sec28_registry_fields,
    check_static_nct05485402_sec29_registry_fields,
    check_static_nct05485402_sec31_registry_fields,
    check_static_nct05485402_sec32_registry_fields,
    check_static_nct05485402_sec33_registry_fields,
    check_static_nct05485402_sec34_registry_fields,
    check_static_nct05485402_sec36_registry_fields,
    check_static_nct05485402_sec37_registry_fields,
    check_static_nct05485402_sec38_registry_fields,
]

REWARD_HACKING_CHECKS = [
    check_reward_hacking_nct02048007_result_quote_verbatim,
    check_reward_hacking_nct02048007_result_quote_numeric,
    check_reward_hacking_nct02048007_role_quote_verbatim,
    check_reward_hacking_nct02048007_negative_rows_clean,
    check_reward_hacking_nct02048007_additional_within_bound,
    check_reward_hacking_nct02048007_row_shape_rules,
    check_reward_hacking_nct02048007_distinct_result_quotes,
    check_reward_hacking_nct02391337_result_quote_verbatim,
    check_reward_hacking_nct02391337_result_quote_numeric,
    check_reward_hacking_nct02391337_role_quote_verbatim,
    check_reward_hacking_nct02391337_negative_rows_clean,
    check_reward_hacking_nct02391337_additional_within_bound,
    check_reward_hacking_nct02391337_row_shape_rules,
    check_reward_hacking_nct02391337_distinct_result_quotes,
    check_reward_hacking_nct02409680_result_quote_verbatim,
    check_reward_hacking_nct02409680_result_quote_numeric,
    check_reward_hacking_nct02409680_role_quote_verbatim,
    check_reward_hacking_nct02409680_negative_rows_clean,
    check_reward_hacking_nct02409680_additional_within_bound,
    check_reward_hacking_nct02409680_row_shape_rules,
    check_reward_hacking_nct02409680_distinct_result_quotes,
    check_reward_hacking_nct02429180_result_quote_verbatim,
    check_reward_hacking_nct02429180_result_quote_numeric,
    check_reward_hacking_nct02429180_role_quote_verbatim,
    check_reward_hacking_nct02429180_negative_rows_clean,
    check_reward_hacking_nct02429180_additional_within_bound,
    check_reward_hacking_nct02429180_row_shape_rules,
    check_reward_hacking_nct02429180_distinct_result_quotes,
    check_reward_hacking_nct02584283_result_quote_verbatim,
    check_reward_hacking_nct02584283_result_quote_numeric,
    check_reward_hacking_nct02584283_role_quote_verbatim,
    check_reward_hacking_nct02584283_negative_rows_clean,
    check_reward_hacking_nct02584283_additional_within_bound,
    check_reward_hacking_nct02584283_row_shape_rules,
    check_reward_hacking_nct02584283_distinct_result_quotes,
    check_reward_hacking_nct02747927_result_quote_verbatim,
    check_reward_hacking_nct02747927_result_quote_numeric,
    check_reward_hacking_nct02747927_role_quote_verbatim,
    check_reward_hacking_nct02747927_negative_rows_clean,
    check_reward_hacking_nct02747927_additional_within_bound,
    check_reward_hacking_nct02747927_row_shape_rules,
    check_reward_hacking_nct02747927_distinct_result_quotes,
    check_reward_hacking_nct02944682_result_quote_verbatim,
    check_reward_hacking_nct02944682_result_quote_numeric,
    check_reward_hacking_nct02944682_role_quote_verbatim,
    check_reward_hacking_nct02944682_negative_rows_clean,
    check_reward_hacking_nct02944682_additional_within_bound,
    check_reward_hacking_nct02944682_row_shape_rules,
    check_reward_hacking_nct02944682_distinct_result_quotes,
    check_reward_hacking_nct03114917_result_quote_verbatim,
    check_reward_hacking_nct03114917_result_quote_numeric,
    check_reward_hacking_nct03114917_role_quote_verbatim,
    check_reward_hacking_nct03114917_negative_rows_clean,
    check_reward_hacking_nct03114917_additional_within_bound,
    check_reward_hacking_nct03114917_row_shape_rules,
    check_reward_hacking_nct03114917_distinct_result_quotes,
    check_reward_hacking_nct03148457_result_quote_verbatim,
    check_reward_hacking_nct03148457_result_quote_numeric,
    check_reward_hacking_nct03148457_role_quote_verbatim,
    check_reward_hacking_nct03148457_negative_rows_clean,
    check_reward_hacking_nct03148457_additional_within_bound,
    check_reward_hacking_nct03148457_row_shape_rules,
    check_reward_hacking_nct03148457_distinct_result_quotes,
    check_reward_hacking_nct03198585_result_quote_verbatim,
    check_reward_hacking_nct03198585_result_quote_numeric,
    check_reward_hacking_nct03198585_role_quote_verbatim,
    check_reward_hacking_nct03198585_negative_rows_clean,
    check_reward_hacking_nct03198585_additional_within_bound,
    check_reward_hacking_nct03198585_row_shape_rules,
    check_reward_hacking_nct03198585_distinct_result_quotes,
    check_reward_hacking_nct03502616_result_quote_verbatim,
    check_reward_hacking_nct03502616_result_quote_numeric,
    check_reward_hacking_nct03502616_role_quote_verbatim,
    check_reward_hacking_nct03502616_negative_rows_clean,
    check_reward_hacking_nct03502616_additional_within_bound,
    check_reward_hacking_nct03502616_row_shape_rules,
    check_reward_hacking_nct03502616_distinct_result_quotes,
    check_reward_hacking_nct03574597_result_quote_verbatim,
    check_reward_hacking_nct03574597_result_quote_numeric,
    check_reward_hacking_nct03574597_role_quote_verbatim,
    check_reward_hacking_nct03574597_negative_rows_clean,
    check_reward_hacking_nct03574597_additional_within_bound,
    check_reward_hacking_nct03574597_row_shape_rules,
    check_reward_hacking_nct03574597_distinct_result_quotes,
    check_reward_hacking_nct03667690_result_quote_verbatim,
    check_reward_hacking_nct03667690_result_quote_numeric,
    check_reward_hacking_nct03667690_role_quote_verbatim,
    check_reward_hacking_nct03667690_negative_rows_clean,
    check_reward_hacking_nct03667690_additional_within_bound,
    check_reward_hacking_nct03667690_row_shape_rules,
    check_reward_hacking_nct03667690_distinct_result_quotes,
    check_reward_hacking_nct03869177_result_quote_verbatim,
    check_reward_hacking_nct03869177_result_quote_numeric,
    check_reward_hacking_nct03869177_role_quote_verbatim,
    check_reward_hacking_nct03869177_negative_rows_clean,
    check_reward_hacking_nct03869177_additional_within_bound,
    check_reward_hacking_nct03869177_row_shape_rules,
    check_reward_hacking_nct03869177_distinct_result_quotes,
    check_reward_hacking_nct04033003_result_quote_verbatim,
    check_reward_hacking_nct04033003_result_quote_numeric,
    check_reward_hacking_nct04033003_role_quote_verbatim,
    check_reward_hacking_nct04033003_negative_rows_clean,
    check_reward_hacking_nct04033003_additional_within_bound,
    check_reward_hacking_nct04033003_row_shape_rules,
    check_reward_hacking_nct04033003_distinct_result_quotes,
    check_reward_hacking_nct04048967_result_quote_verbatim,
    check_reward_hacking_nct04048967_result_quote_numeric,
    check_reward_hacking_nct04048967_role_quote_verbatim,
    check_reward_hacking_nct04048967_negative_rows_clean,
    check_reward_hacking_nct04048967_additional_within_bound,
    check_reward_hacking_nct04048967_row_shape_rules,
    check_reward_hacking_nct04048967_distinct_result_quotes,
    check_reward_hacking_nct04066881_result_quote_verbatim,
    check_reward_hacking_nct04066881_result_quote_numeric,
    check_reward_hacking_nct04066881_role_quote_verbatim,
    check_reward_hacking_nct04066881_negative_rows_clean,
    check_reward_hacking_nct04066881_additional_within_bound,
    check_reward_hacking_nct04066881_row_shape_rules,
    check_reward_hacking_nct04066881_distinct_result_quotes,
    check_reward_hacking_nct04224987_result_quote_verbatim,
    check_reward_hacking_nct04224987_result_quote_numeric,
    check_reward_hacking_nct04224987_role_quote_verbatim,
    check_reward_hacking_nct04224987_negative_rows_clean,
    check_reward_hacking_nct04224987_additional_within_bound,
    check_reward_hacking_nct04224987_row_shape_rules,
    check_reward_hacking_nct04224987_distinct_result_quotes,
    check_reward_hacking_nct04247009_result_quote_verbatim,
    check_reward_hacking_nct04247009_result_quote_numeric,
    check_reward_hacking_nct04247009_role_quote_verbatim,
    check_reward_hacking_nct04247009_negative_rows_clean,
    check_reward_hacking_nct04247009_additional_within_bound,
    check_reward_hacking_nct04247009_row_shape_rules,
    check_reward_hacking_nct04247009_distinct_result_quotes,
    check_reward_hacking_nct04369326_result_quote_verbatim,
    check_reward_hacking_nct04369326_result_quote_numeric,
    check_reward_hacking_nct04369326_role_quote_verbatim,
    check_reward_hacking_nct04369326_negative_rows_clean,
    check_reward_hacking_nct04369326_additional_within_bound,
    check_reward_hacking_nct04369326_row_shape_rules,
    check_reward_hacking_nct04369326_distinct_result_quotes,
    check_reward_hacking_nct04424511_result_quote_verbatim,
    check_reward_hacking_nct04424511_result_quote_numeric,
    check_reward_hacking_nct04424511_role_quote_verbatim,
    check_reward_hacking_nct04424511_negative_rows_clean,
    check_reward_hacking_nct04424511_additional_within_bound,
    check_reward_hacking_nct04424511_row_shape_rules,
    check_reward_hacking_nct04424511_distinct_result_quotes,
    check_reward_hacking_nct05254002_result_quote_verbatim,
    check_reward_hacking_nct05254002_result_quote_numeric,
    check_reward_hacking_nct05254002_role_quote_verbatim,
    check_reward_hacking_nct05254002_negative_rows_clean,
    check_reward_hacking_nct05254002_additional_within_bound,
    check_reward_hacking_nct05254002_row_shape_rules,
    check_reward_hacking_nct05254002_distinct_result_quotes,
    check_reward_hacking_nct05485402_result_quote_verbatim,
    check_reward_hacking_nct05485402_result_quote_numeric,
    check_reward_hacking_nct05485402_role_quote_verbatim,
    check_reward_hacking_nct05485402_negative_rows_clean,
    check_reward_hacking_nct05485402_additional_within_bound,
    check_reward_hacking_nct05485402_row_shape_rules,
    check_reward_hacking_nct05485402_distinct_result_quotes,
]

PARTIAL_ORACLE_CHECKS = [
    check_po_nct02048007_basis_derived,
    check_po_nct02048007_pri1_reported,
    check_po_nct02048007_pri1_document,
    check_po_nct02048007_pri1_label,
    check_po_nct02048007_pri1_instrument,
    check_po_nct02048007_pri1_role,
    check_po_nct02048007_pri2_reported,
    check_po_nct02048007_pri2_document,
    check_po_nct02048007_pri2_label,
    check_po_nct02048007_pri2_instrument,
    check_po_nct02048007_pri2_role,
    check_po_nct02048007_pri5_reported,
    check_po_nct02048007_pri6_reported,
    check_po_nct02048007_pri6_document,
    check_po_nct02048007_pri6_label,
    check_po_nct02048007_pri6_instrument,
    check_po_nct02048007_pri6_role,
    check_po_nct02048007_pri7_reported,
    check_po_nct02048007_pri7_document,
    check_po_nct02048007_pri7_label,
    check_po_nct02048007_pri7_role,
    check_po_nct02048007_sec1_reported,
    check_po_nct02048007_sec2_reported,
    check_po_nct02048007_sec2_document,
    check_po_nct02048007_sec2_label,
    check_po_nct02048007_sec2_instrument,
    check_po_nct02048007_sec2_role,
    check_po_nct02048007_sec3_reported,
    check_po_nct02048007_sec3_document,
    check_po_nct02048007_sec3_label,
    check_po_nct02048007_sec3_instrument,
    check_po_nct02048007_sec3_role,
    check_po_nct02048007_sec5_reported,
    check_po_nct02048007_sec6_reported,
    check_po_nct02048007_sec10_reported,
    check_po_nct02048007_sec14_reported,
    check_po_nct02048007_sec15_reported,
    check_po_nct02048007_sec16_reported,
    check_po_nct02048007_sec17_reported,
    check_po_nct02048007_sec20_reported,
    check_po_nct02048007_sec21_reported,
    check_po_nct02048007_sec22_reported,
    check_po_nct02048007_sec23_reported,
    check_po_nct02048007_sec24_reported,
    check_po_nct02048007_sec25_reported,
    check_po_nct02048007_sec27_reported,
    check_po_nct02048007_sec28_reported,
    check_po_nct02048007_sec29_reported,
    check_po_nct02048007_add0_found,
    check_po_nct02048007_add1_found,
    check_po_nct02048007_add2_found,
    check_po_nct02048007_add3_found,
    check_po_nct02048007_add4_found,
    check_po_nct02048007_add5_found,
    check_po_nct02048007_add6_found,
    check_po_nct02048007_add7_found,
    check_po_nct02048007_add8_found,
    check_po_nct02048007_add9_found,
    check_po_nct02048007_add10_found,
    check_po_nct02048007_add11_found,
    check_po_nct02048007_add12_found,
    check_po_nct02048007_add13_found,
    check_po_nct02048007_add14_found,
    check_po_nct02048007_add15_found,
    check_po_nct02048007_add16_found,
    check_po_nct02048007_add17_found,
    check_po_nct02048007_add18_found,
    check_po_nct02048007_add19_found,
    check_po_nct02048007_add20_found,
    check_po_nct02048007_add21_found,
    check_po_nct02048007_add22_found,
    check_po_nct02048007_add23_found,
    check_po_nct02048007_add24_found,
    check_po_nct02048007_add25_found,
    check_po_nct02048007_add26_found,
    check_po_nct02048007_add27_found,
    check_po_nct02048007_add28_found,
    check_po_nct02048007_add29_found,
    check_po_nct02048007_add30_found,
    check_po_nct02048007_add31_found,
    check_po_nct02048007_add32_found,
    check_po_nct02048007_add33_found,
    check_po_nct02048007_add34_found,
    check_po_nct02048007_add35_found,
    check_po_nct02048007_add36_found,
    check_po_nct02048007_add37_found,
    check_po_nct02048007_add38_found,
    check_po_nct02048007_add39_found,
    check_po_nct02048007_add40_found,
    check_po_nct02048007_add41_found,
    check_po_nct02048007_add42_found,
    check_po_nct02048007_add43_found,
    check_po_nct02048007_add44_found,
    check_po_nct02048007_add45_found,
    check_po_nct02048007_add46_found,
    check_po_nct02048007_add47_found,
    check_po_nct02048007_add48_found,
    check_po_nct02048007_add49_found,
    check_po_nct02048007_add50_found,
    check_po_nct02048007_add51_found,
    check_po_nct02048007_add52_found,
    check_po_nct02048007_add53_found,
    check_po_nct02048007_add54_found,
    check_po_nct02048007_add55_found,
    check_po_nct02048007_add56_found,
    check_po_nct02048007_add57_found,
    check_po_nct02048007_add58_found,
    check_po_nct02048007_add59_found,
    check_po_nct02048007_add60_found,
    check_po_nct02048007_add61_found,
    check_po_nct02048007_add62_found,
    check_po_nct02048007_add63_found,
    check_po_nct02048007_add64_found,
    check_po_nct02048007_add65_found,
    check_po_nct02048007_add66_found,
    check_po_nct02048007_add67_found,
    check_po_nct02048007_add68_found,
    check_po_nct02048007_add69_found,
    check_po_nct02048007_add70_found,
    check_po_nct02048007_add71_found,
    check_po_nct02048007_add72_found,
    check_po_nct02048007_add73_found,
    check_po_nct02048007_add74_found,
    check_po_nct02048007_add75_found,
    check_po_nct02048007_add76_found,
    check_po_nct02048007_add77_found,
    check_po_nct02048007_add78_found,
    check_po_nct02048007_add79_found,
    check_po_nct02048007_add80_found,
    check_po_nct02048007_add81_found,
    check_po_nct02048007_add82_found,
    check_po_nct02048007_add83_found,
    check_po_nct02048007_add84_found,
    check_po_nct02048007_add85_found,
    check_po_nct02048007_add86_found,
    check_po_nct02048007_add87_found,
    check_po_nct02048007_add88_found,
    check_po_nct02048007_add89_found,
    check_po_nct02048007_add90_found,
    check_po_nct02048007_add91_found,
    check_po_nct02048007_add92_found,
    check_po_nct02048007_add93_found,
    check_po_nct02048007_add94_found,
    check_po_nct02048007_add95_found,
    check_po_nct02048007_add96_found,
    check_po_nct02048007_add97_found,
    check_po_nct02048007_add98_found,
    check_po_nct02048007_add99_found,
    check_po_nct02048007_add100_found,
    check_po_nct02048007_add101_found,
    check_po_nct02048007_add102_found,
    check_po_nct02048007_add103_found,
    check_po_nct02048007_add104_found,
    check_po_nct02048007_add105_found,
    check_po_nct02048007_add106_found,
    check_po_nct02048007_add107_found,
    check_po_nct02048007_add108_found,
    check_po_nct02048007_add109_found,
    check_po_nct02048007_add110_found,
    check_po_nct02048007_add111_found,
    check_po_nct02048007_add112_found,
    check_po_nct02048007_add113_found,
    check_po_nct02048007_add114_found,
    check_po_nct02048007_add115_found,
    check_po_nct02048007_add116_found,
    check_po_nct02048007_add117_found,
    check_po_nct02048007_add118_found,
    check_po_nct02048007_add119_found,
    check_po_nct02048007_add120_found,
    check_po_nct02048007_add121_found,
    check_po_nct02048007_add122_found,
    check_po_nct02048007_add123_found,
    check_po_nct02048007_add124_found,
    check_po_nct02048007_add125_found,
    check_po_nct02048007_add126_found,
    check_po_nct02048007_add127_found,
    check_po_nct02048007_add128_found,
    check_po_nct02048007_add129_found,
    check_po_nct02048007_add130_found,
    check_po_nct02048007_add131_found,
    check_po_nct02048007_add132_found,
    check_po_nct02048007_add133_found,
    check_po_nct02048007_add134_found,
    check_po_nct02048007_add135_found,
    check_po_nct02048007_add136_found,
    check_po_nct02048007_add137_found,
    check_po_nct02048007_add138_found,
    check_po_nct02048007_add139_found,
    check_po_nct02048007_add140_found,
    check_po_nct02048007_add141_found,
    check_po_nct02048007_add142_found,
    check_po_nct02048007_add143_found,
    check_po_nct02048007_add144_found,
    check_po_nct02048007_add145_found,
    check_po_nct02048007_add146_found,
    check_po_nct02048007_add147_found,
    check_po_nct02048007_add148_found,
    check_po_nct02048007_add149_found,
    check_po_nct02048007_add150_found,
    check_po_nct02048007_add151_found,
    check_po_nct02048007_add152_found,
    check_po_nct02048007_add153_found,
    check_po_nct02048007_add154_found,
    check_po_nct02048007_add155_found,
    check_po_nct02048007_add156_found,
    check_po_nct02048007_add157_found,
    check_po_nct02048007_add158_found,
    check_po_nct02048007_add159_found,
    check_po_nct02048007_add160_found,
    check_po_nct02048007_add161_found,
    check_po_nct02048007_add162_found,
    check_po_nct02048007_add163_found,
    check_po_nct02048007_add164_found,
    check_po_nct02048007_add165_found,
    check_po_nct02391337_basis_derived,
    check_po_nct02391337_sec1_reported,
    check_po_nct02391337_sec2_reported,
    check_po_nct02391337_sec4_reported,
    check_po_nct02391337_sec8_reported,
    check_po_nct02391337_sec8_document,
    check_po_nct02391337_sec8_label,
    check_po_nct02391337_sec8_instrument,
    check_po_nct02391337_sec8_role,
    check_po_nct02391337_oth2_reported,
    check_po_nct02391337_oth3_reported,
    check_po_nct02391337_oth3_document,
    check_po_nct02391337_oth3_label,
    check_po_nct02391337_oth3_role,
    check_po_nct02391337_oth4_reported,
    check_po_nct02391337_oth5_reported,
    check_po_nct02391337_oth6_reported,
    check_po_nct02391337_oth7_reported,
    check_po_nct02391337_oth8_reported,
    check_po_nct02391337_oth9_reported,
    check_po_nct02391337_oth10_reported,
    check_po_nct02391337_oth11_reported,
    check_po_nct02391337_add0_found,
    check_po_nct02391337_add1_found,
    check_po_nct02391337_add2_found,
    check_po_nct02391337_add3_found,
    check_po_nct02391337_add4_found,
    check_po_nct02391337_add5_found,
    check_po_nct02391337_add6_found,
    check_po_nct02391337_add7_found,
    check_po_nct02391337_add8_found,
    check_po_nct02391337_add9_found,
    check_po_nct02391337_add10_found,
    check_po_nct02391337_add11_found,
    check_po_nct02391337_add12_found,
    check_po_nct02391337_add13_found,
    check_po_nct02391337_add14_found,
    check_po_nct02391337_add15_found,
    check_po_nct02391337_add16_found,
    check_po_nct02391337_add17_found,
    check_po_nct02391337_add18_found,
    check_po_nct02391337_add19_found,
    check_po_nct02391337_add20_found,
    check_po_nct02391337_add21_found,
    check_po_nct02391337_add22_found,
    check_po_nct02391337_add23_found,
    check_po_nct02391337_add24_found,
    check_po_nct02391337_add25_found,
    check_po_nct02391337_add26_found,
    check_po_nct02391337_add27_found,
    check_po_nct02391337_add28_found,
    check_po_nct02391337_add29_found,
    check_po_nct02391337_add30_found,
    check_po_nct02391337_add31_found,
    check_po_nct02391337_add32_found,
    check_po_nct02391337_add33_found,
    check_po_nct02391337_add34_found,
    check_po_nct02391337_add35_found,
    check_po_nct02391337_add36_found,
    check_po_nct02391337_add37_found,
    check_po_nct02391337_add38_found,
    check_po_nct02391337_add39_found,
    check_po_nct02391337_add40_found,
    check_po_nct02391337_add41_found,
    check_po_nct02391337_add42_found,
    check_po_nct02391337_add43_found,
    check_po_nct02391337_add44_found,
    check_po_nct02391337_add45_found,
    check_po_nct02391337_add46_found,
    check_po_nct02391337_add47_found,
    check_po_nct02391337_add48_found,
    check_po_nct02391337_add49_found,
    check_po_nct02391337_add50_found,
    check_po_nct02391337_add51_found,
    check_po_nct02391337_add52_found,
    check_po_nct02391337_add53_found,
    check_po_nct02391337_add54_found,
    check_po_nct02391337_add55_found,
    check_po_nct02391337_add56_found,
    check_po_nct02391337_add57_found,
    check_po_nct02391337_add58_found,
    check_po_nct02391337_add59_found,
    check_po_nct02391337_add60_found,
    check_po_nct02391337_add61_found,
    check_po_nct02391337_add62_found,
    check_po_nct02391337_add63_found,
    check_po_nct02391337_add64_found,
    check_po_nct02391337_add65_found,
    check_po_nct02391337_add66_found,
    check_po_nct02391337_add67_found,
    check_po_nct02391337_add68_found,
    check_po_nct02391337_add69_found,
    check_po_nct02391337_add70_found,
    check_po_nct02391337_add71_found,
    check_po_nct02391337_add72_found,
    check_po_nct02391337_add73_found,
    check_po_nct02391337_add74_found,
    check_po_nct02391337_add75_found,
    check_po_nct02391337_add76_found,
    check_po_nct02391337_add77_found,
    check_po_nct02391337_add78_found,
    check_po_nct02391337_add79_found,
    check_po_nct02391337_add80_found,
    check_po_nct02391337_add81_found,
    check_po_nct02391337_add82_found,
    check_po_nct02391337_add83_found,
    check_po_nct02391337_add84_found,
    check_po_nct02391337_add85_found,
    check_po_nct02391337_add86_found,
    check_po_nct02391337_add87_found,
    check_po_nct02391337_add88_found,
    check_po_nct02391337_add89_found,
    check_po_nct02391337_add90_found,
    check_po_nct02391337_add91_found,
    check_po_nct02391337_add92_found,
    check_po_nct02409680_basis_derived,
    check_po_nct02409680_pri1_reported,
    check_po_nct02409680_pri1_document,
    check_po_nct02409680_pri1_label,
    check_po_nct02409680_pri1_instrument,
    check_po_nct02409680_pri1_role,
    check_po_nct02409680_sec2_reported,
    check_po_nct02409680_sec2_document,
    check_po_nct02409680_sec2_label,
    check_po_nct02409680_sec2_instrument,
    check_po_nct02409680_sec2_role,
    check_po_nct02409680_sec3_reported,
    check_po_nct02409680_sec3_document,
    check_po_nct02409680_sec3_label,
    check_po_nct02409680_sec3_role,
    check_po_nct02409680_oth12_reported,
    check_po_nct02409680_add0_found,
    check_po_nct02409680_add1_found,
    check_po_nct02409680_add2_found,
    check_po_nct02409680_add3_found,
    check_po_nct02409680_add4_found,
    check_po_nct02409680_add5_found,
    check_po_nct02409680_add6_found,
    check_po_nct02409680_add7_found,
    check_po_nct02409680_add8_found,
    check_po_nct02409680_add9_found,
    check_po_nct02409680_add10_found,
    check_po_nct02409680_add11_found,
    check_po_nct02409680_add12_found,
    check_po_nct02409680_add13_found,
    check_po_nct02409680_add14_found,
    check_po_nct02409680_add15_found,
    check_po_nct02409680_add16_found,
    check_po_nct02409680_add17_found,
    check_po_nct02409680_add18_found,
    check_po_nct02409680_add19_found,
    check_po_nct02409680_add20_found,
    check_po_nct02409680_add21_found,
    check_po_nct02409680_add22_found,
    check_po_nct02409680_add23_found,
    check_po_nct02409680_add24_found,
    check_po_nct02409680_add25_found,
    check_po_nct02409680_add26_found,
    check_po_nct02409680_add27_found,
    check_po_nct02409680_add28_found,
    check_po_nct02409680_add29_found,
    check_po_nct02409680_add30_found,
    check_po_nct02409680_add31_found,
    check_po_nct02409680_add32_found,
    check_po_nct02409680_add33_found,
    check_po_nct02409680_add34_found,
    check_po_nct02409680_add35_found,
    check_po_nct02409680_add36_found,
    check_po_nct02409680_add37_found,
    check_po_nct02409680_add38_found,
    check_po_nct02409680_add39_found,
    check_po_nct02409680_add40_found,
    check_po_nct02409680_add41_found,
    check_po_nct02409680_add42_found,
    check_po_nct02409680_add43_found,
    check_po_nct02409680_add44_found,
    check_po_nct02409680_add45_found,
    check_po_nct02409680_add46_found,
    check_po_nct02409680_add47_found,
    check_po_nct02409680_add48_found,
    check_po_nct02409680_add49_found,
    check_po_nct02409680_add50_found,
    check_po_nct02409680_add51_found,
    check_po_nct02409680_add52_found,
    check_po_nct02409680_add53_found,
    check_po_nct02409680_add54_found,
    check_po_nct02409680_add55_found,
    check_po_nct02409680_add56_found,
    check_po_nct02409680_add57_found,
    check_po_nct02409680_add58_found,
    check_po_nct02429180_basis_derived,
    check_po_nct02429180_pri1_reported,
    check_po_nct02429180_pri1_document,
    check_po_nct02429180_pri1_label,
    check_po_nct02429180_pri1_instrument,
    check_po_nct02429180_pri1_role,
    check_po_nct02429180_pri2_reported,
    check_po_nct02429180_pri2_document,
    check_po_nct02429180_pri2_label,
    check_po_nct02429180_pri2_instrument,
    check_po_nct02429180_pri2_role,
    check_po_nct02429180_pri3_reported,
    check_po_nct02429180_pri3_document,
    check_po_nct02429180_pri3_label,
    check_po_nct02429180_pri3_instrument,
    check_po_nct02429180_pri3_role,
    check_po_nct02429180_pri4_reported,
    check_po_nct02429180_pri4_document,
    check_po_nct02429180_pri4_label,
    check_po_nct02429180_pri4_instrument,
    check_po_nct02429180_pri4_role,
    check_po_nct02429180_pri5_reported,
    check_po_nct02429180_pri5_document,
    check_po_nct02429180_pri5_label,
    check_po_nct02429180_pri5_instrument,
    check_po_nct02429180_pri5_role,
    check_po_nct02429180_sec1_reported,
    check_po_nct02429180_sec1_document,
    check_po_nct02429180_sec1_label,
    check_po_nct02429180_sec1_instrument,
    check_po_nct02429180_sec1_role,
    check_po_nct02429180_sec2_reported,
    check_po_nct02429180_sec2_document,
    check_po_nct02429180_sec2_label,
    check_po_nct02429180_sec2_instrument,
    check_po_nct02429180_sec2_role,
    check_po_nct02429180_sec3_reported,
    check_po_nct02429180_sec3_document,
    check_po_nct02429180_sec3_label,
    check_po_nct02429180_sec3_instrument,
    check_po_nct02429180_sec3_role,
    check_po_nct02429180_sec4_reported,
    check_po_nct02429180_sec4_document,
    check_po_nct02429180_sec4_label,
    check_po_nct02429180_sec4_instrument,
    check_po_nct02429180_sec4_role,
    check_po_nct02429180_sec5_reported,
    check_po_nct02429180_sec5_document,
    check_po_nct02429180_sec5_label,
    check_po_nct02429180_sec5_instrument,
    check_po_nct02429180_sec5_role,
    check_po_nct02429180_sec6_reported,
    check_po_nct02429180_sec6_document,
    check_po_nct02429180_sec6_label,
    check_po_nct02429180_sec6_instrument,
    check_po_nct02429180_sec6_role,
    check_po_nct02429180_sec8_reported,
    check_po_nct02429180_sec8_document,
    check_po_nct02429180_sec8_label,
    check_po_nct02429180_sec8_instrument,
    check_po_nct02429180_sec8_role,
    check_po_nct02429180_sec9_reported,
    check_po_nct02429180_sec9_document,
    check_po_nct02429180_sec9_label,
    check_po_nct02429180_sec9_instrument,
    check_po_nct02429180_sec9_role,
    check_po_nct02429180_sec10_reported,
    check_po_nct02429180_sec10_document,
    check_po_nct02429180_sec10_label,
    check_po_nct02429180_sec10_role,
    check_po_nct02429180_oth1_reported,
    check_po_nct02429180_oth1_document,
    check_po_nct02429180_oth1_label,
    check_po_nct02429180_oth1_instrument,
    check_po_nct02429180_oth1_role,
    check_po_nct02429180_add0_found,
    check_po_nct02429180_add1_found,
    check_po_nct02429180_add2_found,
    check_po_nct02429180_add3_found,
    check_po_nct02429180_add4_found,
    check_po_nct02429180_add5_found,
    check_po_nct02429180_add6_found,
    check_po_nct02429180_add7_found,
    check_po_nct02429180_add8_found,
    check_po_nct02429180_add9_found,
    check_po_nct02429180_add10_found,
    check_po_nct02429180_add11_found,
    check_po_nct02429180_add12_found,
    check_po_nct02429180_add13_found,
    check_po_nct02429180_add14_found,
    check_po_nct02429180_add15_found,
    check_po_nct02429180_add16_found,
    check_po_nct02429180_add17_found,
    check_po_nct02429180_add18_found,
    check_po_nct02429180_add19_found,
    check_po_nct02429180_add20_found,
    check_po_nct02429180_add21_found,
    check_po_nct02429180_add22_found,
    check_po_nct02429180_add23_found,
    check_po_nct02429180_add24_found,
    check_po_nct02429180_add25_found,
    check_po_nct02429180_add26_found,
    check_po_nct02429180_add27_found,
    check_po_nct02429180_add28_found,
    check_po_nct02429180_add29_found,
    check_po_nct02429180_add30_found,
    check_po_nct02429180_add31_found,
    check_po_nct02429180_add32_found,
    check_po_nct02429180_add33_found,
    check_po_nct02429180_add34_found,
    check_po_nct02429180_add35_found,
    check_po_nct02429180_add36_found,
    check_po_nct02429180_add37_found,
    check_po_nct02429180_add38_found,
    check_po_nct02429180_add39_found,
    check_po_nct02429180_add40_found,
    check_po_nct02429180_add41_found,
    check_po_nct02429180_add42_found,
    check_po_nct02429180_add43_found,
    check_po_nct02429180_add44_found,
    check_po_nct02429180_add45_found,
    check_po_nct02429180_add46_found,
    check_po_nct02429180_add47_found,
    check_po_nct02429180_add48_found,
    check_po_nct02429180_add49_found,
    check_po_nct02429180_add50_found,
    check_po_nct02429180_add51_found,
    check_po_nct02429180_add52_found,
    check_po_nct02429180_add53_found,
    check_po_nct02429180_add54_found,
    check_po_nct02429180_add55_found,
    check_po_nct02429180_add56_found,
    check_po_nct02429180_add57_found,
    check_po_nct02429180_add58_found,
    check_po_nct02429180_add59_found,
    check_po_nct02429180_add60_found,
    check_po_nct02429180_add61_found,
    check_po_nct02584283_basis_derived,
    check_po_nct02584283_pri1_reported,
    check_po_nct02584283_pri1_document,
    check_po_nct02584283_pri1_label,
    check_po_nct02584283_pri1_role,
    check_po_nct02584283_sec1_reported,
    check_po_nct02584283_sec1_document,
    check_po_nct02584283_sec1_label,
    check_po_nct02584283_sec1_instrument,
    check_po_nct02584283_sec1_role,
    check_po_nct02584283_sec4_reported,
    check_po_nct02584283_sec4_document,
    check_po_nct02584283_sec4_label,
    check_po_nct02584283_sec4_role,
    check_po_nct02584283_sec5_reported,
    check_po_nct02584283_sec5_document,
    check_po_nct02584283_sec5_label,
    check_po_nct02584283_sec5_role,
    check_po_nct02584283_sec7_reported,
    check_po_nct02584283_sec8_reported,
    check_po_nct02584283_sec9_reported,
    check_po_nct02584283_sec10_reported,
    check_po_nct02584283_sec13_reported,
    check_po_nct02584283_sec14_reported,
    check_po_nct02584283_sec15_reported,
    check_po_nct02584283_sec16_reported,
    check_po_nct02584283_sec17_reported,
    check_po_nct02584283_sec18_reported,
    check_po_nct02584283_sec19_reported,
    check_po_nct02584283_sec20_reported,
    check_po_nct02584283_sec21_reported,
    check_po_nct02584283_sec22_reported,
    check_po_nct02584283_sec23_reported,
    check_po_nct02584283_sec24_reported,
    check_po_nct02584283_sec25_reported,
    check_po_nct02584283_sec26_reported,
    check_po_nct02584283_sec27_reported,
    check_po_nct02584283_sec28_reported,
    check_po_nct02584283_sec29_reported,
    check_po_nct02584283_sec30_reported,
    check_po_nct02584283_sec31_reported,
    check_po_nct02584283_sec32_reported,
    check_po_nct02584283_sec33_reported,
    check_po_nct02584283_sec34_reported,
    check_po_nct02584283_sec35_reported,
    check_po_nct02584283_sec36_reported,
    check_po_nct02584283_sec39_reported,
    check_po_nct02584283_add0_found,
    check_po_nct02584283_add1_found,
    check_po_nct02584283_add2_found,
    check_po_nct02584283_add3_found,
    check_po_nct02584283_add4_found,
    check_po_nct02584283_add5_found,
    check_po_nct02584283_add6_found,
    check_po_nct02584283_add7_found,
    check_po_nct02584283_add8_found,
    check_po_nct02584283_add9_found,
    check_po_nct02584283_add10_found,
    check_po_nct02584283_add11_found,
    check_po_nct02584283_add12_found,
    check_po_nct02584283_add13_found,
    check_po_nct02584283_add14_found,
    check_po_nct02584283_add15_found,
    check_po_nct02584283_add16_found,
    check_po_nct02584283_add17_found,
    check_po_nct02584283_add18_found,
    check_po_nct02584283_add19_found,
    check_po_nct02584283_add20_found,
    check_po_nct02584283_add21_found,
    check_po_nct02584283_add22_found,
    check_po_nct02584283_add23_found,
    check_po_nct02584283_add24_found,
    check_po_nct02584283_add25_found,
    check_po_nct02584283_add26_found,
    check_po_nct02584283_add27_found,
    check_po_nct02584283_add28_found,
    check_po_nct02584283_add29_found,
    check_po_nct02584283_add30_found,
    check_po_nct02584283_add31_found,
    check_po_nct02584283_add32_found,
    check_po_nct02584283_add33_found,
    check_po_nct02584283_add34_found,
    check_po_nct02584283_add35_found,
    check_po_nct02584283_add36_found,
    check_po_nct02584283_add37_found,
    check_po_nct02584283_add38_found,
    check_po_nct02584283_add39_found,
    check_po_nct02584283_add40_found,
    check_po_nct02584283_add41_found,
    check_po_nct02584283_add42_found,
    check_po_nct02584283_add43_found,
    check_po_nct02584283_add44_found,
    check_po_nct02584283_add45_found,
    check_po_nct02584283_add46_found,
    check_po_nct02584283_add47_found,
    check_po_nct02584283_add48_found,
    check_po_nct02584283_add49_found,
    check_po_nct02584283_add50_found,
    check_po_nct02584283_add51_found,
    check_po_nct02584283_add52_found,
    check_po_nct02584283_add53_found,
    check_po_nct02584283_add54_found,
    check_po_nct02584283_add55_found,
    check_po_nct02584283_add56_found,
    check_po_nct02584283_add57_found,
    check_po_nct02584283_add58_found,
    check_po_nct02584283_add59_found,
    check_po_nct02584283_add60_found,
    check_po_nct02584283_add61_found,
    check_po_nct02584283_add62_found,
    check_po_nct02584283_add63_found,
    check_po_nct02584283_add64_found,
    check_po_nct02584283_add65_found,
    check_po_nct02584283_add66_found,
    check_po_nct02584283_add67_found,
    check_po_nct02584283_add68_found,
    check_po_nct02584283_add69_found,
    check_po_nct02584283_add70_found,
    check_po_nct02584283_add71_found,
    check_po_nct02584283_add72_found,
    check_po_nct02584283_add73_found,
    check_po_nct02747927_basis_derived,
    check_po_nct02747927_pri1_reported,
    check_po_nct02747927_pri1_document,
    check_po_nct02747927_pri1_label,
    check_po_nct02747927_pri1_instrument,
    check_po_nct02747927_pri1_role,
    check_po_nct02747927_sec4_reported,
    check_po_nct02747927_sec4_document,
    check_po_nct02747927_sec4_label,
    check_po_nct02747927_sec4_instrument,
    check_po_nct02747927_sec4_role,
    check_po_nct02747927_sec6_reported,
    check_po_nct02747927_sec7_reported,
    check_po_nct02747927_sec8_reported,
    check_po_nct02747927_sec9_reported,
    check_po_nct02747927_sec11_reported,
    check_po_nct02747927_sec11_document,
    check_po_nct02747927_sec11_label,
    check_po_nct02747927_sec11_role,
    check_po_nct02747927_sec15_reported,
    check_po_nct02747927_add0_found,
    check_po_nct02747927_add1_found,
    check_po_nct02747927_add2_found,
    check_po_nct02747927_add3_found,
    check_po_nct02747927_add4_found,
    check_po_nct02747927_add5_found,
    check_po_nct02747927_add6_found,
    check_po_nct02747927_add7_found,
    check_po_nct02747927_add8_found,
    check_po_nct02747927_add9_found,
    check_po_nct02747927_add10_found,
    check_po_nct02747927_add11_found,
    check_po_nct02747927_add12_found,
    check_po_nct02747927_add13_found,
    check_po_nct02747927_add14_found,
    check_po_nct02747927_add15_found,
    check_po_nct02747927_add16_found,
    check_po_nct02747927_add17_found,
    check_po_nct02747927_add18_found,
    check_po_nct02747927_add19_found,
    check_po_nct02747927_add20_found,
    check_po_nct02747927_add21_found,
    check_po_nct02747927_add22_found,
    check_po_nct02747927_add23_found,
    check_po_nct02747927_add24_found,
    check_po_nct02747927_add25_found,
    check_po_nct02747927_add26_found,
    check_po_nct02747927_add27_found,
    check_po_nct02747927_add28_found,
    check_po_nct02747927_add29_found,
    check_po_nct02747927_add30_found,
    check_po_nct02747927_add31_found,
    check_po_nct02747927_add32_found,
    check_po_nct02747927_add33_found,
    check_po_nct02747927_add34_found,
    check_po_nct02747927_add35_found,
    check_po_nct02747927_add36_found,
    check_po_nct02747927_add37_found,
    check_po_nct02747927_add38_found,
    check_po_nct02747927_add39_found,
    check_po_nct02747927_add40_found,
    check_po_nct02747927_add41_found,
    check_po_nct02747927_add42_found,
    check_po_nct02747927_add43_found,
    check_po_nct02747927_add44_found,
    check_po_nct02747927_add45_found,
    check_po_nct02747927_add46_found,
    check_po_nct02747927_add47_found,
    check_po_nct02747927_add48_found,
    check_po_nct02747927_add49_found,
    check_po_nct02747927_add50_found,
    check_po_nct02747927_add51_found,
    check_po_nct02747927_add52_found,
    check_po_nct02747927_add53_found,
    check_po_nct02747927_add54_found,
    check_po_nct02747927_add55_found,
    check_po_nct02747927_add56_found,
    check_po_nct02747927_add57_found,
    check_po_nct02747927_add58_found,
    check_po_nct02747927_add59_found,
    check_po_nct02747927_add60_found,
    check_po_nct02747927_add61_found,
    check_po_nct02747927_add62_found,
    check_po_nct02747927_add63_found,
    check_po_nct02747927_add64_found,
    check_po_nct02747927_add65_found,
    check_po_nct02747927_add66_found,
    check_po_nct02747927_add67_found,
    check_po_nct02747927_add68_found,
    check_po_nct02747927_add69_found,
    check_po_nct02747927_add70_found,
    check_po_nct02747927_add71_found,
    check_po_nct02747927_add72_found,
    check_po_nct02747927_add73_found,
    check_po_nct02747927_add74_found,
    check_po_nct02747927_add75_found,
    check_po_nct02747927_add76_found,
    check_po_nct02747927_add77_found,
    check_po_nct02747927_add78_found,
    check_po_nct02747927_add79_found,
    check_po_nct02747927_add80_found,
    check_po_nct02747927_add81_found,
    check_po_nct02747927_add82_found,
    check_po_nct02747927_add83_found,
    check_po_nct02747927_add84_found,
    check_po_nct02747927_add85_found,
    check_po_nct02747927_add86_found,
    check_po_nct02747927_add87_found,
    check_po_nct02747927_add88_found,
    check_po_nct02747927_add89_found,
    check_po_nct02747927_add90_found,
    check_po_nct02747927_add91_found,
    check_po_nct02747927_add92_found,
    check_po_nct02747927_add93_found,
    check_po_nct02747927_add94_found,
    check_po_nct02747927_add95_found,
    check_po_nct02747927_add96_found,
    check_po_nct02747927_add97_found,
    check_po_nct02747927_add98_found,
    check_po_nct02747927_add99_found,
    check_po_nct02747927_add100_found,
    check_po_nct02747927_add101_found,
    check_po_nct02747927_add102_found,
    check_po_nct02747927_add103_found,
    check_po_nct02747927_add104_found,
    check_po_nct02747927_add105_found,
    check_po_nct02747927_add106_found,
    check_po_nct02747927_add107_found,
    check_po_nct02747927_add108_found,
    check_po_nct02747927_add109_found,
    check_po_nct02747927_add110_found,
    check_po_nct02747927_add111_found,
    check_po_nct02747927_add112_found,
    check_po_nct02747927_add113_found,
    check_po_nct02747927_add114_found,
    check_po_nct02747927_add115_found,
    check_po_nct02747927_add116_found,
    check_po_nct02747927_add117_found,
    check_po_nct02747927_add118_found,
    check_po_nct02944682_basis_derived,
    check_po_nct02944682_pri1_reported,
    check_po_nct02944682_pri1_document,
    check_po_nct02944682_pri1_label,
    check_po_nct02944682_pri1_instrument,
    check_po_nct02944682_pri1_role,
    check_po_nct02944682_pri3_reported,
    check_po_nct02944682_pri3_document,
    check_po_nct02944682_pri3_label,
    check_po_nct02944682_pri3_instrument,
    check_po_nct02944682_pri3_role,
    check_po_nct02944682_pri4_reported,
    check_po_nct02944682_pri4_document,
    check_po_nct02944682_pri4_label,
    check_po_nct02944682_pri4_instrument,
    check_po_nct02944682_pri4_role,
    check_po_nct02944682_sec2_reported,
    check_po_nct02944682_sec2_document,
    check_po_nct02944682_sec2_label,
    check_po_nct02944682_sec2_instrument,
    check_po_nct02944682_sec2_role,
    check_po_nct02944682_sec4_reported,
    check_po_nct02944682_sec5_reported,
    check_po_nct02944682_sec6_reported,
    check_po_nct02944682_sec7_reported,
    check_po_nct02944682_oth2_reported,
    check_po_nct02944682_oth2_document,
    check_po_nct02944682_oth2_label,
    check_po_nct02944682_oth2_instrument,
    check_po_nct02944682_oth2_role,
    check_po_nct02944682_oth3_reported,
    check_po_nct02944682_oth3_document,
    check_po_nct02944682_oth3_label,
    check_po_nct02944682_oth3_instrument,
    check_po_nct02944682_oth3_role,
    check_po_nct02944682_add0_found,
    check_po_nct02944682_add1_found,
    check_po_nct02944682_add2_found,
    check_po_nct02944682_add3_found,
    check_po_nct02944682_add4_found,
    check_po_nct02944682_add5_found,
    check_po_nct02944682_add6_found,
    check_po_nct02944682_add7_found,
    check_po_nct02944682_add8_found,
    check_po_nct02944682_add9_found,
    check_po_nct02944682_add10_found,
    check_po_nct02944682_add11_found,
    check_po_nct02944682_add12_found,
    check_po_nct02944682_add13_found,
    check_po_nct02944682_add14_found,
    check_po_nct02944682_add15_found,
    check_po_nct02944682_add16_found,
    check_po_nct02944682_add17_found,
    check_po_nct02944682_add18_found,
    check_po_nct02944682_add19_found,
    check_po_nct02944682_add20_found,
    check_po_nct02944682_add21_found,
    check_po_nct02944682_add22_found,
    check_po_nct02944682_add23_found,
    check_po_nct02944682_add24_found,
    check_po_nct02944682_add25_found,
    check_po_nct02944682_add26_found,
    check_po_nct02944682_add27_found,
    check_po_nct02944682_add28_found,
    check_po_nct02944682_add29_found,
    check_po_nct02944682_add30_found,
    check_po_nct02944682_add31_found,
    check_po_nct02944682_add32_found,
    check_po_nct02944682_add33_found,
    check_po_nct02944682_add34_found,
    check_po_nct02944682_add35_found,
    check_po_nct02944682_add36_found,
    check_po_nct02944682_add37_found,
    check_po_nct02944682_add38_found,
    check_po_nct02944682_add39_found,
    check_po_nct02944682_add40_found,
    check_po_nct02944682_add41_found,
    check_po_nct02944682_add42_found,
    check_po_nct02944682_add43_found,
    check_po_nct02944682_add44_found,
    check_po_nct02944682_add45_found,
    check_po_nct02944682_add46_found,
    check_po_nct02944682_add47_found,
    check_po_nct02944682_add48_found,
    check_po_nct02944682_add49_found,
    check_po_nct02944682_add50_found,
    check_po_nct02944682_add51_found,
    check_po_nct02944682_add52_found,
    check_po_nct02944682_add53_found,
    check_po_nct02944682_add54_found,
    check_po_nct02944682_add55_found,
    check_po_nct02944682_add56_found,
    check_po_nct02944682_add57_found,
    check_po_nct02944682_add58_found,
    check_po_nct02944682_add59_found,
    check_po_nct02944682_add60_found,
    check_po_nct02944682_add61_found,
    check_po_nct02944682_add62_found,
    check_po_nct02944682_add63_found,
    check_po_nct02944682_add64_found,
    check_po_nct02944682_add65_found,
    check_po_nct02944682_add66_found,
    check_po_nct02944682_add67_found,
    check_po_nct02944682_add68_found,
    check_po_nct02944682_add69_found,
    check_po_nct02944682_add70_found,
    check_po_nct02944682_add71_found,
    check_po_nct02944682_add72_found,
    check_po_nct02944682_add73_found,
    check_po_nct02944682_add74_found,
    check_po_nct02944682_add75_found,
    check_po_nct02944682_add76_found,
    check_po_nct02944682_add77_found,
    check_po_nct02944682_add78_found,
    check_po_nct02944682_add79_found,
    check_po_nct02944682_add80_found,
    check_po_nct02944682_add81_found,
    check_po_nct02944682_add82_found,
    check_po_nct02944682_add83_found,
    check_po_nct02944682_add84_found,
    check_po_nct02944682_add85_found,
    check_po_nct02944682_add86_found,
    check_po_nct02944682_add87_found,
    check_po_nct02944682_add88_found,
    check_po_nct02944682_add89_found,
    check_po_nct02944682_add90_found,
    check_po_nct02944682_add91_found,
    check_po_nct02944682_add92_found,
    check_po_nct02944682_add93_found,
    check_po_nct02944682_add94_found,
    check_po_nct02944682_add95_found,
    check_po_nct02944682_add96_found,
    check_po_nct02944682_add97_found,
    check_po_nct02944682_add98_found,
    check_po_nct02944682_add99_found,
    check_po_nct02944682_add100_found,
    check_po_nct02944682_add101_found,
    check_po_nct02944682_add102_found,
    check_po_nct02944682_add103_found,
    check_po_nct02944682_add104_found,
    check_po_nct02944682_add105_found,
    check_po_nct02944682_add106_found,
    check_po_nct02944682_add107_found,
    check_po_nct02944682_add108_found,
    check_po_nct02944682_add109_found,
    check_po_nct02944682_add110_found,
    check_po_nct02944682_add111_found,
    check_po_nct02944682_add112_found,
    check_po_nct02944682_add113_found,
    check_po_nct02944682_add114_found,
    check_po_nct02944682_add115_found,
    check_po_nct02944682_add116_found,
    check_po_nct02944682_add117_found,
    check_po_nct02944682_add118_found,
    check_po_nct02944682_add119_found,
    check_po_nct02944682_add120_found,
    check_po_nct02944682_add121_found,
    check_po_nct02944682_add122_found,
    check_po_nct02944682_add123_found,
    check_po_nct02944682_add124_found,
    check_po_nct02944682_add125_found,
    check_po_nct02944682_add126_found,
    check_po_nct02944682_add127_found,
    check_po_nct02944682_add128_found,
    check_po_nct02944682_add129_found,
    check_po_nct02944682_add130_found,
    check_po_nct02944682_add131_found,
    check_po_nct02944682_add132_found,
    check_po_nct02944682_add133_found,
    check_po_nct02944682_add134_found,
    check_po_nct02944682_add135_found,
    check_po_nct02944682_add136_found,
    check_po_nct02944682_add137_found,
    check_po_nct02944682_add138_found,
    check_po_nct02944682_add139_found,
    check_po_nct02944682_add140_found,
    check_po_nct02944682_add141_found,
    check_po_nct02944682_add142_found,
    check_po_nct02944682_add143_found,
    check_po_nct02944682_add144_found,
    check_po_nct02944682_add145_found,
    check_po_nct02944682_add146_found,
    check_po_nct02944682_add147_found,
    check_po_nct02944682_add148_found,
    check_po_nct02944682_add149_found,
    check_po_nct02944682_add150_found,
    check_po_nct02944682_add151_found,
    check_po_nct02944682_add152_found,
    check_po_nct02944682_add153_found,
    check_po_nct02944682_add154_found,
    check_po_nct02944682_add155_found,
    check_po_nct02944682_add156_found,
    check_po_nct02944682_add157_found,
    check_po_nct02944682_add158_found,
    check_po_nct02944682_add159_found,
    check_po_nct02944682_add160_found,
    check_po_nct02944682_add161_found,
    check_po_nct02944682_add162_found,
    check_po_nct02944682_add163_found,
    check_po_nct02944682_add164_found,
    check_po_nct02944682_add165_found,
    check_po_nct02944682_add166_found,
    check_po_nct02944682_add167_found,
    check_po_nct02944682_add168_found,
    check_po_nct02944682_add169_found,
    check_po_nct02944682_add170_found,
    check_po_nct02944682_add171_found,
    check_po_nct02944682_add172_found,
    check_po_nct02944682_add173_found,
    check_po_nct02944682_add174_found,
    check_po_nct02944682_add175_found,
    check_po_nct02944682_add176_found,
    check_po_nct02944682_add177_found,
    check_po_nct02944682_add178_found,
    check_po_nct02944682_add179_found,
    check_po_nct02944682_add180_found,
    check_po_nct02944682_add181_found,
    check_po_nct02944682_add182_found,
    check_po_nct02944682_add183_found,
    check_po_nct03114917_basis_derived,
    check_po_nct03114917_pri1_reported,
    check_po_nct03114917_sec3_reported,
    check_po_nct03114917_sec4_reported,
    check_po_nct03114917_oth1_reported,
    check_po_nct03114917_oth2_reported,
    check_po_nct03114917_oth3_reported,
    check_po_nct03114917_oth5_reported,
    check_po_nct03114917_oth6_reported,
    check_po_nct03114917_oth7_reported,
    check_po_nct03114917_oth8_reported,
    check_po_nct03114917_oth9_reported,
    check_po_nct03114917_oth10_reported,
    check_po_nct03114917_oth11_reported,
    check_po_nct03114917_oth12_reported,
    check_po_nct03114917_oth13_reported,
    check_po_nct03114917_oth14_reported,
    check_po_nct03114917_oth15_reported,
    check_po_nct03114917_oth16_reported,
    check_po_nct03114917_oth17_reported,
    check_po_nct03114917_oth18_reported,
    check_po_nct03114917_add0_found,
    check_po_nct03114917_add1_found,
    check_po_nct03114917_add2_found,
    check_po_nct03148457_basis_derived,
    check_po_nct03148457_sec1_reported,
    check_po_nct03148457_sec2_reported,
    check_po_nct03148457_sec2_document,
    check_po_nct03148457_sec2_label,
    check_po_nct03148457_sec2_role,
    check_po_nct03148457_sec3_reported,
    check_po_nct03148457_sec3_document,
    check_po_nct03148457_sec3_label,
    check_po_nct03148457_sec3_role,
    check_po_nct03148457_sec4_reported,
    check_po_nct03148457_sec4_document,
    check_po_nct03148457_sec4_label,
    check_po_nct03148457_sec4_role,
    check_po_nct03148457_sec5_reported,
    check_po_nct03148457_sec5_document,
    check_po_nct03148457_sec5_label,
    check_po_nct03148457_sec5_role,
    check_po_nct03148457_sec6_reported,
    check_po_nct03148457_sec6_document,
    check_po_nct03148457_sec6_label,
    check_po_nct03148457_sec6_role,
    check_po_nct03148457_sec7_reported,
    check_po_nct03148457_sec8_reported,
    check_po_nct03148457_sec10_reported,
    check_po_nct03148457_sec12_reported,
    check_po_nct03148457_sec13_reported,
    check_po_nct03148457_sec15_reported,
    check_po_nct03148457_add0_found,
    check_po_nct03148457_add1_found,
    check_po_nct03148457_add2_found,
    check_po_nct03148457_add3_found,
    check_po_nct03148457_add4_found,
    check_po_nct03148457_add5_found,
    check_po_nct03148457_add6_found,
    check_po_nct03148457_add7_found,
    check_po_nct03148457_add8_found,
    check_po_nct03148457_add9_found,
    check_po_nct03148457_add10_found,
    check_po_nct03148457_add11_found,
    check_po_nct03148457_add12_found,
    check_po_nct03148457_add13_found,
    check_po_nct03148457_add14_found,
    check_po_nct03148457_add15_found,
    check_po_nct03148457_add16_found,
    check_po_nct03148457_add17_found,
    check_po_nct03148457_add18_found,
    check_po_nct03148457_add19_found,
    check_po_nct03148457_add20_found,
    check_po_nct03148457_add21_found,
    check_po_nct03148457_add22_found,
    check_po_nct03148457_add23_found,
    check_po_nct03148457_add24_found,
    check_po_nct03148457_add25_found,
    check_po_nct03148457_add26_found,
    check_po_nct03148457_add27_found,
    check_po_nct03148457_add28_found,
    check_po_nct03148457_add29_found,
    check_po_nct03148457_add30_found,
    check_po_nct03148457_add31_found,
    check_po_nct03198585_basis_derived,
    check_po_nct03198585_pri1_reported,
    check_po_nct03198585_pri1_document,
    check_po_nct03198585_pri1_label,
    check_po_nct03198585_pri1_role,
    check_po_nct03198585_sec1_reported,
    check_po_nct03198585_sec2_reported,
    check_po_nct03198585_sec4_reported,
    check_po_nct03198585_sec4_document,
    check_po_nct03198585_sec4_label,
    check_po_nct03198585_sec4_role,
    check_po_nct03198585_sec5_reported,
    check_po_nct03198585_sec6_reported,
    check_po_nct03198585_sec7_reported,
    check_po_nct03198585_sec8_reported,
    check_po_nct03198585_sec9_reported,
    check_po_nct03198585_sec12_reported,
    check_po_nct03198585_sec13_reported,
    check_po_nct03198585_sec14_reported,
    check_po_nct03198585_sec15_reported,
    check_po_nct03198585_add0_found,
    check_po_nct03198585_add1_found,
    check_po_nct03198585_add2_found,
    check_po_nct03198585_add3_found,
    check_po_nct03198585_add4_found,
    check_po_nct03198585_add5_found,
    check_po_nct03198585_add6_found,
    check_po_nct03198585_add7_found,
    check_po_nct03198585_add8_found,
    check_po_nct03198585_add9_found,
    check_po_nct03198585_add10_found,
    check_po_nct03198585_add11_found,
    check_po_nct03198585_add12_found,
    check_po_nct03198585_add13_found,
    check_po_nct03198585_add14_found,
    check_po_nct03198585_add15_found,
    check_po_nct03198585_add16_found,
    check_po_nct03198585_add17_found,
    check_po_nct03198585_add18_found,
    check_po_nct03198585_add19_found,
    check_po_nct03198585_add20_found,
    check_po_nct03198585_add21_found,
    check_po_nct03198585_add22_found,
    check_po_nct03198585_add23_found,
    check_po_nct03198585_add24_found,
    check_po_nct03198585_add25_found,
    check_po_nct03198585_add26_found,
    check_po_nct03198585_add27_found,
    check_po_nct03198585_add28_found,
    check_po_nct03198585_add29_found,
    check_po_nct03198585_add30_found,
    check_po_nct03198585_add31_found,
    check_po_nct03198585_add32_found,
    check_po_nct03198585_add33_found,
    check_po_nct03198585_add34_found,
    check_po_nct03198585_add35_found,
    check_po_nct03198585_add36_found,
    check_po_nct03198585_add37_found,
    check_po_nct03198585_add38_found,
    check_po_nct03198585_add39_found,
    check_po_nct03198585_add40_found,
    check_po_nct03198585_add41_found,
    check_po_nct03198585_add42_found,
    check_po_nct03198585_add43_found,
    check_po_nct03198585_add44_found,
    check_po_nct03198585_add45_found,
    check_po_nct03198585_add46_found,
    check_po_nct03198585_add47_found,
    check_po_nct03198585_add48_found,
    check_po_nct03198585_add49_found,
    check_po_nct03198585_add50_found,
    check_po_nct03198585_add51_found,
    check_po_nct03198585_add52_found,
    check_po_nct03198585_add53_found,
    check_po_nct03198585_add54_found,
    check_po_nct03502616_basis_derived,
    check_po_nct03502616_pri1_reported,
    check_po_nct03502616_sec1_reported,
    check_po_nct03502616_sec2_reported,
    check_po_nct03502616_sec3_reported,
    check_po_nct03502616_sec6_reported,
    check_po_nct03502616_sec6_document,
    check_po_nct03502616_sec6_label,
    check_po_nct03502616_sec6_instrument,
    check_po_nct03502616_sec6_role,
    check_po_nct03502616_sec9_reported,
    check_po_nct03502616_sec10_reported,
    check_po_nct03502616_sec11_reported,
    check_po_nct03502616_sec12_reported,
    check_po_nct03502616_sec13_reported,
    check_po_nct03502616_sec14_reported,
    check_po_nct03502616_sec15_reported,
    check_po_nct03502616_sec16_reported,
    check_po_nct03502616_sec17_reported,
    check_po_nct03502616_sec19_reported,
    check_po_nct03502616_sec20_reported,
    check_po_nct03502616_sec21_reported,
    check_po_nct03502616_sec22_reported,
    check_po_nct03502616_sec22_document,
    check_po_nct03502616_sec22_label,
    check_po_nct03502616_sec22_instrument,
    check_po_nct03502616_sec22_role,
    check_po_nct03502616_add0_found,
    check_po_nct03502616_add1_found,
    check_po_nct03502616_add2_found,
    check_po_nct03502616_add3_found,
    check_po_nct03502616_add4_found,
    check_po_nct03502616_add5_found,
    check_po_nct03502616_add6_found,
    check_po_nct03502616_add7_found,
    check_po_nct03502616_add8_found,
    check_po_nct03502616_add9_found,
    check_po_nct03502616_add10_found,
    check_po_nct03502616_add11_found,
    check_po_nct03502616_add12_found,
    check_po_nct03502616_add13_found,
    check_po_nct03502616_add14_found,
    check_po_nct03502616_add15_found,
    check_po_nct03502616_add16_found,
    check_po_nct03502616_add17_found,
    check_po_nct03502616_add18_found,
    check_po_nct03502616_add19_found,
    check_po_nct03502616_add20_found,
    check_po_nct03502616_add21_found,
    check_po_nct03502616_add22_found,
    check_po_nct03502616_add23_found,
    check_po_nct03502616_add24_found,
    check_po_nct03502616_add25_found,
    check_po_nct03502616_add26_found,
    check_po_nct03502616_add27_found,
    check_po_nct03502616_add28_found,
    check_po_nct03502616_add29_found,
    check_po_nct03502616_add30_found,
    check_po_nct03502616_add31_found,
    check_po_nct03502616_add32_found,
    check_po_nct03502616_add33_found,
    check_po_nct03502616_add34_found,
    check_po_nct03502616_add35_found,
    check_po_nct03502616_add36_found,
    check_po_nct03502616_add37_found,
    check_po_nct03502616_add38_found,
    check_po_nct03502616_add39_found,
    check_po_nct03502616_add40_found,
    check_po_nct03502616_add41_found,
    check_po_nct03502616_add42_found,
    check_po_nct03502616_add43_found,
    check_po_nct03502616_add44_found,
    check_po_nct03502616_add45_found,
    check_po_nct03502616_add46_found,
    check_po_nct03502616_add47_found,
    check_po_nct03502616_add48_found,
    check_po_nct03502616_add49_found,
    check_po_nct03502616_add50_found,
    check_po_nct03502616_add51_found,
    check_po_nct03502616_add52_found,
    check_po_nct03502616_add53_found,
    check_po_nct03502616_add54_found,
    check_po_nct03502616_add55_found,
    check_po_nct03574597_basis_derived,
    check_po_nct03574597_sec2_reported,
    check_po_nct03574597_sec6_reported,
    check_po_nct03574597_sec7_reported,
    check_po_nct03574597_sec8_reported,
    check_po_nct03574597_sec9_reported,
    check_po_nct03574597_sec10_reported,
    check_po_nct03574597_sec11_reported,
    check_po_nct03574597_sec12_reported,
    check_po_nct03574597_sec12_document,
    check_po_nct03574597_sec12_label,
    check_po_nct03574597_sec12_role,
    check_po_nct03574597_sec13_reported,
    check_po_nct03574597_sec14_reported,
    check_po_nct03574597_sec15_reported,
    check_po_nct03574597_sec16_reported,
    check_po_nct03574597_sec17_reported,
    check_po_nct03574597_sec18_reported,
    check_po_nct03574597_sec19_reported,
    check_po_nct03574597_sec20_reported,
    check_po_nct03574597_sec21_reported,
    check_po_nct03574597_sec22_reported,
    check_po_nct03574597_sec23_reported,
    check_po_nct03574597_sec23_document,
    check_po_nct03574597_sec23_label,
    check_po_nct03574597_sec23_instrument,
    check_po_nct03574597_sec23_role,
    check_po_nct03574597_sec25_reported,
    check_po_nct03574597_sec27_reported,
    check_po_nct03574597_sec28_reported,
    check_po_nct03574597_add0_found,
    check_po_nct03574597_add1_found,
    check_po_nct03574597_add2_found,
    check_po_nct03574597_add3_found,
    check_po_nct03574597_add4_found,
    check_po_nct03574597_add5_found,
    check_po_nct03574597_add6_found,
    check_po_nct03574597_add7_found,
    check_po_nct03574597_add8_found,
    check_po_nct03574597_add9_found,
    check_po_nct03574597_add10_found,
    check_po_nct03574597_add11_found,
    check_po_nct03574597_add12_found,
    check_po_nct03574597_add13_found,
    check_po_nct03574597_add14_found,
    check_po_nct03574597_add15_found,
    check_po_nct03574597_add16_found,
    check_po_nct03574597_add17_found,
    check_po_nct03574597_add18_found,
    check_po_nct03574597_add19_found,
    check_po_nct03574597_add20_found,
    check_po_nct03574597_add21_found,
    check_po_nct03574597_add22_found,
    check_po_nct03574597_add23_found,
    check_po_nct03574597_add24_found,
    check_po_nct03574597_add25_found,
    check_po_nct03574597_add26_found,
    check_po_nct03574597_add27_found,
    check_po_nct03574597_add28_found,
    check_po_nct03574597_add29_found,
    check_po_nct03574597_add30_found,
    check_po_nct03574597_add31_found,
    check_po_nct03574597_add32_found,
    check_po_nct03574597_add33_found,
    check_po_nct03574597_add34_found,
    check_po_nct03574597_add35_found,
    check_po_nct03574597_add36_found,
    check_po_nct03574597_add37_found,
    check_po_nct03574597_add38_found,
    check_po_nct03574597_add39_found,
    check_po_nct03574597_add40_found,
    check_po_nct03574597_add41_found,
    check_po_nct03574597_add42_found,
    check_po_nct03574597_add43_found,
    check_po_nct03574597_add44_found,
    check_po_nct03574597_add45_found,
    check_po_nct03574597_add46_found,
    check_po_nct03574597_add47_found,
    check_po_nct03574597_add48_found,
    check_po_nct03574597_add49_found,
    check_po_nct03574597_add50_found,
    check_po_nct03574597_add51_found,
    check_po_nct03574597_add52_found,
    check_po_nct03667690_basis_derived,
    check_po_nct03667690_pri3_reported,
    check_po_nct03667690_pri3_document,
    check_po_nct03667690_pri3_label,
    check_po_nct03667690_pri3_instrument,
    check_po_nct03667690_pri3_role,
    check_po_nct03667690_pri4_reported,
    check_po_nct03667690_pri4_document,
    check_po_nct03667690_pri4_label,
    check_po_nct03667690_pri4_instrument,
    check_po_nct03667690_pri4_role,
    check_po_nct03667690_sec1_reported,
    check_po_nct03667690_sec1_document,
    check_po_nct03667690_sec1_label,
    check_po_nct03667690_sec1_instrument,
    check_po_nct03667690_sec1_role,
    check_po_nct03667690_sec2_reported,
    check_po_nct03667690_sec2_document,
    check_po_nct03667690_sec2_label,
    check_po_nct03667690_sec2_instrument,
    check_po_nct03667690_sec2_role,
    check_po_nct03667690_sec5_reported,
    check_po_nct03667690_sec5_document,
    check_po_nct03667690_sec5_label,
    check_po_nct03667690_sec5_instrument,
    check_po_nct03667690_sec5_role,
    check_po_nct03667690_sec6_reported,
    check_po_nct03667690_sec6_document,
    check_po_nct03667690_sec6_label,
    check_po_nct03667690_sec6_instrument,
    check_po_nct03667690_sec6_role,
    check_po_nct03667690_sec7_reported,
    check_po_nct03667690_sec7_document,
    check_po_nct03667690_sec7_label,
    check_po_nct03667690_sec7_role,
    check_po_nct03667690_sec8_reported,
    check_po_nct03667690_sec8_document,
    check_po_nct03667690_sec8_label,
    check_po_nct03667690_sec8_role,
    check_po_nct03667690_sec11_reported,
    check_po_nct03667690_sec11_document,
    check_po_nct03667690_sec11_label,
    check_po_nct03667690_sec11_instrument,
    check_po_nct03667690_sec11_role,
    check_po_nct03667690_sec12_reported,
    check_po_nct03667690_sec13_reported,
    check_po_nct03667690_sec14_reported,
    check_po_nct03667690_add0_found,
    check_po_nct03667690_add1_found,
    check_po_nct03667690_add2_found,
    check_po_nct03667690_add3_found,
    check_po_nct03667690_add4_found,
    check_po_nct03667690_add5_found,
    check_po_nct03667690_add6_found,
    check_po_nct03667690_add7_found,
    check_po_nct03667690_add8_found,
    check_po_nct03667690_add9_found,
    check_po_nct03667690_add10_found,
    check_po_nct03667690_add11_found,
    check_po_nct03667690_add12_found,
    check_po_nct03667690_add13_found,
    check_po_nct03667690_add14_found,
    check_po_nct03667690_add15_found,
    check_po_nct03667690_add16_found,
    check_po_nct03667690_add17_found,
    check_po_nct03667690_add18_found,
    check_po_nct03667690_add19_found,
    check_po_nct03667690_add20_found,
    check_po_nct03667690_add21_found,
    check_po_nct03667690_add22_found,
    check_po_nct03667690_add23_found,
    check_po_nct03667690_add24_found,
    check_po_nct03667690_add25_found,
    check_po_nct03667690_add26_found,
    check_po_nct03667690_add27_found,
    check_po_nct03667690_add28_found,
    check_po_nct03667690_add29_found,
    check_po_nct03667690_add30_found,
    check_po_nct03667690_add31_found,
    check_po_nct03667690_add32_found,
    check_po_nct03667690_add33_found,
    check_po_nct03667690_add34_found,
    check_po_nct03667690_add35_found,
    check_po_nct03667690_add36_found,
    check_po_nct03667690_add37_found,
    check_po_nct03667690_add38_found,
    check_po_nct03667690_add39_found,
    check_po_nct03667690_add40_found,
    check_po_nct03667690_add41_found,
    check_po_nct03667690_add42_found,
    check_po_nct03667690_add43_found,
    check_po_nct03667690_add44_found,
    check_po_nct03667690_add45_found,
    check_po_nct03667690_add46_found,
    check_po_nct03667690_add47_found,
    check_po_nct03667690_add48_found,
    check_po_nct03667690_add49_found,
    check_po_nct03667690_add50_found,
    check_po_nct03667690_add51_found,
    check_po_nct03667690_add52_found,
    check_po_nct03667690_add53_found,
    check_po_nct03667690_add54_found,
    check_po_nct03667690_add55_found,
    check_po_nct03667690_add56_found,
    check_po_nct03667690_add57_found,
    check_po_nct03667690_add58_found,
    check_po_nct03667690_add59_found,
    check_po_nct03667690_add60_found,
    check_po_nct03667690_add61_found,
    check_po_nct03667690_add62_found,
    check_po_nct03667690_add63_found,
    check_po_nct03667690_add64_found,
    check_po_nct03667690_add65_found,
    check_po_nct03667690_add66_found,
    check_po_nct03667690_add67_found,
    check_po_nct03667690_add68_found,
    check_po_nct03667690_add69_found,
    check_po_nct03667690_add70_found,
    check_po_nct03667690_add71_found,
    check_po_nct03667690_add72_found,
    check_po_nct03667690_add73_found,
    check_po_nct03667690_add74_found,
    check_po_nct03869177_basis_derived,
    check_po_nct03869177_pri1_reported,
    check_po_nct03869177_pri1_document,
    check_po_nct03869177_pri1_label,
    check_po_nct03869177_pri1_instrument,
    check_po_nct03869177_pri1_role,
    check_po_nct03869177_pri3_reported,
    check_po_nct03869177_pri3_document,
    check_po_nct03869177_pri3_label,
    check_po_nct03869177_pri3_instrument,
    check_po_nct03869177_pri3_role,
    check_po_nct03869177_sec2_reported,
    check_po_nct03869177_sec2_document,
    check_po_nct03869177_sec2_label,
    check_po_nct03869177_sec2_instrument,
    check_po_nct03869177_sec2_role,
    check_po_nct03869177_sec6_reported,
    check_po_nct03869177_sec7_reported,
    check_po_nct03869177_sec10_reported,
    check_po_nct03869177_sec11_reported,
    check_po_nct03869177_sec14_reported,
    check_po_nct03869177_sec15_reported,
    check_po_nct03869177_sec16_reported,
    check_po_nct03869177_oth1_reported,
    check_po_nct03869177_oth2_reported,
    check_po_nct03869177_oth4_reported,
    check_po_nct03869177_add0_found,
    check_po_nct03869177_add1_found,
    check_po_nct03869177_add2_found,
    check_po_nct03869177_add3_found,
    check_po_nct03869177_add4_found,
    check_po_nct03869177_add5_found,
    check_po_nct03869177_add6_found,
    check_po_nct03869177_add7_found,
    check_po_nct03869177_add8_found,
    check_po_nct03869177_add9_found,
    check_po_nct03869177_add10_found,
    check_po_nct03869177_add11_found,
    check_po_nct03869177_add12_found,
    check_po_nct03869177_add13_found,
    check_po_nct03869177_add14_found,
    check_po_nct03869177_add15_found,
    check_po_nct03869177_add16_found,
    check_po_nct03869177_add17_found,
    check_po_nct03869177_add18_found,
    check_po_nct03869177_add19_found,
    check_po_nct03869177_add20_found,
    check_po_nct03869177_add21_found,
    check_po_nct03869177_add22_found,
    check_po_nct03869177_add23_found,
    check_po_nct03869177_add24_found,
    check_po_nct03869177_add25_found,
    check_po_nct03869177_add26_found,
    check_po_nct03869177_add27_found,
    check_po_nct03869177_add28_found,
    check_po_nct03869177_add29_found,
    check_po_nct03869177_add30_found,
    check_po_nct03869177_add31_found,
    check_po_nct03869177_add32_found,
    check_po_nct03869177_add33_found,
    check_po_nct03869177_add34_found,
    check_po_nct03869177_add35_found,
    check_po_nct03869177_add36_found,
    check_po_nct03869177_add37_found,
    check_po_nct03869177_add38_found,
    check_po_nct03869177_add39_found,
    check_po_nct03869177_add40_found,
    check_po_nct03869177_add41_found,
    check_po_nct03869177_add42_found,
    check_po_nct03869177_add43_found,
    check_po_nct03869177_add44_found,
    check_po_nct03869177_add45_found,
    check_po_nct03869177_add46_found,
    check_po_nct03869177_add47_found,
    check_po_nct03869177_add48_found,
    check_po_nct03869177_add49_found,
    check_po_nct03869177_add50_found,
    check_po_nct03869177_add51_found,
    check_po_nct03869177_add52_found,
    check_po_nct03869177_add53_found,
    check_po_nct03869177_add54_found,
    check_po_nct03869177_add55_found,
    check_po_nct03869177_add56_found,
    check_po_nct03869177_add57_found,
    check_po_nct03869177_add58_found,
    check_po_nct03869177_add59_found,
    check_po_nct03869177_add60_found,
    check_po_nct03869177_add61_found,
    check_po_nct03869177_add62_found,
    check_po_nct03869177_add63_found,
    check_po_nct03869177_add64_found,
    check_po_nct03869177_add65_found,
    check_po_nct03869177_add66_found,
    check_po_nct03869177_add67_found,
    check_po_nct03869177_add68_found,
    check_po_nct03869177_add69_found,
    check_po_nct03869177_add70_found,
    check_po_nct03869177_add71_found,
    check_po_nct03869177_add72_found,
    check_po_nct03869177_add73_found,
    check_po_nct03869177_add74_found,
    check_po_nct03869177_add75_found,
    check_po_nct03869177_add76_found,
    check_po_nct03869177_add77_found,
    check_po_nct03869177_add78_found,
    check_po_nct03869177_add79_found,
    check_po_nct03869177_add80_found,
    check_po_nct03869177_add81_found,
    check_po_nct03869177_add82_found,
    check_po_nct03869177_add83_found,
    check_po_nct03869177_add84_found,
    check_po_nct03869177_add85_found,
    check_po_nct03869177_add86_found,
    check_po_nct03869177_add87_found,
    check_po_nct03869177_add88_found,
    check_po_nct03869177_add89_found,
    check_po_nct03869177_add90_found,
    check_po_nct03869177_add91_found,
    check_po_nct03869177_add92_found,
    check_po_nct03869177_add93_found,
    check_po_nct03869177_add94_found,
    check_po_nct03869177_add95_found,
    check_po_nct03869177_add96_found,
    check_po_nct03869177_add97_found,
    check_po_nct03869177_add98_found,
    check_po_nct03869177_add99_found,
    check_po_nct03869177_add100_found,
    check_po_nct03869177_add101_found,
    check_po_nct03869177_add102_found,
    check_po_nct03869177_add103_found,
    check_po_nct03869177_add104_found,
    check_po_nct03869177_add105_found,
    check_po_nct03869177_add106_found,
    check_po_nct03869177_add107_found,
    check_po_nct03869177_add108_found,
    check_po_nct03869177_add109_found,
    check_po_nct04033003_basis_derived,
    check_po_nct04033003_pri1_reported,
    check_po_nct04033003_pri1_document,
    check_po_nct04033003_pri1_label,
    check_po_nct04033003_pri1_instrument,
    check_po_nct04033003_pri1_role,
    check_po_nct04033003_pri4_reported,
    check_po_nct04033003_sec2_reported,
    check_po_nct04033003_sec5_reported,
    check_po_nct04033003_sec5_document,
    check_po_nct04033003_sec5_label,
    check_po_nct04033003_sec5_role,
    check_po_nct04033003_sec6_reported,
    check_po_nct04033003_sec7_reported,
    check_po_nct04033003_sec8_reported,
    check_po_nct04033003_sec9_reported,
    check_po_nct04033003_sec11_reported,
    check_po_nct04033003_add0_found,
    check_po_nct04033003_add1_found,
    check_po_nct04033003_add2_found,
    check_po_nct04033003_add3_found,
    check_po_nct04033003_add4_found,
    check_po_nct04033003_add5_found,
    check_po_nct04033003_add6_found,
    check_po_nct04033003_add7_found,
    check_po_nct04033003_add8_found,
    check_po_nct04033003_add9_found,
    check_po_nct04033003_add10_found,
    check_po_nct04033003_add11_found,
    check_po_nct04033003_add12_found,
    check_po_nct04033003_add13_found,
    check_po_nct04033003_add14_found,
    check_po_nct04033003_add15_found,
    check_po_nct04033003_add16_found,
    check_po_nct04033003_add17_found,
    check_po_nct04033003_add18_found,
    check_po_nct04033003_add19_found,
    check_po_nct04033003_add20_found,
    check_po_nct04033003_add21_found,
    check_po_nct04033003_add22_found,
    check_po_nct04033003_add23_found,
    check_po_nct04033003_add24_found,
    check_po_nct04033003_add25_found,
    check_po_nct04033003_add26_found,
    check_po_nct04033003_add27_found,
    check_po_nct04033003_add28_found,
    check_po_nct04033003_add29_found,
    check_po_nct04033003_add30_found,
    check_po_nct04033003_add31_found,
    check_po_nct04033003_add32_found,
    check_po_nct04033003_add33_found,
    check_po_nct04033003_add34_found,
    check_po_nct04033003_add35_found,
    check_po_nct04033003_add36_found,
    check_po_nct04033003_add37_found,
    check_po_nct04033003_add38_found,
    check_po_nct04033003_add39_found,
    check_po_nct04033003_add40_found,
    check_po_nct04033003_add41_found,
    check_po_nct04033003_add42_found,
    check_po_nct04033003_add43_found,
    check_po_nct04048967_basis_derived,
    check_po_nct04048967_pri1_reported,
    check_po_nct04048967_pri2_reported,
    check_po_nct04048967_pri3_reported,
    check_po_nct04048967_pri4_reported,
    check_po_nct04048967_pri5_reported,
    check_po_nct04048967_pri6_reported,
    check_po_nct04048967_pri7_reported,
    check_po_nct04048967_pri7_document,
    check_po_nct04048967_pri7_label,
    check_po_nct04048967_pri7_instrument,
    check_po_nct04048967_pri7_role,
    check_po_nct04048967_sec3_reported,
    check_po_nct04048967_sec4_reported,
    check_po_nct04048967_sec7_reported,
    check_po_nct04048967_sec8_reported,
    check_po_nct04048967_sec9_reported,
    check_po_nct04048967_sec10_reported,
    check_po_nct04048967_add0_found,
    check_po_nct04048967_add1_found,
    check_po_nct04048967_add2_found,
    check_po_nct04048967_add3_found,
    check_po_nct04048967_add4_found,
    check_po_nct04048967_add5_found,
    check_po_nct04048967_add6_found,
    check_po_nct04048967_add7_found,
    check_po_nct04048967_add8_found,
    check_po_nct04048967_add9_found,
    check_po_nct04048967_add10_found,
    check_po_nct04048967_add11_found,
    check_po_nct04048967_add12_found,
    check_po_nct04048967_add13_found,
    check_po_nct04048967_add14_found,
    check_po_nct04048967_add15_found,
    check_po_nct04048967_add16_found,
    check_po_nct04048967_add17_found,
    check_po_nct04048967_add18_found,
    check_po_nct04048967_add19_found,
    check_po_nct04048967_add20_found,
    check_po_nct04048967_add21_found,
    check_po_nct04048967_add22_found,
    check_po_nct04048967_add23_found,
    check_po_nct04048967_add24_found,
    check_po_nct04048967_add25_found,
    check_po_nct04048967_add26_found,
    check_po_nct04048967_add27_found,
    check_po_nct04048967_add28_found,
    check_po_nct04048967_add29_found,
    check_po_nct04048967_add30_found,
    check_po_nct04048967_add31_found,
    check_po_nct04048967_add32_found,
    check_po_nct04048967_add33_found,
    check_po_nct04048967_add34_found,
    check_po_nct04048967_add35_found,
    check_po_nct04048967_add36_found,
    check_po_nct04048967_add37_found,
    check_po_nct04048967_add38_found,
    check_po_nct04048967_add39_found,
    check_po_nct04048967_add40_found,
    check_po_nct04048967_add41_found,
    check_po_nct04048967_add42_found,
    check_po_nct04048967_add43_found,
    check_po_nct04048967_add44_found,
    check_po_nct04048967_add45_found,
    check_po_nct04048967_add46_found,
    check_po_nct04048967_add47_found,
    check_po_nct04048967_add48_found,
    check_po_nct04048967_add49_found,
    check_po_nct04048967_add50_found,
    check_po_nct04048967_add51_found,
    check_po_nct04048967_add52_found,
    check_po_nct04048967_add53_found,
    check_po_nct04048967_add54_found,
    check_po_nct04048967_add55_found,
    check_po_nct04048967_add56_found,
    check_po_nct04048967_add57_found,
    check_po_nct04048967_add58_found,
    check_po_nct04048967_add59_found,
    check_po_nct04048967_add60_found,
    check_po_nct04048967_add61_found,
    check_po_nct04048967_add62_found,
    check_po_nct04048967_add63_found,
    check_po_nct04048967_add64_found,
    check_po_nct04048967_add65_found,
    check_po_nct04048967_add66_found,
    check_po_nct04048967_add67_found,
    check_po_nct04048967_add68_found,
    check_po_nct04048967_add69_found,
    check_po_nct04048967_add70_found,
    check_po_nct04048967_add71_found,
    check_po_nct04048967_add72_found,
    check_po_nct04048967_add73_found,
    check_po_nct04048967_add74_found,
    check_po_nct04048967_add75_found,
    check_po_nct04048967_add76_found,
    check_po_nct04048967_add77_found,
    check_po_nct04048967_add78_found,
    check_po_nct04048967_add79_found,
    check_po_nct04048967_add80_found,
    check_po_nct04048967_add81_found,
    check_po_nct04048967_add82_found,
    check_po_nct04048967_add83_found,
    check_po_nct04048967_add84_found,
    check_po_nct04048967_add85_found,
    check_po_nct04048967_add86_found,
    check_po_nct04048967_add87_found,
    check_po_nct04048967_add88_found,
    check_po_nct04048967_add89_found,
    check_po_nct04048967_add90_found,
    check_po_nct04048967_add91_found,
    check_po_nct04048967_add92_found,
    check_po_nct04048967_add93_found,
    check_po_nct04048967_add94_found,
    check_po_nct04048967_add95_found,
    check_po_nct04048967_add96_found,
    check_po_nct04048967_add97_found,
    check_po_nct04048967_add98_found,
    check_po_nct04048967_add99_found,
    check_po_nct04048967_add100_found,
    check_po_nct04048967_add101_found,
    check_po_nct04048967_add102_found,
    check_po_nct04048967_add103_found,
    check_po_nct04048967_add104_found,
    check_po_nct04048967_add105_found,
    check_po_nct04048967_add106_found,
    check_po_nct04048967_add107_found,
    check_po_nct04048967_add108_found,
    check_po_nct04048967_add109_found,
    check_po_nct04048967_add110_found,
    check_po_nct04048967_add111_found,
    check_po_nct04066881_basis_derived,
    check_po_nct04066881_pri1_reported,
    check_po_nct04066881_pri2_reported,
    check_po_nct04066881_pri3_reported,
    check_po_nct04066881_pri4_reported,
    check_po_nct04066881_sec1_reported,
    check_po_nct04066881_sec2_reported,
    check_po_nct04066881_sec3_reported,
    check_po_nct04066881_sec4_reported,
    check_po_nct04066881_sec5_reported,
    check_po_nct04066881_sec6_reported,
    check_po_nct04066881_sec7_reported,
    check_po_nct04066881_sec8_reported,
    check_po_nct04066881_sec9_reported,
    check_po_nct04066881_sec10_reported,
    check_po_nct04066881_sec11_reported,
    check_po_nct04066881_sec12_reported,
    check_po_nct04066881_add0_found,
    check_po_nct04066881_add1_found,
    check_po_nct04066881_add2_found,
    check_po_nct04066881_add3_found,
    check_po_nct04066881_add4_found,
    check_po_nct04066881_add5_found,
    check_po_nct04066881_add6_found,
    check_po_nct04066881_add7_found,
    check_po_nct04224987_basis_derived,
    check_po_nct04224987_pri1_reported,
    check_po_nct04224987_pri1_document,
    check_po_nct04224987_pri1_label,
    check_po_nct04224987_pri1_role,
    check_po_nct04224987_pri2_reported,
    check_po_nct04224987_pri2_document,
    check_po_nct04224987_pri2_label,
    check_po_nct04224987_pri2_instrument,
    check_po_nct04224987_pri2_role,
    check_po_nct04224987_pri3_reported,
    check_po_nct04224987_pri3_document,
    check_po_nct04224987_pri3_label,
    check_po_nct04224987_pri3_role,
    check_po_nct04224987_pri4_reported,
    check_po_nct04224987_pri4_document,
    check_po_nct04224987_pri4_label,
    check_po_nct04224987_pri4_instrument,
    check_po_nct04224987_pri4_role,
    check_po_nct04224987_pri5_reported,
    check_po_nct04224987_pri5_document,
    check_po_nct04224987_pri5_label,
    check_po_nct04224987_pri5_instrument,
    check_po_nct04224987_pri5_role,
    check_po_nct04224987_sec2_reported,
    check_po_nct04224987_sec2_document,
    check_po_nct04224987_sec2_label,
    check_po_nct04224987_sec2_instrument,
    check_po_nct04224987_sec2_role,
    check_po_nct04224987_sec10_reported,
    check_po_nct04224987_sec10_document,
    check_po_nct04224987_sec10_label,
    check_po_nct04224987_sec10_role,
    check_po_nct04224987_sec14_reported,
    check_po_nct04224987_sec15_reported,
    check_po_nct04224987_sec16_reported,
    check_po_nct04224987_add0_found,
    check_po_nct04224987_add1_found,
    check_po_nct04224987_add2_found,
    check_po_nct04224987_add3_found,
    check_po_nct04224987_add4_found,
    check_po_nct04224987_add5_found,
    check_po_nct04224987_add6_found,
    check_po_nct04224987_add7_found,
    check_po_nct04224987_add8_found,
    check_po_nct04224987_add9_found,
    check_po_nct04224987_add10_found,
    check_po_nct04224987_add11_found,
    check_po_nct04224987_add12_found,
    check_po_nct04224987_add13_found,
    check_po_nct04224987_add14_found,
    check_po_nct04224987_add15_found,
    check_po_nct04224987_add16_found,
    check_po_nct04224987_add17_found,
    check_po_nct04224987_add18_found,
    check_po_nct04224987_add19_found,
    check_po_nct04224987_add20_found,
    check_po_nct04224987_add21_found,
    check_po_nct04224987_add22_found,
    check_po_nct04224987_add23_found,
    check_po_nct04224987_add24_found,
    check_po_nct04224987_add25_found,
    check_po_nct04224987_add26_found,
    check_po_nct04224987_add27_found,
    check_po_nct04224987_add28_found,
    check_po_nct04224987_add29_found,
    check_po_nct04224987_add30_found,
    check_po_nct04224987_add31_found,
    check_po_nct04224987_add32_found,
    check_po_nct04224987_add33_found,
    check_po_nct04224987_add34_found,
    check_po_nct04224987_add35_found,
    check_po_nct04224987_add36_found,
    check_po_nct04224987_add37_found,
    check_po_nct04224987_add38_found,
    check_po_nct04224987_add39_found,
    check_po_nct04224987_add40_found,
    check_po_nct04224987_add41_found,
    check_po_nct04224987_add42_found,
    check_po_nct04224987_add43_found,
    check_po_nct04224987_add44_found,
    check_po_nct04224987_add45_found,
    check_po_nct04224987_add46_found,
    check_po_nct04224987_add47_found,
    check_po_nct04224987_add48_found,
    check_po_nct04224987_add49_found,
    check_po_nct04224987_add50_found,
    check_po_nct04224987_add51_found,
    check_po_nct04224987_add52_found,
    check_po_nct04224987_add53_found,
    check_po_nct04224987_add54_found,
    check_po_nct04224987_add55_found,
    check_po_nct04224987_add56_found,
    check_po_nct04224987_add57_found,
    check_po_nct04224987_add58_found,
    check_po_nct04224987_add59_found,
    check_po_nct04224987_add60_found,
    check_po_nct04224987_add61_found,
    check_po_nct04247009_basis_derived,
    check_po_nct04247009_pri2_reported,
    check_po_nct04247009_pri4_reported,
    check_po_nct04247009_pri6_reported,
    check_po_nct04247009_sec1_reported,
    check_po_nct04247009_sec2_reported,
    check_po_nct04247009_sec3_reported,
    check_po_nct04247009_sec5_reported,
    check_po_nct04247009_sec6_reported,
    check_po_nct04247009_sec8_reported,
    check_po_nct04247009_sec9_reported,
    check_po_nct04247009_sec10_reported,
    check_po_nct04247009_add0_found,
    check_po_nct04247009_add1_found,
    check_po_nct04247009_add2_found,
    check_po_nct04247009_add3_found,
    check_po_nct04247009_add4_found,
    check_po_nct04247009_add5_found,
    check_po_nct04247009_add6_found,
    check_po_nct04247009_add7_found,
    check_po_nct04247009_add8_found,
    check_po_nct04247009_add9_found,
    check_po_nct04247009_add10_found,
    check_po_nct04247009_add11_found,
    check_po_nct04247009_add12_found,
    check_po_nct04247009_add13_found,
    check_po_nct04247009_add14_found,
    check_po_nct04247009_add15_found,
    check_po_nct04247009_add16_found,
    check_po_nct04247009_add17_found,
    check_po_nct04247009_add18_found,
    check_po_nct04247009_add19_found,
    check_po_nct04247009_add20_found,
    check_po_nct04247009_add21_found,
    check_po_nct04247009_add22_found,
    check_po_nct04247009_add23_found,
    check_po_nct04247009_add24_found,
    check_po_nct04247009_add25_found,
    check_po_nct04247009_add26_found,
    check_po_nct04247009_add27_found,
    check_po_nct04247009_add28_found,
    check_po_nct04247009_add29_found,
    check_po_nct04247009_add30_found,
    check_po_nct04247009_add31_found,
    check_po_nct04247009_add32_found,
    check_po_nct04247009_add33_found,
    check_po_nct04247009_add34_found,
    check_po_nct04247009_add35_found,
    check_po_nct04247009_add36_found,
    check_po_nct04247009_add37_found,
    check_po_nct04247009_add38_found,
    check_po_nct04247009_add39_found,
    check_po_nct04247009_add40_found,
    check_po_nct04247009_add41_found,
    check_po_nct04247009_add42_found,
    check_po_nct04247009_add43_found,
    check_po_nct04247009_add44_found,
    check_po_nct04247009_add45_found,
    check_po_nct04247009_add46_found,
    check_po_nct04247009_add47_found,
    check_po_nct04247009_add48_found,
    check_po_nct04247009_add49_found,
    check_po_nct04247009_add50_found,
    check_po_nct04247009_add51_found,
    check_po_nct04247009_add52_found,
    check_po_nct04247009_add53_found,
    check_po_nct04247009_add54_found,
    check_po_nct04247009_add55_found,
    check_po_nct04247009_add56_found,
    check_po_nct04247009_add57_found,
    check_po_nct04247009_add58_found,
    check_po_nct04247009_add59_found,
    check_po_nct04247009_add60_found,
    check_po_nct04247009_add61_found,
    check_po_nct04247009_add62_found,
    check_po_nct04369326_basis_derived,
    check_po_nct04369326_sec1_reported,
    check_po_nct04369326_sec1_document,
    check_po_nct04369326_sec1_label,
    check_po_nct04369326_sec1_role,
    check_po_nct04369326_sec7_reported,
    check_po_nct04369326_sec7_document,
    check_po_nct04369326_sec7_label,
    check_po_nct04369326_sec7_role,
    check_po_nct04369326_sec14_reported,
    check_po_nct04369326_sec15_reported,
    check_po_nct04369326_sec16_reported,
    check_po_nct04369326_add0_found,
    check_po_nct04369326_add1_found,
    check_po_nct04369326_add2_found,
    check_po_nct04369326_add3_found,
    check_po_nct04369326_add4_found,
    check_po_nct04369326_add5_found,
    check_po_nct04369326_add6_found,
    check_po_nct04369326_add7_found,
    check_po_nct04369326_add8_found,
    check_po_nct04369326_add9_found,
    check_po_nct04369326_add10_found,
    check_po_nct04369326_add11_found,
    check_po_nct04369326_add12_found,
    check_po_nct04369326_add13_found,
    check_po_nct04369326_add14_found,
    check_po_nct04369326_add15_found,
    check_po_nct04369326_add16_found,
    check_po_nct04369326_add17_found,
    check_po_nct04369326_add18_found,
    check_po_nct04369326_add19_found,
    check_po_nct04424511_basis_derived,
    check_po_nct04424511_pri1_reported,
    check_po_nct04424511_sec1_reported,
    check_po_nct04424511_sec5_reported,
    check_po_nct04424511_sec8_reported,
    check_po_nct04424511_sec9_reported,
    check_po_nct04424511_sec10_reported,
    check_po_nct04424511_sec11_reported,
    check_po_nct04424511_sec12_reported,
    check_po_nct04424511_sec13_reported,
    check_po_nct04424511_sec14_reported,
    check_po_nct04424511_sec15_reported,
    check_po_nct04424511_sec16_reported,
    check_po_nct04424511_sec17_reported,
    check_po_nct04424511_sec18_reported,
    check_po_nct04424511_sec19_reported,
    check_po_nct04424511_add0_found,
    check_po_nct04424511_add1_found,
    check_po_nct04424511_add2_found,
    check_po_nct04424511_add3_found,
    check_po_nct04424511_add4_found,
    check_po_nct04424511_add5_found,
    check_po_nct04424511_add6_found,
    check_po_nct04424511_add7_found,
    check_po_nct04424511_add8_found,
    check_po_nct04424511_add9_found,
    check_po_nct04424511_add10_found,
    check_po_nct04424511_add11_found,
    check_po_nct04424511_add12_found,
    check_po_nct04424511_add13_found,
    check_po_nct04424511_add14_found,
    check_po_nct04424511_add15_found,
    check_po_nct05254002_basis_derived,
    check_po_nct05254002_pri1_reported,
    check_po_nct05254002_pri1_document,
    check_po_nct05254002_pri1_label,
    check_po_nct05254002_pri1_instrument,
    check_po_nct05254002_pri1_role,
    check_po_nct05254002_pri2_reported,
    check_po_nct05254002_pri2_document,
    check_po_nct05254002_pri2_label,
    check_po_nct05254002_pri2_instrument,
    check_po_nct05254002_pri2_role,
    check_po_nct05254002_sec3_reported,
    check_po_nct05254002_sec3_document,
    check_po_nct05254002_sec3_label,
    check_po_nct05254002_sec3_instrument,
    check_po_nct05254002_sec3_role,
    check_po_nct05254002_sec5_reported,
    check_po_nct05254002_sec5_document,
    check_po_nct05254002_sec5_label,
    check_po_nct05254002_sec5_instrument,
    check_po_nct05254002_sec5_role,
    check_po_nct05254002_sec7_reported,
    check_po_nct05254002_sec7_document,
    check_po_nct05254002_sec7_label,
    check_po_nct05254002_sec7_role,
    check_po_nct05254002_sec8_reported,
    check_po_nct05254002_sec9_reported,
    check_po_nct05254002_sec9_document,
    check_po_nct05254002_sec9_label,
    check_po_nct05254002_sec9_role,
    check_po_nct05254002_sec11_reported,
    check_po_nct05254002_sec14_reported,
    check_po_nct05254002_sec14_document,
    check_po_nct05254002_sec14_label,
    check_po_nct05254002_sec14_role,
    check_po_nct05254002_sec16_reported,
    check_po_nct05254002_sec16_document,
    check_po_nct05254002_sec16_label,
    check_po_nct05254002_sec16_role,
    check_po_nct05254002_sec18_reported,
    check_po_nct05254002_sec19_reported,
    check_po_nct05254002_sec20_reported,
    check_po_nct05254002_sec21_reported,
    check_po_nct05254002_sec22_reported,
    check_po_nct05254002_sec22_document,
    check_po_nct05254002_sec22_label,
    check_po_nct05254002_sec22_role,
    check_po_nct05254002_add0_found,
    check_po_nct05254002_add1_found,
    check_po_nct05254002_add2_found,
    check_po_nct05254002_add3_found,
    check_po_nct05254002_add4_found,
    check_po_nct05254002_add5_found,
    check_po_nct05254002_add6_found,
    check_po_nct05254002_add7_found,
    check_po_nct05254002_add8_found,
    check_po_nct05254002_add9_found,
    check_po_nct05254002_add10_found,
    check_po_nct05254002_add11_found,
    check_po_nct05254002_add12_found,
    check_po_nct05254002_add13_found,
    check_po_nct05254002_add14_found,
    check_po_nct05254002_add15_found,
    check_po_nct05254002_add16_found,
    check_po_nct05254002_add17_found,
    check_po_nct05254002_add18_found,
    check_po_nct05485402_basis_derived,
    check_po_nct05485402_pri1_reported,
    check_po_nct05485402_pri1_document,
    check_po_nct05485402_pri1_label,
    check_po_nct05485402_pri1_instrument,
    check_po_nct05485402_pri1_role,
    check_po_nct05485402_sec1_reported,
    check_po_nct05485402_sec1_document,
    check_po_nct05485402_sec1_label,
    check_po_nct05485402_sec1_instrument,
    check_po_nct05485402_sec1_role,
    check_po_nct05485402_sec2_reported,
    check_po_nct05485402_sec3_reported,
    check_po_nct05485402_sec3_document,
    check_po_nct05485402_sec3_label,
    check_po_nct05485402_sec3_instrument,
    check_po_nct05485402_sec3_role,
    check_po_nct05485402_sec4_reported,
    check_po_nct05485402_sec4_document,
    check_po_nct05485402_sec4_label,
    check_po_nct05485402_sec4_instrument,
    check_po_nct05485402_sec4_role,
    check_po_nct05485402_sec5_reported,
    check_po_nct05485402_sec7_reported,
    check_po_nct05485402_sec7_document,
    check_po_nct05485402_sec7_label,
    check_po_nct05485402_sec7_instrument,
    check_po_nct05485402_sec7_role,
    check_po_nct05485402_sec9_reported,
    check_po_nct05485402_sec9_document,
    check_po_nct05485402_sec9_label,
    check_po_nct05485402_sec9_instrument,
    check_po_nct05485402_sec9_role,
    check_po_nct05485402_sec10_reported,
    check_po_nct05485402_sec11_reported,
    check_po_nct05485402_sec12_reported,
    check_po_nct05485402_sec13_reported,
    check_po_nct05485402_sec15_reported,
    check_po_nct05485402_sec16_reported,
    check_po_nct05485402_sec17_reported,
    check_po_nct05485402_sec18_reported,
    check_po_nct05485402_sec19_reported,
    check_po_nct05485402_sec20_reported,
    check_po_nct05485402_sec21_reported,
    check_po_nct05485402_sec23_reported,
    check_po_nct05485402_sec24_reported,
    check_po_nct05485402_sec25_reported,
    check_po_nct05485402_sec26_reported,
    check_po_nct05485402_sec27_reported,
    check_po_nct05485402_sec28_reported,
    check_po_nct05485402_sec29_reported,
    check_po_nct05485402_sec31_reported,
    check_po_nct05485402_sec32_reported,
    check_po_nct05485402_sec33_reported,
    check_po_nct05485402_sec33_document,
    check_po_nct05485402_sec33_label,
    check_po_nct05485402_sec33_role,
    check_po_nct05485402_sec34_reported,
    check_po_nct05485402_sec36_reported,
    check_po_nct05485402_sec37_reported,
    check_po_nct05485402_sec38_reported,
    check_po_nct05485402_add0_found,
    check_po_nct05485402_add1_found,
    check_po_nct05485402_add2_found,
    check_po_nct05485402_add3_found,
    check_po_nct05485402_add4_found,
    check_po_nct05485402_add5_found,
    check_po_nct05485402_add6_found,
    check_po_nct05485402_add7_found,
    check_po_nct05485402_add8_found,
    check_po_nct05485402_add9_found,
    check_po_nct05485402_add10_found,
    check_po_nct05485402_add11_found,
    check_po_nct05485402_add12_found,
    check_po_nct05485402_add13_found,
    check_po_nct05485402_add14_found,
    check_po_nct05485402_add15_found,
    check_po_nct05485402_add16_found,
    check_po_nct05485402_add17_found,
    check_po_nct05485402_add18_found,
    check_po_nct05485402_add19_found,
    check_po_nct05485402_add20_found,
    check_po_nct05485402_add21_found,
    check_po_nct05485402_add22_found,
    check_po_nct05485402_add23_found,
    check_po_nct05485402_add24_found,
    check_po_nct05485402_add25_found,
    check_po_nct05485402_add26_found,
    check_po_nct05485402_add27_found,
    check_po_nct05485402_add28_found,
    check_po_nct05485402_add29_found,
    check_po_nct05485402_add30_found,
    check_po_nct05485402_add31_found,
    check_po_nct05485402_add32_found,
    check_po_nct05485402_add33_found,
    check_po_nct05485402_add34_found,
    check_po_nct05485402_add35_found,
    check_po_nct05485402_add36_found,
    check_po_nct05485402_add37_found,
    check_po_nct05485402_add38_found,
    check_po_nct05485402_add39_found,
    check_po_nct05485402_add40_found,
    check_po_nct05485402_add41_found,
    check_po_nct05485402_add42_found,
    check_po_nct05485402_add43_found,
    check_po_nct05485402_add44_found,
    check_po_nct05485402_add45_found,
    check_po_nct05485402_add46_found,
    check_po_nct05485402_add47_found,
    check_po_nct05485402_add48_found,
    check_po_nct05485402_add49_found,
    check_po_nct05485402_add50_found,
    check_po_nct05485402_add51_found,
    check_po_nct05485402_add52_found,
    check_po_nct05485402_add53_found,
    check_po_nct05485402_add54_found,
    check_po_nct05485402_add55_found,
    check_po_nct05485402_add56_found,
    check_po_nct05485402_add57_found,
    check_po_nct05485402_add58_found,
    check_po_nct05485402_add59_found,
    check_po_nct05485402_add60_found,
    check_po_nct05485402_add61_found,
    check_po_nct05485402_add62_found,
    check_po_nct05485402_add63_found,
    check_po_nct05485402_add64_found,
    check_po_nct05485402_add65_found,
    check_po_nct05485402_add66_found,
    check_po_nct05485402_add67_found,
    check_po_nct05485402_add68_found,
    check_po_nct05485402_add69_found,
    check_po_nct05485402_add70_found,
    check_po_nct05485402_add71_found,
    check_po_nct05485402_add72_found,
    check_po_nct05485402_add73_found,
    check_po_nct05485402_add74_found,
    check_po_nct05485402_add75_found,
    check_po_nct05485402_add76_found,
    check_po_nct05485402_add77_found,
    check_po_nct05485402_add78_found,
    check_po_nct05485402_add79_found,
    check_po_nct05485402_add80_found,
    check_po_nct05485402_add81_found,
    check_po_nct05485402_add82_found,
    check_po_nct05485402_add83_found,
    check_po_nct05485402_add84_found,
    check_po_nct05485402_add85_found,
    check_po_nct05485402_add86_found,
    check_po_nct05485402_add87_found,
    check_po_nct05485402_add88_found,
    check_po_nct05485402_add89_found,
    check_po_nct05485402_add90_found,
    check_po_nct05485402_add91_found,
    check_po_nct05485402_add92_found,
    check_po_nct05485402_add93_found,
    check_po_nct05485402_add94_found,
    check_po_nct05485402_add95_found,
    check_po_nct05485402_add96_found,
    check_po_nct05485402_add97_found,
    check_po_nct05485402_add98_found,
    check_po_nct05485402_add99_found,
]

def bucket(checks, notes):
    scores = []
    for fn in checks:
        score, check_notes = fn()
        scores.append(float(score))
        notes.extend(check_notes)
    return sum(scores) / len(scores) if scores else 0.0


def main():
    notes = []
    try:
        load()
        static = bucket(STATIC_CHECKS, notes)
        hacking = bucket(REWARD_HACKING_CHECKS, notes)
        oracle = bucket(PARTIAL_ORACLE_CHECKS, notes)
        infrastructure_failure = False
        error = ""
    except Exception:
        static = hacking = oracle = 0.0
        infrastructure_failure = True
        error = traceback.format_exc()
        print(error, file=sys.stderr)

    reward = (static * 1 + hacking * 2 + oracle * 3) / 6
    os.makedirs("/logs/verifier", exist_ok=True)
    payload = {
        "reward": round(reward, 4),
        "total_static_check_score": round(static, 4),
        "total_reward_hacking_check_score": round(hacking, 4),
        "total_partial_oracle_check_score": round(oracle, 4),
        "infrastructure_failure": infrastructure_failure,
    }
    if error:
        payload["error"] = error
    content = (hacking * 2 + oracle * 3) / 5
    payload["content_score"] = round(content, 4)
    payload["structural_score"] = round(static, 4)
    with open("/logs/verifier/reward.json", "w") as fh:
        json.dump(payload, fh)
    with open("/logs/verifier/reward.txt", "w") as fh:
        fh.write(str(round(reward, 4)))
    with open("/logs/verifier/details.json", "w") as fh:
        json.dump(
            {
                "counts": {
                    "static": len(STATIC_CHECKS),
                    "reward_hacking": len(REWARD_HACKING_CHECKS),
                    "partial_oracle": len(PARTIAL_ORACLE_CHECKS),
                },
                "trials_in_key": len(KEY),
                "ledger_rows": len(ROWS),
                "notes": notes[:400],
            },
            fh,
        )
    print("reward:", round(reward, 4))
    print("static:", round(static, 4), "reward_hacking:", round(hacking, 4), "partial_oracle:", round(oracle, 4))


if __name__ == "__main__":
    main()
