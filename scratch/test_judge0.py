import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_judge0():
    url = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true"
    api_key = os.environ.get("JUDGE0_API_KEY")
    api_host = os.environ.get("JUDGE0_API_HOST")

    print(f"Testing with Key: {api_key[:5]}...{api_key[-5:]}")
    print(f"Host: {api_host}")

    code = 'print("Hello from Judge0!")'
    encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    payload = {
        "language_id": 71,  # Python
        "source_code": encoded_code,
        "stdin": ""
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print("Result:", result)
        
        stdout = base64.b64decode(result.get("stdout") or "").decode("utf-8") if result.get("stdout") else "No Stdout"
        print("Decoded Stdout:", stdout)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_judge0()
