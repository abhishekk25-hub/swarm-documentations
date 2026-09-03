#!/usr/bin/env python3

import os
import re
import subprocess
import sys

N_CHAPTERS = 20
FRONT_SKIP = 16          
PAD_PAGES = 4            
FIG_RE = re.compile(r"\b(?:FIGURE|TABLE)\s+(\d{1,2})\.\d", re.IGNORECASE)
BACKMATTER_RE = re.compile(r"(?im)^\s*(answer key|references|^index\b|appendix\s+[a-z]\b)")


def extract_pages(pdf_path):
    """Return the book as a list of per-page text strings."""
    try:
        out = subprocess.run(["pdftotext", "-layout", pdf_path, "-"],
                             capture_output=True, timeout=600)
        if out.returncode == 0 and out.stdout:
            text = out.stdout.decode("utf-8", errors="ignore")
            pages = text.split("\x0c")
            if len(pages) > 50:
                return pages
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        return [(pg.extract_text() or "") for pg in reader.pages]
    except Exception:
        return []


def detect_spans(pages):
    """Map chapter 1..N -> text using FIGURE/TABLE 'k.M' anchors."""
    if not pages or len(pages) < 50:
        return None

    anchor = {}
    for i, t in enumerate(pages):
        if i < FRONT_SKIP:
            continue
        for m in FIG_RE.finditer(t):
            k = int(m.group(1))
            if 1 <= k <= N_CHAPTERS and k not in anchor:
                anchor[k] = i

    if len(anchor) < N_CHAPTERS - 2:
        return None
    ordered = [anchor.get(k) for k in range(1, N_CHAPTERS + 1)]
    seen = [p for p in ordered if p is not None]
    if any(seen[i] >= seen[i + 1] for i in range(len(seen) - 1)):
        return None

    for k in range(1, N_CHAPTERS + 1):
        if anchor.get(k) is None:
            prev = next((anchor[j] for j in range(k - 1, 0, -1) if anchor.get(j) is not None), FRONT_SKIP)
            nxt = next((anchor[j] for j in range(k + 1, N_CHAPTERS + 1) if anchor.get(j) is not None), len(pages))
            anchor[k] = (prev + nxt) // 2

    gaps = [anchor[k + 1] - anchor[k] for k in range(1, N_CHAPTERS)]
    med = sorted(gaps)[len(gaps) // 2] if gaps else 24

    starts = {}
    prev = FRONT_SKIP - 1
    for k in range(1, N_CHAPTERS + 1):
        s = max(prev + 1, anchor[k] - PAD_PAGES, FRONT_SKIP)
        starts[k] = s
        prev = s

    back = None
    for i in range(anchor[N_CHAPTERS] + 5, len(pages)):
        if BACKMATTER_RE.search(pages[i]):
            back = i
            break
    end_last = back if back is not None else min(len(pages), anchor[N_CHAPTERS] + med)

    spans = {}
    for k in range(1, N_CHAPTERS + 1):
        end = starts[k + 1] if k < N_CHAPTERS else end_last
        text = "\n".join(pages[starts[k]:end]).strip()
        if text:
            spans[k] = text
    return spans if len(spans) >= N_CHAPTERS - 2 else None


def main():
    pdf_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    pages = extract_pages(pdf_path)
    spans = detect_spans(pages) if pages else None

    if not spans:
        with open(os.path.join(out_dir, "UNAVAILABLE"), "w", encoding="utf-8") as f:
            f.write("chapter detection unreliable; read chapters from the PDF instead\n")
        print("prepare_chapters: detection unreliable -> wrote UNAVAILABLE marker")
        return

    for k in range(1, N_CHAPTERS + 1):
        text = spans.get(k, "")
        with open(os.path.join(out_dir, f"chapter_{k:02d}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    print(f"prepare_chapters: wrote {len(spans)} chapter files to {out_dir}")


if __name__ == "__main__":
    main()
