FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        poppler-utils curl ca-certificates jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pypdf==4.3.1 python-pptx==1.0.2 openai==1.109.1

COPY input_artifacts/ /input_artifacts/

COPY prepare_chapters.py /opt/prepare_chapters.py

COPY assemble_deck.py /opt/assemble_deck.py

# Pre-split the book into per-chapter text files at /opt/book_chapters so every run
# (single-agent and multi-agent alike) reads one small chapter file instead of the
# ~30MB PDF. Runs synchronously at build; on detection failure an UNAVAILABLE marker
# is written and readers fall back to the PDF.
RUN python3 /opt/prepare_chapters.py /input_artifacts/Principles_Finance.pdf /opt/book_chapters \
    && ls -la /opt/book_chapters

WORKDIR /workspace
