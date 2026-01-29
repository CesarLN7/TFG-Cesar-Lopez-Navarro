# Pasos a seguir para la instalación del entorno virtual de esta herramienta

1. Creación del entorno virtual:
   python -m venv venv
   venv\Scripts\activate   (Windows)
   source venv/bin/activate  (Linux/Mac)

2. Instalación de dependencias:
   pip install -r requirements.txt

3. Ejecución del bot:
   python main.py

- Para el completo funcionamiento de la herramienta es necesaria la instalación previa de la versión
   más reciente que sea posible programa ffmpeg en el dispositivo en el que va a ser ejecutada.
   
- Así mismo, tambien se requiere la actualización de la línea número siete del archivo con nombre
   get_transcript.py con la ruta en la que dicho programa se encuentre en el dispositivo.