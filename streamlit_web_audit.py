#!/usr/bin/env python3
"""
Compat redirect for legacy users running from workspace root.
Simply calls the refactored ui.app entrypoint.
"""
import sys
import os

# Insert workspace root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import main

if __name__ == "__main__":
    main()
