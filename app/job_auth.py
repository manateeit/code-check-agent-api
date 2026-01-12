"""
API Key Authentication for Job Endpoints
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
import os

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_job_api_key(request: Request):
    """
    Dependency to verify API key from header for job endpoints
    
    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    api_key = request.headers.get("X-API-Key")
    expected_key = os.getenv("API_KEY")
    
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY not configured on server"
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header."
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True
