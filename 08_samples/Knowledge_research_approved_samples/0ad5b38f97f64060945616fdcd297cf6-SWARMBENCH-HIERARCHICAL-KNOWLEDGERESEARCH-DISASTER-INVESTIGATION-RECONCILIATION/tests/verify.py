import csv
import json
import os
import re
import sys

RECON = "/logs/agent/reconciliation"
LEDGER = "/logs/agent/reconciliation_ledger.csv"
RECORD_PATHS = {
    "camp-fire-2018": "/logs/agent/reconciliation/camp-fire-2018.json",
    "colorado-floods-2013": "/logs/agent/reconciliation/colorado-floods-2013.json",
    "florence-michael-2018": "/logs/agent/reconciliation/florence-michael-2018.json",
    "harvey-2017": "/logs/agent/reconciliation/harvey-2017.json",
    "ida-2021": "/logs/agent/reconciliation/ida-2021.json",
    "irene-2011": "/logs/agent/reconciliation/irene-2011.json",
    "joplin-tornado-2011": "/logs/agent/reconciliation/joplin-tornado-2011.json",
    "matthew-2016": "/logs/agent/reconciliation/matthew-2016.json",
    "sandy-2012": "/logs/agent/reconciliation/sandy-2012.json",
    "sc-floods-2015": "/logs/agent/reconciliation/sc-floods-2015.json",
    "table-rock-lake-2018": "/logs/agent/reconciliation/table-rock-lake-2018.json",
}
REWARD_TXT = "/logs/verifier/reward.txt"
VENDOR = "/tests/test_logic/vendor/corpus"
KEY_PATH = "/tests/test_logic/answer_key.json"
OUT = "/logs/verifier/reward.json"
DETAILS = "/logs/verifier/details.json"
WINDOW = 400
OVERLAP = 0.5
CATEGORIES = ["fatalities_total", "fatalities_split", "injuries", "damage_usd",
              "peak_wind", "min_pressure", "landfall", "rainfall_max", "surge_or_crest",
              "warning_timing", "outage", "evacuation", "structures", "tornado_or_rating",
              "timeline_event", "other"]
VERDICTS = ["agree_exact", "agree_after_mapping", "discrepant", "single_source_only"]
VERDICT_ALIASES = {
    "agree": "agree_exact", "agrees": "agree_exact", "exact": "agree_exact",
    "agreeexact": "agree_exact", "exactagreement": "agree_exact",
    "identical": "agree_exact", "match": "agree_exact", "consistent": "agree_exact",
    "agreeaftermapping": "agree_after_mapping", "mapping": "agree_after_mapping",
    "agreewithmapping": "agree_after_mapping", "reconcilable": "agree_after_mapping",
    "agreesaftermapping": "agree_after_mapping", "equivalent": "agree_after_mapping",
    "discrepant": "discrepant", "discrepancy": "discrepant", "conflict": "discrepant",
    "conflicting": "discrepant", "disagree": "discrepant", "disagreement": "discrepant",
    "contradiction": "discrepant", "contradictory": "discrepant", "inconsistent": "discrepant",
    "singlesourceonly": "single_source_only", "singlesource": "single_source_only",
    "onesource": "single_source_only", "unique": "single_source_only",
    "onlyonesource": "single_source_only", "solesource": "single_source_only",
    "agreementexact": "agree_exact", "exactly": "agree_exact", "same": "agree_exact",
    "exactmatch": "agree_exact", "agreementexactly": "agree_exact",
    "agreesexactly": "agree_exact", "concur": "agree_exact", "corroborated": "agree_exact",
    "agreementaftermapping": "agree_after_mapping", "aftermapping": "agree_after_mapping",
    "mappingrequired": "agree_after_mapping", "reconcilable": "agree_after_mapping",
    "reconcilesaftermapping": "agree_after_mapping", "mapped": "agree_after_mapping",
    "agreeswithmapping": "agree_after_mapping", "equivalentaftermapping": "agree_after_mapping",
    "partitiondifference": "agree_after_mapping", "taxonomydifference": "agree_after_mapping",
    "differs": "discrepant", "different": "discrepant", "mismatch": "discrepant",
    "conflicts": "discrepant", "contradicts": "discrepant", "notreconcilable": "discrepant",
    "irreconcilable": "discrepant", "diverges": "discrepant",
    "singlesourceonlyfact": "single_source_only", "onlyonereport": "single_source_only",
    "onedocumentonly": "single_source_only", "uniquetoonesource": "single_source_only",
    "notstatedbytheother": "single_source_only", "sourceonly": "single_source_only",
    "contradict": "discrepant", "contradicted": "discrepant", "contradicting": "discrepant",
    "conflicted": "discrepant", "conflictingvalues": "discrepant", "differ": "discrepant",
    "differing": "discrepant", "mismatched": "discrepant", "disagrees": "discrepant",
    "divergent": "discrepant", "diverge": "discrepant", "discrepancies": "discrepant",
    "doesnotmatch": "discrepant", "notmatching": "discrepant", "inconsistency": "discrepant",
    "corroborate": "agree_exact", "corroborates": "agree_exact",
    "corroboration": "agree_exact", "confirms": "agree_exact", "confirmed": "agree_exact",
    "matches": "agree_exact", "matching": "agree_exact", "samevalue": "agree_exact",
    "identicalvalues": "agree_exact", "inagreement": "agree_exact",
    "reconciled": "agree_after_mapping", "reconciles": "agree_after_mapping",
    "derivable": "agree_after_mapping", "convertible": "agree_after_mapping",
    "unitconversion": "agree_after_mapping", "differentpartition": "agree_after_mapping",
    "equivalentafterconversion": "agree_after_mapping",
    "onlyinone": "single_source_only", "oneagencyonly": "single_source_only",
    "notstatedbyother": "single_source_only", "absentfromother": "single_source_only",
    "uniquetoonereport": "single_source_only", "onereportonly": "single_source_only",
}
CATEGORY_ALIASES = {
    "fatalities": "fatalities_total", "deaths": "fatalities_total",
    "deathtoll": "fatalities_total", "totalfatalities": "fatalities_total",
    "fatalitiesbreakdown": "fatalities_split", "deathsplit": "fatalities_split",
    "fatalitysplit": "fatalities_split", "injury": "injuries",
    "damage": "damage_usd", "damages": "damage_usd", "damageestimate": "damage_usd",
    "cost": "damage_usd", "wind": "peak_wind", "winds": "peak_wind",
    "maxwind": "peak_wind", "peakgust": "peak_wind", "windgust": "peak_wind",
    "pressure": "min_pressure", "minimumpressure": "min_pressure",
    "centralpressure": "min_pressure", "rainfall": "rainfall_max",
    "precipitation": "rainfall_max", "maxrainfall": "rainfall_max",
    "surge": "surge_or_crest", "stormsurge": "surge_or_crest", "crest": "surge_or_crest",
    "floodcrest": "surge_or_crest", "streamflow": "surge_or_crest",
    "warning": "warning_timing", "warnings": "warning_timing",
    "leadtime": "warning_timing", "poweroutage": "outage", "outages": "outage",
    "evacuations": "evacuation", "buildings": "structures", "homes": "structures",
    "structuresdestroyed": "structures", "tornado": "tornado_or_rating",
    "tornadoes": "tornado_or_rating", "efrating": "tornado_or_rating",
    "rating": "tornado_or_rating", "timeline": "timeline_event", "chronology": "timeline_event",
}
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
             "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
             "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
             "nineteen": 19, "twenty": 20}
SCALES = {"thousand": 1000.0, "million": 1000000.0, "billion": 1000000000.0,
          "trillion": 1000000000000.0}


def bounded_value(x):
    v = float(x)
    if v < 0.0 or v > 1.0:
        raise RuntimeError("score out of range: %r" % (x,))
    return v


def share(numerator, denominator):
    if denominator <= 0:
        return 0.0
    return bounded_value(float(numerator) / float(denominator))


def corpus_denominator(observed, expected):
    return observed if observed > expected else expected


def collapse(text):
    return re.sub("[\\s\\u00a0]+", " ", text).strip()


def strip_furniture(flat, idx):
    out, oidx, pos = [], [], 0
    for token in re.split("( )", flat):
        if token and re.match("^[0-9]{1,4}$", token):
            pos += len(token)
            continue
        for j, ch in enumerate(token):
            out.append(ch)
            oidx.append(idx[pos + j] if pos + j < len(idx) else idx[-1])
        pos += len(token)
    return "".join(out), oidx


def build_index(text):
    out, idx, prev_space = [], [], True
    for i, ch in enumerate(text):
        if ch.isspace() or ch == "\u00a0":
            if prev_space:
                continue
            out.append(" ")
            idx.append(i)
            prev_space = True
        else:
            out.append(ch)
            idx.append(i)
            prev_space = False
    s = "".join(out)
    lead = len(s) - len(s.lstrip())
    return s.strip(), idx[lead:lead + len(s.strip())]


def fold(text):
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return text


def norm_key(text):
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def resolve_verdict(raw):
    k = norm_key(raw)
    if not k:
        return None
    if k in [norm_key(v) for v in VERDICTS]:
        for v in VERDICTS:
            if norm_key(v) == k:
                return v
    hit = VERDICT_ALIASES.get(k)
    if hit:
        return hit
    for v in VERDICTS:
        if norm_key(v) in k:
            return v
    for alias in sorted(VERDICT_ALIASES, key=len, reverse=True):
        if len(alias) >= 6 and alias in k:
            return VERDICT_ALIASES[alias]
    return None


def resolve_category(raw):
    k = norm_key(raw)
    for c in CATEGORIES:
        if norm_key(c) == k:
            return c
    return CATEGORY_ALIASES.get(k)


def numbers_in(text):
    t = fold(str(text)).lower().replace(",", "")
    out = set()
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(thousand|million|billion|trillion)?", t):
        try:
            v = float(m.group(1))
        except ValueError:
            continue
        if m.group(2):
            v *= SCALES[m.group(2)]
        out.add(round(v, 4))
    for w, v in NUM_WORDS.items():
        if re.search(r"\b%s\b" % w, t):
            out.add(float(v))
    for m in re.finditer(r"\b(\d{1,2}):?(\d{2})\s*(am|pm)?\b", t):
        h, mi = int(m.group(1)), int(m.group(2))
        if m.group(3) == "pm" and h < 12:
            h += 12
        out.add(float(h * 100 + mi))
    return out


def value_is_specific(agent_numbers, key_numbers):
    allowed = len(key_numbers) + 8
    scaled = 3 * len(key_numbers) + 4
    if scaled > allowed:
        allowed = scaled
    return len(agent_numbers) <= allowed


MIN_PROSE_OVERLAP = 0.5
RESTATE_FRACTION = 0.8


def restates_a_source(text, sources):
    m = norm_key(text)
    if not m:
        return False
    for s in sources:
        v = norm_key(s.get("stated_value"))
        if not v:
            continue
        if m == v or (v in m and len(v) >= RESTATE_FRACTION * len(m)):
            return True
    return False


def content_tokens(text):
    return set(t for t in re.findall(r"[a-z0-9]+", fold(str(text or "")).lower())
               if len(t) > 3)


def token_overlap(agent_text, source_text):
    a = content_tokens(agent_text)
    b = content_tokens(source_text)
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a))


def values_match(agent_value, key_value):
    a, k = numbers_in(agent_value), numbers_in(key_value)
    if not value_is_specific(a, k):
        return False
    if k and a:
        if k & a:
            return True
        for kv in k:
            for av in a:
                tol = abs(kv) / 200.0
                if tol < 0.01:
                    tol = 0.01
                if kv and abs(kv - av) <= tol:
                    return True
        return False
    return norm_key(agent_value) == norm_key(key_value) and bool(norm_key(key_value))


class Corpus(object):
    def __init__(self):
        self.raw, self.flat, self.index, self.alias = {}, {}, {}, {}
        self.bare, self.bare_index = {}, {}
        for event in sorted(os.listdir(VENDOR)):
            d = os.path.join(VENDOR, event)
            if not os.path.isdir(d):
                continue
            for name in sorted(os.listdir(d)):
                if not name.endswith(".txt"):
                    continue
                text = open(os.path.join(d, name), encoding="utf-8", errors="replace").read()
                flat, idx = build_index(fold(text))
                self.raw[(event, name)] = text
                self.flat[(event, name)] = flat
                self.index[(event, name)] = idx
                bare, bidx = strip_furniture(flat, idx)
                self.bare[(event, name)] = bare
                self.bare_index[(event, name)] = bidx
                stem = name[:-4]
                for a in (name, stem, norm_key(stem), stem.replace("-", " ")):
                    self.alias.setdefault((event, norm_key(a)), name)
                for a in self.short_names(stem):
                    self.alias.setdefault((event, norm_key(a)), name)

    def short_names(self, stem):
        out = []
        if "tropical-cyclone-report" in stem:
            out += ["tcr", "nhc report", "nhc", "tropical cyclone report"]
            if stem.endswith("-florence"):
                out += ["tcr florence", "florence tcr"]
            if stem.endswith("-michael"):
                out += ["tcr michael", "michael tcr"]
        if "service-assessment" in stem:
            out += ["sa", "nws", "service assessment", "nws service assessment"]
        if "nist" in stem:
            out += ["nist", "nist report", "nist investigation"]
        if "ntsb" in stem:
            out += ["ntsb", "ntsb report"]
        if "usgs" in stem:
            out += ["usgs", "usgs report"]
        if "fema" in stem:
            out += ["fema", "fema report", "after action report"]
        return out

    def resolve_doc(self, event, name):
        if not name:
            return None
        base = os.path.basename(str(name).strip())
        if (event, base) in self.raw:
            return base
        return self.alias.get((event, norm_key(base)))

    def locate(self, event, doc, quote):
        key = (event, doc)
        if key not in self.flat or not quote:
            return None
        needle, _ = build_index(fold(str(quote)))
        if len(needle) < 60:
            return None
        hay = self.flat[key]
        idx = self.index[key]
        pos = hay.find(needle)
        if pos < 0:
            pos = hay.lower().find(needle.lower())
        if pos < 0:
            original = needle
            bare_needle, _ = strip_furniture(needle, list(range(len(needle))))
            hay, idx = self.bare[key], self.bare_index[key]
            pos = hay.find(bare_needle)
            if pos < 0:
                pos = hay.lower().find(bare_needle.lower())
            if pos >= 0:
                last = pos + len(bare_needle)
                if last > len(idx):
                    last = len(idx)
                if last > pos:
                    span = self.raw[key][idx[pos]:idx[last - 1] + 1]
                    if not numbers_in(original) <= numbers_in(span):
                        return None
            needle = bare_needle
        if pos < 0 or not idx:
            return None
        last = pos + len(needle)
        if last > len(idx):
            last = len(idx)
        end = last - 1
        if end < pos:
            end = pos
        return (idx[pos], idx[end])

    def span_text(self, event, doc, span):
        raw = self.raw.get((event, doc))
        if raw is None or not span:
            return ""
        return raw[span[0]:span[1] + 1]


