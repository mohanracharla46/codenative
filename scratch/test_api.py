
import requests
import json

base_url = "http://127.0.0.1:5000" # Assuming it's running locally

try:
    # Try to fetch content for python introduction
    response = requests.get(f"{base_url}/api/content/python/introduction")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Could not connect: {e}")
