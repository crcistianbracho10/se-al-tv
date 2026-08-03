import http.server
import os
import socketserver
import subprocess
import threading
import time
import streamlit as st

# Carpetas y archivos
OUTPUT_DIR = "video_data"
MASTER_NAME = "canalcstreaming0934.m3u8"
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"
PORT = 8080


# 1. Servidor de archivos estáticos en segundo plano
def run_file_server():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.chdir(OUTPUT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    # Permitir peticiones CORS para que reproductores externos puedan leerlo
    handler.extensions_map.update({".m3u8": "application/x-mpegURL"})
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()


# 2. Proceso de retransmisión con FFmpeg
def start_ffmpeg_stream():
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
        "segment_%03d.ts",
        MASTER_NAME,
    ]

    try:
        process = subprocess.Popen(command)
        process.wait()
    except Exception as e:
        print(f"Error en FFmpeg: {e}")


# --- INICIALIZACIÓN DE HILOS SECUNDARIOS ---
if "servers_started" not in st.session_state:
    st.session_state["servers_started"] = True

    # Iniciar servidor estático en el puerto 8080
    t_server = threading.Thread(target=run_file_server, daemon=True)
    t_server.start()

    # Iniciar FFmpeg
    t_ffmpeg = threading.Thread(target=start_ffmpeg_stream, daemon=True)
    t_ffmpeg.start()


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Señal TV Live", layout="wide")
st.title("📺 Señal TV - Transmisión en Vivo")

# URL de reproducción local/interna
m3u8_file_path = os.path.join(OUTPUT_DIR, MASTER_NAME)

st.subheader("Estado de la retransmisión:")

if os.path.exists(m3u8_file_path):
    st.success("¡Manifiesto M3U8 generado correctamente!")

    # Si se usa un reproductor interno, leemos el archivo local o servido por HTTP
    st.video(f"http://localhost:{PORT}/{MASTER_NAME}")
else:
    st.info("Generando segmentos HLS... Por favor espera unos segundos.")
    time.sleep(3)
    st.rerun()
