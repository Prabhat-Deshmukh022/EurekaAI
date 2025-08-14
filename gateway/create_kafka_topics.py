import asyncio
import os
import uuid
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "gateway")
UNIQUE_ID = str(uuid.uuid4())[:8]  # Or load from env or file

TOPICS = [
   "gateway_topic",
   "preprocessed_topic",
   "similarity_search_topic",
   "llm_response_topic",
   
]

async def create_topics():
    admin = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await admin.start()
    try:
        topic_objs = [NewTopic(name=topic, num_partitions=1, replication_factor=1) for topic in TOPICS]
        await admin.create_topics(topic_objs, validate_only=False)
        print(f"✅ Topics created: {TOPICS}")
    except Exception as e:
        print(f"⚠️ Error creating topics: {e}")
    finally:
        await admin.close()

if __name__ == "__main__":
    asyncio.run(create_topics())
