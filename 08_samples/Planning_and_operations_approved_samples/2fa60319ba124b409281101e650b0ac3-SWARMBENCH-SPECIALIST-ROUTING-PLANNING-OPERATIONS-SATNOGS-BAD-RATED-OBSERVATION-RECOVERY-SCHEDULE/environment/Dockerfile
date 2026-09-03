FROM python:3.12-slim-bookworm

# Libraries the agent needs to read the packaged inputs. The grader adds nothing
# of its own: tests/verify.py runs on the standard library, reusing pypdf only to
# resolve page citations against the shipped PDF.
RUN pip install --no-cache-dir pandas==2.2.3 pypdf==5.1.0 beautifulsoup4==4.12.3 lxml==5.3.0

WORKDIR /workspace

COPY input_artifacts/ /input_artifacts/
