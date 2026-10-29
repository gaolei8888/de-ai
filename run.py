"""Serve the MVP studio and API on one local port."""
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from api.main import app

app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "web"), html=True), name="studio")
