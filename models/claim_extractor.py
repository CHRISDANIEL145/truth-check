# models/claim_extractor.py
import re
import spacy

class ClaimExtractor:
    def __init__(self): # Corrected __init__
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            raise
    
    def extract_claims(self, text):
        """Extract factual claims from text"""
        if not text or len(text.strip()) < 10:
            return []
        
        # Use spaCy for sentence segmentation
        doc = self.nlp(text)
        claims = []
        
        for sent in doc.sents:
            sentence = sent.text.strip()
            
            # Filter out questions, commands, and short sentences
            if (len(sentence.split()) > 5 and 
                not sentence.endswith('?') and 
                not sentence.startswith(('How', 'What', 'When', 'Where', 'Why', 'Who')) and
                not re.match(r'^(Please|Let|Can you)', sentence, re.IGNORECASE)):
                
                claims.append(sentence)
        
        return claims if claims else [text.strip()]

