import os
import subprocess
import streamlit as st

st.set_page_config(page_title="Retransmisor RTMP Automático", layout="centered")

st.title("Retransmisor Automático HLS a RTMP")
st.write("La señal se está retransmitiendo en segundo plano de manera automática.")

# Configuración de URLs y Token
default_hls = "https://cristianbracho9047-lista-reproduccion.hf.space/hls/index.m3u8"
default_rtmp = "rtmp://ssh101.bozztv.com/ssh101/canalczulia"
default_token = "a56b7ad1426888f0491438f8384eda3101559a579294c04b38a0722767300449"

# Campos editables en la interfaz por si necesitas ajustarlos
hls_url = st.text_input("URL del Stream HLS de Origen:", value=default_hls)
rtmp_url = st.text_input("URL del Servidor RTMP de Destino:", value=default_rtmp)
hf_token = st.text_input("Token de Hugging Face:", type="password", value=default_token)

# Inicializar el estado del proceso si no existe
if "process" not in st.session_state:
    st.session_state.process = None

# Función para iniciar la retransmisión automáticamente
def iniciar_transmision():
    if st.session_state.process is None or st.session_state.process.poll() is not None:
        ffmpeg_cmd = [
            "ffmpeg",
            "-headers", f"Authorization: Bearer {hf_token}",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "5",
            "-i", hls_url,
            "-c", "copy",
            "-f", "flv",
            rtmp_url
        ]
        try:
            st.session_state.process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except Exception as e:
            st.error(f"Error al iniciar FFmpeg: {e}")
            return False
    return True

# Auto-ejecución al cargar la app por primera vez
if st.session_state.process is None:
    iniciar_transmision()

# Panel de control manual para detener o reiniciar si es necesario
col1, col2 = st.columns(2)

with col1:
    if st.button("Reiniciar Transmisión"):
        if st.session_state.process is not None and st.session_state.process.poll() is None:
            st.session_state.process.terminate()
        iniciar_transmision()
        st.success("Transmisión reiniciada.")

with col2:
    if st.button("Detener Transmisión"):
        if st.session_state.process is not None and st.session_state.process.poll() is None:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.success("Transmisión detenida manualmente.")
        else:
            st.info("Ya se encuentra detenida.")

# Mostrar estado actual en pantalla
if st.session_state.process is not None and st.session_state.process.poll() is None:
    st.success("Estado: 🟢 Retransmitiendo en vivo automáticamente.")
else:
    st.warning("Estado: 🔴 Detenido.")
