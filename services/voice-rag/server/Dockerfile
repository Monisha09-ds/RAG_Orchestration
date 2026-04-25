FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency file and install
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy source code
COPY server/ ./server/

EXPOSE 5000

CMD ["uv", "run", "python", "server/app.py"]
