import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("TESTING CURRENT API KEY")
print("=" * 60)

if not api_key:
    print("❌ No API key found!")
    exit(1)

print(f"\nAPI Key: {api_key[:30]}...")
print(f"Testing with gpt-4o-mini...\n")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
}

try:
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API KEY IS WORKING!")
        result = response.json()
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ ERROR!")
        error = response.json()
        print(f"Error Code: {error['error']['code']}")
        print(f"Message: {error['error']['message']}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")
