FROM python:3.11-slim@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Agent-facing dependencies only. Grader-only HTTP/LLM clients are installed by
# tests/test.sh at grading time and are NOT baked into this image.
RUN pip install --no-cache-dir \
    requests==2.32.3 \
    matplotlib==3.9.2 \
    pypdf==4.3.1

# Never COPY instruction.md / task.toml / decomposition.yaml / tests/ into the image.
COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace
