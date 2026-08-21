import os
import subprocess
import threading
import streamlit as st

# Configuración de URLs y Token
INPUT_M3U8 = "https://cristianbracho9047-lista-reproduccion.hf.space/hls/index.m3u8"
RTMP_DESTINATION = "rtmp://ssh101.bozztv.com/ssh101/canalczulia"
HF_TOKEN = "a56b7ad1426888f0491438f8384eda3101559a579294c04b38a0722767300449"

# Variable global para guardar los logs de FFmpeg
if "ffmpeg_logs" not in st.session_state:
    st.session_state["ffmpeg_logs"] = "Esperando inicio..."

def run_stream():
    command = [
        "ffmpeg",
        "-re",
        "-headers", f"Authorization: Bearer {HF_TOKEN}",
        "-i", INPUT_M3U8,
        "-c", "copy",
        "-f", "flv",
        RTMP_DESTINATION,
    ]

    try:
        # Ejecutamos y capturamos el error (stderr de ffmpeg)
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True
        )
        
        # Leemos la salida de error en tiempo real
        for line in process.stderr:
            st.session_state["ffmpeg_logs"] = line
            print(line) # También sale en la consola del servidor
            
        process.wait()
    except Exception as e:
        st.session_state["ffmpeg_logs"] = f"Error crítico: {e}"

# Control del hilo en segundo plano
if "rtmp_started" not in st.session_state:
    st.session_state["rtmp_started"] = True
    threading.Thread(target=run_stream, daemon=True).start()

# Interfaz en Streamlit
st.set_page_config(page_title="Depuración - Retransmisión", layout="wide")
st.title("📺 Estado y Depuración de la Retransmisión")

st.success("El hilo de retransmisión está activo. Revisa el registro de abajo para ver si FFmpeg logró conectar.")

st.markdown(f"""
### Configuración actual:
- **Origen:** `{INPUT_M3U8}`
- **Destino:** `{RTMP_DESTINATION}`
""")

st.subheader("🛠️ Registro de FFmpeg (Última línea recibida):")
st.code(st.session_state["ffmpeg_logs"])

# Botón para refrescar la página y ver si cambió el log
if st.button("Actualizar estado"):
    st.rerun()
