# Este archivo contiene la función para transcribir los audios de los vídeos a analizar usando Whisper (API OpenAI).

import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables del entorno (.env)
load_dotenv()

TRANSCRIPTS_DIR = "data/transcripts"
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

client = OpenAI()  # Ya usa OPENAI_API_KEY del .env


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

    # 2. Transcribir con Whisper
    print(f"🔊 Transcribiendo audio: {audio_path}")

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    text = response.text

    # 3. Guardar en caché
    save_transcription(video_id, text)

    return text
