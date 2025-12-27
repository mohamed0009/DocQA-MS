
from app.analyzers import get_analyzer
from app.config import settings
import structlog

logger = structlog.get_logger()

def test_medical():
    print("Initializing Analyzer...")
    analyzer = get_analyzer()
    
    text = "Patient has diabetes and is taking metformin."
    print(f"Text: {text}")
    
    print("Preserve entities:", settings.PRESERVE_ENTITIES)
    
    print("Calling detect_medical_entities...")
    entities = analyzer.detect_medical_entities(text)
    print(f"Medical Entities: {entities}")

if __name__ == "__main__":
    test_medical()
