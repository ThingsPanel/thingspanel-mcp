FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/thingspanel-mcp /usr/local/bin/

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start the MCP server with SSE by default for containerized environments
ENTRYPOINT ["thingspanel-mcp", "--transport", "sse"] 