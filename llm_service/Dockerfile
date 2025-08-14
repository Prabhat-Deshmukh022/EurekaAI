FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# System dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY main.py .
COPY language_model_api.py .

# Optional: If you have config or utils modules
# COPY config/ ./config/
# COPY utils/ ./utils/

# Start the service
CMD ["python", "main.py"]
