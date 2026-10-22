import torch
import numpy as np
from faster_whisper import WhisperModel
#from recipes.DNS.noisyspeech_synthesizer.audiolib import segmental_snr_mixer

promptExtra = ("Reunião de operações: PCP, KLP, PIP, sistema Sankhya, relatórios de BI, "
    "fábricas de Uberlândia e Rio Verde, software Mitra, ponto eletrônico, EPIs, ")

class TranscricaoWhisper:
    def __init__(self, tamanho_modelo="medium", initial_prompt=promptExtra):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device =="cuda" else "int8"
        self.initial_prompt = initial_prompt
        self.modelo = WhisperModel(
            tamanho_modelo,
            device=self.device,
            compute_type=self.compute_type
        )

    def transcreverParte(self, audio_array: np.ndarray)-> str:
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)

        if len(audio_array) < 8000:
            return ""

        segmentos, _ = self.modelo.transcribe(
            audio_array,
            language="pt",
            initial_prompt=self.initial_prompt,
            beam_size=5,
            vad_filter=False,
            condition_on_previous_text=False
        )

        textoFinal = " ".join([seg.text.strip() for seg in segmentos]).strip()
        return textoFinal