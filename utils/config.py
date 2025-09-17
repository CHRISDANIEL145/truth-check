# utils/config.py
import os

class Config:
    """Configuration settings for TruthCheck"""
    
    # Model settings
    SIMILARITY_THRESHOLD = 0.5
    CONFIDENCE_THRESHOLD = 0.7 # This threshold is currently not explicitly used in app.py logic but can be for stricter classification
    
    # API settings
    WIKIPEDIA_TIMEOUT = 10
    # NEWS_TIMEOUT is less relevant now as we use google_search tool directly
    MAX_EVIDENCE_SOURCES = 5 # Max number of evidence sources to retrieve (e.g., 2 wiki, 3 web search)
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'truthcheck-secret-key-2024')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Model paths (for local models if needed)
    SPACY_MODEL = "en_core_web_sm"
    SBERT_MODEL = "all-MiniLM-L6-v2"
    NLI_MODEL = "roberta-large-mnli" # Or "distilbert-base-uncased-mnli" as a fallback

