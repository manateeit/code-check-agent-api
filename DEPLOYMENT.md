# Vercel Deployment Guide

Step-by-step guide to deploy Code Check Agent API to Vercel.

## Prerequisites

- Vercel account (free or pro)
- Vercel CLI installed
- API keys ready:
  - Perplexity API key
  - OpenAI API key
  - Gemini API key (optional)

## Step 1: Prepare API Keys

### Generate Secure API Key

```bash
# Generate a strong API key for your service
openssl rand -base64 32
# Example output: 8xKpP9vR3mN2wQ5tY7uI0oL4jH6gF1dS8aZ3xC9vB5n=
```

**Save this key** - you'll use it to authenticate requests to your API.

### Get AI Service Keys

1. **Perplexity API Key** (Required)
   - Go to: https://www.perplexity.ai/settings/api
   - Create API key
   - Copy: `pplx-xxxxxxxxxxxxxxxx`

2. **OpenAI API Key** (Required for OpenAI provider)
   - Go to: https://platform.openai.com/api-keys
   - Create API key
   - Copy: `sk-xxxxxxxxxxxxxxxx`

3. **Gemini API Key** (Optional, for Gemini provider)
   - Go to: https://aistudio.google.com/app/apikey
   - Create API key
   - Copy: `xxxxxxxxxxxxxxxx`

## Step 2: Install Vercel CLI

```bash
# Install globally
npm install -g vercel

# Or use with npx (no install required)
npx vercel
```

## Step 3: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate via email or GitHub.

## Step 4: Link Project

```bash
# Navigate to project directory
cd /path/to/code_check_agent_api

# Link to Vercel
vercel link
```

Answer the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Choose your account/team
- **Link to existing project?** No (first time)
- **Project name?** code-check-agent-api (or your choice)

## Step 5: Add Secrets to Vercel

```bash
# Add your service API key
vercel secrets add api_key "8xKpP9vR3mN2wQ5tY7uI0oL4jH6gF1dS8aZ3xC9vB5n="

# Add Perplexity API key (required)
vercel secrets add perplexity_api_key "pplx-xxxxxxxxxxxxxxxx"

# Add OpenAI API key (required for openai provider)
vercel secrets add openai_api_key "sk-xxxxxxxxxxxxxxxx"

# Add Gemini API key (optional, for gemini provider)
vercel secrets add gemini_api_key "xxxxxxxxxxxxxxxx"
```

**Verify secrets were added:**
```bash
vercel secrets ls
```

You should see:
```
api_key
perplexity_api_key
openai_api_key
gemini_api_key
```

## Step 6: Deploy to Preview

```bash
# Deploy to preview environment
vercel
```

This creates a preview deployment at: `https://code-check-agent-api-xxxxx.vercel.app`

**Test the preview deployment:**
```bash
# Get the preview URL from the output
PREVIEW_URL="https://code-check-agent-api-xxxxx.vercel.app"

# Test health check
curl $PREVIEW_URL/health

# Test research endpoint (use your API key)
curl -X POST "$PREVIEW_URL/research" \
  -H "X-API-Key: 8xKpP9vR3mN2wQ5tY7uI0oL4jH6gF1dS8aZ3xC9vB5n=" \
  -H "Content-Type: application/json" \
  -d '{"address": "401 Biscayne Blvd, Miami, FL 33132"}'
```

## Step 7: Deploy to Production

Once preview testing is successful:

```bash
# Deploy to production
vercel --prod
```

Your production API is now available at: `https://code-check-agent-api.vercel.app`

## Step 8: Verify Production Deployment

```bash
# Set production URL
PROD_URL="https://code-check-agent-api.vercel.app"

# Test health check (no auth required)
curl $PROD_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "services": {
#     "perplexity": true,
#     "openai": true,
#     "gemini": true
#   }
# }
```

## Step 9: Test Full Research Flow

```bash
# Test research endpoint (takes 2-3 minutes)
curl -X POST "$PROD_URL/research" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Springfield, IL 62701",
    "llm_provider": "openai"
  }' | jq '.location_information.jurisdiction'

# Expected output:
# {
#   "value": "City of Springfield",
#   "source_url": "https://...",
#   "source_quote": null,
#   "notes": null
# }
```

## Step 10: Configure Custom Domain (Optional)

### Add Domain

```bash
# Add your custom domain
vercel domains add api.yourdomain.com
```

### Configure DNS

Vercel will provide DNS records to add to your domain registrar:

