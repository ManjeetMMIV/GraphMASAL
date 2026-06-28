from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY)

client = OpenAI(api_key=OPENAI_API_KEY)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'API connection successful!'"}]
    )
    print(response.choices[0].message.content)

except Exception as e:
    print(f"Error testing API key: {e}")