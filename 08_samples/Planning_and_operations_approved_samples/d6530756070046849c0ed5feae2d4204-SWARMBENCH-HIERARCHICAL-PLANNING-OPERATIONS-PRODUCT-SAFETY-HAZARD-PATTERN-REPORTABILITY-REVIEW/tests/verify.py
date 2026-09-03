#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import traceback
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(HERE, "reference_inputs")

BUCKET_WEIGHTS = {"static_checks": 1, "reward_hacking_checks": 2, "partial_oracle_checks": 3}

RATIONALE_MIN_CHARS = 60
RATIONALE_MIN_VOCAB_HITS = 3
RATIONALE_MIN_AUTHORED_CHARS = 40
QUOTE_RUN_WORDS = 5
TEMPLATE_GRAM_WORDS = 4
TEMPLATE_CONTAINMENT = 0.85
TEMPLATE_MIN_OWN_GRAMS = 6
SKELETON_SHARE_LIMIT = 0.34
ALTERNATE_READING_CREDIT = 0.5
MEMO_MIN_CHARS = 7000
MEMO_DETERMINATION_WINDOW = 400
SHINGLE_WORDS = 12
SHINGLE_FLOOR = 0.40
SHINGLE_CEILING = 0.70
BANNED_TOKENS = ("lorem", "[insert", "tbd", "todo", "placeholder", "<fill", "to be determined",
                 "xxx-", "n/a pending")

MEMO_SECTIONS = [
    ["executive summary"],
    ["corpus overview", "corpus"],
    ["method", "methodology"],
    ["failure-mode classification", "failure mode classification", "classification"],
    ["harm substantiation", "severity conflict", "coded-severity", "coded severity"],
    ["company posture", "evidence grading", "evidence grade"],
    ["pattern consolidation", "consolidation"],
    ["reportability trigger", "trigger", "exposure"],
    ["board docket", "docket", "capacity"],
    ["pattern determination", "determinations"],
    ["recommendation", "escalation"],
]
MEMO_CONCEPTS = ["failure mode", "harm", "posture", "pattern", "trigger", "exposure", "docket"]

HARM_RANK = {"H0": 0, "H1": 1, "H2": 2, "H3": 3}
DIGITS_RX = re.compile(r"\d+")
REPORT_NO_RX = re.compile(r"\b\d{8}-[0-9A-Za-z]{4,6}-\d{6,12}\b")

_L_INGEST = re.compile(r"\b(swallow\w*|ingest\w*|chok\w*|aspirat\w*|button batter\w*|magnet\w*|"
    r"small part\w*|came off in (his|her|their|the child'?s?) mouth|put it in (his|her|their) mouth)\b", re.I)
_L_SHOCK = re.compile(r"\b(shock\w*|electrocut\w*|arc(ed|ing|s)?\b|short(ed|ing|[ -]circuit\w*)?|"
    r"live wire\w*|exposed wir\w*|bare wir\w*|ground(ing)? fault|zapped?|tingl\w*|"
    r"electrical current|current (ran|went) through)\b", re.I)
_L_FIRE = re.compile(r"\b(fire|flame\w*|caught fire|burst into|smoke|smoking|smolder\w*|"
    r"overheat\w*|melt(ed|ing|s)?|scorch\w*|char(red|ring)?|burn(ed|ing|s|t)?|"
    r"burning smell|smell(ed|s|ing)? (like )?burn\w*|too hot|extremely hot|red hot|"
    r"ignit\w*|combust\w*|thermal runaway|singe\w*)\b", re.I)
_L_PINCH = re.compile(r"\b(pinch\w*|caught (my|his|her|their|the) (finger|hand|arm|hair|foot)\w*|"
    r"finger\w* (got |was |were )?(caught|trapped|stuck|crushed)|entangl\w*|entrap\w*|"
    r"amputat\w*|crush(ed|ing)?|jam(med|ming)?|gear\w*|pull(ed)? (my|his|her) (hair|finger)|"
    r"snag(ged|ging)?|wrapped around (my|his|her|their) (neck|arm|finger))\b", re.I)
_L_CUT = re.compile(r"\b(cut\b|cuts\b|cutting|laceration\w*|slic(ed|ing)|sharp edge\w*|sharp (metal|plastic|piece)|"
    r"shatter\w*|shard\w*|broken glass|glass (broke|exploded|burst)|jagged|burr\w*|blade\w*|"
    r"stitch(es|ed)?|sutur\w*|gash\w*|punctur\w*|stab(bed)?)\b", re.I)
_L_COLLAPSE = re.compile(r"\b(collaps\w*|gave way|give way|tip(ped|ping)? over|tipover|tip-over|"
    r"fell (apart|over|off|down)|falling apart|snap(ped|ping)?|frame (broke|cracked|failed|bent)|"
    r"weld\w* (broke|failed|cracked)|seam\w* (fail\w*|rip\w*|tore|split)|leg\w* (broke|snapped|bent|buckl\w*)|"
    r"buckl(ed|ing)|structural(ly)? (fail\w*|unsound)|rail\w* (broke|detach\w*)|"
    r"came apart|detach(ed|ing)?|broke (in half|apart|off))\b", re.I)
_L_CHEM = re.compile(r"\b(fume\w*|chemical\w*|toxic|odor\w*|off-?gas\w*|mold\w*|mildew|contaminat\w*|"
    r"foreign (object|material|matter)|metal (shaving|fragment|flake|piece)s?|rust(ed|ing|y)?|"
    r"gas leak\w*|carbon monoxide|formaldehyde|lead paint|petroleum|solvent\w*|"
    r"plastic (in|inside) the food|found .{0,20}in (my|the) food)\b", re.I)
_L_LOSS = re.compile(r"\b(did ?n[o']?t (sound|alarm|alert|detect|trigger|lock|latch|engage|shut off|turn off)|"
    r"fail(ed|s|ure)? to (sound|alarm|alert|detect|latch|lock|engage|shut ?off|stop)|"
    r"never (sounded|alarmed|alerted|went off)|(alarm|detector|sensor|brake\w*|lock|latch|safety switch|"
    r"shut-?off|auto shut)\w* (did ?n[o']?t|fail\w*|not work\w*|stopped work\w*|malfunction\w*)|"
    r"turn(s|ed|ing)? (itself )?on by itself|turns? on (on its own|unprompted|spontaneous\w*)|"
    r"would ?n[o']?t (shut off|turn off|stop)|no alarm sounded)\b", re.I)

MODE_ORDER = ["Ingestion or Choking", "Electrical Shock or Arcing", "Thermal or Fire",
              "Mechanical Entrapment or Pinch", "Laceration or Sharp Edge",
              "Structural Collapse or Breakage", "Chemical Exposure or Contamination",
              "Loss of Protective Function", "Other or Undetermined"]
RESIDUAL_MODE = "Other or Undetermined"
LOOSE_MODE_CUES = [("Ingestion or Choking", _L_INGEST), ("Electrical Shock or Arcing", _L_SHOCK),
                   ("Thermal or Fire", _L_FIRE), ("Mechanical Entrapment or Pinch", _L_PINCH),
                   ("Laceration or Sharp Edge", _L_CUT), ("Structural Collapse or Breakage", _L_COLLAPSE),
                   ("Chemical Exposure or Contamination", _L_CHEM),
                   ("Loss of Protective Function", _L_LOSS)]

_S_INGEST = re.compile(r"\b(swallowed (a|the|it|one)|ingested (a|the)|(was|started) choking|"
    r"button batter\w+[^.]{0,30}(swallow|ingest|mouth))\b", re.I)
_S_SHOCK = re.compile(r"\b(electric(al)? shock|got shocked|was shocked|received a shock|shocked (me|my|him|her)|"
    r"electrocut\w+|arc(ed|ing) (out|across)|exposed (live |bare )?wir\w+|shorted out)\b", re.I)
_S_FIRE = re.compile(r"\b(caught (on )?fire|burst into flames?|(was|were|started) (on fire|smoking|smoldering)|"
    r"flames? (came|shot|were)|(unit|product|device|it) overheated|"
    r"fire department|put (the|out the) fire|smoke (filled|poured|billow\w+))\b", re.I)
_S_PINCH = re.compile(r"\b(amputat\w+|(finger|hand|thumb|arm|hair)s? (got |was |were )?(caught|trapped|stuck) in|"
    r"pinch(ed) (my|his|her|their) (finger|hand|skin)|crushed (my|his|her|their) (finger|hand))\b", re.I)
_S_CUT = re.compile(r"\b(lacerat\w+|(needed|required|got|received) stitches|deep cut|"
    r"cut (my|his|her|their) (finger|hand|arm|leg|foot)|sliced (my|his|her|open)|"
    r"(glass|it) shattered|shards? of glass)\b", re.I)
_S_COLLAPSE = re.compile(r"\b((completely |suddenly )?collapsed|tipped over (on|onto)|"
    r"(frame|weld|leg|seam|rail)s? (broke|snapped|failed|gave way)|gave way (under|beneath)|"
    r"structural failure)\b", re.I)
STRICT_MODE_CUES = [("Ingestion or Choking", _S_INGEST), ("Electrical Shock or Arcing", _S_SHOCK),
                    ("Thermal or Fire", _S_FIRE), ("Mechanical Entrapment or Pinch", _S_PINCH),
                    ("Laceration or Sharp Edge", _S_CUT), ("Structural Collapse or Breakage", _S_COLLAPSE)]

_NEG = re.compile(r"\b(no|not|never|without|thankfully no|luckily no)\b(\s+\w+){0,3}\s+"
                  r"(injur\w*|hurt|harm\w*|burn\w*|fire|shock\w*)", re.I)

_H3 = re.compile(r"\b(emergency room|\ber\b|emergency depart\w*|hospital\w*|ambulance|paramedic\w*|911|"
    r"surger\w*|operat(ed|ing) room|admitted|fractur\w*|broken (bone|arm|leg|wrist|hip|nose|rib)|"
    r"third[- ]degree burn|3rd[- ]degree burn|died|death|fatal\w*|unconscious|passed out|"
    r"intubat\w*|seizure|skin graft|\bicu\b|intensive care)\b", re.I)
