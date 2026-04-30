# 🌙 Baseera LLM Suggestions Service

> **بصيرة** — See your money's future before it happens.

AI-powered financial suggestion engine for the Baseera budget tracker. Built for **Salam Hack 2026**.

---

## What it does

Accepts a list of pre-tagged bank transactions and returns structured, Sharia-compliant financial insights and saving suggestions.

## Stack

- **Python 3.11** + **FastAPI** + **Pydantic v2**
- **OpenRouter via OpenAI SDK**
- **pytest** for testing · **ruff** for linting · **mypy** for types
- **Docker** for containerized deployment

---

## Quick Start

### 1. Set up the environment

```bash
cd llm-suggestions
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and set at least:

- `OPENROUTER_API_KEY`
- `SERVICE_API_KEY`

The default OpenRouter model is `openai/gpt-4o-mini`.
`OPENROUTER_API_KEY` is what lets the service talk to OpenRouter. `SERVICE_API_KEY` is the local bearer token that the mock-data script sends to your FastAPI server.

### 2. Start the server

```bash
bash scripts/run_dev.sh
```

The script starts Uvicorn with reload enabled and serves the API at `http://localhost:8000`.
Open the interactive docs at `http://localhost:8000/docs`.
If you change `.env`, the dev server reloads automatically; if you are on an older run or a terminal without reload support, restart `bash scripts/run_dev.sh` once after updating keys.

### 3. Run the mock-data test

In a second terminal, from the same `llm-suggestions` directory, run:

```bash
python scripts/seed_mock_data.py --api-key change-me-before-deploy
```

That script posts the mock transactions defined in `scripts/seed_mock_data.py` to `POST /v1/suggestions` and prints the generated response.
### What to expect

- If `.env` is missing, `scripts/run_dev.sh` copies `.env.example` to `.env` and exits so you can fill in the keys.
- The server should log one `POST /suggestions` request and then return a JSON response.
- If the upstream model is slow or returns empty content, the service now falls back to a deterministic response instead of hanging.

---

## Testing

```bash
# Run all tests with coverage
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

---

## Manual Testing

If you already have the server running, you can re-run the mock data test any time with:

```bash
python scripts/seed_mock_data.py --api-key change-me-before-deploy
```

The `--api-key` value must match `SERVICE_API_KEY` from your `.env` file. It is separate from `OPENROUTER_API_KEY`, which stays inside the service and is never passed to the mock-data script.

For a full local smoke test, use the exact sequence above: start the server with `scripts/run_dev.sh`, then run the seed script in a second terminal.

## Shared-key development workflow

To reduce friction in development you can opt to use a single API token for both upstream calls and local service authentication. This is strictly a developer convenience and should not be used in production unless you fully understand the security implications.

- Enable the fallback behavior by setting `ALLOW_SHARED_API_KEY=true` in `.env` (or export it):

```bash
# In .env
ALLOW_SHARED_API_KEY=true

# Or export in your shell (temporary)
export ALLOW_SHARED_API_KEY=true
```

- With this enabled (or when `APP_ENV` != `production`) the service will accept `OPENROUTER_API_KEY` as the bearer token for local requests when `SERVICE_API_KEY` is not present.

- Recommended local sequence using a single token:

```bash
# Export a single token that will be used both for upstream and local auth in dev
export OPENROUTER_API_KEY="sk-or-..."
export ALLOW_SHARED_API_KEY=true

# Start the server (it will accept OPENROUTER_API_KEY as the local bearer)
bash scripts/run_dev.sh

# Send mock data (no need to pass --api-key if SERVICE_API_KEY is not set)
python scripts/seed_mock_data.py
```

Migration helper

If you'd rather copy the value from `OPENROUTER_API_KEY` into `SERVICE_API_KEY` in your `.env` once, use the included helper:

```bash
python scripts/migrate_shared_key.py    # prompts and writes .env (use --force to overwrite)
```

This helper updates `.env` safely (backing up the original), sets `ALLOW_SHARED_API_KEY=true`, and is intended for local convenience only.

The seed script now reads `.env` automatically, so after migration you can run `python scripts/seed_mock_data.py` without passing `--api-key` as long as `SERVICE_API_KEY` is present in `.env` or exported in your shell.

---

## Docker

```bash
docker compose up --build
```

---

## Project structure

```text
llm-suggestions/
├── app/
│   ├── api/v1/endpoints/     # FastAPI route handlers
│   ├── core/                 # Config, logging, exceptions
│   ├── models/               # Pydantic data contracts
│   ├── services/             # Business logic: AI engine, prompt builder, analyzer
│   └── utils/                # Validators, formatters
├── tests/
│   ├── unit/                 # Pure function tests (no I/O)
│   └── integration/          # HTTP-level tests (AI mocked)
├── scripts/                  # Dev helpers
├── docs/                     # Architecture & API reference
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Key design decisions

- **Prompt-as-code**: The system prompt lives in `prompt_builder.py` and is unit-tested — not buried in a config file.
- **Pre-processing before AI**: `transaction_analyzer.py` deduplicates and sorts data before it ever reaches the LLM, keeping the AI layer clean.
- **Schema-first responses**: The AI is instructed to return JSON that is immediately validated against Pydantic models — no loose string parsing.
- **Sharia-first design**: Islamic finance principles are baked into the model's identity, not bolted on as filters.

---

## Docs

- [`docs/architecture.md`](docs/architecture.md) — System design and data flow
- [`docs/api_reference.md`](docs/api_reference.md) — Full endpoint reference
