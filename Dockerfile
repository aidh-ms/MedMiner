# Build stage
FROM python:3.13-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project into the intermediate image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-default-groups --python-preference only-system


# Final image stage
FROM python:3.13-slim-bookworm AS final

RUN useradd --user-group --system --create-home --no-log-init app \
    && mkdir -p /app \
    && chown -R app:app /app

WORKDIR /app

COPY --chown=app:app . /app
COPY --from=builder --chown=app:app --chmod=755 /app/.venv /app/.venv
COPY --chown=app:app --chmod=755 docker/start.sh /app/start.sh

RUN chmod +x /app/.venv/bin/*

USER app

ENV VENV_PATH=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["/app/start.sh"]
