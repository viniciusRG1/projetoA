import os
import subprocess
import tempfile
import torch
import soundfile as sf


def carregarAudio(caminho):
    arquivo_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    caminho_temp = arquivo_temp.name
    arquivo_temp.close()

    try:
        comando = [
            "ffmpeg",
            "-y",
            "-i", caminho,
            "-ar", "16000",
            "-ac", "1",
            caminho_temp
        ]
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        dados, sr = sf.read(caminho_temp, dtype='float32')
        waveform = torch.from_numpy(dados).unsqueeze(0)

        return waveform
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)
