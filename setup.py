import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

PACOTES = [
    "torch",
    "torchaudio",
    "faster-whisper",
    "speechbrain",
    "customtkinter",
    "tkinterdnd2",
    "Pillow",
    "python-docx",
    "ollama",
    "soundfile",
    "scipy",
    "numpy",
]


def instalarPacotes():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        check=False,
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install"] + PACOTES, check=False
    )


def baixarFfmpeg():
    if shutil.which("ffmpeg") or os.path.exists("ffmpeg.exe"):
        return

    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zipTemp = "ffmpeg_temp.zip"

    urllib.request.urlretrieve(url, zipTemp)
    with zipfile.ZipFile(zipTemp, "r") as z:
        for membro in z.namelist():
            if membro.endswith("ffmpeg.exe"):
                with z.open(membro) as src, open("ffmpeg.exe", "wb") as dst:
                    shutil.copyfileobj(src, dst)
                break

    if os.path.exists(zipTemp):
        os.remove(zipTemp)


def configurarOllama():
    if not shutil.which("ollama"):
        subprocess.run(
            ["winget", "install", "-e", "--id", "Ollama.Ollama", "--silent"],
            check=False,
        )
        time.sleep(5)

    subprocess.run(["ollama", "pull", "llama3.2:3b"], check=False)


def baixarModelos():
    import torch
    from faster_whisper import WhisperModel
    from speechbrain.inference.speaker import SpeakerRecognition

    torch.hub.load(
        repo_or_dir="snakers4/silero-vad:v4.0",
        model="silero_vad",
        force_reload=False,
        onnx=False,
        verbose=False,
    )

    SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="./tmpdir",
    )

    WhisperModel("medium", device="cpu", compute_type="int8")


if __name__ == "__main__":
    instalarPacotes()
    baixarFfmpeg()
    configurarOllama()
    baixarModelos()
