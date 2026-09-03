FROM python:3.11.9-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*
COPY input_artifacts/ /input_artifacts/
WORKDIR /workspace
RUN mkdir -p /logs/agent /logs/verifier /workspace /tests /solution
