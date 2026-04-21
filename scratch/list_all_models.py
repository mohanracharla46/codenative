import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_models():
    gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
    if not gemini_api_key:
        print("GEMINI_API_KEY not found in .env")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_api_key}"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            for m in models:
                if 'generateContent' in m['supportedGenerationMethods']:
                    print(m['name'])
        else:
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
