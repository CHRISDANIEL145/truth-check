# app.py - Main Flask application

from flask import Flask, render_template, request, jsonify
import os
import threading 
import time 

# Import all necessary components from your models and utils directories
from models.claim_extractor import ClaimExtractor
from models.keyword_extractor import KeywordExtractor
from models.evidence_retriever import EvidenceRetriever
from models.nli_classifier import NLIClassifier
from utils.similarity import calculate_similarity 
from utils.config import Config 

# Initialize models globally or within a singleton pattern for efficiency
claim_extractor = ClaimExtractor()
keyword_extractor = KeywordExtractor()
evidence_retriever = EvidenceRetriever()
nli_classifier = NLIClassifier()

class TruthCheckSystem:
    def __init__(self): 
        self.claim_extractor = claim_extractor
        self.keyword_extractor = keyword_extractor
        self.evidence_retriever = evidence_retriever
        self.nli_classifier = nli_classifier
    
    def verify_claim(self, text):
        """
        Main function to verify a factual claim.
        Processes the claim through extraction, evidence retrieval, and NLI.
        """
        try:
            # Step 1: Extract claims from the input text
            claims = self.claim_extractor.extract_claims(text)
            if not claims:
                return "No valid claims found", 0.0, "Please provide a clear factual statement."
            
            claim = claims[0]
            
            # Step 2: Extract keywords from the claim
            keywords = self.keyword_extractor.extract_keywords(claim)
            
            # Step 3: Retrieve evidence from external sources (Wikipedia, Google News, Academic, Gov, Fact-Check)
            evidence_items = self.evidence_retriever.get_evidence(keywords)
            
            if not evidence_items:
                return "Low Confidence", 0.3, "Not enough reliable evidence found from external sources."
            
            # Step 4: Check semantic similarity between the claim and retrieved evidence
            relevant_evidence = []
            for item in evidence_items:
                similarity = calculate_similarity(claim, item['content'])
                if similarity > Config.SIMILARITY_THRESHOLD: 
                    relevant_evidence.append(item)
            
            if not relevant_evidence:
                return "Low Confidence", 0.4, "No semantically relevant evidence found after similarity check."
            
            # --- NEW: Sort relevant evidence by credibility score before NLI ---
            # We want to prioritize the most credible relevant evidence for classification
            relevant_evidence.sort(key=lambda x: x.get('credibility_score', 0.0), reverse=True)
            primary_evidence = relevant_evidence[0] # The most credible relevant piece of evidence
            # --- END NEW ---

            # Step 5: Perform Natural Language Inference (NLI)
            nli_result = self.nli_classifier.classify(claim, primary_evidence['content'])
            
            # Step 6: Format the result based on NLI classification and adjust confidence by credibility
            label = "Low Confidence" 
            nli_confidence = nli_result['confidence'] 
            
            # --- NEW: Factor in source credibility to the final confidence score ---
            # Weight the NLI confidence (e.g., 70%) and the source credibility (e.g., 30%)
            source_credibility_weight = primary_evidence.get('credibility_score', 0.5) # Default to 0.5 if somehow missing
            final_confidence = (nli_confidence * 0.7) + (source_credibility_weight * 0.3)
            final_confidence = min(max(final_confidence, 0.0), 1.0) # Ensure it stays within 0-1
            # --- END NEW ---

            if nli_result['label'] == 'ENTAILMENT':
                label = "True"
            elif nli_result['label'] == 'CONTRADICTION':
                label = "False"
            else:
                label = "Low Confidence"
                # If NLI is neutral, the credibility helps fine-tune, but still indicates low confidence
                final_confidence = max(final_confidence, 0.3) # Ensure neutral isn't too high from credibility alone


            evidence_snippet = primary_evidence['content']
            if len(evidence_snippet) > 500:
                evidence_snippet = evidence_snippet[:500] + "..."
            
            source = f"Source: {primary_evidence['source']} (Credibility: {source_credibility_weight:.2f})" # NEW: Show credibility
            
            return label, final_confidence, f"{evidence_snippet}\n\n{source}"
            
        except Exception as e:
            print(f"An error occurred during claim verification: {e}")
            return "Error", 0.0, f"An internal error occurred: {str(e)}. Please try again."

# Initialize TruthCheck system globally once when the app starts
truthcheck_system_instance = TruthCheckSystem()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    app.config['DEBUG'] = Config.DEBUG 

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/verify', methods=['POST'])
    def verify_claim_api():
        try:
            data = request.get_json()
            claim_text = data.get('claim', '')
            
            if not claim_text:
                return jsonify({'error': 'No claim provided'}), 400
            
            label, confidence, evidence = truthcheck_system_instance.verify_claim(claim_text)
            
            result = {
                'label': label,
                'confidence': round(confidence, 3), 
                'evidence': evidence,
                'claim': claim_text
            }
            
            return jsonify(result) 
            
        except Exception as e:
            print(f"API error: {e}")
            return jsonify({'error': f'An error occurred on the server: {str(e)}'}), 500
    
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'TruthCheck backend is running.'})
    
    return app
