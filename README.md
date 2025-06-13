# EvalKit

An open-source evaluation and optimization system for LLM-powered features, with a focus on retrieval-augmented generation (RAG).

## Features

- Track and test various metrics for LLM-powered features
- Support for multiple vector stores (FAISS and pgvector)
- Comprehensive evaluation system
- Real-time monitoring and metrics collection
- Beautiful Streamlit dashboard
- Docker support for easy deployment

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/evalkit.git
cd evalkit
```

2. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the services:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## Vector Store Options

EvalKit supports two vector store implementations:

### FAISS
- In-memory vector store
- Fast similarity search
- Good for development and testing
- Configure with `VECTOR_STORE_TYPE=faiss`

### pgvector
- PostgreSQL-based vector store
- Persistent storage
- Production-ready
- Configure with `VECTOR_STORE_TYPE=pgvector`

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -e .
```

3. Initialize the database:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn evalkit.api.main:app --reload
```

## API Usage

### Record an Interaction

```python
import requests

response = requests.post(
    "http://localhost:8000/interactions",
    json={
        "query": "What is the capital of France?",
        "response": "The capital of France is Paris.",
        "metadata": {
            "model": "gpt-4",
            "temperature": 0.7
        }
    }
)
```

### Run an Evaluation

```python
response = requests.post(
    "http://localhost:8000/evaluations",
    json={
        "interaction_id": 1,
        "criteria": {
            "relevance": 0.9,
            "coherence": 0.8,
            "completeness": 0.7
        }
    }
)
```

## Monitoring

EvalKit includes comprehensive monitoring through Prometheus and Grafana:

- Track interaction counts
- Monitor response times
- Analyze evaluation scores
- Set up alerts for performance issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 