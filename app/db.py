"""
Database Client for Async Job Queue

Provides CRUD operations for jobs and research results using Supabase.
Uses connection pooling via singleton pattern.
"""
from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Get cached Supabase client with connection pooling.
    
    Uses lru_cache to ensure single instance (singleton pattern).
    Environment variables:
    - SUPABASE_URL: Project URL from Supabase dashboard
    - SUPABASE_KEY, SUPABASE_SERVICE_KEY, or SUPABASE_SERVICE_ROLE_KEY: Service role key
    
    Returns:
        Client: Configured Supabase client
    
    Raises:
        ValueError: If environment variables not set
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = (os.getenv("SUPABASE_KEY") or 
                    os.getenv("SUPABASE_SERVICE_KEY") or 
                    os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable not set")
    if not supabase_key:
        raise ValueError("SUPABASE_KEY, SUPABASE_SERVICE_KEY, or SUPABASE_SERVICE_ROLE_KEY environment variable not set")
    
    return create_client(supabase_url, supabase_key)


class JobDB:
    """
    Database operations for jobs and research results.
    
    All methods use the singleton Supabase client for connection pooling.
    """
    
    @staticmethod
    def _get_client() -> Client:
        """Get the pooled Supabase client"""
        return get_supabase_client()
    
    @staticmethod
    def create_job(address: str, llm_provider: str = "openai") -> Dict[str, Any]:
        """
        Create a new job record.
        
        Args:
            address: US address to research
            llm_provider: LLM provider ('openai' or 'gemini')
        
        Returns:
            Dict containing job data with 'id', 'status', 'address', etc.
        
        Raises:
            Exception: If database insert fails
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_jobs").insert({
            "address": address,
            "llm_provider": llm_provider,
            "status": "pending",
            "progress": "0/13 sections"
        }).execute()
        
        return result.data[0]
    
    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID.
        
        Args:
            job_id: UUID of the job
        
        Returns:
            Dict containing job data, or None if not found
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_jobs")\
            .select("*")\
            .eq("id", job_id)\
            .execute()
        
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_job(job_id: str, **updates) -> Dict[str, Any]:
        """
        Update job fields.
        
        Args:
            job_id: UUID of the job
            **updates: Field names and values to update
        
        Returns:
            Dict containing updated job data
        
        Example:
            update_job(job_id, status="processing", progress="5/13")
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_jobs")\
            .update(updates)\
            .eq("id", job_id)\
            .execute()
        
        return result.data[0]
    
    @staticmethod
    def save_section_result(
        job_id: str,
        section_name: str,
        section_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save research result for a specific section.
        
        Args:
            job_id: UUID of the parent job
            section_name: Name of the section (e.g., 'location_information')
            section_data: Full section data as dict (Pydantic model dict)
        
        Returns:
            Dict containing saved result with 'id', 'job_id', 'section_name', etc.
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_research_results").insert({
            "job_id": job_id,
            "section_name": section_name,
            "section_data": section_data
        }).execute()
        
        return result.data[0]
    
    @staticmethod
    def get_job_results(job_id: str) -> List[Dict[str, Any]]:
        """
        Get all research results for a job.
        
        Args:
            job_id: UUID of the job
        
        Returns:
            List of dicts containing section results, ordered by created_at
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_research_results")\
            .select("*")\
            .eq("job_id", job_id)\
            .order("created_at")\
            .execute()
        
        return result.data
    
    @staticmethod
    def list_jobs(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List jobs with pagination.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
        
        Returns:
            List of dicts containing job data, ordered by created_at DESC
        """
        client = JobDB._get_client()
        
        result = client.table("code_research_jobs")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return result.data
    
    @staticmethod
    def delete_job(job_id: str) -> None:
        """
        Delete a job and all associated results (CASCADE).
        
        Args:
            job_id: UUID of the job to delete
        
        Note:
            This will automatically delete all research_results rows
            associated with this job due to ON DELETE CASCADE.
        """
        client = JobDB._get_client()
        
        client.table("code_research_jobs").delete().eq("id", job_id).execute()


# Module-level singleton instance for backwards compatibility
supabase = get_supabase_client()
