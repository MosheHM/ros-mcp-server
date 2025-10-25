# Multi-stage Dockerfile for ROS MCP Server
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Production stage
FROM python:3.10-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from base stage
COPY --from=base /root/.cargo/bin/uv /usr/local/bin/uv

# Copy installed dependencies from base
COPY --from=base /app/.venv /app/.venv

# Copy application code
COPY server.py ./
COPY server.json ./
COPY config/ ./config/
COPY utils/ ./utils/

# Set environment to production
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Run server
CMD ["/app/.venv/bin/python", "server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "9000"]
