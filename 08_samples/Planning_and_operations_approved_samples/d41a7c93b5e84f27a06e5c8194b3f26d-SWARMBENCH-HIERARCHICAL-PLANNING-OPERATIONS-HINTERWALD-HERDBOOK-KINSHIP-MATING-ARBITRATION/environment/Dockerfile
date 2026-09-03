FROM python:3.12-slim-bookworm

# Libraries for reading the packaged corpus. The grader adds nothing of its own:
# tests/verify.py recomputes the whole pedigree and every derived movement attribute on
# the standard library alone.
RUN pip install --no-cache-dir pandas==2.2.3 beautifulsoup4==4.12.3 lxml==5.3.0

WORKDIR /workspace

# Only the agent-visible working set is copied. tests/ is deliberately not copied: it
# holds health_standing.json, the reconciled standing frozen from the prose herd health
# correspondence, which is the answer to the hardest part of the task.
COPY input_artifacts/ /input_artifacts/
