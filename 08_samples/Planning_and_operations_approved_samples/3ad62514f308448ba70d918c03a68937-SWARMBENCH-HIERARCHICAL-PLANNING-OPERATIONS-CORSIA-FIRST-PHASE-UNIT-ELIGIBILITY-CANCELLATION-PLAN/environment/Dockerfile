FROM python:3.12-slim-bookworm

WORKDIR /

# The agent reads the pinned public sources and the registry extracts. tests/ is not copied:
# it carries the grader and the recomputed clearance.
COPY input_artifacts/ /input_artifacts/

RUN mkdir -p /logs/agent /logs/verifier /workspace
WORKDIR /workspace
