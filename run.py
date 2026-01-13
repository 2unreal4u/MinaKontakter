#!/usr/bin/env python3
"""
KontaktRegister - Entry Point
Lokalt kontaktregister med krypterad databas.
"""

import sys
import os

# Lägg till src i path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import main

if __name__ == "__main__":
    main()
