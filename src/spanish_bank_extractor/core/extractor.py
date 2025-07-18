"""
Phone Number Extractor Module

Core functionality for extracting phone numbers from Spanish bank IBAN data.
"""

import re
from typing import List, Dict, Optional, Any
from .bank_registry import BankRegistry
import os


class SpanishBankExtractor:
    """Main class for extracting phone numbers from Spanish bank IBAN data."""
    
    def __init__(self, bank_registry: Optional[BankRegistry] = None):
        """
        Initialize the extractor.
        
        Args:
            bank_registry: Bank registry instance. If None, creates a new one.
        """
        self.bank_registry = bank_registry or BankRegistry()
        self._phone_patterns = self._compile_phone_patterns()
    
    def _compile_phone_patterns(self) -> List[re.Pattern]:
        """
        Compile phone number patterns for Spanish numbers.
        Excludes numbers starting with 9.
        
        Returns:
            List of compiled regex patterns.
        """
        patterns = [
            # International format with +34 prefix
            r'\+34\s*\d{9}',  # +34 123456789 or +34123456789
            # International format with grouping
            r'\+34\s*\d{2,3}\s*\d{3}\s*\d{2}\s*\d{2}',  # +34 12 345 67 89 or +34 123 45 67 89
            
            # Spanish mobile numbers (6, 7, 8) - must be exactly 9 digits (excludes 9)
            r'\b[6-8]\d{8}\b',  # 612345678, 712345678, 812345678
            
            # Spanish mobile numbers with spaces (9 digits total) (excludes 9)
            r'\b[6-8]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}\b',  # 612 345 67 89, 712 345 67 89, 812 345 67 89
            
            # Spanish landline numbers (9 digits starting with 8 only)
            r'\b8\d{8}\b',  # 812345678
            
            # Spanish landline numbers with spaces (9 digits total) (excludes 9)
            r'\b8\d{2}\s*\d{3}\s*\d{2}\s*\d{2}\b',  # 812 345 67 89
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def extract_phone_numbers(self, iban_prefix: str, text: str) -> List[str]:
        """
        Extract phone numbers from text that match the given IBAN prefix.
        
        Args:
            iban_prefix: The IBAN prefix of the bank to filter by.
            text: The text to extract phone numbers from.
            
        Returns:
            List of extracted phone numbers.
        """
        # Normalize IBAN prefix to match registry format
        normalized_prefix = self.normalize_iban_prefix(iban_prefix)
        # Get the entity code for the bank
        entity_code = self.bank_registry.get_entity_code(normalized_prefix)
        if not entity_code:
            return []

        # Find all IBANs in the line
        iban_pattern = re.compile(r'ES\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}', re.IGNORECASE)
        ibans_in_line = iban_pattern.findall(text.replace('-', ''))
        found_match = False
        for iban in ibans_in_line:
            clean_iban = iban.replace(' ', '')
            if len(clean_iban) >= 8 and clean_iban.startswith('ES'):
                iban_entity_code = clean_iban[4:8]
                if iban_entity_code == entity_code:
                    found_match = True
                    break
        if not found_match:
            return []

        # Extract phone numbers
        phone_numbers = []
        for pattern in self._phone_patterns:
            matches = pattern.findall(text)
            phone_numbers.extend(matches)
        # Remove duplicates while preserving order
        seen = set()
        unique_phones = []
        for phone in phone_numbers:
            if phone not in seen:
                seen.add(phone)
                unique_phones.append(phone)
        return unique_phones
    
    def normalize_iban_prefix(self, iban_prefix: str) -> str:
        """
        Normalize IBAN prefix to match registry format.
        
        Args:
            iban_prefix: The IBAN prefix (e.g., 'ES91 0049' or 'ES0049')
            
        Returns:
            Normalized prefix (e.g., 'ES0049')
        """
        # Remove spaces
        clean_prefix = iban_prefix.replace(' ', '')
        
        # If it starts with ES and has more than 2 characters after ES
        if clean_prefix.startswith('ES') and len(clean_prefix) > 2:
            # Check if this is already a 4-digit entity code (like ES0049)
            if len(clean_prefix) == 6 and clean_prefix[2:6].isdigit():
                return clean_prefix  # Already in correct format
            
            # Extract the entity code part (after ES and check digits)
            # Spanish IBAN format: ES + 2 check digits + 4 entity code + rest
            if len(clean_prefix) >= 6:
                # Extract entity code (positions 4-7 after ES)
                entity_code = clean_prefix[4:8]
                return f"ES{entity_code}"
        
        return clean_prefix
    
    def process_text(self, iban_prefix: str, text: str) -> List[Dict[str, Any]]:
        """
        Process text and extract phone numbers with line information.
        
        Args:
            iban_prefix: The IBAN prefix of the bank to filter by.
            text: The text to process.
            
        Returns:
            List of dictionaries with line information and phone numbers.
        """
        lines = text.split('\n')
        results = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                phone_numbers = self.extract_phone_numbers(iban_prefix, line)
                if phone_numbers:
                    results.append({
                        'line_number': i + 1,
                        'text': line,
                        'phone_numbers': phone_numbers,
                        'phone_count': len(phone_numbers)
                    })
        
        return results
    
    def process_file(self, iban_prefix: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a file and extract phone numbers.
        
        Args:
            iban_prefix: The IBAN prefix of the bank to filter by.
            file_path: Path to the file to process.
            
        Returns:
            List of dictionaries with line information and phone numbers.
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                return self.process_text(iban_prefix, content)
        except Exception as e:
            raise RuntimeError(f"Error processing file {file_path}: {e}")
    
    def process_large_file(self, iban_prefix: str, file_path: str, chunk_size: int = 10000, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Process large files in chunks to avoid memory issues.
        
        Args:
            iban_prefix: The IBAN prefix of the bank to filter by.
            file_path: Path to the file to process.
            chunk_size: Number of lines to process at once.
            progress_callback: Optional callback function for progress reporting.
            
        Returns:
            List of dictionaries with line information and phone numbers.
        """
        results = []
        total_lines = 0
        processed_lines = 0
        
        try:
            # Count total lines first
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                total_lines = sum(1 for _ in file)
            
            # Process file in chunks
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                chunk_lines = []
                
                for line_num, line in enumerate(file, 1):
                    chunk_lines.append((line_num, line.strip()))
                    
                    # Process chunk when it reaches the specified size
                    if len(chunk_lines) >= chunk_size:
                        chunk_results = self._process_chunk(iban_prefix, chunk_lines)
                        results.extend(chunk_results)
                        
                        processed_lines += len(chunk_lines)
                        if progress_callback:
                            progress = (processed_lines / total_lines) * 100
                            progress_callback(progress, processed_lines, total_lines)
                        
                        chunk_lines = []
                
                # Process remaining lines
                if chunk_lines:
                    chunk_results = self._process_chunk(iban_prefix, chunk_lines)
                    results.extend(chunk_results)
                    
                    processed_lines += len(chunk_lines)
                    if progress_callback:
                        progress = (processed_lines / total_lines) * 100
                        progress_callback(progress, processed_lines, total_lines)
                        
        except Exception as e:
            raise RuntimeError(f"Error processing large file {file_path}: {e}")
        
        return results
    
    def _process_chunk(self, iban_prefix: str, chunk_lines: List[tuple]) -> List[Dict[str, Any]]:
        """
        Process a chunk of lines.
        
        Args:
            iban_prefix: The IBAN prefix of the bank to filter by.
            chunk_lines: List of (line_number, line_text) tuples.
            
        Returns:
            List of dictionaries with line information and phone numbers.
        """
        results = []
        
        for line_num, line in chunk_lines:
            if line:  # Skip empty lines
                phone_numbers = self.extract_phone_numbers(iban_prefix, line)
                if phone_numbers:
                    results.append({
                        'line_number': line_num,
                        'text': line,
                        'phone_numbers': phone_numbers,
                        'phone_count': len(phone_numbers)
                    })
        
        return results
    
    def estimate_file_size(self, file_path: str) -> dict:
        """
        Estimate file size and processing requirements.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary with file statistics.
        """
        try:
            file_size = os.path.getsize(file_path)
            line_count = 0
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                # Count lines efficiently
                for _ in file:
                    line_count += 1
                    if line_count > 10000:  # Sample first 10k lines
                        break
            
            # Estimate total lines if we sampled
            if line_count == 10000:
                estimated_lines = int((file_size / file.tell()) * line_count)
            else:
                estimated_lines = line_count
            
            return {
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'estimated_lines': estimated_lines,
                'is_large_file': file_size > 10 * 1024 * 1024,  # > 10MB
                'recommended_chunk_size': min(5000, max(1000, estimated_lines // 100))
            }
        except Exception as e:
            raise RuntimeError(f"Error estimating file size: {e}")
    
    def get_bank_info(self, iban_prefix: str) -> Optional[Dict[str, str]]:
        """
        Get information about a specific bank.
        
        Args:
            iban_prefix: The IBAN prefix of the bank.
            
        Returns:
            Bank information dictionary or None if not found.
        """
        normalized_prefix = self.normalize_iban_prefix(iban_prefix)
        return self.bank_registry.get_bank_info(normalized_prefix)
    
    def get_major_banks(self) -> List[tuple]:
        """
        Get list of major Spanish banks.
        
        Returns:
            List of tuples (iban_prefix, display_name) for major banks.
        """
        return self.bank_registry.get_major_banks()
    
    def search_banks(self, search_term: str) -> List[tuple]:
        """
        Search banks by name.
        
        Args:
            search_term: Search term to match against bank names.
            
        Returns:
            List of tuples (iban_prefix, bank_name) for matching banks.
        """
        return self.bank_registry.search_banks(search_term)
    
    def get_all_banks(self) -> List[tuple]:
        """
        Get all banks in the registry.
        
        Returns:
            List of tuples (iban_prefix, name, entity_code, address).
        """
        return self.bank_registry.get_all_banks()
    
    def validate_iban_format(self, iban: str) -> bool:
        """
        Validate Spanish IBAN format.
        
        Args:
            iban: The IBAN to validate.
            
        Returns:
            True if the IBAN format is valid, False otherwise.
        """
        # Spanish IBAN format: ES + 2 check digits + 4 entity code + rest
        pattern = r'^ES\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}$'
        return bool(re.match(pattern, iban.replace(' ', '')))
    
    def extract_entity_code_from_iban(self, iban: str) -> Optional[str]:
        """
        Extract entity code from a Spanish IBAN.
        
        Args:
            iban: The Spanish IBAN.
            
        Returns:
            The 4-digit entity code or None if invalid format.
        """
        # Remove spaces and check format
        clean_iban = iban.replace(' ', '')
        if not clean_iban.startswith('ES') or len(clean_iban) < 6:
            return None
        
        # Extract entity code (positions 4-7 after ES)
        return clean_iban[4:8] 