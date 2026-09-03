#!/usr/bin/env python3
import csv, json, os, pathlib, re, sys, unicodedata

RECORDS = pathlib.Path("/logs/agent/claim_records")
MATRIX = pathlib.Path("/logs/agent/attribution_matrix.csv")
VENDOR = pathlib.Path(__file__).parent / "test_logic" / "vendor"
KEYFILE = pathlib.Path(__file__).parent / "test_logic" / "key.json"
REWARD_JSON = "/logs/verifier/reward.json"
REWARD_TXT = "/logs/verifier/reward.txt"
OUTDIR = pathlib.Path(REWARD_JSON).parent
MIN_QUOTE_WORDS = 10
MAX_QUOTE_WORDS = 120
MIN_KEY_OVERLAP = 0.5
MIN_SPAN_FRACTION = 0.5
COVERAGE_LEVELS = 2
STOPWORDS = set("the a an of to in and that on for with as by it is was were be been are this at or "
                "which would from their its had has have not they he she we i you but if than then so "
                "such these those there some more most other about may might can could should also "
                "into over under between during after before our us them will do does did being very "
                "much many few".split())


def content_words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower())
            if w not in STOPWORDS and len(w) > 3}


def norm(s):
    s = unicodedata.normalize("NFKC", str(s))
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", " ").replace("\u2013", " ").replace("\u2010", "-")
    s = s.replace("-", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def _surname(raw):
    if not isinstance(raw, str) or not raw.strip():
        return ""
    tok = raw.strip().upper().split()[-1]
    return "".join(ch for ch in tok if ch.isalpha() or ch in "'-")


class Evidence:

    def __init__(self):
        self.key = json.loads(KEYFILE.read_text())
        self.speaker_text = {}
        for f in sorted(VENDOR.glob("*.json")):
            self.speaker_text[f.stem] = json.loads(f.read_text())
        self.records = {}
        self.parse_error = {}
        if RECORDS.is_dir():
            for f in sorted(RECORDS.glob("*.json")):
                try:
                    self.records[f.stem] = json.loads(f.read_text())
                except Exception as exc:
                    self.parse_error[f.stem] = repr(exc)
        self.matrix = self._load_matrix()
        self._credit = {}
        self._quote_use = {}
        self._key_reuse = {}
        for cid, v in self.key.items():
            for field in ("roster", "counterpoints"):
                for e in v[field]:
                    self._key_reuse.setdefault(self._shingle(e["quote"]), set()).add(cid)
        self._index_quotes()

    def _load_matrix(self):
        if not MATRIX.is_file():
            return None
        try:
            with MATRIX.open() as fh:
                return list(csv.reader(fh))
        except Exception:
            return None

    def _entries(self, claim_id, field):
        rec = self.records.get(claim_id)
        if not isinstance(rec, dict):
            return []
        vals = rec.get(field)
        if not isinstance(vals, list):
            return []
        out = []
        for e in vals:
            if isinstance(e, dict):
                sp, q = e.get("speaker"), e.get("quote")
                if isinstance(sp, str) and isinstance(q, str):
                    out.append((_surname(sp), q))
        return out

    def _shingle(self, q):
        words = [w for w in norm(q).split() if w not in STOPWORDS and len(w) > 3]
        return " ".join(words[:8])

    def _index_quotes(self):
        for claim_id in self.key:
            for field in ("roster", "counterpoints"):
                for sp, q in self._entries(claim_id, field):
                    self._quote_use.setdefault(self._shingle(q), set()).add(claim_id)

    def meeting_of(self, claim_id):
        return claim_id.split("-")[0]

    def valid_quote(self, claim_id, speaker, quote, field):
        q = norm(quote)
        if not MIN_QUOTE_WORDS <= len(q.split()) <= MAX_QUOTE_WORDS:
            return False
        shingle = self._shingle(q)
        allowed_reuse = len(self._key_reuse.get(shingle, ()))
        if allowed_reuse < 1:
            allowed_reuse = 1
        if len(self._quote_use.get(shingle, ())) > allowed_reuse:
            return False
        text = self.speaker_text.get(self.meeting_of(claim_id), {}).get(speaker)
        if not text:
            return False
        spans = [e["pos"] for e in self.key[claim_id][field] if e["speaker"] == speaker]
        if not spans:
            return False
        submitted = content_words(q)
        for e in self.key[claim_id][field]:
            if e["speaker"] != speaker:
                continue
            keyed = content_words(e["quote"])
            if not keyed or not submitted:
                continue
            shared = len(submitted & keyed)
            smaller = len(keyed)
            if len(submitted) < smaller:
                smaller = len(submitted)
            if shared / smaller < MIN_KEY_OVERLAP:
                continue
            kq = norm(e["quote"])
            k0, k1 = e["pos"], e["pos"] + len(kq)
            shorter = len(kq)
            if len(q) < shorter:
                shorter = len(q)
            start = text.find(q)
            while start >= 0:
                lo = start
                if k0 > lo:
                    lo = k0
                hi = start + len(q)
                if k1 < hi:
                    hi = k1
                if shorter and (hi - lo) / shorter >= MIN_SPAN_FRACTION:
                    return True
                start = text.find(q, start + 1)
        return False

    def credited(self, claim_id, field):
        ck = (claim_id, field)
        if ck not in self._credit:
            got = set()
            for sp, q in self._entries(claim_id, field):
                if self.valid_quote(claim_id, sp, q, field):
                    got.add(sp)
            self._credit[ck] = got
        return self._credit[ck]

    def needed_at(self, claim_id, level):
        n = len({e["speaker"] for e in self.key[claim_id]["roster"]
                 if e["tier"] == "core"})
        if n < 1:
            n = len({e["speaker"] for e in self.key[claim_id]["roster"]})
        need = (n * level + COVERAGE_LEVELS - 1) // COVERAGE_LEVELS
        if need < 1:
            need = 1
        return need

    def covered(self, claim_id, level):
        if len(self.credited(claim_id, "roster")) < self.needed_at(claim_id, level):
            return False
        if self.key[claim_id]["counterpoints"]:
            return bool(self.credited(claim_id, "counterpoints"))
        return True

    def authored(self, claim_id):
        return self.covered(claim_id, 1)

    def allowed(self, claim_id, field):
        return {e["speaker"] for e in self.key[claim_id][field]}

    def rostered(self, claim_id, field):
        return {sp for sp, _ in self._entries(claim_id, field)}

    def record_shape_ok(self, claim_id, level):
        rec = self.records.get(claim_id)
        if not isinstance(rec, dict) or claim_id in self.parse_error:
            return False
        if str(rec.get("claim_id", "")).strip() != claim_id:
            return False
        for field in ("roster", "counterpoints"):
            if not isinstance(rec.get(field), list):
                return False
        want = "%s-%s-%s" % (claim_id[:4], claim_id[4:6], claim_id[6:8])
        if str(rec.get("meeting_date", "")).strip() != want:
            return False
        return self.covered(claim_id, level) and self.matrix_agrees(claim_id)

    def no_foreign_speaker(self, claim_id, level):
        if not self.covered(claim_id, level):
            return False
        for field in ("roster", "counterpoints"):
            if self.rostered(claim_id, field) - self.allowed(claim_id, field):
                return False
        return True

    def no_padded_entries(self, claim_id, level):
        if not self.covered(claim_id, level):
            return False
        for field in ("roster", "counterpoints"):
            entries = self._entries(claim_id, field)
            speakers = [sp for sp, _ in entries]
            if len(speakers) != len(set(speakers)):
                return False
        return True

    def matrix_agrees(self, claim_id):
        if not self.authored(claim_id) or not self.matrix or len(self.matrix) < 2:
            return False
        header = [_surname(c) for c in self.matrix[0]]
        for row in self.matrix[1:]:
            if not row or row[0].strip() != claim_id:
                continue
            marked = {header[i] for i, cell in enumerate(row)
                      if 0 < i < len(header)
                      and cell.strip().lower() not in ("", "0", "0.0", "no", "n", "false", "f", "-")}
            if marked - self.allowed(claim_id, "roster"):
                return False
            return marked == self.rostered(claim_id, "roster")
        return False

    def no_invented_records(self, meeting):
        want = {c for c in self.key if c.startswith(meeting)}
        if not any(self.authored(c) for c in want):
            return False
        got = {f.stem for f in RECORDS.glob("*.json")} if RECORDS.is_dir() else set()
        return not any(g.startswith(meeting) and g not in want for g in got)

    def no_orphan_records(self):
        if not any(self.authored(c) for c in self.key):
            return False
        got = {f.stem for f in RECORDS.glob("*.json")} if RECORDS.is_dir() else set()
        return not (got - set(self.key))

    def matrix_matches_meeting(self, meeting):
        claims = [c for c in self.key if c.startswith(meeting)]
        if not any(self.authored(c) for c in claims):
            return False
        return all(self.matrix_agrees(c) for c in claims)

    def counter_speaker_found(self, claim_id, speaker):
        return speaker in self.credited(claim_id, "counterpoints")

    def roster_speaker_found(self, claim_id, speaker):
        return speaker in self.credited(claim_id, "roster")


ev = None

def check_static_record_l1_20200129_01():
    return ev.record_shape_ok("20200129-01", 1)

def check_static_record_l2_20200129_01():
    return ev.record_shape_ok("20200129-01", 2)

def check_rh_foreign_l1_20200129_01():
    return ev.no_foreign_speaker("20200129-01", 1)

def check_rh_foreign_l2_20200129_01():
    return ev.no_foreign_speaker("20200129-01", 2)

def check_rh_padding_l1_20200129_01():
    return ev.no_padded_entries("20200129-01", 1)

def check_rh_padding_l2_20200129_01():
    return ev.no_padded_entries("20200129-01", 2)

def check_po_roster_20200129_01_POWELL():
    return ev.roster_speaker_found("20200129-01", "POWELL")

def check_po_roster_20200129_01_KASHKARI():
    return ev.roster_speaker_found("20200129-01", "KASHKARI")

def check_po_roster_20200129_01_CLARIDA():
    return ev.roster_speaker_found("20200129-01", "CLARIDA")

def check_po_roster_20200129_01_MESTER():
    return ev.roster_speaker_found("20200129-01", "MESTER")

def check_po_roster_20200129_01_ROSENGREN():
    return ev.roster_speaker_found("20200129-01", "ROSENGREN")

def check_po_roster_20200129_01_BOWMAN():
    return ev.roster_speaker_found("20200129-01", "BOWMAN")

def check_po_counter_20200129_01_BULLARD():
    return ev.counter_speaker_found("20200129-01", "BULLARD")

def check_po_counter_20200129_01_BOSTIC():
    return ev.counter_speaker_found("20200129-01", "BOSTIC")

def check_po_counter_20200129_01_ROSENGREN():
    return ev.counter_speaker_found("20200129-01", "ROSENGREN")

def check_po_counter_20200129_01_BRAINARD():
    return ev.counter_speaker_found("20200129-01", "BRAINARD")

def check_static_record_l1_20200129_02():
    return ev.record_shape_ok("20200129-02", 1)

def check_static_record_l2_20200129_02():
    return ev.record_shape_ok("20200129-02", 2)

def check_rh_foreign_l1_20200129_02():
    return ev.no_foreign_speaker("20200129-02", 1)

def check_rh_foreign_l2_20200129_02():
    return ev.no_foreign_speaker("20200129-02", 2)

def check_rh_padding_l1_20200129_02():
    return ev.no_padded_entries("20200129-02", 1)

def check_rh_padding_l2_20200129_02():
    return ev.no_padded_entries("20200129-02", 2)

def check_po_roster_20200129_02_QUARLES():
    return ev.roster_speaker_found("20200129-02", "QUARLES")

def check_po_roster_20200129_02_BOWMAN():
    return ev.roster_speaker_found("20200129-02", "BOWMAN")

def check_po_roster_20200129_02_EVANS():
    return ev.roster_speaker_found("20200129-02", "EVANS")

def check_po_counter_20200129_02_BOSTIC():
    return ev.counter_speaker_found("20200129-02", "BOSTIC")

def check_po_counter_20200129_02_ROSENGREN():
    return ev.counter_speaker_found("20200129-02", "ROSENGREN")

def check_po_counter_20200129_02_GEORGE():
    return ev.counter_speaker_found("20200129-02", "GEORGE")

def check_po_counter_20200129_02_KAPLAN():
    return ev.counter_speaker_found("20200129-02", "KAPLAN")

def check_po_counter_20200129_02_BRAINARD():
    return ev.counter_speaker_found("20200129-02", "BRAINARD")

def check_static_record_l1_20200129_03():
    return ev.record_shape_ok("20200129-03", 1)

def check_static_record_l2_20200129_03():
    return ev.record_shape_ok("20200129-03", 2)

def check_rh_foreign_l1_20200129_03():
    return ev.no_foreign_speaker("20200129-03", 1)

def check_rh_foreign_l2_20200129_03():
    return ev.no_foreign_speaker("20200129-03", 2)

def check_rh_padding_l1_20200129_03():
    return ev.no_padded_entries("20200129-03", 1)

def check_rh_padding_l2_20200129_03():
    return ev.no_padded_entries("20200129-03", 2)

def check_po_roster_20200129_03_BULLARD():
    return ev.roster_speaker_found("20200129-03", "BULLARD")

def check_po_roster_20200129_03_BOSTIC():
    return ev.roster_speaker_found("20200129-03", "BOSTIC")

def check_po_roster_20200129_03_MESTER():
    return ev.roster_speaker_found("20200129-03", "MESTER")

def check_po_roster_20200129_03_ROSENGREN():
    return ev.roster_speaker_found("20200129-03", "ROSENGREN")

def check_po_roster_20200129_03_GEORGE():
    return ev.roster_speaker_found("20200129-03", "GEORGE")

def check_po_roster_20200129_03_EVANS():
    return ev.roster_speaker_found("20200129-03", "EVANS")

def check_po_roster_20200129_03_BRAINARD():
    return ev.roster_speaker_found("20200129-03", "BRAINARD")

def check_po_roster_20200129_03_KAPLAN():
    return ev.roster_speaker_found("20200129-03", "KAPLAN")

def check_po_counter_20200129_03_POWELL():
    return ev.counter_speaker_found("20200129-03", "POWELL")

def check_po_counter_20200129_03_KASHKARI():
    return ev.counter_speaker_found("20200129-03", "KASHKARI")

def check_po_counter_20200129_03_CLARIDA():
    return ev.counter_speaker_found("20200129-03", "CLARIDA")

def check_po_counter_20200129_03_HARKER():
    return ev.counter_speaker_found("20200129-03", "HARKER")

def check_po_counter_20200129_03_BOWMAN():
    return ev.counter_speaker_found("20200129-03", "BOWMAN")

def check_static_record_l1_20200129_04():
    return ev.record_shape_ok("20200129-04", 1)

def check_static_record_l2_20200129_04():
    return ev.record_shape_ok("20200129-04", 2)

def check_rh_foreign_l1_20200129_04():
    return ev.no_foreign_speaker("20200129-04", 1)

def check_rh_foreign_l2_20200129_04():
    return ev.no_foreign_speaker("20200129-04", 2)

def check_rh_padding_l1_20200129_04():
    return ev.no_padded_entries("20200129-04", 1)

def check_rh_padding_l2_20200129_04():
    return ev.no_padded_entries("20200129-04", 2)

def check_po_roster_20200129_04_WILLIAMS():
    return ev.roster_speaker_found("20200129-04", "WILLIAMS")

def check_po_roster_20200129_04_EVANS():
    return ev.roster_speaker_found("20200129-04", "EVANS")

def check_po_roster_20200129_04_BRAINARD():
    return ev.roster_speaker_found("20200129-04", "BRAINARD")

def check_po_counter_20200129_04_POWELL():
    return ev.counter_speaker_found("20200129-04", "POWELL")

def check_po_counter_20200129_04_KASHKARI():
    return ev.counter_speaker_found("20200129-04", "KASHKARI")

def check_static_record_l1_20200129_05():
    return ev.record_shape_ok("20200129-05", 1)

def check_static_record_l2_20200129_05():
    return ev.record_shape_ok("20200129-05", 2)

def check_rh_foreign_l1_20200129_05():
    return ev.no_foreign_speaker("20200129-05", 1)

def check_rh_foreign_l2_20200129_05():
    return ev.no_foreign_speaker("20200129-05", 2)

def check_rh_padding_l1_20200129_05():
    return ev.no_padded_entries("20200129-05", 1)

def check_rh_padding_l2_20200129_05():
    return ev.no_padded_entries("20200129-05", 2)

def check_po_roster_20200129_05_QUARLES():
    return ev.roster_speaker_found("20200129-05", "QUARLES")

def check_po_roster_20200129_05_KASHKARI():
    return ev.roster_speaker_found("20200129-05", "KASHKARI")

def check_po_roster_20200129_05_POWELL():
    return ev.roster_speaker_found("20200129-05", "POWELL")

def check_po_roster_20200129_05_BOSTIC():
    return ev.roster_speaker_found("20200129-05", "BOSTIC")

def check_po_roster_20200129_05_HARKER():
    return ev.roster_speaker_found("20200129-05", "HARKER")

def check_po_roster_20200129_05_CLARIDA():
    return ev.roster_speaker_found("20200129-05", "CLARIDA")

def check_po_roster_20200129_05_MESTER():
    return ev.roster_speaker_found("20200129-05", "MESTER")

def check_po_roster_20200129_05_DALY():
    return ev.roster_speaker_found("20200129-05", "DALY")

def check_po_roster_20200129_05_EVANS():
    return ev.roster_speaker_found("20200129-05", "EVANS")

def check_po_roster_20200129_05_BOWMAN():
    return ev.roster_speaker_found("20200129-05", "BOWMAN")

def check_po_roster_20200129_05_BRAINARD():
    return ev.roster_speaker_found("20200129-05", "BRAINARD")

def check_po_roster_20200129_05_KAPLAN():
    return ev.roster_speaker_found("20200129-05", "KAPLAN")

def check_po_counter_20200129_05_ROSENGREN():
    return ev.counter_speaker_found("20200129-05", "ROSENGREN")

def check_static_record_l1_20200129_06():
    return ev.record_shape_ok("20200129-06", 1)

def check_static_record_l2_20200129_06():
    return ev.record_shape_ok("20200129-06", 2)

def check_rh_foreign_l1_20200129_06():
    return ev.no_foreign_speaker("20200129-06", 1)

def check_rh_foreign_l2_20200129_06():
    return ev.no_foreign_speaker("20200129-06", 2)

def check_rh_padding_l1_20200129_06():
    return ev.no_padded_entries("20200129-06", 1)

def check_rh_padding_l2_20200129_06():
    return ev.no_padded_entries("20200129-06", 2)

def check_po_roster_20200129_06_QUARLES():
    return ev.roster_speaker_found("20200129-06", "QUARLES")

def check_po_roster_20200129_06_BOSTIC():
    return ev.roster_speaker_found("20200129-06", "BOSTIC")

def check_po_roster_20200129_06_MESTER():
    return ev.roster_speaker_found("20200129-06", "MESTER")

def check_po_roster_20200129_06_ROSENGREN():
    return ev.roster_speaker_found("20200129-06", "ROSENGREN")

def check_po_roster_20200129_06_BOWMAN():
    return ev.roster_speaker_found("20200129-06", "BOWMAN")

def check_po_roster_20200129_06_DALY():
    return ev.roster_speaker_found("20200129-06", "DALY")

def check_po_roster_20200129_06_KAPLAN():
    return ev.roster_speaker_found("20200129-06", "KAPLAN")

def check_po_roster_20200129_06_BARKIN():
    return ev.roster_speaker_found("20200129-06", "BARKIN")

def check_static_record_l1_20200129_07():
    return ev.record_shape_ok("20200129-07", 1)

def check_static_record_l2_20200129_07():
    return ev.record_shape_ok("20200129-07", 2)

def check_rh_foreign_l1_20200129_07():
    return ev.no_foreign_speaker("20200129-07", 1)

def check_rh_foreign_l2_20200129_07():
    return ev.no_foreign_speaker("20200129-07", 2)

def check_rh_padding_l1_20200129_07():
    return ev.no_padded_entries("20200129-07", 1)

def check_rh_padding_l2_20200129_07():
    return ev.no_padded_entries("20200129-07", 2)

def check_po_roster_20200129_07_POWELL():
    return ev.roster_speaker_found("20200129-07", "POWELL")

def check_po_roster_20200129_07_BOSTIC():
    return ev.roster_speaker_found("20200129-07", "BOSTIC")

def check_po_roster_20200129_07_WILLIAMS():
    return ev.roster_speaker_found("20200129-07", "WILLIAMS")

def check_po_roster_20200129_07_MESTER():
    return ev.roster_speaker_found("20200129-07", "MESTER")

def check_po_roster_20200129_07_ROSENGREN():
    return ev.roster_speaker_found("20200129-07", "ROSENGREN")

def check_po_roster_20200129_07_BOWMAN():
    return ev.roster_speaker_found("20200129-07", "BOWMAN")

def check_po_roster_20200129_07_BRAINARD():
    return ev.roster_speaker_found("20200129-07", "BRAINARD")

def check_po_roster_20200129_07_KAPLAN():
    return ev.roster_speaker_found("20200129-07", "KAPLAN")

def check_po_roster_20200129_07_BARKIN():
    return ev.roster_speaker_found("20200129-07", "BARKIN")

def check_po_counter_20200129_07_QUARLES():
    return ev.counter_speaker_found("20200129-07", "QUARLES")

def check_po_counter_20200129_07_KASHKARI():
    return ev.counter_speaker_found("20200129-07", "KASHKARI")

def check_po_counter_20200129_07_DALY():
    return ev.counter_speaker_found("20200129-07", "DALY")

def check_po_counter_20200129_07_EVANS():
    return ev.counter_speaker_found("20200129-07", "EVANS")

def check_static_record_l1_20200129_08():
    return ev.record_shape_ok("20200129-08", 1)

def check_static_record_l2_20200129_08():
    return ev.record_shape_ok("20200129-08", 2)

def check_rh_foreign_l1_20200129_08():
    return ev.no_foreign_speaker("20200129-08", 1)

def check_rh_foreign_l2_20200129_08():
    return ev.no_foreign_speaker("20200129-08", 2)

def check_rh_padding_l1_20200129_08():
    return ev.no_padded_entries("20200129-08", 1)

def check_rh_padding_l2_20200129_08():
    return ev.no_padded_entries("20200129-08", 2)

def check_po_roster_20200129_08_QUARLES():
    return ev.roster_speaker_found("20200129-08", "QUARLES")

def check_po_roster_20200129_08_KASHKARI():
    return ev.roster_speaker_found("20200129-08", "KASHKARI")

def check_po_roster_20200129_08_HARKER():
    return ev.roster_speaker_found("20200129-08", "HARKER")

def check_po_roster_20200129_08_DALY():
    return ev.roster_speaker_found("20200129-08", "DALY")

def check_po_roster_20200129_08_EVANS():
    return ev.roster_speaker_found("20200129-08", "EVANS")

def check_po_roster_20200129_08_BOWMAN():
    return ev.roster_speaker_found("20200129-08", "BOWMAN")

def check_po_counter_20200129_08_ROSENGREN():
    return ev.counter_speaker_found("20200129-08", "ROSENGREN")

def check_po_counter_20200129_08_BARKIN():
    return ev.counter_speaker_found("20200129-08", "BARKIN")

def check_po_counter_20200129_08_KAPLAN():
    return ev.counter_speaker_found("20200129-08", "KAPLAN")

def check_static_record_l1_20200129_09():
    return ev.record_shape_ok("20200129-09", 1)

def check_static_record_l2_20200129_09():
    return ev.record_shape_ok("20200129-09", 2)

def check_rh_foreign_l1_20200129_09():
    return ev.no_foreign_speaker("20200129-09", 1)

def check_rh_foreign_l2_20200129_09():
    return ev.no_foreign_speaker("20200129-09", 2)

def check_rh_padding_l1_20200129_09():
    return ev.no_padded_entries("20200129-09", 1)

def check_rh_padding_l2_20200129_09():
    return ev.no_padded_entries("20200129-09", 2)

def check_po_roster_20200129_09_KASHKARI():
    return ev.roster_speaker_found("20200129-09", "KASHKARI")

def check_po_roster_20200129_09_DALY():
    return ev.roster_speaker_found("20200129-09", "DALY")

def check_po_roster_20200129_09_EVANS():
    return ev.roster_speaker_found("20200129-09", "EVANS")

def check_po_roster_20200129_09_BOWMAN():
    return ev.roster_speaker_found("20200129-09", "BOWMAN")

def check_po_counter_20200129_09_ROSENGREN():
    return ev.counter_speaker_found("20200129-09", "ROSENGREN")

def check_static_record_l1_20200129_10():
    return ev.record_shape_ok("20200129-10", 1)

def check_static_record_l2_20200129_10():
    return ev.record_shape_ok("20200129-10", 2)

def check_rh_foreign_l1_20200129_10():
    return ev.no_foreign_speaker("20200129-10", 1)

def check_rh_foreign_l2_20200129_10():
    return ev.no_foreign_speaker("20200129-10", 2)

def check_rh_padding_l1_20200129_10():
    return ev.no_padded_entries("20200129-10", 1)

def check_rh_padding_l2_20200129_10():
    return ev.no_padded_entries("20200129-10", 2)

def check_po_roster_20200129_10_QUARLES():
    return ev.roster_speaker_found("20200129-10", "QUARLES")

def check_po_roster_20200129_10_CLARIDA():
    return ev.roster_speaker_found("20200129-10", "CLARIDA")

def check_po_roster_20200129_10_MESTER():
    return ev.roster_speaker_found("20200129-10", "MESTER")

def check_po_roster_20200129_10_EVANS():
    return ev.roster_speaker_found("20200129-10", "EVANS")

def check_po_roster_20200129_10_BRAINARD():
    return ev.roster_speaker_found("20200129-10", "BRAINARD")

def check_po_counter_20200129_10_QUARLES():
    return ev.counter_speaker_found("20200129-10", "QUARLES")

def check_static_record_l1_20200129_11():
    return ev.record_shape_ok("20200129-11", 1)

def check_static_record_l2_20200129_11():
    return ev.record_shape_ok("20200129-11", 2)

def check_rh_foreign_l1_20200129_11():
    return ev.no_foreign_speaker("20200129-11", 1)

def check_rh_foreign_l2_20200129_11():
    return ev.no_foreign_speaker("20200129-11", 2)

def check_rh_padding_l1_20200129_11():
    return ev.no_padded_entries("20200129-11", 1)

def check_rh_padding_l2_20200129_11():
    return ev.no_padded_entries("20200129-11", 2)

def check_po_roster_20200129_11_CLARIDA():
    return ev.roster_speaker_found("20200129-11", "CLARIDA")

def check_po_roster_20200129_11_BOSTIC():
    return ev.roster_speaker_found("20200129-11", "BOSTIC")

def check_po_roster_20200129_11_MESTER():
    return ev.roster_speaker_found("20200129-11", "MESTER")

def check_po_roster_20200129_11_EVANS():
    return ev.roster_speaker_found("20200129-11", "EVANS")

def check_po_roster_20200129_11_BRAINARD():
    return ev.roster_speaker_found("20200129-11", "BRAINARD")

def check_po_counter_20200129_11_EVANS():
    return ev.counter_speaker_found("20200129-11", "EVANS")

def check_static_record_l1_20200129_12():
    return ev.record_shape_ok("20200129-12", 1)

def check_static_record_l2_20200129_12():
    return ev.record_shape_ok("20200129-12", 2)

def check_rh_foreign_l1_20200129_12():
    return ev.no_foreign_speaker("20200129-12", 1)

def check_rh_foreign_l2_20200129_12():
    return ev.no_foreign_speaker("20200129-12", 2)

def check_rh_padding_l1_20200129_12():
    return ev.no_padded_entries("20200129-12", 1)

def check_rh_padding_l2_20200129_12():
    return ev.no_padded_entries("20200129-12", 2)

def check_po_roster_20200129_12_POWELL():
    return ev.roster_speaker_found("20200129-12", "POWELL")

def check_po_roster_20200129_12_BULLARD():
    return ev.roster_speaker_found("20200129-12", "BULLARD")

def check_po_roster_20200129_12_KASHKARI():
    return ev.roster_speaker_found("20200129-12", "KASHKARI")

def check_po_roster_20200129_12_WILLIAMS():
    return ev.roster_speaker_found("20200129-12", "WILLIAMS")

def check_po_roster_20200129_12_CLARIDA():
    return ev.roster_speaker_found("20200129-12", "CLARIDA")

def check_po_roster_20200129_12_HARKER():
    return ev.roster_speaker_found("20200129-12", "HARKER")

def check_po_roster_20200129_12_DALY():
    return ev.roster_speaker_found("20200129-12", "DALY")

def check_po_roster_20200129_12_BOWMAN():
    return ev.roster_speaker_found("20200129-12", "BOWMAN")

def check_po_roster_20200129_12_BRAINARD():
    return ev.roster_speaker_found("20200129-12", "BRAINARD")

def check_po_roster_20200129_12_BARKIN():
    return ev.roster_speaker_found("20200129-12", "BARKIN")

def check_po_counter_20200129_12_QUARLES():
    return ev.counter_speaker_found("20200129-12", "QUARLES")

def check_po_counter_20200129_12_BOSTIC():
    return ev.counter_speaker_found("20200129-12", "BOSTIC")

def check_po_counter_20200129_12_MESTER():
    return ev.counter_speaker_found("20200129-12", "MESTER")

def check_po_counter_20200129_12_BARKIN():
    return ev.counter_speaker_found("20200129-12", "BARKIN")

def check_static_record_l1_20200129_13():
    return ev.record_shape_ok("20200129-13", 1)

def check_static_record_l2_20200129_13():
    return ev.record_shape_ok("20200129-13", 2)

def check_rh_foreign_l1_20200129_13():
    return ev.no_foreign_speaker("20200129-13", 1)

def check_rh_foreign_l2_20200129_13():
    return ev.no_foreign_speaker("20200129-13", 2)

def check_rh_padding_l1_20200129_13():
    return ev.no_padded_entries("20200129-13", 1)

def check_rh_padding_l2_20200129_13():
    return ev.no_padded_entries("20200129-13", 2)

def check_po_roster_20200129_13_BULLARD():
    return ev.roster_speaker_found("20200129-13", "BULLARD")

def check_po_roster_20200129_13_KASHKARI():
    return ev.roster_speaker_found("20200129-13", "KASHKARI")

def check_po_roster_20200129_13_CLARIDA():
    return ev.roster_speaker_found("20200129-13", "CLARIDA")

def check_po_roster_20200129_13_HARKER():
    return ev.roster_speaker_found("20200129-13", "HARKER")

def check_po_roster_20200129_13_WILLIAMS():
    return ev.roster_speaker_found("20200129-13", "WILLIAMS")

def check_po_roster_20200129_13_DALY():
    return ev.roster_speaker_found("20200129-13", "DALY")

def check_po_roster_20200129_13_BOWMAN():
    return ev.roster_speaker_found("20200129-13", "BOWMAN")

def check_po_roster_20200129_13_BRAINARD():
    return ev.roster_speaker_found("20200129-13", "BRAINARD")

def check_po_roster_20200129_13_BARKIN():
    return ev.roster_speaker_found("20200129-13", "BARKIN")

def check_po_counter_20200129_13_QUARLES():
    return ev.counter_speaker_found("20200129-13", "QUARLES")

def check_po_counter_20200129_13_MESTER():
    return ev.counter_speaker_found("20200129-13", "MESTER")

def check_po_counter_20200129_13_GEORGE():
    return ev.counter_speaker_found("20200129-13", "GEORGE")

def check_po_counter_20200129_13_BARKIN():
    return ev.counter_speaker_found("20200129-13", "BARKIN")

def check_static_record_l1_20200129_14():
    return ev.record_shape_ok("20200129-14", 1)

def check_static_record_l2_20200129_14():
    return ev.record_shape_ok("20200129-14", 2)

def check_rh_foreign_l1_20200129_14():
    return ev.no_foreign_speaker("20200129-14", 1)

def check_rh_foreign_l2_20200129_14():
    return ev.no_foreign_speaker("20200129-14", 2)

def check_rh_padding_l1_20200129_14():
    return ev.no_padded_entries("20200129-14", 1)

def check_rh_padding_l2_20200129_14():
    return ev.no_padded_entries("20200129-14", 2)

def check_po_roster_20200129_14_BULLARD():
    return ev.roster_speaker_found("20200129-14", "BULLARD")

def check_po_roster_20200129_14_KASHKARI():
    return ev.roster_speaker_found("20200129-14", "KASHKARI")

def check_po_roster_20200129_14_WILLIAMS():
    return ev.roster_speaker_found("20200129-14", "WILLIAMS")

def check_po_roster_20200129_14_HARKER():
    return ev.roster_speaker_found("20200129-14", "HARKER")

def check_po_roster_20200129_14_GEORGE():
    return ev.roster_speaker_found("20200129-14", "GEORGE")

def check_po_roster_20200129_14_DALY():
    return ev.roster_speaker_found("20200129-14", "DALY")

def check_po_roster_20200129_14_EVANS():
    return ev.roster_speaker_found("20200129-14", "EVANS")

def check_po_roster_20200129_14_BOWMAN():
    return ev.roster_speaker_found("20200129-14", "BOWMAN")

def check_po_counter_20200129_14_POWELL():
    return ev.counter_speaker_found("20200129-14", "POWELL")

def check_po_counter_20200129_14_HARKER():
    return ev.counter_speaker_found("20200129-14", "HARKER")

def check_po_counter_20200129_14_BOSTIC():
    return ev.counter_speaker_found("20200129-14", "BOSTIC")

def check_po_counter_20200129_14_MESTER():
    return ev.counter_speaker_found("20200129-14", "MESTER")

def check_po_counter_20200129_14_ROSENGREN():
    return ev.counter_speaker_found("20200129-14", "ROSENGREN")

def check_po_counter_20200129_14_GEORGE():
    return ev.counter_speaker_found("20200129-14", "GEORGE")

def check_po_counter_20200129_14_BARKIN():
    return ev.counter_speaker_found("20200129-14", "BARKIN")

def check_po_counter_20200129_14_KAPLAN():
    return ev.counter_speaker_found("20200129-14", "KAPLAN")

def check_static_record_l1_20200129_15():
    return ev.record_shape_ok("20200129-15", 1)

def check_static_record_l2_20200129_15():
    return ev.record_shape_ok("20200129-15", 2)

def check_rh_foreign_l1_20200129_15():
    return ev.no_foreign_speaker("20200129-15", 1)

def check_rh_foreign_l2_20200129_15():
    return ev.no_foreign_speaker("20200129-15", 2)

def check_rh_padding_l1_20200129_15():
    return ev.no_padded_entries("20200129-15", 1)

def check_rh_padding_l2_20200129_15():
    return ev.no_padded_entries("20200129-15", 2)

def check_po_roster_20200129_15_POWELL():
    return ev.roster_speaker_found("20200129-15", "POWELL")

def check_po_roster_20200129_15_BOSTIC():
    return ev.roster_speaker_found("20200129-15", "BOSTIC")

def check_po_roster_20200129_15_CLARIDA():
    return ev.roster_speaker_found("20200129-15", "CLARIDA")

def check_po_roster_20200129_15_HARKER():
    return ev.roster_speaker_found("20200129-15", "HARKER")

def check_po_roster_20200129_15_WILLIAMS():
    return ev.roster_speaker_found("20200129-15", "WILLIAMS")

def check_po_roster_20200129_15_MESTER():
    return ev.roster_speaker_found("20200129-15", "MESTER")

def check_po_roster_20200129_15_KAPLAN():
    return ev.roster_speaker_found("20200129-15", "KAPLAN")

def check_po_roster_20200129_15_BARKIN():
    return ev.roster_speaker_found("20200129-15", "BARKIN")

def check_po_counter_20200129_15_BULLARD():
    return ev.counter_speaker_found("20200129-15", "BULLARD")

def check_po_counter_20200129_15_KASHKARI():
    return ev.counter_speaker_found("20200129-15", "KASHKARI")

def check_po_counter_20200129_15_POWELL():
    return ev.counter_speaker_found("20200129-15", "POWELL")

def check_po_counter_20200129_15_WILLIAMS():
    return ev.counter_speaker_found("20200129-15", "WILLIAMS")

def check_po_counter_20200129_15_HARKER():
    return ev.counter_speaker_found("20200129-15", "HARKER")

def check_po_counter_20200129_15_CLARIDA():
    return ev.counter_speaker_found("20200129-15", "CLARIDA")

def check_po_counter_20200129_15_DALY():
    return ev.counter_speaker_found("20200129-15", "DALY")

def check_po_counter_20200129_15_EVANS():
    return ev.counter_speaker_found("20200129-15", "EVANS")

def check_po_counter_20200129_15_BOWMAN():
    return ev.counter_speaker_found("20200129-15", "BOWMAN")

def check_po_counter_20200129_15_BRAINARD():
    return ev.counter_speaker_found("20200129-15", "BRAINARD")

def check_po_counter_20200129_15_BARKIN():
    return ev.counter_speaker_found("20200129-15", "BARKIN")

def check_static_record_l1_20200129_16():
    return ev.record_shape_ok("20200129-16", 1)

def check_static_record_l2_20200129_16():
    return ev.record_shape_ok("20200129-16", 2)

def check_rh_foreign_l1_20200129_16():
    return ev.no_foreign_speaker("20200129-16", 1)

def check_rh_foreign_l2_20200129_16():
    return ev.no_foreign_speaker("20200129-16", 2)

def check_rh_padding_l1_20200129_16():
    return ev.no_padded_entries("20200129-16", 1)

def check_rh_padding_l2_20200129_16():
    return ev.no_padded_entries("20200129-16", 2)

def check_po_roster_20200129_16_QUARLES():
    return ev.roster_speaker_found("20200129-16", "QUARLES")

def check_po_roster_20200129_16_BOSTIC():
    return ev.roster_speaker_found("20200129-16", "BOSTIC")

def check_po_roster_20200129_16_MESTER():
    return ev.roster_speaker_found("20200129-16", "MESTER")

def check_po_roster_20200129_16_KAPLAN():
    return ev.roster_speaker_found("20200129-16", "KAPLAN")

def check_po_roster_20200129_16_BARKIN():
    return ev.roster_speaker_found("20200129-16", "BARKIN")

def check_po_counter_20200129_16_DALY():
    return ev.counter_speaker_found("20200129-16", "DALY")

def check_static_record_l1_20200129_17():
    return ev.record_shape_ok("20200129-17", 1)

def check_static_record_l2_20200129_17():
    return ev.record_shape_ok("20200129-17", 2)

def check_rh_foreign_l1_20200129_17():
    return ev.no_foreign_speaker("20200129-17", 1)

def check_rh_foreign_l2_20200129_17():
    return ev.no_foreign_speaker("20200129-17", 2)

def check_rh_padding_l1_20200129_17():
    return ev.no_padded_entries("20200129-17", 1)

def check_rh_padding_l2_20200129_17():
    return ev.no_padded_entries("20200129-17", 2)

def check_po_roster_20200129_17_POWELL():
    return ev.roster_speaker_found("20200129-17", "POWELL")

def check_po_roster_20200129_17_BOSTIC():
    return ev.roster_speaker_found("20200129-17", "BOSTIC")

def check_po_roster_20200129_17_HARKER():
    return ev.roster_speaker_found("20200129-17", "HARKER")

def check_po_roster_20200129_17_ROSENGREN():
    return ev.roster_speaker_found("20200129-17", "ROSENGREN")

def check_po_roster_20200129_17_EVANS():
    return ev.roster_speaker_found("20200129-17", "EVANS")

def check_po_roster_20200129_17_BRAINARD():
    return ev.roster_speaker_found("20200129-17", "BRAINARD")

def check_po_roster_20200129_17_BARKIN():
    return ev.roster_speaker_found("20200129-17", "BARKIN")

def check_po_counter_20200129_17_BULLARD():
    return ev.counter_speaker_found("20200129-17", "BULLARD")

def check_po_counter_20200129_17_GEORGE():
    return ev.counter_speaker_found("20200129-17", "GEORGE")

def check_po_counter_20200129_17_DALY():
    return ev.counter_speaker_found("20200129-17", "DALY")

def check_po_counter_20200129_17_EVANS():
    return ev.counter_speaker_found("20200129-17", "EVANS")

def check_po_counter_20200129_17_BOWMAN():
    return ev.counter_speaker_found("20200129-17", "BOWMAN")

def check_static_record_l1_20200129_18():
    return ev.record_shape_ok("20200129-18", 1)

def check_static_record_l2_20200129_18():
    return ev.record_shape_ok("20200129-18", 2)

def check_rh_foreign_l1_20200129_18():
    return ev.no_foreign_speaker("20200129-18", 1)

def check_rh_foreign_l2_20200129_18():
    return ev.no_foreign_speaker("20200129-18", 2)

def check_rh_padding_l1_20200129_18():
    return ev.no_padded_entries("20200129-18", 1)

def check_rh_padding_l2_20200129_18():
    return ev.no_padded_entries("20200129-18", 2)

def check_po_roster_20200129_18_BULLARD():
    return ev.roster_speaker_found("20200129-18", "BULLARD")

def check_po_roster_20200129_18_BOSTIC():
    return ev.roster_speaker_found("20200129-18", "BOSTIC")

def check_po_roster_20200129_18_GEORGE():
    return ev.roster_speaker_found("20200129-18", "GEORGE")

def check_po_roster_20200129_18_MESTER():
    return ev.roster_speaker_found("20200129-18", "MESTER")

def check_po_roster_20200129_18_BOWMAN():
    return ev.roster_speaker_found("20200129-18", "BOWMAN")

def check_po_roster_20200129_18_DALY():
    return ev.roster_speaker_found("20200129-18", "DALY")

def check_po_roster_20200129_18_BARKIN():
    return ev.roster_speaker_found("20200129-18", "BARKIN")

def check_po_counter_20200129_18_QUARLES():
    return ev.counter_speaker_found("20200129-18", "QUARLES")

def check_po_counter_20200129_18_KASHKARI():
    return ev.counter_speaker_found("20200129-18", "KASHKARI")

def check_static_record_l1_20200129_19():
    return ev.record_shape_ok("20200129-19", 1)

def check_static_record_l2_20200129_19():
    return ev.record_shape_ok("20200129-19", 2)

def check_rh_foreign_l1_20200129_19():
    return ev.no_foreign_speaker("20200129-19", 1)

def check_rh_foreign_l2_20200129_19():
    return ev.no_foreign_speaker("20200129-19", 2)

def check_rh_padding_l1_20200129_19():
    return ev.no_padded_entries("20200129-19", 1)

def check_rh_padding_l2_20200129_19():
    return ev.no_padded_entries("20200129-19", 2)

def check_po_roster_20200129_19_KASHKARI():
    return ev.roster_speaker_found("20200129-19", "KASHKARI")

def check_po_roster_20200129_19_WILLIAMS():
    return ev.roster_speaker_found("20200129-19", "WILLIAMS")

def check_po_roster_20200129_19_MESTER():
    return ev.roster_speaker_found("20200129-19", "MESTER")

def check_po_roster_20200129_19_GEORGE():
    return ev.roster_speaker_found("20200129-19", "GEORGE")

def check_po_roster_20200129_19_BOWMAN():
    return ev.roster_speaker_found("20200129-19", "BOWMAN")

def check_po_roster_20200129_19_BARKIN():
    return ev.roster_speaker_found("20200129-19", "BARKIN")

def check_static_record_l1_20200129_20():
    return ev.record_shape_ok("20200129-20", 1)

def check_static_record_l2_20200129_20():
    return ev.record_shape_ok("20200129-20", 2)

def check_rh_foreign_l1_20200129_20():
    return ev.no_foreign_speaker("20200129-20", 1)

def check_rh_foreign_l2_20200129_20():
    return ev.no_foreign_speaker("20200129-20", 2)

def check_rh_padding_l1_20200129_20():
    return ev.no_padded_entries("20200129-20", 1)

def check_rh_padding_l2_20200129_20():
    return ev.no_padded_entries("20200129-20", 2)

def check_po_roster_20200129_20_CLARIDA():
    return ev.roster_speaker_found("20200129-20", "CLARIDA")

def check_po_roster_20200129_20_WILLIAMS():
    return ev.roster_speaker_found("20200129-20", "WILLIAMS")

def check_po_roster_20200129_20_MESTER():
    return ev.roster_speaker_found("20200129-20", "MESTER")

def check_po_roster_20200129_20_BOWMAN():
    return ev.roster_speaker_found("20200129-20", "BOWMAN")

def check_po_roster_20200129_20_DALY():
    return ev.roster_speaker_found("20200129-20", "DALY")

def check_po_roster_20200129_20_KAPLAN():
    return ev.roster_speaker_found("20200129-20", "KAPLAN")

def check_po_roster_20200129_20_BARKIN():
    return ev.roster_speaker_found("20200129-20", "BARKIN")

def check_po_counter_20200129_20_QUARLES():
    return ev.counter_speaker_found("20200129-20", "QUARLES")

def check_po_counter_20200129_20_BOSTIC():
    return ev.counter_speaker_found("20200129-20", "BOSTIC")

def check_po_counter_20200129_20_WILLIAMS():
    return ev.counter_speaker_found("20200129-20", "WILLIAMS")

def check_po_counter_20200129_20_GEORGE():
    return ev.counter_speaker_found("20200129-20", "GEORGE")

def check_po_counter_20200129_20_MESTER():
    return ev.counter_speaker_found("20200129-20", "MESTER")

def check_po_counter_20200129_20_EVANS():
    return ev.counter_speaker_found("20200129-20", "EVANS")

def check_po_counter_20200129_20_KAPLAN():
    return ev.counter_speaker_found("20200129-20", "KAPLAN")

def check_po_counter_20200129_20_BARKIN():
    return ev.counter_speaker_found("20200129-20", "BARKIN")

def check_static_record_l1_20200129_21():
    return ev.record_shape_ok("20200129-21", 1)

def check_static_record_l2_20200129_21():
    return ev.record_shape_ok("20200129-21", 2)

def check_rh_foreign_l1_20200129_21():
    return ev.no_foreign_speaker("20200129-21", 1)

def check_rh_foreign_l2_20200129_21():
    return ev.no_foreign_speaker("20200129-21", 2)

def check_rh_padding_l1_20200129_21():
    return ev.no_padded_entries("20200129-21", 1)

def check_rh_padding_l2_20200129_21():
    return ev.no_padded_entries("20200129-21", 2)

def check_po_roster_20200129_21_KASHKARI():
    return ev.roster_speaker_found("20200129-21", "KASHKARI")

def check_po_roster_20200129_21_HARKER():
    return ev.roster_speaker_found("20200129-21", "HARKER")

def check_po_roster_20200129_21_MESTER():
    return ev.roster_speaker_found("20200129-21", "MESTER")

def check_po_roster_20200129_21_DALY():
    return ev.roster_speaker_found("20200129-21", "DALY")

def check_po_roster_20200129_21_KAPLAN():
    return ev.roster_speaker_found("20200129-21", "KAPLAN")

def check_po_roster_20200129_21_BARKIN():
    return ev.roster_speaker_found("20200129-21", "BARKIN")

def check_po_counter_20200129_21_BOSTIC():
    return ev.counter_speaker_found("20200129-21", "BOSTIC")

def check_po_counter_20200129_21_EVANS():
    return ev.counter_speaker_found("20200129-21", "EVANS")

def check_po_counter_20200129_21_KAPLAN():
    return ev.counter_speaker_found("20200129-21", "KAPLAN")

def check_static_record_l1_20200129_22():
    return ev.record_shape_ok("20200129-22", 1)

def check_static_record_l2_20200129_22():
    return ev.record_shape_ok("20200129-22", 2)

def check_rh_foreign_l1_20200129_22():
    return ev.no_foreign_speaker("20200129-22", 1)

def check_rh_foreign_l2_20200129_22():
    return ev.no_foreign_speaker("20200129-22", 2)

def check_rh_padding_l1_20200129_22():
    return ev.no_padded_entries("20200129-22", 1)

def check_rh_padding_l2_20200129_22():
    return ev.no_padded_entries("20200129-22", 2)

def check_po_roster_20200129_22_KASHKARI():
    return ev.roster_speaker_found("20200129-22", "KASHKARI")

def check_po_roster_20200129_22_GEORGE():
    return ev.roster_speaker_found("20200129-22", "GEORGE")

def check_po_roster_20200129_22_BOWMAN():
    return ev.roster_speaker_found("20200129-22", "BOWMAN")

def check_po_roster_20200129_22_KAPLAN():
    return ev.roster_speaker_found("20200129-22", "KAPLAN")

def check_static_record_l1_20200129_23():
    return ev.record_shape_ok("20200129-23", 1)

def check_static_record_l2_20200129_23():
    return ev.record_shape_ok("20200129-23", 2)

def check_rh_foreign_l1_20200129_23():
    return ev.no_foreign_speaker("20200129-23", 1)

def check_rh_foreign_l2_20200129_23():
    return ev.no_foreign_speaker("20200129-23", 2)

def check_rh_padding_l1_20200129_23():
    return ev.no_padded_entries("20200129-23", 1)

def check_rh_padding_l2_20200129_23():
    return ev.no_padded_entries("20200129-23", 2)

def check_po_roster_20200129_23_BULLARD():
    return ev.roster_speaker_found("20200129-23", "BULLARD")

def check_po_roster_20200129_23_BOSTIC():
    return ev.roster_speaker_found("20200129-23", "BOSTIC")

def check_po_roster_20200129_23_HARKER():
    return ev.roster_speaker_found("20200129-23", "HARKER")

def check_po_roster_20200129_23_MESTER():
    return ev.roster_speaker_found("20200129-23", "MESTER")

def check_po_roster_20200129_23_EVANS():
    return ev.roster_speaker_found("20200129-23", "EVANS")

def check_po_roster_20200129_23_BARKIN():
    return ev.roster_speaker_found("20200129-23", "BARKIN")

def check_po_counter_20200129_23_KASHKARI():
    return ev.counter_speaker_found("20200129-23", "KASHKARI")

def check_po_counter_20200129_23_CLARIDA():
    return ev.counter_speaker_found("20200129-23", "CLARIDA")

def check_po_counter_20200129_23_DALY():
    return ev.counter_speaker_found("20200129-23", "DALY")

def check_po_counter_20200129_23_KAPLAN():
    return ev.counter_speaker_found("20200129-23", "KAPLAN")

def check_static_record_l1_20200129_24():
    return ev.record_shape_ok("20200129-24", 1)

def check_static_record_l2_20200129_24():
    return ev.record_shape_ok("20200129-24", 2)

def check_rh_foreign_l1_20200129_24():
    return ev.no_foreign_speaker("20200129-24", 1)

def check_rh_foreign_l2_20200129_24():
    return ev.no_foreign_speaker("20200129-24", 2)

def check_rh_padding_l1_20200129_24():
    return ev.no_padded_entries("20200129-24", 1)

def check_rh_padding_l2_20200129_24():
    return ev.no_padded_entries("20200129-24", 2)

def check_po_roster_20200129_24_CLARIDA():
    return ev.roster_speaker_found("20200129-24", "CLARIDA")

def check_po_roster_20200129_24_MESTER():
    return ev.roster_speaker_found("20200129-24", "MESTER")

def check_po_roster_20200129_24_DALY():
    return ev.roster_speaker_found("20200129-24", "DALY")

def check_po_roster_20200129_24_BRAINARD():
    return ev.roster_speaker_found("20200129-24", "BRAINARD")

def check_po_roster_20200129_24_BARKIN():
    return ev.roster_speaker_found("20200129-24", "BARKIN")

def check_static_record_l1_20200129_25():
    return ev.record_shape_ok("20200129-25", 1)

def check_static_record_l2_20200129_25():
    return ev.record_shape_ok("20200129-25", 2)

def check_rh_foreign_l1_20200129_25():
    return ev.no_foreign_speaker("20200129-25", 1)

def check_rh_foreign_l2_20200129_25():
    return ev.no_foreign_speaker("20200129-25", 2)

def check_rh_padding_l1_20200129_25():
    return ev.no_padded_entries("20200129-25", 1)

def check_rh_padding_l2_20200129_25():
    return ev.no_padded_entries("20200129-25", 2)

def check_po_roster_20200129_25_KASHKARI():
    return ev.roster_speaker_found("20200129-25", "KASHKARI")

def check_po_roster_20200129_25_BOSTIC():
    return ev.roster_speaker_found("20200129-25", "BOSTIC")

def check_po_roster_20200129_25_CLARIDA():
    return ev.roster_speaker_found("20200129-25", "CLARIDA")

def check_po_roster_20200129_25_MESTER():
    return ev.roster_speaker_found("20200129-25", "MESTER")

def check_po_roster_20200129_25_DALY():
    return ev.roster_speaker_found("20200129-25", "DALY")

def check_po_roster_20200129_25_KAPLAN():
    return ev.roster_speaker_found("20200129-25", "KAPLAN")

def check_po_counter_20200129_25_BARKIN():
    return ev.counter_speaker_found("20200129-25", "BARKIN")

def check_static_record_l1_20200129_26():
    return ev.record_shape_ok("20200129-26", 1)

def check_static_record_l2_20200129_26():
    return ev.record_shape_ok("20200129-26", 2)

def check_rh_foreign_l1_20200129_26():
    return ev.no_foreign_speaker("20200129-26", 1)

def check_rh_foreign_l2_20200129_26():
    return ev.no_foreign_speaker("20200129-26", 2)

def check_rh_padding_l1_20200129_26():
    return ev.no_padded_entries("20200129-26", 1)

def check_rh_padding_l2_20200129_26():
    return ev.no_padded_entries("20200129-26", 2)

def check_po_roster_20200129_26_KASHKARI():
    return ev.roster_speaker_found("20200129-26", "KASHKARI")

def check_po_roster_20200129_26_QUARLES():
    return ev.roster_speaker_found("20200129-26", "QUARLES")

def check_po_roster_20200129_26_WILLIAMS():
    return ev.roster_speaker_found("20200129-26", "WILLIAMS")

def check_po_roster_20200129_26_CLARIDA():
    return ev.roster_speaker_found("20200129-26", "CLARIDA")

def check_po_roster_20200129_26_HARKER():
    return ev.roster_speaker_found("20200129-26", "HARKER")

def check_po_roster_20200129_26_MESTER():
    return ev.roster_speaker_found("20200129-26", "MESTER")

def check_po_roster_20200129_26_BOWMAN():
    return ev.roster_speaker_found("20200129-26", "BOWMAN")

def check_po_roster_20200129_26_DALY():
    return ev.roster_speaker_found("20200129-26", "DALY")

def check_static_record_l1_20200129_27():
    return ev.record_shape_ok("20200129-27", 1)

def check_static_record_l2_20200129_27():
    return ev.record_shape_ok("20200129-27", 2)

def check_rh_foreign_l1_20200129_27():
    return ev.no_foreign_speaker("20200129-27", 1)

def check_rh_foreign_l2_20200129_27():
    return ev.no_foreign_speaker("20200129-27", 2)

def check_rh_padding_l1_20200129_27():
    return ev.no_padded_entries("20200129-27", 1)

def check_rh_padding_l2_20200129_27():
    return ev.no_padded_entries("20200129-27", 2)

def check_po_roster_20200129_27_KASHKARI():
    return ev.roster_speaker_found("20200129-27", "KASHKARI")

def check_po_roster_20200129_27_POWELL():
    return ev.roster_speaker_found("20200129-27", "POWELL")

def check_po_roster_20200129_27_WILLIAMS():
    return ev.roster_speaker_found("20200129-27", "WILLIAMS")

def check_po_roster_20200129_27_CLARIDA():
    return ev.roster_speaker_found("20200129-27", "CLARIDA")

def check_po_roster_20200129_27_GEORGE():
    return ev.roster_speaker_found("20200129-27", "GEORGE")

def check_po_roster_20200129_27_DALY():
    return ev.roster_speaker_found("20200129-27", "DALY")

def check_po_roster_20200129_27_BRAINARD():
    return ev.roster_speaker_found("20200129-27", "BRAINARD")

def check_po_roster_20200129_27_KAPLAN():
    return ev.roster_speaker_found("20200129-27", "KAPLAN")

def check_po_counter_20200129_27_BOSTIC():
    return ev.counter_speaker_found("20200129-27", "BOSTIC")

def check_po_counter_20200129_27_MESTER():
    return ev.counter_speaker_found("20200129-27", "MESTER")

def check_po_counter_20200129_27_BOWMAN():
    return ev.counter_speaker_found("20200129-27", "BOWMAN")

def check_po_counter_20200129_27_BARKIN():
    return ev.counter_speaker_found("20200129-27", "BARKIN")

def check_static_record_l1_20200129_28():
    return ev.record_shape_ok("20200129-28", 1)

def check_static_record_l2_20200129_28():
    return ev.record_shape_ok("20200129-28", 2)

def check_rh_foreign_l1_20200129_28():
    return ev.no_foreign_speaker("20200129-28", 1)

def check_rh_foreign_l2_20200129_28():
    return ev.no_foreign_speaker("20200129-28", 2)

def check_rh_padding_l1_20200129_28():
    return ev.no_padded_entries("20200129-28", 1)

def check_rh_padding_l2_20200129_28():
    return ev.no_padded_entries("20200129-28", 2)

def check_po_roster_20200129_28_BOSTIC():
    return ev.roster_speaker_found("20200129-28", "BOSTIC")

def check_po_roster_20200129_28_MESTER():
    return ev.roster_speaker_found("20200129-28", "MESTER")

def check_po_roster_20200129_28_GEORGE():
    return ev.roster_speaker_found("20200129-28", "GEORGE")

def check_po_roster_20200129_28_KAPLAN():
    return ev.roster_speaker_found("20200129-28", "KAPLAN")

def check_po_counter_20200129_28_KASHKARI():
    return ev.counter_speaker_found("20200129-28", "KASHKARI")

def check_po_counter_20200129_28_WILLIAMS():
    return ev.counter_speaker_found("20200129-28", "WILLIAMS")

def check_po_counter_20200129_28_GEORGE():
    return ev.counter_speaker_found("20200129-28", "GEORGE")

def check_po_counter_20200129_28_DALY():
    return ev.counter_speaker_found("20200129-28", "DALY")

def check_po_counter_20200129_28_EVANS():
    return ev.counter_speaker_found("20200129-28", "EVANS")

def check_po_counter_20200129_28_BRAINARD():
    return ev.counter_speaker_found("20200129-28", "BRAINARD")

def check_static_record_l1_20200129_29():
    return ev.record_shape_ok("20200129-29", 1)

def check_static_record_l2_20200129_29():
    return ev.record_shape_ok("20200129-29", 2)

def check_rh_foreign_l1_20200129_29():
    return ev.no_foreign_speaker("20200129-29", 1)

def check_rh_foreign_l2_20200129_29():
    return ev.no_foreign_speaker("20200129-29", 2)

def check_rh_padding_l1_20200129_29():
    return ev.no_padded_entries("20200129-29", 1)

def check_rh_padding_l2_20200129_29():
    return ev.no_padded_entries("20200129-29", 2)

def check_po_roster_20200129_29_QUARLES():
    return ev.roster_speaker_found("20200129-29", "QUARLES")

def check_po_roster_20200129_29_BULLARD():
    return ev.roster_speaker_found("20200129-29", "BULLARD")

def check_po_roster_20200129_29_WILLIAMS():
    return ev.roster_speaker_found("20200129-29", "WILLIAMS")

def check_po_roster_20200129_29_MESTER():
    return ev.roster_speaker_found("20200129-29", "MESTER")

def check_po_roster_20200129_29_GEORGE():
    return ev.roster_speaker_found("20200129-29", "GEORGE")

def check_po_roster_20200129_29_ROSENGREN():
    return ev.roster_speaker_found("20200129-29", "ROSENGREN")

def check_po_roster_20200129_29_BRAINARD():
    return ev.roster_speaker_found("20200129-29", "BRAINARD")

def check_po_roster_20200129_29_KAPLAN():
    return ev.roster_speaker_found("20200129-29", "KAPLAN")

def check_po_counter_20200129_29_BULLARD():
    return ev.counter_speaker_found("20200129-29", "BULLARD")

def check_po_counter_20200129_29_CLARIDA():
    return ev.counter_speaker_found("20200129-29", "CLARIDA")

def check_po_counter_20200129_29_DALY():
    return ev.counter_speaker_found("20200129-29", "DALY")

def check_static_record_l1_20200129_30():
    return ev.record_shape_ok("20200129-30", 1)

def check_static_record_l2_20200129_30():
    return ev.record_shape_ok("20200129-30", 2)

def check_rh_foreign_l1_20200129_30():
    return ev.no_foreign_speaker("20200129-30", 1)

def check_rh_foreign_l2_20200129_30():
    return ev.no_foreign_speaker("20200129-30", 2)

def check_rh_padding_l1_20200129_30():
    return ev.no_padded_entries("20200129-30", 1)

def check_rh_padding_l2_20200129_30():
    return ev.no_padded_entries("20200129-30", 2)

def check_po_roster_20200129_30_POWELL():
    return ev.roster_speaker_found("20200129-30", "POWELL")

def check_po_roster_20200129_30_QUARLES():
    return ev.roster_speaker_found("20200129-30", "QUARLES")

def check_po_roster_20200129_30_BULLARD():
    return ev.roster_speaker_found("20200129-30", "BULLARD")

def check_po_roster_20200129_30_WILLIAMS():
    return ev.roster_speaker_found("20200129-30", "WILLIAMS")

def check_po_roster_20200129_30_BOSTIC():
    return ev.roster_speaker_found("20200129-30", "BOSTIC")

def check_po_roster_20200129_30_ROSENGREN():
    return ev.roster_speaker_found("20200129-30", "ROSENGREN")

def check_po_roster_20200129_30_GEORGE():
    return ev.roster_speaker_found("20200129-30", "GEORGE")

def check_po_roster_20200129_30_MESTER():
    return ev.roster_speaker_found("20200129-30", "MESTER")

def check_po_roster_20200129_30_EVANS():
    return ev.roster_speaker_found("20200129-30", "EVANS")

def check_po_roster_20200129_30_BRAINARD():
    return ev.roster_speaker_found("20200129-30", "BRAINARD")

def check_po_roster_20200129_30_KAPLAN():
    return ev.roster_speaker_found("20200129-30", "KAPLAN")

def check_po_roster_20200129_30_BARKIN():
    return ev.roster_speaker_found("20200129-30", "BARKIN")

def check_po_counter_20200129_30_POWELL():
    return ev.counter_speaker_found("20200129-30", "POWELL")

def check_po_counter_20200129_30_QUARLES():
    return ev.counter_speaker_found("20200129-30", "QUARLES")

def check_po_counter_20200129_30_KASHKARI():
    return ev.counter_speaker_found("20200129-30", "KASHKARI")

def check_po_counter_20200129_30_CLARIDA():
    return ev.counter_speaker_found("20200129-30", "CLARIDA")

def check_po_counter_20200129_30_HARKER():
    return ev.counter_speaker_found("20200129-30", "HARKER")

def check_po_counter_20200129_30_BOWMAN():
    return ev.counter_speaker_found("20200129-30", "BOWMAN")

def check_static_record_l1_20200129_31():
    return ev.record_shape_ok("20200129-31", 1)

def check_static_record_l2_20200129_31():
    return ev.record_shape_ok("20200129-31", 2)

def check_rh_foreign_l1_20200129_31():
    return ev.no_foreign_speaker("20200129-31", 1)

def check_rh_foreign_l2_20200129_31():
    return ev.no_foreign_speaker("20200129-31", 2)

def check_rh_padding_l1_20200129_31():
    return ev.no_padded_entries("20200129-31", 1)

def check_rh_padding_l2_20200129_31():
    return ev.no_padded_entries("20200129-31", 2)

def check_po_roster_20200129_31_WILLIAMS():
    return ev.roster_speaker_found("20200129-31", "WILLIAMS")

def check_po_roster_20200129_31_MESTER():
    return ev.roster_speaker_found("20200129-31", "MESTER")

def check_po_roster_20200129_31_ROSENGREN():
    return ev.roster_speaker_found("20200129-31", "ROSENGREN")

def check_po_roster_20200129_31_GEORGE():
    return ev.roster_speaker_found("20200129-31", "GEORGE")

def check_po_roster_20200129_31_BRAINARD():
    return ev.roster_speaker_found("20200129-31", "BRAINARD")

def check_po_counter_20200129_31_QUARLES():
    return ev.counter_speaker_found("20200129-31", "QUARLES")

def check_static_record_l1_20200129_32():
    return ev.record_shape_ok("20200129-32", 1)

def check_static_record_l2_20200129_32():
    return ev.record_shape_ok("20200129-32", 2)

def check_rh_foreign_l1_20200129_32():
    return ev.no_foreign_speaker("20200129-32", 1)

def check_rh_foreign_l2_20200129_32():
    return ev.no_foreign_speaker("20200129-32", 2)

def check_rh_padding_l1_20200129_32():
    return ev.no_padded_entries("20200129-32", 1)

def check_rh_padding_l2_20200129_32():
    return ev.no_padded_entries("20200129-32", 2)

def check_po_roster_20200129_32_POWELL():
    return ev.roster_speaker_found("20200129-32", "POWELL")

def check_po_roster_20200129_32_KASHKARI():
    return ev.roster_speaker_found("20200129-32", "KASHKARI")

def check_po_roster_20200129_32_CLARIDA():
    return ev.roster_speaker_found("20200129-32", "CLARIDA")

def check_po_roster_20200129_32_HARKER():
    return ev.roster_speaker_found("20200129-32", "HARKER")

def check_po_roster_20200129_32_ROSENGREN():
    return ev.roster_speaker_found("20200129-32", "ROSENGREN")

def check_po_roster_20200129_32_DALY():
    return ev.roster_speaker_found("20200129-32", "DALY")

def check_po_roster_20200129_32_EVANS():
    return ev.roster_speaker_found("20200129-32", "EVANS")

def check_po_roster_20200129_32_BRAINARD():
    return ev.roster_speaker_found("20200129-32", "BRAINARD")

def check_po_counter_20200129_32_QUARLES():
    return ev.counter_speaker_found("20200129-32", "QUARLES")

def check_po_counter_20200129_32_GEORGE():
    return ev.counter_speaker_found("20200129-32", "GEORGE")

def check_static_record_l1_20200129_33():
    return ev.record_shape_ok("20200129-33", 1)

def check_static_record_l2_20200129_33():
    return ev.record_shape_ok("20200129-33", 2)

def check_rh_foreign_l1_20200129_33():
    return ev.no_foreign_speaker("20200129-33", 1)

def check_rh_foreign_l2_20200129_33():
    return ev.no_foreign_speaker("20200129-33", 2)

def check_rh_padding_l1_20200129_33():
    return ev.no_padded_entries("20200129-33", 1)

def check_rh_padding_l2_20200129_33():
    return ev.no_padded_entries("20200129-33", 2)

def check_po_roster_20200129_33_POWELL():
    return ev.roster_speaker_found("20200129-33", "POWELL")

def check_po_roster_20200129_33_KASHKARI():
    return ev.roster_speaker_found("20200129-33", "KASHKARI")

def check_po_roster_20200129_33_CLARIDA():
    return ev.roster_speaker_found("20200129-33", "CLARIDA")

def check_po_roster_20200129_33_DALY():
    return ev.roster_speaker_found("20200129-33", "DALY")

def check_po_roster_20200129_33_EVANS():
    return ev.roster_speaker_found("20200129-33", "EVANS")

def check_po_roster_20200129_33_BRAINARD():
    return ev.roster_speaker_found("20200129-33", "BRAINARD")

def check_po_counter_20200129_33_QUARLES():
    return ev.counter_speaker_found("20200129-33", "QUARLES")

def check_po_counter_20200129_33_BOWMAN():
    return ev.counter_speaker_found("20200129-33", "BOWMAN")

def check_static_record_l1_20200129_34():
    return ev.record_shape_ok("20200129-34", 1)

def check_static_record_l2_20200129_34():
    return ev.record_shape_ok("20200129-34", 2)

def check_rh_foreign_l1_20200129_34():
    return ev.no_foreign_speaker("20200129-34", 1)

def check_rh_foreign_l2_20200129_34():
    return ev.no_foreign_speaker("20200129-34", 2)

def check_rh_padding_l1_20200129_34():
    return ev.no_padded_entries("20200129-34", 1)

def check_rh_padding_l2_20200129_34():
    return ev.no_padded_entries("20200129-34", 2)

def check_po_roster_20200129_34_POWELL():
    return ev.roster_speaker_found("20200129-34", "POWELL")

def check_po_roster_20200129_34_KASHKARI():
    return ev.roster_speaker_found("20200129-34", "KASHKARI")

def check_po_roster_20200129_34_CLARIDA():
    return ev.roster_speaker_found("20200129-34", "CLARIDA")

def check_po_roster_20200129_34_BOSTIC():
    return ev.roster_speaker_found("20200129-34", "BOSTIC")

def check_po_roster_20200129_34_HARKER():
    return ev.roster_speaker_found("20200129-34", "HARKER")

def check_po_roster_20200129_34_MESTER():
    return ev.roster_speaker_found("20200129-34", "MESTER")

def check_po_roster_20200129_34_ROSENGREN():
    return ev.roster_speaker_found("20200129-34", "ROSENGREN")

def check_po_roster_20200129_34_EVANS():
    return ev.roster_speaker_found("20200129-34", "EVANS")

def check_po_roster_20200129_34_BRAINARD():
    return ev.roster_speaker_found("20200129-34", "BRAINARD")

def check_po_roster_20200129_34_KAPLAN():
    return ev.roster_speaker_found("20200129-34", "KAPLAN")

def check_po_roster_20200129_34_BARKIN():
    return ev.roster_speaker_found("20200129-34", "BARKIN")

def check_po_counter_20200129_34_GEORGE():
    return ev.counter_speaker_found("20200129-34", "GEORGE")

def check_po_counter_20200129_34_BOWMAN():
    return ev.counter_speaker_found("20200129-34", "BOWMAN")

def check_static_record_l1_20200129_35():
    return ev.record_shape_ok("20200129-35", 1)

def check_static_record_l2_20200129_35():
    return ev.record_shape_ok("20200129-35", 2)

def check_rh_foreign_l1_20200129_35():
    return ev.no_foreign_speaker("20200129-35", 1)

def check_rh_foreign_l2_20200129_35():
    return ev.no_foreign_speaker("20200129-35", 2)

def check_rh_padding_l1_20200129_35():
    return ev.no_padded_entries("20200129-35", 1)

def check_rh_padding_l2_20200129_35():
    return ev.no_padded_entries("20200129-35", 2)

def check_po_roster_20200129_35_KASHKARI():
    return ev.roster_speaker_found("20200129-35", "KASHKARI")

def check_po_roster_20200129_35_WILLIAMS():
    return ev.roster_speaker_found("20200129-35", "WILLIAMS")

def check_po_roster_20200129_35_CLARIDA():
    return ev.roster_speaker_found("20200129-35", "CLARIDA")

def check_po_roster_20200129_35_DALY():
    return ev.roster_speaker_found("20200129-35", "DALY")

def check_po_counter_20200129_35_ROSENGREN():
    return ev.counter_speaker_found("20200129-35", "ROSENGREN")

def check_po_counter_20200129_35_MESTER():
    return ev.counter_speaker_found("20200129-35", "MESTER")

def check_static_record_l1_20200129_36():
    return ev.record_shape_ok("20200129-36", 1)

def check_static_record_l2_20200129_36():
    return ev.record_shape_ok("20200129-36", 2)

def check_rh_foreign_l1_20200129_36():
    return ev.no_foreign_speaker("20200129-36", 1)

def check_rh_foreign_l2_20200129_36():
    return ev.no_foreign_speaker("20200129-36", 2)

def check_rh_padding_l1_20200129_36():
    return ev.no_padded_entries("20200129-36", 1)

def check_rh_padding_l2_20200129_36():
    return ev.no_padded_entries("20200129-36", 2)

def check_po_roster_20200129_36_POWELL():
    return ev.roster_speaker_found("20200129-36", "POWELL")

def check_po_roster_20200129_36_QUARLES():
    return ev.roster_speaker_found("20200129-36", "QUARLES")

def check_po_roster_20200129_36_WILLIAMS():
    return ev.roster_speaker_found("20200129-36", "WILLIAMS")

def check_po_roster_20200129_36_EVANS():
    return ev.roster_speaker_found("20200129-36", "EVANS")

def check_po_roster_20200129_36_BRAINARD():
    return ev.roster_speaker_found("20200129-36", "BRAINARD")

def check_po_roster_20200129_36_KAPLAN():
    return ev.roster_speaker_found("20200129-36", "KAPLAN")

def check_static_record_l1_20200129_37():
    return ev.record_shape_ok("20200129-37", 1)

def check_static_record_l2_20200129_37():
    return ev.record_shape_ok("20200129-37", 2)

def check_rh_foreign_l1_20200129_37():
    return ev.no_foreign_speaker("20200129-37", 1)

def check_rh_foreign_l2_20200129_37():
    return ev.no_foreign_speaker("20200129-37", 2)

def check_rh_padding_l1_20200129_37():
    return ev.no_padded_entries("20200129-37", 1)

def check_rh_padding_l2_20200129_37():
    return ev.no_padded_entries("20200129-37", 2)

def check_po_roster_20200129_37_BULLARD():
    return ev.roster_speaker_found("20200129-37", "BULLARD")

def check_po_roster_20200129_37_QUARLES():
    return ev.roster_speaker_found("20200129-37", "QUARLES")

def check_po_roster_20200129_37_WILLIAMS():
    return ev.roster_speaker_found("20200129-37", "WILLIAMS")

def check_po_roster_20200129_37_MESTER():
    return ev.roster_speaker_found("20200129-37", "MESTER")

def check_po_roster_20200129_37_BRAINARD():
    return ev.roster_speaker_found("20200129-37", "BRAINARD")

def check_po_counter_20200129_37_WILLIAMS():
    return ev.counter_speaker_found("20200129-37", "WILLIAMS")

def check_static_record_l1_20200315_01():
    return ev.record_shape_ok("20200315-01", 1)

def check_static_record_l2_20200315_01():
    return ev.record_shape_ok("20200315-01", 2)

def check_rh_foreign_l1_20200315_01():
    return ev.no_foreign_speaker("20200315-01", 1)

def check_rh_foreign_l2_20200315_01():
    return ev.no_foreign_speaker("20200315-01", 2)

def check_rh_padding_l1_20200315_01():
    return ev.no_padded_entries("20200315-01", 1)

def check_rh_padding_l2_20200315_01():
    return ev.no_padded_entries("20200315-01", 2)

def check_po_roster_20200315_01_POWELL():
    return ev.roster_speaker_found("20200315-01", "POWELL")

def check_po_roster_20200315_01_DALY():
    return ev.roster_speaker_found("20200315-01", "DALY")

def check_po_roster_20200315_01_BOWMAN():
    return ev.roster_speaker_found("20200315-01", "BOWMAN")

def check_po_roster_20200315_01_CLARIDA():
    return ev.roster_speaker_found("20200315-01", "CLARIDA")

def check_static_record_l1_20200315_02():
    return ev.record_shape_ok("20200315-02", 1)

def check_static_record_l2_20200315_02():
    return ev.record_shape_ok("20200315-02", 2)

def check_rh_foreign_l1_20200315_02():
    return ev.no_foreign_speaker("20200315-02", 1)

def check_rh_foreign_l2_20200315_02():
    return ev.no_foreign_speaker("20200315-02", 2)

def check_rh_padding_l1_20200315_02():
    return ev.no_padded_entries("20200315-02", 1)

def check_rh_padding_l2_20200315_02():
    return ev.no_padded_entries("20200315-02", 2)

def check_po_roster_20200315_02_MESTER():
    return ev.roster_speaker_found("20200315-02", "MESTER")

def check_po_roster_20200315_02_DALY():
    return ev.roster_speaker_found("20200315-02", "DALY")

def check_po_roster_20200315_02_BOSTIC():
    return ev.roster_speaker_found("20200315-02", "BOSTIC")

def check_po_roster_20200315_02_BARKIN():
    return ev.roster_speaker_found("20200315-02", "BARKIN")

def check_po_counter_20200315_02_QUARLES():
    return ev.counter_speaker_found("20200315-02", "QUARLES")

def check_po_counter_20200315_02_BOWMAN():
    return ev.counter_speaker_found("20200315-02", "BOWMAN")

def check_po_counter_20200315_02_BARKIN():
    return ev.counter_speaker_found("20200315-02", "BARKIN")

def check_static_record_l1_20200315_03():
    return ev.record_shape_ok("20200315-03", 1)

def check_static_record_l2_20200315_03():
    return ev.record_shape_ok("20200315-03", 2)

def check_rh_foreign_l1_20200315_03():
    return ev.no_foreign_speaker("20200315-03", 1)

def check_rh_foreign_l2_20200315_03():
    return ev.no_foreign_speaker("20200315-03", 2)

def check_rh_padding_l1_20200315_03():
    return ev.no_padded_entries("20200315-03", 1)

def check_rh_padding_l2_20200315_03():
    return ev.no_padded_entries("20200315-03", 2)

def check_po_roster_20200315_03_HARKER():
    return ev.roster_speaker_found("20200315-03", "HARKER")

def check_po_roster_20200315_03_BULLARD():
    return ev.roster_speaker_found("20200315-03", "BULLARD")

def check_po_roster_20200315_03_QUARLES():
    return ev.roster_speaker_found("20200315-03", "QUARLES")

def check_po_roster_20200315_03_KASHKARI():
    return ev.roster_speaker_found("20200315-03", "KASHKARI")

def check_po_roster_20200315_03_BRAINARD():
    return ev.roster_speaker_found("20200315-03", "BRAINARD")

def check_po_roster_20200315_03_BOWMAN():
    return ev.roster_speaker_found("20200315-03", "BOWMAN")

def check_po_roster_20200315_03_WILLIAMS():
    return ev.roster_speaker_found("20200315-03", "WILLIAMS")

def check_po_roster_20200315_03_BARKIN():
    return ev.roster_speaker_found("20200315-03", "BARKIN")

def check_po_counter_20200315_03_KAPLAN():
    return ev.counter_speaker_found("20200315-03", "KAPLAN")

def check_po_counter_20200315_03_DALY():
    return ev.counter_speaker_found("20200315-03", "DALY")

def check_po_counter_20200315_03_GEORGE():
    return ev.counter_speaker_found("20200315-03", "GEORGE")

def check_po_counter_20200315_03_BRAINARD():
    return ev.counter_speaker_found("20200315-03", "BRAINARD")

def check_po_counter_20200315_03_ROSENGREN():
    return ev.counter_speaker_found("20200315-03", "ROSENGREN")

def check_po_counter_20200315_03_BOWMAN():
    return ev.counter_speaker_found("20200315-03", "BOWMAN")

def check_static_record_l1_20200315_04():
    return ev.record_shape_ok("20200315-04", 1)

def check_static_record_l2_20200315_04():
    return ev.record_shape_ok("20200315-04", 2)

def check_rh_foreign_l1_20200315_04():
    return ev.no_foreign_speaker("20200315-04", 1)

def check_rh_foreign_l2_20200315_04():
    return ev.no_foreign_speaker("20200315-04", 2)

def check_rh_padding_l1_20200315_04():
    return ev.no_padded_entries("20200315-04", 1)

def check_rh_padding_l2_20200315_04():
    return ev.no_padded_entries("20200315-04", 2)

def check_po_roster_20200315_04_KAPLAN():
    return ev.roster_speaker_found("20200315-04", "KAPLAN")

def check_po_roster_20200315_04_POWELL():
    return ev.roster_speaker_found("20200315-04", "POWELL")

def check_po_roster_20200315_04_MESTER():
    return ev.roster_speaker_found("20200315-04", "MESTER")

def check_po_roster_20200315_04_DALY():
    return ev.roster_speaker_found("20200315-04", "DALY")

def check_po_roster_20200315_04_ROSENGREN():
    return ev.roster_speaker_found("20200315-04", "ROSENGREN")

def check_po_roster_20200315_04_BRAINARD():
    return ev.roster_speaker_found("20200315-04", "BRAINARD")

def check_po_roster_20200315_04_KASHKARI():
    return ev.roster_speaker_found("20200315-04", "KASHKARI")

def check_po_roster_20200315_04_BOSTIC():
    return ev.roster_speaker_found("20200315-04", "BOSTIC")

def check_po_roster_20200315_04_BOWMAN():
    return ev.roster_speaker_found("20200315-04", "BOWMAN")

def check_po_roster_20200315_04_WILLIAMS():
    return ev.roster_speaker_found("20200315-04", "WILLIAMS")

def check_static_record_l1_20200315_05():
    return ev.record_shape_ok("20200315-05", 1)

def check_static_record_l2_20200315_05():
    return ev.record_shape_ok("20200315-05", 2)

def check_rh_foreign_l1_20200315_05():
    return ev.no_foreign_speaker("20200315-05", 1)

def check_rh_foreign_l2_20200315_05():
    return ev.no_foreign_speaker("20200315-05", 2)

def check_rh_padding_l1_20200315_05():
    return ev.no_padded_entries("20200315-05", 1)

def check_rh_padding_l2_20200315_05():
    return ev.no_padded_entries("20200315-05", 2)

def check_po_roster_20200315_05_BULLARD():
    return ev.roster_speaker_found("20200315-05", "BULLARD")

def check_po_roster_20200315_05_POWELL():
    return ev.roster_speaker_found("20200315-05", "POWELL")

def check_po_roster_20200315_05_HARKER():
    return ev.roster_speaker_found("20200315-05", "HARKER")

def check_po_roster_20200315_05_DALY():
    return ev.roster_speaker_found("20200315-05", "DALY")

def check_po_roster_20200315_05_GEORGE():
    return ev.roster_speaker_found("20200315-05", "GEORGE")

def check_po_roster_20200315_05_QUARLES():
    return ev.roster_speaker_found("20200315-05", "QUARLES")

def check_po_roster_20200315_05_KASHKARI():
    return ev.roster_speaker_found("20200315-05", "KASHKARI")

def check_po_roster_20200315_05_ROSENGREN():
    return ev.roster_speaker_found("20200315-05", "ROSENGREN")

def check_po_roster_20200315_05_BRAINARD():
    return ev.roster_speaker_found("20200315-05", "BRAINARD")

def check_po_roster_20200315_05_EVANS():
    return ev.roster_speaker_found("20200315-05", "EVANS")

def check_po_roster_20200315_05_WILLIAMS():
    return ev.roster_speaker_found("20200315-05", "WILLIAMS")

def check_po_roster_20200315_05_CLARIDA():
    return ev.roster_speaker_found("20200315-05", "CLARIDA")

def check_po_roster_20200315_05_BARKIN():
    return ev.roster_speaker_found("20200315-05", "BARKIN")

def check_po_counter_20200315_05_KAPLAN():
    return ev.counter_speaker_found("20200315-05", "KAPLAN")

def check_po_counter_20200315_05_MESTER():
    return ev.counter_speaker_found("20200315-05", "MESTER")

def check_po_counter_20200315_05_QUARLES():
    return ev.counter_speaker_found("20200315-05", "QUARLES")

def check_po_counter_20200315_05_BOSTIC():
    return ev.counter_speaker_found("20200315-05", "BOSTIC")

def check_po_counter_20200315_05_BOWMAN():
    return ev.counter_speaker_found("20200315-05", "BOWMAN")

def check_static_record_l1_20200315_06():
    return ev.record_shape_ok("20200315-06", 1)

def check_static_record_l2_20200315_06():
    return ev.record_shape_ok("20200315-06", 2)

def check_rh_foreign_l1_20200315_06():
    return ev.no_foreign_speaker("20200315-06", 1)

def check_rh_foreign_l2_20200315_06():
    return ev.no_foreign_speaker("20200315-06", 2)

def check_rh_padding_l1_20200315_06():
    return ev.no_padded_entries("20200315-06", 1)

def check_rh_padding_l2_20200315_06():
    return ev.no_padded_entries("20200315-06", 2)

def check_po_roster_20200315_06_KAPLAN():
    return ev.roster_speaker_found("20200315-06", "KAPLAN")

def check_po_roster_20200315_06_MESTER():
    return ev.roster_speaker_found("20200315-06", "MESTER")

def check_po_roster_20200315_06_BOSTIC():
    return ev.roster_speaker_found("20200315-06", "BOSTIC")

def check_po_roster_20200315_06_BOWMAN():
    return ev.roster_speaker_found("20200315-06", "BOWMAN")

def check_po_counter_20200315_06_POWELL():
    return ev.counter_speaker_found("20200315-06", "POWELL")

def check_po_counter_20200315_06_HARKER():
    return ev.counter_speaker_found("20200315-06", "HARKER")

def check_po_counter_20200315_06_BULLARD():
    return ev.counter_speaker_found("20200315-06", "BULLARD")

def check_po_counter_20200315_06_DALY():
    return ev.counter_speaker_found("20200315-06", "DALY")

def check_po_counter_20200315_06_KASHKARI():
    return ev.counter_speaker_found("20200315-06", "KASHKARI")

def check_po_counter_20200315_06_EVANS():
    return ev.counter_speaker_found("20200315-06", "EVANS")

def check_po_counter_20200315_06_WILLIAMS():
    return ev.counter_speaker_found("20200315-06", "WILLIAMS")

def check_po_counter_20200315_06_CLARIDA():
    return ev.counter_speaker_found("20200315-06", "CLARIDA")

def check_static_record_l1_20200315_07():
    return ev.record_shape_ok("20200315-07", 1)

def check_static_record_l2_20200315_07():
    return ev.record_shape_ok("20200315-07", 2)

def check_rh_foreign_l1_20200315_07():
    return ev.no_foreign_speaker("20200315-07", 1)

def check_rh_foreign_l2_20200315_07():
    return ev.no_foreign_speaker("20200315-07", 2)

def check_rh_padding_l1_20200315_07():
    return ev.no_padded_entries("20200315-07", 1)

def check_rh_padding_l2_20200315_07():
    return ev.no_padded_entries("20200315-07", 2)

def check_po_roster_20200315_07_HARKER():
    return ev.roster_speaker_found("20200315-07", "HARKER")

def check_po_roster_20200315_07_POWELL():
    return ev.roster_speaker_found("20200315-07", "POWELL")

def check_po_roster_20200315_07_MESTER():
    return ev.roster_speaker_found("20200315-07", "MESTER")

def check_po_roster_20200315_07_DALY():
    return ev.roster_speaker_found("20200315-07", "DALY")

def check_po_roster_20200315_07_BRAINARD():
    return ev.roster_speaker_found("20200315-07", "BRAINARD")

def check_po_roster_20200315_07_KASHKARI():
    return ev.roster_speaker_found("20200315-07", "KASHKARI")

def check_po_roster_20200315_07_BOWMAN():
    return ev.roster_speaker_found("20200315-07", "BOWMAN")

def check_po_roster_20200315_07_BARKIN():
    return ev.roster_speaker_found("20200315-07", "BARKIN")

def check_po_counter_20200315_07_BULLARD():
    return ev.counter_speaker_found("20200315-07", "BULLARD")

def check_po_counter_20200315_07_WILLIAMS():
    return ev.counter_speaker_found("20200315-07", "WILLIAMS")

def check_static_record_l1_20200315_08():
    return ev.record_shape_ok("20200315-08", 1)

def check_static_record_l2_20200315_08():
    return ev.record_shape_ok("20200315-08", 2)

def check_rh_foreign_l1_20200315_08():
    return ev.no_foreign_speaker("20200315-08", 1)

def check_rh_foreign_l2_20200315_08():
    return ev.no_foreign_speaker("20200315-08", 2)

def check_rh_padding_l1_20200315_08():
    return ev.no_padded_entries("20200315-08", 1)

def check_rh_padding_l2_20200315_08():
    return ev.no_padded_entries("20200315-08", 2)

def check_po_roster_20200315_08_WILLIAMS():
    return ev.roster_speaker_found("20200315-08", "WILLIAMS")

def check_po_counter_20200315_08_BRAINARD():
    return ev.counter_speaker_found("20200315-08", "BRAINARD")

def check_po_counter_20200315_08_BARKIN():
    return ev.counter_speaker_found("20200315-08", "BARKIN")

def check_static_record_l1_20200315_09():
    return ev.record_shape_ok("20200315-09", 1)

def check_static_record_l2_20200315_09():
    return ev.record_shape_ok("20200315-09", 2)

def check_rh_foreign_l1_20200315_09():
    return ev.no_foreign_speaker("20200315-09", 1)

def check_rh_foreign_l2_20200315_09():
    return ev.no_foreign_speaker("20200315-09", 2)

def check_rh_padding_l1_20200315_09():
    return ev.no_padded_entries("20200315-09", 1)

def check_rh_padding_l2_20200315_09():
    return ev.no_padded_entries("20200315-09", 2)

def check_po_roster_20200315_09_BULLARD():
    return ev.roster_speaker_found("20200315-09", "BULLARD")

def check_po_roster_20200315_09_HARKER():
    return ev.roster_speaker_found("20200315-09", "HARKER")

def check_po_roster_20200315_09_KAPLAN():
    return ev.roster_speaker_found("20200315-09", "KAPLAN")

def check_po_roster_20200315_09_MESTER():
    return ev.roster_speaker_found("20200315-09", "MESTER")

def check_po_roster_20200315_09_DALY():
    return ev.roster_speaker_found("20200315-09", "DALY")

def check_po_roster_20200315_09_BOSTIC():
    return ev.roster_speaker_found("20200315-09", "BOSTIC")

def check_po_roster_20200315_09_BOWMAN():
    return ev.roster_speaker_found("20200315-09", "BOWMAN")

def check_po_roster_20200315_09_BARKIN():
    return ev.roster_speaker_found("20200315-09", "BARKIN")

def check_static_record_l1_20200315_10():
    return ev.record_shape_ok("20200315-10", 1)

def check_static_record_l2_20200315_10():
    return ev.record_shape_ok("20200315-10", 2)

def check_rh_foreign_l1_20200315_10():
    return ev.no_foreign_speaker("20200315-10", 1)

def check_rh_foreign_l2_20200315_10():
    return ev.no_foreign_speaker("20200315-10", 2)

def check_rh_padding_l1_20200315_10():
    return ev.no_padded_entries("20200315-10", 1)

def check_rh_padding_l2_20200315_10():
    return ev.no_padded_entries("20200315-10", 2)

def check_po_roster_20200315_10_BULLARD():
    return ev.roster_speaker_found("20200315-10", "BULLARD")

def check_po_roster_20200315_10_HARKER():
    return ev.roster_speaker_found("20200315-10", "HARKER")

def check_po_roster_20200315_10_MESTER():
    return ev.roster_speaker_found("20200315-10", "MESTER")

def check_po_roster_20200315_10_QUARLES():
    return ev.roster_speaker_found("20200315-10", "QUARLES")

def check_po_roster_20200315_10_GEORGE():
    return ev.roster_speaker_found("20200315-10", "GEORGE")

def check_po_roster_20200315_10_BOSTIC():
    return ev.roster_speaker_found("20200315-10", "BOSTIC")

def check_po_roster_20200315_10_BOWMAN():
    return ev.roster_speaker_found("20200315-10", "BOWMAN")

def check_po_roster_20200315_10_BARKIN():
    return ev.roster_speaker_found("20200315-10", "BARKIN")

def check_po_counter_20200315_10_DALY():
    return ev.counter_speaker_found("20200315-10", "DALY")

def check_po_counter_20200315_10_EVANS():
    return ev.counter_speaker_found("20200315-10", "EVANS")

def check_static_record_l1_20200315_11():
    return ev.record_shape_ok("20200315-11", 1)

def check_static_record_l2_20200315_11():
    return ev.record_shape_ok("20200315-11", 2)

def check_rh_foreign_l1_20200315_11():
    return ev.no_foreign_speaker("20200315-11", 1)

def check_rh_foreign_l2_20200315_11():
    return ev.no_foreign_speaker("20200315-11", 2)

def check_rh_padding_l1_20200315_11():
    return ev.no_padded_entries("20200315-11", 1)

def check_rh_padding_l2_20200315_11():
    return ev.no_padded_entries("20200315-11", 2)

def check_po_roster_20200315_11_BULLARD():
    return ev.roster_speaker_found("20200315-11", "BULLARD")

def check_po_roster_20200315_11_MESTER():
    return ev.roster_speaker_found("20200315-11", "MESTER")

def check_po_roster_20200315_11_ROSENGREN():
    return ev.roster_speaker_found("20200315-11", "ROSENGREN")

def check_po_roster_20200315_11_BARKIN():
    return ev.roster_speaker_found("20200315-11", "BARKIN")

def check_static_record_l1_20200315_12():
    return ev.record_shape_ok("20200315-12", 1)

def check_static_record_l2_20200315_12():
    return ev.record_shape_ok("20200315-12", 2)

def check_rh_foreign_l1_20200315_12():
    return ev.no_foreign_speaker("20200315-12", 1)

def check_rh_foreign_l2_20200315_12():
    return ev.no_foreign_speaker("20200315-12", 2)

def check_rh_padding_l1_20200315_12():
    return ev.no_padded_entries("20200315-12", 1)

def check_rh_padding_l2_20200315_12():
    return ev.no_padded_entries("20200315-12", 2)

def check_po_roster_20200315_12_MESTER():
    return ev.roster_speaker_found("20200315-12", "MESTER")

def check_po_roster_20200315_12_BOWMAN():
    return ev.roster_speaker_found("20200315-12", "BOWMAN")

def check_po_roster_20200315_12_BARKIN():
    return ev.roster_speaker_found("20200315-12", "BARKIN")

def check_po_counter_20200315_12_DALY():
    return ev.counter_speaker_found("20200315-12", "DALY")

def check_po_counter_20200315_12_BOSTIC():
    return ev.counter_speaker_found("20200315-12", "BOSTIC")

def check_static_record_l1_20200315_13():
    return ev.record_shape_ok("20200315-13", 1)

def check_static_record_l2_20200315_13():
    return ev.record_shape_ok("20200315-13", 2)

def check_rh_foreign_l1_20200315_13():
    return ev.no_foreign_speaker("20200315-13", 1)

def check_rh_foreign_l2_20200315_13():
    return ev.no_foreign_speaker("20200315-13", 2)

def check_rh_padding_l1_20200315_13():
    return ev.no_padded_entries("20200315-13", 1)

def check_rh_padding_l2_20200315_13():
    return ev.no_padded_entries("20200315-13", 2)

def check_po_roster_20200315_13_POWELL():
    return ev.roster_speaker_found("20200315-13", "POWELL")

def check_po_roster_20200315_13_KAPLAN():
    return ev.roster_speaker_found("20200315-13", "KAPLAN")

def check_po_roster_20200315_13_DALY():
    return ev.roster_speaker_found("20200315-13", "DALY")

def check_po_roster_20200315_13_MESTER():
    return ev.roster_speaker_found("20200315-13", "MESTER")

def check_po_roster_20200315_13_BRAINARD():
    return ev.roster_speaker_found("20200315-13", "BRAINARD")

def check_po_roster_20200315_13_EVANS():
    return ev.roster_speaker_found("20200315-13", "EVANS")

def check_po_counter_20200315_13_BRAINARD():
    return ev.counter_speaker_found("20200315-13", "BRAINARD")

def check_po_counter_20200315_13_BOWMAN():
    return ev.counter_speaker_found("20200315-13", "BOWMAN")

def check_po_counter_20200315_13_BARKIN():
    return ev.counter_speaker_found("20200315-13", "BARKIN")

def check_static_record_l1_20200315_14():
    return ev.record_shape_ok("20200315-14", 1)

def check_static_record_l2_20200315_14():
    return ev.record_shape_ok("20200315-14", 2)

def check_rh_foreign_l1_20200315_14():
    return ev.no_foreign_speaker("20200315-14", 1)

def check_rh_foreign_l2_20200315_14():
    return ev.no_foreign_speaker("20200315-14", 2)

def check_rh_padding_l1_20200315_14():
    return ev.no_padded_entries("20200315-14", 1)

def check_rh_padding_l2_20200315_14():
    return ev.no_padded_entries("20200315-14", 2)

def check_po_roster_20200315_14_HARKER():
    return ev.roster_speaker_found("20200315-14", "HARKER")

def check_po_roster_20200315_14_POWELL():
    return ev.roster_speaker_found("20200315-14", "POWELL")

def check_po_roster_20200315_14_KAPLAN():
    return ev.roster_speaker_found("20200315-14", "KAPLAN")

def check_po_roster_20200315_14_MESTER():
    return ev.roster_speaker_found("20200315-14", "MESTER")

def check_po_roster_20200315_14_GEORGE():
    return ev.roster_speaker_found("20200315-14", "GEORGE")

def check_po_roster_20200315_14_DALY():
    return ev.roster_speaker_found("20200315-14", "DALY")

def check_po_roster_20200315_14_QUARLES():
    return ev.roster_speaker_found("20200315-14", "QUARLES")

def check_po_roster_20200315_14_KASHKARI():
    return ev.roster_speaker_found("20200315-14", "KASHKARI")

def check_po_roster_20200315_14_BRAINARD():
    return ev.roster_speaker_found("20200315-14", "BRAINARD")

def check_po_roster_20200315_14_WILLIAMS():
    return ev.roster_speaker_found("20200315-14", "WILLIAMS")

def check_po_roster_20200315_14_CLARIDA():
    return ev.roster_speaker_found("20200315-14", "CLARIDA")

def check_po_counter_20200315_14_QUARLES():
    return ev.counter_speaker_found("20200315-14", "QUARLES")

def check_po_counter_20200315_14_ROSENGREN():
    return ev.counter_speaker_found("20200315-14", "ROSENGREN")

def check_po_counter_20200315_14_BRAINARD():
    return ev.counter_speaker_found("20200315-14", "BRAINARD")

def check_static_record_l1_20200315_15():
    return ev.record_shape_ok("20200315-15", 1)

def check_static_record_l2_20200315_15():
    return ev.record_shape_ok("20200315-15", 2)

def check_rh_foreign_l1_20200315_15():
    return ev.no_foreign_speaker("20200315-15", 1)

def check_rh_foreign_l2_20200315_15():
    return ev.no_foreign_speaker("20200315-15", 2)

def check_rh_padding_l1_20200315_15():
    return ev.no_padded_entries("20200315-15", 1)

def check_rh_padding_l2_20200315_15():
    return ev.no_padded_entries("20200315-15", 2)

def check_po_roster_20200315_15_KAPLAN():
    return ev.roster_speaker_found("20200315-15", "KAPLAN")

def check_po_roster_20200315_15_DALY():
    return ev.roster_speaker_found("20200315-15", "DALY")

def check_po_roster_20200315_15_GEORGE():
    return ev.roster_speaker_found("20200315-15", "GEORGE")

def check_po_roster_20200315_15_QUARLES():
    return ev.roster_speaker_found("20200315-15", "QUARLES")

def check_po_roster_20200315_15_KASHKARI():
    return ev.roster_speaker_found("20200315-15", "KASHKARI")

def check_po_roster_20200315_15_ROSENGREN():
    return ev.roster_speaker_found("20200315-15", "ROSENGREN")

def check_po_roster_20200315_15_BRAINARD():
    return ev.roster_speaker_found("20200315-15", "BRAINARD")

def check_po_counter_20200315_15_KASHKARI():
    return ev.counter_speaker_found("20200315-15", "KASHKARI")

def check_static_record_l1_20200429_01():
    return ev.record_shape_ok("20200429-01", 1)

def check_static_record_l2_20200429_01():
    return ev.record_shape_ok("20200429-01", 2)

def check_rh_foreign_l1_20200429_01():
    return ev.no_foreign_speaker("20200429-01", 1)

def check_rh_foreign_l2_20200429_01():
    return ev.no_foreign_speaker("20200429-01", 2)

def check_rh_padding_l1_20200429_01():
    return ev.no_padded_entries("20200429-01", 1)

def check_rh_padding_l2_20200429_01():
    return ev.no_padded_entries("20200429-01", 2)

def check_po_roster_20200429_01_KAPLAN():
    return ev.roster_speaker_found("20200429-01", "KAPLAN")

def check_po_roster_20200429_01_WILLIAMS():
    return ev.roster_speaker_found("20200429-01", "WILLIAMS")

def check_po_roster_20200429_01_DALY():
    return ev.roster_speaker_found("20200429-01", "DALY")

def check_static_record_l1_20200429_02():
    return ev.record_shape_ok("20200429-02", 1)

def check_static_record_l2_20200429_02():
    return ev.record_shape_ok("20200429-02", 2)

def check_rh_foreign_l1_20200429_02():
    return ev.no_foreign_speaker("20200429-02", 1)

def check_rh_foreign_l2_20200429_02():
    return ev.no_foreign_speaker("20200429-02", 2)

def check_rh_padding_l1_20200429_02():
    return ev.no_padded_entries("20200429-02", 1)

def check_rh_padding_l2_20200429_02():
    return ev.no_padded_entries("20200429-02", 2)

def check_po_roster_20200429_02_BRAINARD():
    return ev.roster_speaker_found("20200429-02", "BRAINARD")

def check_po_roster_20200429_02_BOSTIC():
    return ev.roster_speaker_found("20200429-02", "BOSTIC")

def check_po_roster_20200429_02_KAPLAN():
    return ev.roster_speaker_found("20200429-02", "KAPLAN")

def check_po_roster_20200429_02_WILLIAMS():
    return ev.roster_speaker_found("20200429-02", "WILLIAMS")

def check_po_roster_20200429_02_MESTER():
    return ev.roster_speaker_found("20200429-02", "MESTER")

def check_po_roster_20200429_02_EVANS():
    return ev.roster_speaker_found("20200429-02", "EVANS")

def check_po_roster_20200429_02_POWELL():
    return ev.roster_speaker_found("20200429-02", "POWELL")

def check_po_roster_20200429_02_CLARIDA():
    return ev.roster_speaker_found("20200429-02", "CLARIDA")

def check_po_roster_20200429_02_GEORGE():
    return ev.roster_speaker_found("20200429-02", "GEORGE")

def check_po_roster_20200429_02_KASHKARI():
    return ev.roster_speaker_found("20200429-02", "KASHKARI")

def check_po_roster_20200429_02_ROSENGREN():
    return ev.roster_speaker_found("20200429-02", "ROSENGREN")

def check_static_record_l1_20200429_03():
    return ev.record_shape_ok("20200429-03", 1)

def check_static_record_l2_20200429_03():
    return ev.record_shape_ok("20200429-03", 2)

def check_rh_foreign_l1_20200429_03():
    return ev.no_foreign_speaker("20200429-03", 1)

def check_rh_foreign_l2_20200429_03():
    return ev.no_foreign_speaker("20200429-03", 2)

def check_rh_padding_l1_20200429_03():
    return ev.no_padded_entries("20200429-03", 1)

def check_rh_padding_l2_20200429_03():
    return ev.no_padded_entries("20200429-03", 2)

def check_po_roster_20200429_03_QUARLES():
    return ev.roster_speaker_found("20200429-03", "QUARLES")

def check_po_roster_20200429_03_KAPLAN():
    return ev.roster_speaker_found("20200429-03", "KAPLAN")

def check_po_counter_20200429_03_POWELL():
    return ev.counter_speaker_found("20200429-03", "POWELL")

def check_static_record_l1_20200429_04():
    return ev.record_shape_ok("20200429-04", 1)

def check_static_record_l2_20200429_04():
    return ev.record_shape_ok("20200429-04", 2)

def check_rh_foreign_l1_20200429_04():
    return ev.no_foreign_speaker("20200429-04", 1)

def check_rh_foreign_l2_20200429_04():
    return ev.no_foreign_speaker("20200429-04", 2)

def check_rh_padding_l1_20200429_04():
    return ev.no_padded_entries("20200429-04", 1)

def check_rh_padding_l2_20200429_04():
    return ev.no_padded_entries("20200429-04", 2)

def check_po_roster_20200429_04_BRAINARD():
    return ev.roster_speaker_found("20200429-04", "BRAINARD")

def check_po_roster_20200429_04_QUARLES():
    return ev.roster_speaker_found("20200429-04", "QUARLES")

def check_po_roster_20200429_04_KAPLAN():
    return ev.roster_speaker_found("20200429-04", "KAPLAN")

def check_po_roster_20200429_04_MESTER():
    return ev.roster_speaker_found("20200429-04", "MESTER")

def check_po_roster_20200429_04_WILLIAMS():
    return ev.roster_speaker_found("20200429-04", "WILLIAMS")

def check_po_roster_20200429_04_BARKIN():
    return ev.roster_speaker_found("20200429-04", "BARKIN")

def check_po_roster_20200429_04_DALY():
    return ev.roster_speaker_found("20200429-04", "DALY")

def check_po_roster_20200429_04_BULLARD():
    return ev.roster_speaker_found("20200429-04", "BULLARD")

def check_po_roster_20200429_04_POWELL():
    return ev.roster_speaker_found("20200429-04", "POWELL")

def check_po_roster_20200429_04_CLARIDA():
    return ev.roster_speaker_found("20200429-04", "CLARIDA")

def check_po_roster_20200429_04_GEORGE():
    return ev.roster_speaker_found("20200429-04", "GEORGE")

def check_po_roster_20200429_04_KASHKARI():
    return ev.roster_speaker_found("20200429-04", "KASHKARI")

def check_po_roster_20200429_04_BOWMAN():
    return ev.roster_speaker_found("20200429-04", "BOWMAN")

def check_po_roster_20200429_04_ROSENGREN():
    return ev.roster_speaker_found("20200429-04", "ROSENGREN")

def check_static_record_l1_20200429_05():
    return ev.record_shape_ok("20200429-05", 1)

def check_static_record_l2_20200429_05():
    return ev.record_shape_ok("20200429-05", 2)

def check_rh_foreign_l1_20200429_05():
    return ev.no_foreign_speaker("20200429-05", 1)

def check_rh_foreign_l2_20200429_05():
    return ev.no_foreign_speaker("20200429-05", 2)

def check_rh_padding_l1_20200429_05():
    return ev.no_padded_entries("20200429-05", 1)

def check_rh_padding_l2_20200429_05():
    return ev.no_padded_entries("20200429-05", 2)

def check_po_roster_20200429_05_BRAINARD():
    return ev.roster_speaker_found("20200429-05", "BRAINARD")

def check_po_roster_20200429_05_DALY():
    return ev.roster_speaker_found("20200429-05", "DALY")

def check_po_roster_20200429_05_GEORGE():
    return ev.roster_speaker_found("20200429-05", "GEORGE")

def check_po_roster_20200429_05_KASHKARI():
    return ev.roster_speaker_found("20200429-05", "KASHKARI")

def check_po_roster_20200429_05_ROSENGREN():
    return ev.roster_speaker_found("20200429-05", "ROSENGREN")

def check_po_counter_20200429_05_QUARLES():
    return ev.counter_speaker_found("20200429-05", "QUARLES")

def check_static_record_l1_20200429_06():
    return ev.record_shape_ok("20200429-06", 1)

def check_static_record_l2_20200429_06():
    return ev.record_shape_ok("20200429-06", 2)

def check_rh_foreign_l1_20200429_06():
    return ev.no_foreign_speaker("20200429-06", 1)

def check_rh_foreign_l2_20200429_06():
    return ev.no_foreign_speaker("20200429-06", 2)

def check_rh_padding_l1_20200429_06():
    return ev.no_padded_entries("20200429-06", 1)

def check_rh_padding_l2_20200429_06():
    return ev.no_padded_entries("20200429-06", 2)

def check_po_roster_20200429_06_BRAINARD():
    return ev.roster_speaker_found("20200429-06", "BRAINARD")

def check_po_roster_20200429_06_QUARLES():
    return ev.roster_speaker_found("20200429-06", "QUARLES")

def check_po_roster_20200429_06_KASHKARI():
    return ev.roster_speaker_found("20200429-06", "KASHKARI")

def check_static_record_l1_20200429_07():
    return ev.record_shape_ok("20200429-07", 1)

def check_static_record_l2_20200429_07():
    return ev.record_shape_ok("20200429-07", 2)

def check_rh_foreign_l1_20200429_07():
    return ev.no_foreign_speaker("20200429-07", 1)

def check_rh_foreign_l2_20200429_07():
    return ev.no_foreign_speaker("20200429-07", 2)

def check_rh_padding_l1_20200429_07():
    return ev.no_padded_entries("20200429-07", 1)

def check_rh_padding_l2_20200429_07():
    return ev.no_padded_entries("20200429-07", 2)

def check_po_roster_20200429_07_MESTER():
    return ev.roster_speaker_found("20200429-07", "MESTER")

def check_po_roster_20200429_07_BARKIN():
    return ev.roster_speaker_found("20200429-07", "BARKIN")

def check_po_roster_20200429_07_HARKER():
    return ev.roster_speaker_found("20200429-07", "HARKER")

def check_po_roster_20200429_07_POWELL():
    return ev.roster_speaker_found("20200429-07", "POWELL")

def check_po_roster_20200429_07_ROSENGREN():
    return ev.roster_speaker_found("20200429-07", "ROSENGREN")

def check_po_roster_20200429_07_BOWMAN():
    return ev.roster_speaker_found("20200429-07", "BOWMAN")

def check_static_record_l1_20200429_08():
    return ev.record_shape_ok("20200429-08", 1)

def check_static_record_l2_20200429_08():
    return ev.record_shape_ok("20200429-08", 2)

def check_rh_foreign_l1_20200429_08():
    return ev.no_foreign_speaker("20200429-08", 1)

def check_rh_foreign_l2_20200429_08():
    return ev.no_foreign_speaker("20200429-08", 2)

def check_rh_padding_l1_20200429_08():
    return ev.no_padded_entries("20200429-08", 1)

def check_rh_padding_l2_20200429_08():
    return ev.no_padded_entries("20200429-08", 2)

def check_po_roster_20200429_08_BRAINARD():
    return ev.roster_speaker_found("20200429-08", "BRAINARD")

def check_po_roster_20200429_08_MESTER():
    return ev.roster_speaker_found("20200429-08", "MESTER")

def check_po_roster_20200429_08_HARKER():
    return ev.roster_speaker_found("20200429-08", "HARKER")

def check_po_roster_20200429_08_DALY():
    return ev.roster_speaker_found("20200429-08", "DALY")

def check_po_roster_20200429_08_POWELL():
    return ev.roster_speaker_found("20200429-08", "POWELL")

def check_po_roster_20200429_08_CLARIDA():
    return ev.roster_speaker_found("20200429-08", "CLARIDA")

def check_po_roster_20200429_08_GEORGE():
    return ev.roster_speaker_found("20200429-08", "GEORGE")

def check_po_roster_20200429_08_KASHKARI():
    return ev.roster_speaker_found("20200429-08", "KASHKARI")

def check_po_roster_20200429_08_BOWMAN():
    return ev.roster_speaker_found("20200429-08", "BOWMAN")

def check_po_counter_20200429_08_WILLIAMS():
    return ev.counter_speaker_found("20200429-08", "WILLIAMS")

def check_po_counter_20200429_08_BULLARD():
    return ev.counter_speaker_found("20200429-08", "BULLARD")

def check_po_counter_20200429_08_EVANS():
    return ev.counter_speaker_found("20200429-08", "EVANS")

def check_po_counter_20200429_08_POWELL():
    return ev.counter_speaker_found("20200429-08", "POWELL")

def check_po_counter_20200429_08_CLARIDA():
    return ev.counter_speaker_found("20200429-08", "CLARIDA")

def check_static_record_l1_20200429_09():
    return ev.record_shape_ok("20200429-09", 1)

def check_static_record_l2_20200429_09():
    return ev.record_shape_ok("20200429-09", 2)

def check_rh_foreign_l1_20200429_09():
    return ev.no_foreign_speaker("20200429-09", 1)

def check_rh_foreign_l2_20200429_09():
    return ev.no_foreign_speaker("20200429-09", 2)

def check_rh_padding_l1_20200429_09():
    return ev.no_padded_entries("20200429-09", 1)

def check_rh_padding_l2_20200429_09():
    return ev.no_padded_entries("20200429-09", 2)

def check_po_roster_20200429_09_BRAINARD():
    return ev.roster_speaker_found("20200429-09", "BRAINARD")

def check_po_roster_20200429_09_WILLIAMS():
    return ev.roster_speaker_found("20200429-09", "WILLIAMS")

def check_po_roster_20200429_09_DALY():
    return ev.roster_speaker_found("20200429-09", "DALY")

def check_po_roster_20200429_09_POWELL():
    return ev.roster_speaker_found("20200429-09", "POWELL")

def check_static_record_l1_20200429_10():
    return ev.record_shape_ok("20200429-10", 1)

def check_static_record_l2_20200429_10():
    return ev.record_shape_ok("20200429-10", 2)

def check_rh_foreign_l1_20200429_10():
    return ev.no_foreign_speaker("20200429-10", 1)

def check_rh_foreign_l2_20200429_10():
    return ev.no_foreign_speaker("20200429-10", 2)

def check_rh_padding_l1_20200429_10():
    return ev.no_padded_entries("20200429-10", 1)

def check_rh_padding_l2_20200429_10():
    return ev.no_padded_entries("20200429-10", 2)

def check_po_roster_20200429_10_MESTER():
    return ev.roster_speaker_found("20200429-10", "MESTER")

def check_po_roster_20200429_10_DALY():
    return ev.roster_speaker_found("20200429-10", "DALY")

def check_po_roster_20200429_10_CLARIDA():
    return ev.roster_speaker_found("20200429-10", "CLARIDA")

def check_po_roster_20200429_10_BOWMAN():
    return ev.roster_speaker_found("20200429-10", "BOWMAN")

def check_po_counter_20200429_10_CLARIDA():
    return ev.counter_speaker_found("20200429-10", "CLARIDA")

def check_static_record_l1_20200429_11():
    return ev.record_shape_ok("20200429-11", 1)

def check_static_record_l2_20200429_11():
    return ev.record_shape_ok("20200429-11", 2)

def check_rh_foreign_l1_20200429_11():
    return ev.no_foreign_speaker("20200429-11", 1)

def check_rh_foreign_l2_20200429_11():
    return ev.no_foreign_speaker("20200429-11", 2)

def check_rh_padding_l1_20200429_11():
    return ev.no_padded_entries("20200429-11", 1)

def check_rh_padding_l2_20200429_11():
    return ev.no_padded_entries("20200429-11", 2)

def check_po_roster_20200429_11_CLARIDA():
    return ev.roster_speaker_found("20200429-11", "CLARIDA")

def check_po_counter_20200429_11_WILLIAMS():
    return ev.counter_speaker_found("20200429-11", "WILLIAMS")

def check_po_counter_20200429_11_BARKIN():
    return ev.counter_speaker_found("20200429-11", "BARKIN")

def check_po_counter_20200429_11_GEORGE():
    return ev.counter_speaker_found("20200429-11", "GEORGE")

def check_static_record_l1_20200429_12():
    return ev.record_shape_ok("20200429-12", 1)

def check_static_record_l2_20200429_12():
    return ev.record_shape_ok("20200429-12", 2)

def check_rh_foreign_l1_20200429_12():
    return ev.no_foreign_speaker("20200429-12", 1)

def check_rh_foreign_l2_20200429_12():
    return ev.no_foreign_speaker("20200429-12", 2)

def check_rh_padding_l1_20200429_12():
    return ev.no_padded_entries("20200429-12", 1)

def check_rh_padding_l2_20200429_12():
    return ev.no_padded_entries("20200429-12", 2)

def check_po_roster_20200429_12_BRAINARD():
    return ev.roster_speaker_found("20200429-12", "BRAINARD")

def check_po_roster_20200429_12_MESTER():
    return ev.roster_speaker_found("20200429-12", "MESTER")

def check_po_roster_20200429_12_DALY():
    return ev.roster_speaker_found("20200429-12", "DALY")

def check_po_roster_20200429_12_CLARIDA():
    return ev.roster_speaker_found("20200429-12", "CLARIDA")

def check_po_counter_20200429_12_MESTER():
    return ev.counter_speaker_found("20200429-12", "MESTER")

def check_po_counter_20200429_12_GEORGE():
    return ev.counter_speaker_found("20200429-12", "GEORGE")

def check_static_record_l1_20200610_01():
    return ev.record_shape_ok("20200610-01", 1)

def check_static_record_l2_20200610_01():
    return ev.record_shape_ok("20200610-01", 2)

def check_rh_foreign_l1_20200610_01():
    return ev.no_foreign_speaker("20200610-01", 1)

def check_rh_foreign_l2_20200610_01():
    return ev.no_foreign_speaker("20200610-01", 2)

def check_rh_padding_l1_20200610_01():
    return ev.no_padded_entries("20200610-01", 1)

def check_rh_padding_l2_20200610_01():
    return ev.no_padded_entries("20200610-01", 2)

def check_po_roster_20200610_01_WILLIAMS():
    return ev.roster_speaker_found("20200610-01", "WILLIAMS")

def check_po_roster_20200610_01_BRAINARD():
    return ev.roster_speaker_found("20200610-01", "BRAINARD")

def check_po_roster_20200610_01_KASHKARI():
    return ev.roster_speaker_found("20200610-01", "KASHKARI")

def check_po_roster_20200610_01_ROSENGREN():
    return ev.roster_speaker_found("20200610-01", "ROSENGREN")

def check_po_roster_20200610_01_GEORGE():
    return ev.roster_speaker_found("20200610-01", "GEORGE")

def check_po_roster_20200610_01_MESTER():
    return ev.roster_speaker_found("20200610-01", "MESTER")

def check_po_roster_20200610_01_DALY():
    return ev.roster_speaker_found("20200610-01", "DALY")

def check_po_roster_20200610_01_POWELL():
    return ev.roster_speaker_found("20200610-01", "POWELL")

def check_po_roster_20200610_01_EVANS():
    return ev.roster_speaker_found("20200610-01", "EVANS")

def check_po_counter_20200610_01_BOSTIC():
    return ev.counter_speaker_found("20200610-01", "BOSTIC")

def check_static_record_l1_20200610_02():
    return ev.record_shape_ok("20200610-02", 1)

def check_static_record_l2_20200610_02():
    return ev.record_shape_ok("20200610-02", 2)

def check_rh_foreign_l1_20200610_02():
    return ev.no_foreign_speaker("20200610-02", 1)

def check_rh_foreign_l2_20200610_02():
    return ev.no_foreign_speaker("20200610-02", 2)

def check_rh_padding_l1_20200610_02():
    return ev.no_padded_entries("20200610-02", 1)

def check_rh_padding_l2_20200610_02():
    return ev.no_padded_entries("20200610-02", 2)

def check_po_roster_20200610_02_BRAINARD():
    return ev.roster_speaker_found("20200610-02", "BRAINARD")

def check_po_roster_20200610_02_KASHKARI():
    return ev.roster_speaker_found("20200610-02", "KASHKARI")

def check_po_roster_20200610_02_WILLIAMS():
    return ev.roster_speaker_found("20200610-02", "WILLIAMS")

def check_po_roster_20200610_02_DALY():
    return ev.roster_speaker_found("20200610-02", "DALY")

def check_po_roster_20200610_02_POWELL():
    return ev.roster_speaker_found("20200610-02", "POWELL")

def check_po_roster_20200610_02_EVANS():
    return ev.roster_speaker_found("20200610-02", "EVANS")

def check_po_roster_20200610_02_CLARIDA():
    return ev.roster_speaker_found("20200610-02", "CLARIDA")

def check_po_counter_20200610_02_BARKIN():
    return ev.counter_speaker_found("20200610-02", "BARKIN")

def check_po_counter_20200610_02_BULLARD():
    return ev.counter_speaker_found("20200610-02", "BULLARD")

def check_po_counter_20200610_02_GEORGE():
    return ev.counter_speaker_found("20200610-02", "GEORGE")

def check_po_counter_20200610_02_HARKER():
    return ev.counter_speaker_found("20200610-02", "HARKER")

def check_static_record_l1_20200610_03():
    return ev.record_shape_ok("20200610-03", 1)

def check_static_record_l2_20200610_03():
    return ev.record_shape_ok("20200610-03", 2)

def check_rh_foreign_l1_20200610_03():
    return ev.no_foreign_speaker("20200610-03", 1)

def check_rh_foreign_l2_20200610_03():
    return ev.no_foreign_speaker("20200610-03", 2)

def check_rh_padding_l1_20200610_03():
    return ev.no_padded_entries("20200610-03", 1)

def check_rh_padding_l2_20200610_03():
    return ev.no_padded_entries("20200610-03", 2)

def check_po_roster_20200610_03_ROSENGREN():
    return ev.roster_speaker_found("20200610-03", "ROSENGREN")

def check_po_roster_20200610_03_BARKIN():
    return ev.roster_speaker_found("20200610-03", "BARKIN")

def check_po_roster_20200610_03_BOWMAN():
    return ev.roster_speaker_found("20200610-03", "BOWMAN")

def check_po_counter_20200610_03_BRAINARD():
    return ev.counter_speaker_found("20200610-03", "BRAINARD")

def check_po_counter_20200610_03_HARKER():
    return ev.counter_speaker_found("20200610-03", "HARKER")

def check_po_counter_20200610_03_EVANS():
    return ev.counter_speaker_found("20200610-03", "EVANS")

def check_static_record_l1_20200610_04():
    return ev.record_shape_ok("20200610-04", 1)

def check_static_record_l2_20200610_04():
    return ev.record_shape_ok("20200610-04", 2)

def check_rh_foreign_l1_20200610_04():
    return ev.no_foreign_speaker("20200610-04", 1)

def check_rh_foreign_l2_20200610_04():
    return ev.no_foreign_speaker("20200610-04", 2)

def check_rh_padding_l1_20200610_04():
    return ev.no_padded_entries("20200610-04", 1)

def check_rh_padding_l2_20200610_04():
    return ev.no_padded_entries("20200610-04", 2)

def check_po_roster_20200610_04_BARKIN():
    return ev.roster_speaker_found("20200610-04", "BARKIN")

def check_po_roster_20200610_04_MESTER():
    return ev.roster_speaker_found("20200610-04", "MESTER")

def check_po_roster_20200610_04_KAPLAN():
    return ev.roster_speaker_found("20200610-04", "KAPLAN")

def check_po_roster_20200610_04_EVANS():
    return ev.roster_speaker_found("20200610-04", "EVANS")

def check_po_counter_20200610_04_WILLIAMS():
    return ev.counter_speaker_found("20200610-04", "WILLIAMS")

def check_po_counter_20200610_04_KASHKARI():
    return ev.counter_speaker_found("20200610-04", "KASHKARI")

def check_static_record_l1_20200610_05():
    return ev.record_shape_ok("20200610-05", 1)

def check_static_record_l2_20200610_05():
    return ev.record_shape_ok("20200610-05", 2)

def check_rh_foreign_l1_20200610_05():
    return ev.no_foreign_speaker("20200610-05", 1)

def check_rh_foreign_l2_20200610_05():
    return ev.no_foreign_speaker("20200610-05", 2)

def check_rh_padding_l1_20200610_05():
    return ev.no_padded_entries("20200610-05", 1)

def check_rh_padding_l2_20200610_05():
    return ev.no_padded_entries("20200610-05", 2)

def check_po_roster_20200610_05_ROSENGREN():
    return ev.roster_speaker_found("20200610-05", "ROSENGREN")

def check_po_roster_20200610_05_GEORGE():
    return ev.roster_speaker_found("20200610-05", "GEORGE")

def check_po_roster_20200610_05_BOSTIC():
    return ev.roster_speaker_found("20200610-05", "BOSTIC")

def check_po_roster_20200610_05_BARKIN():
    return ev.roster_speaker_found("20200610-05", "BARKIN")

def check_po_roster_20200610_05_BULLARD():
    return ev.roster_speaker_found("20200610-05", "BULLARD")

def check_po_roster_20200610_05_MESTER():
    return ev.roster_speaker_found("20200610-05", "MESTER")

def check_po_roster_20200610_05_POWELL():
    return ev.roster_speaker_found("20200610-05", "POWELL")

def check_po_roster_20200610_05_KAPLAN():
    return ev.roster_speaker_found("20200610-05", "KAPLAN")

def check_po_roster_20200610_05_HARKER():
    return ev.roster_speaker_found("20200610-05", "HARKER")

def check_po_roster_20200610_05_EVANS():
    return ev.roster_speaker_found("20200610-05", "EVANS")

def check_po_counter_20200610_05_WILLIAMS():
    return ev.counter_speaker_found("20200610-05", "WILLIAMS")

def check_po_counter_20200610_05_BULLARD():
    return ev.counter_speaker_found("20200610-05", "BULLARD")

def check_po_counter_20200610_05_QUARLES():
    return ev.counter_speaker_found("20200610-05", "QUARLES")

def check_static_record_l1_20200610_06():
    return ev.record_shape_ok("20200610-06", 1)

def check_static_record_l2_20200610_06():
    return ev.record_shape_ok("20200610-06", 2)

def check_rh_foreign_l1_20200610_06():
    return ev.no_foreign_speaker("20200610-06", 1)

def check_rh_foreign_l2_20200610_06():
    return ev.no_foreign_speaker("20200610-06", 2)

def check_rh_padding_l1_20200610_06():
    return ev.no_padded_entries("20200610-06", 1)

def check_rh_padding_l2_20200610_06():
    return ev.no_padded_entries("20200610-06", 2)

def check_po_roster_20200610_06_GEORGE():
    return ev.roster_speaker_found("20200610-06", "GEORGE")

def check_po_roster_20200610_06_BARKIN():
    return ev.roster_speaker_found("20200610-06", "BARKIN")

def check_po_roster_20200610_06_KAPLAN():
    return ev.roster_speaker_found("20200610-06", "KAPLAN")

def check_po_roster_20200610_06_BOWMAN():
    return ev.roster_speaker_found("20200610-06", "BOWMAN")

def check_po_counter_20200610_06_KASHKARI():
    return ev.counter_speaker_found("20200610-06", "KASHKARI")

def check_po_counter_20200610_06_ROSENGREN():
    return ev.counter_speaker_found("20200610-06", "ROSENGREN")

def check_po_counter_20200610_06_BOSTIC():
    return ev.counter_speaker_found("20200610-06", "BOSTIC")

def check_po_counter_20200610_06_MESTER():
    return ev.counter_speaker_found("20200610-06", "MESTER")

def check_po_counter_20200610_06_DALY():
    return ev.counter_speaker_found("20200610-06", "DALY")

def check_po_counter_20200610_06_POWELL():
    return ev.counter_speaker_found("20200610-06", "POWELL")

def check_po_counter_20200610_06_HARKER():
    return ev.counter_speaker_found("20200610-06", "HARKER")

def check_po_counter_20200610_06_EVANS():
    return ev.counter_speaker_found("20200610-06", "EVANS")

def check_po_counter_20200610_06_CLARIDA():
    return ev.counter_speaker_found("20200610-06", "CLARIDA")

def check_static_record_l1_20200610_07():
    return ev.record_shape_ok("20200610-07", 1)

def check_static_record_l2_20200610_07():
    return ev.record_shape_ok("20200610-07", 2)

def check_rh_foreign_l1_20200610_07():
    return ev.no_foreign_speaker("20200610-07", 1)

def check_rh_foreign_l2_20200610_07():
    return ev.no_foreign_speaker("20200610-07", 2)

def check_rh_padding_l1_20200610_07():
    return ev.no_padded_entries("20200610-07", 1)

def check_rh_padding_l2_20200610_07():
    return ev.no_padded_entries("20200610-07", 2)

def check_po_roster_20200610_07_ROSENGREN():
    return ev.roster_speaker_found("20200610-07", "ROSENGREN")

def check_po_roster_20200610_07_BULLARD():
    return ev.roster_speaker_found("20200610-07", "BULLARD")

def check_po_roster_20200610_07_GEORGE():
    return ev.roster_speaker_found("20200610-07", "GEORGE")

def check_po_roster_20200610_07_BOSTIC():
    return ev.roster_speaker_found("20200610-07", "BOSTIC")

def check_po_roster_20200610_07_MESTER():
    return ev.roster_speaker_found("20200610-07", "MESTER")

def check_po_roster_20200610_07_DALY():
    return ev.roster_speaker_found("20200610-07", "DALY")

def check_po_roster_20200610_07_QUARLES():
    return ev.roster_speaker_found("20200610-07", "QUARLES")

def check_po_roster_20200610_07_POWELL():
    return ev.roster_speaker_found("20200610-07", "POWELL")

def check_po_roster_20200610_07_KAPLAN():
    return ev.roster_speaker_found("20200610-07", "KAPLAN")

def check_po_roster_20200610_07_HARKER():
    return ev.roster_speaker_found("20200610-07", "HARKER")

def check_po_roster_20200610_07_EVANS():
    return ev.roster_speaker_found("20200610-07", "EVANS")

def check_po_roster_20200610_07_BOWMAN():
    return ev.roster_speaker_found("20200610-07", "BOWMAN")

def check_po_counter_20200610_07_BRAINARD():
    return ev.counter_speaker_found("20200610-07", "BRAINARD")

def check_po_counter_20200610_07_KASHKARI():
    return ev.counter_speaker_found("20200610-07", "KASHKARI")

def check_static_record_l1_20200610_08():
    return ev.record_shape_ok("20200610-08", 1)

def check_static_record_l2_20200610_08():
    return ev.record_shape_ok("20200610-08", 2)

def check_rh_foreign_l1_20200610_08():
    return ev.no_foreign_speaker("20200610-08", 1)

def check_rh_foreign_l2_20200610_08():
    return ev.no_foreign_speaker("20200610-08", 2)

def check_rh_padding_l1_20200610_08():
    return ev.no_padded_entries("20200610-08", 1)

def check_rh_padding_l2_20200610_08():
    return ev.no_padded_entries("20200610-08", 2)

def check_po_roster_20200610_08_BRAINARD():
    return ev.roster_speaker_found("20200610-08", "BRAINARD")

def check_po_roster_20200610_08_ROSENGREN():
    return ev.roster_speaker_found("20200610-08", "ROSENGREN")

def check_po_roster_20200610_08_KASHKARI():
    return ev.roster_speaker_found("20200610-08", "KASHKARI")

def check_po_roster_20200610_08_WILLIAMS():
    return ev.roster_speaker_found("20200610-08", "WILLIAMS")

def check_po_roster_20200610_08_BULLARD():
    return ev.roster_speaker_found("20200610-08", "BULLARD")

def check_po_roster_20200610_08_GEORGE():
    return ev.roster_speaker_found("20200610-08", "GEORGE")

def check_po_roster_20200610_08_BOSTIC():
    return ev.roster_speaker_found("20200610-08", "BOSTIC")

def check_po_roster_20200610_08_BARKIN():
    return ev.roster_speaker_found("20200610-08", "BARKIN")

def check_po_roster_20200610_08_MESTER():
    return ev.roster_speaker_found("20200610-08", "MESTER")

def check_po_roster_20200610_08_DALY():
    return ev.roster_speaker_found("20200610-08", "DALY")

def check_po_roster_20200610_08_QUARLES():
    return ev.roster_speaker_found("20200610-08", "QUARLES")

def check_po_roster_20200610_08_KAPLAN():
    return ev.roster_speaker_found("20200610-08", "KAPLAN")

def check_po_roster_20200610_08_HARKER():
    return ev.roster_speaker_found("20200610-08", "HARKER")

def check_po_roster_20200610_08_EVANS():
    return ev.roster_speaker_found("20200610-08", "EVANS")

def check_po_roster_20200610_08_CLARIDA():
    return ev.roster_speaker_found("20200610-08", "CLARIDA")

def check_po_roster_20200610_08_BOWMAN():
    return ev.roster_speaker_found("20200610-08", "BOWMAN")

def check_po_counter_20200610_08_KASHKARI():
    return ev.counter_speaker_found("20200610-08", "KASHKARI")

def check_static_record_l1_20200610_09():
    return ev.record_shape_ok("20200610-09", 1)

def check_static_record_l2_20200610_09():
    return ev.record_shape_ok("20200610-09", 2)

def check_rh_foreign_l1_20200610_09():
    return ev.no_foreign_speaker("20200610-09", 1)

def check_rh_foreign_l2_20200610_09():
    return ev.no_foreign_speaker("20200610-09", 2)

def check_rh_padding_l1_20200610_09():
    return ev.no_padded_entries("20200610-09", 1)

def check_rh_padding_l2_20200610_09():
    return ev.no_padded_entries("20200610-09", 2)

def check_po_roster_20200610_09_BOSTIC():
    return ev.roster_speaker_found("20200610-09", "BOSTIC")

def check_po_roster_20200610_09_GEORGE():
    return ev.roster_speaker_found("20200610-09", "GEORGE")

def check_po_roster_20200610_09_DALY():
    return ev.roster_speaker_found("20200610-09", "DALY")

def check_po_roster_20200610_09_MESTER():
    return ev.roster_speaker_found("20200610-09", "MESTER")

def check_po_roster_20200610_09_HARKER():
    return ev.roster_speaker_found("20200610-09", "HARKER")

def check_po_roster_20200610_09_EVANS():
    return ev.roster_speaker_found("20200610-09", "EVANS")

def check_static_record_l1_20200610_10():
    return ev.record_shape_ok("20200610-10", 1)

def check_static_record_l2_20200610_10():
    return ev.record_shape_ok("20200610-10", 2)

def check_rh_foreign_l1_20200610_10():
    return ev.no_foreign_speaker("20200610-10", 1)

def check_rh_foreign_l2_20200610_10():
    return ev.no_foreign_speaker("20200610-10", 2)

def check_rh_padding_l1_20200610_10():
    return ev.no_padded_entries("20200610-10", 1)

def check_rh_padding_l2_20200610_10():
    return ev.no_padded_entries("20200610-10", 2)

def check_po_roster_20200610_10_BRAINARD():
    return ev.roster_speaker_found("20200610-10", "BRAINARD")

def check_po_roster_20200610_10_WILLIAMS():
    return ev.roster_speaker_found("20200610-10", "WILLIAMS")

def check_po_roster_20200610_10_KASHKARI():
    return ev.roster_speaker_found("20200610-10", "KASHKARI")

def check_po_roster_20200610_10_DALY():
    return ev.roster_speaker_found("20200610-10", "DALY")

def check_po_roster_20200610_10_EVANS():
    return ev.roster_speaker_found("20200610-10", "EVANS")

def check_po_counter_20200610_10_ROSENGREN():
    return ev.counter_speaker_found("20200610-10", "ROSENGREN")

def check_po_counter_20200610_10_BULLARD():
    return ev.counter_speaker_found("20200610-10", "BULLARD")

def check_po_counter_20200610_10_BOSTIC():
    return ev.counter_speaker_found("20200610-10", "BOSTIC")

def check_po_counter_20200610_10_GEORGE():
    return ev.counter_speaker_found("20200610-10", "GEORGE")

def check_po_counter_20200610_10_DALY():
    return ev.counter_speaker_found("20200610-10", "DALY")

def check_po_counter_20200610_10_HARKER():
    return ev.counter_speaker_found("20200610-10", "HARKER")

def check_po_counter_20200610_10_KAPLAN():
    return ev.counter_speaker_found("20200610-10", "KAPLAN")

def check_po_counter_20200610_10_EVANS():
    return ev.counter_speaker_found("20200610-10", "EVANS")

def check_po_counter_20200610_10_BOWMAN():
    return ev.counter_speaker_found("20200610-10", "BOWMAN")

def check_static_record_l1_20200610_11():
    return ev.record_shape_ok("20200610-11", 1)

def check_static_record_l2_20200610_11():
    return ev.record_shape_ok("20200610-11", 2)

def check_rh_foreign_l1_20200610_11():
    return ev.no_foreign_speaker("20200610-11", 1)

def check_rh_foreign_l2_20200610_11():
    return ev.no_foreign_speaker("20200610-11", 2)

def check_rh_padding_l1_20200610_11():
    return ev.no_padded_entries("20200610-11", 1)

def check_rh_padding_l2_20200610_11():
    return ev.no_padded_entries("20200610-11", 2)

def check_po_roster_20200610_11_WILLIAMS():
    return ev.roster_speaker_found("20200610-11", "WILLIAMS")

def check_po_roster_20200610_11_KASHKARI():
    return ev.roster_speaker_found("20200610-11", "KASHKARI")

def check_po_roster_20200610_11_BRAINARD():
    return ev.roster_speaker_found("20200610-11", "BRAINARD")

def check_po_roster_20200610_11_ROSENGREN():
    return ev.roster_speaker_found("20200610-11", "ROSENGREN")

def check_po_roster_20200610_11_BOSTIC():
    return ev.roster_speaker_found("20200610-11", "BOSTIC")

def check_po_roster_20200610_11_GEORGE():
    return ev.roster_speaker_found("20200610-11", "GEORGE")

def check_po_roster_20200610_11_DALY():
    return ev.roster_speaker_found("20200610-11", "DALY")

def check_po_roster_20200610_11_MESTER():
    return ev.roster_speaker_found("20200610-11", "MESTER")

def check_po_roster_20200610_11_POWELL():
    return ev.roster_speaker_found("20200610-11", "POWELL")

def check_po_roster_20200610_11_KAPLAN():
    return ev.roster_speaker_found("20200610-11", "KAPLAN")

def check_po_roster_20200610_11_CLARIDA():
    return ev.roster_speaker_found("20200610-11", "CLARIDA")

def check_po_roster_20200610_11_EVANS():
    return ev.roster_speaker_found("20200610-11", "EVANS")

def check_static_record_l1_20200610_12():
    return ev.record_shape_ok("20200610-12", 1)

def check_static_record_l2_20200610_12():
    return ev.record_shape_ok("20200610-12", 2)

def check_rh_foreign_l1_20200610_12():
    return ev.no_foreign_speaker("20200610-12", 1)

def check_rh_foreign_l2_20200610_12():
    return ev.no_foreign_speaker("20200610-12", 2)

def check_rh_padding_l1_20200610_12():
    return ev.no_padded_entries("20200610-12", 1)

def check_rh_padding_l2_20200610_12():
    return ev.no_padded_entries("20200610-12", 2)

def check_po_roster_20200610_12_WILLIAMS():
    return ev.roster_speaker_found("20200610-12", "WILLIAMS")

def check_po_roster_20200610_12_BRAINARD():
    return ev.roster_speaker_found("20200610-12", "BRAINARD")

def check_po_roster_20200610_12_BULLARD():
    return ev.roster_speaker_found("20200610-12", "BULLARD")

def check_po_roster_20200610_12_BOSTIC():
    return ev.roster_speaker_found("20200610-12", "BOSTIC")

def check_po_roster_20200610_12_MESTER():
    return ev.roster_speaker_found("20200610-12", "MESTER")

def check_po_roster_20200610_12_DALY():
    return ev.roster_speaker_found("20200610-12", "DALY")

def check_po_roster_20200610_12_POWELL():
    return ev.roster_speaker_found("20200610-12", "POWELL")

def check_po_roster_20200610_12_EVANS():
    return ev.roster_speaker_found("20200610-12", "EVANS")

def check_po_roster_20200610_12_CLARIDA():
    return ev.roster_speaker_found("20200610-12", "CLARIDA")

def check_po_counter_20200610_12_BOSTIC():
    return ev.counter_speaker_found("20200610-12", "BOSTIC")

def check_static_record_l1_20200610_13():
    return ev.record_shape_ok("20200610-13", 1)

def check_static_record_l2_20200610_13():
    return ev.record_shape_ok("20200610-13", 2)

def check_rh_foreign_l1_20200610_13():
    return ev.no_foreign_speaker("20200610-13", 1)

def check_rh_foreign_l2_20200610_13():
    return ev.no_foreign_speaker("20200610-13", 2)

def check_rh_padding_l1_20200610_13():
    return ev.no_padded_entries("20200610-13", 1)

def check_rh_padding_l2_20200610_13():
    return ev.no_padded_entries("20200610-13", 2)

def check_po_roster_20200610_13_BARKIN():
    return ev.roster_speaker_found("20200610-13", "BARKIN")

def check_po_roster_20200610_13_QUARLES():
    return ev.roster_speaker_found("20200610-13", "QUARLES")

def check_po_roster_20200610_13_BOWMAN():
    return ev.roster_speaker_found("20200610-13", "BOWMAN")

def check_static_record_l1_20200610_14():
    return ev.record_shape_ok("20200610-14", 1)

def check_static_record_l2_20200610_14():
    return ev.record_shape_ok("20200610-14", 2)

def check_rh_foreign_l1_20200610_14():
    return ev.no_foreign_speaker("20200610-14", 1)

def check_rh_foreign_l2_20200610_14():
    return ev.no_foreign_speaker("20200610-14", 2)

def check_rh_padding_l1_20200610_14():
    return ev.no_padded_entries("20200610-14", 1)

def check_rh_padding_l2_20200610_14():
    return ev.no_padded_entries("20200610-14", 2)

def check_po_roster_20200610_14_GEORGE():
    return ev.roster_speaker_found("20200610-14", "GEORGE")

def check_po_roster_20200610_14_KAPLAN():
    return ev.roster_speaker_found("20200610-14", "KAPLAN")

def check_static_record_l1_20200610_15():
    return ev.record_shape_ok("20200610-15", 1)

def check_static_record_l2_20200610_15():
    return ev.record_shape_ok("20200610-15", 2)

def check_rh_foreign_l1_20200610_15():
    return ev.no_foreign_speaker("20200610-15", 1)

def check_rh_foreign_l2_20200610_15():
    return ev.no_foreign_speaker("20200610-15", 2)

def check_rh_padding_l1_20200610_15():
    return ev.no_padded_entries("20200610-15", 1)

def check_rh_padding_l2_20200610_15():
    return ev.no_padded_entries("20200610-15", 2)

def check_po_roster_20200610_15_KASHKARI():
    return ev.roster_speaker_found("20200610-15", "KASHKARI")

def check_po_roster_20200610_15_BRAINARD():
    return ev.roster_speaker_found("20200610-15", "BRAINARD")

def check_po_roster_20200610_15_GEORGE():
    return ev.roster_speaker_found("20200610-15", "GEORGE")

def check_po_roster_20200610_15_CLARIDA():
    return ev.roster_speaker_found("20200610-15", "CLARIDA")

def check_po_roster_20200610_15_EVANS():
    return ev.roster_speaker_found("20200610-15", "EVANS")

def check_static_record_l1_20200610_16():
    return ev.record_shape_ok("20200610-16", 1)

def check_static_record_l2_20200610_16():
    return ev.record_shape_ok("20200610-16", 2)

def check_rh_foreign_l1_20200610_16():
    return ev.no_foreign_speaker("20200610-16", 1)

def check_rh_foreign_l2_20200610_16():
    return ev.no_foreign_speaker("20200610-16", 2)

def check_rh_padding_l1_20200610_16():
    return ev.no_padded_entries("20200610-16", 1)

def check_rh_padding_l2_20200610_16():
    return ev.no_padded_entries("20200610-16", 2)

def check_po_roster_20200610_16_KASHKARI():
    return ev.roster_speaker_found("20200610-16", "KASHKARI")

def check_po_roster_20200610_16_ROSENGREN():
    return ev.roster_speaker_found("20200610-16", "ROSENGREN")

def check_po_roster_20200610_16_BRAINARD():
    return ev.roster_speaker_found("20200610-16", "BRAINARD")

def check_po_roster_20200610_16_WILLIAMS():
    return ev.roster_speaker_found("20200610-16", "WILLIAMS")

def check_po_roster_20200610_16_BOSTIC():
    return ev.roster_speaker_found("20200610-16", "BOSTIC")

def check_po_roster_20200610_16_MESTER():
    return ev.roster_speaker_found("20200610-16", "MESTER")

def check_po_roster_20200610_16_DALY():
    return ev.roster_speaker_found("20200610-16", "DALY")

def check_po_roster_20200610_16_POWELL():
    return ev.roster_speaker_found("20200610-16", "POWELL")

def check_po_roster_20200610_16_EVANS():
    return ev.roster_speaker_found("20200610-16", "EVANS")

def check_po_roster_20200610_16_CLARIDA():
    return ev.roster_speaker_found("20200610-16", "CLARIDA")

def check_po_counter_20200610_16_BULLARD():
    return ev.counter_speaker_found("20200610-16", "BULLARD")

def check_po_counter_20200610_16_BARKIN():
    return ev.counter_speaker_found("20200610-16", "BARKIN")

def check_po_counter_20200610_16_QUARLES():
    return ev.counter_speaker_found("20200610-16", "QUARLES")

def check_po_counter_20200610_16_BOWMAN():
    return ev.counter_speaker_found("20200610-16", "BOWMAN")

def check_static_record_l1_20200610_17():
    return ev.record_shape_ok("20200610-17", 1)

def check_static_record_l2_20200610_17():
    return ev.record_shape_ok("20200610-17", 2)

def check_rh_foreign_l1_20200610_17():
    return ev.no_foreign_speaker("20200610-17", 1)

def check_rh_foreign_l2_20200610_17():
    return ev.no_foreign_speaker("20200610-17", 2)

def check_rh_padding_l1_20200610_17():
    return ev.no_padded_entries("20200610-17", 1)

def check_rh_padding_l2_20200610_17():
    return ev.no_padded_entries("20200610-17", 2)

def check_po_roster_20200610_17_ROSENGREN():
    return ev.roster_speaker_found("20200610-17", "ROSENGREN")

def check_po_roster_20200610_17_BRAINARD():
    return ev.roster_speaker_found("20200610-17", "BRAINARD")

def check_po_roster_20200610_17_BARKIN():
    return ev.roster_speaker_found("20200610-17", "BARKIN")

def check_po_roster_20200610_17_POWELL():
    return ev.roster_speaker_found("20200610-17", "POWELL")

def check_static_record_l1_20200610_18():
    return ev.record_shape_ok("20200610-18", 1)

def check_static_record_l2_20200610_18():
    return ev.record_shape_ok("20200610-18", 2)

def check_rh_foreign_l1_20200610_18():
    return ev.no_foreign_speaker("20200610-18", 1)

def check_rh_foreign_l2_20200610_18():
    return ev.no_foreign_speaker("20200610-18", 2)

def check_rh_padding_l1_20200610_18():
    return ev.no_padded_entries("20200610-18", 1)

def check_rh_padding_l2_20200610_18():
    return ev.no_padded_entries("20200610-18", 2)

def check_po_roster_20200610_18_WILLIAMS():
    return ev.roster_speaker_found("20200610-18", "WILLIAMS")

def check_po_roster_20200610_18_BRAINARD():
    return ev.roster_speaker_found("20200610-18", "BRAINARD")

def check_po_roster_20200610_18_KASHKARI():
    return ev.roster_speaker_found("20200610-18", "KASHKARI")

def check_po_roster_20200610_18_ROSENGREN():
    return ev.roster_speaker_found("20200610-18", "ROSENGREN")

def check_po_roster_20200610_18_GEORGE():
    return ev.roster_speaker_found("20200610-18", "GEORGE")

def check_po_roster_20200610_18_BARKIN():
    return ev.roster_speaker_found("20200610-18", "BARKIN")

def check_po_roster_20200610_18_BOSTIC():
    return ev.roster_speaker_found("20200610-18", "BOSTIC")

def check_po_roster_20200610_18_MESTER():
    return ev.roster_speaker_found("20200610-18", "MESTER")

def check_po_roster_20200610_18_DALY():
    return ev.roster_speaker_found("20200610-18", "DALY")

def check_po_roster_20200610_18_QUARLES():
    return ev.roster_speaker_found("20200610-18", "QUARLES")

def check_po_roster_20200610_18_POWELL():
    return ev.roster_speaker_found("20200610-18", "POWELL")

def check_po_roster_20200610_18_KAPLAN():
    return ev.roster_speaker_found("20200610-18", "KAPLAN")

def check_po_roster_20200610_18_EVANS():
    return ev.roster_speaker_found("20200610-18", "EVANS")

def check_po_roster_20200610_18_CLARIDA():
    return ev.roster_speaker_found("20200610-18", "CLARIDA")

def check_po_counter_20200610_18_BOSTIC():
    return ev.counter_speaker_found("20200610-18", "BOSTIC")

def check_static_record_l1_20200610_19():
    return ev.record_shape_ok("20200610-19", 1)

def check_static_record_l2_20200610_19():
    return ev.record_shape_ok("20200610-19", 2)

def check_rh_foreign_l1_20200610_19():
    return ev.no_foreign_speaker("20200610-19", 1)

def check_rh_foreign_l2_20200610_19():
    return ev.no_foreign_speaker("20200610-19", 2)

def check_rh_padding_l1_20200610_19():
    return ev.no_padded_entries("20200610-19", 1)

def check_rh_padding_l2_20200610_19():
    return ev.no_padded_entries("20200610-19", 2)

def check_po_roster_20200610_19_KASHKARI():
    return ev.roster_speaker_found("20200610-19", "KASHKARI")

def check_po_roster_20200610_19_BRAINARD():
    return ev.roster_speaker_found("20200610-19", "BRAINARD")

def check_po_roster_20200610_19_WILLIAMS():
    return ev.roster_speaker_found("20200610-19", "WILLIAMS")

def check_po_roster_20200610_19_ROSENGREN():
    return ev.roster_speaker_found("20200610-19", "ROSENGREN")

def check_po_roster_20200610_19_DALY():
    return ev.roster_speaker_found("20200610-19", "DALY")

def check_po_roster_20200610_19_MESTER():
    return ev.roster_speaker_found("20200610-19", "MESTER")

def check_po_roster_20200610_19_KAPLAN():
    return ev.roster_speaker_found("20200610-19", "KAPLAN")

def check_po_roster_20200610_19_POWELL():
    return ev.roster_speaker_found("20200610-19", "POWELL")

def check_po_roster_20200610_19_EVANS():
    return ev.roster_speaker_found("20200610-19", "EVANS")

def check_po_roster_20200610_19_CLARIDA():
    return ev.roster_speaker_found("20200610-19", "CLARIDA")

def check_po_counter_20200610_19_GEORGE():
    return ev.counter_speaker_found("20200610-19", "GEORGE")

def check_po_counter_20200610_19_BARKIN():
    return ev.counter_speaker_found("20200610-19", "BARKIN")

def check_po_counter_20200610_19_QUARLES():
    return ev.counter_speaker_found("20200610-19", "QUARLES")

def check_po_counter_20200610_19_HARKER():
    return ev.counter_speaker_found("20200610-19", "HARKER")

def check_static_record_l1_20200610_20():
    return ev.record_shape_ok("20200610-20", 1)

def check_static_record_l2_20200610_20():
    return ev.record_shape_ok("20200610-20", 2)

def check_rh_foreign_l1_20200610_20():
    return ev.no_foreign_speaker("20200610-20", 1)

def check_rh_foreign_l2_20200610_20():
    return ev.no_foreign_speaker("20200610-20", 2)

def check_rh_padding_l1_20200610_20():
    return ev.no_padded_entries("20200610-20", 1)

def check_rh_padding_l2_20200610_20():
    return ev.no_padded_entries("20200610-20", 2)

def check_po_roster_20200610_20_WILLIAMS():
    return ev.roster_speaker_found("20200610-20", "WILLIAMS")

def check_po_roster_20200610_20_BRAINARD():
    return ev.roster_speaker_found("20200610-20", "BRAINARD")

def check_po_roster_20200610_20_DALY():
    return ev.roster_speaker_found("20200610-20", "DALY")

def check_po_roster_20200610_20_MESTER():
    return ev.roster_speaker_found("20200610-20", "MESTER")

def check_po_roster_20200610_20_POWELL():
    return ev.roster_speaker_found("20200610-20", "POWELL")

def check_po_roster_20200610_20_EVANS():
    return ev.roster_speaker_found("20200610-20", "EVANS")

def check_static_record_l1_20200729_01():
    return ev.record_shape_ok("20200729-01", 1)

def check_static_record_l2_20200729_01():
    return ev.record_shape_ok("20200729-01", 2)

def check_rh_foreign_l1_20200729_01():
    return ev.no_foreign_speaker("20200729-01", 1)

def check_rh_foreign_l2_20200729_01():
    return ev.no_foreign_speaker("20200729-01", 2)

def check_rh_padding_l1_20200729_01():
    return ev.no_padded_entries("20200729-01", 1)

def check_rh_padding_l2_20200729_01():
    return ev.no_padded_entries("20200729-01", 2)

def check_po_roster_20200729_01_MESTER():
    return ev.roster_speaker_found("20200729-01", "MESTER")

def check_po_roster_20200729_01_EVANS():
    return ev.roster_speaker_found("20200729-01", "EVANS")

def check_po_roster_20200729_01_BOSTIC():
    return ev.roster_speaker_found("20200729-01", "BOSTIC")

def check_po_roster_20200729_01_GEORGE():
    return ev.roster_speaker_found("20200729-01", "GEORGE")

def check_po_roster_20200729_01_BOWMAN():
    return ev.roster_speaker_found("20200729-01", "BOWMAN")

def check_po_roster_20200729_01_BARKIN():
    return ev.roster_speaker_found("20200729-01", "BARKIN")

def check_static_record_l1_20200729_02():
    return ev.record_shape_ok("20200729-02", 1)

def check_static_record_l2_20200729_02():
    return ev.record_shape_ok("20200729-02", 2)

def check_rh_foreign_l1_20200729_02():
    return ev.no_foreign_speaker("20200729-02", 1)

def check_rh_foreign_l2_20200729_02():
    return ev.no_foreign_speaker("20200729-02", 2)

def check_rh_padding_l1_20200729_02():
    return ev.no_padded_entries("20200729-02", 1)

def check_rh_padding_l2_20200729_02():
    return ev.no_padded_entries("20200729-02", 2)

def check_po_roster_20200729_02_QUARLES():
    return ev.roster_speaker_found("20200729-02", "QUARLES")

def check_po_roster_20200729_02_CLARIDA():
    return ev.roster_speaker_found("20200729-02", "CLARIDA")

def check_po_roster_20200729_02_KAPLAN():
    return ev.roster_speaker_found("20200729-02", "KAPLAN")

def check_po_roster_20200729_02_EVANS():
    return ev.roster_speaker_found("20200729-02", "EVANS")

def check_po_roster_20200729_02_BOSTIC():
    return ev.roster_speaker_found("20200729-02", "BOSTIC")

def check_po_roster_20200729_02_ROSENGREN():
    return ev.roster_speaker_found("20200729-02", "ROSENGREN")

def check_po_roster_20200729_02_BOWMAN():
    return ev.roster_speaker_found("20200729-02", "BOWMAN")

def check_po_roster_20200729_02_BARKIN():
    return ev.roster_speaker_found("20200729-02", "BARKIN")

def check_static_record_l1_20200729_03():
    return ev.record_shape_ok("20200729-03", 1)

def check_static_record_l2_20200729_03():
    return ev.record_shape_ok("20200729-03", 2)

def check_rh_foreign_l1_20200729_03():
    return ev.no_foreign_speaker("20200729-03", 1)

def check_rh_foreign_l2_20200729_03():
    return ev.no_foreign_speaker("20200729-03", 2)

def check_rh_padding_l1_20200729_03():
    return ev.no_padded_entries("20200729-03", 1)

def check_rh_padding_l2_20200729_03():
    return ev.no_padded_entries("20200729-03", 2)

def check_po_roster_20200729_03_MESTER():
    return ev.roster_speaker_found("20200729-03", "MESTER")

def check_po_roster_20200729_03_BULLARD():
    return ev.roster_speaker_found("20200729-03", "BULLARD")

def check_po_roster_20200729_03_BRAINARD():
    return ev.roster_speaker_found("20200729-03", "BRAINARD")

def check_po_roster_20200729_03_DALY():
    return ev.roster_speaker_found("20200729-03", "DALY")

def check_po_roster_20200729_03_KAPLAN():
    return ev.roster_speaker_found("20200729-03", "KAPLAN")

def check_po_roster_20200729_03_KASHKARI():
    return ev.roster_speaker_found("20200729-03", "KASHKARI")

def check_po_roster_20200729_03_EVANS():
    return ev.roster_speaker_found("20200729-03", "EVANS")

def check_po_roster_20200729_03_POWELL():
    return ev.roster_speaker_found("20200729-03", "POWELL")

def check_po_roster_20200729_03_BOSTIC():
    return ev.roster_speaker_found("20200729-03", "BOSTIC")

def check_po_roster_20200729_03_WILLIAMS():
    return ev.roster_speaker_found("20200729-03", "WILLIAMS")

def check_po_roster_20200729_03_GEORGE():
    return ev.roster_speaker_found("20200729-03", "GEORGE")

def check_po_roster_20200729_03_BOWMAN():
    return ev.roster_speaker_found("20200729-03", "BOWMAN")

def check_po_roster_20200729_03_BARKIN():
    return ev.roster_speaker_found("20200729-03", "BARKIN")

def check_po_counter_20200729_03_BOWMAN():
    return ev.counter_speaker_found("20200729-03", "BOWMAN")

def check_static_record_l1_20200729_04():
    return ev.record_shape_ok("20200729-04", 1)

def check_static_record_l2_20200729_04():
    return ev.record_shape_ok("20200729-04", 2)

def check_rh_foreign_l1_20200729_04():
    return ev.no_foreign_speaker("20200729-04", 1)

def check_rh_foreign_l2_20200729_04():
    return ev.no_foreign_speaker("20200729-04", 2)

def check_rh_padding_l1_20200729_04():
    return ev.no_padded_entries("20200729-04", 1)

def check_rh_padding_l2_20200729_04():
    return ev.no_padded_entries("20200729-04", 2)

def check_po_roster_20200729_04_DALY():
    return ev.roster_speaker_found("20200729-04", "DALY")

def check_po_roster_20200729_04_KAPLAN():
    return ev.roster_speaker_found("20200729-04", "KAPLAN")

def check_po_roster_20200729_04_GEORGE():
    return ev.roster_speaker_found("20200729-04", "GEORGE")

def check_po_roster_20200729_04_BOWMAN():
    return ev.roster_speaker_found("20200729-04", "BOWMAN")

def check_po_counter_20200729_04_KAPLAN():
    return ev.counter_speaker_found("20200729-04", "KAPLAN")

def check_static_record_l1_20200729_05():
    return ev.record_shape_ok("20200729-05", 1)

def check_static_record_l2_20200729_05():
    return ev.record_shape_ok("20200729-05", 2)

def check_rh_foreign_l1_20200729_05():
    return ev.no_foreign_speaker("20200729-05", 1)

def check_rh_foreign_l2_20200729_05():
    return ev.no_foreign_speaker("20200729-05", 2)

def check_rh_padding_l1_20200729_05():
    return ev.no_padded_entries("20200729-05", 1)

def check_rh_padding_l2_20200729_05():
    return ev.no_padded_entries("20200729-05", 2)

def check_po_roster_20200729_05_BRAINARD():
    return ev.roster_speaker_found("20200729-05", "BRAINARD")

def check_po_roster_20200729_05_DALY():
    return ev.roster_speaker_found("20200729-05", "DALY")

def check_po_roster_20200729_05_KAPLAN():
    return ev.roster_speaker_found("20200729-05", "KAPLAN")

def check_po_roster_20200729_05_KASHKARI():
    return ev.roster_speaker_found("20200729-05", "KASHKARI")

def check_po_roster_20200729_05_POWELL():
    return ev.roster_speaker_found("20200729-05", "POWELL")

def check_po_roster_20200729_05_ROSENGREN():
    return ev.roster_speaker_found("20200729-05", "ROSENGREN")

def check_po_roster_20200729_05_WILLIAMS():
    return ev.roster_speaker_found("20200729-05", "WILLIAMS")

def check_po_roster_20200729_05_BARKIN():
    return ev.roster_speaker_found("20200729-05", "BARKIN")

def check_po_roster_20200729_05_HARKER():
    return ev.roster_speaker_found("20200729-05", "HARKER")

def check_po_counter_20200729_05_BULLARD():
    return ev.counter_speaker_found("20200729-05", "BULLARD")

def check_po_counter_20200729_05_BOWMAN():
    return ev.counter_speaker_found("20200729-05", "BOWMAN")

def check_static_record_l1_20200729_06():
    return ev.record_shape_ok("20200729-06", 1)

def check_static_record_l2_20200729_06():
    return ev.record_shape_ok("20200729-06", 2)

def check_rh_foreign_l1_20200729_06():
    return ev.no_foreign_speaker("20200729-06", 1)

def check_rh_foreign_l2_20200729_06():
    return ev.no_foreign_speaker("20200729-06", 2)

def check_rh_padding_l1_20200729_06():
    return ev.no_padded_entries("20200729-06", 1)

def check_rh_padding_l2_20200729_06():
    return ev.no_padded_entries("20200729-06", 2)

def check_po_roster_20200729_06_MESTER():
    return ev.roster_speaker_found("20200729-06", "MESTER")

def check_po_roster_20200729_06_BRAINARD():
    return ev.roster_speaker_found("20200729-06", "BRAINARD")

def check_po_roster_20200729_06_CLARIDA():
    return ev.roster_speaker_found("20200729-06", "CLARIDA")

def check_po_roster_20200729_06_KASHKARI():
    return ev.roster_speaker_found("20200729-06", "KASHKARI")

def check_po_roster_20200729_06_EVANS():
    return ev.roster_speaker_found("20200729-06", "EVANS")

def check_po_roster_20200729_06_POWELL():
    return ev.roster_speaker_found("20200729-06", "POWELL")

def check_po_roster_20200729_06_ROSENGREN():
    return ev.roster_speaker_found("20200729-06", "ROSENGREN")

def check_po_roster_20200729_06_WILLIAMS():
    return ev.roster_speaker_found("20200729-06", "WILLIAMS")

def check_po_counter_20200729_06_QUARLES():
    return ev.counter_speaker_found("20200729-06", "QUARLES")

def check_po_counter_20200729_06_WILLIAMS():
    return ev.counter_speaker_found("20200729-06", "WILLIAMS")

def check_po_counter_20200729_06_GEORGE():
    return ev.counter_speaker_found("20200729-06", "GEORGE")

def check_po_counter_20200729_06_BOWMAN():
    return ev.counter_speaker_found("20200729-06", "BOWMAN")

def check_static_record_l1_20200729_07():
    return ev.record_shape_ok("20200729-07", 1)

def check_static_record_l2_20200729_07():
    return ev.record_shape_ok("20200729-07", 2)

def check_rh_foreign_l1_20200729_07():
    return ev.no_foreign_speaker("20200729-07", 1)

def check_rh_foreign_l2_20200729_07():
    return ev.no_foreign_speaker("20200729-07", 2)

def check_rh_padding_l1_20200729_07():
    return ev.no_padded_entries("20200729-07", 1)

def check_rh_padding_l2_20200729_07():
    return ev.no_padded_entries("20200729-07", 2)

def check_po_roster_20200729_07_QUARLES():
    return ev.roster_speaker_found("20200729-07", "QUARLES")

def check_po_roster_20200729_07_MESTER():
    return ev.roster_speaker_found("20200729-07", "MESTER")

def check_po_roster_20200729_07_BRAINARD():
    return ev.roster_speaker_found("20200729-07", "BRAINARD")

def check_po_roster_20200729_07_EVANS():
    return ev.roster_speaker_found("20200729-07", "EVANS")

def check_po_roster_20200729_07_KAPLAN():
    return ev.roster_speaker_found("20200729-07", "KAPLAN")

def check_po_roster_20200729_07_BOSTIC():
    return ev.roster_speaker_found("20200729-07", "BOSTIC")

def check_po_roster_20200729_07_ROSENGREN():
    return ev.roster_speaker_found("20200729-07", "ROSENGREN")

def check_po_roster_20200729_07_GEORGE():
    return ev.roster_speaker_found("20200729-07", "GEORGE")

def check_po_roster_20200729_07_HARKER():
    return ev.roster_speaker_found("20200729-07", "HARKER")

def check_po_roster_20200729_07_BARKIN():
    return ev.roster_speaker_found("20200729-07", "BARKIN")

def check_static_record_l1_20200729_08():
    return ev.record_shape_ok("20200729-08", 1)

def check_static_record_l2_20200729_08():
    return ev.record_shape_ok("20200729-08", 2)

def check_rh_foreign_l1_20200729_08():
    return ev.no_foreign_speaker("20200729-08", 1)

def check_rh_foreign_l2_20200729_08():
    return ev.no_foreign_speaker("20200729-08", 2)

def check_rh_padding_l1_20200729_08():
    return ev.no_padded_entries("20200729-08", 1)

def check_rh_padding_l2_20200729_08():
    return ev.no_padded_entries("20200729-08", 2)

def check_po_roster_20200729_08_QUARLES():
    return ev.roster_speaker_found("20200729-08", "QUARLES")

def check_po_roster_20200729_08_MESTER():
    return ev.roster_speaker_found("20200729-08", "MESTER")

def check_po_roster_20200729_08_BULLARD():
    return ev.roster_speaker_found("20200729-08", "BULLARD")

def check_po_roster_20200729_08_BRAINARD():
    return ev.roster_speaker_found("20200729-08", "BRAINARD")

def check_po_roster_20200729_08_DALY():
    return ev.roster_speaker_found("20200729-08", "DALY")

def check_po_roster_20200729_08_CLARIDA():
    return ev.roster_speaker_found("20200729-08", "CLARIDA")

def check_po_roster_20200729_08_KAPLAN():
    return ev.roster_speaker_found("20200729-08", "KAPLAN")

def check_po_roster_20200729_08_KASHKARI():
    return ev.roster_speaker_found("20200729-08", "KASHKARI")

def check_po_roster_20200729_08_EVANS():
    return ev.roster_speaker_found("20200729-08", "EVANS")

def check_po_roster_20200729_08_BOSTIC():
    return ev.roster_speaker_found("20200729-08", "BOSTIC")

def check_po_roster_20200729_08_ROSENGREN():
    return ev.roster_speaker_found("20200729-08", "ROSENGREN")

def check_po_roster_20200729_08_WILLIAMS():
    return ev.roster_speaker_found("20200729-08", "WILLIAMS")

def check_po_roster_20200729_08_GEORGE():
    return ev.roster_speaker_found("20200729-08", "GEORGE")

def check_po_roster_20200729_08_BARKIN():
    return ev.roster_speaker_found("20200729-08", "BARKIN")

def check_po_roster_20200729_08_BOWMAN():
    return ev.roster_speaker_found("20200729-08", "BOWMAN")

def check_po_roster_20200729_08_HARKER():
    return ev.roster_speaker_found("20200729-08", "HARKER")

def check_po_counter_20200729_08_WILLIAMS():
    return ev.counter_speaker_found("20200729-08", "WILLIAMS")

def check_static_record_l1_20200729_09():
    return ev.record_shape_ok("20200729-09", 1)

def check_static_record_l2_20200729_09():
    return ev.record_shape_ok("20200729-09", 2)

def check_rh_foreign_l1_20200729_09():
    return ev.no_foreign_speaker("20200729-09", 1)

def check_rh_foreign_l2_20200729_09():
    return ev.no_foreign_speaker("20200729-09", 2)

def check_rh_padding_l1_20200729_09():
    return ev.no_padded_entries("20200729-09", 1)

def check_rh_padding_l2_20200729_09():
    return ev.no_padded_entries("20200729-09", 2)

def check_po_roster_20200729_09_MESTER():
    return ev.roster_speaker_found("20200729-09", "MESTER")

def check_po_roster_20200729_09_BRAINARD():
    return ev.roster_speaker_found("20200729-09", "BRAINARD")

def check_po_roster_20200729_09_BOSTIC():
    return ev.roster_speaker_found("20200729-09", "BOSTIC")

def check_po_roster_20200729_09_WILLIAMS():
    return ev.roster_speaker_found("20200729-09", "WILLIAMS")

def check_static_record_l1_20200729_10():
    return ev.record_shape_ok("20200729-10", 1)

def check_static_record_l2_20200729_10():
    return ev.record_shape_ok("20200729-10", 2)

def check_rh_foreign_l1_20200729_10():
    return ev.no_foreign_speaker("20200729-10", 1)

def check_rh_foreign_l2_20200729_10():
    return ev.no_foreign_speaker("20200729-10", 2)

def check_rh_padding_l1_20200729_10():
    return ev.no_padded_entries("20200729-10", 1)

def check_rh_padding_l2_20200729_10():
    return ev.no_padded_entries("20200729-10", 2)

def check_po_roster_20200729_10_QUARLES():
    return ev.roster_speaker_found("20200729-10", "QUARLES")

def check_po_roster_20200729_10_MESTER():
    return ev.roster_speaker_found("20200729-10", "MESTER")

def check_po_roster_20200729_10_DALY():
    return ev.roster_speaker_found("20200729-10", "DALY")

def check_po_counter_20200729_10_ROSENGREN():
    return ev.counter_speaker_found("20200729-10", "ROSENGREN")

def check_static_record_l1_20200729_11():
    return ev.record_shape_ok("20200729-11", 1)

def check_static_record_l2_20200729_11():
    return ev.record_shape_ok("20200729-11", 2)

def check_rh_foreign_l1_20200729_11():
    return ev.no_foreign_speaker("20200729-11", 1)

def check_rh_foreign_l2_20200729_11():
    return ev.no_foreign_speaker("20200729-11", 2)

def check_rh_padding_l1_20200729_11():
    return ev.no_padded_entries("20200729-11", 1)

def check_rh_padding_l2_20200729_11():
    return ev.no_padded_entries("20200729-11", 2)

def check_po_roster_20200729_11_MESTER():
    return ev.roster_speaker_found("20200729-11", "MESTER")

def check_po_roster_20200729_11_BRAINARD():
    return ev.roster_speaker_found("20200729-11", "BRAINARD")

def check_po_roster_20200729_11_DALY():
    return ev.roster_speaker_found("20200729-11", "DALY")

def check_po_roster_20200729_11_KASHKARI():
    return ev.roster_speaker_found("20200729-11", "KASHKARI")

def check_po_roster_20200729_11_ROSENGREN():
    return ev.roster_speaker_found("20200729-11", "ROSENGREN")

def check_po_counter_20200729_11_QUARLES():
    return ev.counter_speaker_found("20200729-11", "QUARLES")

def check_static_record_l1_20200729_12():
    return ev.record_shape_ok("20200729-12", 1)

def check_static_record_l2_20200729_12():
    return ev.record_shape_ok("20200729-12", 2)

def check_rh_foreign_l1_20200729_12():
    return ev.no_foreign_speaker("20200729-12", 1)

def check_rh_foreign_l2_20200729_12():
    return ev.no_foreign_speaker("20200729-12", 2)

def check_rh_padding_l1_20200729_12():
    return ev.no_padded_entries("20200729-12", 1)

def check_rh_padding_l2_20200729_12():
    return ev.no_padded_entries("20200729-12", 2)

def check_po_roster_20200729_12_QUARLES():
    return ev.roster_speaker_found("20200729-12", "QUARLES")

def check_po_roster_20200729_12_MESTER():
    return ev.roster_speaker_found("20200729-12", "MESTER")

def check_po_roster_20200729_12_BRAINARD():
    return ev.roster_speaker_found("20200729-12", "BRAINARD")

def check_po_roster_20200729_12_DALY():
    return ev.roster_speaker_found("20200729-12", "DALY")

def check_po_roster_20200729_12_EVANS():
    return ev.roster_speaker_found("20200729-12", "EVANS")

def check_po_roster_20200729_12_ROSENGREN():
    return ev.roster_speaker_found("20200729-12", "ROSENGREN")

def check_po_roster_20200729_12_GEORGE():
    return ev.roster_speaker_found("20200729-12", "GEORGE")

def check_po_roster_20200729_12_BOWMAN():
    return ev.roster_speaker_found("20200729-12", "BOWMAN")

def check_po_counter_20200729_12_KAPLAN():
    return ev.counter_speaker_found("20200729-12", "KAPLAN")

def check_po_counter_20200729_12_BULLARD():
    return ev.counter_speaker_found("20200729-12", "BULLARD")

def check_po_counter_20200729_12_BARKIN():
    return ev.counter_speaker_found("20200729-12", "BARKIN")

def check_po_counter_20200729_12_BOSTIC():
    return ev.counter_speaker_found("20200729-12", "BOSTIC")

def check_static_record_l1_20200729_13():
    return ev.record_shape_ok("20200729-13", 1)

def check_static_record_l2_20200729_13():
    return ev.record_shape_ok("20200729-13", 2)

def check_rh_foreign_l1_20200729_13():
    return ev.no_foreign_speaker("20200729-13", 1)

def check_rh_foreign_l2_20200729_13():
    return ev.no_foreign_speaker("20200729-13", 2)

def check_rh_padding_l1_20200729_13():
    return ev.no_padded_entries("20200729-13", 1)

def check_rh_padding_l2_20200729_13():
    return ev.no_padded_entries("20200729-13", 2)

def check_po_roster_20200729_13_QUARLES():
    return ev.roster_speaker_found("20200729-13", "QUARLES")

def check_po_roster_20200729_13_MESTER():
    return ev.roster_speaker_found("20200729-13", "MESTER")

def check_po_roster_20200729_13_DALY():
    return ev.roster_speaker_found("20200729-13", "DALY")

def check_po_roster_20200729_13_KAPLAN():
    return ev.roster_speaker_found("20200729-13", "KAPLAN")

def check_po_roster_20200729_13_KASHKARI():
    return ev.roster_speaker_found("20200729-13", "KASHKARI")

def check_po_roster_20200729_13_EVANS():
    return ev.roster_speaker_found("20200729-13", "EVANS")

def check_po_roster_20200729_13_POWELL():
    return ev.roster_speaker_found("20200729-13", "POWELL")

def check_po_roster_20200729_13_ROSENGREN():
    return ev.roster_speaker_found("20200729-13", "ROSENGREN")

def check_po_roster_20200729_13_BARKIN():
    return ev.roster_speaker_found("20200729-13", "BARKIN")

def check_po_counter_20200729_13_BOWMAN():
    return ev.counter_speaker_found("20200729-13", "BOWMAN")

def check_static_record_l1_20200729_14():
    return ev.record_shape_ok("20200729-14", 1)

def check_static_record_l2_20200729_14():
    return ev.record_shape_ok("20200729-14", 2)

def check_rh_foreign_l1_20200729_14():
    return ev.no_foreign_speaker("20200729-14", 1)

def check_rh_foreign_l2_20200729_14():
    return ev.no_foreign_speaker("20200729-14", 2)

def check_rh_padding_l1_20200729_14():
    return ev.no_padded_entries("20200729-14", 1)

def check_rh_padding_l2_20200729_14():
    return ev.no_padded_entries("20200729-14", 2)

def check_po_roster_20200729_14_MESTER():
    return ev.roster_speaker_found("20200729-14", "MESTER")

def check_po_roster_20200729_14_QUARLES():
    return ev.roster_speaker_found("20200729-14", "QUARLES")

def check_po_roster_20200729_14_BRAINARD():
    return ev.roster_speaker_found("20200729-14", "BRAINARD")

def check_po_roster_20200729_14_DALY():
    return ev.roster_speaker_found("20200729-14", "DALY")

def check_po_roster_20200729_14_CLARIDA():
    return ev.roster_speaker_found("20200729-14", "CLARIDA")

def check_po_roster_20200729_14_KAPLAN():
    return ev.roster_speaker_found("20200729-14", "KAPLAN")

def check_po_roster_20200729_14_KASHKARI():
    return ev.roster_speaker_found("20200729-14", "KASHKARI")

def check_po_roster_20200729_14_EVANS():
    return ev.roster_speaker_found("20200729-14", "EVANS")

def check_po_roster_20200729_14_POWELL():
    return ev.roster_speaker_found("20200729-14", "POWELL")

def check_po_roster_20200729_14_ROSENGREN():
    return ev.roster_speaker_found("20200729-14", "ROSENGREN")

def check_po_roster_20200729_14_WILLIAMS():
    return ev.roster_speaker_found("20200729-14", "WILLIAMS")

def check_po_roster_20200729_14_GEORGE():
    return ev.roster_speaker_found("20200729-14", "GEORGE")

def check_po_roster_20200729_14_BOWMAN():
    return ev.roster_speaker_found("20200729-14", "BOWMAN")

def check_po_roster_20200729_14_BARKIN():
    return ev.roster_speaker_found("20200729-14", "BARKIN")

def check_static_record_l1_20200729_15():
    return ev.record_shape_ok("20200729-15", 1)

def check_static_record_l2_20200729_15():
    return ev.record_shape_ok("20200729-15", 2)

def check_rh_foreign_l1_20200729_15():
    return ev.no_foreign_speaker("20200729-15", 1)

def check_rh_foreign_l2_20200729_15():
    return ev.no_foreign_speaker("20200729-15", 2)

def check_rh_padding_l1_20200729_15():
    return ev.no_padded_entries("20200729-15", 1)

def check_rh_padding_l2_20200729_15():
    return ev.no_padded_entries("20200729-15", 2)

def check_po_roster_20200729_15_MESTER():
    return ev.roster_speaker_found("20200729-15", "MESTER")

def check_po_roster_20200729_15_BRAINARD():
    return ev.roster_speaker_found("20200729-15", "BRAINARD")

def check_po_roster_20200729_15_DALY():
    return ev.roster_speaker_found("20200729-15", "DALY")

def check_po_roster_20200729_15_CLARIDA():
    return ev.roster_speaker_found("20200729-15", "CLARIDA")

def check_po_roster_20200729_15_KAPLAN():
    return ev.roster_speaker_found("20200729-15", "KAPLAN")

def check_po_roster_20200729_15_KASHKARI():
    return ev.roster_speaker_found("20200729-15", "KASHKARI")

def check_po_roster_20200729_15_ROSENGREN():
    return ev.roster_speaker_found("20200729-15", "ROSENGREN")

def check_po_roster_20200729_15_GEORGE():
    return ev.roster_speaker_found("20200729-15", "GEORGE")

def check_po_roster_20200729_15_BOWMAN():
    return ev.roster_speaker_found("20200729-15", "BOWMAN")

def check_po_counter_20200729_15_QUARLES():
    return ev.counter_speaker_found("20200729-15", "QUARLES")

def check_po_counter_20200729_15_GEORGE():
    return ev.counter_speaker_found("20200729-15", "GEORGE")

def check_static_record_l1_20200729_16():
    return ev.record_shape_ok("20200729-16", 1)

def check_static_record_l2_20200729_16():
    return ev.record_shape_ok("20200729-16", 2)

def check_rh_foreign_l1_20200729_16():
    return ev.no_foreign_speaker("20200729-16", 1)

def check_rh_foreign_l2_20200729_16():
    return ev.no_foreign_speaker("20200729-16", 2)

def check_rh_padding_l1_20200729_16():
    return ev.no_padded_entries("20200729-16", 1)

def check_rh_padding_l2_20200729_16():
    return ev.no_padded_entries("20200729-16", 2)

def check_po_roster_20200729_16_MESTER():
    return ev.roster_speaker_found("20200729-16", "MESTER")

def check_po_roster_20200729_16_DALY():
    return ev.roster_speaker_found("20200729-16", "DALY")

def check_po_roster_20200729_16_KAPLAN():
    return ev.roster_speaker_found("20200729-16", "KAPLAN")

def check_po_roster_20200729_16_WILLIAMS():
    return ev.roster_speaker_found("20200729-16", "WILLIAMS")

def check_po_roster_20200729_16_GEORGE():
    return ev.roster_speaker_found("20200729-16", "GEORGE")

def check_po_roster_20200729_16_BARKIN():
    return ev.roster_speaker_found("20200729-16", "BARKIN")

def check_static_record_l1_20200729_17():
    return ev.record_shape_ok("20200729-17", 1)

def check_static_record_l2_20200729_17():
    return ev.record_shape_ok("20200729-17", 2)

def check_rh_foreign_l1_20200729_17():
    return ev.no_foreign_speaker("20200729-17", 1)

def check_rh_foreign_l2_20200729_17():
    return ev.no_foreign_speaker("20200729-17", 2)

def check_rh_padding_l1_20200729_17():
    return ev.no_padded_entries("20200729-17", 1)

def check_rh_padding_l2_20200729_17():
    return ev.no_padded_entries("20200729-17", 2)

def check_po_roster_20200729_17_QUARLES():
    return ev.roster_speaker_found("20200729-17", "QUARLES")

def check_po_roster_20200729_17_BULLARD():
    return ev.roster_speaker_found("20200729-17", "BULLARD")

def check_po_roster_20200729_17_BRAINARD():
    return ev.roster_speaker_found("20200729-17", "BRAINARD")

def check_po_roster_20200729_17_DALY():
    return ev.roster_speaker_found("20200729-17", "DALY")

def check_po_roster_20200729_17_CLARIDA():
    return ev.roster_speaker_found("20200729-17", "CLARIDA")

def check_po_roster_20200729_17_KASHKARI():
    return ev.roster_speaker_found("20200729-17", "KASHKARI")

def check_po_roster_20200729_17_EVANS():
    return ev.roster_speaker_found("20200729-17", "EVANS")

def check_po_roster_20200729_17_POWELL():
    return ev.roster_speaker_found("20200729-17", "POWELL")

def check_po_roster_20200729_17_WILLIAMS():
    return ev.roster_speaker_found("20200729-17", "WILLIAMS")

def check_po_roster_20200729_17_ROSENGREN():
    return ev.roster_speaker_found("20200729-17", "ROSENGREN")

def check_po_roster_20200729_17_GEORGE():
    return ev.roster_speaker_found("20200729-17", "GEORGE")

def check_po_roster_20200729_17_HARKER():
    return ev.roster_speaker_found("20200729-17", "HARKER")

def check_po_roster_20200729_17_BOWMAN():
    return ev.roster_speaker_found("20200729-17", "BOWMAN")

def check_po_counter_20200729_17_MESTER():
    return ev.counter_speaker_found("20200729-17", "MESTER")

def check_po_counter_20200729_17_BOSTIC():
    return ev.counter_speaker_found("20200729-17", "BOSTIC")

def check_static_record_l1_20200729_18():
    return ev.record_shape_ok("20200729-18", 1)

def check_static_record_l2_20200729_18():
    return ev.record_shape_ok("20200729-18", 2)

def check_rh_foreign_l1_20200729_18():
    return ev.no_foreign_speaker("20200729-18", 1)

def check_rh_foreign_l2_20200729_18():
    return ev.no_foreign_speaker("20200729-18", 2)

def check_rh_padding_l1_20200729_18():
    return ev.no_padded_entries("20200729-18", 1)

def check_rh_padding_l2_20200729_18():
    return ev.no_padded_entries("20200729-18", 2)

def check_po_roster_20200729_18_QUARLES():
    return ev.roster_speaker_found("20200729-18", "QUARLES")

def check_po_roster_20200729_18_BRAINARD():
    return ev.roster_speaker_found("20200729-18", "BRAINARD")

def check_po_roster_20200729_18_KASHKARI():
    return ev.roster_speaker_found("20200729-18", "KASHKARI")

def check_po_roster_20200729_18_POWELL():
    return ev.roster_speaker_found("20200729-18", "POWELL")

def check_po_roster_20200729_18_WILLIAMS():
    return ev.roster_speaker_found("20200729-18", "WILLIAMS")

def check_po_roster_20200729_18_GEORGE():
    return ev.roster_speaker_found("20200729-18", "GEORGE")

def check_po_roster_20200729_18_BOWMAN():
    return ev.roster_speaker_found("20200729-18", "BOWMAN")

def check_po_roster_20200729_18_HARKER():
    return ev.roster_speaker_found("20200729-18", "HARKER")

def check_static_record_l1_20200729_19():
    return ev.record_shape_ok("20200729-19", 1)

def check_static_record_l2_20200729_19():
    return ev.record_shape_ok("20200729-19", 2)

def check_rh_foreign_l1_20200729_19():
    return ev.no_foreign_speaker("20200729-19", 1)

def check_rh_foreign_l2_20200729_19():
    return ev.no_foreign_speaker("20200729-19", 2)

def check_rh_padding_l1_20200729_19():
    return ev.no_padded_entries("20200729-19", 1)

def check_rh_padding_l2_20200729_19():
    return ev.no_padded_entries("20200729-19", 2)

def check_po_roster_20200729_19_QUARLES():
    return ev.roster_speaker_found("20200729-19", "QUARLES")

def check_po_roster_20200729_19_BRAINARD():
    return ev.roster_speaker_found("20200729-19", "BRAINARD")

def check_po_roster_20200729_19_KASHKARI():
    return ev.roster_speaker_found("20200729-19", "KASHKARI")

def check_po_roster_20200729_19_POWELL():
    return ev.roster_speaker_found("20200729-19", "POWELL")

def check_po_roster_20200729_19_WILLIAMS():
    return ev.roster_speaker_found("20200729-19", "WILLIAMS")

def check_po_roster_20200729_19_GEORGE():
    return ev.roster_speaker_found("20200729-19", "GEORGE")

def check_po_roster_20200729_19_BOWMAN():
    return ev.roster_speaker_found("20200729-19", "BOWMAN")

def check_po_roster_20200729_19_HARKER():
    return ev.roster_speaker_found("20200729-19", "HARKER")

def check_po_counter_20200729_19_BRAINARD():
    return ev.counter_speaker_found("20200729-19", "BRAINARD")

def check_static_record_l1_20200729_20():
    return ev.record_shape_ok("20200729-20", 1)

def check_static_record_l2_20200729_20():
    return ev.record_shape_ok("20200729-20", 2)

def check_rh_foreign_l1_20200729_20():
    return ev.no_foreign_speaker("20200729-20", 1)

def check_rh_foreign_l2_20200729_20():
    return ev.no_foreign_speaker("20200729-20", 2)

def check_rh_padding_l1_20200729_20():
    return ev.no_padded_entries("20200729-20", 1)

def check_rh_padding_l2_20200729_20():
    return ev.no_padded_entries("20200729-20", 2)

def check_po_roster_20200729_20_BRAINARD():
    return ev.roster_speaker_found("20200729-20", "BRAINARD")

def check_po_roster_20200729_20_KASHKARI():
    return ev.roster_speaker_found("20200729-20", "KASHKARI")

def check_po_roster_20200729_20_WILLIAMS():
    return ev.roster_speaker_found("20200729-20", "WILLIAMS")

def check_po_counter_20200729_20_QUARLES():
    return ev.counter_speaker_found("20200729-20", "QUARLES")

def check_po_counter_20200729_20_POWELL():
    return ev.counter_speaker_found("20200729-20", "POWELL")

def check_po_counter_20200729_20_HARKER():
    return ev.counter_speaker_found("20200729-20", "HARKER")

def check_po_counter_20200729_20_KASHKARI():
    return ev.counter_speaker_found("20200729-20", "KASHKARI")

def check_po_counter_20200729_20_GEORGE():
    return ev.counter_speaker_found("20200729-20", "GEORGE")

def check_po_counter_20200729_20_BOWMAN():
    return ev.counter_speaker_found("20200729-20", "BOWMAN")

def check_static_record_l1_20200916_01():
    return ev.record_shape_ok("20200916-01", 1)

def check_static_record_l2_20200916_01():
    return ev.record_shape_ok("20200916-01", 2)

def check_rh_foreign_l1_20200916_01():
    return ev.no_foreign_speaker("20200916-01", 1)

def check_rh_foreign_l2_20200916_01():
    return ev.no_foreign_speaker("20200916-01", 2)

def check_rh_padding_l1_20200916_01():
    return ev.no_padded_entries("20200916-01", 1)

def check_rh_padding_l2_20200916_01():
    return ev.no_padded_entries("20200916-01", 2)

def check_po_roster_20200916_01_BOWMAN():
    return ev.roster_speaker_found("20200916-01", "BOWMAN")

def check_po_roster_20200916_01_CLARIDA():
    return ev.roster_speaker_found("20200916-01", "CLARIDA")

def check_po_roster_20200916_01_BOSTIC():
    return ev.roster_speaker_found("20200916-01", "BOSTIC")

def check_po_roster_20200916_01_BRAINARD():
    return ev.roster_speaker_found("20200916-01", "BRAINARD")

def check_po_roster_20200916_01_KASHKARI():
    return ev.roster_speaker_found("20200916-01", "KASHKARI")

def check_po_roster_20200916_01_EVANS():
    return ev.roster_speaker_found("20200916-01", "EVANS")

def check_po_roster_20200916_01_QUARLES():
    return ev.roster_speaker_found("20200916-01", "QUARLES")

def check_po_roster_20200916_01_DALY():
    return ev.roster_speaker_found("20200916-01", "DALY")

def check_po_roster_20200916_01_WILLIAMS():
    return ev.roster_speaker_found("20200916-01", "WILLIAMS")

def check_po_roster_20200916_01_GEORGE():
    return ev.roster_speaker_found("20200916-01", "GEORGE")

def check_po_roster_20200916_01_POWELL():
    return ev.roster_speaker_found("20200916-01", "POWELL")

def check_po_counter_20200916_01_BULLARD():
    return ev.counter_speaker_found("20200916-01", "BULLARD")

def check_po_counter_20200916_01_BARKIN():
    return ev.counter_speaker_found("20200916-01", "BARKIN")

def check_po_counter_20200916_01_QUARLES():
    return ev.counter_speaker_found("20200916-01", "QUARLES")

def check_po_counter_20200916_01_WILLIAMS():
    return ev.counter_speaker_found("20200916-01", "WILLIAMS")

def check_po_counter_20200916_01_POWELL():
    return ev.counter_speaker_found("20200916-01", "POWELL")

def check_static_record_l1_20200916_02():
    return ev.record_shape_ok("20200916-02", 1)

def check_static_record_l2_20200916_02():
    return ev.record_shape_ok("20200916-02", 2)

def check_rh_foreign_l1_20200916_02():
    return ev.no_foreign_speaker("20200916-02", 1)

def check_rh_foreign_l2_20200916_02():
    return ev.no_foreign_speaker("20200916-02", 2)

def check_rh_padding_l1_20200916_02():
    return ev.no_padded_entries("20200916-02", 1)

def check_rh_padding_l2_20200916_02():
    return ev.no_padded_entries("20200916-02", 2)

def check_po_roster_20200916_02_MESTER():
    return ev.roster_speaker_found("20200916-02", "MESTER")

def check_po_roster_20200916_02_CLARIDA():
    return ev.roster_speaker_found("20200916-02", "CLARIDA")

def check_po_roster_20200916_02_BRAINARD():
    return ev.roster_speaker_found("20200916-02", "BRAINARD")

def check_po_roster_20200916_02_KASHKARI():
    return ev.roster_speaker_found("20200916-02", "KASHKARI")

def check_po_roster_20200916_02_QUARLES():
    return ev.roster_speaker_found("20200916-02", "QUARLES")

def check_po_roster_20200916_02_ROSENGREN():
    return ev.roster_speaker_found("20200916-02", "ROSENGREN")

def check_po_roster_20200916_02_EVANS():
    return ev.roster_speaker_found("20200916-02", "EVANS")

def check_po_roster_20200916_02_DALY():
    return ev.roster_speaker_found("20200916-02", "DALY")

def check_po_roster_20200916_02_WILLIAMS():
    return ev.roster_speaker_found("20200916-02", "WILLIAMS")

def check_po_roster_20200916_02_GEORGE():
    return ev.roster_speaker_found("20200916-02", "GEORGE")

def check_po_roster_20200916_02_POWELL():
    return ev.roster_speaker_found("20200916-02", "POWELL")

def check_po_roster_20200916_02_HARKER():
    return ev.roster_speaker_found("20200916-02", "HARKER")

def check_po_counter_20200916_02_BULLARD():
    return ev.counter_speaker_found("20200916-02", "BULLARD")

def check_static_record_l1_20200916_03():
    return ev.record_shape_ok("20200916-03", 1)

def check_static_record_l2_20200916_03():
    return ev.record_shape_ok("20200916-03", 2)

def check_rh_foreign_l1_20200916_03():
    return ev.no_foreign_speaker("20200916-03", 1)

def check_rh_foreign_l2_20200916_03():
    return ev.no_foreign_speaker("20200916-03", 2)

def check_rh_padding_l1_20200916_03():
    return ev.no_padded_entries("20200916-03", 1)

def check_rh_padding_l2_20200916_03():
    return ev.no_padded_entries("20200916-03", 2)

def check_po_roster_20200916_03_CLARIDA():
    return ev.roster_speaker_found("20200916-03", "CLARIDA")

def check_po_roster_20200916_03_BARKIN():
    return ev.roster_speaker_found("20200916-03", "BARKIN")

def check_po_roster_20200916_03_QUARLES():
    return ev.roster_speaker_found("20200916-03", "QUARLES")

def check_po_counter_20200916_03_KASHKARI():
    return ev.counter_speaker_found("20200916-03", "KASHKARI")

def check_po_counter_20200916_03_BRAINARD():
    return ev.counter_speaker_found("20200916-03", "BRAINARD")

def check_po_counter_20200916_03_EVANS():
    return ev.counter_speaker_found("20200916-03", "EVANS")

def check_po_counter_20200916_03_POWELL():
    return ev.counter_speaker_found("20200916-03", "POWELL")

def check_static_record_l1_20200916_04():
    return ev.record_shape_ok("20200916-04", 1)

def check_static_record_l2_20200916_04():
    return ev.record_shape_ok("20200916-04", 2)

def check_rh_foreign_l1_20200916_04():
    return ev.no_foreign_speaker("20200916-04", 1)

def check_rh_foreign_l2_20200916_04():
    return ev.no_foreign_speaker("20200916-04", 2)

def check_rh_padding_l1_20200916_04():
    return ev.no_padded_entries("20200916-04", 1)

def check_rh_padding_l2_20200916_04():
    return ev.no_padded_entries("20200916-04", 2)

def check_po_roster_20200916_04_CLARIDA():
    return ev.roster_speaker_found("20200916-04", "CLARIDA")

def check_po_roster_20200916_04_POWELL():
    return ev.roster_speaker_found("20200916-04", "POWELL")

def check_static_record_l1_20200916_05():
    return ev.record_shape_ok("20200916-05", 1)

def check_static_record_l2_20200916_05():
    return ev.record_shape_ok("20200916-05", 2)

def check_rh_foreign_l1_20200916_05():
    return ev.no_foreign_speaker("20200916-05", 1)

def check_rh_foreign_l2_20200916_05():
    return ev.no_foreign_speaker("20200916-05", 2)

def check_rh_padding_l1_20200916_05():
    return ev.no_padded_entries("20200916-05", 1)

def check_rh_padding_l2_20200916_05():
    return ev.no_padded_entries("20200916-05", 2)

def check_po_roster_20200916_05_BOWMAN():
    return ev.roster_speaker_found("20200916-05", "BOWMAN")

def check_po_roster_20200916_05_BRAINARD():
    return ev.roster_speaker_found("20200916-05", "BRAINARD")

def check_po_roster_20200916_05_BOSTIC():
    return ev.roster_speaker_found("20200916-05", "BOSTIC")

def check_po_roster_20200916_05_POWELL():
    return ev.roster_speaker_found("20200916-05", "POWELL")

def check_static_record_l1_20200916_06():
    return ev.record_shape_ok("20200916-06", 1)

def check_static_record_l2_20200916_06():
    return ev.record_shape_ok("20200916-06", 2)

def check_rh_foreign_l1_20200916_06():
    return ev.no_foreign_speaker("20200916-06", 1)

def check_rh_foreign_l2_20200916_06():
    return ev.no_foreign_speaker("20200916-06", 2)

def check_rh_padding_l1_20200916_06():
    return ev.no_padded_entries("20200916-06", 1)

def check_rh_padding_l2_20200916_06():
    return ev.no_padded_entries("20200916-06", 2)

def check_po_roster_20200916_06_MESTER():
    return ev.roster_speaker_found("20200916-06", "MESTER")

def check_po_roster_20200916_06_BOSTIC():
    return ev.roster_speaker_found("20200916-06", "BOSTIC")

def check_po_roster_20200916_06_EVANS():
    return ev.roster_speaker_found("20200916-06", "EVANS")

def check_po_roster_20200916_06_DALY():
    return ev.roster_speaker_found("20200916-06", "DALY")

def check_po_roster_20200916_06_WILLIAMS():
    return ev.roster_speaker_found("20200916-06", "WILLIAMS")

def check_po_roster_20200916_06_POWELL():
    return ev.roster_speaker_found("20200916-06", "POWELL")

def check_static_record_l1_20200916_07():
    return ev.record_shape_ok("20200916-07", 1)

def check_static_record_l2_20200916_07():
    return ev.record_shape_ok("20200916-07", 2)

def check_rh_foreign_l1_20200916_07():
    return ev.no_foreign_speaker("20200916-07", 1)

def check_rh_foreign_l2_20200916_07():
    return ev.no_foreign_speaker("20200916-07", 2)

def check_rh_padding_l1_20200916_07():
    return ev.no_padded_entries("20200916-07", 1)

def check_rh_padding_l2_20200916_07():
    return ev.no_padded_entries("20200916-07", 2)

def check_po_roster_20200916_07_MESTER():
    return ev.roster_speaker_found("20200916-07", "MESTER")

def check_po_roster_20200916_07_BOWMAN():
    return ev.roster_speaker_found("20200916-07", "BOWMAN")

def check_po_roster_20200916_07_BARKIN():
    return ev.roster_speaker_found("20200916-07", "BARKIN")

def check_po_roster_20200916_07_EVANS():
    return ev.roster_speaker_found("20200916-07", "EVANS")

def check_po_roster_20200916_07_HARKER():
    return ev.roster_speaker_found("20200916-07", "HARKER")

def check_static_record_l1_20200916_08():
    return ev.record_shape_ok("20200916-08", 1)

def check_static_record_l2_20200916_08():
    return ev.record_shape_ok("20200916-08", 2)

def check_rh_foreign_l1_20200916_08():
    return ev.no_foreign_speaker("20200916-08", 1)

def check_rh_foreign_l2_20200916_08():
    return ev.no_foreign_speaker("20200916-08", 2)

def check_rh_padding_l1_20200916_08():
    return ev.no_padded_entries("20200916-08", 1)

def check_rh_padding_l2_20200916_08():
    return ev.no_padded_entries("20200916-08", 2)

def check_po_roster_20200916_08_MESTER():
    return ev.roster_speaker_found("20200916-08", "MESTER")

def check_po_roster_20200916_08_BRAINARD():
    return ev.roster_speaker_found("20200916-08", "BRAINARD")

def check_po_roster_20200916_08_EVANS():
    return ev.roster_speaker_found("20200916-08", "EVANS")

def check_po_roster_20200916_08_ROSENGREN():
    return ev.roster_speaker_found("20200916-08", "ROSENGREN")

def check_po_roster_20200916_08_WILLIAMS():
    return ev.roster_speaker_found("20200916-08", "WILLIAMS")

def check_po_roster_20200916_08_GEORGE():
    return ev.roster_speaker_found("20200916-08", "GEORGE")

def check_po_roster_20200916_08_POWELL():
    return ev.roster_speaker_found("20200916-08", "POWELL")

def check_po_counter_20200916_08_KASHKARI():
    return ev.counter_speaker_found("20200916-08", "KASHKARI")

def check_po_counter_20200916_08_GEORGE():
    return ev.counter_speaker_found("20200916-08", "GEORGE")

def check_po_counter_20200916_08_KAPLAN():
    return ev.counter_speaker_found("20200916-08", "KAPLAN")

def check_static_record_l1_20200916_09():
    return ev.record_shape_ok("20200916-09", 1)

def check_static_record_l2_20200916_09():
    return ev.record_shape_ok("20200916-09", 2)

def check_rh_foreign_l1_20200916_09():
    return ev.no_foreign_speaker("20200916-09", 1)

def check_rh_foreign_l2_20200916_09():
    return ev.no_foreign_speaker("20200916-09", 2)

def check_rh_padding_l1_20200916_09():
    return ev.no_padded_entries("20200916-09", 1)

def check_rh_padding_l2_20200916_09():
    return ev.no_padded_entries("20200916-09", 2)

def check_po_roster_20200916_09_MESTER():
    return ev.roster_speaker_found("20200916-09", "MESTER")

def check_po_roster_20200916_09_ROSENGREN():
    return ev.roster_speaker_found("20200916-09", "ROSENGREN")

def check_static_record_l1_20200916_10():
    return ev.record_shape_ok("20200916-10", 1)

def check_static_record_l2_20200916_10():
    return ev.record_shape_ok("20200916-10", 2)

def check_rh_foreign_l1_20200916_10():
    return ev.no_foreign_speaker("20200916-10", 1)

def check_rh_foreign_l2_20200916_10():
    return ev.no_foreign_speaker("20200916-10", 2)

def check_rh_padding_l1_20200916_10():
    return ev.no_padded_entries("20200916-10", 1)

def check_rh_padding_l2_20200916_10():
    return ev.no_padded_entries("20200916-10", 2)

def check_po_roster_20200916_10_MESTER():
    return ev.roster_speaker_found("20200916-10", "MESTER")

def check_po_roster_20200916_10_BARKIN():
    return ev.roster_speaker_found("20200916-10", "BARKIN")

def check_po_roster_20200916_10_BRAINARD():
    return ev.roster_speaker_found("20200916-10", "BRAINARD")

def check_po_roster_20200916_10_ROSENGREN():
    return ev.roster_speaker_found("20200916-10", "ROSENGREN")

def check_po_roster_20200916_10_GEORGE():
    return ev.roster_speaker_found("20200916-10", "GEORGE")

def check_po_roster_20200916_10_KAPLAN():
    return ev.roster_speaker_found("20200916-10", "KAPLAN")

def check_po_counter_20200916_10_EVANS():
    return ev.counter_speaker_found("20200916-10", "EVANS")

def check_po_counter_20200916_10_POWELL():
    return ev.counter_speaker_found("20200916-10", "POWELL")

def check_static_record_l1_20200916_11():
    return ev.record_shape_ok("20200916-11", 1)

def check_static_record_l2_20200916_11():
    return ev.record_shape_ok("20200916-11", 2)

def check_rh_foreign_l1_20200916_11():
    return ev.no_foreign_speaker("20200916-11", 1)

def check_rh_foreign_l2_20200916_11():
    return ev.no_foreign_speaker("20200916-11", 2)

def check_rh_padding_l1_20200916_11():
    return ev.no_padded_entries("20200916-11", 1)

def check_rh_padding_l2_20200916_11():
    return ev.no_padded_entries("20200916-11", 2)

def check_po_roster_20200916_11_MESTER():
    return ev.roster_speaker_found("20200916-11", "MESTER")

def check_po_roster_20200916_11_BRAINARD():
    return ev.roster_speaker_found("20200916-11", "BRAINARD")

def check_po_roster_20200916_11_EVANS():
    return ev.roster_speaker_found("20200916-11", "EVANS")

def check_po_roster_20200916_11_QUARLES():
    return ev.roster_speaker_found("20200916-11", "QUARLES")

def check_po_roster_20200916_11_ROSENGREN():
    return ev.roster_speaker_found("20200916-11", "ROSENGREN")

def check_po_roster_20200916_11_DALY():
    return ev.roster_speaker_found("20200916-11", "DALY")

def check_po_roster_20200916_11_WILLIAMS():
    return ev.roster_speaker_found("20200916-11", "WILLIAMS")

def check_po_roster_20200916_11_GEORGE():
    return ev.roster_speaker_found("20200916-11", "GEORGE")

def check_po_roster_20200916_11_POWELL():
    return ev.roster_speaker_found("20200916-11", "POWELL")

def check_po_counter_20200916_11_BULLARD():
    return ev.counter_speaker_found("20200916-11", "BULLARD")

def check_static_record_l1_20200916_12():
    return ev.record_shape_ok("20200916-12", 1)

def check_static_record_l2_20200916_12():
    return ev.record_shape_ok("20200916-12", 2)

def check_rh_foreign_l1_20200916_12():
    return ev.no_foreign_speaker("20200916-12", 1)

def check_rh_foreign_l2_20200916_12():
    return ev.no_foreign_speaker("20200916-12", 2)

def check_rh_padding_l1_20200916_12():
    return ev.no_padded_entries("20200916-12", 1)

def check_rh_padding_l2_20200916_12():
    return ev.no_padded_entries("20200916-12", 2)

def check_po_roster_20200916_12_QUARLES():
    return ev.roster_speaker_found("20200916-12", "QUARLES")

def check_po_roster_20200916_12_POWELL():
    return ev.roster_speaker_found("20200916-12", "POWELL")

def check_po_counter_20200916_12_BRAINARD():
    return ev.counter_speaker_found("20200916-12", "BRAINARD")

def check_po_counter_20200916_12_EVANS():
    return ev.counter_speaker_found("20200916-12", "EVANS")

def check_po_counter_20200916_12_ROSENGREN():
    return ev.counter_speaker_found("20200916-12", "ROSENGREN")

def check_po_counter_20200916_12_WILLIAMS():
    return ev.counter_speaker_found("20200916-12", "WILLIAMS")

def check_static_record_l1_20200916_13():
    return ev.record_shape_ok("20200916-13", 1)

def check_static_record_l2_20200916_13():
    return ev.record_shape_ok("20200916-13", 2)

def check_rh_foreign_l1_20200916_13():
    return ev.no_foreign_speaker("20200916-13", 1)

def check_rh_foreign_l2_20200916_13():
    return ev.no_foreign_speaker("20200916-13", 2)

def check_rh_padding_l1_20200916_13():
    return ev.no_padded_entries("20200916-13", 1)

def check_rh_padding_l2_20200916_13():
    return ev.no_padded_entries("20200916-13", 2)

def check_po_roster_20200916_13_MESTER():
    return ev.roster_speaker_found("20200916-13", "MESTER")

def check_po_roster_20200916_13_BOSTIC():
    return ev.roster_speaker_found("20200916-13", "BOSTIC")

def check_po_roster_20200916_13_BARKIN():
    return ev.roster_speaker_found("20200916-13", "BARKIN")

def check_po_roster_20200916_13_ROSENGREN():
    return ev.roster_speaker_found("20200916-13", "ROSENGREN")

def check_po_roster_20200916_13_EVANS():
    return ev.roster_speaker_found("20200916-13", "EVANS")

def check_po_roster_20200916_13_DALY():
    return ev.roster_speaker_found("20200916-13", "DALY")

def check_po_roster_20200916_13_GEORGE():
    return ev.roster_speaker_found("20200916-13", "GEORGE")

def check_po_roster_20200916_13_KAPLAN():
    return ev.roster_speaker_found("20200916-13", "KAPLAN")

def check_po_roster_20200916_13_HARKER():
    return ev.roster_speaker_found("20200916-13", "HARKER")

def check_static_record_l1_20200916_14():
    return ev.record_shape_ok("20200916-14", 1)

def check_static_record_l2_20200916_14():
    return ev.record_shape_ok("20200916-14", 2)

def check_rh_foreign_l1_20200916_14():
    return ev.no_foreign_speaker("20200916-14", 1)

def check_rh_foreign_l2_20200916_14():
    return ev.no_foreign_speaker("20200916-14", 2)

def check_rh_padding_l1_20200916_14():
    return ev.no_padded_entries("20200916-14", 1)

def check_rh_padding_l2_20200916_14():
    return ev.no_padded_entries("20200916-14", 2)

def check_po_roster_20200916_14_BULLARD():
    return ev.roster_speaker_found("20200916-14", "BULLARD")

def check_po_roster_20200916_14_BOWMAN():
    return ev.roster_speaker_found("20200916-14", "BOWMAN")

def check_po_roster_20200916_14_CLARIDA():
    return ev.roster_speaker_found("20200916-14", "CLARIDA")

def check_po_roster_20200916_14_BRAINARD():
    return ev.roster_speaker_found("20200916-14", "BRAINARD")

def check_po_roster_20200916_14_KASHKARI():
    return ev.roster_speaker_found("20200916-14", "KASHKARI")

def check_po_roster_20200916_14_QUARLES():
    return ev.roster_speaker_found("20200916-14", "QUARLES")

def check_po_roster_20200916_14_EVANS():
    return ev.roster_speaker_found("20200916-14", "EVANS")

def check_po_roster_20200916_14_DALY():
    return ev.roster_speaker_found("20200916-14", "DALY")

def check_po_roster_20200916_14_WILLIAMS():
    return ev.roster_speaker_found("20200916-14", "WILLIAMS")

def check_po_roster_20200916_14_GEORGE():
    return ev.roster_speaker_found("20200916-14", "GEORGE")

def check_po_roster_20200916_14_POWELL():
    return ev.roster_speaker_found("20200916-14", "POWELL")

def check_po_roster_20200916_14_HARKER():
    return ev.roster_speaker_found("20200916-14", "HARKER")

def check_po_counter_20200916_14_MESTER():
    return ev.counter_speaker_found("20200916-14", "MESTER")

def check_po_counter_20200916_14_BOSTIC():
    return ev.counter_speaker_found("20200916-14", "BOSTIC")

def check_po_counter_20200916_14_BARKIN():
    return ev.counter_speaker_found("20200916-14", "BARKIN")

def check_po_counter_20200916_14_ROSENGREN():
    return ev.counter_speaker_found("20200916-14", "ROSENGREN")

def check_po_counter_20200916_14_GEORGE():
    return ev.counter_speaker_found("20200916-14", "GEORGE")

def check_po_counter_20200916_14_KAPLAN():
    return ev.counter_speaker_found("20200916-14", "KAPLAN")

def check_static_record_l1_20200916_15():
    return ev.record_shape_ok("20200916-15", 1)

def check_static_record_l2_20200916_15():
    return ev.record_shape_ok("20200916-15", 2)

def check_rh_foreign_l1_20200916_15():
    return ev.no_foreign_speaker("20200916-15", 1)

def check_rh_foreign_l2_20200916_15():
    return ev.no_foreign_speaker("20200916-15", 2)

def check_rh_padding_l1_20200916_15():
    return ev.no_padded_entries("20200916-15", 1)

def check_rh_padding_l2_20200916_15():
    return ev.no_padded_entries("20200916-15", 2)

def check_po_roster_20200916_15_KASHKARI():
    return ev.roster_speaker_found("20200916-15", "KASHKARI")

def check_po_roster_20200916_15_EVANS():
    return ev.roster_speaker_found("20200916-15", "EVANS")

def check_po_counter_20200916_15_MESTER():
    return ev.counter_speaker_found("20200916-15", "MESTER")

def check_po_counter_20200916_15_BOWMAN():
    return ev.counter_speaker_found("20200916-15", "BOWMAN")

def check_po_counter_20200916_15_BOSTIC():
    return ev.counter_speaker_found("20200916-15", "BOSTIC")

def check_po_counter_20200916_15_BARKIN():
    return ev.counter_speaker_found("20200916-15", "BARKIN")

def check_po_counter_20200916_15_ROSENGREN():
    return ev.counter_speaker_found("20200916-15", "ROSENGREN")

def check_po_counter_20200916_15_QUARLES():
    return ev.counter_speaker_found("20200916-15", "QUARLES")

def check_po_counter_20200916_15_GEORGE():
    return ev.counter_speaker_found("20200916-15", "GEORGE")

def check_po_counter_20200916_15_KAPLAN():
    return ev.counter_speaker_found("20200916-15", "KAPLAN")

def check_po_counter_20200916_15_HARKER():
    return ev.counter_speaker_found("20200916-15", "HARKER")

def check_static_record_l1_20200916_16():
    return ev.record_shape_ok("20200916-16", 1)

def check_static_record_l2_20200916_16():
    return ev.record_shape_ok("20200916-16", 2)

def check_rh_foreign_l1_20200916_16():
    return ev.no_foreign_speaker("20200916-16", 1)

def check_rh_foreign_l2_20200916_16():
    return ev.no_foreign_speaker("20200916-16", 2)

def check_rh_padding_l1_20200916_16():
    return ev.no_padded_entries("20200916-16", 1)

def check_rh_padding_l2_20200916_16():
    return ev.no_padded_entries("20200916-16", 2)

def check_po_roster_20200916_16_MESTER():
    return ev.roster_speaker_found("20200916-16", "MESTER")

def check_po_roster_20200916_16_BARKIN():
    return ev.roster_speaker_found("20200916-16", "BARKIN")

def check_po_roster_20200916_16_BOSTIC():
    return ev.roster_speaker_found("20200916-16", "BOSTIC")

def check_po_roster_20200916_16_ROSENGREN():
    return ev.roster_speaker_found("20200916-16", "ROSENGREN")

def check_po_roster_20200916_16_KAPLAN():
    return ev.roster_speaker_found("20200916-16", "KAPLAN")

def check_po_counter_20200916_16_BOWMAN():
    return ev.counter_speaker_found("20200916-16", "BOWMAN")

def check_po_counter_20200916_16_BRAINARD():
    return ev.counter_speaker_found("20200916-16", "BRAINARD")

def check_po_counter_20200916_16_KASHKARI():
    return ev.counter_speaker_found("20200916-16", "KASHKARI")

def check_po_counter_20200916_16_EVANS():
    return ev.counter_speaker_found("20200916-16", "EVANS")

def check_po_counter_20200916_16_QUARLES():
    return ev.counter_speaker_found("20200916-16", "QUARLES")

def check_po_counter_20200916_16_DALY():
    return ev.counter_speaker_found("20200916-16", "DALY")

def check_po_counter_20200916_16_WILLIAMS():
    return ev.counter_speaker_found("20200916-16", "WILLIAMS")

def check_po_counter_20200916_16_POWELL():
    return ev.counter_speaker_found("20200916-16", "POWELL")

def check_static_record_l1_20200916_17():
    return ev.record_shape_ok("20200916-17", 1)

def check_static_record_l2_20200916_17():
    return ev.record_shape_ok("20200916-17", 2)

def check_rh_foreign_l1_20200916_17():
    return ev.no_foreign_speaker("20200916-17", 1)

def check_rh_foreign_l2_20200916_17():
    return ev.no_foreign_speaker("20200916-17", 2)

def check_rh_padding_l1_20200916_17():
    return ev.no_padded_entries("20200916-17", 1)

def check_rh_padding_l2_20200916_17():
    return ev.no_padded_entries("20200916-17", 2)

def check_po_roster_20200916_17_CLARIDA():
    return ev.roster_speaker_found("20200916-17", "CLARIDA")

def check_po_roster_20200916_17_BOSTIC():
    return ev.roster_speaker_found("20200916-17", "BOSTIC")

def check_po_roster_20200916_17_BRAINARD():
    return ev.roster_speaker_found("20200916-17", "BRAINARD")

def check_po_roster_20200916_17_DALY():
    return ev.roster_speaker_found("20200916-17", "DALY")

def check_po_roster_20200916_17_WILLIAMS():
    return ev.roster_speaker_found("20200916-17", "WILLIAMS")

def check_po_roster_20200916_17_GEORGE():
    return ev.roster_speaker_found("20200916-17", "GEORGE")

def check_static_record_l1_20201105_01():
    return ev.record_shape_ok("20201105-01", 1)

def check_static_record_l2_20201105_01():
    return ev.record_shape_ok("20201105-01", 2)

def check_rh_foreign_l1_20201105_01():
    return ev.no_foreign_speaker("20201105-01", 1)

def check_rh_foreign_l2_20201105_01():
    return ev.no_foreign_speaker("20201105-01", 2)

def check_rh_padding_l1_20201105_01():
    return ev.no_padded_entries("20201105-01", 1)

def check_rh_padding_l2_20201105_01():
    return ev.no_padded_entries("20201105-01", 2)

def check_po_roster_20201105_01_QUARLES():
    return ev.roster_speaker_found("20201105-01", "QUARLES")

def check_po_roster_20201105_01_KAPLAN():
    return ev.roster_speaker_found("20201105-01", "KAPLAN")

def check_po_roster_20201105_01_ROSENGREN():
    return ev.roster_speaker_found("20201105-01", "ROSENGREN")

def check_po_roster_20201105_01_BULLARD():
    return ev.roster_speaker_found("20201105-01", "BULLARD")

def check_po_roster_20201105_01_BOWMAN():
    return ev.roster_speaker_found("20201105-01", "BOWMAN")

def check_po_roster_20201105_01_FELDMAN():
    return ev.roster_speaker_found("20201105-01", "FELDMAN")

def check_po_roster_20201105_01_BRAINARD():
    return ev.roster_speaker_found("20201105-01", "BRAINARD")

def check_po_roster_20201105_01_BOSTIC():
    return ev.roster_speaker_found("20201105-01", "BOSTIC")

def check_po_roster_20201105_01_DALY():
    return ev.roster_speaker_found("20201105-01", "DALY")

def check_po_roster_20201105_01_GEORGE():
    return ev.roster_speaker_found("20201105-01", "GEORGE")

def check_po_roster_20201105_01_MESTER():
    return ev.roster_speaker_found("20201105-01", "MESTER")

def check_po_roster_20201105_01_EVANS():
    return ev.roster_speaker_found("20201105-01", "EVANS")

def check_po_roster_20201105_01_CLARIDA():
    return ev.roster_speaker_found("20201105-01", "CLARIDA")

def check_po_counter_20201105_01_QUARLES():
    return ev.counter_speaker_found("20201105-01", "QUARLES")

def check_po_counter_20201105_01_ROSENGREN():
    return ev.counter_speaker_found("20201105-01", "ROSENGREN")

def check_po_counter_20201105_01_POWELL():
    return ev.counter_speaker_found("20201105-01", "POWELL")

def check_po_counter_20201105_01_HARKER():
    return ev.counter_speaker_found("20201105-01", "HARKER")

def check_po_counter_20201105_01_BOSTIC():
    return ev.counter_speaker_found("20201105-01", "BOSTIC")

def check_static_record_l1_20201105_02():
    return ev.record_shape_ok("20201105-02", 1)

def check_static_record_l2_20201105_02():
    return ev.record_shape_ok("20201105-02", 2)

def check_rh_foreign_l1_20201105_02():
    return ev.no_foreign_speaker("20201105-02", 1)

def check_rh_foreign_l2_20201105_02():
    return ev.no_foreign_speaker("20201105-02", 2)

def check_rh_padding_l1_20201105_02():
    return ev.no_padded_entries("20201105-02", 1)

def check_rh_padding_l2_20201105_02():
    return ev.no_padded_entries("20201105-02", 2)

def check_po_roster_20201105_02_QUARLES():
    return ev.roster_speaker_found("20201105-02", "QUARLES")

def check_po_roster_20201105_02_ROSENGREN():
    return ev.roster_speaker_found("20201105-02", "ROSENGREN")

def check_po_roster_20201105_02_BULLARD():
    return ev.roster_speaker_found("20201105-02", "BULLARD")

def check_po_roster_20201105_02_BRAINARD():
    return ev.roster_speaker_found("20201105-02", "BRAINARD")

def check_po_roster_20201105_02_DALY():
    return ev.roster_speaker_found("20201105-02", "DALY")

def check_po_roster_20201105_02_MESTER():
    return ev.roster_speaker_found("20201105-02", "MESTER")

def check_po_roster_20201105_02_CLARIDA():
    return ev.roster_speaker_found("20201105-02", "CLARIDA")

def check_po_counter_20201105_02_BARKIN():
    return ev.counter_speaker_found("20201105-02", "BARKIN")

def check_po_counter_20201105_02_HARKER():
    return ev.counter_speaker_found("20201105-02", "HARKER")

def check_po_counter_20201105_02_CLARIDA():
    return ev.counter_speaker_found("20201105-02", "CLARIDA")

def check_static_record_l1_20201105_03():
    return ev.record_shape_ok("20201105-03", 1)

def check_static_record_l2_20201105_03():
    return ev.record_shape_ok("20201105-03", 2)

def check_rh_foreign_l1_20201105_03():
    return ev.no_foreign_speaker("20201105-03", 1)

def check_rh_foreign_l2_20201105_03():
    return ev.no_foreign_speaker("20201105-03", 2)

def check_rh_padding_l1_20201105_03():
    return ev.no_padded_entries("20201105-03", 1)

def check_rh_padding_l2_20201105_03():
    return ev.no_padded_entries("20201105-03", 2)

def check_po_roster_20201105_03_QUARLES():
    return ev.roster_speaker_found("20201105-03", "QUARLES")

def check_po_roster_20201105_03_KAPLAN():
    return ev.roster_speaker_found("20201105-03", "KAPLAN")

def check_po_roster_20201105_03_ROSENGREN():
    return ev.roster_speaker_found("20201105-03", "ROSENGREN")

def check_po_roster_20201105_03_BARKIN():
    return ev.roster_speaker_found("20201105-03", "BARKIN")

def check_po_roster_20201105_03_BULLARD():
    return ev.roster_speaker_found("20201105-03", "BULLARD")

def check_po_roster_20201105_03_BOWMAN():
    return ev.roster_speaker_found("20201105-03", "BOWMAN")

def check_po_roster_20201105_03_BOSTIC():
    return ev.roster_speaker_found("20201105-03", "BOSTIC")

def check_po_roster_20201105_03_HARKER():
    return ev.roster_speaker_found("20201105-03", "HARKER")

def check_po_roster_20201105_03_GEORGE():
    return ev.roster_speaker_found("20201105-03", "GEORGE")

def check_po_roster_20201105_03_MESTER():
    return ev.roster_speaker_found("20201105-03", "MESTER")

def check_po_counter_20201105_03_POWELL():
    return ev.counter_speaker_found("20201105-03", "POWELL")

def check_po_counter_20201105_03_BRAINARD():
    return ev.counter_speaker_found("20201105-03", "BRAINARD")

def check_po_counter_20201105_03_DALY():
    return ev.counter_speaker_found("20201105-03", "DALY")

def check_po_counter_20201105_03_WILLIAMS():
    return ev.counter_speaker_found("20201105-03", "WILLIAMS")

def check_po_counter_20201105_03_EVANS():
    return ev.counter_speaker_found("20201105-03", "EVANS")

def check_static_record_l1_20201105_04():
    return ev.record_shape_ok("20201105-04", 1)

def check_static_record_l2_20201105_04():
    return ev.record_shape_ok("20201105-04", 2)

def check_rh_foreign_l1_20201105_04():
    return ev.no_foreign_speaker("20201105-04", 1)

def check_rh_foreign_l2_20201105_04():
    return ev.no_foreign_speaker("20201105-04", 2)

def check_rh_padding_l1_20201105_04():
    return ev.no_padded_entries("20201105-04", 1)

def check_rh_padding_l2_20201105_04():
    return ev.no_padded_entries("20201105-04", 2)

def check_po_roster_20201105_04_QUARLES():
    return ev.roster_speaker_found("20201105-04", "QUARLES")

def check_po_roster_20201105_04_KAPLAN():
    return ev.roster_speaker_found("20201105-04", "KAPLAN")

def check_po_roster_20201105_04_ROSENGREN():
    return ev.roster_speaker_found("20201105-04", "ROSENGREN")

def check_po_roster_20201105_04_BOWMAN():
    return ev.roster_speaker_found("20201105-04", "BOWMAN")

def check_po_roster_20201105_04_BRAINARD():
    return ev.roster_speaker_found("20201105-04", "BRAINARD")

def check_po_roster_20201105_04_GEORGE():
    return ev.roster_speaker_found("20201105-04", "GEORGE")

def check_po_counter_20201105_04_QUARLES():
    return ev.counter_speaker_found("20201105-04", "QUARLES")

def check_po_counter_20201105_04_BULLARD():
    return ev.counter_speaker_found("20201105-04", "BULLARD")

def check_po_counter_20201105_04_POWELL():
    return ev.counter_speaker_found("20201105-04", "POWELL")

def check_po_counter_20201105_04_FELDMAN():
    return ev.counter_speaker_found("20201105-04", "FELDMAN")

def check_po_counter_20201105_04_BRAINARD():
    return ev.counter_speaker_found("20201105-04", "BRAINARD")

def check_po_counter_20201105_04_HARKER():
    return ev.counter_speaker_found("20201105-04", "HARKER")

def check_po_counter_20201105_04_BOSTIC():
    return ev.counter_speaker_found("20201105-04", "BOSTIC")

def check_po_counter_20201105_04_WILLIAMS():
    return ev.counter_speaker_found("20201105-04", "WILLIAMS")

def check_po_counter_20201105_04_MESTER():
    return ev.counter_speaker_found("20201105-04", "MESTER")

def check_po_counter_20201105_04_EVANS():
    return ev.counter_speaker_found("20201105-04", "EVANS")

def check_po_counter_20201105_04_CLARIDA():
    return ev.counter_speaker_found("20201105-04", "CLARIDA")

def check_static_record_l1_20201105_05():
    return ev.record_shape_ok("20201105-05", 1)

def check_static_record_l2_20201105_05():
    return ev.record_shape_ok("20201105-05", 2)

def check_rh_foreign_l1_20201105_05():
    return ev.no_foreign_speaker("20201105-05", 1)

def check_rh_foreign_l2_20201105_05():
    return ev.no_foreign_speaker("20201105-05", 2)

def check_rh_padding_l1_20201105_05():
    return ev.no_padded_entries("20201105-05", 1)

def check_rh_padding_l2_20201105_05():
    return ev.no_padded_entries("20201105-05", 2)

def check_po_roster_20201105_05_BULLARD():
    return ev.roster_speaker_found("20201105-05", "BULLARD")

def check_po_roster_20201105_05_HARKER():
    return ev.roster_speaker_found("20201105-05", "HARKER")

def check_static_record_l1_20201105_06():
    return ev.record_shape_ok("20201105-06", 1)

def check_static_record_l2_20201105_06():
    return ev.record_shape_ok("20201105-06", 2)

def check_rh_foreign_l1_20201105_06():
    return ev.no_foreign_speaker("20201105-06", 1)

def check_rh_foreign_l2_20201105_06():
    return ev.no_foreign_speaker("20201105-06", 2)

def check_rh_padding_l1_20201105_06():
    return ev.no_padded_entries("20201105-06", 1)

def check_rh_padding_l2_20201105_06():
    return ev.no_padded_entries("20201105-06", 2)

def check_po_roster_20201105_06_QUARLES():
    return ev.roster_speaker_found("20201105-06", "QUARLES")

def check_po_roster_20201105_06_KAPLAN():
    return ev.roster_speaker_found("20201105-06", "KAPLAN")

def check_po_roster_20201105_06_ROSENGREN():
    return ev.roster_speaker_found("20201105-06", "ROSENGREN")

def check_po_roster_20201105_06_BARKIN():
    return ev.roster_speaker_found("20201105-06", "BARKIN")

def check_po_roster_20201105_06_BULLARD():
    return ev.roster_speaker_found("20201105-06", "BULLARD")

def check_po_roster_20201105_06_POWELL():
    return ev.roster_speaker_found("20201105-06", "POWELL")

def check_po_roster_20201105_06_BOWMAN():
    return ev.roster_speaker_found("20201105-06", "BOWMAN")

def check_po_roster_20201105_06_FELDMAN():
    return ev.roster_speaker_found("20201105-06", "FELDMAN")

def check_po_roster_20201105_06_BRAINARD():
    return ev.roster_speaker_found("20201105-06", "BRAINARD")

def check_po_roster_20201105_06_HARKER():
    return ev.roster_speaker_found("20201105-06", "HARKER")

def check_po_roster_20201105_06_WILLIAMS():
    return ev.roster_speaker_found("20201105-06", "WILLIAMS")

def check_po_roster_20201105_06_DALY():
    return ev.roster_speaker_found("20201105-06", "DALY")

def check_po_roster_20201105_06_GEORGE():
    return ev.roster_speaker_found("20201105-06", "GEORGE")

def check_po_roster_20201105_06_MESTER():
    return ev.roster_speaker_found("20201105-06", "MESTER")

def check_po_roster_20201105_06_EVANS():
    return ev.roster_speaker_found("20201105-06", "EVANS")

def check_po_roster_20201105_06_CLARIDA():
    return ev.roster_speaker_found("20201105-06", "CLARIDA")

def check_po_counter_20201105_06_GEORGE():
    return ev.counter_speaker_found("20201105-06", "GEORGE")

def check_static_record_l1_20201105_07():
    return ev.record_shape_ok("20201105-07", 1)

def check_static_record_l2_20201105_07():
    return ev.record_shape_ok("20201105-07", 2)

def check_rh_foreign_l1_20201105_07():
    return ev.no_foreign_speaker("20201105-07", 1)

def check_rh_foreign_l2_20201105_07():
    return ev.no_foreign_speaker("20201105-07", 2)

def check_rh_padding_l1_20201105_07():
    return ev.no_padded_entries("20201105-07", 1)

def check_rh_padding_l2_20201105_07():
    return ev.no_padded_entries("20201105-07", 2)

def check_po_roster_20201105_07_QUARLES():
    return ev.roster_speaker_found("20201105-07", "QUARLES")

def check_po_roster_20201105_07_KAPLAN():
    return ev.roster_speaker_found("20201105-07", "KAPLAN")

def check_po_roster_20201105_07_ROSENGREN():
    return ev.roster_speaker_found("20201105-07", "ROSENGREN")

def check_po_roster_20201105_07_BARKIN():
    return ev.roster_speaker_found("20201105-07", "BARKIN")

def check_po_roster_20201105_07_BULLARD():
    return ev.roster_speaker_found("20201105-07", "BULLARD")

def check_po_roster_20201105_07_BOSTIC():
    return ev.roster_speaker_found("20201105-07", "BOSTIC")

def check_po_roster_20201105_07_HARKER():
    return ev.roster_speaker_found("20201105-07", "HARKER")

def check_po_counter_20201105_07_POWELL():
    return ev.counter_speaker_found("20201105-07", "POWELL")

def check_po_counter_20201105_07_BOWMAN():
    return ev.counter_speaker_found("20201105-07", "BOWMAN")

def check_po_counter_20201105_07_BRAINARD():
    return ev.counter_speaker_found("20201105-07", "BRAINARD")

def check_po_counter_20201105_07_DALY():
    return ev.counter_speaker_found("20201105-07", "DALY")

def check_po_counter_20201105_07_WILLIAMS():
    return ev.counter_speaker_found("20201105-07", "WILLIAMS")

def check_po_counter_20201105_07_MESTER():
    return ev.counter_speaker_found("20201105-07", "MESTER")

def check_po_counter_20201105_07_EVANS():
    return ev.counter_speaker_found("20201105-07", "EVANS")

def check_static_record_l1_20201105_08():
    return ev.record_shape_ok("20201105-08", 1)

def check_static_record_l2_20201105_08():
    return ev.record_shape_ok("20201105-08", 2)

def check_rh_foreign_l1_20201105_08():
    return ev.no_foreign_speaker("20201105-08", 1)

def check_rh_foreign_l2_20201105_08():
    return ev.no_foreign_speaker("20201105-08", 2)

def check_rh_padding_l1_20201105_08():
    return ev.no_padded_entries("20201105-08", 1)

def check_rh_padding_l2_20201105_08():
    return ev.no_padded_entries("20201105-08", 2)

def check_po_roster_20201105_08_QUARLES():
    return ev.roster_speaker_found("20201105-08", "QUARLES")

def check_po_roster_20201105_08_BOWMAN():
    return ev.roster_speaker_found("20201105-08", "BOWMAN")

def check_po_roster_20201105_08_FELDMAN():
    return ev.roster_speaker_found("20201105-08", "FELDMAN")

def check_po_roster_20201105_08_POWELL():
    return ev.roster_speaker_found("20201105-08", "POWELL")

def check_po_roster_20201105_08_BRAINARD():
    return ev.roster_speaker_found("20201105-08", "BRAINARD")

def check_po_roster_20201105_08_DALY():
    return ev.roster_speaker_found("20201105-08", "DALY")

def check_po_roster_20201105_08_EVANS():
    return ev.roster_speaker_found("20201105-08", "EVANS")

def check_po_roster_20201105_08_CLARIDA():
    return ev.roster_speaker_found("20201105-08", "CLARIDA")

def check_po_counter_20201105_08_KAPLAN():
    return ev.counter_speaker_found("20201105-08", "KAPLAN")

def check_po_counter_20201105_08_MESTER():
    return ev.counter_speaker_found("20201105-08", "MESTER")

def check_static_record_l1_20201105_09():
    return ev.record_shape_ok("20201105-09", 1)

def check_static_record_l2_20201105_09():
    return ev.record_shape_ok("20201105-09", 2)

def check_rh_foreign_l1_20201105_09():
    return ev.no_foreign_speaker("20201105-09", 1)

def check_rh_foreign_l2_20201105_09():
    return ev.no_foreign_speaker("20201105-09", 2)

def check_rh_padding_l1_20201105_09():
    return ev.no_padded_entries("20201105-09", 1)

def check_rh_padding_l2_20201105_09():
    return ev.no_padded_entries("20201105-09", 2)

def check_po_roster_20201105_09_KAPLAN():
    return ev.roster_speaker_found("20201105-09", "KAPLAN")

def check_po_roster_20201105_09_POWELL():
    return ev.roster_speaker_found("20201105-09", "POWELL")

def check_po_roster_20201105_09_EVANS():
    return ev.roster_speaker_found("20201105-09", "EVANS")

def check_po_counter_20201105_09_HARKER():
    return ev.counter_speaker_found("20201105-09", "HARKER")

def check_static_record_l1_20201105_10():
    return ev.record_shape_ok("20201105-10", 1)

def check_static_record_l2_20201105_10():
    return ev.record_shape_ok("20201105-10", 2)

def check_rh_foreign_l1_20201105_10():
    return ev.no_foreign_speaker("20201105-10", 1)

def check_rh_foreign_l2_20201105_10():
    return ev.no_foreign_speaker("20201105-10", 2)

def check_rh_padding_l1_20201105_10():
    return ev.no_padded_entries("20201105-10", 1)

def check_rh_padding_l2_20201105_10():
    return ev.no_padded_entries("20201105-10", 2)

def check_po_roster_20201105_10_QUARLES():
    return ev.roster_speaker_found("20201105-10", "QUARLES")

def check_po_roster_20201105_10_ROSENGREN():
    return ev.roster_speaker_found("20201105-10", "ROSENGREN")

def check_po_roster_20201105_10_BOWMAN():
    return ev.roster_speaker_found("20201105-10", "BOWMAN")

def check_po_roster_20201105_10_BULLARD():
    return ev.roster_speaker_found("20201105-10", "BULLARD")

def check_po_roster_20201105_10_HARKER():
    return ev.roster_speaker_found("20201105-10", "HARKER")

def check_po_roster_20201105_10_GEORGE():
    return ev.roster_speaker_found("20201105-10", "GEORGE")

def check_po_counter_20201105_10_POWELL():
    return ev.counter_speaker_found("20201105-10", "POWELL")

def check_po_counter_20201105_10_WILLIAMS():
    return ev.counter_speaker_found("20201105-10", "WILLIAMS")

def check_po_counter_20201105_10_EVANS():
    return ev.counter_speaker_found("20201105-10", "EVANS")

def check_static_record_l1_20201105_11():
    return ev.record_shape_ok("20201105-11", 1)

def check_static_record_l2_20201105_11():
    return ev.record_shape_ok("20201105-11", 2)

def check_rh_foreign_l1_20201105_11():
    return ev.no_foreign_speaker("20201105-11", 1)

def check_rh_foreign_l2_20201105_11():
    return ev.no_foreign_speaker("20201105-11", 2)

def check_rh_padding_l1_20201105_11():
    return ev.no_padded_entries("20201105-11", 1)

def check_rh_padding_l2_20201105_11():
    return ev.no_padded_entries("20201105-11", 2)

def check_po_roster_20201105_11_KAPLAN():
    return ev.roster_speaker_found("20201105-11", "KAPLAN")

def check_po_roster_20201105_11_ROSENGREN():
    return ev.roster_speaker_found("20201105-11", "ROSENGREN")

def check_po_roster_20201105_11_BULLARD():
    return ev.roster_speaker_found("20201105-11", "BULLARD")

def check_po_roster_20201105_11_POWELL():
    return ev.roster_speaker_found("20201105-11", "POWELL")

def check_po_roster_20201105_11_FELDMAN():
    return ev.roster_speaker_found("20201105-11", "FELDMAN")

def check_po_roster_20201105_11_BRAINARD():
    return ev.roster_speaker_found("20201105-11", "BRAINARD")

def check_po_roster_20201105_11_BOSTIC():
    return ev.roster_speaker_found("20201105-11", "BOSTIC")

def check_po_roster_20201105_11_HARKER():
    return ev.roster_speaker_found("20201105-11", "HARKER")

def check_po_roster_20201105_11_WILLIAMS():
    return ev.roster_speaker_found("20201105-11", "WILLIAMS")

def check_po_roster_20201105_11_EVANS():
    return ev.roster_speaker_found("20201105-11", "EVANS")

def check_po_roster_20201105_11_CLARIDA():
    return ev.roster_speaker_found("20201105-11", "CLARIDA")

def check_po_counter_20201105_11_QUARLES():
    return ev.counter_speaker_found("20201105-11", "QUARLES")

def check_po_counter_20201105_11_BARKIN():
    return ev.counter_speaker_found("20201105-11", "BARKIN")

def check_po_counter_20201105_11_DALY():
    return ev.counter_speaker_found("20201105-11", "DALY")

def check_po_counter_20201105_11_CLARIDA():
    return ev.counter_speaker_found("20201105-11", "CLARIDA")

def check_static_record_l1_20201105_12():
    return ev.record_shape_ok("20201105-12", 1)

def check_static_record_l2_20201105_12():
    return ev.record_shape_ok("20201105-12", 2)

def check_rh_foreign_l1_20201105_12():
    return ev.no_foreign_speaker("20201105-12", 1)

def check_rh_foreign_l2_20201105_12():
    return ev.no_foreign_speaker("20201105-12", 2)

def check_rh_padding_l1_20201105_12():
    return ev.no_padded_entries("20201105-12", 1)

def check_rh_padding_l2_20201105_12():
    return ev.no_padded_entries("20201105-12", 2)

def check_po_roster_20201105_12_QUARLES():
    return ev.roster_speaker_found("20201105-12", "QUARLES")

def check_po_roster_20201105_12_KAPLAN():
    return ev.roster_speaker_found("20201105-12", "KAPLAN")

def check_po_roster_20201105_12_ROSENGREN():
    return ev.roster_speaker_found("20201105-12", "ROSENGREN")

def check_po_roster_20201105_12_FELDMAN():
    return ev.roster_speaker_found("20201105-12", "FELDMAN")

def check_po_roster_20201105_12_BOWMAN():
    return ev.roster_speaker_found("20201105-12", "BOWMAN")

def check_po_roster_20201105_12_BULLARD():
    return ev.roster_speaker_found("20201105-12", "BULLARD")

def check_po_roster_20201105_12_WILLIAMS():
    return ev.roster_speaker_found("20201105-12", "WILLIAMS")

def check_po_roster_20201105_12_DALY():
    return ev.roster_speaker_found("20201105-12", "DALY")

def check_po_roster_20201105_12_EVANS():
    return ev.roster_speaker_found("20201105-12", "EVANS")

def check_po_roster_20201105_12_CLARIDA():
    return ev.roster_speaker_found("20201105-12", "CLARIDA")

def check_po_counter_20201105_12_QUARLES():
    return ev.counter_speaker_found("20201105-12", "QUARLES")

def check_po_counter_20201105_12_EVANS():
    return ev.counter_speaker_found("20201105-12", "EVANS")

def check_static_record_l1_20201105_13():
    return ev.record_shape_ok("20201105-13", 1)

def check_static_record_l2_20201105_13():
    return ev.record_shape_ok("20201105-13", 2)

def check_rh_foreign_l1_20201105_13():
    return ev.no_foreign_speaker("20201105-13", 1)

def check_rh_foreign_l2_20201105_13():
    return ev.no_foreign_speaker("20201105-13", 2)

def check_rh_padding_l1_20201105_13():
    return ev.no_padded_entries("20201105-13", 1)

def check_rh_padding_l2_20201105_13():
    return ev.no_padded_entries("20201105-13", 2)

def check_po_roster_20201105_13_QUARLES():
    return ev.roster_speaker_found("20201105-13", "QUARLES")

def check_po_roster_20201105_13_BARKIN():
    return ev.roster_speaker_found("20201105-13", "BARKIN")

def check_po_roster_20201105_13_HARKER():
    return ev.roster_speaker_found("20201105-13", "HARKER")

def check_po_roster_20201105_13_MESTER():
    return ev.roster_speaker_found("20201105-13", "MESTER")

def check_po_roster_20201105_13_CLARIDA():
    return ev.roster_speaker_found("20201105-13", "CLARIDA")

def check_po_counter_20201105_13_KAPLAN():
    return ev.counter_speaker_found("20201105-13", "KAPLAN")

def check_po_counter_20201105_13_POWELL():
    return ev.counter_speaker_found("20201105-13", "POWELL")

def check_po_counter_20201105_13_BRAINARD():
    return ev.counter_speaker_found("20201105-13", "BRAINARD")

def check_po_counter_20201105_13_BOSTIC():
    return ev.counter_speaker_found("20201105-13", "BOSTIC")

def check_po_counter_20201105_13_GEORGE():
    return ev.counter_speaker_found("20201105-13", "GEORGE")

def check_po_counter_20201105_13_DALY():
    return ev.counter_speaker_found("20201105-13", "DALY")

def check_static_record_l1_20201105_14():
    return ev.record_shape_ok("20201105-14", 1)

def check_static_record_l2_20201105_14():
    return ev.record_shape_ok("20201105-14", 2)

def check_rh_foreign_l1_20201105_14():
    return ev.no_foreign_speaker("20201105-14", 1)

def check_rh_foreign_l2_20201105_14():
    return ev.no_foreign_speaker("20201105-14", 2)

def check_rh_padding_l1_20201105_14():
    return ev.no_padded_entries("20201105-14", 1)

def check_rh_padding_l2_20201105_14():
    return ev.no_padded_entries("20201105-14", 2)

def check_po_roster_20201105_14_KAPLAN():
    return ev.roster_speaker_found("20201105-14", "KAPLAN")

def check_po_roster_20201105_14_POWELL():
    return ev.roster_speaker_found("20201105-14", "POWELL")

def check_po_roster_20201105_14_BOWMAN():
    return ev.roster_speaker_found("20201105-14", "BOWMAN")

def check_po_roster_20201105_14_BRAINARD():
    return ev.roster_speaker_found("20201105-14", "BRAINARD")

def check_po_roster_20201105_14_BOSTIC():
    return ev.roster_speaker_found("20201105-14", "BOSTIC")

def check_po_roster_20201105_14_GEORGE():
    return ev.roster_speaker_found("20201105-14", "GEORGE")

def check_po_counter_20201105_14_BARKIN():
    return ev.counter_speaker_found("20201105-14", "BARKIN")

def check_po_counter_20201105_14_BULLARD():
    return ev.counter_speaker_found("20201105-14", "BULLARD")

def check_po_counter_20201105_14_HARKER():
    return ev.counter_speaker_found("20201105-14", "HARKER")

def check_po_counter_20201105_14_CLARIDA():
    return ev.counter_speaker_found("20201105-14", "CLARIDA")

def check_static_record_l1_20201105_15():
    return ev.record_shape_ok("20201105-15", 1)

def check_static_record_l2_20201105_15():
    return ev.record_shape_ok("20201105-15", 2)

def check_rh_foreign_l1_20201105_15():
    return ev.no_foreign_speaker("20201105-15", 1)

def check_rh_foreign_l2_20201105_15():
    return ev.no_foreign_speaker("20201105-15", 2)

def check_rh_padding_l1_20201105_15():
    return ev.no_padded_entries("20201105-15", 1)

def check_rh_padding_l2_20201105_15():
    return ev.no_padded_entries("20201105-15", 2)

def check_po_roster_20201105_15_QUARLES():
    return ev.roster_speaker_found("20201105-15", "QUARLES")

def check_po_roster_20201105_15_KAPLAN():
    return ev.roster_speaker_found("20201105-15", "KAPLAN")

def check_po_roster_20201105_15_BARKIN():
    return ev.roster_speaker_found("20201105-15", "BARKIN")

def check_po_roster_20201105_15_BULLARD():
    return ev.roster_speaker_found("20201105-15", "BULLARD")

def check_po_roster_20201105_15_BOSTIC():
    return ev.roster_speaker_found("20201105-15", "BOSTIC")

def check_po_roster_20201105_15_HARKER():
    return ev.roster_speaker_found("20201105-15", "HARKER")

def check_po_roster_20201105_15_MESTER():
    return ev.roster_speaker_found("20201105-15", "MESTER")

def check_po_roster_20201105_15_EVANS():
    return ev.roster_speaker_found("20201105-15", "EVANS")

def check_po_counter_20201105_15_MESTER():
    return ev.counter_speaker_found("20201105-15", "MESTER")

def check_po_counter_20201105_15_EVANS():
    return ev.counter_speaker_found("20201105-15", "EVANS")

def check_static_record_l1_20201105_16():
    return ev.record_shape_ok("20201105-16", 1)

def check_static_record_l2_20201105_16():
    return ev.record_shape_ok("20201105-16", 2)

def check_rh_foreign_l1_20201105_16():
    return ev.no_foreign_speaker("20201105-16", 1)

def check_rh_foreign_l2_20201105_16():
    return ev.no_foreign_speaker("20201105-16", 2)

def check_rh_padding_l1_20201105_16():
    return ev.no_padded_entries("20201105-16", 1)

def check_rh_padding_l2_20201105_16():
    return ev.no_padded_entries("20201105-16", 2)

def check_po_roster_20201105_16_QUARLES():
    return ev.roster_speaker_found("20201105-16", "QUARLES")

def check_po_roster_20201105_16_KAPLAN():
    return ev.roster_speaker_found("20201105-16", "KAPLAN")

def check_po_roster_20201105_16_ROSENGREN():
    return ev.roster_speaker_found("20201105-16", "ROSENGREN")

def check_po_roster_20201105_16_BARKIN():
    return ev.roster_speaker_found("20201105-16", "BARKIN")

def check_po_roster_20201105_16_BRAINARD():
    return ev.roster_speaker_found("20201105-16", "BRAINARD")

def check_po_roster_20201105_16_CLARIDA():
    return ev.roster_speaker_found("20201105-16", "CLARIDA")

def check_static_record_l1_20201105_17():
    return ev.record_shape_ok("20201105-17", 1)

def check_static_record_l2_20201105_17():
    return ev.record_shape_ok("20201105-17", 2)

def check_rh_foreign_l1_20201105_17():
    return ev.no_foreign_speaker("20201105-17", 1)

def check_rh_foreign_l2_20201105_17():
    return ev.no_foreign_speaker("20201105-17", 2)

def check_rh_padding_l1_20201105_17():
    return ev.no_padded_entries("20201105-17", 1)

def check_rh_padding_l2_20201105_17():
    return ev.no_padded_entries("20201105-17", 2)

def check_po_roster_20201105_17_ROSENGREN():
    return ev.roster_speaker_found("20201105-17", "ROSENGREN")

def check_po_roster_20201105_17_BARKIN():
    return ev.roster_speaker_found("20201105-17", "BARKIN")

def check_po_roster_20201105_17_POWELL():
    return ev.roster_speaker_found("20201105-17", "POWELL")

def check_po_roster_20201105_17_BULLARD():
    return ev.roster_speaker_found("20201105-17", "BULLARD")

def check_po_roster_20201105_17_FELDMAN():
    return ev.roster_speaker_found("20201105-17", "FELDMAN")

def check_po_roster_20201105_17_BRAINARD():
    return ev.roster_speaker_found("20201105-17", "BRAINARD")

def check_po_roster_20201105_17_BOSTIC():
    return ev.roster_speaker_found("20201105-17", "BOSTIC")

def check_po_roster_20201105_17_DALY():
    return ev.roster_speaker_found("20201105-17", "DALY")

def check_po_roster_20201105_17_GEORGE():
    return ev.roster_speaker_found("20201105-17", "GEORGE")

def check_po_roster_20201105_17_MESTER():
    return ev.roster_speaker_found("20201105-17", "MESTER")

def check_po_counter_20201105_17_QUARLES():
    return ev.counter_speaker_found("20201105-17", "QUARLES")

def check_static_record_l1_20201105_18():
    return ev.record_shape_ok("20201105-18", 1)

def check_static_record_l2_20201105_18():
    return ev.record_shape_ok("20201105-18", 2)

def check_rh_foreign_l1_20201105_18():
    return ev.no_foreign_speaker("20201105-18", 1)

def check_rh_foreign_l2_20201105_18():
    return ev.no_foreign_speaker("20201105-18", 2)

def check_rh_padding_l1_20201105_18():
    return ev.no_padded_entries("20201105-18", 1)

def check_rh_padding_l2_20201105_18():
    return ev.no_padded_entries("20201105-18", 2)

def check_po_roster_20201105_18_QUARLES():
    return ev.roster_speaker_found("20201105-18", "QUARLES")

def check_po_roster_20201105_18_ROSENGREN():
    return ev.roster_speaker_found("20201105-18", "ROSENGREN")

def check_po_roster_20201105_18_BULLARD():
    return ev.roster_speaker_found("20201105-18", "BULLARD")

def check_po_roster_20201105_18_BRAINARD():
    return ev.roster_speaker_found("20201105-18", "BRAINARD")

def check_po_roster_20201105_18_WILLIAMS():
    return ev.roster_speaker_found("20201105-18", "WILLIAMS")

def check_po_roster_20201105_18_DALY():
    return ev.roster_speaker_found("20201105-18", "DALY")

def check_static_record_l1_20201105_19():
    return ev.record_shape_ok("20201105-19", 1)

def check_static_record_l2_20201105_19():
    return ev.record_shape_ok("20201105-19", 2)

def check_rh_foreign_l1_20201105_19():
    return ev.no_foreign_speaker("20201105-19", 1)

def check_rh_foreign_l2_20201105_19():
    return ev.no_foreign_speaker("20201105-19", 2)

def check_rh_padding_l1_20201105_19():
    return ev.no_padded_entries("20201105-19", 1)

def check_rh_padding_l2_20201105_19():
    return ev.no_padded_entries("20201105-19", 2)

def check_po_roster_20201105_19_KAPLAN():
    return ev.roster_speaker_found("20201105-19", "KAPLAN")

def check_po_roster_20201105_19_ROSENGREN():
    return ev.roster_speaker_found("20201105-19", "ROSENGREN")

def check_po_roster_20201105_19_BRAINARD():
    return ev.roster_speaker_found("20201105-19", "BRAINARD")

def check_po_counter_20201105_19_DALY():
    return ev.counter_speaker_found("20201105-19", "DALY")

def check_static_record_l1_20201105_20():
    return ev.record_shape_ok("20201105-20", 1)

def check_static_record_l2_20201105_20():
    return ev.record_shape_ok("20201105-20", 2)

def check_rh_foreign_l1_20201105_20():
    return ev.no_foreign_speaker("20201105-20", 1)

def check_rh_foreign_l2_20201105_20():
    return ev.no_foreign_speaker("20201105-20", 2)

def check_rh_padding_l1_20201105_20():
    return ev.no_padded_entries("20201105-20", 1)

def check_rh_padding_l2_20201105_20():
    return ev.no_padded_entries("20201105-20", 2)

def check_po_roster_20201105_20_QUARLES():
    return ev.roster_speaker_found("20201105-20", "QUARLES")

def check_po_roster_20201105_20_KAPLAN():
    return ev.roster_speaker_found("20201105-20", "KAPLAN")

def check_po_roster_20201105_20_BARKIN():
    return ev.roster_speaker_found("20201105-20", "BARKIN")

def check_po_roster_20201105_20_BRAINARD():
    return ev.roster_speaker_found("20201105-20", "BRAINARD")

def check_po_roster_20201105_20_BOSTIC():
    return ev.roster_speaker_found("20201105-20", "BOSTIC")

def check_po_roster_20201105_20_WILLIAMS():
    return ev.roster_speaker_found("20201105-20", "WILLIAMS")

def check_po_roster_20201105_20_GEORGE():
    return ev.roster_speaker_found("20201105-20", "GEORGE")

def check_po_roster_20201105_20_MESTER():
    return ev.roster_speaker_found("20201105-20", "MESTER")

def check_po_counter_20201105_20_EVANS():
    return ev.counter_speaker_found("20201105-20", "EVANS")

def check_static_record_l1_20201105_21():
    return ev.record_shape_ok("20201105-21", 1)

def check_static_record_l2_20201105_21():
    return ev.record_shape_ok("20201105-21", 2)

def check_rh_foreign_l1_20201105_21():
    return ev.no_foreign_speaker("20201105-21", 1)

def check_rh_foreign_l2_20201105_21():
    return ev.no_foreign_speaker("20201105-21", 2)

def check_rh_padding_l1_20201105_21():
    return ev.no_padded_entries("20201105-21", 1)

def check_rh_padding_l2_20201105_21():
    return ev.no_padded_entries("20201105-21", 2)

def check_po_roster_20201105_21_QUARLES():
    return ev.roster_speaker_found("20201105-21", "QUARLES")

def check_po_roster_20201105_21_KAPLAN():
    return ev.roster_speaker_found("20201105-21", "KAPLAN")

def check_po_roster_20201105_21_BRAINARD():
    return ev.roster_speaker_found("20201105-21", "BRAINARD")

def check_po_roster_20201105_21_BOSTIC():
    return ev.roster_speaker_found("20201105-21", "BOSTIC")

def check_po_roster_20201105_21_EVANS():
    return ev.roster_speaker_found("20201105-21", "EVANS")

def check_static_record_l1_20201105_22():
    return ev.record_shape_ok("20201105-22", 1)

def check_static_record_l2_20201105_22():
    return ev.record_shape_ok("20201105-22", 2)

def check_rh_foreign_l1_20201105_22():
    return ev.no_foreign_speaker("20201105-22", 1)

def check_rh_foreign_l2_20201105_22():
    return ev.no_foreign_speaker("20201105-22", 2)

def check_rh_padding_l1_20201105_22():
    return ev.no_padded_entries("20201105-22", 1)

def check_rh_padding_l2_20201105_22():
    return ev.no_padded_entries("20201105-22", 2)

def check_po_roster_20201105_22_QUARLES():
    return ev.roster_speaker_found("20201105-22", "QUARLES")

def check_po_roster_20201105_22_KAPLAN():
    return ev.roster_speaker_found("20201105-22", "KAPLAN")

def check_po_roster_20201105_22_BARKIN():
    return ev.roster_speaker_found("20201105-22", "BARKIN")

def check_po_roster_20201105_22_POWELL():
    return ev.roster_speaker_found("20201105-22", "POWELL")

def check_po_roster_20201105_22_FELDMAN():
    return ev.roster_speaker_found("20201105-22", "FELDMAN")

def check_po_roster_20201105_22_BOWMAN():
    return ev.roster_speaker_found("20201105-22", "BOWMAN")

def check_po_roster_20201105_22_BRAINARD():
    return ev.roster_speaker_found("20201105-22", "BRAINARD")

def check_po_roster_20201105_22_BOSTIC():
    return ev.roster_speaker_found("20201105-22", "BOSTIC")

def check_po_roster_20201105_22_WILLIAMS():
    return ev.roster_speaker_found("20201105-22", "WILLIAMS")

def check_po_roster_20201105_22_GEORGE():
    return ev.roster_speaker_found("20201105-22", "GEORGE")

def check_po_roster_20201105_22_DALY():
    return ev.roster_speaker_found("20201105-22", "DALY")

def check_po_roster_20201105_22_MESTER():
    return ev.roster_speaker_found("20201105-22", "MESTER")

def check_po_roster_20201105_22_EVANS():
    return ev.roster_speaker_found("20201105-22", "EVANS")

def check_po_roster_20201105_22_CLARIDA():
    return ev.roster_speaker_found("20201105-22", "CLARIDA")

def check_po_counter_20201105_22_BULLARD():
    return ev.counter_speaker_found("20201105-22", "BULLARD")

def check_po_counter_20201105_22_CLARIDA():
    return ev.counter_speaker_found("20201105-22", "CLARIDA")

def check_static_record_l1_20201105_23():
    return ev.record_shape_ok("20201105-23", 1)

def check_static_record_l2_20201105_23():
    return ev.record_shape_ok("20201105-23", 2)

def check_rh_foreign_l1_20201105_23():
    return ev.no_foreign_speaker("20201105-23", 1)

def check_rh_foreign_l2_20201105_23():
    return ev.no_foreign_speaker("20201105-23", 2)

def check_rh_padding_l1_20201105_23():
    return ev.no_padded_entries("20201105-23", 1)

def check_rh_padding_l2_20201105_23():
    return ev.no_padded_entries("20201105-23", 2)

def check_po_roster_20201105_23_QUARLES():
    return ev.roster_speaker_found("20201105-23", "QUARLES")

def check_po_roster_20201105_23_ROSENGREN():
    return ev.roster_speaker_found("20201105-23", "ROSENGREN")

def check_po_roster_20201105_23_BULLARD():
    return ev.roster_speaker_found("20201105-23", "BULLARD")

def check_po_roster_20201105_23_POWELL():
    return ev.roster_speaker_found("20201105-23", "POWELL")

def check_po_roster_20201105_23_FELDMAN():
    return ev.roster_speaker_found("20201105-23", "FELDMAN")

def check_po_roster_20201105_23_BRAINARD():
    return ev.roster_speaker_found("20201105-23", "BRAINARD")

def check_po_roster_20201105_23_WILLIAMS():
    return ev.roster_speaker_found("20201105-23", "WILLIAMS")

def check_po_roster_20201105_23_GEORGE():
    return ev.roster_speaker_found("20201105-23", "GEORGE")

def check_po_roster_20201105_23_DALY():
    return ev.roster_speaker_found("20201105-23", "DALY")

def check_po_roster_20201105_23_CLARIDA():
    return ev.roster_speaker_found("20201105-23", "CLARIDA")

def check_static_record_l1_20201105_24():
    return ev.record_shape_ok("20201105-24", 1)

def check_static_record_l2_20201105_24():
    return ev.record_shape_ok("20201105-24", 2)

def check_rh_foreign_l1_20201105_24():
    return ev.no_foreign_speaker("20201105-24", 1)

def check_rh_foreign_l2_20201105_24():
    return ev.no_foreign_speaker("20201105-24", 2)

def check_rh_padding_l1_20201105_24():
    return ev.no_padded_entries("20201105-24", 1)

def check_rh_padding_l2_20201105_24():
    return ev.no_padded_entries("20201105-24", 2)

def check_po_roster_20201105_24_KAPLAN():
    return ev.roster_speaker_found("20201105-24", "KAPLAN")

def check_po_roster_20201105_24_ROSENGREN():
    return ev.roster_speaker_found("20201105-24", "ROSENGREN")

def check_po_roster_20201105_24_BULLARD():
    return ev.roster_speaker_found("20201105-24", "BULLARD")

def check_po_roster_20201105_24_FELDMAN():
    return ev.roster_speaker_found("20201105-24", "FELDMAN")

def check_po_roster_20201105_24_BOSTIC():
    return ev.roster_speaker_found("20201105-24", "BOSTIC")

def check_po_roster_20201105_24_BRAINARD():
    return ev.roster_speaker_found("20201105-24", "BRAINARD")

def check_po_roster_20201105_24_GEORGE():
    return ev.roster_speaker_found("20201105-24", "GEORGE")

def check_po_roster_20201105_24_MESTER():
    return ev.roster_speaker_found("20201105-24", "MESTER")

def check_po_roster_20201105_24_EVANS():
    return ev.roster_speaker_found("20201105-24", "EVANS")

def check_po_counter_20201105_24_KAPLAN():
    return ev.counter_speaker_found("20201105-24", "KAPLAN")

def check_po_counter_20201105_24_BULLARD():
    return ev.counter_speaker_found("20201105-24", "BULLARD")

def check_po_counter_20201105_24_DALY():
    return ev.counter_speaker_found("20201105-24", "DALY")

def check_static_record_l1_20201105_25():
    return ev.record_shape_ok("20201105-25", 1)

def check_static_record_l2_20201105_25():
    return ev.record_shape_ok("20201105-25", 2)

def check_rh_foreign_l1_20201105_25():
    return ev.no_foreign_speaker("20201105-25", 1)

def check_rh_foreign_l2_20201105_25():
    return ev.no_foreign_speaker("20201105-25", 2)

def check_rh_padding_l1_20201105_25():
    return ev.no_padded_entries("20201105-25", 1)

def check_rh_padding_l2_20201105_25():
    return ev.no_padded_entries("20201105-25", 2)

def check_po_roster_20201105_25_QUARLES():
    return ev.roster_speaker_found("20201105-25", "QUARLES")

def check_po_roster_20201105_25_KAPLAN():
    return ev.roster_speaker_found("20201105-25", "KAPLAN")

def check_po_roster_20201105_25_ROSENGREN():
    return ev.roster_speaker_found("20201105-25", "ROSENGREN")

def check_po_roster_20201105_25_BARKIN():
    return ev.roster_speaker_found("20201105-25", "BARKIN")

def check_po_roster_20201105_25_BOWMAN():
    return ev.roster_speaker_found("20201105-25", "BOWMAN")

def check_po_roster_20201105_25_FELDMAN():
    return ev.roster_speaker_found("20201105-25", "FELDMAN")

def check_po_roster_20201105_25_BRAINARD():
    return ev.roster_speaker_found("20201105-25", "BRAINARD")

def check_po_roster_20201105_25_BOSTIC():
    return ev.roster_speaker_found("20201105-25", "BOSTIC")

def check_po_roster_20201105_25_HARKER():
    return ev.roster_speaker_found("20201105-25", "HARKER")

def check_po_roster_20201105_25_GEORGE():
    return ev.roster_speaker_found("20201105-25", "GEORGE")

def check_po_roster_20201105_25_DALY():
    return ev.roster_speaker_found("20201105-25", "DALY")

def check_po_roster_20201105_25_WILLIAMS():
    return ev.roster_speaker_found("20201105-25", "WILLIAMS")

def check_po_roster_20201105_25_MESTER():
    return ev.roster_speaker_found("20201105-25", "MESTER")

def check_static_record_l1_20201105_26():
    return ev.record_shape_ok("20201105-26", 1)

def check_static_record_l2_20201105_26():
    return ev.record_shape_ok("20201105-26", 2)

def check_rh_foreign_l1_20201105_26():
    return ev.no_foreign_speaker("20201105-26", 1)

def check_rh_foreign_l2_20201105_26():
    return ev.no_foreign_speaker("20201105-26", 2)

def check_rh_padding_l1_20201105_26():
    return ev.no_padded_entries("20201105-26", 1)

def check_rh_padding_l2_20201105_26():
    return ev.no_padded_entries("20201105-26", 2)

def check_po_roster_20201105_26_QUARLES():
    return ev.roster_speaker_found("20201105-26", "QUARLES")

def check_po_roster_20201105_26_BOWMAN():
    return ev.roster_speaker_found("20201105-26", "BOWMAN")

def check_po_roster_20201105_26_DALY():
    return ev.roster_speaker_found("20201105-26", "DALY")

def check_po_roster_20201105_26_MESTER():
    return ev.roster_speaker_found("20201105-26", "MESTER")

def check_po_counter_20201105_26_FELDMAN():
    return ev.counter_speaker_found("20201105-26", "FELDMAN")

def check_po_counter_20201105_26_GEORGE():
    return ev.counter_speaker_found("20201105-26", "GEORGE")

def check_static_record_l1_20201105_27():
    return ev.record_shape_ok("20201105-27", 1)

def check_static_record_l2_20201105_27():
    return ev.record_shape_ok("20201105-27", 2)

def check_rh_foreign_l1_20201105_27():
    return ev.no_foreign_speaker("20201105-27", 1)

def check_rh_foreign_l2_20201105_27():
    return ev.no_foreign_speaker("20201105-27", 2)

def check_rh_padding_l1_20201105_27():
    return ev.no_padded_entries("20201105-27", 1)

def check_rh_padding_l2_20201105_27():
    return ev.no_padded_entries("20201105-27", 2)

def check_po_roster_20201105_27_ROSENGREN():
    return ev.roster_speaker_found("20201105-27", "ROSENGREN")

def check_po_roster_20201105_27_FELDMAN():
    return ev.roster_speaker_found("20201105-27", "FELDMAN")

def check_po_roster_20201105_27_BRAINARD():
    return ev.roster_speaker_found("20201105-27", "BRAINARD")

def check_po_roster_20201105_27_GEORGE():
    return ev.roster_speaker_found("20201105-27", "GEORGE")

def check_po_roster_20201105_27_MESTER():
    return ev.roster_speaker_found("20201105-27", "MESTER")

def check_po_counter_20201105_27_QUARLES():
    return ev.counter_speaker_found("20201105-27", "QUARLES")

def check_static_record_l1_20201105_28():
    return ev.record_shape_ok("20201105-28", 1)

def check_static_record_l2_20201105_28():
    return ev.record_shape_ok("20201105-28", 2)

def check_rh_foreign_l1_20201105_28():
    return ev.no_foreign_speaker("20201105-28", 1)

def check_rh_foreign_l2_20201105_28():
    return ev.no_foreign_speaker("20201105-28", 2)

def check_rh_padding_l1_20201105_28():
    return ev.no_padded_entries("20201105-28", 1)

def check_rh_padding_l2_20201105_28():
    return ev.no_padded_entries("20201105-28", 2)

def check_po_roster_20201105_28_QUARLES():
    return ev.roster_speaker_found("20201105-28", "QUARLES")

def check_po_roster_20201105_28_KAPLAN():
    return ev.roster_speaker_found("20201105-28", "KAPLAN")

def check_po_roster_20201105_28_BRAINARD():
    return ev.roster_speaker_found("20201105-28", "BRAINARD")

def check_po_roster_20201105_28_GEORGE():
    return ev.roster_speaker_found("20201105-28", "GEORGE")

def check_po_roster_20201105_28_MESTER():
    return ev.roster_speaker_found("20201105-28", "MESTER")

def check_static_record_l1_20201105_29():
    return ev.record_shape_ok("20201105-29", 1)

def check_static_record_l2_20201105_29():
    return ev.record_shape_ok("20201105-29", 2)

def check_rh_foreign_l1_20201105_29():
    return ev.no_foreign_speaker("20201105-29", 1)

def check_rh_foreign_l2_20201105_29():
    return ev.no_foreign_speaker("20201105-29", 2)

def check_rh_padding_l1_20201105_29():
    return ev.no_padded_entries("20201105-29", 1)

def check_rh_padding_l2_20201105_29():
    return ev.no_padded_entries("20201105-29", 2)

def check_po_roster_20201105_29_ROSENGREN():
    return ev.roster_speaker_found("20201105-29", "ROSENGREN")

def check_po_roster_20201105_29_BARKIN():
    return ev.roster_speaker_found("20201105-29", "BARKIN")

def check_po_roster_20201105_29_BOWMAN():
    return ev.roster_speaker_found("20201105-29", "BOWMAN")

def check_po_counter_20201105_29_QUARLES():
    return ev.counter_speaker_found("20201105-29", "QUARLES")

def check_po_counter_20201105_29_DALY():
    return ev.counter_speaker_found("20201105-29", "DALY")

def check_po_counter_20201105_29_EVANS():
    return ev.counter_speaker_found("20201105-29", "EVANS")

def check_static_record_l1_20201105_30():
    return ev.record_shape_ok("20201105-30", 1)

def check_static_record_l2_20201105_30():
    return ev.record_shape_ok("20201105-30", 2)

def check_rh_foreign_l1_20201105_30():
    return ev.no_foreign_speaker("20201105-30", 1)

def check_rh_foreign_l2_20201105_30():
    return ev.no_foreign_speaker("20201105-30", 2)

def check_rh_padding_l1_20201105_30():
    return ev.no_padded_entries("20201105-30", 1)

def check_rh_padding_l2_20201105_30():
    return ev.no_padded_entries("20201105-30", 2)

def check_po_roster_20201105_30_BRAINARD():
    return ev.roster_speaker_found("20201105-30", "BRAINARD")

def check_po_roster_20201105_30_DALY():
    return ev.roster_speaker_found("20201105-30", "DALY")

def check_po_roster_20201105_30_MESTER():
    return ev.roster_speaker_found("20201105-30", "MESTER")

def check_static_record_l1_20201105_31():
    return ev.record_shape_ok("20201105-31", 1)

def check_static_record_l2_20201105_31():
    return ev.record_shape_ok("20201105-31", 2)

def check_rh_foreign_l1_20201105_31():
    return ev.no_foreign_speaker("20201105-31", 1)

def check_rh_foreign_l2_20201105_31():
    return ev.no_foreign_speaker("20201105-31", 2)

def check_rh_padding_l1_20201105_31():
    return ev.no_padded_entries("20201105-31", 1)

def check_rh_padding_l2_20201105_31():
    return ev.no_padded_entries("20201105-31", 2)

def check_po_roster_20201105_31_QUARLES():
    return ev.roster_speaker_found("20201105-31", "QUARLES")

def check_po_roster_20201105_31_BULLARD():
    return ev.roster_speaker_found("20201105-31", "BULLARD")

def check_po_roster_20201105_31_FELDMAN():
    return ev.roster_speaker_found("20201105-31", "FELDMAN")

def check_po_roster_20201105_31_DALY():
    return ev.roster_speaker_found("20201105-31", "DALY")

def check_po_roster_20201105_31_MESTER():
    return ev.roster_speaker_found("20201105-31", "MESTER")

def check_po_counter_20201105_31_ROSENGREN():
    return ev.counter_speaker_found("20201105-31", "ROSENGREN")

def check_po_counter_20201105_31_BARKIN():
    return ev.counter_speaker_found("20201105-31", "BARKIN")

def check_po_counter_20201105_31_BOWMAN():
    return ev.counter_speaker_found("20201105-31", "BOWMAN")

def check_po_counter_20201105_31_BOSTIC():
    return ev.counter_speaker_found("20201105-31", "BOSTIC")

def check_po_counter_20201105_31_HARKER():
    return ev.counter_speaker_found("20201105-31", "HARKER")

def check_static_record_l1_20201105_32():
    return ev.record_shape_ok("20201105-32", 1)

def check_static_record_l2_20201105_32():
    return ev.record_shape_ok("20201105-32", 2)

def check_rh_foreign_l1_20201105_32():
    return ev.no_foreign_speaker("20201105-32", 1)

def check_rh_foreign_l2_20201105_32():
    return ev.no_foreign_speaker("20201105-32", 2)

def check_rh_padding_l1_20201105_32():
    return ev.no_padded_entries("20201105-32", 1)

def check_rh_padding_l2_20201105_32():
    return ev.no_padded_entries("20201105-32", 2)

def check_po_roster_20201105_32_KAPLAN():
    return ev.roster_speaker_found("20201105-32", "KAPLAN")

def check_po_roster_20201105_32_ROSENGREN():
    return ev.roster_speaker_found("20201105-32", "ROSENGREN")

def check_po_roster_20201105_32_BULLARD():
    return ev.roster_speaker_found("20201105-32", "BULLARD")

def check_po_roster_20201105_32_POWELL():
    return ev.roster_speaker_found("20201105-32", "POWELL")

def check_po_roster_20201105_32_BRAINARD():
    return ev.roster_speaker_found("20201105-32", "BRAINARD")

def check_po_roster_20201105_32_WILLIAMS():
    return ev.roster_speaker_found("20201105-32", "WILLIAMS")

def check_static_record_l1_20201105_33():
    return ev.record_shape_ok("20201105-33", 1)

def check_static_record_l2_20201105_33():
    return ev.record_shape_ok("20201105-33", 2)

def check_rh_foreign_l1_20201105_33():
    return ev.no_foreign_speaker("20201105-33", 1)

def check_rh_foreign_l2_20201105_33():
    return ev.no_foreign_speaker("20201105-33", 2)

def check_rh_padding_l1_20201105_33():
    return ev.no_padded_entries("20201105-33", 1)

def check_rh_padding_l2_20201105_33():
    return ev.no_padded_entries("20201105-33", 2)

def check_po_roster_20201105_33_ROSENGREN():
    return ev.roster_speaker_found("20201105-33", "ROSENGREN")

def check_po_roster_20201105_33_POWELL():
    return ev.roster_speaker_found("20201105-33", "POWELL")

def check_po_roster_20201105_33_FELDMAN():
    return ev.roster_speaker_found("20201105-33", "FELDMAN")

def check_po_roster_20201105_33_BRAINARD():
    return ev.roster_speaker_found("20201105-33", "BRAINARD")

def check_po_roster_20201105_33_WILLIAMS():
    return ev.roster_speaker_found("20201105-33", "WILLIAMS")

def check_static_record_l1_20201105_34():
    return ev.record_shape_ok("20201105-34", 1)

def check_static_record_l2_20201105_34():
    return ev.record_shape_ok("20201105-34", 2)

def check_rh_foreign_l1_20201105_34():
    return ev.no_foreign_speaker("20201105-34", 1)

def check_rh_foreign_l2_20201105_34():
    return ev.no_foreign_speaker("20201105-34", 2)

def check_rh_padding_l1_20201105_34():
    return ev.no_padded_entries("20201105-34", 1)

def check_rh_padding_l2_20201105_34():
    return ev.no_padded_entries("20201105-34", 2)

def check_po_roster_20201105_34_QUARLES():
    return ev.roster_speaker_found("20201105-34", "QUARLES")

def check_po_roster_20201105_34_BARKIN():
    return ev.roster_speaker_found("20201105-34", "BARKIN")

def check_po_roster_20201105_34_BRAINARD():
    return ev.roster_speaker_found("20201105-34", "BRAINARD")

def check_po_roster_20201105_34_HARKER():
    return ev.roster_speaker_found("20201105-34", "HARKER")

def check_po_roster_20201105_34_WILLIAMS():
    return ev.roster_speaker_found("20201105-34", "WILLIAMS")

def check_po_roster_20201105_34_DALY():
    return ev.roster_speaker_found("20201105-34", "DALY")

def check_po_roster_20201105_34_CLARIDA():
    return ev.roster_speaker_found("20201105-34", "CLARIDA")

def check_po_counter_20201105_34_BULLARD():
    return ev.counter_speaker_found("20201105-34", "BULLARD")

def check_po_counter_20201105_34_EVANS():
    return ev.counter_speaker_found("20201105-34", "EVANS")

def check_static_record_l1_20201105_35():
    return ev.record_shape_ok("20201105-35", 1)

def check_static_record_l2_20201105_35():
    return ev.record_shape_ok("20201105-35", 2)

def check_rh_foreign_l1_20201105_35():
    return ev.no_foreign_speaker("20201105-35", 1)

def check_rh_foreign_l2_20201105_35():
    return ev.no_foreign_speaker("20201105-35", 2)

def check_rh_padding_l1_20201105_35():
    return ev.no_padded_entries("20201105-35", 1)

def check_rh_padding_l2_20201105_35():
    return ev.no_padded_entries("20201105-35", 2)

def check_po_roster_20201105_35_KAPLAN():
    return ev.roster_speaker_found("20201105-35", "KAPLAN")

def check_po_roster_20201105_35_BARKIN():
    return ev.roster_speaker_found("20201105-35", "BARKIN")

def check_po_roster_20201105_35_POWELL():
    return ev.roster_speaker_found("20201105-35", "POWELL")

def check_po_roster_20201105_35_BOWMAN():
    return ev.roster_speaker_found("20201105-35", "BOWMAN")

def check_po_roster_20201105_35_FELDMAN():
    return ev.roster_speaker_found("20201105-35", "FELDMAN")

def check_po_roster_20201105_35_BRAINARD():
    return ev.roster_speaker_found("20201105-35", "BRAINARD")

def check_po_roster_20201105_35_BOSTIC():
    return ev.roster_speaker_found("20201105-35", "BOSTIC")

def check_po_roster_20201105_35_WILLIAMS():
    return ev.roster_speaker_found("20201105-35", "WILLIAMS")

def check_po_roster_20201105_35_DALY():
    return ev.roster_speaker_found("20201105-35", "DALY")

def check_po_roster_20201105_35_GEORGE():
    return ev.roster_speaker_found("20201105-35", "GEORGE")

def check_po_roster_20201105_35_MESTER():
    return ev.roster_speaker_found("20201105-35", "MESTER")

def check_po_counter_20201105_35_QUARLES():
    return ev.counter_speaker_found("20201105-35", "QUARLES")

def check_po_counter_20201105_35_ROSENGREN():
    return ev.counter_speaker_found("20201105-35", "ROSENGREN")

def check_po_counter_20201105_35_BULLARD():
    return ev.counter_speaker_found("20201105-35", "BULLARD")

def check_po_counter_20201105_35_HARKER():
    return ev.counter_speaker_found("20201105-35", "HARKER")

def check_po_counter_20201105_35_DALY():
    return ev.counter_speaker_found("20201105-35", "DALY")

def check_po_counter_20201105_35_EVANS():
    return ev.counter_speaker_found("20201105-35", "EVANS")

def check_po_counter_20201105_35_CLARIDA():
    return ev.counter_speaker_found("20201105-35", "CLARIDA")

def check_static_record_l1_20201105_36():
    return ev.record_shape_ok("20201105-36", 1)

def check_static_record_l2_20201105_36():
    return ev.record_shape_ok("20201105-36", 2)

def check_rh_foreign_l1_20201105_36():
    return ev.no_foreign_speaker("20201105-36", 1)

def check_rh_foreign_l2_20201105_36():
    return ev.no_foreign_speaker("20201105-36", 2)

def check_rh_padding_l1_20201105_36():
    return ev.no_padded_entries("20201105-36", 1)

def check_rh_padding_l2_20201105_36():
    return ev.no_padded_entries("20201105-36", 2)

def check_po_roster_20201105_36_KAPLAN():
    return ev.roster_speaker_found("20201105-36", "KAPLAN")

def check_po_roster_20201105_36_POWELL():
    return ev.roster_speaker_found("20201105-36", "POWELL")

def check_po_roster_20201105_36_BOWMAN():
    return ev.roster_speaker_found("20201105-36", "BOWMAN")

def check_po_roster_20201105_36_BULLARD():
    return ev.roster_speaker_found("20201105-36", "BULLARD")

def check_po_roster_20201105_36_FELDMAN():
    return ev.roster_speaker_found("20201105-36", "FELDMAN")

def check_po_roster_20201105_36_BRAINARD():
    return ev.roster_speaker_found("20201105-36", "BRAINARD")

def check_po_roster_20201105_36_DALY():
    return ev.roster_speaker_found("20201105-36", "DALY")

def check_po_roster_20201105_36_WILLIAMS():
    return ev.roster_speaker_found("20201105-36", "WILLIAMS")

def check_po_roster_20201105_36_GEORGE():
    return ev.roster_speaker_found("20201105-36", "GEORGE")

def check_po_roster_20201105_36_MESTER():
    return ev.roster_speaker_found("20201105-36", "MESTER")

def check_po_roster_20201105_36_EVANS():
    return ev.roster_speaker_found("20201105-36", "EVANS")

def check_po_counter_20201105_36_BARKIN():
    return ev.counter_speaker_found("20201105-36", "BARKIN")

def check_po_counter_20201105_36_QUARLES():
    return ev.counter_speaker_found("20201105-36", "QUARLES")

def check_po_counter_20201105_36_BULLARD():
    return ev.counter_speaker_found("20201105-36", "BULLARD")

def check_po_counter_20201105_36_BOSTIC():
    return ev.counter_speaker_found("20201105-36", "BOSTIC")

def check_po_counter_20201105_36_HARKER():
    return ev.counter_speaker_found("20201105-36", "HARKER")

def check_po_counter_20201105_36_CLARIDA():
    return ev.counter_speaker_found("20201105-36", "CLARIDA")

def check_static_record_l1_20201105_37():
    return ev.record_shape_ok("20201105-37", 1)

def check_static_record_l2_20201105_37():
    return ev.record_shape_ok("20201105-37", 2)

def check_rh_foreign_l1_20201105_37():
    return ev.no_foreign_speaker("20201105-37", 1)

def check_rh_foreign_l2_20201105_37():
    return ev.no_foreign_speaker("20201105-37", 2)

def check_rh_padding_l1_20201105_37():
    return ev.no_padded_entries("20201105-37", 1)

def check_rh_padding_l2_20201105_37():
    return ev.no_padded_entries("20201105-37", 2)

def check_po_roster_20201105_37_QUARLES():
    return ev.roster_speaker_found("20201105-37", "QUARLES")

def check_po_roster_20201105_37_KAPLAN():
    return ev.roster_speaker_found("20201105-37", "KAPLAN")

def check_po_roster_20201105_37_ROSENGREN():
    return ev.roster_speaker_found("20201105-37", "ROSENGREN")

def check_po_roster_20201105_37_BARKIN():
    return ev.roster_speaker_found("20201105-37", "BARKIN")

def check_po_roster_20201105_37_POWELL():
    return ev.roster_speaker_found("20201105-37", "POWELL")

def check_po_roster_20201105_37_BULLARD():
    return ev.roster_speaker_found("20201105-37", "BULLARD")

def check_po_roster_20201105_37_BOWMAN():
    return ev.roster_speaker_found("20201105-37", "BOWMAN")

def check_po_roster_20201105_37_FELDMAN():
    return ev.roster_speaker_found("20201105-37", "FELDMAN")

def check_po_roster_20201105_37_BRAINARD():
    return ev.roster_speaker_found("20201105-37", "BRAINARD")

def check_po_roster_20201105_37_HARKER():
    return ev.roster_speaker_found("20201105-37", "HARKER")

def check_po_roster_20201105_37_WILLIAMS():
    return ev.roster_speaker_found("20201105-37", "WILLIAMS")

def check_po_roster_20201105_37_DALY():
    return ev.roster_speaker_found("20201105-37", "DALY")

def check_po_roster_20201105_37_MESTER():
    return ev.roster_speaker_found("20201105-37", "MESTER")

def check_po_roster_20201105_37_EVANS():
    return ev.roster_speaker_found("20201105-37", "EVANS")

def check_po_roster_20201105_37_CLARIDA():
    return ev.roster_speaker_found("20201105-37", "CLARIDA")

def check_po_counter_20201105_37_BOSTIC():
    return ev.counter_speaker_found("20201105-37", "BOSTIC")

def check_po_counter_20201105_37_HARKER():
    return ev.counter_speaker_found("20201105-37", "HARKER")

def check_po_counter_20201105_37_GEORGE():
    return ev.counter_speaker_found("20201105-37", "GEORGE")

def check_static_record_l1_20201105_38():
    return ev.record_shape_ok("20201105-38", 1)

def check_static_record_l2_20201105_38():
    return ev.record_shape_ok("20201105-38", 2)

def check_rh_foreign_l1_20201105_38():
    return ev.no_foreign_speaker("20201105-38", 1)

def check_rh_foreign_l2_20201105_38():
    return ev.no_foreign_speaker("20201105-38", 2)

def check_rh_padding_l1_20201105_38():
    return ev.no_padded_entries("20201105-38", 1)

def check_rh_padding_l2_20201105_38():
    return ev.no_padded_entries("20201105-38", 2)

def check_po_roster_20201105_38_QUARLES():
    return ev.roster_speaker_found("20201105-38", "QUARLES")

def check_po_roster_20201105_38_BARKIN():
    return ev.roster_speaker_found("20201105-38", "BARKIN")

def check_po_roster_20201105_38_ROSENGREN():
    return ev.roster_speaker_found("20201105-38", "ROSENGREN")

def check_po_roster_20201105_38_BULLARD():
    return ev.roster_speaker_found("20201105-38", "BULLARD")

def check_po_roster_20201105_38_BOSTIC():
    return ev.roster_speaker_found("20201105-38", "BOSTIC")

def check_po_roster_20201105_38_HARKER():
    return ev.roster_speaker_found("20201105-38", "HARKER")

def check_po_roster_20201105_38_CLARIDA():
    return ev.roster_speaker_found("20201105-38", "CLARIDA")

def check_po_counter_20201105_38_POWELL():
    return ev.counter_speaker_found("20201105-38", "POWELL")

def check_po_counter_20201105_38_BOWMAN():
    return ev.counter_speaker_found("20201105-38", "BOWMAN")

def check_po_counter_20201105_38_BRAINARD():
    return ev.counter_speaker_found("20201105-38", "BRAINARD")

def check_po_counter_20201105_38_DALY():
    return ev.counter_speaker_found("20201105-38", "DALY")

def check_po_counter_20201105_38_WILLIAMS():
    return ev.counter_speaker_found("20201105-38", "WILLIAMS")

def check_po_counter_20201105_38_MESTER():
    return ev.counter_speaker_found("20201105-38", "MESTER")

def check_po_counter_20201105_38_EVANS():
    return ev.counter_speaker_found("20201105-38", "EVANS")

def check_static_record_l1_20201105_39():
    return ev.record_shape_ok("20201105-39", 1)

def check_static_record_l2_20201105_39():
    return ev.record_shape_ok("20201105-39", 2)

def check_rh_foreign_l1_20201105_39():
    return ev.no_foreign_speaker("20201105-39", 1)

def check_rh_foreign_l2_20201105_39():
    return ev.no_foreign_speaker("20201105-39", 2)

def check_rh_padding_l1_20201105_39():
    return ev.no_padded_entries("20201105-39", 1)

def check_rh_padding_l2_20201105_39():
    return ev.no_padded_entries("20201105-39", 2)

def check_po_roster_20201105_39_KAPLAN():
    return ev.roster_speaker_found("20201105-39", "KAPLAN")

def check_po_roster_20201105_39_ROSENGREN():
    return ev.roster_speaker_found("20201105-39", "ROSENGREN")

def check_po_roster_20201105_39_BOWMAN():
    return ev.roster_speaker_found("20201105-39", "BOWMAN")

def check_po_roster_20201105_39_POWELL():
    return ev.roster_speaker_found("20201105-39", "POWELL")

def check_po_roster_20201105_39_GEORGE():
    return ev.roster_speaker_found("20201105-39", "GEORGE")

def check_po_roster_20201105_39_DALY():
    return ev.roster_speaker_found("20201105-39", "DALY")

def check_po_roster_20201105_39_CLARIDA():
    return ev.roster_speaker_found("20201105-39", "CLARIDA")

def check_po_roster_20201105_39_MESTER():
    return ev.roster_speaker_found("20201105-39", "MESTER")

def check_po_counter_20201105_39_BARKIN():
    return ev.counter_speaker_found("20201105-39", "BARKIN")

def check_po_counter_20201105_39_BOWMAN():
    return ev.counter_speaker_found("20201105-39", "BOWMAN")

def check_static_record_l1_20201105_40():
    return ev.record_shape_ok("20201105-40", 1)

def check_static_record_l2_20201105_40():
    return ev.record_shape_ok("20201105-40", 2)

def check_rh_foreign_l1_20201105_40():
    return ev.no_foreign_speaker("20201105-40", 1)

def check_rh_foreign_l2_20201105_40():
    return ev.no_foreign_speaker("20201105-40", 2)

def check_rh_padding_l1_20201105_40():
    return ev.no_padded_entries("20201105-40", 1)

def check_rh_padding_l2_20201105_40():
    return ev.no_padded_entries("20201105-40", 2)

def check_po_roster_20201105_40_BARKIN():
    return ev.roster_speaker_found("20201105-40", "BARKIN")

def check_po_roster_20201105_40_BULLARD():
    return ev.roster_speaker_found("20201105-40", "BULLARD")

def check_po_roster_20201105_40_DALY():
    return ev.roster_speaker_found("20201105-40", "DALY")

def check_po_roster_20201105_40_GEORGE():
    return ev.roster_speaker_found("20201105-40", "GEORGE")

def check_po_roster_20201105_40_WILLIAMS():
    return ev.roster_speaker_found("20201105-40", "WILLIAMS")

def check_po_roster_20201105_40_CLARIDA():
    return ev.roster_speaker_found("20201105-40", "CLARIDA")

def check_po_roster_20201105_40_MESTER():
    return ev.roster_speaker_found("20201105-40", "MESTER")

def check_static_record_l1_20201216_01():
    return ev.record_shape_ok("20201216-01", 1)

def check_static_record_l2_20201216_01():
    return ev.record_shape_ok("20201216-01", 2)

def check_rh_foreign_l1_20201216_01():
    return ev.no_foreign_speaker("20201216-01", 1)

def check_rh_foreign_l2_20201216_01():
    return ev.no_foreign_speaker("20201216-01", 2)

def check_rh_padding_l1_20201216_01():
    return ev.no_padded_entries("20201216-01", 1)

def check_rh_padding_l2_20201216_01():
    return ev.no_padded_entries("20201216-01", 2)

def check_po_roster_20201216_01_POWELL():
    return ev.roster_speaker_found("20201216-01", "POWELL")

def check_po_roster_20201216_01_BRAINARD():
    return ev.roster_speaker_found("20201216-01", "BRAINARD")

def check_po_roster_20201216_01_HARKER():
    return ev.roster_speaker_found("20201216-01", "HARKER")

def check_po_roster_20201216_01_QUARLES():
    return ev.roster_speaker_found("20201216-01", "QUARLES")

def check_po_roster_20201216_01_ROSENGREN():
    return ev.roster_speaker_found("20201216-01", "ROSENGREN")

def check_po_roster_20201216_01_GEORGE():
    return ev.roster_speaker_found("20201216-01", "GEORGE")

def check_po_roster_20201216_01_WILLIAMS():
    return ev.roster_speaker_found("20201216-01", "WILLIAMS")

def check_po_roster_20201216_01_BOWMAN():
    return ev.roster_speaker_found("20201216-01", "BOWMAN")

def check_po_counter_20201216_01_BARKIN():
    return ev.counter_speaker_found("20201216-01", "BARKIN")

def check_po_counter_20201216_01_HARKER():
    return ev.counter_speaker_found("20201216-01", "HARKER")

def check_po_counter_20201216_01_BULLARD():
    return ev.counter_speaker_found("20201216-01", "BULLARD")

def check_static_record_l1_20201216_02():
    return ev.record_shape_ok("20201216-02", 1)

def check_static_record_l2_20201216_02():
    return ev.record_shape_ok("20201216-02", 2)

def check_rh_foreign_l1_20201216_02():
    return ev.no_foreign_speaker("20201216-02", 1)

def check_rh_foreign_l2_20201216_02():
    return ev.no_foreign_speaker("20201216-02", 2)

def check_rh_padding_l1_20201216_02():
    return ev.no_padded_entries("20201216-02", 1)

def check_rh_padding_l2_20201216_02():
    return ev.no_padded_entries("20201216-02", 2)

def check_po_roster_20201216_02_POWELL():
    return ev.roster_speaker_found("20201216-02", "POWELL")

def check_po_roster_20201216_02_BRAINARD():
    return ev.roster_speaker_found("20201216-02", "BRAINARD")

def check_po_roster_20201216_02_KAPLAN():
    return ev.roster_speaker_found("20201216-02", "KAPLAN")

def check_po_roster_20201216_02_BARKIN():
    return ev.roster_speaker_found("20201216-02", "BARKIN")

def check_po_roster_20201216_02_MESTER():
    return ev.roster_speaker_found("20201216-02", "MESTER")

def check_po_roster_20201216_02_KASHKARI():
    return ev.roster_speaker_found("20201216-02", "KASHKARI")

def check_po_roster_20201216_02_EVANS():
    return ev.roster_speaker_found("20201216-02", "EVANS")

def check_po_roster_20201216_02_BOSTIC():
    return ev.roster_speaker_found("20201216-02", "BOSTIC")

def check_po_roster_20201216_02_GEORGE():
    return ev.roster_speaker_found("20201216-02", "GEORGE")

def check_po_roster_20201216_02_DALY():
    return ev.roster_speaker_found("20201216-02", "DALY")

def check_po_roster_20201216_02_BOWMAN():
    return ev.roster_speaker_found("20201216-02", "BOWMAN")

def check_po_counter_20201216_02_QUARLES():
    return ev.counter_speaker_found("20201216-02", "QUARLES")

def check_static_record_l1_20201216_03():
    return ev.record_shape_ok("20201216-03", 1)

def check_static_record_l2_20201216_03():
    return ev.record_shape_ok("20201216-03", 2)

def check_rh_foreign_l1_20201216_03():
    return ev.no_foreign_speaker("20201216-03", 1)

def check_rh_foreign_l2_20201216_03():
    return ev.no_foreign_speaker("20201216-03", 2)

def check_rh_padding_l1_20201216_03():
    return ev.no_padded_entries("20201216-03", 1)

def check_rh_padding_l2_20201216_03():
    return ev.no_padded_entries("20201216-03", 2)

def check_po_roster_20201216_03_BARKIN():
    return ev.roster_speaker_found("20201216-03", "BARKIN")

def check_po_roster_20201216_03_GEORGE():
    return ev.roster_speaker_found("20201216-03", "GEORGE")

def check_static_record_l1_20201216_04():
    return ev.record_shape_ok("20201216-04", 1)

def check_static_record_l2_20201216_04():
    return ev.record_shape_ok("20201216-04", 2)

def check_rh_foreign_l1_20201216_04():
    return ev.no_foreign_speaker("20201216-04", 1)

def check_rh_foreign_l2_20201216_04():
    return ev.no_foreign_speaker("20201216-04", 2)

def check_rh_padding_l1_20201216_04():
    return ev.no_padded_entries("20201216-04", 1)

def check_rh_padding_l2_20201216_04():
    return ev.no_padded_entries("20201216-04", 2)

def check_po_roster_20201216_04_BRAINARD():
    return ev.roster_speaker_found("20201216-04", "BRAINARD")

def check_po_roster_20201216_04_KAPLAN():
    return ev.roster_speaker_found("20201216-04", "KAPLAN")

def check_po_roster_20201216_04_MESTER():
    return ev.roster_speaker_found("20201216-04", "MESTER")

def check_po_roster_20201216_04_QUARLES():
    return ev.roster_speaker_found("20201216-04", "QUARLES")

def check_po_roster_20201216_04_EVANS():
    return ev.roster_speaker_found("20201216-04", "EVANS")

def check_po_roster_20201216_04_BOSTIC():
    return ev.roster_speaker_found("20201216-04", "BOSTIC")

def check_po_roster_20201216_04_GEORGE():
    return ev.roster_speaker_found("20201216-04", "GEORGE")

def check_po_roster_20201216_04_DALY():
    return ev.roster_speaker_found("20201216-04", "DALY")

def check_po_roster_20201216_04_BOWMAN():
    return ev.roster_speaker_found("20201216-04", "BOWMAN")

def check_static_record_l1_20201216_05():
    return ev.record_shape_ok("20201216-05", 1)

def check_static_record_l2_20201216_05():
    return ev.record_shape_ok("20201216-05", 2)

def check_rh_foreign_l1_20201216_05():
    return ev.no_foreign_speaker("20201216-05", 1)

def check_rh_foreign_l2_20201216_05():
    return ev.no_foreign_speaker("20201216-05", 2)

def check_rh_padding_l1_20201216_05():
    return ev.no_padded_entries("20201216-05", 1)

def check_rh_padding_l2_20201216_05():
    return ev.no_padded_entries("20201216-05", 2)

def check_po_roster_20201216_05_BRAINARD():
    return ev.roster_speaker_found("20201216-05", "BRAINARD")

def check_po_roster_20201216_05_BARKIN():
    return ev.roster_speaker_found("20201216-05", "BARKIN")

def check_po_roster_20201216_05_POWELL():
    return ev.roster_speaker_found("20201216-05", "POWELL")

def check_po_roster_20201216_05_CLARIDA():
    return ev.roster_speaker_found("20201216-05", "CLARIDA")

def check_po_roster_20201216_05_QUARLES():
    return ev.roster_speaker_found("20201216-05", "QUARLES")

def check_static_record_l1_20201216_06():
    return ev.record_shape_ok("20201216-06", 1)

def check_static_record_l2_20201216_06():
    return ev.record_shape_ok("20201216-06", 2)

def check_rh_foreign_l1_20201216_06():
    return ev.no_foreign_speaker("20201216-06", 1)

def check_rh_foreign_l2_20201216_06():
    return ev.no_foreign_speaker("20201216-06", 2)

def check_rh_padding_l1_20201216_06():
    return ev.no_padded_entries("20201216-06", 1)

def check_rh_padding_l2_20201216_06():
    return ev.no_padded_entries("20201216-06", 2)

def check_po_roster_20201216_06_KAPLAN():
    return ev.roster_speaker_found("20201216-06", "KAPLAN")

def check_po_roster_20201216_06_POWELL():
    return ev.roster_speaker_found("20201216-06", "POWELL")

def check_po_roster_20201216_06_BARKIN():
    return ev.roster_speaker_found("20201216-06", "BARKIN")

def check_po_roster_20201216_06_MESTER():
    return ev.roster_speaker_found("20201216-06", "MESTER")

def check_po_roster_20201216_06_ROSENGREN():
    return ev.roster_speaker_found("20201216-06", "ROSENGREN")

def check_po_roster_20201216_06_EVANS():
    return ev.roster_speaker_found("20201216-06", "EVANS")

def check_po_roster_20201216_06_BOSTIC():
    return ev.roster_speaker_found("20201216-06", "BOSTIC")

def check_po_roster_20201216_06_GEORGE():
    return ev.roster_speaker_found("20201216-06", "GEORGE")

def check_po_roster_20201216_06_DALY():
    return ev.roster_speaker_found("20201216-06", "DALY")

def check_po_roster_20201216_06_WILLIAMS():
    return ev.roster_speaker_found("20201216-06", "WILLIAMS")

def check_po_counter_20201216_06_BULLARD():
    return ev.counter_speaker_found("20201216-06", "BULLARD")

def check_po_counter_20201216_06_DALY():
    return ev.counter_speaker_found("20201216-06", "DALY")

def check_static_record_l1_20201216_07():
    return ev.record_shape_ok("20201216-07", 1)

def check_static_record_l2_20201216_07():
    return ev.record_shape_ok("20201216-07", 2)

def check_rh_foreign_l1_20201216_07():
    return ev.no_foreign_speaker("20201216-07", 1)

def check_rh_foreign_l2_20201216_07():
    return ev.no_foreign_speaker("20201216-07", 2)

def check_rh_padding_l1_20201216_07():
    return ev.no_padded_entries("20201216-07", 1)

def check_rh_padding_l2_20201216_07():
    return ev.no_padded_entries("20201216-07", 2)

def check_po_roster_20201216_07_BARKIN():
    return ev.roster_speaker_found("20201216-07", "BARKIN")

def check_po_roster_20201216_07_KAPLAN():
    return ev.roster_speaker_found("20201216-07", "KAPLAN")

def check_po_roster_20201216_07_CLARIDA():
    return ev.roster_speaker_found("20201216-07", "CLARIDA")

def check_po_roster_20201216_07_ROSENGREN():
    return ev.roster_speaker_found("20201216-07", "ROSENGREN")

def check_po_roster_20201216_07_BOSTIC():
    return ev.roster_speaker_found("20201216-07", "BOSTIC")

def check_po_roster_20201216_07_DALY():
    return ev.roster_speaker_found("20201216-07", "DALY")

def check_po_counter_20201216_07_BULLARD():
    return ev.counter_speaker_found("20201216-07", "BULLARD")

def check_po_counter_20201216_07_WILLIAMS():
    return ev.counter_speaker_found("20201216-07", "WILLIAMS")

def check_static_record_l1_20201216_08():
    return ev.record_shape_ok("20201216-08", 1)

def check_static_record_l2_20201216_08():
    return ev.record_shape_ok("20201216-08", 2)

def check_rh_foreign_l1_20201216_08():
    return ev.no_foreign_speaker("20201216-08", 1)

def check_rh_foreign_l2_20201216_08():
    return ev.no_foreign_speaker("20201216-08", 2)

def check_rh_padding_l1_20201216_08():
    return ev.no_padded_entries("20201216-08", 1)

def check_rh_padding_l2_20201216_08():
    return ev.no_padded_entries("20201216-08", 2)

def check_po_roster_20201216_08_KAPLAN():
    return ev.roster_speaker_found("20201216-08", "KAPLAN")

def check_po_roster_20201216_08_BRAINARD():
    return ev.roster_speaker_found("20201216-08", "BRAINARD")

def check_po_roster_20201216_08_MESTER():
    return ev.roster_speaker_found("20201216-08", "MESTER")

def check_po_roster_20201216_08_GEORGE():
    return ev.roster_speaker_found("20201216-08", "GEORGE")

def check_po_counter_20201216_08_CLARIDA():
    return ev.counter_speaker_found("20201216-08", "CLARIDA")

def check_po_counter_20201216_08_QUARLES():
    return ev.counter_speaker_found("20201216-08", "QUARLES")

def check_po_counter_20201216_08_GEORGE():
    return ev.counter_speaker_found("20201216-08", "GEORGE")

def check_po_counter_20201216_08_BOSTIC():
    return ev.counter_speaker_found("20201216-08", "BOSTIC")

def check_static_record_l1_20201216_09():
    return ev.record_shape_ok("20201216-09", 1)

def check_static_record_l2_20201216_09():
    return ev.record_shape_ok("20201216-09", 2)

def check_rh_foreign_l1_20201216_09():
    return ev.no_foreign_speaker("20201216-09", 1)

def check_rh_foreign_l2_20201216_09():
    return ev.no_foreign_speaker("20201216-09", 2)

def check_rh_padding_l1_20201216_09():
    return ev.no_padded_entries("20201216-09", 1)

def check_rh_padding_l2_20201216_09():
    return ev.no_padded_entries("20201216-09", 2)

def check_po_roster_20201216_09_BRAINARD():
    return ev.roster_speaker_found("20201216-09", "BRAINARD")

def check_po_roster_20201216_09_BARKIN():
    return ev.roster_speaker_found("20201216-09", "BARKIN")

def check_po_roster_20201216_09_QUARLES():
    return ev.roster_speaker_found("20201216-09", "QUARLES")

def check_po_roster_20201216_09_BULLARD():
    return ev.roster_speaker_found("20201216-09", "BULLARD")

def check_po_roster_20201216_09_WILLIAMS():
    return ev.roster_speaker_found("20201216-09", "WILLIAMS")

def check_static_record_l1_20201216_10():
    return ev.record_shape_ok("20201216-10", 1)

def check_static_record_l2_20201216_10():
    return ev.record_shape_ok("20201216-10", 2)

def check_rh_foreign_l1_20201216_10():
    return ev.no_foreign_speaker("20201216-10", 1)

def check_rh_foreign_l2_20201216_10():
    return ev.no_foreign_speaker("20201216-10", 2)

def check_rh_padding_l1_20201216_10():
    return ev.no_padded_entries("20201216-10", 1)

def check_rh_padding_l2_20201216_10():
    return ev.no_padded_entries("20201216-10", 2)

def check_po_roster_20201216_10_KAPLAN():
    return ev.roster_speaker_found("20201216-10", "KAPLAN")

def check_po_roster_20201216_10_BRAINARD():
    return ev.roster_speaker_found("20201216-10", "BRAINARD")

def check_po_roster_20201216_10_MESTER():
    return ev.roster_speaker_found("20201216-10", "MESTER")

def check_po_roster_20201216_10_QUARLES():
    return ev.roster_speaker_found("20201216-10", "QUARLES")

def check_po_roster_20201216_10_BOWMAN():
    return ev.roster_speaker_found("20201216-10", "BOWMAN")

def check_static_record_l1_20201216_11():
    return ev.record_shape_ok("20201216-11", 1)

def check_static_record_l2_20201216_11():
    return ev.record_shape_ok("20201216-11", 2)

def check_rh_foreign_l1_20201216_11():
    return ev.no_foreign_speaker("20201216-11", 1)

def check_rh_foreign_l2_20201216_11():
    return ev.no_foreign_speaker("20201216-11", 2)

def check_rh_padding_l1_20201216_11():
    return ev.no_padded_entries("20201216-11", 1)

def check_rh_padding_l2_20201216_11():
    return ev.no_padded_entries("20201216-11", 2)

def check_po_roster_20201216_11_BARKIN():
    return ev.roster_speaker_found("20201216-11", "BARKIN")

def check_po_roster_20201216_11_ROSENGREN():
    return ev.roster_speaker_found("20201216-11", "ROSENGREN")

def check_po_roster_20201216_11_BOWMAN():
    return ev.roster_speaker_found("20201216-11", "BOWMAN")

def check_static_record_l1_20201216_12():
    return ev.record_shape_ok("20201216-12", 1)

def check_static_record_l2_20201216_12():
    return ev.record_shape_ok("20201216-12", 2)

def check_rh_foreign_l1_20201216_12():
    return ev.no_foreign_speaker("20201216-12", 1)

def check_rh_foreign_l2_20201216_12():
    return ev.no_foreign_speaker("20201216-12", 2)

def check_rh_padding_l1_20201216_12():
    return ev.no_padded_entries("20201216-12", 1)

def check_rh_padding_l2_20201216_12():
    return ev.no_padded_entries("20201216-12", 2)

def check_po_roster_20201216_12_BRAINARD():
    return ev.roster_speaker_found("20201216-12", "BRAINARD")

def check_po_roster_20201216_12_KAPLAN():
    return ev.roster_speaker_found("20201216-12", "KAPLAN")

def check_po_roster_20201216_12_POWELL():
    return ev.roster_speaker_found("20201216-12", "POWELL")

def check_po_roster_20201216_12_MESTER():
    return ev.roster_speaker_found("20201216-12", "MESTER")

def check_po_roster_20201216_12_ROSENGREN():
    return ev.roster_speaker_found("20201216-12", "ROSENGREN")

def check_po_roster_20201216_12_GEORGE():
    return ev.roster_speaker_found("20201216-12", "GEORGE")

def check_po_counter_20201216_12_QUARLES():
    return ev.counter_speaker_found("20201216-12", "QUARLES")

def check_static_record_l1_20201216_13():
    return ev.record_shape_ok("20201216-13", 1)

def check_static_record_l2_20201216_13():
    return ev.record_shape_ok("20201216-13", 2)

def check_rh_foreign_l1_20201216_13():
    return ev.no_foreign_speaker("20201216-13", 1)

def check_rh_foreign_l2_20201216_13():
    return ev.no_foreign_speaker("20201216-13", 2)

def check_rh_padding_l1_20201216_13():
    return ev.no_padded_entries("20201216-13", 1)

def check_rh_padding_l2_20201216_13():
    return ev.no_padded_entries("20201216-13", 2)

def check_po_roster_20201216_13_POWELL():
    return ev.roster_speaker_found("20201216-13", "POWELL")

def check_po_roster_20201216_13_BRAINARD():
    return ev.roster_speaker_found("20201216-13", "BRAINARD")

def check_po_roster_20201216_13_BARKIN():
    return ev.roster_speaker_found("20201216-13", "BARKIN")

def check_po_roster_20201216_13_MESTER():
    return ev.roster_speaker_found("20201216-13", "MESTER")

def check_po_roster_20201216_13_CLARIDA():
    return ev.roster_speaker_found("20201216-13", "CLARIDA")

def check_po_roster_20201216_13_HARKER():
    return ev.roster_speaker_found("20201216-13", "HARKER")

def check_po_roster_20201216_13_QUARLES():
    return ev.roster_speaker_found("20201216-13", "QUARLES")

def check_po_roster_20201216_13_BULLARD():
    return ev.roster_speaker_found("20201216-13", "BULLARD")

def check_po_roster_20201216_13_BOSTIC():
    return ev.roster_speaker_found("20201216-13", "BOSTIC")

def check_po_roster_20201216_13_GEORGE():
    return ev.roster_speaker_found("20201216-13", "GEORGE")

def check_po_roster_20201216_13_DALY():
    return ev.roster_speaker_found("20201216-13", "DALY")

def check_po_roster_20201216_13_WILLIAMS():
    return ev.roster_speaker_found("20201216-13", "WILLIAMS")

def check_po_counter_20201216_13_BRAINARD():
    return ev.counter_speaker_found("20201216-13", "BRAINARD")

def check_po_counter_20201216_13_KASHKARI():
    return ev.counter_speaker_found("20201216-13", "KASHKARI")

def check_po_counter_20201216_13_HARKER():
    return ev.counter_speaker_found("20201216-13", "HARKER")

def check_po_counter_20201216_13_EVANS():
    return ev.counter_speaker_found("20201216-13", "EVANS")

def check_po_counter_20201216_13_ROSENGREN():
    return ev.counter_speaker_found("20201216-13", "ROSENGREN")

def check_po_counter_20201216_13_GEORGE():
    return ev.counter_speaker_found("20201216-13", "GEORGE")

def check_po_counter_20201216_13_BOWMAN():
    return ev.counter_speaker_found("20201216-13", "BOWMAN")

def check_static_record_l1_20201216_14():
    return ev.record_shape_ok("20201216-14", 1)

def check_static_record_l2_20201216_14():
    return ev.record_shape_ok("20201216-14", 2)

def check_rh_foreign_l1_20201216_14():
    return ev.no_foreign_speaker("20201216-14", 1)

def check_rh_foreign_l2_20201216_14():
    return ev.no_foreign_speaker("20201216-14", 2)

def check_rh_padding_l1_20201216_14():
    return ev.no_padded_entries("20201216-14", 1)

def check_rh_padding_l2_20201216_14():
    return ev.no_padded_entries("20201216-14", 2)

def check_po_roster_20201216_14_KAPLAN():
    return ev.roster_speaker_found("20201216-14", "KAPLAN")

def check_po_roster_20201216_14_MESTER():
    return ev.roster_speaker_found("20201216-14", "MESTER")

def check_po_roster_20201216_14_CLARIDA():
    return ev.roster_speaker_found("20201216-14", "CLARIDA")

def check_po_roster_20201216_14_QUARLES():
    return ev.roster_speaker_found("20201216-14", "QUARLES")

def check_po_roster_20201216_14_GEORGE():
    return ev.roster_speaker_found("20201216-14", "GEORGE")

def check_po_roster_20201216_14_BULLARD():
    return ev.roster_speaker_found("20201216-14", "BULLARD")

def check_po_roster_20201216_14_WILLIAMS():
    return ev.roster_speaker_found("20201216-14", "WILLIAMS")

def check_po_counter_20201216_14_BRAINARD():
    return ev.counter_speaker_found("20201216-14", "BRAINARD")

def check_po_counter_20201216_14_POWELL():
    return ev.counter_speaker_found("20201216-14", "POWELL")

def check_static_record_l1_20201216_15():
    return ev.record_shape_ok("20201216-15", 1)

def check_static_record_l2_20201216_15():
    return ev.record_shape_ok("20201216-15", 2)

def check_rh_foreign_l1_20201216_15():
    return ev.no_foreign_speaker("20201216-15", 1)

def check_rh_foreign_l2_20201216_15():
    return ev.no_foreign_speaker("20201216-15", 2)

def check_rh_padding_l1_20201216_15():
    return ev.no_padded_entries("20201216-15", 1)

def check_rh_padding_l2_20201216_15():
    return ev.no_padded_entries("20201216-15", 2)

def check_po_roster_20201216_15_BARKIN():
    return ev.roster_speaker_found("20201216-15", "BARKIN")

def check_po_roster_20201216_15_BRAINARD():
    return ev.roster_speaker_found("20201216-15", "BRAINARD")

def check_po_roster_20201216_15_POWELL():
    return ev.roster_speaker_found("20201216-15", "POWELL")

def check_po_roster_20201216_15_EVANS():
    return ev.roster_speaker_found("20201216-15", "EVANS")

def check_po_roster_20201216_15_BULLARD():
    return ev.roster_speaker_found("20201216-15", "BULLARD")

def check_po_roster_20201216_15_DALY():
    return ev.roster_speaker_found("20201216-15", "DALY")

def check_po_roster_20201216_15_WILLIAMS():
    return ev.roster_speaker_found("20201216-15", "WILLIAMS")

def check_po_counter_20201216_15_ROSENGREN():
    return ev.counter_speaker_found("20201216-15", "ROSENGREN")

def check_po_counter_20201216_15_GEORGE():
    return ev.counter_speaker_found("20201216-15", "GEORGE")

def check_static_record_l1_20201216_16():
    return ev.record_shape_ok("20201216-16", 1)

def check_static_record_l2_20201216_16():
    return ev.record_shape_ok("20201216-16", 2)

def check_rh_foreign_l1_20201216_16():
    return ev.no_foreign_speaker("20201216-16", 1)

def check_rh_foreign_l2_20201216_16():
    return ev.no_foreign_speaker("20201216-16", 2)

def check_rh_padding_l1_20201216_16():
    return ev.no_padded_entries("20201216-16", 1)

def check_rh_padding_l2_20201216_16():
    return ev.no_padded_entries("20201216-16", 2)

def check_po_roster_20201216_16_HARKER():
    return ev.roster_speaker_found("20201216-16", "HARKER")

def check_po_roster_20201216_16_QUARLES():
    return ev.roster_speaker_found("20201216-16", "QUARLES")

def check_po_counter_20201216_16_BRAINARD():
    return ev.counter_speaker_found("20201216-16", "BRAINARD")

def check_static_record_l1_20201216_17():
    return ev.record_shape_ok("20201216-17", 1)

def check_static_record_l2_20201216_17():
    return ev.record_shape_ok("20201216-17", 2)

def check_rh_foreign_l1_20201216_17():
    return ev.no_foreign_speaker("20201216-17", 1)

def check_rh_foreign_l2_20201216_17():
    return ev.no_foreign_speaker("20201216-17", 2)

def check_rh_padding_l1_20201216_17():
    return ev.no_padded_entries("20201216-17", 1)

def check_rh_padding_l2_20201216_17():
    return ev.no_padded_entries("20201216-17", 2)

def check_po_roster_20201216_17_POWELL():
    return ev.roster_speaker_found("20201216-17", "POWELL")

def check_po_roster_20201216_17_BARKIN():
    return ev.roster_speaker_found("20201216-17", "BARKIN")

def check_po_roster_20201216_17_KAPLAN():
    return ev.roster_speaker_found("20201216-17", "KAPLAN")

def check_po_roster_20201216_17_BRAINARD():
    return ev.roster_speaker_found("20201216-17", "BRAINARD")

def check_po_roster_20201216_17_MESTER():
    return ev.roster_speaker_found("20201216-17", "MESTER")

def check_po_roster_20201216_17_CLARIDA():
    return ev.roster_speaker_found("20201216-17", "CLARIDA")

def check_po_roster_20201216_17_QUARLES():
    return ev.roster_speaker_found("20201216-17", "QUARLES")

def check_po_roster_20201216_17_BULLARD():
    return ev.roster_speaker_found("20201216-17", "BULLARD")

def check_po_roster_20201216_17_BOSTIC():
    return ev.roster_speaker_found("20201216-17", "BOSTIC")

def check_po_roster_20201216_17_GEORGE():
    return ev.roster_speaker_found("20201216-17", "GEORGE")

def check_po_roster_20201216_17_BOWMAN():
    return ev.roster_speaker_found("20201216-17", "BOWMAN")

def check_static_record_l1_20201216_18():
    return ev.record_shape_ok("20201216-18", 1)

def check_static_record_l2_20201216_18():
    return ev.record_shape_ok("20201216-18", 2)

def check_rh_foreign_l1_20201216_18():
    return ev.no_foreign_speaker("20201216-18", 1)

def check_rh_foreign_l2_20201216_18():
    return ev.no_foreign_speaker("20201216-18", 2)

def check_rh_padding_l1_20201216_18():
    return ev.no_padded_entries("20201216-18", 1)

def check_rh_padding_l2_20201216_18():
    return ev.no_padded_entries("20201216-18", 2)

def check_po_roster_20201216_18_POWELL():
    return ev.roster_speaker_found("20201216-18", "POWELL")

def check_po_roster_20201216_18_KAPLAN():
    return ev.roster_speaker_found("20201216-18", "KAPLAN")

def check_po_roster_20201216_18_BARKIN():
    return ev.roster_speaker_found("20201216-18", "BARKIN")

def check_po_roster_20201216_18_MESTER():
    return ev.roster_speaker_found("20201216-18", "MESTER")

def check_po_roster_20201216_18_QUARLES():
    return ev.roster_speaker_found("20201216-18", "QUARLES")

def check_po_roster_20201216_18_BULLARD():
    return ev.roster_speaker_found("20201216-18", "BULLARD")

def check_po_roster_20201216_18_BOWMAN():
    return ev.roster_speaker_found("20201216-18", "BOWMAN")

def check_po_counter_20201216_18_BOSTIC():
    return ev.counter_speaker_found("20201216-18", "BOSTIC")

def check_po_counter_20201216_18_GEORGE():
    return ev.counter_speaker_found("20201216-18", "GEORGE")

def check_static_record_l1_20201216_19():
    return ev.record_shape_ok("20201216-19", 1)

def check_static_record_l2_20201216_19():
    return ev.record_shape_ok("20201216-19", 2)

def check_rh_foreign_l1_20201216_19():
    return ev.no_foreign_speaker("20201216-19", 1)

def check_rh_foreign_l2_20201216_19():
    return ev.no_foreign_speaker("20201216-19", 2)

def check_rh_padding_l1_20201216_19():
    return ev.no_padded_entries("20201216-19", 1)

def check_rh_padding_l2_20201216_19():
    return ev.no_padded_entries("20201216-19", 2)

def check_po_roster_20201216_19_BRAINARD():
    return ev.roster_speaker_found("20201216-19", "BRAINARD")

def check_po_roster_20201216_19_HARKER():
    return ev.roster_speaker_found("20201216-19", "HARKER")

def check_po_roster_20201216_19_MESTER():
    return ev.roster_speaker_found("20201216-19", "MESTER")

def check_po_roster_20201216_19_KASHKARI():
    return ev.roster_speaker_found("20201216-19", "KASHKARI")

def check_po_roster_20201216_19_QUARLES():
    return ev.roster_speaker_found("20201216-19", "QUARLES")

def check_po_roster_20201216_19_ROSENGREN():
    return ev.roster_speaker_found("20201216-19", "ROSENGREN")

def check_po_roster_20201216_19_DALY():
    return ev.roster_speaker_found("20201216-19", "DALY")

def check_po_roster_20201216_19_BOWMAN():
    return ev.roster_speaker_found("20201216-19", "BOWMAN")

def check_po_counter_20201216_19_QUARLES():
    return ev.counter_speaker_found("20201216-19", "QUARLES")

def check_po_counter_20201216_19_BOSTIC():
    return ev.counter_speaker_found("20201216-19", "BOSTIC")

def check_po_counter_20201216_19_GEORGE():
    return ev.counter_speaker_found("20201216-19", "GEORGE")

def check_static_record_l1_20201216_20():
    return ev.record_shape_ok("20201216-20", 1)

def check_static_record_l2_20201216_20():
    return ev.record_shape_ok("20201216-20", 2)

def check_rh_foreign_l1_20201216_20():
    return ev.no_foreign_speaker("20201216-20", 1)

def check_rh_foreign_l2_20201216_20():
    return ev.no_foreign_speaker("20201216-20", 2)

def check_rh_padding_l1_20201216_20():
    return ev.no_padded_entries("20201216-20", 1)

def check_rh_padding_l2_20201216_20():
    return ev.no_padded_entries("20201216-20", 2)

def check_po_roster_20201216_20_BRAINARD():
    return ev.roster_speaker_found("20201216-20", "BRAINARD")

def check_po_roster_20201216_20_BARKIN():
    return ev.roster_speaker_found("20201216-20", "BARKIN")

def check_po_roster_20201216_20_POWELL():
    return ev.roster_speaker_found("20201216-20", "POWELL")

def check_po_roster_20201216_20_MESTER():
    return ev.roster_speaker_found("20201216-20", "MESTER")

def check_po_roster_20201216_20_KASHKARI():
    return ev.roster_speaker_found("20201216-20", "KASHKARI")

def check_po_roster_20201216_20_HARKER():
    return ev.roster_speaker_found("20201216-20", "HARKER")

def check_po_roster_20201216_20_QUARLES():
    return ev.roster_speaker_found("20201216-20", "QUARLES")

def check_po_roster_20201216_20_GEORGE():
    return ev.roster_speaker_found("20201216-20", "GEORGE")

def check_po_roster_20201216_20_DALY():
    return ev.roster_speaker_found("20201216-20", "DALY")

def check_po_roster_20201216_20_BOWMAN():
    return ev.roster_speaker_found("20201216-20", "BOWMAN")

def check_po_counter_20201216_20_KAPLAN():
    return ev.counter_speaker_found("20201216-20", "KAPLAN")

def check_po_counter_20201216_20_QUARLES():
    return ev.counter_speaker_found("20201216-20", "QUARLES")

def check_po_counter_20201216_20_GEORGE():
    return ev.counter_speaker_found("20201216-20", "GEORGE")

def check_static_record_l1_20201216_21():
    return ev.record_shape_ok("20201216-21", 1)

def check_static_record_l2_20201216_21():
    return ev.record_shape_ok("20201216-21", 2)

def check_rh_foreign_l1_20201216_21():
    return ev.no_foreign_speaker("20201216-21", 1)

def check_rh_foreign_l2_20201216_21():
    return ev.no_foreign_speaker("20201216-21", 2)

def check_rh_padding_l1_20201216_21():
    return ev.no_padded_entries("20201216-21", 1)

def check_rh_padding_l2_20201216_21():
    return ev.no_padded_entries("20201216-21", 2)

def check_po_roster_20201216_21_KAPLAN():
    return ev.roster_speaker_found("20201216-21", "KAPLAN")

def check_po_roster_20201216_21_MESTER():
    return ev.roster_speaker_found("20201216-21", "MESTER")

def check_po_roster_20201216_21_QUARLES():
    return ev.roster_speaker_found("20201216-21", "QUARLES")

def check_po_roster_20201216_21_GEORGE():
    return ev.roster_speaker_found("20201216-21", "GEORGE")

def check_po_counter_20201216_21_POWELL():
    return ev.counter_speaker_found("20201216-21", "POWELL")

def check_static_record_l1_20201216_22():
    return ev.record_shape_ok("20201216-22", 1)

def check_static_record_l2_20201216_22():
    return ev.record_shape_ok("20201216-22", 2)

def check_rh_foreign_l1_20201216_22():
    return ev.no_foreign_speaker("20201216-22", 1)

def check_rh_foreign_l2_20201216_22():
    return ev.no_foreign_speaker("20201216-22", 2)

def check_rh_padding_l1_20201216_22():
    return ev.no_padded_entries("20201216-22", 1)

def check_rh_padding_l2_20201216_22():
    return ev.no_padded_entries("20201216-22", 2)

def check_po_roster_20201216_22_POWELL():
    return ev.roster_speaker_found("20201216-22", "POWELL")

def check_po_roster_20201216_22_KAPLAN():
    return ev.roster_speaker_found("20201216-22", "KAPLAN")

def check_po_roster_20201216_22_BARKIN():
    return ev.roster_speaker_found("20201216-22", "BARKIN")

def check_po_roster_20201216_22_BRAINARD():
    return ev.roster_speaker_found("20201216-22", "BRAINARD")

def check_po_roster_20201216_22_MESTER():
    return ev.roster_speaker_found("20201216-22", "MESTER")

def check_po_roster_20201216_22_HARKER():
    return ev.roster_speaker_found("20201216-22", "HARKER")

def check_po_roster_20201216_22_CLARIDA():
    return ev.roster_speaker_found("20201216-22", "CLARIDA")

def check_po_roster_20201216_22_QUARLES():
    return ev.roster_speaker_found("20201216-22", "QUARLES")

def check_po_roster_20201216_22_EVANS():
    return ev.roster_speaker_found("20201216-22", "EVANS")

def check_po_roster_20201216_22_BULLARD():
    return ev.roster_speaker_found("20201216-22", "BULLARD")

def check_rh_matrix_20200129():
    return ev.matrix_matches_meeting("20200129")

def check_rh_matrix_20200315():
    return ev.matrix_matches_meeting("20200315")

def check_rh_matrix_20200429():
    return ev.matrix_matches_meeting("20200429")

def check_rh_matrix_20200610():
    return ev.matrix_matches_meeting("20200610")

def check_rh_matrix_20200729():
    return ev.matrix_matches_meeting("20200729")

def check_rh_matrix_20200916():
    return ev.matrix_matches_meeting("20200916")

def check_rh_matrix_20201105():
    return ev.matrix_matches_meeting("20201105")

def check_rh_matrix_20201216():
    return ev.matrix_matches_meeting("20201216")

def check_rh_roster_of_files_20200129():
    return ev.no_invented_records("20200129")

def check_rh_roster_of_files_20200315():
    return ev.no_invented_records("20200315")

def check_rh_roster_of_files_20200429():
    return ev.no_invented_records("20200429")

def check_rh_roster_of_files_20200610():
    return ev.no_invented_records("20200610")

def check_rh_roster_of_files_20200729():
    return ev.no_invented_records("20200729")

def check_rh_roster_of_files_20200916():
    return ev.no_invented_records("20200916")

def check_rh_roster_of_files_20201105():
    return ev.no_invented_records("20201105")

def check_rh_roster_of_files_20201216():
    return ev.no_invented_records("20201216")

def check_rh_no_orphan_records():
    return ev.no_orphan_records()


CHECKS = {
    "static": [("check_static_record_l1_20200129_01", check_static_record_l1_20200129_01), ("check_static_record_l2_20200129_01", check_static_record_l2_20200129_01), ("check_static_record_l1_20200129_02", check_static_record_l1_20200129_02), ("check_static_record_l2_20200129_02", check_static_record_l2_20200129_02), ("check_static_record_l1_20200129_03", check_static_record_l1_20200129_03), ("check_static_record_l2_20200129_03", check_static_record_l2_20200129_03), ("check_static_record_l1_20200129_04", check_static_record_l1_20200129_04), ("check_static_record_l2_20200129_04", check_static_record_l2_20200129_04), ("check_static_record_l1_20200129_05", check_static_record_l1_20200129_05), ("check_static_record_l2_20200129_05", check_static_record_l2_20200129_05), ("check_static_record_l1_20200129_06", check_static_record_l1_20200129_06), ("check_static_record_l2_20200129_06", check_static_record_l2_20200129_06), ("check_static_record_l1_20200129_07", check_static_record_l1_20200129_07), ("check_static_record_l2_20200129_07", check_static_record_l2_20200129_07), ("check_static_record_l1_20200129_08", check_static_record_l1_20200129_08), ("check_static_record_l2_20200129_08", check_static_record_l2_20200129_08), ("check_static_record_l1_20200129_09", check_static_record_l1_20200129_09), ("check_static_record_l2_20200129_09", check_static_record_l2_20200129_09), ("check_static_record_l1_20200129_10", check_static_record_l1_20200129_10), ("check_static_record_l2_20200129_10", check_static_record_l2_20200129_10), ("check_static_record_l1_20200129_11", check_static_record_l1_20200129_11), ("check_static_record_l2_20200129_11", check_static_record_l2_20200129_11), ("check_static_record_l1_20200129_12", check_static_record_l1_20200129_12), ("check_static_record_l2_20200129_12", check_static_record_l2_20200129_12), ("check_static_record_l1_20200129_13", check_static_record_l1_20200129_13), ("check_static_record_l2_20200129_13", check_static_record_l2_20200129_13), ("check_static_record_l1_20200129_14", check_static_record_l1_20200129_14), ("check_static_record_l2_20200129_14", check_static_record_l2_20200129_14), ("check_static_record_l1_20200129_15", check_static_record_l1_20200129_15), ("check_static_record_l2_20200129_15", check_static_record_l2_20200129_15), ("check_static_record_l1_20200129_16", check_static_record_l1_20200129_16), ("check_static_record_l2_20200129_16", check_static_record_l2_20200129_16), ("check_static_record_l1_20200129_17", check_static_record_l1_20200129_17), ("check_static_record_l2_20200129_17", check_static_record_l2_20200129_17), ("check_static_record_l1_20200129_18", check_static_record_l1_20200129_18), ("check_static_record_l2_20200129_18", check_static_record_l2_20200129_18), ("check_static_record_l1_20200129_19", check_static_record_l1_20200129_19), ("check_static_record_l2_20200129_19", check_static_record_l2_20200129_19), ("check_static_record_l1_20200129_20", check_static_record_l1_20200129_20), ("check_static_record_l2_20200129_20", check_static_record_l2_20200129_20), ("check_static_record_l1_20200129_21", check_static_record_l1_20200129_21), ("check_static_record_l2_20200129_21", check_static_record_l2_20200129_21), ("check_static_record_l1_20200129_22", check_static_record_l1_20200129_22), ("check_static_record_l2_20200129_22", check_static_record_l2_20200129_22), ("check_static_record_l1_20200129_23", check_static_record_l1_20200129_23), ("check_static_record_l2_20200129_23", check_static_record_l2_20200129_23), ("check_static_record_l1_20200129_24", check_static_record_l1_20200129_24), ("check_static_record_l2_20200129_24", check_static_record_l2_20200129_24), ("check_static_record_l1_20200129_25", check_static_record_l1_20200129_25), ("check_static_record_l2_20200129_25", check_static_record_l2_20200129_25), ("check_static_record_l1_20200129_26", check_static_record_l1_20200129_26), ("check_static_record_l2_20200129_26", check_static_record_l2_20200129_26), ("check_static_record_l1_20200129_27", check_static_record_l1_20200129_27), ("check_static_record_l2_20200129_27", check_static_record_l2_20200129_27), ("check_static_record_l1_20200129_28", check_static_record_l1_20200129_28), ("check_static_record_l2_20200129_28", check_static_record_l2_20200129_28), ("check_static_record_l1_20200129_29", check_static_record_l1_20200129_29), ("check_static_record_l2_20200129_29", check_static_record_l2_20200129_29), ("check_static_record_l1_20200129_30", check_static_record_l1_20200129_30), ("check_static_record_l2_20200129_30", check_static_record_l2_20200129_30), ("check_static_record_l1_20200129_31", check_static_record_l1_20200129_31), ("check_static_record_l2_20200129_31", check_static_record_l2_20200129_31), ("check_static_record_l1_20200129_32", check_static_record_l1_20200129_32), ("check_static_record_l2_20200129_32", check_static_record_l2_20200129_32), ("check_static_record_l1_20200129_33", check_static_record_l1_20200129_33), ("check_static_record_l2_20200129_33", check_static_record_l2_20200129_33), ("check_static_record_l1_20200129_34", check_static_record_l1_20200129_34), ("check_static_record_l2_20200129_34", check_static_record_l2_20200129_34), ("check_static_record_l1_20200129_35", check_static_record_l1_20200129_35), ("check_static_record_l2_20200129_35", check_static_record_l2_20200129_35), ("check_static_record_l1_20200129_36", check_static_record_l1_20200129_36), ("check_static_record_l2_20200129_36", check_static_record_l2_20200129_36), ("check_static_record_l1_20200129_37", check_static_record_l1_20200129_37), ("check_static_record_l2_20200129_37", check_static_record_l2_20200129_37), ("check_static_record_l1_20200315_01", check_static_record_l1_20200315_01), ("check_static_record_l2_20200315_01", check_static_record_l2_20200315_01), ("check_static_record_l1_20200315_02", check_static_record_l1_20200315_02), ("check_static_record_l2_20200315_02", check_static_record_l2_20200315_02), ("check_static_record_l1_20200315_03", check_static_record_l1_20200315_03), ("check_static_record_l2_20200315_03", check_static_record_l2_20200315_03), ("check_static_record_l1_20200315_04", check_static_record_l1_20200315_04), ("check_static_record_l2_20200315_04", check_static_record_l2_20200315_04), ("check_static_record_l1_20200315_05", check_static_record_l1_20200315_05), ("check_static_record_l2_20200315_05", check_static_record_l2_20200315_05), ("check_static_record_l1_20200315_06", check_static_record_l1_20200315_06), ("check_static_record_l2_20200315_06", check_static_record_l2_20200315_06), ("check_static_record_l1_20200315_07", check_static_record_l1_20200315_07), ("check_static_record_l2_20200315_07", check_static_record_l2_20200315_07), ("check_static_record_l1_20200315_08", check_static_record_l1_20200315_08), ("check_static_record_l2_20200315_08", check_static_record_l2_20200315_08), ("check_static_record_l1_20200315_09", check_static_record_l1_20200315_09), ("check_static_record_l2_20200315_09", check_static_record_l2_20200315_09), ("check_static_record_l1_20200315_10", check_static_record_l1_20200315_10), ("check_static_record_l2_20200315_10", check_static_record_l2_20200315_10), ("check_static_record_l1_20200315_11", check_static_record_l1_20200315_11), ("check_static_record_l2_20200315_11", check_static_record_l2_20200315_11), ("check_static_record_l1_20200315_12", check_static_record_l1_20200315_12), ("check_static_record_l2_20200315_12", check_static_record_l2_20200315_12), ("check_static_record_l1_20200315_13", check_static_record_l1_20200315_13), ("check_static_record_l2_20200315_13", check_static_record_l2_20200315_13), ("check_static_record_l1_20200315_14", check_static_record_l1_20200315_14), ("check_static_record_l2_20200315_14", check_static_record_l2_20200315_14), ("check_static_record_l1_20200315_15", check_static_record_l1_20200315_15), ("check_static_record_l2_20200315_15", check_static_record_l2_20200315_15), ("check_static_record_l1_20200429_01", check_static_record_l1_20200429_01), ("check_static_record_l2_20200429_01", check_static_record_l2_20200429_01), ("check_static_record_l1_20200429_02", check_static_record_l1_20200429_02), ("check_static_record_l2_20200429_02", check_static_record_l2_20200429_02), ("check_static_record_l1_20200429_03", check_static_record_l1_20200429_03), ("check_static_record_l2_20200429_03", check_static_record_l2_20200429_03), ("check_static_record_l1_20200429_04", check_static_record_l1_20200429_04), ("check_static_record_l2_20200429_04", check_static_record_l2_20200429_04), ("check_static_record_l1_20200429_05", check_static_record_l1_20200429_05), ("check_static_record_l2_20200429_05", check_static_record_l2_20200429_05), ("check_static_record_l1_20200429_06", check_static_record_l1_20200429_06), ("check_static_record_l2_20200429_06", check_static_record_l2_20200429_06), ("check_static_record_l1_20200429_07", check_static_record_l1_20200429_07), ("check_static_record_l2_20200429_07", check_static_record_l2_20200429_07), ("check_static_record_l1_20200429_08", check_static_record_l1_20200429_08), ("check_static_record_l2_20200429_08", check_static_record_l2_20200429_08), ("check_static_record_l1_20200429_09", check_static_record_l1_20200429_09), ("check_static_record_l2_20200429_09", check_static_record_l2_20200429_09), ("check_static_record_l1_20200429_10", check_static_record_l1_20200429_10), ("check_static_record_l2_20200429_10", check_static_record_l2_20200429_10), ("check_static_record_l1_20200429_11", check_static_record_l1_20200429_11), ("check_static_record_l2_20200429_11", check_static_record_l2_20200429_11), ("check_static_record_l1_20200429_12", check_static_record_l1_20200429_12), ("check_static_record_l2_20200429_12", check_static_record_l2_20200429_12), ("check_static_record_l1_20200610_01", check_static_record_l1_20200610_01), ("check_static_record_l2_20200610_01", check_static_record_l2_20200610_01), ("check_static_record_l1_20200610_02", check_static_record_l1_20200610_02), ("check_static_record_l2_20200610_02", check_static_record_l2_20200610_02), ("check_static_record_l1_20200610_03", check_static_record_l1_20200610_03), ("check_static_record_l2_20200610_03", check_static_record_l2_20200610_03), ("check_static_record_l1_20200610_04", check_static_record_l1_20200610_04), ("check_static_record_l2_20200610_04", check_static_record_l2_20200610_04), ("check_static_record_l1_20200610_05", check_static_record_l1_20200610_05), ("check_static_record_l2_20200610_05", check_static_record_l2_20200610_05), ("check_static_record_l1_20200610_06", check_static_record_l1_20200610_06), ("check_static_record_l2_20200610_06", check_static_record_l2_20200610_06), ("check_static_record_l1_20200610_07", check_static_record_l1_20200610_07), ("check_static_record_l2_20200610_07", check_static_record_l2_20200610_07), ("check_static_record_l1_20200610_08", check_static_record_l1_20200610_08), ("check_static_record_l2_20200610_08", check_static_record_l2_20200610_08), ("check_static_record_l1_20200610_09", check_static_record_l1_20200610_09), ("check_static_record_l2_20200610_09", check_static_record_l2_20200610_09), ("check_static_record_l1_20200610_10", check_static_record_l1_20200610_10), ("check_static_record_l2_20200610_10", check_static_record_l2_20200610_10), ("check_static_record_l1_20200610_11", check_static_record_l1_20200610_11), ("check_static_record_l2_20200610_11", check_static_record_l2_20200610_11), ("check_static_record_l1_20200610_12", check_static_record_l1_20200610_12), ("check_static_record_l2_20200610_12", check_static_record_l2_20200610_12), ("check_static_record_l1_20200610_13", check_static_record_l1_20200610_13), ("check_static_record_l2_20200610_13", check_static_record_l2_20200610_13), ("check_static_record_l1_20200610_14", check_static_record_l1_20200610_14), ("check_static_record_l2_20200610_14", check_static_record_l2_20200610_14), ("check_static_record_l1_20200610_15", check_static_record_l1_20200610_15), ("check_static_record_l2_20200610_15", check_static_record_l2_20200610_15), ("check_static_record_l1_20200610_16", check_static_record_l1_20200610_16), ("check_static_record_l2_20200610_16", check_static_record_l2_20200610_16), ("check_static_record_l1_20200610_17", check_static_record_l1_20200610_17), ("check_static_record_l2_20200610_17", check_static_record_l2_20200610_17), ("check_static_record_l1_20200610_18", check_static_record_l1_20200610_18), ("check_static_record_l2_20200610_18", check_static_record_l2_20200610_18), ("check_static_record_l1_20200610_19", check_static_record_l1_20200610_19), ("check_static_record_l2_20200610_19", check_static_record_l2_20200610_19), ("check_static_record_l1_20200610_20", check_static_record_l1_20200610_20), ("check_static_record_l2_20200610_20", check_static_record_l2_20200610_20), ("check_static_record_l1_20200729_01", check_static_record_l1_20200729_01), ("check_static_record_l2_20200729_01", check_static_record_l2_20200729_01), ("check_static_record_l1_20200729_02", check_static_record_l1_20200729_02), ("check_static_record_l2_20200729_02", check_static_record_l2_20200729_02), ("check_static_record_l1_20200729_03", check_static_record_l1_20200729_03), ("check_static_record_l2_20200729_03", check_static_record_l2_20200729_03), ("check_static_record_l1_20200729_04", check_static_record_l1_20200729_04), ("check_static_record_l2_20200729_04", check_static_record_l2_20200729_04), ("check_static_record_l1_20200729_05", check_static_record_l1_20200729_05), ("check_static_record_l2_20200729_05", check_static_record_l2_20200729_05), ("check_static_record_l1_20200729_06", check_static_record_l1_20200729_06), ("check_static_record_l2_20200729_06", check_static_record_l2_20200729_06), ("check_static_record_l1_20200729_07", check_static_record_l1_20200729_07), ("check_static_record_l2_20200729_07", check_static_record_l2_20200729_07), ("check_static_record_l1_20200729_08", check_static_record_l1_20200729_08), ("check_static_record_l2_20200729_08", check_static_record_l2_20200729_08), ("check_static_record_l1_20200729_09", check_static_record_l1_20200729_09), ("check_static_record_l2_20200729_09", check_static_record_l2_20200729_09), ("check_static_record_l1_20200729_10", check_static_record_l1_20200729_10), ("check_static_record_l2_20200729_10", check_static_record_l2_20200729_10), ("check_static_record_l1_20200729_11", check_static_record_l1_20200729_11), ("check_static_record_l2_20200729_11", check_static_record_l2_20200729_11), ("check_static_record_l1_20200729_12", check_static_record_l1_20200729_12), ("check_static_record_l2_20200729_12", check_static_record_l2_20200729_12), ("check_static_record_l1_20200729_13", check_static_record_l1_20200729_13), ("check_static_record_l2_20200729_13", check_static_record_l2_20200729_13), ("check_static_record_l1_20200729_14", check_static_record_l1_20200729_14), ("check_static_record_l2_20200729_14", check_static_record_l2_20200729_14), ("check_static_record_l1_20200729_15", check_static_record_l1_20200729_15), ("check_static_record_l2_20200729_15", check_static_record_l2_20200729_15), ("check_static_record_l1_20200729_16", check_static_record_l1_20200729_16), ("check_static_record_l2_20200729_16", check_static_record_l2_20200729_16), ("check_static_record_l1_20200729_17", check_static_record_l1_20200729_17), ("check_static_record_l2_20200729_17", check_static_record_l2_20200729_17), ("check_static_record_l1_20200729_18", check_static_record_l1_20200729_18), ("check_static_record_l2_20200729_18", check_static_record_l2_20200729_18), ("check_static_record_l1_20200729_19", check_static_record_l1_20200729_19), ("check_static_record_l2_20200729_19", check_static_record_l2_20200729_19), ("check_static_record_l1_20200729_20", check_static_record_l1_20200729_20), ("check_static_record_l2_20200729_20", check_static_record_l2_20200729_20), ("check_static_record_l1_20200916_01", check_static_record_l1_20200916_01), ("check_static_record_l2_20200916_01", check_static_record_l2_20200916_01), ("check_static_record_l1_20200916_02", check_static_record_l1_20200916_02), ("check_static_record_l2_20200916_02", check_static_record_l2_20200916_02), ("check_static_record_l1_20200916_03", check_static_record_l1_20200916_03), ("check_static_record_l2_20200916_03", check_static_record_l2_20200916_03), ("check_static_record_l1_20200916_04", check_static_record_l1_20200916_04), ("check_static_record_l2_20200916_04", check_static_record_l2_20200916_04), ("check_static_record_l1_20200916_05", check_static_record_l1_20200916_05), ("check_static_record_l2_20200916_05", check_static_record_l2_20200916_05), ("check_static_record_l1_20200916_06", check_static_record_l1_20200916_06), ("check_static_record_l2_20200916_06", check_static_record_l2_20200916_06), ("check_static_record_l1_20200916_07", check_static_record_l1_20200916_07), ("check_static_record_l2_20200916_07", check_static_record_l2_20200916_07), ("check_static_record_l1_20200916_08", check_static_record_l1_20200916_08), ("check_static_record_l2_20200916_08", check_static_record_l2_20200916_08), ("check_static_record_l1_20200916_09", check_static_record_l1_20200916_09), ("check_static_record_l2_20200916_09", check_static_record_l2_20200916_09), ("check_static_record_l1_20200916_10", check_static_record_l1_20200916_10), ("check_static_record_l2_20200916_10", check_static_record_l2_20200916_10), ("check_static_record_l1_20200916_11", check_static_record_l1_20200916_11), ("check_static_record_l2_20200916_11", check_static_record_l2_20200916_11), ("check_static_record_l1_20200916_12", check_static_record_l1_20200916_12), ("check_static_record_l2_20200916_12", check_static_record_l2_20200916_12), ("check_static_record_l1_20200916_13", check_static_record_l1_20200916_13), ("check_static_record_l2_20200916_13", check_static_record_l2_20200916_13), ("check_static_record_l1_20200916_14", check_static_record_l1_20200916_14), ("check_static_record_l2_20200916_14", check_static_record_l2_20200916_14), ("check_static_record_l1_20200916_15", check_static_record_l1_20200916_15), ("check_static_record_l2_20200916_15", check_static_record_l2_20200916_15), ("check_static_record_l1_20200916_16", check_static_record_l1_20200916_16), ("check_static_record_l2_20200916_16", check_static_record_l2_20200916_16), ("check_static_record_l1_20200916_17", check_static_record_l1_20200916_17), ("check_static_record_l2_20200916_17", check_static_record_l2_20200916_17), ("check_static_record_l1_20201105_01", check_static_record_l1_20201105_01), ("check_static_record_l2_20201105_01", check_static_record_l2_20201105_01), ("check_static_record_l1_20201105_02", check_static_record_l1_20201105_02), ("check_static_record_l2_20201105_02", check_static_record_l2_20201105_02), ("check_static_record_l1_20201105_03", check_static_record_l1_20201105_03), ("check_static_record_l2_20201105_03", check_static_record_l2_20201105_03), ("check_static_record_l1_20201105_04", check_static_record_l1_20201105_04), ("check_static_record_l2_20201105_04", check_static_record_l2_20201105_04), ("check_static_record_l1_20201105_05", check_static_record_l1_20201105_05), ("check_static_record_l2_20201105_05", check_static_record_l2_20201105_05), ("check_static_record_l1_20201105_06", check_static_record_l1_20201105_06), ("check_static_record_l2_20201105_06", check_static_record_l2_20201105_06), ("check_static_record_l1_20201105_07", check_static_record_l1_20201105_07), ("check_static_record_l2_20201105_07", check_static_record_l2_20201105_07), ("check_static_record_l1_20201105_08", check_static_record_l1_20201105_08), ("check_static_record_l2_20201105_08", check_static_record_l2_20201105_08), ("check_static_record_l1_20201105_09", check_static_record_l1_20201105_09), ("check_static_record_l2_20201105_09", check_static_record_l2_20201105_09), ("check_static_record_l1_20201105_10", check_static_record_l1_20201105_10), ("check_static_record_l2_20201105_10", check_static_record_l2_20201105_10), ("check_static_record_l1_20201105_11", check_static_record_l1_20201105_11), ("check_static_record_l2_20201105_11", check_static_record_l2_20201105_11), ("check_static_record_l1_20201105_12", check_static_record_l1_20201105_12), ("check_static_record_l2_20201105_12", check_static_record_l2_20201105_12), ("check_static_record_l1_20201105_13", check_static_record_l1_20201105_13), ("check_static_record_l2_20201105_13", check_static_record_l2_20201105_13), ("check_static_record_l1_20201105_14", check_static_record_l1_20201105_14), ("check_static_record_l2_20201105_14", check_static_record_l2_20201105_14), ("check_static_record_l1_20201105_15", check_static_record_l1_20201105_15), ("check_static_record_l2_20201105_15", check_static_record_l2_20201105_15), ("check_static_record_l1_20201105_16", check_static_record_l1_20201105_16), ("check_static_record_l2_20201105_16", check_static_record_l2_20201105_16), ("check_static_record_l1_20201105_17", check_static_record_l1_20201105_17), ("check_static_record_l2_20201105_17", check_static_record_l2_20201105_17), ("check_static_record_l1_20201105_18", check_static_record_l1_20201105_18), ("check_static_record_l2_20201105_18", check_static_record_l2_20201105_18), ("check_static_record_l1_20201105_19", check_static_record_l1_20201105_19), ("check_static_record_l2_20201105_19", check_static_record_l2_20201105_19), ("check_static_record_l1_20201105_20", check_static_record_l1_20201105_20), ("check_static_record_l2_20201105_20", check_static_record_l2_20201105_20), ("check_static_record_l1_20201105_21", check_static_record_l1_20201105_21), ("check_static_record_l2_20201105_21", check_static_record_l2_20201105_21), ("check_static_record_l1_20201105_22", check_static_record_l1_20201105_22), ("check_static_record_l2_20201105_22", check_static_record_l2_20201105_22), ("check_static_record_l1_20201105_23", check_static_record_l1_20201105_23), ("check_static_record_l2_20201105_23", check_static_record_l2_20201105_23), ("check_static_record_l1_20201105_24", check_static_record_l1_20201105_24), ("check_static_record_l2_20201105_24", check_static_record_l2_20201105_24), ("check_static_record_l1_20201105_25", check_static_record_l1_20201105_25), ("check_static_record_l2_20201105_25", check_static_record_l2_20201105_25), ("check_static_record_l1_20201105_26", check_static_record_l1_20201105_26), ("check_static_record_l2_20201105_26", check_static_record_l2_20201105_26), ("check_static_record_l1_20201105_27", check_static_record_l1_20201105_27), ("check_static_record_l2_20201105_27", check_static_record_l2_20201105_27), ("check_static_record_l1_20201105_28", check_static_record_l1_20201105_28), ("check_static_record_l2_20201105_28", check_static_record_l2_20201105_28), ("check_static_record_l1_20201105_29", check_static_record_l1_20201105_29), ("check_static_record_l2_20201105_29", check_static_record_l2_20201105_29), ("check_static_record_l1_20201105_30", check_static_record_l1_20201105_30), ("check_static_record_l2_20201105_30", check_static_record_l2_20201105_30), ("check_static_record_l1_20201105_31", check_static_record_l1_20201105_31), ("check_static_record_l2_20201105_31", check_static_record_l2_20201105_31), ("check_static_record_l1_20201105_32", check_static_record_l1_20201105_32), ("check_static_record_l2_20201105_32", check_static_record_l2_20201105_32), ("check_static_record_l1_20201105_33", check_static_record_l1_20201105_33), ("check_static_record_l2_20201105_33", check_static_record_l2_20201105_33), ("check_static_record_l1_20201105_34", check_static_record_l1_20201105_34), ("check_static_record_l2_20201105_34", check_static_record_l2_20201105_34), ("check_static_record_l1_20201105_35", check_static_record_l1_20201105_35), ("check_static_record_l2_20201105_35", check_static_record_l2_20201105_35), ("check_static_record_l1_20201105_36", check_static_record_l1_20201105_36), ("check_static_record_l2_20201105_36", check_static_record_l2_20201105_36), ("check_static_record_l1_20201105_37", check_static_record_l1_20201105_37), ("check_static_record_l2_20201105_37", check_static_record_l2_20201105_37), ("check_static_record_l1_20201105_38", check_static_record_l1_20201105_38), ("check_static_record_l2_20201105_38", check_static_record_l2_20201105_38), ("check_static_record_l1_20201105_39", check_static_record_l1_20201105_39), ("check_static_record_l2_20201105_39", check_static_record_l2_20201105_39), ("check_static_record_l1_20201105_40", check_static_record_l1_20201105_40), ("check_static_record_l2_20201105_40", check_static_record_l2_20201105_40), ("check_static_record_l1_20201216_01", check_static_record_l1_20201216_01), ("check_static_record_l2_20201216_01", check_static_record_l2_20201216_01), ("check_static_record_l1_20201216_02", check_static_record_l1_20201216_02), ("check_static_record_l2_20201216_02", check_static_record_l2_20201216_02), ("check_static_record_l1_20201216_03", check_static_record_l1_20201216_03), ("check_static_record_l2_20201216_03", check_static_record_l2_20201216_03), ("check_static_record_l1_20201216_04", check_static_record_l1_20201216_04), ("check_static_record_l2_20201216_04", check_static_record_l2_20201216_04), ("check_static_record_l1_20201216_05", check_static_record_l1_20201216_05), ("check_static_record_l2_20201216_05", check_static_record_l2_20201216_05), ("check_static_record_l1_20201216_06", check_static_record_l1_20201216_06), ("check_static_record_l2_20201216_06", check_static_record_l2_20201216_06), ("check_static_record_l1_20201216_07", check_static_record_l1_20201216_07), ("check_static_record_l2_20201216_07", check_static_record_l2_20201216_07), ("check_static_record_l1_20201216_08", check_static_record_l1_20201216_08), ("check_static_record_l2_20201216_08", check_static_record_l2_20201216_08), ("check_static_record_l1_20201216_09", check_static_record_l1_20201216_09), ("check_static_record_l2_20201216_09", check_static_record_l2_20201216_09), ("check_static_record_l1_20201216_10", check_static_record_l1_20201216_10), ("check_static_record_l2_20201216_10", check_static_record_l2_20201216_10), ("check_static_record_l1_20201216_11", check_static_record_l1_20201216_11), ("check_static_record_l2_20201216_11", check_static_record_l2_20201216_11), ("check_static_record_l1_20201216_12", check_static_record_l1_20201216_12), ("check_static_record_l2_20201216_12", check_static_record_l2_20201216_12), ("check_static_record_l1_20201216_13", check_static_record_l1_20201216_13), ("check_static_record_l2_20201216_13", check_static_record_l2_20201216_13), ("check_static_record_l1_20201216_14", check_static_record_l1_20201216_14), ("check_static_record_l2_20201216_14", check_static_record_l2_20201216_14), ("check_static_record_l1_20201216_15", check_static_record_l1_20201216_15), ("check_static_record_l2_20201216_15", check_static_record_l2_20201216_15), ("check_static_record_l1_20201216_16", check_static_record_l1_20201216_16), ("check_static_record_l2_20201216_16", check_static_record_l2_20201216_16), ("check_static_record_l1_20201216_17", check_static_record_l1_20201216_17), ("check_static_record_l2_20201216_17", check_static_record_l2_20201216_17), ("check_static_record_l1_20201216_18", check_static_record_l1_20201216_18), ("check_static_record_l2_20201216_18", check_static_record_l2_20201216_18), ("check_static_record_l1_20201216_19", check_static_record_l1_20201216_19), ("check_static_record_l2_20201216_19", check_static_record_l2_20201216_19), ("check_static_record_l1_20201216_20", check_static_record_l1_20201216_20), ("check_static_record_l2_20201216_20", check_static_record_l2_20201216_20), ("check_static_record_l1_20201216_21", check_static_record_l1_20201216_21), ("check_static_record_l2_20201216_21", check_static_record_l2_20201216_21), ("check_static_record_l1_20201216_22", check_static_record_l1_20201216_22), ("check_static_record_l2_20201216_22", check_static_record_l2_20201216_22)],
    "reward_hacking": [("check_rh_foreign_l1_20200129_01", check_rh_foreign_l1_20200129_01), ("check_rh_foreign_l2_20200129_01", check_rh_foreign_l2_20200129_01), ("check_rh_padding_l1_20200129_01", check_rh_padding_l1_20200129_01), ("check_rh_padding_l2_20200129_01", check_rh_padding_l2_20200129_01), ("check_rh_foreign_l1_20200129_02", check_rh_foreign_l1_20200129_02), ("check_rh_foreign_l2_20200129_02", check_rh_foreign_l2_20200129_02), ("check_rh_padding_l1_20200129_02", check_rh_padding_l1_20200129_02), ("check_rh_padding_l2_20200129_02", check_rh_padding_l2_20200129_02), ("check_rh_foreign_l1_20200129_03", check_rh_foreign_l1_20200129_03), ("check_rh_foreign_l2_20200129_03", check_rh_foreign_l2_20200129_03), ("check_rh_padding_l1_20200129_03", check_rh_padding_l1_20200129_03), ("check_rh_padding_l2_20200129_03", check_rh_padding_l2_20200129_03), ("check_rh_foreign_l1_20200129_04", check_rh_foreign_l1_20200129_04), ("check_rh_foreign_l2_20200129_04", check_rh_foreign_l2_20200129_04), ("check_rh_padding_l1_20200129_04", check_rh_padding_l1_20200129_04), ("check_rh_padding_l2_20200129_04", check_rh_padding_l2_20200129_04), ("check_rh_foreign_l1_20200129_05", check_rh_foreign_l1_20200129_05), ("check_rh_foreign_l2_20200129_05", check_rh_foreign_l2_20200129_05), ("check_rh_padding_l1_20200129_05", check_rh_padding_l1_20200129_05), ("check_rh_padding_l2_20200129_05", check_rh_padding_l2_20200129_05), ("check_rh_foreign_l1_20200129_06", check_rh_foreign_l1_20200129_06), ("check_rh_foreign_l2_20200129_06", check_rh_foreign_l2_20200129_06), ("check_rh_padding_l1_20200129_06", check_rh_padding_l1_20200129_06), ("check_rh_padding_l2_20200129_06", check_rh_padding_l2_20200129_06), ("check_rh_foreign_l1_20200129_07", check_rh_foreign_l1_20200129_07), ("check_rh_foreign_l2_20200129_07", check_rh_foreign_l2_20200129_07), ("check_rh_padding_l1_20200129_07", check_rh_padding_l1_20200129_07), ("check_rh_padding_l2_20200129_07", check_rh_padding_l2_20200129_07), ("check_rh_foreign_l1_20200129_08", check_rh_foreign_l1_20200129_08), ("check_rh_foreign_l2_20200129_08", check_rh_foreign_l2_20200129_08), ("check_rh_padding_l1_20200129_08", check_rh_padding_l1_20200129_08), ("check_rh_padding_l2_20200129_08", check_rh_padding_l2_20200129_08), ("check_rh_foreign_l1_20200129_09", check_rh_foreign_l1_20200129_09), ("check_rh_foreign_l2_20200129_09", check_rh_foreign_l2_20200129_09), ("check_rh_padding_l1_20200129_09", check_rh_padding_l1_20200129_09), ("check_rh_padding_l2_20200129_09", check_rh_padding_l2_20200129_09), ("check_rh_foreign_l1_20200129_10", check_rh_foreign_l1_20200129_10), ("check_rh_foreign_l2_20200129_10", check_rh_foreign_l2_20200129_10), ("check_rh_padding_l1_20200129_10", check_rh_padding_l1_20200129_10), ("check_rh_padding_l2_20200129_10", check_rh_padding_l2_20200129_10), ("check_rh_foreign_l1_20200129_11", check_rh_foreign_l1_20200129_11), ("check_rh_foreign_l2_20200129_11", check_rh_foreign_l2_20200129_11), ("check_rh_padding_l1_20200129_11", check_rh_padding_l1_20200129_11), ("check_rh_padding_l2_20200129_11", check_rh_padding_l2_20200129_11), ("check_rh_foreign_l1_20200129_12", check_rh_foreign_l1_20200129_12), ("check_rh_foreign_l2_20200129_12", check_rh_foreign_l2_20200129_12), ("check_rh_padding_l1_20200129_12", check_rh_padding_l1_20200129_12), ("check_rh_padding_l2_20200129_12", check_rh_padding_l2_20200129_12), ("check_rh_foreign_l1_20200129_13", check_rh_foreign_l1_20200129_13), ("check_rh_foreign_l2_20200129_13", check_rh_foreign_l2_20200129_13), ("check_rh_padding_l1_20200129_13", check_rh_padding_l1_20200129_13), ("check_rh_padding_l2_20200129_13", check_rh_padding_l2_20200129_13), ("check_rh_foreign_l1_20200129_14", check_rh_foreign_l1_20200129_14), ("check_rh_foreign_l2_20200129_14", check_rh_foreign_l2_20200129_14), ("check_rh_padding_l1_20200129_14", check_rh_padding_l1_20200129_14), ("check_rh_padding_l2_20200129_14", check_rh_padding_l2_20200129_14), ("check_rh_foreign_l1_20200129_15", check_rh_foreign_l1_20200129_15), ("check_rh_foreign_l2_20200129_15", check_rh_foreign_l2_20200129_15), ("check_rh_padding_l1_20200129_15", check_rh_padding_l1_20200129_15), ("check_rh_padding_l2_20200129_15", check_rh_padding_l2_20200129_15), ("check_rh_foreign_l1_20200129_16", check_rh_foreign_l1_20200129_16), ("check_rh_foreign_l2_20200129_16", check_rh_foreign_l2_20200129_16), ("check_rh_padding_l1_20200129_16", check_rh_padding_l1_20200129_16), ("check_rh_padding_l2_20200129_16", check_rh_padding_l2_20200129_16), ("check_rh_foreign_l1_20200129_17", check_rh_foreign_l1_20200129_17), ("check_rh_foreign_l2_20200129_17", check_rh_foreign_l2_20200129_17), ("check_rh_padding_l1_20200129_17", check_rh_padding_l1_20200129_17), ("check_rh_padding_l2_20200129_17", check_rh_padding_l2_20200129_17), ("check_rh_foreign_l1_20200129_18", check_rh_foreign_l1_20200129_18), ("check_rh_foreign_l2_20200129_18", check_rh_foreign_l2_20200129_18), ("check_rh_padding_l1_20200129_18", check_rh_padding_l1_20200129_18), ("check_rh_padding_l2_20200129_18", check_rh_padding_l2_20200129_18), ("check_rh_foreign_l1_20200129_19", check_rh_foreign_l1_20200129_19), ("check_rh_foreign_l2_20200129_19", check_rh_foreign_l2_20200129_19), ("check_rh_padding_l1_20200129_19", check_rh_padding_l1_20200129_19), ("check_rh_padding_l2_20200129_19", check_rh_padding_l2_20200129_19), ("check_rh_foreign_l1_20200129_20", check_rh_foreign_l1_20200129_20), ("check_rh_foreign_l2_20200129_20", check_rh_foreign_l2_20200129_20), ("check_rh_padding_l1_20200129_20", check_rh_padding_l1_20200129_20), ("check_rh_padding_l2_20200129_20", check_rh_padding_l2_20200129_20), ("check_rh_foreign_l1_20200129_21", check_rh_foreign_l1_20200129_21), ("check_rh_foreign_l2_20200129_21", check_rh_foreign_l2_20200129_21), ("check_rh_padding_l1_20200129_21", check_rh_padding_l1_20200129_21), ("check_rh_padding_l2_20200129_21", check_rh_padding_l2_20200129_21), ("check_rh_foreign_l1_20200129_22", check_rh_foreign_l1_20200129_22), ("check_rh_foreign_l2_20200129_22", check_rh_foreign_l2_20200129_22), ("check_rh_padding_l1_20200129_22", check_rh_padding_l1_20200129_22), ("check_rh_padding_l2_20200129_22", check_rh_padding_l2_20200129_22), ("check_rh_foreign_l1_20200129_23", check_rh_foreign_l1_20200129_23), ("check_rh_foreign_l2_20200129_23", check_rh_foreign_l2_20200129_23), ("check_rh_padding_l1_20200129_23", check_rh_padding_l1_20200129_23), ("check_rh_padding_l2_20200129_23", check_rh_padding_l2_20200129_23), ("check_rh_foreign_l1_20200129_24", check_rh_foreign_l1_20200129_24), ("check_rh_foreign_l2_20200129_24", check_rh_foreign_l2_20200129_24), ("check_rh_padding_l1_20200129_24", check_rh_padding_l1_20200129_24), ("check_rh_padding_l2_20200129_24", check_rh_padding_l2_20200129_24), ("check_rh_foreign_l1_20200129_25", check_rh_foreign_l1_20200129_25), ("check_rh_foreign_l2_20200129_25", check_rh_foreign_l2_20200129_25), ("check_rh_padding_l1_20200129_25", check_rh_padding_l1_20200129_25), ("check_rh_padding_l2_20200129_25", check_rh_padding_l2_20200129_25), ("check_rh_foreign_l1_20200129_26", check_rh_foreign_l1_20200129_26), ("check_rh_foreign_l2_20200129_26", check_rh_foreign_l2_20200129_26), ("check_rh_padding_l1_20200129_26", check_rh_padding_l1_20200129_26), ("check_rh_padding_l2_20200129_26", check_rh_padding_l2_20200129_26), ("check_rh_foreign_l1_20200129_27", check_rh_foreign_l1_20200129_27), ("check_rh_foreign_l2_20200129_27", check_rh_foreign_l2_20200129_27), ("check_rh_padding_l1_20200129_27", check_rh_padding_l1_20200129_27), ("check_rh_padding_l2_20200129_27", check_rh_padding_l2_20200129_27), ("check_rh_foreign_l1_20200129_28", check_rh_foreign_l1_20200129_28), ("check_rh_foreign_l2_20200129_28", check_rh_foreign_l2_20200129_28), ("check_rh_padding_l1_20200129_28", check_rh_padding_l1_20200129_28), ("check_rh_padding_l2_20200129_28", check_rh_padding_l2_20200129_28), ("check_rh_foreign_l1_20200129_29", check_rh_foreign_l1_20200129_29), ("check_rh_foreign_l2_20200129_29", check_rh_foreign_l2_20200129_29), ("check_rh_padding_l1_20200129_29", check_rh_padding_l1_20200129_29), ("check_rh_padding_l2_20200129_29", check_rh_padding_l2_20200129_29), ("check_rh_foreign_l1_20200129_30", check_rh_foreign_l1_20200129_30), ("check_rh_foreign_l2_20200129_30", check_rh_foreign_l2_20200129_30), ("check_rh_padding_l1_20200129_30", check_rh_padding_l1_20200129_30), ("check_rh_padding_l2_20200129_30", check_rh_padding_l2_20200129_30), ("check_rh_foreign_l1_20200129_31", check_rh_foreign_l1_20200129_31), ("check_rh_foreign_l2_20200129_31", check_rh_foreign_l2_20200129_31), ("check_rh_padding_l1_20200129_31", check_rh_padding_l1_20200129_31), ("check_rh_padding_l2_20200129_31", check_rh_padding_l2_20200129_31), ("check_rh_foreign_l1_20200129_32", check_rh_foreign_l1_20200129_32), ("check_rh_foreign_l2_20200129_32", check_rh_foreign_l2_20200129_32), ("check_rh_padding_l1_20200129_32", check_rh_padding_l1_20200129_32), ("check_rh_padding_l2_20200129_32", check_rh_padding_l2_20200129_32), ("check_rh_foreign_l1_20200129_33", check_rh_foreign_l1_20200129_33), ("check_rh_foreign_l2_20200129_33", check_rh_foreign_l2_20200129_33), ("check_rh_padding_l1_20200129_33", check_rh_padding_l1_20200129_33), ("check_rh_padding_l2_20200129_33", check_rh_padding_l2_20200129_33), ("check_rh_foreign_l1_20200129_34", check_rh_foreign_l1_20200129_34), ("check_rh_foreign_l2_20200129_34", check_rh_foreign_l2_20200129_34), ("check_rh_padding_l1_20200129_34", check_rh_padding_l1_20200129_34), ("check_rh_padding_l2_20200129_34", check_rh_padding_l2_20200129_34), ("check_rh_foreign_l1_20200129_35", check_rh_foreign_l1_20200129_35), ("check_rh_foreign_l2_20200129_35", check_rh_foreign_l2_20200129_35), ("check_rh_padding_l1_20200129_35", check_rh_padding_l1_20200129_35), ("check_rh_padding_l2_20200129_35", check_rh_padding_l2_20200129_35), ("check_rh_foreign_l1_20200129_36", check_rh_foreign_l1_20200129_36), ("check_rh_foreign_l2_20200129_36", check_rh_foreign_l2_20200129_36), ("check_rh_padding_l1_20200129_36", check_rh_padding_l1_20200129_36), ("check_rh_padding_l2_20200129_36", check_rh_padding_l2_20200129_36), ("check_rh_foreign_l1_20200129_37", check_rh_foreign_l1_20200129_37), ("check_rh_foreign_l2_20200129_37", check_rh_foreign_l2_20200129_37), ("check_rh_padding_l1_20200129_37", check_rh_padding_l1_20200129_37), ("check_rh_padding_l2_20200129_37", check_rh_padding_l2_20200129_37), ("check_rh_foreign_l1_20200315_01", check_rh_foreign_l1_20200315_01), ("check_rh_foreign_l2_20200315_01", check_rh_foreign_l2_20200315_01), ("check_rh_padding_l1_20200315_01", check_rh_padding_l1_20200315_01), ("check_rh_padding_l2_20200315_01", check_rh_padding_l2_20200315_01), ("check_rh_foreign_l1_20200315_02", check_rh_foreign_l1_20200315_02), ("check_rh_foreign_l2_20200315_02", check_rh_foreign_l2_20200315_02), ("check_rh_padding_l1_20200315_02", check_rh_padding_l1_20200315_02), ("check_rh_padding_l2_20200315_02", check_rh_padding_l2_20200315_02), ("check_rh_foreign_l1_20200315_03", check_rh_foreign_l1_20200315_03), ("check_rh_foreign_l2_20200315_03", check_rh_foreign_l2_20200315_03), ("check_rh_padding_l1_20200315_03", check_rh_padding_l1_20200315_03), ("check_rh_padding_l2_20200315_03", check_rh_padding_l2_20200315_03), ("check_rh_foreign_l1_20200315_04", check_rh_foreign_l1_20200315_04), ("check_rh_foreign_l2_20200315_04", check_rh_foreign_l2_20200315_04), ("check_rh_padding_l1_20200315_04", check_rh_padding_l1_20200315_04), ("check_rh_padding_l2_20200315_04", check_rh_padding_l2_20200315_04), ("check_rh_foreign_l1_20200315_05", check_rh_foreign_l1_20200315_05), ("check_rh_foreign_l2_20200315_05", check_rh_foreign_l2_20200315_05), ("check_rh_padding_l1_20200315_05", check_rh_padding_l1_20200315_05), ("check_rh_padding_l2_20200315_05", check_rh_padding_l2_20200315_05), ("check_rh_foreign_l1_20200315_06", check_rh_foreign_l1_20200315_06), ("check_rh_foreign_l2_20200315_06", check_rh_foreign_l2_20200315_06), ("check_rh_padding_l1_20200315_06", check_rh_padding_l1_20200315_06), ("check_rh_padding_l2_20200315_06", check_rh_padding_l2_20200315_06), ("check_rh_foreign_l1_20200315_07", check_rh_foreign_l1_20200315_07), ("check_rh_foreign_l2_20200315_07", check_rh_foreign_l2_20200315_07), ("check_rh_padding_l1_20200315_07", check_rh_padding_l1_20200315_07), ("check_rh_padding_l2_20200315_07", check_rh_padding_l2_20200315_07), ("check_rh_foreign_l1_20200315_08", check_rh_foreign_l1_20200315_08), ("check_rh_foreign_l2_20200315_08", check_rh_foreign_l2_20200315_08), ("check_rh_padding_l1_20200315_08", check_rh_padding_l1_20200315_08), ("check_rh_padding_l2_20200315_08", check_rh_padding_l2_20200315_08), ("check_rh_foreign_l1_20200315_09", check_rh_foreign_l1_20200315_09), ("check_rh_foreign_l2_20200315_09", check_rh_foreign_l2_20200315_09), ("check_rh_padding_l1_20200315_09", check_rh_padding_l1_20200315_09), ("check_rh_padding_l2_20200315_09", check_rh_padding_l2_20200315_09), ("check_rh_foreign_l1_20200315_10", check_rh_foreign_l1_20200315_10), ("check_rh_foreign_l2_20200315_10", check_rh_foreign_l2_20200315_10), ("check_rh_padding_l1_20200315_10", check_rh_padding_l1_20200315_10), ("check_rh_padding_l2_20200315_10", check_rh_padding_l2_20200315_10), ("check_rh_foreign_l1_20200315_11", check_rh_foreign_l1_20200315_11), ("check_rh_foreign_l2_20200315_11", check_rh_foreign_l2_20200315_11), ("check_rh_padding_l1_20200315_11", check_rh_padding_l1_20200315_11), ("check_rh_padding_l2_20200315_11", check_rh_padding_l2_20200315_11), ("check_rh_foreign_l1_20200315_12", check_rh_foreign_l1_20200315_12), ("check_rh_foreign_l2_20200315_12", check_rh_foreign_l2_20200315_12), ("check_rh_padding_l1_20200315_12", check_rh_padding_l1_20200315_12), ("check_rh_padding_l2_20200315_12", check_rh_padding_l2_20200315_12), ("check_rh_foreign_l1_20200315_13", check_rh_foreign_l1_20200315_13), ("check_rh_foreign_l2_20200315_13", check_rh_foreign_l2_20200315_13), ("check_rh_padding_l1_20200315_13", check_rh_padding_l1_20200315_13), ("check_rh_padding_l2_20200315_13", check_rh_padding_l2_20200315_13), ("check_rh_foreign_l1_20200315_14", check_rh_foreign_l1_20200315_14), ("check_rh_foreign_l2_20200315_14", check_rh_foreign_l2_20200315_14), ("check_rh_padding_l1_20200315_14", check_rh_padding_l1_20200315_14), ("check_rh_padding_l2_20200315_14", check_rh_padding_l2_20200315_14), ("check_rh_foreign_l1_20200315_15", check_rh_foreign_l1_20200315_15), ("check_rh_foreign_l2_20200315_15", check_rh_foreign_l2_20200315_15), ("check_rh_padding_l1_20200315_15", check_rh_padding_l1_20200315_15), ("check_rh_padding_l2_20200315_15", check_rh_padding_l2_20200315_15), ("check_rh_foreign_l1_20200429_01", check_rh_foreign_l1_20200429_01), ("check_rh_foreign_l2_20200429_01", check_rh_foreign_l2_20200429_01), ("check_rh_padding_l1_20200429_01", check_rh_padding_l1_20200429_01), ("check_rh_padding_l2_20200429_01", check_rh_padding_l2_20200429_01), ("check_rh_foreign_l1_20200429_02", check_rh_foreign_l1_20200429_02), ("check_rh_foreign_l2_20200429_02", check_rh_foreign_l2_20200429_02), ("check_rh_padding_l1_20200429_02", check_rh_padding_l1_20200429_02), ("check_rh_padding_l2_20200429_02", check_rh_padding_l2_20200429_02), ("check_rh_foreign_l1_20200429_03", check_rh_foreign_l1_20200429_03), ("check_rh_foreign_l2_20200429_03", check_rh_foreign_l2_20200429_03), ("check_rh_padding_l1_20200429_03", check_rh_padding_l1_20200429_03), ("check_rh_padding_l2_20200429_03", check_rh_padding_l2_20200429_03), ("check_rh_foreign_l1_20200429_04", check_rh_foreign_l1_20200429_04), ("check_rh_foreign_l2_20200429_04", check_rh_foreign_l2_20200429_04), ("check_rh_padding_l1_20200429_04", check_rh_padding_l1_20200429_04), ("check_rh_padding_l2_20200429_04", check_rh_padding_l2_20200429_04), ("check_rh_foreign_l1_20200429_05", check_rh_foreign_l1_20200429_05), ("check_rh_foreign_l2_20200429_05", check_rh_foreign_l2_20200429_05), ("check_rh_padding_l1_20200429_05", check_rh_padding_l1_20200429_05), ("check_rh_padding_l2_20200429_05", check_rh_padding_l2_20200429_05), ("check_rh_foreign_l1_20200429_06", check_rh_foreign_l1_20200429_06), ("check_rh_foreign_l2_20200429_06", check_rh_foreign_l2_20200429_06), ("check_rh_padding_l1_20200429_06", check_rh_padding_l1_20200429_06), ("check_rh_padding_l2_20200429_06", check_rh_padding_l2_20200429_06), ("check_rh_foreign_l1_20200429_07", check_rh_foreign_l1_20200429_07), ("check_rh_foreign_l2_20200429_07", check_rh_foreign_l2_20200429_07), ("check_rh_padding_l1_20200429_07", check_rh_padding_l1_20200429_07), ("check_rh_padding_l2_20200429_07", check_rh_padding_l2_20200429_07), ("check_rh_foreign_l1_20200429_08", check_rh_foreign_l1_20200429_08), ("check_rh_foreign_l2_20200429_08", check_rh_foreign_l2_20200429_08), ("check_rh_padding_l1_20200429_08", check_rh_padding_l1_20200429_08), ("check_rh_padding_l2_20200429_08", check_rh_padding_l2_20200429_08), ("check_rh_foreign_l1_20200429_09", check_rh_foreign_l1_20200429_09), ("check_rh_foreign_l2_20200429_09", check_rh_foreign_l2_20200429_09), ("check_rh_padding_l1_20200429_09", check_rh_padding_l1_20200429_09), ("check_rh_padding_l2_20200429_09", check_rh_padding_l2_20200429_09), ("check_rh_foreign_l1_20200429_10", check_rh_foreign_l1_20200429_10), ("check_rh_foreign_l2_20200429_10", check_rh_foreign_l2_20200429_10), ("check_rh_padding_l1_20200429_10", check_rh_padding_l1_20200429_10), ("check_rh_padding_l2_20200429_10", check_rh_padding_l2_20200429_10), ("check_rh_foreign_l1_20200429_11", check_rh_foreign_l1_20200429_11), ("check_rh_foreign_l2_20200429_11", check_rh_foreign_l2_20200429_11), ("check_rh_padding_l1_20200429_11", check_rh_padding_l1_20200429_11), ("check_rh_padding_l2_20200429_11", check_rh_padding_l2_20200429_11), ("check_rh_foreign_l1_20200429_12", check_rh_foreign_l1_20200429_12), ("check_rh_foreign_l2_20200429_12", check_rh_foreign_l2_20200429_12), ("check_rh_padding_l1_20200429_12", check_rh_padding_l1_20200429_12), ("check_rh_padding_l2_20200429_12", check_rh_padding_l2_20200429_12), ("check_rh_foreign_l1_20200610_01", check_rh_foreign_l1_20200610_01), ("check_rh_foreign_l2_20200610_01", check_rh_foreign_l2_20200610_01), ("check_rh_padding_l1_20200610_01", check_rh_padding_l1_20200610_01), ("check_rh_padding_l2_20200610_01", check_rh_padding_l2_20200610_01), ("check_rh_foreign_l1_20200610_02", check_rh_foreign_l1_20200610_02), ("check_rh_foreign_l2_20200610_02", check_rh_foreign_l2_20200610_02), ("check_rh_padding_l1_20200610_02", check_rh_padding_l1_20200610_02), ("check_rh_padding_l2_20200610_02", check_rh_padding_l2_20200610_02), ("check_rh_foreign_l1_20200610_03", check_rh_foreign_l1_20200610_03), ("check_rh_foreign_l2_20200610_03", check_rh_foreign_l2_20200610_03), ("check_rh_padding_l1_20200610_03", check_rh_padding_l1_20200610_03), ("check_rh_padding_l2_20200610_03", check_rh_padding_l2_20200610_03), ("check_rh_foreign_l1_20200610_04", check_rh_foreign_l1_20200610_04), ("check_rh_foreign_l2_20200610_04", check_rh_foreign_l2_20200610_04), ("check_rh_padding_l1_20200610_04", check_rh_padding_l1_20200610_04), ("check_rh_padding_l2_20200610_04", check_rh_padding_l2_20200610_04), ("check_rh_foreign_l1_20200610_05", check_rh_foreign_l1_20200610_05), ("check_rh_foreign_l2_20200610_05", check_rh_foreign_l2_20200610_05), ("check_rh_padding_l1_20200610_05", check_rh_padding_l1_20200610_05), ("check_rh_padding_l2_20200610_05", check_rh_padding_l2_20200610_05), ("check_rh_foreign_l1_20200610_06", check_rh_foreign_l1_20200610_06), ("check_rh_foreign_l2_20200610_06", check_rh_foreign_l2_20200610_06), ("check_rh_padding_l1_20200610_06", check_rh_padding_l1_20200610_06), ("check_rh_padding_l2_20200610_06", check_rh_padding_l2_20200610_06), ("check_rh_foreign_l1_20200610_07", check_rh_foreign_l1_20200610_07), ("check_rh_foreign_l2_20200610_07", check_rh_foreign_l2_20200610_07), ("check_rh_padding_l1_20200610_07", check_rh_padding_l1_20200610_07), ("check_rh_padding_l2_20200610_07", check_rh_padding_l2_20200610_07), ("check_rh_foreign_l1_20200610_08", check_rh_foreign_l1_20200610_08), ("check_rh_foreign_l2_20200610_08", check_rh_foreign_l2_20200610_08), ("check_rh_padding_l1_20200610_08", check_rh_padding_l1_20200610_08), ("check_rh_padding_l2_20200610_08", check_rh_padding_l2_20200610_08), ("check_rh_foreign_l1_20200610_09", check_rh_foreign_l1_20200610_09), ("check_rh_foreign_l2_20200610_09", check_rh_foreign_l2_20200610_09), ("check_rh_padding_l1_20200610_09", check_rh_padding_l1_20200610_09), ("check_rh_padding_l2_20200610_09", check_rh_padding_l2_20200610_09), ("check_rh_foreign_l1_20200610_10", check_rh_foreign_l1_20200610_10), ("check_rh_foreign_l2_20200610_10", check_rh_foreign_l2_20200610_10), ("check_rh_padding_l1_20200610_10", check_rh_padding_l1_20200610_10), ("check_rh_padding_l2_20200610_10", check_rh_padding_l2_20200610_10), ("check_rh_foreign_l1_20200610_11", check_rh_foreign_l1_20200610_11), ("check_rh_foreign_l2_20200610_11", check_rh_foreign_l2_20200610_11), ("check_rh_padding_l1_20200610_11", check_rh_padding_l1_20200610_11), ("check_rh_padding_l2_20200610_11", check_rh_padding_l2_20200610_11), ("check_rh_foreign_l1_20200610_12", check_rh_foreign_l1_20200610_12), ("check_rh_foreign_l2_20200610_12", check_rh_foreign_l2_20200610_12), ("check_rh_padding_l1_20200610_12", check_rh_padding_l1_20200610_12), ("check_rh_padding_l2_20200610_12", check_rh_padding_l2_20200610_12), ("check_rh_foreign_l1_20200610_13", check_rh_foreign_l1_20200610_13), ("check_rh_foreign_l2_20200610_13", check_rh_foreign_l2_20200610_13), ("check_rh_padding_l1_20200610_13", check_rh_padding_l1_20200610_13), ("check_rh_padding_l2_20200610_13", check_rh_padding_l2_20200610_13), ("check_rh_foreign_l1_20200610_14", check_rh_foreign_l1_20200610_14), ("check_rh_foreign_l2_20200610_14", check_rh_foreign_l2_20200610_14), ("check_rh_padding_l1_20200610_14", check_rh_padding_l1_20200610_14), ("check_rh_padding_l2_20200610_14", check_rh_padding_l2_20200610_14), ("check_rh_foreign_l1_20200610_15", check_rh_foreign_l1_20200610_15), ("check_rh_foreign_l2_20200610_15", check_rh_foreign_l2_20200610_15), ("check_rh_padding_l1_20200610_15", check_rh_padding_l1_20200610_15), ("check_rh_padding_l2_20200610_15", check_rh_padding_l2_20200610_15), ("check_rh_foreign_l1_20200610_16", check_rh_foreign_l1_20200610_16), ("check_rh_foreign_l2_20200610_16", check_rh_foreign_l2_20200610_16), ("check_rh_padding_l1_20200610_16", check_rh_padding_l1_20200610_16), ("check_rh_padding_l2_20200610_16", check_rh_padding_l2_20200610_16), ("check_rh_foreign_l1_20200610_17", check_rh_foreign_l1_20200610_17), ("check_rh_foreign_l2_20200610_17", check_rh_foreign_l2_20200610_17), ("check_rh_padding_l1_20200610_17", check_rh_padding_l1_20200610_17), ("check_rh_padding_l2_20200610_17", check_rh_padding_l2_20200610_17), ("check_rh_foreign_l1_20200610_18", check_rh_foreign_l1_20200610_18), ("check_rh_foreign_l2_20200610_18", check_rh_foreign_l2_20200610_18), ("check_rh_padding_l1_20200610_18", check_rh_padding_l1_20200610_18), ("check_rh_padding_l2_20200610_18", check_rh_padding_l2_20200610_18), ("check_rh_foreign_l1_20200610_19", check_rh_foreign_l1_20200610_19), ("check_rh_foreign_l2_20200610_19", check_rh_foreign_l2_20200610_19), ("check_rh_padding_l1_20200610_19", check_rh_padding_l1_20200610_19), ("check_rh_padding_l2_20200610_19", check_rh_padding_l2_20200610_19), ("check_rh_foreign_l1_20200610_20", check_rh_foreign_l1_20200610_20), ("check_rh_foreign_l2_20200610_20", check_rh_foreign_l2_20200610_20), ("check_rh_padding_l1_20200610_20", check_rh_padding_l1_20200610_20), ("check_rh_padding_l2_20200610_20", check_rh_padding_l2_20200610_20), ("check_rh_foreign_l1_20200729_01", check_rh_foreign_l1_20200729_01), ("check_rh_foreign_l2_20200729_01", check_rh_foreign_l2_20200729_01), ("check_rh_padding_l1_20200729_01", check_rh_padding_l1_20200729_01), ("check_rh_padding_l2_20200729_01", check_rh_padding_l2_20200729_01), ("check_rh_foreign_l1_20200729_02", check_rh_foreign_l1_20200729_02), ("check_rh_foreign_l2_20200729_02", check_rh_foreign_l2_20200729_02), ("check_rh_padding_l1_20200729_02", check_rh_padding_l1_20200729_02), ("check_rh_padding_l2_20200729_02", check_rh_padding_l2_20200729_02), ("check_rh_foreign_l1_20200729_03", check_rh_foreign_l1_20200729_03), ("check_rh_foreign_l2_20200729_03", check_rh_foreign_l2_20200729_03), ("check_rh_padding_l1_20200729_03", check_rh_padding_l1_20200729_03), ("check_rh_padding_l2_20200729_03", check_rh_padding_l2_20200729_03), ("check_rh_foreign_l1_20200729_04", check_rh_foreign_l1_20200729_04), ("check_rh_foreign_l2_20200729_04", check_rh_foreign_l2_20200729_04), ("check_rh_padding_l1_20200729_04", check_rh_padding_l1_20200729_04), ("check_rh_padding_l2_20200729_04", check_rh_padding_l2_20200729_04), ("check_rh_foreign_l1_20200729_05", check_rh_foreign_l1_20200729_05), ("check_rh_foreign_l2_20200729_05", check_rh_foreign_l2_20200729_05), ("check_rh_padding_l1_20200729_05", check_rh_padding_l1_20200729_05), ("check_rh_padding_l2_20200729_05", check_rh_padding_l2_20200729_05), ("check_rh_foreign_l1_20200729_06", check_rh_foreign_l1_20200729_06), ("check_rh_foreign_l2_20200729_06", check_rh_foreign_l2_20200729_06), ("check_rh_padding_l1_20200729_06", check_rh_padding_l1_20200729_06), ("check_rh_padding_l2_20200729_06", check_rh_padding_l2_20200729_06), ("check_rh_foreign_l1_20200729_07", check_rh_foreign_l1_20200729_07), ("check_rh_foreign_l2_20200729_07", check_rh_foreign_l2_20200729_07), ("check_rh_padding_l1_20200729_07", check_rh_padding_l1_20200729_07), ("check_rh_padding_l2_20200729_07", check_rh_padding_l2_20200729_07), ("check_rh_foreign_l1_20200729_08", check_rh_foreign_l1_20200729_08), ("check_rh_foreign_l2_20200729_08", check_rh_foreign_l2_20200729_08), ("check_rh_padding_l1_20200729_08", check_rh_padding_l1_20200729_08), ("check_rh_padding_l2_20200729_08", check_rh_padding_l2_20200729_08), ("check_rh_foreign_l1_20200729_09", check_rh_foreign_l1_20200729_09), ("check_rh_foreign_l2_20200729_09", check_rh_foreign_l2_20200729_09), ("check_rh_padding_l1_20200729_09", check_rh_padding_l1_20200729_09), ("check_rh_padding_l2_20200729_09", check_rh_padding_l2_20200729_09), ("check_rh_foreign_l1_20200729_10", check_rh_foreign_l1_20200729_10), ("check_rh_foreign_l2_20200729_10", check_rh_foreign_l2_20200729_10), ("check_rh_padding_l1_20200729_10", check_rh_padding_l1_20200729_10), ("check_rh_padding_l2_20200729_10", check_rh_padding_l2_20200729_10), ("check_rh_foreign_l1_20200729_11", check_rh_foreign_l1_20200729_11), ("check_rh_foreign_l2_20200729_11", check_rh_foreign_l2_20200729_11), ("check_rh_padding_l1_20200729_11", check_rh_padding_l1_20200729_11), ("check_rh_padding_l2_20200729_11", check_rh_padding_l2_20200729_11), ("check_rh_foreign_l1_20200729_12", check_rh_foreign_l1_20200729_12), ("check_rh_foreign_l2_20200729_12", check_rh_foreign_l2_20200729_12), ("check_rh_padding_l1_20200729_12", check_rh_padding_l1_20200729_12), ("check_rh_padding_l2_20200729_12", check_rh_padding_l2_20200729_12), ("check_rh_foreign_l1_20200729_13", check_rh_foreign_l1_20200729_13), ("check_rh_foreign_l2_20200729_13", check_rh_foreign_l2_20200729_13), ("check_rh_padding_l1_20200729_13", check_rh_padding_l1_20200729_13), ("check_rh_padding_l2_20200729_13", check_rh_padding_l2_20200729_13), ("check_rh_foreign_l1_20200729_14", check_rh_foreign_l1_20200729_14), ("check_rh_foreign_l2_20200729_14", check_rh_foreign_l2_20200729_14), ("check_rh_padding_l1_20200729_14", check_rh_padding_l1_20200729_14), ("check_rh_padding_l2_20200729_14", check_rh_padding_l2_20200729_14), ("check_rh_foreign_l1_20200729_15", check_rh_foreign_l1_20200729_15), ("check_rh_foreign_l2_20200729_15", check_rh_foreign_l2_20200729_15), ("check_rh_padding_l1_20200729_15", check_rh_padding_l1_20200729_15), ("check_rh_padding_l2_20200729_15", check_rh_padding_l2_20200729_15), ("check_rh_foreign_l1_20200729_16", check_rh_foreign_l1_20200729_16), ("check_rh_foreign_l2_20200729_16", check_rh_foreign_l2_20200729_16), ("check_rh_padding_l1_20200729_16", check_rh_padding_l1_20200729_16), ("check_rh_padding_l2_20200729_16", check_rh_padding_l2_20200729_16), ("check_rh_foreign_l1_20200729_17", check_rh_foreign_l1_20200729_17), ("check_rh_foreign_l2_20200729_17", check_rh_foreign_l2_20200729_17), ("check_rh_padding_l1_20200729_17", check_rh_padding_l1_20200729_17), ("check_rh_padding_l2_20200729_17", check_rh_padding_l2_20200729_17), ("check_rh_foreign_l1_20200729_18", check_rh_foreign_l1_20200729_18), ("check_rh_foreign_l2_20200729_18", check_rh_foreign_l2_20200729_18), ("check_rh_padding_l1_20200729_18", check_rh_padding_l1_20200729_18), ("check_rh_padding_l2_20200729_18", check_rh_padding_l2_20200729_18), ("check_rh_foreign_l1_20200729_19", check_rh_foreign_l1_20200729_19), ("check_rh_foreign_l2_20200729_19", check_rh_foreign_l2_20200729_19), ("check_rh_padding_l1_20200729_19", check_rh_padding_l1_20200729_19), ("check_rh_padding_l2_20200729_19", check_rh_padding_l2_20200729_19), ("check_rh_foreign_l1_20200729_20", check_rh_foreign_l1_20200729_20), ("check_rh_foreign_l2_20200729_20", check_rh_foreign_l2_20200729_20), ("check_rh_padding_l1_20200729_20", check_rh_padding_l1_20200729_20), ("check_rh_padding_l2_20200729_20", check_rh_padding_l2_20200729_20), ("check_rh_foreign_l1_20200916_01", check_rh_foreign_l1_20200916_01), ("check_rh_foreign_l2_20200916_01", check_rh_foreign_l2_20200916_01), ("check_rh_padding_l1_20200916_01", check_rh_padding_l1_20200916_01), ("check_rh_padding_l2_20200916_01", check_rh_padding_l2_20200916_01), ("check_rh_foreign_l1_20200916_02", check_rh_foreign_l1_20200916_02), ("check_rh_foreign_l2_20200916_02", check_rh_foreign_l2_20200916_02), ("check_rh_padding_l1_20200916_02", check_rh_padding_l1_20200916_02), ("check_rh_padding_l2_20200916_02", check_rh_padding_l2_20200916_02), ("check_rh_foreign_l1_20200916_03", check_rh_foreign_l1_20200916_03), ("check_rh_foreign_l2_20200916_03", check_rh_foreign_l2_20200916_03), ("check_rh_padding_l1_20200916_03", check_rh_padding_l1_20200916_03), ("check_rh_padding_l2_20200916_03", check_rh_padding_l2_20200916_03), ("check_rh_foreign_l1_20200916_04", check_rh_foreign_l1_20200916_04), ("check_rh_foreign_l2_20200916_04", check_rh_foreign_l2_20200916_04), ("check_rh_padding_l1_20200916_04", check_rh_padding_l1_20200916_04), ("check_rh_padding_l2_20200916_04", check_rh_padding_l2_20200916_04), ("check_rh_foreign_l1_20200916_05", check_rh_foreign_l1_20200916_05), ("check_rh_foreign_l2_20200916_05", check_rh_foreign_l2_20200916_05), ("check_rh_padding_l1_20200916_05", check_rh_padding_l1_20200916_05), ("check_rh_padding_l2_20200916_05", check_rh_padding_l2_20200916_05), ("check_rh_foreign_l1_20200916_06", check_rh_foreign_l1_20200916_06), ("check_rh_foreign_l2_20200916_06", check_rh_foreign_l2_20200916_06), ("check_rh_padding_l1_20200916_06", check_rh_padding_l1_20200916_06), ("check_rh_padding_l2_20200916_06", check_rh_padding_l2_20200916_06), ("check_rh_foreign_l1_20200916_07", check_rh_foreign_l1_20200916_07), ("check_rh_foreign_l2_20200916_07", check_rh_foreign_l2_20200916_07), ("check_rh_padding_l1_20200916_07", check_rh_padding_l1_20200916_07), ("check_rh_padding_l2_20200916_07", check_rh_padding_l2_20200916_07), ("check_rh_foreign_l1_20200916_08", check_rh_foreign_l1_20200916_08), ("check_rh_foreign_l2_20200916_08", check_rh_foreign_l2_20200916_08), ("check_rh_padding_l1_20200916_08", check_rh_padding_l1_20200916_08), ("check_rh_padding_l2_20200916_08", check_rh_padding_l2_20200916_08), ("check_rh_foreign_l1_20200916_09", check_rh_foreign_l1_20200916_09), ("check_rh_foreign_l2_20200916_09", check_rh_foreign_l2_20200916_09), ("check_rh_padding_l1_20200916_09", check_rh_padding_l1_20200916_09), ("check_rh_padding_l2_20200916_09", check_rh_padding_l2_20200916_09), ("check_rh_foreign_l1_20200916_10", check_rh_foreign_l1_20200916_10), ("check_rh_foreign_l2_20200916_10", check_rh_foreign_l2_20200916_10), ("check_rh_padding_l1_20200916_10", check_rh_padding_l1_20200916_10), ("check_rh_padding_l2_20200916_10", check_rh_padding_l2_20200916_10), ("check_rh_foreign_l1_20200916_11", check_rh_foreign_l1_20200916_11), ("check_rh_foreign_l2_20200916_11", check_rh_foreign_l2_20200916_11), ("check_rh_padding_l1_20200916_11", check_rh_padding_l1_20200916_11), ("check_rh_padding_l2_20200916_11", check_rh_padding_l2_20200916_11), ("check_rh_foreign_l1_20200916_12", check_rh_foreign_l1_20200916_12), ("check_rh_foreign_l2_20200916_12", check_rh_foreign_l2_20200916_12), ("check_rh_padding_l1_20200916_12", check_rh_padding_l1_20200916_12), ("check_rh_padding_l2_20200916_12", check_rh_padding_l2_20200916_12), ("check_rh_foreign_l1_20200916_13", check_rh_foreign_l1_20200916_13), ("check_rh_foreign_l2_20200916_13", check_rh_foreign_l2_20200916_13), ("check_rh_padding_l1_20200916_13", check_rh_padding_l1_20200916_13), ("check_rh_padding_l2_20200916_13", check_rh_padding_l2_20200916_13), ("check_rh_foreign_l1_20200916_14", check_rh_foreign_l1_20200916_14), ("check_rh_foreign_l2_20200916_14", check_rh_foreign_l2_20200916_14), ("check_rh_padding_l1_20200916_14", check_rh_padding_l1_20200916_14), ("check_rh_padding_l2_20200916_14", check_rh_padding_l2_20200916_14), ("check_rh_foreign_l1_20200916_15", check_rh_foreign_l1_20200916_15), ("check_rh_foreign_l2_20200916_15", check_rh_foreign_l2_20200916_15), ("check_rh_padding_l1_20200916_15", check_rh_padding_l1_20200916_15), ("check_rh_padding_l2_20200916_15", check_rh_padding_l2_20200916_15), ("check_rh_foreign_l1_20200916_16", check_rh_foreign_l1_20200916_16), ("check_rh_foreign_l2_20200916_16", check_rh_foreign_l2_20200916_16), ("check_rh_padding_l1_20200916_16", check_rh_padding_l1_20200916_16), ("check_rh_padding_l2_20200916_16", check_rh_padding_l2_20200916_16), ("check_rh_foreign_l1_20200916_17", check_rh_foreign_l1_20200916_17), ("check_rh_foreign_l2_20200916_17", check_rh_foreign_l2_20200916_17), ("check_rh_padding_l1_20200916_17", check_rh_padding_l1_20200916_17), ("check_rh_padding_l2_20200916_17", check_rh_padding_l2_20200916_17), ("check_rh_foreign_l1_20201105_01", check_rh_foreign_l1_20201105_01), ("check_rh_foreign_l2_20201105_01", check_rh_foreign_l2_20201105_01), ("check_rh_padding_l1_20201105_01", check_rh_padding_l1_20201105_01), ("check_rh_padding_l2_20201105_01", check_rh_padding_l2_20201105_01), ("check_rh_foreign_l1_20201105_02", check_rh_foreign_l1_20201105_02), ("check_rh_foreign_l2_20201105_02", check_rh_foreign_l2_20201105_02), ("check_rh_padding_l1_20201105_02", check_rh_padding_l1_20201105_02), ("check_rh_padding_l2_20201105_02", check_rh_padding_l2_20201105_02), ("check_rh_foreign_l1_20201105_03", check_rh_foreign_l1_20201105_03), ("check_rh_foreign_l2_20201105_03", check_rh_foreign_l2_20201105_03), ("check_rh_padding_l1_20201105_03", check_rh_padding_l1_20201105_03), ("check_rh_padding_l2_20201105_03", check_rh_padding_l2_20201105_03), ("check_rh_foreign_l1_20201105_04", check_rh_foreign_l1_20201105_04), ("check_rh_foreign_l2_20201105_04", check_rh_foreign_l2_20201105_04), ("check_rh_padding_l1_20201105_04", check_rh_padding_l1_20201105_04), ("check_rh_padding_l2_20201105_04", check_rh_padding_l2_20201105_04), ("check_rh_foreign_l1_20201105_05", check_rh_foreign_l1_20201105_05), ("check_rh_foreign_l2_20201105_05", check_rh_foreign_l2_20201105_05), ("check_rh_padding_l1_20201105_05", check_rh_padding_l1_20201105_05), ("check_rh_padding_l2_20201105_05", check_rh_padding_l2_20201105_05), ("check_rh_foreign_l1_20201105_06", check_rh_foreign_l1_20201105_06), ("check_rh_foreign_l2_20201105_06", check_rh_foreign_l2_20201105_06), ("check_rh_padding_l1_20201105_06", check_rh_padding_l1_20201105_06), ("check_rh_padding_l2_20201105_06", check_rh_padding_l2_20201105_06), ("check_rh_foreign_l1_20201105_07", check_rh_foreign_l1_20201105_07), ("check_rh_foreign_l2_20201105_07", check_rh_foreign_l2_20201105_07), ("check_rh_padding_l1_20201105_07", check_rh_padding_l1_20201105_07), ("check_rh_padding_l2_20201105_07", check_rh_padding_l2_20201105_07), ("check_rh_foreign_l1_20201105_08", check_rh_foreign_l1_20201105_08), ("check_rh_foreign_l2_20201105_08", check_rh_foreign_l2_20201105_08), ("check_rh_padding_l1_20201105_08", check_rh_padding_l1_20201105_08), ("check_rh_padding_l2_20201105_08", check_rh_padding_l2_20201105_08), ("check_rh_foreign_l1_20201105_09", check_rh_foreign_l1_20201105_09), ("check_rh_foreign_l2_20201105_09", check_rh_foreign_l2_20201105_09), ("check_rh_padding_l1_20201105_09", check_rh_padding_l1_20201105_09), ("check_rh_padding_l2_20201105_09", check_rh_padding_l2_20201105_09), ("check_rh_foreign_l1_20201105_10", check_rh_foreign_l1_20201105_10), ("check_rh_foreign_l2_20201105_10", check_rh_foreign_l2_20201105_10), ("check_rh_padding_l1_20201105_10", check_rh_padding_l1_20201105_10), ("check_rh_padding_l2_20201105_10", check_rh_padding_l2_20201105_10), ("check_rh_foreign_l1_20201105_11", check_rh_foreign_l1_20201105_11), ("check_rh_foreign_l2_20201105_11", check_rh_foreign_l2_20201105_11), ("check_rh_padding_l1_20201105_11", check_rh_padding_l1_20201105_11), ("check_rh_padding_l2_20201105_11", check_rh_padding_l2_20201105_11), ("check_rh_foreign_l1_20201105_12", check_rh_foreign_l1_20201105_12), ("check_rh_foreign_l2_20201105_12", check_rh_foreign_l2_20201105_12), ("check_rh_padding_l1_20201105_12", check_rh_padding_l1_20201105_12), ("check_rh_padding_l2_20201105_12", check_rh_padding_l2_20201105_12), ("check_rh_foreign_l1_20201105_13", check_rh_foreign_l1_20201105_13), ("check_rh_foreign_l2_20201105_13", check_rh_foreign_l2_20201105_13), ("check_rh_padding_l1_20201105_13", check_rh_padding_l1_20201105_13), ("check_rh_padding_l2_20201105_13", check_rh_padding_l2_20201105_13), ("check_rh_foreign_l1_20201105_14", check_rh_foreign_l1_20201105_14), ("check_rh_foreign_l2_20201105_14", check_rh_foreign_l2_20201105_14), ("check_rh_padding_l1_20201105_14", check_rh_padding_l1_20201105_14), ("check_rh_padding_l2_20201105_14", check_rh_padding_l2_20201105_14), ("check_rh_foreign_l1_20201105_15", check_rh_foreign_l1_20201105_15), ("check_rh_foreign_l2_20201105_15", check_rh_foreign_l2_20201105_15), ("check_rh_padding_l1_20201105_15", check_rh_padding_l1_20201105_15), ("check_rh_padding_l2_20201105_15", check_rh_padding_l2_20201105_15), ("check_rh_foreign_l1_20201105_16", check_rh_foreign_l1_20201105_16), ("check_rh_foreign_l2_20201105_16", check_rh_foreign_l2_20201105_16), ("check_rh_padding_l1_20201105_16", check_rh_padding_l1_20201105_16), ("check_rh_padding_l2_20201105_16", check_rh_padding_l2_20201105_16), ("check_rh_foreign_l1_20201105_17", check_rh_foreign_l1_20201105_17), ("check_rh_foreign_l2_20201105_17", check_rh_foreign_l2_20201105_17), ("check_rh_padding_l1_20201105_17", check_rh_padding_l1_20201105_17), ("check_rh_padding_l2_20201105_17", check_rh_padding_l2_20201105_17), ("check_rh_foreign_l1_20201105_18", check_rh_foreign_l1_20201105_18), ("check_rh_foreign_l2_20201105_18", check_rh_foreign_l2_20201105_18), ("check_rh_padding_l1_20201105_18", check_rh_padding_l1_20201105_18), ("check_rh_padding_l2_20201105_18", check_rh_padding_l2_20201105_18), ("check_rh_foreign_l1_20201105_19", check_rh_foreign_l1_20201105_19), ("check_rh_foreign_l2_20201105_19", check_rh_foreign_l2_20201105_19), ("check_rh_padding_l1_20201105_19", check_rh_padding_l1_20201105_19), ("check_rh_padding_l2_20201105_19", check_rh_padding_l2_20201105_19), ("check_rh_foreign_l1_20201105_20", check_rh_foreign_l1_20201105_20), ("check_rh_foreign_l2_20201105_20", check_rh_foreign_l2_20201105_20), ("check_rh_padding_l1_20201105_20", check_rh_padding_l1_20201105_20), ("check_rh_padding_l2_20201105_20", check_rh_padding_l2_20201105_20), ("check_rh_foreign_l1_20201105_21", check_rh_foreign_l1_20201105_21), ("check_rh_foreign_l2_20201105_21", check_rh_foreign_l2_20201105_21), ("check_rh_padding_l1_20201105_21", check_rh_padding_l1_20201105_21), ("check_rh_padding_l2_20201105_21", check_rh_padding_l2_20201105_21), ("check_rh_foreign_l1_20201105_22", check_rh_foreign_l1_20201105_22), ("check_rh_foreign_l2_20201105_22", check_rh_foreign_l2_20201105_22), ("check_rh_padding_l1_20201105_22", check_rh_padding_l1_20201105_22), ("check_rh_padding_l2_20201105_22", check_rh_padding_l2_20201105_22), ("check_rh_foreign_l1_20201105_23", check_rh_foreign_l1_20201105_23), ("check_rh_foreign_l2_20201105_23", check_rh_foreign_l2_20201105_23), ("check_rh_padding_l1_20201105_23", check_rh_padding_l1_20201105_23), ("check_rh_padding_l2_20201105_23", check_rh_padding_l2_20201105_23), ("check_rh_foreign_l1_20201105_24", check_rh_foreign_l1_20201105_24), ("check_rh_foreign_l2_20201105_24", check_rh_foreign_l2_20201105_24), ("check_rh_padding_l1_20201105_24", check_rh_padding_l1_20201105_24), ("check_rh_padding_l2_20201105_24", check_rh_padding_l2_20201105_24), ("check_rh_foreign_l1_20201105_25", check_rh_foreign_l1_20201105_25), ("check_rh_foreign_l2_20201105_25", check_rh_foreign_l2_20201105_25), ("check_rh_padding_l1_20201105_25", check_rh_padding_l1_20201105_25), ("check_rh_padding_l2_20201105_25", check_rh_padding_l2_20201105_25), ("check_rh_foreign_l1_20201105_26", check_rh_foreign_l1_20201105_26), ("check_rh_foreign_l2_20201105_26", check_rh_foreign_l2_20201105_26), ("check_rh_padding_l1_20201105_26", check_rh_padding_l1_20201105_26), ("check_rh_padding_l2_20201105_26", check_rh_padding_l2_20201105_26), ("check_rh_foreign_l1_20201105_27", check_rh_foreign_l1_20201105_27), ("check_rh_foreign_l2_20201105_27", check_rh_foreign_l2_20201105_27), ("check_rh_padding_l1_20201105_27", check_rh_padding_l1_20201105_27), ("check_rh_padding_l2_20201105_27", check_rh_padding_l2_20201105_27), ("check_rh_foreign_l1_20201105_28", check_rh_foreign_l1_20201105_28), ("check_rh_foreign_l2_20201105_28", check_rh_foreign_l2_20201105_28), ("check_rh_padding_l1_20201105_28", check_rh_padding_l1_20201105_28), ("check_rh_padding_l2_20201105_28", check_rh_padding_l2_20201105_28), ("check_rh_foreign_l1_20201105_29", check_rh_foreign_l1_20201105_29), ("check_rh_foreign_l2_20201105_29", check_rh_foreign_l2_20201105_29), ("check_rh_padding_l1_20201105_29", check_rh_padding_l1_20201105_29), ("check_rh_padding_l2_20201105_29", check_rh_padding_l2_20201105_29), ("check_rh_foreign_l1_20201105_30", check_rh_foreign_l1_20201105_30), ("check_rh_foreign_l2_20201105_30", check_rh_foreign_l2_20201105_30), ("check_rh_padding_l1_20201105_30", check_rh_padding_l1_20201105_30), ("check_rh_padding_l2_20201105_30", check_rh_padding_l2_20201105_30), ("check_rh_foreign_l1_20201105_31", check_rh_foreign_l1_20201105_31), ("check_rh_foreign_l2_20201105_31", check_rh_foreign_l2_20201105_31), ("check_rh_padding_l1_20201105_31", check_rh_padding_l1_20201105_31), ("check_rh_padding_l2_20201105_31", check_rh_padding_l2_20201105_31), ("check_rh_foreign_l1_20201105_32", check_rh_foreign_l1_20201105_32), ("check_rh_foreign_l2_20201105_32", check_rh_foreign_l2_20201105_32), ("check_rh_padding_l1_20201105_32", check_rh_padding_l1_20201105_32), ("check_rh_padding_l2_20201105_32", check_rh_padding_l2_20201105_32), ("check_rh_foreign_l1_20201105_33", check_rh_foreign_l1_20201105_33), ("check_rh_foreign_l2_20201105_33", check_rh_foreign_l2_20201105_33), ("check_rh_padding_l1_20201105_33", check_rh_padding_l1_20201105_33), ("check_rh_padding_l2_20201105_33", check_rh_padding_l2_20201105_33), ("check_rh_foreign_l1_20201105_34", check_rh_foreign_l1_20201105_34), ("check_rh_foreign_l2_20201105_34", check_rh_foreign_l2_20201105_34), ("check_rh_padding_l1_20201105_34", check_rh_padding_l1_20201105_34), ("check_rh_padding_l2_20201105_34", check_rh_padding_l2_20201105_34), ("check_rh_foreign_l1_20201105_35", check_rh_foreign_l1_20201105_35), ("check_rh_foreign_l2_20201105_35", check_rh_foreign_l2_20201105_35), ("check_rh_padding_l1_20201105_35", check_rh_padding_l1_20201105_35), ("check_rh_padding_l2_20201105_35", check_rh_padding_l2_20201105_35), ("check_rh_foreign_l1_20201105_36", check_rh_foreign_l1_20201105_36), ("check_rh_foreign_l2_20201105_36", check_rh_foreign_l2_20201105_36), ("check_rh_padding_l1_20201105_36", check_rh_padding_l1_20201105_36), ("check_rh_padding_l2_20201105_36", check_rh_padding_l2_20201105_36), ("check_rh_foreign_l1_20201105_37", check_rh_foreign_l1_20201105_37), ("check_rh_foreign_l2_20201105_37", check_rh_foreign_l2_20201105_37), ("check_rh_padding_l1_20201105_37", check_rh_padding_l1_20201105_37), ("check_rh_padding_l2_20201105_37", check_rh_padding_l2_20201105_37), ("check_rh_foreign_l1_20201105_38", check_rh_foreign_l1_20201105_38), ("check_rh_foreign_l2_20201105_38", check_rh_foreign_l2_20201105_38), ("check_rh_padding_l1_20201105_38", check_rh_padding_l1_20201105_38), ("check_rh_padding_l2_20201105_38", check_rh_padding_l2_20201105_38), ("check_rh_foreign_l1_20201105_39", check_rh_foreign_l1_20201105_39), ("check_rh_foreign_l2_20201105_39", check_rh_foreign_l2_20201105_39), ("check_rh_padding_l1_20201105_39", check_rh_padding_l1_20201105_39), ("check_rh_padding_l2_20201105_39", check_rh_padding_l2_20201105_39), ("check_rh_foreign_l1_20201105_40", check_rh_foreign_l1_20201105_40), ("check_rh_foreign_l2_20201105_40", check_rh_foreign_l2_20201105_40), ("check_rh_padding_l1_20201105_40", check_rh_padding_l1_20201105_40), ("check_rh_padding_l2_20201105_40", check_rh_padding_l2_20201105_40), ("check_rh_foreign_l1_20201216_01", check_rh_foreign_l1_20201216_01), ("check_rh_foreign_l2_20201216_01", check_rh_foreign_l2_20201216_01), ("check_rh_padding_l1_20201216_01", check_rh_padding_l1_20201216_01), ("check_rh_padding_l2_20201216_01", check_rh_padding_l2_20201216_01), ("check_rh_foreign_l1_20201216_02", check_rh_foreign_l1_20201216_02), ("check_rh_foreign_l2_20201216_02", check_rh_foreign_l2_20201216_02), ("check_rh_padding_l1_20201216_02", check_rh_padding_l1_20201216_02), ("check_rh_padding_l2_20201216_02", check_rh_padding_l2_20201216_02), ("check_rh_foreign_l1_20201216_03", check_rh_foreign_l1_20201216_03), ("check_rh_foreign_l2_20201216_03", check_rh_foreign_l2_20201216_03), ("check_rh_padding_l1_20201216_03", check_rh_padding_l1_20201216_03), ("check_rh_padding_l2_20201216_03", check_rh_padding_l2_20201216_03), ("check_rh_foreign_l1_20201216_04", check_rh_foreign_l1_20201216_04), ("check_rh_foreign_l2_20201216_04", check_rh_foreign_l2_20201216_04), ("check_rh_padding_l1_20201216_04", check_rh_padding_l1_20201216_04), ("check_rh_padding_l2_20201216_04", check_rh_padding_l2_20201216_04), ("check_rh_foreign_l1_20201216_05", check_rh_foreign_l1_20201216_05), ("check_rh_foreign_l2_20201216_05", check_rh_foreign_l2_20201216_05), ("check_rh_padding_l1_20201216_05", check_rh_padding_l1_20201216_05), ("check_rh_padding_l2_20201216_05", check_rh_padding_l2_20201216_05), ("check_rh_foreign_l1_20201216_06", check_rh_foreign_l1_20201216_06), ("check_rh_foreign_l2_20201216_06", check_rh_foreign_l2_20201216_06), ("check_rh_padding_l1_20201216_06", check_rh_padding_l1_20201216_06), ("check_rh_padding_l2_20201216_06", check_rh_padding_l2_20201216_06), ("check_rh_foreign_l1_20201216_07", check_rh_foreign_l1_20201216_07), ("check_rh_foreign_l2_20201216_07", check_rh_foreign_l2_20201216_07), ("check_rh_padding_l1_20201216_07", check_rh_padding_l1_20201216_07), ("check_rh_padding_l2_20201216_07", check_rh_padding_l2_20201216_07), ("check_rh_foreign_l1_20201216_08", check_rh_foreign_l1_20201216_08), ("check_rh_foreign_l2_20201216_08", check_rh_foreign_l2_20201216_08), ("check_rh_padding_l1_20201216_08", check_rh_padding_l1_20201216_08), ("check_rh_padding_l2_20201216_08", check_rh_padding_l2_20201216_08), ("check_rh_foreign_l1_20201216_09", check_rh_foreign_l1_20201216_09), ("check_rh_foreign_l2_20201216_09", check_rh_foreign_l2_20201216_09), ("check_rh_padding_l1_20201216_09", check_rh_padding_l1_20201216_09), ("check_rh_padding_l2_20201216_09", check_rh_padding_l2_20201216_09), ("check_rh_foreign_l1_20201216_10", check_rh_foreign_l1_20201216_10), ("check_rh_foreign_l2_20201216_10", check_rh_foreign_l2_20201216_10), ("check_rh_padding_l1_20201216_10", check_rh_padding_l1_20201216_10), ("check_rh_padding_l2_20201216_10", check_rh_padding_l2_20201216_10), ("check_rh_foreign_l1_20201216_11", check_rh_foreign_l1_20201216_11), ("check_rh_foreign_l2_20201216_11", check_rh_foreign_l2_20201216_11), ("check_rh_padding_l1_20201216_11", check_rh_padding_l1_20201216_11), ("check_rh_padding_l2_20201216_11", check_rh_padding_l2_20201216_11), ("check_rh_foreign_l1_20201216_12", check_rh_foreign_l1_20201216_12), ("check_rh_foreign_l2_20201216_12", check_rh_foreign_l2_20201216_12), ("check_rh_padding_l1_20201216_12", check_rh_padding_l1_20201216_12), ("check_rh_padding_l2_20201216_12", check_rh_padding_l2_20201216_12), ("check_rh_foreign_l1_20201216_13", check_rh_foreign_l1_20201216_13), ("check_rh_foreign_l2_20201216_13", check_rh_foreign_l2_20201216_13), ("check_rh_padding_l1_20201216_13", check_rh_padding_l1_20201216_13), ("check_rh_padding_l2_20201216_13", check_rh_padding_l2_20201216_13), ("check_rh_foreign_l1_20201216_14", check_rh_foreign_l1_20201216_14), ("check_rh_foreign_l2_20201216_14", check_rh_foreign_l2_20201216_14), ("check_rh_padding_l1_20201216_14", check_rh_padding_l1_20201216_14), ("check_rh_padding_l2_20201216_14", check_rh_padding_l2_20201216_14), ("check_rh_foreign_l1_20201216_15", check_rh_foreign_l1_20201216_15), ("check_rh_foreign_l2_20201216_15", check_rh_foreign_l2_20201216_15), ("check_rh_padding_l1_20201216_15", check_rh_padding_l1_20201216_15), ("check_rh_padding_l2_20201216_15", check_rh_padding_l2_20201216_15), ("check_rh_foreign_l1_20201216_16", check_rh_foreign_l1_20201216_16), ("check_rh_foreign_l2_20201216_16", check_rh_foreign_l2_20201216_16), ("check_rh_padding_l1_20201216_16", check_rh_padding_l1_20201216_16), ("check_rh_padding_l2_20201216_16", check_rh_padding_l2_20201216_16), ("check_rh_foreign_l1_20201216_17", check_rh_foreign_l1_20201216_17), ("check_rh_foreign_l2_20201216_17", check_rh_foreign_l2_20201216_17), ("check_rh_padding_l1_20201216_17", check_rh_padding_l1_20201216_17), ("check_rh_padding_l2_20201216_17", check_rh_padding_l2_20201216_17), ("check_rh_foreign_l1_20201216_18", check_rh_foreign_l1_20201216_18), ("check_rh_foreign_l2_20201216_18", check_rh_foreign_l2_20201216_18), ("check_rh_padding_l1_20201216_18", check_rh_padding_l1_20201216_18), ("check_rh_padding_l2_20201216_18", check_rh_padding_l2_20201216_18), ("check_rh_foreign_l1_20201216_19", check_rh_foreign_l1_20201216_19), ("check_rh_foreign_l2_20201216_19", check_rh_foreign_l2_20201216_19), ("check_rh_padding_l1_20201216_19", check_rh_padding_l1_20201216_19), ("check_rh_padding_l2_20201216_19", check_rh_padding_l2_20201216_19), ("check_rh_foreign_l1_20201216_20", check_rh_foreign_l1_20201216_20), ("check_rh_foreign_l2_20201216_20", check_rh_foreign_l2_20201216_20), ("check_rh_padding_l1_20201216_20", check_rh_padding_l1_20201216_20), ("check_rh_padding_l2_20201216_20", check_rh_padding_l2_20201216_20), ("check_rh_foreign_l1_20201216_21", check_rh_foreign_l1_20201216_21), ("check_rh_foreign_l2_20201216_21", check_rh_foreign_l2_20201216_21), ("check_rh_padding_l1_20201216_21", check_rh_padding_l1_20201216_21), ("check_rh_padding_l2_20201216_21", check_rh_padding_l2_20201216_21), ("check_rh_foreign_l1_20201216_22", check_rh_foreign_l1_20201216_22), ("check_rh_foreign_l2_20201216_22", check_rh_foreign_l2_20201216_22), ("check_rh_padding_l1_20201216_22", check_rh_padding_l1_20201216_22), ("check_rh_padding_l2_20201216_22", check_rh_padding_l2_20201216_22), ("check_rh_matrix_20200129", check_rh_matrix_20200129), ("check_rh_matrix_20200315", check_rh_matrix_20200315), ("check_rh_matrix_20200429", check_rh_matrix_20200429), ("check_rh_matrix_20200610", check_rh_matrix_20200610), ("check_rh_matrix_20200729", check_rh_matrix_20200729), ("check_rh_matrix_20200916", check_rh_matrix_20200916), ("check_rh_matrix_20201105", check_rh_matrix_20201105), ("check_rh_matrix_20201216", check_rh_matrix_20201216), ("check_rh_roster_of_files_20200129", check_rh_roster_of_files_20200129), ("check_rh_roster_of_files_20200315", check_rh_roster_of_files_20200315), ("check_rh_roster_of_files_20200429", check_rh_roster_of_files_20200429), ("check_rh_roster_of_files_20200610", check_rh_roster_of_files_20200610), ("check_rh_roster_of_files_20200729", check_rh_roster_of_files_20200729), ("check_rh_roster_of_files_20200916", check_rh_roster_of_files_20200916), ("check_rh_roster_of_files_20201105", check_rh_roster_of_files_20201105), ("check_rh_roster_of_files_20201216", check_rh_roster_of_files_20201216), ("check_rh_no_orphan_records", check_rh_no_orphan_records)],
    "partial_oracle": [("check_po_roster_20200129_01_POWELL", check_po_roster_20200129_01_POWELL), ("check_po_roster_20200129_01_KASHKARI", check_po_roster_20200129_01_KASHKARI), ("check_po_roster_20200129_01_CLARIDA", check_po_roster_20200129_01_CLARIDA), ("check_po_roster_20200129_01_MESTER", check_po_roster_20200129_01_MESTER), ("check_po_roster_20200129_01_ROSENGREN", check_po_roster_20200129_01_ROSENGREN), ("check_po_roster_20200129_01_BOWMAN", check_po_roster_20200129_01_BOWMAN), ("check_po_counter_20200129_01_BULLARD", check_po_counter_20200129_01_BULLARD), ("check_po_counter_20200129_01_BOSTIC", check_po_counter_20200129_01_BOSTIC), ("check_po_counter_20200129_01_ROSENGREN", check_po_counter_20200129_01_ROSENGREN), ("check_po_counter_20200129_01_BRAINARD", check_po_counter_20200129_01_BRAINARD), ("check_po_roster_20200129_02_QUARLES", check_po_roster_20200129_02_QUARLES), ("check_po_roster_20200129_02_BOWMAN", check_po_roster_20200129_02_BOWMAN), ("check_po_roster_20200129_02_EVANS", check_po_roster_20200129_02_EVANS), ("check_po_counter_20200129_02_BOSTIC", check_po_counter_20200129_02_BOSTIC), ("check_po_counter_20200129_02_ROSENGREN", check_po_counter_20200129_02_ROSENGREN), ("check_po_counter_20200129_02_GEORGE", check_po_counter_20200129_02_GEORGE), ("check_po_counter_20200129_02_KAPLAN", check_po_counter_20200129_02_KAPLAN), ("check_po_counter_20200129_02_BRAINARD", check_po_counter_20200129_02_BRAINARD), ("check_po_roster_20200129_03_BULLARD", check_po_roster_20200129_03_BULLARD), ("check_po_roster_20200129_03_BOSTIC", check_po_roster_20200129_03_BOSTIC), ("check_po_roster_20200129_03_MESTER", check_po_roster_20200129_03_MESTER), ("check_po_roster_20200129_03_ROSENGREN", check_po_roster_20200129_03_ROSENGREN), ("check_po_roster_20200129_03_GEORGE", check_po_roster_20200129_03_GEORGE), ("check_po_roster_20200129_03_EVANS", check_po_roster_20200129_03_EVANS), ("check_po_roster_20200129_03_BRAINARD", check_po_roster_20200129_03_BRAINARD), ("check_po_roster_20200129_03_KAPLAN", check_po_roster_20200129_03_KAPLAN), ("check_po_counter_20200129_03_POWELL", check_po_counter_20200129_03_POWELL), ("check_po_counter_20200129_03_KASHKARI", check_po_counter_20200129_03_KASHKARI), ("check_po_counter_20200129_03_CLARIDA", check_po_counter_20200129_03_CLARIDA), ("check_po_counter_20200129_03_HARKER", check_po_counter_20200129_03_HARKER), ("check_po_counter_20200129_03_BOWMAN", check_po_counter_20200129_03_BOWMAN), ("check_po_roster_20200129_04_WILLIAMS", check_po_roster_20200129_04_WILLIAMS), ("check_po_roster_20200129_04_EVANS", check_po_roster_20200129_04_EVANS), ("check_po_roster_20200129_04_BRAINARD", check_po_roster_20200129_04_BRAINARD), ("check_po_counter_20200129_04_POWELL", check_po_counter_20200129_04_POWELL), ("check_po_counter_20200129_04_KASHKARI", check_po_counter_20200129_04_KASHKARI), ("check_po_roster_20200129_05_QUARLES", check_po_roster_20200129_05_QUARLES), ("check_po_roster_20200129_05_KASHKARI", check_po_roster_20200129_05_KASHKARI), ("check_po_roster_20200129_05_POWELL", check_po_roster_20200129_05_POWELL), ("check_po_roster_20200129_05_BOSTIC", check_po_roster_20200129_05_BOSTIC), ("check_po_roster_20200129_05_HARKER", check_po_roster_20200129_05_HARKER), ("check_po_roster_20200129_05_CLARIDA", check_po_roster_20200129_05_CLARIDA), ("check_po_roster_20200129_05_MESTER", check_po_roster_20200129_05_MESTER), ("check_po_roster_20200129_05_DALY", check_po_roster_20200129_05_DALY), ("check_po_roster_20200129_05_EVANS", check_po_roster_20200129_05_EVANS), ("check_po_roster_20200129_05_BOWMAN", check_po_roster_20200129_05_BOWMAN), ("check_po_roster_20200129_05_BRAINARD", check_po_roster_20200129_05_BRAINARD), ("check_po_roster_20200129_05_KAPLAN", check_po_roster_20200129_05_KAPLAN), ("check_po_counter_20200129_05_ROSENGREN", check_po_counter_20200129_05_ROSENGREN), ("check_po_roster_20200129_06_QUARLES", check_po_roster_20200129_06_QUARLES), ("check_po_roster_20200129_06_BOSTIC", check_po_roster_20200129_06_BOSTIC), ("check_po_roster_20200129_06_MESTER", check_po_roster_20200129_06_MESTER), ("check_po_roster_20200129_06_ROSENGREN", check_po_roster_20200129_06_ROSENGREN), ("check_po_roster_20200129_06_BOWMAN", check_po_roster_20200129_06_BOWMAN), ("check_po_roster_20200129_06_DALY", check_po_roster_20200129_06_DALY), ("check_po_roster_20200129_06_KAPLAN", check_po_roster_20200129_06_KAPLAN), ("check_po_roster_20200129_06_BARKIN", check_po_roster_20200129_06_BARKIN), ("check_po_roster_20200129_07_POWELL", check_po_roster_20200129_07_POWELL), ("check_po_roster_20200129_07_BOSTIC", check_po_roster_20200129_07_BOSTIC), ("check_po_roster_20200129_07_WILLIAMS", check_po_roster_20200129_07_WILLIAMS), ("check_po_roster_20200129_07_MESTER", check_po_roster_20200129_07_MESTER), ("check_po_roster_20200129_07_ROSENGREN", check_po_roster_20200129_07_ROSENGREN), ("check_po_roster_20200129_07_BOWMAN", check_po_roster_20200129_07_BOWMAN), ("check_po_roster_20200129_07_BRAINARD", check_po_roster_20200129_07_BRAINARD), ("check_po_roster_20200129_07_KAPLAN", check_po_roster_20200129_07_KAPLAN), ("check_po_roster_20200129_07_BARKIN", check_po_roster_20200129_07_BARKIN), ("check_po_counter_20200129_07_QUARLES", check_po_counter_20200129_07_QUARLES), ("check_po_counter_20200129_07_KASHKARI", check_po_counter_20200129_07_KASHKARI), ("check_po_counter_20200129_07_DALY", check_po_counter_20200129_07_DALY), ("check_po_counter_20200129_07_EVANS", check_po_counter_20200129_07_EVANS), ("check_po_roster_20200129_08_QUARLES", check_po_roster_20200129_08_QUARLES), ("check_po_roster_20200129_08_KASHKARI", check_po_roster_20200129_08_KASHKARI), ("check_po_roster_20200129_08_HARKER", check_po_roster_20200129_08_HARKER), ("check_po_roster_20200129_08_DALY", check_po_roster_20200129_08_DALY), ("check_po_roster_20200129_08_EVANS", check_po_roster_20200129_08_EVANS), ("check_po_roster_20200129_08_BOWMAN", check_po_roster_20200129_08_BOWMAN), ("check_po_counter_20200129_08_ROSENGREN", check_po_counter_20200129_08_ROSENGREN), ("check_po_counter_20200129_08_BARKIN", check_po_counter_20200129_08_BARKIN), ("check_po_counter_20200129_08_KAPLAN", check_po_counter_20200129_08_KAPLAN), ("check_po_roster_20200129_09_KASHKARI", check_po_roster_20200129_09_KASHKARI), ("check_po_roster_20200129_09_DALY", check_po_roster_20200129_09_DALY), ("check_po_roster_20200129_09_EVANS", check_po_roster_20200129_09_EVANS), ("check_po_roster_20200129_09_BOWMAN", check_po_roster_20200129_09_BOWMAN), ("check_po_counter_20200129_09_ROSENGREN", check_po_counter_20200129_09_ROSENGREN), ("check_po_roster_20200129_10_QUARLES", check_po_roster_20200129_10_QUARLES), ("check_po_roster_20200129_10_CLARIDA", check_po_roster_20200129_10_CLARIDA), ("check_po_roster_20200129_10_MESTER", check_po_roster_20200129_10_MESTER), ("check_po_roster_20200129_10_EVANS", check_po_roster_20200129_10_EVANS), ("check_po_roster_20200129_10_BRAINARD", check_po_roster_20200129_10_BRAINARD), ("check_po_counter_20200129_10_QUARLES", check_po_counter_20200129_10_QUARLES), ("check_po_roster_20200129_11_CLARIDA", check_po_roster_20200129_11_CLARIDA), ("check_po_roster_20200129_11_BOSTIC", check_po_roster_20200129_11_BOSTIC), ("check_po_roster_20200129_11_MESTER", check_po_roster_20200129_11_MESTER), ("check_po_roster_20200129_11_EVANS", check_po_roster_20200129_11_EVANS), ("check_po_roster_20200129_11_BRAINARD", check_po_roster_20200129_11_BRAINARD), ("check_po_counter_20200129_11_EVANS", check_po_counter_20200129_11_EVANS), ("check_po_roster_20200129_12_POWELL", check_po_roster_20200129_12_POWELL), ("check_po_roster_20200129_12_BULLARD", check_po_roster_20200129_12_BULLARD), ("check_po_roster_20200129_12_KASHKARI", check_po_roster_20200129_12_KASHKARI), ("check_po_roster_20200129_12_WILLIAMS", check_po_roster_20200129_12_WILLIAMS), ("check_po_roster_20200129_12_CLARIDA", check_po_roster_20200129_12_CLARIDA), ("check_po_roster_20200129_12_HARKER", check_po_roster_20200129_12_HARKER), ("check_po_roster_20200129_12_DALY", check_po_roster_20200129_12_DALY), ("check_po_roster_20200129_12_BOWMAN", check_po_roster_20200129_12_BOWMAN), ("check_po_roster_20200129_12_BRAINARD", check_po_roster_20200129_12_BRAINARD), ("check_po_roster_20200129_12_BARKIN", check_po_roster_20200129_12_BARKIN), ("check_po_counter_20200129_12_QUARLES", check_po_counter_20200129_12_QUARLES), ("check_po_counter_20200129_12_BOSTIC", check_po_counter_20200129_12_BOSTIC), ("check_po_counter_20200129_12_MESTER", check_po_counter_20200129_12_MESTER), ("check_po_counter_20200129_12_BARKIN", check_po_counter_20200129_12_BARKIN), ("check_po_roster_20200129_13_BULLARD", check_po_roster_20200129_13_BULLARD), ("check_po_roster_20200129_13_KASHKARI", check_po_roster_20200129_13_KASHKARI), ("check_po_roster_20200129_13_CLARIDA", check_po_roster_20200129_13_CLARIDA), ("check_po_roster_20200129_13_HARKER", check_po_roster_20200129_13_HARKER), ("check_po_roster_20200129_13_WILLIAMS", check_po_roster_20200129_13_WILLIAMS), ("check_po_roster_20200129_13_DALY", check_po_roster_20200129_13_DALY), ("check_po_roster_20200129_13_BOWMAN", check_po_roster_20200129_13_BOWMAN), ("check_po_roster_20200129_13_BRAINARD", check_po_roster_20200129_13_BRAINARD), ("check_po_roster_20200129_13_BARKIN", check_po_roster_20200129_13_BARKIN), ("check_po_counter_20200129_13_QUARLES", check_po_counter_20200129_13_QUARLES), ("check_po_counter_20200129_13_MESTER", check_po_counter_20200129_13_MESTER), ("check_po_counter_20200129_13_GEORGE", check_po_counter_20200129_13_GEORGE), ("check_po_counter_20200129_13_BARKIN", check_po_counter_20200129_13_BARKIN), ("check_po_roster_20200129_14_BULLARD", check_po_roster_20200129_14_BULLARD), ("check_po_roster_20200129_14_KASHKARI", check_po_roster_20200129_14_KASHKARI), ("check_po_roster_20200129_14_WILLIAMS", check_po_roster_20200129_14_WILLIAMS), ("check_po_roster_20200129_14_HARKER", check_po_roster_20200129_14_HARKER), ("check_po_roster_20200129_14_GEORGE", check_po_roster_20200129_14_GEORGE), ("check_po_roster_20200129_14_DALY", check_po_roster_20200129_14_DALY), ("check_po_roster_20200129_14_EVANS", check_po_roster_20200129_14_EVANS), ("check_po_roster_20200129_14_BOWMAN", check_po_roster_20200129_14_BOWMAN), ("check_po_counter_20200129_14_POWELL", check_po_counter_20200129_14_POWELL), ("check_po_counter_20200129_14_HARKER", check_po_counter_20200129_14_HARKER), ("check_po_counter_20200129_14_BOSTIC", check_po_counter_20200129_14_BOSTIC), ("check_po_counter_20200129_14_MESTER", check_po_counter_20200129_14_MESTER), ("check_po_counter_20200129_14_ROSENGREN", check_po_counter_20200129_14_ROSENGREN), ("check_po_counter_20200129_14_GEORGE", check_po_counter_20200129_14_GEORGE), ("check_po_counter_20200129_14_BARKIN", check_po_counter_20200129_14_BARKIN), ("check_po_counter_20200129_14_KAPLAN", check_po_counter_20200129_14_KAPLAN), ("check_po_roster_20200129_15_POWELL", check_po_roster_20200129_15_POWELL), ("check_po_roster_20200129_15_BOSTIC", check_po_roster_20200129_15_BOSTIC), ("check_po_roster_20200129_15_CLARIDA", check_po_roster_20200129_15_CLARIDA), ("check_po_roster_20200129_15_HARKER", check_po_roster_20200129_15_HARKER), ("check_po_roster_20200129_15_WILLIAMS", check_po_roster_20200129_15_WILLIAMS), ("check_po_roster_20200129_15_MESTER", check_po_roster_20200129_15_MESTER), ("check_po_roster_20200129_15_KAPLAN", check_po_roster_20200129_15_KAPLAN), ("check_po_roster_20200129_15_BARKIN", check_po_roster_20200129_15_BARKIN), ("check_po_counter_20200129_15_BULLARD", check_po_counter_20200129_15_BULLARD), ("check_po_counter_20200129_15_KASHKARI", check_po_counter_20200129_15_KASHKARI), ("check_po_counter_20200129_15_POWELL", check_po_counter_20200129_15_POWELL), ("check_po_counter_20200129_15_WILLIAMS", check_po_counter_20200129_15_WILLIAMS), ("check_po_counter_20200129_15_HARKER", check_po_counter_20200129_15_HARKER), ("check_po_counter_20200129_15_CLARIDA", check_po_counter_20200129_15_CLARIDA), ("check_po_counter_20200129_15_DALY", check_po_counter_20200129_15_DALY), ("check_po_counter_20200129_15_EVANS", check_po_counter_20200129_15_EVANS), ("check_po_counter_20200129_15_BOWMAN", check_po_counter_20200129_15_BOWMAN), ("check_po_counter_20200129_15_BRAINARD", check_po_counter_20200129_15_BRAINARD), ("check_po_counter_20200129_15_BARKIN", check_po_counter_20200129_15_BARKIN), ("check_po_roster_20200129_16_QUARLES", check_po_roster_20200129_16_QUARLES), ("check_po_roster_20200129_16_BOSTIC", check_po_roster_20200129_16_BOSTIC), ("check_po_roster_20200129_16_MESTER", check_po_roster_20200129_16_MESTER), ("check_po_roster_20200129_16_KAPLAN", check_po_roster_20200129_16_KAPLAN), ("check_po_roster_20200129_16_BARKIN", check_po_roster_20200129_16_BARKIN), ("check_po_counter_20200129_16_DALY", check_po_counter_20200129_16_DALY), ("check_po_roster_20200129_17_POWELL", check_po_roster_20200129_17_POWELL), ("check_po_roster_20200129_17_BOSTIC", check_po_roster_20200129_17_BOSTIC), ("check_po_roster_20200129_17_HARKER", check_po_roster_20200129_17_HARKER), ("check_po_roster_20200129_17_ROSENGREN", check_po_roster_20200129_17_ROSENGREN), ("check_po_roster_20200129_17_EVANS", check_po_roster_20200129_17_EVANS), ("check_po_roster_20200129_17_BRAINARD", check_po_roster_20200129_17_BRAINARD), ("check_po_roster_20200129_17_BARKIN", check_po_roster_20200129_17_BARKIN), ("check_po_counter_20200129_17_BULLARD", check_po_counter_20200129_17_BULLARD), ("check_po_counter_20200129_17_GEORGE", check_po_counter_20200129_17_GEORGE), ("check_po_counter_20200129_17_DALY", check_po_counter_20200129_17_DALY), ("check_po_counter_20200129_17_EVANS", check_po_counter_20200129_17_EVANS), ("check_po_counter_20200129_17_BOWMAN", check_po_counter_20200129_17_BOWMAN), ("check_po_roster_20200129_18_BULLARD", check_po_roster_20200129_18_BULLARD), ("check_po_roster_20200129_18_BOSTIC", check_po_roster_20200129_18_BOSTIC), ("check_po_roster_20200129_18_GEORGE", check_po_roster_20200129_18_GEORGE), ("check_po_roster_20200129_18_MESTER", check_po_roster_20200129_18_MESTER), ("check_po_roster_20200129_18_BOWMAN", check_po_roster_20200129_18_BOWMAN), ("check_po_roster_20200129_18_DALY", check_po_roster_20200129_18_DALY), ("check_po_roster_20200129_18_BARKIN", check_po_roster_20200129_18_BARKIN), ("check_po_counter_20200129_18_QUARLES", check_po_counter_20200129_18_QUARLES), ("check_po_counter_20200129_18_KASHKARI", check_po_counter_20200129_18_KASHKARI), ("check_po_roster_20200129_19_KASHKARI", check_po_roster_20200129_19_KASHKARI), ("check_po_roster_20200129_19_WILLIAMS", check_po_roster_20200129_19_WILLIAMS), ("check_po_roster_20200129_19_MESTER", check_po_roster_20200129_19_MESTER), ("check_po_roster_20200129_19_GEORGE", check_po_roster_20200129_19_GEORGE), ("check_po_roster_20200129_19_BOWMAN", check_po_roster_20200129_19_BOWMAN), ("check_po_roster_20200129_19_BARKIN", check_po_roster_20200129_19_BARKIN), ("check_po_roster_20200129_20_CLARIDA", check_po_roster_20200129_20_CLARIDA), ("check_po_roster_20200129_20_WILLIAMS", check_po_roster_20200129_20_WILLIAMS), ("check_po_roster_20200129_20_MESTER", check_po_roster_20200129_20_MESTER), ("check_po_roster_20200129_20_BOWMAN", check_po_roster_20200129_20_BOWMAN), ("check_po_roster_20200129_20_DALY", check_po_roster_20200129_20_DALY), ("check_po_roster_20200129_20_KAPLAN", check_po_roster_20200129_20_KAPLAN), ("check_po_roster_20200129_20_BARKIN", check_po_roster_20200129_20_BARKIN), ("check_po_counter_20200129_20_QUARLES", check_po_counter_20200129_20_QUARLES), ("check_po_counter_20200129_20_BOSTIC", check_po_counter_20200129_20_BOSTIC), ("check_po_counter_20200129_20_WILLIAMS", check_po_counter_20200129_20_WILLIAMS), ("check_po_counter_20200129_20_GEORGE", check_po_counter_20200129_20_GEORGE), ("check_po_counter_20200129_20_MESTER", check_po_counter_20200129_20_MESTER), ("check_po_counter_20200129_20_EVANS", check_po_counter_20200129_20_EVANS), ("check_po_counter_20200129_20_KAPLAN", check_po_counter_20200129_20_KAPLAN), ("check_po_counter_20200129_20_BARKIN", check_po_counter_20200129_20_BARKIN), ("check_po_roster_20200129_21_KASHKARI", check_po_roster_20200129_21_KASHKARI), ("check_po_roster_20200129_21_HARKER", check_po_roster_20200129_21_HARKER), ("check_po_roster_20200129_21_MESTER", check_po_roster_20200129_21_MESTER), ("check_po_roster_20200129_21_DALY", check_po_roster_20200129_21_DALY), ("check_po_roster_20200129_21_KAPLAN", check_po_roster_20200129_21_KAPLAN), ("check_po_roster_20200129_21_BARKIN", check_po_roster_20200129_21_BARKIN), ("check_po_counter_20200129_21_BOSTIC", check_po_counter_20200129_21_BOSTIC), ("check_po_counter_20200129_21_EVANS", check_po_counter_20200129_21_EVANS), ("check_po_counter_20200129_21_KAPLAN", check_po_counter_20200129_21_KAPLAN), ("check_po_roster_20200129_22_KASHKARI", check_po_roster_20200129_22_KASHKARI), ("check_po_roster_20200129_22_GEORGE", check_po_roster_20200129_22_GEORGE), ("check_po_roster_20200129_22_BOWMAN", check_po_roster_20200129_22_BOWMAN), ("check_po_roster_20200129_22_KAPLAN", check_po_roster_20200129_22_KAPLAN), ("check_po_roster_20200129_23_BULLARD", check_po_roster_20200129_23_BULLARD), ("check_po_roster_20200129_23_BOSTIC", check_po_roster_20200129_23_BOSTIC), ("check_po_roster_20200129_23_HARKER", check_po_roster_20200129_23_HARKER), ("check_po_roster_20200129_23_MESTER", check_po_roster_20200129_23_MESTER), ("check_po_roster_20200129_23_EVANS", check_po_roster_20200129_23_EVANS), ("check_po_roster_20200129_23_BARKIN", check_po_roster_20200129_23_BARKIN), ("check_po_counter_20200129_23_KASHKARI", check_po_counter_20200129_23_KASHKARI), ("check_po_counter_20200129_23_CLARIDA", check_po_counter_20200129_23_CLARIDA), ("check_po_counter_20200129_23_DALY", check_po_counter_20200129_23_DALY), ("check_po_counter_20200129_23_KAPLAN", check_po_counter_20200129_23_KAPLAN), ("check_po_roster_20200129_24_CLARIDA", check_po_roster_20200129_24_CLARIDA), ("check_po_roster_20200129_24_MESTER", check_po_roster_20200129_24_MESTER), ("check_po_roster_20200129_24_DALY", check_po_roster_20200129_24_DALY), ("check_po_roster_20200129_24_BRAINARD", check_po_roster_20200129_24_BRAINARD), ("check_po_roster_20200129_24_BARKIN", check_po_roster_20200129_24_BARKIN), ("check_po_roster_20200129_25_KASHKARI", check_po_roster_20200129_25_KASHKARI), ("check_po_roster_20200129_25_BOSTIC", check_po_roster_20200129_25_BOSTIC), ("check_po_roster_20200129_25_CLARIDA", check_po_roster_20200129_25_CLARIDA), ("check_po_roster_20200129_25_MESTER", check_po_roster_20200129_25_MESTER), ("check_po_roster_20200129_25_DALY", check_po_roster_20200129_25_DALY), ("check_po_roster_20200129_25_KAPLAN", check_po_roster_20200129_25_KAPLAN), ("check_po_counter_20200129_25_BARKIN", check_po_counter_20200129_25_BARKIN), ("check_po_roster_20200129_26_KASHKARI", check_po_roster_20200129_26_KASHKARI), ("check_po_roster_20200129_26_QUARLES", check_po_roster_20200129_26_QUARLES), ("check_po_roster_20200129_26_WILLIAMS", check_po_roster_20200129_26_WILLIAMS), ("check_po_roster_20200129_26_CLARIDA", check_po_roster_20200129_26_CLARIDA), ("check_po_roster_20200129_26_HARKER", check_po_roster_20200129_26_HARKER), ("check_po_roster_20200129_26_MESTER", check_po_roster_20200129_26_MESTER), ("check_po_roster_20200129_26_BOWMAN", check_po_roster_20200129_26_BOWMAN), ("check_po_roster_20200129_26_DALY", check_po_roster_20200129_26_DALY), ("check_po_roster_20200129_27_KASHKARI", check_po_roster_20200129_27_KASHKARI), ("check_po_roster_20200129_27_POWELL", check_po_roster_20200129_27_POWELL), ("check_po_roster_20200129_27_WILLIAMS", check_po_roster_20200129_27_WILLIAMS), ("check_po_roster_20200129_27_CLARIDA", check_po_roster_20200129_27_CLARIDA), ("check_po_roster_20200129_27_GEORGE", check_po_roster_20200129_27_GEORGE), ("check_po_roster_20200129_27_DALY", check_po_roster_20200129_27_DALY), ("check_po_roster_20200129_27_BRAINARD", check_po_roster_20200129_27_BRAINARD), ("check_po_roster_20200129_27_KAPLAN", check_po_roster_20200129_27_KAPLAN), ("check_po_counter_20200129_27_BOSTIC", check_po_counter_20200129_27_BOSTIC), ("check_po_counter_20200129_27_MESTER", check_po_counter_20200129_27_MESTER), ("check_po_counter_20200129_27_BOWMAN", check_po_counter_20200129_27_BOWMAN), ("check_po_counter_20200129_27_BARKIN", check_po_counter_20200129_27_BARKIN), ("check_po_roster_20200129_28_BOSTIC", check_po_roster_20200129_28_BOSTIC), ("check_po_roster_20200129_28_MESTER", check_po_roster_20200129_28_MESTER), ("check_po_roster_20200129_28_GEORGE", check_po_roster_20200129_28_GEORGE), ("check_po_roster_20200129_28_KAPLAN", check_po_roster_20200129_28_KAPLAN), ("check_po_counter_20200129_28_KASHKARI", check_po_counter_20200129_28_KASHKARI), ("check_po_counter_20200129_28_WILLIAMS", check_po_counter_20200129_28_WILLIAMS), ("check_po_counter_20200129_28_GEORGE", check_po_counter_20200129_28_GEORGE), ("check_po_counter_20200129_28_DALY", check_po_counter_20200129_28_DALY), ("check_po_counter_20200129_28_EVANS", check_po_counter_20200129_28_EVANS), ("check_po_counter_20200129_28_BRAINARD", check_po_counter_20200129_28_BRAINARD), ("check_po_roster_20200129_29_QUARLES", check_po_roster_20200129_29_QUARLES), ("check_po_roster_20200129_29_BULLARD", check_po_roster_20200129_29_BULLARD), ("check_po_roster_20200129_29_WILLIAMS", check_po_roster_20200129_29_WILLIAMS), ("check_po_roster_20200129_29_MESTER", check_po_roster_20200129_29_MESTER), ("check_po_roster_20200129_29_GEORGE", check_po_roster_20200129_29_GEORGE), ("check_po_roster_20200129_29_ROSENGREN", check_po_roster_20200129_29_ROSENGREN), ("check_po_roster_20200129_29_BRAINARD", check_po_roster_20200129_29_BRAINARD), ("check_po_roster_20200129_29_KAPLAN", check_po_roster_20200129_29_KAPLAN), ("check_po_counter_20200129_29_BULLARD", check_po_counter_20200129_29_BULLARD), ("check_po_counter_20200129_29_CLARIDA", check_po_counter_20200129_29_CLARIDA), ("check_po_counter_20200129_29_DALY", check_po_counter_20200129_29_DALY), ("check_po_roster_20200129_30_POWELL", check_po_roster_20200129_30_POWELL), ("check_po_roster_20200129_30_QUARLES", check_po_roster_20200129_30_QUARLES), ("check_po_roster_20200129_30_BULLARD", check_po_roster_20200129_30_BULLARD), ("check_po_roster_20200129_30_WILLIAMS", check_po_roster_20200129_30_WILLIAMS), ("check_po_roster_20200129_30_BOSTIC", check_po_roster_20200129_30_BOSTIC), ("check_po_roster_20200129_30_ROSENGREN", check_po_roster_20200129_30_ROSENGREN), ("check_po_roster_20200129_30_GEORGE", check_po_roster_20200129_30_GEORGE), ("check_po_roster_20200129_30_MESTER", check_po_roster_20200129_30_MESTER), ("check_po_roster_20200129_30_EVANS", check_po_roster_20200129_30_EVANS), ("check_po_roster_20200129_30_BRAINARD", check_po_roster_20200129_30_BRAINARD), ("check_po_roster_20200129_30_KAPLAN", check_po_roster_20200129_30_KAPLAN), ("check_po_roster_20200129_30_BARKIN", check_po_roster_20200129_30_BARKIN), ("check_po_counter_20200129_30_POWELL", check_po_counter_20200129_30_POWELL), ("check_po_counter_20200129_30_QUARLES", check_po_counter_20200129_30_QUARLES), ("check_po_counter_20200129_30_KASHKARI", check_po_counter_20200129_30_KASHKARI), ("check_po_counter_20200129_30_CLARIDA", check_po_counter_20200129_30_CLARIDA), ("check_po_counter_20200129_30_HARKER", check_po_counter_20200129_30_HARKER), ("check_po_counter_20200129_30_BOWMAN", check_po_counter_20200129_30_BOWMAN), ("check_po_roster_20200129_31_WILLIAMS", check_po_roster_20200129_31_WILLIAMS), ("check_po_roster_20200129_31_MESTER", check_po_roster_20200129_31_MESTER), ("check_po_roster_20200129_31_ROSENGREN", check_po_roster_20200129_31_ROSENGREN), ("check_po_roster_20200129_31_GEORGE", check_po_roster_20200129_31_GEORGE), ("check_po_roster_20200129_31_BRAINARD", check_po_roster_20200129_31_BRAINARD), ("check_po_counter_20200129_31_QUARLES", check_po_counter_20200129_31_QUARLES), ("check_po_roster_20200129_32_POWELL", check_po_roster_20200129_32_POWELL), ("check_po_roster_20200129_32_KASHKARI", check_po_roster_20200129_32_KASHKARI), ("check_po_roster_20200129_32_CLARIDA", check_po_roster_20200129_32_CLARIDA), ("check_po_roster_20200129_32_HARKER", check_po_roster_20200129_32_HARKER), ("check_po_roster_20200129_32_ROSENGREN", check_po_roster_20200129_32_ROSENGREN), ("check_po_roster_20200129_32_DALY", check_po_roster_20200129_32_DALY), ("check_po_roster_20200129_32_EVANS", check_po_roster_20200129_32_EVANS), ("check_po_roster_20200129_32_BRAINARD", check_po_roster_20200129_32_BRAINARD), ("check_po_counter_20200129_32_QUARLES", check_po_counter_20200129_32_QUARLES), ("check_po_counter_20200129_32_GEORGE", check_po_counter_20200129_32_GEORGE), ("check_po_roster_20200129_33_POWELL", check_po_roster_20200129_33_POWELL), ("check_po_roster_20200129_33_KASHKARI", check_po_roster_20200129_33_KASHKARI), ("check_po_roster_20200129_33_CLARIDA", check_po_roster_20200129_33_CLARIDA), ("check_po_roster_20200129_33_DALY", check_po_roster_20200129_33_DALY), ("check_po_roster_20200129_33_EVANS", check_po_roster_20200129_33_EVANS), ("check_po_roster_20200129_33_BRAINARD", check_po_roster_20200129_33_BRAINARD), ("check_po_counter_20200129_33_QUARLES", check_po_counter_20200129_33_QUARLES), ("check_po_counter_20200129_33_BOWMAN", check_po_counter_20200129_33_BOWMAN), ("check_po_roster_20200129_34_POWELL", check_po_roster_20200129_34_POWELL), ("check_po_roster_20200129_34_KASHKARI", check_po_roster_20200129_34_KASHKARI), ("check_po_roster_20200129_34_CLARIDA", check_po_roster_20200129_34_CLARIDA), ("check_po_roster_20200129_34_BOSTIC", check_po_roster_20200129_34_BOSTIC), ("check_po_roster_20200129_34_HARKER", check_po_roster_20200129_34_HARKER), ("check_po_roster_20200129_34_MESTER", check_po_roster_20200129_34_MESTER), ("check_po_roster_20200129_34_ROSENGREN", check_po_roster_20200129_34_ROSENGREN), ("check_po_roster_20200129_34_EVANS", check_po_roster_20200129_34_EVANS), ("check_po_roster_20200129_34_BRAINARD", check_po_roster_20200129_34_BRAINARD), ("check_po_roster_20200129_34_KAPLAN", check_po_roster_20200129_34_KAPLAN), ("check_po_roster_20200129_34_BARKIN", check_po_roster_20200129_34_BARKIN), ("check_po_counter_20200129_34_GEORGE", check_po_counter_20200129_34_GEORGE), ("check_po_counter_20200129_34_BOWMAN", check_po_counter_20200129_34_BOWMAN), ("check_po_roster_20200129_35_KASHKARI", check_po_roster_20200129_35_KASHKARI), ("check_po_roster_20200129_35_WILLIAMS", check_po_roster_20200129_35_WILLIAMS), ("check_po_roster_20200129_35_CLARIDA", check_po_roster_20200129_35_CLARIDA), ("check_po_roster_20200129_35_DALY", check_po_roster_20200129_35_DALY), ("check_po_counter_20200129_35_ROSENGREN", check_po_counter_20200129_35_ROSENGREN), ("check_po_counter_20200129_35_MESTER", check_po_counter_20200129_35_MESTER), ("check_po_roster_20200129_36_POWELL", check_po_roster_20200129_36_POWELL), ("check_po_roster_20200129_36_QUARLES", check_po_roster_20200129_36_QUARLES), ("check_po_roster_20200129_36_WILLIAMS", check_po_roster_20200129_36_WILLIAMS), ("check_po_roster_20200129_36_EVANS", check_po_roster_20200129_36_EVANS), ("check_po_roster_20200129_36_BRAINARD", check_po_roster_20200129_36_BRAINARD), ("check_po_roster_20200129_36_KAPLAN", check_po_roster_20200129_36_KAPLAN), ("check_po_roster_20200129_37_BULLARD", check_po_roster_20200129_37_BULLARD), ("check_po_roster_20200129_37_QUARLES", check_po_roster_20200129_37_QUARLES), ("check_po_roster_20200129_37_WILLIAMS", check_po_roster_20200129_37_WILLIAMS), ("check_po_roster_20200129_37_MESTER", check_po_roster_20200129_37_MESTER), ("check_po_roster_20200129_37_BRAINARD", check_po_roster_20200129_37_BRAINARD), ("check_po_counter_20200129_37_WILLIAMS", check_po_counter_20200129_37_WILLIAMS), ("check_po_roster_20200315_01_POWELL", check_po_roster_20200315_01_POWELL), ("check_po_roster_20200315_01_DALY", check_po_roster_20200315_01_DALY), ("check_po_roster_20200315_01_BOWMAN", check_po_roster_20200315_01_BOWMAN), ("check_po_roster_20200315_01_CLARIDA", check_po_roster_20200315_01_CLARIDA), ("check_po_roster_20200315_02_MESTER", check_po_roster_20200315_02_MESTER), ("check_po_roster_20200315_02_DALY", check_po_roster_20200315_02_DALY), ("check_po_roster_20200315_02_BOSTIC", check_po_roster_20200315_02_BOSTIC), ("check_po_roster_20200315_02_BARKIN", check_po_roster_20200315_02_BARKIN), ("check_po_counter_20200315_02_QUARLES", check_po_counter_20200315_02_QUARLES), ("check_po_counter_20200315_02_BOWMAN", check_po_counter_20200315_02_BOWMAN), ("check_po_counter_20200315_02_BARKIN", check_po_counter_20200315_02_BARKIN), ("check_po_roster_20200315_03_HARKER", check_po_roster_20200315_03_HARKER), ("check_po_roster_20200315_03_BULLARD", check_po_roster_20200315_03_BULLARD), ("check_po_roster_20200315_03_QUARLES", check_po_roster_20200315_03_QUARLES), ("check_po_roster_20200315_03_KASHKARI", check_po_roster_20200315_03_KASHKARI), ("check_po_roster_20200315_03_BRAINARD", check_po_roster_20200315_03_BRAINARD), ("check_po_roster_20200315_03_BOWMAN", check_po_roster_20200315_03_BOWMAN), ("check_po_roster_20200315_03_WILLIAMS", check_po_roster_20200315_03_WILLIAMS), ("check_po_roster_20200315_03_BARKIN", check_po_roster_20200315_03_BARKIN), ("check_po_counter_20200315_03_KAPLAN", check_po_counter_20200315_03_KAPLAN), ("check_po_counter_20200315_03_DALY", check_po_counter_20200315_03_DALY), ("check_po_counter_20200315_03_GEORGE", check_po_counter_20200315_03_GEORGE), ("check_po_counter_20200315_03_BRAINARD", check_po_counter_20200315_03_BRAINARD), ("check_po_counter_20200315_03_ROSENGREN", check_po_counter_20200315_03_ROSENGREN), ("check_po_counter_20200315_03_BOWMAN", check_po_counter_20200315_03_BOWMAN), ("check_po_roster_20200315_04_KAPLAN", check_po_roster_20200315_04_KAPLAN), ("check_po_roster_20200315_04_POWELL", check_po_roster_20200315_04_POWELL), ("check_po_roster_20200315_04_MESTER", check_po_roster_20200315_04_MESTER), ("check_po_roster_20200315_04_DALY", check_po_roster_20200315_04_DALY), ("check_po_roster_20200315_04_ROSENGREN", check_po_roster_20200315_04_ROSENGREN), ("check_po_roster_20200315_04_BRAINARD", check_po_roster_20200315_04_BRAINARD), ("check_po_roster_20200315_04_KASHKARI", check_po_roster_20200315_04_KASHKARI), ("check_po_roster_20200315_04_BOSTIC", check_po_roster_20200315_04_BOSTIC), ("check_po_roster_20200315_04_BOWMAN", check_po_roster_20200315_04_BOWMAN), ("check_po_roster_20200315_04_WILLIAMS", check_po_roster_20200315_04_WILLIAMS), ("check_po_roster_20200315_05_BULLARD", check_po_roster_20200315_05_BULLARD), ("check_po_roster_20200315_05_POWELL", check_po_roster_20200315_05_POWELL), ("check_po_roster_20200315_05_HARKER", check_po_roster_20200315_05_HARKER), ("check_po_roster_20200315_05_DALY", check_po_roster_20200315_05_DALY), ("check_po_roster_20200315_05_GEORGE", check_po_roster_20200315_05_GEORGE), ("check_po_roster_20200315_05_QUARLES", check_po_roster_20200315_05_QUARLES), ("check_po_roster_20200315_05_KASHKARI", check_po_roster_20200315_05_KASHKARI), ("check_po_roster_20200315_05_ROSENGREN", check_po_roster_20200315_05_ROSENGREN), ("check_po_roster_20200315_05_BRAINARD", check_po_roster_20200315_05_BRAINARD), ("check_po_roster_20200315_05_EVANS", check_po_roster_20200315_05_EVANS), ("check_po_roster_20200315_05_WILLIAMS", check_po_roster_20200315_05_WILLIAMS), ("check_po_roster_20200315_05_CLARIDA", check_po_roster_20200315_05_CLARIDA), ("check_po_roster_20200315_05_BARKIN", check_po_roster_20200315_05_BARKIN), ("check_po_counter_20200315_05_KAPLAN", check_po_counter_20200315_05_KAPLAN), ("check_po_counter_20200315_05_MESTER", check_po_counter_20200315_05_MESTER), ("check_po_counter_20200315_05_QUARLES", check_po_counter_20200315_05_QUARLES), ("check_po_counter_20200315_05_BOSTIC", check_po_counter_20200315_05_BOSTIC), ("check_po_counter_20200315_05_BOWMAN", check_po_counter_20200315_05_BOWMAN), ("check_po_roster_20200315_06_KAPLAN", check_po_roster_20200315_06_KAPLAN), ("check_po_roster_20200315_06_MESTER", check_po_roster_20200315_06_MESTER), ("check_po_roster_20200315_06_BOSTIC", check_po_roster_20200315_06_BOSTIC), ("check_po_roster_20200315_06_BOWMAN", check_po_roster_20200315_06_BOWMAN), ("check_po_counter_20200315_06_POWELL", check_po_counter_20200315_06_POWELL), ("check_po_counter_20200315_06_HARKER", check_po_counter_20200315_06_HARKER), ("check_po_counter_20200315_06_BULLARD", check_po_counter_20200315_06_BULLARD), ("check_po_counter_20200315_06_DALY", check_po_counter_20200315_06_DALY), ("check_po_counter_20200315_06_KASHKARI", check_po_counter_20200315_06_KASHKARI), ("check_po_counter_20200315_06_EVANS", check_po_counter_20200315_06_EVANS), ("check_po_counter_20200315_06_WILLIAMS", check_po_counter_20200315_06_WILLIAMS), ("check_po_counter_20200315_06_CLARIDA", check_po_counter_20200315_06_CLARIDA), ("check_po_roster_20200315_07_HARKER", check_po_roster_20200315_07_HARKER), ("check_po_roster_20200315_07_POWELL", check_po_roster_20200315_07_POWELL), ("check_po_roster_20200315_07_MESTER", check_po_roster_20200315_07_MESTER), ("check_po_roster_20200315_07_DALY", check_po_roster_20200315_07_DALY), ("check_po_roster_20200315_07_BRAINARD", check_po_roster_20200315_07_BRAINARD), ("check_po_roster_20200315_07_KASHKARI", check_po_roster_20200315_07_KASHKARI), ("check_po_roster_20200315_07_BOWMAN", check_po_roster_20200315_07_BOWMAN), ("check_po_roster_20200315_07_BARKIN", check_po_roster_20200315_07_BARKIN), ("check_po_counter_20200315_07_BULLARD", check_po_counter_20200315_07_BULLARD), ("check_po_counter_20200315_07_WILLIAMS", check_po_counter_20200315_07_WILLIAMS), ("check_po_roster_20200315_08_WILLIAMS", check_po_roster_20200315_08_WILLIAMS), ("check_po_counter_20200315_08_BRAINARD", check_po_counter_20200315_08_BRAINARD), ("check_po_counter_20200315_08_BARKIN", check_po_counter_20200315_08_BARKIN), ("check_po_roster_20200315_09_BULLARD", check_po_roster_20200315_09_BULLARD), ("check_po_roster_20200315_09_HARKER", check_po_roster_20200315_09_HARKER), ("check_po_roster_20200315_09_KAPLAN", check_po_roster_20200315_09_KAPLAN), ("check_po_roster_20200315_09_MESTER", check_po_roster_20200315_09_MESTER), ("check_po_roster_20200315_09_DALY", check_po_roster_20200315_09_DALY), ("check_po_roster_20200315_09_BOSTIC", check_po_roster_20200315_09_BOSTIC), ("check_po_roster_20200315_09_BOWMAN", check_po_roster_20200315_09_BOWMAN), ("check_po_roster_20200315_09_BARKIN", check_po_roster_20200315_09_BARKIN), ("check_po_roster_20200315_10_BULLARD", check_po_roster_20200315_10_BULLARD), ("check_po_roster_20200315_10_HARKER", check_po_roster_20200315_10_HARKER), ("check_po_roster_20200315_10_MESTER", check_po_roster_20200315_10_MESTER), ("check_po_roster_20200315_10_QUARLES", check_po_roster_20200315_10_QUARLES), ("check_po_roster_20200315_10_GEORGE", check_po_roster_20200315_10_GEORGE), ("check_po_roster_20200315_10_BOSTIC", check_po_roster_20200315_10_BOSTIC), ("check_po_roster_20200315_10_BOWMAN", check_po_roster_20200315_10_BOWMAN), ("check_po_roster_20200315_10_BARKIN", check_po_roster_20200315_10_BARKIN), ("check_po_counter_20200315_10_DALY", check_po_counter_20200315_10_DALY), ("check_po_counter_20200315_10_EVANS", check_po_counter_20200315_10_EVANS), ("check_po_roster_20200315_11_BULLARD", check_po_roster_20200315_11_BULLARD), ("check_po_roster_20200315_11_MESTER", check_po_roster_20200315_11_MESTER), ("check_po_roster_20200315_11_ROSENGREN", check_po_roster_20200315_11_ROSENGREN), ("check_po_roster_20200315_11_BARKIN", check_po_roster_20200315_11_BARKIN), ("check_po_roster_20200315_12_MESTER", check_po_roster_20200315_12_MESTER), ("check_po_roster_20200315_12_BOWMAN", check_po_roster_20200315_12_BOWMAN), ("check_po_roster_20200315_12_BARKIN", check_po_roster_20200315_12_BARKIN), ("check_po_counter_20200315_12_DALY", check_po_counter_20200315_12_DALY), ("check_po_counter_20200315_12_BOSTIC", check_po_counter_20200315_12_BOSTIC), ("check_po_roster_20200315_13_POWELL", check_po_roster_20200315_13_POWELL), ("check_po_roster_20200315_13_KAPLAN", check_po_roster_20200315_13_KAPLAN), ("check_po_roster_20200315_13_DALY", check_po_roster_20200315_13_DALY), ("check_po_roster_20200315_13_MESTER", check_po_roster_20200315_13_MESTER), ("check_po_roster_20200315_13_BRAINARD", check_po_roster_20200315_13_BRAINARD), ("check_po_roster_20200315_13_EVANS", check_po_roster_20200315_13_EVANS), ("check_po_counter_20200315_13_BRAINARD", check_po_counter_20200315_13_BRAINARD), ("check_po_counter_20200315_13_BOWMAN", check_po_counter_20200315_13_BOWMAN), ("check_po_counter_20200315_13_BARKIN", check_po_counter_20200315_13_BARKIN), ("check_po_roster_20200315_14_HARKER", check_po_roster_20200315_14_HARKER), ("check_po_roster_20200315_14_POWELL", check_po_roster_20200315_14_POWELL), ("check_po_roster_20200315_14_KAPLAN", check_po_roster_20200315_14_KAPLAN), ("check_po_roster_20200315_14_MESTER", check_po_roster_20200315_14_MESTER), ("check_po_roster_20200315_14_GEORGE", check_po_roster_20200315_14_GEORGE), ("check_po_roster_20200315_14_DALY", check_po_roster_20200315_14_DALY), ("check_po_roster_20200315_14_QUARLES", check_po_roster_20200315_14_QUARLES), ("check_po_roster_20200315_14_KASHKARI", check_po_roster_20200315_14_KASHKARI), ("check_po_roster_20200315_14_BRAINARD", check_po_roster_20200315_14_BRAINARD), ("check_po_roster_20200315_14_WILLIAMS", check_po_roster_20200315_14_WILLIAMS), ("check_po_roster_20200315_14_CLARIDA", check_po_roster_20200315_14_CLARIDA), ("check_po_counter_20200315_14_QUARLES", check_po_counter_20200315_14_QUARLES), ("check_po_counter_20200315_14_ROSENGREN", check_po_counter_20200315_14_ROSENGREN), ("check_po_counter_20200315_14_BRAINARD", check_po_counter_20200315_14_BRAINARD), ("check_po_roster_20200315_15_KAPLAN", check_po_roster_20200315_15_KAPLAN), ("check_po_roster_20200315_15_DALY", check_po_roster_20200315_15_DALY), ("check_po_roster_20200315_15_GEORGE", check_po_roster_20200315_15_GEORGE), ("check_po_roster_20200315_15_QUARLES", check_po_roster_20200315_15_QUARLES), ("check_po_roster_20200315_15_KASHKARI", check_po_roster_20200315_15_KASHKARI), ("check_po_roster_20200315_15_ROSENGREN", check_po_roster_20200315_15_ROSENGREN), ("check_po_roster_20200315_15_BRAINARD", check_po_roster_20200315_15_BRAINARD), ("check_po_counter_20200315_15_KASHKARI", check_po_counter_20200315_15_KASHKARI), ("check_po_roster_20200429_01_KAPLAN", check_po_roster_20200429_01_KAPLAN), ("check_po_roster_20200429_01_WILLIAMS", check_po_roster_20200429_01_WILLIAMS), ("check_po_roster_20200429_01_DALY", check_po_roster_20200429_01_DALY), ("check_po_roster_20200429_02_BRAINARD", check_po_roster_20200429_02_BRAINARD), ("check_po_roster_20200429_02_BOSTIC", check_po_roster_20200429_02_BOSTIC), ("check_po_roster_20200429_02_KAPLAN", check_po_roster_20200429_02_KAPLAN), ("check_po_roster_20200429_02_WILLIAMS", check_po_roster_20200429_02_WILLIAMS), ("check_po_roster_20200429_02_MESTER", check_po_roster_20200429_02_MESTER), ("check_po_roster_20200429_02_EVANS", check_po_roster_20200429_02_EVANS), ("check_po_roster_20200429_02_POWELL", check_po_roster_20200429_02_POWELL), ("check_po_roster_20200429_02_CLARIDA", check_po_roster_20200429_02_CLARIDA), ("check_po_roster_20200429_02_GEORGE", check_po_roster_20200429_02_GEORGE), ("check_po_roster_20200429_02_KASHKARI", check_po_roster_20200429_02_KASHKARI), ("check_po_roster_20200429_02_ROSENGREN", check_po_roster_20200429_02_ROSENGREN), ("check_po_roster_20200429_03_QUARLES", check_po_roster_20200429_03_QUARLES), ("check_po_roster_20200429_03_KAPLAN", check_po_roster_20200429_03_KAPLAN), ("check_po_counter_20200429_03_POWELL", check_po_counter_20200429_03_POWELL), ("check_po_roster_20200429_04_BRAINARD", check_po_roster_20200429_04_BRAINARD), ("check_po_roster_20200429_04_QUARLES", check_po_roster_20200429_04_QUARLES), ("check_po_roster_20200429_04_KAPLAN", check_po_roster_20200429_04_KAPLAN), ("check_po_roster_20200429_04_MESTER", check_po_roster_20200429_04_MESTER), ("check_po_roster_20200429_04_WILLIAMS", check_po_roster_20200429_04_WILLIAMS), ("check_po_roster_20200429_04_BARKIN", check_po_roster_20200429_04_BARKIN), ("check_po_roster_20200429_04_DALY", check_po_roster_20200429_04_DALY), ("check_po_roster_20200429_04_BULLARD", check_po_roster_20200429_04_BULLARD), ("check_po_roster_20200429_04_POWELL", check_po_roster_20200429_04_POWELL), ("check_po_roster_20200429_04_CLARIDA", check_po_roster_20200429_04_CLARIDA), ("check_po_roster_20200429_04_GEORGE", check_po_roster_20200429_04_GEORGE), ("check_po_roster_20200429_04_KASHKARI", check_po_roster_20200429_04_KASHKARI), ("check_po_roster_20200429_04_BOWMAN", check_po_roster_20200429_04_BOWMAN), ("check_po_roster_20200429_04_ROSENGREN", check_po_roster_20200429_04_ROSENGREN), ("check_po_roster_20200429_05_BRAINARD", check_po_roster_20200429_05_BRAINARD), ("check_po_roster_20200429_05_DALY", check_po_roster_20200429_05_DALY), ("check_po_roster_20200429_05_GEORGE", check_po_roster_20200429_05_GEORGE), ("check_po_roster_20200429_05_KASHKARI", check_po_roster_20200429_05_KASHKARI), ("check_po_roster_20200429_05_ROSENGREN", check_po_roster_20200429_05_ROSENGREN), ("check_po_counter_20200429_05_QUARLES", check_po_counter_20200429_05_QUARLES), ("check_po_roster_20200429_06_BRAINARD", check_po_roster_20200429_06_BRAINARD), ("check_po_roster_20200429_06_QUARLES", check_po_roster_20200429_06_QUARLES), ("check_po_roster_20200429_06_KASHKARI", check_po_roster_20200429_06_KASHKARI), ("check_po_roster_20200429_07_MESTER", check_po_roster_20200429_07_MESTER), ("check_po_roster_20200429_07_BARKIN", check_po_roster_20200429_07_BARKIN), ("check_po_roster_20200429_07_HARKER", check_po_roster_20200429_07_HARKER), ("check_po_roster_20200429_07_POWELL", check_po_roster_20200429_07_POWELL), ("check_po_roster_20200429_07_ROSENGREN", check_po_roster_20200429_07_ROSENGREN), ("check_po_roster_20200429_07_BOWMAN", check_po_roster_20200429_07_BOWMAN), ("check_po_roster_20200429_08_BRAINARD", check_po_roster_20200429_08_BRAINARD), ("check_po_roster_20200429_08_MESTER", check_po_roster_20200429_08_MESTER), ("check_po_roster_20200429_08_HARKER", check_po_roster_20200429_08_HARKER), ("check_po_roster_20200429_08_DALY", check_po_roster_20200429_08_DALY), ("check_po_roster_20200429_08_POWELL", check_po_roster_20200429_08_POWELL), ("check_po_roster_20200429_08_CLARIDA", check_po_roster_20200429_08_CLARIDA), ("check_po_roster_20200429_08_GEORGE", check_po_roster_20200429_08_GEORGE), ("check_po_roster_20200429_08_KASHKARI", check_po_roster_20200429_08_KASHKARI), ("check_po_roster_20200429_08_BOWMAN", check_po_roster_20200429_08_BOWMAN), ("check_po_counter_20200429_08_WILLIAMS", check_po_counter_20200429_08_WILLIAMS), ("check_po_counter_20200429_08_BULLARD", check_po_counter_20200429_08_BULLARD), ("check_po_counter_20200429_08_EVANS", check_po_counter_20200429_08_EVANS), ("check_po_counter_20200429_08_POWELL", check_po_counter_20200429_08_POWELL), ("check_po_counter_20200429_08_CLARIDA", check_po_counter_20200429_08_CLARIDA), ("check_po_roster_20200429_09_BRAINARD", check_po_roster_20200429_09_BRAINARD), ("check_po_roster_20200429_09_WILLIAMS", check_po_roster_20200429_09_WILLIAMS), ("check_po_roster_20200429_09_DALY", check_po_roster_20200429_09_DALY), ("check_po_roster_20200429_09_POWELL", check_po_roster_20200429_09_POWELL), ("check_po_roster_20200429_10_MESTER", check_po_roster_20200429_10_MESTER), ("check_po_roster_20200429_10_DALY", check_po_roster_20200429_10_DALY), ("check_po_roster_20200429_10_CLARIDA", check_po_roster_20200429_10_CLARIDA), ("check_po_roster_20200429_10_BOWMAN", check_po_roster_20200429_10_BOWMAN), ("check_po_counter_20200429_10_CLARIDA", check_po_counter_20200429_10_CLARIDA), ("check_po_roster_20200429_11_CLARIDA", check_po_roster_20200429_11_CLARIDA), ("check_po_counter_20200429_11_WILLIAMS", check_po_counter_20200429_11_WILLIAMS), ("check_po_counter_20200429_11_BARKIN", check_po_counter_20200429_11_BARKIN), ("check_po_counter_20200429_11_GEORGE", check_po_counter_20200429_11_GEORGE), ("check_po_roster_20200429_12_BRAINARD", check_po_roster_20200429_12_BRAINARD), ("check_po_roster_20200429_12_MESTER", check_po_roster_20200429_12_MESTER), ("check_po_roster_20200429_12_DALY", check_po_roster_20200429_12_DALY), ("check_po_roster_20200429_12_CLARIDA", check_po_roster_20200429_12_CLARIDA), ("check_po_counter_20200429_12_MESTER", check_po_counter_20200429_12_MESTER), ("check_po_counter_20200429_12_GEORGE", check_po_counter_20200429_12_GEORGE), ("check_po_roster_20200610_01_WILLIAMS", check_po_roster_20200610_01_WILLIAMS), ("check_po_roster_20200610_01_BRAINARD", check_po_roster_20200610_01_BRAINARD), ("check_po_roster_20200610_01_KASHKARI", check_po_roster_20200610_01_KASHKARI), ("check_po_roster_20200610_01_ROSENGREN", check_po_roster_20200610_01_ROSENGREN), ("check_po_roster_20200610_01_GEORGE", check_po_roster_20200610_01_GEORGE), ("check_po_roster_20200610_01_MESTER", check_po_roster_20200610_01_MESTER), ("check_po_roster_20200610_01_DALY", check_po_roster_20200610_01_DALY), ("check_po_roster_20200610_01_POWELL", check_po_roster_20200610_01_POWELL), ("check_po_roster_20200610_01_EVANS", check_po_roster_20200610_01_EVANS), ("check_po_counter_20200610_01_BOSTIC", check_po_counter_20200610_01_BOSTIC), ("check_po_roster_20200610_02_BRAINARD", check_po_roster_20200610_02_BRAINARD), ("check_po_roster_20200610_02_KASHKARI", check_po_roster_20200610_02_KASHKARI), ("check_po_roster_20200610_02_WILLIAMS", check_po_roster_20200610_02_WILLIAMS), ("check_po_roster_20200610_02_DALY", check_po_roster_20200610_02_DALY), ("check_po_roster_20200610_02_POWELL", check_po_roster_20200610_02_POWELL), ("check_po_roster_20200610_02_EVANS", check_po_roster_20200610_02_EVANS), ("check_po_roster_20200610_02_CLARIDA", check_po_roster_20200610_02_CLARIDA), ("check_po_counter_20200610_02_BARKIN", check_po_counter_20200610_02_BARKIN), ("check_po_counter_20200610_02_BULLARD", check_po_counter_20200610_02_BULLARD), ("check_po_counter_20200610_02_GEORGE", check_po_counter_20200610_02_GEORGE), ("check_po_counter_20200610_02_HARKER", check_po_counter_20200610_02_HARKER), ("check_po_roster_20200610_03_ROSENGREN", check_po_roster_20200610_03_ROSENGREN), ("check_po_roster_20200610_03_BARKIN", check_po_roster_20200610_03_BARKIN), ("check_po_roster_20200610_03_BOWMAN", check_po_roster_20200610_03_BOWMAN), ("check_po_counter_20200610_03_BRAINARD", check_po_counter_20200610_03_BRAINARD), ("check_po_counter_20200610_03_HARKER", check_po_counter_20200610_03_HARKER), ("check_po_counter_20200610_03_EVANS", check_po_counter_20200610_03_EVANS), ("check_po_roster_20200610_04_BARKIN", check_po_roster_20200610_04_BARKIN), ("check_po_roster_20200610_04_MESTER", check_po_roster_20200610_04_MESTER), ("check_po_roster_20200610_04_KAPLAN", check_po_roster_20200610_04_KAPLAN), ("check_po_roster_20200610_04_EVANS", check_po_roster_20200610_04_EVANS), ("check_po_counter_20200610_04_WILLIAMS", check_po_counter_20200610_04_WILLIAMS), ("check_po_counter_20200610_04_KASHKARI", check_po_counter_20200610_04_KASHKARI), ("check_po_roster_20200610_05_ROSENGREN", check_po_roster_20200610_05_ROSENGREN), ("check_po_roster_20200610_05_GEORGE", check_po_roster_20200610_05_GEORGE), ("check_po_roster_20200610_05_BOSTIC", check_po_roster_20200610_05_BOSTIC), ("check_po_roster_20200610_05_BARKIN", check_po_roster_20200610_05_BARKIN), ("check_po_roster_20200610_05_BULLARD", check_po_roster_20200610_05_BULLARD), ("check_po_roster_20200610_05_MESTER", check_po_roster_20200610_05_MESTER), ("check_po_roster_20200610_05_POWELL", check_po_roster_20200610_05_POWELL), ("check_po_roster_20200610_05_KAPLAN", check_po_roster_20200610_05_KAPLAN), ("check_po_roster_20200610_05_HARKER", check_po_roster_20200610_05_HARKER), ("check_po_roster_20200610_05_EVANS", check_po_roster_20200610_05_EVANS), ("check_po_counter_20200610_05_WILLIAMS", check_po_counter_20200610_05_WILLIAMS), ("check_po_counter_20200610_05_BULLARD", check_po_counter_20200610_05_BULLARD), ("check_po_counter_20200610_05_QUARLES", check_po_counter_20200610_05_QUARLES), ("check_po_roster_20200610_06_GEORGE", check_po_roster_20200610_06_GEORGE), ("check_po_roster_20200610_06_BARKIN", check_po_roster_20200610_06_BARKIN), ("check_po_roster_20200610_06_KAPLAN", check_po_roster_20200610_06_KAPLAN), ("check_po_roster_20200610_06_BOWMAN", check_po_roster_20200610_06_BOWMAN), ("check_po_counter_20200610_06_KASHKARI", check_po_counter_20200610_06_KASHKARI), ("check_po_counter_20200610_06_ROSENGREN", check_po_counter_20200610_06_ROSENGREN), ("check_po_counter_20200610_06_BOSTIC", check_po_counter_20200610_06_BOSTIC), ("check_po_counter_20200610_06_MESTER", check_po_counter_20200610_06_MESTER), ("check_po_counter_20200610_06_DALY", check_po_counter_20200610_06_DALY), ("check_po_counter_20200610_06_POWELL", check_po_counter_20200610_06_POWELL), ("check_po_counter_20200610_06_HARKER", check_po_counter_20200610_06_HARKER), ("check_po_counter_20200610_06_EVANS", check_po_counter_20200610_06_EVANS), ("check_po_counter_20200610_06_CLARIDA", check_po_counter_20200610_06_CLARIDA), ("check_po_roster_20200610_07_ROSENGREN", check_po_roster_20200610_07_ROSENGREN), ("check_po_roster_20200610_07_BULLARD", check_po_roster_20200610_07_BULLARD), ("check_po_roster_20200610_07_GEORGE", check_po_roster_20200610_07_GEORGE), ("check_po_roster_20200610_07_BOSTIC", check_po_roster_20200610_07_BOSTIC), ("check_po_roster_20200610_07_MESTER", check_po_roster_20200610_07_MESTER), ("check_po_roster_20200610_07_DALY", check_po_roster_20200610_07_DALY), ("check_po_roster_20200610_07_QUARLES", check_po_roster_20200610_07_QUARLES), ("check_po_roster_20200610_07_POWELL", check_po_roster_20200610_07_POWELL), ("check_po_roster_20200610_07_KAPLAN", check_po_roster_20200610_07_KAPLAN), ("check_po_roster_20200610_07_HARKER", check_po_roster_20200610_07_HARKER), ("check_po_roster_20200610_07_EVANS", check_po_roster_20200610_07_EVANS), ("check_po_roster_20200610_07_BOWMAN", check_po_roster_20200610_07_BOWMAN), ("check_po_counter_20200610_07_BRAINARD", check_po_counter_20200610_07_BRAINARD), ("check_po_counter_20200610_07_KASHKARI", check_po_counter_20200610_07_KASHKARI), ("check_po_roster_20200610_08_BRAINARD", check_po_roster_20200610_08_BRAINARD), ("check_po_roster_20200610_08_ROSENGREN", check_po_roster_20200610_08_ROSENGREN), ("check_po_roster_20200610_08_KASHKARI", check_po_roster_20200610_08_KASHKARI), ("check_po_roster_20200610_08_WILLIAMS", check_po_roster_20200610_08_WILLIAMS), ("check_po_roster_20200610_08_BULLARD", check_po_roster_20200610_08_BULLARD), ("check_po_roster_20200610_08_GEORGE", check_po_roster_20200610_08_GEORGE), ("check_po_roster_20200610_08_BOSTIC", check_po_roster_20200610_08_BOSTIC), ("check_po_roster_20200610_08_BARKIN", check_po_roster_20200610_08_BARKIN), ("check_po_roster_20200610_08_MESTER", check_po_roster_20200610_08_MESTER), ("check_po_roster_20200610_08_DALY", check_po_roster_20200610_08_DALY), ("check_po_roster_20200610_08_QUARLES", check_po_roster_20200610_08_QUARLES), ("check_po_roster_20200610_08_KAPLAN", check_po_roster_20200610_08_KAPLAN), ("check_po_roster_20200610_08_HARKER", check_po_roster_20200610_08_HARKER), ("check_po_roster_20200610_08_EVANS", check_po_roster_20200610_08_EVANS), ("check_po_roster_20200610_08_CLARIDA", check_po_roster_20200610_08_CLARIDA), ("check_po_roster_20200610_08_BOWMAN", check_po_roster_20200610_08_BOWMAN), ("check_po_counter_20200610_08_KASHKARI", check_po_counter_20200610_08_KASHKARI), ("check_po_roster_20200610_09_BOSTIC", check_po_roster_20200610_09_BOSTIC), ("check_po_roster_20200610_09_GEORGE", check_po_roster_20200610_09_GEORGE), ("check_po_roster_20200610_09_DALY", check_po_roster_20200610_09_DALY), ("check_po_roster_20200610_09_MESTER", check_po_roster_20200610_09_MESTER), ("check_po_roster_20200610_09_HARKER", check_po_roster_20200610_09_HARKER), ("check_po_roster_20200610_09_EVANS", check_po_roster_20200610_09_EVANS), ("check_po_roster_20200610_10_BRAINARD", check_po_roster_20200610_10_BRAINARD), ("check_po_roster_20200610_10_WILLIAMS", check_po_roster_20200610_10_WILLIAMS), ("check_po_roster_20200610_10_KASHKARI", check_po_roster_20200610_10_KASHKARI), ("check_po_roster_20200610_10_DALY", check_po_roster_20200610_10_DALY), ("check_po_roster_20200610_10_EVANS", check_po_roster_20200610_10_EVANS), ("check_po_counter_20200610_10_ROSENGREN", check_po_counter_20200610_10_ROSENGREN), ("check_po_counter_20200610_10_BULLARD", check_po_counter_20200610_10_BULLARD), ("check_po_counter_20200610_10_BOSTIC", check_po_counter_20200610_10_BOSTIC), ("check_po_counter_20200610_10_GEORGE", check_po_counter_20200610_10_GEORGE), ("check_po_counter_20200610_10_DALY", check_po_counter_20200610_10_DALY), ("check_po_counter_20200610_10_HARKER", check_po_counter_20200610_10_HARKER), ("check_po_counter_20200610_10_KAPLAN", check_po_counter_20200610_10_KAPLAN), ("check_po_counter_20200610_10_EVANS", check_po_counter_20200610_10_EVANS), ("check_po_counter_20200610_10_BOWMAN", check_po_counter_20200610_10_BOWMAN), ("check_po_roster_20200610_11_WILLIAMS", check_po_roster_20200610_11_WILLIAMS), ("check_po_roster_20200610_11_KASHKARI", check_po_roster_20200610_11_KASHKARI), ("check_po_roster_20200610_11_BRAINARD", check_po_roster_20200610_11_BRAINARD), ("check_po_roster_20200610_11_ROSENGREN", check_po_roster_20200610_11_ROSENGREN), ("check_po_roster_20200610_11_BOSTIC", check_po_roster_20200610_11_BOSTIC), ("check_po_roster_20200610_11_GEORGE", check_po_roster_20200610_11_GEORGE), ("check_po_roster_20200610_11_DALY", check_po_roster_20200610_11_DALY), ("check_po_roster_20200610_11_MESTER", check_po_roster_20200610_11_MESTER), ("check_po_roster_20200610_11_POWELL", check_po_roster_20200610_11_POWELL), ("check_po_roster_20200610_11_KAPLAN", check_po_roster_20200610_11_KAPLAN), ("check_po_roster_20200610_11_CLARIDA", check_po_roster_20200610_11_CLARIDA), ("check_po_roster_20200610_11_EVANS", check_po_roster_20200610_11_EVANS), ("check_po_roster_20200610_12_WILLIAMS", check_po_roster_20200610_12_WILLIAMS), ("check_po_roster_20200610_12_BRAINARD", check_po_roster_20200610_12_BRAINARD), ("check_po_roster_20200610_12_BULLARD", check_po_roster_20200610_12_BULLARD), ("check_po_roster_20200610_12_BOSTIC", check_po_roster_20200610_12_BOSTIC), ("check_po_roster_20200610_12_MESTER", check_po_roster_20200610_12_MESTER), ("check_po_roster_20200610_12_DALY", check_po_roster_20200610_12_DALY), ("check_po_roster_20200610_12_POWELL", check_po_roster_20200610_12_POWELL), ("check_po_roster_20200610_12_EVANS", check_po_roster_20200610_12_EVANS), ("check_po_roster_20200610_12_CLARIDA", check_po_roster_20200610_12_CLARIDA), ("check_po_counter_20200610_12_BOSTIC", check_po_counter_20200610_12_BOSTIC), ("check_po_roster_20200610_13_BARKIN", check_po_roster_20200610_13_BARKIN), ("check_po_roster_20200610_13_QUARLES", check_po_roster_20200610_13_QUARLES), ("check_po_roster_20200610_13_BOWMAN", check_po_roster_20200610_13_BOWMAN), ("check_po_roster_20200610_14_GEORGE", check_po_roster_20200610_14_GEORGE), ("check_po_roster_20200610_14_KAPLAN", check_po_roster_20200610_14_KAPLAN), ("check_po_roster_20200610_15_KASHKARI", check_po_roster_20200610_15_KASHKARI), ("check_po_roster_20200610_15_BRAINARD", check_po_roster_20200610_15_BRAINARD), ("check_po_roster_20200610_15_GEORGE", check_po_roster_20200610_15_GEORGE), ("check_po_roster_20200610_15_CLARIDA", check_po_roster_20200610_15_CLARIDA), ("check_po_roster_20200610_15_EVANS", check_po_roster_20200610_15_EVANS), ("check_po_roster_20200610_16_KASHKARI", check_po_roster_20200610_16_KASHKARI), ("check_po_roster_20200610_16_ROSENGREN", check_po_roster_20200610_16_ROSENGREN), ("check_po_roster_20200610_16_BRAINARD", check_po_roster_20200610_16_BRAINARD), ("check_po_roster_20200610_16_WILLIAMS", check_po_roster_20200610_16_WILLIAMS), ("check_po_roster_20200610_16_BOSTIC", check_po_roster_20200610_16_BOSTIC), ("check_po_roster_20200610_16_MESTER", check_po_roster_20200610_16_MESTER), ("check_po_roster_20200610_16_DALY", check_po_roster_20200610_16_DALY), ("check_po_roster_20200610_16_POWELL", check_po_roster_20200610_16_POWELL), ("check_po_roster_20200610_16_EVANS", check_po_roster_20200610_16_EVANS), ("check_po_roster_20200610_16_CLARIDA", check_po_roster_20200610_16_CLARIDA), ("check_po_counter_20200610_16_BULLARD", check_po_counter_20200610_16_BULLARD), ("check_po_counter_20200610_16_BARKIN", check_po_counter_20200610_16_BARKIN), ("check_po_counter_20200610_16_QUARLES", check_po_counter_20200610_16_QUARLES), ("check_po_counter_20200610_16_BOWMAN", check_po_counter_20200610_16_BOWMAN), ("check_po_roster_20200610_17_ROSENGREN", check_po_roster_20200610_17_ROSENGREN), ("check_po_roster_20200610_17_BRAINARD", check_po_roster_20200610_17_BRAINARD), ("check_po_roster_20200610_17_BARKIN", check_po_roster_20200610_17_BARKIN), ("check_po_roster_20200610_17_POWELL", check_po_roster_20200610_17_POWELL), ("check_po_roster_20200610_18_WILLIAMS", check_po_roster_20200610_18_WILLIAMS), ("check_po_roster_20200610_18_BRAINARD", check_po_roster_20200610_18_BRAINARD), ("check_po_roster_20200610_18_KASHKARI", check_po_roster_20200610_18_KASHKARI), ("check_po_roster_20200610_18_ROSENGREN", check_po_roster_20200610_18_ROSENGREN), ("check_po_roster_20200610_18_GEORGE", check_po_roster_20200610_18_GEORGE), ("check_po_roster_20200610_18_BARKIN", check_po_roster_20200610_18_BARKIN), ("check_po_roster_20200610_18_BOSTIC", check_po_roster_20200610_18_BOSTIC), ("check_po_roster_20200610_18_MESTER", check_po_roster_20200610_18_MESTER), ("check_po_roster_20200610_18_DALY", check_po_roster_20200610_18_DALY), ("check_po_roster_20200610_18_QUARLES", check_po_roster_20200610_18_QUARLES), ("check_po_roster_20200610_18_POWELL", check_po_roster_20200610_18_POWELL), ("check_po_roster_20200610_18_KAPLAN", check_po_roster_20200610_18_KAPLAN), ("check_po_roster_20200610_18_EVANS", check_po_roster_20200610_18_EVANS), ("check_po_roster_20200610_18_CLARIDA", check_po_roster_20200610_18_CLARIDA), ("check_po_counter_20200610_18_BOSTIC", check_po_counter_20200610_18_BOSTIC), ("check_po_roster_20200610_19_KASHKARI", check_po_roster_20200610_19_KASHKARI), ("check_po_roster_20200610_19_BRAINARD", check_po_roster_20200610_19_BRAINARD), ("check_po_roster_20200610_19_WILLIAMS", check_po_roster_20200610_19_WILLIAMS), ("check_po_roster_20200610_19_ROSENGREN", check_po_roster_20200610_19_ROSENGREN), ("check_po_roster_20200610_19_DALY", check_po_roster_20200610_19_DALY), ("check_po_roster_20200610_19_MESTER", check_po_roster_20200610_19_MESTER), ("check_po_roster_20200610_19_KAPLAN", check_po_roster_20200610_19_KAPLAN), ("check_po_roster_20200610_19_POWELL", check_po_roster_20200610_19_POWELL), ("check_po_roster_20200610_19_EVANS", check_po_roster_20200610_19_EVANS), ("check_po_roster_20200610_19_CLARIDA", check_po_roster_20200610_19_CLARIDA), ("check_po_counter_20200610_19_GEORGE", check_po_counter_20200610_19_GEORGE), ("check_po_counter_20200610_19_BARKIN", check_po_counter_20200610_19_BARKIN), ("check_po_counter_20200610_19_QUARLES", check_po_counter_20200610_19_QUARLES), ("check_po_counter_20200610_19_HARKER", check_po_counter_20200610_19_HARKER), ("check_po_roster_20200610_20_WILLIAMS", check_po_roster_20200610_20_WILLIAMS), ("check_po_roster_20200610_20_BRAINARD", check_po_roster_20200610_20_BRAINARD), ("check_po_roster_20200610_20_DALY", check_po_roster_20200610_20_DALY), ("check_po_roster_20200610_20_MESTER", check_po_roster_20200610_20_MESTER), ("check_po_roster_20200610_20_POWELL", check_po_roster_20200610_20_POWELL), ("check_po_roster_20200610_20_EVANS", check_po_roster_20200610_20_EVANS), ("check_po_roster_20200729_01_MESTER", check_po_roster_20200729_01_MESTER), ("check_po_roster_20200729_01_EVANS", check_po_roster_20200729_01_EVANS), ("check_po_roster_20200729_01_BOSTIC", check_po_roster_20200729_01_BOSTIC), ("check_po_roster_20200729_01_GEORGE", check_po_roster_20200729_01_GEORGE), ("check_po_roster_20200729_01_BOWMAN", check_po_roster_20200729_01_BOWMAN), ("check_po_roster_20200729_01_BARKIN", check_po_roster_20200729_01_BARKIN), ("check_po_roster_20200729_02_QUARLES", check_po_roster_20200729_02_QUARLES), ("check_po_roster_20200729_02_CLARIDA", check_po_roster_20200729_02_CLARIDA), ("check_po_roster_20200729_02_KAPLAN", check_po_roster_20200729_02_KAPLAN), ("check_po_roster_20200729_02_EVANS", check_po_roster_20200729_02_EVANS), ("check_po_roster_20200729_02_BOSTIC", check_po_roster_20200729_02_BOSTIC), ("check_po_roster_20200729_02_ROSENGREN", check_po_roster_20200729_02_ROSENGREN), ("check_po_roster_20200729_02_BOWMAN", check_po_roster_20200729_02_BOWMAN), ("check_po_roster_20200729_02_BARKIN", check_po_roster_20200729_02_BARKIN), ("check_po_roster_20200729_03_MESTER", check_po_roster_20200729_03_MESTER), ("check_po_roster_20200729_03_BULLARD", check_po_roster_20200729_03_BULLARD), ("check_po_roster_20200729_03_BRAINARD", check_po_roster_20200729_03_BRAINARD), ("check_po_roster_20200729_03_DALY", check_po_roster_20200729_03_DALY), ("check_po_roster_20200729_03_KAPLAN", check_po_roster_20200729_03_KAPLAN), ("check_po_roster_20200729_03_KASHKARI", check_po_roster_20200729_03_KASHKARI), ("check_po_roster_20200729_03_EVANS", check_po_roster_20200729_03_EVANS), ("check_po_roster_20200729_03_POWELL", check_po_roster_20200729_03_POWELL), ("check_po_roster_20200729_03_BOSTIC", check_po_roster_20200729_03_BOSTIC), ("check_po_roster_20200729_03_WILLIAMS", check_po_roster_20200729_03_WILLIAMS), ("check_po_roster_20200729_03_GEORGE", check_po_roster_20200729_03_GEORGE), ("check_po_roster_20200729_03_BOWMAN", check_po_roster_20200729_03_BOWMAN), ("check_po_roster_20200729_03_BARKIN", check_po_roster_20200729_03_BARKIN), ("check_po_counter_20200729_03_BOWMAN", check_po_counter_20200729_03_BOWMAN), ("check_po_roster_20200729_04_DALY", check_po_roster_20200729_04_DALY), ("check_po_roster_20200729_04_KAPLAN", check_po_roster_20200729_04_KAPLAN), ("check_po_roster_20200729_04_GEORGE", check_po_roster_20200729_04_GEORGE), ("check_po_roster_20200729_04_BOWMAN", check_po_roster_20200729_04_BOWMAN), ("check_po_counter_20200729_04_KAPLAN", check_po_counter_20200729_04_KAPLAN), ("check_po_roster_20200729_05_BRAINARD", check_po_roster_20200729_05_BRAINARD), ("check_po_roster_20200729_05_DALY", check_po_roster_20200729_05_DALY), ("check_po_roster_20200729_05_KAPLAN", check_po_roster_20200729_05_KAPLAN), ("check_po_roster_20200729_05_KASHKARI", check_po_roster_20200729_05_KASHKARI), ("check_po_roster_20200729_05_POWELL", check_po_roster_20200729_05_POWELL), ("check_po_roster_20200729_05_ROSENGREN", check_po_roster_20200729_05_ROSENGREN), ("check_po_roster_20200729_05_WILLIAMS", check_po_roster_20200729_05_WILLIAMS), ("check_po_roster_20200729_05_BARKIN", check_po_roster_20200729_05_BARKIN), ("check_po_roster_20200729_05_HARKER", check_po_roster_20200729_05_HARKER), ("check_po_counter_20200729_05_BULLARD", check_po_counter_20200729_05_BULLARD), ("check_po_counter_20200729_05_BOWMAN", check_po_counter_20200729_05_BOWMAN), ("check_po_roster_20200729_06_MESTER", check_po_roster_20200729_06_MESTER), ("check_po_roster_20200729_06_BRAINARD", check_po_roster_20200729_06_BRAINARD), ("check_po_roster_20200729_06_CLARIDA", check_po_roster_20200729_06_CLARIDA), ("check_po_roster_20200729_06_KASHKARI", check_po_roster_20200729_06_KASHKARI), ("check_po_roster_20200729_06_EVANS", check_po_roster_20200729_06_EVANS), ("check_po_roster_20200729_06_POWELL", check_po_roster_20200729_06_POWELL), ("check_po_roster_20200729_06_ROSENGREN", check_po_roster_20200729_06_ROSENGREN), ("check_po_roster_20200729_06_WILLIAMS", check_po_roster_20200729_06_WILLIAMS), ("check_po_counter_20200729_06_QUARLES", check_po_counter_20200729_06_QUARLES), ("check_po_counter_20200729_06_WILLIAMS", check_po_counter_20200729_06_WILLIAMS), ("check_po_counter_20200729_06_GEORGE", check_po_counter_20200729_06_GEORGE), ("check_po_counter_20200729_06_BOWMAN", check_po_counter_20200729_06_BOWMAN), ("check_po_roster_20200729_07_QUARLES", check_po_roster_20200729_07_QUARLES), ("check_po_roster_20200729_07_MESTER", check_po_roster_20200729_07_MESTER), ("check_po_roster_20200729_07_BRAINARD", check_po_roster_20200729_07_BRAINARD), ("check_po_roster_20200729_07_EVANS", check_po_roster_20200729_07_EVANS), ("check_po_roster_20200729_07_KAPLAN", check_po_roster_20200729_07_KAPLAN), ("check_po_roster_20200729_07_BOSTIC", check_po_roster_20200729_07_BOSTIC), ("check_po_roster_20200729_07_ROSENGREN", check_po_roster_20200729_07_ROSENGREN), ("check_po_roster_20200729_07_GEORGE", check_po_roster_20200729_07_GEORGE), ("check_po_roster_20200729_07_HARKER", check_po_roster_20200729_07_HARKER), ("check_po_roster_20200729_07_BARKIN", check_po_roster_20200729_07_BARKIN), ("check_po_roster_20200729_08_QUARLES", check_po_roster_20200729_08_QUARLES), ("check_po_roster_20200729_08_MESTER", check_po_roster_20200729_08_MESTER), ("check_po_roster_20200729_08_BULLARD", check_po_roster_20200729_08_BULLARD), ("check_po_roster_20200729_08_BRAINARD", check_po_roster_20200729_08_BRAINARD), ("check_po_roster_20200729_08_DALY", check_po_roster_20200729_08_DALY), ("check_po_roster_20200729_08_CLARIDA", check_po_roster_20200729_08_CLARIDA), ("check_po_roster_20200729_08_KAPLAN", check_po_roster_20200729_08_KAPLAN), ("check_po_roster_20200729_08_KASHKARI", check_po_roster_20200729_08_KASHKARI), ("check_po_roster_20200729_08_EVANS", check_po_roster_20200729_08_EVANS), ("check_po_roster_20200729_08_BOSTIC", check_po_roster_20200729_08_BOSTIC), ("check_po_roster_20200729_08_ROSENGREN", check_po_roster_20200729_08_ROSENGREN), ("check_po_roster_20200729_08_WILLIAMS", check_po_roster_20200729_08_WILLIAMS), ("check_po_roster_20200729_08_GEORGE", check_po_roster_20200729_08_GEORGE), ("check_po_roster_20200729_08_BARKIN", check_po_roster_20200729_08_BARKIN), ("check_po_roster_20200729_08_BOWMAN", check_po_roster_20200729_08_BOWMAN), ("check_po_roster_20200729_08_HARKER", check_po_roster_20200729_08_HARKER), ("check_po_counter_20200729_08_WILLIAMS", check_po_counter_20200729_08_WILLIAMS), ("check_po_roster_20200729_09_MESTER", check_po_roster_20200729_09_MESTER), ("check_po_roster_20200729_09_BRAINARD", check_po_roster_20200729_09_BRAINARD), ("check_po_roster_20200729_09_BOSTIC", check_po_roster_20200729_09_BOSTIC), ("check_po_roster_20200729_09_WILLIAMS", check_po_roster_20200729_09_WILLIAMS), ("check_po_roster_20200729_10_QUARLES", check_po_roster_20200729_10_QUARLES), ("check_po_roster_20200729_10_MESTER", check_po_roster_20200729_10_MESTER), ("check_po_roster_20200729_10_DALY", check_po_roster_20200729_10_DALY), ("check_po_counter_20200729_10_ROSENGREN", check_po_counter_20200729_10_ROSENGREN), ("check_po_roster_20200729_11_MESTER", check_po_roster_20200729_11_MESTER), ("check_po_roster_20200729_11_BRAINARD", check_po_roster_20200729_11_BRAINARD), ("check_po_roster_20200729_11_DALY", check_po_roster_20200729_11_DALY), ("check_po_roster_20200729_11_KASHKARI", check_po_roster_20200729_11_KASHKARI), ("check_po_roster_20200729_11_ROSENGREN", check_po_roster_20200729_11_ROSENGREN), ("check_po_counter_20200729_11_QUARLES", check_po_counter_20200729_11_QUARLES), ("check_po_roster_20200729_12_QUARLES", check_po_roster_20200729_12_QUARLES), ("check_po_roster_20200729_12_MESTER", check_po_roster_20200729_12_MESTER), ("check_po_roster_20200729_12_BRAINARD", check_po_roster_20200729_12_BRAINARD), ("check_po_roster_20200729_12_DALY", check_po_roster_20200729_12_DALY), ("check_po_roster_20200729_12_EVANS", check_po_roster_20200729_12_EVANS), ("check_po_roster_20200729_12_ROSENGREN", check_po_roster_20200729_12_ROSENGREN), ("check_po_roster_20200729_12_GEORGE", check_po_roster_20200729_12_GEORGE), ("check_po_roster_20200729_12_BOWMAN", check_po_roster_20200729_12_BOWMAN), ("check_po_counter_20200729_12_KAPLAN", check_po_counter_20200729_12_KAPLAN), ("check_po_counter_20200729_12_BULLARD", check_po_counter_20200729_12_BULLARD), ("check_po_counter_20200729_12_BARKIN", check_po_counter_20200729_12_BARKIN), ("check_po_counter_20200729_12_BOSTIC", check_po_counter_20200729_12_BOSTIC), ("check_po_roster_20200729_13_QUARLES", check_po_roster_20200729_13_QUARLES), ("check_po_roster_20200729_13_MESTER", check_po_roster_20200729_13_MESTER), ("check_po_roster_20200729_13_DALY", check_po_roster_20200729_13_DALY), ("check_po_roster_20200729_13_KAPLAN", check_po_roster_20200729_13_KAPLAN), ("check_po_roster_20200729_13_KASHKARI", check_po_roster_20200729_13_KASHKARI), ("check_po_roster_20200729_13_EVANS", check_po_roster_20200729_13_EVANS), ("check_po_roster_20200729_13_POWELL", check_po_roster_20200729_13_POWELL), ("check_po_roster_20200729_13_ROSENGREN", check_po_roster_20200729_13_ROSENGREN), ("check_po_roster_20200729_13_BARKIN", check_po_roster_20200729_13_BARKIN), ("check_po_counter_20200729_13_BOWMAN", check_po_counter_20200729_13_BOWMAN), ("check_po_roster_20200729_14_MESTER", check_po_roster_20200729_14_MESTER), ("check_po_roster_20200729_14_QUARLES", check_po_roster_20200729_14_QUARLES), ("check_po_roster_20200729_14_BRAINARD", check_po_roster_20200729_14_BRAINARD), ("check_po_roster_20200729_14_DALY", check_po_roster_20200729_14_DALY), ("check_po_roster_20200729_14_CLARIDA", check_po_roster_20200729_14_CLARIDA), ("check_po_roster_20200729_14_KAPLAN", check_po_roster_20200729_14_KAPLAN), ("check_po_roster_20200729_14_KASHKARI", check_po_roster_20200729_14_KASHKARI), ("check_po_roster_20200729_14_EVANS", check_po_roster_20200729_14_EVANS), ("check_po_roster_20200729_14_POWELL", check_po_roster_20200729_14_POWELL), ("check_po_roster_20200729_14_ROSENGREN", check_po_roster_20200729_14_ROSENGREN), ("check_po_roster_20200729_14_WILLIAMS", check_po_roster_20200729_14_WILLIAMS), ("check_po_roster_20200729_14_GEORGE", check_po_roster_20200729_14_GEORGE), ("check_po_roster_20200729_14_BOWMAN", check_po_roster_20200729_14_BOWMAN), ("check_po_roster_20200729_14_BARKIN", check_po_roster_20200729_14_BARKIN), ("check_po_roster_20200729_15_MESTER", check_po_roster_20200729_15_MESTER), ("check_po_roster_20200729_15_BRAINARD", check_po_roster_20200729_15_BRAINARD), ("check_po_roster_20200729_15_DALY", check_po_roster_20200729_15_DALY), ("check_po_roster_20200729_15_CLARIDA", check_po_roster_20200729_15_CLARIDA), ("check_po_roster_20200729_15_KAPLAN", check_po_roster_20200729_15_KAPLAN), ("check_po_roster_20200729_15_KASHKARI", check_po_roster_20200729_15_KASHKARI), ("check_po_roster_20200729_15_ROSENGREN", check_po_roster_20200729_15_ROSENGREN), ("check_po_roster_20200729_15_GEORGE", check_po_roster_20200729_15_GEORGE), ("check_po_roster_20200729_15_BOWMAN", check_po_roster_20200729_15_BOWMAN), ("check_po_counter_20200729_15_QUARLES", check_po_counter_20200729_15_QUARLES), ("check_po_counter_20200729_15_GEORGE", check_po_counter_20200729_15_GEORGE), ("check_po_roster_20200729_16_MESTER", check_po_roster_20200729_16_MESTER), ("check_po_roster_20200729_16_DALY", check_po_roster_20200729_16_DALY), ("check_po_roster_20200729_16_KAPLAN", check_po_roster_20200729_16_KAPLAN), ("check_po_roster_20200729_16_WILLIAMS", check_po_roster_20200729_16_WILLIAMS), ("check_po_roster_20200729_16_GEORGE", check_po_roster_20200729_16_GEORGE), ("check_po_roster_20200729_16_BARKIN", check_po_roster_20200729_16_BARKIN), ("check_po_roster_20200729_17_QUARLES", check_po_roster_20200729_17_QUARLES), ("check_po_roster_20200729_17_BULLARD", check_po_roster_20200729_17_BULLARD), ("check_po_roster_20200729_17_BRAINARD", check_po_roster_20200729_17_BRAINARD), ("check_po_roster_20200729_17_DALY", check_po_roster_20200729_17_DALY), ("check_po_roster_20200729_17_CLARIDA", check_po_roster_20200729_17_CLARIDA), ("check_po_roster_20200729_17_KASHKARI", check_po_roster_20200729_17_KASHKARI), ("check_po_roster_20200729_17_EVANS", check_po_roster_20200729_17_EVANS), ("check_po_roster_20200729_17_POWELL", check_po_roster_20200729_17_POWELL), ("check_po_roster_20200729_17_WILLIAMS", check_po_roster_20200729_17_WILLIAMS), ("check_po_roster_20200729_17_ROSENGREN", check_po_roster_20200729_17_ROSENGREN), ("check_po_roster_20200729_17_GEORGE", check_po_roster_20200729_17_GEORGE), ("check_po_roster_20200729_17_HARKER", check_po_roster_20200729_17_HARKER), ("check_po_roster_20200729_17_BOWMAN", check_po_roster_20200729_17_BOWMAN), ("check_po_counter_20200729_17_MESTER", check_po_counter_20200729_17_MESTER), ("check_po_counter_20200729_17_BOSTIC", check_po_counter_20200729_17_BOSTIC), ("check_po_roster_20200729_18_QUARLES", check_po_roster_20200729_18_QUARLES), ("check_po_roster_20200729_18_BRAINARD", check_po_roster_20200729_18_BRAINARD), ("check_po_roster_20200729_18_KASHKARI", check_po_roster_20200729_18_KASHKARI), ("check_po_roster_20200729_18_POWELL", check_po_roster_20200729_18_POWELL), ("check_po_roster_20200729_18_WILLIAMS", check_po_roster_20200729_18_WILLIAMS), ("check_po_roster_20200729_18_GEORGE", check_po_roster_20200729_18_GEORGE), ("check_po_roster_20200729_18_BOWMAN", check_po_roster_20200729_18_BOWMAN), ("check_po_roster_20200729_18_HARKER", check_po_roster_20200729_18_HARKER), ("check_po_roster_20200729_19_QUARLES", check_po_roster_20200729_19_QUARLES), ("check_po_roster_20200729_19_BRAINARD", check_po_roster_20200729_19_BRAINARD), ("check_po_roster_20200729_19_KASHKARI", check_po_roster_20200729_19_KASHKARI), ("check_po_roster_20200729_19_POWELL", check_po_roster_20200729_19_POWELL), ("check_po_roster_20200729_19_WILLIAMS", check_po_roster_20200729_19_WILLIAMS), ("check_po_roster_20200729_19_GEORGE", check_po_roster_20200729_19_GEORGE), ("check_po_roster_20200729_19_BOWMAN", check_po_roster_20200729_19_BOWMAN), ("check_po_roster_20200729_19_HARKER", check_po_roster_20200729_19_HARKER), ("check_po_counter_20200729_19_BRAINARD", check_po_counter_20200729_19_BRAINARD), ("check_po_roster_20200729_20_BRAINARD", check_po_roster_20200729_20_BRAINARD), ("check_po_roster_20200729_20_KASHKARI", check_po_roster_20200729_20_KASHKARI), ("check_po_roster_20200729_20_WILLIAMS", check_po_roster_20200729_20_WILLIAMS), ("check_po_counter_20200729_20_QUARLES", check_po_counter_20200729_20_QUARLES), ("check_po_counter_20200729_20_POWELL", check_po_counter_20200729_20_POWELL), ("check_po_counter_20200729_20_HARKER", check_po_counter_20200729_20_HARKER), ("check_po_counter_20200729_20_KASHKARI", check_po_counter_20200729_20_KASHKARI), ("check_po_counter_20200729_20_GEORGE", check_po_counter_20200729_20_GEORGE), ("check_po_counter_20200729_20_BOWMAN", check_po_counter_20200729_20_BOWMAN), ("check_po_roster_20200916_01_BOWMAN", check_po_roster_20200916_01_BOWMAN), ("check_po_roster_20200916_01_CLARIDA", check_po_roster_20200916_01_CLARIDA), ("check_po_roster_20200916_01_BOSTIC", check_po_roster_20200916_01_BOSTIC), ("check_po_roster_20200916_01_BRAINARD", check_po_roster_20200916_01_BRAINARD), ("check_po_roster_20200916_01_KASHKARI", check_po_roster_20200916_01_KASHKARI), ("check_po_roster_20200916_01_EVANS", check_po_roster_20200916_01_EVANS), ("check_po_roster_20200916_01_QUARLES", check_po_roster_20200916_01_QUARLES), ("check_po_roster_20200916_01_DALY", check_po_roster_20200916_01_DALY), ("check_po_roster_20200916_01_WILLIAMS", check_po_roster_20200916_01_WILLIAMS), ("check_po_roster_20200916_01_GEORGE", check_po_roster_20200916_01_GEORGE), ("check_po_roster_20200916_01_POWELL", check_po_roster_20200916_01_POWELL), ("check_po_counter_20200916_01_BULLARD", check_po_counter_20200916_01_BULLARD), ("check_po_counter_20200916_01_BARKIN", check_po_counter_20200916_01_BARKIN), ("check_po_counter_20200916_01_QUARLES", check_po_counter_20200916_01_QUARLES), ("check_po_counter_20200916_01_WILLIAMS", check_po_counter_20200916_01_WILLIAMS), ("check_po_counter_20200916_01_POWELL", check_po_counter_20200916_01_POWELL), ("check_po_roster_20200916_02_MESTER", check_po_roster_20200916_02_MESTER), ("check_po_roster_20200916_02_CLARIDA", check_po_roster_20200916_02_CLARIDA), ("check_po_roster_20200916_02_BRAINARD", check_po_roster_20200916_02_BRAINARD), ("check_po_roster_20200916_02_KASHKARI", check_po_roster_20200916_02_KASHKARI), ("check_po_roster_20200916_02_QUARLES", check_po_roster_20200916_02_QUARLES), ("check_po_roster_20200916_02_ROSENGREN", check_po_roster_20200916_02_ROSENGREN), ("check_po_roster_20200916_02_EVANS", check_po_roster_20200916_02_EVANS), ("check_po_roster_20200916_02_DALY", check_po_roster_20200916_02_DALY), ("check_po_roster_20200916_02_WILLIAMS", check_po_roster_20200916_02_WILLIAMS), ("check_po_roster_20200916_02_GEORGE", check_po_roster_20200916_02_GEORGE), ("check_po_roster_20200916_02_POWELL", check_po_roster_20200916_02_POWELL), ("check_po_roster_20200916_02_HARKER", check_po_roster_20200916_02_HARKER), ("check_po_counter_20200916_02_BULLARD", check_po_counter_20200916_02_BULLARD), ("check_po_roster_20200916_03_CLARIDA", check_po_roster_20200916_03_CLARIDA), ("check_po_roster_20200916_03_BARKIN", check_po_roster_20200916_03_BARKIN), ("check_po_roster_20200916_03_QUARLES", check_po_roster_20200916_03_QUARLES), ("check_po_counter_20200916_03_KASHKARI", check_po_counter_20200916_03_KASHKARI), ("check_po_counter_20200916_03_BRAINARD", check_po_counter_20200916_03_BRAINARD), ("check_po_counter_20200916_03_EVANS", check_po_counter_20200916_03_EVANS), ("check_po_counter_20200916_03_POWELL", check_po_counter_20200916_03_POWELL), ("check_po_roster_20200916_04_CLARIDA", check_po_roster_20200916_04_CLARIDA), ("check_po_roster_20200916_04_POWELL", check_po_roster_20200916_04_POWELL), ("check_po_roster_20200916_05_BOWMAN", check_po_roster_20200916_05_BOWMAN), ("check_po_roster_20200916_05_BRAINARD", check_po_roster_20200916_05_BRAINARD), ("check_po_roster_20200916_05_BOSTIC", check_po_roster_20200916_05_BOSTIC), ("check_po_roster_20200916_05_POWELL", check_po_roster_20200916_05_POWELL), ("check_po_roster_20200916_06_MESTER", check_po_roster_20200916_06_MESTER), ("check_po_roster_20200916_06_BOSTIC", check_po_roster_20200916_06_BOSTIC), ("check_po_roster_20200916_06_EVANS", check_po_roster_20200916_06_EVANS), ("check_po_roster_20200916_06_DALY", check_po_roster_20200916_06_DALY), ("check_po_roster_20200916_06_WILLIAMS", check_po_roster_20200916_06_WILLIAMS), ("check_po_roster_20200916_06_POWELL", check_po_roster_20200916_06_POWELL), ("check_po_roster_20200916_07_MESTER", check_po_roster_20200916_07_MESTER), ("check_po_roster_20200916_07_BOWMAN", check_po_roster_20200916_07_BOWMAN), ("check_po_roster_20200916_07_BARKIN", check_po_roster_20200916_07_BARKIN), ("check_po_roster_20200916_07_EVANS", check_po_roster_20200916_07_EVANS), ("check_po_roster_20200916_07_HARKER", check_po_roster_20200916_07_HARKER), ("check_po_roster_20200916_08_MESTER", check_po_roster_20200916_08_MESTER), ("check_po_roster_20200916_08_BRAINARD", check_po_roster_20200916_08_BRAINARD), ("check_po_roster_20200916_08_EVANS", check_po_roster_20200916_08_EVANS), ("check_po_roster_20200916_08_ROSENGREN", check_po_roster_20200916_08_ROSENGREN), ("check_po_roster_20200916_08_WILLIAMS", check_po_roster_20200916_08_WILLIAMS), ("check_po_roster_20200916_08_GEORGE", check_po_roster_20200916_08_GEORGE), ("check_po_roster_20200916_08_POWELL", check_po_roster_20200916_08_POWELL), ("check_po_counter_20200916_08_KASHKARI", check_po_counter_20200916_08_KASHKARI), ("check_po_counter_20200916_08_GEORGE", check_po_counter_20200916_08_GEORGE), ("check_po_counter_20200916_08_KAPLAN", check_po_counter_20200916_08_KAPLAN), ("check_po_roster_20200916_09_MESTER", check_po_roster_20200916_09_MESTER), ("check_po_roster_20200916_09_ROSENGREN", check_po_roster_20200916_09_ROSENGREN), ("check_po_roster_20200916_10_MESTER", check_po_roster_20200916_10_MESTER), ("check_po_roster_20200916_10_BARKIN", check_po_roster_20200916_10_BARKIN), ("check_po_roster_20200916_10_BRAINARD", check_po_roster_20200916_10_BRAINARD), ("check_po_roster_20200916_10_ROSENGREN", check_po_roster_20200916_10_ROSENGREN), ("check_po_roster_20200916_10_GEORGE", check_po_roster_20200916_10_GEORGE), ("check_po_roster_20200916_10_KAPLAN", check_po_roster_20200916_10_KAPLAN), ("check_po_counter_20200916_10_EVANS", check_po_counter_20200916_10_EVANS), ("check_po_counter_20200916_10_POWELL", check_po_counter_20200916_10_POWELL), ("check_po_roster_20200916_11_MESTER", check_po_roster_20200916_11_MESTER), ("check_po_roster_20200916_11_BRAINARD", check_po_roster_20200916_11_BRAINARD), ("check_po_roster_20200916_11_EVANS", check_po_roster_20200916_11_EVANS), ("check_po_roster_20200916_11_QUARLES", check_po_roster_20200916_11_QUARLES), ("check_po_roster_20200916_11_ROSENGREN", check_po_roster_20200916_11_ROSENGREN), ("check_po_roster_20200916_11_DALY", check_po_roster_20200916_11_DALY), ("check_po_roster_20200916_11_WILLIAMS", check_po_roster_20200916_11_WILLIAMS), ("check_po_roster_20200916_11_GEORGE", check_po_roster_20200916_11_GEORGE), ("check_po_roster_20200916_11_POWELL", check_po_roster_20200916_11_POWELL), ("check_po_counter_20200916_11_BULLARD", check_po_counter_20200916_11_BULLARD), ("check_po_roster_20200916_12_QUARLES", check_po_roster_20200916_12_QUARLES), ("check_po_roster_20200916_12_POWELL", check_po_roster_20200916_12_POWELL), ("check_po_counter_20200916_12_BRAINARD", check_po_counter_20200916_12_BRAINARD), ("check_po_counter_20200916_12_EVANS", check_po_counter_20200916_12_EVANS), ("check_po_counter_20200916_12_ROSENGREN", check_po_counter_20200916_12_ROSENGREN), ("check_po_counter_20200916_12_WILLIAMS", check_po_counter_20200916_12_WILLIAMS), ("check_po_roster_20200916_13_MESTER", check_po_roster_20200916_13_MESTER), ("check_po_roster_20200916_13_BOSTIC", check_po_roster_20200916_13_BOSTIC), ("check_po_roster_20200916_13_BARKIN", check_po_roster_20200916_13_BARKIN), ("check_po_roster_20200916_13_ROSENGREN", check_po_roster_20200916_13_ROSENGREN), ("check_po_roster_20200916_13_EVANS", check_po_roster_20200916_13_EVANS), ("check_po_roster_20200916_13_DALY", check_po_roster_20200916_13_DALY), ("check_po_roster_20200916_13_GEORGE", check_po_roster_20200916_13_GEORGE), ("check_po_roster_20200916_13_KAPLAN", check_po_roster_20200916_13_KAPLAN), ("check_po_roster_20200916_13_HARKER", check_po_roster_20200916_13_HARKER), ("check_po_roster_20200916_14_BULLARD", check_po_roster_20200916_14_BULLARD), ("check_po_roster_20200916_14_BOWMAN", check_po_roster_20200916_14_BOWMAN), ("check_po_roster_20200916_14_CLARIDA", check_po_roster_20200916_14_CLARIDA), ("check_po_roster_20200916_14_BRAINARD", check_po_roster_20200916_14_BRAINARD), ("check_po_roster_20200916_14_KASHKARI", check_po_roster_20200916_14_KASHKARI), ("check_po_roster_20200916_14_QUARLES", check_po_roster_20200916_14_QUARLES), ("check_po_roster_20200916_14_EVANS", check_po_roster_20200916_14_EVANS), ("check_po_roster_20200916_14_DALY", check_po_roster_20200916_14_DALY), ("check_po_roster_20200916_14_WILLIAMS", check_po_roster_20200916_14_WILLIAMS), ("check_po_roster_20200916_14_GEORGE", check_po_roster_20200916_14_GEORGE), ("check_po_roster_20200916_14_POWELL", check_po_roster_20200916_14_POWELL), ("check_po_roster_20200916_14_HARKER", check_po_roster_20200916_14_HARKER), ("check_po_counter_20200916_14_MESTER", check_po_counter_20200916_14_MESTER), ("check_po_counter_20200916_14_BOSTIC", check_po_counter_20200916_14_BOSTIC), ("check_po_counter_20200916_14_BARKIN", check_po_counter_20200916_14_BARKIN), ("check_po_counter_20200916_14_ROSENGREN", check_po_counter_20200916_14_ROSENGREN), ("check_po_counter_20200916_14_GEORGE", check_po_counter_20200916_14_GEORGE), ("check_po_counter_20200916_14_KAPLAN", check_po_counter_20200916_14_KAPLAN), ("check_po_roster_20200916_15_KASHKARI", check_po_roster_20200916_15_KASHKARI), ("check_po_roster_20200916_15_EVANS", check_po_roster_20200916_15_EVANS), ("check_po_counter_20200916_15_MESTER", check_po_counter_20200916_15_MESTER), ("check_po_counter_20200916_15_BOWMAN", check_po_counter_20200916_15_BOWMAN), ("check_po_counter_20200916_15_BOSTIC", check_po_counter_20200916_15_BOSTIC), ("check_po_counter_20200916_15_BARKIN", check_po_counter_20200916_15_BARKIN), ("check_po_counter_20200916_15_ROSENGREN", check_po_counter_20200916_15_ROSENGREN), ("check_po_counter_20200916_15_QUARLES", check_po_counter_20200916_15_QUARLES), ("check_po_counter_20200916_15_GEORGE", check_po_counter_20200916_15_GEORGE), ("check_po_counter_20200916_15_KAPLAN", check_po_counter_20200916_15_KAPLAN), ("check_po_counter_20200916_15_HARKER", check_po_counter_20200916_15_HARKER), ("check_po_roster_20200916_16_MESTER", check_po_roster_20200916_16_MESTER), ("check_po_roster_20200916_16_BARKIN", check_po_roster_20200916_16_BARKIN), ("check_po_roster_20200916_16_BOSTIC", check_po_roster_20200916_16_BOSTIC), ("check_po_roster_20200916_16_ROSENGREN", check_po_roster_20200916_16_ROSENGREN), ("check_po_roster_20200916_16_KAPLAN", check_po_roster_20200916_16_KAPLAN), ("check_po_counter_20200916_16_BOWMAN", check_po_counter_20200916_16_BOWMAN), ("check_po_counter_20200916_16_BRAINARD", check_po_counter_20200916_16_BRAINARD), ("check_po_counter_20200916_16_KASHKARI", check_po_counter_20200916_16_KASHKARI), ("check_po_counter_20200916_16_EVANS", check_po_counter_20200916_16_EVANS), ("check_po_counter_20200916_16_QUARLES", check_po_counter_20200916_16_QUARLES), ("check_po_counter_20200916_16_DALY", check_po_counter_20200916_16_DALY), ("check_po_counter_20200916_16_WILLIAMS", check_po_counter_20200916_16_WILLIAMS), ("check_po_counter_20200916_16_POWELL", check_po_counter_20200916_16_POWELL), ("check_po_roster_20200916_17_CLARIDA", check_po_roster_20200916_17_CLARIDA), ("check_po_roster_20200916_17_BOSTIC", check_po_roster_20200916_17_BOSTIC), ("check_po_roster_20200916_17_BRAINARD", check_po_roster_20200916_17_BRAINARD), ("check_po_roster_20200916_17_DALY", check_po_roster_20200916_17_DALY), ("check_po_roster_20200916_17_WILLIAMS", check_po_roster_20200916_17_WILLIAMS), ("check_po_roster_20200916_17_GEORGE", check_po_roster_20200916_17_GEORGE), ("check_po_roster_20201105_01_QUARLES", check_po_roster_20201105_01_QUARLES), ("check_po_roster_20201105_01_KAPLAN", check_po_roster_20201105_01_KAPLAN), ("check_po_roster_20201105_01_ROSENGREN", check_po_roster_20201105_01_ROSENGREN), ("check_po_roster_20201105_01_BULLARD", check_po_roster_20201105_01_BULLARD), ("check_po_roster_20201105_01_BOWMAN", check_po_roster_20201105_01_BOWMAN), ("check_po_roster_20201105_01_FELDMAN", check_po_roster_20201105_01_FELDMAN), ("check_po_roster_20201105_01_BRAINARD", check_po_roster_20201105_01_BRAINARD), ("check_po_roster_20201105_01_BOSTIC", check_po_roster_20201105_01_BOSTIC), ("check_po_roster_20201105_01_DALY", check_po_roster_20201105_01_DALY), ("check_po_roster_20201105_01_GEORGE", check_po_roster_20201105_01_GEORGE), ("check_po_roster_20201105_01_MESTER", check_po_roster_20201105_01_MESTER), ("check_po_roster_20201105_01_EVANS", check_po_roster_20201105_01_EVANS), ("check_po_roster_20201105_01_CLARIDA", check_po_roster_20201105_01_CLARIDA), ("check_po_counter_20201105_01_QUARLES", check_po_counter_20201105_01_QUARLES), ("check_po_counter_20201105_01_ROSENGREN", check_po_counter_20201105_01_ROSENGREN), ("check_po_counter_20201105_01_POWELL", check_po_counter_20201105_01_POWELL), ("check_po_counter_20201105_01_HARKER", check_po_counter_20201105_01_HARKER), ("check_po_counter_20201105_01_BOSTIC", check_po_counter_20201105_01_BOSTIC), ("check_po_roster_20201105_02_QUARLES", check_po_roster_20201105_02_QUARLES), ("check_po_roster_20201105_02_ROSENGREN", check_po_roster_20201105_02_ROSENGREN), ("check_po_roster_20201105_02_BULLARD", check_po_roster_20201105_02_BULLARD), ("check_po_roster_20201105_02_BRAINARD", check_po_roster_20201105_02_BRAINARD), ("check_po_roster_20201105_02_DALY", check_po_roster_20201105_02_DALY), ("check_po_roster_20201105_02_MESTER", check_po_roster_20201105_02_MESTER), ("check_po_roster_20201105_02_CLARIDA", check_po_roster_20201105_02_CLARIDA), ("check_po_counter_20201105_02_BARKIN", check_po_counter_20201105_02_BARKIN), ("check_po_counter_20201105_02_HARKER", check_po_counter_20201105_02_HARKER), ("check_po_counter_20201105_02_CLARIDA", check_po_counter_20201105_02_CLARIDA), ("check_po_roster_20201105_03_QUARLES", check_po_roster_20201105_03_QUARLES), ("check_po_roster_20201105_03_KAPLAN", check_po_roster_20201105_03_KAPLAN), ("check_po_roster_20201105_03_ROSENGREN", check_po_roster_20201105_03_ROSENGREN), ("check_po_roster_20201105_03_BARKIN", check_po_roster_20201105_03_BARKIN), ("check_po_roster_20201105_03_BULLARD", check_po_roster_20201105_03_BULLARD), ("check_po_roster_20201105_03_BOWMAN", check_po_roster_20201105_03_BOWMAN), ("check_po_roster_20201105_03_BOSTIC", check_po_roster_20201105_03_BOSTIC), ("check_po_roster_20201105_03_HARKER", check_po_roster_20201105_03_HARKER), ("check_po_roster_20201105_03_GEORGE", check_po_roster_20201105_03_GEORGE), ("check_po_roster_20201105_03_MESTER", check_po_roster_20201105_03_MESTER), ("check_po_counter_20201105_03_POWELL", check_po_counter_20201105_03_POWELL), ("check_po_counter_20201105_03_BRAINARD", check_po_counter_20201105_03_BRAINARD), ("check_po_counter_20201105_03_DALY", check_po_counter_20201105_03_DALY), ("check_po_counter_20201105_03_WILLIAMS", check_po_counter_20201105_03_WILLIAMS), ("check_po_counter_20201105_03_EVANS", check_po_counter_20201105_03_EVANS), ("check_po_roster_20201105_04_QUARLES", check_po_roster_20201105_04_QUARLES), ("check_po_roster_20201105_04_KAPLAN", check_po_roster_20201105_04_KAPLAN), ("check_po_roster_20201105_04_ROSENGREN", check_po_roster_20201105_04_ROSENGREN), ("check_po_roster_20201105_04_BOWMAN", check_po_roster_20201105_04_BOWMAN), ("check_po_roster_20201105_04_BRAINARD", check_po_roster_20201105_04_BRAINARD), ("check_po_roster_20201105_04_GEORGE", check_po_roster_20201105_04_GEORGE), ("check_po_counter_20201105_04_QUARLES", check_po_counter_20201105_04_QUARLES), ("check_po_counter_20201105_04_BULLARD", check_po_counter_20201105_04_BULLARD), ("check_po_counter_20201105_04_POWELL", check_po_counter_20201105_04_POWELL), ("check_po_counter_20201105_04_FELDMAN", check_po_counter_20201105_04_FELDMAN), ("check_po_counter_20201105_04_BRAINARD", check_po_counter_20201105_04_BRAINARD), ("check_po_counter_20201105_04_HARKER", check_po_counter_20201105_04_HARKER), ("check_po_counter_20201105_04_BOSTIC", check_po_counter_20201105_04_BOSTIC), ("check_po_counter_20201105_04_WILLIAMS", check_po_counter_20201105_04_WILLIAMS), ("check_po_counter_20201105_04_MESTER", check_po_counter_20201105_04_MESTER), ("check_po_counter_20201105_04_EVANS", check_po_counter_20201105_04_EVANS), ("check_po_counter_20201105_04_CLARIDA", check_po_counter_20201105_04_CLARIDA), ("check_po_roster_20201105_05_BULLARD", check_po_roster_20201105_05_BULLARD), ("check_po_roster_20201105_05_HARKER", check_po_roster_20201105_05_HARKER), ("check_po_roster_20201105_06_QUARLES", check_po_roster_20201105_06_QUARLES), ("check_po_roster_20201105_06_KAPLAN", check_po_roster_20201105_06_KAPLAN), ("check_po_roster_20201105_06_ROSENGREN", check_po_roster_20201105_06_ROSENGREN), ("check_po_roster_20201105_06_BARKIN", check_po_roster_20201105_06_BARKIN), ("check_po_roster_20201105_06_BULLARD", check_po_roster_20201105_06_BULLARD), ("check_po_roster_20201105_06_POWELL", check_po_roster_20201105_06_POWELL), ("check_po_roster_20201105_06_BOWMAN", check_po_roster_20201105_06_BOWMAN), ("check_po_roster_20201105_06_FELDMAN", check_po_roster_20201105_06_FELDMAN), ("check_po_roster_20201105_06_BRAINARD", check_po_roster_20201105_06_BRAINARD), ("check_po_roster_20201105_06_HARKER", check_po_roster_20201105_06_HARKER), ("check_po_roster_20201105_06_WILLIAMS", check_po_roster_20201105_06_WILLIAMS), ("check_po_roster_20201105_06_DALY", check_po_roster_20201105_06_DALY), ("check_po_roster_20201105_06_GEORGE", check_po_roster_20201105_06_GEORGE), ("check_po_roster_20201105_06_MESTER", check_po_roster_20201105_06_MESTER), ("check_po_roster_20201105_06_EVANS", check_po_roster_20201105_06_EVANS), ("check_po_roster_20201105_06_CLARIDA", check_po_roster_20201105_06_CLARIDA), ("check_po_counter_20201105_06_GEORGE", check_po_counter_20201105_06_GEORGE), ("check_po_roster_20201105_07_QUARLES", check_po_roster_20201105_07_QUARLES), ("check_po_roster_20201105_07_KAPLAN", check_po_roster_20201105_07_KAPLAN), ("check_po_roster_20201105_07_ROSENGREN", check_po_roster_20201105_07_ROSENGREN), ("check_po_roster_20201105_07_BARKIN", check_po_roster_20201105_07_BARKIN), ("check_po_roster_20201105_07_BULLARD", check_po_roster_20201105_07_BULLARD), ("check_po_roster_20201105_07_BOSTIC", check_po_roster_20201105_07_BOSTIC), ("check_po_roster_20201105_07_HARKER", check_po_roster_20201105_07_HARKER), ("check_po_counter_20201105_07_POWELL", check_po_counter_20201105_07_POWELL), ("check_po_counter_20201105_07_BOWMAN", check_po_counter_20201105_07_BOWMAN), ("check_po_counter_20201105_07_BRAINARD", check_po_counter_20201105_07_BRAINARD), ("check_po_counter_20201105_07_DALY", check_po_counter_20201105_07_DALY), ("check_po_counter_20201105_07_WILLIAMS", check_po_counter_20201105_07_WILLIAMS), ("check_po_counter_20201105_07_MESTER", check_po_counter_20201105_07_MESTER), ("check_po_counter_20201105_07_EVANS", check_po_counter_20201105_07_EVANS), ("check_po_roster_20201105_08_QUARLES", check_po_roster_20201105_08_QUARLES), ("check_po_roster_20201105_08_BOWMAN", check_po_roster_20201105_08_BOWMAN), ("check_po_roster_20201105_08_FELDMAN", check_po_roster_20201105_08_FELDMAN), ("check_po_roster_20201105_08_POWELL", check_po_roster_20201105_08_POWELL), ("check_po_roster_20201105_08_BRAINARD", check_po_roster_20201105_08_BRAINARD), ("check_po_roster_20201105_08_DALY", check_po_roster_20201105_08_DALY), ("check_po_roster_20201105_08_EVANS", check_po_roster_20201105_08_EVANS), ("check_po_roster_20201105_08_CLARIDA", check_po_roster_20201105_08_CLARIDA), ("check_po_counter_20201105_08_KAPLAN", check_po_counter_20201105_08_KAPLAN), ("check_po_counter_20201105_08_MESTER", check_po_counter_20201105_08_MESTER), ("check_po_roster_20201105_09_KAPLAN", check_po_roster_20201105_09_KAPLAN), ("check_po_roster_20201105_09_POWELL", check_po_roster_20201105_09_POWELL), ("check_po_roster_20201105_09_EVANS", check_po_roster_20201105_09_EVANS), ("check_po_counter_20201105_09_HARKER", check_po_counter_20201105_09_HARKER), ("check_po_roster_20201105_10_QUARLES", check_po_roster_20201105_10_QUARLES), ("check_po_roster_20201105_10_ROSENGREN", check_po_roster_20201105_10_ROSENGREN), ("check_po_roster_20201105_10_BOWMAN", check_po_roster_20201105_10_BOWMAN), ("check_po_roster_20201105_10_BULLARD", check_po_roster_20201105_10_BULLARD), ("check_po_roster_20201105_10_HARKER", check_po_roster_20201105_10_HARKER), ("check_po_roster_20201105_10_GEORGE", check_po_roster_20201105_10_GEORGE), ("check_po_counter_20201105_10_POWELL", check_po_counter_20201105_10_POWELL), ("check_po_counter_20201105_10_WILLIAMS", check_po_counter_20201105_10_WILLIAMS), ("check_po_counter_20201105_10_EVANS", check_po_counter_20201105_10_EVANS), ("check_po_roster_20201105_11_KAPLAN", check_po_roster_20201105_11_KAPLAN), ("check_po_roster_20201105_11_ROSENGREN", check_po_roster_20201105_11_ROSENGREN), ("check_po_roster_20201105_11_BULLARD", check_po_roster_20201105_11_BULLARD), ("check_po_roster_20201105_11_POWELL", check_po_roster_20201105_11_POWELL), ("check_po_roster_20201105_11_FELDMAN", check_po_roster_20201105_11_FELDMAN), ("check_po_roster_20201105_11_BRAINARD", check_po_roster_20201105_11_BRAINARD), ("check_po_roster_20201105_11_BOSTIC", check_po_roster_20201105_11_BOSTIC), ("check_po_roster_20201105_11_HARKER", check_po_roster_20201105_11_HARKER), ("check_po_roster_20201105_11_WILLIAMS", check_po_roster_20201105_11_WILLIAMS), ("check_po_roster_20201105_11_EVANS", check_po_roster_20201105_11_EVANS), ("check_po_roster_20201105_11_CLARIDA", check_po_roster_20201105_11_CLARIDA), ("check_po_counter_20201105_11_QUARLES", check_po_counter_20201105_11_QUARLES), ("check_po_counter_20201105_11_BARKIN", check_po_counter_20201105_11_BARKIN), ("check_po_counter_20201105_11_DALY", check_po_counter_20201105_11_DALY), ("check_po_counter_20201105_11_CLARIDA", check_po_counter_20201105_11_CLARIDA), ("check_po_roster_20201105_12_QUARLES", check_po_roster_20201105_12_QUARLES), ("check_po_roster_20201105_12_KAPLAN", check_po_roster_20201105_12_KAPLAN), ("check_po_roster_20201105_12_ROSENGREN", check_po_roster_20201105_12_ROSENGREN), ("check_po_roster_20201105_12_FELDMAN", check_po_roster_20201105_12_FELDMAN), ("check_po_roster_20201105_12_BOWMAN", check_po_roster_20201105_12_BOWMAN), ("check_po_roster_20201105_12_BULLARD", check_po_roster_20201105_12_BULLARD), ("check_po_roster_20201105_12_WILLIAMS", check_po_roster_20201105_12_WILLIAMS), ("check_po_roster_20201105_12_DALY", check_po_roster_20201105_12_DALY), ("check_po_roster_20201105_12_EVANS", check_po_roster_20201105_12_EVANS), ("check_po_roster_20201105_12_CLARIDA", check_po_roster_20201105_12_CLARIDA), ("check_po_counter_20201105_12_QUARLES", check_po_counter_20201105_12_QUARLES), ("check_po_counter_20201105_12_EVANS", check_po_counter_20201105_12_EVANS), ("check_po_roster_20201105_13_QUARLES", check_po_roster_20201105_13_QUARLES), ("check_po_roster_20201105_13_BARKIN", check_po_roster_20201105_13_BARKIN), ("check_po_roster_20201105_13_HARKER", check_po_roster_20201105_13_HARKER), ("check_po_roster_20201105_13_MESTER", check_po_roster_20201105_13_MESTER), ("check_po_roster_20201105_13_CLARIDA", check_po_roster_20201105_13_CLARIDA), ("check_po_counter_20201105_13_KAPLAN", check_po_counter_20201105_13_KAPLAN), ("check_po_counter_20201105_13_POWELL", check_po_counter_20201105_13_POWELL), ("check_po_counter_20201105_13_BRAINARD", check_po_counter_20201105_13_BRAINARD), ("check_po_counter_20201105_13_BOSTIC", check_po_counter_20201105_13_BOSTIC), ("check_po_counter_20201105_13_GEORGE", check_po_counter_20201105_13_GEORGE), ("check_po_counter_20201105_13_DALY", check_po_counter_20201105_13_DALY), ("check_po_roster_20201105_14_KAPLAN", check_po_roster_20201105_14_KAPLAN), ("check_po_roster_20201105_14_POWELL", check_po_roster_20201105_14_POWELL), ("check_po_roster_20201105_14_BOWMAN", check_po_roster_20201105_14_BOWMAN), ("check_po_roster_20201105_14_BRAINARD", check_po_roster_20201105_14_BRAINARD), ("check_po_roster_20201105_14_BOSTIC", check_po_roster_20201105_14_BOSTIC), ("check_po_roster_20201105_14_GEORGE", check_po_roster_20201105_14_GEORGE), ("check_po_counter_20201105_14_BARKIN", check_po_counter_20201105_14_BARKIN), ("check_po_counter_20201105_14_BULLARD", check_po_counter_20201105_14_BULLARD), ("check_po_counter_20201105_14_HARKER", check_po_counter_20201105_14_HARKER), ("check_po_counter_20201105_14_CLARIDA", check_po_counter_20201105_14_CLARIDA), ("check_po_roster_20201105_15_QUARLES", check_po_roster_20201105_15_QUARLES), ("check_po_roster_20201105_15_KAPLAN", check_po_roster_20201105_15_KAPLAN), ("check_po_roster_20201105_15_BARKIN", check_po_roster_20201105_15_BARKIN), ("check_po_roster_20201105_15_BULLARD", check_po_roster_20201105_15_BULLARD), ("check_po_roster_20201105_15_BOSTIC", check_po_roster_20201105_15_BOSTIC), ("check_po_roster_20201105_15_HARKER", check_po_roster_20201105_15_HARKER), ("check_po_roster_20201105_15_MESTER", check_po_roster_20201105_15_MESTER), ("check_po_roster_20201105_15_EVANS", check_po_roster_20201105_15_EVANS), ("check_po_counter_20201105_15_MESTER", check_po_counter_20201105_15_MESTER), ("check_po_counter_20201105_15_EVANS", check_po_counter_20201105_15_EVANS), ("check_po_roster_20201105_16_QUARLES", check_po_roster_20201105_16_QUARLES), ("check_po_roster_20201105_16_KAPLAN", check_po_roster_20201105_16_KAPLAN), ("check_po_roster_20201105_16_ROSENGREN", check_po_roster_20201105_16_ROSENGREN), ("check_po_roster_20201105_16_BARKIN", check_po_roster_20201105_16_BARKIN), ("check_po_roster_20201105_16_BRAINARD", check_po_roster_20201105_16_BRAINARD), ("check_po_roster_20201105_16_CLARIDA", check_po_roster_20201105_16_CLARIDA), ("check_po_roster_20201105_17_ROSENGREN", check_po_roster_20201105_17_ROSENGREN), ("check_po_roster_20201105_17_BARKIN", check_po_roster_20201105_17_BARKIN), ("check_po_roster_20201105_17_POWELL", check_po_roster_20201105_17_POWELL), ("check_po_roster_20201105_17_BULLARD", check_po_roster_20201105_17_BULLARD), ("check_po_roster_20201105_17_FELDMAN", check_po_roster_20201105_17_FELDMAN), ("check_po_roster_20201105_17_BRAINARD", check_po_roster_20201105_17_BRAINARD), ("check_po_roster_20201105_17_BOSTIC", check_po_roster_20201105_17_BOSTIC), ("check_po_roster_20201105_17_DALY", check_po_roster_20201105_17_DALY), ("check_po_roster_20201105_17_GEORGE", check_po_roster_20201105_17_GEORGE), ("check_po_roster_20201105_17_MESTER", check_po_roster_20201105_17_MESTER), ("check_po_counter_20201105_17_QUARLES", check_po_counter_20201105_17_QUARLES), ("check_po_roster_20201105_18_QUARLES", check_po_roster_20201105_18_QUARLES), ("check_po_roster_20201105_18_ROSENGREN", check_po_roster_20201105_18_ROSENGREN), ("check_po_roster_20201105_18_BULLARD", check_po_roster_20201105_18_BULLARD), ("check_po_roster_20201105_18_BRAINARD", check_po_roster_20201105_18_BRAINARD), ("check_po_roster_20201105_18_WILLIAMS", check_po_roster_20201105_18_WILLIAMS), ("check_po_roster_20201105_18_DALY", check_po_roster_20201105_18_DALY), ("check_po_roster_20201105_19_KAPLAN", check_po_roster_20201105_19_KAPLAN), ("check_po_roster_20201105_19_ROSENGREN", check_po_roster_20201105_19_ROSENGREN), ("check_po_roster_20201105_19_BRAINARD", check_po_roster_20201105_19_BRAINARD), ("check_po_counter_20201105_19_DALY", check_po_counter_20201105_19_DALY), ("check_po_roster_20201105_20_QUARLES", check_po_roster_20201105_20_QUARLES), ("check_po_roster_20201105_20_KAPLAN", check_po_roster_20201105_20_KAPLAN), ("check_po_roster_20201105_20_BARKIN", check_po_roster_20201105_20_BARKIN), ("check_po_roster_20201105_20_BRAINARD", check_po_roster_20201105_20_BRAINARD), ("check_po_roster_20201105_20_BOSTIC", check_po_roster_20201105_20_BOSTIC), ("check_po_roster_20201105_20_WILLIAMS", check_po_roster_20201105_20_WILLIAMS), ("check_po_roster_20201105_20_GEORGE", check_po_roster_20201105_20_GEORGE), ("check_po_roster_20201105_20_MESTER", check_po_roster_20201105_20_MESTER), ("check_po_counter_20201105_20_EVANS", check_po_counter_20201105_20_EVANS), ("check_po_roster_20201105_21_QUARLES", check_po_roster_20201105_21_QUARLES), ("check_po_roster_20201105_21_KAPLAN", check_po_roster_20201105_21_KAPLAN), ("check_po_roster_20201105_21_BRAINARD", check_po_roster_20201105_21_BRAINARD), ("check_po_roster_20201105_21_BOSTIC", check_po_roster_20201105_21_BOSTIC), ("check_po_roster_20201105_21_EVANS", check_po_roster_20201105_21_EVANS), ("check_po_roster_20201105_22_QUARLES", check_po_roster_20201105_22_QUARLES), ("check_po_roster_20201105_22_KAPLAN", check_po_roster_20201105_22_KAPLAN), ("check_po_roster_20201105_22_BARKIN", check_po_roster_20201105_22_BARKIN), ("check_po_roster_20201105_22_POWELL", check_po_roster_20201105_22_POWELL), ("check_po_roster_20201105_22_FELDMAN", check_po_roster_20201105_22_FELDMAN), ("check_po_roster_20201105_22_BOWMAN", check_po_roster_20201105_22_BOWMAN), ("check_po_roster_20201105_22_BRAINARD", check_po_roster_20201105_22_BRAINARD), ("check_po_roster_20201105_22_BOSTIC", check_po_roster_20201105_22_BOSTIC), ("check_po_roster_20201105_22_WILLIAMS", check_po_roster_20201105_22_WILLIAMS), ("check_po_roster_20201105_22_GEORGE", check_po_roster_20201105_22_GEORGE), ("check_po_roster_20201105_22_DALY", check_po_roster_20201105_22_DALY), ("check_po_roster_20201105_22_MESTER", check_po_roster_20201105_22_MESTER), ("check_po_roster_20201105_22_EVANS", check_po_roster_20201105_22_EVANS), ("check_po_roster_20201105_22_CLARIDA", check_po_roster_20201105_22_CLARIDA), ("check_po_counter_20201105_22_BULLARD", check_po_counter_20201105_22_BULLARD), ("check_po_counter_20201105_22_CLARIDA", check_po_counter_20201105_22_CLARIDA), ("check_po_roster_20201105_23_QUARLES", check_po_roster_20201105_23_QUARLES), ("check_po_roster_20201105_23_ROSENGREN", check_po_roster_20201105_23_ROSENGREN), ("check_po_roster_20201105_23_BULLARD", check_po_roster_20201105_23_BULLARD), ("check_po_roster_20201105_23_POWELL", check_po_roster_20201105_23_POWELL), ("check_po_roster_20201105_23_FELDMAN", check_po_roster_20201105_23_FELDMAN), ("check_po_roster_20201105_23_BRAINARD", check_po_roster_20201105_23_BRAINARD), ("check_po_roster_20201105_23_WILLIAMS", check_po_roster_20201105_23_WILLIAMS), ("check_po_roster_20201105_23_GEORGE", check_po_roster_20201105_23_GEORGE), ("check_po_roster_20201105_23_DALY", check_po_roster_20201105_23_DALY), ("check_po_roster_20201105_23_CLARIDA", check_po_roster_20201105_23_CLARIDA), ("check_po_roster_20201105_24_KAPLAN", check_po_roster_20201105_24_KAPLAN), ("check_po_roster_20201105_24_ROSENGREN", check_po_roster_20201105_24_ROSENGREN), ("check_po_roster_20201105_24_BULLARD", check_po_roster_20201105_24_BULLARD), ("check_po_roster_20201105_24_FELDMAN", check_po_roster_20201105_24_FELDMAN), ("check_po_roster_20201105_24_BOSTIC", check_po_roster_20201105_24_BOSTIC), ("check_po_roster_20201105_24_BRAINARD", check_po_roster_20201105_24_BRAINARD), ("check_po_roster_20201105_24_GEORGE", check_po_roster_20201105_24_GEORGE), ("check_po_roster_20201105_24_MESTER", check_po_roster_20201105_24_MESTER), ("check_po_roster_20201105_24_EVANS", check_po_roster_20201105_24_EVANS), ("check_po_counter_20201105_24_KAPLAN", check_po_counter_20201105_24_KAPLAN), ("check_po_counter_20201105_24_BULLARD", check_po_counter_20201105_24_BULLARD), ("check_po_counter_20201105_24_DALY", check_po_counter_20201105_24_DALY), ("check_po_roster_20201105_25_QUARLES", check_po_roster_20201105_25_QUARLES), ("check_po_roster_20201105_25_KAPLAN", check_po_roster_20201105_25_KAPLAN), ("check_po_roster_20201105_25_ROSENGREN", check_po_roster_20201105_25_ROSENGREN), ("check_po_roster_20201105_25_BARKIN", check_po_roster_20201105_25_BARKIN), ("check_po_roster_20201105_25_BOWMAN", check_po_roster_20201105_25_BOWMAN), ("check_po_roster_20201105_25_FELDMAN", check_po_roster_20201105_25_FELDMAN), ("check_po_roster_20201105_25_BRAINARD", check_po_roster_20201105_25_BRAINARD), ("check_po_roster_20201105_25_BOSTIC", check_po_roster_20201105_25_BOSTIC), ("check_po_roster_20201105_25_HARKER", check_po_roster_20201105_25_HARKER), ("check_po_roster_20201105_25_GEORGE", check_po_roster_20201105_25_GEORGE), ("check_po_roster_20201105_25_DALY", check_po_roster_20201105_25_DALY), ("check_po_roster_20201105_25_WILLIAMS", check_po_roster_20201105_25_WILLIAMS), ("check_po_roster_20201105_25_MESTER", check_po_roster_20201105_25_MESTER), ("check_po_roster_20201105_26_QUARLES", check_po_roster_20201105_26_QUARLES), ("check_po_roster_20201105_26_BOWMAN", check_po_roster_20201105_26_BOWMAN), ("check_po_roster_20201105_26_DALY", check_po_roster_20201105_26_DALY), ("check_po_roster_20201105_26_MESTER", check_po_roster_20201105_26_MESTER), ("check_po_counter_20201105_26_FELDMAN", check_po_counter_20201105_26_FELDMAN), ("check_po_counter_20201105_26_GEORGE", check_po_counter_20201105_26_GEORGE), ("check_po_roster_20201105_27_ROSENGREN", check_po_roster_20201105_27_ROSENGREN), ("check_po_roster_20201105_27_FELDMAN", check_po_roster_20201105_27_FELDMAN), ("check_po_roster_20201105_27_BRAINARD", check_po_roster_20201105_27_BRAINARD), ("check_po_roster_20201105_27_GEORGE", check_po_roster_20201105_27_GEORGE), ("check_po_roster_20201105_27_MESTER", check_po_roster_20201105_27_MESTER), ("check_po_counter_20201105_27_QUARLES", check_po_counter_20201105_27_QUARLES), ("check_po_roster_20201105_28_QUARLES", check_po_roster_20201105_28_QUARLES), ("check_po_roster_20201105_28_KAPLAN", check_po_roster_20201105_28_KAPLAN), ("check_po_roster_20201105_28_BRAINARD", check_po_roster_20201105_28_BRAINARD), ("check_po_roster_20201105_28_GEORGE", check_po_roster_20201105_28_GEORGE), ("check_po_roster_20201105_28_MESTER", check_po_roster_20201105_28_MESTER), ("check_po_roster_20201105_29_ROSENGREN", check_po_roster_20201105_29_ROSENGREN), ("check_po_roster_20201105_29_BARKIN", check_po_roster_20201105_29_BARKIN), ("check_po_roster_20201105_29_BOWMAN", check_po_roster_20201105_29_BOWMAN), ("check_po_counter_20201105_29_QUARLES", check_po_counter_20201105_29_QUARLES), ("check_po_counter_20201105_29_DALY", check_po_counter_20201105_29_DALY), ("check_po_counter_20201105_29_EVANS", check_po_counter_20201105_29_EVANS), ("check_po_roster_20201105_30_BRAINARD", check_po_roster_20201105_30_BRAINARD), ("check_po_roster_20201105_30_DALY", check_po_roster_20201105_30_DALY), ("check_po_roster_20201105_30_MESTER", check_po_roster_20201105_30_MESTER), ("check_po_roster_20201105_31_QUARLES", check_po_roster_20201105_31_QUARLES), ("check_po_roster_20201105_31_BULLARD", check_po_roster_20201105_31_BULLARD), ("check_po_roster_20201105_31_FELDMAN", check_po_roster_20201105_31_FELDMAN), ("check_po_roster_20201105_31_DALY", check_po_roster_20201105_31_DALY), ("check_po_roster_20201105_31_MESTER", check_po_roster_20201105_31_MESTER), ("check_po_counter_20201105_31_ROSENGREN", check_po_counter_20201105_31_ROSENGREN), ("check_po_counter_20201105_31_BARKIN", check_po_counter_20201105_31_BARKIN), ("check_po_counter_20201105_31_BOWMAN", check_po_counter_20201105_31_BOWMAN), ("check_po_counter_20201105_31_BOSTIC", check_po_counter_20201105_31_BOSTIC), ("check_po_counter_20201105_31_HARKER", check_po_counter_20201105_31_HARKER), ("check_po_roster_20201105_32_KAPLAN", check_po_roster_20201105_32_KAPLAN), ("check_po_roster_20201105_32_ROSENGREN", check_po_roster_20201105_32_ROSENGREN), ("check_po_roster_20201105_32_BULLARD", check_po_roster_20201105_32_BULLARD), ("check_po_roster_20201105_32_POWELL", check_po_roster_20201105_32_POWELL), ("check_po_roster_20201105_32_BRAINARD", check_po_roster_20201105_32_BRAINARD), ("check_po_roster_20201105_32_WILLIAMS", check_po_roster_20201105_32_WILLIAMS), ("check_po_roster_20201105_33_ROSENGREN", check_po_roster_20201105_33_ROSENGREN), ("check_po_roster_20201105_33_POWELL", check_po_roster_20201105_33_POWELL), ("check_po_roster_20201105_33_FELDMAN", check_po_roster_20201105_33_FELDMAN), ("check_po_roster_20201105_33_BRAINARD", check_po_roster_20201105_33_BRAINARD), ("check_po_roster_20201105_33_WILLIAMS", check_po_roster_20201105_33_WILLIAMS), ("check_po_roster_20201105_34_QUARLES", check_po_roster_20201105_34_QUARLES), ("check_po_roster_20201105_34_BARKIN", check_po_roster_20201105_34_BARKIN), ("check_po_roster_20201105_34_BRAINARD", check_po_roster_20201105_34_BRAINARD), ("check_po_roster_20201105_34_HARKER", check_po_roster_20201105_34_HARKER), ("check_po_roster_20201105_34_WILLIAMS", check_po_roster_20201105_34_WILLIAMS), ("check_po_roster_20201105_34_DALY", check_po_roster_20201105_34_DALY), ("check_po_roster_20201105_34_CLARIDA", check_po_roster_20201105_34_CLARIDA), ("check_po_counter_20201105_34_BULLARD", check_po_counter_20201105_34_BULLARD), ("check_po_counter_20201105_34_EVANS", check_po_counter_20201105_34_EVANS), ("check_po_roster_20201105_35_KAPLAN", check_po_roster_20201105_35_KAPLAN), ("check_po_roster_20201105_35_BARKIN", check_po_roster_20201105_35_BARKIN), ("check_po_roster_20201105_35_POWELL", check_po_roster_20201105_35_POWELL), ("check_po_roster_20201105_35_BOWMAN", check_po_roster_20201105_35_BOWMAN), ("check_po_roster_20201105_35_FELDMAN", check_po_roster_20201105_35_FELDMAN), ("check_po_roster_20201105_35_BRAINARD", check_po_roster_20201105_35_BRAINARD), ("check_po_roster_20201105_35_BOSTIC", check_po_roster_20201105_35_BOSTIC), ("check_po_roster_20201105_35_WILLIAMS", check_po_roster_20201105_35_WILLIAMS), ("check_po_roster_20201105_35_DALY", check_po_roster_20201105_35_DALY), ("check_po_roster_20201105_35_GEORGE", check_po_roster_20201105_35_GEORGE), ("check_po_roster_20201105_35_MESTER", check_po_roster_20201105_35_MESTER), ("check_po_counter_20201105_35_QUARLES", check_po_counter_20201105_35_QUARLES), ("check_po_counter_20201105_35_ROSENGREN", check_po_counter_20201105_35_ROSENGREN), ("check_po_counter_20201105_35_BULLARD", check_po_counter_20201105_35_BULLARD), ("check_po_counter_20201105_35_HARKER", check_po_counter_20201105_35_HARKER), ("check_po_counter_20201105_35_DALY", check_po_counter_20201105_35_DALY), ("check_po_counter_20201105_35_EVANS", check_po_counter_20201105_35_EVANS), ("check_po_counter_20201105_35_CLARIDA", check_po_counter_20201105_35_CLARIDA), ("check_po_roster_20201105_36_KAPLAN", check_po_roster_20201105_36_KAPLAN), ("check_po_roster_20201105_36_POWELL", check_po_roster_20201105_36_POWELL), ("check_po_roster_20201105_36_BOWMAN", check_po_roster_20201105_36_BOWMAN), ("check_po_roster_20201105_36_BULLARD", check_po_roster_20201105_36_BULLARD), ("check_po_roster_20201105_36_FELDMAN", check_po_roster_20201105_36_FELDMAN), ("check_po_roster_20201105_36_BRAINARD", check_po_roster_20201105_36_BRAINARD), ("check_po_roster_20201105_36_DALY", check_po_roster_20201105_36_DALY), ("check_po_roster_20201105_36_WILLIAMS", check_po_roster_20201105_36_WILLIAMS), ("check_po_roster_20201105_36_GEORGE", check_po_roster_20201105_36_GEORGE), ("check_po_roster_20201105_36_MESTER", check_po_roster_20201105_36_MESTER), ("check_po_roster_20201105_36_EVANS", check_po_roster_20201105_36_EVANS), ("check_po_counter_20201105_36_BARKIN", check_po_counter_20201105_36_BARKIN), ("check_po_counter_20201105_36_QUARLES", check_po_counter_20201105_36_QUARLES), ("check_po_counter_20201105_36_BULLARD", check_po_counter_20201105_36_BULLARD), ("check_po_counter_20201105_36_BOSTIC", check_po_counter_20201105_36_BOSTIC), ("check_po_counter_20201105_36_HARKER", check_po_counter_20201105_36_HARKER), ("check_po_counter_20201105_36_CLARIDA", check_po_counter_20201105_36_CLARIDA), ("check_po_roster_20201105_37_QUARLES", check_po_roster_20201105_37_QUARLES), ("check_po_roster_20201105_37_KAPLAN", check_po_roster_20201105_37_KAPLAN), ("check_po_roster_20201105_37_ROSENGREN", check_po_roster_20201105_37_ROSENGREN), ("check_po_roster_20201105_37_BARKIN", check_po_roster_20201105_37_BARKIN), ("check_po_roster_20201105_37_POWELL", check_po_roster_20201105_37_POWELL), ("check_po_roster_20201105_37_BULLARD", check_po_roster_20201105_37_BULLARD), ("check_po_roster_20201105_37_BOWMAN", check_po_roster_20201105_37_BOWMAN), ("check_po_roster_20201105_37_FELDMAN", check_po_roster_20201105_37_FELDMAN), ("check_po_roster_20201105_37_BRAINARD", check_po_roster_20201105_37_BRAINARD), ("check_po_roster_20201105_37_HARKER", check_po_roster_20201105_37_HARKER), ("check_po_roster_20201105_37_WILLIAMS", check_po_roster_20201105_37_WILLIAMS), ("check_po_roster_20201105_37_DALY", check_po_roster_20201105_37_DALY), ("check_po_roster_20201105_37_MESTER", check_po_roster_20201105_37_MESTER), ("check_po_roster_20201105_37_EVANS", check_po_roster_20201105_37_EVANS), ("check_po_roster_20201105_37_CLARIDA", check_po_roster_20201105_37_CLARIDA), ("check_po_counter_20201105_37_BOSTIC", check_po_counter_20201105_37_BOSTIC), ("check_po_counter_20201105_37_HARKER", check_po_counter_20201105_37_HARKER), ("check_po_counter_20201105_37_GEORGE", check_po_counter_20201105_37_GEORGE), ("check_po_roster_20201105_38_QUARLES", check_po_roster_20201105_38_QUARLES), ("check_po_roster_20201105_38_BARKIN", check_po_roster_20201105_38_BARKIN), ("check_po_roster_20201105_38_ROSENGREN", check_po_roster_20201105_38_ROSENGREN), ("check_po_roster_20201105_38_BULLARD", check_po_roster_20201105_38_BULLARD), ("check_po_roster_20201105_38_BOSTIC", check_po_roster_20201105_38_BOSTIC), ("check_po_roster_20201105_38_HARKER", check_po_roster_20201105_38_HARKER), ("check_po_roster_20201105_38_CLARIDA", check_po_roster_20201105_38_CLARIDA), ("check_po_counter_20201105_38_POWELL", check_po_counter_20201105_38_POWELL), ("check_po_counter_20201105_38_BOWMAN", check_po_counter_20201105_38_BOWMAN), ("check_po_counter_20201105_38_BRAINARD", check_po_counter_20201105_38_BRAINARD), ("check_po_counter_20201105_38_DALY", check_po_counter_20201105_38_DALY), ("check_po_counter_20201105_38_WILLIAMS", check_po_counter_20201105_38_WILLIAMS), ("check_po_counter_20201105_38_MESTER", check_po_counter_20201105_38_MESTER), ("check_po_counter_20201105_38_EVANS", check_po_counter_20201105_38_EVANS), ("check_po_roster_20201105_39_KAPLAN", check_po_roster_20201105_39_KAPLAN), ("check_po_roster_20201105_39_ROSENGREN", check_po_roster_20201105_39_ROSENGREN), ("check_po_roster_20201105_39_BOWMAN", check_po_roster_20201105_39_BOWMAN), ("check_po_roster_20201105_39_POWELL", check_po_roster_20201105_39_POWELL), ("check_po_roster_20201105_39_GEORGE", check_po_roster_20201105_39_GEORGE), ("check_po_roster_20201105_39_DALY", check_po_roster_20201105_39_DALY), ("check_po_roster_20201105_39_CLARIDA", check_po_roster_20201105_39_CLARIDA), ("check_po_roster_20201105_39_MESTER", check_po_roster_20201105_39_MESTER), ("check_po_counter_20201105_39_BARKIN", check_po_counter_20201105_39_BARKIN), ("check_po_counter_20201105_39_BOWMAN", check_po_counter_20201105_39_BOWMAN), ("check_po_roster_20201105_40_BARKIN", check_po_roster_20201105_40_BARKIN), ("check_po_roster_20201105_40_BULLARD", check_po_roster_20201105_40_BULLARD), ("check_po_roster_20201105_40_DALY", check_po_roster_20201105_40_DALY), ("check_po_roster_20201105_40_GEORGE", check_po_roster_20201105_40_GEORGE), ("check_po_roster_20201105_40_WILLIAMS", check_po_roster_20201105_40_WILLIAMS), ("check_po_roster_20201105_40_CLARIDA", check_po_roster_20201105_40_CLARIDA), ("check_po_roster_20201105_40_MESTER", check_po_roster_20201105_40_MESTER), ("check_po_roster_20201216_01_POWELL", check_po_roster_20201216_01_POWELL), ("check_po_roster_20201216_01_BRAINARD", check_po_roster_20201216_01_BRAINARD), ("check_po_roster_20201216_01_HARKER", check_po_roster_20201216_01_HARKER), ("check_po_roster_20201216_01_QUARLES", check_po_roster_20201216_01_QUARLES), ("check_po_roster_20201216_01_ROSENGREN", check_po_roster_20201216_01_ROSENGREN), ("check_po_roster_20201216_01_GEORGE", check_po_roster_20201216_01_GEORGE), ("check_po_roster_20201216_01_WILLIAMS", check_po_roster_20201216_01_WILLIAMS), ("check_po_roster_20201216_01_BOWMAN", check_po_roster_20201216_01_BOWMAN), ("check_po_counter_20201216_01_BARKIN", check_po_counter_20201216_01_BARKIN), ("check_po_counter_20201216_01_HARKER", check_po_counter_20201216_01_HARKER), ("check_po_counter_20201216_01_BULLARD", check_po_counter_20201216_01_BULLARD), ("check_po_roster_20201216_02_POWELL", check_po_roster_20201216_02_POWELL), ("check_po_roster_20201216_02_BRAINARD", check_po_roster_20201216_02_BRAINARD), ("check_po_roster_20201216_02_KAPLAN", check_po_roster_20201216_02_KAPLAN), ("check_po_roster_20201216_02_BARKIN", check_po_roster_20201216_02_BARKIN), ("check_po_roster_20201216_02_MESTER", check_po_roster_20201216_02_MESTER), ("check_po_roster_20201216_02_KASHKARI", check_po_roster_20201216_02_KASHKARI), ("check_po_roster_20201216_02_EVANS", check_po_roster_20201216_02_EVANS), ("check_po_roster_20201216_02_BOSTIC", check_po_roster_20201216_02_BOSTIC), ("check_po_roster_20201216_02_GEORGE", check_po_roster_20201216_02_GEORGE), ("check_po_roster_20201216_02_DALY", check_po_roster_20201216_02_DALY), ("check_po_roster_20201216_02_BOWMAN", check_po_roster_20201216_02_BOWMAN), ("check_po_counter_20201216_02_QUARLES", check_po_counter_20201216_02_QUARLES), ("check_po_roster_20201216_03_BARKIN", check_po_roster_20201216_03_BARKIN), ("check_po_roster_20201216_03_GEORGE", check_po_roster_20201216_03_GEORGE), ("check_po_roster_20201216_04_BRAINARD", check_po_roster_20201216_04_BRAINARD), ("check_po_roster_20201216_04_KAPLAN", check_po_roster_20201216_04_KAPLAN), ("check_po_roster_20201216_04_MESTER", check_po_roster_20201216_04_MESTER), ("check_po_roster_20201216_04_QUARLES", check_po_roster_20201216_04_QUARLES), ("check_po_roster_20201216_04_EVANS", check_po_roster_20201216_04_EVANS), ("check_po_roster_20201216_04_BOSTIC", check_po_roster_20201216_04_BOSTIC), ("check_po_roster_20201216_04_GEORGE", check_po_roster_20201216_04_GEORGE), ("check_po_roster_20201216_04_DALY", check_po_roster_20201216_04_DALY), ("check_po_roster_20201216_04_BOWMAN", check_po_roster_20201216_04_BOWMAN), ("check_po_roster_20201216_05_BRAINARD", check_po_roster_20201216_05_BRAINARD), ("check_po_roster_20201216_05_BARKIN", check_po_roster_20201216_05_BARKIN), ("check_po_roster_20201216_05_POWELL", check_po_roster_20201216_05_POWELL), ("check_po_roster_20201216_05_CLARIDA", check_po_roster_20201216_05_CLARIDA), ("check_po_roster_20201216_05_QUARLES", check_po_roster_20201216_05_QUARLES), ("check_po_roster_20201216_06_KAPLAN", check_po_roster_20201216_06_KAPLAN), ("check_po_roster_20201216_06_POWELL", check_po_roster_20201216_06_POWELL), ("check_po_roster_20201216_06_BARKIN", check_po_roster_20201216_06_BARKIN), ("check_po_roster_20201216_06_MESTER", check_po_roster_20201216_06_MESTER), ("check_po_roster_20201216_06_ROSENGREN", check_po_roster_20201216_06_ROSENGREN), ("check_po_roster_20201216_06_EVANS", check_po_roster_20201216_06_EVANS), ("check_po_roster_20201216_06_BOSTIC", check_po_roster_20201216_06_BOSTIC), ("check_po_roster_20201216_06_GEORGE", check_po_roster_20201216_06_GEORGE), ("check_po_roster_20201216_06_DALY", check_po_roster_20201216_06_DALY), ("check_po_roster_20201216_06_WILLIAMS", check_po_roster_20201216_06_WILLIAMS), ("check_po_counter_20201216_06_BULLARD", check_po_counter_20201216_06_BULLARD), ("check_po_counter_20201216_06_DALY", check_po_counter_20201216_06_DALY), ("check_po_roster_20201216_07_BARKIN", check_po_roster_20201216_07_BARKIN), ("check_po_roster_20201216_07_KAPLAN", check_po_roster_20201216_07_KAPLAN), ("check_po_roster_20201216_07_CLARIDA", check_po_roster_20201216_07_CLARIDA), ("check_po_roster_20201216_07_ROSENGREN", check_po_roster_20201216_07_ROSENGREN), ("check_po_roster_20201216_07_BOSTIC", check_po_roster_20201216_07_BOSTIC), ("check_po_roster_20201216_07_DALY", check_po_roster_20201216_07_DALY), ("check_po_counter_20201216_07_BULLARD", check_po_counter_20201216_07_BULLARD), ("check_po_counter_20201216_07_WILLIAMS", check_po_counter_20201216_07_WILLIAMS), ("check_po_roster_20201216_08_KAPLAN", check_po_roster_20201216_08_KAPLAN), ("check_po_roster_20201216_08_BRAINARD", check_po_roster_20201216_08_BRAINARD), ("check_po_roster_20201216_08_MESTER", check_po_roster_20201216_08_MESTER), ("check_po_roster_20201216_08_GEORGE", check_po_roster_20201216_08_GEORGE), ("check_po_counter_20201216_08_CLARIDA", check_po_counter_20201216_08_CLARIDA), ("check_po_counter_20201216_08_QUARLES", check_po_counter_20201216_08_QUARLES), ("check_po_counter_20201216_08_GEORGE", check_po_counter_20201216_08_GEORGE), ("check_po_counter_20201216_08_BOSTIC", check_po_counter_20201216_08_BOSTIC), ("check_po_roster_20201216_09_BRAINARD", check_po_roster_20201216_09_BRAINARD), ("check_po_roster_20201216_09_BARKIN", check_po_roster_20201216_09_BARKIN), ("check_po_roster_20201216_09_QUARLES", check_po_roster_20201216_09_QUARLES), ("check_po_roster_20201216_09_BULLARD", check_po_roster_20201216_09_BULLARD), ("check_po_roster_20201216_09_WILLIAMS", check_po_roster_20201216_09_WILLIAMS), ("check_po_roster_20201216_10_KAPLAN", check_po_roster_20201216_10_KAPLAN), ("check_po_roster_20201216_10_BRAINARD", check_po_roster_20201216_10_BRAINARD), ("check_po_roster_20201216_10_MESTER", check_po_roster_20201216_10_MESTER), ("check_po_roster_20201216_10_QUARLES", check_po_roster_20201216_10_QUARLES), ("check_po_roster_20201216_10_BOWMAN", check_po_roster_20201216_10_BOWMAN), ("check_po_roster_20201216_11_BARKIN", check_po_roster_20201216_11_BARKIN), ("check_po_roster_20201216_11_ROSENGREN", check_po_roster_20201216_11_ROSENGREN), ("check_po_roster_20201216_11_BOWMAN", check_po_roster_20201216_11_BOWMAN), ("check_po_roster_20201216_12_BRAINARD", check_po_roster_20201216_12_BRAINARD), ("check_po_roster_20201216_12_KAPLAN", check_po_roster_20201216_12_KAPLAN), ("check_po_roster_20201216_12_POWELL", check_po_roster_20201216_12_POWELL), ("check_po_roster_20201216_12_MESTER", check_po_roster_20201216_12_MESTER), ("check_po_roster_20201216_12_ROSENGREN", check_po_roster_20201216_12_ROSENGREN), ("check_po_roster_20201216_12_GEORGE", check_po_roster_20201216_12_GEORGE), ("check_po_counter_20201216_12_QUARLES", check_po_counter_20201216_12_QUARLES), ("check_po_roster_20201216_13_POWELL", check_po_roster_20201216_13_POWELL), ("check_po_roster_20201216_13_BRAINARD", check_po_roster_20201216_13_BRAINARD), ("check_po_roster_20201216_13_BARKIN", check_po_roster_20201216_13_BARKIN), ("check_po_roster_20201216_13_MESTER", check_po_roster_20201216_13_MESTER), ("check_po_roster_20201216_13_CLARIDA", check_po_roster_20201216_13_CLARIDA), ("check_po_roster_20201216_13_HARKER", check_po_roster_20201216_13_HARKER), ("check_po_roster_20201216_13_QUARLES", check_po_roster_20201216_13_QUARLES), ("check_po_roster_20201216_13_BULLARD", check_po_roster_20201216_13_BULLARD), ("check_po_roster_20201216_13_BOSTIC", check_po_roster_20201216_13_BOSTIC), ("check_po_roster_20201216_13_GEORGE", check_po_roster_20201216_13_GEORGE), ("check_po_roster_20201216_13_DALY", check_po_roster_20201216_13_DALY), ("check_po_roster_20201216_13_WILLIAMS", check_po_roster_20201216_13_WILLIAMS), ("check_po_counter_20201216_13_BRAINARD", check_po_counter_20201216_13_BRAINARD), ("check_po_counter_20201216_13_KASHKARI", check_po_counter_20201216_13_KASHKARI), ("check_po_counter_20201216_13_HARKER", check_po_counter_20201216_13_HARKER), ("check_po_counter_20201216_13_EVANS", check_po_counter_20201216_13_EVANS), ("check_po_counter_20201216_13_ROSENGREN", check_po_counter_20201216_13_ROSENGREN), ("check_po_counter_20201216_13_GEORGE", check_po_counter_20201216_13_GEORGE), ("check_po_counter_20201216_13_BOWMAN", check_po_counter_20201216_13_BOWMAN), ("check_po_roster_20201216_14_KAPLAN", check_po_roster_20201216_14_KAPLAN), ("check_po_roster_20201216_14_MESTER", check_po_roster_20201216_14_MESTER), ("check_po_roster_20201216_14_CLARIDA", check_po_roster_20201216_14_CLARIDA), ("check_po_roster_20201216_14_QUARLES", check_po_roster_20201216_14_QUARLES), ("check_po_roster_20201216_14_GEORGE", check_po_roster_20201216_14_GEORGE), ("check_po_roster_20201216_14_BULLARD", check_po_roster_20201216_14_BULLARD), ("check_po_roster_20201216_14_WILLIAMS", check_po_roster_20201216_14_WILLIAMS), ("check_po_counter_20201216_14_BRAINARD", check_po_counter_20201216_14_BRAINARD), ("check_po_counter_20201216_14_POWELL", check_po_counter_20201216_14_POWELL), ("check_po_roster_20201216_15_BARKIN", check_po_roster_20201216_15_BARKIN), ("check_po_roster_20201216_15_BRAINARD", check_po_roster_20201216_15_BRAINARD), ("check_po_roster_20201216_15_POWELL", check_po_roster_20201216_15_POWELL), ("check_po_roster_20201216_15_EVANS", check_po_roster_20201216_15_EVANS), ("check_po_roster_20201216_15_BULLARD", check_po_roster_20201216_15_BULLARD), ("check_po_roster_20201216_15_DALY", check_po_roster_20201216_15_DALY), ("check_po_roster_20201216_15_WILLIAMS", check_po_roster_20201216_15_WILLIAMS), ("check_po_counter_20201216_15_ROSENGREN", check_po_counter_20201216_15_ROSENGREN), ("check_po_counter_20201216_15_GEORGE", check_po_counter_20201216_15_GEORGE), ("check_po_roster_20201216_16_HARKER", check_po_roster_20201216_16_HARKER), ("check_po_roster_20201216_16_QUARLES", check_po_roster_20201216_16_QUARLES), ("check_po_counter_20201216_16_BRAINARD", check_po_counter_20201216_16_BRAINARD), ("check_po_roster_20201216_17_POWELL", check_po_roster_20201216_17_POWELL), ("check_po_roster_20201216_17_BARKIN", check_po_roster_20201216_17_BARKIN), ("check_po_roster_20201216_17_KAPLAN", check_po_roster_20201216_17_KAPLAN), ("check_po_roster_20201216_17_BRAINARD", check_po_roster_20201216_17_BRAINARD), ("check_po_roster_20201216_17_MESTER", check_po_roster_20201216_17_MESTER), ("check_po_roster_20201216_17_CLARIDA", check_po_roster_20201216_17_CLARIDA), ("check_po_roster_20201216_17_QUARLES", check_po_roster_20201216_17_QUARLES), ("check_po_roster_20201216_17_BULLARD", check_po_roster_20201216_17_BULLARD), ("check_po_roster_20201216_17_BOSTIC", check_po_roster_20201216_17_BOSTIC), ("check_po_roster_20201216_17_GEORGE", check_po_roster_20201216_17_GEORGE), ("check_po_roster_20201216_17_BOWMAN", check_po_roster_20201216_17_BOWMAN), ("check_po_roster_20201216_18_POWELL", check_po_roster_20201216_18_POWELL), ("check_po_roster_20201216_18_KAPLAN", check_po_roster_20201216_18_KAPLAN), ("check_po_roster_20201216_18_BARKIN", check_po_roster_20201216_18_BARKIN), ("check_po_roster_20201216_18_MESTER", check_po_roster_20201216_18_MESTER), ("check_po_roster_20201216_18_QUARLES", check_po_roster_20201216_18_QUARLES), ("check_po_roster_20201216_18_BULLARD", check_po_roster_20201216_18_BULLARD), ("check_po_roster_20201216_18_BOWMAN", check_po_roster_20201216_18_BOWMAN), ("check_po_counter_20201216_18_BOSTIC", check_po_counter_20201216_18_BOSTIC), ("check_po_counter_20201216_18_GEORGE", check_po_counter_20201216_18_GEORGE), ("check_po_roster_20201216_19_BRAINARD", check_po_roster_20201216_19_BRAINARD), ("check_po_roster_20201216_19_HARKER", check_po_roster_20201216_19_HARKER), ("check_po_roster_20201216_19_MESTER", check_po_roster_20201216_19_MESTER), ("check_po_roster_20201216_19_KASHKARI", check_po_roster_20201216_19_KASHKARI), ("check_po_roster_20201216_19_QUARLES", check_po_roster_20201216_19_QUARLES), ("check_po_roster_20201216_19_ROSENGREN", check_po_roster_20201216_19_ROSENGREN), ("check_po_roster_20201216_19_DALY", check_po_roster_20201216_19_DALY), ("check_po_roster_20201216_19_BOWMAN", check_po_roster_20201216_19_BOWMAN), ("check_po_counter_20201216_19_QUARLES", check_po_counter_20201216_19_QUARLES), ("check_po_counter_20201216_19_BOSTIC", check_po_counter_20201216_19_BOSTIC), ("check_po_counter_20201216_19_GEORGE", check_po_counter_20201216_19_GEORGE), ("check_po_roster_20201216_20_BRAINARD", check_po_roster_20201216_20_BRAINARD), ("check_po_roster_20201216_20_BARKIN", check_po_roster_20201216_20_BARKIN), ("check_po_roster_20201216_20_POWELL", check_po_roster_20201216_20_POWELL), ("check_po_roster_20201216_20_MESTER", check_po_roster_20201216_20_MESTER), ("check_po_roster_20201216_20_KASHKARI", check_po_roster_20201216_20_KASHKARI), ("check_po_roster_20201216_20_HARKER", check_po_roster_20201216_20_HARKER), ("check_po_roster_20201216_20_QUARLES", check_po_roster_20201216_20_QUARLES), ("check_po_roster_20201216_20_GEORGE", check_po_roster_20201216_20_GEORGE), ("check_po_roster_20201216_20_DALY", check_po_roster_20201216_20_DALY), ("check_po_roster_20201216_20_BOWMAN", check_po_roster_20201216_20_BOWMAN), ("check_po_counter_20201216_20_KAPLAN", check_po_counter_20201216_20_KAPLAN), ("check_po_counter_20201216_20_QUARLES", check_po_counter_20201216_20_QUARLES), ("check_po_counter_20201216_20_GEORGE", check_po_counter_20201216_20_GEORGE), ("check_po_roster_20201216_21_KAPLAN", check_po_roster_20201216_21_KAPLAN), ("check_po_roster_20201216_21_MESTER", check_po_roster_20201216_21_MESTER), ("check_po_roster_20201216_21_QUARLES", check_po_roster_20201216_21_QUARLES), ("check_po_roster_20201216_21_GEORGE", check_po_roster_20201216_21_GEORGE), ("check_po_counter_20201216_21_POWELL", check_po_counter_20201216_21_POWELL), ("check_po_roster_20201216_22_POWELL", check_po_roster_20201216_22_POWELL), ("check_po_roster_20201216_22_KAPLAN", check_po_roster_20201216_22_KAPLAN), ("check_po_roster_20201216_22_BARKIN", check_po_roster_20201216_22_BARKIN), ("check_po_roster_20201216_22_BRAINARD", check_po_roster_20201216_22_BRAINARD), ("check_po_roster_20201216_22_MESTER", check_po_roster_20201216_22_MESTER), ("check_po_roster_20201216_22_HARKER", check_po_roster_20201216_22_HARKER), ("check_po_roster_20201216_22_CLARIDA", check_po_roster_20201216_22_CLARIDA), ("check_po_roster_20201216_22_QUARLES", check_po_roster_20201216_22_QUARLES), ("check_po_roster_20201216_22_EVANS", check_po_roster_20201216_22_EVANS), ("check_po_roster_20201216_22_BULLARD", check_po_roster_20201216_22_BULLARD)],
}


def bounded(name, value):
    if value is not True and value is not False:
        raise RuntimeError("check %s returned a non-boolean: %r" % (name, value))
    return 1 if value else 0


def main():
    global ev
    OUTDIR.mkdir(parents=True, exist_ok=True)
    infra_error = None
    buckets = {"static": [], "reward_hacking": [], "partial_oracle": []}
    details = {}
    try:
        ev = Evidence()
        for bucket, checks in CHECKS.items():
            for name, fn in checks:
                passed = bounded(name, fn())
                buckets[bucket].append(passed)
                details[name] = passed
    except Exception as exc:
        infra_error = repr(exc)

    def mean(vals):
        return (sum(vals) / len(vals)) if vals else 0.0

    static = mean(buckets["static"])
    rh = mean(buckets["reward_hacking"])
    po = mean(buckets["partial_oracle"])
    reward = (static * 1 + rh * 2 + po * 3) / 6

    out = {
        "reward": reward,
        "total_static_check_score": static,
        "total_reward_hacking_check_score": rh,
        "total_partial_oracle_check_score": po,
        "content_score": po,
        "structural_score": static,
        "infrastructure_failure": infra_error is not None,
    }
    if infra_error:
        out["error"] = infra_error
    pathlib.Path(REWARD_JSON).write_text(json.dumps(out, indent=1))
    pathlib.Path(REWARD_TXT).write_text("%.6f" % reward + chr(10))
    (OUTDIR / "details.json").write_text(json.dumps({
        "per_check": details,
        "counts": {k: len(v) for k, v in buckets.items()},
    }, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
