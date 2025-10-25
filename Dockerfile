FROM python:3.10-slim

WORKDIR /app
COPY . /app


# Install system dependencies if your app needs them (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["python3", "app.py"]