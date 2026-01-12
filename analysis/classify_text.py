# Este archivo clasifica transcripciones normalizadas usando Gemini (Google AI)

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY no encontrado en .env")

genai.configure(api_key=API_KEY)

# Cargar modelo UNA sola vez por ejecución
print("🧠 Cargando modelo Gemini...")
model = genai.GenerativeModel("gemini-1.5-pro")

# Directorio para guardar clasificaciones en caché
CLASSIFICATION_DIR = "data/classification"
os.makedirs(CLASSIFICATION_DIR, exist_ok=True)

# Esta función obtiene la ruta del archivo de clasificación en caché
def get_classification_path(video_id: str) -> str:
    return f"{CLASSIFICATION_DIR}/{video_id}_classification.json"

# Esta función verifica si la clasificación ya está en caché
def is_classification_cached(video_id: str) -> dict | None:
    path = get_classification_path(video_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Esta función guarda la clasificación en caché
def save_classification(video_id: str, data: dict):
    path = get_classification_path(video_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Esta función envía un prompt al modelo de Gemini para determinar si el vídeo es de viajes y su distribución temática mediante un JSON.
def classify_transcript(video_id: str, normalized_text: str) -> dict:
    
    # 1. Caché
    cached_result = is_classification_cached(video_id)
    if cached_result:
        print("📦 Clasificación encontrada en caché.")
        return cached_result

    # 2. Clasificación mediante Gemini
    prompt = f"""
Eres un sistema experto en análisis de contenido audiovisual.

Vas a analizar la transcripción normalizada de un vídeo y debes responder
EXCLUSIVAMENTE en formato JSON válido.

Tareas:

1. Determinar si el vídeo es de viajes.
2. Si lo es, repartir el contenido del vídeo en los siguientes ejes:
   - Gastronomía
   - Cultura
   - Entretenimiento
   - Otros

Definiciones:
- Gastronomía: comida típica, platos, restaurantes, bebidas locales y experiencias culinarias.
- Cultura: historia, tradiciones, costumbres, patrimonio, contexto social del país,
  así como información práctica integrada en la experiencia del viaje
  (precios, moneda, coste de vida, transporte, desplazamientos, alojamiento y logística local).
- Entretenimiento: anécdotas personales, vivencias, humor y experiencias narrativas del viaje.
- Otros: contenido no clasificable claramente en las categorías anteriores
  (introducciones genéricas, despedidas, reflexiones no relacionadas con el viaje,
  patrocinio explícito, contenido off-topic).

Reglas IMPORTANTES:
- Usa valores entre 0 y 1.
- Si NO es un vídeo de viajes, todos los valores deben ser 0.
- Si is_travel = true, la suma de los cuatro valores debe ser exactamente 1.
- No añadas explicaciones ni texto fuera del JSON.

Formato EXACTO de salida:

{{
  "is_travel": true | false,
  "travel_confidence": float,
  "distribution": {{
    "gastronomy": float,
    "culture": float,
    "entertainment": float,
    "others": float
  }}
}}

Transcripción:
\"\"\"
{normalized_text}
\"\"\"
"""

    # 3. Llamada al modelo
    response = model.generate_content(prompt)

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError("❌ La respuesta del modelo no es JSON válido")
    
    # 4. Guardar caché
    save_classification(video_id, result)

    return result