FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home lungcare && mkdir -p /data/uploads /data/reports && chown -R lungcare:lungcare /app /data
USER lungcare
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=15s --start-period=180s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/ready', timeout=12)" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "180", "wsgi:app"]
