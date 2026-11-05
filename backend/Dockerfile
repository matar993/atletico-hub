# Build context: backend/. Runs the Atletico Hub API.
FROM ghcr.io/astral-sh/uv:0.13.5-trixie-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_NO_CACHE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app \
    && mkdir -p "$UV_PYTHON_INSTALL_DIR"

WORKDIR /app
COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev \
    && chmod -R a+rX "$UV_PYTHON_INSTALL_DIR" /opt/venv

COPY src src
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "atletico_hub.main:app", "--host", "0.0.0.0", "--port", "8000"]

# The development stack, which also runs the tests. The sources are mounted, editable.
FROM base AS dev
# /app belongs to root, so pytest cannot keep its cache there, and coverage writes its data to /tmp.
ENV PYTEST_ADDOPTS="-p no:cacheprovider" \
    COVERAGE_FILE=/tmp/.coverage
RUN uv sync --frozen \
    && chmod -R a+rX "$UV_PYTHON_INSTALL_DIR" /opt/venv
USER app

# Last stage: what a plain `docker build` produces.
FROM base AS runtime
RUN uv sync --frozen --no-editable --no-dev \
    && chmod -R a+rX "$UV_PYTHON_INSTALL_DIR" /opt/venv
USER app
