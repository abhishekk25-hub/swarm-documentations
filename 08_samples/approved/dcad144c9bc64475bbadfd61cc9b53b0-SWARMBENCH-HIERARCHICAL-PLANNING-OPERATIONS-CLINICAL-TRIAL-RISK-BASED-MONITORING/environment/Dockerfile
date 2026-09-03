FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl git ca-certificates jq && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir openpyxl==3.1.5

COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace
