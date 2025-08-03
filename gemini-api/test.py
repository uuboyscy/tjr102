import os

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
os.environ["GEMINI_API_KEY"] = "Ajgofds-YFUIDHSJnjy8bv98hxjkljdsklhHLHA"

# client = genai.Client()

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)


from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0), # Disables thinking
        temperature=1.8
    ),
)
print(response.text)