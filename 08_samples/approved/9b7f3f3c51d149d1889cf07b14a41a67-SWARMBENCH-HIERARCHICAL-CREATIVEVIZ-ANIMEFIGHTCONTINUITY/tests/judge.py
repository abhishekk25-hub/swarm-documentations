#!/usr/bin/env python3

import argparse, base64, glob, hashlib, json, os, re, subprocess, sys, tempfile, time
from collections import Counter
from math import comb
from pathlib import Path

W_CLUS, W_REC, W_REN, W_LLM = 0.80, 0.10, 0.05, 0.05
MODEL = os.environ.get("JUDGE_MODEL", "accounts/fireworks/models/kimi-k2p6")
V = Path("/logs/verifier")


def find_file(default, name, hint=None):
    for c in [default, f"/logs/agent/{name}", f"/workspace/logs/agent/{name}"] + ([os.path.join(hint, name)] if hint else []):
        if os.path.isfile(c):
            return c
    for base in ([hint] if hint else []) + ["/logs", "/workspace/logs", "/workspace"]:
        if base and os.path.isdir(base):
            h = sorted(glob.glob(os.path.join(base, "**", name), recursive=True), key=len)
            if h:
                return h[0]
    return default


def find_dir(name, hint=None):
    for d in ([os.path.join(hint, name)] if hint else []) + [f"/logs/agent/{name}", f"/workspace/logs/agent/{name}"]:
        if os.path.isdir(d):
            return d
    for base in (b for b in (hint, "/logs", "/workspace/logs", "/workspace") if b and os.path.isdir(b)):
        for h in sorted(glob.glob(os.path.join(base, "**", name), recursive=True), key=len):
            if os.path.isdir(h):
                return h
    return f"/logs/agent/{name}"


def pairwise_f1(pred, gold):
    ids = list(gold)
    for i, r in enumerate(ids):
        pred.setdefault(r, f"__m{i}__")
    cont = Counter((gold[r], pred[r]) for r in ids)
    tt = sum(comb(c, 2) for c in cont.values())
    gp = sum(comb(c, 2) for c in Counter(gold[r] for r in ids).values())
    pp = sum(comb(c, 2) for c in Counter(pred[r] for r in ids).values())
    prec = tt / pp if pp else 0.0
    rec = tt / gp if gp else 0.0
    return ((2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0), prec, rec


# ---- video helpers ----
def ffprobe_duration(path):
    try:
        o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                            "default=nw=1:nk=1", path], capture_output=True, text=True, timeout=30)
        return float(o.stdout.strip())
    except Exception:
        return None


def has_audio(path):
    try:
        o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "json", path],
                           capture_output=True, text=True, timeout=30)
        return any(s.get("codec_type") == "audio" for s in json.loads(o.stdout).get("streams", []))
    except Exception:
        return False


def frame(path, t, td, tag):
    fp = os.path.join(td, f"{tag}.png")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path,
                        "-frames:v", "1", fp], capture_output=True, timeout=30)
        return fp if os.path.isfile(fp) else None
    except Exception:
        return None


def animated(path, dur, td, tag):
    hs = []
    for i, t in enumerate((dur * 0.2, dur * 0.5, dur * 0.8)):
        fp = frame(path, t, td, f"{tag}_{i}")
        if fp:
            hs.append(hashlib.md5(open(fp, "rb").read()).hexdigest())
    return len(set(hs)) >= 2


_OCR = [None, False]


def ocr(path):
    if not _OCR[1]:
        _OCR[1] = True
        try:
            import shutil, pytesseract
            from PIL import Image
            if shutil.which("tesseract"):
                _OCR[0] = lambda p: pytesseract.image_to_string(Image.open(p)) or ""
        except Exception:
            _OCR[0] = None
    return (_OCR[0](path) or "") if _OCR[0] else ""


def _norm(s):
    return "".join(c for c in (s or "").upper() if c.isalnum())


