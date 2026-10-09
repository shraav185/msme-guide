"""Convenience launcher for the MSME Guide website."""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent / "Flask-Web-App-Tutorial-main"
sys.path.insert(0, str(PROJECT_DIR))

from website import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
