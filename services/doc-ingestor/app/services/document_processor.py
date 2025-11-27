"""
Document processing service - handles parsing and content extraction
"""

import hashlib
from typing import Tuple, Dict, Any
from pathlib import Path
import structlog

from ..parsers import PDFParser, DOCXParser, HL7Parser, FHIRParser
from ..config import settings

logger = structlog.get_logger()


class DocumentProcessor:
    """Main document processing service"""
    
    def __init__(self):
        self.pdf_parser = PDFParser(enable_ocr=settings.ENABLE_OCR)
        self.docx_parser = DOCXParser()
        self.hl7_parser = HL7Parser()
        self.fhir_parser = FHIRParser()
    
    def process_document(self, file_path: str, file_type: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process document and extract text and metadata
        
        Args:
            file_path: Path to document file
            file_type: Type of document (pdf, docx, hl7, fhir, etc.)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        logger.info("Processing document", file_path=file_path, file_type=file_type)
        
        try:
            if file_type == 'pdf':
                return self.pdf_parser.parse(file_path)
            elif file_type == 'docx':
                return self.docx_parser.parse(file_path)
            elif file_type in ['hl7', 'hl7v2']:
                return self.hl7_parser.parse(file_path)
            elif file_type in ['fhir', 'json']:
                # Try FHIR parser for JSON files
                return self.fhir_parser.parse(file_path)
            elif file_type == 'txt':
                return self._parse_text_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error("Error processing document", file_path=file_path, error=str(e))
            raise
    
    def _parse_text_file(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        metadata = {
            "num_chars": len(text),
            "num_lines": text.count('\n'),
        }
        
        return text, metadata
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA256 hash of file content for deduplication
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """
        Determine file type from filename extension
        
        Args:
            filename: Name of file
            
        Returns:
            File type string
        """
        ext = Path(filename).suffix.lower().lstrip('.')
        
        # Map extensions to standardized types
        type_mapping = {
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'docx',
            'txt': 'txt',
            'hl7': 'hl7',
            'json': 'fhir',  # Assume JSON is FHIR
            'xml': 'fhir',
        }
        
        return type_mapping.get(ext, ext)
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Validate file size is within limits
        
        Args:
            file_size: Size in bytes
            
        Returns:
            True if valid, False otherwise
        """
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate file extension is allowed
        
        Args:
            filename: Name of file
            
        Returns:
            True if valid, False otherwise
        """
        ext = Path(filename).suffix.lower().lstrip('.')
        return ext in settings.ALLOWED_EXTENSIONS
