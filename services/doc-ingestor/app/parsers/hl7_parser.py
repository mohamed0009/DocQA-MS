"""
HL7 Parser - Parse HL7 v2.x messages
"""

import hl7
from typing import Dict, Any, Tuple
import structlog

logger = structlog.get_logger()


class HL7Parser:
    """HL7 v2.x message parser"""
    
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse HL7 file and extract text and metadata
        
        Args:
            file_path: Path to HL7 file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                hl7_content = f.read()
            
            # Parse HL7 message
            message = hl7.parse(hl7_content)
            
            # Extract patient information (PID segment)
            pid_segment = message.segment('PID')
            
            metadata = {}
            text_parts = []
            
            if pid_segment:
                metadata.update({
                    "patient_id": str(pid_segment[3]) if len(pid_segment) > 3 else None,
                    "patient_name": str(pid_segment[5]) if len(pid_segment) > 5 else None,
                    "date_of_birth": str(pid_segment[7]) if len(pid_segment) > 7 else None,
                    "sex": str(pid_segment[8]) if len(pid_segment) > 8 else None,
                })
                text_parts.append(f"Patient: {metadata.get('patient_name', 'Unknown')}")
            
            # Extract observation/result segments (OBX)
            obx_segments = message.segments('OBX')
            if obx_segments:
                text_parts.append("\n=== Observations/Results ===")
                for obx in obx_segments:
                    if len(obx) > 5:
                        observation = f"{obx[3]}: {obx[5]}"
                        text_parts.append(observation)
            
            # Extract notes (NTE segments)
            nte_segments = message.segments('NTE')
            if nte_segments:
                text_parts.append("\n=== Notes ===")
                for nte in nte_segments:
                    if len(nte) > 3:
                        text_parts.append(str(nte[3]))
            
            # Message header info
            msh_segment = message.segment('MSH')
            if msh_segment:
                metadata.update({
                    "message_type": str(msh_segment[9]) if len(msh_segment) > 9 else None,
                    "message_datetime": str(msh_segment[7]) if len(msh_segment) > 7 else None,
                    "sending_facility": str(msh_segment[4]) if len(msh_segment) > 4 else None,
                })
            
            text = "\n".join(text_parts)
            
            return text, metadata
            
        except Exception as e:
            logger.error("Error parsing HL7", file=file_path, error=str(e))
            raise
