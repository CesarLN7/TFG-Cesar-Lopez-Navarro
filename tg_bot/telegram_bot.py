# Este archivo contiene la lógica principal del bot de Telegram.

import os
import re
import shutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from yt_download.downloader import extract_video_id, download_audio, is_audio_cached
from yt_transcript.get_transcript import transcribe_audio
from analysis.preprocess_text import normalize_transcript



# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ ERROR: TELEGRAM_BOT_TOKEN no encontrado en .env")

# -----------------------------------------
# FUNCIONES DE MANEJO
# -----------------------------------------

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Envíame un enlace de YouTube y analizaré el vídeo."
    )

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Solo envíame un enlace de YouTube y me encargo del resto."
    )

# Detectar si el mensaje contiene un URL de YouTube
YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_\-]{11})"

# Comando /test para probar con un audio local
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Si el usuario no pasa ruta, usamos un archivo por defecto
    if len(context.args) == 0:
        audio_path = "data/audios/test_audio_1.mp3"
    else:
        audio_path = " ".join(context.args)

    if not os.path.exists(audio_path):
        await update.message.reply_text(f"❌ Archivo no encontrado:\n{audio_path}")
        return

    await update.message.reply_text(f"🎧 Usando archivo:\n{audio_path}")
    await update.message.reply_text("📝 Transcribiendo el audio...")

    try:
        test_id = os.path.splitext(os.path.basename(audio_path))[0]
        raw_transcription = transcribe_audio(test_id, audio_path)                                   #(CUIDADO CON LOS ARGUMENTOS DE AQUÍ, SON DE PRUEBA!!!!!!)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error transcribiendo audio:\n{e}")
        return

    await update.message.reply_text("✔ Audio transcrito con éxito.")

    # Enviar preview al usuario
    preview = raw_transcription[:1500] + ("..." if len(raw_transcription) > 1500 else "")

    await update.message.reply_text(
        f"🗒️ **Preview de la transcripción:**\n\n{preview}",
        parse_mode="Markdown"
    )
    
    await update.message.reply_text("🧹 Normalizando transcripción...")

    try:
        normalized_text = normalize_transcript(raw_transcription)
    except Exception as e:
        await update.message.reply_text(f"❌ Error normalizando texto:\n{e}")
        return
    
    normalized_path = f"data/transcripts/{test_id}_normalized.txt"

    with open(normalized_path, "w", encoding="utf-8") as f:
        f.write(normalized_text)
    
    preview = normalized_text[:1500] + ("..." if len(normalized_text) > 1500 else "")

    await update.message.reply_text(
        f"🧠 **Transcripción normalizada (preview):**\n\n{preview}",
        parse_mode="Markdown"
    )

# Manejar mensajes generales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #Como ahora vamos a usar un audio de prueba, se usará el path absoluto en /test. En el futuro, se usará la URL aquí (!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
    # url = update.message.text
    
    '''
    Cuando vuelva a descargar vídeos será:
    
    video_id = extract_video_id(url)

    audio_path = download_audio(url)  # guardado como data/audios/<video_id>.mp3

    transcription = transcribe_audio(video_id, audio_path)

    
    
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
        
    '''
    
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

    audio_cache = "data/audios"
    transcript_cache = "data/transcripts"

    # Borrar audios
    if os.path.exists(audio_cache):
        print("🧹 Borrando caché de audio…")
        shutil.rmtree(audio_cache)
        print("✔ Caché de audio eliminada.")
    else:
        print("No había caché de audio.")

    # Borrar transcripciones
    if os.path.exists(transcript_cache):
        print("🧹 Borrando caché de transcripciones…")
        shutil.rmtree(transcript_cache)
        print("✔ Caché de transcripciones eliminada.")
    else:
        print("No había caché de transcripciones.")


# -----------------------------------------
# FUNCIÓN PRINCIPAL PARA INICIAR EL BOT
# -----------------------------------------

def run_bot():
    print("Iniciando bot de Telegram...")

    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("test", test_command))


    # Mensajes generales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en ejecución. Esperando mensajes...")
    try:
        app.run_polling()
    finally:
        print("Caché borrada. Ejecución finalizada. ¡Hasta pronto!")
        clean_cache()  

