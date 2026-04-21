import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_headers():
    gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
    if not gemini_api_key:
        print("GEMINI_API_KEY not found in .env")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    payload = {
        "contents": [{"parts": [{"text": "hi"}]}]
    }
    
    try:
        resp = requests.post(url, json=payload)
        print(f"Status Code: {resp.status_code}")
        print("Headers:")
        for k, v in resp.headers.items():
            if 'ratelimit' in k.lower():
                print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_headers()
