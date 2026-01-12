"""
Phase 0 Tests: Setup & Dependencies

These tests verify that the development environment is properly configured.
All tests should pass before proceeding to Phase 1.
"""
import pytest
import sys
import os


def test_python_version():
    """
    Test 1/5: Ensure Python 3.12+ is available
    
    RED phase: This test verifies Python version.
    GREEN phase: Should pass if Python 3.12+ is installed.
    """
    assert sys.version_info >= (3, 12), \
        f"Python 3.12+ required, got {sys.version_info.major}.{sys.version_info.minor}"


def test_required_packages_importable():
    """
    Test 2/5: Verify all new dependencies can be imported
    
    RED phase: Will fail if packages not installed.
    GREEN phase: Run `pip install -r requirements.txt`
    """
    # Core dependencies
    import supabase
    import modal
    import pytest
    import httpx
    
    # Existing dependencies (should already work)
    import fastapi
    import pydantic
    import openai
    
    assert True, "All packages imported successfully"


def test_supabase_connection():
    """
    Test 3/5: Verify Supabase credentials configured and connection works
    
    RED phase: Will fail without Supabase project and credentials.
    GREEN phase: Create Supabase project and add credentials to .env.test
    
    Prerequisites:
    1. Create Supabase project at https://supabase.com
    2. Get SUPABASE_URL from project settings
    3. Get SUPABASE_KEY (service_role key) from API settings
    4. Add both to .env.test
    """
    # Check environment variables are set
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = (os.getenv('SUPABASE_KEY') or 
                    os.getenv('SUPABASE_SERVICE_KEY') or 
                    os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
    
    assert supabase_url, "SUPABASE_URL not set in environment"
    assert supabase_key, "SUPABASE_KEY, SUPABASE_SERVICE_KEY, or SUPABASE_SERVICE_ROLE_KEY not set in environment"
    assert not supabase_url.startswith('your-'), "SUPABASE_URL not configured (still has placeholder)"
    assert not supabase_key.startswith('your-'), "SUPABASE_KEY not configured (still has placeholder)"
    
    # Test connection
    from supabase import create_client
    client = create_client(supabase_url, supabase_key)
    
    # Simple connection test - this will work even without tables
    # Just verifies credentials are valid
    result = client.table('_supabase_migrations').select('*').limit(0).execute()
    assert result is not None, "Failed to connect to Supabase"


def test_modal_authentication():
    """
    Test 4/5: Verify Modal is authenticated
    
    RED phase: Will fail if not authenticated with Modal.
    GREEN phase: Run `modal token new` to authenticate
    
    Prerequisites:
    1. Create Modal account at https://modal.com
    2. Install Modal CLI: `pip install modal`
    3. Authenticate: `modal token new`
    """
    import modal
    
    # Check if authenticated
    try:
        client = modal.Client()
        # In Modal, successful Client() creation means authenticated
        # Modal will raise an exception if not authenticated
        assert True, "Modal authenticated successfully"
    except Exception as e:
        pytest.fail(f"Modal not authenticated. Run 'modal token new'. Error: {str(e)}")


def test_environment_variables():
    """
    Test 5/5: Ensure all required environment variables are set
    
    RED phase: Will fail if env vars not configured.
    GREEN phase: Get all API keys and add to .env.test
    
    Required Variables:
    - SUPABASE_URL: From Supabase project settings
    - SUPABASE_KEY: Service role key from Supabase
    - PERPLEXITY_API_KEY: From https://perplexity.ai/settings/api
    - OPENAI_API_KEY: From https://platform.openai.com/api-keys
    """
    required_vars = [
        'SUPABASE_URL',
        ('SUPABASE_KEY', 'SUPABASE_SERVICE_KEY', 'SUPABASE_SERVICE_ROLE_KEY'),  # Any one is fine
        'PERPLEXITY_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if isinstance(var, tuple):
            # Check if any of the alternatives exist
            if not any(os.getenv(v) for v in var):
                missing_vars.append(f"{var[0]} (or alternatives)")
        else:
            if not os.getenv(var):
                missing_vars.append(var)
    
    assert not missing_vars, \
        f"Missing environment variables: {', '.join(missing_vars)}. " \
        f"Check .env.test file and ensure all API keys are configured."
    
    # Verify no placeholder values remain
    for var in ['SUPABASE_URL', 'PERPLEXITY_API_KEY', 'OPENAI_API_KEY']:
        value = os.getenv(var)
        if value:
            assert not value.startswith('your-'), \
                f"{var} still has placeholder value. Replace with actual API key."
