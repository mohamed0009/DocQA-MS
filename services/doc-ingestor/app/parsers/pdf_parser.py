"""
PDF Parser - Extract text and metadata from PDF files
"""

import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
from typing import Dict, Any, Tuple
import os
import structlog

logger = structlog.get_logger()


class PDFParser:
    """PDF document parser with OCR support"""
    
    def __init__(self, enable_ocr: bool = True):
        self.enable_ocr = enable_ocr
    
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse PDF file and extract text and metadata
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            # Try extracting text with PyPDF2 first
            text, metadata = self._extract_with_pypdf2(file_path)
            
            # If no text found and OCR is enabled, use OCR
            if not text.strip() and self.enable_ocr:
                logger.info("No text found, attempting OCR extraction", file=file_path)
                text = self._extract_with_ocr(file_path)
            
            # If still no text, try pdfplumber
            if not text.strip():
                logger.info("Attempting pdfplumber extraction", file=file_path)
                text = self._extract_with_pdfplumber(file_path)
            
            return text, metadata
            
        except Exception as e:
            logger.error("Error parsing PDF", file=file_path, error=str(e))
            raise
    
    def _extract_with_pypdf2(self, file_path: str) -> Tuple [str, Dict[str, Any]]:
        """Extract text and metadata using PyPDF2"""
        text = ""
        metadata = {}
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get('/Title'),
                    "author": reader.metadata.get('/Author'),
                    "subject": reader.metadata.get('/Subject'),
                    "creator": reader.metadata.get('/Creator'),
                    "producer": reader.metadata.get('/Producer'),
                    "creation_date": reader.metadata.get('/CreationDate'),
                }
            
            metadata["num_pages"] = len(reader.pages)
            
            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text, metadata
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (better for tables)"""
        text = ""
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text
    
    def _extract_with_ocr(self, file_path: str) -> str:
        """Extract text using Tesseract OCR"""
        text = ""
        
        try:
            # Convert PDF pages to images and run OCR
            from pdf2image import convert_from_path
            
            images = convert_from_path(file_path)
            
            for i, image in enumerate(images):
                logger.info("Running OCR on page", page=i+1)
                page_text = pytesseract.image_to_string(image, lang='fra+eng')
                text += page_text + "\n\n"
        
        except Exception as e:
            logger.error("OCR failed", error=str(e))
        
        return text
