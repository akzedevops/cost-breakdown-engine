FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user — the app only needs read access to its own files
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
