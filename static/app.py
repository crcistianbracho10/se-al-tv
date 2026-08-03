import os
import streamlit as st

st.set_page_config(page_title="Señal TV Live", layout="wide")

st.title("📺 Señal TV - Transmisión en Vivo")

# URL relativa pública generada por Streamlit
public_m3u8_url = "app/static/canalcstreaming0934.m3u8"
full_public_url = (
    "https://senal-tv03.streamlit.app/app/static/canalcstreaming0934.m3u8"
)

st.subheader("Enlace directo M3U8 para IPTV / Reproductores:")
st.code(full_public_url, language="text")

# Mostrar el video en la misma página de Streamlit
if os.path.exists(os.path.join("static", "canalcstreaming0934.m3u8")):
    st.video(public_m3u8_url)
else:
    st.info("Iniciando flujo de video... Por favor refresca en unos segundos.")
