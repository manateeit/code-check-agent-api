"""
Modal Background Worker for Code Research Jobs

This module defines the Modal serverless function that processes research jobs.
Deployed to Modal cloud and triggered by the API.
"""
import modal
import os

# Create Modal app
app = modal.App("code-check-worker")

# Define secrets (configure in Modal dashboard)
secrets = modal.Secret.from_name("code-check-secrets")

# Define image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "supabase==2.0.3",
        "httpx==0.24.1",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "openai>=1.10.0",
        "google-generativeai>=0.3.2",
        "requests>=2.31.0",
        "smartsheet-python-sdk==3.0.2",
        "python-dotenv>=1.0.0"
    )
)

@app.function(
    image=image,
    secrets=[secrets],
    timeout=600,  # 10 minutes max
    retries=0  # Don't retry automatically (jobs are idempotent)
)
def process_research_job(job_id: str, address: str, llm_provider: str = "openai"):
    """
    Modal function: Process a research job in the background.
    
    This function is deployed to Modal and invoked asynchronously
    when a job is submitted via POST /jobs.
    
    Args:
        job_id: UUID of the job to process
        address: US address to research  
        llm_provider: LLM provider ('openai' or 'gemini')
    
    Returns:
        Dict with status and results
    """
    import sys
    
    # Add app directory to path for imports
    sys.path.insert(0, "/root/app")
    
    # Import worker logic
    from worker_logic import process_research_job as worker_process
    
    print(f"[Modal] Processing job {job_id}", file=sys.stderr)
    
    # Execute worker logic
    result = worker_process(job_id, address, llm_provider)
    
    print(f"[Modal] Job {job_id} finished with status: {result['status']}", file=sys.stderr)
    
    return result


# Local testing function
@app.local_entrypoint()
def test_job():
    """
    Test function for local Modal execution.
    
    Run with: modal run app/modal_worker.py
    """
    print("Testing Modal worker locally...")
    
    # Test with a dummy job (you'll need to create one first)
    job_id = "test-job-id"
    address = "123 Test St, Test City, TS"
    
    result = process_research_job.remote(job_id, address, "openai")
    print(f"Result: {result}")


if __name__ == "__main__":
    # For local development
    print("Modal worker module loaded")
    print("Deploy with: modal deploy app/modal_worker.py")
    print("Test with: modal run app/modal_worker.py")
