FROM python:3.11-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY server/ ./server/
COPY .env ./

# Expose port
EXPOSE 5000

# Run the application
CMD ["uv", "run", "python", "server/app.py"]
