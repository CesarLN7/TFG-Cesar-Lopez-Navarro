import os
from google import genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY no encontrado en .env")

def is_stable_model(name: str) -> bool:
    unstable_keywords = [
        "preview",
        "experimental",
        "live",
        "tts",
        "image",
        "robotics"
    ]
    return not any(k in name for k in unstable_keywords)

def get_gemini_models():
    client = genai.Client(api_key=API_KEY)

    valid_models = []

    for model in client.models.list():

        name = getattr(model, "name", None)
        methods = getattr(model, "supported_generation_methods", [])

        if name and "generateContent" in methods and is_stable_model(name):
            valid_models.append(name)
            
    return valid_models