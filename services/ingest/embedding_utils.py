"""
Embedding generation and PCA reduction utilities for Ingest Service.
"""
import logging
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)

# Global model instances
_embedding_model: SentenceTransformer = None
_pca_model: PCA = None
_pca_fitted: bool = False


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize sentence transformer model."""
    global _embedding_model
    
    if _embedding_model is None:
        try:
            # Use lightweight model for embeddings (384 dimensions)
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
        384-dimensional embedding vector
    """
    if not text or not text.strip():
        return [0.0] * 384
    
    try:
        model = get_embedding_model()
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return [0.0] * 384


def get_pca_model() -> PCA:
    """Get or initialize PCA model for 3D reduction."""
    global _pca_model, _pca_fitted
    
    if _pca_model is None:
        _pca_model = PCA(n_components=3)
        _pca_fitted = False
    
    return _pca_model


def fit_pca_model(embeddings: List[List[float]]) -> None:
    """Fit PCA model on a set of embeddings."""
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
        
        # If PCA not fitted, fit on this single embedding
        if not _pca_fitted:
            fit_pca_model([embedding])
        
        embedding_array = np.array([embedding])
        reduced = model.transform(embedding_array)[0]
        
        return (float(reduced[0]), float(reduced[1]), float(reduced[2]))
    except Exception as e:
        logger.error(f"Failed to reduce embedding with PCA: {e}")
        return (0.0, 0.0, 0.0)

