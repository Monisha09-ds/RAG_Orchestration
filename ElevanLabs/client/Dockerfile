FROM python:3.11-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY client/ ./client/

# Expose port
EXPOSE 8501

# Run the application
CMD ["uv", "run", "streamlit", "run", "client/app.py", "--server.address=0.0.0.0"]
