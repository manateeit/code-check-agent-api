# Code Check Agent API - Technical Documentation

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
│                    (Your App/Frontend/Script)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS + X-API-Key
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Service (Vercel)                    │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────────┐ │
│  │   Auth     │  │  Research   │  │  Smartsheet Export       │ │
│  │ Middleware │→ │  Endpoints  │→ │  Endpoints               │ │
│  └────────────┘  └─────────────┘  └──────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      ┌──────────────┐ ┌─────────┐ ┌─────────────────┐
      │  Perplexity  │ │ OpenAI  │ │   Smartsheet    │
      │     API      │ │ / Gemini│ │      API        │
      │   (sonar-    │ │ (gpt-4o/│ │  (Sheet Export) │
      │    pro)      │ │  1.5-pro)│ │                 │
      └──────────────┘ └─────────┘ └─────────────────┘
           Research      Extraction     Organization
```

### Request Flow

1. **Authentication Layer**
   - Client sends request with `X-API-Key` header
   - `verify_api_key()` validates against `API_KEY` env var
   - Invalid key → 401 Unauthorized
   - Valid key → proceed to endpoint

2. **Research Orchestration**
   - `CodeCheckAgent` initialized with LLM provider
   - Step 1: Jurisdiction research (Perplexity → LLM)
   - Steps 2-13: Section research (12 sign regulation categories)
   - Each step: Perplexity search → append citations → LLM extraction

3. **Data Extraction**
   - Perplexity returns content + citations
   - Citations appended to content for LLM context
   - LLM extracts structured data using Pydantic schema
   - Every field maps to source URL from citations

4. **Optional Export**
   - Smartsheet client initialized with caller's token
   - Workspace/folder hierarchy created (State → City)
   - Sheet created with 5 columns
   - Rows batched and inserted

---

## API Reference

### Base URL

**Local:** `http://localhost:8000`
**Production:** `https://your-project.vercel.app`

### Authentication

**Method:** API Key in header
**Header:** `X-API-Key: your-api-key`
**Location:** All `/research*` endpoints
**Error:** 401 Unauthorized if missing/invalid

---

## Endpoints

### 1. Root Information

**Endpoint:** `GET /`

**Description:** API metadata and documentation links

**Authentication:** None

**Response:**
```json
{
  "name": "Code Check API",
  "version": "1.0.0",
  "description": "AI-powered zoning and sign code research API",
  "docs": "/docs",
  "health": "/health"
}
```

**Status Codes:**
- `200 OK` - Always succeeds

---

### 2. Health Check

**Endpoint:** `GET /health`

**Description:** Service health and dependency status

**Authentication:** None

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "perplexity": true,
    "openai": true,
    "gemini": false
  }
}
```

**Status Codes:**
- `200 OK` - Service operational

**Notes:**
- `services` shows which LLM providers are configured
- `true` = API key present, `false` = not configured
- Does NOT validate API keys (no external calls)

---

### 3. Research Address

**Endpoint:** `POST /research`

**Description:** Research zoning and sign codes for US address

**Authentication:** Required (`X-API-Key`)

**Request Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "address": "401 Biscayne Blvd, Miami, FL 33132",
  "llm_provider": "openai"
}
```

**Request Schema:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| address | string | ✅ Yes | - | Full US address with city, state |
| llm_provider | string | ❌ No | "openai" | LLM provider: "openai" or "gemini" |

**Response:** Full `CodeCheckForm` object (see Data Models section)

**Status Codes:**
- `200 OK` - Research completed successfully
- `400 Bad Request` - Invalid request (bad llm_provider)
- `401 Unauthorized` - Invalid API key
- `500 Internal Server Error` - Research failed

**Error Responses:**
```json
{
  "error": "Invalid llm_provider. Must be 'openai' or 'gemini'"
}
```

```json
{
  "error": "Research failed: Perplexity API error"
}
```

**Example cURL:**
```bash
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: abc123xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Springfield, IL 62701",
    "llm_provider": "openai"
  }'
```

**Performance:**
- Duration: 2-3 minutes
- Cost: ~$0.91 (OpenAI) or ~$0.72 (Gemini)

---

