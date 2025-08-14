import json
# import aioredis
import redis.asyncio as redis
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_CONSUMER_TOPIC = "llm_response_topic"

REDIS_HOST = "redis"
REDIS_PORT = 6379

async def obtain_messages(redis_client, kafka_consumer, kafka_producer):
    async for msg in kafka_consumer:
        try:
            data = json.loads(msg.value.decode("utf-8"))
            session_id = data.get("session_id")
            answer = data.get("answer")

            if not session_id or not answer:
                print("❌ Invalid message structure:", data)
                continue

            gateway_id = await redis_client.get(session_id)
            if not gateway_id:
                print(f"❌ Gateway ID not found in Redis for session: {session_id}")
                continue

            answer_topic = f"answer.{gateway_id}"

            message = {
                "session_id": session_id,
                "answer": answer
            }

            await kafka_producer.send_and_wait(
                topic=answer_topic,
                value=json.dumps(message).encode("utf-8")
            )

            print(f"✅ Dispatched answer for session {session_id} to topic {answer_topic}")

        except Exception as e:
            print(f"❌ Error while dispatching: {e}")


async def main():
    redis_client = await redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        decode_responses=True
    )

    kafka_consumer = AIOKafkaConsumer(
        KAFKA_CONSUMER_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        enable_auto_commit=True
    )
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )

    await kafka_consumer.start()
    await kafka_producer.start()

    try:
        await obtain_messages(redis_client, kafka_consumer, kafka_producer)
    finally:
        await kafka_consumer.stop()
        await kafka_producer.stop()
        await redis_client.close()
        print("🛑 Dispatcher shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())
