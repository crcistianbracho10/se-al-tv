import os
import subprocess
import threading
import time
import streamlit as st

# Configuración de URLs y directorios
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"
OUTPUT_DIR = "static"
MASTER_NAME = "canalcstreaming0934.m3u8"


def start_ffmpeg_stream():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    command = [
        "ffmpeg",
        "-re",
        "-i",
        INPUT_M3U8,
        "-vf",
        "scale=w=854:h=480",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-b:v",
        "800k",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
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
        process = subprocess.Popen(command)
        process.wait()
    except Exception as e:
        print(f"Error en FFmpeg: {e}")


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Señal TV Live", layout="wide")
st.title("📺 Señal TV - Transmisión en Vivo")

# Iniciar proceso único
if "ffmpeg_active" not in st.session_state:
    st.session_state["ffmpeg_active"] = True
    thread = threading.Thread(target=start_ffmpeg_stream, daemon=True)
    thread.start()

# URL Web pública servida por Streamlit
full_public_url = (
    f"https://senal-tv03.streamlit.app/app/static/{MASTER_NAME}"
)

st.subheader("Enlace directo M3U8 para IPTV / Reproductores:")
st.code(full_public_url, language="text")

# Ruta física en el disco local para comprobar si el archivo ya se creó
local_file_path = os.path.join(OUTPUT_DIR, MASTER_NAME)

if os.path.exists(local_file_path):
    st.success("Transmisión activa")
    # Pasamos la URL pública (con https://) para que el reproductor la lea por red
    st.video(full_public_url)
else:
    st.info("Generando manifiesto M3U8... Espere unos segundos.")
    time.sleep(3)
    st.rerun()
