from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
INTERACTION_COUNTER = Counter(
    'evalkit_interactions_total',
    'Total number of interactions',
    ['status']
)

EVALUATION_COUNTER = Counter(
    'evalkit_evaluations_total',
    'Total number of evaluations',
    ['evaluator_type', 'status']
)

LATENCY_HISTOGRAM = Histogram(
    'evalkit_latency_seconds',
    'Latency of operations',
    ['operation'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

COST_GAUGE = Gauge(
    'evalkit_cost_usd',
    'Cost of operations in USD',
    ['operation']
)

SCORE_HISTOGRAM = Histogram(
    'evalkit_score',
    'Evaluation scores',
    ['metric'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

class MetricsCollector:
    """Collector for EvalKit metrics."""
    
    @staticmethod
    def record_interaction(status: str = "success") -> None:
        """Record an interaction."""
        INTERACTION_COUNTER.labels(status=status).inc()
    
    @staticmethod
    def record_evaluation(
        evaluator_type: str,
        status: str = "success"
    ) -> None:
        """Record an evaluation."""
        EVALUATION_COUNTER.labels(
            evaluator_type=evaluator_type,
            status=status
        ).inc()
    
    @staticmethod
    def record_latency(
        operation: str,
        duration: float
    ) -> None:
        """Record operation latency."""
        LATENCY_HISTOGRAM.labels(operation=operation).observe(duration)
    
    @staticmethod
    def record_cost(
        operation: str,
        cost: float
    ) -> None:
        """Record operation cost."""
        COST_GAUGE.labels(operation=operation).set(cost)
    
    @staticmethod
    def record_score(
        metric: str,
        score: float
    ) -> None:
        """Record an evaluation score."""
        SCORE_HISTOGRAM.labels(metric=metric).observe(score)

class MetricsContext:
    """Context manager for recording metrics."""
    
    def __init__(
        self,
        operation: str,
        collector: MetricsCollector
    ):
        self.operation = operation
        self.collector = collector
        self.start_time = None
    
    async def __aenter__(self) -> 'MetricsContext':
        self.start_time = time.time()
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> None:
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.collector.record_latency(self.operation, duration)
        
        if exc_type is not None:
            self.collector.record_interaction(status="error")
        else:
            self.collector.record_interaction(status="success") 