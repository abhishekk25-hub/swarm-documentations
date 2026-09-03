#!/usr/bin/env python3
import argparse, base64, glob, hashlib, json, os, re, subprocess, sys, tempfile, time
import urllib.parse, urllib.request
from pathlib import Path

STRUCT_PER = 5      # exists, duration, animated, label, manifest_entry
GLOBAL_STRUCT = 2   # manifest_ok, distinct_reels
FACT_PER = 5        # value, trend, peak, trough, peer
MIN_WORDS = 100     # a faithful per-section narrative; thin templated blurbs fall short
NET_TIMEOUT = int(os.environ.get("WB_API_TIMEOUT", "25"))
WB_API = "https://api.worldbank.org/v2/country/{cc}/indicator/{ind}"
MODEL = os.environ.get("JUDGE_MODEL", "accounts/fireworks/models/kimi-k2p6")
V = Path("/logs/verifier")


def find_file(default, name, hint_dir=None):
    cands = [default, f"/logs/agent/{name}", f"/workspace/logs/agent/{name}"]
    if hint_dir:
        cands += [os.path.join(hint_dir, name)]
    for c in cands:
        if os.path.isfile(c):
            return c
    bases = [hint_dir] if hint_dir else []
    bases += ["/logs", "/workspace/logs", "/workspace"]
    for base in bases:
        if base and os.path.isdir(base):
            hits = sorted(glob.glob(os.path.join(base, "**", name), recursive=True), key=len)
            if hits:
                return hits[0]
    return default


def find_reels_dir(hint_dir=None):
    cands = ([os.path.join(hint_dir, "reels")] if hint_dir else []) + \
            ["/logs/agent/reels", "/workspace/logs/agent/reels"]
    for d in cands:
        if os.path.isdir(d):
            return d
    for base in (b for b in (hint_dir, "/logs", "/workspace/logs", "/workspace") if b and os.path.isdir(b)):
        for h in sorted(glob.glob(os.path.join(base, "**", "reels"), recursive=True), key=len):
            if os.path.isdir(h):
                return h
    return "/logs/agent/reels"


def ffprobe_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, timeout=30)
        return float(out.stdout.strip())
    except Exception:
        return None


def _frame(path, t, vf=None):
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "f.png")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1"]
        if vf:
            cmd += ["-vf", vf]
        cmd += [fp]
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.isfile(fp):
                return Path(fp).read_bytes()
        except Exception:
            pass
    return None


def is_animated(path):
    dur = ffprobe_duration(path)
    if not dur or dur <= 0:
        return False
    hashes = []
    for t in (max(0.2, dur * 0.15), dur * 0.5, max(0.2, dur - 0.3)):
        b = _frame(path, t)
        if b:
            hashes.append(hashlib.md5(b).hexdigest())
    return len(set(hashes)) >= 2


def mid_frame_hash(path):
    dur = ffprobe_duration(path)
    if not dur or dur <= 0:
        return None
    b = _frame(path, dur * 0.5)
    return hashlib.md5(b).hexdigest() if b else None


def frame_b64(path):
    dur = ffprobe_duration(path)
    b = _frame(path, max(0.2, (dur * 0.92) if dur else 7.0), vf="scale=560:-1")
    return base64.b64encode(b).decode() if b else None


_OCR_READER, _OCR_INIT = None, False


def _get_ocr():
    global _OCR_READER, _OCR_INIT
    if _OCR_INIT:
        return _OCR_READER
    _OCR_INIT = True
    try:
        import shutil, pytesseract
        from PIL import Image
        if shutil.which("tesseract"):
            _OCR_READER = lambda p: pytesseract.image_to_string(Image.open(p)) or ""
    except Exception:
        _OCR_READER = None
    return _OCR_READER


def ocr_text(path):
    reader = _get_ocr()
    dur = ffprobe_duration(path) if reader else None
    if not reader or not dur or dur <= 0:
        return ""
    chunks = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate((max(0.2, dur * 0.2), dur * 0.5, max(0.2, dur - 0.4))):
            fp = os.path.join(td, f"o{i}.png")
            try:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}",
                                "-i", path, "-frames:v", "1", fp], capture_output=True, timeout=30)
                if os.path.isfile(fp):
                    chunks.append(reader(fp) or "")
            except Exception:
                pass
    return " ".join(chunks)


