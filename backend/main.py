"""
Backend Entry Point
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true"
    )
