import os
import subprocess
import threading
import streamlit as st

# Configuración de URLs y Token
INPUT_M3U8 = "https://cristianbracho9047-lista-reproduccion.hf.space/hls/index.m3u8"
RTMP_DESTINATION = "rtmp://ssh101.bozztv.com/ssh101/canalczulia"
HF_TOKEN = "a56b7ad1426888f0491438f8384eda3101559a579294c04b38a0722767300449"

# Proceso de retransmisión directa (copia exacta sin procesar)
def start_direct_stream():
    command = [
        "ffmpeg",
        "-re",
        "-headers", f"Authorization: Bearer {HF_TOKEN}",
        "-i", INPUT_M3U8,
        "-c", "copy",  # Copia directa sin re-escalar ni gastar CPU
        "-f", "flv",
        RTMP_DESTINATION,
    ]

    try:
        process = subprocess.Popen(command)
        process.wait()
    except Exception as e:
        print(f"Error en la retransmisión: {e}")

# Control del hilo en segundo plano
if "rtmp_started" not in st.session_state:
    st.session_state["rtmp_started"] = True
    threading.Thread(target=start_direct_stream, daemon=True).start()

# Interfaz en Streamlit
st.set_page_config(page_title="Retransmisión Directa - Canal Zulia", layout="wide")
st.title("📺 Retransmisión Directa (Modo Copia)")

st.success("Transmisión iniciada en segundo plano enviando la señal tal cual al servidor RTMP.")

st.markdown(f"""
### Detalles:
- **Origen:** `{INPUT_M3U8}`
- **Destino:** `{RTMP_DESTINATION}`
- **Método:** Copia directa (`-c copy`) para consumo mínimo de recursos.
""")