def _norm(s):
    return "".join(ch for ch in (s or "").upper() if ch.isalnum())


def narrative_gate(s, rec):
    """Deterministic faithfulness gate (oracle ground truth, no network): the narrative is
    substantial and names the real peak year, trough year, and peer country."""
    narr = str(rec.get("narrative", ""))
    return bool(str(s.get("peak_year")) in narr and str(s.get("trough_year")) in narr
                and _norm(s.get("peer_country", "")) in _norm(narr)
                and len(narr.split()) >= MIN_WORDS)


def _wb_series(cc, ind, date_range="2000:2022"):
    q = {"format": "json", "date": date_range, "per_page": "100"}
    url = WB_API.format(cc=cc, ind=ind) + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "swarmbench-verifier/1.0"})
    with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    rows = data[1] if isinstance(data, list) and len(data) > 1 and data[1] else []
    pts = [(int(x["date"]), float(x["value"])) for x in rows
           if isinstance(x, dict) and x.get("value") is not None and str(x.get("date", "")).isdigit()]
    pts.sort()
    return pts


def _truths(cc, ind, peer_cc, date_range):
    pts = _wb_series(cc, ind, date_range)
    if len(pts) < 2:
        return None
    latest, first = pts[-1][1], pts[0][1]
    trend = "rising" if latest > first * 1.02 else ("falling" if latest < first * 0.98 else "flat")
    out = {"latest": latest, "latest_year": pts[-1][0],
           "peak_year": max(pts, key=lambda x: x[1])[0],
           "trough_year": min(pts, key=lambda x: x[1])[0], "trend": trend, "peer_comparison": None}
    try:
        ppts = _wb_series(peer_cc, ind, date_range)
        if ppts:
            out["peer_comparison"] = "higher" if latest > ppts[-1][1] else "lower"
    except Exception:
        pass
    return out


def network_ok():
    try:
        _wb_series("DE", "SP.POP.TOTL", "2022:2022")
        return True
    except Exception:
        return False


def _to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def _to_int(v):
    try:
        return int(v)
    except Exception:
        return None


def _records(obj):
    if isinstance(obj, dict) and isinstance(obj.get("sections"), list):
        return obj["sections"]
    return obj if isinstance(obj, list) else []


def extract_json(text):
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    start, depth = text.find("{"), 0
    if start != -1:
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return text


