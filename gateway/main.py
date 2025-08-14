import json
from typing import Dict
from fastapi import FastAPI, Form, WebSocket
from uuid import uuid4
import redis.asyncio as redis
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from contextlib import asynccontextmanager

kafka_producer = None
kafka_consumer = None
gateway_id = str(uuid4())

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "gateway_topic"
ANSWER_TOPIC = f"answer.{gateway_id}"

redis_client = None
REDIS_HOST = "redis"
REDIS_PORT = 6379

websocket_sessions: Dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app:FastAPI):
    global kafka_producer
    global redis_client
    global kafka_consumer

    redis_client = await redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)

    kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await kafka_producer.start()

    try:
        admin_client = KafkaAdminClient(bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS)
        topic = NewTopic(name=ANSWER_TOPIC, num_partitions=1, replication_factor=1)
        admin_client.create_topics([topic])
        print(f"Created topic {ANSWER_TOPIC}")
    
    except TopicAlreadyExistsError:
        print(f"Topic {ANSWER_TOPIC} already exists")
    
    except Exception as e:
        print(f"Topic creation exception {e}")
    
    finally:
        admin_client.close()

    kafka_consumer = AIOKafkaConsumer(ANSWER_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=gateway_id, enable_auto_commit=True)
    await kafka_consumer.start()

    asyncio.create_task(dispatcher_listener())

    print("Kafka producer, consumer and redis started")
    try:
        yield
    except Exception as e:
        print(f"Exception occurred in starting kafka producer {e}")
    finally:
        await kafka_producer.stop()


app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def gateway(websocket:WebSocket):
    await websocket.accept()
    print("🔌 WebSocket connected", flush=True)

    try:
        while True:
            print("Waiting for message...", flush=True)
            user_query = await websocket.receive_text()
            print(f"Sent user query - {user_query}", flush=True)
            session_id = str(uuid4())

            websocket_sessions[session_id] = websocket
            await redis_client.set(session_id,gateway_id,ex=600)

            message = {
                "question":user_query,
                "session_id":session_id
            }

            print(f"Sending to Kafka: {message}", flush=True)
            await kafka_producer.send_and_wait(KAFKA_TOPIC, value=json.dumps(message).encode("utf-8"))
            print("Message sent to Kafka", flush=True)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
    finally:
        # Clean up all WebSockets that may remain
        for sid, ws in list(websocket_sessions.items()):
            if ws == websocket:
                del websocket_sessions[sid]

async def dispatcher_listener():
    print("Dispatcher listener started", flush=True)  
    async for msg in kafka_consumer:
        try:
            data = json.loads(msg.value.decode("utf-8")) 
            print(f"DATA received {data}")
            session_id = data.get("session_id")
            answer = None

            if "error" in data:
                answer = data.get("error")
            else: 
                answer = data.get("answer")

            ws = websocket_sessions.get(session_id)

            if ws:
                await ws.send_text(answer)
                # await ws.close()
                # del websocket_sessions[session_id]
        
        except Exception as e:
            print(f"Exception occurred {e}")
            await ws.send_text(f"Exception occurred {e}")

