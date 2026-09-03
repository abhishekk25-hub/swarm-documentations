FROM python:3.11.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY input_artifacts/ /environment/input_artifacts/

RUN mkdir -p /logs/agent/output /logs/agent/raw_trajectory /logs/verifier

CMD ["bash"]