def static_check(oracle, recs, manifest, reels_dir):
    """Deterministic structural + live factual checks -> (score in [0,1], info)."""
    sections = oracle["sections"]
    rel = float(oracle.get("value_tolerance_rel", 0.01))
    abs_tol = float(oracle.get("value_tolerance_abs", 1.0))
    date_range = str(oracle.get("date_range", "2000:2022"))
    n = len(sections)
    REQ = ("section_id", "country", "indicator", "latest_value", "trend_direction", "peak_year",
           "trough_year", "peer_country", "peer_comparison", "narrative", "reel")
    man = {}
    if isinstance(manifest, list):
        for e in manifest:
            if isinstance(e, dict) and e.get("section_id") is not None:
                man[str(e["section_id"])] = e

    def manifest_complete(sid):
        e = man.get(sid)
        return bool(isinstance(e, dict) and all(e.get(k) not in (None, "") for k in REQ))

    ocr_on = _get_ocr() is not None
    net = network_ok()
    s_pass = f_pass = f_total = narr_pass = 0
    midhashes, per = [], {}

    for s in sections:
        sid = str(s["section_id"])
        rec = recs.get(sid, {})
        path = os.path.join(reels_dir, f"{sid}.mp4")
        info = {}

        c_exists = os.path.isfile(path)
        dur = ffprobe_duration(path) if c_exists else None
        c_dur = bool(dur and 7.0 <= dur <= 9.0)
        c_anim = bool(c_exists and is_animated(path))
        if not ocr_on:
            c_label = True
            info["label"] = "skip(no-ocr)"
        elif c_exists:
            txt = _norm(ocr_text(path))
            c_label = (_norm(s["label_country"]) in txt) and (_norm(s.get("label_keyword", "")) in txt)
            info["label"] = c_label
        else:
            c_label = False
            info["label"] = False
        c_man = manifest_complete(sid)
        s_here = sum(1 for c in (c_exists, c_dur, c_anim, c_label, c_man) if c)
        s_pass += s_here
        info.update(exists=c_exists, duration=round(dur, 2) if dur else None, duration_ok=c_dur,
                    animated=c_anim, manifest_entry=c_man, struct=f"{s_here}/{STRUCT_PER}")
        if c_exists:
            h = mid_frame_hash(path)
            if h:
                midhashes.append(h)

        c_narr = narrative_gate(s, rec)
        narr_pass += 1 if c_narr else 0
        info["narrative_ok"] = c_narr
        info["narrative_words"] = len(str(rec.get("narrative", "")).split())

        if not net:
            f_pass += FACT_PER; f_total += FACT_PER
            info["factual"] = "skip(no-network)"
            per[sid] = info
            continue
        try:
            t = _truths(s["country_code"], s["indicator_code"], s["peer_code"], date_range)
        except Exception:
            t = None
        if t is None:
            f_pass += FACT_PER; f_total += FACT_PER
            info["factual"] = "skip(fetch-error)"
            per[sid] = info
            continue
        f_total += FACT_PER
        av = _to_float(rec.get("latest_value"))
        tol = max(rel * abs(t["latest"]), abs_tol)
        c_val = av is not None and abs(av - t["latest"]) <= tol
        c_trend = str(rec.get("trend_direction", "")).strip().lower() == t["trend"]
        c_peak = _to_int(rec.get("peak_year")) == t["peak_year"]
        c_trough = _to_int(rec.get("trough_year")) == t["trough_year"]
        c_peer = (t["peer_comparison"] is None) or \
                 (str(rec.get("peer_comparison", "")).strip().lower() == t["peer_comparison"])
        fh = sum(1 for c in (c_val, c_trend, c_peak, c_trough, c_peer) if c)
        f_pass += fh
        info["factual"] = {"value": c_val, "trend": c_trend, "peak": c_peak, "trough": c_trough,
                           "peer": c_peer, "score": f"{fh}/{FACT_PER}",
                           "live": {"latest": round(t["latest"], 4), "trend": t["trend"],
                                    "peak": t["peak_year"], "trough": t["trough_year"],
                                    "peer_cmp": t["peer_comparison"]}}
        per[sid] = info

    manifest_ok = bool(isinstance(manifest, list) and all(manifest_complete(str(s["section_id"])) for s in sections))
    n_unique = len(set(midhashes))
    distinct_ok = bool(midhashes) and (n_unique >= max(2, len(midhashes) // 2))
    s_pass += (1 if manifest_ok else 0) + (1 if distinct_ok else 0)

    structural = s_pass / (n * STRUCT_PER + GLOBAL_STRUCT)
    factual = (f_pass / f_total) if f_total else 0.0
    narrative = (narr_pass / n) if n else 0.0
    score = max(0.0, min(1.0, (structural + factual + narrative) / 3))
    info = {"structural": round(structural, 6), "factual": round(factual, 6),
            "narrative": round(narrative, 6), "static": round(score, 6),
            "ocr_enabled": ocr_on, "network": net, "manifest_ok": manifest_ok,
            "distinct_reels": distinct_ok, "narrative_pass": f"{narr_pass}/{n}", "per_section": per}
    return score, info


def llm_judge(sections, recs, reels_dir):
    """Strict multimodal faithfulness judge -> (score|None, status, detail). None = fail-open."""
    items = [(s, recs.get(str(s["section_id"]), {}),
              frame_b64(os.path.join(reels_dir, f"{s['section_id']}.mp4"))
              if os.path.isfile(os.path.join(reels_dir, f"{s['section_id']}.mp4")) else None)
             for s in sections]
    total = len(sections)

    if not any(b for _, _, b in items) and not any(r.get("narrative") for _, r, _ in items):
        return 0.0, "no_output", "no reels and no narratives"
    api_key = os.environ.get("FIREWORKS_API_KEY", "").strip()
    if not api_key:
        return None, "failopen", "FIREWORKS_API_KEY unset"

    content = [{"type": "text", "text": (
        f"You STRICTLY grade {total} data-story reels. For EACH section you get the GROUND-TRUTH "
        "facts, the agent's NARRATIVE, and a frame from its reel. The section PASSES only if ALL hold:\n"
        "1. the narrative states the correct TREND;\n"
        "2. it names the real PEAK year and the real TROUGH year;\n"
        "3. it gives the correct PEER comparison (higher/lower vs the named peer);\n"
        "4. it uses the real latest value (right magnitude);\n"
        "5. it is SPECIFIC to this series, NOT generic filler, with nothing the data doesn't support;\n"
        "6. the frame shows a real labelled line chart (country + indicator legible).\n"
        "Vague, templated, thin (<~100 words), wrong-turning-point, or fabricated stories FAIL. "
        "Reply JSON only: {\"results\":[{\"section_id\":\"..\",\"pass\":true|false,\"reason\":\"..\"}],"
        "\"passed\":<int>,\"total\":<int>}")}]
    for s, r, b in items:
        gt = (f"GROUND TRUTH section_id={s['section_id']}: country={s['label_country']}, "
              f"indicator={s['label_indicator']}, latest≈{s.get('expected_latest_value')} "
              f"({s.get('latest_year')}), trend={s.get('trend_direction')}, peak_year={s.get('peak_year')}, "
              f"trough_year={s.get('trough_year')}, peer={s.get('peer_country')}, "
              f"peer_comparison={s.get('peer_comparison')}")
        narr = str(r.get("narrative", "")).strip() or "(no narrative provided)"
        content.append({"type": "text", "text": gt + "\nAGENT NARRATIVE: " + narr})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b}"}} if b
                        else {"type": "text", "text": "(no reel frame -> visual check FAILS)"})

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.fireworks.ai/inference/v1")
    except Exception as e:
        return None, "failopen", f"client init: {e}"

    raw = ""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL, messages=[{"role": "user", "content": content}], temperature=0)
            raw = resp.choices[0].message.content or ""
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (2 ** attempt))
            else:
                return None, "failopen", f"vision judge API failed 3x: {e}"
    try:
        result = json.loads(extract_json(raw))
        verdict = {str(r.get("section_id")): (r.get("pass") is True)
                   for r in result.get("results", []) if isinstance(r, dict)}
        # gated: the judge can only pass a section that also clears the deterministic gate,
        # so a lenient/flaky verdict cannot rescue a thin or generic narrative.
        passed = sum(1 for s in sections
                     if verdict.get(str(s["section_id"])) and narrative_gate(s, recs.get(str(s["section_id"]), {})))
        score = max(0.0, min(1.0, passed / total)) if total else 0.0
    except Exception as e:
        return None, "failopen", f"parse error: {e}\nraw: {raw[:600]}"
    return score, "ok", json.dumps({"gated_pass": passed, "total": total, "judge": result}, indent=2)[:3000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-output", default="/logs/agent/output.json")
    ap.add_argument("--oracle", default="/tests/oracle.json")
    ap.add_argument("--reward-out", default="/logs/verifier/reward.json")
    args = ap.parse_args()
    V.mkdir(parents=True, exist_ok=True)
    try:
        Path("/logs/agent").mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    def finish(final, detail):
        final = round(max(0.0, min(1.0, final)), 6)
        (V / "reward.txt").write_text(f"{final}\n")
        (V / "reward.json").write_text(json.dumps({"reward": final}))
        try:
            (V / "justification.txt").write_text(json.dumps(detail, indent=2, default=str))
        except Exception:
            pass
        print(json.dumps({"reward": final, **{k: detail.get(k) for k in ("static", "llm", "llm_status")}}))
        sys.exit(0)

    try:
        oracle = json.loads(Path(args.oracle).read_text())
        sections = oracle["sections"]
    except Exception as e:
        finish(0.0, {"error": f"oracle load: {e}"})

    op = find_file(args.agent_output, "output.json")
    hint_dir = os.path.dirname(op) if os.path.isfile(op) else None
    try:
        agent = json.loads(Path(op).read_text())
    except Exception:
        agent = {}
    recs = {str(r.get("section_id")): r for r in _records(agent) if isinstance(r, dict)}

    mp = find_file("/logs/agent/manifest.json", "manifest.json", hint_dir)
    try:
        manifest = json.loads(Path(mp).read_text())
    except Exception:
        manifest = None
    reels_dir = find_reels_dir(hint_dir)

    static, static_info = static_check(oracle, recs, manifest, reels_dir)
    llm, llm_status, llm_detail = llm_judge(sections, recs, reels_dir)
    final = static if llm is None else (static + llm) / 2.0
    finish(final, {"static": round(static, 6), "llm": llm, "llm_status": llm_status,
                   "static_info": static_info, "llm_detail": llm_detail})


if __name__ == "__main__":
    main()
