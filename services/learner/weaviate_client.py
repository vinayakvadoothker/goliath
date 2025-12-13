"""
Weaviate client for human capability embeddings.
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
            logger.info("Weaviate client initialized for Learner service")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            return None
    
    return _weaviate_client


def _ensure_schema():
    """Ensure Weaviate schema exists for Human."""
    client = get_weaviate_client()
    if not client:
        return
    
    try:
        # Check if collection exists
        if client.collections.exists("Human"):
            return
        
        # Create collection
        client.collections.create(
            name="Human",
            vectorizer_config=Configure.Vectorizer.none(),  # We provide vectors
            properties=[
                Property(name="id", data_type=DataType.TEXT),
                Property(name="display_name", data_type=DataType.TEXT),
                Property(name="service", data_type=DataType.TEXT),
                Property(name="capability_summary", data_type=DataType.TEXT),
            ]
        )
        logger.info("Weaviate Human schema created")
    except Exception as e:
        logger.error(f"Failed to create Weaviate Human schema: {e}")


def update_human_embedding(
    human_id: str,
    display_name: str,
    service: str,
    embedding: List[float],
    capability_summary: str = ""
) -> bool:
    """
    Update human embedding in Weaviate.
    
    Args:
        human_id: Human ID
        display_name: Human display name
        service: Service name
        embedding: 768-dimensional embedding vector (aggregated from work items)
        capability_summary: Text summary of capabilities
    
    Returns:
        True if successful, False otherwise
    """
    client = get_weaviate_client()
    if not client:
        return False
    
    try:
        collection = client.collections.get("Human")
        
        # Use human_id + service as unique identifier
        object_id = f"{human_id}_{service}"
        
        # Check if object exists
        try:
            existing = collection.data.fetch_by_id(object_id)
            if existing:
                # Update existing
                collection.data.update(
                    uuid=object_id,
                    properties={
                        "id": human_id,
                        "display_name": display_name,
                        "service": service,
                        "capability_summary": capability_summary
                    },
                    vector=embedding
                )
            else:
                # Insert new
                collection.data.insert(
                    uuid=object_id,
                    properties={
                        "id": human_id,
                        "display_name": display_name,
                        "service": service,
                        "capability_summary": capability_summary
                    },
                    vector=embedding
                )
        except Exception:
            # Object doesn't exist, insert new
            try:
                collection.data.insert(
                    uuid=object_id,
                    properties={
                        "id": human_id,
                        "display_name": display_name,
                        "service": service,
                        "capability_summary": capability_summary
                    },
                    vector=embedding
                )
            except Exception as insert_error:
                logger.warning(f"Failed to insert human embedding: {insert_error}")
                return False
        
        logger.info(f"Updated human embedding for {human_id} in service {service}")
        return True
    except Exception as e:
        logger.error(f"Failed to update human embedding in Weaviate: {e}")
        return False


def get_human_embedding(human_id: str, service: str) -> Optional[List[float]]:
    """
    Get human embedding from Weaviate.
    
    Args:
        human_id: Human ID
        service: Service name
    
    Returns:
        Embedding vector or None if not found
    """
    client = get_weaviate_client()
    if not client:
        return None
    
    try:
        collection = client.collections.get("Human")
        object_id = f"{human_id}_{service}"
        
        result = collection.data.fetch_by_id(object_id, include_vector=True)
        if result and hasattr(result, 'vector'):
            return result.vector
        return None
    except Exception as e:
        logger.warning(f"Failed to get human embedding: {e}")
        return None