class Evaluator(object):
    def __init__(self):
        self.corpus = Corpus()
        self.key = json.load(open(KEY_PATH, encoding="utf-8"))["units"]
        self.key_by_event = {}
        for u in self.key:
            self.key_by_event.setdefault(u["event"], []).append(u)
        self.events = sorted(self.key_by_event)
        self.submitted = {}
        self.parse_errors = {}
        for event in self.events:
            self.submitted[event] = self.read_event(event)
        self.ledger_rows, self.ledger_header = self.read_ledger()
        self.aligned = {}
        self.claimed_key = {}
        self.unit_spans = {}
        self.notes = {"unresolved_verdicts": [], "unresolved_categories": [],
                      "unresolved_documents": []}
        self.align()

    def read_event(self, event):
        path = RECORD_PATHS.get(event, os.path.join(RECON, "%s.json" % event))
        if not os.path.isfile(path):
            return []
        try:
            data = json.load(open(path, encoding="utf-8", errors="replace"))
        except Exception as exc:
            self.parse_errors[event] = repr(exc)
            return []
        units = data.get("units") if isinstance(data, dict) else data
        if not isinstance(units, list):
            return []
        out = []
        for u in units:
            if isinstance(u, dict):
                out.append(u)
        return out

    def read_ledger(self):
        if not os.path.isfile(LEDGER):
            return [], []
        try:
            with open(LEDGER, encoding="utf-8", errors="replace") as fh:
                rows = list(csv.reader(fh))
        except Exception:
            return [], []
        if not rows:
            return [], []
        return rows[1:], [norm_key(c) for c in rows[0]]

    def unit_sources(self, event, unit):
        out = []
        for s in (unit.get("sources") or []):
            if not isinstance(s, dict):
                continue
            doc = self.corpus.resolve_doc(event, s.get("document"))
            quote = s.get("quote") or ""
            span = self.corpus.locate(event, doc, quote) if doc else None
            out.append({"document": doc, "raw_document": s.get("document"),
                        "stated_value": s.get("stated_value", ""),
                        "quote": quote, "span": span})
        return out

    def near(self, span, key_source, value=None):
        if not span:
            return False
        a0, a1 = span
        b0, b1 = key_source["quote_start"], key_source["quote_end"]
        klen = float(b1 - b0) if b1 > b0 else 1.0
        lo = a0 if a0 > b0 else b0
        hi = a1 if a1 < b1 else b1
        if hi > lo and (hi - lo) / klen >= OVERLAP:
            return True
        gap = (b0 - a1 if b0 > a1 else a0 - b1)
        if gap <= WINDOW and value is not None:
            return values_match(value, key_source["stated_value"])
        return False

    def pair_quality(self, srcs, unit, keyunit):
        matched, values, best = 0, 0, None
        for ks in keyunit["sources"]:
            for s in srcs:
                if s["document"] != ks["document"] or not self.near(
                        s["span"], ks, s["stated_value"]):
                    continue
                matched += 1
                if values_match(s["stated_value"], ks["stated_value"]):
                    values += 1
                mid = (s["span"][0] + s["span"][1]) // 2
                kmid = (ks["quote_start"] + ks["quote_end"]) // 2
                d = abs(mid - kmid)
                best = d if best is None else (d if d < best else best)
                break
        if not matched:
            return None
        return (matched, values, -(best if best is not None else 0))

    def align(self):
        for event in self.events:
            keyunits = self.key_by_event[event]
            submitted = self.submitted.get(event, [])
            for pos, unit in enumerate(submitted):
                self.unit_spans[(event, pos)] = self.unit_sources(event, unit)
            candidates = []
            for pos, unit in enumerate(submitted):
                srcs = self.unit_spans[(event, pos)]
                cat = resolve_category(unit.get("category"))
                for ku in keyunits:
                    if cat != ku["category"]:
                        continue
                    q = self.pair_quality(srcs, unit, ku)
                    if q is not None:
                        candidates.append((q, pos, ku["unit_id"]))
            candidates.sort(key=lambda c: (c[0][0], c[0][1], c[0][2]), reverse=True)
            used_key, used_pos, claimed_spans = set(), set(), []
            for _, pos, uid in candidates:
                if uid in used_key or pos in used_pos:
                    continue
                srcs = self.unit_spans[(event, pos)]
                if any(self.span_taken(claimed_spans, s) for s in srcs if s["span"]):
                    continue
                used_key.add(uid)
                used_pos.add(pos)
                self.aligned[uid] = {"event": event, "pos": pos, "unit": submitted[pos],
                                     "sources": srcs}
                self.claimed_key[(event, pos)] = uid
                for s in srcs:
                    if s["span"]:
                        claimed_spans.append((s["document"], s["span"]))

    def span_taken(self, claimed, src):
        if not src["span"]:
            return False
        a0, a1 = src["span"]
        for doc, (b0, b1) in claimed:
            if doc != src["document"]:
                continue
            lo = a0 if a0 > b0 else b0
            hi = a1 if a1 < b1 else b1
            if hi <= lo:
                continue
            shorter = (a1 - a0) if (a1 - a0) < (b1 - b0) else (b1 - b0)
            if shorter <= 0 or (hi - lo) / float(shorter) >= OVERLAP:
                return True
        return False

    def grounded_sources(self, event, pos):
        return [s for s in self.unit_spans.get((event, pos), []) if s["span"]]

    def unit_grounding(self, unit_id):
        rec = self.aligned.get(unit_id)
        if not rec:
            return 0.0
        ku = [u for u in self.key if u["unit_id"] == unit_id][0]
        hit = 0
        for ks in ku["sources"]:
            for s in rec["sources"]:
                if s["document"] == ks["document"] and self.near(
                        s["span"], ks, s["stated_value"]):
                    hit += 1
                    break
        return share(hit, len(ku["sources"]))

    def key_passage(self, event, key_source):
        raw = self.corpus.raw.get((event, key_source["document"]))
        if raw is None:
            return ""
        a = key_source.get("quote_start")
        b = key_source.get("quote_end")
        if a is None or b is None:
            return ""
        return raw[a:b]

    def passage_numbers(self, event, key_source):
        return numbers_in(self.key_passage(event, key_source))

    def unit_values(self, unit_id):
        rec = self.aligned.get(unit_id)
        if not rec:
            return 0.0
        ku = [u for u in self.key if u["unit_id"] == unit_id][0]
        event = ku["event"]
        hit = 0
        for ks in ku["sources"]:
            for s in rec["sources"]:
                if s["document"] != ks["document"]:
                    continue
                if self.value_from_passage(event, ks, s["stated_value"]):
                    hit += 1
                    break
        return share(hit, len(ku["sources"]))

    def value_from_passage(self, event, key_source, stated):
        text = str(stated or "")
        if not text.strip():
            return False
        passage = self.key_passage(event, key_source)
        if not passage:
            return False
        said = numbers_in(text)
        source = numbers_in(passage)
        if said:
            if not value_is_specific(said, source):
                return False
            outside = [x for x in said if not any(
                x == y or (y and abs(x - y) <= max(abs(y) / 200.0, 0.01)) for y in source)]
            if outside:
                return False
            return bool(said)
        return token_overlap(text, passage) >= MIN_PROSE_OVERLAP

    def unit_verdict(self, unit_id):
        rec = self.aligned.get(unit_id)
        if not rec:
            return 0.0
        ku = [u for u in self.key if u["unit_id"] == unit_id][0]
        got = resolve_verdict(rec["unit"].get("verdict"))
        if got is None:
            self.notes["unresolved_verdicts"].append(str(rec["unit"].get("verdict"))[:60])
            return 0.0
        if not self.verdict_supported(ku, rec, got):
            return 0.0
        return 1.0 if got == ku["verdict"] else 0.0

    def verdict_supported(self, ku, rec, got):
        grounded = [s for s in rec["sources"] if s.get("span")]
        docs = set(s["document"] for s in grounded)
        if got == "single_source_only":
            return len(docs) <= 1
        if len(docs) < 2:
            return False
        if got != "agree_after_mapping":
            return True
        text = rec["unit"].get("mapping_arithmetic")
        return bool(text and str(text).strip()
                    and norm_key(text) not in ("null", "none", "na"))

    def unit_mapping(self, unit_id):
        rec = self.aligned.get(unit_id)
        if not rec:
            return 0.0
        ku = [u for u in self.key if u["unit_id"] == unit_id][0]
        event = ku["event"]
        text = rec["unit"].get("mapping_arithmetic")
        if not text or not str(text).strip() or norm_key(text) in ("null", "none", "na"):
            return 0.0
        if restates_a_source(text, rec["sources"]):
            return 0.0
        got = numbers_in(text)
        if not got:
            return 0.0
        sides = [self.passage_numbers(event, ks) for ks in ku["sources"]]
        sides = [s for s in sides if s]
        if len(sides) < 2:
            return 0.0
        union = set()
        for s in sides:
            union |= s
        if not value_is_specific(got, union):
            return 0.0
        reached = sum(1 for s in sides if got & s)
        return share(reached, len(sides))

    def reconciled_positions(self, event):
        out, claimed = [], []
        for pos in range(len(self.submitted.get(event, []))):
            grounded = self.grounded_sources(event, pos)
            docs = set(s["document"] for s in grounded)
            spans = set((s["document"], s["span"]) for s in grounded)
            if len(docs) < 2 or len(spans) < 2:
                continue
            if any(self.span_taken(claimed, s) for s in grounded):
                continue
            for s in grounded:
                claimed.append((s["document"], s["span"]))
            out.append(pos)
        return out

    def event_aligned_positions(self, event):
        return [pos for (e, pos) in self.claimed_key if e == event]

    def shows_comprehension(self, event, pos):
        uid = self.claimed_key.get((event, pos))
        if not uid:
            return False
        ku = [k for k in self.key if k["unit_id"] == uid][0]
        unit = self.submitted[event][pos]
        if resolve_verdict(unit.get("verdict")) == ku["verdict"]:
            return True
        want = numbers_in(ku.get("mapping") or "")
        got = numbers_in(unit.get("mapping_arithmetic") or "")
        return bool(want) and len(want & got) >= 2

    def event_credit_positions(self, event):
        aligned = set(self.event_aligned_positions(event))
        sourced = [p for p in self.reconciled_positions(event) if p in aligned]
        for pos in aligned:
            if pos in sourced:
                continue
            unit = self.submitted[event][pos]
            if resolve_verdict(unit.get("verdict")) != "single_source_only":
                continue
            if len(self.grounded_sources(event, pos)) == 1:
                sourced.append(pos)
        return sorted(p for p in sourced if self.shows_comprehension(event, p))

    def has_any_reconciliation(self):
        for event in self.events:
            if self.event_credit_positions(event):
                return True
        return False

    def event_records_usable(self, event):
        units = self.submitted.get(event, [])
        credit = self.event_credit_positions(event)
        if not units or not credit:
            return 0.0
        mass = 0.0
        for u in [units[p] for p in credit]:
            fields = 0
            if resolve_category(u.get("category")):
                fields += 1
            if str(u.get("qualifier") or "").strip():
                fields += 1
            if resolve_verdict(u.get("verdict")):
                fields += 1
            srcs = u.get("sources") or []
            if srcs and all(isinstance(s, dict) and s.get("document")
                            and str(s.get("stated_value") or "").strip()
                            and str(s.get("quote") or "").strip() for s in srcs):
                fields += 1
            mass += fields / 4.0
        return share(mass, corpus_denominator(len(credit),
                                              len(self.key_by_event.get(event, []))))

    def ledger_shape(self):
        if not self.has_any_reconciliation() or not self.ledger_header:
            return 0.0
        want = ["event", "category", "verdict", "documents"]
        hit = sum(1 for w in want if norm_key(w) in self.ledger_header)
        return share(hit, len(want))

    def event_coverage(self):
        if not self.has_any_reconciliation():
            return 0.0
        ok = 0
        for event in self.events:
            if event not in self.parse_errors:
                ok += len(self.event_credit_positions(event))
        return share(ok, len(self.key))

    def key_source_count(self):
        return sum(len(u["sources"]) for u in self.key)

    def key_size(self, event):
        return len([u for u in self.key_by_event.get(event, [])
                    if u["verdict"] != "single_source_only"])

    def event_authorship(self, event):
        units = self.submitted.get(event, [])
        claimed = [pos for pos, u in enumerate(units)
                   if resolve_verdict(u.get("verdict")) != "single_source_only"]
        credit = set(self.event_credit_positions(event))
        ok = len([p for p in claimed if p in credit])
        return share(ok, corpus_denominator(len(claimed), self.key_size(event)))

    def event_span_distinct(self, event):
        seen, ok, total = [], 0, 0
        for pos in self.event_credit_positions(event):
            for s in self.grounded_sources(event, pos):
                total += 1
                if not self.span_taken(seen, s):
                    ok += 1
                seen.append((s["document"], s["span"]))
        return share(ok, corpus_denominator(total, 2 * self.key_size(event)))

    def alignment_precision(self):
        submitted = sum(len(v) for v in self.submitted.values())
        return share(len(self.aligned), corpus_denominator(submitted, len(self.key)))

    def stated_values_in_source(self):
        ok = total = 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                for s in self.unit_spans.get((event, pos), []):
                    nums = numbers_in(s["stated_value"])
                    if not nums:
                        continue
                    total += 1
                    if nums & numbers_in(s["quote"]):
                        ok += 1
        return share(ok, corpus_denominator(total, self.key_source_count()))

    def verdict_not_blanket(self):
        counts, grounded = {}, 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                u = self.submitted[event][pos]
                grounded += 1
                v = resolve_verdict(u.get("verdict"))
                counts[v] = counts.get(v, 0) + 1
        if grounded <= 0:
            return 0.0
        denom = float(grounded if grounded > 20 else 20)
        keyc = {}
        for u in self.key:
            keyc[u["verdict"]] = keyc.get(u["verdict"], 0) + 1
        spread = 0.0
        for v in VERDICTS:
            spread += abs(counts.get(v, 0) / denom - keyc.get(v, 0) / float(len(self.key)))
        return bounded_value(1.0 - spread / 2.0)

    def ledger_agrees_with_records(self):
        if not self.ledger_rows or not self.ledger_header:
            return 0.0
        want = set()
        for event in self.events:
            for pos in self.event_credit_positions(event):
                u = self.submitted[event][pos]
                docs = tuple(sorted(s["document"] or ""
                                    for s in self.unit_spans.get((event, pos), [])))
                want.add((event, resolve_category(u.get("category")),
                          resolve_verdict(u.get("verdict")), docs))
        idx = {}
        for i, c in enumerate(self.ledger_header):
            idx.setdefault(c, i)
        need = [norm_key(x) for x in ("event", "category", "verdict", "documents")]
        if any(c not in idx for c in need):
            return 0.0
        ok = 0
        for row in self.ledger_rows:
            try:
                e = row[idx[need[0]]].strip()
                c = resolve_category(row[idx[need[1]]])
                v = resolve_verdict(row[idx[need[2]]])
                parts = [p for p in re.split(r"[;|]", row[idx[need[3]]]) if p.strip()]
                d = tuple(sorted(self.corpus.resolve_doc(e, p) or "" for p in parts))
            except Exception:
                continue
            if (e, c, v, d) in want:
                ok += 1
        return share(ok, corpus_denominator(len(self.ledger_rows), len(self.key)))

    def no_cross_event_quote_reuse(self):
        seen, ok, total = {}, 0, 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                for s in self.grounded_sources(event, pos):
                    k = norm_key(s["quote"])[:200]
                    total += 1
                    if seen.setdefault(k, event) == event:
                        ok += 1
        return share(ok, corpus_denominator(total, self.key_source_count()))

    def document_attribution_valid(self):
        ok = total = 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                for s in self.unit_spans.get((event, pos), []):
                    if len(collapse(str(s["quote"] or ""))) < 40:
                        continue
                    total += 1
                    if s["span"]:
                        ok += 1
        return share(ok, corpus_denominator(total, self.key_source_count()))

    def mapping_present_where_claimed(self):
        ok = total = 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                u = self.submitted[event][pos]
                if resolve_verdict(u.get("verdict")) not in ("agree_after_mapping", "discrepant"):
                    continue
                total += 1
                if restates_a_source(u.get("mapping_arithmetic"), u.get("sources") or []):
                    continue
                nums = numbers_in(u.get("mapping_arithmetic") or "")
                srcs = []
                for x in self.unit_spans.get((event, pos), []):
                    if not x["span"]:
                        continue
                    cited = numbers_in(self.corpus.span_text(event, x["document"], x["span"]))
                    if cited:
                        srcs.append(cited)
                if not nums or not srcs:
                    continue
                reached = len([cited for cited in srcs if nums & cited])
                ok += share(reached, len(srcs))
        expected = len([u for u in self.key
                        if u["verdict"] in ("agree_after_mapping", "discrepant")])
        return share(ok, corpus_denominator(total, expected))

    def sources_from_distinct_reports(self):
        ok = total = 0
        for event in self.events:
            for pos, u in enumerate(self.submitted.get(event, [])):
                srcs = self.unit_spans.get((event, pos), [])
                if len(srcs) < 2 or not self.grounded_sources(event, pos):
                    continue
                total += 1
                named = [s["document"] for s in srcs if s["document"]]
                if len(set(named)) == len(srcs):
                    ok += 1
        expected = len([u for u in self.key if len(u["sources"]) >= 2])
        return share(ok, corpus_denominator(total, expected))

    def single_source_discipline(self):
        expected = [u for u in self.key if u["verdict"] == "single_source_only"]
        ok = 0
        for u in expected:
            rec = self.aligned.get(u["unit_id"])
            if rec and resolve_verdict(rec["unit"].get("verdict")) == "single_source_only":
                ok += 1
        wrong = 0
        for event in self.events:
            for pos in self.event_credit_positions(event):
                uid = self.claimed_key.get((event, pos))
                if not uid:
                    continue
                ku = [k for k in self.key if k["unit_id"] == uid][0]
                got = resolve_verdict(self.submitted[event][pos].get("verdict"))
                if got == "single_source_only" and ku["verdict"] != "single_source_only":
                    wrong += 1
        return share(ok, corpus_denominator(len(expected) + wrong, len(expected)))


def load_evaluator():
    return Evaluator()


def check_event_camp_fire_2018_records_usable(ev):
    return ev.event_records_usable('camp-fire-2018')

def check_event_colorado_floods_2013_records_usable(ev):
    return ev.event_records_usable('colorado-floods-2013')

def check_event_florence_michael_2018_records_usable(ev):
    return ev.event_records_usable('florence-michael-2018')

def check_event_harvey_2017_records_usable(ev):
    return ev.event_records_usable('harvey-2017')

def check_event_ida_2021_records_usable(ev):
    return ev.event_records_usable('ida-2021')

def check_event_irene_2011_records_usable(ev):
    return ev.event_records_usable('irene-2011')

def check_event_joplin_tornado_2011_records_usable(ev):
    return ev.event_records_usable('joplin-tornado-2011')

def check_event_matthew_2016_records_usable(ev):
    return ev.event_records_usable('matthew-2016')

def check_event_sandy_2012_records_usable(ev):
    return ev.event_records_usable('sandy-2012')

def check_event_sc_floods_2015_records_usable(ev):
    return ev.event_records_usable('sc-floods-2015')

def check_event_table_rock_lake_2018_records_usable(ev):
    return ev.event_records_usable('table-rock-lake-2018')

def check_ledger_shape(ev):
    return ev.ledger_shape()

def check_event_coverage(ev):
    return ev.event_coverage()

def check_authorship_camp_fire_2018(ev):
    return ev.event_authorship('camp-fire-2018')

def check_authorship_colorado_floods_2013(ev):
    return ev.event_authorship('colorado-floods-2013')

def check_authorship_florence_michael_2018(ev):
    return ev.event_authorship('florence-michael-2018')

def check_authorship_harvey_2017(ev):
    return ev.event_authorship('harvey-2017')

def check_authorship_ida_2021(ev):
    return ev.event_authorship('ida-2021')

def check_authorship_irene_2011(ev):
    return ev.event_authorship('irene-2011')

def check_authorship_joplin_tornado_2011(ev):
    return ev.event_authorship('joplin-tornado-2011')

