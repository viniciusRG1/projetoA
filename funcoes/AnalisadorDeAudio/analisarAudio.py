from datetime import datetime
import gc
import os
import warnings
import ollama
from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.utils.fetching import LocalStrategy
import torch
import torch.nn.functional as F

from funcoes.bancoDeVoz.bancoDeVoz import bancoVoz, salvarBanco
from funcoes.carregarEtratarAudio.carregar.Audio import carregarAudio
from funcoes.salvaArquivo.caminhoTxt import selecionarCaminhoSalvarTxt
from funcoes.carregarEtratarAudio.tratar.formatador import formatarTempo
from funcoes.carregarEtratarAudio.tratar.sincronizarAudio import (
    sincronizarMultiplosAudios,
)
from funcoes.transcricao.transcricao import TranscricaoWhisper
from funcoes.salvaArquivo.gerarArquivo import gerarAtaCompleta

warnings.filterwarnings("ignore", category=FutureWarning, module="torch.jit")

device = "cuda" if torch.cuda.is_available() else "cpu"
KHZ = 16000

modeloVad, utilitarios = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False,
    onnx=False,
    verbose=False,
)
getSpeechTimestamps = utilitarios[0]

reconhecerVoz = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="./tmpdir",
    run_opts={"device": device},
    local_strategy=LocalStrategy.COPY,
)


def _detectarFala(waveform):
    waveNorm = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
    wavParaVad = waveNorm.squeeze().cpu().float()
    return getSpeechTimestamps(
        wavParaVad,
        modeloVad,
        sampling_rate=KHZ,
        threshold=0.4,
        min_speech_duration_ms=300,
        min_silence_duration_ms=500,
    )


def cadastrarPessoas(nome, cargo, caminhoAudio):
    waveform = carregarAudio(caminhoAudio)
    intervalosFala = _detectarFala(waveform)

    if not intervalosFala:
        print(f"Erro: Nenhuma fala detectada no áudio de {nome}.")
        return

    inicioReal = intervalosFala[0]["start"]
    fimReal = intervalosFala[-1]["end"]
    waveformLimpa = waveform[:, inicioReal:fimReal].to(device)

    with torch.no_grad():
        embedding = reconhecerVoz.encode_batch(waveformLimpa).squeeze(0)
        embedding = F.normalize(embedding, p=2, dim=-1)

        bancoVoz[nome] = {"cargo": cargo, "embedding": embedding.cpu()}
        salvarBanco(bancoVoz)

    print(f"{nome} ({cargo}) cadastrado com sucesso.")


