"""
Integration tests for POST /v1/suggestions.
AI engine calls are mocked so these tests do not require a live API key.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.response import SuggestionsResponse
from tests.conftest import SAMPLE_TRANSACTIONS

client = TestClient(app)

MOCK_AI_RESPONSE = {
    "analysis_period": {
        "from": "2025-01-01",
        "to": "2025-01-02",
        "total_debits": 716.73,
        "total_credits": 12000.0,
        "net_cashflow": 11283.27,
        "currency": "EGP",
    },
    "spending_breakdown": [
        {
            "category": "Services_and_Utilities",
            "total": 676.10,
            "percentage_of_debits": 94.34,
            "transaction_count": 1,
        },
        {
            "category": "Transportation",
            "total": 40.63,
            "percentage_of_debits": 5.66,
            "transaction_count": 1,
        },
    ],
    "suggestions": [
        {
            "id": "sug_001",
            "priority": "HIGH",
            "type": "REDUCE",
            "title": "Review your Orange Egypt subscription",
            "body": (
                "Your Orange Egypt subscription charged EGP 676.10 twice this month. "
                "Reviewing your plan could save you meaningfully without disrupting connectivity."
            ),
            "estimated_monthly_saving_egp": 200.0,
            "affected_categories": ["Services_and_Utilities"],
            "action_label": "Review subscription plan",
        }
    ],
    "savings_potential": {
        "conservative_egp": 200.0,
        "moderate_egp": 400.0,
        "summary": "Small adjustments to utilities could unlock EGP 200–400 every month.",
    },
    "insight_of_the_day": {
        "text": "Your income comfortably covers your expenses — a great foundation to build on.",
        "icon_hint": "trend_up",
    },
}


def _auth_headers() -> dict[str, str]:
    from app.core.config import settings
    return {"Authorization": f"Bearer {settings.service_api_key}"}


@patch("app.services.ai_engine.generate_suggestions")
def test_suggestions_success(mock_generate: MagicMock) -> None:
    mock_generate.return_value = SuggestionsResponse.model_validate(MOCK_AI_RESPONSE)
    response = client.post(
        "/v1/suggestions",
        json={"transactions": SAMPLE_TRANSACTIONS},
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) >= 1
    assert data["suggestions"][0]["priority"] == "HIGH"


def test_suggestions_missing_auth() -> None:
    response = client.post("/v1/suggestions", json={"transactions": SAMPLE_TRANSACTIONS})
    assert response.status_code == 403  # HTTPBearer raises 403 when header absent


def test_suggestions_wrong_api_key() -> None:
    response = client.post(
        "/v1/suggestions",
        json={"transactions": SAMPLE_TRANSACTIONS},
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 401


def test_suggestions_empty_transactions() -> None:
    response = client.post(
        "/v1/suggestions",
        json={"transactions": []},
        headers=_auth_headers(),
    )
    assert response.status_code == 422


def test_suggestions_only_credits_rejected() -> None:
    credit_only = [
        {
            "transaction_id": "aaaa-0000-0000-0000-000000000001",
            "timestamp": "2025-01-01 10:00",
            "merchant": "Employer",
            "category": "Salary",
            "amount": 5000.0,
            "currency": "EGP",
            "type": "CREDIT",
            "note": None,
        }
    ]
    response = client.post(
        "/v1/suggestions",
        json={"transactions": credit_only},
        headers=_auth_headers(),
    )
    assert response.status_code == 422


def test_health_check() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
