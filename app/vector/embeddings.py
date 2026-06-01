"""
Embedding generation service.
Supports both OpenAI API and fallback Mock Embeddings.
"""
from app.config import settings
from openai import OpenAI
import hashlib
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_EMBEDDING_MODEL or "text-embedding-3-small"
        self.dimension = settings.EMBEDDING_DIMENSION or 1536
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized for embeddings.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client for embeddings: {e}")
                self.client = None
        else:
            logger.warning("No OPENAI_API_KEY provided. Using deterministic Mock Embeddings fallback.")
            self.client = None

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates embedding vector for the given text.
        If OpenAI API key is missing, uses a deterministic mock embedding generator.
        """
        if self.client and self.api_key:
            try:
                response = self.client.embeddings.create(
                    input=[text],
                    model=self.model
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding generation failed: {e}. Falling back to mock embeddings.")
                return self._generate_mock_embedding(text)
        else:
            return self._generate_mock_embedding(text)

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic vector based on MD5 hash of the input text.
        This guarantees that identical texts will always yield the exact same mock vector,
        which is ideal for basic offline RAG testing.
        """
        # Create hash
        hasher = hashlib.md5(text.encode('utf-8'))
        hash_digest = hasher.digest()
        
        # Use hash to seed np.random
        seed = int.from_bytes(hash_digest[:4], byteorder='big')
        rng = np.random.default_rng(seed)
        
        # Generate random normalized vector of correct size
        vector = rng.standard_normal(self.dimension)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

embedding_service = EmbeddingService()
