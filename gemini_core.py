# gemini_core.py
import os
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai

# Securely loads your API key from your terminal session's environment variable.
API_KEY = os.getenv("GEMINI_API_KEY")

# This check is important. If the key is not set, the script will stop with a clear error.
if not API_KEY:
    raise ValueError("Error: The GEMINI_API_KEY environment variable is not set. Please set it in your command prompt before running the agent.")

# Configure the library with your API key.
genai.configure(api_key=API_KEY)

def call_gemini(prompt: str) -> str:
    """
    Sends a prompt to the Gemini model via the Google AI Studio API.

    Args:
        prompt: The complete prompt to send to the model.

    Returns:
        The text response from the model, or an error message if something goes wrong.
    """
    # --- THIS IS THE KEY CHANGE ---
    # We are specifying the exact model you have access to.
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    try:
        # Send the prompt to the API and get the response.
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # If there's an error (e.g., internet issue, bad API key), return a helpful message.
        return f"An error occurred while calling the API: {e}"