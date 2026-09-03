FROM python:3.12.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace
