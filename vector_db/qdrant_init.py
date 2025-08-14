from qdrant_client import QdrantClient
import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

QDRANT_URL = "http://qdrant:6333"

qdrant_client = QdrantClient(url=QDRANT_URL)

collection_name = "vector"