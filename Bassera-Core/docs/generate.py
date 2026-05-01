import os
import sys
import json

# Ensure the root directory is accessible so we can import the api module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import app

def generate_openapi_json():
    os.makedirs('docs', exist_ok=True)
    
    # Get the generated OpenAPI schema from the FastAPI app
    openapi_schema = app.openapi()
    
    # Convert and write to JSON
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)
        
    print("Successfully generated docs/openapi.json")

if __name__ == "__main__":
    generate_openapi_json()
