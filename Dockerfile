FROM python:3.11-slim

# LibreOffice (headless) is required by the Time Card -> PDF tool.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice-calc \
        fonts-dejavu \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV NO_BROWSER=1 PORT=10000
EXPOSE 10000

# 1 worker + threads keeps memory under the free-tier 512MB limit;
# long timeout so LibreOffice conversions finish.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 180 --worker-class gthread app:app"]
