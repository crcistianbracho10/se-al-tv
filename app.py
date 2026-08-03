import os
import subprocess
import threading
import streamlit as st
import streamlit.components.v1 as components

# Configuración de URLs
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"
RTMP_DESTINATION = (
    "rtmp://us-central-ch.livepush.io/live/rtmp_ebf057998c85491e9bc445c709e7077b"
)


# Proceso de retransmisión con re-escalado a 480p optimizado
def start_rtmp_480p_stream():
    command = [
        "ffmpeg",
        "-re",
        "-i",
        INPUT_M3U8,
        # Re-escalar a 480p (854x480)
        "-vf",
        "scale=854:480",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",  # Mínimo uso de CPU
        "-tune",
        "zerolatency",
        "-b:v",
        "800k",  # Bitrate ideal para 480p
        "-maxrate",
        "900k",
        "-bufsize",
        "1200k",
        "-g",
        "48",  # Keyframe interval para estabilidad en RTMP
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-ar",
        "44100",
        "-f",
        "flv",
        RTMP_DESTINATION,
    ]

    try:
        process = subprocess.Popen(command)
        process.wait()
    except Exception as e:
        print(f"Error reenviando señal a Livepush: {e}")


# Control del hilo en segundo plano
if "rtmp_started" not in st.session_state:
    st.session_state["rtmp_started"] = True
    threading.Thread(target=start_rtmp_480p_stream, daemon=True).start()


# Interfaz en Streamlit
st.set_page_config(page_title="Señal TV 480p - Livepush", layout="wide")
st.title("📺 Señal TV - Retransmisión Livepush (480p)")

st.success(" Transmisión activa y enviando a Livepush en 480p.")

st.info(
    "La señal se está enviando a tu servidor RTMP. Revisa el panel de Livepush para obtener tu enlace HLS/M3U8 o reproductor embebido."
)