def analisarAudio(
    dadosEntrada, limiar=0.3, taxaAtualizacao=0.10, callbackProgresso=None
):
    if not bancoVoz:
        print("Erro: Cadastre pelo menos uma pessoa antes de analisar.")
        return None

    if callbackProgresso:
        callbackProgresso(0.05, "Limpando VRAM...")

    try:
        ollama.generate(model="qwen2.5:1.5b", keep_alive=0)
    except Exception:
        pass

    caminhosAudios = []
    if isinstance(dadosEntrada, dict):
        caminhosAudios.extend(
            dadosEntrada.get("Online", []) or dadosEntrada.get("teams", [])
        )
        caminhosAudios.extend(dadosEntrada.get("presenciais", []))
    elif isinstance(dadosEntrada, list):
        caminhosAudios = dadosEntrada
    elif isinstance(dadosEntrada, str):
        caminhosAudios = [dadosEntrada]

    caminhosAudios = [
        c for c in caminhosAudios if not c.lower().endswith(".vtt")
    ]
    if not caminhosAudios:
        print("Nenhum arquivo de áudio fornecido.")
        return None

    if callbackProgresso:
        callbackProgresso(0.10, "Carregando gravações...")

    sr = KHZ
    waveformsBrutas = [carregarAudio(caminho) for caminho in caminhosAudios]

    if callbackProgresso:
        callbackProgresso(0.15, "Sincronizando áudios...")

    waveformsAlinhadas = sincronizarMultiplosAudios(waveformsBrutas)

    if len(waveformsAlinhadas) > 1:
        mix = torch.mean(torch.stack(waveformsAlinhadas), dim=0)
    else:
        mix = waveformsAlinhadas[0]

    if callbackProgresso:
        callbackProgresso(0.20, "Detectando falas...")

    intervalosFala = _detectarFala(mix)
    if not intervalosFala:
        print("Nenhuma fala detectada.")
        return None

    limiteAmostras = 30 * sr

    intervalosAjustados = []
    for fala in intervalosFala:
        inicio = fala["start"]
        fim = fala["end"]
        while (fim - inicio) > limiteAmostras:
            corte = inicio + limiteAmostras
            intervalosAjustados.append({"start": inicio, "end": corte})
            inicio = corte
        if (fim - inicio) >= (sr * 0.3):
            intervalosAjustados.append({"start": inicio, "end": fim})

    if callbackProgresso:
        callbackProgresso(0.25, "Carregando Whisper...")

    transcritor = TranscricaoWhisper(tamanho_modelo="medium")

    cos = torch.nn.CosineSimilarity(dim=-1)
    waveformsGpu = [wf.to(device) for wf in waveformsAlinhadas]
    bancoVozGpu = {
        nome: dados["embedding"].to(device) for nome, dados in bancoVoz.items()
    }

    linhasTexto = ["Ata de Reunião"]
    dataAtual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    linhasTexto.append(f"Data de reunião:{dataAtual}\n")

    atualizacoesFeitas = 0
    totalFalasProcessadas = 0
    totalTrechos = len(intervalosAjustados)

    for idx, fala in enumerate(intervalosAjustados):
        if callbackProgresso and totalTrechos > 0:
            prog = 0.25 + 0.50 * (idx / totalTrechos)
            callbackProgresso(
                prog, f"Transcrevendo fala {idx + 1} de {totalTrechos}..."
            )

        inicio = fala["start"]
        fim = fala["end"]
        inicioSeg = inicio / sr
        fimSeg = fim / sr

        melhorScoreGlobal = -1.0
        quemFalouGlobal = "Desconhecido"
        canalVencedor = 1
        embMelhorCanal = None

        for idxCanal, wfCanal in enumerate(waveformsGpu):
            trechoVoz = wfCanal[:, inicio:fim]
            with torch.no_grad():
                embTrecho = reconhecerVoz.encode_batch(trechoVoz).squeeze(0)
                embTrecho = F.normalize(embTrecho, p=2, dim=-1)

            for nome, embBase in bancoVozGpu.items():
                score = cos(embTrecho, embBase).item()
                if score > melhorScoreGlobal:
                    melhorScoreGlobal = score
                    canalVencedor = idxCanal + 1
                    embMelhorCanal = embTrecho
                    if score >= limiar:
                        quemFalouGlobal = nome

        timeInicio = formatarTempo(inicioSeg)
        timeFim = formatarTempo(fimSeg)

        if quemFalouGlobal != "Desconhecido" and embMelhorCanal is not None:
            embAtual = bancoVozGpu[quemFalouGlobal]
            novaEmb = (
                1.0 - taxaAtualizacao
            ) * embAtual + taxaAtualizacao * embMelhorCanal
            novaEmbNorm = F.normalize(novaEmb, p=2, dim=-1)
            bancoVozGpu[quemFalouGlobal] = novaEmbNorm
            bancoVoz[quemFalouGlobal]["embedding"] = novaEmbNorm.cpu()
            atualizacoesFeitas += 1

        trechoVencedorTensor = waveformsAlinhadas[canalVencedor - 1][
            :, inicio:fim
        ]
        trechoVencedorNp = trechoVencedorTensor.squeeze().cpu().numpy()
        textoFala = transcritor.transcreverParte(trechoVencedorNp)

        rotuloCanal = (
            f"Celular {canalVencedor}"
            if len(waveformsGpu) > 1
            else "Canal Único"
        )
        print(f"[{timeInicio} - {timeFim}] {quemFalouGlobal}")

        if textoFala:
            cargoFalante = (
                bancoVoz[quemFalouGlobal].get("cargo", "")
                if isinstance(bancoVoz.get(quemFalouGlobal), dict)
                else ""
            )
            rotuloFalante = (
                f"{quemFalouGlobal} - {cargoFalante}"
                if cargoFalante
                else quemFalouGlobal
            )

            linhasTexto.append(
                f"[{timeInicio} até {timeFim}] {rotuloFalante} ({rotuloCanal} | Confiança: {melhorScoreGlobal:.2f})"
            )
            linhasTexto.append(f'"{textoFala}"\n')
            totalFalasProcessadas += 1

    del transcritor.modelo
    del transcritor
    del waveformsGpu
    del bancoVozGpu
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if atualizacoesFeitas > 0:
        salvarBanco(bancoVoz)

    if totalFalasProcessadas > 0:
        if callbackProgresso:
            callbackProgresso(0.75, "Salvando arquivo TXT...")

        dataSugerida = datetime.now().strftime("%Y%m%d_%H%M")
        caminhoSalvar = selecionarCaminhoSalvarTxt(
            f"Transcricao_{dataSugerida}.txt"
        )

        if caminhoSalvar:
            with open(caminhoSalvar, "w", encoding="utf-8") as f:
                f.write("\n".join(linhasTexto))

            caminhoDocx = caminhoSalvar.replace(".txt", "_Ata.docx")

            def progressoAta(p, msg):
                if callbackProgresso:
                    progReal = 0.75 + (p * 0.25)
                    callbackProgresso(progReal, msg)

            gerarAtaCompleta(
                caminhoSalvar, caminhoDocx, callbackProgresso=progressoAta
            )
            return caminhoDocx
        return None
    return None