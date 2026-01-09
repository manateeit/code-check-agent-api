# Getting Started with Code Check Agent API

## What Was Created

A complete FastAPI service that converts your prototype into a production-ready API with:

✅ **Secure API Key Authentication** - Protect your service
✅ **Dual LLM Support** - OpenAI or Gemini
✅ **Smartsheet Integration** - Caller provides their token
✅ **Vercel Deployment Ready** - Full serverless configuration
✅ **Environment Variable Security** - All keys in Vercel Secrets
✅ **Comprehensive Documentation** - API docs, deployment guide

## Directory Structure

```
code_check_agent_api/
├── app/
│   ├── main.py              # FastAPI app with endpoints
│   ├── models.py            # Pydantic data models (from prototype)
│   ├── clients.py           # Perplexity & LLM clients (from prototype)
│   ├── agent.py             # Research logic (from prototype)
│   ├── smartsheet_exporter.py  # Export logic (enhanced)
│   ├── auth.py              # API key authentication
│   ├── config.py            # Environment configuration
│   └── schemas.py           # Request/response models
├── requirements.txt         # Dependencies
├── vercel.json             # Vercel deployment config
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # User guide
├── API.md                  # Technical API docs
├── DEPLOYMENT.md           # Vercel deployment guide
└── GETTING_STARTED.md      # This file
```

## Key Features

### 1. API Key Authentication

All research endpoints require `X-API-Key` header:

```bash
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: your-secure-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, State"}'
```

### 2. Smartsheet Token Per-Request

**Design:** Caller provides Smartsheet token in each request
- ✅ API never stores tokens
- ✅ Each user uses their own credentials
- ✅ Granular permission control

```json
{
  "address": "...",
  "smartsheet_access_token": "caller-provides-this",
  "workspace_name": "Code Research"
}
```

### 3. Secure Environment Variables

**In Vercel Secrets (not in code):**
- `API_KEY` - Your service authentication key
- `PERPLEXITY_API_KEY` - Perplexity API key
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Gemini API key (optional)

### 4. Two Endpoints

**`POST /research`**
- Research address, return JSON data
- No Smartsheet export

**`POST /research/smartsheet`**
- Research address, export to Smartsheet
- Returns data + Smartsheet link

## Quick Start (Local)

### 1. Install Dependencies

```bash
cd code_check_agent_api
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example
cp .env.example .env

# Edit .env and add:
# - API_KEY=your-secure-key-here
# - PERPLEXITY_API_KEY=pplx-xxx
# - OPENAI_API_KEY=sk-xxx
# - GEMINI_API_KEY=xxx (optional)
```

### 3. Run Locally

```bash
uvicorn app.main:app --reload
```

API available at: http://localhost:8000

**Interactive docs at:** http://localhost:8000/docs

### 4. Test

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Research (with auth)
curl -X POST "http://localhost:8000/research" \
  -H "X-API-Key: your-key-from-env" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "401 Biscayne Blvd, Miami, FL",
    "llm_provider": "openai"
  }'
```

## Deploy to Vercel

### Prerequisites

- Vercel account (Pro tier required for production)
- Vercel CLI: `npm install -g vercel`

### Quick Deploy

```bash
# 1. Login
vercel login

# 2. Add secrets
vercel secrets add api_key "$(openssl rand -base64 32)"
vercel secrets add perplexity_api_key "pplx-xxx"
vercel secrets add openai_api_key "sk-xxx"
vercel secrets add gemini_api_key "xxx"  # optional

# 3. Deploy
vercel --prod
```

**Your API is live!** 🎉

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps.

## API Endpoints

### 🏠 GET `/` - API Info
No authentication required

### ❤️ GET `/health` - Health Check
No authentication required

Returns:
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

### 🔍 POST `/research` - Research Address

**Requires:** `X-API-Key` header

**Request:**
```json
{
  "address": "123 Main St, Springfield, IL 62701",
  "llm_provider": "openai"  // or "gemini"
}
```

**Response:** Full CodeCheckForm with all researched data

**Duration:** 2-3 minutes

### 📊 POST `/research/smartsheet` - Research & Export

**Requires:** `X-API-Key` header

**Request:**
```json
{
  "address": "123 Main St, Springfield, IL",
  "llm_provider": "openai",
  "smartsheet_access_token": "your-smartsheet-token",
  "workspace_name": "Code Research",
  "workspace_id": null  // optional
}
```

**Response:**
```json
{
  "research_data": { /* Full CodeCheckForm */ },
  "smartsheet": {
    "sheet_url": "https://app.smartsheet.com/sheets/...",
    "sheet_id": 1234567890,
    "rows_created": 156
  }
}
```

**Duration:** 2.5-3.5 minutes

## Integration Example

### Python

```python
import requests

API_URL = "https://your-api.vercel.app"
API_KEY = "your-api-key"

# Research address
response = requests.post(
    f"{API_URL}/research",
    headers={"X-API-Key": API_KEY},
    json={
        "address": "401 Biscayne Blvd, Miami, FL",
        "llm_provider": "openai"
    }
)

