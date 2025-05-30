"""
API Documentation Configuration

This module provides utilities for customizing the FastAPI documentation.
It includes functions for configuring OpenAPI schemas and Swagger UI.
"""

from typing import Dict, List, Optional, Union

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import HTMLResponse

from app.core.config import settings


def custom_openapi(app: FastAPI) -> Dict:
    """
    Generate a custom OpenAPI schema with additional information.
    
    Args:
        app: The FastAPI application
        
    Returns:
        A dictionary containing the OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    # Base OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom branding
    openapi_schema["info"]["x-logo"] = {
        "url": settings.DOCS_LOGO_URL,
        "altText": f"{settings.APP_NAME} Logo",
    }
    
    # Add API server information
    openapi_schema["servers"] = [
        {
            "url": settings.APP_URL,
            "description": f"{settings.APP_ENV.capitalize()} environment",
        }
    ]
    
    # Add security schemes if needed
    if settings.AUTH_REQUIRED:
        openapi_schema["components"] = openapi_schema.get("components", {})
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your JWT token in the format: Bearer {token}",
            }
        }
        
        # Apply security globally
        openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Add custom API tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "health",
            "description": "Health check endpoints for monitoring system status",
            "externalDocs": {
                "description": "Health Check Documentation",
                "url": "https://example.com/docs/health",
            },
        },
        # Add more tags as needed
    ]
    
    # Store the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def custom_swagger_ui_html(
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
) -> HTMLResponse:
    """
    Generate custom Swagger UI HTML with additional styling.
    
    Args:
        openapi_url: URL to the OpenAPI schema
        title: API title
        swagger_js_url: URL to the Swagger UI JavaScript
        swagger_css_url: URL to the Swagger UI CSS
        swagger_favicon_url: URL to the favicon
        
    Returns:
        HTML response with custom Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_js_url=swagger_js_url,
        swagger_css_url=swagger_css_url,
        swagger_favicon_url=swagger_favicon_url,
        extra_html=f"""
        <style>
            .topbar {{
                background-color: {settings.DOCS_PRIMARY_COLOR} !important;
            }}
            .swagger-ui .opblock.opblock-get .opblock-summary-method {{
                background-color: #61affe !important;
            }}
            .swagger-ui .opblock.opblock-post .opblock-summary-method {{
                background-color: #49cc90 !important;
            }}
            .swagger-ui .opblock.opblock-put .opblock-summary-method {{
                background-color: #fca130 !important;
            }}
            .swagger-ui .opblock.opblock-delete .opblock-summary-method {{
                background-color: #f93e3e !important;
            }}
        </style>
        """,
    )


def custom_redoc_html(
    openapi_url: str,
    title: str,
    redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    redoc_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
) -> HTMLResponse:
    """
    Generate custom ReDoc HTML with additional styling.
    
    Args:
        openapi_url: URL to the OpenAPI schema
        title: API title
        redoc_js_url: URL to the ReDoc JavaScript
        redoc_favicon_url: URL to the favicon
        
    Returns:
        HTML response with custom ReDoc
    """
    return get_redoc_html(
        openapi_url=openapi_url,
        title=title,
        redoc_js_url=redoc_js_url,
        redoc_favicon_url=redoc_favicon_url,
        extra_head=f"""
        <style>
            :root {{
                --primary-color: {settings.DOCS_PRIMARY_COLOR};
            }}
            body {{
                margin: 0;
                padding: 0;
            }}
            .menu-content {{
                padding-top: 20px;
            }}
        </style>
        """,
    )


def setup_docs(app: FastAPI) -> None:
    """
    Set up custom API documentation.
    
    Args:
        app: The FastAPI application
    """
    # Set custom OpenAPI function
    app.openapi = lambda: custom_openapi(app)
    
    # Only set up docs in non-production environments
    if settings.APP_ENV != "production":
        # Mount custom Swagger UI
        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui():
            return custom_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - Swagger UI",
            )
        
        # Mount custom ReDoc
        @app.get("/redoc", include_in_schema=False)
        async def custom_redoc():
            return custom_redoc_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - ReDoc",
            )
