import os
import subprocess
import threading
import time
import streamlit as st

# Configuración de URLs y directorios
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"
OUTPUT_DIR = "static"
MASTER_NAME = "canalcstreaming0934.m3u8"

# Guardar la referencia del proceso
ffmpeg_process = None


def start_ffmpeg_stream():
    global ffmpeg_process
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Comando ultra ligero para no saturar la RAM/CPU del servidor gratuito
    command = [
        "ffmpeg",
        "-re",
        "-i",
        INPUT_M3U8,
        # Re-codificación liviana de video y audio
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-b:v",
        "800k",
        "-s",
        "854x480",  # Calidad fija 480p estable para evitar caídas
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        # Formato HLS
        "-f",
        "hls",
        "-hls_time",
        "4",
        "-hls_list_size",
        "5",
        "-hls_flags",
        "delete_segments+independent_segments",
        "-hls_segment_filename",
        os.path.join(OUTPUT_DIR, "segment_%03d.ts"),
        os.path.join(OUTPUT_DIR, MASTER_NAME),
    ]

    try:
        ffmpeg_process = subprocess.Popen(command)
        ffmpeg_process.wait()
    except Exception as e:
        print(f"Error en FFmpeg: {e}")


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Señal TV Live", layout="wide")
st.title("📺 Señal TV - Transmisión en Vivo")

# Iniciar FFmpeg ÚNICAMENTE si no se está ejecutando ya en segundo plano
if "stream_running" not in st.session_state:
    st.session_state["stream_running"] = True
    thread = threading.Thread(target=start_ffmpeg_stream, daemon=True)
    thread.start()

full_public_url = (
    f"https://senal-tv03.streamlit.app/app/static/{MASTER_NAME}"
)

st.subheader("Enlace directo M3U8 para IPTV / Reproductores:")
st.code(full_public_url, language="text")

m3u8_file_path = os.path.join(OUTPUT_DIR, MASTER_NAME)

# Verificar si el manifiesto ya se generó
if os.path.exists(m3u8_file_path):
    st.success("Transmisión activa")
    st.video(f"app/static/{MASTER_NAME}")
else:
    st.info("Iniciando el motor de video... Espere unos segundos.")
    time.sleep(4)
    st.rerun()
