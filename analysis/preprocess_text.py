# Este archivo contiene funciones para preprocesar y normalizar transcripciones de audio para su posterior análisis con LLM.

import re
from typing import List

# Variables globales
FILLER_WORDS = [
    "eh", "em", "mmm", "mm", "eeeh", "vale", "bueno", "pues", "o sea", "digamos", "este", "esto", "como que", "en plan", "¿vale?", "¿no?", "¿sí?", "¿me explico?", "¿entiendes?",
    "¿de acuerdo?", "a ver", "vamos a ver", "es decir", "entonces", "claro", "básicamente", "literalmente", "realmente", "simplemente", "prácticamente",
    "más o menos", "un poco", "algo así", "por así decirlo", "no sé", "qué sé yo", "¿sabes?", "¿me sigues?", "¿ok?", "ehm", "mmm", "ah", "oh", "hmm", "ehhh", "pues nada", "en fin"
]

TOPIC_SHIFT_MARKERS = [
    "por otro lado", "por otra parte", "en cambio", "ahora bien", "sin embargo", "no obstante", "a continuación", "seguidamente", "en primer lugar", "en segundo lugar",
    "por último", "vamos a hablar de", "vamos a ver", "vamos a pasar a", "pasando a", "centrándonos en", "respecto a", "en relación con", "es importante destacar", "hay que tener en cuenta",
    "conviene señalar", "cabe destacar", "por ejemplo", "un ejemplo de esto", "como ejemplo", "pongamos el caso", "en conclusión", "para concluir", "para finalizar", "en resumen", "resumiendo",
    "dicho esto", "una vez dicho esto", "hecha esta aclaración", "volviendo al tema", "retomando", "como decíamos antes", "ojo con esto", "hay un matiz importante", "esto es clave"
]


MIN_SENTENCE_LENGTH = 20  # caracteres mínimos para considerar una frase útil

# Esta función elimina muletillas comunes del texto
def remove_filler_words(text: str) -> str:
    for filler in FILLER_WORDS:
        pattern = rf"\b{re.escape(filler)}\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text

# Esta función limpia espacios en blanco excesivos
def clean_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Esta función divide el texto en frases basadas en puntuación
def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) >= MIN_SENTENCE_LENGTH]

# Esta función agrupa frases en párrafos teniendo en cuenta los cambios de tema
def group_sentences_into_paragraphs(sentences: List[str], min_sentences: int = 2, max_sentences: int = 6) -> List[str]:

    paragraphs = []
    current = []

    for sentence in sentences:
        lower = sentence.lower()

        # Detectar cambio de tema
        if any(marker in lower for marker in TOPIC_SHIFT_MARKERS) and len(current) >= min_sentences:
            paragraphs.append(" ".join(current))
            current = []

        current.append(sentence)

        if len(current) >= max_sentences:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return paragraphs

# Esta función normaliza la transcripción completa
def normalize_transcript(raw_text: str) -> str:

    if not raw_text or not raw_text.strip():
        raise ValueError("La transcripción está vacía.")

    # 1. Minúsculas controladas (manteniendo legibilidad)
    text = raw_text.strip()

    # 2. Eliminar muletillas
    text = remove_filler_words(text)

    # 3. Normalizar espacios
    text = clean_whitespace(text)

    # 4. Separar en frases útiles
    sentences = split_into_sentences(text)

    if not sentences:
        raise ValueError("No se pudieron extraer frases válidas del texto.")

    # 5. Agrupar en párrafos
    paragraphs = group_sentences_into_paragraphs(sentences)

    # 6. Formato final
    normalized_text = [
        "TRANSCRIPCIÓN NORMALIZADA",
        "",
        f"Idioma: Español",
        f"Número de párrafos: {len(paragraphs)}",
        "",
        "Contenido:"
    ]

    for i, paragraph in enumerate(paragraphs, start=1):
        normalized_text.append(f"[{i}] {paragraph}")

    return "\n".join(normalized_text)
