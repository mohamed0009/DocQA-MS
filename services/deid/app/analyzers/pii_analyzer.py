"""
PII Analyzer using Presidio and spaCy
"""

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from typing import List, Dict, Any
import spacy
import structlog

from ..config import settings

logger = structlog.get_logger()


class PIIAnalyzer:
    """PII detection using Presidio and spaCy"""
    
    def __init__(self):
        self.analyzer = None
        self.nlp = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Presidio analyzer and spaCy"""
        try:
            # Load spaCy model
            logger.info("Loading spaCy model", model=settings.SPACY_MODEL)
            self.nlp = spacy.load(settings.SPACY_MODEL)
            
            # Configure NLP engine provider
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {
                        "lang_code": "en",
                        "model_name": settings.SPACY_MODEL
                    }
                ]
            }
            
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            
            # Create analyzer
            registry = RecognizerRegistry()
            registry.load_predefined_recognizers()
            
            self.analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine,
                registry=registry,
                supported_languages=settings.PRESIDIO_SUPPORTED_LANGUAGES
            )
            
            logger.info("PII Analyzer initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize PII Analyzer", error=str(e))
            raise
    
    def analyze(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        """
        Analyze text for PII entities
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            List of detected entities with metadata
        """
        try:
            # Analyze with Presidio
            print(f"DEBUG: calling self.analyzer.analyze with text len {len(text)}")
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=settings.PII_ENTITIES,
                score_threshold=settings.DEID_CONFIDENCE_THRESHOLD
            )
            print(f"DEBUG: analyzer returned {len(results)} results")
            
            # Convert to dict format
            entities = []
            for result in results:
                entity = {
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "start": result.start,
                    "end": result.end,
                    "confidence": result.score,
                    "recognition_metadata": result.recognition_metadata
                }
                entities.append(entity)
            
            logger.info(
                "PII analysis completed",
                entities_found=len(entities),
                text_length=len(text)
            )
            
            return entities
            
        except Exception as e:
            logger.error("PII analysis failed", error=str(e))
            raise
    
    def analyze_batch(self, texts: List[str], language: str = "en") -> List[List[Dict[str, Any]]]:
        """
        Analyze multiple texts in batch
        
        Args:
            texts: List of texts to analyze
            language: Language code
            
        Returns:
            List of entity lists for each text
        """
        results = []
        for text in texts:
            entities = self.analyze(text, language)
            results.append(entities)
        return results
    
    def detect_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect medical entities to preserve (diseases, medications, etc.)
        
        Args:
            text: Text to analyze
            
        Returns:
            List of medical entities
        """
        try:
            print(f"DEBUG: calling self.nlp with text len {len(text)}")
            doc = self.nlp(text)
            print(f"DEBUG: nlp returned doc with {len(doc.ents)} ents")
            
            medical_entities = []
            for ent in doc.ents:
                # Check if entity should be preserved
                if ent.label_ in settings.PRESERVE_ENTITIES:
                    entity = {
                        "type": ent.label_,
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char
                    }
                    medical_entities.append(entity)
            
            logger.info(
                "Medical entity detection completed",
                entities_found=len(medical_entities)
            )
            
            return medical_entities
            
        except Exception as e:
            logger.error("Medical entity detection failed", error=str(e))
            raise


# Global analyzer instance
_analyzer = None


def get_analyzer() -> PIIAnalyzer:
    """Get PII analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = PIIAnalyzer()
    return _analyzer
