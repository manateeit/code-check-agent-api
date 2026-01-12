#!/bin/bash
set -e

echo "📝 Creating Phase 0 Issues..."

REPO="manateeit/code-check-agent-api"
ASSIGNEE="manateeit"

# Helper function
create_issue() {
  local title="$1"
  local body="$2"
  local labels="$3"
  local milestone="$4"
  
  gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body "$body" \
    --label "$labels" \
    --milestone "$milestone" \
    --assignee "$ASSIGNEE" 2>/dev/null || echo "  ⚠️  Issue may exist: $title"
}

# Phase 0 Implementation Issue
create_issue \
  "[Phase 0] Setup Test Infrastructure" \
  "## 🎯 Objective
Setup pytest and test infrastructure for TDD workflow

## 📋 Tasks
- [ ] Install dependencies: \`pip install pytest pytest-asyncio httpx pytest-timeout\`
- [ ] Create \`pytest.ini\` configuration
- [ ] Create \`.env.test\` file with test credentials
- [ ] Create \`tests/\` directory structure
- [ ] Update \`requirements.txt\` with new dependencies

## 📦 New Dependencies
\`\`\`txt
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
pytest-timeout==2.2.0
supabase==2.3.0
modal==0.63.0
\`\`\`

## 📄 Files to Create
- \`pytest.ini\`
- \`.env.test\`
- \`tests/test_setup.py\`

## ✅ Exit Criteria
- All test dependencies installed
- pytest runs without import errors
- All 5 Phase 0 tests written (can fail - RED phase)

## 🔗 References
- TDD Plan Phase 0
- pytest documentation: https://docs.pytest.org" \
  "phase-0-setup,implementation,tdd" \
  "Phase 0: Setup & Dependencies"

# Test 1
create_issue \
  "[Phase 0][TEST] test_python_version" \
  "## 🧪 Test Description
Ensure Python 3.12+ is available

## 📄 Test File
\`tests/test_setup.py\`

## 💻 Implementation
\`\`\`python
import pytest

def test_python_version():
    \"\"\"Ensure Python 3.12+ is available\"\"\"
    import sys
    assert sys.version_info >= (3, 12), f\"Python 3.12+ required, got {sys.version}\"
\`\`\`

## 🔴 RED Phase
- [ ] Test written and fails (expected)

## 🟢 GREEN Phase
- [ ] Python 3.12+ verified
- [ ] Test passes

## ✅ Done
- [ ] Test committed to main branch" \
  "phase-0-setup,test,tdd" \
  "Phase 0: Setup & Dependencies"

# Test 2
create_issue \
  "[Phase 0][TEST] test_required_packages_importable" \
  "## 🧪 Test Description
Verify all new dependencies can be imported

## 📄 Test File
\`tests/test_setup.py\`

## 💻 Implementation
\`\`\`python
def test_required_packages_importable():
    \"\"\"Verify all new dependencies can be imported\"\"\"
    import supabase
    import modal
    import pytest
    import httpx
    assert True
\`\`\`

## 🔴 RED Phase
- [ ] Test written and fails (expected - packages not installed)

## 🟢 GREEN Phase
- [ ] Run: \`pip install -r requirements.txt\`
- [ ] Test passes

## ✅ Done
- [ ] All packages importable" \
  "phase-0-setup,test,tdd" \
  "Phase 0: Setup & Dependencies"

# Test 3
create_issue \
  "[Phase 0][TEST] test_supabase_connection" \
  "## 🧪 Test Description
Verify Supabase credentials configured and connection works

## 📄 Test File
\`tests/test_setup.py\`

## 💻 Implementation
\`\`\`python
def test_supabase_connection():
    \"\"\"Verify Supabase credentials are configured\"\"\"
    from app.db import supabase
    result = supabase.table('jobs').select('count').execute()
    assert result is not None
\`\`\`

## 📋 Prerequisites
- [ ] Create Supabase project at https://supabase.com
- [ ] Get SUPABASE_URL from project settings
- [ ] Get SUPABASE_KEY (service_role key) from API settings
- [ ] Add to \`.env.test\`

## 🔴 RED Phase
- [ ] Test written and fails (no credentials)

## 🟢 GREEN Phase
- [ ] Supabase project created
- [ ] Credentials in .env.test
- [ ] Test passes" \
  "phase-0-setup,test,tdd" \
  "Phase 0: Setup & Dependencies"

# Test 4
create_issue \
  "[Phase 0][TEST] test_modal_authentication" \
  "## 🧪 Test Description
Verify Modal is authenticated

## 📄 Test File
\`tests/test_setup.py\`

## 💻 Implementation
\`\`\`python
def test_modal_authentication():
    \"\"\"Verify Modal is authenticated\"\"\"
    import modal
    client = modal.Client()
    assert client.authenticated
\`\`\`

## 📋 Prerequisites
- [ ] Create Modal account at https://modal.com
- [ ] Install Modal CLI: \`pip install modal\`
- [ ] Authenticate: \`modal token new\`

## 🔴 RED Phase
- [ ] Test written and fails (not authenticated)

## 🟢 GREEN Phase
- [ ] Modal account created
- [ ] Authenticated with \`modal token new\`
- [ ] Test passes" \
  "phase-0-setup,test,tdd" \
  "Phase 0: Setup & Dependencies"

# Test 5
create_issue \
  "[Phase 0][TEST] test_environment_variables" \
  "## 🧪 Test Description
Ensure all required environment variables are set

## 📄 Test File
\`tests/test_setup.py\`

## 💻 Implementation
\`\`\`python
def test_environment_variables():
    \"\"\"Ensure all required env vars are set\"\"\"
    import os
    required = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'PERPLEXITY_API_KEY',
        'OPENAI_API_KEY'
    ]
    for var in required:
        assert os.getenv(var), f\"{var} not set in environment\"
\`\`\`

## 📋 Required Variables
- \`SUPABASE_URL\` - From Supabase project settings
- \`SUPABASE_KEY\` - Service role key from Supabase
- \`PERPLEXITY_API_KEY\` - From https://perplexity.ai/settings/api
- \`OPENAI_API_KEY\` - From https://platform.openai.com/api-keys

## 🔴 RED Phase
- [ ] Test written and fails (vars not set)

## 🟢 GREEN Phase
- [ ] All API keys obtained
- [ ] Added to \`.env.test\`
- [ ] Test passes" \
  "phase-0-setup,test,tdd" \
  "Phase 0: Setup & Dependencies"

# Gate Issue
create_issue \
  "[Phase 0][🚦 GATE] Phase 0 Exit Criteria" \
  "## 🚦 Exit Criteria Checklist

**All Phase 0 tests MUST pass before proceeding to Phase 1.**

### 📊 Tests Status (5 total)
- [ ] test_python_version ✅
- [ ] test_required_packages_importable ✅
- [ ] test_supabase_connection ✅
- [ ] test_modal_authentication ✅
- [ ] test_environment_variables ✅

### 🧪 Run All Tests
\`\`\`bash
pytest tests/test_setup.py -v
\`\`\`

### ✅ Expected Output
\`\`\`
tests/test_setup.py::test_python_version PASSED                    [ 20%]
tests/test_setup.py::test_required_packages_importable PASSED      [ 40%]
tests/test_setup.py::test_supabase_connection PASSED               [ 60%]
tests/test_setup.py::test_modal_authentication PASSED              [ 80%]
tests/test_setup.py::test_environment_variables PASSED             [100%]

======================== 5 passed in 2.34s =========================
\`\`\`

## 📋 Additional Verification
- [ ] \`requirements.txt\` updated with new dependencies
- [ ] \`pytest.ini\` created
- [ ] \`.env.test\` created with all credentials
- [ ] \`.gitignore\` includes \`.env.test\`

## 🚦 Gate Status
Current: **⏳ PENDING**

Once all tests pass:
1. ✅ Update status to **🟢 PASSED**
2. 🎉 Close this issue
3. 🚀 Proceed to Phase 1" \
  "phase-0-setup,gate,tdd" \
  "Phase 0: Setup & Dependencies"

echo "✅ Phase 0: Created 7 issues (5 tests + 1 implementation + 1 gate)"
