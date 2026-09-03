FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    requests==2.32.5 \
    beautifulsoup4==4.14.3 \
    pypdf==6.10.2

COPY input_artifacts/ /environment/input_artifacts/

RUN mkdir -p /logs/agent/output /workspace/intermediate
