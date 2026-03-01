"""Test Groq API connection"""

import os
from dotenv import load_dotenv
from groq import Groq

print("\n" + "="*60)
print("TESTING GROQ API")
print("="*60 + "\n")

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GROQ_API_KEY')

if not api_key:
    print("[FAIL] GROQ_API_KEY not found in .env file")
    exit(1)

print(f"[OK] API Key loaded: {api_key[:20]}...")

# Test API connection
try:
    print("\nTesting API connection...")
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Groq API is working!' in one sentence."}
        ],
        max_tokens=50,
        temperature=0.2
    )
    
    result = response.choices[0].message.content
    print(f"\n[SUCCESS] Groq API Response:")
    print(f"  {result}")
    print(f"\n[OK] Model: {response.model}")
    print(f"[OK] Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"\n[FAIL] API Error: {e}")
    exit(1)

print("\n" + "="*60)
print("GROQ API IS WORKING!")
print("="*60 + "\n")

print("Your dashboard will now use AI predictions!")
print("Run: streamlit run app.py")
