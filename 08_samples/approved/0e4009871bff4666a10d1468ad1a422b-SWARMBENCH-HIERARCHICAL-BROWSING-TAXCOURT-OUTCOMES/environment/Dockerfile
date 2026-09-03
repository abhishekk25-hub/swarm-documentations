FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl git ca-certificates jq \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      openpyxl==3.1.5 \
      matplotlib==3.9.2 \
      requests==2.32.3 \
      beautifulsoup4==4.12.3

WORKDIR /workspace
