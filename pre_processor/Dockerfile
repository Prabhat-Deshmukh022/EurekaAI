FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN echo "Updating apt and installing system dependencies..." && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        python3-dev \
        libpython3-dev \
        libffi-dev \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "Container build complete. Setting default command..."
CMD ["python", "-u", "main.py"]

