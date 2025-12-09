# Este archivo contiene el programa que descarga los vídeos de YouTube. Usa yt-dlp para descargar los vídeos y devuelve la ruta del archivo.

import os
import re
from yt_dlp import YoutubeDL

AUDIO_DIR = "data/audios"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Esta función extrae el ID del vídeo de una URL de YouTube
def extract_video_id(url: str) -> str:
    patterns = [
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError("No se pudo extraer el ID del vídeo")

# Esta función devuelve la ruta del audio dado el ID del vídeo
def get_audio_path(video_id: str) -> str:
    return f"{AUDIO_DIR}/{video_id}.mp3"

#Esta función comprueba si el audio ya está descargado
def is_audio_cached(video_id: str) -> str | None:
    audio_path = get_audio_path(video_id)
    return audio_path if os.path.exists(audio_path) else None

# Esta función descarga solo el audio en formato MP3
def download_audio(url: str) -> str:
    video_id = extract_video_id(url)
    output_path = os.path.join(AUDIO_DIR, f"{video_id}.mp3")

    # -----------------------------
    # 1. Caché
    # -----------------------------
    if os.path.exists(output_path):
        print(f"📦 Audio ya descargado (caché): {output_path}")
        return output_path

    print(f"⬇ Descargando audio de: {url}")

    # -----------------------------
    # 2. Opciones modernas YT-DLP
    # -----------------------------
    ydl_opts = {
        "format": "bestaudio/best",     # El mejor audio disponible
        "outtmpl": os.path.join(AUDIO_DIR, f"{video_id}.%(ext)s"),

        # Extraer audio siempre como MP3
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],

        # Cabeceras para evitar bloqueos
        "http_headers": {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },

        # Evita problemas con nsig
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android"],
            }
        },

        "quiet": False,
        "noprogress": True,
    }

    # -----------------------------
    # 3. Ejecutar descarga
    # -----------------------------
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("❌ ERROR descargando audio:", e)
        raise RuntimeError("Falló la descarga del audio")

    #       yt-dlp asegura que termina como .mp3
    print(f"✔ Audio descargado correctamente: {output_path}")
    return output_path
