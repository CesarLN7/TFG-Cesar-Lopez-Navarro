# Este archivo contiene la función para transcribir los audios de los vídeos a analizar usando Whisper en local. Se necesita tener instalado FFmpeg.

import os
import whisper

os.environ["PATH"] += os.pathsep + r"C:\Users\César\OneDrive - Universidad Carlos III de Madrid\Documentos\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin"

TRANSCRIPTS_DIR = "data/transcripts"
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# Cargar modelo UNA sola vez por ejecución
print("🧠 Cargando modelo Whisper...")
model = whisper.load_model("small")

def get_transcript_path(video_id: str) -> str:
    return f"{TRANSCRIPTS_DIR}/{video_id}.txt"


def is_transcript_cached(video_id: str) -> str | None:
    path = get_transcript_path(video_id)
    return path if os.path.exists(path) else None


def save_transcription(video_id: str, text: str):
    path = get_transcript_path(video_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def transcribe_audio(video_id: str, audio_path: str) -> str:
    
    # 1. Caché
    cached_path = is_transcript_cached(video_id)
    if cached_path:
        print("📦 Transcripción encontrada en caché.")
        with open(cached_path, "r", encoding="utf-8") as f:
            return f.read()

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio no encontrado: {audio_path}")
    
    # 2. Transcripción
    print(f"🔊 Transcribiendo audio con Whisper: {audio_path}")
    result = model.transcribe(audio_path, language="es")

    text = result["text"]

    # 3. Guardar caché
    save_transcription(video_id, text)

    return text
