#!/usr/bin/env python3
import concurrent.futures as cf
import json
import os
import re
import shutil
import sys
import time
import traceback
import unicodedata
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.environ.get("AGENT_DIR", "/logs/agent")
BRIEF_DIR = os.environ.get("VERIFY_BRIEF_DIR", os.path.join(AGENT, "briefs"))
INPUTS = os.environ.get("INPUT_DIR", "/input_artifacts")
PROXY_DIR = os.path.join(INPUTS, "proxies")
REWARD_JSON_PATH = os.environ.get("REWARD_JSON_PATH", "/logs/verifier/reward.json")
KEY_PATH = os.environ.get("VERIFY_KEY_PATH", os.path.join(HERE, "proxy_key.json"))
ORACLE_PATH = os.path.join(HERE, "partial_oracle.json")

WANDB_API = os.environ.get(
    "JUDGE_URL", "https://api.inference.wandb.ai/v1/chat/completions"
)
# Same judge stack as the working language-memory-models survey: requests client
# (installed in test.sh) + model fallback list. urllib alone hits Cloudflare 1010.
JUDGE_MODELS = [
    m.strip()
    for m in os.environ.get(
        "JUDGE_MODELS",
        os.environ.get(
            "JUDGE_MODEL",
            "deepseek-ai/DeepSeek-V4-Flash,moonshotai/Kimi-K2.6",
        ),
    ).split(",")
    if m.strip()
]
OPENAI_PROJECT = os.environ.get(
    "OPENAI_PROJECT",
    os.environ.get("WANDB_PROJECT", "meta-hopfield/multi-agent-swarm"),
)
JUDGE_WORKERS = int(os.environ.get("JUDGE_WORKERS", "4"))
JUDGE_TIMEOUT = int(os.environ.get("JUDGE_TIMEOUT", "180"))
BRIEF_CHAR_LIMIT = int(os.environ.get("VERIFY_BRIEF_CHAR_LIMIT", "45000"))
_MODEL_STATE = {"active": None}
MAX_VERBATIM_RATIO = 0.15
MIN_VERBATIM_RATIO = 0.005
MIN_UNIQUE_RATIO = 0.28
SECTION_BODY_MIN_WORDS = 25

REQUIRED_HEADINGS = [
    "## Company and meeting",
    "## Board and governance structure",
    "## Executive compensation design",
    "## Pay-for-performance and say-on-pay",
    "## Related-party and conflict flags",
    "## Shareholder voting takeaway",
]

GOV_TERMS = ("board", "director", "committee", "independent", "chair", "nominee")
COMP_TERMS = ("compensation", "pay", "bonus", "equity", "rsu", "psu", "salary", "incentive")
REASONING_MARKERS = (
    "because", "however", "therefore", "weigh", "risk", "concern",
    "strength", "weakness", "implication", "should", "versus", "compared",
)

