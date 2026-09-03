FROM python:3.11.9-slim

# This task is LIVE-BROWSING on purpose: the agent fetches each metric at run time
# from the public, no-auth World Bank Indicators API (https://api.worldbank.org).
# requires_network = true. The verifier re-fetches the same series to check the
# agent's reported values (with a per-section fail-open if the network is down).

# ffmpeg/ffprobe: render and probe the animated MP4 reels.
# matplotlib + numpy + pillow: build the animations.
# tesseract-ocr + pytesseract: used by the VERIFIER (not the agent) to OCR each reel
#   and confirm the country + indicator label is actually rendered on screen.
# requests: the agent's (and solver's) live HTTP fetch.
# opencv-python-headless: image utilities (no GUI/X deps).
# openai: used by the VERIFIER's LLM-judge slice (Fireworks-compatible client).
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg fonts-dejavu-core tesseract-ocr curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    matplotlib==3.9.2 numpy==2.1.3 pillow==10.4.0 \
    pytesseract==0.3.13 requests==2.32.3 opencv-python-headless==4.10.0.84 \
    openai==1.109.1

# Machine-readable copy of the 8 sections (labels + codes only, NO fetched values).
COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace

RUN mkdir -p /logs/agent /logs/agent/reels /logs/verifier /workspace /tests /solution
