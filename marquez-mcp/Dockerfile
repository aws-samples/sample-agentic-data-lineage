# Multi-stage build for smaller final image
FROM python:3.13-slim AS builder

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to a virtual environment
RUN uv sync --frozen --no-dev

# Final stage - minimal runtime image
FROM python:3.13-slim

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --no-log-init --shell /bin/bash --uid 1000 app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=app:app server.py settings.py settings.toml ./

# Switch to non-root user
USER app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check (simplified)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=2 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "server.py"]
