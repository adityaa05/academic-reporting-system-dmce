# backend/Dockerfile

# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential

# Copy the uv executable from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml uv.lock* ./

# Install dependencies directly into the system environment
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY ./app ./app

# Expose the port Cloud Run expects
EXPOSE 8080

# Command to run the production server
CMD ["fastapi", "run", "app/main.py", "--port", "8080"]