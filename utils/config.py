# utils/config.py
import os

class Config:
    """Enhanced configuration for TruthCheck"""
    
    # Model settings
    SIMILARITY_THRESHOLD = 0.45  # Lowered slightly for better recall
    CONFIDENCE_THRESHOLD = 0.6   # Consensus threshold
    CONSENSUS_THRESHOLD = 0.6    # For multi-evidence voting
    
    # Evidence settings
    MAX_EVIDENCE_SOURCES = 10
    TOP_EVIDENCE_FOR_NLI = 4  # Use top 4 for consensus
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'truthcheck-production-key-2025')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Model paths
    SPACY_MODEL = "en_core_web_sm"
    SBERT_MODEL = "all-MiniLM-L6-v2"
