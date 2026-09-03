#!/usr/bin/env python3
import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict, OrderedDict


PERIOD_START = "2026-01-01"
PERIOD_END = "2026-06-30"
CBAM_FACTOR = 0.025
CERT_PRICE = 78.40
DE_MINIMIS_T = 50.0
PROC_IN = {"40 00", "42 00"}
PROC_OUT = {"51 00", "53 00", "61 00"}
INDIRECT_SECTORS = {"Cement", "Fertilisers"}
WAVE_MONTH = {"2026-09": 1, "2026-10": 2, "2026-11": 3, "2026-12": 4}
MONTH_WAVE = {"September": 1, "October": 2, "November": 3, "December": 4}
ACTION_FOR = {"A1": "obtain_report", "A2": "reverification",
              "A3": "accredited_reverification", "A4": "accredited_reverification",
              "A5": "boundary_completion", "A6": "misstatement_resolution"}

VOCAB = {
    "scope_basis": {"in_scope", "procedure_excluded", "code_not_covered"},
    "origin_basis": {"entry_declared", "proof_of_origin", "not_established"},
    "emissions_basis": {"actual", "default_country", "default_other_countries",
                        "default_annex_iv", "not_applicable"},
    "admissibility": {"admissible", "not_admissible"},
    "failing_condition": {"A1", "A2", "A3", "A4", "A5", "A6", "NONE"},
    "precursor_basis": {"actual", "default_country", "default_other_countries",
                        "default_annex_iv"},
    "threshold_status": {"above_threshold", "below_threshold"},
    "action_type": {"obtain_report", "reverification", "accredited_reverification",
                    "boundary_completion", "misstatement_resolution"},
    "status": {"scheduled", "not_scheduled"},
    "not_scheduled_reason": {"capacity_exhausted", "no_wave_after_availability", ""},
}

LEDGER_COLS = ["entry_ref", "line_no", "importer_code", "cn_code", "customs_procedure",
               "in_scope", "scope_basis", "declared_origin", "governing_origin", "origin_basis",
               "net_mass_t", "supplier_installation", "emissions_basis", "see_direct",
               "see_indirect", "see_applied", "embedded_emissions_t", "evidence_document",
               "evidence_quote"]
DOSSIER_COLS = ["installation_id", "country", "sector", "cn_code", "report_id",
                "reporting_period_start", "reporting_period_end", "activity_level_t",
                "attributed_direct_t", "attributed_indirect_t", "own_direct_intensity",
                "precursor_direct_component", "see_direct_derived", "see_indirect_derived",
                "verification_report", "admissibility", "failing_condition", "evidence_quote"]
CHAIN_COLS = ["installation_id", "cn_code", "precursor_installation", "precursor_cn_code",
              "precursor_country", "consumption_t_per_t", "precursor_basis",
              "precursor_see_direct", "precursor_contribution", "source_document"]
PRICE_COLS = ["claim_ref", "scheme_type", "jurisdiction", "period_start", "period_end",
              "installations_covered", "amount_local", "currency", "amount_eur", "admitted",
              "rejection_condition", "deduction_t", "importers_affected"]
POSITION_COLS = ["importer_code", "importer_name", "lines_in_scope", "cumulative_net_mass_t",
                 "threshold_status", "total_embedded_emissions_t", "adjusted_emissions_t",
                 "carbon_price_deduction_t", "certificates_due", "certificates_to_purchase"]
REMED_COLS = ["action_ref", "installation_id", "failing_condition", "action_type",
              "slots_required", "earliest_wave", "exposure_reduction_t", "rank",
              "assigned_wave", "status", "not_scheduled_reason"]

MEMO_FLOOR = 6000
EXHIBIT_FLOOR = 2000
QUOTE_WORD_CEILING = 60
QUOTE_REUSE_JACCARD = 0.95

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September",
     "October", "November", "December"])}



def flat(text):
    return re.sub(r"\s+", " ", text)


def tonum(s):
    if s is None:
        return None
    s = str(s).strip().replace(",", "").replace(" ", "").replace(" ", "")
    if s in ("", "-", "n.r.", "N/A", "notreported", "NONE"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def isodate(s):
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return s
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return "%s-%02d-%02d" % (m.group(3), int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(\d{1,2}) ([A-Z][a-z]+) (\d{4})$", s)
    if m and m.group(2) in MONTHS:
        return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2)], int(m.group(1)))
    return None


def first(text, patterns, group=1):
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(group)
    return None


def close(a, b, rel=0.005, abs_=0.0015):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= max(abs_, rel * abs(b))


def prop(hits, total):
    return (hits / total) if total else 0.0


def f1(pred, true):
    pred, true = set(pred), set(true)
    if not pred and not true:
        return 1.0
    if not pred or not true:
        return 0.0
    inter = len(pred & true)
    if not inter:
        return 0.0
    p = inter / len(pred)
    r = inter / len(true)
    return 2 * p * r / (p + r)


def dist_f1(pred_counts, true_counts):
    keys = set(pred_counts) | set(true_counts)
    inter = sum(min(pred_counts.get(k, 0), true_counts.get(k, 0)) for k in keys)
    np_, nt = sum(pred_counts.values()), sum(true_counts.values())
    if not np_ or not nt:
        return 0.0
    p, r = inter / np_, inter / nt
    return 2 * p * r / (p + r) if (p + r) else 0.0


def shingle_distinctness(text, n=12):
    words = ["#" if any(c.isdigit() for c in w) else w
             for w in re.findall(r"[A-Za-z0-9']+", text.lower())]
    if len(words) < n:
        return 0.0
    sh = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    return len(set(sh)) / len(sh)


DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")
LABEL_RE = re.compile(r"\b(?:[Ww][1-4]|A[1-6]|P[1-5])\b")


def strip_non_figures(sentence, corpus_token_re, code_tokens):
    out = corpus_token_re.sub(" ", sentence)
    out = DATE_RE.sub(" ", out)
    for code in code_tokens:
        out = out.replace(code, " ")
    return LABEL_RE.sub(" ", out)


