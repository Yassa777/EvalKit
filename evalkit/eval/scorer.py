from typing import Dict, Any, List, Optional
import openai
from evalkit.core.config import settings

class Scorer:
    """Base class for evaluation scorers."""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        if model.startswith("gpt"):
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not set")
            openai.api_key = settings.OPENAI_API_KEY
    
    async def score(
        self,
        query: str,
        response: str,
        expected_response: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score a query-response pair."""
        raise NotImplementedError

class GPTScorer(Scorer):
    """Scorer using GPT models for evaluation."""
    
    async def score(
        self,
        query: str,
        response: str,
        expected_response: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score a query-response pair using GPT."""
        
        # Construct the prompt
        prompt = f"""Evaluate the following query-response pair:

Query: {query}

Response: {response}
"""

        if expected_response:
            prompt += f"\nExpected Response: {expected_response}"

        if context:
            prompt += f"\nContext: {context}"

        prompt += """

Please evaluate the response on the following criteria:
1. Relevance (0-1): How well does the response address the query?
2. Accuracy (0-1): Is the information in the response factually correct?
3. Completeness (0-1): Does the response cover all necessary aspects of the query?
4. Clarity (0-1): Is the response clear and well-structured?

Provide your evaluation in JSON format with the following structure:
{
    "scores": {
        "relevance": 0.0,
        "accuracy": 0.0,
        "completeness": 0.0,
        "clarity": 0.0
    },
    "overall_score": 0.0,
    "explanation": "Brief explanation of the scores"
}
"""

        # Get evaluation from GPT
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of LLM responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            # Parse the response
            evaluation = response.choices[0].message.content
            # TODO: Parse the JSON response and return structured data
            
            return {
                "scores": {
                    "relevance": 0.8,
                    "accuracy": 0.9,
                    "completeness": 0.7,
                    "clarity": 0.85
                },
                "overall_score": 0.81,
                "explanation": "Example evaluation"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "scores": {
                    "relevance": 0.0,
                    "accuracy": 0.0,
                    "completeness": 0.0,
                    "clarity": 0.0
                },
                "overall_score": 0.0,
                "explanation": f"Error during evaluation: {str(e)}"
            }

class ScorerFactory:
    """Factory for creating scorer instances."""
    
    _scorers = {}
    
    @classmethod
    def register(cls, scorer_type: str, scorer_class: type) -> None:
        """Register a scorer implementation."""
        cls._scorers[scorer_type] = scorer_class
    
    @classmethod
    def create(cls, scorer_type: str, **kwargs) -> Scorer:
        """Create a scorer instance."""
        if scorer_type not in cls._scorers:
            raise ValueError(f"Unknown scorer type: {scorer_type}")
        
        return cls._scorers[scorer_type](**kwargs)

# Register default scorers
ScorerFactory.register("gpt", GPTScorer) 