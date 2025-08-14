import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
# from vector_db.vector_db import Vector_DB
# from vector_db.qdrant_init import collection_name

from vector_db.vector_db import Vector_DB
from vector_db.qdrant_init import collection_name

# Kafka config
KAFKA_CONSUMER_TOPIC = "preprocessed_topic"
KAFKA_PRODUCER_TOPIC = "similarity_search_topic"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

vector_db = Vector_DB(collection_name=collection_name)

def similarity_search(query: str, option: int = 2):
    print(f"Question asked {query}")
    results = []

    match option:
        case 1:
            print("🔍 Dense retrieval", flush=True)
            results.extend(vector_db.dense_retrieval(user_query=query, top_k=4))

        case 2:
            print("🔍 Hybrid retrieval", flush=True)
            results.extend(vector_db.hybrid_retrieval(user_query=query, top_k=4))

        case 3:
            print("🔍 Rerank retrieval", flush=True)
            results.extend(vector_db.rerank_retrieval(user_query=query, top_k=4))
    
    print(f"Retrieved raw results: {results}", flush=True)

    relevant_docs = [res[0] for res in results]  
    return relevant_docs

# similarity_search("Who coined the term Compiler?")

async def consume_and_process(kafka_producer: AIOKafkaProducer, kafka_consumer: AIOKafkaConsumer):
    async for msg in kafka_consumer:
        try:
            data = json.loads(msg.value.decode("utf-8"))
            session_id = data.get("session_id")
            question = data.get("preprocessed_result")

            print(f"IN SIMILARITY SEARCH {question}", flush=True)

            if not session_id or not question:
                print("⚠️ Invalid message received, skipping...", flush=True)
                continue

            print(f"📨 Received: {question}", flush=True)

            relevant_docs = similarity_search(query=question)

            # relevant_docs = [doc[:1030] for doc in relevant_docs ]
            print(f"RELEVANT DOCS {relevant_docs}", flush=True)

            out_message = {
                "session_id": session_id,
                "question": question,
                "relevant_docs": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    } for doc in relevant_docs
                ]
            }

            await kafka_producer.send_and_wait(
                topic=KAFKA_PRODUCER_TOPIC,
                value=json.dumps(out_message).encode("utf-8")
            )

            print(f"✅ Sent relevant_docs for session_id: {session_id}", flush=True)

        except Exception as e:
            print(f"❌ Error processing message: {e}")


async def main():
    kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    kafka_consumer = AIOKafkaConsumer(
        KAFKA_CONSUMER_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        enable_auto_commit=True
    )

    await kafka_producer.start()
    print("🚀 Similarity Search Service Started", flush=True)

    await kafka_consumer.start()

    try:
        await consume_and_process(kafka_producer, kafka_consumer)
    finally:
        await kafka_producer.stop()
        await kafka_consumer.stop()
        print("🛑 Kafka producer and consumer stopped.")


if __name__ == "__main__":
    asyncio.run(main())
