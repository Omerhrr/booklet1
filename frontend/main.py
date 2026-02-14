"""
Frontend Entry Point
"""

import os
from app import create_app

app = create_app(os.getenv("APP_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host=os.getenv("FRONTEND_HOST", "0.0.0.0"),
        port=int(os.getenv("FRONTEND_PORT", 5000)),
        debug=os.getenv("DEBUG", "true").lower() == "true"
    )
