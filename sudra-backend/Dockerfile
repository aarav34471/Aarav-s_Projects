FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server_ts.py .
COPY artifacts/config.json artifacts/config.json
COPY artifacts/model_traced.pt artifacts/model_traced.pt

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.getenv('PORT', '8000'), timeout=3).read()"

CMD ["sh", "-c", "uvicorn server_ts:app --host 0.0.0.0 --port ${PORT:-8000}"]
