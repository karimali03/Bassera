import json
import sys
import os
from datetime import datetime
from bson import ObjectId

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lib.db import get_mongo_client

db = get_mongo_client()

BANK_ID = "BANK-KARIM-001"

# Insert bank record with transactions
with open("../Bank-API/generated_ledger.json") as f:
    transactions = json.load(f)

for t in transactions:
    t["timestamp"] = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M")

balance = sum(
    t["amount"] if t["type"] == "CREDIT" else -t["amount"]
    for t in transactions
)

db["banks"].delete_one({"bank_id": BANK_ID})
db["banks"].insert_one({
    "bank_id": BANK_ID,
    "balance": round(balance, 2),
    "transactions": transactions,
})
print(f"Inserted bank record with {len(transactions)} transactions (balance: {balance:.2f} EGP)")

# Insert user
db["users"].delete_one({"fname": "Karim", "lname": "Ali"})
result = db["users"].insert_one({
    "fname": "Karim",
    "lname": "Ali",
    "bank_id": BANK_ID,
    "ai_status": "NOT_STARTED",
    "ai_last_run": None,
    "ai_forecast_data": None,
})
print(f"Inserted user Karim Ali with _id={result.inserted_id}")
