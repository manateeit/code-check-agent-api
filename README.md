# Code Check Agent API

A secure FastAPI service for researching zoning and sign codes using AI. Designed for Vercel deployment with API key authentication.

## Features

- 🔐 **Secure API Key Authentication** - Protect your service with X-API-Key header
- 🤖 **Dual LLM Support** - Choose between OpenAI (gpt-4o) or Gemini (1.5-pro)
- 🔍 **Comprehensive Research** - 13 sections of sign code regulations with source citations
- 📊 **Smartsheet Integration** - Direct export to organized Smartsheet workspaces
- ☁️ **Vercel Ready** - Optimized for serverless deployment
- 🔒 **Secure Secrets** - API keys managed via Vercel environment variables

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Add your keys to .env:
# - API_KEY (your service API key)
# - PERPLEXITY_API_KEY
# - OPENAI_API_KEY
# - GEMINI_API_KEY (optional)

# Run locally
uvicorn app.main:app --reload

# API available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

### 2. Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Add secrets (one-time setup)
vercel secrets add api_key "your-secure-api-key"
vercel secrets add perplexity_api_key "pplx-xxxxxxx"
vercel secrets add openai_api_key "sk-xxxxxxx"
vercel secrets add gemini_api_key "xxxxxxx"  # optional

# Deploy
vercel --prod
```

Your API will be available at: `https://your-project.vercel.app`

## API Endpoints

### 🏠 Root - API Info
```bash
GET /
```
Returns API name, version, and documentation links. No authentication required.

### ❤️ Health Check
```bash
GET /health
```
Verify service status and dependency availability. No authentication required.

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

### 🔍 Research Address
```bash
POST /research
```
Research zoning and sign codes for a US address.

**Headers:**
```
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "address": "401 Biscayne Blvd, Miami, FL 33132",
  "llm_provider": "openai"
}
```

**Response:**
```json
{
  "form_name": "Code Check Form",
  "location_information": {
    "jurisdiction": {
      "value": "City of Miami",
      "source_url": "https://library.municode.com/...",
      "notes": null
    },
    ...
  },
  "wall_signs": { ... },
  "projecting_signs": { ... },
  ...
}
```

### 📊 Research & Export to Smartsheet
```bash
POST /research/smartsheet
```
Research address and export directly to Smartsheet.

**Headers:**
```
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "address": "401 Biscayne Blvd, Miami, FL 33132",
  "llm_provider": "openai",
  "smartsheet_access_token": "your-smartsheet-token",
  "workspace_name": "Code Research",
  "workspace_id": null
}
```

**Response:**
```json
{
  "research_data": { ... },
  "smartsheet": {
    "sheet_url": "https://app.smartsheet.com/sheets/...",
    "sheet_id": 1234567890,
    "rows_created": 156
  }
}
```

## Authentication

All `/research*` endpoints require authentication via the `X-API-Key` header.

**Example:**
```bash
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: your-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Springfield, IL"}'
```

**Error Response (401):**
```json
{
  "error": "Invalid API key"
}
```

## Configuration

### Environment Variables

**Required:**
- `API_KEY` - Your service API key for authentication
- `PERPLEXITY_API_KEY` - Perplexity API key for research
- `OPENAI_API_KEY` - OpenAI API key (if using openai provider)

**Optional:**
- `GEMINI_API_KEY` - Google Gemini API key (if using gemini provider)
- `DEFAULT_LLM_PROVIDER` - Default provider (default: "openai")
- `API_TITLE` - API title (default: "Code Check API")
- `API_VERSION` - API version (default: "1.0.0")

### Vercel Secrets Management

```bash
# Add a secret
vercel secrets add secret_name "secret_value"

# List secrets
vercel secrets ls

# Remove a secret
vercel secrets rm secret_name
```

Secrets are referenced in `vercel.json` with `@` prefix (e.g., `@api_key`).

## LLM Provider Selection

Choose between two providers:

### OpenAI (gpt-4o)
- ✅ Better structured output
- ✅ More reliable extraction
- ✅ Faster inference
- 💰 Higher cost (~$0.26 per address)

### Gemini (1.5-pro)
- ✅ Larger context window
- ✅ Lower cost (~$0.07 per address)
- ✅ Multimodal capabilities
- ⚠️ Slightly less deterministic

**Usage:**
```json
{
  "address": "...",
  "llm_provider": "gemini"  // or "openai"
}
```

## Smartsheet Integration

### Requirements

