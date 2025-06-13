# EvalKit Quick Start Guide

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- OpenAI API key (for evaluation)

## Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/evalkit.git
   cd evalkit
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

2. **Environment Setup**
   Create a `.env` file:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./evalkit.db
   OPENAI_API_KEY=your-api-key
   SECRET_KEY=your-secret-key
   ```

3. **Database Initialization**
   ```bash
   alembic upgrade head
   ```

4. **Start Development Server**
   ```bash
   uvicorn evalkit.api.main:app --reload
   ```

## Docker Setup

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

2. **Access Services**
   - API: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

## Basic Usage

### 1. Record an Interaction

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/interactions",
    json={
        "query": "What is RAG?",
        "response": "Retrieval-Augmented Generation...",
        "metadata": {"source": "test"}
    }
)
```

### 2. Run Evaluations

```bash
evalkit evaluate --dataset golden --model gpt-4
```

### 3. View Interactions

```bash
evalkit list-interactions --limit 10 --with-evaluations
```

### 4. Check Metrics

```bash
evalkit metrics --days 7
```

## API Endpoints

### Interactions

- `POST /api/v1/interactions`: Create new interaction
- `GET /api/v1/interactions`: List interactions

### Evaluations

- `POST /api/v1/evaluations`: Create new evaluation
- `GET /api/v1/evaluations`: List evaluations

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Run Tests**
   ```bash
   pytest
   ```

3. **Check Code Quality**
   ```bash
   ruff check .
   mypy evalkit
   ```

4. **Create Pull Request**

## Monitoring

1. **Access Grafana**
   - URL: http://localhost:3000
   - Default credentials: admin/admin

2. **View Metrics**
   - Interaction counts
   - Evaluation scores
   - Latency metrics
   - Cost tracking

## Common Issues

1. **Database Connection**
   - Check `DATABASE_URL` in `.env`
   - Ensure database is initialized

2. **OpenAI API**
   - Verify API key in `.env`
   - Check API rate limits

3. **Docker Issues**
   - Clear Docker volumes: `docker-compose down -v`
   - Rebuild: `docker-compose up --build`

## Next Steps

1. Review [Architecture Documentation](ARCHITECTURE.md)
2. Set up monitoring dashboards
3. Configure CI/CD pipeline
4. Add custom evaluation criteria 