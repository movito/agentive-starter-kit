"""
Pytest configuration for project-level test setup.

Adds project root to sys.path to enable imports from scripts/ directory.
"""

import sys
from pathlib import Path

# Add project root to Python path for test imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
