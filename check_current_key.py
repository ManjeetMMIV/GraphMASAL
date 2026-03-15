import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Check all sources
env_var = os.getenv("OPENAI_API_KEY")
print(f"🔍 Current OPENAI_API_KEY loaded:")
print(f"   Starts with: {env_var[:30] if env_var else 'NOT SET'}")
print(f"   Full key: {env_var}")
print(f"   Length: {len(env_var) if env_var else 0}")
