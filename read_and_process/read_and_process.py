import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from process_images import process_images
from vector_db.vector_db import Vector_DB
from vector_db.qdrant_init import collection_name

vector_db = Vector_DB(collection_name=collection_name)

text_splitter=SentenceTransformersTokenTextSplitter(
                chunk_overlap=50,
                model_name="sentence-transformers/all-mpnet-base-v2"
            )

def chunk_and_embed(directory):
    chunks=[]

    for file in os.listdir(path=directory):
        file_name=f"{directory}/{file}"
        print(file_name)
        chunk = process_images(file_path=file_name)
        print(f"Process images done {chunk}")
        chunks.extend(chunk)
    
    print(f"Chunks after processing image {chunks}")
    
    ids = [ str(uuid4()) for _ in range(len(chunks)) ]

    vector_db.ingest(documents=chunks, uuids=ids)

# chunk_and_embed(directory="../temp_uploads")