### 4. Research & Export to Smartsheet

**Endpoint:** `POST /research/smartsheet`

**Description:** Research address and export to Smartsheet workspace

**Authentication:** Required (`X-API-Key`)

**Request Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "address": "401 Biscayne Blvd, Miami, FL 33132",
  "llm_provider": "openai",
  "smartsheet_access_token": "your-smartsheet-token-here",
  "workspace_name": "Code Research",
  "workspace_id": null
}
```

**Request Schema:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| address | string | ✅ Yes | - | Full US address |
| llm_provider | string | ❌ No | "openai" | LLM provider |
| smartsheet_access_token | string | ✅ Yes | - | Smartsheet API token (from caller) |
| workspace_name | string | ❌ No | "Code Research" | Smartsheet workspace name |
| workspace_id | integer | ❌ No | null | Pre-defined workspace ID (skip lookup) |

**Response:**
```json
{
  "research_data": {
    "form_name": "Code Check Form",
    "location_information": { ... },
    "wall_signs": { ... },
    ...
  },
  "smartsheet": {
    "sheet_url": "https://app.smartsheet.com/sheets/xyz123",
    "sheet_id": 1234567890,
    "rows_created": 156
  }
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| research_data | object | Full CodeCheckForm (same as /research) |
| smartsheet.sheet_url | string | Direct link to created Smartsheet |
| smartsheet.sheet_id | integer | Smartsheet ID for programmatic access |
| smartsheet.rows_created | integer | Number of rows inserted |

**Status Codes:**
- `200 OK` - Research and export successful
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Invalid API key
- `500 Internal Server Error` - Research or export failed

**Error Responses:**
```json
{
  "error": "Workspace 'Code Research' not found and no workspace_id provided"
}
```

```json
{
  "error": "Research or export failed: Invalid Smartsheet token"
}
```

**Example cURL:**
```bash
curl -X POST "https://your-api.vercel.app/research/smartsheet" \
  -H "X-API-Key: abc123xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "789 Oak Ave, Austin, TX 78701",
    "llm_provider": "gemini",
    "smartsheet_access_token": "xxxxxxxxxxxx",
    "workspace_name": "Code Research"
  }'
```

**Performance:**
- Duration: 2.5-3.5 minutes
- Cost: Same as /research + Smartsheet API calls (free)

---

## Data Models

### CodeCheckForm (Response Model)

Complete research form with 13 sections:

```typescript
{
  form_name: string,
  location_information: LocationInformation,
  wall_signs: WallSigns,
  projecting_signs: ProjectingSigns,
  freestanding_signs: FreestandingSigns,
  directionals_regulatory: DirectionalsRegulatory,
  informational_signs: InformationalSigns,
  awnings: Awnings,
  undercanopy_signs: UndercanopySigns,
  window_signs: WindowSigns,
  temporary_signs: TemporarySigns,
  approval_process: ApprovalProcess,
  permit_requirements: PermitRequirements,
  variance_procedures: VarianceProcedures
}
```

### ResearchedField<T>

Every data field uses this wrapper:

```typescript
{
  value: T | null,              // The actual data
  source_url: string | null,    // Citation URL
  source_quote: string | null,  // Relevant quote
  notes: string | null          // Additional context
}
```

**Example:**
```json
{
  "maximum_sf_allowed": {
    "value": 200,
    "source_url": "https://library.municode.com/fl/miami/codes/code_of_ordinances?nodeId=...",
    "source_quote": null,
    "notes": null
  }
}
```

### Section Details

Each section contains 5-20 ResearchedField attributes. See `models.py` for complete schemas.

**Example Section (WallSigns):**
```json
{
  "wall_signs_allowed": {
    "value": true,
    "source_url": "https://...",
    "source_quote": null,
    "notes": null
  },
  "maximum_sf_allowed": {
    "value": 200,
    "source_url": "https://...",
    "source_quote": null,
    "notes": null
  },
  "illumination_restrictions": {
    "value": "Internal illumination permitted",
    "source_url": "https://...",
    "source_quote": null,
    "notes": null
  }
}
```

---

## Security

### API Key Authentication

**Implementation:**
- API key validated via `verify_api_key()` dependency
- Checked against `settings.api_key` from environment
- Constant-time comparison to prevent timing attacks

**Best Practices:**
1. Use strong, random keys (32+ characters)
2. Rotate keys quarterly
3. Never commit keys to version control
4. Use Vercel Secrets for production
5. Implement rate limiting (optional)

**Key Generation:**
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(api_key)  # Use this as your API_KEY
```

### Smartsheet Token Security

**Design Decision:** Caller provides token per-request
- ✅ API never stores Smartsheet credentials
- ✅ Each client uses their own token
- ✅ Tokens not logged or persisted
- ✅ Granular permission control

**Token Requirements:**
- Permission: "Create sheets"
- Scope: Specific workspace (recommended)
- Expiration: Set token expiration in Smartsheet

**Get Token:**
1. Go to https://app.smartsheet.com/account/apps
2. Create new API access token
3. Copy token (shown once)
4. Grant "Create sheets" permission

### Environment Variable Security

**Vercel Secrets:** Encrypted at rest
**Access:** Only available during function execution
**Visibility:** Not exposed in logs or error messages

**Setting Secrets:**
```bash
vercel secrets add api_key "$(openssl rand -base64 32)"
vercel secrets add perplexity_api_key "pplx-xxx"
vercel secrets add openai_api_key "sk-xxx"
```

### CORS Configuration

**Current:** Allows all origins (`allow_origins=["*"]`)

**Production Recommendation:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["POST"],  # Only allow POST
    allow_headers=["X-API-Key", "Content-Type"],
)
```

---

## Rate Limiting

### Current Implementation

No rate limiting implemented (unlimited requests per key).

### Recommended Implementation

```python
# Install: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/research")
@limiter.limit("10/hour")  # 10 requests per hour per IP
async def research_address(...):
    ...
```

### External Rate Limits

**Perplexity:** 20 requests/minute
- Current: 13 sequential requests per address = safe
- Parallel research: Would exceed limit

**OpenAI:** 5,000 requests/minute (Tier 1)
- No concern for current usage

**Gemini:** 2 requests/minute (Free tier)
- Could bottleneck if parallel research implemented

**Smartsheet:** 300 requests/minute
- Batch row insertion = 1 request per export = safe

---

## Error Handling

### Error Response Format

All errors return consistent JSON:

```json
{
  "error": "Human-readable error message",
  "detail": "Optional technical details"
}
```

### HTTP Status Codes

| Code | Meaning | Cause |
|------|---------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing/invalid API key |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Internal Server Error | Server-side failure |

### Common Errors

**401 - Invalid API Key**
```json
{
  "error": "Invalid API key"
}
```
**Solution:** Check `X-API-Key` header matches `API_KEY` env var

**400 - Invalid LLM Provider**
```json
{
  "error": "Invalid llm_provider. Must be 'openai' or 'gemini'"
}
```
**Solution:** Use "openai" or "gemini" for `llm_provider` field

**500 - LLM Not Configured**
```json
{
  "error": "OpenAI API key not configured"
}
```
**Solution:** Add `OPENAI_API_KEY` to Vercel secrets

**500 - Research Failed**
```json
{
  "error": "Research failed: Perplexity API error",
  "detail": "429 Too Many Requests"
}
```
**Solution:** Wait 1 minute (rate limit), retry

**500 - Smartsheet Export Failed**
```json
{
  "error": "Research or export failed: Invalid Smartsheet token"
}
```
**Solution:** Verify Smartsheet token is valid and has permissions

### Error Handling Best Practices

**Client-Side:**
1. Check status code before parsing JSON
2. Display `error` field to user
3. Log `detail` for debugging
4. Implement exponential backoff for 500 errors

**Example:**
```javascript
const response = await fetch('/research', {
  method: 'POST',
  headers: {
    'X-API-Key': apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ address: '...' })
});

if (!response.ok) {
  const error = await response.json();
  console.error('API Error:', error.detail);
  alert(`Error: ${error.error}`);
  return;
}

const data = await response.json();
// Process data
```

---

## Performance Optimization

### Request Duration

**Breakdown:**
- Jurisdiction research: 10-15 seconds
- Section research (×12): 8-12 seconds each
- Smartsheet export: 3-5 seconds
- **Total:** 2-3.5 minutes

### Cost Per Request

**Research Only:**
- Perplexity: 13 queries × $0.05 = $0.65
- OpenAI (gpt-4o): 13 extractions × $0.02 = $0.26
- Gemini (1.5-pro): 13 extractions × $0.005 = $0.07
- **Total:** $0.91 (OpenAI) or $0.72 (Gemini)

**With Smartsheet Export:**
- Smartsheet API: Free
- **Total:** Same as above

### Optimization Strategies

**1. Use Gemini for Cost**
```json
{
  "llm_provider": "gemini"  // 30% cheaper
}
```

**2. Cache Jurisdiction Data**
If researching multiple addresses in same city:
```python
# Pseudo-code
jurisdiction_cache = {}
if city in jurisdiction_cache:
    location_info = jurisdiction_cache[city]
else:
    location_info = agent.research_jurisdiction(address)
    jurisdiction_cache[city] = location_info
```

**3. Parallel Section Research (Advanced)**
⚠️ Requires rate limit handling:
```python
import asyncio

async def research_sections_parallel():
    tasks = [research_section(name, model) for name, model in sections]
    results = await asyncio.gather(*tasks)
    return results
```

**Trade-offs:**
- ✅ 10x faster (2-3 min → 15-20 sec)
- ❌ Risk exceeding Perplexity rate limit (20/min)
- ❌ Higher concurrent costs

---

## Deployment

### Vercel Deployment Steps

**1. Initial Setup**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project (from code_check_agent_api/ directory)
vercel link
```

**2. Add Secrets**
```bash
# Required secrets
vercel secrets add api_key "$(openssl rand -base64 32)"
vercel secrets add perplexity_api_key "pplx-xxxxxxx"
vercel secrets add openai_api_key "sk-xxxxxxx"

# Optional (if using Gemini)
vercel secrets add gemini_api_key "xxxxxxx"
```

**3. Deploy**
```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

**4. Verify**
```bash
# Get deployment URL
vercel ls

# Test health check
curl https://your-project.vercel.app/health

# Test research (with your API key)
curl -X POST "https://your-project.vercel.app/research" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, State"}'
```

### Vercel Configuration

**vercel.json:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "API_KEY": "@api_key",
    "PERPLEXITY_API_KEY": "@perplexity_api_key",
    "OPENAI_API_KEY": "@openai_api_key",
    "GEMINI_API_KEY": "@gemini_api_key",
    "DEFAULT_LLM_PROVIDER": "openai"
  }
}
```

**Key Points:**
- `@` prefix references Vercel Secrets
- `DEFAULT_LLM_PROVIDER` can be set directly (not secret)
- All routes point to `app/main.py` (FastAPI app)

### Vercel Limits

**Free Tier:**
- Function timeout: 10 seconds (❌ Too short for research)
- Execution time: 100 GB-hours/month
- Deployments: Unlimited

**Pro Tier (Required):**
- Function timeout: 300 seconds (✅ Enough for research)
- Execution time: 1000 GB-hours/month
- Cost: $20/month

**Recommendation:** Use Pro tier for production

### Custom Domain

```bash
# Add domain
vercel domains add yourdomain.com

