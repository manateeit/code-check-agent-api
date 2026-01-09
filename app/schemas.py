from pydantic import BaseModel, Field
from typing import Optional

class ResearchRequest(BaseModel):
    """Request to research an address."""
    address: str = Field(..., description="Full US address to research (e.g., '123 Main St, Springfield, IL 62701')")
    llm_provider: Optional[str] = Field(default="openai", description="LLM provider to use: 'openai' or 'gemini'")

class SmartsheetExportRequest(BaseModel):
    """Request to export research to Smartsheet."""
    address: str = Field(..., description="Full US address to research")
    llm_provider: Optional[str] = Field(default="openai", description="LLM provider to use: 'openai' or 'gemini'")
    smartsheet_access_token: str = Field(..., description="Smartsheet API access token")
    workspace_name: Optional[str] = Field(default="Code Research", description="Smartsheet workspace name")
    workspace_id: Optional[int] = Field(default=None, description="Optional: Pre-defined workspace ID to skip lookup")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    services: dict = Field(..., description="Service availability status")