_H2 = re.compile(r"\b(urgent care|doctor|physician|pediatrician|dermatologist|dentist|"
    r"(medical|health) (professional|provider)|clinic|stitch(es|ed)|sutur\w*|prescri\w*|antibiotic\w*|"
    r"x-?ray|second[- ]degree burn|2nd[- ]degree burn|(seen|treated|examined) by a? ?(doctor|nurse|medical)|"
    r"medical (attention|treatment|care)|went to (the|a) (doctor|clinic|urgent))\b", re.I)
_H1 = re.compile(r"\b(first aid|band-?aid|bandage\w*|ice pack|iced it|aloe|burn cream|neosporin|"
    r"redness|red mark|welt\w*|blister\w*|bruis\w*|scratch\w*|minor (burn|cut|injur\w*)|small (burn|cut)|"
    r"sore|swell\w*|(it|that) hurt|painful|stung|singed (my|his|her)|"
    r"burn(ed|t) (my|his|her|their) (hand|finger|arm|wrist|leg|skin|foot))\b", re.I)

POSTURE_ORDER = ["Recall or Corrective Action Cited", "Remedy Offered", "Disputes or Deflects",
                 "Standards Assurance Only", "Acknowledged Under Review", "None"]
_P_RECALL = re.compile(r"\b(recall\w*|corrective action|cpsc\.gov/recalls|"
    r"(warning|replacement|repair|inspection|remedy) program|voluntary (program|action|correction)|"
    r"stop[- ]sale|retrofit)\b", re.I)
_P_REMEDY = re.compile(r"(\brefund\w*|\breimburs\w*|\bcredit(ed)? (the|our|his|her|their) (consumer|customer|account)|"
    r"\bfree replacement|replacement at no (cost|charge)|replace (it|the (unit|product|item)) at no (cost|charge)|"
    r"eligible for a (free |no[- ]cost )?(replacement|repair|refund)|"
    r"(offered|agreed|arranged|will|would|have|has|had) (to )?(replace|repair|refund|send a replacement)|"
    r"(sent|shipped|provided|issued|processed) (a |the )?(replacement|refund|credit|voucher|new unit)|"
    r"replaced the (unit|product|item)|agreed to a resolution|resolv(ed|ing) (this|the) (matter|issue|incident)|"
    r"made (the consumer|them) whole|warranty claim (was )?(approved|processed|honored)|"
    r"at no (cost|charge) to (the|our) (consumer|customer)|"
    r"(reach|reached|reaching) out to (the |our )?(consumer|customer) to (arrange|schedule|provide))", re.I)
_P_DEFLECT = re.compile(r"(\bmisuse\w*|\bmis-?use|\bimproper\w*|\babuse\b|"
    r"(instruction|user|owner'?s?) manual|failure to follow|"
    r"(reminds?|remind|encourage[sd]?) (users|consumers|customers)|"
    r"(as|per) (directed|instructed|intended)|not intended (for|to)|"
    r"(was|had been|appears to have been) modified|required (heavy-duty )?(work )?gloves|"
    r"(read|review) the (product )?(instruction|manual|warning)|"
    r"not manufactured by|unable to (identify|locate|verify)|(no|not a) record of|counterfeit|"
    r"unauthorized (seller|reseller|distributor)|does not appear to be (our|a)|"
    r"cannot (identify|confirm) the product|not sold by|"
    r"(performed|functioned|operated) as (designed|intended)|no (product )?(defect|malfunction) (was )?(found|identified)|"
    r"did not (find|identify) (any|a) (defect|safety))", re.I)
_P_STD = re.compile(r"(meets? or exceeds?|meet or exceed|compl(y|ies|iant) with|conform\w* to|"
    r"(all )?(relevant|applicable|globally applicable|rigorous) (safety |performance )?standards|"
    r"\b(ul|astm|iec|ansi|en)\s?\d|rigorous\w* (test|standard)\w*|certified to|"
    r"multiple (layers|levels) of (thermal )?protection|safety (features|protections) designed)", re.I)
_P_ACK = re.compile(r"(thank you|thanks|appreciat\w*|(has|have|will) (been )?(shared|forward\w*)|"
    r"(is|are|will be) (being )?(review\w*|investigat\w*|evaluat\w*)|"
    r"(review|investigat)\w* (this|the|each) (report|incident|matter|concern)|"
    r"look(ing)? into|takes? .{0,40}seriously|committed to|values? (our|the) (consumer|customer))", re.I)
POSTURE_CUES = [("Recall or Corrective Action Cited", _P_RECALL), ("Remedy Offered", _P_REMEDY),
                ("Disputes or Deflects", _P_DEFLECT), ("Standards Assurance Only", _P_STD),
                ("Acknowledged Under Review", _P_ACK)]
CORROBORATING = {"Recall or Corrective Action Cited", "Remedy Offered"}
CONTESTING = {"Disputes or Deflects"}
COUNTABLE_GRADES = {"Corroborated", "Uncontested"}

_VOCAB_STOPWORDS = frozenset("""
about above after again against almost already also although always another anything anyway
appeared appears around arrived asked away back because become been before began behind being
believe below beside between beyond both bought brand broke broken bought called came cannot
company completely concern concerned contact contacted could customer damage damaged date
decided description device different does doing down during either else email enough entire
even ever every everything exactly except explained fact family finally first found from
further gave getting given going happened have having here however immediately inside instead
into issue issues itself just keep known later least like little located longer look looking
made mail make making many matter model month months more most much multiple must myself
never next nothing notice noticed number occurred often once only opened order other over
overall part person phone place placed please point possible potential prior probably problem
product products purchase purchased quickly rather really reason received recently replace
replaced report reported representative right said same second seemed seems sent service
several should showed since small some someone something soon started state still stopped
such support sure system take taken taking tell that their them then there these they thing
think this those though three through time times today told took total tried true trying under
understand until upon used using very want wanted week weeks well went were what when where
whether which while will with within without work worked would year years your
""".split())


def scrub(text):
    return _NEG.sub(" ", text or "")


def narrative_modes(narr):
    hits = [f for f, rx in LOOSE_MODE_CUES if rx.search(narr or "")]
    return hits or [RESIDUAL_MODE]


def primary_mode(narr):
    hits = set(narrative_modes(narr))
    for f in MODE_ORDER:
        if f in hits:
            return f
    return RESIDUAL_MODE


def unambiguous_mode(narr):
    hits = [f for f, rx in STRICT_MODE_CUES if rx.search(narr or "")]
    if len(hits) != 1:
        return None
    return hits[0] if primary_mode(narr) == hits[0] else None


def harm_level(narr):
    t = scrub(narr)
    if _H3.search(t):
        return "H3"
    if _H2.search(t):
        return "H2"
    if _H1.search(t):
        return "H1"
    return "H0"


def unambiguous_harm(narr):
    t = scrub(narr)
    if _H3.search(t):
        return "H3"
    if not (_H3.search(t) or _H2.search(t) or _H1.search(t)):
        return "H0"
    return None


def posture_candidates(comment):
    c = (comment or "").strip()
    if not c:
        return ["None"]
    hits = [n for n, rx in POSTURE_CUES if rx.search(c)]
    return hits or ["Acknowledged Under Review"]


def primary_posture(comment):
    cands = set(posture_candidates(comment))
    for p in POSTURE_ORDER:
        if p in cands:
            return p
    return "None"


def evidence_grade(posture, harm):
    if posture in CORROBORATING:
        return "Corroborated"
    if posture in CONTESTING:
        return "Contested"
    return "Uncontested" if harm != "H0" else "Insufficient"


def narrative_vocab(narr, limit=48):
    out = []
    for w in re.findall(r"[a-z][a-z\-]{4,}", (narr or "").lower()):
        w = w.strip("-")
        if len(w) >= 5 and w not in _VOCAB_STOPWORDS and w not in out:
            out.append(w)
    return out[:limit]


def load_reference(policy):
    data = json.load(open(os.path.join(REF_DIR, "incidents_reference.json"), encoding="utf-8"))
    band = policy["coded_severity_band"]
    by_id = {}
    for c in data["incidents"]:
        nar = c.get("incident_description") or ""
        com = c.get("company_comment") or ""
        modes = narrative_modes(nar)
        harm = harm_level(nar)
        postures = posture_candidates(com)
        prim_post = primary_posture(com)
        coded = band.get(c.get("victim_severity_coded") or "")
        by_id[c["report_no"]] = {
            "report_no": c["report_no"],
            "report_date": c["report_date"],
            "brand_family": c["brand_family"],
            "product_category": c.get("product_category") or "",
            "modes": modes,
            "primary_mode": primary_mode(nar),
            "strict_mode": unambiguous_mode(nar),
            "harm": harm,
            "harms": {harm},
            "strict_harm": unambiguous_harm(nar),
            "coded_band": coded,
            "severity_conflict": bool(coded) and coded != harm,
            "coded_comparable": bool(coded),
            "postures": postures,
            "primary_posture": prim_post,
            "has_comment": bool(com.strip()),
            "grades": {evidence_grade(p, harm) for p in postures},
            "primary_grade": evidence_grade(prim_post, harm),
            "vocab": narrative_vocab(nar),
            "narrative_words": re.findall(r"[a-z0-9']+", nar.lower()),
        }
    return by_id


def _window_complete(dates, k, win):
    d = sorted(dates)
    for i in range(len(d)):
        if len([x for x in d[:i + 1] if (d[i] - x).days <= win]) >= k:
            return d[i]
    return None


def pattern_trigger(members, policy):
    c = sorted([(d, h) for d, h, ok in members if ok])
    cands = []
    a = _window_complete([d for d, _ in c], policy["trigger_rule_a"]["min_countable"],
                         policy["trigger_rule_a"]["window_days"])
    if a:
        cands.append(("A", a))
    b = _window_complete([d for d, h in c if HARM_RANK.get(h, 0) >= 2],
                         policy["trigger_rule_b"]["min_countable_h2_plus"],
                         policy["trigger_rule_b"]["window_days"])
    if b:
        cands.append(("B", b))
    h3 = [d for d, h in c if h == "H3"]
    if h3 and len(c) >= policy["trigger_rule_c"]["min_countable_total"]:
        cands.append(("C", max(h3[0], c[policy["trigger_rule_c"]["min_countable_total"] - 1][0])))
    if not cands:
        return None, None
    order = {"A": 0, "B": 1, "C": 2}
    best = min(cands, key=lambda t: (t[1], order[t[0]]))
    return best[0], best[1]