def check_authorship_matthew_2016(ev):
    return ev.event_authorship('matthew-2016')

def check_authorship_sandy_2012(ev):
    return ev.event_authorship('sandy-2012')

def check_authorship_sc_floods_2015(ev):
    return ev.event_authorship('sc-floods-2015')

def check_authorship_table_rock_lake_2018(ev):
    return ev.event_authorship('table-rock-lake-2018')

def check_span_distinct_camp_fire_2018(ev):
    return ev.event_span_distinct('camp-fire-2018')

def check_span_distinct_colorado_floods_2013(ev):
    return ev.event_span_distinct('colorado-floods-2013')

def check_span_distinct_florence_michael_2018(ev):
    return ev.event_span_distinct('florence-michael-2018')

def check_span_distinct_harvey_2017(ev):
    return ev.event_span_distinct('harvey-2017')

def check_span_distinct_ida_2021(ev):
    return ev.event_span_distinct('ida-2021')

def check_span_distinct_irene_2011(ev):
    return ev.event_span_distinct('irene-2011')

def check_span_distinct_joplin_tornado_2011(ev):
    return ev.event_span_distinct('joplin-tornado-2011')

def check_span_distinct_matthew_2016(ev):
    return ev.event_span_distinct('matthew-2016')

def check_span_distinct_sandy_2012(ev):
    return ev.event_span_distinct('sandy-2012')

def check_span_distinct_sc_floods_2015(ev):
    return ev.event_span_distinct('sc-floods-2015')

def check_span_distinct_table_rock_lake_2018(ev):
    return ev.event_span_distinct('table-rock-lake-2018')

def check_alignment_precision(ev):
    return ev.alignment_precision()

def check_stated_values_in_source(ev):
    return ev.stated_values_in_source()

def check_verdict_not_blanket(ev):
    return ev.verdict_not_blanket()

def check_ledger_agrees_with_records(ev):
    return ev.ledger_agrees_with_records()

def check_no_cross_event_quote_reuse(ev):
    return ev.no_cross_event_quote_reuse()

def check_document_attribution_valid(ev):
    return ev.document_attribution_valid()

def check_mapping_present_where_claimed(ev):
    return ev.mapping_present_where_claimed()

def check_single_source_discipline(ev):
    return ev.single_source_discipline()

def check_sources_from_distinct_reports(ev):
    return ev.sources_from_distinct_reports()

def check_camp_fire_2018_01_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-01')

def check_camp_fire_2018_01_values(ev):
    return ev.unit_values('camp-fire-2018-01')

def check_camp_fire_2018_01_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-01')

def check_camp_fire_2018_01_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-01')

def check_camp_fire_2018_02_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-02')

def check_camp_fire_2018_02_values(ev):
    return ev.unit_values('camp-fire-2018-02')

def check_camp_fire_2018_02_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-02')

def check_camp_fire_2018_02_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-02')

def check_camp_fire_2018_03_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-03')

def check_camp_fire_2018_03_values(ev):
    return ev.unit_values('camp-fire-2018-03')

def check_camp_fire_2018_03_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-03')

def check_camp_fire_2018_03_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-03')

def check_camp_fire_2018_04_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-04')

def check_camp_fire_2018_04_values(ev):
    return ev.unit_values('camp-fire-2018-04')

def check_camp_fire_2018_04_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-04')

def check_camp_fire_2018_04_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-04')

def check_camp_fire_2018_05_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-05')

def check_camp_fire_2018_05_values(ev):
    return ev.unit_values('camp-fire-2018-05')

def check_camp_fire_2018_05_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-05')

def check_camp_fire_2018_05_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-05')

def check_camp_fire_2018_06_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-06')

def check_camp_fire_2018_06_values(ev):
    return ev.unit_values('camp-fire-2018-06')

def check_camp_fire_2018_06_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-06')

def check_camp_fire_2018_06_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-06')

def check_camp_fire_2018_07_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-07')

def check_camp_fire_2018_07_values(ev):
    return ev.unit_values('camp-fire-2018-07')

def check_camp_fire_2018_07_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-07')

def check_camp_fire_2018_08_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-08')

def check_camp_fire_2018_08_values(ev):
    return ev.unit_values('camp-fire-2018-08')

def check_camp_fire_2018_08_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-08')

def check_camp_fire_2018_08_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-08')

def check_camp_fire_2018_09_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-09')

def check_camp_fire_2018_09_values(ev):
    return ev.unit_values('camp-fire-2018-09')

def check_camp_fire_2018_09_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-09')

def check_camp_fire_2018_10_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-10')

def check_camp_fire_2018_10_values(ev):
    return ev.unit_values('camp-fire-2018-10')

def check_camp_fire_2018_10_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-10')

def check_camp_fire_2018_10_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-10')

def check_camp_fire_2018_11_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-11')

def check_camp_fire_2018_11_values(ev):
    return ev.unit_values('camp-fire-2018-11')

def check_camp_fire_2018_11_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-11')

def check_camp_fire_2018_12_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-12')

def check_camp_fire_2018_12_values(ev):
    return ev.unit_values('camp-fire-2018-12')

def check_camp_fire_2018_12_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-12')

def check_camp_fire_2018_12_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-12')

def check_camp_fire_2018_13_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-13')

def check_camp_fire_2018_13_values(ev):
    return ev.unit_values('camp-fire-2018-13')

def check_camp_fire_2018_13_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-13')

def check_camp_fire_2018_14_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-14')

def check_camp_fire_2018_14_values(ev):
    return ev.unit_values('camp-fire-2018-14')

def check_camp_fire_2018_14_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-14')

def check_camp_fire_2018_14_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-14')

def check_camp_fire_2018_15_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-15')

def check_camp_fire_2018_15_values(ev):
    return ev.unit_values('camp-fire-2018-15')

def check_camp_fire_2018_15_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-15')

def check_camp_fire_2018_15_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-15')

def check_camp_fire_2018_16_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-16')

def check_camp_fire_2018_16_values(ev):
    return ev.unit_values('camp-fire-2018-16')

def check_camp_fire_2018_16_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-16')

def check_camp_fire_2018_16_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-16')

def check_camp_fire_2018_17_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-17')

def check_camp_fire_2018_17_values(ev):
    return ev.unit_values('camp-fire-2018-17')

def check_camp_fire_2018_17_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-17')

def check_camp_fire_2018_17_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-17')

def check_camp_fire_2018_18_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-18')

def check_camp_fire_2018_18_values(ev):
    return ev.unit_values('camp-fire-2018-18')

def check_camp_fire_2018_18_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-18')

def check_camp_fire_2018_18_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-18')

def check_camp_fire_2018_19_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-19')

def check_camp_fire_2018_19_values(ev):
    return ev.unit_values('camp-fire-2018-19')

def check_camp_fire_2018_19_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-19')

def check_camp_fire_2018_19_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-19')

def check_camp_fire_2018_20_grounding(ev):
    return ev.unit_grounding('camp-fire-2018-20')

def check_camp_fire_2018_20_values(ev):
    return ev.unit_values('camp-fire-2018-20')

def check_camp_fire_2018_20_verdict(ev):
    return ev.unit_verdict('camp-fire-2018-20')

def check_camp_fire_2018_20_mapping(ev):
    return ev.unit_mapping('camp-fire-2018-20')

def check_colorado_floods_2013_01_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-01')

def check_colorado_floods_2013_01_values(ev):
    return ev.unit_values('colorado-floods-2013-01')

def check_colorado_floods_2013_01_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-01')

def check_colorado_floods_2013_01_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-01')

def check_colorado_floods_2013_02_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-02')

def check_colorado_floods_2013_02_values(ev):
    return ev.unit_values('colorado-floods-2013-02')

def check_colorado_floods_2013_02_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-02')

def check_colorado_floods_2013_02_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-02')

def check_colorado_floods_2013_03_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-03')

def check_colorado_floods_2013_03_values(ev):
    return ev.unit_values('colorado-floods-2013-03')

def check_colorado_floods_2013_03_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-03')

def check_colorado_floods_2013_04_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-04')

def check_colorado_floods_2013_04_values(ev):
    return ev.unit_values('colorado-floods-2013-04')

def check_colorado_floods_2013_04_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-04')

def check_colorado_floods_2013_04_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-04')

def check_colorado_floods_2013_05_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-05')

def check_colorado_floods_2013_05_values(ev):
    return ev.unit_values('colorado-floods-2013-05')

def check_colorado_floods_2013_05_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-05')

def check_colorado_floods_2013_06_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-06')

def check_colorado_floods_2013_06_values(ev):
    return ev.unit_values('colorado-floods-2013-06')

def check_colorado_floods_2013_06_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-06')

def check_colorado_floods_2013_07_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-07')

def check_colorado_floods_2013_07_values(ev):
    return ev.unit_values('colorado-floods-2013-07')

def check_colorado_floods_2013_07_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-07')

def check_colorado_floods_2013_07_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-07')

def check_colorado_floods_2013_08_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-08')

def check_colorado_floods_2013_08_values(ev):
    return ev.unit_values('colorado-floods-2013-08')

def check_colorado_floods_2013_08_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-08')

def check_colorado_floods_2013_08_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-08')

def check_colorado_floods_2013_09_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-09')

def check_colorado_floods_2013_09_values(ev):
    return ev.unit_values('colorado-floods-2013-09')

def check_colorado_floods_2013_09_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-09')

def check_colorado_floods_2013_09_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-09')

def check_colorado_floods_2013_10_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-10')

def check_colorado_floods_2013_10_values(ev):
    return ev.unit_values('colorado-floods-2013-10')

def check_colorado_floods_2013_10_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-10')

def check_colorado_floods_2013_10_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-10')

def check_colorado_floods_2013_11_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-11')

def check_colorado_floods_2013_11_values(ev):
    return ev.unit_values('colorado-floods-2013-11')

def check_colorado_floods_2013_11_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-11')

def check_colorado_floods_2013_12_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-12')

def check_colorado_floods_2013_12_values(ev):
    return ev.unit_values('colorado-floods-2013-12')

def check_colorado_floods_2013_12_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-12')

def check_colorado_floods_2013_12_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-12')

def check_colorado_floods_2013_13_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-13')

def check_colorado_floods_2013_13_values(ev):
    return ev.unit_values('colorado-floods-2013-13')

def check_colorado_floods_2013_13_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-13')

def check_colorado_floods_2013_13_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-13')

def check_colorado_floods_2013_14_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-14')

def check_colorado_floods_2013_14_values(ev):
    return ev.unit_values('colorado-floods-2013-14')

def check_colorado_floods_2013_14_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-14')

def check_colorado_floods_2013_14_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-14')

def check_colorado_floods_2013_15_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-15')

def check_colorado_floods_2013_15_values(ev):
    return ev.unit_values('colorado-floods-2013-15')

def check_colorado_floods_2013_15_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-15')

def check_colorado_floods_2013_15_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-15')

def check_colorado_floods_2013_16_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-16')

def check_colorado_floods_2013_16_values(ev):
    return ev.unit_values('colorado-floods-2013-16')

def check_colorado_floods_2013_16_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-16')

def check_colorado_floods_2013_16_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-16')

def check_colorado_floods_2013_17_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-17')

def check_colorado_floods_2013_17_values(ev):
    return ev.unit_values('colorado-floods-2013-17')

def check_colorado_floods_2013_17_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-17')

def check_colorado_floods_2013_17_mapping(ev):
    return ev.unit_mapping('colorado-floods-2013-17')

def check_colorado_floods_2013_18_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-18')

def check_colorado_floods_2013_18_values(ev):
    return ev.unit_values('colorado-floods-2013-18')

def check_colorado_floods_2013_18_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-18')

def check_colorado_floods_2013_19_grounding(ev):
    return ev.unit_grounding('colorado-floods-2013-19')

def check_colorado_floods_2013_19_values(ev):
    return ev.unit_values('colorado-floods-2013-19')

def check_colorado_floods_2013_19_verdict(ev):
    return ev.unit_verdict('colorado-floods-2013-19')

def check_florence_michael_2018_01_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-01')

def check_florence_michael_2018_01_values(ev):
    return ev.unit_values('florence-michael-2018-01')

def check_florence_michael_2018_01_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-01')

def check_florence_michael_2018_01_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-01')

def check_florence_michael_2018_02_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-02')

def check_florence_michael_2018_02_values(ev):
    return ev.unit_values('florence-michael-2018-02')

def check_florence_michael_2018_02_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-02')

def check_florence_michael_2018_02_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-02')

def check_florence_michael_2018_03_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-03')

def check_florence_michael_2018_03_values(ev):
    return ev.unit_values('florence-michael-2018-03')

def check_florence_michael_2018_03_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-03')

def check_florence_michael_2018_04_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-04')

def check_florence_michael_2018_04_values(ev):
    return ev.unit_values('florence-michael-2018-04')

def check_florence_michael_2018_04_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-04')

def check_florence_michael_2018_04_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-04')

def check_florence_michael_2018_05_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-05')

def check_florence_michael_2018_05_values(ev):
    return ev.unit_values('florence-michael-2018-05')

def check_florence_michael_2018_05_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-05')

def check_florence_michael_2018_05_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-05')

def check_florence_michael_2018_06_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-06')

def check_florence_michael_2018_06_values(ev):
    return ev.unit_values('florence-michael-2018-06')

def check_florence_michael_2018_06_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-06')

def check_florence_michael_2018_06_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-06')

def check_florence_michael_2018_07_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-07')

def check_florence_michael_2018_07_values(ev):
    return ev.unit_values('florence-michael-2018-07')

def check_florence_michael_2018_07_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-07')

def check_florence_michael_2018_08_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-08')

def check_florence_michael_2018_08_values(ev):
    return ev.unit_values('florence-michael-2018-08')

def check_florence_michael_2018_08_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-08')

def check_florence_michael_2018_08_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-08')

def check_florence_michael_2018_09_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-09')

def check_florence_michael_2018_09_values(ev):
    return ev.unit_values('florence-michael-2018-09')

def check_florence_michael_2018_09_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-09')

def check_florence_michael_2018_10_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-10')

def check_florence_michael_2018_10_values(ev):
    return ev.unit_values('florence-michael-2018-10')

def check_florence_michael_2018_10_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-10')

def check_florence_michael_2018_11_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-11')

def check_florence_michael_2018_11_values(ev):
    return ev.unit_values('florence-michael-2018-11')

def check_florence_michael_2018_11_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-11')

def check_florence_michael_2018_12_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-12')

def check_florence_michael_2018_12_values(ev):
    return ev.unit_values('florence-michael-2018-12')

def check_florence_michael_2018_12_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-12')

def check_florence_michael_2018_12_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-12')

def check_florence_michael_2018_13_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-13')

def check_florence_michael_2018_13_values(ev):
    return ev.unit_values('florence-michael-2018-13')

def check_florence_michael_2018_13_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-13')

def check_florence_michael_2018_13_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-13')

def check_florence_michael_2018_14_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-14')

def check_florence_michael_2018_14_values(ev):
    return ev.unit_values('florence-michael-2018-14')

def check_florence_michael_2018_14_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-14')

def check_florence_michael_2018_15_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-15')

def check_florence_michael_2018_15_values(ev):
    return ev.unit_values('florence-michael-2018-15')

def check_florence_michael_2018_15_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-15')

def check_florence_michael_2018_16_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-16')

def check_florence_michael_2018_16_values(ev):
    return ev.unit_values('florence-michael-2018-16')

def check_florence_michael_2018_16_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-16')

def check_florence_michael_2018_16_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-16')

def check_florence_michael_2018_17_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-17')

def check_florence_michael_2018_17_values(ev):
    return ev.unit_values('florence-michael-2018-17')

def check_florence_michael_2018_17_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-17')

def check_florence_michael_2018_17_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-17')

def check_florence_michael_2018_18_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-18')

def check_florence_michael_2018_18_values(ev):
    return ev.unit_values('florence-michael-2018-18')

def check_florence_michael_2018_18_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-18')

def check_florence_michael_2018_18_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-18')

def check_florence_michael_2018_19_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-19')

def check_florence_michael_2018_19_values(ev):
    return ev.unit_values('florence-michael-2018-19')

def check_florence_michael_2018_19_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-19')

def check_florence_michael_2018_19_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-19')

def check_florence_michael_2018_20_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-20')

def check_florence_michael_2018_20_values(ev):
    return ev.unit_values('florence-michael-2018-20')

def check_florence_michael_2018_20_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-20')

def check_florence_michael_2018_21_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-21')

def check_florence_michael_2018_21_values(ev):
    return ev.unit_values('florence-michael-2018-21')

def check_florence_michael_2018_21_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-21')

def check_florence_michael_2018_21_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-21')

def check_florence_michael_2018_22_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-22')

def check_florence_michael_2018_22_values(ev):
    return ev.unit_values('florence-michael-2018-22')

def check_florence_michael_2018_22_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-22')

def check_florence_michael_2018_22_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-22')

def check_florence_michael_2018_23_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-23')

def check_florence_michael_2018_23_values(ev):
    return ev.unit_values('florence-michael-2018-23')

def check_florence_michael_2018_23_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-23')

def check_florence_michael_2018_23_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-23')

def check_florence_michael_2018_24_grounding(ev):
    return ev.unit_grounding('florence-michael-2018-24')

def check_florence_michael_2018_24_values(ev):
    return ev.unit_values('florence-michael-2018-24')

def check_florence_michael_2018_24_verdict(ev):
    return ev.unit_verdict('florence-michael-2018-24')

def check_florence_michael_2018_24_mapping(ev):
    return ev.unit_mapping('florence-michael-2018-24')

