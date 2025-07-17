"""
Bank Registry Module

Handles loading and managing Spanish bank information from the official registry.
"""

import csv
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class BankRegistry:
    """Manages Spanish bank information and provides search functionality."""
    
    def __init__(self, csv_file: Optional[str] = None):
        """
        Initialize the bank registry.
        
        Args:
            csv_file: Path to the CSV file containing bank data.
                      If None, uses default location.
        """
        if csv_file is None:
            # Look for the CSV file in data directory or current directory
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "data" / "lista-psri-es.csv",
                Path(__file__).parent.parent.parent.parent / "lista-psri-es.csv",
                Path("lista-psri-es.csv")
            ]
            
            for path in possible_paths:
                if path.exists():
                    csv_file = str(path)
                    break
            else:
                raise FileNotFoundError("Could not find lista-psri-es.csv in any expected location")
        
        self.csv_file = csv_file
        self.banks = self._load_banks()
    
    def _load_banks(self) -> Dict[str, Dict[str, str]]:
        """
        Load bank information from the CSV file.
        
        Returns:
            Dictionary mapping IBAN prefixes to bank information.
        """
        banks = {}
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    iban_prefix = row['CÓDIGO EUROPEO']
                    bank_name = row['NOMBRE']
                    
                    banks[iban_prefix] = {
                        'name': bank_name,
                        'iban_prefix': iban_prefix,
                        'address': row['DIRECCIÓN'],
                        'entity_code': iban_prefix[2:] if len(iban_prefix) >= 6 else iban_prefix,
                        'lei': row.get('LEI', ''),
                        'operator': row.get('OPERADOR', ''),
                        'provider': row.get('PROVEEDOR', ''),
                        'supervisor_code': row.get('CÓDIGO DE SUPERVISOR', '')
                    }
        except Exception as e:
            raise RuntimeError(f"Error reading CSV file: {e}")
        
        return banks
    
    def get_major_banks(self) -> List[Tuple[str, str]]:
        """
        Get a list of major Spanish banks for quick selection.
        
        Returns:
            List of tuples (iban_prefix, display_name) for major banks.
        """
        major_banks = [
            ('ES0182', 'BBVA (Banco Bilbao Vizcaya Argentaria)'),
            ('ES0049', 'Santander (Banco Santander)'),
            ('ES2100', 'Caixabank'),
            ('ES0081', 'Sabadell (Banco de Sabadell)'),
            ('ES0128', 'Bankinter'),
            ('ES0003', 'Banco de Depósitos'),
            ('ES0061', 'Banca March'),
            ('ES0188', 'Banco Alcalá'),
            ('ES0225', 'Banco Cetelem'),
            ('ES0198', 'Banco Cooperativo Español'),
        ]
        
        # Filter to only include banks that exist in our registry
        available_banks = []
        for iban_prefix, display_name in major_banks:
            if iban_prefix in self.banks:
                available_banks.append((iban_prefix, display_name))
        
        return available_banks
    
    def search_banks(self, search_term: str) -> List[Tuple[str, str]]:
        """
        Search banks by name.
        
        Args:
            search_term: Search term to match against bank names.
            
        Returns:
            List of tuples (iban_prefix, bank_name) for matching banks.
        """
        if not search_term.strip():
            return []
        
        matches = []
        search_term = search_term.lower().strip()
        
        # Early exit for very short search terms
        if len(search_term) < 2:
            return []
        
        for iban_prefix, bank_info in self.banks.items():
            if search_term in bank_info['name'].lower():
                matches.append((iban_prefix, bank_info['name']))
                # Limit results for performance
                if len(matches) >= 100:
                    break
        
        return matches
    
    def get_bank_info(self, iban_prefix: str) -> Optional[Dict[str, str]]:
        """
        Get information for a specific bank.
        
        Args:
            iban_prefix: The IBAN prefix of the bank.
            
        Returns:
            Bank information dictionary or None if not found.
        """
        return self.banks.get(iban_prefix)
    
    def get_all_banks(self) -> List[Tuple[str, str, str, str]]:
        """
        Get all banks in the registry.
        
        Returns:
            List of tuples (iban_prefix, name, entity_code, address).
        """
        all_banks = []
        for iban_prefix, bank_info in self.banks.items():
            all_banks.append((
                iban_prefix,
                bank_info['name'],
                bank_info['entity_code'],
                bank_info['address']
            ))
        return all_banks
    
    def get_entity_code(self, iban_prefix: str) -> Optional[str]:
        """
        Get the entity code for a given IBAN prefix.
        
        Args:
            iban_prefix: The IBAN prefix.
            
        Returns:
            The 4-digit entity code or None if not found.
        """
        bank_info = self.get_bank_info(iban_prefix)
        return bank_info['entity_code'] if bank_info else None
    
    def __len__(self) -> int:
        """Return the number of banks in the registry."""
        return len(self.banks)
    
    def __contains__(self, iban_prefix: str) -> bool:
        """Check if a bank exists in the registry."""
        return iban_prefix in self.banks 