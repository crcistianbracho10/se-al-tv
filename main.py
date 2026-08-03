import os
import subprocess
import sys

# URL del stream de entrada (tu enlace M3U8)
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"

# URL de salida RTMP (es recomendable usar variables de entorno para las claves)
RTMP_URL = os.getenv(
    "OPENCASTER_RTMP_URL",
    "rtmp://vs20.live.opencaster.com/opencaster/cristianhilos_314b91b0?psk=cristianhilos_314b91b0&tk=b77f89cbf4f83af5295e37a562a3379de814c3a945e7402811a589c00d91f442"
)

def start_retransmission():
    print(f"Iniciando retransmisión desde:\n -> {INPUT_M3U8}")
    print("Enviando flujo a Opencaster RTMP...")

    # Comando FFmpeg optimizado para M3U8 -> RTMP
    command = [
        "ffmpeg",
        "-re",                           # Lee el HLS a velocidad de tiempo real
        "-i", INPUT_M3U8,                 # Entrada M3U8
        "-c:v", "copy",                   # Copia el video sin re-codificar (ahorra mucha CPU)
        "-c:a", "aac",                    # Codifica audio a AAC por seguridad
        "-b:a", "128k",                   # Bitrate de audio
        "-f", "flv",                      # Formato requerido para RTMP
        RTMP_URL
    ]

    try:
        process = subprocess.Popen(command)
        process.wait()
    except KeyboardInterrupt:
        print("\nTransmisión detenida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error durante la transmisión: {e}")

if __name__ == "__main__":
    start_retransmission()
