# Este archivo contiene la lógica principal del bot de Telegram.

import os
import re
import shutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from yt_download.downloader import extract_video_id, download_audio, is_audio_cached

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN no encontrado en .env")

# -----------------------------------------
# FUNCIONES DE MANEJO
# -----------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Envíame un enlace de YouTube y analizaré el vídeo."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Solo envíame un enlace de YouTube y me encargo del resto."
    )

# Detectar si el mensaje contiene un URL de YouTube
YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_\-]{11})"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text
    
    # 1. Extraer ID
    try:
        video_id = extract_video_id(url)
    except:
        await update.message.reply_text("❌ Ese mensaje no parece un enlace de YouTube válido.")
        return

    await update.message.reply_text(f"🎯 ID detectado: {video_id}")

    # 2. Comprobar caché
    cached_audio = is_audio_cached(video_id)

    if cached_audio:
        await update.message.reply_text(
            "📦 El audio ya estaba descargado.\nUsando archivo en caché."
        )
        audio_path = cached_audio
        print("USANDO CACHÉ:", audio_path)

    else:
        # 3. Descargar audio
        await update.message.reply_text("⬇ Descargando audio… espera un momento…")

        try:
            audio_path = download_audio(url)
        except Exception as e:
            await update.message.reply_text("❌ Error descargando el audio")
            print("ERROR:", e)
            return

        await update.message.reply_text("✔ Audio descargado con éxito.")

    # 4. Mostrar ruta interna (debug)
    await update.message.reply_text(f"Ruta del audio utilizada:\n{audio_path}")
    
    # Aquí en el futuro llamaremos a:
    # 1. Descargar el vídeo.
    # 2. Transcribir con Whisper
    # 3. Clasificar contenido
    # 4. Generar gráfica
    return

# -----------------------------------------
# LIMPIAR CACHÉ
# -----------------------------------------
def clean_cache():
    """Elimina la carpeta cache/audio/ al cerrar el bot."""
    cache_dir = "data/audio"
    if os.path.exists(cache_dir):
        print("🧹 Borrando caché de audio…")
        shutil.rmtree(cache_dir)
        print("✔ Caché eliminada.")
    else:
        print("No había caché que borrar.")

# -----------------------------------------
# FUNCIÓN PRINCIPAL PARA INICIAR EL BOT
# -----------------------------------------

def run_bot():
    print("Iniciando bot de Telegram...")

    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Mensajes generales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en ejecución. Esperando mensajes...")
    try:
        app.run_polling()
    finally:
        clean_cache()  

