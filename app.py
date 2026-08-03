import time
import mux_python
import streamlit as st
import streamlit.components.v1 as components

# Configuración de credenciales de Mux (Idealmente guardarlas en Secrets de Streamlit)
TOKEN_ID = "33702d41-b878-4adf-ae53-000feb1fc90c"
SECRET_KEY = (
    "uT202zast8MbgFdeEwBxU3h2wdlZZ2JMkAYbgTJy97H6TPS5TmCCTS/JAw2F5Fw5T3muEK33V0z"
)

# Enlace de origen que quieres transmitir
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"

st.set_page_config(page_title="Señal TV - Mux Live", layout="wide")
st.title("📺 Señal TV - Transmisión con Mux Video")


@st.cache_resource
def setup_mux_asset(input_url):
    """Crea un Asset en Mux a partir de tu URL M3U8 y obtiene el Playback ID."""
    # Configurar cliente API de Mux
    configuration = mux_python.Configuration()
    configuration.username = TOKEN_ID
    configuration.password = SECRET_KEY

    assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))

    # Definir el recurso de entrada con política pública
    input_settings = [mux_python.InputSettings(url=input_url)]
    create_asset_request = mux_python.CreateAssetRequest(
        input=input_settings, playback_policy=[mux_python.PlaybackPolicy.PUBLIC]
    )

    # Crear el asset en Mux
    asset = assets_api.create_asset(create_asset_request)

    # Esperar unos segundos a que Mux genere el Playback ID
    asset_id = asset.data.id
    while True:
        asset_info = assets_api.get_asset(asset_id)
        if asset_info.data.status == "ready":
            playback_id = asset_info.data.playback_ids[0].id
            return playback_id
        elif asset_info.data.status == "errored":
            return None
        time.sleep(2)


# Obtener o procesar el ID de Mux
with st.spinner("Conectando señal con Mux Video..."):
    try:
        playback_id = setup_mux_asset(INPUT_M3U8)
    except Exception as e:
        st.error(f"Error conectando con la API de Mux: {e}")
        playback_id = None

if playback_id:
    # URL directa del archivo M3U8 entregado por Mux
    mux_m3u8_url = f"https://stream.mux.com/{playback_id}.m3u8"

    st.success(" Transmisión lista y optimizada por Mux")

    st.subheader("Enlace M3U8 directo para IPTV / Reproductores:")
    st.code(mux_m3u8_url, language="text")

    # Reproductor web oficial de Mux (Mux Player)
    mux_player_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/@mux/mux-player"></script>
    </head>
    <body style="margin:0; background-color: black;">
      <mux-player
        playback-id="{playback_id}"
        metadata-video-title="Señal TV"
        stream-type="on-demand"
        autoplay
        style="width: 100%; height: 480px;">
      </mux-player>
    </body>
    </html>
    """

    components.html(mux_player_html, height=500)
else:
    st.error(
        "No se pudo procesar el flujo de video en Mux. Revisa que la URL de origen esté activa."
    )
