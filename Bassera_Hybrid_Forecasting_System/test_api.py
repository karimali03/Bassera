import json
import requests

# 1. Load the huge list of transactions
with open('data/generated_ledger.json', 'r') as f:
    ledger = json.load(f)

# 2. Wrap it in the payload structure the API expects
payload = {
    "starting_balance": 250000,
    "horizon_days": 60,
    "transactions": ledger
}

# 3. Send to your live Hugging Face Space
print("Sending data to Hugging Face...")
url = 'https://mo7amed20o03-bassera-hybrid-forecasting-system.hf.space/analyze'
response = requests.post(url, json=payload)

# 4. Save the results
if response.status_code == 200:
    with open('outputs/live_api_response.json', 'w') as f:
        json.dump(response.json(), f, indent=2)
    print("Success! Saved to outputs/live_api_response.json")
else:
    print(f"Error {response.status_code}: {response.text}")
