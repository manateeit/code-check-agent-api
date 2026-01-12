"""
Phase 1 Tests: Database Schema + Client

These tests verify database CRUD operations work correctly.
Run AFTER creating Supabase tables with migrations/001_create_tables.sql

All tests should pass before proceeding to Phase 2.
"""
import pytest
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def job_data():
    """Sample job data for testing"""
    return {
        "address": "123 Test St, Miami, FL",
        "llm_provider": "openai",
        "status": "pending",
        "progress": "0/13 sections"
    }


class TestJobDatabase:
    """Test job CRUD operations"""
    
    def test_create_job(self, job_data):
        """
        Test 1/9: Test job creation returns valid UUID and default values
        
        RED phase: Will fail until JobDB.create_job() is implemented
        GREEN phase: Implement create_job() method
        """
        from app.db import JobDB
        
        job = JobDB.create_job(
            address=job_data["address"],
            llm_provider=job_data["llm_provider"]
        )
        
        # Verify job was created with correct structure
        assert job["id"] is not None, "Job ID should not be None"
        assert isinstance(job["id"], str), "Job ID should be a string (UUID)"
        assert job["status"] == "pending", "New job should have 'pending' status"
        assert job["address"] == job_data["address"], "Address should match input"
        assert job["llm_provider"] == job_data["llm_provider"], "Provider should match input"
        assert "created_at" in job, "Job should have created_at timestamp"
        assert job["progress"] == "0/13 sections", "New job should start at 0/13"
    
    def test_get_job_exists(self, job_data):
        """
        Test 2/9: Test retrieving existing job returns correct data
        
        RED phase: Will fail until JobDB.get_job() is implemented
        GREEN phase: Implement get_job() method
        """
        from app.db import JobDB
        
        # Create a job first
        created = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        
        # Retrieve it
        retrieved = JobDB.get_job(created["id"])
        
        # Verify data matches
        assert retrieved is not None, "Job should be found"
        assert retrieved["id"] == created["id"], "IDs should match"
        assert retrieved["address"] == job_data["address"], "Address should match"
        assert retrieved["status"] == "pending", "Status should match"
    
    def test_get_job_not_found(self):
        """
        Test 3/9: Test retrieving non-existent job returns None
        
        RED phase: Will fail if get_job() doesn't handle missing jobs
        GREEN phase: Add None return for missing jobs
        """
        from app.db import JobDB
        
        fake_id = str(uuid4())
        job = JobDB.get_job(fake_id)
        
        assert job is None, "Non-existent job should return None"
    
    def test_update_job_status(self, job_data):
        """
        Test 4/9: Test updating job status works correctly
        
        RED phase: Will fail until JobDB.update_job() is implemented
        GREEN phase: Implement update_job() method
        """
        from app.db import JobDB
        
        # Create job
        job = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        
        # Update status
        updated = JobDB.update_job(job["id"], status="processing")
        
        # Verify update
        assert updated["status"] == "processing", "Status should be updated"
        assert updated["id"] == job["id"], "ID should remain same"
    
    def test_update_job_progress(self, job_data):
        """
        Test 5/9: Test updating job progress field
        
        RED phase: Will fail until update_job() handles progress field
        GREEN phase: Ensure update_job() can update any field
        """
        from app.db import JobDB
        
        job = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        
        # Update progress
        updated = JobDB.update_job(job["id"], progress="5/13 sections")
        
        assert updated["progress"] == "5/13 sections", "Progress should be updated"
    
    def test_save_research_result(self, job_data):
        """
        Test 6/9: Test saving section results to database
        
        RED phase: Will fail until JobDB.save_section_result() is implemented
        GREEN phase: Implement save_section_result() method
        """
        from app.db import JobDB
        
        job = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        
        # Sample section data (simplified Pydantic model)
        section_data = {
            "jurisdiction": {
                "value": "City of Miami",
                "source_url": "http://example.com/code",
                "notes": "Test data"
            }
        }
        
        # Save section result
        result = JobDB.save_section_result(
            job_id=job["id"],
            section_name="location_information",
            section_data=section_data
        )
        
        # Verify result was saved
        assert result["section_name"] == "location_information", "Section name should match"
        assert result["section_data"] == section_data, "Section data should match"
        assert result["job_id"] == job["id"], "Job ID should match"
        assert "id" in result, "Result should have an ID"
    
    def test_get_job_results(self, job_data):
        """
        Test 7/9: Test retrieving all section results for a job
        
        RED phase: Will fail until JobDB.get_job_results() is implemented
        GREEN phase: Implement get_job_results() method
        """
        from app.db import JobDB
        
        job = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        
        # Save 3 different sections
        for i in range(3):
            JobDB.save_section_result(
                job_id=job["id"],
                section_name=f"section_{i}",
                section_data={"data": f"test_{i}"}
            )
        
        # Retrieve all results
        results = JobDB.get_job_results(job["id"])
        
        # Verify all results returned
        assert len(results) == 3, "Should return all 3 results"
        assert results[0]["section_name"] == "section_0", "First section should be section_0"
        assert results[1]["section_name"] == "section_1", "Second section should be section_1"
        assert results[2]["section_name"] == "section_2", "Third section should be section_2"
    
    def test_list_jobs_pagination(self, job_data):
        """
        Test 8/9: Test listing jobs with pagination support
        
        RED phase: Will fail until JobDB.list_jobs() is implemented
        GREEN phase: Implement list_jobs() with limit/offset
        """
        from app.db import JobDB
        
        # Create 5 test jobs
        created_ids = []
        for i in range(5):
            job = JobDB.create_job(f"Address {i}", "openai")
            created_ids.append(job["id"])
        
        # Get first page (3 jobs)
        page1 = JobDB.list_jobs(limit=3, offset=0)
        
        # Get second page (2 jobs)
        page2 = JobDB.list_jobs(limit=3, offset=3)
        
        # Verify pagination works
        assert len(page1) == 3, "First page should have 3 jobs"
        assert len(page2) >= 2, "Second page should have at least 2 jobs"
        
        # Verify no overlap between pages
        page1_ids = [j["id"] for j in page1]
        page2_ids = [j["id"] for j in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0, "Pages should not overlap"
    
    def test_delete_job_cascade(self, job_data):
        """
        Test 9/9: Test deleting job also deletes associated results (CASCADE)
        
        RED phase: Will fail until JobDB.delete_job() is implemented
        GREEN phase: Implement delete_job() - CASCADE should be automatic from SQL
        """
        from app.db import JobDB
        
        # Create job with a result
        job = JobDB.create_job(job_data["address"], job_data["llm_provider"])
        JobDB.save_section_result(
            job_id=job["id"],
            section_name="test_section",
            section_data={"data": "test"}
        )
        
        # Verify result exists
        results_before = JobDB.get_job_results(job["id"])
        assert len(results_before) == 1, "Should have 1 result before delete"
        
        # Delete job
        JobDB.delete_job(job["id"])
        
        # Verify job is gone
        deleted_job = JobDB.get_job(job["id"])
        assert deleted_job is None, "Job should be deleted"
        
        # Verify results are also gone (CASCADE)
        results_after = JobDB.get_job_results(job["id"])
        assert len(results_after) == 0, "Results should be cascade deleted"


# Test fixtures cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """
    Automatically cleanup test data after each test.
    This prevents test pollution and ensures tests are independent.
    """
    yield  # Run the test
    
    # Cleanup after test
    # Note: In practice, you might want to track created IDs and delete them
    # For now, we rely on manual cleanup or test database reset
    pass
