import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from qdrant.qdrant_init import qdrant_client
from .qdrant_init import qdrant_client
from qdrant_client.http.models import VectorParams, Distance, SparseVectorParams
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import models
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain.schema import Document
from sentence_transformers import CrossEncoder

class Vector_DB:
    def __init__(self, collection_name:str):

        self.embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.fast_embeddings=FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name=collection_name

        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        try:
            qdrant_client.get_collection(collection_name=self.collection_name)
        except Exception:
            qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "dense":VectorParams(
                        size=768,
                        distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                }
            )

        self.__hybrid_vector_store=QdrantVectorStore(
            client=qdrant_client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
            sparse_embedding=self.fast_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse"
        )

        self.__dense_vector_store=QdrantVectorStore(
            client=qdrant_client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
            retrieval_mode=RetrievalMode.DENSE,
            vector_name="dense"
        )

        # qdrant_client.optimize_collection(collection_name=self.collection_name)
        # qdrant_client.u
    
    def get_vector_db_instance(self):
        return self.__hybrid_vector_store
    
    def ingest(self,documents:list[Document], uuids:list[str]):
        self.__hybrid_vector_store.add_documents(documents=documents, ids=uuids)

    def dense_retrieval(self, user_query:str, top_k:int = 7 ) -> list[tuple[Document,float]]:
        print(qdrant_client.get_collection(self.collection_name))

        documents = self.__dense_vector_store.similarity_search_with_relevance_scores(query=user_query, k=top_k)
        print("DENSE2")

        return documents
    
    def hybrid_retrieval(self, user_query, top_k:int = 7) -> list[tuple[Document,float]]:
        documents = self.__hybrid_vector_store.similarity_search_with_relevance_scores(query=user_query, k=top_k)
        print("HYBRID")

        return documents
    
    def rerank_retrieval(self, user_query, top_k:int = 7) -> list[tuple[Document,float]]:
        initial_docs = self.dense_retrieval(user_query=user_query, top_k=top_k)
        print("RERANKER")

        docs = [item[0] for item in initial_docs]

        to_rerank = [(user_query,doc.page_content) for doc in docs]
        scores = self.reranker.predict(sentences=to_rerank)

        reranked = sorted(zip(docs,scores), key=lambda x:x[1], reverse=True)
        # print(reranked)

        return reranked