data = response.json()
print(f"Jurisdiction: {data['location_information']['jurisdiction']['value']}")

# Research and export to Smartsheet
response = requests.post(
    f"{API_URL}/research/smartsheet",
    headers={"X-API-Key": API_KEY},
    json={
        "address": "123 Main St, Springfield, IL",
        "smartsheet_access_token": "your-smartsheet-token",
        "workspace_name": "Code Research"
    }
)

result = response.json()
print(f"Sheet URL: {result['smartsheet']['sheet_url']}")
```

### JavaScript/TypeScript

```javascript
const API_URL = "https://your-api.vercel.app";
const API_KEY = "your-api-key";

async function researchAddress(address) {
  const response = await fetch(`${API_URL}/research`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      address: address,
      llm_provider: "openai"
    })
  });

  const data = await response.json();
  console.log(`Jurisdiction: ${data.location_information.jurisdiction.value}`);
  return data;
}

// Usage
researchAddress("789 Oak Ave, Austin, TX");
```

## Security Best Practices

### 🔐 API Key Management

1. **Generate strong keys:**
   ```bash
   openssl rand -base64 32
   ```

2. **Store in Vercel Secrets:**
   ```bash
   vercel secrets add api_key "your-key"
   ```

3. **Never commit to git:**
   - `.env` is in `.gitignore`
   - Use `.env.example` as template

4. **Rotate regularly:**
   - Update key quarterly
   - Redeploy after rotation

### 🔑 Smartsheet Token Security

**Caller provides token per-request:**
- API doesn't store tokens
- Each user manages their own credentials
- Tokens not logged or exposed

**Get Smartsheet token:**
1. https://app.smartsheet.com/account/apps
2. Create "API Access Token"
3. Grant "Create sheets" permission
4. Copy token (shown once)

## Cost Estimates

### Vercel Hosting
- **Free Tier:** $0/month (10s timeout - not sufficient)
- **Pro Tier:** $20/month (300s timeout - **required**)

### API Usage (per research)
- Perplexity: $0.65
- OpenAI: $0.26
- Gemini: $0.07
- **Total:** $0.91 (OpenAI) or $0.72 (Gemini)

### Monthly (100 requests)
- Vercel Pro: $20
- API usage: $91 (OpenAI) or $72 (Gemini)
- **Total:** ~$111/month (OpenAI) or ~$92/month (Gemini)

## Performance

- **Request Duration:** 2-3 minutes
- **Perplexity Rate Limit:** 20 requests/minute
- **OpenAI Rate Limit:** 5,000 requests/minute
- **Gemini Rate Limit:** 2 requests/minute (free tier)

**Recommendation:** Use Gemini for cost savings (30% cheaper)

## Troubleshooting

### "Invalid API key"
- Check `X-API-Key` header
- Verify secret in Vercel: `vercel secrets ls`

### "OpenAI API key not configured"
- Add secret: `vercel secrets add openai_api_key "sk-xxx"`
- Redeploy: `vercel --prod`

### Request times out
- Upgrade to Vercel Pro (300s timeout)
- Free tier has 10s timeout (too short)

### Empty research results
- Verify address is valid and public
- Include full address with city, state, zip
- Check if address in unincorporated area

## Documentation

- **README.md** - User guide and quick reference
- **API.md** - Technical API documentation
- **DEPLOYMENT.md** - Step-by-step Vercel deployment
- **GETTING_STARTED.md** - This file

**Interactive API Docs:**
- Swagger UI: `https://your-api.vercel.app/docs`
- ReDoc: `https://your-api.vercel.app/redoc`

## Differences from Prototype

| Feature | Prototype | API Service |
|---------|-----------|-------------|
| **Interface** | CLI (`python main.py`) | HTTP API (POST /research) |
| **Authentication** | None | API key required |
| **Deployment** | Local only | Vercel serverless |
| **Smartsheet Token** | In `.env` file | Provided per-request |
| **Configuration** | `.env` file | Vercel Secrets |
| **Output** | JSON to stdout | HTTP JSON response |
| **Documentation** | README only | Full API docs + Swagger |

## Next Steps

1. **Deploy to Vercel** (see DEPLOYMENT.md)
2. **Test with real addresses**
3. **Integrate into your application**
4. **Set up monitoring** (health checks)
5. **Configure custom domain** (optional)
6. **Implement rate limiting** (optional)

## Support

**Questions?**
- Check API docs: `/docs` endpoint
- Review technical docs: `API.md`
- Deployment issues: `DEPLOYMENT.md`

**Issues?**
- Verify `/health` endpoint
- Check Vercel logs: `vercel logs`
- Test with cURL before client code

---

## Quick Commands Reference

```bash
# Local development
uvicorn app.main:app --reload

# Deploy to Vercel
vercel --prod

# View logs
vercel logs --follow

# Test health
curl https://your-api.vercel.app/health

# Test research
curl -X POST "https://your-api.vercel.app/research" \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, State"}'
```

---

**Ready to deploy?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

**Need help?** Check [API.md](./API.md) for complete technical documentation.
