import os
import subprocess
import sys

# URL del stream de entrada
INPUT_M3U8 = "https://calm-forest-3478.cristianbracho904.workers.dev/master.m3u8"

# La carpeta DEBE llamarse 'static' para que Streamlit la exponga públicamente
OUTPUT_DIR = "static"
MASTER_NAME = "canalcstreaming0934.m3u8"


def start_multi_bitrate_stream():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(
        f"Iniciando procesamiento y guardando en public: {OUTPUT_DIR}/{MASTER_NAME}"
    )

    command = [
        "ffmpeg",
        "-re",
        "-i",
        INPUT_M3U8,
        # Renderizar resoluciones (1080p, 720p, 480p, 360p)
        "-filter_complex",
        "[0:v]split=4[v1,v2,v3,v4]; "
        "[v1]copy[v1out]; "
        "[v2]scale=w=1280:h=720[v2out]; "
        "[v3]scale=w=854:h=480[v3out]; "
        "[v4]scale=w=640:h=360[v4out]",
        # Configuración 1080p
        "-map",
        "[v1out]",
        "-c:v:0",
        "libx264",
        "-b:v:0",
        "4000k",
        "-maxrate:v:0",
        "4400k",
        "-bufsize:v:0",
        "6000k",
        "-map",
        "0:a?",
        "-c:a:0",
        "aac",
        "-b:a:0",
        "160k",
        # Configuración 720p
        "-map",
        "[v2out]",
        "-c:v:1",
        "libx264",
        "-b:v:1",
        "2200k",
        "-maxrate:v:1",
        "2500k",
        "-bufsize:v:1",
        "3300k",
        "-map",
        "0:a?",
        "-c:a:1",
        "aac",
        "-b:a:1",
        "128k",
        # Configuración 480p
        "-map",
        "[v3out]",
        "-c:v:2",
        "libx264",
        "-b:v:2",
        "1200k",
        "-maxrate:v:2",
        "1400k",
        "-bufsize:v:2",
        "1800k",
        "-map",
        "0:a?",
        "-c:a:2",
        "aac",
        "-b:a:2",
        "96k",
        # Configuración 360p
        "-map",
        "[v4out]",
        "-c:v:3",
        "libx264",
        "-b:v:3",
        "600k",
        "-maxrate:v:3",
        "700k",
        "-bufsize:v:3",
        "900k",
        "-map",
        "0:a?",
        "-c:a:3",
        "aac",
        "-b:a:3",
        "64k",
        # Parámetros HLS
        "-f",
        "hls",
        "-hls_time",
        "6",
        "-hls_playlist_type",
        "event",
        "-hls_flags",
        "independent_segments",
        "-hls_segment_filename",
        os.path.join(OUTPUT_DIR, "stream_%v_%03d.ts"),
        "-master_pl_name",
        MASTER_NAME,
        "-var_stream_map",
        "v:0,a:0,name:1080p v:1,a:1,name:720p v:2,a:2,name:480p v:3,a:3,name:360p",
        os.path.join(OUTPUT_DIR, "stream_%v.m3u8"),
    ]

    try:
        process = subprocess.Popen(command)
        process.wait()
    except KeyboardInterrupt:
        print("\nTransmisión detenida.")
        sys.exit(0)


if __name__ == "__main__":
    start_multi_bitrate_stream()
