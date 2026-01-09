# API Architecture - Dual AI System

## ✅ Correct Implementation - Two-Phase Approach

Your API **DOES** use both Perplexity and OpenAI/Gemini, each for their specialized task.

### 🎯 The Two-Phase Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  API Request                                                 │
│  POST /research                                              │
│  { "address": "...", "llm_provider": "openai" }             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  CodeCheckAgent.__init__()                                   │
│                                                              │
│  self.perplexity = PerplexityClient()     ◄── ALWAYS used  │
│  self.llm = LLMClient("openai")           ◄── User's choice │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  For Each Section (×13)      │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: Research (Perplexity - ALWAYS)                    │
│                                                              │
│  result = self.perplexity.search(query)                     │
│    ↓                                                         │
│  Returns:                                                    │
│    - Raw text from web search                               │
│    - Citation URLs                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Extraction (OpenAI/Gemini - User Choice)          │
│                                                              │
│  return self.llm.extract_data(                              │
│      content=perplexity_result,                             │
│      schema=WallSigns,                                      │
│      instructions="Extract..."                              │
│  )                                                           │
│    ↓                                                         │
│  Returns:                                                    │
│    - Structured Pydantic model                              │
│    - Fields mapped to source URLs                           │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Code Evidence

### Agent Initialization (app/agent.py:24-26)

```python
def __init__(self, llm_provider: str = "openai"):
    self.perplexity = PerplexityClient()      # ← ALWAYS initialized
    self.llm = LLMClient(provider=llm_provider)  # ← User chooses this
```

### Research Flow (app/agent.py:42, 52)

```python
# Phase 1: Perplexity searches
result = self.perplexity.search(query)  # ← Line 42

# Phase 2: LLM extracts
return self.llm.extract_data(full_content, LocationInformation, ...)  # ← Line 52
```

## 🔑 What `llm_provider` Parameter Controls

**It does NOT mean "only use this LLM"**

It means: **"Which LLM should extract data from Perplexity's research?"**

### Request Example:

```json
{
  "address": "401 Biscayne Blvd, Miami, FL",
  "llm_provider": "openai"
}
```

**What happens:**

1. ✅ **Perplexity** searches the web (13 queries)
2. ✅ **OpenAI** extracts structured data from Perplexity's results (13 extractions)

### Alternative Request:

```json
{
  "address": "401 Biscayne Blvd, Miami, FL",
  "llm_provider": "gemini"
}
```

**What happens:**

1. ✅ **Perplexity** searches the web (13 queries) ← Same as above
2. ✅ **Gemini** extracts structured data from Perplexity's results (13 extractions) ← Different extractor

## 💰 Cost Breakdown Per Request

### With OpenAI:
- **Perplexity** (research): 13 queries × $0.05 = **$0.65**
- **OpenAI** (extraction): 13 extractions × $0.02 = **$0.26**
- **Total:** **$0.91**

### With Gemini:
- **Perplexity** (research): 13 queries × $0.05 = **$0.65**
- **Gemini** (extraction): 13 extractions × $0.005 = **$0.07**
- **Total:** **$0.72** (20% cheaper)

## 🎯 Why This Architecture?

### Perplexity's Strengths:
✅ Real-time web search with citations
✅ Finds current, official government sources
✅ Returns raw text + source URLs

### OpenAI/Gemini's Strengths:
✅ Excellent at structured data extraction
✅ Maps fields to source citations
✅ Handles complex nested models (Pydantic)

## 🔍 Verification

You can trace this in the logs when the API runs:

```
[Research Phase - Perplexity]
Searching: "What are the wall sign regulations for 401 Biscayne Blvd..."
← Returns raw text + citations

[Extraction Phase - OpenAI/Gemini]
Extracting structured data using gpt-4o...
← Returns WallSigns Pydantic model
```

## ✅ Summary

**Your API correctly implements the dual-AI architecture:**

1. 🔍 **Perplexity** = Research & Search (always used)
2. 🧠 **OpenAI/Gemini** = Data Extraction (user's choice)

The `llm_provider` parameter lets users choose which extraction engine to use, **NOT** which research engine (Perplexity is always used for research).

This matches your original prototype design exactly! ✨