def check_harvey_2017_01_grounding(ev):
    return ev.unit_grounding('harvey-2017-01')

def check_harvey_2017_01_values(ev):
    return ev.unit_values('harvey-2017-01')

def check_harvey_2017_01_verdict(ev):
    return ev.unit_verdict('harvey-2017-01')

def check_harvey_2017_01_mapping(ev):
    return ev.unit_mapping('harvey-2017-01')

def check_harvey_2017_02_grounding(ev):
    return ev.unit_grounding('harvey-2017-02')

def check_harvey_2017_02_values(ev):
    return ev.unit_values('harvey-2017-02')

def check_harvey_2017_02_verdict(ev):
    return ev.unit_verdict('harvey-2017-02')

def check_harvey_2017_03_grounding(ev):
    return ev.unit_grounding('harvey-2017-03')

def check_harvey_2017_03_values(ev):
    return ev.unit_values('harvey-2017-03')

def check_harvey_2017_03_verdict(ev):
    return ev.unit_verdict('harvey-2017-03')

def check_harvey_2017_03_mapping(ev):
    return ev.unit_mapping('harvey-2017-03')

def check_harvey_2017_04_grounding(ev):
    return ev.unit_grounding('harvey-2017-04')

def check_harvey_2017_04_values(ev):
    return ev.unit_values('harvey-2017-04')

def check_harvey_2017_04_verdict(ev):
    return ev.unit_verdict('harvey-2017-04')

def check_harvey_2017_05_grounding(ev):
    return ev.unit_grounding('harvey-2017-05')

def check_harvey_2017_05_values(ev):
    return ev.unit_values('harvey-2017-05')

def check_harvey_2017_05_verdict(ev):
    return ev.unit_verdict('harvey-2017-05')

def check_harvey_2017_05_mapping(ev):
    return ev.unit_mapping('harvey-2017-05')

def check_harvey_2017_06_grounding(ev):
    return ev.unit_grounding('harvey-2017-06')

def check_harvey_2017_06_values(ev):
    return ev.unit_values('harvey-2017-06')

def check_harvey_2017_06_verdict(ev):
    return ev.unit_verdict('harvey-2017-06')

def check_harvey_2017_06_mapping(ev):
    return ev.unit_mapping('harvey-2017-06')

def check_harvey_2017_07_grounding(ev):
    return ev.unit_grounding('harvey-2017-07')

def check_harvey_2017_07_values(ev):
    return ev.unit_values('harvey-2017-07')

def check_harvey_2017_07_verdict(ev):
    return ev.unit_verdict('harvey-2017-07')

def check_harvey_2017_07_mapping(ev):
    return ev.unit_mapping('harvey-2017-07')

def check_harvey_2017_08_grounding(ev):
    return ev.unit_grounding('harvey-2017-08')

def check_harvey_2017_08_values(ev):
    return ev.unit_values('harvey-2017-08')

def check_harvey_2017_08_verdict(ev):
    return ev.unit_verdict('harvey-2017-08')

def check_harvey_2017_09_grounding(ev):
    return ev.unit_grounding('harvey-2017-09')

def check_harvey_2017_09_values(ev):
    return ev.unit_values('harvey-2017-09')

def check_harvey_2017_09_verdict(ev):
    return ev.unit_verdict('harvey-2017-09')

def check_harvey_2017_09_mapping(ev):
    return ev.unit_mapping('harvey-2017-09')

def check_harvey_2017_10_grounding(ev):
    return ev.unit_grounding('harvey-2017-10')

def check_harvey_2017_10_values(ev):
    return ev.unit_values('harvey-2017-10')

def check_harvey_2017_10_verdict(ev):
    return ev.unit_verdict('harvey-2017-10')

def check_harvey_2017_11_grounding(ev):
    return ev.unit_grounding('harvey-2017-11')

def check_harvey_2017_11_values(ev):
    return ev.unit_values('harvey-2017-11')

def check_harvey_2017_11_verdict(ev):
    return ev.unit_verdict('harvey-2017-11')

def check_harvey_2017_11_mapping(ev):
    return ev.unit_mapping('harvey-2017-11')

def check_harvey_2017_12_grounding(ev):
    return ev.unit_grounding('harvey-2017-12')

def check_harvey_2017_12_values(ev):
    return ev.unit_values('harvey-2017-12')

def check_harvey_2017_12_verdict(ev):
    return ev.unit_verdict('harvey-2017-12')

def check_harvey_2017_12_mapping(ev):
    return ev.unit_mapping('harvey-2017-12')

def check_harvey_2017_13_grounding(ev):
    return ev.unit_grounding('harvey-2017-13')

def check_harvey_2017_13_values(ev):
    return ev.unit_values('harvey-2017-13')

def check_harvey_2017_13_verdict(ev):
    return ev.unit_verdict('harvey-2017-13')

def check_harvey_2017_13_mapping(ev):
    return ev.unit_mapping('harvey-2017-13')

def check_harvey_2017_14_grounding(ev):
    return ev.unit_grounding('harvey-2017-14')

def check_harvey_2017_14_values(ev):
    return ev.unit_values('harvey-2017-14')

def check_harvey_2017_14_verdict(ev):
    return ev.unit_verdict('harvey-2017-14')

def check_harvey_2017_14_mapping(ev):
    return ev.unit_mapping('harvey-2017-14')

def check_harvey_2017_15_grounding(ev):
    return ev.unit_grounding('harvey-2017-15')

def check_harvey_2017_15_values(ev):
    return ev.unit_values('harvey-2017-15')

def check_harvey_2017_15_verdict(ev):
    return ev.unit_verdict('harvey-2017-15')

def check_harvey_2017_15_mapping(ev):
    return ev.unit_mapping('harvey-2017-15')

def check_harvey_2017_16_grounding(ev):
    return ev.unit_grounding('harvey-2017-16')

def check_harvey_2017_16_values(ev):
    return ev.unit_values('harvey-2017-16')

def check_harvey_2017_16_verdict(ev):
    return ev.unit_verdict('harvey-2017-16')

def check_harvey_2017_16_mapping(ev):
    return ev.unit_mapping('harvey-2017-16')

def check_harvey_2017_17_grounding(ev):
    return ev.unit_grounding('harvey-2017-17')

def check_harvey_2017_17_values(ev):
    return ev.unit_values('harvey-2017-17')

def check_harvey_2017_17_verdict(ev):
    return ev.unit_verdict('harvey-2017-17')

def check_harvey_2017_17_mapping(ev):
    return ev.unit_mapping('harvey-2017-17')

def check_harvey_2017_18_grounding(ev):
    return ev.unit_grounding('harvey-2017-18')

def check_harvey_2017_18_values(ev):
    return ev.unit_values('harvey-2017-18')

def check_harvey_2017_18_verdict(ev):
    return ev.unit_verdict('harvey-2017-18')

def check_harvey_2017_18_mapping(ev):
    return ev.unit_mapping('harvey-2017-18')

def check_harvey_2017_19_grounding(ev):
    return ev.unit_grounding('harvey-2017-19')

def check_harvey_2017_19_values(ev):
    return ev.unit_values('harvey-2017-19')

def check_harvey_2017_19_verdict(ev):
    return ev.unit_verdict('harvey-2017-19')

def check_harvey_2017_19_mapping(ev):
    return ev.unit_mapping('harvey-2017-19')

def check_harvey_2017_20_grounding(ev):
    return ev.unit_grounding('harvey-2017-20')

def check_harvey_2017_20_values(ev):
    return ev.unit_values('harvey-2017-20')

def check_harvey_2017_20_verdict(ev):
    return ev.unit_verdict('harvey-2017-20')

def check_harvey_2017_20_mapping(ev):
    return ev.unit_mapping('harvey-2017-20')

def check_ida_2021_01_grounding(ev):
    return ev.unit_grounding('ida-2021-01')

def check_ida_2021_01_values(ev):
    return ev.unit_values('ida-2021-01')

def check_ida_2021_01_verdict(ev):
    return ev.unit_verdict('ida-2021-01')

def check_ida_2021_01_mapping(ev):
    return ev.unit_mapping('ida-2021-01')

def check_ida_2021_02_grounding(ev):
    return ev.unit_grounding('ida-2021-02')

def check_ida_2021_02_values(ev):
    return ev.unit_values('ida-2021-02')

def check_ida_2021_02_verdict(ev):
    return ev.unit_verdict('ida-2021-02')

def check_ida_2021_02_mapping(ev):
    return ev.unit_mapping('ida-2021-02')

def check_ida_2021_03_grounding(ev):
    return ev.unit_grounding('ida-2021-03')

def check_ida_2021_03_values(ev):
    return ev.unit_values('ida-2021-03')

def check_ida_2021_03_verdict(ev):
    return ev.unit_verdict('ida-2021-03')

def check_ida_2021_04_grounding(ev):
    return ev.unit_grounding('ida-2021-04')

def check_ida_2021_04_values(ev):
    return ev.unit_values('ida-2021-04')

def check_ida_2021_04_verdict(ev):
    return ev.unit_verdict('ida-2021-04')

def check_ida_2021_05_grounding(ev):
    return ev.unit_grounding('ida-2021-05')

def check_ida_2021_05_values(ev):
    return ev.unit_values('ida-2021-05')

def check_ida_2021_05_verdict(ev):
    return ev.unit_verdict('ida-2021-05')

def check_ida_2021_05_mapping(ev):
    return ev.unit_mapping('ida-2021-05')

def check_ida_2021_06_grounding(ev):
    return ev.unit_grounding('ida-2021-06')

def check_ida_2021_06_values(ev):
    return ev.unit_values('ida-2021-06')

def check_ida_2021_06_verdict(ev):
    return ev.unit_verdict('ida-2021-06')

def check_ida_2021_06_mapping(ev):
    return ev.unit_mapping('ida-2021-06')

def check_ida_2021_07_grounding(ev):
    return ev.unit_grounding('ida-2021-07')

def check_ida_2021_07_values(ev):
    return ev.unit_values('ida-2021-07')

def check_ida_2021_07_verdict(ev):
    return ev.unit_verdict('ida-2021-07')

def check_ida_2021_07_mapping(ev):
    return ev.unit_mapping('ida-2021-07')

def check_ida_2021_08_grounding(ev):
    return ev.unit_grounding('ida-2021-08')

def check_ida_2021_08_values(ev):
    return ev.unit_values('ida-2021-08')

def check_ida_2021_08_verdict(ev):
    return ev.unit_verdict('ida-2021-08')

def check_ida_2021_09_grounding(ev):
    return ev.unit_grounding('ida-2021-09')

def check_ida_2021_09_values(ev):
    return ev.unit_values('ida-2021-09')

def check_ida_2021_09_verdict(ev):
    return ev.unit_verdict('ida-2021-09')

def check_ida_2021_10_grounding(ev):
    return ev.unit_grounding('ida-2021-10')

def check_ida_2021_10_values(ev):
    return ev.unit_values('ida-2021-10')

def check_ida_2021_10_verdict(ev):
    return ev.unit_verdict('ida-2021-10')

def check_ida_2021_11_grounding(ev):
    return ev.unit_grounding('ida-2021-11')

def check_ida_2021_11_values(ev):
    return ev.unit_values('ida-2021-11')

def check_ida_2021_11_verdict(ev):
    return ev.unit_verdict('ida-2021-11')

def check_ida_2021_12_grounding(ev):
    return ev.unit_grounding('ida-2021-12')

def check_ida_2021_12_values(ev):
    return ev.unit_values('ida-2021-12')

def check_ida_2021_12_verdict(ev):
    return ev.unit_verdict('ida-2021-12')

def check_ida_2021_12_mapping(ev):
    return ev.unit_mapping('ida-2021-12')

def check_ida_2021_13_grounding(ev):
    return ev.unit_grounding('ida-2021-13')

def check_ida_2021_13_values(ev):
    return ev.unit_values('ida-2021-13')

def check_ida_2021_13_verdict(ev):
    return ev.unit_verdict('ida-2021-13')

def check_ida_2021_13_mapping(ev):
    return ev.unit_mapping('ida-2021-13')

def check_ida_2021_14_grounding(ev):
    return ev.unit_grounding('ida-2021-14')

def check_ida_2021_14_values(ev):
    return ev.unit_values('ida-2021-14')

def check_ida_2021_14_verdict(ev):
    return ev.unit_verdict('ida-2021-14')

def check_ida_2021_15_grounding(ev):
    return ev.unit_grounding('ida-2021-15')

def check_ida_2021_15_values(ev):
    return ev.unit_values('ida-2021-15')

def check_ida_2021_15_verdict(ev):
    return ev.unit_verdict('ida-2021-15')

def check_ida_2021_16_grounding(ev):
    return ev.unit_grounding('ida-2021-16')

def check_ida_2021_16_values(ev):
    return ev.unit_values('ida-2021-16')

def check_ida_2021_16_verdict(ev):
    return ev.unit_verdict('ida-2021-16')

def check_ida_2021_17_grounding(ev):
    return ev.unit_grounding('ida-2021-17')

def check_ida_2021_17_values(ev):
    return ev.unit_values('ida-2021-17')

def check_ida_2021_17_verdict(ev):
    return ev.unit_verdict('ida-2021-17')

def check_ida_2021_18_grounding(ev):
    return ev.unit_grounding('ida-2021-18')

def check_ida_2021_18_values(ev):
    return ev.unit_values('ida-2021-18')

def check_ida_2021_18_verdict(ev):
    return ev.unit_verdict('ida-2021-18')

def check_ida_2021_19_grounding(ev):
    return ev.unit_grounding('ida-2021-19')

def check_ida_2021_19_values(ev):
    return ev.unit_values('ida-2021-19')

def check_ida_2021_19_verdict(ev):
    return ev.unit_verdict('ida-2021-19')

def check_ida_2021_20_grounding(ev):
    return ev.unit_grounding('ida-2021-20')

def check_ida_2021_20_values(ev):
    return ev.unit_values('ida-2021-20')

def check_ida_2021_20_verdict(ev):
    return ev.unit_verdict('ida-2021-20')

def check_ida_2021_20_mapping(ev):
    return ev.unit_mapping('ida-2021-20')

def check_irene_2011_01_grounding(ev):
    return ev.unit_grounding('irene-2011-01')

def check_irene_2011_01_values(ev):
    return ev.unit_values('irene-2011-01')

def check_irene_2011_01_verdict(ev):
    return ev.unit_verdict('irene-2011-01')

def check_irene_2011_01_mapping(ev):
    return ev.unit_mapping('irene-2011-01')

def check_irene_2011_02_grounding(ev):
    return ev.unit_grounding('irene-2011-02')

def check_irene_2011_02_values(ev):
    return ev.unit_values('irene-2011-02')

def check_irene_2011_02_verdict(ev):
    return ev.unit_verdict('irene-2011-02')

def check_irene_2011_02_mapping(ev):
    return ev.unit_mapping('irene-2011-02')

def check_irene_2011_03_grounding(ev):
    return ev.unit_grounding('irene-2011-03')

def check_irene_2011_03_values(ev):
    return ev.unit_values('irene-2011-03')

def check_irene_2011_03_verdict(ev):
    return ev.unit_verdict('irene-2011-03')

def check_irene_2011_03_mapping(ev):
    return ev.unit_mapping('irene-2011-03')

def check_irene_2011_04_grounding(ev):
    return ev.unit_grounding('irene-2011-04')

def check_irene_2011_04_values(ev):
    return ev.unit_values('irene-2011-04')

def check_irene_2011_04_verdict(ev):
    return ev.unit_verdict('irene-2011-04')

def check_irene_2011_04_mapping(ev):
    return ev.unit_mapping('irene-2011-04')

def check_irene_2011_05_grounding(ev):
    return ev.unit_grounding('irene-2011-05')

def check_irene_2011_05_values(ev):
    return ev.unit_values('irene-2011-05')

def check_irene_2011_05_verdict(ev):
    return ev.unit_verdict('irene-2011-05')

def check_irene_2011_05_mapping(ev):
    return ev.unit_mapping('irene-2011-05')

def check_irene_2011_06_grounding(ev):
    return ev.unit_grounding('irene-2011-06')

def check_irene_2011_06_values(ev):
    return ev.unit_values('irene-2011-06')

def check_irene_2011_06_verdict(ev):
    return ev.unit_verdict('irene-2011-06')

def check_irene_2011_06_mapping(ev):
    return ev.unit_mapping('irene-2011-06')

def check_irene_2011_07_grounding(ev):
    return ev.unit_grounding('irene-2011-07')

def check_irene_2011_07_values(ev):
    return ev.unit_values('irene-2011-07')

def check_irene_2011_07_verdict(ev):
    return ev.unit_verdict('irene-2011-07')

def check_irene_2011_07_mapping(ev):
    return ev.unit_mapping('irene-2011-07')

def check_irene_2011_08_grounding(ev):
    return ev.unit_grounding('irene-2011-08')

def check_irene_2011_08_values(ev):
    return ev.unit_values('irene-2011-08')

def check_irene_2011_08_verdict(ev):
    return ev.unit_verdict('irene-2011-08')

def check_irene_2011_08_mapping(ev):
    return ev.unit_mapping('irene-2011-08')

def check_irene_2011_09_grounding(ev):
    return ev.unit_grounding('irene-2011-09')

def check_irene_2011_09_values(ev):
    return ev.unit_values('irene-2011-09')

def check_irene_2011_09_verdict(ev):
    return ev.unit_verdict('irene-2011-09')

def check_irene_2011_09_mapping(ev):
    return ev.unit_mapping('irene-2011-09')

def check_irene_2011_10_grounding(ev):
    return ev.unit_grounding('irene-2011-10')