1. Smartsheet API access token (get from: https://app.smartsheet.com/account/apps)
2. Workspace named "Code Research" (or custom name)
3. Token must have "Create sheets" permission

### Folder Structure

```
Workspace: Code Research
├── Florida/
│   ├── Miami/
│   │   └── 401 Biscayne Blvd (Sheet)
│   └── Tampa/
│       └── 123 Main St (Sheet)
└── Illinois/
    └── Springfield/
        └── 789 Oak Ave (Sheet)
```

### Sheet Format

| Section | Field | Value | Source URL | Notes |
|---------|-------|-------|------------|-------|
| Location Info | Jurisdiction | City of Miami | [link] | |
| Wall Signs | Maximum Sf Allowed | 200 | [link] | |

### Passing Smartsheet Credentials

**Option 1: Per-Request (Recommended)**
```json
{
  "address": "...",
  "smartsheet_access_token": "your-token-here",
  "workspace_name": "Code Research"
}
```

**Option 2: Pre-defined Workspace ID**
```json
{
  "address": "...",
  "smartsheet_access_token": "your-token-here",
  "workspace_id": 1234567890
}
```

## Error Handling

### Common Errors

**401 Unauthorized**
```json
{
  "error": "Invalid API key"
}
```
**Solution:** Check your X-API-Key header

**400 Bad Request**
```json
{
  "error": "Invalid llm_provider. Must be 'openai' or 'gemini'"
}
```
**Solution:** Use "openai" or "gemini" for llm_provider

**500 Internal Server Error**
```json
{
  "error": "OpenAI API key not configured"
}
```
**Solution:** Add OPENAI_API_KEY to Vercel secrets

## Security Best Practices

### 🔒 API Key Protection

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use Vercel Secrets** - Store keys securely in Vercel
3. **Rotate keys regularly** - Update API_KEY periodically
4. **Restrict CORS** - Update `allow_origins` in production

### 🔑 Smartsheet Token Security

1. **Never log tokens** - Tokens are not logged in API
2. **Use per-request tokens** - Caller provides token, API doesn't store
3. **Limit token permissions** - Only grant "Create sheets" permission
4. **Token rotation** - Regenerate Smartsheet tokens regularly

### 🛡️ Rate Limiting

Consider adding rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/research")
@limiter.limit("10/hour")  # 10 requests per hour
async def research_address(...):
    ...
```

## Performance

### Request Duration
- Research only: **2-3 minutes** per address
- Research + Smartsheet: **2.5-3.5 minutes** per address

### Cost Estimates (per address)
- Perplexity: $0.65 (13 queries)
- OpenAI: $0.26 (13 extractions)
- Gemini: $0.07 (13 extractions)
- **Total**: $0.91 (OpenAI) or $0.72 (Gemini)

### Optimization Tips

1. **Use Gemini for cost** - 30% cheaper than OpenAI
2. **Cache jurisdiction data** - Reuse for same city
3. **Batch requests** - Process multiple addresses sequentially
4. **Monitor rate limits** - Perplexity: 20 req/min

## Testing

### Local Testing

```bash
# Health check
curl http://localhost:8000/health

# Research (local)
curl -X POST "http://localhost:8000/research" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "401 Biscayne Blvd, Miami, FL 33132",
    "llm_provider": "openai"
  }'
```

### Production Testing

```bash
# Health check
curl https://your-api.vercel.app/health

# Research (production)
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: your-production-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Springfield, IL",
    "llm_provider": "gemini"
  }'
```

## Monitoring

### Vercel Logs

```bash
# View deployment logs
vercel logs

# View function logs
vercel logs --follow
```

### Health Monitoring

Set up automated health checks:

```bash
# Cron job (every 5 minutes)
*/5 * * * * curl https://your-api.vercel.app/health
```

## Troubleshooting

### Issue: "Invalid API key"
**Cause:** X-API-Key header missing or incorrect
**Solution:** Add header: `-H "X-API-Key: your-key"`

### Issue: "OpenAI API key not configured"
**Cause:** OPENAI_API_KEY not in Vercel secrets
**Solution:** `vercel secrets add openai_api_key "sk-xxx"`

### Issue: Timeout on Vercel
**Cause:** Free tier has 10s timeout, research takes 2-3 minutes
**Solution:** Upgrade to Pro plan (300s timeout)

### Issue: "Workspace 'Code Research' not found"
**Cause:** Workspace doesn't exist in Smartsheet
**Solution:** Create workspace or pass `workspace_id`

## Development

### Project Structure

```
code_check_agent_api/
├── app/
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic data models
│   ├── clients.py           # Perplexity & LLM clients
│   ├── agent.py             # Research orchestration
│   ├── smartsheet_exporter.py  # Smartsheet export logic
│   ├── auth.py              # API key authentication
│   ├── config.py            # Settings & environment
│   └── schemas.py           # Request/response schemas
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
├── .env.example            # Environment template
└── README.md               # This file
```

### Adding New Endpoints

```python
@app.post("/your-endpoint", dependencies=[Depends(verify_api_key)])
async def your_handler(request: YourSchema):
    # Your logic here
    return {"result": "data"}
```

### Custom Authentication

Replace `verify_api_key` in `app/auth.py`:

```python
async def verify_api_key(api_key: str = Security(api_key_header)):
    # Custom validation logic
    if not is_valid(api_key):
        raise HTTPException(status_code=401, detail="Invalid")
    return api_key
```

## Support & Documentation

- **API Docs (Swagger):** `/docs`
- **API Docs (ReDoc):** `/redoc`
- **Health Check:** `/health`
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com

## License

[Your License Here]

## Contact

[Your Contact Info Here]
