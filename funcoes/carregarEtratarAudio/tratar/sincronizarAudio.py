import numpy as np
from scipy import signal

def calcular_lag(ancora_np, audio_np):
    correlacao = signal.correlate(ancora_np, audio_np, mode="full", method="fft")
    lags = signal.correlation_lags(len(ancora_np), len(audio_np), mode="full")
    return lags[np.argmax(correlacao)]

def sincronizarMultiplosAudios(waveforms, sr=16000, segundos_analise=30):
    if len(waveforms) <= 1:
        return waveforms

    amostras_analise = segundos_analise * sr
    ancora = waveforms[0].squeeze().cpu().numpy()[:amostras_analise]
    ancora = ancora - np.mean(ancora)

    lags = [0]
    for i in range(1, len(waveforms)):
        atual = waveforms[i].squeeze().cpu().numpy()[:amostras_analise]
        atual = atual - np.mean(atual)
        lags.append(calcular_lag(ancora, atual))

    inicio_comum_ancora = max(0, max(lags))
    pontos_inicio = [inicio_comum_ancora - lag for lag in lags]

    duracoes_restantes = [
        waveforms[i].shape[1] - pontos_inicio[i]
        for i in range(len(waveforms))
    ]
    duracao_minima = min(duracoes_restantes)

    waveforms_alinhadas = []
    for i in range(len(waveforms)):
        ini = pontos_inicio[i]
        fim = ini + duracao_minima
        waveforms_alinhadas.append(waveforms[i][:, ini:fim])

    return waveforms_alinhadas