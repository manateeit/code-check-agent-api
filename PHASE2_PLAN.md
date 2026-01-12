# Phase 2: API Endpoints Implementation Plan

## 🎯 Goal
Create FastAPI endpoints for async job management with comprehensive test coverage.

## 📋 TDD Approach

### RED Phase (Write Failing Tests)
Write 8 tests that define the API contract:
1. `test_submit_job` - POST /jobs with address
2. `test_submit_job_validation` - POST /jobs with invalid data
3. `test_get_job_status` - GET /jobs/{job_id}
4. `test_get_job_not_found` - GET /jobs/{invalid_id}
5. `test_get_job_results` - GET /jobs/{job_id}/results
6. `test_list_jobs` - GET /jobs with pagination
7. `test_delete_job` - DELETE /jobs/{job_id}
8. `test_api_key_required` - Authentication check

### GREEN Phase (Implement)
1. Create Pydantic schemas for request/response
2. Implement 5 FastAPI endpoints
3. Add API key authentication
4. Make all tests pass

## 🔧 API Design

### Endpoint 1: Submit Job
```
POST /jobs
Headers: X-API-Key: <key>
Body: {
  "address": "123 Main St, Miami, FL",
  "llm_provider": "openai"  // optional, default: "openai"
}

Response 201: {
  "job_id": "uuid",
  "status": "pending",
  "address": "123 Main St, Miami, FL",
  "llm_provider": "openai",
  "progress": "0/13 sections",
  "created_at": "2026-01-12T10:30:00Z"
}
```

### Endpoint 2: Get Job Status
```
GET /jobs/{job_id}
Headers: X-API-Key: <key>

Response 200: {
  "job_id": "uuid",
  "status": "processing",  // pending, processing, completed, failed, cancelled
  "address": "123 Main St, Miami, FL",
  "llm_provider": "openai",
  "progress": "5/13 sections",
  "created_at": "2026-01-12T10:30:00Z",
  "started_at": "2026-01-12T10:30:15Z",
  "completed_at": null,
  "error_message": null
}

Response 404: {
  "detail": "Job not found"
}
```

### Endpoint 3: Get Job Results
```
GET /jobs/{job_id}/results
Headers: X-API-Key: <key>

Response 200: {
  "job_id": "uuid",
  "status": "completed",
  "sections": [
    {
      "section_name": "location_information",
      "section_data": { ... },
      "created_at": "2026-01-12T10:31:00Z"
    },
    ...
  ]
}

Response 400: {
  "detail": "Job not completed yet. Current status: processing"
}
```

### Endpoint 4: List Jobs
```
GET /jobs?limit=50&offset=0
Headers: X-API-Key: <key>

Response 200: {
  "jobs": [
    {
      "job_id": "uuid",
      "status": "completed",
      "address": "123 Main St",
      "created_at": "2026-01-12T10:30:00Z"
    },
    ...
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Endpoint 5: Delete Job
```
DELETE /jobs/{job_id}
Headers: X-API-Key: <key>

Response 204: (no content)

Response 404: {
  "detail": "Job not found"
}
```

## 📁 File Structure

```
app/
├── main.py           # FastAPI app initialization (EXISTING)
├── db.py             # Database client (EXISTING - Phase 1)
├── routers/
│   └── jobs.py       # NEW - Job endpoints
├── schemas/
│   └── jobs.py       # NEW - Pydantic models
└── middleware/
    └── auth.py       # NEW - API key authentication

tests/
├── test_setup.py     # Phase 0 tests (EXISTING)
├── test_database.py  # Phase 1 tests (EXISTING)
└── test_api.py       # NEW - Phase 2 API tests
```

## 🔐 Authentication

Simple API key authentication:
- Header: `X-API-Key: <key>`
- Key stored in environment: `API_KEY=your-secret-key`
- Middleware checks header on all endpoints
- Returns 401 if missing/invalid

## 🧪 Test Strategy

Using `httpx.AsyncClient` for testing:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    return {"X-API-Key": os.getenv("API_KEY")}
```

## ⏱️ Estimated Timeline

- **RED Phase**: 30 minutes (write 8 tests)
- **GREEN Phase**: 60 minutes (implement endpoints)
- **Testing & Fixes**: 30 minutes
- **Total**: ~2 hours

## 🚦 Gate Criteria

Phase 2 is complete when:
- ✅ All 8 API tests pass
- ✅ All Phase 0 tests still pass (no regression)
- ✅ All Phase 1 tests still pass (no regression)
- ✅ API documentation auto-generated (FastAPI /docs)
- ✅ Code committed to Git

## 📝 Notes

- Keep endpoints simple - no background processing yet (Phase 3)
- Jobs stay in "pending" status (Modal workers in Phase 3)
- Focus on API contract and error handling
- Use existing `JobDB` class from Phase 1
