FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency file and install
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy source code
COPY client/ ./client/

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "client/app.py", "--server.address=0.0.0.0"]