def check_irene_2011_10_values(ev):
    return ev.unit_values('irene-2011-10')

def check_irene_2011_10_verdict(ev):
    return ev.unit_verdict('irene-2011-10')

def check_irene_2011_10_mapping(ev):
    return ev.unit_mapping('irene-2011-10')

def check_irene_2011_11_grounding(ev):
    return ev.unit_grounding('irene-2011-11')

def check_irene_2011_11_values(ev):
    return ev.unit_values('irene-2011-11')

def check_irene_2011_11_verdict(ev):
    return ev.unit_verdict('irene-2011-11')

def check_irene_2011_11_mapping(ev):
    return ev.unit_mapping('irene-2011-11')

def check_irene_2011_12_grounding(ev):
    return ev.unit_grounding('irene-2011-12')

def check_irene_2011_12_values(ev):
    return ev.unit_values('irene-2011-12')

def check_irene_2011_12_verdict(ev):
    return ev.unit_verdict('irene-2011-12')

def check_irene_2011_12_mapping(ev):
    return ev.unit_mapping('irene-2011-12')

def check_irene_2011_13_grounding(ev):
    return ev.unit_grounding('irene-2011-13')

def check_irene_2011_13_values(ev):
    return ev.unit_values('irene-2011-13')

def check_irene_2011_13_verdict(ev):
    return ev.unit_verdict('irene-2011-13')

def check_irene_2011_13_mapping(ev):
    return ev.unit_mapping('irene-2011-13')

def check_irene_2011_14_grounding(ev):
    return ev.unit_grounding('irene-2011-14')

def check_irene_2011_14_values(ev):
    return ev.unit_values('irene-2011-14')

def check_irene_2011_14_verdict(ev):
    return ev.unit_verdict('irene-2011-14')

def check_irene_2011_14_mapping(ev):
    return ev.unit_mapping('irene-2011-14')

def check_irene_2011_15_grounding(ev):
    return ev.unit_grounding('irene-2011-15')

def check_irene_2011_15_values(ev):
    return ev.unit_values('irene-2011-15')

def check_irene_2011_15_verdict(ev):
    return ev.unit_verdict('irene-2011-15')

def check_irene_2011_16_grounding(ev):
    return ev.unit_grounding('irene-2011-16')

def check_irene_2011_16_values(ev):
    return ev.unit_values('irene-2011-16')

def check_irene_2011_16_verdict(ev):
    return ev.unit_verdict('irene-2011-16')

def check_irene_2011_16_mapping(ev):
    return ev.unit_mapping('irene-2011-16')

def check_irene_2011_17_grounding(ev):
    return ev.unit_grounding('irene-2011-17')

def check_irene_2011_17_values(ev):
    return ev.unit_values('irene-2011-17')

def check_irene_2011_17_verdict(ev):
    return ev.unit_verdict('irene-2011-17')

def check_irene_2011_17_mapping(ev):
    return ev.unit_mapping('irene-2011-17')

def check_irene_2011_18_grounding(ev):
    return ev.unit_grounding('irene-2011-18')

def check_irene_2011_18_values(ev):
    return ev.unit_values('irene-2011-18')

def check_irene_2011_18_verdict(ev):
    return ev.unit_verdict('irene-2011-18')

def check_irene_2011_18_mapping(ev):
    return ev.unit_mapping('irene-2011-18')

def check_irene_2011_19_grounding(ev):
    return ev.unit_grounding('irene-2011-19')

def check_irene_2011_19_values(ev):
    return ev.unit_values('irene-2011-19')

def check_irene_2011_19_verdict(ev):
    return ev.unit_verdict('irene-2011-19')

def check_irene_2011_19_mapping(ev):
    return ev.unit_mapping('irene-2011-19')

def check_irene_2011_20_grounding(ev):
    return ev.unit_grounding('irene-2011-20')

def check_irene_2011_20_values(ev):
    return ev.unit_values('irene-2011-20')

def check_irene_2011_20_verdict(ev):
    return ev.unit_verdict('irene-2011-20')

def check_joplin_tornado_2011_01_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-01')

def check_joplin_tornado_2011_01_values(ev):
    return ev.unit_values('joplin-tornado-2011-01')

def check_joplin_tornado_2011_01_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-01')

def check_joplin_tornado_2011_01_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-01')

def check_joplin_tornado_2011_02_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-02')

def check_joplin_tornado_2011_02_values(ev):
    return ev.unit_values('joplin-tornado-2011-02')

def check_joplin_tornado_2011_02_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-02')

def check_joplin_tornado_2011_02_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-02')

def check_joplin_tornado_2011_03_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-03')

def check_joplin_tornado_2011_03_values(ev):
    return ev.unit_values('joplin-tornado-2011-03')

def check_joplin_tornado_2011_03_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-03')

def check_joplin_tornado_2011_03_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-03')

def check_joplin_tornado_2011_04_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-04')

def check_joplin_tornado_2011_04_values(ev):
    return ev.unit_values('joplin-tornado-2011-04')

def check_joplin_tornado_2011_04_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-04')

def check_joplin_tornado_2011_05_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-05')

def check_joplin_tornado_2011_05_values(ev):
    return ev.unit_values('joplin-tornado-2011-05')

def check_joplin_tornado_2011_05_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-05')

def check_joplin_tornado_2011_05_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-05')

def check_joplin_tornado_2011_06_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-06')

def check_joplin_tornado_2011_06_values(ev):
    return ev.unit_values('joplin-tornado-2011-06')

def check_joplin_tornado_2011_06_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-06')

def check_joplin_tornado_2011_07_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-07')

def check_joplin_tornado_2011_07_values(ev):
    return ev.unit_values('joplin-tornado-2011-07')

def check_joplin_tornado_2011_07_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-07')

def check_joplin_tornado_2011_07_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-07')

def check_joplin_tornado_2011_08_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-08')

def check_joplin_tornado_2011_08_values(ev):
    return ev.unit_values('joplin-tornado-2011-08')

def check_joplin_tornado_2011_08_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-08')

def check_joplin_tornado_2011_08_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-08')

def check_joplin_tornado_2011_09_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-09')

def check_joplin_tornado_2011_09_values(ev):
    return ev.unit_values('joplin-tornado-2011-09')

def check_joplin_tornado_2011_09_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-09')

def check_joplin_tornado_2011_10_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-10')

def check_joplin_tornado_2011_10_values(ev):
    return ev.unit_values('joplin-tornado-2011-10')

def check_joplin_tornado_2011_10_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-10')

def check_joplin_tornado_2011_10_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-10')

def check_joplin_tornado_2011_11_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-11')

def check_joplin_tornado_2011_11_values(ev):
    return ev.unit_values('joplin-tornado-2011-11')

def check_joplin_tornado_2011_11_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-11')

def check_joplin_tornado_2011_11_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-11')

def check_joplin_tornado_2011_12_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-12')

def check_joplin_tornado_2011_12_values(ev):
    return ev.unit_values('joplin-tornado-2011-12')

def check_joplin_tornado_2011_12_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-12')

def check_joplin_tornado_2011_12_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-12')

def check_joplin_tornado_2011_13_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-13')

def check_joplin_tornado_2011_13_values(ev):
    return ev.unit_values('joplin-tornado-2011-13')

def check_joplin_tornado_2011_13_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-13')

def check_joplin_tornado_2011_14_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-14')

def check_joplin_tornado_2011_14_values(ev):
    return ev.unit_values('joplin-tornado-2011-14')

def check_joplin_tornado_2011_14_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-14')

def check_joplin_tornado_2011_14_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-14')

def check_joplin_tornado_2011_15_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-15')

def check_joplin_tornado_2011_15_values(ev):
    return ev.unit_values('joplin-tornado-2011-15')

def check_joplin_tornado_2011_15_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-15')

def check_joplin_tornado_2011_15_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-15')

def check_joplin_tornado_2011_16_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-16')

def check_joplin_tornado_2011_16_values(ev):
    return ev.unit_values('joplin-tornado-2011-16')

def check_joplin_tornado_2011_16_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-16')

def check_joplin_tornado_2011_16_mapping(ev):
    return ev.unit_mapping('joplin-tornado-2011-16')

def check_joplin_tornado_2011_17_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-17')

def check_joplin_tornado_2011_17_values(ev):
    return ev.unit_values('joplin-tornado-2011-17')

def check_joplin_tornado_2011_17_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-17')

def check_joplin_tornado_2011_18_grounding(ev):
    return ev.unit_grounding('joplin-tornado-2011-18')

def check_joplin_tornado_2011_18_values(ev):
    return ev.unit_values('joplin-tornado-2011-18')

def check_joplin_tornado_2011_18_verdict(ev):
    return ev.unit_verdict('joplin-tornado-2011-18')

def check_matthew_2016_01_grounding(ev):
    return ev.unit_grounding('matthew-2016-01')

def check_matthew_2016_01_values(ev):
    return ev.unit_values('matthew-2016-01')

def check_matthew_2016_01_verdict(ev):
    return ev.unit_verdict('matthew-2016-01')

def check_matthew_2016_01_mapping(ev):
    return ev.unit_mapping('matthew-2016-01')

def check_matthew_2016_02_grounding(ev):
    return ev.unit_grounding('matthew-2016-02')

def check_matthew_2016_02_values(ev):
    return ev.unit_values('matthew-2016-02')

def check_matthew_2016_02_verdict(ev):
    return ev.unit_verdict('matthew-2016-02')

def check_matthew_2016_02_mapping(ev):
    return ev.unit_mapping('matthew-2016-02')

def check_matthew_2016_03_grounding(ev):
    return ev.unit_grounding('matthew-2016-03')

def check_matthew_2016_03_values(ev):
    return ev.unit_values('matthew-2016-03')

def check_matthew_2016_03_verdict(ev):
    return ev.unit_verdict('matthew-2016-03')

def check_matthew_2016_03_mapping(ev):
    return ev.unit_mapping('matthew-2016-03')

def check_matthew_2016_04_grounding(ev):
    return ev.unit_grounding('matthew-2016-04')

def check_matthew_2016_04_values(ev):
    return ev.unit_values('matthew-2016-04')

def check_matthew_2016_04_verdict(ev):
    return ev.unit_verdict('matthew-2016-04')

def check_matthew_2016_04_mapping(ev):
    return ev.unit_mapping('matthew-2016-04')

def check_matthew_2016_05_grounding(ev):
    return ev.unit_grounding('matthew-2016-05')

def check_matthew_2016_05_values(ev):
    return ev.unit_values('matthew-2016-05')

def check_matthew_2016_05_verdict(ev):
    return ev.unit_verdict('matthew-2016-05')

def check_matthew_2016_05_mapping(ev):
    return ev.unit_mapping('matthew-2016-05')

def check_matthew_2016_06_grounding(ev):
    return ev.unit_grounding('matthew-2016-06')

def check_matthew_2016_06_values(ev):
    return ev.unit_values('matthew-2016-06')

def check_matthew_2016_06_verdict(ev):
    return ev.unit_verdict('matthew-2016-06')

def check_matthew_2016_06_mapping(ev):
    return ev.unit_mapping('matthew-2016-06')

def check_matthew_2016_07_grounding(ev):
    return ev.unit_grounding('matthew-2016-07')

def check_matthew_2016_07_values(ev):
    return ev.unit_values('matthew-2016-07')

def check_matthew_2016_07_verdict(ev):
    return ev.unit_verdict('matthew-2016-07')

def check_matthew_2016_08_grounding(ev):
    return ev.unit_grounding('matthew-2016-08')

def check_matthew_2016_08_values(ev):
    return ev.unit_values('matthew-2016-08')

def check_matthew_2016_08_verdict(ev):
    return ev.unit_verdict('matthew-2016-08')

def check_matthew_2016_08_mapping(ev):
    return ev.unit_mapping('matthew-2016-08')

def check_matthew_2016_09_grounding(ev):
    return ev.unit_grounding('matthew-2016-09')

def check_matthew_2016_09_values(ev):
    return ev.unit_values('matthew-2016-09')

def check_matthew_2016_09_verdict(ev):
    return ev.unit_verdict('matthew-2016-09')

def check_matthew_2016_09_mapping(ev):
    return ev.unit_mapping('matthew-2016-09')

def check_matthew_2016_10_grounding(ev):
    return ev.unit_grounding('matthew-2016-10')

def check_matthew_2016_10_values(ev):
    return ev.unit_values('matthew-2016-10')

def check_matthew_2016_10_verdict(ev):
    return ev.unit_verdict('matthew-2016-10')

def check_matthew_2016_11_grounding(ev):
    return ev.unit_grounding('matthew-2016-11')

def check_matthew_2016_11_values(ev):
    return ev.unit_values('matthew-2016-11')

def check_matthew_2016_11_verdict(ev):
    return ev.unit_verdict('matthew-2016-11')

def check_matthew_2016_11_mapping(ev):
    return ev.unit_mapping('matthew-2016-11')

def check_matthew_2016_12_grounding(ev):
    return ev.unit_grounding('matthew-2016-12')

def check_matthew_2016_12_values(ev):
    return ev.unit_values('matthew-2016-12')

def check_matthew_2016_12_verdict(ev):
    return ev.unit_verdict('matthew-2016-12')

def check_matthew_2016_12_mapping(ev):
    return ev.unit_mapping('matthew-2016-12')

def check_matthew_2016_13_grounding(ev):
    return ev.unit_grounding('matthew-2016-13')

def check_matthew_2016_13_values(ev):
    return ev.unit_values('matthew-2016-13')

def check_matthew_2016_13_verdict(ev):
    return ev.unit_verdict('matthew-2016-13')

def check_matthew_2016_14_grounding(ev):
    return ev.unit_grounding('matthew-2016-14')

def check_matthew_2016_14_values(ev):
    return ev.unit_values('matthew-2016-14')

def check_matthew_2016_14_verdict(ev):
    return ev.unit_verdict('matthew-2016-14')

def check_matthew_2016_15_grounding(ev):
    return ev.unit_grounding('matthew-2016-15')

def check_matthew_2016_15_values(ev):
    return ev.unit_values('matthew-2016-15')

def check_matthew_2016_15_verdict(ev):
    return ev.unit_verdict('matthew-2016-15')

def check_matthew_2016_16_grounding(ev):
    return ev.unit_grounding('matthew-2016-16')

def check_matthew_2016_16_values(ev):
    return ev.unit_values('matthew-2016-16')

def check_matthew_2016_16_verdict(ev):
    return ev.unit_verdict('matthew-2016-16')

def check_matthew_2016_17_grounding(ev):
    return ev.unit_grounding('matthew-2016-17')

def check_matthew_2016_17_values(ev):
    return ev.unit_values('matthew-2016-17')

def check_matthew_2016_17_verdict(ev):
    return ev.unit_verdict('matthew-2016-17')

def check_matthew_2016_18_grounding(ev):
    return ev.unit_grounding('matthew-2016-18')

def check_matthew_2016_18_values(ev):
    return ev.unit_values('matthew-2016-18')

def check_matthew_2016_18_verdict(ev):
    return ev.unit_verdict('matthew-2016-18')

def check_matthew_2016_18_mapping(ev):
    return ev.unit_mapping('matthew-2016-18')

def check_sandy_2012_01_grounding(ev):
    return ev.unit_grounding('sandy-2012-01')

def check_sandy_2012_01_values(ev):
    return ev.unit_values('sandy-2012-01')

def check_sandy_2012_01_verdict(ev):
    return ev.unit_verdict('sandy-2012-01')

def check_sandy_2012_01_mapping(ev):
    return ev.unit_mapping('sandy-2012-01')

def check_sandy_2012_02_grounding(ev):
    return ev.unit_grounding('sandy-2012-02')

def check_sandy_2012_02_values(ev):
    return ev.unit_values('sandy-2012-02')

def check_sandy_2012_02_verdict(ev):
    return ev.unit_verdict('sandy-2012-02')

def check_sandy_2012_03_grounding(ev):
    return ev.unit_grounding('sandy-2012-03')

def check_sandy_2012_03_values(ev):
    return ev.unit_values('sandy-2012-03')

def check_sandy_2012_03_verdict(ev):
    return ev.unit_verdict('sandy-2012-03')

def check_sandy_2012_03_mapping(ev):
    return ev.unit_mapping('sandy-2012-03')

def check_sandy_2012_04_grounding(ev):
    return ev.unit_grounding('sandy-2012-04')

def check_sandy_2012_04_values(ev):
    return ev.unit_values('sandy-2012-04')

def check_sandy_2012_04_verdict(ev):
    return ev.unit_verdict('sandy-2012-04')

def check_sandy_2012_05_grounding(ev):
    return ev.unit_grounding('sandy-2012-05')

def check_sandy_2012_05_values(ev):
    return ev.unit_values('sandy-2012-05')

def check_sandy_2012_05_verdict(ev):
    return ev.unit_verdict('sandy-2012-05')

def check_sandy_2012_05_mapping(ev):
    return ev.unit_mapping('sandy-2012-05')

def check_sandy_2012_06_grounding(ev):
    return ev.unit_grounding('sandy-2012-06')

def check_sandy_2012_06_values(ev):
    return ev.unit_values('sandy-2012-06')

def check_sandy_2012_06_verdict(ev):
    return ev.unit_verdict('sandy-2012-06')

def check_sandy_2012_07_grounding(ev):
    return ev.unit_grounding('sandy-2012-07')

def check_sandy_2012_07_values(ev):
    return ev.unit_values('sandy-2012-07')

def check_sandy_2012_07_verdict(ev):
    return ev.unit_verdict('sandy-2012-07')

def check_sandy_2012_07_mapping(ev):
    return ev.unit_mapping('sandy-2012-07')