# Configure DNS (follow Vercel instructions)

# Access API at:
# https://api.yourdomain.com/research
```

---

## Monitoring & Logging

### Vercel Logs

**View Logs:**
```bash
# Real-time logs
vercel logs --follow

# Logs from specific deployment
vercel logs <deployment-url>

# Filter by function
vercel logs --output=raw | grep "research_address"
```

**Log Format:**
```
2024-01-15T10:30:45.123Z POST /research 200 125.4s
```

### Health Monitoring

**Automated Health Checks:**
```bash
# Cron job (every 5 minutes)
*/5 * * * * curl -s https://your-api.vercel.app/health | jq '.status'

# Uptime monitoring service
# Use: UptimeRobot, Pingdom, StatusCake, etc.
```

**Alerting:**
```bash
# Email alert if down
*/5 * * * * curl -f https://your-api.vercel.app/health || \
  echo "API is down!" | mail -s "API Alert" admin@example.com
```

### Application Logging

**Structured Logging (Optional Enhancement):**
```python
import logging
import json

logger = logging.getLogger(__name__)

@app.post("/research")
async def research_address(request: ResearchRequest):
    logger.info(json.dumps({
        "event": "research_started",
        "address": request.address,
        "llm_provider": request.llm_provider
    }))

    result = agent.run(request.address)

    logger.info(json.dumps({
        "event": "research_completed",
        "address": request.address,
        "sections_researched": 13
    }))

    return result