GROUNDING_KEYS = [
    "identity_correct",
    "governance_grounded",
    "compensation_grounded",
    "sayonpay_relatedparty_grounded",
]
DEPTH_KEYS = [
    "kp_board_independence",
    "kp_comp_design",
    "kp_pay_performance",
    "kp_sayonpay",
    "kp_related_party",
    "kp_shareholder_takeaway",
    "specific_to_this_company",
    "no_contradiction",
]


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def collapsed(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def alnum_fold(value):
    text = unicodedata.normalize("NFKD", collapsed(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", text)


def read_briefs(brief_dir):
    out = {}
    if not os.path.isdir(brief_dir):
        return out
    for fn in os.listdir(brief_dir):
        if not fn.lower().endswith(".md"):
            continue
        bn = fn[:-3].strip().lower()
        out[bn] = read_text(os.path.join(brief_dir, fn))
    return out


def freeze_briefs(src, dst):
    try:
        if os.path.isdir(dst):
            shutil.rmtree(dst, ignore_errors=True)
        os.makedirs(dst, exist_ok=True)
        if os.path.isdir(src):
            for fn in os.listdir(src):
                if fn.lower().endswith(".md"):
                    try:
                        shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
                    except OSError:
                        pass
        return dst
    except OSError:
        return src


def _proxy_header_and_body(proxy):
    lines = (proxy or "").splitlines()
    header_lines = []
    body_start = 0
    for i, line in enumerate(lines[:40]):
        if i < 12 or re.match(r"(?i)^(company|ticker|cik|form|filing)\b", line.strip()):
            header_lines.append(line)
            body_start = i + 1
            continue
        if line.strip() == "" and i < 15:
            header_lines.append(line)
            body_start = i + 1
            continue
        break
    header = "\n".join(lines[: max(body_start, 8)])
    body = "\n".join(lines[max(body_start, 8):])
    return header, body


def _section_bodies(text):
    bodies = {}
    if not text:
        return bodies
    pattern = re.compile(r"(?im)^(##\s+[^\n]+)\s*$")
    matches = list(pattern.finditer(text))
    for idx, match in enumerate(matches):
        heading = re.sub(r"\s+", " ", match.group(1)).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        bodies[heading.lower()] = text[start:end].strip()
    return bodies


def _unique_word_ratio(text):
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9']+", text or "")]
    if len(words) < 40:
        return 0.0
    return len(set(words)) / len(words)


def _verbatim_overlap_ratio(brief, proxy_body):
    if not brief or not proxy_body:
        return 0.0
    brief_words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'/-]*", brief)
    if len(brief_words) < 40:
        return 0.0
    proxy_c = collapsed(proxy_body)
    covered = 0
    i = 0
    while i < len(brief_words) - 5:
        span = " ".join(brief_words[i:i + 6]).lower()
        if len(span) >= 28 and span in proxy_c:
            covered += 6
            i += 6
            continue
        i += 1
    return covered / len(brief_words)


def _term_hits(text, terms):
    low = collapsed(text)
    return [term for term in terms if re.search(r"\b%s\b" % re.escape(term), low)]


class Context:
    def __init__(self):
        self.key = load_json(KEY_PATH) or {}
        self.oracle = load_json(ORACLE_PATH) or {}
        self.expected = sorted(self.key.keys())
        frozen = os.environ.get("VERIFY_FROZEN_DIR") or "/logs/verifier/briefs_frozen"
        if not os.path.isdir(frozen) or not any(
            fn.endswith(".md") for fn in os.listdir(frozen) if os.path.isfile(os.path.join(frozen, fn))
        ):
            freeze_briefs(BRIEF_DIR, frozen)
        self.briefs = read_briefs(frozen if os.path.isdir(frozen) else BRIEF_DIR)
        self.proxy_text = {}
        self.proxy_header = {}
        self.proxy_body = {}
        for ticker in self.expected:
            path = os.path.join(PROXY_DIR, ticker + ".txt")
            if not os.path.isfile(path):
                path = os.path.join(HERE, "..", "environment", "input_artifacts", "proxies", ticker + ".txt")
            text = read_text(path)
            self.proxy_text[ticker] = text
            header, body = _proxy_header_and_body(text)
            self.proxy_header[ticker] = header
            self.proxy_body[ticker] = body
        self.api_key = os.environ.get("WANDB_API_KEY")
        self.llm_audit = []


def _mean(values):
    return sum(values) / len(values) if values else 0.0


TOPIC_TERMS = tuple(sorted(set(GOV_TERMS + COMP_TERMS)))


def _is_topical(text):
    low = collapsed(text)
    return any(re.search(r"\b%s\b" % re.escape(term), low) for term in TOPIC_TERMS)


def _topical_body_span_in_brief(body, brief, brief_c, step=17, window=6):
    # Returns True only if a governance/compensation-bearing multi-word span from the
    # proxy body appears verbatim in the brief, so arbitrary copied text does not count.
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'/-]*", body or "")
    for i in range(0, max(0, len(words) - window + 1), step):
        span = " ".join(words[i:i + window])
        if len(span) < 28 or not _is_topical(span):
            continue
        if span in brief:
            return True
        short = collapsed(" ".join(words[i:i + 5]))
        if len(short) >= 24 and _is_topical(short) and short in brief_c:
            return True
    return False


def _sentences(text):
    return re.split(r"(?<=[.!?])\s+", collapsed(text))


def _reasoning_on_claim(text):
    # Counts sentences where a reasoning marker co-occurs with a governance/compensation
    # term, i.e. analysis applied to an actual claim rather than a bare connective word.
    count = 0
    for sent in _sentences(text):
        if not sent:
            continue
        has_marker = any(re.search(r"\b%s\b" % m, sent) for m in REASONING_MARKERS)
        if has_marker and _is_topical(sent):
            count += 1
    return count


def check_brief_coverage(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    present = sum(1 for t in ctx.expected if (ctx.briefs.get(t) or "").strip())
    return present / len(ctx.expected), "%d/%d expected company briefs present" % (present, len(ctx.expected))


def check_required_sections(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    good = 0
    for ticker in ctx.expected:
        text = ctx.briefs.get(ticker, "")
        if not text.strip():
            continue
        bodies = _section_bodies(text)
        ok = True
        for heading in REQUIRED_HEADINGS:
            body = bodies.get(heading.lower(), "")
            if len(body.split()) < SECTION_BODY_MIN_WORDS:
                ok = False
                break
        if ok:
            good += 1
    return (
        good / len(ctx.expected),
        "%d/%d briefs have all six required headings each followed by >=%d words of body"
        % (good, len(ctx.expected), SECTION_BODY_MIN_WORDS),
    )


def check_heading_format(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    good = 0
    for ticker in ctx.expected:
        text = ctx.briefs.get(ticker, "")
        if not text.strip():
            continue
        # Anchor to the first non-blank line only (document open).
        first_line = ""
        for line in text.splitlines():
            if line.strip():
                first_line = line.rstrip()
                break
        company = (ctx.key.get(ticker) or {}).get("company", "")
        pat = re.compile(r"(?i)^#\s+.+\(" + re.escape(ticker.upper()) + r"\)")
        name_tok = alnum_fold(company.split()[0]) if company else ""
        if pat.search(first_line) and (not name_tok or len(name_tok) <= 2 or name_tok in alnum_fold(first_line)):
            good += 1
    return good / len(ctx.expected), "%d/%d briefs open on the first non-blank line with a level-1 heading naming the ticker" % (good, len(ctx.expected))


def check_brief_length_floor(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    good = 0
    for ticker in ctx.expected:
        text = ctx.briefs.get(ticker, "")
        words = text.split()
        if len(words) >= 250 and _unique_word_ratio(text) >= MIN_UNIQUE_RATIO:
            good += 1
    return (
        good / len(ctx.expected),
        "%d/%d briefs have >=250 words and unique-word ratio >=%.2f"
        % (good, len(ctx.expected), MIN_UNIQUE_RATIO),
    )


def check_deliverable_paths(ctx):
    if not any((ctx.briefs.get(t) or "").strip() for t in ctx.expected):
        return 0.0, "no briefs delivered; path hygiene not credited on an empty submission"
    violations = []
    if os.path.isdir(INPUTS):
        for name in os.listdir(INPUTS):
            if name == "proxies":
                continue
            path = os.path.join(INPUTS, name)
            if os.path.isfile(path):
                violations.append("extra file under /input_artifacts: " + name)
            elif os.path.isdir(path):
                violations.append("extra directory under /input_artifacts: " + name)
        proxy_dir = os.path.join(INPUTS, "proxies")
        if os.path.isdir(proxy_dir):
            for name in os.listdir(proxy_dir):
                if not name.lower().endswith(".txt"):
                    violations.append("non-proxy file under proxies/: " + name)
    if os.path.isdir(AGENT):
        for name in os.listdir(AGENT):
            if name in ("briefs", "briefs_index.md", "opencode.txt", "opencode-internal.log",
                        "trajectory.json", "raw_trajectory", "setup", "sessions"):
                continue
            path = os.path.join(AGENT, name)
            if os.path.isfile(path) and name.lower().endswith(".md"):
                stem = name[:-3].lower()
                if stem in ctx.expected:
                    violations.append("ticker brief outside briefs/: " + name)
    if violations:
        return 0.0, "path hygiene failures: " + "; ".join(violations[:6])
    return 1.0, "deliverables confined to /logs/agent/briefs/; /input_artifacts unmodified"


def check_ticker_identity(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    good = 0
    for ticker in ctx.expected:
        brief = ctx.briefs.get(ticker, "")
        text = collapsed(brief)
        row = ctx.key.get(ticker) or {}
        company = collapsed(row.get("company", ""))
        if not text:
            continue
        name_ok = bool(company) and (
            company in text or any(tok in text for tok in company.split()[:2] if len(tok) > 3)
        )
        ticker_ok = ticker in text
        filing = str(row.get("filing_date", "") or "")
        year = filing[:4] if len(filing) >= 4 else ""
        filing_ok = (not year) or (year in text) or (collapsed(filing) in text)
        # Require at least one governance/compensation-bearing span from the proxy BODY
        # (not the short header), so arbitrary copied text does not count as engagement.
        body = ctx.proxy_body.get(ticker, "")
        body_hit = _topical_body_span_in_brief(body, brief, text, step=23)
        if ticker_ok and name_ok and filing_ok and body_hit:
            good += 1
    return (
        good / len(ctx.expected),
        "%d/%d briefs identify company/ticker/filing year and carry a topical body-derived proxy span"
        % (good, len(ctx.expected)),
    )


def check_proxy_phrase_grounding(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    scores = []
    for ticker in ctx.expected:
        brief = ctx.briefs.get(ticker, "")
        body = ctx.proxy_body.get(ticker, "")
        if not brief.strip() or not body:
            scores.append(0.0)
            continue
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'/-]*", body)
        hits = 0
        seen = set()
        for i in range(0, max(0, len(words) - 5), 17):
            span = " ".join(words[i:i + 6])
            key = span.lower()
            if len(span) < 28 or key in seen:
                continue
            seen.add(key)
            # Only governance/compensation-bearing spans count as topical grounding.
            if span in brief and _is_topical(span):
                hits += 1
            if hits >= 2:
                break
        ratio = _verbatim_overlap_ratio(brief, body)
        ground = 1.0 if hits >= 2 else (0.5 if hits == 1 else 0.0)
        if ratio > MAX_VERBATIM_RATIO:
            # Bulk copy satisfies spans as a side effect; discount heavily.
            copy_score = 0.0
        elif ratio < MIN_VERBATIM_RATIO and hits < 2:
            copy_score = 0.0
        else:
            copy_score = 1.0
        scores.append(0.5 * ground + 0.5 * copy_score)
    return (
        _mean(scores),
        "mean grounding+anti-copy score over %d companies = %.4f (need >=2 body spans and verbatim overlap <=%.0f%%)"
        % (len(ctx.expected), _mean(scores), MAX_VERBATIM_RATIO * 100),
    )


def check_no_templated_briefs(ctx):
    present = [t for t in ctx.expected if (ctx.briefs.get(t) or "").strip()]
    if len(present) < 2:
        return 0.0 if ctx.expected else 1.0, "too few briefs to test templating" if ctx.expected else "no expected companies"
    # Full-document scrubbed bodies (no 1200-char truncation) so later required
    # sections are inside the cross-brief comparison window.
    bodies = []
    for ticker in present:
        text = collapsed(ctx.briefs.get(ticker, ""))
        row = ctx.key.get(ticker) or {}
        scrubbed = text
        for token in [ticker, collapsed(row.get("company", "")), collapsed(row.get("ticker", ""))]:
            if token:
                scrubbed = scrubbed.replace(token, " ")
        bodies.append((ticker, re.sub(r"\s+", " ", scrubbed).strip()))
    worst = 1
    for i in range(len(bodies)):
        ba = set(re.findall(r"\w+\s+\w+", bodies[i][1]))
        for j in range(i + 1, len(bodies)):
            bb = set(re.findall(r"\w+\s+\w+", bodies[j][1]))
            if not ba or not bb:
                continue
            overlap = len(ba & bb) / max(1, min(len(ba), len(bb)))
            if overlap > 0.85:
                worst = max(worst, 2)
            if overlap > 0.95:
                worst = max(worst, 3)
    template_score = 0.0 if worst >= 3 else (0.4 if worst >= 2 else 1.0)
    # Each brief must also be grounded in its OWN proxy (topical body span), so a
    # distinct-but-ungrounded submission cannot pass on cross-brief distinctness alone.
    grounded = 0
    for ticker in present:
        brief = ctx.briefs.get(ticker, "")
        body = ctx.proxy_body.get(ticker, "")
        if _topical_body_span_in_brief(body, brief, collapsed(brief), step=17):
            grounded += 1
    ground_share = grounded / len(present)
    score = 0.5 * template_score + 0.5 * ground_share
    return (
        score,
        "template_score=%.2f (full-doc bigram overlap) and %d/%d briefs grounded in own proxy"
        % (template_score, grounded, len(present)),
    )


def check_brief_synthesis(ctx):
    if not ctx.expected:
        return 0.0, "proxy key missing"
    scores = []
    for ticker in ctx.expected:
        brief = ctx.briefs.get(ticker, "")
        body = ctx.proxy_body.get(ticker, "")
        if not brief.strip():
            scores.append(0.0)
            continue
        sections = _section_bodies(brief)
        board = sections.get("## board and governance structure", "")
        takeaway = sections.get("## shareholder voting takeaway", "")
        ratio = _verbatim_overlap_ratio(brief, body)
        paraphrase_ok = ratio <= MAX_VERBATIM_RATIO
        # Prefer briefs that are not pure copy: some paraphrase room below the cap.
        paraphrase_ok = paraphrase_ok and (ratio < 0.12 or len(brief.split()) >= 300)
        # Reasoning must be applied to an actual governance/compensation claim in the
        # same sentence, not a bare connective word counted anywhere in the section.
        reason_board = _reasoning_on_claim(board)
        reason_take = _reasoning_on_claim(takeaway)
        reason_ok = reason_board >= 1 and reason_take >= 1 and len(takeaway.split()) >= SECTION_BODY_MIN_WORDS
        # Company-specific token from body that is not in the short header.
        header_c = collapsed(ctx.proxy_header.get(ticker, ""))
        body_words = re.findall(r"[A-Za-z]{5,}", body)
        specific = False
        brief_c = collapsed(brief)
        seen = set()
        for w in body_words:
            lw = w.lower()
            if lw in seen or lw in header_c:
                continue
            seen.add(lw)
            if lw in brief_c:
                specific = True
                break
            if len(seen) > 400:
                break
        parts = [1.0 if paraphrase_ok else 0.0, 1.0 if reason_ok else 0.0, 1.0 if specific else 0.0]
        scores.append(_mean(parts))
    return _mean(scores), "mean synthesis score over %d companies = %.4f (paraphrase cap, reasoning markers, body-specific tokens)" % (len(ctx.expected), _mean(scores))


def _ref_block(k, include_depth=False):
    ref = (
        "COMPANY: %s\nTICKER: %s\nCIK: %s\nFILING DATE: %s\n\n"
        "CORPORATE GOVERNANCE (reference excerpt):\n%s\n\n"
        "COMPENSATION DISCUSSION AND ANALYSIS (reference excerpt):\n%s\n\n"
        "SAY-ON-PAY / ADVISORY VOTE (reference excerpt):\n%s\n\n"
        "RELATED-PERSON TRANSACTIONS (reference excerpt):\n%s\n"
    ) % (
        k.get("company", ""),
        k.get("ticker", ""),
        k.get("cik", ""),
        k.get("filing_date", ""),
        k.get("governance_excerpt", ""),
        k.get("cda_excerpt", ""),
        k.get("sayonpay_excerpt", ""),
        k.get("related_party_excerpt", ""),
    )
    if include_depth:
        lines = k.get("key_sentences") or []
        ref += "\nKEY SENTENCES (reference, verbatim; non-exhaustive):\n%s\n" % (
            "\n".join("- " + str(x) for x in lines) if lines else "(none extracted)"
        )
    return ref


def _post_judge(model, system, user, key, max_tokens=1800):
    # Mirrors language-memory-models survey `_post_judge`: prefer `requests`
    # (pip-installed in test.sh). Bare urllib User-Agent triggers Cloudflare 1010.
    payload = json.dumps({
        "model": model,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode("utf-8")
    headers = {
        "Authorization": "Bearer %s" % key,
        "Content-Type": "application/json",
        "OpenAI-Project": OPENAI_PROJECT,
        "User-Agent": "swarmbench-verifier/1.0 (+https://api.inference.wandb.ai)",
        "Accept": "application/json",
    }
    try:
        import requests
        resp = requests.post(
            WANDB_API, data=payload, headers=headers, timeout=JUDGE_TIMEOUT
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                "HTTP Error %s: %s body=%s"
                % (resp.status_code, resp.reason, (resp.text or "")[:300])
            )
        body = resp.json()
    except ImportError:
        req = urllib.request.Request(WANDB_API, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=JUDGE_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    choices = body.get("choices") or []
    msg = (choices[0].get("message") or {}) if choices else {}
    content = (msg.get("content") or "").strip()
    if not content:
        raise RuntimeError("empty content from judge model %s" % model)
    return content


def _call_model(system, user, key, max_tokens=1800):
    if _MODEL_STATE["active"]:
        return _post_judge(_MODEL_STATE["active"], system, user, key, max_tokens)
    last = ""
    for model in JUDGE_MODELS:
        try:
            content = _post_judge(model, system, user, key, max_tokens)
            _MODEL_STATE["active"] = model
            print("LLM_JUDGE_MODEL=%s" % model)
            return content
        except Exception as exc:
            last = "%s (%s)" % (type(exc).__name__, str(exc)[:180])
            time.sleep(1)
    raise RuntimeError(last or "no judge model available")


def _parse_obj(content):
    content = (content or "").replace("```json", "").replace("```", "")
    try:
        return json.loads(content.strip())
    except ValueError:
        pass
    if "{" in content and "}" in content:
        span = content[content.index("{"): content.rindex("}") + 1]
        try:
            return json.loads(span)
        except ValueError:
            pass
    raise ValueError("no json object in reply")


def _llm_grade_company(ticker, text, row, api_key, kind):
    if kind == "grounding":
        system = (
            "You are a corporate-governance analyst fact-checking a governance-and-pay brief about ONE real "
            "company's SEC proxy statement (DEF 14A). Use the reference excerpts drawn from that proxy. For each "
            "boolean field, mark TRUE only if the brief states the fact and it is consistent with the reference; "
            "mark FALSE if missing, wrong, contradicted, or too vague. Judge meaning, not exact wording. Reply "
            "with ONLY a JSON object containing the boolean keys and a short justification string."
        )
        keys = GROUNDING_KEYS
        user = (
            _ref_block(row) + "\n\nGOVERNANCE-AND-PAY BRIEF TO GRADE:\n" + text[:BRIEF_CHAR_LIMIT] + "\n\n"
            "Grade each true/false:\n"
            "identity_correct, governance_grounded, compensation_grounded, sayonpay_relatedparty_grounded.\n"
            "Also provide justification: one or two sentences naming what was grounded or missing.\n"
            "Reply with ONLY JSON of the form "
            '{"identity_correct": true, "governance_grounded": true, "compensation_grounded": true, '
            '"sayonpay_relatedparty_grounded": true, "justification": "..." }.'
        )
        max_tokens = 1600
    else:
        system = (
            "You are a demanding governance lead grading a governance-and-pay BRIEF about ONE real company's "
            "proxy against a frozen reference from that proxy. Restating facts is necessary but not sufficient. "
            "Reward company-specific reasoning. When in doubt, mark FALSE. Reply with ONLY a JSON object "
            "containing the boolean keys and a short justification string."
        )
        keys = DEPTH_KEYS
        user = (
            _ref_block(row, include_depth=True) + "\n\nGOVERNANCE-AND-PAY BRIEF TO GRADE:\n"
            + text[:BRIEF_CHAR_LIMIT] + "\n\n"
            "Grade each point true/false: kp_board_independence, kp_comp_design, kp_pay_performance, "
            "kp_sayonpay, kp_related_party, kp_shareholder_takeaway, specific_to_this_company, no_contradiction.\n"
            "Also provide justification: one or two sentences on depth and company-specificity.\n"
            "Reply with ONLY JSON including those boolean keys plus "
            '{"justification": "..."}.'
        )
        max_tokens = 1800
    obj = _parse_obj(_call_model(system, user, api_key, max_tokens=max_tokens))
    graded = {kk: bool(obj.get(kk)) for kk in keys}
    justification = str(obj.get("justification") or "").strip() or "no justification returned"
    return graded, justification


def _llm_bucket_score(ctx, kind, keys):
    # Match the canonical county-service pattern: if WANDB_API_KEY is missing or the
    # OpenAI client cannot be imported, skip the judge (score 1.0) rather than
    # collapsing the reward to a silent zero for an infrastructure gap.
    if not ctx.api_key:
        note = "LLM_JUDGE_STATUS=skipped reason=WANDB_API_KEY is not set"
        print(note)
        return 1.0, note
    if not ctx.expected:
        return 0.0, "proxy key missing"

    def work(ticker):
        text = ctx.briefs.get(ticker, "")
        row = ctx.key.get(ticker) or {}
        if not text.strip():
            return {
                "ticker": ticker,
                "status": "missing_brief",
                "score": 0.0,
                "graded": {},
                "justification": "no brief submitted",
            }
        try:
            graded, justification = _llm_grade_company(ticker, text, row, ctx.api_key, kind)
            score = sum(1 for k in keys if graded.get(k)) / len(keys)
            return {
                "ticker": ticker,
                "status": "ok",
                "score": score,
                "graded": graded,
                "justification": justification,
            }
        except Exception as exc:
            return {
                "ticker": ticker,
                "status": "error",
                "score": 0.0,
                "graded": {},
                "justification": "",
                "error": "%s: %s" % (type(exc).__name__, exc),
            }

    results = []
    with cf.ThreadPoolExecutor(max_workers=JUDGE_WORKERS) as ex:
        for item in ex.map(work, ctx.expected):
            results.append(item)
            ctx.llm_audit.append({"kind": kind, **item})

    errors = [r for r in results if r.get("status") == "error"]
    unavailable = [r for r in results if r.get("status") == "missing_brief"]
    # If every attempted call failed with an infrastructure error (no successful
    # grades at all), treat as judge skipped -- same as the sample's except -> 1.0.
    ok_results = [r for r in results if r.get("status") == "ok"]
    if not ok_results and errors and len(errors) == len(results) - len(unavailable):
        note = "LLM_JUDGE_STATUS=skipped reason=W&B Inference call failed for all companies example=%s" % (
            (errors[0].get("error") or "")[:160]
        )
        print(note)
        for r in errors[:5]:
            print("  LLM_ITEM kind=%s ticker=%s status=error error=%s" % (kind, r["ticker"], r.get("error", "")[:160]))
        return 1.0, note

    scores = [float(r["score"]) for r in results]
    mean = _mean(scores)

    print("LLM_JUDGE_STATUS=%s kind=%s companies=%d errors=%d missing=%d mean=%.4f" % (
        "partial_error" if errors else "ok",
        kind,
        len(results),
        len(errors),
        len(unavailable),
        mean,
    ))
    for r in results:
        if r.get("status") == "error":
            print(
                "  LLM_ITEM kind=%s ticker=%s status=error score=0.0000 error=%s"
                % (kind, r["ticker"], r.get("error", "unknown")[:160])
            )
        else:
            print(
                "  LLM_ITEM kind=%s ticker=%s status=%s score=%.4f graded=%s justification=%s"
                % (
                    kind,
                    r["ticker"],
                    r.get("status"),
                    float(r["score"]),
                    json.dumps(r.get("graded") or {}, sort_keys=True),
                    str(r.get("justification") or "")[:220],
                )
            )

    note = "mean %s LLM score over %d companies = %.4f" % (kind, len(scores), mean)
    if errors:
        note += " | LLM_JUDGE_STATUS=partial_error errors=%d example=%s" % (
            len(errors),
            (errors[0].get("error") or "")[:120],
        )
    return mean, note


def check_llm_grounding(ctx):
    return _llm_bucket_score(ctx, "grounding", GROUNDING_KEYS)


def check_llm_depth(ctx):
    return _llm_bucket_score(ctx, "depth", DEPTH_KEYS)


def check_oracle_identity(ctx):
    companies = (ctx.oracle.get("companies") or {})
    if not companies:
        return 0.0, "partial oracle missing"
    good = 0
    for ticker, exp in companies.items():
        brief = ctx.briefs.get(ticker, "")
        text = collapsed(brief)
        if not text:
            continue
        company = collapsed(exp.get("company", ""))
        name_tokens = [tok for tok in company.split() if len(tok) > 2][:2]
        name_ok = bool(name_tokens) and all(tok in text for tok in name_tokens)
        ticker_ok = collapsed(exp.get("ticker", "")) in text
        filing = str(exp.get("filing_date", "") or "")
        year = filing[:4] if len(filing) >= 4 else ""
        filing_ok = (not year) or (year in text) or (collapsed(filing) in text)
        # Beyond header echo: at least one distinctive oracle phrase window, or a body span.
        phrase_ok = any(_phrase_hit(p, brief) for p in (exp.get("distinctive_phrases") or []))
        body = ctx.proxy_body.get(ticker, "")
        body_hit = False
        if body:
            bwords = re.findall(r"[A-Za-z0-9][A-Za-z0-9'/-]*", body)
            for i in range(0, max(0, len(bwords) - 5), 29):
                span = " ".join(bwords[i:i + 5])
                if len(span) >= 24 and collapsed(span) in text:
                    body_hit = True
                    break
        if ticker_ok and name_ok and filing_ok and (phrase_ok or body_hit):
            good += 1
    return good / len(companies), "%d/%d oracle companies identify issuer/filing and show body-level content" % (good, len(companies))


def _phrase_hit(phrase, brief):
    if not phrase or not brief:
        return False
    if phrase in brief:
        return True
    brief_c = collapsed(brief)
    if collapsed(phrase) in brief_c:
        return True
    toks = re.findall(r"[A-Za-z0-9]+", phrase)
    if len(toks) < 5:
        return False
    for i in range(0, len(toks) - 4):
        window = " ".join(toks[i:i + 5]).lower()
        if window in brief_c:
            return True
    return False


def check_oracle_distinctive_phrases(ctx):
    companies = (ctx.oracle.get("companies") or {})
    if not companies:
        return 0.0, "partial oracle missing"
    scores = []
    for ticker, exp in companies.items():
        brief = ctx.briefs.get(ticker, "")
        phrases = exp.get("distinctive_phrases") or []
        if not phrases:
            scores.append(0.0)
            continue
        hits = sum(1 for phrase in phrases if _phrase_hit(phrase, brief))
        # Also require the brief is not a bulk dump of the proxy.
        ratio = _verbatim_overlap_ratio(brief, ctx.proxy_body.get(ticker, ""))
        hit_rate = hits / len(phrases)
        if ratio > MAX_VERBATIM_RATIO:
            scores.append(hit_rate * 0.25)
        else:
            scores.append(hit_rate)
    return _mean(scores), "mean distinctive-phrase hit rate over %d oracle companies = %.4f" % (len(companies), _mean(scores))


def check_oracle_coverage_completeness(ctx):
    companies = (ctx.oracle.get("companies") or {})
    if not companies:
        return 0.0, "partial oracle missing"
    good = 0
    for ticker in companies:
        text = ctx.briefs.get(ticker, "")
        if not text.strip():
            continue
        sections = _section_bodies(text)
        if any(len(sections.get(h.lower(), "").split()) < SECTION_BODY_MIN_WORDS for h in REQUIRED_HEADINGS):
            continue
        if len(text.split()) < 250 or _unique_word_ratio(text) < MIN_UNIQUE_RATIO:
            continue
        board = sections.get("## board and governance structure", "")
        comp = sections.get("## executive compensation design", "")
        gov_hits = _term_hits(board, GOV_TERMS)
        comp_hits = _term_hits(comp, COMP_TERMS)
        if len(gov_hits) < 2 or len(comp_hits) < 2:
            continue
        # Beyond generic vocabulary: require company-specific grounding - either a
        # hand-verified distinctive phrase or a topical span from this proxy's body.
        exp = companies.get(ticker) or {}
        brief_c = collapsed(text)
        specific = any(_phrase_hit(p, text) for p in (exp.get("distinctive_phrases") or []))
        if not specific:
            specific = _topical_body_span_in_brief(ctx.proxy_body.get(ticker, ""), text, brief_c, step=13)
        if specific:
            good += 1
    return (
        good / len(companies),
        "%d/%d oracle companies have complete sections plus company-specific grounded content"
        % (good, len(companies)),
    )


STATIC_CHECKS = [
    ("check_brief_coverage", check_brief_coverage),
    ("check_required_sections", check_required_sections),
    ("check_heading_format", check_heading_format),
    ("check_brief_length_floor", check_brief_length_floor),
    ("check_deliverable_paths", check_deliverable_paths),
]
REWARD_HACKING_CHECKS = [
    ("check_ticker_identity", check_ticker_identity),
    ("check_proxy_phrase_grounding", check_proxy_phrase_grounding),
    ("check_no_templated_briefs", check_no_templated_briefs),
    ("check_brief_synthesis", check_brief_synthesis),
    ("check_llm_grounding", check_llm_grounding),
    ("check_llm_depth", check_llm_depth),
]
PARTIAL_ORACLE_CHECKS = [
    ("check_oracle_identity", check_oracle_identity),
    ("check_oracle_distinctive_phrases", check_oracle_distinctive_phrases),
    ("check_oracle_coverage_completeness", check_oracle_coverage_completeness),
]


def _bucket_mean(checks, ctx, breakdown, bucket):
    scores = []
    for name, fn in checks:
        try:
            score, notes = fn(ctx)
            score = max(0.0, min(1.0, float(score)))
            note = notes
            err = None
        except Exception as exc:
            score = 0.0
            note = "check error"
            err = "%s: %s" % (type(exc).__name__, exc)
            print("CHECK_ERROR name=%s bucket=%s error=%s" % (name, bucket, err), file=sys.stderr)
        scores.append(score)
        item = {"check": name, "bucket": bucket, "score": score, "notes": [note]}
        if err:
            item["error"] = err
            item["notes"] = ["check error: " + err]
        breakdown.append(item)
    return _mean(scores)


def _write_reward(static_score, rh_score, po_score):
    reward = (static_score * 1 + rh_score * 2 + po_score * 3) / 6
    os.makedirs(os.path.dirname(REWARD_JSON_PATH), exist_ok=True)
    with open(REWARD_JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "reward": round(reward, 4),
                "total_static_check_score": round(static_score, 4),
                "total_reward_hacking_check_score": round(rh_score, 4),
                "total_partial_oracle_check_score": round(po_score, 4),
            },
            fh,
            indent=2,
        )
    return reward


def main():
    try:
        ctx = Context()
        breakdown = []
        static_score = _bucket_mean(STATIC_CHECKS, ctx, breakdown, "static")
        rh_score = _bucket_mean(REWARD_HACKING_CHECKS, ctx, breakdown, "reward_hacking")
        po_score = _bucket_mean(PARTIAL_ORACLE_CHECKS, ctx, breakdown, "partial_oracle")
        reward = _write_reward(static_score, rh_score, po_score)
        print("reward %.4f = (static*1 + reward_hacking*2 + partial_oracle*3)/6" % reward)
        print(
            "  static=%.4f  reward_hacking=%.4f  partial_oracle=%.4f"
            % (static_score, rh_score, po_score)
        )
        for c in breakdown:
            extra = ""
            if c.get("error"):
                extra = " | ERROR=" + c["error"][:120]
            print(
                "  %-32s %.4f  %s%s"
                % (c["check"], c["score"], "; ".join(c["notes"])[:160], extra)
            )
        return 0
    except Exception as exc:
        _write_reward(0.0, 0.0, 0.0)
        print("verifier error: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
