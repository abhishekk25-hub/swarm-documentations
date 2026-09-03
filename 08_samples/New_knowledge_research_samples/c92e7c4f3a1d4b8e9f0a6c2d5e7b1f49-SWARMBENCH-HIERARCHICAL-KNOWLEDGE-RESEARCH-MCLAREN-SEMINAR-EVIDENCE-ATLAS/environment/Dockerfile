FROM python:3.12-slim

RUN pip install --no-cache-dir beautifulsoup4==4.12.3 pypdf==5.1.0 requests==2.32.3

COPY input_artifacts/ /input_artifacts/
WORKDIR /workspace
