"""
Job Management API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.job_schemas import (
    JobCreateRequest,
    JobCreateResponse,
    JobResponse,
    JobResultsResponse,
    JobListResponse,
    JobListItem,
    SectionResult
)
from app.db import JobDB
from app.job_auth import verify_job_api_key

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_job_api_key)]
)
async def create_job(request: JobCreateRequest):
    """
    Submit a new research job
    
    **Authentication**: Requires X-API-Key header
    
    **Request Body**:
    - address: US address to research (required)
    - llm_provider: LLM provider - 'openai' or 'gemini' (default: 'openai')
    
    **Returns**: Job details with job_id and status
    """
    try:
        job = JobDB.create_job(
            address=request.address,
            llm_provider=request.llm_provider.value
        )
        
        return JobCreateResponse(
            job_id=job["id"],
            status=job["status"],
            address=job["address"],
            llm_provider=job["llm_provider"],
            progress=job["progress"],
            created_at=job["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    dependencies=[Depends(verify_job_api_key)]
)
async def get_job(job_id: str):
    """
    Get job status by ID
    
    **Authentication**: Requires X-API-Key header
    
    **Path Parameters**:
    - job_id: UUID of the job
    
    **Returns**: Job details including status and progress
    """
    job = JobDB.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    return JobResponse(
        job_id=job["id"],
        status=job["status"],
        address=job["address"],
        llm_provider=job["llm_provider"],
        progress=job.get("progress"),
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        error_message=job.get("error_message")
    )


@router.get(
    "/{job_id}/results",
    response_model=JobResultsResponse,
    dependencies=[Depends(verify_job_api_key)]
)
async def get_job_results(job_id: str):
    """
    Get job results (all completed sections)
    
    **Authentication**: Requires X-API-Key header
    
    **Path Parameters**:
    - job_id: UUID of the job
    
    **Returns**: Job status and array of section results
    
    **Note**: If job is not completed, returns empty sections array
    """
    job = JobDB.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    # Get all section results
    results = JobDB.get_job_results(job_id)
    
    sections = [
        SectionResult(
            section_name=result["section_name"],
            section_data=result["section_data"],
            created_at=result["created_at"]
        )
        for result in results
    ]
    
    return JobResultsResponse(
        job_id=job["id"],
        status=job["status"],
        sections=sections
    )


@router.get(
    "",
    response_model=JobListResponse,
    dependencies=[Depends(verify_job_api_key)]
)
async def list_jobs(limit: int = 50, offset: int = 0):
    """
    List all jobs with pagination
    
    **Authentication**: Requires X-API-Key header
    
    **Query Parameters**:
    - limit: Maximum number of jobs to return (default: 50, max: 100)
    - offset: Number of jobs to skip (default: 0)
    
    **Returns**: Paginated list of jobs with total count
    """
    # Enforce max limit
    if limit > 100:
        limit = 100
    
    if offset < 0:
        offset = 0
    
    jobs = JobDB.list_jobs(limit=limit, offset=offset)
    
    # For total count, we'd need a separate query
    # For now, just return the length of current page
    # TODO: Add count query in Phase 3
    total = len(jobs) + offset  # Approximate
    
    job_items = [
        JobListItem(
            job_id=job["id"],
            status=job["status"],
            address=job["address"],
            created_at=job["created_at"]
        )
        for job in jobs
    ]
    
    return JobListResponse(
        jobs=job_items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_job_api_key)]
)
async def delete_job(job_id: str):
    """
    Delete a job and all its results
    
    **Authentication**: Requires X-API-Key header
    
    **Path Parameters**:
    - job_id: UUID of the job to delete
    
    **Returns**: 204 No Content on success
    
    **Note**: Cascades to delete all associated research_results
    """
    job = JobDB.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    try:
        JobDB.delete_job(job_id)
        return None  # 204 No Content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )
