import json
import os
import subprocess
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import streamlit as st
import uvicorn

# Configuración básica
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"
OUTPUT_DIR = "hls_output"
MASTER_NAME = "canalcstreaming0934.m3u8"
FASTAPI_PORT = 8080


# --- 1. DETECTOR DE CALIDAD DE FUENTE ---
def get_stream_resolution(stream_url):
    """Analiza la fuente con ffprobe para saber la resolución de origen."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        stream_url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        width = data["streams"][0]["width"]
        height = data["streams"][0]["height"]
        return width, height
    except Exception as e:
        print(f"No se pudo detectar resolución, usando valor por defecto: {e}")
        return 1280, 720


# --- 2. SERVIDOR FASTAPI CON CORS PARA HLS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=OUTPUT_DIR), name="hls")


def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=FASTAPI_PORT, log_level="error")


# --- 3. PROCESADOR HLS MULTICALIDAD INTELIGENTE ---
def start_multi_bitrate_stream():
    width, height = get_stream_resolution(INPUT_M3U8)
    print(f"Resolución de origen detectada: {width}x{height}")

    # Configurar escalas según origen
    if height >= 1080:
        filter_str = (
            "[0:v]split=3[v1,v2,v3]; "
            "[v1]copy[v1out]; "
            "[v2]scale=w=1280:h=720[v2out]; "
            "[v3]scale=w=854:h=480[v3out]"
        )
        stream_map = "v:0,a:0,name:1080p v:1,a:1,name:720p v:2,a:2,name:480p"
        bitrate_args = [
            "-map",
            "[v1out]",
            "-c:v:0",
            "libx264",
            "-preset",
            "ultrafast",
            "-b:v:0",
            "2500k",
            "-map",
            "0:a?",
            "-c:a:0",
            "aac",
            "-b:a:0",
            "128k",
            "-map",
            "[v2out]",
            "-c:v:1",
            "libx264",
            "-preset",
            "ultrafast",
            "-b:v:1",
            "1200k",
            "-map",
            "0:a?",
            "-c:a:1",
            "aac",
            "-b:a:1",
            "96k",
            "-map",
            "[v3out]",
            "-c:v:2",
            "libx264",
            "-preset",
            "ultrafast",
            "-b:v:2",
            "600k",
            "-map",
            "0:a?",
            "-c:a:2",
            "aac",
            "-b:a:2",
            "64k",
        ]
    else:
        # Si es 720p o menor
        filter_str = (
            "[0:v]split=2[v1,v2]; "
            "[v1]scale=w=1280:h=720[v1out]; "
            "[v2]scale=w=854:h=480[v2out]"
        )
        stream_map = "v:0,a:0,name:720p v:1,a:1,name:480p"
        bitrate_args = [
            "-map",
            "[v1out]",
            "-c:v:0",
            "libx264",
            "-preset",
            "ultrafast",
            "-b:v:0",
            "1200k",
            "-map",
            "0:a?",
            "-c:a:0",
            "aac",
            "-b:a:0",
            "96k",
            "-map",
            "[v2out]",
            "-c:v:1",
            "libx264",
            "-preset",
            "ultrafast",
            "-b:v:1",
            "600k",
            "-map",
            "0:a?",
            "-c:a:1",
            "aac",
            "-b:a:1",
            "64k",
        ]

    command = (
        ["ffmpeg", "-re", "-i", INPUT_M3U8, "-filter_complex", filter_str]
        + bitrate_args
        + [
            "-f",
            "hls",
            "-hls_time",
            "4",
            "-hls_list_size",
            "5",
            "-hls_flags",
            "delete_segments+independent_segments",
            "-hls_segment_filename",
            os.path.join(OUTPUT_DIR, "stream_%v_%03d.ts"),
            "-master_pl_name",
            MASTER_NAME,
            "-var_stream_map",
            stream_map,
            os.path.join(OUTPUT_DIR, "stream_%v.m3u8"),
        ]
    )

    try:
        process = subprocess.Popen(command)
        process.wait()
    except Exception as e:
        print(f"Error procesando transmisión: {e}")


# --- 4. CONTROL DE SERVICIOS EN STREAMLIT ---
if "services_started" not in st.session_state:
    st.session_state["services_started"] = True
    threading.Thread(target=run_fastapi, daemon=True).start()
    threading.Thread(target=start_multi_bitrate_stream, daemon=True).start()

# --- 5. INTERFAZ WEB Y REPRODUCTOR INTERACTIVO ---
st.set_page_config(page_title="Señal TV Multicalidad", layout="wide")
st.title("📺 Transmisión Multicalidad ABR")

local_stream_url = f"http://localhost:{FASTAPI_PORT}/{MASTER_NAME}"
master_file_path = os.path.join(OUTPUT_DIR, MASTER_NAME)

if os.path.exists(master_file_path):
    st.success("Transmisión activa con detector de calidad automatizado")

    # Reproductor HTML5 optimizado para HLS con Video.js
    player_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://vjs.zencdn.net/8.3.0/video-js.css" rel="stylesheet" />
    </head>
    <body style="margin:0; background:black;">
      <video id="my-video" class="video-js vjs-default-skin vjs-big-play-centered" controls preload="auto" width="100%" height="450" data-setup='{{}}'>
        <source src="{local_stream_url}" type="application/x-mpegURL">
      </video>
      <script src="https://vjs.zencdn.net/8.3.0/video.min.js"></script>
    </body>
    </html>
    """
    st.components.v1.html(player_code, height=470)
    st.code(local_stream_url, language="text")
else:
    st.info("Analizando fuente e iniciando lista HLS... Espere un momento.")
    time.sleep(3)
    st.rerun()
