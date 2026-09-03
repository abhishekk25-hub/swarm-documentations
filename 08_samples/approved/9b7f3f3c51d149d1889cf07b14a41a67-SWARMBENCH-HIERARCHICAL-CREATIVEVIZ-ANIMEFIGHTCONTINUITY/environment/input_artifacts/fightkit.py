#!/usr/bin/env python3
"""fightkit -- render a REAL 2D anime fight to MP4 by compositing hand-drawn anime fighter sprites
(samurai AKIRA vs ninja RYU-X) onto an anime forest stage, with motion, HP/combo/timer HUD and hit FX.
Provided so the agent gets a genuine anime fight scene without writing render code. The agent decides
the CHOREOGRAPHY (which fighter does which move, order, HP); fightkit animates the sprites.

Sprites: LuizMelo "Martial Hero" 1 & 2 (free, see sprites/CREDITS.txt), baked at sprites/{akira,ryux}/.

    from fightkit import render_fight
    render_fight(beats, "/logs/agent/final.mp4", "/logs/agent/shots")
beats = [{"attacker":"A"|"B", "move":"uppercut"|...|"kick", "callout":"RISING DRAGON",
          "hp_a":1000,"hp_b":880,"combo":1,"timer":90,"duration":3.0}, ...]
"""
import math, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, HPMAX, FW = 1280, 720, 24, 1000, 200            # FW = sprite frame width
GROUND = 638
SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
COL = {"A": (90, 180, 255), "B": (255, 90, 90)}
NAME = {"A": "AKIRA", "B": "RYU-X"}
_F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fbig, fmid, fsm = (ImageFont.truetype(_F, s) for s in (64, 30, 22))
_BG = Image.open(os.path.join(SP, "background.png")).convert("RGBA").resize((W, H))
# heavy/light move -> Attack2 / Attack1
HEAVY = {"uppercut", "smash", "overhead", "knee", "elbow"}


def _sheet(fighter, name):
    im = Image.open(os.path.join(SP, fighter, name)).convert("RGBA")
    n = im.width // FW
    return [im.crop((i * FW, 0, (i + 1) * FW, im.height)) for i in range(n)]


_CACHE = {}


def _anim(fighter, name):
    k = (fighter, name)
    if k not in _CACHE:
        _CACHE[k] = _sheet(fighter, name)
    return _CACHE[k]


def _frame_for(fighter, kind, t):
    """Pick a sprite frame for a fighter given its action kind and shot progress t in [0,1].
    kind 'attack'/'hit' play their animation in the active window, else idle-cycle."""
    idle = _anim(fighter, "Idle.png")
    if kind == "attack":
        if t < 0.28 or t > 0.66:
            seq = idle
        else:
            seq = _anim(fighter, "Attack2.png") if getattr(_frame_for, "_heavy", False) else _anim(fighter, "Attack1.png")
            ti = (t - 0.28) / 0.38
            return seq[max(0, min(len(seq) - 1, int(ti * len(seq))))]
    elif kind == "hit":
        if 0.42 < t < 0.7:
            seq = _anim(fighter, "Take_Hit.png" if fighter == "akira" else "Take_hit.png")
            ti = (t - 0.42) / 0.28
            return seq[max(0, min(len(seq) - 1, int(ti * len(seq))))]
        seq = idle
    else:
        seq = idle
    return seq[int((t * 10)) % len(seq)]   # idle cycle


def _paste(base, sprite, cx, scale=2.2, flip=False):
    s = sprite.resize((int(sprite.width * scale), int(sprite.height * scale)))
    if flip:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    x = int(cx * W - s.width / 2)
    y = GROUND - s.height + int(0.10 * s.height)   # feet near ground (sprites have bottom padding)
    base.alpha_composite(s, (x, y))


def _spark(d, p, t):
    r = 16 + 40 * t
    for k in range(10):
        a = math.radians(k * 36 + t * 70)
        d.line([p[0], p[1], p[0] + r * math.cos(a), p[1] + r * math.sin(a)], fill=(255, 235, 110), width=4)


