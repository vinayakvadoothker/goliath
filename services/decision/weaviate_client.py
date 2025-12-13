"""
Weaviate client for vector similarity search.
"""
import os
import logging
from typing import Optional, List, Dict, Any
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery

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
                Property(name="resolver_id", data_type=DataType.TEXT),
                Property(name="resolved_at", data_type=DataType.TEXT),  # Using TEXT for simplicity
            ]
        )
        logger.info("Weaviate WorkItem schema created")
    except Exception as e:
        logger.error(f"Failed to create Weaviate schema: {e}")


def search_similar_work_items(
    embedding: List[float],
    service: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for similar work items using vector similarity.
    
    Args:
        embedding: 1536-dimensional embedding vector
        service: Optional service filter
        limit: Maximum number of results
    
    Returns:
        List of similar work items with similarity scores
    """
    client = get_weaviate_client()
    if not client:
        return []
    
    try:
        collection = client.collections.get("WorkItem")
        
        # Build query
        from weaviate.classes.query import Filter
        
        query_builder = collection.query.near_vector(
            near_vector=embedding,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )
        
        # Add service filter if provided
        if service:
            query_builder = query_builder.where(
                Filter.by_property("service").equal(service)
            )
        
        results = query_builder.do()
        
        similar_items = []
        for item in results.objects:
            props = item.properties
            metadata = item.metadata if hasattr(item, 'metadata') else None
            distance = metadata.distance if metadata and hasattr(metadata, 'distance') else 1.0
            
            similar_items.append({
                "id": props.get("id", ""),
                "description": props.get("description", ""),
                "service": props.get("service", ""),
                "severity": props.get("severity", ""),
                "resolver_id": props.get("resolver_id", ""),
                "resolved_at": props.get("resolved_at", ""),
                "similarity": max(0.0, min(1.0, 1.0 - distance))  # Convert distance to similarity (0-1)
            })
        
        return similar_items
    except Exception as e:
        logger.error(f"Vector similarity search failed: {e}")
        return []


def store_work_item(
    work_item_id: str,
    description: str,
    service: str,
    severity: str,
    embedding: List[float],
    resolver_id: Optional[str] = None,
    resolved_at: Optional[str] = None
) -> bool:
    """
    Store work item in Weaviate for future similarity searches.
    
    Args:
        work_item_id: Work item ID
        description: Work item description
        service: Service name
        severity: Severity level
        embedding: 1536-dimensional embedding vector
        resolver_id: Optional resolver human ID
        resolved_at: Optional resolution timestamp
    
    Returns:
        True if successful, False otherwise
    """
    client = get_weaviate_client()
    if not client:
        return False
    
    try:
        collection = client.collections.get("WorkItem")
        
        collection.data.insert(
            properties={
                "id": work_item_id,
                "description": description,
                "service": service,
                "severity": severity,
                "resolver_id": resolver_id or "",
                "resolved_at": resolved_at or ""
            },
            vector=embedding
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to store work item in Weaviate: {e}")
        return False

