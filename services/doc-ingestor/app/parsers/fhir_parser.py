"""
FHIR Parser - Parse FHIR R4/R5 resources
"""

from fhir.resources.documentreference import DocumentReference
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from typing import Dict, Any, Tuple
import json
import structlog

logger = structlog.get_logger()


class FHIRParser:
    """FHIR R4/R5 resource parser"""
    
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse FHIR JSON file and extract text and metadata
        
        Args:
            file_path: Path to FHIR JSON file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                fhir_data = json.load(f)
            
            resource_type = fhir_data.get('resourceType', 'Unknown')
            
            # Route to appropriate parser based on resource type
            if resource_type == 'DocumentReference':
                return self._parse_document_reference(fhir_data)
            elif resource_type == 'Patient':
                return self._parse_patient(fhir_data)
            elif resource_type == 'Observation':
                return self._parse_observation(fhir_data)
            elif resource_type == 'Bundle':
                return self._parse_bundle(fhir_data)
            else:
                # Generic parsing
                return self._parse_generic(fhir_data)
            
        except Exception as e:
            logger.error("Error parsing FHIR", file=file_path, error=str(e))
            raise
    
    def _parse_document_reference(self, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """Parse DocumentReference resource"""
        doc_ref = DocumentReference(**data)
        
        text_parts = []
        metadata = {
            "resource_type": "DocumentReference",
            "id": doc_ref.id,
            "status": doc_ref.status,
        }
        
        # Extract patient reference
        if doc_ref.subject:
            metadata["patient_id"] = doc_ref.subject.reference
            text_parts.append(f"Patient: {doc_ref.subject.reference}")
        
        # Extract document type
        if doc_ref.type:
            doc_type = doc_ref.type.coding[0].display if doc_ref.type.coding else "Unknown"
            metadata["document_type"] = doc_type
            text_parts.append(f"Document Type: {doc_type}")
        
        # Extract content
        if doc_ref.content:
            for content in doc_ref.content:
                if content.attachment:
                    if content.attachment.data:
                        # Base64 encoded data
                        import base64
                        decoded = base64.b64decode(content.attachment.data).decode('utf-8', errors='ignore')
                        text_parts.append(decoded)
                    elif content.attachment.url:
                        text_parts.append(f"URL: {content.attachment.url}")
        
        # Extract description
        if doc_ref.description:
            text_parts.append(f"Description: {doc_ref.description}")
        
        text = "\n".join(text_parts)
        return text, metadata
    
    def _parse_patient(self, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """Parse Patient resource"""
        patient = Patient(**data)
        
        text_parts = []
        metadata = {
            "resource_type": "Patient",
            "id": patient.id,
        }
        
        # Extract name
        if patient.name:
            name = patient.name[0]
            full_name = f"{' '.join(name.given or [])} {name.family or ''}".strip()
            metadata["patient_name"] = full_name
            text_parts.append(f"Name: {full_name}")
        
        # Extract identifiers
        if patient.identifier:
            for identifier in patient.identifier:
                text_parts.append(f"ID ({identifier.system}): {identifier.value}")
        
        # Extract birth date
        if patient.birthDate:
            metadata["birth_date"] = str(patient.birthDate)
            text_parts.append(f"Birth Date: {patient.birthDate}")
        
        # Extract gender
        if patient.gender:
            metadata["gender"] = patient.gender
            text_parts.append(f"Gender: {patient.gender}")
        
        text = "\n".join(text_parts)
        return text, metadata
    
    def _parse_observation(self, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """Parse Observation resource"""
        observation = Observation(**data)
        
        text_parts = []
        metadata = {
            "resource_type": "Observation",
            "id": observation.id,
            "status": observation.status,
        }
        
        # Extract observation code
        if observation.code:
            code_display = observation.code.coding[0].display if observation.code.coding else "Unknown"
            text_parts.append(f"Observation: {code_display}")
        
        # Extract value
        if observation.valueQuantity:
            value = f"{observation.valueQuantity.value} {observation.valueQuantity.unit}"
            text_parts.append(f"Value: {value}")
        elif observation.valueString:
            text_parts.append(f"Value: {observation.valueString}")
        
        # Extract effective date
        if observation.effectiveDateTime:
            metadata["observation_date"] = str(observation.effectiveDateTime)
            text_parts.append(f"Date: {observation.effectiveDateTime}")
        
        text = "\n".join(text_parts)
        return text, metadata
    
    def _parse_bundle(self, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """Parse Bundle resource (multiple resources)"""
        text_parts = []
        metadata = {
            "resource_type": "Bundle",
            "type": data.get('type', 'Unknown'),
            "total": data.get('total', 0),
        }
        
        entries = data.get('entry', [])
        for entry in entries:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType', 'Unknown')
            
            try:
                if resource_type == 'DocumentReference':
                    text, _ = self._parse_document_reference(resource)
                    text_parts.append(f"\n=== {resource_type} ===\n{text}")
                elif resource_type == 'Patient':
                    text, _ = self._parse_patient(resource)
                    text_parts.append(f"\n=== {resource_type} ===\n{text}")
                elif resource_type == 'Observation':
                    text, _ = self._parse_observation(resource)
                    text_parts.append(f"\n=== {resource_type} ===\n{text}")
            except Exception as e:
                logger.warning(f"Failed to parse {resource_type}", error=str(e))
        
        text = "\n".join(text_parts)
        return text, metadata
    
    def _parse_generic(self, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """Generic FHIR resource parser"""
        metadata = {
            "resource_type": data.get('resourceType', 'Unknown'),
            "id": data.get('id'),
        }
        
        # Extract text narrative if available
        text = ""
        if 'text' in data and 'div' in data['text']:
            # Remove HTML tags
            import re
            text = re.sub('<[^<]+?>', '', data['text']['div'])
        
        # If no narrative, use JSON pretty print
        if not text:
            text = json.dumps(data, indent=2)
        
        return text, metadata
