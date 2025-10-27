__version__ = "0.1.0"

# Expose FastAPI app to allow: uvicorn python:app
from .main import app

__all__ = ["app", "__version__"]
