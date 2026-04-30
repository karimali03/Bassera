#!/usr/bin/env bash
set -e

echo "🌙 Starting Baseera AI Service (dev mode)..."

if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Edit .env and set OPENROUTER_API_KEY and SERVICE_API_KEY before re-running."
    exit 1
fi

# Check for OPENROUTER_API_KEY either in the environment or in the .env file
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    if ! grep -qE "^OPENROUTER_API_KEY\s*=" .env >/dev/null 2>&1; then
        echo "❗ OPENROUTER_API_KEY is not set in environment or .env."
        echo "Set OPENROUTER_API_KEY in your shell or edit .env and re-run."
        exit 1
    fi
fi

# Check for SERVICE_API_KEY (used to authenticate local requests)
if [ -z "${SERVICE_API_KEY:-}" ]; then
    allow_shared=false
    if grep -qE "^ALLOW_SHARED_API_KEY\s*=\s*true" .env >/dev/null 2>&1; then
        allow_shared=true
    elif [ "${APP_ENV:-development}" != "production" ]; then
        allow_shared=true
    fi

    if [ "$allow_shared" = true ]; then
        # Allow falling back to OPENROUTER_API_KEY in dev or when explicitly enabled
        if [ -n "${OPENROUTER_API_KEY:-}" ] || grep -qE "^OPENROUTER_API_KEY\s*=" .env >/dev/null 2>&1; then
            echo "⚠️ SERVICE_API_KEY not set — falling back to OPENROUTER_API_KEY for local auth (dev mode or ALLOW_SHARED_API_KEY=true)."
        else
            echo "❗ SERVICE_API_KEY is not set and no OPENROUTER_API_KEY found to fall back to."
            echo "Set SERVICE_API_KEY in your shell or edit .env and re-run."
            exit 1
        fi
    else
        if ! grep -qE "^SERVICE_API_KEY\s*=" .env >/dev/null 2>&1; then
            echo "❗ SERVICE_API_KEY is not set in environment or .env."
            echo "Set SERVICE_API_KEY in your shell or edit .env and re-run."
            exit 1
        fi
    fi
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-include ".env" --log-level info
