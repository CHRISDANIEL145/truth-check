# models/keyword_extractor.py
import spacy
from collections import Counter

class KeywordExtractor:
    def __init__(self): # Corrected __init__
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            raise
    
    def extract_keywords(self, text):
        """Extract keywords and named entities from text"""
        doc = self.nlp(text)
        
        keywords = []
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'DATE']:
                keywords.append(ent.text)
        
        # Extract noun phrases and important words
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Avoid very long phrases
                keywords.append(chunk.text)
        
        # Extract individual important words
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.text)
        
        # Remove duplicates and return most common
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]

