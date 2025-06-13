# EvalKit Architecture

## Overview

EvalKit is a production-grade evaluation and optimization system for LLM-powered features, with a focus on RAG (Retrieval-Augmented Generation) systems. It provides tools for tracking, testing, and preventing regressions in retrieval quality, model faithfulness, latency, and cost.

## Core Components

### 1. API Layer (`evalkit/api/`)
- FastAPI-based REST API
- Endpoints for:
  - Interaction recording (`/interactions`)
  - Evaluation management (`/evaluations`)
- Schema definitions for request/response models
- CORS middleware for cross-origin requests

### 2. Database Layer (`evalkit/db/`)
- SQLAlchemy models for:
  - `Interaction`: Stores user queries and responses
  - `Evaluation`: Stores evaluation results
  - `GoldenDataset`: Stores reference data for evaluation
  - `VectorStore`: Stores vector store configurations
- Async database operations
- Alembic migrations for schema management
- SQLite (dev) → PostgreSQL (prod) support

### 3. Evaluation System (`evalkit/eval/`)
- Base `Scorer` interface
- `GPTScorer` implementation using OpenAI models
- Evaluation criteria:
  - Relevance
  - Accuracy
  - Completeness
  - Clarity
- Factory pattern for scorer creation

### 4. Vector Store (`evalkit/vector/`)
- Abstract `VectorStore` interface
- `FAISSStore` implementation
- Features:
  - Vector similarity search
  - Metadata storage
  - Performance metrics
  - GPU support (optional)

### 5. Metrics Collection (`evalkit/metrics/`)
- Prometheus integration
- Metrics tracked:
  - Interaction counts
  - Evaluation counts
  - Latency histograms
  - Cost tracking
  - Score distributions
- Context manager for metric recording

### 6. CLI Interface (`evalkit/cli/`)
- Rich-based terminal UI
- Commands:
  - `evaluate`: Run evaluations
  - `list_interactions`: View recent interactions
  - `metrics`: Show evaluation metrics

## Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key
- `SECRET_KEY`: Application secret key
- `ENABLE_METRICS`: Toggle metrics collection

### Settings Management
- Pydantic-based configuration
- Environment file support
- Cached settings instance

## Development Setup

### Local Development
1. Virtual environment setup
2. Database initialization
3. Development server
4. Docker Compose for full stack

### Docker Environment
- Multi-container setup:
  - API service
  - Prometheus
  - Grafana
- Volume mounts for development
- Environment variable management

### CI/CD Pipeline
- GitHub Actions workflow
- Jobs:
  - Testing
  - Linting
  - Type checking
  - Automated evaluation

## Monitoring

### Prometheus
- Metrics collection
- Scrape configuration
- Storage management

### Grafana
- Dashboard setup
- Metric visualization
- Alert configuration

## Data Flow

1. **Interaction Recording**
   ```
   Client → API → Database
   ```

2. **Evaluation Process**
   ```
   Interaction → Scorer → Evaluation → Database
   ```

3. **Vector Search**
   ```
   Query → Vector Store → Results → Client
   ```

4. **Metrics Collection**
   ```
   Operations → Metrics Collector → Prometheus → Grafana
   ```

## Security

- API authentication (HMAC/Bearer)
- Environment-based secrets
- Non-root Docker user
- CORS configuration

## Performance Considerations

- Async database operations
- Vector store optimization
- Metrics collection overhead
- Docker resource limits

## Future Improvements

1. **Vector Store**
   - Qdrant integration
   - pgvector support
   - Hybrid search

2. **Evaluation**
   - Custom evaluation criteria
   - Multi-model support
   - Batch processing

3. **Monitoring**
   - Custom dashboards
   - Alert rules
   - Cost tracking

4. **API**
   - Authentication
   - Rate limiting
   - API versioning 