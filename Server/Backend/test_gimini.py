import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load your .env file
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found. Check your .env file.")
else:
    print("✅ API Key found.")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Say hello from Gemini!")
    print("✅ Gemini API response:", response.text)
except Exception as e:
    print("❌ Gemini API failed:", str(e))
