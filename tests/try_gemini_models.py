import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY no encontrado en .env")

client = genai.Client(api_key=API_KEY)

MODELS_TO_TEST = [
    "models/gemini-2.5-flash-lite",
    "models/gemini-flash-lite-latest",
    "models/gemini-2.0-flash-lite",
    "models/gemini-2.0-flash-lite-001",
    "models/gemini-2.5-flash",
]

for model_name in MODELS_TO_TEST:
    print(f"\nProbando: {model_name}")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents='Responde solo con este JSON: {"ok": true}'
        )
        print("✅ FUNCIONA")
        print(response.text)
        break

    except Exception as e:
        print("❌ FALLA")
        print(e)