1. **CNAME Record:**
   - Name: `api`
   - Value: `cname.vercel-dns.com`

2. Wait for DNS propagation (5-60 minutes)

3. **Test custom domain:**
```bash
curl https://api.yourdomain.com/health
```

## Troubleshooting

### Issue: "Secret not found"

**Symptom:**
```
Error: Secret "api_key" not found
```

**Solution:**
```bash
# List all secrets
vercel secrets ls

# If missing, add it
vercel secrets add api_key "your-key-here"

# Redeploy
vercel --prod
```

### Issue: "Function timeout"

**Symptom:**
```
Error: Function execution timed out after 10s
```

**Cause:** Free tier has 10-second timeout, research takes 2-3 minutes.

**Solution:** Upgrade to Vercel Pro ($20/month) for 300-second timeout:
1. Go to: https://vercel.com/account/billing
2. Upgrade to Pro
3. Redeploy: `vercel --prod`

### Issue: "OPENAI_API_KEY not configured"

**Symptom:**
```json
{
  "error": "OpenAI API key not configured"
}
```

**Solution:**
```bash
# Verify secret exists
vercel secrets ls | grep openai

# If missing, add it
vercel secrets add openai_api_key "sk-xxxxxxxx"

# Redeploy
vercel --prod
```

### Issue: CORS errors from browser

**Symptom:**
```
Access to fetch at 'https://...' from origin 'https://yourdomain.com'
has been blocked by CORS policy
```

**Solution:** Update CORS settings in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["X-API-Key", "Content-Type"],
)
```

Then redeploy: `vercel --prod`

## Monitoring & Logs

### View Deployment Logs

```bash
# Real-time logs
vercel logs --follow

# Logs from specific deployment
vercel logs https://code-check-agent-api-xxxxx.vercel.app

# Filter by function
vercel logs | grep "research_address"
```

### Dashboard

Access the Vercel dashboard:
- https://vercel.com/dashboard
- View deployments, logs, analytics

## Updating the API

### Deploy Changes

```bash
# 1. Make changes to code
# 2. Test locally:
uvicorn app.main:app --reload

# 3. Deploy to preview
vercel

# 4. Test preview deployment
curl https://preview-url.vercel.app/health

# 5. Deploy to production
vercel --prod
```

### Rollback Deployment

```bash
# List recent deployments
vercel ls

# Promote a previous deployment to production
vercel promote <deployment-url>
```

## Security Checklist

- ✅ API key is strong (32+ characters)
- ✅ API key stored in Vercel Secrets (not in code)
- ✅ All AI service keys in Vercel Secrets
- ✅ `.env` file in `.gitignore`
- ✅ CORS configured for production domains only
- ✅ Vercel Pro tier enabled (for production)
- ✅ Custom domain with HTTPS (optional)

## Cost Estimates

### Vercel Costs
- **Free Tier:** $0/month (10s timeout - not sufficient)
- **Pro Tier:** $20/month (300s timeout - required)

### API Usage Costs (per research request)
- **Perplexity:** ~$0.65 (13 queries)
- **OpenAI:** ~$0.26 (13 extractions)
- **Gemini:** ~$0.07 (13 extractions)
- **Total:** ~$0.91 (OpenAI) or ~$0.72 (Gemini)

**Monthly estimate (100 requests):**
- Vercel Pro: $20
- API usage: $91 (OpenAI) or $72 (Gemini)
- **Total:** $111/month (OpenAI) or $92/month (Gemini)

## Next Steps

1. **Test thoroughly** with various addresses
2. **Set up monitoring** (health checks, uptime)
3. **Implement rate limiting** (optional)
4. **Create client SDKs** (Python, JavaScript)
5. **Document API** for your team
6. **Set up CI/CD** (optional, GitHub Actions)

## Support

For deployment issues:
- Vercel Docs: https://vercel.com/docs
- Vercel Support: https://vercel.com/support

For API issues:
- Check `/health` endpoint
- Review Vercel logs: `vercel logs`
- Verify API keys are configured
- Test with cURL to isolate issues

## Quick Reference

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs --follow

# List deployments
vercel ls

# List secrets
vercel secrets ls

# Add secret
vercel secrets add key_name "value"

# Remove secret
vercel secrets rm key_name

# Rollback
vercel promote <deployment-url>
```

---

**Deployment Complete!** 🎉

Your API is now live at: `https://your-project.vercel.app`

Save your API key securely and share it with authorized users.
