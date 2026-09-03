FROM python:3.11.9-slim

# Agent-side image for the offline 2D anime-fight render. The agent renders via the provided
# /input_artifacts/fightkit.py toolkit, which needs only Pillow + ffmpeg + fonts.
# ffmpeg/ffprobe: render per-shot mp4s, concat final.mp4, synth + mux audio.
# fonts-dejavu: on-screen callout / HUD text. pillow: sprite compositing + HUD drawing.
# numpy/pyyaml: general utilities available to the agent. curl: agent runtime bootstrap.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg fonts-dejavu-core fonts-dejavu-extra curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    numpy==2.1.3 pillow==10.4.0 pyyaml==6.0.2

COPY input_artifacts/ /input_artifacts/
WORKDIR /workspace
RUN mkdir -p /logs/agent /logs/agent/shots /logs/verifier /workspace /tests
