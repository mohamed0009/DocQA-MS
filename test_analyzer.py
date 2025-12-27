
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
import spacy
import os

def test_analyzer():
    print("Loading spacy model en_core_web_sm...")
    nlp = spacy.load("en_core_web_sm")
    print("Model loaded.")
    
    print("Configuring NLP engine...")
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    
    print("Initializing AnalyzerEngine...")
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry, supported_languages=["en"])
    
    text = "My name is John Smith and I have diabetes."
    print(f"Analyzing text: {text}")
    
    results = analyzer.analyze(text=text, language="en", entities=["PERSON", "v"], score_threshold=0.5)
    print(f"Results: {results}")

if __name__ == "__main__":
    try:
        test_analyzer()
    except Exception as e:
        print(f"Error: {e}")
