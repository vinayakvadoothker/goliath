"""
LLM client wrapper with retries and error handling.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

# Global OpenAI client
_openai_client: Optional[OpenAI] = None


def get_llm_client() -> Optional[OpenAI]:
    """Get OpenAI client instance."""
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-your-") or api_key == "":
            logger.warning("OPENAI_API_KEY not set or invalid, LLM features will be disabled")
            return None
        
        _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client


async def extract_entities(text: str, model: str = None) -> Dict[str, Any]:
    """
    Extract entities from text using LLM.
    Returns structured entities for evidence generation.
    """
    client = get_llm_client()
    if not client:
        return {}
    
    model = model or os.getenv("OPENAI_MODEL", "gpt-4")
    
    prompt = f"""Extract key entities from this incident description. Return ONLY a JSON object with:
- error_type: string (e.g., "database_error", "api_timeout", "memory_leak")
- affected_component: string (e.g., "payment-service", "database", "cache")
- keywords: array of strings (important terms for similarity matching)

Description: {text}

JSON:"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic
                timeout=10.0
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            return json.loads(content)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 0.5
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"LLM entity extraction failed after {max_retries} attempts: {e}")
                return {}


def generate_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """
    Generate embedding for text using OpenAI embeddings API.
    Returns 1536-dimensional vector.
    """
    client = get_llm_client()
    if not client:
        return None
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 0.5
                logger.warning(f"Embedding generation failed (attempt {attempt + 1}/{max_retries}), retrying: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"Embedding generation failed after {max_retries} attempts: {e}")
                return None

