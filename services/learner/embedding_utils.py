"""
Embedding generation and PCA reduction utilities.
"""
import logging
import numpy as np
from typing import List, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import pickle
import os

logger = logging.getLogger(__name__)

# Global model instances
_embedding_model: Optional[SentenceTransformer] = None
_pca_model: Optional[PCA] = None
_pca_fitted: bool = False


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize sentence transformer model."""
    global _embedding_model
    
    if _embedding_model is None:
        try:
            # Use a lightweight model for embeddings (768 dimensions)
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using sentence-transformers.
    
    Args:
        text: Input text
    
    Returns:
        768-dimensional embedding vector
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * 384  # all-MiniLM-L6-v2 produces 384-dim vectors
    
    try:
        model = get_embedding_model()
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return zero vector on error
        return [0.0] * 384


def aggregate_embeddings(embeddings: List[List[float]], weights: Optional[List[float]] = None) -> List[float]:
    """
    Aggregate multiple embeddings using weighted average.
    
    Args:
        embeddings: List of embedding vectors
        weights: Optional weights for each embedding (more recent = higher weight)
    
    Returns:
        Aggregated embedding vector
    """
    if not embeddings:
        return [0.0] * 384
    
    if len(embeddings) == 1:
        return embeddings[0]
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Normalize weights
    if weights:
        weights_array = np.array(weights)
        weights_array = weights_array / weights_array.sum()  # Normalize
    else:
        weights_array = np.ones(len(embeddings)) / len(embeddings)
    
    # Weighted average
    aggregated = np.average(embeddings_array, axis=0, weights=weights_array)
    
    # Normalize the result
    norm = np.linalg.norm(aggregated)
    if norm > 0:
        aggregated = aggregated / norm
    
    return aggregated.tolist()


def get_pca_model() -> PCA:
    """Get or initialize PCA model for 3D reduction."""
    global _pca_model, _pca_fitted
    
    if _pca_model is None:
        _pca_model = PCA(n_components=3)
        _pca_fitted = False
    
    return _pca_model


def fit_pca_model(embeddings: List[List[float]]) -> None:
    """
    Fit PCA model on a set of embeddings.
    
    Args:
        embeddings: List of embedding vectors to fit on
    """
    global _pca_fitted
    
    if not embeddings:
        return
    
    try:
        model = get_pca_model()
        embeddings_array = np.array(embeddings)
        model.fit(embeddings_array)
        _pca_fitted = True
        logger.info("PCA model fitted on embeddings")
    except Exception as e:
        logger.error(f"Failed to fit PCA model: {e}")


def pca_reduce(embedding: List[float]) -> Tuple[float, float, float]:
    """
    Reduce embedding from 384D to 3D using PCA.
    
    Args:
        embedding: 384-dimensional embedding vector
    
    Returns:
        Tuple of (x, y, z) coordinates
    """
    if not embedding or len(embedding) == 0:
        return (0.0, 0.0, 0.0)
    
    try:
        model = get_pca_model()
        
        # If PCA not fitted, fit on this single embedding (not ideal but works)
        if not _pca_fitted:
            fit_pca_model([embedding])
        
        embedding_array = np.array([embedding])
        reduced = model.transform(embedding_array)[0]
        
        return (float(reduced[0]), float(reduced[1]), float(reduced[2]))
    except Exception as e:
        logger.error(f"Failed to reduce embedding with PCA: {e}")
        # Return zero coordinates on error
        return (0.0, 0.0, 0.0)


def generate_capability_summary(resolved_items: List[dict]) -> str:
    """
    Generate a text summary of human capabilities from resolved work items.
    
    Args:
        resolved_items: List of resolved work items with descriptions
    
    Returns:
        Text summary of capabilities
    """
    if not resolved_items:
        return "No resolved items yet"
    
    # Extract unique services and error types from descriptions
    services = set()
    descriptions = []
    
    for item in resolved_items[:10]:  # Limit to recent 10
        desc = item.get("description", "")
        if desc:
            descriptions.append(desc[:200])  # Truncate long descriptions
        service = item.get("service", "")
        if service:
            services.add(service)
    
    summary_parts = []
    if services:
        summary_parts.append(f"Works on: {', '.join(sorted(services))}")
    
    if descriptions:
        # Combine descriptions (truncated)
        combined = " ".join(descriptions)[:500]
        summary_parts.append(f"Recent work: {combined}...")
    
    return ". ".join(summary_parts) if summary_parts else "No summary available"
