from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAiGsczDRLUgQirKq0sJ2Zyp2P507pvc90")

MODEL_ID = "gemini-2.5-flash" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"] {"allow-input":true, isTemplate: true}


response = client.models.generate_content(
    model=MODEL_ID,
    contents="What's the largest planet in our solar system?"
)


print(response)
     
