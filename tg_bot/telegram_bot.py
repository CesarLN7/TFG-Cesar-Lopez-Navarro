# Este archivo contiene la lógica principal del bot de Telegram.

import os
import shutil
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from yt_transcript.get_transcript import transcribe_audio
from analysis.preprocess_text import normalize_transcript
from analysis.classify_text.classify_text import classify_transcript
from analysis.classify_text.get_gemini_model import get_gemini_models
from analysis.generate_graph import generate_graph


# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ ERROR: TELEGRAM_BOT_TOKEN no encontrado en .env")

# Asegurar que los directorios necesarios existen
def ensure_directories():
    required_dirs = [
        "data/audios",
        "data/transcripts",
        "data/classification",
        "data/graphs"
    ]

    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

# -----------------------------------------
# FUNCIONES DE MANEJO
# -----------------------------------------

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
    "👋 *Bienvenido al analizador de contenido audiovisual*\n\n"
    "Este bot clasifica automáticamente el contenido de un audio "
    "y genera una visualización del tipo de información presente "
    "(viajes, gastronomía, cultura, entretenimiento, etc.).\n\n"

    "🔹 *Uso principal*\n"
    "Envía el comando:\n"
    "`/analyze ruta/del/audio.mp3`\n\n"

    "📦 El proyecto incluye audios de prueba listos para usar.\n"
    "También puedes analizar tus propios archivos `.mp3`.\n\n"

    "ℹ️ Para ver instrucciones detalladas, escribe `/help`."
        )

    await update.message.reply_text(text, parse_mode="Markdown")

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
    "📖 *Instrucciones de uso*\n\n"
    "Este bot analiza contenido audiovisual a partir de archivos de audio "
    "en formato `.mp3` y genera una visualización automática del tipo de contenido.\n\n"

    "🔹 *Comando principal*\n"
    "`/analyze ruta/del/audio.mp3`\n\n"

    "Ejemplos:\n"
    "`/analyze data/audios/test1.mp3`\n"
    "`/analyze data/audios/viaje_japon.mp3`\n\n"
    
    "📂 *Añadir audios manualmente*\n"
    "El bot no descarga contenido externo.\n"
    "Para analizar nuevos audios:\n\n"
    "1️⃣ Copia tus archivos `.mp3` en la carpeta:\n"
    "`data/audios/`\n\n"
    "2️⃣ Ejecuta el comando:\n"
    "`/analyze data/audios/nombre_del_audio.mp3`\n\n"
    "📦 El proyecto incluye una batería inicial de audios de prueba,\n"
    "pero puede ser ampliada libremente añadiendo nuevos archivos.\n\n"

    "⚠️ *Restricciones*\n"
    "• Solo se admiten archivos en formato `.mp3`\n"
    "• El archivo debe existir en el sistema\n\n"

    "📊 *Resultado del análisis*\n"
    "Al ejecutar `/analyze`, el bot devuelve directamente una gráfica que resume "
    "la clasificación del contenido del audio.\n\n"

    "🔍 *Consultas adicionales (opcional)*\n"
    "Tras ejecutar un análisis, puedes explorar los resultados en detalle usando:\n\n"
    "`/raw ID` → preview de la transcripción original\n"
    "`/normalized ID` → preview del texto normalizado\n"
    "`/json ID` → resultado de la clasificación en formato JSON\n\n"

    "ℹ️ El identificador (`ID`) corresponde al nombre del archivo de audio "
    "sin la extensión `.mp3`.\n"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

