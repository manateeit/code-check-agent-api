from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Optional

from .config import settings
from .auth import verify_api_key
from .schemas import (
    ResearchRequest,
    SmartsheetExportRequest,
    ErrorResponse,
    HealthResponse
)
from .models import CodeCheckForm
from .agent import CodeCheckAgent
from .smartsheet_exporter import export_to_smartsheet

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint - verify service and dependencies.
    Does not require API key authentication.
    """
    services = {
        "perplexity": bool(settings.perplexity_api_key),
        "openai": bool(settings.openai_api_key),
        "gemini": bool(settings.gemini_api_key)
    }

    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        services=services
    )

@app.post(
    "/research",
    response_model=CodeCheckForm,
    tags=["Research"],
    dependencies=[Depends(verify_api_key)],
    responses={
        200: {"description": "Research completed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def research_address(request: ResearchRequest):
    """
    Research zoning and sign codes for a US address.

    **Required Header:**
    - `X-API-Key`: Your API key

    **Request Body:**
    - `address`: Full US address (e.g., "123 Main St, Springfield, IL 62701")
    - `llm_provider`: Optional, "openai" (default) or "gemini"

    **Returns:**
    - Complete CodeCheckForm with all researched data and source citations
    """
    try:
        # Validate LLM provider
        if request.llm_provider not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid llm_provider. Must be 'openai' or 'gemini'"
            )

        # Validate provider API key exists
        if request.llm_provider == "openai" and not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured"
            )
        if request.llm_provider == "gemini" and not settings.gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )

        # Execute research
        agent = CodeCheckAgent(llm_provider=request.llm_provider)
        result = agent.run(request.address)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research failed: {str(e)}"
        )

@app.post(
    "/research/smartsheet",
    tags=["Research"],
    dependencies=[Depends(verify_api_key)],
    responses={
        200: {"description": "Research completed and exported to Smartsheet"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def research_and_export(request: SmartsheetExportRequest):
    """
    Research zoning and sign codes for a US address and export to Smartsheet.

    **Required Header:**
    - `X-API-Key`: Your API key

    **Request Body:**
    - `address`: Full US address
    - `smartsheet_access_token`: Smartsheet API access token (provided by caller)
    - `llm_provider`: Optional, "openai" (default) or "gemini"
    - `workspace_name`: Optional, Smartsheet workspace name (default: "Code Research")
    - `workspace_id`: Optional, Pre-defined workspace ID to skip lookup

    **Returns:**
    - Research data (CodeCheckForm)
    - Smartsheet export details (sheet_url, sheet_id, rows_created)
    """
    try:
        # Validate LLM provider
        if request.llm_provider not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid llm_provider. Must be 'openai' or 'gemini'"
            )

        # Validate provider API key exists
        if request.llm_provider == "openai" and not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured"
            )
        if request.llm_provider == "gemini" and not settings.gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )

        # Execute research
        agent = CodeCheckAgent(llm_provider=request.llm_provider)
        result = agent.run(request.address)

        # Export to Smartsheet
        export_result = export_to_smartsheet(
            form=result,
            access_token=request.smartsheet_access_token,
            workspace_name=request.workspace_name,
            workspace_id=request.workspace_id
        )

        return {
            "research_data": result.model_dump(),
            "smartsheet": export_result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research or export failed: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# For Vercel deployment
handler = app