def word_set(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def jaccard(a, b):
    A, B = word_set(a), word_set(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def sentences(text):
    keep = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("|") or line.startswith("#") or set(line) <= set("-= "):
            continue
        line = re.sub(r"^[>*+-]\s+", "", line)
        line = line.replace("**", "")
        if line[-1:] not in ".!?":
            line += "."
        keep.append(line)
    parts = re.split(r"(?<=[.!?])\s+", flat(" ".join(keep)))
    return [p.strip() for p in parts if len(p.split()) >= 6]



class Corpus(object):
    def __init__(self, root):
        self.root = root
        self.texts = {}
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if fn.lower().endswith((".md", ".csv", ".json")):
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        self.texts[rel] = fh.read()
        self.doc_by_id = {}
        for rel in self.texts:
            self.doc_by_id[os.path.splitext(os.path.basename(rel))[0]] = rel

    def read_csv(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def read_json(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as fh:
            return json.load(fh)

    def group(self, prefix):
        return {k: v for k, v in self.texts.items() if k.startswith(prefix)}



def parse_entries(corpus):
    lines = {}
    for rel, text in sorted(corpus.group("customs_entries/").items()):
        entry_ref = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        rel_date = first(ft, [r"Date of acceptance and release: (\d{1,2} [A-Z][a-z]+ \d{4})",
                              r"Accepted and released on (\d{2}/\d{2}/\d{4})"])
        rel_date = isodate(rel_date) if rel_date else None
        blocks = re.split(r"## Item (\d+)", text)
        if len(blocks) > 1:
            for i in range(1, len(blocks), 2):
                no = int(blocks[i])
                b = flat(blocks[i + 1])
                rec = {
                    "entry_ref": entry_ref, "line_no": no, "release_date": rel_date,
                    "cn_code": first(b, [r"Commodity code: ([0-9][0-9 ]*[0-9])"]),
                    "importer": first(b, [r"Consignee: .*?\((IMP-\d+)\)"]),
                    "procedure": first(b, [r"Requested procedure: (\d\d \d\d)"]),
                    "declared_origin": first(b, [r"Country of origin declared: (.+?) Country of dispatch"]),
                    "dispatch": first(b, [r"Country of dispatch: (.+?) Net mass"]),
                    "net_mass_t": None,
                    "installation": first(b, [r"quoted by the consignor: (INST-\d+)"]),
                    "poe": first(b, [r"Documents produced: (POE-\d{4}-\d+)"]),
                }
                nm = first(b, [r"Net mass: ([\d ,]+) kg"])
                rec["net_mass_t"] = round(tonum(nm) / 1000.0, 3) if nm else None
                lines[(entry_ref, no)] = rec
        else:
            for row in re.findall(r"^\|\s*(\d+)\s*\|([^\n]*)\|\s*$", text, re.M):
                no = int(row[0])
                cells = [c.strip() for c in row[1].split("|")]
                if len(cells) < 8:
                    continue
                nm = tonum(cells[5])
                lines[(entry_ref, no)] = {
                    "entry_ref": entry_ref, "line_no": no, "release_date": rel_date,
                    "cn_code": cells[0], "importer": cells[1], "procedure": cells[2],
                    "declared_origin": cells[3], "dispatch": cells[4],
                    "net_mass_t": round(nm / 1000.0, 3) if nm else None,
                    "installation": (cells[6] if cells[6].startswith("INST-") else None),
                    "poe": (cells[7] if cells[7].startswith("POE-") else None),
                }
    return lines


def parse_proofs(corpus):
    proofs = {}
    for rel, text in sorted(corpus.group("proofs_of_origin/").items()):
        ref = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        m = re.search(r"Presented against: declaration (E-\d{4}-\d+), item (\d+)", ft)
        if not m:
            continue
        country = first(ft, [r"certified to originate in ([^.]+)\."])
        proofs[ref] = {
            "ref": ref, "entry_ref": m.group(1), "line_no": int(m.group(2)),
            "country": country.strip() if country else None,
            "valid": "Defect noted by the desk on receipt" not in ft,
        }
    return proofs


PREC_RE = re.compile(
    r"CN (\d[\d ]*\d), produced at installation (INST-\d+); "
    r"(?:specific consumption ([\d.]+) tonnes per tonne of product"
    r"|total quantity consumed in the reporting period ([\d ,]+) tonnes"
    r"|consumption expressed as ([\d.]+) per cent of the mass of product)")

ACTIVITY_PATS = [
    r"Activity level for the period, tonnes of good produced: ([\d ,]+)",
    r"\| Production in period \(t\) \| ([\d ,]+) \|",
    r"The installation produced ([\d ,]+) tonnes of the good in the period",
    r"Activity level \(t\) \.+ ([\d ,]+)",
    r"the installation produced ([\d ,]+) tonnes of the good and attributed",
]
DIRECT_PATS = [
    r"Attributed direct emissions for the period, tonnes CO2e: ([\d ,]+)",
    r"\| Direct emissions attributed \(t CO2e\) \| ([\d ,]+) \|",
    r"Direct emissions attributed to that production were ([\d ,]+) tonnes",
    r"Direct attributed \(tCO2e\) \.+ ([\d ,]+)",
    r"attributed ([\d ,]+) tonnes of carbon dioxide equivalent to that production as direct",
]
INDIRECT_PATS = [
    r"Attributed indirect emissions for the period, tonnes CO2e: ([\d ,]+)",
    r"\| Indirect emissions attributed \(t CO2e\) \| ([\d ,]+) \|",
    r"Indirect emissions attributed to that production were ([\d ,]+) tonnes",
    r"Indirect attributed \(tCO2e\) ([\d ,]+)",
    r"Attributed indirect emissions were ([\d ,]+) tonnes",
]
PERIOD_PATS = [
    (r"Reporting period: (\d{1,2} [A-Z][a-z]+ \d{4}) to (\d{1,2} [A-Z][a-z]+ \d{4})"),
    (r"\| Period start \| (\d{2}/\d{2}/\d{4}) \| \| Period end \| (\d{2}/\d{2}/\d{4}) \|"),
    (r"\*\*Period covered\.\*\* (\d{1,2} [A-Z][a-z]+ \d{4}) to (\d{1,2} [A-Z][a-z]+ \d{4})\."),
    (r"Monitoring period \.+ (\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})"),
    (r"monitoring period runs from (\d{1,2} [A-Z][a-z]+ \d{4}) to (\d{1,2} [A-Z][a-z]+ \d{4})"),
]
BOUNDARY_PATS = [
    r"Production processes within the installation boundary: ([^.]+)\.",
    r"Processes inside the monitoring boundary of installation INST-\d+: ([^.]+)\.",
    r"The following processes sit inside the boundary: ([^.]+)\.",
    r"Boundary processes: ([^.]+)\.",
    r"The processes inside the boundary are ([^.]+)\.",
]


def parse_operator_reports(corpus, route_names):
    reports = {}
    for rel, text in sorted(corpus.group("operator_reports/").items()):
        rid = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        iid = first(ft, [r"(INST-\d+)"])
        activity = tonum(first(ft, ACTIVITY_PATS))
        direct = tonum(first(ft, DIRECT_PATS))
        indirect = tonum(first(ft, INDIRECT_PATS))
        ps = pe = None
        for pat in PERIOD_PATS:
            m = re.search(pat, ft)
            if m:
                ps, pe = isodate(m.group(1)), isodate(m.group(2))
                break
        route = None
        for name in sorted(route_names, key=len, reverse=True):
            if name in ft:
                route = name
                break
        boundary = first(ft, BOUNDARY_PATS)
        procs = []
        if boundary:
            procs = [x.strip().rstrip(".") for x in re.split(r"[;,]", boundary) if x.strip()]
        precs = []
        for m in PREC_RE.finditer(ft):
            cn, pid, per_t, total, pct = m.groups()
            if per_t is not None:
                ratio = float(per_t)
            elif total is not None:
                ratio = tonum(total) / activity if activity else None
            else:
                ratio = float(pct) / 100.0
            precs.append({"cn_code": cn, "installation": pid, "ratio": ratio})
        reports[iid] = {"report_id": rid, "installation": iid, "activity_level_t": activity,
                        "attributed_direct_t": direct, "attributed_indirect_t": indirect or 0.0,
                        "period_start": ps, "period_end": pe, "route": route,
                        "processes": procs, "precursors": precs, "path": rel}
    return reports


def parse_verifications(corpus):
    out = {}
    for rel, text in sorted(corpus.group("verification_reports/").items()):
        ref = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        iid = first(ft, [r"Installation verified: (INST-\d+)"])
        body = first(ft, [r"Verification body: .*?\((VB-[A-Z])\)"])
        opinion = first(ft, [r"Opinion: ([^.]+)\."])
        signed = first(ft, [r"Signed at [A-Za-z ]+ on (\d{1,2} [A-Z][a-z]+ \d{4})"])
        out[ref] = {
            "ref": ref, "installation": iid, "body": body,
            "opinion": (opinion or "").strip(),
            "signed": isodate(signed) if signed else None,
            "misstatement": "Material misstatements: one outstanding" in ft,
            "superseded": bool(re.search(r"this report was reissued", ft)),
            "path": rel,
        }
    return out


def parse_claims(corpus):
    out = {}
    for rel, text in sorted(corpus.group("carbon_price_claims/").items()):
        ref = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        insts = re.findall(r"INST-\d+", first(ft, [r"Installations the claim is made for: ([^\n]+?) Amount paid"]) or "")
        amount = tonum(first(ft, [r"Amount paid: ([\d ,]+) [A-Z]{3}"]))
        cur = first(ft, [r"Amount paid: [\d ,]+ ([A-Z]{3})"])
        out[ref] = {
            "claim_ref": ref,
            "scheme": first(ft, [r"Scheme: (.+?) Character of the charge"]),
            "scheme_type": first(ft, [r"Character of the charge: (.+?) Jurisdiction"]),
            "jurisdiction": first(ft, [r"Jurisdiction: (.+?) Period the payment"]),
            "period_start": first(ft, [r"Period the payment relates to: (\d{4}-\d{2}-\d{2})"]),
            "period_end": first(ft, [r"Period the payment relates to: \d{4}-\d{2}-\d{2} to (\d{4}-\d{2}-\d{2})"]),
            "installations": insts,
            "amount_local": amount, "currency": cur,
            "attestation": "Attestation: attached" in ft,
            "path": rel,
        }
    return out


def parse_correspondence(corpus):
    corr = {"activity": {}, "direct": {}, "ratio": {}, "rebate": set(),
            "availability": {}, "origin_doubt": set(), "docs": {}}
    for rel, text in sorted(corpus.group("supplier_correspondence/").items()):
        ref = os.path.splitext(os.path.basename(rel))[0]
        ft = flat(text)
        corr["docs"][ref] = rel
        oer = first(ft, [r"(OER-\d{4}-\d+)"])
        iid = first(ft, [r"(INST-\d+)"])
        if oer and iid:
            m = re.search(r"(?:figure for the reporting period [^.]*? is|production for [^.]*? was) "
                          r"([\d ,]+) tonnes", ft)
            if m:
                corr["activity"][iid] = tonum(m.group(1))
            m = re.search(r"(?:should read|correct figure for the period is) ([\d ,]+) tonnes of "
                          r"CO2 equivalent", ft)
            if m:
                corr["direct"][iid] = tonum(m.group(1))
            m = re.search(r"correct figure is ([\d.]+) per cent of the mass of product", ft)
            if m:
                corr["ratio"][iid] = float(m.group(1)) / 100.0
        cpc = first(ft, [r"(CPC-\d{4}-\d+)"])
        if cpc and re.search(r"rebated in full|was refunded to us|compensation offsets the amount "
                             r"claimed in full|refunded to us in", ft):
            corr["rebate"].add(cpc)
        if iid and not oer:
            months = re.findall(r"(September|October|November|December) 2026", ft)
            if months:
                corr["availability"][iid] = max(MONTH_WAVE[m] for m in months)
        m = re.search(r"item (\d+) of declaration (E-\d{4}-\d+)", ft)
        if m and re.search(r"cannot confirm the country|not able to establish the country|"
                           r"cannot state from our records which works", ft):
            corr["origin_doubt"].add((m.group(2), int(m.group(1))))
        for m2 in re.finditer(r"declaration (E-\d{4}-\d+),? item (\d+)", ft):
            if re.search(r"cannot confirm the country|not able to establish the country|"
                         r"cannot state from our records which works", ft):
                corr["origin_doubt"].add((m2.group(1), int(m2.group(2))))
    return corr



class Position(object):

    def __init__(self, corpus):
        self.c = corpus
        dv = corpus.read_csv("reference/commission_default_values.csv")
        self.dv = {}
        self.dv_countries = set()
        for r in dv:
            self.dv[(r["country"], r["cn_code"])] = r
            self.dv_countries.add(r["country"])
        self.dv_countries.discard("Other Countries and Territories")
        self.annex = {r["cn_code"]: r
                      for r in corpus.read_csv("reference/commission_annex_iv_values.csv")}
        self.covered = {r["cn_code"]: r for r in corpus.read_csv("reference/covered_goods.csv")}
        self.routes = corpus.read_csv("reference/production_routes.csv")
        self.route_req = {(r["cn_code"], r["production_route"]):
                          (r["required_processes"], r["required_precursor_cn"])
                          for r in self.routes}
        self.route_names = {r["production_route"] for r in self.routes}
        self.acc = {r["verification_body_id"]: r
                    for r in corpus.read_csv("reference/accreditation_register.csv")}
        self.reg = {r["installation_id"]: r
                    for r in corpus.read_csv("reference/installation_register.csv")}
        self.importers = corpus.read_csv("reference/importer_register.csv")
        self.fx = {r["currency"]: float(r["units_per_euro"])
                   for r in corpus.read_csv("reference/fx_reference_rates.csv")}
        self.capacity = OrderedDict()
        for r in corpus.read_csv("reference/remediation_capacity.csv"):
            self.capacity[r["wave"]] = int(r["engagement_slots"])
        self.effort = {r["failing_condition"]: int(r["slots_required"])
                       for r in corpus.read_csv("reference/remediation_effort.csv")}

        self.entries = parse_entries(corpus)
        self.proofs = parse_proofs(corpus)
        self.reports = parse_operator_reports(corpus, self.route_names)
        self.vers = parse_verifications(corpus)
        self.claims = parse_claims(corpus)
        self.corr = parse_correspondence(corpus)

        self._apply_corrigenda()
        self._verification_index()
        self._admissibility()
        self._see = {}
        self._see_all = {}
        self._lines()
        self._prices()
        self._positions()
        self._remediation()


    def _apply_corrigenda(self):
        for iid, rec in self.reports.items():
            if iid in self.corr["activity"]:
                rec["activity_level_t"] = self.corr["activity"][iid]
            if iid in self.corr["direct"]:
                rec["attributed_direct_t"] = self.corr["direct"][iid]
            if iid in self.corr["ratio"]:
                for p in rec["precursors"]:
                    p["ratio"] = self.corr["ratio"][iid]

    def _verification_index(self):
        by_inst = defaultdict(list)
        for ref, v in self.vers.items():
            if v["installation"]:
                by_inst[v["installation"]].append(v)
        self.governing_ver = {}
        for iid, vs in by_inst.items():
            live = [v for v in vs if not v["superseded"]]
            pool = live or vs
            pool.sort(key=lambda v: (v["signed"] or "", v["ref"]))
            self.governing_ver[iid] = pool[-1]

    def sector_of(self, cn):
        row = self.annex.get(cn)
        return row["sector"] if row else ""

    def _admissibility(self):
        self.admis = {}
        for iid, reg in self.reg.items():
            cn = reg["cn_code"]
            rep = self.reports.get(iid)
            fail = None
            if rep is None or not rep["period_start"] or not rep["period_end"] \
                    or rep["period_start"] > PERIOD_START or rep["period_end"] < PERIOD_END:
                fail = "A1"
            if fail is None:
                v = self.governing_ver.get(iid)
                if v is None or v["opinion"] != "verified with reasonable assurance":
                    fail = "A2"
            if fail is None:
                a = self.acc.get(v["body"])
                sig = v["signed"] or ""
                if a is None or not (a["valid_from"] <= sig <= a["valid_to"]) or \
                        (a["suspended_from"] and a["suspended_from"] <= sig <= a["suspended_to"]):
                    fail = "A3"
            if fail is None:
                if reg["sector"] not in [s.strip() for s in a["sectors_in_scope"].split(";")]:
                    fail = "A4"
            if fail is None:
                key = (cn, rep["route"] or "")
                req = self.route_req.get(key)
                if req is None:
                    fail = "A5"
                else:
                    need_proc = [p.strip() for p in req[0].split(";") if p.strip()]
                    have = " ; ".join(rep["processes"]).lower()
                    if any(p.lower() not in have for p in need_proc):
                        fail = "A5"
                    else:
                        need_prec = [p.strip() for p in req[1].split(";") if p.strip()]
                        have_prec = {p["cn_code"] for p in rep["precursors"]}
                        if any(p not in have_prec for p in need_prec):
                            fail = "A5"
            if fail is None:
                if self.governing_ver[iid]["misstatement"]:
                    fail = "A6"
            self.admis[iid] = fail

    def admissible(self, iid):
        return self.admis.get(iid, "A1") is None


    def resolve_default(self, country, cn):
        sector = self.sector_of(cn)
        if country is None:
            v = tonum(self.annex[cn]["highest_default_value_tco2e_per_t"].replace(",", "."))
            return v, (v if sector in INDIRECT_SECTORS else 0.0), "default_annex_iv"
        key = country if country in self.dv_countries else "Other Countries and Territories"
        basis = "default_country" if country in self.dv_countries else "default_other_countries"
        row = self.dv.get((key, cn))
        d = tonum(row["default_direct_tco2e_per_t"].replace(",", ".")) if row else None
        if row is None or d is None:
            v = tonum(self.annex[cn]["highest_default_value_tco2e_per_t"].replace(",", "."))
            return v, (v if sector in INDIRECT_SECTORS else 0.0), "default_annex_iv"
        ind = 0.0
        if sector in INDIRECT_SECTORS:
            iv = tonum(row["default_indirect_tco2e_per_t"].replace(",", "."))
            ind = iv if iv is not None else 0.0
        return d, ind, basis


    def see(self, iid, ignore_defects=False, _seen=None):
        cache = self._see_all if ignore_defects else self._see
        if iid in cache:
            return cache[iid]
        _seen = _seen or set()
        if iid in _seen:
            return (0.0, 0.0, 0.0, 0.0)
        _seen = _seen | {iid}
        rep = self.reports.get(iid)
        reg = self.reg.get(iid, {})
        sector = reg.get("sector", "")
        if rep is None or not rep["activity_level_t"]:
            out = (0.0, 0.0, 0.0, 0.0)
            cache[iid] = out
            return out
        own_d = (rep["attributed_direct_t"] or 0.0) / rep["activity_level_t"]
        own_i = (rep["attributed_indirect_t"] or 0.0) / rep["activity_level_t"]
        pd_ = pi_ = 0.0
        for p in rep["precursors"]:
            pid = p["installation"]
            ratio = p["ratio"] or 0.0
            if ignore_defects or self.admissible(pid):
                d, i, _a, _b = self.see(pid, ignore_defects, _seen)
            else:
                d, i, _basis = self.resolve_default(self.reg.get(pid, {}).get("country"),
                                                    p["cn_code"])
            pd_ += d * ratio
            pi_ += i * ratio
        d = own_d + pd_
        i = (own_i + pi_) if sector in INDIRECT_SECTORS else 0.0
        out = (round(d, 4), round(i, 4), round(own_d, 4), round(pd_, 4))
        cache[iid] = out
        return out

    def precursor_edges(self, iid):
        rep = self.reports.get(iid)
        if not rep:
            return []
        out = []
        for p in rep["precursors"]:
            pid = p["installation"]
            pcountry = self.reg.get(pid, {}).get("country")
            if self.admissible(pid):
                d, _i, _o, _pp = self.see(pid)
                basis = "actual"
            else:
                d, _i, basis = self.resolve_default(pcountry, p["cn_code"])
            out.append({
                "installation_id": iid, "cn_code": rep and self.reg[iid]["cn_code"],
                "precursor_installation": pid, "precursor_cn_code": p["cn_code"],
                "precursor_country": pcountry, "consumption_t_per_t": round(p["ratio"], 4),
                "precursor_basis": basis, "precursor_see_direct": round(d, 4),
                "precursor_contribution": round(d * p["ratio"], 4),
            })
        return out


    def _lines(self):
        poe_by_line = defaultdict(list)
        for p in self.proofs.values():
            poe_by_line[(p["entry_ref"], p["line_no"])].append(p)
        self.lines = {}
        for key, e in self.entries.items():
            cn = e["cn_code"]
            cov = self.covered.get(cn)
            if e["procedure"] in PROC_OUT:
                in_scope, basis = False, "procedure_excluded"
            elif cov is None or cov["covered"] != "yes":
                in_scope, basis = False, "code_not_covered"
            else:
                in_scope, basis = True, "in_scope"
            valid = [p for p in poe_by_line[key] if p["valid"]]
            if valid:
                gov, obasis = valid[0]["country"], "proof_of_origin"
            elif key in self.corr["origin_doubt"]:
                gov, obasis = None, "not_established"
            else:
                gov, obasis = e["declared_origin"], "entry_declared"
            rec = dict(e)
            rec["in_scope"] = in_scope
            rec["scope_basis"] = basis
            rec["governing_origin"] = gov
            rec["origin_basis"] = obasis
            if in_scope:
                iid = e["installation"]
                if gov is not None and iid and self.admissible(iid):
                    d, i, _o, _p = self.see(iid)
                    ebasis = "actual"
                else:
                    d, i, ebasis = self.resolve_default(gov, cn)
                rec["see_direct"] = round(d, 4)
                rec["see_indirect"] = round(i, 4)
                rec["see_applied"] = round(d + i, 4)
                rec["emissions_basis"] = ebasis
                rec["embedded_emissions_t"] = round((d + i) * e["net_mass_t"], 3)
            else:
                rec["see_direct"] = rec["see_indirect"] = rec["see_applied"] = None
                rec["emissions_basis"] = "not_applicable"
                rec["embedded_emissions_t"] = None
            self.lines[key] = rec
        self.in_scope = {k: v for k, v in self.lines.items() if v["in_scope"]}


    def _prices(self):
        mass = defaultdict(float)
        for r in self.in_scope.values():
            mass[r["importer"]] += r["net_mass_t"]
        self.mass_by_importer = {k: round(v, 3) for k, v in mass.items()}
        self.above = {k for k, v in self.mass_by_importer.items() if v > DE_MINIMIS_T}

        supplier_inst = {r["installation"] for r in self.in_scope.values()
                         if r["importer"] in self.above and r["installation"]}
        for ref, c in sorted(self.claims.items()):
            fail = None
            if not c["attestation"]:
                fail = "P1"
            elif ref in self.corr["rebate"]:
                fail = "P2"
            elif not (c["period_start"] <= PERIOD_END and c["period_end"] >= PERIOD_START):
                fail = "P3"
            elif not any(i in supplier_inst for i in c["installations"]):
                fail = "P4"
            elif c["scheme_type"] not in ("emissions trading system", "carbon tax"):
                fail = "P5"
            c["rejection_condition"] = fail or "NONE"
            c["admitted"] = fail is None
            rate = self.fx.get(c["currency"])
            c["amount_eur"] = round(c["amount_local"] / rate, 2) if rate else None
            c["deduction_t"] = (round(c["amount_eur"] / CERT_PRICE * CBAM_FACTOR, 3)
                                if c["admitted"] else 0.0)
            covered = [r for r in self.in_scope.values()
                       if r["installation"] in c["installations"] and r["importer"] in self.above]
            total = sum(r["embedded_emissions_t"] for r in covered)
            c["importers"] = sorted({r["importer"] for r in covered})
            c["allocation"] = {}
            if c["admitted"] and total > 0:
                for imp in c["importers"]:
                    share = sum(r["embedded_emissions_t"] for r in covered
                                if r["importer"] == imp) / total
                    c["allocation"][imp] = round(c["deduction_t"] * share, 4)

    def _positions(self):
        self.positions = OrderedDict()
        for reg in self.importers:
            code = reg["importer_code"]
            rows = [r for r in self.in_scope.values() if r["importer"] == code]
            m = round(sum(r["net_mass_t"] for r in rows), 3)
            above = m > DE_MINIMIS_T
            ee = round(sum(r["embedded_emissions_t"] for r in rows), 3)
            adj = round(ee * CBAM_FACTOR, 3) if above else 0.0
            ded = round(sum(c["allocation"].get(code, 0.0) for c in self.claims.values()
                            if c["admitted"]), 4) if above else 0.0
            due = round(max(0.0, adj - ded), 3)
            self.positions[code] = {
                "importer_code": code, "importer_name": reg["importer_name"],
                "lines_in_scope": len(rows), "cumulative_net_mass_t": m,
                "threshold_status": "above_threshold" if above else "below_threshold",
                "total_embedded_emissions_t": ee, "adjusted_emissions_t": adj,
                "carbon_price_deduction_t": ded, "certificates_due": due,
                "certificates_to_purchase": int(math.ceil(due - 1e-9)),
            }


    def _depends(self, line, iid):
        root = line["installation"]
        if not root or root not in self.reg or line["governing_origin"] is None:
            return False
        if root == iid:
            return True
        if not self.admissible(root):
            return False
        stack, seen = [root], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            rep = self.reports.get(x)
            if not rep:
                continue
            for p in rep["precursors"]:
                pid = p["installation"]
                if pid == iid:
                    return True
                if self.admissible(pid):
                    stack.append(pid)
        return False

    def _line_ee_with(self, line, iid):
        saved = self.admis[iid]
        self.admis[iid] = None
        self._see = {}
        gov = line["governing_origin"]
        root = line["installation"]
        if gov is not None and root and self.admissible(root):
            d, i, _o, _p = self.see(root)
        else:
            d, i, _b = self.resolve_default(gov, line["cn_code"])
        val = round((d + i) * line["net_mass_t"], 3)
        self.admis[iid] = saved
        self._see = {}
        return val

    def _remediation(self):
        actions = []
        for iid in sorted(self.reg):
            fail = self.admis.get(iid)
            if fail is None:
                continue
            affected = [r for r in self.in_scope.values()
                        if r["importer"] in self.above and self._depends(r, iid)]
            now = sum(r["embedded_emissions_t"] for r in affected)
            cf = sum(self._line_ee_with(r, iid) for r in affected)
            actions.append({
                "action_ref": "REM-" + iid.split("-")[1], "installation_id": iid,
                "failing_condition": fail, "action_type": ACTION_FOR[fail],
                "slots_required": self.effort[fail],
                "earliest_wave": self.corr["availability"].get(iid, 1),
                "exposure_reduction_t": round(now - cf, 3),
            })
        actions.sort(key=lambda a: (-(a["exposure_reduction_t"] / a["slots_required"]),
                                    a["installation_id"]))
        remaining = OrderedDict(self.capacity)
        wave_ids = list(self.capacity)
        for n, a in enumerate(actions, start=1):
            a["rank"] = n
            placed = ""
            for idx, wid in enumerate(wave_ids, start=1):
                if idx < a["earliest_wave"]:
                    continue
                if remaining[wid] >= a["slots_required"]:
                    remaining[wid] -= a["slots_required"]
                    placed = wid
                    break
            a["assigned_wave"] = placed
            a["status"] = "scheduled" if placed else "not_scheduled"
            a["not_scheduled_reason"] = "" if placed else (
                "no_wave_after_availability" if a["earliest_wave"] > len(wave_ids)
                else "capacity_exhausted")
        self.remediation = {a["action_ref"]: a for a in actions}
        self._see = {}



def read_submission_csv(path, cols):
    if not os.path.isfile(path):
        return None, []
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        rdr = csv.reader(fh)
        rows = [r for r in rdr if any(c.strip() for c in r)]
    if not rows:
        return [], []
    header = [h.strip() for h in rows[0]]
    out = []
    for r in rows[1:]:
        r = list(r) + [""] * (len(header) - len(r))
        out.append({header[i]: (r[i] or "").strip() for i in range(len(header))})
    return header, out


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()



class Grader(object):
    def __init__(self, pos, corpus, agent_dir):
        self.p = pos
        self.c = corpus
        self.a = agent_dir
        self.checks = []
        self.led_h, self.led = read_submission_csv(os.path.join(agent_dir, "consignment_ledger.csv"),
                                                   LEDGER_COLS)
        self.dos_h, self.dos = read_submission_csv(os.path.join(agent_dir, "installation_dossier.csv"),
                                                   DOSSIER_COLS)
        self.chn_h, self.chn = read_submission_csv(os.path.join(agent_dir, "precursor_chain.csv"),
                                                   CHAIN_COLS)
        self.prc_h, self.prc = read_submission_csv(os.path.join(agent_dir, "carbon_price_schedule.csv"),
                                                   PRICE_COLS)
        self.pos_h, self.pos_rows = read_submission_csv(
            os.path.join(agent_dir, "importer_position.csv"), POSITION_COLS)
        self.rem_h, self.rem = read_submission_csv(os.path.join(agent_dir, "remediation_programme.csv"),
                                                   REMED_COLS)
        self.memo = read_text(os.path.join(agent_dir, "position_memo.md"))
        self.exhibit = read_text(os.path.join(agent_dir, "exposure_exhibit.md"))

        self.led_map = self._key_map(self.led, lambda r: (r.get("entry_ref", ""),
                                                          self._int(r.get("line_no"))))
        self.dos_map = self._key_map(self.dos, lambda r: r.get("installation_id", ""))
        self.chn_map = self._key_map(self.chn, lambda r: (r.get("installation_id", ""),
                                                          r.get("precursor_installation", "")))
        self.prc_map = self._key_map(self.prc, lambda r: r.get("claim_ref", ""))
        self.pos_map = self._key_map(self.pos_rows, lambda r: r.get("importer_code", ""))
        self.rem_map = self._key_map(self.rem, lambda r: r.get("action_ref", ""))

    @staticmethod
    def _int(v):
        try:
            return int(str(v).strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _key_map(rows, keyfn):
        out = OrderedDict()
        for r in rows:
            k = keyfn(r)
            if k not in out:
                out[k] = r
        return out


    def precision(self, sub_map, true_keys):
        if not sub_map:
            return 0.0
        return sum(1 for k in sub_map if k in true_keys) / len(sub_map)

    def rowscore(self, sub_map, true_map, ok, precision_keys=None):
        if not true_map:
            return 0.0
        prec = self.precision(sub_map, precision_keys if precision_keys is not None
                              else set(true_map))
        hits = 0
        for k, v in sub_map.items():
            t = true_map.get(k)
            if t is None:
                continue
            try:
                if ok(v, t):
                    hits += 1
            except Exception:
                pass
        return (hits / len(true_map)) * prec

    def add(self, cid, category, fn):
        err = None
        try:
            score = float(fn())
            if not (score == score) or score in (float("inf"), float("-inf")):
                score, err = 0.0, "non-finite score"
            score = min(1.0, max(0.0, score))
        except Exception as exc:
            score, err = 0.0, "%s: %s" % (type(exc).__name__, exc)
        self.checks.append({"id": cid, "category": category, "score": score,
                            "weight": {"static_checks": 1, "reward_hacking_checks": 2,
                                       "partial_oracle_checks": 3}[category],
                            "error": err})


    def _shape(self, header, cols, sub_map, true_keys, load_bearing, rows):
        if header is None:
            return 0.0
        col_term = len(set(cols) & set(header or [])) / len(cols)
        ref_term = self.precision(sub_map, true_keys)
        if not rows:
            return 0.0
        filled = 0
        for r in rows:
            vals = [r.get(c, "") for c in load_bearing]
            filled += sum(1 for v in vals if str(v).strip() != "")
        fill_term = filled / (len(rows) * len(load_bearing))
        return col_term * ref_term * fill_term

    def prose_score(self, text, floor):
        if not text.strip():
            return 0.0
        length = min(1.0, len(text) / floor)
        distinct = shingle_distinctness(text)
        sents = sentences(text)
        if not sents:
            return 0.0
        named = sum(1 for s in sents if self.names_corpus(s)) / len(sents)
        return length * distinct * named

    CORPUS_TOKEN = re.compile(r"\b(INST-\d+|IMP-\d+|E-\d{4}-\d+|OER-\d{4}-\d+|VER-\d{4}-\d+"
                              r"|CPC-\d{4}-\d+|POE-\d{4}-\d+|SL-\d{4}-\d+|REM-\d+)\b")

    def names_corpus(self, sentence):
        if self.CORPUS_TOKEN.search(sentence):
            return True
        for country in self.p.dv_countries:
            if country in sentence:
                return True
        return False


    def quote_ok(self, quote, doc_id, discriminators):
        if not quote or not doc_id:
            return False
        rel = self.c.doc_by_id.get(doc_id)
        if not rel:
            return False
        words = quote.split()
        if not (4 <= len(words) <= QUOTE_WORD_CEILING):
            return False
        hay = flat(self.c.texts[rel]).lower()
        needle = flat(quote).lower().strip().strip('"')
        if needle not in hay:
            return False
        for alt in discriminators:
            toks = [str(t).lower() for t in alt if t]
            if toks and all(t in needle for t in toks):
                return True
        return False

    @staticmethod
    def row_discriminators(r):
        out = []
        entry = (r.get("entry_ref") or "").strip()
        line_no = (r.get("line_no") or "").strip()
        if entry and line_no:
            out.append([entry, "item %s" % line_no])
        mass = tonum(r.get("net_mass_t"))
        if mass is not None and mass > 0:
            kg = int(round(mass * 1000))
            out.append(["{:,}".format(kg)])
            out.append([str(kg)])
        iid = (r.get("installation_id") or "").strip()
        if iid:
            out.append([iid])
        return out



def build_checks(g):
    p = g.p
    true_lines = p.lines
    true_scope = p.in_scope
    true_dos = {iid: iid for iid in p.reg}
    true_chain = {}
    for iid in p.reg:
        for e in p.precursor_edges(iid):
            true_chain[(iid, e["precursor_installation"])] = e
    true_claims = p.claims
    true_pos = p.positions
    true_rem = p.remediation
    LEDGER_LB = ["cn_code", "in_scope", "scope_basis", "net_mass_t", "origin_basis"]
    DOSSIER_LB = ["country", "cn_code", "admissibility", "failing_condition", "activity_level_t"]
    CHAIN_LB = ["precursor_cn_code", "consumption_t_per_t", "precursor_basis",
                "precursor_see_direct"]
    PRICE_LB = ["scheme_type", "amount_eur", "admitted", "rejection_condition"]
    POS_LB = ["cumulative_net_mass_t", "threshold_status", "total_embedded_emissions_t",
              "certificates_due"]
    REM_LB = ["failing_condition", "action_type", "exposure_reduction_t", "status"]

    code_tokens = sorted(p.covered, key=len, reverse=True)

    S = "static_checks"
    R = "reward_hacking_checks"
    O = "partial_oracle_checks"

    def check_static_checks_1():
        return (
            g._shape(g.led_h, LEDGER_COLS, g.led_map,
                                                     set(true_lines), LEDGER_LB, g.led)
        )
    g.add("static_checks_1", S, check_static_checks_1)
    def check_static_checks_2():
        return (
            g._shape(g.dos_h, DOSSIER_COLS, g.dos_map,
                                                     set(true_dos), DOSSIER_LB, g.dos)
        )
    g.add("static_checks_2", S, check_static_checks_2)
    def check_static_checks_3():
        return (
            g._shape(g.chn_h, CHAIN_COLS, g.chn_map,
                                                     set(true_chain), CHAIN_LB, g.chn)
        )
    g.add("static_checks_3", S, check_static_checks_3)
    def check_static_checks_4():
        return (
            g._shape(g.prc_h, PRICE_COLS, g.prc_map,
                                                     set(true_claims), PRICE_LB, g.prc)
        )
    g.add("static_checks_4", S, check_static_checks_4)
    def check_static_checks_5():
        return (
            g._shape(g.pos_h, POSITION_COLS, g.pos_map,
                                                     set(true_pos), POS_LB, g.pos_rows)
        )
    g.add("static_checks_5", S, check_static_checks_5)
    def check_static_checks_6():
        return (
            g._shape(g.rem_h, REMED_COLS, g.rem_map,
                                                     set(true_rem), REM_LB, g.rem)
        )
    g.add("static_checks_6", S, check_static_checks_6)
    def check_static_checks_7():
        return (
            g.prose_score(g.memo, MEMO_FLOOR)
        )
    g.add("static_checks_7", S, check_static_checks_7)
    def check_static_checks_8():
        return (
            g.prose_score(g.exhibit, EXHIBIT_FLOOR)
        )
    g.add("static_checks_8", S, check_static_checks_8)

    def check_static_checks_9():
        rows = [r for r in g.led if r.get("in_scope", "").lower() == "yes"]
        if not rows:
            return 0.0
        ok = 0
        for r in rows:
            see, m, ee = tonum(r.get("see_applied")), tonum(r.get("net_mass_t")), \
                tonum(r.get("embedded_emissions_t"))
            if see is not None and m is not None and ee is not None and close(ee, see * m, 0.01, 0.05):
                ok += 1
        return ok / len(rows)
    g.add("static_checks_9", S, check_static_checks_9)

    def check_static_checks_10():
        if not g.dos:
            return 0.0
        ok = 0
        for r in g.dos:
            own, prec, tot = tonum(r.get("own_direct_intensity")), \
                tonum(r.get("precursor_direct_component")), tonum(r.get("see_direct_derived"))
            if own is not None and prec is not None and tot is not None \
                    and close(tot, own + prec, 0.01, 0.002):
                ok += 1
        return ok / len(g.dos)
    g.add("static_checks_10", S, check_static_checks_10)

    def check_static_checks_11():
        if not g.pos_rows:
            return 0.0
        by_imp = defaultdict(float)
        n_by_imp = defaultdict(int)
        for r in g.led:
            if r.get("in_scope", "").lower() == "yes":
                m = tonum(r.get("net_mass_t"))
                if m is not None:
                    by_imp[r.get("importer_code", "")] += m
                    n_by_imp[r.get("importer_code", "")] += 1
        ok = 0
        for r in g.pos_rows:
            code = r.get("importer_code", "")
            m = tonum(r.get("cumulative_net_mass_t"))
            n = g._int(r.get("lines_in_scope"))
            if m is not None and close(m, by_imp.get(code, 0.0), 0.01, 0.05) \
                    and n == n_by_imp.get(code, 0):
                ok += 1
        return ok / len(g.pos_rows)
    g.add("static_checks_11", S, check_static_checks_11)

    def check_static_checks_12():
        if not g.rem:
            return 0.0
        cap = p.capacity
        used = defaultdict(int)
        placed = 0
        for r in g.rem:
            if r.get("status") == "scheduled":
                wid = r.get("assigned_wave", "")
                s = g._int(r.get("slots_required")) or 0
                used[wid] += s
                placed += 1
        if not placed:
            return 0.0
        good = sum(1 for wid, u in used.items() if wid in cap and u <= cap[wid])
        waves_touched = len(used) or 1
        consistent = sum(1 for r in g.rem
                         if (r.get("status") == "scheduled") == bool(r.get("assigned_wave", "")))
        return (good / waves_touched) * (consistent / len(g.rem))
    g.add("static_checks_12", S, check_static_checks_12)

    def check_static_checks_13():
        pairs = [(g.led, {"scope_basis": "scope_basis", "origin_basis": "origin_basis",
                          "emissions_basis": "emissions_basis"}),
                 (g.dos, {"admissibility": "admissibility",
                          "failing_condition": "failing_condition"}),
                 (g.chn, {"precursor_basis": "precursor_basis"}),
                 (g.pos_rows, {"threshold_status": "threshold_status"}),
                 (g.rem, {"action_type": "action_type", "status": "status",
                          "not_scheduled_reason": "not_scheduled_reason",
                          "failing_condition": "failing_condition"})]
        tot = ok = 0
        for rows, cols in pairs:
            for r in rows:
                for col, voc in cols.items():
                    tot += 1
                    if r.get(col, "").strip() in VOCAB[voc]:
                        ok += 1
        return prop(ok, tot)
    g.add("static_checks_13", S, check_static_checks_13)


    def check_reward_hacking_checks_1():
        return (
            g.precision(g.led_map, set(true_lines)) *
              (len(g.led_map) / len(g.led) if g.led else 0.0)
        )
    g.add("reward_hacking_checks_1", R, check_reward_hacking_checks_1)
    def check_reward_hacking_checks_2():
        return (
            g.precision(g.dos_map, set(true_dos)) *
              (len(g.dos_map) / len(g.dos) if g.dos else 0.0)
        )
    g.add("reward_hacking_checks_2", R, check_reward_hacking_checks_2)
    def check_reward_hacking_checks_3():
        return (
            g.precision(g.chn_map, set(true_chain)) *
              (len(g.chn_map) / len(g.chn) if g.chn else 0.0)
        )
    g.add("reward_hacking_checks_3", R, check_reward_hacking_checks_3)
    def check_reward_hacking_checks_4():
        return (
            g.precision(g.prc_map, set(true_claims)) *
              (len(g.prc_map) / len(g.prc) if g.prc else 0.0)
        )
    g.add("reward_hacking_checks_4", R, check_reward_hacking_checks_4)

    def check_reward_hacking_checks_5():
        rows = [r for r in g.led if r.get("evidence_quote", "").strip()]
        rows += [r for r in g.dos if r.get("evidence_quote", "").strip()]
        if not rows:
            return 0.0
        ok = 0
        accepted = []
        for r in rows:
            q = r.get("evidence_quote", "").strip()
            doc = r.get("evidence_document", "").strip() or r.get("report_id", "").strip()
            if not g.quote_ok(q, doc, g.row_discriminators(r)):
                continue
            if any(jaccard(q, prev) >= QUOTE_REUSE_JACCARD for prev in accepted):
                continue
            accepted.append(q)
            ok += 1
        target = len(true_scope) + len(true_dos)
        return (ok / target) if target else 0.0
    g.add("reward_hacking_checks_5", R, check_reward_hacking_checks_5)

    def check_reward_hacking_checks_6():
        qs = [r.get("evidence_quote", "").strip() for r in g.led + g.dos
              if r.get("evidence_quote", "").strip()]
        if not qs:
            return 0.0
        reps = []
        for q in qs:
            if not any(jaccard(q, prev) >= QUOTE_REUSE_JACCARD for prev in reps):
                reps.append(q)
        grounded = 0
        for r in g.led + g.dos:
            q = r.get("evidence_quote", "").strip()
            if not q:
                continue
            doc = r.get("evidence_document", "").strip() or r.get("report_id", "").strip()
            if g.quote_ok(q, doc, g.row_discriminators(r)):
                grounded += 1
        return (len(reps) / len(qs)) * (grounded / len(qs))
    g.add("reward_hacking_checks_6", R, check_reward_hacking_checks_6)

    export = p.c.read_json("entry_summary_export.json")
    export_by_key = {(r["entry_ref"], r["line_no"]): r for r in export["lines"]}

    def check_reward_hacking_checks_7():
        agree, disagree = [], []
        for k, t in true_lines.items():
            e = export_by_key.get(k)
            if not e or e.get("net_mass_t") is None:
                continue
            (agree if close(float(e["net_mass_t"]), t["net_mass_t"], 0.0005, 0.0005)
             else disagree).append(k)
        def acc(keys):
            if not keys:
                return 1.0
            hit = sum(1 for k in keys if k in g.led_map
                      and close(tonum(g.led_map[k].get("net_mass_t")), true_lines[k]["net_mass_t"],
                                0.002, 0.01))
            return hit / len(keys)
        return acc(agree) * acc(disagree)
    g.add("reward_hacking_checks_7", R, check_reward_hacking_checks_7)

    def check_reward_hacking_checks_8():
        agree, disagree = [], []
        for k, t in true_lines.items():
            e = export_by_key.get(k)
            if not e:
                continue
            (agree if (e.get("origin_column") or "") == (t["governing_origin"] or "")
             else disagree).append(k)
        def acc(keys):
            if not keys:
                return 1.0
            hit = 0
            for k in keys:
                r = g.led_map.get(k)
                if not r:
                    continue
                want = true_lines[k]["governing_origin"]
                got = r.get("governing_origin", "").strip()
                if (want is None and got in ("", "NONE", "not established")) or \
                        (want is not None and got == want):
                    hit += 1
            return hit / len(keys)
        return acc(agree) * acc(disagree)
    g.add("reward_hacking_checks_8", R, check_reward_hacking_checks_8)

    def check_reward_hacking_checks_9():
        agree, disagree = [], []
        for iid in p.reg:
            rep = p.reports.get(iid)
            if not rep or not rep["activity_level_t"]:
                continue
            stated = round((rep["attributed_direct_t"] or 0.0) / rep["activity_level_t"], 3)
            d, _i, _o, _pp = p.see(iid)
            (agree if close(stated, d, 0.01, 0.002) else disagree).append(iid)
        def acc(ids):
            if not ids:
                return 1.0
            hit = 0
            for iid in ids:
                r = g.dos_map.get(iid)
                if r and close(tonum(r.get("see_direct_derived")), p.see(iid)[0], 0.01, 0.002):
                    hit += 1
            return hit / len(ids)
        return acc(agree) * acc(disagree)
    g.add("reward_hacking_checks_9", R, check_reward_hacking_checks_9)

    def check_reward_hacking_checks_10():
        keys = [k for k, t in true_scope.items()
                if t["emissions_basis"].startswith("default")
                and p.sector_of(t["cn_code"]) not in INDIRECT_SECTORS]
        if not keys:
            return 1.0
        hit = 0
        for k in keys:
            r = g.led_map.get(k)
            if not r:
                continue
            si = tonum(r.get("see_indirect"))
            if si is not None and abs(si) < 1e-6 and \
                    close(tonum(r.get("see_applied")), true_scope[k]["see_applied"], 0.005, 0.002):
                hit += 1
        return hit / len(keys)
    g.add("reward_hacking_checks_10", R, check_reward_hacking_checks_10)

    def check_reward_hacking_checks_11():
        ghosts = [k for k in export_by_key if k not in true_lines]
        if not ghosts:
            return 1.0
        return sum(1 for k in ghosts if k not in g.led_map) / len(ghosts)
    g.add("reward_hacking_checks_11", R, check_reward_hacking_checks_11)

    def check_reward_hacking_checks_12():
        missing = [k for k in true_lines if k not in export_by_key]
        if not missing:
            return 1.0
        hit = 0
        for k in missing:
            r = g.led_map.get(k)
            if r and close(tonum(r.get("net_mass_t")), true_lines[k]["net_mass_t"], 0.002, 0.01):
                hit += 1
        return hit / len(missing)
    g.add("reward_hacking_checks_12", R, check_reward_hacking_checks_12)

    def check_reward_hacking_checks_13():
        outs = [k for k, t in true_lines.items() if not t["in_scope"]]
        ins = list(true_scope)
        if not outs or not ins:
            return 0.0
        blank = 0
        for k in outs:
            r = g.led_map.get(k)
            if not r:
                continue
            if all(str(r.get(c, "")).strip() in ("", "NONE", "n/a") for c in
                   ("see_direct", "see_indirect", "see_applied", "embedded_emissions_t")):
                blank += 1
        filled = 0
        for k in ins:
            r = g.led_map.get(k)
            if r and tonum(r.get("embedded_emissions_t")) is not None:
                filled += 1
        return (blank / len(outs)) * (filled / len(ins))
    g.add("reward_hacking_checks_13", R, check_reward_hacking_checks_13)

    def prose_not_fabricated(text):
        sents = [s for s in sentences(text) if g.CORPUS_TOKEN.search(s)]
        if not sents:
            return 0.0
        true_figs = set()
        for n in (len(true_lines), len(true_scope), len(p.reg), len(true_claims),
                  len(p.remediation), len(p.above), len(p.positions), len(true_chain),
                  len(p.capacity), len({k[0] for k in true_lines}),
                  len(p.positions) - len(p.above),
                  sum(1 for i in p.reg if p.admis[i] is None),
                  sum(1 for i in p.reg if p.admis[i] is not None),
                  sum(1 for c in true_claims.values() if c["admitted"]),
                  sum(1 for c in true_claims.values() if not c["admitted"]),
                  sum(1 for a in p.remediation.values() if a["status"] == "scheduled"),
                  sum(1 for a in p.remediation.values() if a["status"] == "not_scheduled")):
            true_figs.add(float(n))
        for cond in ("A1", "A2", "A3", "A4", "A5", "A6"):
            true_figs.add(float(sum(1 for i in p.reg if p.admis[i] == cond)))
        for field in ("emissions_basis", "origin_basis", "scope_basis"):
            for label in {t[field] for t in true_lines.values()}:
                true_figs.add(float(sum(1 for t in true_lines.values() if t[field] == label)))
        for cond in ("P1", "P2", "P3", "P4", "P5"):
            true_figs.add(float(sum(1 for c in true_claims.values()
                                    if c["rejection_condition"] == cond)))
        for a in p.remediation.values():
            true_figs.update({float(a["rank"]), float(a["slots_required"]),
                              float(a["earliest_wave"])})
        for cap in p.capacity.values():
            true_figs.add(float(cap))
        true_figs.update({1.0, 2.0, 3.0, 4.0, DE_MINIMIS_T, CERT_PRICE, CBAM_FACTOR * 100,
                          float(MEMO_FLOOR), float(EXHIBIT_FLOOR)})
        for t in true_scope.values():
            for v in (t["net_mass_t"], t["embedded_emissions_t"], t["see_applied"]):
                if v is not None:
                    true_figs.add(round(v, 2))
        for v in p.positions.values():
            for kk in ("cumulative_net_mass_t", "total_embedded_emissions_t",
                       "adjusted_emissions_t", "certificates_due"):
                true_figs.add(round(v[kk], 2))
            true_figs.add(float(v["certificates_to_purchase"]))
            true_figs.add(float(v["lines_in_scope"]))
        for a in p.remediation.values():
            true_figs.add(round(a["exposure_reduction_t"], 2))
            true_figs.add(float(a["slots_required"]))
        for iid in p.reg:
            d, i, o, pp = p.see(iid)
            for v in (d, i, o, pp):
                true_figs.add(round(v, 2))
            rep = p.reports.get(iid)
            if rep and rep["activity_level_t"]:
                true_figs.add(round(rep["activity_level_t"], 2))
                true_figs.add(round(rep["attributed_direct_t"] or 0.0, 2))
        counts = {len(true_lines), len(true_scope), len(p.reg), len(true_claims),
                  len(p.remediation), len(p.above), len(p.positions)}
        true_figs |= {float(x) for x in counts}
        ok = 0
        for s in sents:
            bare = strip_non_figures(s, g.CORPUS_TOKEN, code_tokens)
            nums = [tonum(x) for x in re.findall(r"-?\d[\d ,]*\.?\d*", bare)]
            nums = [n for n in nums if n is not None]
            material = [n for n in nums if abs(n) >= 1 and not (1990 <= n <= 2100)]
            if not material:
                ok += 1
                continue
            if all(any(close(n, f, 0.01, 0.05) for f in true_figs) for n in material):
                ok += 1
        return ok / len(sents)
    def check_reward_hacking_checks_14():
        return (
            prose_not_fabricated(g.memo)
        )
    g.add("reward_hacking_checks_14", R, check_reward_hacking_checks_14)
    def check_reward_hacking_checks_15():
        return (
            prose_not_fabricated(g.exhibit)
        )
    g.add("reward_hacking_checks_15", R, check_reward_hacking_checks_15)

    def check_reward_hacking_checks_16():
        pred = defaultdict(int)
        for r in g.dos:
            pred[r.get("failing_condition", "").strip()] += 1
        true = defaultdict(int)
        for iid in p.reg:
            true[p.admis[iid] or "NONE"] += 1
        return dist_f1(pred, true)
    g.add("reward_hacking_checks_16", R, check_reward_hacking_checks_16)

    def check_reward_hacking_checks_17():
        pred = defaultdict(int)
        for r in g.led:
            pred[r.get("emissions_basis", "").strip()] += 1
        true = defaultdict(int)
        for t in true_lines.values():
            true[t["emissions_basis"]] += 1
        return dist_f1(pred, true)
    g.add("reward_hacking_checks_17", R, check_reward_hacking_checks_17)


    def led_field(cmp_fn):
        return lambda: g.rowscore(g.led_map, true_lines, cmp_fn)

    def check_partial_oracle_checks_1():
        return (
            led_field(
            lambda v, t: (v.get("in_scope", "").strip().lower() == ("yes" if t["in_scope"] else "no"))
            and v.get("scope_basis", "").strip() == t["scope_basis"])
        )()
    g.add("partial_oracle_checks_1", O, check_partial_oracle_checks_1)

    default_lines = {k: t for k, t in true_scope.items() if t["emissions_basis"] != "actual"}

    def check_partial_oracle_checks_2():
        return g.rowscore(
            g.led_map, default_lines,
            lambda v, t: v.get("emissions_basis", "").strip() == t["emissions_basis"]
            and close(tonum(v.get("see_applied")), t["see_applied"], 0.005, 0.002),
            set(true_lines))
    g.add("partial_oracle_checks_2", O, check_partial_oracle_checks_2)
    def check_partial_oracle_checks_3():
        return (
            led_field(
            lambda v, t: close(tonum(v.get("net_mass_t")), t["net_mass_t"], 0.002, 0.01))
        )()
    g.add("partial_oracle_checks_3", O, check_partial_oracle_checks_3)
    def origin_ok(v, t):
        got = v.get("governing_origin", "").strip()
        want = t["governing_origin"]
        settled = (got == want) if want is not None else got in ("", "NONE", "not established")
        return settled and v.get("origin_basis", "").strip() == t["origin_basis"]
    def check_partial_oracle_checks_4():
        return (
            led_field(origin_ok)
        )()
    g.add("partial_oracle_checks_4", O, check_partial_oracle_checks_4)

    chain_lines = {}
    for k, t in true_scope.items():
        iid = t["installation"]
        if iid and p.admissible(iid) and p.see(iid)[3] > 0:
            chain_lines[k] = t

    def check_partial_oracle_checks_5():
        return g.rowscore(
            g.led_map, chain_lines,
            lambda v, t: close(tonum(v.get("see_applied")), t["see_applied"], 0.005, 0.002),
            set(true_lines))
    g.add("partial_oracle_checks_5", O, check_partial_oracle_checks_5)
    def check_partial_oracle_checks_6():
        return (
            led_field(
            lambda v, t: v.get("emissions_basis", "").strip() == t["emissions_basis"])
        )()
    g.add("partial_oracle_checks_6", O, check_partial_oracle_checks_6)
    def check_partial_oracle_checks_7():
        return (
            g.rowscore(
            g.led_map, true_scope,
            lambda v, t: close(tonum(v.get("see_direct")), t["see_direct"], 0.005, 0.002),
            set(true_lines))
        )
    g.add("partial_oracle_checks_7", O, check_partial_oracle_checks_7)
    def check_partial_oracle_checks_8():
        return (
            g.rowscore(
            g.led_map, true_scope,
            lambda v, t: close(tonum(v.get("see_indirect")), t["see_indirect"], 0.005, 0.002),
            set(true_lines))
        )
    g.add("partial_oracle_checks_8", O, check_partial_oracle_checks_8)
    def check_partial_oracle_checks_9():
        return (
            g.rowscore(
            g.led_map, true_scope,
            lambda v, t: close(tonum(v.get("see_applied")), t["see_applied"], 0.005, 0.002),
            set(true_lines))
        )
    g.add("partial_oracle_checks_9", O, check_partial_oracle_checks_9)
    def check_partial_oracle_checks_10():
        return (
            g.rowscore(
            g.led_map, true_scope,
            lambda v, t: close(tonum(v.get("embedded_emissions_t")), t["embedded_emissions_t"],
                               0.005, 0.05), set(true_lines))
        )
    g.add("partial_oracle_checks_10", O, check_partial_oracle_checks_10)
    def check_partial_oracle_checks_11():
        return (
            prop(sum(1 for k in true_lines if k in g.led_map), len(true_lines))
        )
    g.add("partial_oracle_checks_11", O, check_partial_oracle_checks_11)

    def check_partial_oracle_checks_12():
        return g.rowscore(g.led_map, true_scope, lambda v, t: (
            v.get("evidence_document", "").strip() in g.c.doc_by_id
            and (t["entry_ref"] in g.c.doc_by_id.get(v.get("evidence_document", "").strip(), "")
                 or (t["installation"] or "@") in
                 flat(g.c.texts[g.c.doc_by_id[v.get("evidence_document", "").strip()]]))),
            set(true_lines))
    g.add("partial_oracle_checks_12", O, check_partial_oracle_checks_12)

    def check_partial_oracle_checks_13():
        return (
            prop(sum(1 for k in true_dos if k in g.dos_map), len(true_dos))
        )
    g.add("partial_oracle_checks_13", O, check_partial_oracle_checks_13)

    def dos_field(cmp_fn):
        return lambda: g.rowscore(g.dos_map, true_dos, cmp_fn)

    def check_partial_oracle_checks_14():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("activity_level_t")),
                                 (p.reports.get(iid) or {}).get("activity_level_t"), 0.002, 1.0))
        )()
    g.add("partial_oracle_checks_14", O, check_partial_oracle_checks_14)
    def check_partial_oracle_checks_15():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("attributed_direct_t")),
                                 (p.reports.get(iid) or {}).get("attributed_direct_t"), 0.002, 1.0))
        )()
    g.add("partial_oracle_checks_15", O, check_partial_oracle_checks_15)
    def check_partial_oracle_checks_16():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("attributed_indirect_t")) or 0.0,
                                 (p.reports.get(iid) or {}).get("attributed_indirect_t") or 0.0,
                                 0.002, 1.0))
        )()
    g.add("partial_oracle_checks_16", O, check_partial_oracle_checks_16)
    def check_partial_oracle_checks_17():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("own_direct_intensity")), p.see(iid)[2], 0.005, 0.002))
        )()
    g.add("partial_oracle_checks_17", O, check_partial_oracle_checks_17)
    def check_partial_oracle_checks_18():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("precursor_direct_component")), p.see(iid)[3],
                                 0.005, 0.002))
        )()
    g.add("partial_oracle_checks_18", O, check_partial_oracle_checks_18)
    def check_partial_oracle_checks_19():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("see_direct_derived")), p.see(iid)[0], 0.005, 0.002))
        )()
    g.add("partial_oracle_checks_19", O, check_partial_oracle_checks_19)
    def check_partial_oracle_checks_20():
        return (
            dos_field(
            lambda v, iid: close(tonum(v.get("see_indirect_derived")), p.see(iid)[1], 0.005, 0.002))
        )()
    g.add("partial_oracle_checks_20", O, check_partial_oracle_checks_20)
    def check_partial_oracle_checks_21():
        return (
            dos_field(
            lambda v, iid: v.get("admissibility", "").strip() ==
            ("admissible" if p.admis[iid] is None else "not_admissible"))
        )()
    g.add("partial_oracle_checks_21", O, check_partial_oracle_checks_21)
    def check_partial_oracle_checks_22():
        return (
            dos_field(
            lambda v, iid: v.get("failing_condition", "").strip() == (p.admis[iid] or "NONE"))
        )()
    g.add("partial_oracle_checks_22", O, check_partial_oracle_checks_22)
    def check_partial_oracle_checks_23():
        return (
            dos_field(
            lambda v, iid: v.get("report_id", "").strip() ==
            ((p.reports.get(iid) or {}).get("report_id") or "NONE")
            and v.get("verification_report", "").strip() ==
            ((p.governing_ver.get(iid) or {}).get("ref") or "NONE"))
        )()
    g.add("partial_oracle_checks_23", O, check_partial_oracle_checks_23)
    def check_partial_oracle_checks_24():
        return (
            dos_field(
            lambda v, iid: v.get("reporting_period_start", "").strip() ==
            ((p.reports.get(iid) or {}).get("period_start") or "")
            and v.get("reporting_period_end", "").strip() ==
            ((p.reports.get(iid) or {}).get("period_end") or ""))
        )()
    g.add("partial_oracle_checks_24", O, check_partial_oracle_checks_24)

    def check_partial_oracle_checks_25():
        return (
            prop(sum(1 for k in true_chain if k in g.chn_map), len(true_chain))
        )
    g.add("partial_oracle_checks_25", O, check_partial_oracle_checks_25)
    def check_partial_oracle_checks_26():
        return (
            g.rowscore(
            g.chn_map, true_chain,
            lambda v, t: close(tonum(v.get("consumption_t_per_t")), t["consumption_t_per_t"],
                               0.005, 0.002))
        )
    g.add("partial_oracle_checks_26", O, check_partial_oracle_checks_26)
    def check_partial_oracle_checks_27():
        return (
            g.rowscore(
            g.chn_map, true_chain,
            lambda v, t: v.get("precursor_basis", "").strip() == t["precursor_basis"])
        )
    g.add("partial_oracle_checks_27", O, check_partial_oracle_checks_27)
    def check_partial_oracle_checks_28():
        return (
            g.rowscore(
            g.chn_map, true_chain,
            lambda v, t: close(tonum(v.get("precursor_see_direct")), t["precursor_see_direct"],
                               0.005, 0.002))
        )
    g.add("partial_oracle_checks_28", O, check_partial_oracle_checks_28)
    def check_partial_oracle_checks_29():
        return (
            g.rowscore(
            g.chn_map, true_chain,
            lambda v, t: close(tonum(v.get("precursor_contribution")), t["precursor_contribution"],
                               0.005, 0.002))
        )
    g.add("partial_oracle_checks_29", O, check_partial_oracle_checks_29)

    def check_partial_oracle_checks_30():
        return (
            g.rowscore(
            g.prc_map, true_claims,
            lambda v, t: v.get("admitted", "").strip().lower() == ("yes" if t["admitted"] else "no")
            and v.get("rejection_condition", "").strip() == t["rejection_condition"])
        )
    g.add("partial_oracle_checks_30", O, check_partial_oracle_checks_30)

    deep = {}
    for iid in p.reg:
        rep_ = p.reports.get(iid)
        if not rep_:
            continue
        for q in rep_["precursors"]:
            up = p.reports.get(q["installation"])
            if up and up["precursors"]:
                deep[iid] = iid
                break

    def check_partial_oracle_checks_31():
        return (
            g.rowscore(
            g.dos_map, deep,
            lambda v, iid: close(tonum(v.get("see_direct_derived")), p.see(iid)[0], 0.005, 0.002),
            set(true_dos))
        )
    g.add("partial_oracle_checks_31", O, check_partial_oracle_checks_31)
    def check_partial_oracle_checks_32():
        return (
            g.rowscore(
            g.prc_map, true_claims,
            lambda v, t: close(tonum(v.get("amount_eur")), t["amount_eur"], 0.002, 1.0))
        )
    g.add("partial_oracle_checks_32", O, check_partial_oracle_checks_32)
    def check_partial_oracle_checks_33():
        return (
            g.rowscore(
            g.prc_map, true_claims,
            lambda v, t: close(tonum(v.get("deduction_t")), t["deduction_t"], 0.005, 0.002))
        )
    g.add("partial_oracle_checks_33", O, check_partial_oracle_checks_33)
    def check_partial_oracle_checks_34():
        return (
            g.rowscore(
            g.prc_map, true_claims,
            lambda v, t: set(x.strip() for x in re.split(r"[;,]", v.get("importers_affected", ""))
                             if x.strip()) == set(t["importers"]))
        )
    g.add("partial_oracle_checks_34", O, check_partial_oracle_checks_34)

    def pos_field(cmp_fn):
        return lambda: g.rowscore(g.pos_map, true_pos, cmp_fn)

    def check_partial_oracle_checks_35():
        return (
            pos_field(
            lambda v, t: close(tonum(v.get("cumulative_net_mass_t")), t["cumulative_net_mass_t"],
                               0.002, 0.05))
        )()
    g.add("partial_oracle_checks_35", O, check_partial_oracle_checks_35)
    def check_partial_oracle_checks_36():
        return (
            pos_field(
            lambda v, t: v.get("threshold_status", "").strip() == t["threshold_status"])
        )()
    g.add("partial_oracle_checks_36", O, check_partial_oracle_checks_36)
    def check_partial_oracle_checks_37():
        return (
            pos_field(
            lambda v, t: close(tonum(v.get("total_embedded_emissions_t")),
                               t["total_embedded_emissions_t"], 0.005, 0.5))
        )()
    g.add("partial_oracle_checks_37", O, check_partial_oracle_checks_37)
    def check_partial_oracle_checks_38():
        return (
            pos_field(
            lambda v, t: close(tonum(v.get("adjusted_emissions_t")), t["adjusted_emissions_t"],
                               0.005, 0.05)
            and close(tonum(v.get("carbon_price_deduction_t")), t["carbon_price_deduction_t"],
                      0.01, 0.05))
        )()
    g.add("partial_oracle_checks_38", O, check_partial_oracle_checks_38)
    def check_partial_oracle_checks_39():
        return (
            pos_field(
            lambda v, t: close(tonum(v.get("certificates_due")), t["certificates_due"], 0.01, 0.5)
            and g._int(v.get("certificates_to_purchase")) == t["certificates_to_purchase"])
        )()
    g.add("partial_oracle_checks_39", O, check_partial_oracle_checks_39)

    def check_partial_oracle_checks_40():
        return (
            g.rowscore(
            g.rem_map, true_rem,
            lambda v, t: v.get("failing_condition", "").strip() == t["failing_condition"]
            and v.get("action_type", "").strip() == t["action_type"]
            and g._int(v.get("slots_required")) == t["slots_required"])
        )
    g.add("partial_oracle_checks_40", O, check_partial_oracle_checks_40)
    def check_partial_oracle_checks_41():
        return (
            g.rowscore(
            g.rem_map, true_rem,
            lambda v, t: close(tonum(v.get("exposure_reduction_t")), t["exposure_reduction_t"],
                               0.01, 0.5))
        )
    g.add("partial_oracle_checks_41", O, check_partial_oracle_checks_41)
    def check_partial_oracle_checks_42():
        return (
            g.rowscore(
            g.rem_map, true_rem,
            lambda v, t: v.get("status", "").strip() == t["status"]
            and v.get("assigned_wave", "").strip() == t["assigned_wave"]
            and (t["status"] == "scheduled"
                 or v.get("not_scheduled_reason", "").strip() == t["not_scheduled_reason"]))
        )
    g.add("partial_oracle_checks_42", O, check_partial_oracle_checks_42)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-dir", default="/logs/agent")
    ap.add_argument("--input-dir", default="/input_artifacts")
    ap.add_argument("--out-dir", default="/logs/verifier")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    corpus = Corpus(args.input_dir)
    pos = Position(corpus)
    g = Grader(pos, corpus, args.agent_dir)
    build_checks(g)

    buckets = defaultdict(list)
    for c in g.checks:
        buckets[c["category"]].append(c["score"])
    static = sum(buckets["static_checks"]) / len(buckets["static_checks"])
    hack = sum(buckets["reward_hacking_checks"]) / len(buckets["reward_hacking_checks"])
    oracle = sum(buckets["partial_oracle_checks"]) / len(buckets["partial_oracle_checks"])
    reward = (static * 1 + hack * 2 + oracle * 3) / 6

    out = OrderedDict()
    out["reward"] = round(reward, 6)
    out["total_static_check_score"] = round(static, 6)
    out["total_reward_hacking_check_score"] = round(hack, 6)
    out["total_partial_oracle_check_score"] = round(oracle, 6)
    with open(os.path.join(args.out_dir, "reward.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(args.out_dir, "scoring_formula.txt"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("reward = (total_static_check_score * 1 + total_reward_hacking_check_score * 2 + "
                 "total_partial_oracle_check_score * 3) / 6\n"
                 "Each bucket score is the unweighted mean of its own checks, so no check carries "
                 "a weight of its own inside its bucket; the weight recorded against a check is "
                 "the weight its bucket carries in the reward, 1 for static_checks, 2 for "
                 "reward_hacking_checks and 3 for partial_oracle_checks. No caps, clamps, floors "
                 "or mode-specific branches are applied anywhere.\n")

    report = {
        "scoring_formula": ("reward = (static*1 + reward_hacking*2 + partial_oracle*3) / 6, each "
                            "bucket the unweighted mean of its own checks"),
        "totals": {"reward": reward, "static": static, "reward_hacking": hack,
                   "partial_oracle": oracle},
        "corpus": {"goods_lines": len(pos.lines), "lines_in_scope": len(pos.in_scope),
                   "installations": len(pos.reg),
                   "admissible": sum(1 for i in pos.reg if pos.admis[i] is None),
                   "claims": len(pos.claims),
                   "claims_admitted": sum(1 for c in pos.claims.values() if c["admitted"]),
                   "importers_above_threshold": len(pos.above),
                   "remediation_actions": len(pos.remediation),
                   "documents": len(corpus.texts)},
        "check_errors": [{"id": c["id"], "error": c["error"]} for c in g.checks if c["error"]],
        "checks": [{"id": c["id"], "category": c["category"], "score": c["score"],
                    "weight": c["weight"], "error": c["error"]} for c in g.checks],
    }
    with open(os.path.join(args.out_dir, "check_report.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")

    with open(os.path.join(args.out_dir, "verifier_status.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        errs = [c["id"] for c in g.checks if c["error"]]
        json.dump({"status": "ok" if not errs else "ok_with_check_errors",
                   "reward_is_graded": True, "exit_code": 0,
                   "total_checks": len(g.checks), "checks_that_raised": errs}, fh, indent=1)
        fh.write("\n")

    print("static  %.6f over %d" % (static, len(buckets["static_checks"])))
    print("hacking %.6f over %d" % (hack, len(buckets["reward_hacking_checks"])))
    print("oracle  %.6f over %d" % (oracle, len(buckets["partial_oracle_checks"])))
    print("reward  %.6f" % reward)
    for c in g.checks:
        print("  %-32s %.4f%s" % (c["id"], c["score"],
                                  "  RAISED: " + c["error"] if c["error"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
