FROM python:3.11-slim

WORKDIR /workspace

# Keep pip/tool progress output ASCII-only so session logs stay portable.
ENV PIP_PROGRESS_BAR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUTF8=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ffmpeg \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN printf '%s\n' \
    'export PIP_PROGRESS_BAR=off' \
    'export PIP_DISABLE_PIP_VERSION_CHECK=1' \
    > /etc/profile.d/task-shell.sh

RUN pip install --no-cache-dir \
    requests==2.32.3 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    matplotlib==3.9.2 \
    pillow==10.4.0 \
    openpyxl==3.1.5

COPY input_artifacts/ /input_artifacts/

# Graded output lives at /logs/agent/ (container root). Sub-agents sometimes write
# to /workspace/logs/agent/ by mistake; keep both paths equivalent.
RUN mkdir -p /logs/agent/charts /workspace/logs \
    && ln -sfn /logs/agent /workspace/logs/agent

# Live World Bank data is fetched at runtime from the Indicators API.
# Requires outbound network during agent execution.
