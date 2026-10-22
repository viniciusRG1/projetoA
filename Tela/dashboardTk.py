import ctypes
import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD

from funcoes.carregarEtratarAudio.carregar.SelecionarArquivoDeAudio import (
    selecionarArquivos,
)
from Tela.componentes.cardsModulos import CardsModulos
from Tela.componentes.painelLateral import PainelLateral
from Tela.constantes import COR_FUNDO
import json

ARQUIVO_CONFIG = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
)

ctk.set_appearance_mode("light")


def _carregarPastaConfig() -> str:
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f).get("pasta_atas", "")
        except Exception:
            return ""
    return ""


def _salvarPastaConfig(caminho: str):
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump({"pasta_atas": caminho}, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


class DashboardApp(ctk.CTk, TkinterDnD.DnDWrapper):

    def __init__(
        self,
        callbackProcessar=None,
        callbackSalvarPasta=None,
        pastaInicial="",
    ):
        try:
            meuAppId = "painel.reunioes.sistema.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(meuAppId)
        except Exception:
            pass

        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("painel de reuniões")
        self.geometry("1000x560")
        self.configure(fg_color=COR_FUNDO)
        self.resizable(False, False)

        pastaIcones = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "icones")
        )

        caminhoIco = os.path.join(pastaIcones, "icone.ico")


        if os.path.exists(caminhoIco):
            self.iconbitmap(caminhoIco)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.arquivos = []
        self.callbackProcessar = callbackProcessar
        self.callbackSalvarPasta = callbackSalvarPasta

        self.painelLateral = PainelLateral(
            self,
            aoSelecionarPasta=self.definirPastaAtas,
            aoProcessarNovo=self._dispararProcessamento,
        )
        self.painelLateral.grid(row=0, column=0, sticky="nsew")

        self.areaPrincipal = CardsModulos(
            self,
            aoSelecionar=self.carregarArquivos,
            aoProcessar=self._dispararProcessamento,
            aoLimpar=self.limparArquivos,
            aoRemover=self.removerArquivo,
        )
        self.areaPrincipal.grid(row=0, column=1, sticky="nsew")

        alvoDrop = self.areaPrincipal.containerDashed
        alvoDrop.drop_target_register(DND_FILES)
        alvoDrop.dnd_bind("<<DropEnter>>", self._aoArrastarEntrar)
        alvoDrop.dnd_bind("<<DropLeave>>", self._aoArrastarSair)
        alvoDrop.dnd_bind("<<Drop>>", self._aoSoltarArquivos)

        pastaAuto = pastaInicial or _carregarPastaConfig()
        if pastaAuto and os.path.exists(pastaAuto):
            self.painelLateral.carregarDocumentos(pastaAuto)

    def _aoArrastarEntrar(self, event):
        self.areaPrincipal.destacarArrasto(True)

    def _aoArrastarSair(self, event):
        self.areaPrincipal.destacarArrasto(False)

    def _aoSoltarArquivos(self, event):
        self.areaPrincipal.destacarArrasto(False)
        extensoes = (".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac", ".mp4", ".vtt")
        caminhos = self.tk.splitlist(event.data)
        for c in caminhos:
            if c.lower().endswith(extensoes) and c not in self.arquivos:
                self.arquivos.append(c)
        self.areaPrincipal.atualizarVisual(self.arquivos)

    def removerArquivo(self, caminho):
        if caminho in self.arquivos:
            self.arquivos.remove(caminho)
            self.areaPrincipal.atualizarVisual(self.arquivos)

    def limparArquivos(self):
        self.arquivos.clear()
        self.areaPrincipal.atualizarVisual(self.arquivos)

    def _dispararProcessamento(self):
        if not self.arquivos:
            self.carregarArquivos()
            return

        if self.callbackProcessar:
            self.callbackProcessar(list(self.arquivos))

    def atualizarStatus(self, texto: str):
        self.painelLateral.atualizarStatus(texto)

    def definirPastaAtas(self):
        pastaAtual = _carregarPastaConfig()
        caminho = filedialog.askdirectory(
            title="Selecionar pasta das Atas",
            initialdir=pastaAtual if os.path.exists(pastaAtual) else None,
        )
        if caminho:
            _salvarPastaConfig(caminho)
            if self.callbackSalvarPasta:
                self.callbackSalvarPasta(caminho)
            self.painelLateral.carregarDocumentos(caminho)

    def carregarArquivos(self):
        novos = selecionarArquivos()
        if novos:
            for c in novos:
                if c not in self.arquivos:
                    self.arquivos.append(c)
            self.areaPrincipal.atualizarVisual(self.arquivos)

