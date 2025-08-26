import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash-001")
    response = model.generate_content(prompt)
    return response.text

def summarize_text(text: str) -> str:
    if not text or text.strip() == "":
        return "0"

    prompt = f"Summarize the following note content for fast and concise access of its information:\n\n'{text}'.\n\ndo not exceed 100 characters in the summary."

    try:
        response = get_gemini_response(prompt)
        summary = response.strip()
        if not summary:
            return "1"
        return summary
    except Exception as e:
        print("Error calling Gemini API:", e)
        return "2"