# Comando /test
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Si el usuario no pasa ruta, usamos un archivo por defecto
    if len(context.args) == 0:
        audio_path = "data/audios/test_audio_1.mp3"
    else:
        audio_path = " ".join(context.args)

    # Validar existencia
    if not os.path.exists(audio_path):
        await update.message.reply_text(f"❌ Archivo no encontrado:\n{audio_path}")
        return

    await update.message.reply_text(f"🎧 Usando archivo:\n{audio_path}")
    await update.message.reply_text("📝 Transcribiendo el audio...")

    # Transcripción
    try:
        test_id = os.path.splitext(os.path.basename(audio_path))[0]
        raw_transcription = transcribe_audio(test_id, audio_path)
        
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

    # Normalización
    try:
        normalized_text = normalize_transcript(raw_transcription)
    except Exception as e:
        await update.message.reply_text(f"❌ Error normalizando texto:\n{e}")
        return
    
    normalized_path = f"data/transcripts/{test_id}_normalized.txt"

    with open(normalized_path, "w", encoding="utf-8") as f:
        f.write(normalized_text)
    
    # Enviar preview al usuario
    preview = normalized_text[:1500] + ("..." if len(normalized_text) > 1500 else "")

    await update.message.reply_text(
        f"🧠 **Transcripción normalizada (preview):**\n\n{preview}",
        parse_mode="Markdown"
    )
    
    await update.message.reply_text("🧠 Clasificando contenido del vídeo...")

    # Clasificación
    try:
        classification = classify_transcript(test_id, normalized_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Error clasificando texto:\n{e}")
        return

    # Enviar JSON formateado al usuario
    pretty_json = json.dumps(classification, ensure_ascii=False, indent=2)

    await update.message.reply_text(
        f"📊 **Resultado de clasificación:**\n\n```json\n{pretty_json}\n```",
        parse_mode="Markdown"
    )
    
    # Gráfica
    graph_path = generate_graph(test_id, classification)

    # Enviar gráfica al usuario
    with open(graph_path, "rb") as img:
        await update.message.reply_photo(photo=img)
     
# Comando /analyze   
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Validar argumentos
    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ Debes indicar la ruta a un archivo `.mp3`.\nEjemplo:\n/analyze data/audios/test1.mp3"
        )
        return

    audio_path = " ".join(context.args)

    # Validar extensión y existencia
    if not audio_path.lower().endswith(".mp3"):
        await update.message.reply_text("❌ Solo se admiten archivos `.mp3`.")
        return

    if not os.path.exists(audio_path):
        await update.message.reply_text(f"❌ Archivo no encontrado:\n{audio_path}")
        return

    # Identificador del análisis
    analysis_id = os.path.splitext(os.path.basename(audio_path))[0]

    # Rutas de caché
    raw_path = f"data/transcripts/{analysis_id}_raw.txt"
    norm_path = f"data/transcripts/{analysis_id}_normalized.txt"
    json_path = f"data/classification/{analysis_id}.json"
    graph_path = f"data/graphs/{analysis_id}.png"

    # Si todo existe, usamos caché completa
    if all(os.path.exists(p) for p in [raw_path, norm_path, json_path, graph_path]):
        with open(graph_path, "rb") as img:
            await update.message.reply_photo(photo=img)
        await update.message.reply_text("📦 Resultado obtenido desde caché.")
        return

    await update.message.reply_text("🎧 Analizando audio...")

    # Realizar análisis con manejo de errores
    try:
        # 1. Transcripción
        await update.message.reply_text("🎧 Transcribiendo audio...")

        raw_text = transcribe_audio(analysis_id, audio_path)
        os.makedirs("data/transcripts", exist_ok=True)

        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        # 2. Normalización
        await update.message.reply_text("🧹 Normalizando transcripción...")

        normalized_text = normalize_transcript(raw_text)

        with open(norm_path, "w", encoding="utf-8") as f:
            f.write(normalized_text)

        # 3. Clasificación
        await update.message.reply_text("🧠 Clasificando contenido...")

        classification = classify_transcript(analysis_id, normalized_text)
        os.makedirs("data/classification", exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(classification, f, ensure_ascii=False, indent=2)

        # 4. Generar gráfica
        await update.message.reply_text("📊 Generando visualización...")

        graph_path = generate_graph(analysis_id, classification)

        # 5. Enviar gráfica al usuario
        with open(graph_path, "rb") as img:
            await update.message.reply_photo(photo=img)

        # 6. Confirmación final
        await update.message.reply_text(
            "✅ *Análisis completado con éxito*\n\n"
            "Puedes consultar más información con:\n"
            f"`/raw {analysis_id}`\n"
            f"`/normalized {analysis_id}`\n"
            f"`/json {analysis_id}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        print("ERROR DURANTE EL ANÁLISIS:", e)
        await update.message.reply_text(
            "❌ Se produjo un error durante el análisis.\n"
            "Consulta la consola para más detalles."
        )

# Comando /raw
async def raw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Validar argumentos
    if len(context.args) == 0:
        await update.message.reply_text("❌ Debes indicar un identificador.\nEjemplo:\n/raw viaje_japon")
        return

    analysis_id = context.args[0]
    path = f"data/transcripts/{analysis_id}_raw.txt"

    # Validar existencia
    if not os.path.exists(path):
        await update.message.reply_text("❌ No existe una transcripción raw para ese ID.")
        return

    # Leer y enviar preview
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    preview = text[:1500] + ("..." if len(text) > 1500 else "")

    await update.message.reply_text(
        f"🗒️ *Transcripción raw (preview):*\n\n{preview}",
        parse_mode="Markdown"
    )

# Comando /normalized
async def normalized_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Validar argumentos
    if len(context.args) == 0:
        await update.message.reply_text("❌ Debes indicar un identificador.\nEjemplo:\n/normalized viaje_japon")
        return

    analysis_id = context.args[0]
    path = f"data/transcripts/{analysis_id}_normalized.txt"

    # Validar existencia
    if not os.path.exists(path):
        await update.message.reply_text("❌ No existe una transcripción normalizada para ese ID.")
        return

    # Leer y enviar preview
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    preview = text[:1500] + ("..." if len(text) > 1500 else "")

    await update.message.reply_text(
        f"🧠 *Transcripción normalizada (preview):*\n\n{preview}",
        parse_mode="Markdown"
    )

# Comando /json
async def json_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Validar argumentos
    if len(context.args) == 0:
        await update.message.reply_text("❌ Debes indicar un identificador.\nEjemplo:\n/json viaje_japon")
        return

    analysis_id = context.args[0]
    path = f"data/classification/{analysis_id}.json"

    # Validar existencia
    if not os.path.exists(path):
        await update.message.reply_text("❌ No existe una clasificación para ese ID.")
        return

    # Leer y enviar JSON formateado
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pretty = json.dumps(data, ensure_ascii=False, indent=2)

    await update.message.reply_text(
        f"📊 *Clasificación JSON:*\n\n```json\n{pretty}\n```",
        parse_mode="Markdown"
    )

# Manejar mensajes generales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Este bot no procesa mensajes de texto directamente.\n\n"
        "Usa:\n"
        "`/analyze ruta/del/audio.mp3`\n\n"
        "Ejemplo:\n"
        "`/analyze data/audios/test1.mp3`\n\n"
        "👉 Usa `/help` para más información.",
        parse_mode="Markdown"
    )

# -----------------------------------------
# LIMPIAR CACHÉ
# -----------------------------------------

def clean_cache():

    audio_cache = "data/audios"
    transcript_cache = "data/transcripts"
    classification_cache = "data/classification"
    graph_cache = "data/graphs"

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
        
    # Borrar clasificaciones
    if os.path.exists(classification_cache):
        print("🧹 Borrando caché de clasificación…")
        shutil.rmtree(classification_cache)
        print("✔ Caché de clasificación eliminada.")
    else:
        print("No había caché de clasificación.")
        
    # Borrar gráficos
    if os.path.exists(graph_cache):
        print("🧹 Borrando caché de gráficos…")
        shutil.rmtree(graph_cache)
        print("✔ Caché de gráficos eliminada.")
    else:
        print("No había caché de gráficos.")

# -----------------------------------------
# FUNCIÓN PRINCIPAL PARA INICIAR EL BOT
# -----------------------------------------

def run_bot():
    print("Iniciando bot de Telegram...")
    
    get_gemini_models()
    
    ensure_directories()

    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("raw", raw_command))
    app.add_handler(CommandHandler("normalized", normalized_command))
    app.add_handler(CommandHandler("json", json_command))


    # Mensajes generales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en ejecución. Esperando mensajes...")
    try:
        app.run_polling()
    finally:
        print("Caché borrada. Ejecución finalizada. ¡Hasta pronto!")
        clean_cache()  

