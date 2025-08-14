FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# System dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./similarity_search/requirements.txt .

# Set a temporary directory for pip, ensuring it's writable
ENV TMPDIR=/app/tmp
RUN mkdir -p /app/tmp 
    
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt
    
RUN rm -rf /app/tmp/*
# Copy only necessary files
COPY ./similarity_search .
COPY ../vector_db ./vector_db

# Optional: If you have config or utils modules
# COPY config/ ./config/
# COPY utils/ ./utils/

# Start the service
CMD ["python", "-u", "main.py"]
