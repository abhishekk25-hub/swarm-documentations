FROM python:3.11-slim

WORKDIR /workspace

RUN pip install --no-cache-dir requests==2.32.4

COPY input_artifacts/ /input_artifacts/

RUN mkdir -p /logs/agent /logs/verifier
