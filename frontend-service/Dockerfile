# --- Stage 1: Build Dependencies ---
# Use a specific slim version for consistency.
FROM python:3.10-slim AS builder

WORKDIR /app

# Copy and install the lightweight requirements for the frontend service.
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Production Image ---
# Start with a clean, slim base image.
FROM python:3.10-slim

# --- System Dependencies & User Setup ---
# Install curl for the HEALTHCHECK and create a non-root user.
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system app && adduser --system --group app

# Set working directory
WORKDIR /app

# --- Copy Application Code & Dependencies ---
# Copy installed Python packages from the builder stage.
COPY --from=builder /root/.local /home/app/.local
# Copy the application files.
COPY --chown=app:app main.py .
COPY --chown=app:app frontend ./frontend

# --- Set Environment Variables ---
# Add the user's local bin directory to the PATH to find uvicorn.
ENV PATH="/home/app/.local/bin:${PATH}"
# Tell Python where to find the installed packages.
ENV PYTHONPATH="/home/app/.local/lib/python3.10/site-packages"
# Standard Python in Docker best practices.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Declare the environment variable the app needs to connect to the RAG service.
ENV RAG_SERVICE_URL=""

# --- Switch to non-root user ---
USER app

# --- Expose Port ---
EXPOSE 8000

# --- Healthcheck ---
# Periodically check if the application is healthy.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# --- Run the Application ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]