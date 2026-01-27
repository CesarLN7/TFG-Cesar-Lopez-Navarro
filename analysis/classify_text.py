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
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

# Directorio para guardar clasificaciones en caché
CLASSIFICATION_DIR = "data/classification"

# Esta función obtiene la ruta del archivo de clasificación en caché
def get_classification_path(analysis_id: str) -> str:
    return f"{CLASSIFICATION_DIR}/{analysis_id}_classification.json"

# Esta función verifica si la clasificación ya está en caché
def is_classification_cached(analysis_id: str) -> dict | None:
    path = get_classification_path(analysis_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Esta función guarda la clasificación en caché
def save_classification(analysis_id: str, data: dict):
    path = get_classification_path(analysis_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Esta función envía un prompt al modelo de Gemini para determinar si el vídeo es de viajes y su distribución temática mediante un JSON.
def classify_transcript(analysis_id: str, normalized_text: str) -> dict:
    
    # 1. Caché
    cached_result = is_classification_cached(analysis_id)
    if cached_result:
        print("📦 Clasificación encontrada en caché.")
        return cached_result

    # 2. Clasificación mediante Gemini
    prompt = """
Eres un sistema experto en análisis de contenido audiovisual.

Tu tarea principal es determinar si un vídeo puede considerarse
un VÍDEO DE VIAJES.

Definición CLAVE (muy importante):

Un vídeo SOLO se considera de viajes si:
- Existe desplazamiento físico a un lugar distinto al entorno habitual del creador, O
- Se narra una experiencia turística (visita a ciudades, países, regiones,
  rutas, alojamientos, transporte, planificación o vivencias durante un viaje).

NO se considera un vídeo de viajes si:
- Habla únicamente de comida, cocina o gastronomía SIN contexto de desplazamiento.
- Trata cultura, historia o costumbres SIN relación con una experiencia turística.
- Es entretenimiento, opinión o divulgación desde un entorno local o doméstico.

La gastronomía, cultura y entretenimiento SOLO cuentan como parte de un vídeo de viajes
si están claramente integrados dentro de una experiencia de viaje.

Vas a analizar la transcripción normalizada del vídeo en cuestión y debes responder
EXCLUSIVAMENTE en formato JSON válido.

Tareas:

1. Determinar si el vídeo es de viajes según la definición anterior.
2. Si lo es, repartir el contenido del vídeo en los siguientes ejes:
   - Gastronomía
   - Cultura
   - Entretenimiento
   - Otros

Definiciones de ejes (solo aplican si is_travel = true):
- Gastronomía: comida típica, platos, restaurantes, bebidas locales y experiencias culinarias vividas DURANTE un viaje o en un destino visitado.
- Cultura: historia, tradiciones, costumbres, patrimonio, contexto social del país,
  así como información práctica integrada en la experiencia del viaje
  (precios, moneda, coste de vida, transporte, desplazamientos, alojamiento y logística local).
- Entretenimiento: anécdotas personales, vivencias, humor y experiencias narrativas del viaje.
- Otros: contenido no clasificable claramente en las categorías anteriores, dentro del contexto del viaje.
  (introducciones genéricas, despedidas, reflexiones no relacionadas con el viaje,
  patrocinio explícito, contenido off-topic).

Reglas IMPORTANTES:
- Usa valores entre 0 y 1.
- Si NO es un vídeo de viajes:
  - is_travel = false
  - travel_confidence = 0
  - todos los valores de distribution deben ser 0
- Si is_travel = true, la suma de los cuatro valores debe ser exactamente 1.
- No añadas explicaciones ni texto fuera del JSON.

Formato EXACTO de salida:

{
  "is_travel": bool,
  "travel_confidence": float,
  "distribution": {
    "gastronomy": float,
    "culture": float,
    "entertainment": float,
    "others": float
  }
}


EJMPLO DE RESPUESTA VÁLIDA:

{
  "is_travel": true,
  "travel_confidence": 0.85,
  "distribution": {
    "gastronomy": 0.3,
    "culture": 0.4,
    "entertainment": 0.2,
    "others": 0.1
  }
}

Transcripción:
\"\"\"
""" + normalized_text + """
\"\"\"
"""

    # 3. Llamar al modelo
    response = model.generate_content(prompt)

    raw = response.text.strip()

    # 4. Limpiar salida
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"❌ La respuesta del modelo no es JSON válido:\n{raw}")


    if result.get("is_travel"):
        distribution = result.get("distribution", {})
        total = sum(distribution.values())

        if not abs(total - 1.0) < 0.01:
            raise ValueError(
                f"❌ Distribución no suma 1 (suma={total})"
            )

    # 5. Guardar caché
    save_classification(analysis_id, result)

    return result