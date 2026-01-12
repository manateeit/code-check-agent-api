"""
Pydantic schemas for job API requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"


class JobStatus(str, Enum):
    """Job status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request schemas
class JobCreateRequest(BaseModel):
    """Request body for creating a new job"""
    address: str = Field(..., min_length=5, max_length=500, description="US address to research")
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider for extraction")
    
    @field_validator('address')
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Address cannot be empty')
        return v.strip()


# Response schemas
class JobResponse(BaseModel):
    """Response for job status"""
    job_id: str
    status: str
    address: str
    llm_provider: str
    progress: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allows creating from ORM models


class JobCreateResponse(BaseModel):
    """Response for job creation"""
    job_id: str
    status: str
    address: str
    llm_provider: str
    progress: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SectionResult(BaseModel):
    """Individual section result"""
    section_name: str
    section_data: dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobResultsResponse(BaseModel):
    """Response for job results with all sections"""
    job_id: str
    status: str
    sections: List[SectionResult]


class JobListItem(BaseModel):
    """Single job in list response"""
    job_id: str
    status: str
    address: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Response for job list with pagination"""
    jobs: List[JobListItem]
    total: int
    limit: int
    offset: int
