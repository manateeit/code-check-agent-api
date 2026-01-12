# Phase 3: Background Workers with Modal

## 🎯 Goal
Integrate Modal for async background job processing. Jobs submitted via POST /jobs should trigger Modal workers that execute the research agent and update job status in real-time.

## 📋 Architecture

```
User → POST /jobs → FastAPI → Modal.Function.spawn() → Returns job_id
                                    ↓
                            Modal Worker Starts
                                    ↓
                        Run CodeCheckAgent.run()
                                    ↓
                    Update job status (processing)
                                    ↓
                    Save section results as completed
                                    ↓
                Update job status (completed/failed)
                                    ↓
                        (Optional: Webhook callback)
```

## 🔧 Implementation Components

### 1. Modal Function (`modal_worker.py`)
- Serverless function deployed to Modal
- Receives: job_id, address, llm_provider
- Executes: CodeCheckAgent.run()
- Updates: Job status via Supabase client

### 2. Updated POST /jobs Endpoint
- Create job record (status: pending)
- Spawn Modal function asynchronously
- Return job_id immediately (don't wait)

### 3. Worker Job Processing
- Update status to "processing"
- Execute 13-section research
- Save each section result to DB
- Update progress: "1/13", "2/13", etc.
- Final status: "completed" or "failed"

### 4. Environment Configuration
- Modal requires authentication: `modal token new`
- Modal app name: `code-check-worker`
- Secrets stored in Modal (Supabase, API keys)

## 🧪 Testing Strategy

### Challenge: Modal Testing
Modal functions run in the cloud, making local testing difficult. Strategy:

1. **Unit Tests**: Test worker logic locally without Modal
2. **Integration Tests**: Mock Modal.Function.spawn()
3. **Manual Tests**: Deploy to Modal and test end-to-end

### Test Files
- `tests/test_modal_worker.py` - Worker logic tests (local)
- `tests/test_modal_integration.py` - Integration tests (mocked)

## 📁 File Structure

```
app/
├── main.py              # Updated: POST /jobs triggers Modal
├── job_routes.py        # Updated: Spawn Modal worker
├── modal_worker.py      # NEW: Modal function definition
└── worker_logic.py      # NEW: Extracted worker logic (testable)

tests/
├── test_modal_worker.py       # NEW: Unit tests for worker logic
└── test_modal_integration.py  # NEW: Integration tests
```

## 🔐 Modal Configuration

### Secrets Required (Modal Dashboard)
```python
# Add via: modal secret create code-check-secrets
SUPABASE_URL=https://project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...  # Optional
```

### Modal App Deployment
```bash
# Deploy Modal function
modal deploy app/modal_worker.py

# Test locally
modal run app/modal_worker.py::test_job
```

## 🚀 Implementation Steps

### Step 1: Extract Worker Logic (Testable)
Create `app/worker_logic.py`:
- `process_job(job_id, address, llm_provider)` - Pure function
- No Modal dependencies
- Fully unit testable

### Step 2: Create Modal Function
Create `app/modal_worker.py`:
- Import worker_logic
- Define Modal app and secrets
- Create `@app.function()` wrapper
- Handle job execution + error handling

### Step 3: Update POST /jobs
In `app/job_routes.py`:
- After creating job, spawn Modal function
- Don't wait for completion
- Return job_id immediately

### Step 4: Write Tests
- Test worker logic locally
- Mock Modal.spawn() in integration tests
- Verify job status updates

## 📊 Expected Job Flow

```
1. POST /jobs → Job created (status: pending) → Returns job_id
2. Modal worker starts → Status: processing
3. Research section 1 → Save to DB → Progress: "1/13"
4. Research section 2 → Save to DB → Progress: "2/13"
   ...
5. Research section 13 → Save to DB → Progress: "13/13"
6. Final status → Status: completed
```

## 🚦 Phase 3 Gate Criteria

- ✅ Modal function deployed and accessible
- ✅ POST /jobs triggers async worker
- ✅ Job status updates to "processing"
- ✅ Section results saved incrementally
- ✅ Final status set to "completed" or "failed"
- ✅ Unit tests pass for worker logic
- ✅ Integration tests pass (mocked Modal)
- ✅ Manual end-to-end test successful

## 🔍 Debugging Strategy

**Local Testing (Without Modal)**:
```python
# Test worker logic directly
from app.worker_logic import process_job
result = process_job(job_id, address, llm_provider)
```

**Modal Logs**:
```bash
# View Modal function logs
modal app logs code-check-worker

# View specific function call
modal function logs code-check-worker.process_research_job
```

## ⏱️ Estimated Timeline

- **Worker Logic Extraction**: 20 minutes
- **Modal Function Creation**: 30 minutes
- **Endpoint Update**: 15 minutes
- **Testing**: 45 minutes
- **Deployment + Manual Test**: 30 minutes
- **Total**: ~2.5 hours

## 📝 Notes

- Modal free tier: 30 free credits/month (sufficient for testing)
- Cold start: ~1-2 seconds for Modal function
- Warm start: ~100ms after first invocation
- Timeout: Set to 300 seconds (5 minutes) for research
- Concurrency: Modal handles automatically
- No need for webhook initially (can poll status)

## 🚨 Important Considerations

1. **Error Handling**: Modal function must catch all errors and set job status to "failed"
2. **Idempotency**: Worker should check if job already processed
3. **Secrets**: Never hardcode API keys in Modal function
4. **Progress Updates**: Update progress frequently for better UX
5. **Database Connections**: Use Supabase client directly (not pooled)

## 🔗 Resources

- Modal Docs: https://modal.com/docs
- Modal Python SDK: https://modal.com/docs/reference/modal
- Modal Secrets: https://modal.com/docs/guide/secrets
