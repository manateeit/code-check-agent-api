"""
Phase 3 Tests: Modal Worker Logic

Tests the worker logic that processes jobs.
These are unit tests that don't require Modal to be running.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


def test_worker_logic_imports():
    """
    Test 1: Verify worker logic module can be imported
    
    RED phase: Will fail if worker_logic.py doesn't exist
    GREEN phase: Module exists and imports successfully
    """
    from app.worker_logic import process_research_job
    
    assert callable(process_research_job)
    assert process_research_job.__name__ == "process_research_job"


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_updates_job_status_to_processing(mock_job_db, mock_agent_class):
    """
    Test 2: Worker updates job status to 'processing' when starting
    
    RED phase: Will fail - worker logic not implemented
    GREEN phase: Status updated correctly
    """
    from app.worker_logic import process_research_job
    
    # Setup mocks
    mock_agent = Mock()
    mock_agent.run.return_value = Mock(location_information=None)  # Minimal result
    mock_agent_class.return_value = mock_agent
    
    # Execute worker
    process_research_job("test-job-123", "123 Main St", "openai")
    
    # Verify status updated to processing
    # Check that update_job was called with status='processing'
    processing_calls = [call for call in mock_job_db.update_job.call_args_list 
                        if len(call[0]) > 0 and call[0][0] == "test-job-123" 
                        and 'status' in call[1] and call[1]['status'] == 'processing']
    assert len(processing_calls) > 0, "Job status never updated to 'processing'"


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_runs_code_check_agent(mock_job_db, mock_agent_class):
    """
    Test 3: Worker executes CodeCheckAgent.run()
    
    RED phase: Will fail - agent not called
    GREEN phase: Agent executed with correct parameters
    """
    from app.worker_logic import process_research_job
    
    # Setup mocks
    mock_agent = Mock()
    mock_result = Mock()
    mock_result.location_information = None
    mock_agent.run.return_value = mock_result
    mock_agent_class.return_value = mock_agent
    
    # Execute worker
    process_research_job("test-job-456", "456 Oak Ave", "gemini")
    
    # Verify agent initialized and run
    mock_agent_class.assert_called_once_with(llm_provider="gemini")
    mock_agent.run.assert_called_once_with("456 Oak Ave")


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_saves_section_results(mock_job_db, mock_agent_class):
    """
    Test 4: Worker saves section results to database
    
    RED phase: Will fail - sections not saved
    GREEN phase: Each section saved via JobDB.save_section_result()
    """
    from app.worker_logic import process_research_job
    
    # Setup mock result with sections
    mock_result = Mock()
    mock_result.location_information = Mock(model_dump=lambda: {"city": "Miami"})
    mock_result.wall_signs = Mock(model_dump=lambda: {"allowed": True})
    # Other sections return None
    for attr in ["projecting_signs", "freestanding_signs", "directionals_regulatory",
                 "informational_signs", "awnings", "undercanopy_signs", "window_signs",
                 "temporary_signs", "approval_process", "permit_requirements", "variance_procedures"]:
        setattr(mock_result, attr, None)
    
    mock_agent = Mock()
    mock_agent.run.return_value = mock_result
    mock_agent_class.return_value = mock_agent
    
    # Execute worker
    result = process_research_job("test-job-789", "789 Elm St", "openai")
    
    # Verify sections saved
    assert mock_job_db.save_section_result.call_count >= 2
    
    # Check specific section saves
    calls = mock_job_db.save_section_result.call_args_list
    section_names = [call[1]['section_name'] for call in calls]
    assert "location_information" in section_names
    assert "wall_signs" in section_names
    
    # Verify result
    assert result["status"] == "completed"
    assert result["sections_completed"] >= 2


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_updates_job_status_to_completed(mock_job_db, mock_agent_class):
    """
    Test 5: Worker updates job status to 'completed' on success
    
    RED phase: Will fail - status not updated
    GREEN phase: Final status set correctly
    """
    from app.worker_logic import process_research_job
    
    # Setup mocks
    mock_agent = Mock()
    mock_agent.run.return_value = Mock(location_information=None)
    mock_agent_class.return_value = mock_agent
    
    # Execute worker
    result = process_research_job("test-job-complete", "Complete St", "openai")
    
    # Verify final status update
    final_call = [call for call in mock_job_db.update_job.call_args_list 
                  if 'status' in call[1] and call[1]['status'] == 'completed']
    assert len(final_call) > 0, "Job status never updated to 'completed'"
    
    # Verify result
    assert result["status"] == "completed"


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_handles_agent_failure(mock_job_db, mock_agent_class):
    """
    Test 6: Worker handles agent failures gracefully
    
    RED phase: Will fail - exceptions not caught
    GREEN phase: Error caught, job status set to 'failed'
    """
    from app.worker_logic import process_research_job
    
    # Setup agent to raise exception
    mock_agent = Mock()
    mock_agent.run.side_effect = Exception("Research failed!")
    mock_agent_class.return_value = mock_agent
    
    # Execute worker (should not raise)
    result = process_research_job("test-job-error", "Error St", "openai")
    
    # Verify error handling
    assert result["status"] == "failed"
    assert "error" in result
    assert "Research failed!" in result["error"]
    
    # Verify job marked as failed
    failed_call = [call for call in mock_job_db.update_job.call_args_list 
                   if 'status' in call[1] and call[1]['status'] == 'failed']
    assert len(failed_call) > 0, "Job status never updated to 'failed'"


@patch('app.agent.CodeCheckAgent')
@patch('app.db.JobDB')
def test_worker_updates_progress_incrementally(mock_job_db, mock_agent_class):
    """
    Test 7: Worker updates progress as sections complete
    
    RED phase: Will fail - progress not tracked
    GREEN phase: Progress updated for each section (1/13, 2/13, etc.)
    """
    from app.worker_logic import process_research_job
    
    # Setup mock result with multiple sections
    mock_result = Mock()
    for i, attr in enumerate(["location_information", "wall_signs", "projecting_signs"]):
        setattr(mock_result, attr, Mock(model_dump=lambda: {"data": i}))
    
    # Other sections return None
    for attr in ["freestanding_signs", "directionals_regulatory", "informational_signs", 
                 "awnings", "undercanopy_signs", "window_signs", "temporary_signs",
                 "approval_process", "permit_requirements", "variance_procedures"]:
        setattr(mock_result, attr, None)
    
    mock_agent = Mock()
    mock_agent.run.return_value = mock_result
    mock_agent_class.return_value = mock_agent
    
    # Execute worker
    process_research_job("test-job-progress", "Progress St", "openai")
    
    # Verify progress updates
    progress_calls = [call for call in mock_job_db.update_job.call_args_list 
                      if 'progress' in call[1]]
    
    assert len(progress_calls) >= 3, "Expected at least 3 progress updates"
    
    # Check progress values
    progress_values = [call[1]['progress'] for call in progress_calls]
    assert any('1/13' in p or '1 ' in p for p in progress_values), "Expected progress 1/13"
    assert any('2/13' in p or '2 ' in p for p in progress_values), "Expected progress 2/13"
    assert any('3/13' in p or '3 ' in p for p in progress_values), "Expected progress 3/13"
