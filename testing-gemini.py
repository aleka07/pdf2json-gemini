import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not set!")
    print("💡 Options to fix this:")
    print("   1. Set environment variable: export GEMINI_API_KEY='your-api-key-here'")
    print("   2. Create .env file: cp .env.example .env and edit it")
    print("   3. Get API key from: https://aistudio.google.com/app/apikey")
    exit(1)

client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.5-flash" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"] {"allow-input":true, isTemplate: true}


response = client.models.generate_content(
    model=MODEL_ID,
    contents="What's the largest planet in our solar system?"
)


print(response)
     
