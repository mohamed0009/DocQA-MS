"""
Anonymizer service - applies de-identification strategies
"""

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
from typing import List, Dict, Any
import hashlib
import random
import structlog

from ..config import settings

logger = structlog.get_logger()


class Anonymizer:
    """Text anonymization with multiple strategies"""
    
    def __init__(self):
        self.engine = AnonymizerEngine()
        self.fake_data_generator = FakeDataGenerator()
    
    def anonymize(
        self,
        text: str,
        entities: List[Dict[str, Any]],
        strategy: str = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Anonymize text based on detected entities
        
        Args:
            text: Original text
            entities: List of PII entities to anonymize
            strategy: Anonymization strategy (redact, replace, hash, synthesize)
            
        Returns:
            Tuple of (anonymized_text, anonymization_metadata)
        """
        strategy = strategy or settings.DEID_STRATEGY
        
        try:
            if strategy == "redact":
                return self._redact(text, entities)
            elif strategy == "replace":
                return self._replace(text, entities)
            elif strategy == "hash":
                return self._hash(text, entities)
            elif strategy == "synthesize":
                return self._synthesize(text, entities)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
                
        except Exception as e:
            logger.error("Anonymization failed", error=str(e), strategy=strategy)
            raise
    
    def _redact(self, text: str, entities: List[Dict[str, Any]]) -> tuple[str, Dict[str, Any]]:
        """Replace entities with [REDACTED] or [REDACTED_TYPE]"""
        
        # Convert to Presidio format
        analyzer_results = self._convert_to_analyzer_results(entities)
        
        # Anonymize with redaction
        result = self.engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig("redact")}
        )
        
        metadata = {
            "strategy": "redact",
            "entities_redacted": len(entities),
            "entity_types": list(set([e["type"] for e in entities]))
        }
        
        return result.text, metadata
    
    def _replace(self, text: str, entities: List[Dict[str, Any]]) -> tuple[str, Dict[str, Any]]:
        """Replace entities with generic placeholders"""
        
        # Sort entities by start position (reverse order for replacement)
        sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)
        
        anonymized_text = text
        replacements = {}
        
        for entity in sorted_entities:
            entity_type = entity["type"]
            original_text = entity["text"]
            start = entity["start"]
            end = entity["end"]
            
            # Generate replacement based on type
            replacement = self._get_replacement_placeholder(entity_type)
            
            # Replace in text
            anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
            
            replacements[original_text] = replacement
        
        metadata = {
            "strategy": "replace",
            "entities_replaced": len(entities),
            "replacements": replacements
        }
        
        return anonymized_text, metadata
    
    def _hash(self, text: str, entities: List[Dict[str, Any]]) -> tuple[str, Dict[str, Any]]:
        """Replace entities with cryptographic hashes"""
        
        sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)
        
        anonymized_text = text
        hashes = {}
        
        for entity in sorted_entities:
            original_text = entity["text"]
            start = entity["start"]
            end = entity["end"]
            
            # Create hash
            hash_value = hashlib.sha256(original_text.encode()).hexdigest()[:16]
            replacement = f"[HASH_{hash_value}]"
            
            # Replace in text
            anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
            
            hashes[hash_value] = original_text
        
        metadata = {
            "strategy": "hash",
            "entities_hashed": len(entities),
            "hashes": hashes
        }
        
        return anonymized_text, metadata
    
    def _synthesize(self, text: str, entities: List[Dict[str, Any]]) -> tuple[str, Dict[str, Any]]:
        """Replace entities with realistic synthetic data"""
        
        sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)
        
        anonymized_text = text
        synthetic_mappings = {}
        
        for entity in sorted_entities:
            entity_type = entity["type"]
            original_text = entity["text"]
            start = entity["start"]
            end = entity["end"]
            
            # Generate synthetic data
            synthetic_value = self.fake_data_generator.generate(entity_type)
            
            # Replace in text
            anonymized_text = anonymized_text[:start] + synthetic_value + anonymized_text[end:]
            
            synthetic_mappings[original_text] = synthetic_value
        
        metadata = {
            "strategy": "synthesize",
            "entities_synthesized": len(entities),
            "synthetic_mappings": synthetic_mappings
        }
        
        return anonymized_text, metadata
    
    def _get_replacement_placeholder(self, entity_type: str) -> str:
        """Get placeholder text for entity type"""
        placeholders = {
            "PERSON": "[NAME]",
            "PATIENT_ID": "[PATIENT_ID]",
            "SSN": "[SSN]",
            "PHONE_NUMBER": "[PHONE]",
            "EMAIL_ADDRESS": "[EMAIL]",
            "LOCATION": "[LOCATION]",
            "DATE_TIME": "[DATE]",
            "AGE": "[AGE]",
            "ID": "[ID]",
            "MEDICAL_LICENSE": "[LICENSE]"
        }
        return placeholders.get(entity_type, "[REDACTED]")
    
    def _convert_to_analyzer_results(self, entities: List[Dict[str, Any]]) -> List[RecognizerResult]:
        """Convert entity dictionaries to Presidio RecognizerResult objects"""
        results = []
        for entity in entities:
            result = RecognizerResult(
                entity_type=entity["type"],
                start=entity["start"],
                end=entity["end"],
                score=entity.get("confidence", 1.0)
            )
            results.append(result)
        return results


class FakeDataGenerator:
    """Generate realistic fake data for synthesis"""
    
    def __init__(self):
        self.names = ["John Smith", "Jane Doe", "Robert Johnson", "Mary Williams"]
        self.locations = ["New York", "Boston", "Chicago", "Los Angeles"]
    
    def generate(self, entity_type: str) -> str:
        """Generate fake data for entity type"""
        
        generators = {
            "PERSON": self._generate_name,
            "PATIENT_ID": self._generate_patient_id,
            "SSN": self._generate_ssn,
            "PHONE_NUMBER": self._generate_phone,
            "EMAIL_ADDRESS": self._generate_email,
            "LOCATION": self._generate_location,
            "DATE_TIME": self._generate_date,
            "AGE": self._generate_age,
            "ID": self._generate_id,
        }
        
        generator = generators.get(entity_type, lambda: "[REDACTED]")
        return generator()
    
    def _generate_name(self) -> str:
        return random.choice(self.names)
    
    def _generate_patient_id(self) -> str:
        return f"PAT{random.randint(100000, 999999)}"
    
    def _generate_ssn(self) -> str:
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    
    def _generate_phone(self) -> str:
        return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def _generate_email(self) -> str:
        return f"user{random.randint(1000, 9999)}@example.com"
    
    def _generate_location(self) -> str:
        return random.choice(self.locations)
    
    def _generate_date(self) -> str:
        return f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    
    def _generate_age(self) -> str:
        return str(random.randint(18, 85))
    
    def _generate_id(self) -> str:
        return f"ID{random.randint(100000, 999999)}"


# Global anonymizer instance
_anonymizer = None


def get_anonymizer() -> Anonymizer:
    """Get anonymizer singleton"""
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = Anonymizer()
    return _anonymizer
