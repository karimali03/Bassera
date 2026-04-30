# Baseera LLM Suggestions Service — Architecture

## Overview

The Baseera LLM Suggestions Service is a **Python FastAPI microservice** that sits between the Baseera frontend and the LLM API. It accepts raw transaction data, pre-processes it, constructs a deterministic prompt, calls OpenRouter, validates and returns structured suggestions.

```text
Frontend (Lovable)
      │
      │  POST /v1/suggestions
      │  Authorization: Bearer <key>
      ▼
┌─────────────────────────────────────────┐
│           FastAPI Application           │
│                                         │
│  ┌─────────────┐   ┌─────────────────┐  │
│  │  /v1/health │   │ /v1/suggestions │  │
│  └─────────────┘   └────────┬────────┘  │
│                             │           │
│                    ┌────────▼────────┐  │
│                    │  transaction_   │  │
│                    │  analyzer.py    │  │
│                    │  (preprocess)   │  │
│                    └────────┬────────┘  │
│                             │           │
│                    ┌────────▼────────┐  │
│                    │ prompt_builder  │  │
│                    │ .py             │  │
│                    └────────┬────────┘  │
│                             │           │
│                    ┌────────▼────────┐  │
│                    │  ai_engine.py   │  │
│                    │ (OpenAI SDK)    │  │
│                    └────────┬────────┘  │
└─────────────────────────────┼───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  OpenRouter API    │
                    │ openai/gpt-4o-mini │
                    └────────────────────┘
```

## Layer Responsibilities

| Layer | File | Responsibility |
| --- | --- | --- |
| **API** | `app/api/v1/endpoints/suggestions.py` | HTTP handling, auth, error mapping |
| **Pre-processing** | `app/services/transaction_analyzer.py` | Dedup, sort, validate — no AI |
| **Prompt assembly** | `app/services/prompt_builder.py` | System prompt + user message serialization |
| **AI call** | `app/services/ai_engine.py` | OpenRouter SDK call, JSON parsing, schema validation |
| **Models** | `app/models/` | Pydantic v2 data contracts for I/O |
| **Config** | `app/core/config.py` | Env-driven settings via pydantic-settings |

## Data Flow

1. `POST /v1/suggestions` receives a JSON body with a `transactions` array.
2. Pydantic validates the request against `SuggestionsRequest`.
3. `transaction_analyzer.preprocess()` deduplicates and sorts the list.
4. `prompt_builder.build_user_message()` serializes transactions to JSON string.
5. `ai_engine.generate_suggestions()` sends system prompt + user message to OpenRouter.
6. The model returns a raw JSON string.
7. The response is parsed and validated against `SuggestionsResponse`.
8. The validated object is returned to the frontend as JSON.

## Error Handling Strategy

| Error source | Exception | HTTP status |
| --- | --- | --- |
| Bad request body | Pydantic `ValidationError` | 422 |
| Only CREDIT transactions | `ValueError` from model validator | 422 |
| OpenRouter API failure | `AIEngineError` | 502 |
| Unparseable AI response | `AIResponseParseError` | 502 |
| Wrong/missing API key | `HTTPException` | 401 / 403 |
