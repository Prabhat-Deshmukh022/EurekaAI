import json
import asyncio
import redis.asyncio as redis
import re
from langdetect import detect
from better_profanity import profanity
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
# import aioredis

# Kafka config
KAFKA_CONSUMER_TOPIC = "gateway_topic"
KAFKA_PRODUCER_TOPIC = "preprocessed_topic"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

# Redis config
REDIS_HOST = "redis"
REDIS_PORT = 6379

# Query validation config
MIN_QUERY_LEN = 5
MAX_QUERY_LEN = 512
BANNED_TOPICS = ["suicide", "kill myself", "bomb", "terrorist"]

# Initialize profanity filter
profanity.load_censor_words()

def validate_query(query: str) -> tuple[bool, str]:
    query = query.strip()

    print(f"The query is {query} IN PREPROCESSOR!")

    if not query:
        return False, "Query cannot be empty."
    if len(query) < MIN_QUERY_LEN:
        return False, "Query is too short."
    if len(query) > MAX_QUERY_LEN:
        return False, "Query is too long."
    if re.fullmatch(r"[^a-zA-Z0-9\s]+", query):
        return False, "Query appears to contain only special characters."
    if len(set(query.lower().split())) <= 1:
        return False, "Query appears to have only repeated words."
    if profanity.contains_profanity(query):
        return False, "Profanity detected in query."
    if any(banned in query.lower() for banned in BANNED_TOPICS):
        return False, "Query contains a restricted topic."

    try:
        if detect(query) != "en":
            return False, "Only English queries are allowed."
    except Exception:
        return False, "Could not detect query language."

    return True, query

async def main():
    # Initialize Redis
    redis_client = await redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)

    # Initialize Kafka
    kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await kafka_producer.start()

    kafka_consumer = AIOKafkaConsumer(
        KAFKA_CONSUMER_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        enable_auto_commit=True
    )
    await kafka_consumer.start()

    print("✅ Preprocessor microservice started.")

    try:
        async for msg in kafka_consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                question = data.get("question")
                session_id = data.get("session_id")

                success, result = validate_query(question)
                gateway_id = await redis_client.get(session_id)
                answer_topic = f"answer.{gateway_id}"

                out_msg = {"session_id": session_id}

                if success:
                    out_msg["preprocessed_result"] = result
                else:
                    out_msg["error"] = result
                    await kafka_producer.send_and_wait(
                        answer_topic,
                        value=json.dumps(out_msg).encode("utf-8")
                    )

                await kafka_producer.send_and_wait(
                    KAFKA_PRODUCER_TOPIC,
                    value=json.dumps(out_msg).encode("utf-8")
                )

            except Exception as e:
                print(f"[❌ Kafka Message Error] {e}")

    except asyncio.CancelledError:
        print("🔁 Shutting down preprocessor...")
    finally:
        await kafka_consumer.stop()
        await kafka_producer.stop()
        await redis_client.close()
        print("❌ Kafka/Redis connections closed.")

if __name__ == "__main__":
    asyncio.run(main())
