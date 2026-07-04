"""Shared test fixtures."""

import os
import sys
from pathlib import Path

# Ensure src/ is on the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Settings is instantiated at import time and requires credentials; give the
# test run dummy ones so importing config/auth/server never depends on a .env.
os.environ.setdefault("SHOPWIRED_API_KEY", "test-key")
os.environ.setdefault("SHOPWIRED_API_SECRET", "test-secret")
