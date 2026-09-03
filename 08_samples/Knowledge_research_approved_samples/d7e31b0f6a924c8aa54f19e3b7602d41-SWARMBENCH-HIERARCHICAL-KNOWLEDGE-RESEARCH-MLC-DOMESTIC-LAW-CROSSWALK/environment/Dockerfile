FROM python:3.12-slim

RUN pip install --no-cache-dir openpyxl==3.1.5 reportlab==4.2.5

RUN mkdir -p /logs/agent/shards /logs/verifier /workspace/staging

COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace
