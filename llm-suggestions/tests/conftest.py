"""Shared test data for the llm-suggestions test suite."""

SAMPLE_TRANSACTIONS = [
	{
		"transaction_id": "ebf90783-868a-4980-97d3-9893231589b8",
		"timestamp": "2025-01-01 06:08",
		"merchant": "Orange Egypt",
		"category": "Services_and_Utilities",
		"amount": 676.10,
		"currency": "EGP",
		"type": "DEBIT",
		"note": "Subscription — twice_monthly",
	},
	{
		"transaction_id": "dfc2f190-8140-43e4-88e4-8935e0512007",
		"timestamp": "2025-01-01 07:11",
		"merchant": "Nile Taxi",
		"category": "Transportation",
		"amount": 40.63,
		"currency": "EGP",
		"type": "DEBIT",
		"note": "Morning commute",
	},
	{
		"transaction_id": "e5f6a7b8-0000-0000-0000-000000000005",
		"timestamp": "2025-01-05 09:00",
		"merchant": "Employer Co.",
		"category": "Salary",
		"amount": 15000.0,
		"currency": "EGP",
		"type": "CREDIT",
		"note": "Monthly salary",
	},
]
