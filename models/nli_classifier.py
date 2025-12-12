# models/nli_classifier.py
from transformers import pipeline
import torch
from collections import Counter


class NLIClassifier:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        try:
            print("Loading NLI models (this may take a moment)...")
            device = 0 if torch.cuda.is_available() else -1
            
            self.models = []
            
            # Model 1: RoBERTa-large-MNLI (most accurate)
            try:
                self.models.append({
                    'name': 'roberta-large-mnli',
                    'pipeline': pipeline(
                        "text-classification",
                        model="roberta-large-mnli",
                        device=device
                    ),
                    'weight': 0.5
                })
                print("✓ Loaded RoBERTa-large-MNLI")
            except Exception as e:
                print(f"⚠ Failed to load RoBERTa-large-MNLI: {e}")
            
            # Model 2: DeBERTa-v3-large MNLI fine-tuned (use pre-trained version)
            try:
                self.models.append({
                    'name': 'deberta-v3-large-mnli',
                    'pipeline': pipeline(
                        "text-classification",
                        model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
                        device=device
                    ),
                    'weight': 0.5
                })
                print("✓ Loaded DeBERTa-v3-large-MNLI")
            except Exception as e:
                print(f"⚠ Failed to load DeBERTa-v3-large-MNLI: {e}")
            
            if not self.models:
                # Fallback to BART if both fail
                try:
                    self.models.append({
                        'name': 'bart-large-mnli',
                        'pipeline': pipeline(
                            "zero-shot-classification",
                            model="facebook/bart-large-mnli",
                            device=device
                        ),
                        'weight': 1.0
                    })
                    print("✓ Loaded BART-large-MNLI (fallback)")
                except Exception as e:
                    print(f"✗ Failed to load any NLI model: {e}")
                    raise Exception("No NLI models loaded successfully")
            
            # Normalize weights
            total_weight = sum(m['weight'] for m in self.models)
            for model in self.models:
                model['weight'] /= total_weight
            
            self._initialized = True
            print(f"✓ Successfully loaded {len(self.models)} NLI model(s)")
            
        except Exception as e:
            print(f"Error loading NLI models: {e}")
            self.models = []
            self._initialized = False
    
    def classify(self, claim, evidence):
        """Classify relationship between claim and evidence using ensemble"""
        if not self.models:
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5,
                'model_votes': {}
            }
        
        try:
            results = []
            model_votes = {}
            
            for model_info in self.models:
                try:
                    pipeline_obj = model_info['pipeline']
                    model_name = model_info['name']
                    
                    # Handle different pipeline types
                    if 'bart' in model_name:
                        result = pipeline_obj(
                            evidence,
                            candidate_labels=["entailment", "contradiction", "neutral"],
                            hypothesis_template="This example is {}."
                        )
                        label = result['labels'][0]
                        confidence = result['scores'][0]
                    else:
                        # Standard NLI: premise [SEP] hypothesis
                        input_text = f"{evidence} [SEP] {claim}"
                        result = pipeline_obj(input_text)[0]
                        label = result['label']
                        confidence = result['score']
                    
                    # Map labels
                    label_mapping = {
                        'ENTAILMENT': 'ENTAILMENT',
                        'CONTRADICTION': 'CONTRADICTION',
                        'NEUTRAL': 'NEUTRAL',
                        'entailment': 'ENTAILMENT',
                        'contradiction': 'CONTRADICTION',
                        'neutral': 'NEUTRAL',
                        'LABEL_0': 'CONTRADICTION',
                        'LABEL_1': 'NEUTRAL',
                        'LABEL_2': 'ENTAILMENT'
                    }
                    
                    mapped_label = label_mapping.get(label, 'NEUTRAL')
                    
                    results.append({
                        'label': mapped_label,
                        'confidence': confidence,
                        'weight': model_info['weight']
                    })
                    
                    model_votes[model_name] = mapped_label
                    
                except Exception as e:
                    print(f"Error with model {model_info['name']}: {e}")
                    continue
            
            if not results:
                return {
                    'label': 'NEUTRAL',
                    'confidence': 0.5,
                    'model_votes': {}
                }
            
            # Weighted voting
            weighted_scores = {
                'ENTAILMENT': 0.0,
                'CONTRADICTION': 0.0,
                'NEUTRAL': 0.0
            }
            
            for result in results:
                weighted_scores[result['label']] += result['confidence'] * result['weight']
            
            # Get final label and confidence
            final_label = max(weighted_scores, key=weighted_scores.get)
            total_score = sum(weighted_scores.values())
            final_confidence = weighted_scores[final_label] / total_score if total_score > 0 else 0.5
            
            return {
                'label': final_label,
                'confidence': final_confidence,
                'model_votes': model_votes,
                'weighted_scores': weighted_scores
            }
            
        except Exception as e:
            print(f"NLI classification error: {e}")
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5,
                'model_votes': {}
            }
