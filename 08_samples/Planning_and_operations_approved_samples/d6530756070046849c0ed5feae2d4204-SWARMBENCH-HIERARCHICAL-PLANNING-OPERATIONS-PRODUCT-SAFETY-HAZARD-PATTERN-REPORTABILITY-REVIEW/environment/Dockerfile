FROM python:3.12-slim

RUN apt-get update && apt-get install -y git ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pandas==2.2.3

COPY input_artifacts/ /input_artifacts/

RUN mkdir -p /logs/agent

WORKDIR /workspace
