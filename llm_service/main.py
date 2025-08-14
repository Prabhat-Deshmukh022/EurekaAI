from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
from language_model_api import language_model_api
import os

# Kafka config
KAFKA_CONSUMER_TOPIC = "similarity_search_topic"
KAFKA_PRODUCER_TOPIC = "llm_response_topic"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")

async def query_model( kafka_producer: AIOKafkaProducer, kafka_consumer: AIOKafkaConsumer):
    async for msg in kafka_consumer:
        try:
            data = json.loads(msg.value.decode("utf-8"))
            session_id = data.get("session_id")
            relevant_docs = data.get("relevant_docs")
            query = data.get("question")

            if not relevant_docs or not query or relevant_docs==[]:
                print(f"⚠️ Missing data for session_id {session_id}")
                continue

            docs = [doc["content"] for doc in relevant_docs]

            # print(relevant_docs)
            
            context_str = "---- CONTEXT {0} ------\n{1}\n"

            metadata_str = "------ METADATA {0} -------\n{1}\n"

            numbered_contexts = [
                context_str.format(idx, context)
                for idx, context in enumerate(docs)
                if context.strip()
            ]

            numbered_metadata = [
                metadata_str.format(idx, json.dumps(context["metadata"], indent=2))
                for idx, context in enumerate(relevant_docs)
            ]

            prompt_template = (
                "You are a helpful AI assistant. Answer the question based only on the provided context and the attached metadata.\n"
                "If the answer is not directly in the context, try to infer it.\n"
                "If the answer isn't clear even then, say that you do not know. NEVER make up information.\n\n"
                "Context:\n{contexts}\n\n"
                "Metadata:\n{metadata}\n\n"
                "Question: {query}\n"
                "Answer:"
            )

            
            final_prompt = prompt_template.format(
                contexts="".join(numbered_contexts),
                metadata="".join(numbered_metadata),
                query=query.strip()
            )

            answer = language_model_api(1,prompt=final_prompt)

            message={
                "session_id":session_id,
                "answer":answer
            }

            await kafka_producer.send_and_wait(topic=KAFKA_PRODUCER_TOPIC, value=json.dumps(message).encode("utf-8"))
        
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
    await kafka_consumer.start()

    try:
        await query_model(kafka_producer, kafka_consumer)
    finally:
        await kafka_producer.stop()
        await kafka_consumer.stop()
        print("🛑 Kafka producer and consumer stopped.")


if __name__ == "__main__":
    asyncio.run(main())

