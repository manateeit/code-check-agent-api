"""
Worker Logic for Background Job Processing

Extracted from Modal worker for testability.
This module contains pure functions that can be tested without Modal.
"""
import os
from typing import Dict, Any
from datetime import datetime
import sys

def process_research_job(job_id: str, address: str, llm_provider: str = "openai") -> Dict[str, Any]:
    """
    Process a research job: execute agent and save results to database.
    
    This is the core worker logic that runs in Modal.
    Separated for unit testing without Modal dependency.
    
    Args:
        job_id: UUID of the job to process
        address: US address to research
        llm_provider: LLM provider ('openai' or 'gemini')
    
    Returns:
        Dict with 'status', 'sections_completed', and optional 'error'
    
    Raises:
        Exception: If critical error occurs (caught by Modal wrapper)
    """
    from app.db import JobDB
    from app.agent import CodeCheckAgent
    
    try:
        print(f"[Worker] Starting job {job_id} for address: {address}", file=sys.stderr)
        
        # Update status to processing
        JobDB.update_job(
            job_id,
            status="processing",
            started_at=datetime.utcnow().isoformat()
        )
        print(f"[Worker] Job {job_id} status updated to processing", file=sys.stderr)
        
        # Initialize agent
        agent = CodeCheckAgent(llm_provider=llm_provider)
        print(f"[Worker] Agent initialized with provider: {llm_provider}", file=sys.stderr)
        
        # Execute research (this takes 2-3 minutes)
        result = agent.run(address)
        print(f"[Worker] Research completed for job {job_id}", file=sys.stderr)
        
        # Save all section results to database
        sections_saved = 0
        section_names = [
            "location_information",
            "wall_signs",
            "projecting_signs",
            "freestanding_signs",
            "directionals_regulatory",
            "informational_signs",
            "awnings",
            "undercanopy_signs",
            "window_signs",
            "temporary_signs",
            "approval_process",
            "permit_requirements",
            "variance_procedures"
        ]
        
        for section_name in section_names:
            if hasattr(result, section_name):
                section_data = getattr(result, section_name)
                if section_data:
                    # Convert Pydantic model to dict
                    section_dict = section_data.model_dump() if hasattr(section_data, 'model_dump') else section_data
                    
                    JobDB.save_section_result(
                        job_id=job_id,
                        section_name=section_name,
                        section_data=section_dict
                    )
                    sections_saved += 1
                    
                    # Update progress
                    JobDB.update_job(
                        job_id,
                        progress=f"{sections_saved}/13 sections"
                    )
                    print(f"[Worker] Saved section: {section_name} ({sections_saved}/13)", file=sys.stderr)
        
        # Mark job as completed
        JobDB.update_job(
            job_id,
            status="completed",
            completed_at=datetime.utcnow().isoformat(),
            progress=f"{sections_saved}/13 sections"
        )
        print(f"[Worker] Job {job_id} completed successfully. Saved {sections_saved} sections.", file=sys.stderr)
        
        return {
            "status": "completed",
            "sections_completed": sections_saved,
            "job_id": job_id
        }
        
    except Exception as e:
        error_msg = f"Job processing failed: {str(e)}"
        print(f"[Worker] ERROR in job {job_id}: {error_msg}", file=sys.stderr)
        
        # Mark job as failed
        try:
            JobDB.update_job(
                job_id,
                status="failed",
                error_message=error_msg,
                completed_at=datetime.utcnow().isoformat()
            )
        except Exception as db_error:
            print(f"[Worker] Failed to update job status: {db_error}", file=sys.stderr)
        
        return {
            "status": "failed",
            "error": error_msg,
            "job_id": job_id
        }
