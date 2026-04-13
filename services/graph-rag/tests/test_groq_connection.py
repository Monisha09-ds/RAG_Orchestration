
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ Missing GROQ_API_KEY!")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.2
    )
    print(f"✅ Groq connection successful! Output: {completion.choices[0].message.content}")
except Exception as e:
    print(f"❌ Groq connection failed: {e}")
