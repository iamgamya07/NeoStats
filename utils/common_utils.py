"""
Common utilities for the Banking Assistant Chatbot.
This module contains reusable functions and classes that can be used throughout the project.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re


class DataProcessor:
    """Utility class for data processing operations."""
    
    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSONL file.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            List of dictionaries loaded from the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logging.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
        return data
    
    @staticmethod
    def save_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save data to a JSONL file.
        
        Args:
            data: List of dictionaries to save
            file_path: Path to the output file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    @staticmethod
    def validate_banking_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate banking data format and quality.
        
        Args:
            data: List of banking documents to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'total_documents': len(data),
            'valid_documents': 0,
            'invalid_documents': 0,
            'missing_title': 0,
            'missing_content': 0,
            'empty_content': 0,
            'errors': []
        }
        
        for i, doc in enumerate(data):
            if not isinstance(doc, dict):
                validation_results['invalid_documents'] += 1
                validation_results['errors'].append(f"Document {i}: Not a dictionary")
                continue
            
            if 'title' not in doc:
                validation_results['missing_title'] += 1
                validation_results['errors'].append(f"Document {i}: Missing title")
            
            if 'content' not in doc:
                validation_results['missing_content'] += 1
                validation_results['errors'].append(f"Document {i}: Missing content")
            
            if 'content' in doc and not doc['content'].strip():
                validation_results['empty_content'] += 1
                validation_results['errors'].append(f"Document {i}: Empty content")
            
            if 'title' in doc and 'content' in doc and doc['content'].strip():
                validation_results['valid_documents'] += 1
        
        return validation_results


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\{\}]', '', text)
        
        return text
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    @staticmethod
    def extract_keywords(text: str, keywords: List[str]) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            
        Returns:
            List of found keywords
        """
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords


class ConfigValidator:
    """Utility class for validating configuration settings."""
    
    @staticmethod
    def validate_env_variables(required_vars: List[str]) -> Dict[str, bool]:
        """
        Validate that required environment variables are set.
        
        Args:
            required_vars: List of required environment variable names
            
        Returns:
            Dictionary with variable names as keys and validation status as values
        """
        validation_results = {}
        for var in required_vars:
            validation_results[var] = os.getenv(var) is not None
        return validation_results
    
    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """
        Check if a file exists and is readable.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file exists and is readable, False otherwise
        """
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


class Cache:
    """Simple in-memory cache utility for query responses."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of items in cache
        """
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = datetime.now()
    
    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.access_times.clear()
    
    def size(self) -> int:
        """
        Get current cache size.
        
        Returns:
            Number of items in cache
        """
        return len(self.cache)


# Global instances for easy access
data_processor = DataProcessor()
text_processor = TextProcessor()
config_validator = ConfigValidator()
cache = Cache() 