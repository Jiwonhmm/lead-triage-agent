# 1) Base image: slim Python 3.12 (matches .python-version)
FROM python:3.12-slim

# 2) Copy the uv binary from its official image
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# 3) Install dependencies first, so this layer is cached when only code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 4) Copy the application code and data
COPY app ./app
COPY data ./data

# 5) Run the API with the virtualenv uv created
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
