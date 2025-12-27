
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
import structlog

logger = structlog.get_logger()

def test_anonymize():
    print("Initializing engine...")
    engine = AnonymizerEngine()
    
    text = "My name is John Smith."
    print(f"Text: {text}")
    
    analyzer_results = [
        RecognizerResult(entity_type="PERSON", start=11, end=21, score=0.85)
    ]
    print(f"Results: {analyzer_results}")
    
    print("Anonymizing...")
    result = engine.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators={"DEFAULT": OperatorConfig("redact")}
    )
    print(f"Result: {result.text}")

if __name__ == "__main__":
    test_anonymize()
