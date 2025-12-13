"""
Weaviate client for storing WorkItems as vectors.
"""
import os
import logging
from typing import Optional, List
import weaviate
from weaviate.classes.config import Configure, Property, DataType

logger = logging.getLogger(__name__)

# Global Weaviate client
_weaviate_client: Optional[weaviate.WeaviateClient] = None


def get_weaviate_client() -> Optional[weaviate.WeaviateClient]:
    """Get Weaviate client instance."""
    global _weaviate_client
    
    if _weaviate_client is None:
        weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        try:
            # Parse URL
            url_parts = weaviate_url.replace("http://", "").replace("https://", "").split(":")
            host = url_parts[0]
            port = int(url_parts[1]) if len(url_parts) > 1 else 8080
            
            _weaviate_client = weaviate.connect_to_local(
                host=host,
                port=port
            )
            _ensure_schema()
            logger.info("Weaviate client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            return None
    
    return _weaviate_client


def _ensure_schema():
    """Ensure Weaviate schema exists for WorkItems."""
    client = get_weaviate_client()
    if not client:
        return
    
    try:
        # Check if collection exists
        if client.collections.exists("WorkItem"):
            return
        
        # Create collection
        client.collections.create(
            name="WorkItem",
            vectorizer_config=Configure.Vectorizer.none(),  # We provide vectors
            properties=[
                Property(name="id", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="service", data_type=DataType.TEXT),
                Property(name="severity", data_type=DataType.TEXT),
            ]
        )
        logger.info("Weaviate WorkItem schema created")
    except Exception as e:
        logger.error(f"Failed to create Weaviate schema: {e}")


def store_work_item(
    work_item_id: str,
    description: str,
    service: str,
    severity: str,
    embedding: List[float]
) -> bool:
    """
    Store WorkItem in Weaviate with its embedding.
    
    Args:
        work_item_id: Work item ID
        description: Work item description
        service: Service name
        severity: Severity level
        embedding: 384-dimensional embedding vector
    
    Returns:
        True if successful, False otherwise
    """
    client = get_weaviate_client()
    if not client:
        logger.warning("Weaviate client not available, skipping vector storage")
        return False
    
    try:
        collection = client.collections.get("WorkItem")
        collection.data.insert(
            properties={
                "id": work_item_id,
                "description": description,
                "service": service,
                "severity": severity,
            },
            vector=embedding,
            uuid=work_item_id  # Use work_item_id as UUID
        )
        logger.debug(f"Stored WorkItem {work_item_id} in Weaviate")
        return True
    except Exception as e:
        logger.error(f"Failed to store WorkItem in Weaviate: {e}")
        return False

