FROM python:3.11.9-slim

# Network access is required — agents browse live vendor trust pages,
# public certification registries (FedRAMP, CSA STAR, ISO), and
# regulatory guidance pages (ICO, FTC) during the run.

RUN pip install --no-cache-dir openpyxl==3.1.5 xlsxwriter==3.2.9 requests==2.34.2

WORKDIR /workspace

RUN mkdir -p /logs/agent /logs/verifier /workspace
