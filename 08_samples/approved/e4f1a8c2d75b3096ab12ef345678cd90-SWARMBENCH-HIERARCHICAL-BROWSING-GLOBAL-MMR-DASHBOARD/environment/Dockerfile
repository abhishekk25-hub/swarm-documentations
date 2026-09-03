FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    matplotlib==3.9.2 \
    pandas==3.0.2 \
    python-pptx==1.0.2 \
    python-docx==1.2.0 \
    Pillow==12.2.0

RUN mkdir -p /logs/agent/countries /logs/agent/regions /logs/agent/maternal-health-board /logs/verifier /workspace /tests

WORKDIR /workspace
