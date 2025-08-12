# --- Stage 1: Build Dependencies ---
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Production Image ---
FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system app && adduser --system --group app

WORKDIR /app


COPY --from=builder /root/.local /home/app/.local

COPY --chown=app:app main.py .
COPY --chown=app:app frontend ./frontend


ENV PATH="/home/app/.local/bin:${PATH}"

ENV PYTHONPATH="/home/app/.local/lib/python3.10/site-packages"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV RAG_SERVICE_URL=""


USER app


EXPOSE 8000

# --- Healthcheck ---

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# --- Run the Application ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]