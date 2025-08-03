import os

from google import genai
from google.genai import types

# Set your Gemini API key
os.environ["GEMINI_API_KEY"] = "Ajgofds-YFUIDHSJnjy8bv98hxjkljdsklhHLHA"

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="List three applications of artificial intelligence in daily life.",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=5),  # Allows some thinking
        temperature=0.7  # Lower temperature for more focused answers
    ),
)
print(response.text)