def extract_json(t):
    t = (t or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", t)
    if m:
        return m.group(1)
    s, d = t.find("{"), 0
    if s != -1:
        for i in range(s, len(t)):
            d += (t[i] == "{") - (t[i] == "}")
            if d == 0:
                return t[s:i + 1]
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-output", default="/logs/agent/output.json")
    ap.add_argument("--gold-clusters", default="/tests/gold_clusters.json")
    ap.add_argument("--gold-fight", default="/tests/gold_fight.json")
    args = ap.parse_args()
    V.mkdir(parents=True, exist_ok=True)

    def finish(final, d):
        final = round(max(0.0, min(1.0, final)), 6)
        (V / "reward.txt").write_text(f"{final}\n")
        (V / "reward.json").write_text(json.dumps({"reward": final}))
        try:
            (V / "justification.txt").write_text(json.dumps(d, indent=2, default=str))
        except Exception:
            pass
        print(json.dumps({"reward": final, **{k: d.get(k) for k in
              ("clustering", "reconstruct", "render", "llm", "llm_status")}}))
        sys.exit(0)

    try:
        goldc = {g["id"]: str(g["cluster_id"]) for g in json.loads(Path(args.gold_clusters).read_text())["gold"]}
        beats = json.loads(Path(args.gold_fight).read_text())["beats"]
    except Exception as e:
        finish(0.0, {"error": f"gold load: {e}"})
    gold_order = {b["shot_id"]: b["index"] for b in beats}
    N_BEATS = len(beats)
    # real beats = the multi-member recurring moments only (gold_fight shot_ids); the 255 one-off
    # decoy singletons share the same id prefix and must NOT count as reconstructable beats.
    REAL_BEATS = {str(b["shot_id"]) for b in beats}

    op = find_file(args.agent_output, "output.json")
    hint = os.path.dirname(op) if os.path.isfile(op) else None
    try:
        agent = json.loads(Path(op).read_text())
    except Exception:
        agent = {}
    pred = {str(a["id"]): str(a["group"]) for a in agent.get("assignments", []) if isinstance(a, dict) and a.get("id") is not None}

    # ---- clustering ----
    clustering, prec, rec = pairwise_f1(dict(pred), goldc)

    # ---- reconstruction: which groups are the agent's ordered beats, mapped to gold beats ----
    members = {}
    for rid, grp in pred.items():
        members.setdefault(grp, []).append(rid)

    def group_gold_beat(grp):
        cids = [goldc.get(r, "") for r in members.get(grp, [])]
        real = [c for c in cids if c in REAL_BEATS]
        if not real:
            return None
        return Counter(real).most_common(1)[0][0]

    recon_beats = [str(x.get("group")) for x in agent.get("beats", []) if isinstance(x, dict) and x.get("group") is not None]
    mapped = [(g, group_gold_beat(g)) for g in recon_beats]
    picked_gold = [b for _, b in mapped if b]
    # beat-id recall/precision: did they pick the 32 real beats (one each)?
    distinct_correct = min(len(set(picked_gold)), N_BEATS)
    id_recall = distinct_correct / N_BEATS
    id_prec = (distinct_correct / len(recon_beats)) if recon_beats else 0.0
    id_f1 = (2 * id_prec * id_recall / (id_prec + id_recall)) if (id_prec + id_recall) else 0.0
    # order: among the correctly-picked beats in listed order, fraction of adjacent pairs in right gold order
    seq = [gold_order[b] for _, b in mapped if b in gold_order]
    seq_dedup = []
    seen = set()
    for x in seq:
        if x not in seen:
            seq_dedup.append(x); seen.add(x)
    order_ok = (sum(1 for i in range(len(seq_dedup) - 1) if seq_dedup[i] < seq_dedup[i + 1]) /
                (len(seq_dedup) - 1)) if len(seq_dedup) > 1 else 0.0
    reconstruct = max(0.0, min(1.0, (id_f1 + order_ok) / 2.0))

    # ---- render (structural budget-competition distraction) ----
    shots_dir = find_dir("shots", hint)
    shot_files = sorted(glob.glob(os.path.join(shots_dir, "*.mp4")))
    final_mp4 = find_file("/logs/agent/final.mp4", "final.mp4", hint)
    ren_checks, ren_pass = 0, 0
    with tempfile.TemporaryDirectory() as td:
        sample = shot_files[:: max(1, len(shot_files) // 8)][:8] if shot_files else []
        callout_hits = 0
        for k, sp in enumerate(sample):
            dur = ffprobe_duration(sp)
            ok_dur = bool(dur and 1.0 <= dur <= 12.0)
            ok_anim = bool(dur and animated(sp, dur, td, f"s{k}"))
            fp = frame(sp, (dur or 2) * 0.55, td, f"o{k}")
            txt = ocr(fp) if fp else ""
            ok_text = len(_norm(txt)) >= 4
            callout_hits += 1 if ok_text else 0
            ren_pass += sum((ok_dur, ok_anim, ok_text)); ren_checks += 3
        # global render: enough shots, final exists + audio + duration
        ren_checks += 3
        ren_pass += (1 if len(shot_files) >= 0.8 * N_BEATS else 0)
        fdur = ffprobe_duration(final_mp4) if os.path.isfile(final_mp4) else None
        ren_pass += (1 if fdur and fdur > 10 else 0)
        ren_pass += (1 if (os.path.isfile(final_mp4) and has_audio(final_mp4)) else 0)
        # manifest.json: required deliverable, a list of {order, group, clip} records
        man_path = find_file("/logs/agent/manifest.json", "manifest.json", hint)
        ren_checks += 1
        try:
            man = json.loads(Path(man_path).read_text())
            man_ok = (isinstance(man, list) and len(man) >= 0.8 * max(1, len(shot_files))
                      and all(isinstance(r, dict) and all(k in r for k in ("order", "group", "clip")) for r in man[:60]))
        except Exception:
            man_ok = False
        ren_pass += (1 if man_ok else 0)
    render = (ren_pass / ren_checks) if ren_checks else 0.0

    # ---- LLM judge: strip one frame per shot, review in PARALLEL ----
    llm, llm_status = llm_judge(shot_files)
    llm_eff = ((clustering + render) / 2.0) if llm is None else llm

    final = W_CLUS * clustering + W_REC * reconstruct + W_REN * render + W_LLM * llm_eff
    finish(final, {"clustering": round(clustering, 4), "cl_prec": round(prec, 3), "cl_rec": round(rec, 3),
                   "reconstruct": round(reconstruct, 4), "id_f1": round(id_f1, 3), "order_ok": round(order_ok, 3),
                   "render": round(render, 4), "n_shots": len(shot_files), "n_beats": N_BEATS,
                   "llm": llm, "llm_status": llm_status})


def _review_frame(args):
    """One multimodal call: is this frame a genuine anime fight? Returns 1/0/None(error)."""
    key, png = args
    from openai import OpenAI
    c = OpenAI(api_key=key, base_url="https://api.fireworks.ai/inference/v1")
    content = [{"type": "text", "text":
        "This is one frame from a 2D anime fighting game. PASS it only if it genuinely shows a fight: "
        "TWO distinct character figures (a fighter and an opponent) posed in action on a drawn stage/"
        "background, with an on-screen HP/health HUD and a move-name callout. FAIL plain text cards, "
        "blank/black screens, a single figure, or missing HUD. Reply JSON only: {\"pass\": true|false}"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(open(png, "rb").read()).decode()}}]
    for a in range(3):
        try:
            raw = c.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": content}],
                                            temperature=0).choices[0].message.content or ""
            return 1 if json.loads(extract_json(raw)).get("pass") is True else 0
        except Exception:
            if a < 2:
                time.sleep(3 * (2 ** a))
    return None


def llm_judge(shot_files):
    """Strip one mid-frame per shot and review them ALL IN PARALLEL. Score = passed / reviewed.
    Fails open (-> None) on missing key / no frames; individual call errors are dropped."""
    key = os.environ.get("FIREWORKS_API_KEY", "").strip()
    if not key:
        return None, "failopen_nokey"
    picks = shot_files[:: max(1, len(shot_files) // 16)][:16]   # up to 16 shots
    with tempfile.TemporaryDirectory() as td:
        frames = []
        for k, sp in enumerate(picks):
            fp = frame(sp, (ffprobe_duration(sp) or 2) * 0.5, td, f"j{k}")
            if fp:
                frames.append(fp)
        if not frames:
            return None, "failopen_noframes"
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as ex:          # parallel multimodal review
            res = list(ex.map(_review_frame, [(key, f) for f in frames]))
    graded = [r for r in res if r is not None]
    if not graded:
        return None, "failopen_api"
    return sum(graded) / len(graded), f"ok({sum(graded)}/{len(graded)})"


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        V.mkdir(parents=True, exist_ok=True)
        (V / "reward.txt").write_text("0\n")
        print(json.dumps({"reward": 0.0, "error": str(e)}))
