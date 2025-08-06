"""
Script to list all available routes in the FastAPI application.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './')))

from app.main import app
from app.core.config import settings

def list_routes():
    """List all available routes in the FastAPI application."""
    print(f"API_PREFIX from settings: {settings.API_PREFIX}")
    print("\nAVAILABLE ROUTES:")
    
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"Route: {route.path}, Methods: {route.methods if hasattr(route, 'methods') else 'N/A'}")

if __name__ == "__main__":
    list_routes()
