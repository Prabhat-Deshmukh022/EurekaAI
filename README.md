# EurekaAI Pipeline

EurekaAI Pipeline is a modular, microservices-based AI system for real-time question answering and document retrieval. It leverages state-of-the-art language models, semantic search, and scalable infrastructure to deliver fast, accurate responses to user queries.

## Features

- **Microservices Architecture:** Each stage of the pipeline is a separate service for easy scaling and maintenance.
- **Real-Time Question Answering:** Supports concurrent multi-client interactions via WebSocket and HTTP APIs.
- **Semantic Similarity Search:** Uses vector databases (Qdrant) for dense and hybrid document retrieval.
- **Large Language Model Integration:** Generates answers and summaries using advanced LLMs.
- **Asynchronous Communication:** Kafka connects all services for robust, decoupled message passing.
- **Session Management:** Redis ensures efficient tracking and routing of client sessions.
- **Containerized Deployment:** All services are Dockerized for portability and scalability.

## Architecture Overview

```
Client
  │
  ▼
Gateway (WebSocket/HTTP) ──► Kafka ──► Pre-Processor ──► Kafka ──► Similarity Search ──► Kafka ──► LLM Service
  ▲                                                                                                   │
  └────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Gateway:** Entry point for clients, manages sessions, and routes responses.
- **Pre-Processor:** Cleans and normalizes incoming questions.
- **Similarity Search:** Finds relevant documents using semantic search.
- **LLM Service:** Generates answers and summaries.
- **Vector DB:** Stores and retrieves document embeddings.
- **WebSocket Dispatcher:** (Optional) Manages multiple WebSocket clients.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Kafka and Redis running (can be started via Docker Compose)

### Clone the Repository

```bash
git clone https://github.com/yourusername/eurekaai-pipeline.git
cd EurekaAI
```

### Build and Start Services

Each service has its own Dockerfile. You can build and run all services using Docker Compose or individually:

```bash
docker-compose up --build
```

Or run services manually:

```bash
cd gateway
docker build -t gateway .
docker run --network="host" gateway
# Repeat for other services
```

### Environment Variables

- Place your API keys and configuration in the `.env` files for each service (see `llm_service/.env` for example).

### Usage

- Connect a client to the Gateway WebSocket (`ws://localhost:8000/ws`) or send HTTP requests.
- The system will process your question and return answers in real time.

## Folder Structure

```
gateway/               # Client entrypoint, session management
pre_processor/         # Text cleaning and normalization
similarity_search/     # Semantic search and retrieval
vector_db/             # Vector database integration
llm_service/           # Language model API and answer generation
websocket_dispatcher/  # (Optional) WebSocket client management
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License

## Contact

For questions or support, please open an issue or contact [your.email@example.com](mailto:your.email@example.com)
