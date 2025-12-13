"""
LLM client for preprocessing logs and descriptions.
"""
import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Global OpenAI client
_openai_client: Optional[OpenAI] = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_llm_client() -> Optional[OpenAI]:
    """Get or initialize OpenAI client."""
    global _openai_client
    
    if _openai_client is None and OPENAI_API_KEY:
        try:
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    return _openai_client


async def llm_preprocess_log(raw_log: str, service_name: str) -> str:
    """
    Use LLM to clean and normalize log text before processing.
    Returns cleaned description ready for entity extraction.
    """
    client = get_llm_client()
    
    if not client:
        # Fallback: basic cleaning without LLM
        cleaned = raw_log.strip()
        # Remove common log prefixes
        for prefix in ["[ERROR]", "[CRITICAL]", "ERROR:", "CRITICAL:"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        return cleaned
    
    try:
        prompt = f"""Clean and normalize this error log. Return ONLY the cleaned description, no other text.

Raw log: {raw_log}
Service: {service_name}

Rules:
- Remove noise (timestamps, log levels, file paths if not relevant)
- Normalize terminology (consistent error type names)
- Fix typos if obvious
- Extract key information (error type, affected component, severity indicators)
- Keep it concise but informative
- Return clean, structured description ready for entity extraction

Cleaned description:"""
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic
            timeout=10.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM preprocessing failed: {e}. Using raw log.")
        return raw_log.strip()