def check_sandy_2012_08_grounding(ev):
    return ev.unit_grounding('sandy-2012-08')

def check_sandy_2012_08_values(ev):
    return ev.unit_values('sandy-2012-08')

def check_sandy_2012_08_verdict(ev):
    return ev.unit_verdict('sandy-2012-08')

def check_sandy_2012_08_mapping(ev):
    return ev.unit_mapping('sandy-2012-08')

def check_sandy_2012_09_grounding(ev):
    return ev.unit_grounding('sandy-2012-09')

def check_sandy_2012_09_values(ev):
    return ev.unit_values('sandy-2012-09')

def check_sandy_2012_09_verdict(ev):
    return ev.unit_verdict('sandy-2012-09')

def check_sandy_2012_09_mapping(ev):
    return ev.unit_mapping('sandy-2012-09')

def check_sandy_2012_10_grounding(ev):
    return ev.unit_grounding('sandy-2012-10')

def check_sandy_2012_10_values(ev):
    return ev.unit_values('sandy-2012-10')

def check_sandy_2012_10_verdict(ev):
    return ev.unit_verdict('sandy-2012-10')

def check_sandy_2012_10_mapping(ev):
    return ev.unit_mapping('sandy-2012-10')

def check_sandy_2012_11_grounding(ev):
    return ev.unit_grounding('sandy-2012-11')

def check_sandy_2012_11_values(ev):
    return ev.unit_values('sandy-2012-11')

def check_sandy_2012_11_verdict(ev):
    return ev.unit_verdict('sandy-2012-11')

def check_sandy_2012_12_grounding(ev):
    return ev.unit_grounding('sandy-2012-12')

def check_sandy_2012_12_values(ev):
    return ev.unit_values('sandy-2012-12')

def check_sandy_2012_12_verdict(ev):
    return ev.unit_verdict('sandy-2012-12')

def check_sandy_2012_12_mapping(ev):
    return ev.unit_mapping('sandy-2012-12')

def check_sandy_2012_13_grounding(ev):
    return ev.unit_grounding('sandy-2012-13')

def check_sandy_2012_13_values(ev):
    return ev.unit_values('sandy-2012-13')

def check_sandy_2012_13_verdict(ev):
    return ev.unit_verdict('sandy-2012-13')

def check_sandy_2012_13_mapping(ev):
    return ev.unit_mapping('sandy-2012-13')

def check_sandy_2012_14_grounding(ev):
    return ev.unit_grounding('sandy-2012-14')

def check_sandy_2012_14_values(ev):
    return ev.unit_values('sandy-2012-14')

def check_sandy_2012_14_verdict(ev):
    return ev.unit_verdict('sandy-2012-14')

def check_sandy_2012_14_mapping(ev):
    return ev.unit_mapping('sandy-2012-14')

def check_sandy_2012_15_grounding(ev):
    return ev.unit_grounding('sandy-2012-15')

def check_sandy_2012_15_values(ev):
    return ev.unit_values('sandy-2012-15')

def check_sandy_2012_15_verdict(ev):
    return ev.unit_verdict('sandy-2012-15')

def check_sandy_2012_15_mapping(ev):
    return ev.unit_mapping('sandy-2012-15')

def check_sandy_2012_16_grounding(ev):
    return ev.unit_grounding('sandy-2012-16')

def check_sandy_2012_16_values(ev):
    return ev.unit_values('sandy-2012-16')

def check_sandy_2012_16_verdict(ev):
    return ev.unit_verdict('sandy-2012-16')

def check_sandy_2012_17_grounding(ev):
    return ev.unit_grounding('sandy-2012-17')

def check_sandy_2012_17_values(ev):
    return ev.unit_values('sandy-2012-17')

def check_sandy_2012_17_verdict(ev):
    return ev.unit_verdict('sandy-2012-17')

def check_sandy_2012_17_mapping(ev):
    return ev.unit_mapping('sandy-2012-17')

def check_sandy_2012_18_grounding(ev):
    return ev.unit_grounding('sandy-2012-18')

def check_sandy_2012_18_values(ev):
    return ev.unit_values('sandy-2012-18')

def check_sandy_2012_18_verdict(ev):
    return ev.unit_verdict('sandy-2012-18')

def check_sandy_2012_18_mapping(ev):
    return ev.unit_mapping('sandy-2012-18')

def check_sandy_2012_19_grounding(ev):
    return ev.unit_grounding('sandy-2012-19')

def check_sandy_2012_19_values(ev):
    return ev.unit_values('sandy-2012-19')

def check_sandy_2012_19_verdict(ev):
    return ev.unit_verdict('sandy-2012-19')

def check_sandy_2012_19_mapping(ev):
    return ev.unit_mapping('sandy-2012-19')

def check_sandy_2012_20_grounding(ev):
    return ev.unit_grounding('sandy-2012-20')

def check_sandy_2012_20_values(ev):
    return ev.unit_values('sandy-2012-20')

def check_sandy_2012_20_verdict(ev):
    return ev.unit_verdict('sandy-2012-20')

def check_sandy_2012_20_mapping(ev):
    return ev.unit_mapping('sandy-2012-20')

def check_sandy_2012_21_grounding(ev):
    return ev.unit_grounding('sandy-2012-21')

def check_sandy_2012_21_values(ev):
    return ev.unit_values('sandy-2012-21')

def check_sandy_2012_21_verdict(ev):
    return ev.unit_verdict('sandy-2012-21')

def check_sandy_2012_22_grounding(ev):
    return ev.unit_grounding('sandy-2012-22')

def check_sandy_2012_22_values(ev):
    return ev.unit_values('sandy-2012-22')

def check_sandy_2012_22_verdict(ev):
    return ev.unit_verdict('sandy-2012-22')

def check_sc_floods_2015_01_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-01')

def check_sc_floods_2015_01_values(ev):
    return ev.unit_values('sc-floods-2015-01')

def check_sc_floods_2015_01_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-01')

def check_sc_floods_2015_01_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-01')

def check_sc_floods_2015_02_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-02')

def check_sc_floods_2015_02_values(ev):
    return ev.unit_values('sc-floods-2015-02')

def check_sc_floods_2015_02_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-02')

def check_sc_floods_2015_03_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-03')

def check_sc_floods_2015_03_values(ev):
    return ev.unit_values('sc-floods-2015-03')

def check_sc_floods_2015_03_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-03')

def check_sc_floods_2015_03_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-03')

def check_sc_floods_2015_04_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-04')

def check_sc_floods_2015_04_values(ev):
    return ev.unit_values('sc-floods-2015-04')

def check_sc_floods_2015_04_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-04')

def check_sc_floods_2015_04_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-04')

def check_sc_floods_2015_05_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-05')

def check_sc_floods_2015_05_values(ev):
    return ev.unit_values('sc-floods-2015-05')

def check_sc_floods_2015_05_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-05')

def check_sc_floods_2015_05_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-05')

def check_sc_floods_2015_06_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-06')

def check_sc_floods_2015_06_values(ev):
    return ev.unit_values('sc-floods-2015-06')

def check_sc_floods_2015_06_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-06')

def check_sc_floods_2015_06_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-06')

def check_sc_floods_2015_07_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-07')

def check_sc_floods_2015_07_values(ev):
    return ev.unit_values('sc-floods-2015-07')

def check_sc_floods_2015_07_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-07')

def check_sc_floods_2015_08_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-08')

def check_sc_floods_2015_08_values(ev):
    return ev.unit_values('sc-floods-2015-08')

def check_sc_floods_2015_08_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-08')

def check_sc_floods_2015_08_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-08')

def check_sc_floods_2015_09_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-09')

def check_sc_floods_2015_09_values(ev):
    return ev.unit_values('sc-floods-2015-09')

def check_sc_floods_2015_09_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-09')

def check_sc_floods_2015_10_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-10')

def check_sc_floods_2015_10_values(ev):
    return ev.unit_values('sc-floods-2015-10')

def check_sc_floods_2015_10_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-10')

def check_sc_floods_2015_10_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-10')

def check_sc_floods_2015_11_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-11')

def check_sc_floods_2015_11_values(ev):
    return ev.unit_values('sc-floods-2015-11')

def check_sc_floods_2015_11_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-11')

def check_sc_floods_2015_11_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-11')

def check_sc_floods_2015_12_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-12')

def check_sc_floods_2015_12_values(ev):
    return ev.unit_values('sc-floods-2015-12')

def check_sc_floods_2015_12_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-12')

def check_sc_floods_2015_12_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-12')

def check_sc_floods_2015_13_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-13')

def check_sc_floods_2015_13_values(ev):
    return ev.unit_values('sc-floods-2015-13')

def check_sc_floods_2015_13_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-13')

def check_sc_floods_2015_14_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-14')

def check_sc_floods_2015_14_values(ev):
    return ev.unit_values('sc-floods-2015-14')

def check_sc_floods_2015_14_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-14')

def check_sc_floods_2015_14_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-14')

def check_sc_floods_2015_15_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-15')

def check_sc_floods_2015_15_values(ev):
    return ev.unit_values('sc-floods-2015-15')

def check_sc_floods_2015_15_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-15')

def check_sc_floods_2015_15_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-15')

def check_sc_floods_2015_16_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-16')

def check_sc_floods_2015_16_values(ev):
    return ev.unit_values('sc-floods-2015-16')

def check_sc_floods_2015_16_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-16')

def check_sc_floods_2015_16_mapping(ev):
    return ev.unit_mapping('sc-floods-2015-16')

def check_sc_floods_2015_17_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-17')

def check_sc_floods_2015_17_values(ev):
    return ev.unit_values('sc-floods-2015-17')

def check_sc_floods_2015_17_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-17')

def check_sc_floods_2015_18_grounding(ev):
    return ev.unit_grounding('sc-floods-2015-18')

def check_sc_floods_2015_18_values(ev):
    return ev.unit_values('sc-floods-2015-18')

def check_sc_floods_2015_18_verdict(ev):
    return ev.unit_verdict('sc-floods-2015-18')

def check_table_rock_lake_2018_01_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-01')

def check_table_rock_lake_2018_01_values(ev):
    return ev.unit_values('table-rock-lake-2018-01')

def check_table_rock_lake_2018_01_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-01')

def check_table_rock_lake_2018_01_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-01')

def check_table_rock_lake_2018_02_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-02')

def check_table_rock_lake_2018_02_values(ev):
    return ev.unit_values('table-rock-lake-2018-02')

def check_table_rock_lake_2018_02_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-02')

def check_table_rock_lake_2018_02_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-02')

def check_table_rock_lake_2018_03_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-03')

def check_table_rock_lake_2018_03_values(ev):
    return ev.unit_values('table-rock-lake-2018-03')

def check_table_rock_lake_2018_03_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-03')

def check_table_rock_lake_2018_03_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-03')

def check_table_rock_lake_2018_04_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-04')

def check_table_rock_lake_2018_04_values(ev):
    return ev.unit_values('table-rock-lake-2018-04')

def check_table_rock_lake_2018_04_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-04')

def check_table_rock_lake_2018_04_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-04')

def check_table_rock_lake_2018_05_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-05')

def check_table_rock_lake_2018_05_values(ev):
    return ev.unit_values('table-rock-lake-2018-05')

def check_table_rock_lake_2018_05_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-05')

def check_table_rock_lake_2018_05_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-05')

def check_table_rock_lake_2018_06_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-06')

def check_table_rock_lake_2018_06_values(ev):
    return ev.unit_values('table-rock-lake-2018-06')

def check_table_rock_lake_2018_06_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-06')

def check_table_rock_lake_2018_06_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-06')

def check_table_rock_lake_2018_07_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-07')

def check_table_rock_lake_2018_07_values(ev):
    return ev.unit_values('table-rock-lake-2018-07')

def check_table_rock_lake_2018_07_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-07')

def check_table_rock_lake_2018_07_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-07')

def check_table_rock_lake_2018_08_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-08')

def check_table_rock_lake_2018_08_values(ev):
    return ev.unit_values('table-rock-lake-2018-08')

def check_table_rock_lake_2018_08_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-08')

def check_table_rock_lake_2018_08_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-08')

def check_table_rock_lake_2018_09_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-09')

def check_table_rock_lake_2018_09_values(ev):
    return ev.unit_values('table-rock-lake-2018-09')

def check_table_rock_lake_2018_09_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-09')

def check_table_rock_lake_2018_09_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-09')

def check_table_rock_lake_2018_10_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-10')

def check_table_rock_lake_2018_10_values(ev):
    return ev.unit_values('table-rock-lake-2018-10')

def check_table_rock_lake_2018_10_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-10')

def check_table_rock_lake_2018_10_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-10')

def check_table_rock_lake_2018_11_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-11')

def check_table_rock_lake_2018_11_values(ev):
    return ev.unit_values('table-rock-lake-2018-11')

def check_table_rock_lake_2018_11_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-11')

def check_table_rock_lake_2018_12_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-12')

def check_table_rock_lake_2018_12_values(ev):
    return ev.unit_values('table-rock-lake-2018-12')

def check_table_rock_lake_2018_12_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-12')

def check_table_rock_lake_2018_12_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-12')

def check_table_rock_lake_2018_13_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-13')

def check_table_rock_lake_2018_13_values(ev):
    return ev.unit_values('table-rock-lake-2018-13')

def check_table_rock_lake_2018_13_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-13')

def check_table_rock_lake_2018_13_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-13')

def check_table_rock_lake_2018_14_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-14')

def check_table_rock_lake_2018_14_values(ev):
    return ev.unit_values('table-rock-lake-2018-14')

def check_table_rock_lake_2018_14_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-14')

def check_table_rock_lake_2018_14_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-14')

def check_table_rock_lake_2018_15_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-15')

def check_table_rock_lake_2018_15_values(ev):
    return ev.unit_values('table-rock-lake-2018-15')

def check_table_rock_lake_2018_15_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-15')

def check_table_rock_lake_2018_15_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-15')

def check_table_rock_lake_2018_16_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-16')

def check_table_rock_lake_2018_16_values(ev):
    return ev.unit_values('table-rock-lake-2018-16')

def check_table_rock_lake_2018_16_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-16')

def check_table_rock_lake_2018_16_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-16')

def check_table_rock_lake_2018_17_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-17')

def check_table_rock_lake_2018_17_values(ev):
    return ev.unit_values('table-rock-lake-2018-17')

def check_table_rock_lake_2018_17_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-17')

def check_table_rock_lake_2018_18_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-18')

def check_table_rock_lake_2018_18_values(ev):
    return ev.unit_values('table-rock-lake-2018-18')

def check_table_rock_lake_2018_18_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-18')

def check_table_rock_lake_2018_19_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-19')

def check_table_rock_lake_2018_19_values(ev):
    return ev.unit_values('table-rock-lake-2018-19')

def check_table_rock_lake_2018_19_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-19')

def check_table_rock_lake_2018_19_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-19')

def check_table_rock_lake_2018_20_grounding(ev):
    return ev.unit_grounding('table-rock-lake-2018-20')

def check_table_rock_lake_2018_20_values(ev):
    return ev.unit_values('table-rock-lake-2018-20')

def check_table_rock_lake_2018_20_verdict(ev):
    return ev.unit_verdict('table-rock-lake-2018-20')

def check_table_rock_lake_2018_20_mapping(ev):
    return ev.unit_mapping('table-rock-lake-2018-20')


