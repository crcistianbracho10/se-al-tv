import os
import subprocess
import threading
import streamlit as st

# Configuración de URLs y Token
INPUT_M3U8 = "https://cristianbracho9047-lista-reproduccion.hf.space/hls/index.m3u8"
RTMP_DESTINATION = "rtmp://ssh101.bozztv.com/ssh101/canalczulia"
HF_TOKEN = "a56b7ad1426888f0491438f8384eda3101559a579294c04b38a0722767300449"

if "ffmpeg_logs" not in st.session_state:
    st.session_state["ffmpeg_logs"] = "Esperando inicio..."

def run_stream():
    # Construimos el argumento de headers correctamente para FFmpeg
    # Usamos -headers para pasar el token de autorización Bearer de Hugging Face
    header_string = f"Authorization: Bearer {HF_TOKEN}\r\n"
    
    command = [
        "ffmpeg",
        "-re",
        "-headers", header_string,
        "-i", INPUT_M3U8,
        "-c", "copy",
        "-f", "flv",
        RTMP_DESTINATION,
    ]

    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True
        )
        
        for line in process.stderr:
            st.session_state["ffmpeg_logs"] = line
            print(line)
            
        process.wait()
    except Exception as e:
        st.session_state["ffmpeg_logs"] = f"Error crítico: {e}"

# Control del hilo en segundo plano
if "rtmp_started" not in st.session_state:
    st.session_state["rtmp_started"] = True
    threading.Thread(target=run_stream, daemon=True).start()

# Interfaz en Streamlit
st.set_page_config(page_title="Retransmisión Protegida - Canal Zulia", layout="wide")
st.title("📺 Retransmisión HLS Protegida a RTMP")

st.success("El proceso de retransmisión se ha lanzado en segundo plano.")

st.markdown(f"""
### Configuración:
- **Origen (con token):** `{INPUT_M3U8}`
- **Destino RTMP:** `{RTMP_DESTINATION}`
""")

st.subheader("🛠️ Registro de actividad de FFmpeg:")
st.code(st.session_state["ffmpeg_logs"])

if st.button("Actualizar registros"):
    st.rerun()
