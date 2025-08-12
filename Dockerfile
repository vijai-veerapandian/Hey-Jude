# --- Stage 1: Build Dependencies ---
# Use a specific slim version for consistency. This stage installs dependencies.
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Install dependencies as a non-root user to a specific path.
# This avoids potential permission issues during the build.
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Production Image ---
# Start with a clean, slim base image for the final container.
FROM python:3.10-slim

# --- System Dependencies & User Setup ---
# Running as root temporarily to install 'curl' for the HEALTHCHECK
# and create a dedicated non-root user for the application.
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system app && adduser --system --group app

# --- Create a writable cache directory for Hugging Face ---
# This directory will be used to store downloaded models.
RUN mkdir -p /home/app/.cache/huggingface && \
    chown -R app:app /home/app/.cache

# Set working directory
WORKDIR /app

# --- Copy Application Code & Dependencies ---
# Copy installed Python packages from the builder stage.
COPY --from=builder /root/.local /home/app/.local
# Copy the application code, setting the owner to the non-root 'app' user.
COPY --chown=app:app ./app /app

# --- Set Environment Variables for the non-root user ---
# Add the user's local bin directory to the PATH. This ensures 'uvicorn' can be found.
ENV PATH="/home/app/.local/bin:${PATH}"
# Tell Python where to find the installed packages.
ENV PYTHONPATH="/home/app/.local/lib/python3.10/site-packages"
# Prevents Python from writing .pyc files to disc.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED=1
# Point Hugging Face libraries to the writable cache directory.
ENV HF_HOME="/home/app/.cache/huggingface"
# Declare the environment variable that the application will use.
# The actual value will be provided at runtime.
ENV OLLAMA_BASE_URL=""

# --- Switch to non-root user ---
# From this point on, all commands run as the 'app' user for better security.
USER app

# --- Expose Port ---
# The application runs on port 8000.
EXPOSE 8000

# --- Healthcheck ---
# Docker will periodically check if the application is healthy by curling the root endpoint.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# --- Run the Application ---
# The command to start the FastAPI server when the container launches.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]