# utils/similarity.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityCalculator:
    def __init__(self): # Corrected __init__
        """Initialize sentence transformer model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading similarity model: {e}")
            self.model = None
    
    def calculate_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts"""
        if not self.model:
            print("Similarity model not loaded. Returning fallback similarity.")
            return 0.5  # Fallback similarity
        
        try:
            # Encode texts to embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                embeddings[0].reshape(1, -1),
                embeddings[1].reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.5

# Global similarity calculator instance
_similarity_calculator = SimilarityCalculator()

def calculate_similarity(text1, text2):
    """Global function to calculate similarity"""
    return _similarity_calculator.calculate_similarity(text1, text2)

