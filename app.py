import os
import subprocess
import streamlit as st

st.set_page_config(page_title="Retransmisor RTMP", layout="centered")

st.title("Panel de Retransmisión de Señal")
st.write("Herramienta para retransmitir desde HLS hacia RTMP sin generar sobrecarga visual local.")

# Configuración de URLs y Tokens
default_hls = "https://cristianbracho9047-lista-reproduccion.hf.space/hls/index.m3u8"
default_rtmp = "rtmp://ssh101.bozztv.com/ssh101/canalczulia"

hls_url = st.text_input("URL del Stream HLS de Origen:", value=default_hls)
rtmp_url = st.text_input("URL del Servidor RTMP de Destino:", value=default_rtmp)
hf_token = st.text_input("Token de Hugging Face (si el espacio es privado):", type="password", value="a56b7ad1426888f0491438f8384eda3101559a579294c04b38a0722767300449")

if "process" not in st.session_state:
    st.session_state.process = None

col1, col2 = st.columns(2)

with col1:
    if st.button("Iniciar Retransmisión", type="primary"):
        if st.session_state.process is None or st.session_state.process.poll() is not None:
            # Comando FFmpeg para retransmitir sin decodificar video (copia directa -reconnect)
            # Si se requiere autenticación con token en Hugging Face, se pasa en los headers de entrada de FFmpeg
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
                # Ejecutar el proceso en segundo plano
                st.session_state.process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                st.success("¡Retransmisión iniciada correctamente hacia el servidor RTMP!")
            except Exception as e:
                st.error(f"Error al iniciar FFmpeg: {e}")
        else:
            st.warning("La retransmisión ya se encuentra activa.")

with col2:
    if st.button("Detener Retransmisión"):
        if st.session_state.process is not None and st.session_state.process.poll() is None:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.success("Retransmisión detenida.")
        else:
            st.info("No hay ninguna retransmisión activa en este momento.")

# Estado actual
if st.session_state.process is not None and st.session_state.process.poll() is None:
    st.info("Estado: Transmitiendo señal en vivo...")
else:
    st.warning("Estado: Detenido.")
