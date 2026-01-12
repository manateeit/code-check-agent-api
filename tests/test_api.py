"""
Phase 2 Tests: API Endpoints

These tests define the API contract for async job management.
All tests should FAIL initially (RED phase), then pass after implementation (GREEN phase).
"""
import pytest
from httpx import AsyncClient
import os
from uuid import uuid4


# Test fixtures
@pytest.fixture
def api_key():
    """Get API key from environment"""
    return os.getenv("API_KEY", "test-api-key-12345")


@pytest.fixture
def auth_headers(api_key):
    """Create authentication headers"""
    return {"X-API-Key": api_key}


@pytest.fixture
async def client():
    """Create async HTTP client for testing"""
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Test 1: Submit Job
@pytest.mark.asyncio
async def test_submit_job(client: AsyncClient, auth_headers: dict):
    """
    Test 1/8: Submit a new research job
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement POST /jobs endpoint
    """
    response = await client.post(
        "/jobs",
        json={
            "address": "123 Main St, Miami, FL",
            "llm_provider": "openai"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["address"] == "123 Main St, Miami, FL"
    assert data["llm_provider"] == "openai"
    assert data["progress"] == "0/13 sections"
    assert "created_at" in data


# Test 2: Submit Job Validation
@pytest.mark.asyncio
async def test_submit_job_validation(client: AsyncClient, auth_headers: dict):
    """
    Test 2/8: Validate request body
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement validation using Pydantic
    """
    # Missing required field 'address'
    response = await client.post(
        "/jobs",
        json={
            "llm_provider": "openai"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
    
    # Invalid llm_provider
    response = await client.post(
        "/jobs",
        json={
            "address": "123 Main St",
            "llm_provider": "invalid_provider"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422, "Should reject invalid llm_provider"


# Test 3: Get Job Status
@pytest.mark.asyncio
async def test_get_job_status(client: AsyncClient, auth_headers: dict):
    """
    Test 3/8: Get job status by ID
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement GET /jobs/{job_id} endpoint
    """
    # First create a job
    create_response = await client.post(
        "/jobs",
        json={"address": "456 Oak Ave, Austin, TX"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]
    
    # Then get its status
    response = await client.get(
        f"/jobs/{job_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "pending"
    assert data["address"] == "456 Oak Ave, Austin, TX"
    assert "created_at" in data


# Test 4: Get Job Not Found
@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient, auth_headers: dict):
    """
    Test 4/8: Handle non-existent job ID
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Return 404 for invalid job_id
    """
    fake_job_id = str(uuid4())
    
    response = await client.get(
        f"/jobs/{fake_job_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    # Check for 'detail' or 'error' key in response
    response_json = response.json()
    detail_msg = (response_json.get("detail", "") or response_json.get("error", "")).lower()
    assert "not found" in detail_msg, f"Expected 'not found' in response, got: {response_json}"


# Test 5: Get Job Results
@pytest.mark.asyncio
async def test_get_job_results(client: AsyncClient, auth_headers: dict):
    """
    Test 5/8: Get completed job results
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement GET /jobs/{job_id}/results endpoint
    
    Note: For now, we'll test with a pending job (no results yet)
    In Phase 3 with Modal workers, we'll have real completed jobs
    """
    # Create a job
    create_response = await client.post(
        "/jobs",
        json={"address": "789 Elm St, Portland, OR"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]
    
    # Try to get results (should fail - job not completed)
    response = await client.get(
        f"/jobs/{job_id}/results",
        headers=auth_headers
    )
    
    # For pending jobs, should return 400 or empty results
    # We'll accept either pattern
    if response.status_code == 400:
        assert "not completed" in response.json()["detail"].lower()
    elif response.status_code == 200:
        # If returning 200, should have empty sections
        data = response.json()
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) == 0  # No results yet


# Test 6: List Jobs
@pytest.mark.asyncio
async def test_list_jobs(client: AsyncClient, auth_headers: dict):
    """
    Test 6/8: List all jobs with pagination
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement GET /jobs endpoint
    """
    # Create a few test jobs
    for i in range(3):
        response = await client.post(
            "/jobs",
            json={"address": f"Address {i}, City, State"},
            headers=auth_headers
        )
        assert response.status_code == 201
    
    # List jobs
    response = await client.get(
        "/jobs?limit=10&offset=0",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["jobs"], list)
    assert len(data["jobs"]) >= 3  # At least the 3 we just created


# Test 7: Delete Job
@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient, auth_headers: dict):
    """
    Test 7/8: Delete a job
    
    RED phase: Will fail - endpoint doesn't exist yet
    GREEN phase: Implement DELETE /jobs/{job_id} endpoint
    """
    # Create a job
    create_response = await client.post(
        "/jobs",
        json={"address": "999 Delete St, Test City"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]
    
    # Delete the job
    response = await client.delete(
        f"/jobs/{job_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204  # No content
    
    # Verify job is deleted
    get_response = await client.get(
        f"/jobs/{job_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


# Test 8: API Key Required
@pytest.mark.asyncio
async def test_api_key_required(client: AsyncClient):
    """
    Test 8/8: Ensure authentication is required
    
    RED phase: Will fail - auth middleware doesn't exist yet
    GREEN phase: Implement API key authentication
    """
    # Try to submit job without API key
    response = await client.post(
        "/jobs",
        json={"address": "Unauthorized Request St"}
    )
    
    assert response.status_code == 401
    response_json = response.json()
    detail_msg = (response_json.get("detail", "") or response_json.get("error", "")).lower()
    assert "unauthorized" in detail_msg or "api key" in detail_msg or "required" in detail_msg, \
        f"Expected auth error in response, got: {response_json}"
    
    # Try with invalid API key
    response = await client.get(
        "/jobs",
        headers={"X-API-Key": "invalid-key-12345"}
    )
    
    assert response.status_code == 401
