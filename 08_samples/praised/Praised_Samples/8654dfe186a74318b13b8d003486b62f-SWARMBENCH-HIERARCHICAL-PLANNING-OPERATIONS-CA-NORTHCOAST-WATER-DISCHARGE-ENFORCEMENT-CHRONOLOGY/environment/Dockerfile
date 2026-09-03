FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl git ca-certificates jq && rm -rf /var/lib/apt/lists/*

# Generation libraries the AGENT uses at runtime (fetching + parsing the enforcement
# order PDFs, the docx dossier, png charts, csv/tabular work) and the parsing libraries
# the VERIFIER uses to open and grade those same artifacts. Kept in one image so the
# judge can read every modality the agent produces.
RUN pip install --no-cache-dir \
    python-docx==1.1.2 \
    matplotlib==3.9.2 \
    Pillow==10.4.0 \
    pypdf==5.1.0 \
    pandas==2.2.3 \
    requests==2.32.3 \
    beautifulsoup4==4.12.3

# Nothing else is copied into the agent image. The source orders are NOT shipped: the
# agent fetches the enforcement order PDFs live from the North Coast Water Board
# adopted-orders portal, so browsing is genuinely load-bearing. instruction.md,
# decomposition.yaml, task.toml and tests/ must never enter the agent image.

WORKDIR /workspace
