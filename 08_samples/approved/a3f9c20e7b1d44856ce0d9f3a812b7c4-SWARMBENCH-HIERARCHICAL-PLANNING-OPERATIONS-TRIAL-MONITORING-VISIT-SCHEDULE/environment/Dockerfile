FROM python:3.11.9-slim

# This task is ONLINE on purpose: the agent must read each trial's CURRENT record on
# ClinicalTrials.gov (public, no auth) to score site risk. curl is provided for the
# public v2 API (https://clinicaltrials.gov/api/v2/studies/<NCT>). No answer key is
# reachable online - the risk rules and the visit budget live only in instruction.md,
# and grading is done offline against a pinned oracle.
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# python-docx: the agent writes (and the judge reads) scheduling_rationale.docx.
# The verifier-only dependency (openai, for the memo grader) is installed by tests/test.sh,
# not baked into the agent image.
RUN pip install --no-cache-dir python-docx==1.1.2

# The roster is the only staged input (real trial sites; NO risk labels, NO answer key).
COPY input_artifacts/ /input_artifacts/

WORKDIR /workspace

RUN mkdir -p /logs/agent /logs/verifier /workspace /tests /solution
