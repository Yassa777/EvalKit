# EvalKit

A production-grade evaluation and optimization system for LLM-powered features, with a focus on retrieval-augmented generation (RAG) systems.

## Features

- Real-time query/response ingestion and storage
- Manual and automated evaluation of LLM interactions
- Golden dataset management and testing
- Automated evaluation loops
- CI integration for blocking regressions
- Vector store benchmarking (FAISS, Qdrant, pgvector)
- Active learning from user feedback
- Metrics dashboard integration

## Architecture

### Core Components

1. **Ingestion Service**
   - FastAPI endpoint for real-time query/response capture
   - Authentication via HMAC or Bearer tokens
   - Async database operations

2. **Database Layer**
   - SQLite (development) → PostgreSQL (production)
   - SQLAlchemy ORM with async support
   - Alembic migrations

3. **Evaluation System**
   - Rich-based CLI for manual evaluation
   - Automated evaluation via LLM judges
   - Golden dataset management
   - Active learning integration

4. **Monitoring & Metrics**
   - Prometheus + Grafana integration
   - Latency, cost, and quality metrics
   - Automated alerting

5. **Vector Store Integration**
   - Support for multiple vector stores
   - Benchmarking tools
   - Easy switching between backends

## Getting Started

### Prerequisites

- Python 3.9+
- SQLite (development) or PostgreSQL (production)
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/evalkit.git
   cd evalkit
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn evalkit.api.main:app --reload
   ```

### Usage

1. **Ingesting Data**
   ```python
   import requests

   response = requests.post(
       "http://localhost:8000/api/v1/interactions",
       json={
           "query": "What is RAG?",
           "response": "Retrieval-Augmented Generation...",
           "metadata": {"source": "test"}
       },
       headers={"Authorization": "Bearer your-token"}
   )
   ```

2. **Running Evaluations**
   ```bash
   evalkit evaluate --dataset golden --model gpt-4
   ```

3. **Viewing Metrics**
   ```bash
   evalkit metrics --dashboard
   ```

## Development

### Project Structure

```
evalkit/
├── api/            # FastAPI application
├── core/           # Core business logic
├── db/             # Database models and migrations
├── eval/           # Evaluation system
├── metrics/        # Metrics collection
├── vector/         # Vector store integration
└── cli/            # Command-line interface
```

### Running Tests

```bash
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 