def business_days(start, n):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def build_reference_patterns(by_id, policy):
    as_of = dt.date.fromisoformat(policy["as_of_date"])
    groups = defaultdict(list)
    for g in by_id.values():
        groups[(g["brand_family"], g["primary_mode"])].append(g)
    pats = {}
    for key, members in groups.items():
        mem = [(dt.date.fromisoformat(m["report_date"]), m["harm"],
                m["primary_grade"] in COUNTABLE_GRADES) for m in members]
        rule, td = pattern_trigger(mem, policy)
        p = {"key": key, "brand_family": key[0], "failure_mode": key[1],
             "incident_count": len(members),
             "countable_count": sum(1 for _d, _h, ok in mem if ok),
             "trigger_rule": rule, "trigger_date": td,
             "categories": sorted({m["product_category"] for m in members}),
             "members": sorted(m["report_no"] for m in members)}
        if td:
            p["filing_deadline"] = td + dt.timedelta(days=policy["filing_deadline_days"])
            p["exposure_days"] = max(0, (as_of - p["filing_deadline"]).days)
        else:
            p["filing_deadline"] = None
            p["exposure_days"] = 0
        pats[key] = p
    ordered = sorted(pats.values(), key=lambda p: (p["brand_family"], p["failure_mode"]))
    for i, p in enumerate(ordered, 1):
        p["ref_id"] = "HP%03d" % i
    trig = sorted([p for p in ordered if p["trigger_rule"]],
                  key=lambda p: (-p["exposure_days"], p["trigger_date"], p["ref_id"]))
    slots = business_days(as_of, policy["board_business_days"])
    per = policy["board_slots_per_business_day"]
    for i, p in enumerate(trig):
        if i < policy["board_capacity"]:
            p["disposition"], p["board_slot"] = "Board Docketed", i + 1
            p["board_date"] = slots[i // per]
        else:
            p["disposition"], p["board_slot"], p["board_date"] = "Board Backlog", None, None
    for p in ordered:
        if not p["trigger_rule"]:
            p["disposition"] = "Monitor" if p["countable_count"] >= 2 else "Close No Action"
            p["board_slot"] = p["board_date"] = None
    return pats


def get(row, *names):
    for n in names:
        if isinstance(row, dict) and n in row and row[n] not in (None, ""):
            return row[n]
    return None


def as_text(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def canon_from(text, options):
    t = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()
    if not t:
        return None
    for o in options:
        if re.sub(r"[^a-z0-9]+", " ", o.lower()).strip() == t:
            return o
    for o in options:
        ot = re.sub(r"[^a-z0-9]+", " ", o.lower()).strip()
        if ot and (ot in t or t in ot):
            return o
    return None


def canon_mode(text):
    m = canon_from(text, MODE_ORDER)
    if m:
        return m
    t = (text or "").lower()
    for key, name in (("choking", "Ingestion or Choking"), ("ingest", "Ingestion or Choking"),
                      ("shock", "Electrical Shock or Arcing"), ("arc", "Electrical Shock or Arcing"),
                      ("thermal", "Thermal or Fire"), ("fire", "Thermal or Fire"),
                      ("pinch", "Mechanical Entrapment or Pinch"), ("entrap", "Mechanical Entrapment or Pinch"),
                      ("lacerat", "Laceration or Sharp Edge"), ("sharp", "Laceration or Sharp Edge"),
                      ("collapse", "Structural Collapse or Breakage"), ("structural", "Structural Collapse or Breakage"),
                      ("chemical", "Chemical Exposure or Contamination"), ("contaminat", "Chemical Exposure or Contamination"),
                      ("protective", "Loss of Protective Function"), ("loss of", "Loss of Protective Function")):
        if key in t:
            return name
    return None


def canon_harm(text):
    t = (text or "").strip().upper()
    m = re.search(r"H\s*([0-3])", t)
    if m:
        return "H" + m.group(1)
    m = re.fullmatch(r"\s*([0-3])\s*", t)
    return "H" + m.group(1) if m else None


def canon_posture(text):
    return canon_from(text, POSTURE_ORDER)


def canon_grade(text):
    return canon_from(text, ["Corroborated", "Contested", "Uncontested", "Insufficient"])


def canon_bool(v):
    if isinstance(v, bool):
        return v
    t = as_text(v).strip().lower()
    if t in ("true", "yes", "y", "1"):
        return True
    if t in ("false", "no", "n", "0"):
        return False
    return None


def canon_date(v):
    t = as_text(v).strip()
    if not t or t.lower() in ("null", "none", "n/a", "-"):
        return None
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        try:
            return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            return None
    return None


def num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?\d+(?:\.\d+)?", as_text(v))
    return float(m.group()) if m else None


def canon_rule(v):
    t = as_text(v).strip().upper()
    m = re.search(r"\b([ABC])\b", t)
    return m.group(1) if m else None


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def load_register(path):
    if not os.path.exists(path):
        return [], [], {}, "missing %s" % path
    try:
        data = json.loads(read_text(path))
    except Exception as ex:
        return [], [], {}, "unparseable JSON: %s" % ex
    incidents, patterns, summary = [], [], {}
    if isinstance(data, dict):
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        incidents = data.get("incidents") if isinstance(data.get("incidents"), list) else []
        patterns = data.get("patterns") if isinstance(data.get("patterns"), list) else []
        if not incidents:
            incidents = next((v for v in data.values() if isinstance(v, list)), [])
    elif isinstance(data, list):
        incidents = data
    return ([r for r in incidents if isinstance(r, dict)],
            [r for r in patterns if isinstance(r, dict)], summary, None)


def load_docket(path):
    txt = read_text(path)
    if not txt.strip():
        return []
    try:
        return [dict(r) for r in csv.DictReader(io.StringIO(txt))]
    except Exception:
        return []


def row_report_no(r):
    v = as_text(get(r, "report_no", "reportNo", "report_number", "report", "id")).strip()
    m = REPORT_NO_RX.search(v)
    return m.group(0) if m else v


def i_brand(r):
    return as_text(get(r, "brand_family", "brand", "family")).strip()


def i_mode(r):
    return canon_mode(as_text(get(r, "failure_mode", "failure", "mode", "hazard_mode")))


def i_harm(r):
    return canon_harm(as_text(get(r, "harm_level", "harm", "substantiated_harm")))


def i_conflict(r):
    return canon_bool(get(r, "severity_conflict", "severity_conflict_flag", "conflict"))


def i_posture(r):
    return canon_posture(as_text(get(r, "company_posture", "posture", "firm_posture")))


def i_grade(r):
    return canon_grade(as_text(get(r, "evidence_grade", "grade", "evidence")))


def i_pattern(r):
    return as_text(get(r, "pattern_id", "pattern", "hazard_pattern_id")).strip()


def i_rationale(r):
    return as_text(get(r, "rationale", "reason", "note", "justification")).strip()


def p_id(r):
    return as_text(get(r, "pattern_id", "id", "pattern")).strip()


def p_key(r):
    b = as_text(get(r, "brand_family", "brand", "family")).strip()
    m = canon_mode(as_text(get(r, "failure_mode", "failure", "mode")))
    return (b, m)


def p_members(r):
    v = get(r, "member_report_nos", "members", "member_reports", "report_nos")
    if isinstance(v, list):
        return [row_report_no({"report_no": as_text(x)}) for x in v]
    return REPORT_NO_RX.findall(as_text(v))


def first_rows(rows, by_id):
    idx = {}
    for r in rows:
        rn = row_report_no(r)
        if rn in by_id and rn not in idx:
            idx[rn] = r
    return idx


def band_score(value, lo, hi):
    if value is None:
        return 0.0
    if lo <= value <= hi:
        return 1.0
    dist = lo - value if value < lo else value - hi
    return max(0.0, 1.0 - dist / max(1, hi))


def brand_family_options(policy):
    return sorted(set(policy["brand_register"].values()))


def canon_brand(text, options):
    return canon_from(text, options)


def check_output_files_present(incidents, docket_rows, memo_text):
    reg = 1.0 if incidents else 0.0
    doc = 1.0 if docket_rows else 0.0
    memo = 1.0 if len(memo_text) >= 500 else 0.0
    return (reg + doc + memo) / 3, [
        "register incidents present=%s (%d), docket rows=%d, memo>=500 chars=%s (%d)"
        % (bool(incidents), len(incidents), len(docket_rows), len(memo_text) >= 500, len(memo_text))]


def check_incident_coverage(incidents, by_id):
    first = first_rows(incidents, by_id)
    return len(first) / max(1, len(by_id)), [
        "%d/%d corpus reports present in the register" % (len(first), len(by_id))]


def check_schema_valid(incidents, by_id, policy):
    fams = brand_family_options(policy)
    first = first_rows(incidents, by_id)
    ok = 0
    for rn, r in first.items():
        good = (canon_brand(i_brand(r), fams) is not None
                and i_mode(r) in MODE_ORDER
                and i_harm(r) in HARM_RANK
                and i_conflict(r) is not None
                and i_posture(r) in POSTURE_ORDER
                and i_grade(r) is not None
                and bool(i_pattern(r)))
        ok += 1 if good else 0
    return ok / max(1, len(by_id)), [
        "%d/%d register rows carry a valid brand family, failure mode, harm level, "
        "severity-conflict flag, posture, evidence grade and pattern id" % (ok, len(by_id))]


def check_no_duplicate_incidents(incidents, by_id):
    idx = defaultdict(list)
    for r in incidents:
        idx[row_report_no(r)].append(r)
    once = sum(1 for rn, rs in idx.items() if rn in by_id and len(rs) == 1)
    dups = sum(1 for rn, rs in idx.items() if rn in by_id and len(rs) > 1)
    hallu = sum(1 for rn in idx if rn not in by_id)
    return once / max(1, len(incidents)), [
        "%d of %d register rows are a corpus report listed exactly once "
        "(duplicated report_nos=%d, report_nos not in the corpus=%d)"
        % (once, len(incidents), dups, hallu)]


def _authored_text(rationale, narrative_words, n=QUOTE_RUN_WORDS):
    words = re.findall(r"[a-z0-9']+", (rationale or "").lower())
    grams = {tuple(narrative_words[i:i + n]) for i in range(len(narrative_words) - n + 1)}
    keep = [True] * len(words)
    for i in range(len(words) - n + 1):
        if tuple(words[i:i + n]) in grams:
            for j in range(i, i + n):
                keep[j] = False
    return " ".join(DIGITS_RX.sub("#", w) for w, k in zip(words, keep) if k)


def _word_grams(text, n=TEMPLATE_GRAM_WORDS):
    w = re.findall(r"[a-z0-9'#]+", (text or "").lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def _containment(a, b):
    return len(a & b) / len(a) if a else 0.0


def _skeleton(authored_text, own_vocab):
    vocab = set(own_vocab) | _LABEL_TOKENS
    out = []
    for w in re.findall(r"[a-z0-9'#]+", (authored_text or "").lower()):
        out.append("#" if (w in vocab or "#" in w or any(c.isdigit() for c in w)) else w)
    return re.sub(r"(?:# )+#?", "# ", " ".join(out)).strip()


_LABEL_TOKENS = frozenset(
    w for phrase in (MODE_ORDER + POSTURE_ORDER + list(HARM_RANK)
                     + ["Corroborated", "Contested", "Uncontested", "Insufficient"]
                     + ["Board Docketed", "Board Backlog", "Monitor", "Close No Action"])
    for w in re.findall(r"[a-z0-9]+", phrase.lower()))


def _templated(authored, vocabs=None):
    grams = {rn: _word_grams(t) for rn, t in authored.items()}
    flagged = set()
    ids = list(grams)
    for a in ids:
        if not grams[a]:
            flagged.add(a)
            continue
        for b in ids:
            if a == b or not grams[b]:
                continue
            if (_containment(grams[a], grams[b]) >= TEMPLATE_CONTAINMENT
                    and len(grams[a] - grams[b]) < TEMPLATE_MIN_OWN_GRAMS):
                flagged.add(a)
                break
    if vocabs and len(authored) >= 10:
        skels = {rn: _skeleton(t, vocabs.get(rn, [])) for rn, t in authored.items()}
        counts = Counter(v for v in skels.values() if v.strip())
        limit = max(2, int(SKELETON_SHARE_LIMIT * len(authored)))
        for rn, sk in skels.items():
            if sk.strip() and counts[sk] > limit:
                flagged.add(rn)
    return flagged


def check_rationale_grounding(incidents, by_id):
    first = first_rows(incidents, by_id)
    authored = {rn: _authored_text(i_rationale(r), by_id[rn]["narrative_words"])
                for rn, r in first.items()}
    templated = _templated(authored, {rn: by_id[rn]["vocab"] for rn in first})
    ok = thin = boiler = 0
    for rn, r in first.items():
        rat = i_rationale(r)
        low = rat.lower()
        vocab = by_id[rn]["vocab"]
        hits = sum(1 for t in vocab if t in low)
        from_narrative = hits >= min(RATIONALE_MIN_VOCAB_HITS, len(vocab)) if vocab else True
        specific = len(authored[rn]) >= RATIONALE_MIN_AUTHORED_CHARS and rn not in templated
        if not from_narrative:
            thin += 1
        if not specific:
            boiler += 1
        if len(rat) >= RATIONALE_MIN_CHARS and rn in rat and from_narrative and specific:
            ok += 1
    return ok / max(1, len(by_id)), [
        "%d/%d reports carry a rationale long enough, naming its own report_no, reusing at "
        "least %d distinctive words from its own account, and stating a determination written "
        "for that report" % (ok, len(by_id), RATIONALE_MIN_VOCAB_HITS),
        "%d rationales draw too little vocabulary from the report's own account to show it was read" % thin,
        "%d rationales are boilerplate: once text quoted from the account and numbers are stripped, "
        "under %d characters remain, they share at least %d%% of their wording with another "
        "report's rationale while adding almost nothing of their own, or the sentence left once "
        "each report's own words are slotted out is shared by more than %d%% of the corpus"
        % (boiler, RATIONALE_MIN_AUTHORED_CHARS, int(TEMPLATE_CONTAINMENT * 100),
           int(SKELETON_SHARE_LIMIT * 100))]


def check_pattern_partition_integrity(incidents, patterns, by_id):
    first = first_rows(incidents, by_id)
    if not patterns:
        return 0.0, ["no pattern array present, so the register does not partition the corpus"]
    by_pid = {}
    for p in patterns:
        pid = p_id(p)
        if pid and pid not in by_pid:
            by_pid[pid] = p
    tests = []
    resolvable = sum(1 for r in first.values() if i_pattern(r) in by_pid)
    tests.append(resolvable / max(1, len(first)))
    claimed = defaultdict(set)
    for rn, r in first.items():
        claimed[i_pattern(r)].add(rn)
    agree = 0
    for pid, p in by_pid.items():
        declared = set(m for m in p_members(p) if m in by_id)
        if declared and declared == claimed.get(pid, set()):
            agree += 1
    tests.append(agree / max(1, len(by_pid)))
    union = set()
    overlap = 0
    for p in by_pid.values():
        ms = set(m for m in p_members(p) if m in by_id)
        overlap += len(union & ms)
        union |= ms
    tests.append(len(union) / max(1, len(by_id)))
    tests.append(1.0 if overlap == 0 else max(0.0, 1.0 - overlap / max(1, len(by_id))))
    return sum(tests) / len(tests), [
        "%d/%d register rows carry a pattern_id that resolves to a declared pattern"
        % (resolvable, len(first)),
        "%d/%d patterns list exactly the reports that claim them" % (agree, len(by_pid)),
        "declared pattern membership covers %d/%d corpus reports with %d report(s) claimed by "
        "more than one pattern" % (len(union), len(by_id), overlap)]


def check_pattern_key_consistency(incidents, patterns, by_id, policy):
    first = first_rows(incidents, by_id)
    fams = brand_family_options(policy)
    by_pid = {}
    for p in patterns:
        pid = p_id(p)
        if pid and pid not in by_pid:
            by_pid[pid] = p
    if not by_pid:
        return 0.0, ["no patterns to test for key consistency"]
    homog = keyed = 0
    for pid, p in by_pid.items():
        members = [first[rn] for rn in first if i_pattern(first[rn]) == pid]
        if not members:
            continue
        keys = {(canon_brand(i_brand(m), fams), i_mode(m)) for m in members}
        if len(keys) == 1:
            homog += 1
        pk = (canon_brand(p_key(p)[0], fams), p_key(p)[1])
        if len(keys) == 1 and pk == next(iter(keys)):
            keyed += 1
    seen_keys = [(canon_brand(p_key(p)[0], fams), p_key(p)[1]) for p in by_pid.values()]
    seen_keys = [k for k in seen_keys if k[0] and k[1]]
    kc = Counter(seen_keys)
    unsplit = (sum(1 for k in seen_keys if kc[k] == 1) / len(seen_keys)) if seen_keys else 0.0
    score = (homog / max(1, len(by_pid)) + keyed / max(1, len(by_pid)) + unsplit) / 3
    return score, [
        "%d/%d patterns hold reports that all share one (brand family, failure mode) pair, and "
        "%d also declare that same pair as their own key" % (homog, len(by_pid), keyed),
        "%d distinct (brand family, failure mode) keys across %d patterns -- a repeated key means "
        "one hazard pattern was left split in two" % (len(set(seen_keys)), len(seen_keys))]


def check_countable_count_consistency(incidents, patterns, by_id):
    first = first_rows(incidents, by_id)
    if not patterns:
        return 0.0, ["no patterns to reconcile countable counts against"]
    ok = considered = 0
    for p in patterns:
        pid = p_id(p)
        declared = num(get(p, "countable_count", "countable", "countable_incidents"))
        if declared is None:
            considered += 1
            continue
        members = [first[rn] for rn in first if i_pattern(first[rn]) == pid]
        if not members:
            considered += 1
            continue
        actual = sum(1 for m in members if i_grade(m) in COUNTABLE_GRADES)
        considered += 1
        if abs(declared - actual) < 0.5:
            ok += 1
    inc_ok = considered_i = 0
    for p in patterns:
        pid = p_id(p)
        declared = num(get(p, "incident_count", "incidents", "member_count"))
        members = [rn for rn in first if i_pattern(first[rn]) == pid]
        if declared is None or not members:
            considered_i += 1
            continue
        considered_i += 1
        if abs(declared - len(members)) < 0.5:
            inc_ok += 1
    return (ok / max(1, considered) + inc_ok / max(1, considered_i)) / 2, [
        "%d/%d patterns declare a countable_count matching the number of their own members the "
        "register grades Corroborated or Uncontested" % (ok, considered),
        "%d/%d patterns declare an incident_count matching the number of register rows that "
        "claim them" % (inc_ok, considered_i)]


def check_grade_derivation_consistency(incidents, by_id):
    first = first_rows(incidents, by_id)
    ok = considered = 0
    for rn, r in first.items():
        post, harm, grade = i_posture(r), i_harm(r), i_grade(r)
        considered += 1
        if post is None or harm is None or grade is None:
            continue
        if grade == evidence_grade(post, harm):
            ok += 1
    silent = [rn for rn, g in by_id.items() if not g["has_comment"]]
    silent_ok = sum(1 for rn in silent
                    if rn in first and i_posture(first[rn]) == "None")
    derived = ok / max(1, considered)
    unanswered = silent_ok / max(1, len(silent))
    return (derived + unanswered) / 2, [
        "%d/%d register rows carry the evidence grade the method derives from that row's own "
        "posture and harm level" % (ok, considered),
        "%d/%d reports that carry no company response at all are recorded with posture None"
        % (silent_ok, len(silent))]


def _agent_pattern_members(incidents, patterns, by_id):
    first = first_rows(incidents, by_id)
    out = {}
    for p in patterns:
        pid = p_id(p)
        if not pid or pid in out:
            continue
        members = []
        for rn, r in first.items():
            if i_pattern(r) == pid:
                members.append((dt.date.fromisoformat(by_id[rn]["report_date"]),
                                i_harm(r), i_grade(r) in COUNTABLE_GRADES))
        out[pid] = (p, members)
    return out


def check_trigger_internal_consistency(incidents, patterns, by_id, policy):
    as_of = dt.date.fromisoformat(policy["as_of_date"])
    pm = _agent_pattern_members(incidents, patterns, by_id)
    if not pm:
        return 0.0, ["no patterns to recompute triggers for"]
    rule_ok = date_ok = dl_ok = exp_ok = 0
    n = 0
    for pid, (p, members) in pm.items():
        if not members:
            continue
        n += 1
        exp_rule, exp_date = pattern_trigger(members, policy)
        got_rule = canon_rule(get(p, "trigger_rule", "rule"))
        got_date = canon_date(get(p, "trigger_date", "triggered_on"))
        if got_rule == exp_rule:
            rule_ok += 1
        if got_date == exp_date:
            date_ok += 1
        want_dl = exp_date + dt.timedelta(days=policy["filing_deadline_days"]) if exp_date else None
        if canon_date(get(p, "filing_deadline", "deadline")) == want_dl:
            dl_ok += 1
        want_exp = max(0, (as_of - want_dl).days) if want_dl else 0
        got_exp = num(get(p, "exposure_days", "exposure"))
        if got_exp is not None and abs(got_exp - want_exp) < 0.5:
            exp_ok += 1
    return (rule_ok + date_ok + dl_ok + exp_ok) / max(1, 4 * n), [
        "recomputing each pattern's trigger from the register's own incident grades and harm "
        "levels: %d/%d patterns declare the rule that actually fires, %d the date that "
        "completes it, %d the matching filing deadline and %d the matching exposure days"
        % (rule_ok, n, date_ok, dl_ok, exp_ok)]


def check_docket_ordering_and_capacity(patterns, docket_rows, policy):
    as_of = dt.date.fromisoformat(policy["as_of_date"])
    cap = policy["board_capacity"]
    per = policy["board_slots_per_business_day"]
    slots = business_days(as_of, policy["board_business_days"])
    if not docket_rows:
        return 0.0, ["no docket rows to test"]
    rows = []
    for r in docket_rows:
        rows.append({
            "slot": num(get(r, "board_slot", "slot")),
            "date": canon_date(get(r, "board_date", "date", "sitting_date")),
            "pid": as_text(get(r, "pattern_id", "pattern", "id")).strip(),
            "exposure": num(get(r, "exposure_days", "exposure")),
            "trigger": canon_date(get(r, "trigger_date", "triggered_on")),
            "rule": canon_rule(get(r, "trigger_rule", "rule")),
            "deadline": canon_date(get(r, "filing_deadline", "deadline")),
            "countable": num(get(r, "countable_count", "countable")),
        })
    tests = []
    tests.append(1.0 if len(rows) <= cap else max(0.0, 1.0 - (len(rows) - cap) / cap))
    have = [r for r in rows if r["slot"] is not None]
    seq = sorted(int(r["slot"]) for r in have)
    tests.append(1.0 if seq == list(range(1, len(rows) + 1)) else
                 len(set(seq) & set(range(1, cap + 1))) / max(1, len(rows)))
    dated = 0
    for r in have:
        want = slots[int(r["slot"] - 1) // per] if 1 <= r["slot"] <= cap else None
        if want and r["date"] == want:
            dated += 1
    tests.append(dated / max(1, len(have)))
    perday = Counter(r["date"] for r in rows if r["date"])
    over = sum(max(0, c - per) for c in perday.values())
    tests.append(1.0 if over == 0 else max(0.0, 1.0 - over / max(1, len(rows))))
    ordered = sorted(rows, key=lambda r: (r["slot"] if r["slot"] is not None else 10 ** 6))
    inversions = 0
    pairs = 0
    for i in range(len(ordered) - 1):
        a, b = ordered[i], ordered[i + 1]
        if a["exposure"] is None or b["exposure"] is None:
            continue
        pairs += 1
        if a["exposure"] < b["exposure"]:
            inversions += 1
        elif a["exposure"] == b["exposure"] and a["trigger"] and b["trigger"] and a["trigger"] > b["trigger"]:
            inversions += 1
        elif (a["exposure"] == b["exposure"] and a["trigger"] == b["trigger"]
              and a["pid"] and b["pid"] and a["pid"] > b["pid"]):
            inversions += 1
    tests.append(1.0 - inversions / max(1, pairs))
    pids = {p_id(p) for p in patterns}
    linked = sum(1 for r in rows if r["pid"] in pids) / max(1, len(rows)) if pids else 0.0
    tests.append(linked)
    return sum(tests) / len(tests), [
        "%d docket rows against a cycle capacity of %d; slot numbers run 1..n=%s; %d/%d rows sit "
        "on the business day their slot maps to; %d seatings exceed the %d-per-sitting-day limit"
        % (len(rows), cap, seq == list(range(1, len(rows) + 1)), dated, len(have), over, per),
        "%d/%d adjacent docket pairs are out of the method's exposure-descending, then "
        "trigger-date-ascending, then pattern-id-ascending order; %.0f%% of docket rows name a pattern_id that exists in "
        "the register" % (inversions, pairs, 100 * linked)]


def _rollup(incidents, patterns, by_id, policy):
    first = first_rows(incidents, by_id)
    grades = Counter()
    conflicts = 0
    for r in first.values():
        g = i_grade(r)
        if g:
            grades[g] += 1
        if i_conflict(r) is True:
            conflicts += 1
    disp = Counter()
    triggered = 0
    seated = 0
    max_exp = 0
    for p in patterns:
        d = canon_from(as_text(get(p, "disposition", "outcome")), policy["dispositions"])
        if d:
            disp[d] += 1
        if canon_rule(get(p, "trigger_rule", "rule")):
            triggered += 1
        if num(get(p, "board_slot", "slot")) is not None:
            seated += 1
        e = num(get(p, "exposure_days", "exposure"))
        if e is not None:
            max_exp = max(max_exp, int(e))
    return {"total_incidents": len(first), "total_patterns": len({p_id(p) for p in patterns if p_id(p)}),
            "severity_conflict_count": conflicts, "grade_counts": dict(grades),
            "disposition_counts": dict(disp), "triggered_pattern_count": triggered,
            "board_slots_used": seated, "board_backlog_count": max(0, triggered - seated),
            "max_exposure_days": max_exp}


def _plausibility(incidents, patterns, by_id, policy, ref_pats):
    roll = _rollup(incidents, patterns, by_id, policy)
    ref_conf = sum(1 for g in by_id.values() if g["severity_conflict"])
    ref_trig = sum(1 for p in ref_pats.values() if p["trigger_rule"])
    tests = [("incident total", 1.0 if roll["total_incidents"] >= len(by_id) - 1
              else roll["total_incidents"] / max(1, len(by_id))),
             ("pattern total", band_score(roll["total_patterns"],
                                          int(len(ref_pats) * 0.7), int(len(ref_pats) * 1.4) + 1)),
             ("severity conflicts", band_score(roll["severity_conflict_count"],
                                               int(ref_conf * 0.5), int(ref_conf * 1.6) + 1)),
             ("triggered patterns", band_score(roll["triggered_pattern_count"],
                                               int(ref_trig * 0.5), int(ref_trig * 1.7) + 1)),
             ("board seats used", 1.0 if roll["board_slots_used"] <= policy["board_capacity"] else 0.0)]
    score = sum(s for _n, s in tests) / len(tests)
    off = ["%s %.2f" % (n, s) for n, s in tests if s < 1.0]
    return score, off, roll


def check_summary_consistency(incidents, patterns, summary, by_id, policy, ref_pats):
    if not isinstance(summary, dict) or not summary:
        return 0.0, ["no summary object present"]
    plaus, off, roll = _plausibility(incidents, patterns, by_id, policy, ref_pats)

    def close(a, b):
        return a is not None and abs(a - b) <= 1

    checks = [close(num(get(summary, "total_incidents", "incident_count", "total")), roll["total_incidents"]),
              close(num(get(summary, "total_patterns", "pattern_count")), roll["total_patterns"]),
              close(num(get(summary, "severity_conflict_count", "conflict_count")), roll["severity_conflict_count"]),
              close(num(get(summary, "triggered_pattern_count", "triggered")), roll["triggered_pattern_count"]),
              close(num(get(summary, "board_slots_used", "slots_used", "docketed_count")), roll["board_slots_used"]),
              close(num(get(summary, "board_backlog_count", "backlog_count", "backlog")), roll["board_backlog_count"]),
              close(num(get(summary, "max_exposure_days", "max_exposure")), roll["max_exposure_days"])]
    gc = get(summary, "grade_counts", "grades") or {}
    if isinstance(gc, dict):
        for g in ("Corroborated", "Contested", "Uncontested", "Insufficient"):
            checks.append(close(num(gc.get(g) if gc.get(g) is not None else gc.get(g.lower())),
                                roll["grade_counts"].get(g, 0)))
    else:
        checks += [False] * 4
    dc = get(summary, "disposition_counts", "dispositions") or {}
    if isinstance(dc, dict):
        for d in policy["dispositions"]:
            checks.append(close(num(dc.get(d) if dc.get(d) is not None else dc.get(d.lower())),
                                roll["disposition_counts"].get(d, 0)))
    else:
        checks += [False] * len(policy["dispositions"])
    internal = sum(1 for c in checks if c) / len(checks)
    return (internal + plaus) / 2, [
        "%d/%d summary metrics reconcile with the register's own incident and pattern arrays"
        % (sum(1 for c in checks if c), len(checks)),
        "the portfolio those metrics describe sits inside the range the corpus supports on "
        "%.4f of the figures%s" % (plaus, (" (outside the supported range: %s)" % ", ".join(off)) if off else "")]


def _memo_variety(memo, keys, window=240):
    contexts = []
    key_rx = re.compile("|".join(re.escape(k) for k in keys)) if keys else None
    for k in keys:
        i = memo.find(k)
        if i < 0:
            continue
        seg = REPORT_NO_RX.sub(" ", memo[i:i + window])
        if key_rx:
            seg = key_rx.sub(" ", seg)
        contexts.append(re.sub(r"\s+", " ", seg.lower()).strip())
    if not contexts:
        return 0.0, 0
    return len(set(contexts)) / len(contexts), len(contexts)


def _memo_non_repetition(memo):
    words = re.findall(r"[a-z0-9]+", memo.lower())
    if len(words) < SHINGLE_WORDS * 4:
        return 0.0, 0.0
    sh = [" ".join(words[i:i + SHINGLE_WORDS]) for i in range(len(words) - SHINGLE_WORDS + 1)]
    ratio = len(set(sh)) / len(sh)
    scaled = (ratio - SHINGLE_FLOOR) / (SHINGLE_CEILING - SHINGLE_FLOOR)
    return max(0.0, min(1.0, scaled)), ratio


def check_memo_structure(memo_text, incidents, patterns, by_id):
    low = memo_text.lower()
    sect = sum(1 for grp in MEMO_SECTIONS if any(k in low for k in grp))
    concepts = sum(1 for c in MEMO_CONCEPTS if c in low)
    no_ph = 0.0 if (not low or any(b in low for b in BANNED_TOKENS)) else 1.0
    length = 1.0 if len(memo_text) >= MEMO_MIN_CHARS else round(len(memo_text) / MEMO_MIN_CHARS, 3)
    pids = [p_id(p) for p in patterns if p_id(p)]
    named = sum(1 for pid in pids if pid and pid in memo_text)
    named_score = named / max(1, len(pids)) if pids else 0.0
    variety, nctx = _memo_variety(memo_text, pids)
    nonrep, raw = _memo_non_repetition(memo_text)
    parts = [sect / len(MEMO_SECTIONS), concepts / len(MEMO_CONCEPTS), no_ph, length,
             named_score, variety, nonrep]
    return sum(parts) / len(parts), [
        "sections %d/%d, concepts %d/%d, no_placeholder=%s, length=%d, patterns named %d/%d"
        % (sect, len(MEMO_SECTIONS), concepts, len(MEMO_CONCEPTS), bool(no_ph), len(memo_text),
           named, len(pids)),
        "per-pattern context variety %.4f over %d named patterns, distinct %d-gram ratio %.4f "
        "(scored %.4f)" % (variety, nctx, SHINGLE_WORDS, raw, nonrep)]


def _states_number(low, value, required, window=110):
    pat = re.compile(r"(?<![\d,.])" + str(int(value)) + r"(?!\d)(?!\.\d)(?!,\d)")
    for m in pat.finditer(low):
        seg = low[max(0, m.start() - window): m.end() + window]
        if not all(any(k in seg for k in grp) for grp in required):
            continue
        return True
    return False


def check_memo_register_agreement(memo_text, incidents, patterns, by_id, policy, ref_pats):
    if not memo_text.strip():
        return 0.0, ["no memo to reconcile against the register"]
    low = memo_text.lower()
    plaus, off, roll = _plausibility(incidents, patterns, by_id, policy, ref_pats)
    facts = [("incident total", roll["total_incidents"], [("report", "incident", "corpus")]),
             ("pattern total", roll["total_patterns"], [("pattern",)]),
             ("severity conflicts", roll["severity_conflict_count"], [("conflict", "disagree", "coded")]),
             ("triggered patterns", roll["triggered_pattern_count"], [("trigger", "reportab")]),
             ("board seats used", roll["board_slots_used"], [("docket", "board", "seat")]),
             ("board backlog", roll["board_backlog_count"], [("backlog", "unseated", "not seated", "capacity")]),
             ("max exposure days", roll["max_exposure_days"], [("exposure", "days", "overdue")])]
    for g in ("Corroborated", "Contested", "Uncontested", "Insufficient"):
        c = roll["grade_counts"].get(g, 0)
        if c:
            facts.append(("%s count" % g, c, [(g.lower(),)]))
    stated = [n for n, v, req in facts if _states_number(low, v, req)]
    missing = [n for n, _v, _r in facts if n not in stated]
    return (len(stated) / max(1, len(facts)) + plaus) / 2, [
        "%d/%d register figures are stated in the memo in the right context%s"
        % (len(stated), len(facts), (" (missing: %s)" % ", ".join(missing)) if missing else ""),
        "those figures describe a portfolio inside the range the corpus supports on %.4f of the "
        "figures%s" % (plaus, (" (outside: %s)" % ", ".join(off)) if off else "")]


def p_basis(r):
    return as_text(get(r, "basis", "basis_note", "pattern_basis", "note", "rationale")).strip()


def check_docket_register_agreement(patterns, docket_rows, policy):
    if not docket_rows:
        return 0.0, ["no docket rows to reconcile against the register"]
    if not patterns:
        return 0.0, ["no register patterns to reconcile the docket against"]
    by_pid = {}
    for pp in patterns:
        pid = p_id(pp)
        if pid and pid not in by_pid:
            by_pid[pid] = pp
    total = 0.0
    joined = 0
    field_miss = Counter()
    for r in docket_rows:
        pid = as_text(get(r, "pattern_id", "pattern", "id")).strip()
        pp = by_pid.get(pid)
        if pp is None:
            continue
        joined += 1
        tests = {
            "brand_family": (as_text(get(r, "brand_family", "brand")).strip().lower()
                             == as_text(get(pp, "brand_family", "brand")).strip().lower()),
            "failure_mode": (canon_mode(as_text(get(r, "failure_mode", "mode")))
                             == canon_mode(as_text(get(pp, "failure_mode", "mode")))),
            "trigger_rule": (canon_rule(get(r, "trigger_rule", "rule"))
                             == canon_rule(get(pp, "trigger_rule", "rule"))),
            "trigger_date": (canon_date(get(r, "trigger_date", "triggered_on"))
                             == canon_date(get(pp, "trigger_date", "triggered_on"))),
            "filing_deadline": (canon_date(get(r, "filing_deadline", "deadline"))
                                == canon_date(get(pp, "filing_deadline", "deadline"))),
            "exposure_days": _same_num(get(r, "exposure_days", "exposure"),
                                       get(pp, "exposure_days", "exposure")),
            "countable_count": _same_num(get(r, "countable_count", "countable"),
                                         get(pp, "countable_count", "countable", "countable_incidents")),
        }
        for k, v in tests.items():
            if not v:
                field_miss[k] += 1
        total += sum(1 for v in tests.values() if v) / len(tests)
    return total / max(1, len(docket_rows)), [
        "%d/%d docket rows join back to a pattern the register declares under the same "
        "pattern_id" % (joined, len(docket_rows)),
        "columns disagreeing with the register they claim to come from: "
        + (", ".join("%s=%d" % (k, n) for k, n in sorted(field_miss.items())) or "none")]


def _same_num(a, b):
    na, nb = num(a), num(b)
    return na is not None and nb is not None and abs(na - nb) < 0.5


def check_basis_grounding(patterns, incidents, by_id):
    if not patterns:
        return 0.0, ["no patterns to read a basis note from"]
    seen = {}
    for pp in patterns:
        pid = p_id(pp)
        if pid and pid not in seen:
            seen[pid] = pp
    if not seen:
        return 0.0, ["no patterns carry a pattern_id, so no basis note can be attributed"]
    notes = {pid: p_basis(pp) for pid, pp in seen.items()}
    templated = _templated({pid: t.lower() for pid, t in notes.items()})
    ok = short = anon = unfigured = boiler = 0
    for pid, pp in seen.items():
        note = notes[pid]
        members = [m for m in p_members(pp) if m in by_id]
        long_enough = len(note) >= 50
        identifies = pid in note or any(m in note for m in members)
        figures = []
        for key in (("incident_count", "incidents", "member_count"),
                    ("countable_count", "countable", "countable_incidents")):
            v = num(get(pp, *key))
            if v is not None:
                figures.append(int(v))
        quotes_own_figure = any(
            re.search(r"(?<![\d,.])" + str(v) + r"(?!\d)(?!\.\d)", note) for v in figures)
        specific = pid not in templated
        if not long_enough:
            short += 1
        if not identifies:
            anon += 1
        if not quotes_own_figure:
            unfigured += 1
        if not specific:
            boiler += 1
        if long_enough and identifies and quotes_own_figure and specific:
            ok += 1
    return ok / max(1, len(seen)), [
        "%d/%d declared patterns carry a basis note that is substantial, names its own pattern "
        "or one of its own member reports, and quotes one of that pattern's own counts"
        % (ok, len(seen)),
        "%d notes are too short, %d name neither the pattern nor any of its members, %d quote "
        "none of the pattern's own figures, and %d are near-wholly contained in another "
        "pattern's note" % (short, anon, unfigured, boiler)]


def check_memo_determination_fidelity(memo_text, patterns, policy):
    if not patterns:
        return 0.0, ["no register patterns to reconcile the memo's determinations against"]
    if not memo_text.strip():
        return 0.0, ["no memo to read determinations from"]
    seen = {}
    for pp in patterns:
        pid = p_id(pp)
        if pid and pid not in seen:
            seen[pid] = pp
    if not seen:
        return 0.0, ["no patterns carry a pattern_id, so no determination can be attributed"]
    total = 0.0
    named = complete = 0
    miss = Counter()
    for pid, pp in seen.items():
        i = memo_text.find(pid)
        if i < 0:
            for f in ("brand family", "failure mode", "disposition", "countable count"):
                miss[f] += 1
            continue
        named += 1
        seg = memo_text[max(0, i - 80): i + MEMO_DETERMINATION_WINDOW].lower()
        brand = as_text(get(pp, "brand_family", "brand")).strip().lower()
        mode = canon_mode(as_text(get(pp, "failure_mode", "mode")))
        disp = canon_from(as_text(get(pp, "disposition", "outcome")), policy["dispositions"])
        cc = num(get(pp, "countable_count", "countable", "countable_incidents"))
        got = {
            "brand family": bool(brand) and brand in seg,
            "failure mode": bool(mode) and mode.lower() in seg,
            "disposition": bool(disp) and disp.lower() in seg,
            "countable count": cc is not None and bool(
                re.search(r"(?<![\d,.])" + str(int(cc)) + r"(?!\d)(?!\.\d)", seg)),
        }
        for f, v in got.items():
            if not v:
                miss[f] += 1
        total += sum(1 for v in got.values() if v) / len(got)
        if all(got.values()):
            complete += 1
    return total / max(1, len(seen)), [
        "%d/%d declared patterns are named in the memo and %d carry a determination stating the "
        "brand family, failure mode, disposition and countable count the register gives them"
        % (named, len(seen), complete),
        "patterns missing each element: " + ", ".join("%s=%d" % (f, miss[f]) for f in
            ("brand family", "failure mode", "disposition", "countable count"))]


def check_countable_population_oracle(incidents, by_id):
    first = first_rows(incidents, by_id)
    tp = fp = fn = tn = 0
    for rn, g in by_id.items():
        r = first.get(rn)
        grade = i_grade(r) if r is not None else None
        got = grade in COUNTABLE_GRADES if grade is not None else None
        want = g["primary_grade"] in COUNTABLE_GRADES
        if got is True and want:
            tp += 1
        elif got is True and not want:
            fp += 1
        elif got is not True and want:
            fn += 1
        elif got is False and not want:
            tn += 1
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    acc = (tp + tn) / max(1, len(by_id))
    return (f1 + acc) / 2, [
        "incidents that count toward a reportability trigger: %d identified correctly, %d counted "
        "that the account and the firm's response do not support, %d genuinely countable incidents "
        "missed (precision %.3f, recall %.3f, agreement %.3f over %d reports)"
        % (tp, fp, fn, prec, rec, acc, len(by_id))]


def check_brand_family_resolution(incidents, by_id, policy):
    fams = brand_family_options(policy)
    first = first_rows(incidents, by_id)
    ok = sum(1 for rn, r in first.items()
             if canon_brand(i_brand(r), fams) == by_id[rn]["brand_family"])
    return ok / max(1, len(by_id)), [
        "%d/%d reports resolved to the brand family the published register maps their reported "
        "brand string to" % (ok, len(by_id))]


def check_failure_mode_unambiguous(incidents, by_id):
    first = first_rows(incidents, by_id)
    subset = [rn for rn, g in by_id.items() if g["strict_mode"]]
    ok = sum(1 for rn in subset if rn in first and i_mode(first[rn]) == by_id[rn]["strict_mode"])
    return ok / max(1, len(subset)), [
        "%d/%d reports whose account carries exactly one unambiguous failure cue are classified "
        "into the family that cue names" % (ok, len(subset))]


def check_harm_unambiguous(incidents, by_id):
    first = first_rows(incidents, by_id)
    ends = {}
    for level in ("H0", "H3"):
        subset = [rn for rn, g in by_id.items() if g["strict_harm"] == level]
        ok = sum(1 for rn in subset if rn in first and i_harm(first[rn]) == level)
        ends[level] = (ok, len(subset))
    parts = [ok / n for ok, n in ends.values() if n]
    return (sum(parts) / len(parts) if parts else 0.0), [
        "reports whose account settles the harm question outright, scored at each end separately: "
        "%d/%d that describe no harm at all sit at H0, and %d/%d that describe an emergency or "
        "severe outcome sit at H3" % (ends["H0"][0], ends["H0"][1], ends["H3"][0], ends["H3"][1])]


def check_severity_conflict_detection(incidents, by_id):
    first = first_rows(incidents, by_id)
    subset = [rn for rn, g in by_id.items() if g["coded_comparable"]]
    tp = fp = fn = tn = 0
    for rn in subset:
        r = first.get(rn)
        got = i_conflict(r) if r is not None else None
        want = by_id[rn]["severity_conflict"]
        if got is True and want:
            tp += 1
        elif got is True and not want:
            fp += 1
        elif got is not True and want:
            fn += 1
        elif got is False and not want:
            tn += 1
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    acc = (tp + tn) / max(1, len(subset))
    return (f1 + acc) / 2, [
        "coded-severity disagreement over the %d reports whose coded value is comparable: "
        "%d found correctly, %d claimed where the account agrees with the code, %d real "
        "disagreements missed (precision %.3f, recall %.3f, accuracy %.3f)"
        % (len(subset), tp, fp, fn, prec, rec, acc)]


def _support(incidents, by_id, alt_key, primary_key, reader, label, classes, subset=None):
    first = first_rows(incidents, by_id)
    ids = subset if subset is not None else list(by_id)
    credit = 0.0
    exact = alt = 0
    declared = defaultdict(lambda: [0.0, 0])
    actual = defaultdict(lambda: [0.0, 0])
    for rn in ids:
        g = by_id[rn]
        r = first.get(rn)
        got = reader(r) if r is not None else None
        if got is not None and got == g[primary_key]:
            c = 1.0
            exact += 1
        elif got is not None and got in g[alt_key]:
            c = ALTERNATE_READING_CREDIT
            alt += 1
        else:
            c = 0.0
        credit += c
        if got is not None:
            declared[got][0] += c
            declared[got][1] += 1
        actual[g[primary_key]][0] += c
        actual[g[primary_key]][1] += 1
    micro = credit / max(1, len(ids))
    live = [c for c in classes if actual.get(c, [0, 0])[1] >= 5]
    if not live:
        live = [c for c in classes if actual.get(c, [0, 0])[1] > 0] or classes
    precision = sum(declared[c][0] / max(1, declared[c][1]) for c in live if c in declared) / max(1, len(live))
    recall = sum(actual[c][0] / max(1, actual[c][1]) for c in live if c in actual) / max(1, len(live))
    macro = min(1.0, (min(1.0, precision) + min(1.0, recall)) / 2)
    breakdown = ", ".join("%s=%.1f/%d" % (c, actual[c][0], actual[c][1]) for c in sorted(actual))
    return (micro + macro) / 2, [
        "%d reports %s, and %d more take a different reading the same account also evidences "
        "(scored %.1f) -- %.1f/%d credit" % (exact, label, alt, ALTERNATE_READING_CREDIT, credit, len(ids)),
        "class-balanced support %.4f over the %d classes carrying at least five reports "
        "(per class read from the accounts: %s)" % (macro, len(live), breakdown)]


def check_failure_mode_support(incidents, by_id):
    return _support(incidents, by_id, "modes", "primary_mode", i_mode,
                    "declare the failure-mode family the published precedence order reads out of "
                    "their account", MODE_ORDER)


def check_harm_support(incidents, by_id):
    def alt_reader(r):
        return i_harm(r) if r is not None else None

    first = first_rows(incidents, by_id)
    credit = 0.0
    exact = adj = 0
    actual = defaultdict(lambda: [0.0, 0])
    declared = defaultdict(lambda: [0.0, 0])
    for rn, g in by_id.items():
        got = alt_reader(first.get(rn))
        want = g["harm"]
        if got == want:
            c = 1.0
            exact += 1
        elif got in HARM_RANK and abs(HARM_RANK[got] - HARM_RANK[want]) == 1:
            c = ALTERNATE_READING_CREDIT
            adj += 1
        else:
            c = 0.0
        credit += c
        if got:
            declared[got][0] += c
            declared[got][1] += 1
        actual[want][0] += c
        actual[want][1] += 1
    micro = credit / max(1, len(by_id))
    live = [c for c in HARM_RANK if actual.get(c, [0, 0])[1] >= 5] or list(HARM_RANK)
    precision = sum(declared[c][0] / max(1, declared[c][1]) for c in live if c in declared) / max(1, len(live))
    recall = sum(actual[c][0] / max(1, actual[c][1]) for c in live if c in actual) / max(1, len(live))
    macro = min(1.0, (min(1.0, precision) + min(1.0, recall)) / 2)
    return (micro + macro) / 2, [
        "%d reports sit at the harm level their own account substantiates and %d more sit one "
        "level away (scored %.1f) -- %.1f/%d credit"
        % (exact, adj, ALTERNATE_READING_CREDIT, credit, len(by_id)),
        "class-balanced harm support %.4f (per level read from the accounts: %s)"
        % (macro, ", ".join("%s=%.1f/%d" % (c, actual[c][0], actual[c][1]) for c in sorted(actual)))]


def check_posture_support(incidents, by_id):
    subset = [rn for rn, g in by_id.items() if g["has_comment"]]
    return _support(incidents, by_id, "postures", "primary_posture", i_posture,
                    "carry the posture the method's precedence order reads out of the response the "
                    "firm actually filed", POSTURE_ORDER[:-1], subset=subset)


def _members_claiming(patterns, ap, by_id):
    v = p_members(ap)
    return [m for m in v if m in by_id]


def _agent_pattern_by_key(patterns, policy):
    fams = brand_family_options(policy)
    out = {}
    for p in patterns:
        b, m = p_key(p)
        key = (canon_brand(b, fams), m)
        if key[0] and key[1] and key not in out:
            out[key] = p
    return out


def check_pattern_consolidation_oracle(patterns, by_id, policy, ref_pats):
    if not patterns:
        return 0.0, ["no patterns to compare against the corpus-derived pattern set"]
    agent = _agent_pattern_by_key(patterns, policy)
    cat_of = {rn: g["product_category"] for rn, g in by_id.items()}
    single, multi = [], []
    for key, rp in ref_pats.items():
        want = set(rp["members"])
        ap = agent.get(key)
        got = set(m for m in p_members(ap) if m in by_id) if ap is not None else set()
        union = want | got
        jac = len(want & got) / len(union) if union else 0.0
        spans = len({cat_of.get(m) for m in want}) > 1
        (multi if spans else single).append(jac)
    allj = single + multi
    score = sum(allj) / max(1, len(allj))
    return score, [
        "member overlap against the %d hazard patterns the corpus yields: %.4f mean Jaccard "
        "overall" % (len(allj), score),
        "%.4f over the %d patterns whose incidents sit in one product category, and %.4f over "
        "the %d whose incidents span several -- a pattern left split along the category "
        "boundary the reading was divided on holds only part of its own members"
        % ((sum(single) / len(single)) if single else 0.0, len(single),
           (sum(multi) / len(multi)) if multi else 0.0, len(multi))]


def check_trigger_exposure_oracle(patterns, by_id, policy, ref_pats):
    if not patterns:
        return 0.0, ["no patterns to compare against the corpus-derived trigger arithmetic"]
    agent = _agent_pattern_by_key(patterns, policy)
    scored = 0.0
    n = 0
    matched = rule_ok = date_ok = exp_ok = 0
    for key, rp in ref_pats.items():
        n += 1
        ap = agent.get(key)
        if ap is None:
            continue
        matched += 1
        got_rule = canon_rule(get(ap, "trigger_rule", "rule"))
        got_date = canon_date(get(ap, "trigger_date", "triggered_on"))
        got_exp = num(get(ap, "exposure_days", "exposure"))
        parts = [1.0 if got_rule == rp["trigger_rule"] else 0.0]
        if rp["trigger_date"] is None:
            parts.append(1.0 if got_date is None else 0.0)
        elif got_date is None:
            parts.append(0.0)
        else:
            d = abs((got_date - rp["trigger_date"]).days)
            parts.append(1.0 if d == 0 else (0.5 if d <= 14 else 0.0))
        want_exp = rp["exposure_days"]
        if got_exp is None:
            parts.append(0.0)
        else:
            d = abs(got_exp - want_exp)
            parts.append(1.0 if d < 0.5 else (0.5 if d <= 14 else 0.0))
        rule_ok += parts[0]
        date_ok += parts[1]
        exp_ok += parts[2]
        scored += sum(parts) / len(parts)
    return scored / max(1, n), [
        "%d/%d hazard patterns the corpus itself yields are present in the register under the "
        "same (brand family, failure mode) key" % (matched, n),
        "against the trigger arithmetic re-derived from the corpus: %.1f patterns carry the rule "
        "that fires, %.1f the trigger date (half credit within 14 days) and %.1f the exposure "
        "days (half credit within 14 days)" % (rule_ok, date_ok, exp_ok)]


def check_disposition_docket_oracle(patterns, docket_rows, by_id, policy, ref_pats):
    if not patterns and not docket_rows:
        return 0.0, ["no patterns or docket rows to compare against the corpus-derived docket"]
    agent = _agent_pattern_by_key(patterns, policy)
    fams = brand_family_options(policy)
    disp_ok = 0
    n = len(ref_pats)
    for key, rp in ref_pats.items():
        ap = agent.get(key)
        if ap is None:
            continue
        got = canon_from(as_text(get(ap, "disposition", "outcome")), policy["dispositions"])
        if got == rp["disposition"]:
            disp_ok += 1
    ref_seated = {k for k, p in ref_pats.items() if p["disposition"] == "Board Docketed"}
    docket_keys = set()
    by_pid = {}
    for p in patterns:
        pid = p_id(p)
        b, m = p_key(p)
        k = (canon_brand(b, fams), m)
        if pid and k[0] and k[1]:
            by_pid[pid] = k
    for r in docket_rows:
        pid = as_text(get(r, "pattern_id", "pattern", "id")).strip()
        if pid in by_pid:
            docket_keys.add(by_pid[pid])
        else:
            k = (canon_brand(as_text(get(r, "brand_family", "brand")), fams),
                 canon_mode(as_text(get(r, "failure_mode", "mode"))))
            if k[0] and k[1]:
                docket_keys.add(k)
    inter = len(ref_seated & docket_keys)
    prec = inter / max(1, len(docket_keys))
    rec = inter / max(1, len(ref_seated))
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return (disp_ok / max(1, n) + f1) / 2, [
        "%d/%d patterns carry the disposition the method assigns them once the trigger and the "
        "board's capacity are worked out from the corpus" % (disp_ok, n),
        "seated docket against the corpus-derived seating: %d of the %d patterns that should be "
        "heard this cycle are on the docket, out of %d rows seated (precision %.3f, recall %.3f)"
        % (inter, len(ref_seated), len(docket_keys), prec, rec)]


def write_reward_json(reward_out, reward, totals):
    path = os.path.join(os.path.dirname(reward_out) or ".", "reward.json")
    payload = {"reward": round(reward, 4),
               "total_static_check_score": round(totals.get("static_checks", 0.0), 4),
               "total_reward_hacking_check_score": round(totals.get("reward_hacking_checks", 0.0), 4),
               "total_partial_oracle_check_score": round(totals.get("partial_oracle_checks", 0.0), 4)}
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
    except OSError as ex:
        print("WARN: could not write reward.json: %s" % ex)
    return payload


def write_status(reward_out, payload):
    path = os.path.join(os.path.dirname(reward_out) or ".", "verifier_status.json")
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
    except OSError as ex:
        print("WARN: could not write verifier status: %s" % ex)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-output", default="/logs/agent/hazard_register.json")
    ap.add_argument("--docket", default="/logs/agent/board_docket.csv")
    ap.add_argument("--memo", default="/logs/agent/hazard_review_memo.md")
    ap.add_argument("--agent-dir", default="/logs/agent")
    ap.add_argument("--reward-out", default="/logs/verifier/reward.txt")
    args = ap.parse_args()

    policy = json.load(open(os.path.join(REF_DIR, "policy_constants.json"), encoding="utf-8"))
    by_id = load_reference(policy)
    ref_pats = build_reference_patterns(by_id, policy)
    incidents, patterns, summary, reg_err = load_register(args.agent_output)
    docket_rows = load_docket(args.docket)
    memo_text = read_text(args.memo)

    buckets = [
        ("static_checks", [
            ("output_files_present", lambda: check_output_files_present(incidents, docket_rows, memo_text)),
            ("incident_coverage", lambda: check_incident_coverage(incidents, by_id)),
            ("schema_valid", lambda: check_schema_valid(incidents, by_id, policy)),
            ("brand_family_resolution", lambda: check_brand_family_resolution(incidents, by_id, policy)),
        ]),
        ("reward_hacking_checks", [
            ("no_duplicate_incidents", lambda: check_no_duplicate_incidents(incidents, by_id)),
            ("rationale_grounding", lambda: check_rationale_grounding(incidents, by_id)),
            ("pattern_partition_integrity", lambda: check_pattern_partition_integrity(incidents, patterns, by_id)),
            ("pattern_key_consistency", lambda: check_pattern_key_consistency(incidents, patterns, by_id, policy)),
            ("countable_count_consistency", lambda: check_countable_count_consistency(incidents, patterns, by_id)),
            ("grade_derivation_consistency", lambda: check_grade_derivation_consistency(incidents, by_id)),
            ("trigger_internal_consistency", lambda: check_trigger_internal_consistency(incidents, patterns, by_id, policy)),
            ("docket_ordering_and_capacity", lambda: check_docket_ordering_and_capacity(patterns, docket_rows, policy)),
            ("summary_consistency", lambda: check_summary_consistency(incidents, patterns, summary, by_id, policy, ref_pats)),
            ("memo_structure", lambda: check_memo_structure(memo_text, incidents, patterns, by_id)),
            ("memo_register_agreement", lambda: check_memo_register_agreement(memo_text, incidents, patterns, by_id, policy, ref_pats)),
            ("docket_register_agreement", lambda: check_docket_register_agreement(patterns, docket_rows, policy)),
            ("basis_grounding", lambda: check_basis_grounding(patterns, incidents, by_id)),
            ("memo_determination_fidelity", lambda: check_memo_determination_fidelity(memo_text, patterns, policy)),
        ]),
        ("partial_oracle_checks", [
            ("countable_population_oracle", lambda: check_countable_population_oracle(incidents, by_id)),
            ("failure_mode_unambiguous", lambda: check_failure_mode_unambiguous(incidents, by_id)),
            ("failure_mode_support", lambda: check_failure_mode_support(incidents, by_id)),
            ("harm_unambiguous", lambda: check_harm_unambiguous(incidents, by_id)),
            ("harm_support", lambda: check_harm_support(incidents, by_id)),
            ("severity_conflict_detection", lambda: check_severity_conflict_detection(incidents, by_id)),
            ("posture_support", lambda: check_posture_support(incidents, by_id)),
            ("pattern_consolidation_oracle", lambda: check_pattern_consolidation_oracle(patterns, by_id, policy, ref_pats)),
            ("trigger_exposure_oracle", lambda: check_trigger_exposure_oracle(patterns, by_id, policy, ref_pats)),
            ("disposition_docket_oracle", lambda: check_disposition_docket_oracle(patterns, docket_rows, by_id, policy, ref_pats)),
        ]),
    ]

    scores, detail, errored = [], [], []
    bucket_scores = {b: [] for b, _ in buckets}
    for bucket, checks in buckets:
        detail.append("[%s]" % bucket)
        for name, fn in checks:
            try:
                s, lines = fn()
            except Exception as ex:
                errored.append({"check": name, "error": "%s: %s" % (type(ex).__name__, ex),
                                "traceback": traceback.format_exc()})
                s, lines = 0.0, ["VERIFIER_ERROR the check itself raised %s: %s -- this 0 is a "
                                 "verifier failure, not a graded result" % (type(ex).__name__, ex)]
            s = max(0.0, min(1.0, float(s)))
            scores.append(s)
            bucket_scores[bucket].append(s)
            detail.append("  %-30s %6s" % (name, round(s, 4)))
            for l in lines:
                detail.append("      %s" % l)

    totals = {b: round(sum(v) / len(v), 4) if v else 0.0 for b, v in bucket_scores.items()}
    reward = round(sum(totals[b] * w for b, w in BUCKET_WEIGHTS.items()) / sum(BUCKET_WEIGHTS.values()), 4)

    out = ["Hazard-pattern reportability review score = %s" % reward,
           "reward = (total_static_check_score*1 + total_reward_hacking_check_score*2 + "
           "total_partial_oracle_check_score*3) / 6; each bucket total is the plain mean of its own "
           "weight-1 checks, no caps, floors, multipliers or mode branches",
           "bucket totals: static %s (%d checks), reward-hacking %s (%d checks), partial-oracle %s (%d checks)"
           % (totals["static_checks"], len(bucket_scores["static_checks"]),
              totals["reward_hacking_checks"], len(bucket_scores["reward_hacking_checks"]),
              totals["partial_oracle_checks"], len(bucket_scores["partial_oracle_checks"])),
           "corpus reports = %d; corpus-derived patterns = %d; register rows = %d; declared patterns = %d; "
           "docket rows = %d%s" % (len(by_id), len(ref_pats), len(incidents), len(patterns),
                                   len(docket_rows), ("; register load error: %s" % reg_err) if reg_err else ""),
           ""] + detail
    if errored:
        out.insert(3, "VERIFIER_ERROR %d check(s) failed to execute: %s"
                   % (len(errored), ", ".join(e["check"] for e in errored)))

    write_status(args.reward_out, {"status": "check_error" if errored else "ok", "reward": reward,
                                   "reward_is_graded": not errored, "checks_total": len(scores),
                                   "bucket_totals": totals, "checks_failed_to_execute": errored,
                                   "register_load_error": reg_err})
    try:
        os.makedirs(os.path.dirname(args.reward_out), exist_ok=True)
        with open(args.reward_out, "w") as f:
            f.write(str(reward))
    except OSError as ex:
        print("WARN: could not write reward: %s" % ex)
    write_reward_json(args.reward_out, reward, totals)
    try:
        with open(os.path.join(args.agent_dir, "judge_justification.txt"), "w") as f:
            f.write("Score: %s\n\n%s" % (reward, "\n".join(out)))
    except OSError:
        pass
    print("\n".join(out))
    print("\nScore: %s" % reward)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        reward_out = "/logs/verifier/reward.txt"
        argv = sys.argv
        if "--reward-out" in argv:
            reward_out = argv[argv.index("--reward-out") + 1]
        write_status(reward_out, {"status": "verifier_crashed", "reward_is_graded": False,
                                  "error": traceback.format_exc()})
        print("VERIFIER_ERROR verify.py crashed before scoring:\n" + traceback.format_exc(), file=sys.stderr)
        raise SystemExit(3)
