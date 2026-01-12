#!/bin/bash
set -e

echo "📝 Creating Phase 1 Issues..."

REPO="manateeit/code-check-agent-api"
ASSIGNEE="manateeit"

create_issue() {
  gh issue create \
    --repo "$REPO" \
    --title "$1" \
    --body "$2" \
    --label "$3" \
    --milestone "$4" \
    --assignee "$ASSIGNEE" 2>/dev/null || echo "  ⚠️  Issue may exist: $1"
}

# Implementation Issue
create_issue \
  "[Phase 1] Create Database Schema + Client" \
  "## 🎯 Objective
Create Supabase tables and database client with CRUD operations

## 📋 Tasks

### Part 1: Database Schema
- [ ] Create \`migrations/001_create_tables.sql\`
- [ ] Define \`jobs\` table with all fields
- [ ] Define \`research_results\` table
- [ ] Create indexes for performance
- [ ] Enable UUID extension
- [ ] Enable real-time for jobs table
- [ ] Run migration in Supabase SQL Editor

### Part 2: Database Client
- [ ] Create \`app/db.py\`
- [ ] Implement \`get_supabase_client()\` with connection pooling
- [ ] Implement \`JobDB.create_job()\`
- [ ] Implement \`JobDB.get_job()\`
- [ ] Implement \`JobDB.update_job()\`
- [ ] Implement \`JobDB.save_section_result()\`
- [ ] Implement \`JobDB.get_job_results()\`
- [ ] Implement \`JobDB.list_jobs()\`
- [ ] Implement \`JobDB.delete_job()\`

## 📄 Files to Create
- \`migrations/001_create_tables.sql\`
- \`app/db.py\`
- \`tests/test_database.py\`

## ✅ Exit Criteria
- SQL schema created in Supabase
- All 8 CRUD methods implemented
- All 9 Phase 1 tests written (RED phase)

## 🔗 References
- TDD Plan Phase 1
- Supabase Python docs: https://supabase.com/docs/reference/python" \
  "phase-1-database,implementation,tdd" \
  "Phase 1: Database Schema + Client"

# Create all 9 test issues
for i in {1..9}; do
  case $i in
    1)
      create_issue \
        "[Phase 1][TEST] test_create_job" \
        "## 🧪 Test
Test job creation returns valid UUID

## 📄 File
\`tests/test_database.py\`

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    2)
      create_issue \
        "[Phase 1][TEST] test_get_job_exists" \
        "## 🧪 Test
Retrieve existing job

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    3)
      create_issue \
        "[Phase 1][TEST] test_get_job_not_found" \
        "## 🧪 Test
Non-existent job returns None

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    4)
      create_issue \
        "[Phase 1][TEST] test_update_job_status" \
        "## 🧪 Test
Update job status

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    5)
      create_issue \
        "[Phase 1][TEST] test_update_job_progress" \
        "## 🧪 Test
Update job progress field

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    6)
      create_issue \
        "[Phase 1][TEST] test_save_research_result" \
        "## 🧪 Test
Save section results

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    7)
      create_issue \
        "[Phase 1][TEST] test_get_job_results" \
        "## 🧪 Test
Retrieve all section results

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    8)
      create_issue \
        "[Phase 1][TEST] test_list_jobs_pagination" \
        "## 🧪 Test
List jobs with pagination

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
    9)
      create_issue \
        "[Phase 1][TEST] test_delete_job_cascade" \
        "## 🧪 Test
Delete job cascades to results

## 🔴→🟢 Status
- [ ] Test written (RED)
- [ ] Implementation
- [ ] Test passes (GREEN)" \
        "phase-1-database,test,tdd" \
        "Phase 1: Database Schema + Client"
      ;;
  esac
done

# Gate Issue
create_issue \
  "[Phase 1][🚦 GATE] Phase 1 Exit Criteria" \
  "## 🚦 Exit Criteria

### 📊 Tests (9 total)
- [ ] test_create_job ✅
- [ ] test_get_job_exists ✅
- [ ] test_get_job_not_found ✅
- [ ] test_update_job_status ✅
- [ ] test_update_job_progress ✅
- [ ] test_save_research_result ✅
- [ ] test_get_job_results ✅
- [ ] test_list_jobs_pagination ✅
- [ ] test_delete_job_cascade ✅

### 🧪 Run
\`\`\`bash
venv/bin/pytest tests/test_database.py -v
\`\`\`

### ✅ Expected
\`\`\`
======== 9 passed in 3.21s ========
\`\`\`

## 🚦 Status: ⏳ PENDING

Close when all tests pass!" \
  "phase-1-database,gate,tdd" \
  "Phase 1: Database Schema + Client"

echo "✅ Phase 1: Created 11 issues (9 tests + 1 implementation + 1 gate)"