```

### Metrics Tracking

**Key Metrics to Track:**
1. Request count per hour/day
2. Average response time
3. Error rate (4xx, 5xx)
4. Cost per request (API usage)
5. Top addresses researched

**Example Analytics:**
```python
# Store in external service (e.g., PostHog, Mixpanel)
analytics.track("research_completed", {
    "address": request.address,
    "llm_provider": request.llm_provider,
    "duration_seconds": duration,
    "cost_usd": estimated_cost
})
```

---

## Testing

### Local Testing

**1. Start Local Server:**
```bash
uvicorn app.main:app --reload
```

**2. Test Health Check:**
```bash
curl http://localhost:8000/health
```

**3. Test Research (with valid API key):**
```bash
curl -X POST "http://localhost:8000/research" \
  -H "X-API-Key: your-local-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "401 Biscayne Blvd, Miami, FL",
    "llm_provider": "openai"
  }' | jq '.'
```

**4. Test Smartsheet Export:**
```bash
curl -X POST "http://localhost:8000/research/smartsheet" \
  -H "X-API-Key: your-local-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Springfield, IL",
    "llm_provider": "openai",
    "smartsheet_access_token": "your-smartsheet-token",
    "workspace_name": "Code Research"
  }' | jq '.smartsheet'
```

### Production Testing

```bash
# Health check
curl https://your-api.vercel.app/health