STATIC_CHECKS = ["check_event_camp_fire_2018_records_usable", "check_event_colorado_floods_2013_records_usable", "check_event_florence_michael_2018_records_usable", "check_event_harvey_2017_records_usable", "check_event_ida_2021_records_usable", "check_event_irene_2011_records_usable", "check_event_joplin_tornado_2011_records_usable", "check_event_matthew_2016_records_usable", "check_event_sandy_2012_records_usable", "check_event_sc_floods_2015_records_usable", "check_event_table_rock_lake_2018_records_usable", "check_ledger_shape", "check_event_coverage"]
REWARD_HACKING_CHECKS = ["check_authorship_camp_fire_2018", "check_authorship_colorado_floods_2013", "check_authorship_florence_michael_2018", "check_authorship_harvey_2017", "check_authorship_ida_2021", "check_authorship_irene_2011", "check_authorship_joplin_tornado_2011", "check_authorship_matthew_2016", "check_authorship_sandy_2012", "check_authorship_sc_floods_2015", "check_authorship_table_rock_lake_2018", "check_span_distinct_camp_fire_2018", "check_span_distinct_colorado_floods_2013", "check_span_distinct_florence_michael_2018", "check_span_distinct_harvey_2017", "check_span_distinct_ida_2021", "check_span_distinct_irene_2011", "check_span_distinct_joplin_tornado_2011", "check_span_distinct_matthew_2016", "check_span_distinct_sandy_2012", "check_span_distinct_sc_floods_2015", "check_span_distinct_table_rock_lake_2018", "check_alignment_precision", "check_stated_values_in_source", "check_verdict_not_blanket", "check_ledger_agrees_with_records", "check_no_cross_event_quote_reuse", "check_document_attribution_valid", "check_mapping_present_where_claimed", "check_single_source_discipline", "check_sources_from_distinct_reports"]
PARTIAL_ORACLE_CHECKS = ["check_camp_fire_2018_01_grounding", "check_camp_fire_2018_01_values", "check_camp_fire_2018_01_verdict", "check_camp_fire_2018_01_mapping", "check_camp_fire_2018_02_grounding", "check_camp_fire_2018_02_values", "check_camp_fire_2018_02_verdict", "check_camp_fire_2018_02_mapping", "check_camp_fire_2018_03_grounding", "check_camp_fire_2018_03_values", "check_camp_fire_2018_03_verdict", "check_camp_fire_2018_03_mapping", "check_camp_fire_2018_04_grounding", "check_camp_fire_2018_04_values", "check_camp_fire_2018_04_verdict", "check_camp_fire_2018_04_mapping", "check_camp_fire_2018_05_grounding", "check_camp_fire_2018_05_values", "check_camp_fire_2018_05_verdict", "check_camp_fire_2018_05_mapping", "check_camp_fire_2018_06_grounding", "check_camp_fire_2018_06_values", "check_camp_fire_2018_06_verdict", "check_camp_fire_2018_06_mapping", "check_camp_fire_2018_07_grounding", "check_camp_fire_2018_07_values", "check_camp_fire_2018_07_verdict", "check_camp_fire_2018_08_grounding", "check_camp_fire_2018_08_values", "check_camp_fire_2018_08_verdict", "check_camp_fire_2018_08_mapping", "check_camp_fire_2018_09_grounding", "check_camp_fire_2018_09_values", "check_camp_fire_2018_09_verdict", "check_camp_fire_2018_10_grounding", "check_camp_fire_2018_10_values", "check_camp_fire_2018_10_verdict", "check_camp_fire_2018_10_mapping", "check_camp_fire_2018_11_grounding", "check_camp_fire_2018_11_values", "check_camp_fire_2018_11_verdict", "check_camp_fire_2018_12_grounding", "check_camp_fire_2018_12_values", "check_camp_fire_2018_12_verdict", "check_camp_fire_2018_12_mapping", "check_camp_fire_2018_13_grounding", "check_camp_fire_2018_13_values", "check_camp_fire_2018_13_verdict", "check_camp_fire_2018_14_grounding", "check_camp_fire_2018_14_values", "check_camp_fire_2018_14_verdict", "check_camp_fire_2018_14_mapping", "check_camp_fire_2018_15_grounding", "check_camp_fire_2018_15_values", "check_camp_fire_2018_15_verdict", "check_camp_fire_2018_15_mapping", "check_camp_fire_2018_16_grounding", "check_camp_fire_2018_16_values", "check_camp_fire_2018_16_verdict", "check_camp_fire_2018_16_mapping", "check_camp_fire_2018_17_grounding", "check_camp_fire_2018_17_values", "check_camp_fire_2018_17_verdict", "check_camp_fire_2018_17_mapping", "check_camp_fire_2018_18_grounding", "check_camp_fire_2018_18_values", "check_camp_fire_2018_18_verdict", "check_camp_fire_2018_18_mapping", "check_camp_fire_2018_19_grounding", "check_camp_fire_2018_19_values", "check_camp_fire_2018_19_verdict", "check_camp_fire_2018_19_mapping", "check_camp_fire_2018_20_grounding", "check_camp_fire_2018_20_values", "check_camp_fire_2018_20_verdict", "check_camp_fire_2018_20_mapping", "check_colorado_floods_2013_01_grounding", "check_colorado_floods_2013_01_values", "check_colorado_floods_2013_01_verdict", "check_colorado_floods_2013_01_mapping", "check_colorado_floods_2013_02_grounding", "check_colorado_floods_2013_02_values", "check_colorado_floods_2013_02_verdict", "check_colorado_floods_2013_02_mapping", "check_colorado_floods_2013_03_grounding", "check_colorado_floods_2013_03_values", "check_colorado_floods_2013_03_verdict", "check_colorado_floods_2013_04_grounding", "check_colorado_floods_2013_04_values", "check_colorado_floods_2013_04_verdict", "check_colorado_floods_2013_04_mapping", "check_colorado_floods_2013_05_grounding", "check_colorado_floods_2013_05_values", "check_colorado_floods_2013_05_verdict", "check_colorado_floods_2013_06_grounding", "check_colorado_floods_2013_06_values", "check_colorado_floods_2013_06_verdict", "check_colorado_floods_2013_07_grounding", "check_colorado_floods_2013_07_values", "check_colorado_floods_2013_07_verdict", "check_colorado_floods_2013_07_mapping", "check_colorado_floods_2013_08_grounding", "check_colorado_floods_2013_08_values", "check_colorado_floods_2013_08_verdict", "check_colorado_floods_2013_08_mapping", "check_colorado_floods_2013_09_grounding", "check_colorado_floods_2013_09_values", "check_colorado_floods_2013_09_verdict", "check_colorado_floods_2013_09_mapping", "check_colorado_floods_2013_10_grounding", "check_colorado_floods_2013_10_values", "check_colorado_floods_2013_10_verdict", "check_colorado_floods_2013_10_mapping", "check_colorado_floods_2013_11_grounding", "check_colorado_floods_2013_11_values", "check_colorado_floods_2013_11_verdict", "check_colorado_floods_2013_12_grounding", "check_colorado_floods_2013_12_values", "check_colorado_floods_2013_12_verdict", "check_colorado_floods_2013_12_mapping", "check_colorado_floods_2013_13_grounding", "check_colorado_floods_2013_13_values", "check_colorado_floods_2013_13_verdict", "check_colorado_floods_2013_13_mapping", "check_colorado_floods_2013_14_grounding", "check_colorado_floods_2013_14_values", "check_colorado_floods_2013_14_verdict", "check_colorado_floods_2013_14_mapping", "check_colorado_floods_2013_15_grounding", "check_colorado_floods_2013_15_values", "check_colorado_floods_2013_15_verdict", "check_colorado_floods_2013_15_mapping", "check_colorado_floods_2013_16_grounding", "check_colorado_floods_2013_16_values", "check_colorado_floods_2013_16_verdict", "check_colorado_floods_2013_16_mapping", "check_colorado_floods_2013_17_grounding", "check_colorado_floods_2013_17_values", "check_colorado_floods_2013_17_verdict", "check_colorado_floods_2013_17_mapping", "check_colorado_floods_2013_18_grounding", "check_colorado_floods_2013_18_values", "check_colorado_floods_2013_18_verdict", "check_colorado_floods_2013_19_grounding", "check_colorado_floods_2013_19_values", "check_colorado_floods_2013_19_verdict", "check_florence_michael_2018_01_grounding", "check_florence_michael_2018_01_values", "check_florence_michael_2018_01_verdict", "check_florence_michael_2018_01_mapping", "check_florence_michael_2018_02_grounding", "check_florence_michael_2018_02_values", "check_florence_michael_2018_02_verdict", "check_florence_michael_2018_02_mapping", "check_florence_michael_2018_03_grounding", "check_florence_michael_2018_03_values", "check_florence_michael_2018_03_verdict", "check_florence_michael_2018_04_grounding", "check_florence_michael_2018_04_values", "check_florence_michael_2018_04_verdict", "check_florence_michael_2018_04_mapping", "check_florence_michael_2018_05_grounding", "check_florence_michael_2018_05_values", "check_florence_michael_2018_05_verdict", "check_florence_michael_2018_05_mapping", "check_florence_michael_2018_06_grounding", "check_florence_michael_2018_06_values", "check_florence_michael_2018_06_verdict", "check_florence_michael_2018_06_mapping", "check_florence_michael_2018_07_grounding", "check_florence_michael_2018_07_values", "check_florence_michael_2018_07_verdict", "check_florence_michael_2018_08_grounding", "check_florence_michael_2018_08_values", "check_florence_michael_2018_08_verdict", "check_florence_michael_2018_08_mapping", "check_florence_michael_2018_09_grounding", "check_florence_michael_2018_09_values", "check_florence_michael_2018_09_verdict", "check_florence_michael_2018_10_grounding", "check_florence_michael_2018_10_values", "check_florence_michael_2018_10_verdict", "check_florence_michael_2018_11_grounding", "check_florence_michael_2018_11_values", "check_florence_michael_2018_11_verdict", "check_florence_michael_2018_12_grounding", "check_florence_michael_2018_12_values", "check_florence_michael_2018_12_verdict", "check_florence_michael_2018_12_mapping", "check_florence_michael_2018_13_grounding", "check_florence_michael_2018_13_values", "check_florence_michael_2018_13_verdict", "check_florence_michael_2018_13_mapping", "check_florence_michael_2018_14_grounding", "check_florence_michael_2018_14_values", "check_florence_michael_2018_14_verdict", "check_florence_michael_2018_15_grounding", "check_florence_michael_2018_15_values", "check_florence_michael_2018_15_verdict", "check_florence_michael_2018_16_grounding", "check_florence_michael_2018_16_values", "check_florence_michael_2018_16_verdict", "check_florence_michael_2018_16_mapping", "check_florence_michael_2018_17_grounding", "check_florence_michael_2018_17_values", "check_florence_michael_2018_17_verdict", "check_florence_michael_2018_17_mapping", "check_florence_michael_2018_18_grounding", "check_florence_michael_2018_18_values", "check_florence_michael_2018_18_verdict", "check_florence_michael_2018_18_mapping", "check_florence_michael_2018_19_grounding", "check_florence_michael_2018_19_values", "check_florence_michael_2018_19_verdict", "check_florence_michael_2018_19_mapping", "check_florence_michael_2018_20_grounding", "check_florence_michael_2018_20_values", "check_florence_michael_2018_20_verdict", "check_florence_michael_2018_21_grounding", "check_florence_michael_2018_21_values", "check_florence_michael_2018_21_verdict", "check_florence_michael_2018_21_mapping", "check_florence_michael_2018_22_grounding", "check_florence_michael_2018_22_values", "check_florence_michael_2018_22_verdict", "check_florence_michael_2018_22_mapping", "check_florence_michael_2018_23_grounding", "check_florence_michael_2018_23_values", "check_florence_michael_2018_23_verdict", "check_florence_michael_2018_23_mapping", "check_florence_michael_2018_24_grounding", "check_florence_michael_2018_24_values", "check_florence_michael_2018_24_verdict", "check_florence_michael_2018_24_mapping", "check_harvey_2017_01_grounding", "check_harvey_2017_01_values", "check_harvey_2017_01_verdict", "check_harvey_2017_01_mapping", "check_harvey_2017_02_grounding", "check_harvey_2017_02_values", "check_harvey_2017_02_verdict", "check_harvey_2017_03_grounding", "check_harvey_2017_03_values", "check_harvey_2017_03_verdict", "check_harvey_2017_03_mapping", "check_harvey_2017_04_grounding", "check_harvey_2017_04_values", "check_harvey_2017_04_verdict", "check_harvey_2017_05_grounding", "check_harvey_2017_05_values", "check_harvey_2017_05_verdict", "check_harvey_2017_05_mapping", "check_harvey_2017_06_grounding", "check_harvey_2017_06_values", "check_harvey_2017_06_verdict", "check_harvey_2017_06_mapping", "check_harvey_2017_07_grounding", "check_harvey_2017_07_values", "check_harvey_2017_07_verdict", "check_harvey_2017_07_mapping", "check_harvey_2017_08_grounding", "check_harvey_2017_08_values", "check_harvey_2017_08_verdict", "check_harvey_2017_09_grounding", "check_harvey_2017_09_values", "check_harvey_2017_09_verdict", "check_harvey_2017_09_mapping", "check_harvey_2017_10_grounding", "check_harvey_2017_10_values", "check_harvey_2017_10_verdict", "check_harvey_2017_11_grounding", "check_harvey_2017_11_values", "check_harvey_2017_11_verdict", "check_harvey_2017_11_mapping", "check_harvey_2017_12_grounding", "check_harvey_2017_12_values", "check_harvey_2017_12_verdict", "check_harvey_2017_12_mapping", "check_harvey_2017_13_grounding", "check_harvey_2017_13_values", "check_harvey_2017_13_verdict", "check_harvey_2017_13_mapping", "check_harvey_2017_14_grounding", "check_harvey_2017_14_values", "check_harvey_2017_14_verdict", "check_harvey_2017_14_mapping", "check_harvey_2017_15_grounding", "check_harvey_2017_15_values", "check_harvey_2017_15_verdict", "check_harvey_2017_15_mapping", "check_harvey_2017_16_grounding", "check_harvey_2017_16_values", "check_harvey_2017_16_verdict", "check_harvey_2017_16_mapping", "check_harvey_2017_17_grounding", "check_harvey_2017_17_values", "check_harvey_2017_17_verdict", "check_harvey_2017_17_mapping", "check_harvey_2017_18_grounding", "check_harvey_2017_18_values", "check_harvey_2017_18_verdict", "check_harvey_2017_18_mapping", "check_harvey_2017_19_grounding", "check_harvey_2017_19_values", "check_harvey_2017_19_verdict", "check_harvey_2017_19_mapping", "check_harvey_2017_20_grounding", "check_harvey_2017_20_values", "check_harvey_2017_20_verdict", "check_harvey_2017_20_mapping", "check_ida_2021_01_grounding", "check_ida_2021_01_values", "check_ida_2021_01_verdict", "check_ida_2021_01_mapping", "check_ida_2021_02_grounding", "check_ida_2021_02_values", "check_ida_2021_02_verdict", "check_ida_2021_02_mapping", "check_ida_2021_03_grounding", "check_ida_2021_03_values", "check_ida_2021_03_verdict", "check_ida_2021_04_grounding", "check_ida_2021_04_values", "check_ida_2021_04_verdict", "check_ida_2021_05_grounding", "check_ida_2021_05_values", "check_ida_2021_05_verdict", "check_ida_2021_05_mapping", "check_ida_2021_06_grounding", "check_ida_2021_06_values", "check_ida_2021_06_verdict", "check_ida_2021_06_mapping", "check_ida_2021_07_grounding", "check_ida_2021_07_values", "check_ida_2021_07_verdict", "check_ida_2021_07_mapping", "check_ida_2021_08_grounding", "check_ida_2021_08_values", "check_ida_2021_08_verdict", "check_ida_2021_09_grounding", "check_ida_2021_09_values", "check_ida_2021_09_verdict", "check_ida_2021_10_grounding", "check_ida_2021_10_values", "check_ida_2021_10_verdict", "check_ida_2021_11_grounding", "check_ida_2021_11_values", "check_ida_2021_11_verdict", "check_ida_2021_12_grounding", "check_ida_2021_12_values", "check_ida_2021_12_verdict", "check_ida_2021_12_mapping", "check_ida_2021_13_grounding", "check_ida_2021_13_values", "check_ida_2021_13_verdict", "check_ida_2021_13_mapping", "check_ida_2021_14_grounding", "check_ida_2021_14_values", "check_ida_2021_14_verdict", "check_ida_2021_15_grounding", "check_ida_2021_15_values", "check_ida_2021_15_verdict", "check_ida_2021_16_grounding", "check_ida_2021_16_values", "check_ida_2021_16_verdict", "check_ida_2021_17_grounding", "check_ida_2021_17_values", "check_ida_2021_17_verdict", "check_ida_2021_18_grounding", "check_ida_2021_18_values", "check_ida_2021_18_verdict", "check_ida_2021_19_grounding", "check_ida_2021_19_values", "check_ida_2021_19_verdict", "check_ida_2021_20_grounding", "check_ida_2021_20_values", "check_ida_2021_20_verdict", "check_ida_2021_20_mapping", "check_irene_2011_01_grounding", "check_irene_2011_01_values", "check_irene_2011_01_verdict", "check_irene_2011_01_mapping", "check_irene_2011_02_grounding", "check_irene_2011_02_values", "check_irene_2011_02_verdict", "check_irene_2011_02_mapping", "check_irene_2011_03_grounding", "check_irene_2011_03_values", "check_irene_2011_03_verdict", "check_irene_2011_03_mapping", "check_irene_2011_04_grounding", "check_irene_2011_04_values", "check_irene_2011_04_verdict", "check_irene_2011_04_mapping", "check_irene_2011_05_grounding", "check_irene_2011_05_values", "check_irene_2011_05_verdict", "check_irene_2011_05_mapping", "check_irene_2011_06_grounding", "check_irene_2011_06_values", "check_irene_2011_06_verdict", "check_irene_2011_06_mapping", "check_irene_2011_07_grounding", "check_irene_2011_07_values", "check_irene_2011_07_verdict", "check_irene_2011_07_mapping", "check_irene_2011_08_grounding", "check_irene_2011_08_values", "check_irene_2011_08_verdict", "check_irene_2011_08_mapping", "check_irene_2011_09_grounding", "check_irene_2011_09_values", "check_irene_2011_09_verdict", "check_irene_2011_09_mapping", "check_irene_2011_10_grounding", "check_irene_2011_10_values", "check_irene_2011_10_verdict", "check_irene_2011_10_mapping", "check_irene_2011_11_grounding", "check_irene_2011_11_values", "check_irene_2011_11_verdict", "check_irene_2011_11_mapping", "check_irene_2011_12_grounding", "check_irene_2011_12_values", "check_irene_2011_12_verdict", "check_irene_2011_12_mapping", "check_irene_2011_13_grounding", "check_irene_2011_13_values", "check_irene_2011_13_verdict", "check_irene_2011_13_mapping", "check_irene_2011_14_grounding", "check_irene_2011_14_values", "check_irene_2011_14_verdict", "check_irene_2011_14_mapping", "check_irene_2011_15_grounding", "check_irene_2011_15_values", "check_irene_2011_15_verdict", "check_irene_2011_16_grounding", "check_irene_2011_16_values", "check_irene_2011_16_verdict", "check_irene_2011_16_mapping", "check_irene_2011_17_grounding", "check_irene_2011_17_values", "check_irene_2011_17_verdict", "check_irene_2011_17_mapping", "check_irene_2011_18_grounding", "check_irene_2011_18_values", "check_irene_2011_18_verdict", "check_irene_2011_18_mapping", "check_irene_2011_19_grounding", "check_irene_2011_19_values", "check_irene_2011_19_verdict", "check_irene_2011_19_mapping", "check_irene_2011_20_grounding", "check_irene_2011_20_values", "check_irene_2011_20_verdict", "check_joplin_tornado_2011_01_grounding", "check_joplin_tornado_2011_01_values", "check_joplin_tornado_2011_01_verdict", "check_joplin_tornado_2011_01_mapping", "check_joplin_tornado_2011_02_grounding", "check_joplin_tornado_2011_02_values", "check_joplin_tornado_2011_02_verdict", "check_joplin_tornado_2011_02_mapping", "check_joplin_tornado_2011_03_grounding", "check_joplin_tornado_2011_03_values", "check_joplin_tornado_2011_03_verdict", "check_joplin_tornado_2011_03_mapping", "check_joplin_tornado_2011_04_grounding", "check_joplin_tornado_2011_04_values", "check_joplin_tornado_2011_04_verdict", "check_joplin_tornado_2011_05_grounding", "check_joplin_tornado_2011_05_values", "check_joplin_tornado_2011_05_verdict", "check_joplin_tornado_2011_05_mapping", "check_joplin_tornado_2011_06_grounding", "check_joplin_tornado_2011_06_values", "check_joplin_tornado_2011_06_verdict", "check_joplin_tornado_2011_07_grounding", "check_joplin_tornado_2011_07_values", "check_joplin_tornado_2011_07_verdict", "check_joplin_tornado_2011_07_mapping", "check_joplin_tornado_2011_08_grounding", "check_joplin_tornado_2011_08_values", "check_joplin_tornado_2011_08_verdict", "check_joplin_tornado_2011_08_mapping", "check_joplin_tornado_2011_09_grounding", "check_joplin_tornado_2011_09_values", "check_joplin_tornado_2011_09_verdict", "check_joplin_tornado_2011_10_grounding", "check_joplin_tornado_2011_10_values", "check_joplin_tornado_2011_10_verdict", "check_joplin_tornado_2011_10_mapping", "check_joplin_tornado_2011_11_grounding", "check_joplin_tornado_2011_11_values", "check_joplin_tornado_2011_11_verdict", "check_joplin_tornado_2011_11_mapping", "check_joplin_tornado_2011_12_grounding", "check_joplin_tornado_2011_12_values", "check_joplin_tornado_2011_12_verdict", "check_joplin_tornado_2011_12_mapping", "check_joplin_tornado_2011_13_grounding", "check_joplin_tornado_2011_13_values", "check_joplin_tornado_2011_13_verdict", "check_joplin_tornado_2011_14_grounding", "check_joplin_tornado_2011_14_values", "check_joplin_tornado_2011_14_verdict", "check_joplin_tornado_2011_14_mapping", "check_joplin_tornado_2011_15_grounding", "check_joplin_tornado_2011_15_values", "check_joplin_tornado_2011_15_verdict", "check_joplin_tornado_2011_15_mapping", "check_joplin_tornado_2011_16_grounding", "check_joplin_tornado_2011_16_values", "check_joplin_tornado_2011_16_verdict", "check_joplin_tornado_2011_16_mapping", "check_joplin_tornado_2011_17_grounding", "check_joplin_tornado_2011_17_values", "check_joplin_tornado_2011_17_verdict", "check_joplin_tornado_2011_18_grounding", "check_joplin_tornado_2011_18_values", "check_joplin_tornado_2011_18_verdict", "check_matthew_2016_01_grounding", "check_matthew_2016_01_values", "check_matthew_2016_01_verdict", "check_matthew_2016_01_mapping", "check_matthew_2016_02_grounding", "check_matthew_2016_02_values", "check_matthew_2016_02_verdict", "check_matthew_2016_02_mapping", "check_matthew_2016_03_grounding", "check_matthew_2016_03_values", "check_matthew_2016_03_verdict", "check_matthew_2016_03_mapping", "check_matthew_2016_04_grounding", "check_matthew_2016_04_values", "check_matthew_2016_04_verdict", "check_matthew_2016_04_mapping", "check_matthew_2016_05_grounding", "check_matthew_2016_05_values", "check_matthew_2016_05_verdict", "check_matthew_2016_05_mapping", "check_matthew_2016_06_grounding", "check_matthew_2016_06_values", "check_matthew_2016_06_verdict", "check_matthew_2016_06_mapping", "check_matthew_2016_07_grounding", "check_matthew_2016_07_values", "check_matthew_2016_07_verdict", "check_matthew_2016_08_grounding", "check_matthew_2016_08_values", "check_matthew_2016_08_verdict", "check_matthew_2016_08_mapping", "check_matthew_2016_09_grounding", "check_matthew_2016_09_values", "check_matthew_2016_09_verdict", "check_matthew_2016_09_mapping", "check_matthew_2016_10_grounding", "check_matthew_2016_10_values", "check_matthew_2016_10_verdict", "check_matthew_2016_11_grounding", "check_matthew_2016_11_values", "check_matthew_2016_11_verdict", "check_matthew_2016_11_mapping", "check_matthew_2016_12_grounding", "check_matthew_2016_12_values", "check_matthew_2016_12_verdict", "check_matthew_2016_12_mapping", "check_matthew_2016_13_grounding", "check_matthew_2016_13_values", "check_matthew_2016_13_verdict", "check_matthew_2016_14_grounding", "check_matthew_2016_14_values", "check_matthew_2016_14_verdict", "check_matthew_2016_15_grounding", "check_matthew_2016_15_values", "check_matthew_2016_15_verdict", "check_matthew_2016_16_grounding", "check_matthew_2016_16_values", "check_matthew_2016_16_verdict", "check_matthew_2016_17_grounding", "check_matthew_2016_17_values", "check_matthew_2016_17_verdict", "check_matthew_2016_18_grounding", "check_matthew_2016_18_values", "check_matthew_2016_18_verdict", "check_matthew_2016_18_mapping", "check_sandy_2012_01_grounding", "check_sandy_2012_01_values", "check_sandy_2012_01_verdict", "check_sandy_2012_01_mapping", "check_sandy_2012_02_grounding", "check_sandy_2012_02_values", "check_sandy_2012_02_verdict", "check_sandy_2012_03_grounding", "check_sandy_2012_03_values", "check_sandy_2012_03_verdict", "check_sandy_2012_03_mapping", "check_sandy_2012_04_grounding", "check_sandy_2012_04_values", "check_sandy_2012_04_verdict", "check_sandy_2012_05_grounding", "check_sandy_2012_05_values", "check_sandy_2012_05_verdict", "check_sandy_2012_05_mapping", "check_sandy_2012_06_grounding", "check_sandy_2012_06_values", "check_sandy_2012_06_verdict", "check_sandy_2012_07_grounding", "check_sandy_2012_07_values", "check_sandy_2012_07_verdict", "check_sandy_2012_07_mapping", "check_sandy_2012_08_grounding", "check_sandy_2012_08_values", "check_sandy_2012_08_verdict", "check_sandy_2012_08_mapping", "check_sandy_2012_09_grounding", "check_sandy_2012_09_values", "check_sandy_2012_09_verdict", "check_sandy_2012_09_mapping", "check_sandy_2012_10_grounding", "check_sandy_2012_10_values", "check_sandy_2012_10_verdict", "check_sandy_2012_10_mapping", "check_sandy_2012_11_grounding", "check_sandy_2012_11_values", "check_sandy_2012_11_verdict", "check_sandy_2012_12_grounding", "check_sandy_2012_12_values", "check_sandy_2012_12_verdict", "check_sandy_2012_12_mapping", "check_sandy_2012_13_grounding", "check_sandy_2012_13_values", "check_sandy_2012_13_verdict", "check_sandy_2012_13_mapping", "check_sandy_2012_14_grounding", "check_sandy_2012_14_values", "check_sandy_2012_14_verdict", "check_sandy_2012_14_mapping", "check_sandy_2012_15_grounding", "check_sandy_2012_15_values", "check_sandy_2012_15_verdict", "check_sandy_2012_15_mapping", "check_sandy_2012_16_grounding", "check_sandy_2012_16_values", "check_sandy_2012_16_verdict", "check_sandy_2012_17_grounding", "check_sandy_2012_17_values", "check_sandy_2012_17_verdict", "check_sandy_2012_17_mapping", "check_sandy_2012_18_grounding", "check_sandy_2012_18_values", "check_sandy_2012_18_verdict", "check_sandy_2012_18_mapping", "check_sandy_2012_19_grounding", "check_sandy_2012_19_values", "check_sandy_2012_19_verdict", "check_sandy_2012_19_mapping", "check_sandy_2012_20_grounding", "check_sandy_2012_20_values", "check_sandy_2012_20_verdict", "check_sandy_2012_20_mapping", "check_sandy_2012_21_grounding", "check_sandy_2012_21_values", "check_sandy_2012_21_verdict", "check_sandy_2012_22_grounding", "check_sandy_2012_22_values", "check_sandy_2012_22_verdict", "check_sc_floods_2015_01_grounding", "check_sc_floods_2015_01_values", "check_sc_floods_2015_01_verdict", "check_sc_floods_2015_01_mapping", "check_sc_floods_2015_02_grounding", "check_sc_floods_2015_02_values", "check_sc_floods_2015_02_verdict", "check_sc_floods_2015_03_grounding", "check_sc_floods_2015_03_values", "check_sc_floods_2015_03_verdict", "check_sc_floods_2015_03_mapping", "check_sc_floods_2015_04_grounding", "check_sc_floods_2015_04_values", "check_sc_floods_2015_04_verdict", "check_sc_floods_2015_04_mapping", "check_sc_floods_2015_05_grounding", "check_sc_floods_2015_05_values", "check_sc_floods_2015_05_verdict", "check_sc_floods_2015_05_mapping", "check_sc_floods_2015_06_grounding", "check_sc_floods_2015_06_values", "check_sc_floods_2015_06_verdict", "check_sc_floods_2015_06_mapping", "check_sc_floods_2015_07_grounding", "check_sc_floods_2015_07_values", "check_sc_floods_2015_07_verdict", "check_sc_floods_2015_08_grounding", "check_sc_floods_2015_08_values", "check_sc_floods_2015_08_verdict", "check_sc_floods_2015_08_mapping", "check_sc_floods_2015_09_grounding", "check_sc_floods_2015_09_values", "check_sc_floods_2015_09_verdict", "check_sc_floods_2015_10_grounding", "check_sc_floods_2015_10_values", "check_sc_floods_2015_10_verdict", "check_sc_floods_2015_10_mapping", "check_sc_floods_2015_11_grounding", "check_sc_floods_2015_11_values", "check_sc_floods_2015_11_verdict", "check_sc_floods_2015_11_mapping", "check_sc_floods_2015_12_grounding", "check_sc_floods_2015_12_values", "check_sc_floods_2015_12_verdict", "check_sc_floods_2015_12_mapping", "check_sc_floods_2015_13_grounding", "check_sc_floods_2015_13_values", "check_sc_floods_2015_13_verdict", "check_sc_floods_2015_14_grounding", "check_sc_floods_2015_14_values", "check_sc_floods_2015_14_verdict", "check_sc_floods_2015_14_mapping", "check_sc_floods_2015_15_grounding", "check_sc_floods_2015_15_values", "check_sc_floods_2015_15_verdict", "check_sc_floods_2015_15_mapping", "check_sc_floods_2015_16_grounding", "check_sc_floods_2015_16_values", "check_sc_floods_2015_16_verdict", "check_sc_floods_2015_16_mapping", "check_sc_floods_2015_17_grounding", "check_sc_floods_2015_17_values", "check_sc_floods_2015_17_verdict", "check_sc_floods_2015_18_grounding", "check_sc_floods_2015_18_values", "check_sc_floods_2015_18_verdict", "check_table_rock_lake_2018_01_grounding", "check_table_rock_lake_2018_01_values", "check_table_rock_lake_2018_01_verdict", "check_table_rock_lake_2018_01_mapping", "check_table_rock_lake_2018_02_grounding", "check_table_rock_lake_2018_02_values", "check_table_rock_lake_2018_02_verdict", "check_table_rock_lake_2018_02_mapping", "check_table_rock_lake_2018_03_grounding", "check_table_rock_lake_2018_03_values", "check_table_rock_lake_2018_03_verdict", "check_table_rock_lake_2018_03_mapping", "check_table_rock_lake_2018_04_grounding", "check_table_rock_lake_2018_04_values", "check_table_rock_lake_2018_04_verdict", "check_table_rock_lake_2018_04_mapping", "check_table_rock_lake_2018_05_grounding", "check_table_rock_lake_2018_05_values", "check_table_rock_lake_2018_05_verdict", "check_table_rock_lake_2018_05_mapping", "check_table_rock_lake_2018_06_grounding", "check_table_rock_lake_2018_06_values", "check_table_rock_lake_2018_06_verdict", "check_table_rock_lake_2018_06_mapping", "check_table_rock_lake_2018_07_grounding", "check_table_rock_lake_2018_07_values", "check_table_rock_lake_2018_07_verdict", "check_table_rock_lake_2018_07_mapping", "check_table_rock_lake_2018_08_grounding", "check_table_rock_lake_2018_08_values", "check_table_rock_lake_2018_08_verdict", "check_table_rock_lake_2018_08_mapping", "check_table_rock_lake_2018_09_grounding", "check_table_rock_lake_2018_09_values", "check_table_rock_lake_2018_09_verdict", "check_table_rock_lake_2018_09_mapping", "check_table_rock_lake_2018_10_grounding", "check_table_rock_lake_2018_10_values", "check_table_rock_lake_2018_10_verdict", "check_table_rock_lake_2018_10_mapping", "check_table_rock_lake_2018_11_grounding", "check_table_rock_lake_2018_11_values", "check_table_rock_lake_2018_11_verdict", "check_table_rock_lake_2018_12_grounding", "check_table_rock_lake_2018_12_values", "check_table_rock_lake_2018_12_verdict", "check_table_rock_lake_2018_12_mapping", "check_table_rock_lake_2018_13_grounding", "check_table_rock_lake_2018_13_values", "check_table_rock_lake_2018_13_verdict", "check_table_rock_lake_2018_13_mapping", "check_table_rock_lake_2018_14_grounding", "check_table_rock_lake_2018_14_values", "check_table_rock_lake_2018_14_verdict", "check_table_rock_lake_2018_14_mapping", "check_table_rock_lake_2018_15_grounding", "check_table_rock_lake_2018_15_values", "check_table_rock_lake_2018_15_verdict", "check_table_rock_lake_2018_15_mapping", "check_table_rock_lake_2018_16_grounding", "check_table_rock_lake_2018_16_values", "check_table_rock_lake_2018_16_verdict", "check_table_rock_lake_2018_16_mapping", "check_table_rock_lake_2018_17_grounding", "check_table_rock_lake_2018_17_values", "check_table_rock_lake_2018_17_verdict", "check_table_rock_lake_2018_18_grounding", "check_table_rock_lake_2018_18_values", "check_table_rock_lake_2018_18_verdict", "check_table_rock_lake_2018_19_grounding", "check_table_rock_lake_2018_19_values", "check_table_rock_lake_2018_19_verdict", "check_table_rock_lake_2018_19_mapping", "check_table_rock_lake_2018_20_grounding", "check_table_rock_lake_2018_20_values", "check_table_rock_lake_2018_20_verdict", "check_table_rock_lake_2018_20_mapping"]


