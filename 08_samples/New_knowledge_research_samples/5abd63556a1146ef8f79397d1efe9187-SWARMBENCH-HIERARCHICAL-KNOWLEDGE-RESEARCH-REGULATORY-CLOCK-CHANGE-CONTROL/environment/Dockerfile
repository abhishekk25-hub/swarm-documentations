FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /workspace/.git /root/.git

COPY input_artifacts/ /input_artifacts/

RUN find /input_artifacts -type f -exec chmod 0444 {} \; \
    && find /input_artifacts -type d -exec chmod 0555 {} \;

CMD ["sleep", "infinity"]
