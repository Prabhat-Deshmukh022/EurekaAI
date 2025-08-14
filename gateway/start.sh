#!/bin/bash

# Create Kafka topics
echo "🔧 Creating Kafka topics..."
python create_kafka_topics.py

# Then start FastAPI
echo "🚀 Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