def run_group(ev, names, per_check):
    total = 0.0
    for name in names:
        try:
            value = bounded_value(globals()[name](ev))
        except RuntimeError:
            raise
        except Exception:
            value = 0.0
        per_check[name] = value
        total += value
    return share(total, len(names))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    per_check = {}
    try:
        ev = load_evaluator()
        static = run_group(ev, STATIC_CHECKS, per_check)
        hacking = run_group(ev, REWARD_HACKING_CHECKS, per_check)
        oracle = run_group(ev, PARTIAL_ORACLE_CHECKS, per_check)
        infra, error = False, None
    except Exception as exc:
        static = hacking = oracle = 0.0
        infra, error = True, repr(exc)
        ev = None

    reward = (static * 1 + hacking * 2 + oracle * 3) / 6
    content = share(hacking * 2 + oracle * 3, 5)
    payload = {
        "reward": round(reward, 6),
        "total_static_check_score": round(static, 6),
        "total_reward_hacking_check_score": round(hacking, 6),
        "total_partial_oracle_check_score": round(oracle, 6),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    with open(REWARD_TXT, "w", encoding="utf-8") as fh:
        print("%.6f" % reward, file=fh)
    details = {"per_check": per_check,
               "content_score": round(content, 6),
               "structural_score": round(static, 6),
               "infrastructure_failure": infra}
    if error:
        details["error"] = error
    if ev is not None:
        details["aligned_units"] = len(ev.aligned)
        details["key_units"] = len(ev.key)
        details["submitted_units"] = sum(len(v) for v in ev.submitted.values())
        details["events_with_records"] = sorted(e for e, v in ev.submitted.items() if v)
        details["parse_errors"] = ev.parse_errors
        details["unresolved_vocabulary"] = ev.notes
    with open(DETAILS, "w", encoding="utf-8") as fh:
        json.dump(details, fh, indent=1)

    print("total_static_check_score: %.6f" % static)
    print("total_reward_hacking_check_score: %.6f" % hacking)
    print("total_partial_oracle_check_score: %.6f" % oracle)
    print("content_score: %.6f" % content)
    print("structural_score: %.6f" % static)
    print("infrastructure_failure: %s" % infra)
    print("reward: %.6f" % reward)
    if ev is not None:
        print("aligned_units: %d of %d key units" % (len(ev.aligned), len(ev.key)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

