# models/nli_classifier.py
from transformers import pipeline
import torch

class NLIClassifier:
    def __init__(self): # Corrected __init__
        """Initialize the Natural Language Inference classifier"""
        try:
            # Use RoBERTa-large-MNLI for NLI
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Alternative: Direct NLI pipeline
            self.nli_pipeline = pipeline(
                "text-classification",
                model="roberta-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
        except Exception as e:
            print(f"Error loading NLI model: {e}")
            # Fallback to a smaller model or a dummy pipeline if the main one fails
            # For a realistic app, consider a more robust fallback or error handling.
            # For now, let's use a simpler, more generally available model if roberta-large-mnli fails.
            # Note: DialoGPT is not an NLI model, it's a conversational model.
            # A better fallback would be to indicate failure or use a simpler NLI model if available.
            # For demonstration, we'll keep the direct NLI pipeline and let it fail if models aren't found.
            # If this becomes an issue, we might need to adjust the requirements or provide more specific fallback.
            print("Attempting to load a smaller NLI model if roberta-large-mnli fails...")
            try:
                self.nli_pipeline = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-mnli", # A smaller NLI model
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as fallback_e:
                print(f"Error loading fallback NLI model: {fallback_e}")
                # If even fallback fails, set pipeline to None and handle in classify method
                self.nli_pipeline = None


    def classify(self, claim, evidence):
        """Classify relationship between claim and evidence"""
        if not self.nli_pipeline:
            print("NLI pipeline not initialized. Returning neutral with low confidence.")
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5
            }

        try:
            # Format for NLI: premise (evidence) and hypothesis (claim)
            premise = evidence
            hypothesis = claim
            
            # Use the NLI pipeline
            # For NLI models, the input typically concatenates premise and hypothesis
            # with a special token, like " [SEP] ".
            # The pipeline itself often handles this, but explicitly formatting can help.
            result = self.nli_pipeline(f"{premise} [SEP] {hypothesis}")
            
            # Map labels to our format
            label_mapping = {
                'ENTAILMENT': 'ENTAILMENT',
                'CONTRADICTION': 'CONTRADICTION',
                'NEUTRAL': 'NEUTRAL',
                'entailment': 'ENTAILMENT',
                'contradiction': 'CONTRADICTION',
                'neutral': 'NEUTRAL'
            }
            
            if isinstance(result, list):
                result = result[0] # The pipeline returns a list, take the first result
            
            mapped_label = label_mapping.get(result['label'], 'NEUTRAL')
            confidence = result['score']
            
            return {
                'label': mapped_label,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"NLI classification error: {e}")
            # Return neutral with low confidence as fallback
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5
            }

