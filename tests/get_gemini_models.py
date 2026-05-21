import os
from google import genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY no encontrado en .env")


def get_gemini_models():

    client = genai.Client(api_key=API_KEY)

    print("=== MODELOS DISPONIBLES ===")

    for model in client.models.list():
        print(model.name)


# Ejecutar script
get_gemini_models()