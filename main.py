#!/usr/bin/env python3
"""
Spanish Bank Phone Extractor - Main Entry Point
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spanish_bank_extractor.gui.app import main

if __name__ == "__main__":
    main() 