# app.py
import os
from flask import Flask, render_template, request, jsonify
from functools import lru_cache
import hashlib
import sqlite3
import datetime
import json

from models.claim_extractor import ClaimExtractor
from models.keyword_extractor import KeywordExtractor
from models.evidence_retriever import EvidenceRetriever
from models.nli_classifier import NLIClassifier
from utils.similarity import calculate_similarity
from utils.config import Config


# Initialize models globally
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
        self.cache = {}
        
    def _get_cache_key(self, text):
        """Generate cache key for claim"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def verify_claim(self, text):
        """
        Enhanced fact verification with multi-evidence aggregation
        and consensus mechanism (similar to FactCheck system)
        """
        try:
            # Check cache
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                print("Returning cached result")
                return self.cache[cache_key]
            
            # Step 1: Extract claims
            claims = self.claim_extractor.extract_claims(text)
            if not claims:
                result = ("Low Confidence", 0.3, "No valid claims found. Please provide a clear factual statement.")
                self.cache[cache_key] = result
                return result
            
            claim = claims[0]
            
            # Step 2: Extract keywords
            keywords = self.keyword_extractor.extract_keywords(claim)
            
            # Step 3: Retrieve evidence from multiple sources
            evidence_items = self.evidence_retriever.get_evidence(keywords)
            
            if not evidence_items:
                result = ("Low Confidence", 0.3, "Not enough reliable evidence found.")
                self.cache[cache_key] = result
                return result
            
            # Step 4: Filter by semantic similarity
            relevant_evidence = []
            for item in evidence_items:
                similarity = calculate_similarity(claim, item['content'])
                if similarity > Config.SIMILARITY_THRESHOLD:
                    item['similarity_score'] = similarity
                    relevant_evidence.append(item)
            
            if not relevant_evidence:
                result = ("Low Confidence", 0.4, "No semantically relevant evidence found.")
                self.cache[cache_key] = result
                return result
            
            # Step 5: Sort by combined score (credibility + similarity)
            for item in relevant_evidence:
                item['combined_score'] = (
                    item.get('credibility_score', 0.5) * 0.6 +
                    item.get('similarity_score', 0.5) * 0.4
                )
            
            relevant_evidence.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Step 6: Multi-Evidence NLI with Consensus Mechanism
            # Use top 4 evidence sources (as per FactCheck research)
            top_evidence = relevant_evidence[:4]
            
            nli_results = []
            for evidence_item in top_evidence:
                nli_result = self.nli_classifier.classify(claim, evidence_item['content'])
                nli_results.append({
                    'nli': nli_result,
                    'credibility': evidence_item.get('credibility_score', 0.5),
                    'similarity': evidence_item.get('similarity_score', 0.5),
                    'source': evidence_item.get('source', 'Unknown'),
                    'url': evidence_item.get('url', '')
                })
            
            # Step 7: Weighted Consensus Voting
            entailment_score = 0
            contradiction_score = 0
            neutral_score = 0
            
            total_weight = 0
            for result in nli_results:
                # Weight by credibility and confidence
                weight = result['credibility'] * result['nli']['confidence']
                total_weight += weight
                
                if result['nli']['label'] == 'ENTAILMENT':
                    entailment_score += weight
                elif result['nli']['label'] == 'CONTRADICTION':
                    contradiction_score += weight
                else:
                    neutral_score += weight
            
            # Normalize scores
            if total_weight > 0:
                entailment_score /= total_weight
                contradiction_score /= total_weight
                neutral_score /= total_weight
            
            # Step 8: Determine final label with consensus threshold
            consensus_threshold = 0.6  # Require 60% agreement
            
            max_score = max(entailment_score, contradiction_score, neutral_score)
            
            if max_score == entailment_score and entailment_score >= consensus_threshold:
                label = "True"
                final_confidence = entailment_score
            elif max_score == contradiction_score and contradiction_score >= consensus_threshold:
                label = "False"
                final_confidence = contradiction_score
            else:
                label = "Low Confidence"
                final_confidence = max(entailment_score, contradiction_score, neutral_score)
            
            # Step 9: Prepare evidence summary
            evidence_summary = self._format_evidence_summary(nli_results, top_evidence)
            
            result = (label, final_confidence, evidence_summary)
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"Error during claim verification: {e}")
            import traceback
            traceback.print_exc()
            return ("Error", 0.0, f"An internal error occurred: {str(e)}")
    
    def _format_evidence_summary(self, nli_results, evidence_items):
        """Format evidence summary with sources and verdicts"""
        summary_parts = []
        
        summary_parts.append(f"**Analyzed {len(nli_results)} sources:**\n")
        
        for i, (nli_res, evidence) in enumerate(zip(nli_results, evidence_items), 1):
            source = nli_res['source']
            verdict = nli_res['nli']['label']
            confidence = nli_res['nli']['confidence']
            credibility = nli_res['credibility']
            url = nli_res['url']
            
            # Get snippet
            content = evidence.get('content', '')[:300]
            
            summary_parts.append(
                f"\n**Source {i}: {source}**\n"
                f"Verdict: {verdict} (Confidence: {confidence:.2%})\n"
                f"Credibility Score: {credibility:.2f}\n"
                f"Excerpt: {content}...\n"
                f"URL: {url}\n"
            )
        
        return "\n".join(summary_parts)


# Initialize system
truthcheck_system_instance = TruthCheckSystem()

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    app.config['DEBUG'] = Config.DEBUG
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/how-it-works')
    def how_it_works():
        return render_template('how_it_works.html')

    @app.route('/api-docs')
    def api_docs():
        return render_template('api.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/api/history')
    def get_history():
        try:
            conn = sqlite3.connect('history.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM verifications ORDER BY date DESC LIMIT 50')
            rows = c.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'id': row['id'],
                    'claim': row['claim'],
                    'label': row['label'],
                    'confidence': row['confidence'],
                    'date': row['date']
                })
            return jsonify(history)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/verify', methods=['POST'])
    def verify_claim_api():
        try:
            data = request.get_json()
            claim_text = data.get('claim', '')
            
            if not claim_text:
                return jsonify({'error': 'No claim provided'}), 400
            
            label, confidence, evidence = truthcheck_system_instance.verify_claim(claim_text)
            
            # Save to DB
            try:
                conn = sqlite3.connect('history.db')
                c = conn.cursor()
                c.execute('INSERT INTO verifications (claim, label, confidence) VALUES (?, ?, ?)',
                          (claim_text, label, float(confidence)))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"DB Error: {e}")
            
            result = {
                'label': label,
                'confidence': round(confidence, 3),
                'evidence': evidence,
                'claim': claim_text
            }
            
            return jsonify(result)
            
        except Exception as e:
            print(f"API error: {e}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'TruthCheck is running.'})
    
    return app