def _hud(d, hp_a, hp_b, callout, combo, timer):
    d.rectangle([0, 0, W, 96], fill=(8, 6, 16, 180))
    for side, hp, col, ax in (("A", hp_a, COL["A"], 40), ("B", hp_b, COL["B"], W - 500)):
        frac = max(0, min(1, hp / HPMAX))
        d.rectangle([ax - 3, 25, ax + 463, 61], outline=(235, 235, 235), width=3)
        fw = int(460 * frac); x0 = ax if side == "A" else ax + 460 - fw
        d.rectangle([x0, 28, x0 + fw, 58], fill=col)
        d.text((ax, 66), NAME[side], font=fsm, fill=col)
    d.text((W // 2, 40), f"{int(timer)}", font=fmid, fill=(255, 220, 60), anchor="mm")
    d.text((W // 2, 78), f"COMBO {combo}", font=fsm, fill=(255, 230, 120), anchor="mm")
    if callout:
        txt = callout.upper().strip()
        if len(txt) > 22:
            txt = txt[:22].rstrip() + "..."
        cf = fbig
        for sz in (62, 52, 44, 38):
            cf = ImageFont.truetype(_F, sz)
            if d.textlength(txt, font=cf) <= W - 120:
                break
        d.text((W // 2, 150), txt, font=cf, fill=(255, 240, 90), anchor="mm", stroke_width=3, stroke_fill=(110, 30, 0))


def render_shot(beat, posA, posB, out_path):
    atk = beat.get("attacker", "A")
    _frame_for._heavy = beat.get("move", "straight") in HEAVY
    dur = float(beat.get("duration", 3.0)); n = max(16, int(dur * FPS))
    with tempfile.TemporaryDirectory() as td:
        for f in range(n):
            t = f / (n - 1)
            shake = int(6 * math.sin(t * 44)) if 0.45 < t < 0.62 else 0
            im = _BG.copy()
            if shake:
                im = Image.new("RGBA", (W, H)); im.alpha_composite(_BG, (shake, 0))
            d = ImageDraw.Draw(im)
            # lunge attacker slightly toward center during the strike
            la = 0.03 * max(0, math.sin(min(1, t / 0.6) * math.pi)) if atk == "A" else 0
            lb = 0.03 * max(0, math.sin(min(1, t / 0.6) * math.pi)) if atk == "B" else 0
            fa = _frame_for("akira", "attack" if atk == "A" else "hit", t)
            fb = _frame_for("ryux", "attack" if atk == "B" else "hit", t)
            # draw back fighter first for depth
            if atk == "A":
                _paste(im, fb, posB - lb, flip=True); _paste(im, fa, posA + la, flip=False)
            else:
                _paste(im, fa, posA + la, flip=False); _paste(im, fb, posB - lb, flip=True)
            if 0.45 < t < 0.62:
                _spark(d, ((posA + posB) / 2 * W, GROUND - 150), (t - 0.45) / 0.17)
            _hud(d, beat.get("hp_a", HPMAX), beat.get("hp_b", HPMAX), beat.get("callout", ""),
                 beat.get("combo", 0), beat.get("timer", 90))
            im.convert("RGB").save(os.path.join(td, f"f{f:04d}.png"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(td, "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", str(FPS), out_path], check=True)


def render_fight(beats, final_path, shots_dir="/logs/agent/shots"):
    os.makedirs(shots_dir, exist_ok=True)
    clips = []
    posA, posB = 0.34, 0.66
    for i, b in enumerate(beats):
        sp = os.path.join(shots_dir, f"{i:02d}.mp4")
        render_shot(b, posA, posB, sp)
        clips.append(sp)
        if b.get("attacker", "A") == "A":
            posA = min(0.42, posA + 0.012); posB = min(0.74, posB + 0.016)
        else:
            posB = max(0.58, posB - 0.012); posA = max(0.26, posA - 0.016)
    lst = os.path.join(tempfile.gettempdir(), "fk_list.txt")
    with open(lst, "w") as fh:
        for c in clips:
            fh.write(f"file '{c}'\n")
    total = sum(float(b.get("duration", 3.0)) for b in beats)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-t", f"{total}", "-i", "sine=frequency=160:sample_rate=44100",
                    "-c:v", "copy", "-c:a", "aac", "-shortest", final_path], check=True)
    return clips


if __name__ == "__main__":
    demo = [{"attacker": "A", "move": "uppercut", "callout": "RISING DRAGON", "hp_a": 1000, "hp_b": 820, "combo": 1, "timer": 96},
            {"attacker": "B", "move": "kick", "callout": "CRESCENT KICK", "hp_a": 900, "hp_b": 820, "combo": 1, "timer": 93}]
    render_fight(demo, "/tmp/fk_demo.mp4", "/tmp/fk_shots")
    print("rendered demo")