# Research (with production API key)
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: production-api-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "789 Oak Ave, Austin, TX"}'
```

### Unit Testing (Optional)

**pytest Example:**
```python
# tests/test_agent.py
import pytest
from unittest.mock import patch
from app.agent import CodeCheckAgent

@patch('app.clients.PerplexityClient.search')
@patch('app.clients.LLMClient.extract_data')
def test_research_jurisdiction(mock_extract, mock_search):
    mock_search.return_value = {
        "content": "Miami, FL is the jurisdiction",
        "citations": ["https://example.com"]
    }
    mock_extract.return_value = LocationInformation(
        jurisdiction=ResearchedField(value="Miami")
    )

    agent = CodeCheckAgent("openai")
    result = agent.research_jurisdiction("401 Biscayne Blvd, Miami, FL")

    assert result.jurisdiction.value == "Miami"
```

**Run Tests:**
```bash
pytest tests/ -v
```

---

## Integration Examples

### Python Client

```python
import requests
import json

class CodeCheckClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def research(self, address: str, llm_provider: str = "openai"):
        response = requests.post(
            f"{self.api_url}/research",
            headers=self.headers,
            json={"address": address, "llm_provider": llm_provider}
        )
        response.raise_for_status()
        return response.json()

    def research_and_export(self, address: str, smartsheet_token: str):
        response = requests.post(
            f"{self.api_url}/research/smartsheet",
            headers=self.headers,
            json={
                "address": address,
                "smartsheet_access_token": smartsheet_token,
                "workspace_name": "Code Research"
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CodeCheckClient(
    api_url="https://your-api.vercel.app",
    api_key="your-api-key"
)

result = client.research("123 Main St, Springfield, IL")
print(f"Jurisdiction: {result['location_information']['jurisdiction']['value']}")
```

### JavaScript/TypeScript Client

```typescript
interface ResearchRequest {
  address: string;
  llm_provider?: 'openai' | 'gemini';
}

interface CodeCheckForm {
  form_name: string;
  location_information: any;
  // ... other sections
}

class CodeCheckClient {
  constructor(
    private apiUrl: string,
    private apiKey: string
  ) {}

  async research(request: ResearchRequest): Promise<CodeCheckForm> {
    const response = await fetch(`${this.apiUrl}/research`, {
      method: 'POST',
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    return response.json();
  }

  async researchAndExport(
    address: string,
    smartsheetToken: string
  ): Promise<any> {
    const response = await fetch(`${this.apiUrl}/research/smartsheet`, {
      method: 'POST',
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        address,
        smartsheet_access_token: smartsheetToken,
        workspace_name: 'Code Research'
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    return response.json();
  }
}

// Usage
const client = new CodeCheckClient(
  'https://your-api.vercel.app',
  'your-api-key'
);

const result = await client.research({
  address: '789 Oak Ave, Austin, TX',
  llm_provider: 'gemini'
});

console.log(`Jurisdiction: ${result.location_information.jurisdiction.value}`);
```

### cURL Batch Processing

```bash
#!/bin/bash
# batch_research.sh

API_URL="https://your-api.vercel.app"
API_KEY="your-api-key"
ADDRESSES_FILE="addresses.txt"

while IFS= read -r address; do
  echo "Researching: $address"

  curl -X POST "$API_URL/research" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"address\": \"$address\", \"llm_provider\": \"gemini\"}" \
    -o "output_$(echo "$address" | tr ' ' '_').json"

  echo "Completed: $address"
  sleep 60  # Rate limiting: 1 per minute
done < "$ADDRESSES_FILE"
```

**addresses.txt:**
```
401 Biscayne Blvd, Miami, FL
123 Main St, Springfield, IL
789 Oak Ave, Austin, TX
```

---

## Troubleshooting

### Common Issues

**Issue: Request times out on Vercel**
- **Cause:** Free tier has 10s timeout, research takes 2-3 min
- **Solution:** Upgrade to Vercel Pro ($20/month) for 300s timeout

**Issue: "Invalid API key" even with correct key**
- **Cause:** Vercel secret not properly linked
- **Solution:** Verify `vercel.json` has `"API_KEY": "@api_key"` and secret exists: `vercel secrets ls`

**Issue: "OpenAI API key not configured"**
- **Cause:** `OPENAI_API_KEY` not in Vercel secrets
- **Solution:** `vercel secrets add openai_api_key "sk-xxx"` and redeploy

**Issue: Empty results (all fields null)**
- **Cause:** Perplexity couldn't find relevant information
- **Solution:** Verify address is valid, include zip code, check if address is in unincorporated area

**Issue: Smartsheet export fails with 401**
- **Cause:** Invalid Smartsheet token or insufficient permissions
- **Solution:** Regenerate token at https://app.smartsheet.com/account/apps with "Create sheets" permission

**Issue: CORS error from browser**
- **Cause:** Frontend on different domain
- **Solution:** Update `allow_origins` in `app/main.py` to include your domain

### Debug Mode

Enable detailed logging:

```python
# app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/research")
async def research_address(request: ResearchRequest):
    logging.debug(f"Request: {request}")
    # ... rest of code
```

### Support

For issues:
1. Check `/health` endpoint
2. Review Vercel logs: `vercel logs`
3. Verify API keys are valid
4. Test with cURL to isolate client issues
5. Check rate limits (Perplexity: 20/min)

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- FastAPI-based API service
- API key authentication
- Dual LLM support (OpenAI, Gemini)
- Smartsheet integration
- Vercel deployment configuration
- Comprehensive documentation

---

## Future Enhancements

### Planned Features

1. **Parallel Section Research** (v1.1)
   - 10x speed improvement
   - Requires rate limit handling

2. **Caching Layer** (v1.2)
   - Redis/Upstash integration
   - Cache jurisdiction data per city
   - 50% cost reduction for repeat cities

3. **Webhook Notifications** (v1.3)
   - Callback URL on completion
   - Async processing
   - No timeout concerns

4. **Batch Endpoint** (v1.4)
   - Submit multiple addresses
   - Process in background
   - Status polling endpoint

5. **Rate Limiting** (v1.5)
   - Per-key limits
   - Tiered pricing support

### Contribution Guidelines

To contribute:
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

---

## License

[Your License Here]

## Contact

[Your Contact Information Here]
