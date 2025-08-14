FROM python:3.12

# Set working directory
WORKDIR /app

RUN echo "Container build complete. Setting default command..."

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the read_and_process requirements file from its folder
COPY ./read_and_process/requirements.txt . 

# Set a temporary directory for pip, ensuring it's writable
ENV TMPDIR=/app/tmp
RUN mkdir -p /app/tmp 
    
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt
    
RUN rm -rf /app/tmp/*


# Copy shared vector_db folder and the entire read_and_process folder 
# into the working directory.
COPY vector_db ./vector_db
COPY ./read_and_process . 

# Ensure the temp_uploads directory exists (for file uploads)
RUN mkdir -p temp_uploads

# Expose port 8001 (you can include EXPOSE 8001 if desired)
EXPOSE 8001

RUN echo "Container build complete. Setting default command..."
# Start the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]

