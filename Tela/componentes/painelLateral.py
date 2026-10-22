import os
import threading
from datetime import datetime
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

from funcoes.salvaArquivo.gerarArquivo import gerarAtaCompleta
from Tela.constantes import (
    COR_AMARELO,
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_SIDEBAR,
    COR_SIDEBAR_ACTIVE,
    COR_SIDEBAR_HOVER,
    COR_TEXTO_MUTED,
)
from Tela.icones.icones import desenharIconeOnda, desenharIconePasta
from Tela.componentes.popupsPessoas import (
    JanelaCadastrarPessoa,
    JanelaListarPessoas,
)

CAMINHO_ICO_DENTRO_JANELA = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "icones", "iconeDentroDaJanela.png")
)

if os.path.exists(CAMINHO_ICO_DENTRO_JANELA):
    _img = Image.open(CAMINHO_ICO_DENTRO_JANELA)
    ICONE_TOPO = ctk.CTkImage(light_image=_img, dark_image=_img, size=(36, 36))
else:
    ICONE_TOPO = None


class PainelLateral(ctk.CTkFrame):

    def __init__(self, master, aoSelecionarPasta=None, aoProcessarNovo=None):
        super().__init__(master, width=280, fg_color=COR_SIDEBAR, corner_radius=0)
        self.pack_propagate(False)
        self.aoSelecionarPasta = aoSelecionarPasta
        self.aoProcessarNovo = aoProcessarNovo
        self.itensRegistados = []

        self.iconeAmarelo = desenharIconeOnda(36, COR_AMARELO, "#1E50A0")
        self.iconeAtivo = desenharIconeOnda(32, COR_AMARELO, "#1E50A0")
        self.iconeInativo = desenharIconeOnda(32, "#9E2322", COR_TEXTO_MUTED)
        self.iconePasta = desenharIconePasta(18, "#FFFFFF")

        self._montarTopo()
        self._montarRodape()
        self._montarLista()

    def atualizarStatus(self, texto: str):
        if hasattr(self, "lblStatusTexto"):
            self.lblStatusTexto.configure(text=texto)

    def iniciarProgresso(self, mensagem="Iniciando..."):
        def _iniciar():
            self.barraProgresso.set(0.0)
            self.barraProgresso.pack(fill="x", pady=(0, 8), before=self.blocoStatus)
            self.atualizarStatus(mensagem)

        self.after(0, _iniciar)

    def atualizarProgresso(self, porcentagem: float, mensagem: str):
        def _atualizar():
            valor = max(0.0, min(1.0, float(porcentagem)))
            self.barraProgresso.set(valor)
            self.atualizarStatus(mensagem)

        self.after(0, _atualizar)

    def finalizarProgresso(self, mensagem="Concluído com sucesso!"):
        def _finalizar():
            self.barraProgresso.pack_forget()
            self.atualizarStatus(mensagem)

        self.after(1500, _finalizar)

    def atualizarLista(self):
        pasta = getattr(self, "pastaAtual", None)
        if not pasta or not os.path.exists(pasta):
            pasta = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "salvarArquivo")
            )
        self.after(0, lambda: self.carregarDocumentos(pasta))

    def _gerarAtaDeTxt(self):
        caminhoTxt = filedialog.askopenfilename(
            title="Selecionar Transcrição",
            filetypes=[("Arquivo de Texto", "*.txt")],
        )
        if not caminhoTxt:
            return

        pastaDestino = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "salvarArquivo")
        )
        os.makedirs(pastaDestino, exist_ok=True)

        nomeBase = os.path.splitext(os.path.basename(caminhoTxt))[0]
        caminhoDocx = os.path.join(pastaDestino, f"{nomeBase}_Ata.docx")

        self.iniciarProgresso("Iniciando processo...")

        def tarefa():
            try:
                gerarAtaCompleta(
                    caminhoTxt, caminhoDocx, callbackProgresso=self.atualizarProgresso
                )
                self.atualizarLista()
                self.finalizarProgresso("Ata salva com sucesso!")
            except Exception as erro:
                self.finalizarProgresso("Erro ao gerar ata.")
                print(f"Erro: {erro}")

        threading.Thread(target=tarefa, daemon=True).start()

    def _montarTopo(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=20, pady=(24, 20))

        ctk.CTkLabel(
            topo, text="", image=ICONE_TOPO, width=36, height=36
        ).pack(side="left")

        ctk.CTkLabel(
            topo, text="painel de reuniões", font=("Arial", 15, "bold"), text_color="#FFFFFF"
        ).pack(side="left", padx=(10, 0))

    def _montarLista(self):
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            cabecalho, text="ÚLTIMAS TRANSCRIÇÕES", font=("Arial", 10, "bold"), text_color=COR_TEXTO_MUTED
        ).pack(side="left")

        self.badgeQtd = ctk.CTkLabel(
            cabecalho, text="00", width=26, height=18, corner_radius=9,
            fg_color="#A32423", text_color=COR_TEXTO_MUTED, font=("Arial", 10, "bold")
        )
        self.badgeQtd.pack(side="right")

        self.scrollLista = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#881C1B",
        )
        self.scrollLista.pack(fill="both", expand=True, padx=6, pady=(0, 8))

    def carregarDocumentos(self, caminhoPasta: str):
        if not os.path.exists(caminhoPasta):
            return

        self.pastaAtual = caminhoPasta
        arquivos = [
            f for f in os.listdir(caminhoPasta)
            if f.lower().endswith(".docx") and not f.startswith("~$")
        ]

        arquivos.sort(
            key=lambda x: os.path.getmtime(os.path.join(caminhoPasta, x)),
            reverse=True,
        )

        for w in self.scrollLista.winfo_children():
            w.destroy()

        self.itensRegistados.clear()
        self.badgeQtd.configure(text=f"{len(arquivos):02d}")

        for arq in arquivos:
            caminhoCompleto = os.path.join(caminhoPasta, arq)
            dataMod = datetime.fromtimestamp(os.path.getmtime(caminhoCompleto))
            subtitulo = dataMod.strftime("%d %b, %H:%M")
            titulo = os.path.splitext(arq)[0]

            self._adicionarItem(titulo, subtitulo, caminhoCompleto)

    def _selecionarItem(self, itemAlvo, iconeAlvo, caminho):
        for item, icone in self.itensRegistados:
            item.configure(fg_color="transparent")
            icone.configure(image=self.iconeInativo)
            item.ativo = False

        itemAlvo.configure(fg_color=COR_SIDEBAR_ACTIVE)
        iconeAlvo.configure(image=self.iconeAtivo)
        itemAlvo.ativo = True

        try:
            os.startfile(caminho)
        except Exception:
            pass

    def _adicionarItem(self, titulo: str, subtitulo: str, caminhoArquivo: str):
        item = ctk.CTkFrame(self.scrollLista, fg_color="transparent", corner_radius=12, height=60)
        item.pack(fill="x", padx=8, pady=3)
        item.pack_propagate(False)
        item.ativo = False

        lblIcone = ctk.CTkLabel(item, text="", image=self.iconeInativo, width=32, height=32)
        lblIcone.pack(side="left", padx=(10, 8))

        textos = ctk.CTkFrame(item, fg_color="transparent")
        textos.pack(side="left", fill="both", expand=True, pady=8)

        lblTit = ctk.CTkLabel(
            textos, text=titulo, font=("Ubuntu", 11, "bold"), text_color="#FFFFFF", anchor="w"
        )
        lblTit.pack(fill="x")

        lblSub = ctk.CTkLabel(
            textos, text=subtitulo, font=("Arial", 9), text_color=COR_TEXTO_MUTED, anchor="w"
        )
        lblSub.pack(fill="x")

        self.itensRegistados.append((item, lblIcone))

        def aoEntrar(e):
            if not getattr(item, "ativo", False):
                item.configure(fg_color=COR_SIDEBAR_HOVER)

        def aoSair(e):
            if not getattr(item, "ativo", False):
                item.configure(fg_color="transparent")

        componentes = [item, lblIcone, textos, lblTit, lblSub]
        for comp in componentes:
            comp.bind("<Enter>", aoEntrar)
            comp.bind("<Leave>", aoSair)
            comp.bind("<Button-1>", lambda _: self._selecionarItem(item, lblIcone, caminhoArquivo))
            comp.configure(cursor="hand2")

    def _montarRodape(self):
        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=20, pady=(0, 16))

        config = {
            "font": ("Ubuntu", 12, "bold"),
            "fg_color": COR_AZUL,
            "hover_color": COR_AZUL_HOVER,
            "height": 40,
            "corner_radius": 10,
        }

        ctk.CTkButton(
            rodape,
            text="Cadastrar Pessoa",
            command=lambda: JanelaCadastrarPessoa(self),
            **config,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            rodape,
            text="Ver Cadastrados",
            command=lambda: JanelaListarPessoas(self),
            **config,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            rodape,
            text="Gerar Ata",
            command=self._gerarAtaDeTxt,
            **config,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            rodape,
            text="  Selecionar pasta das atas",
            image=self.iconePasta,
            compound="left",
            command=self.aoSelecionarPasta,
            **config,
        ).pack(fill="x", pady=(0, 12))

        self.barraProgresso = ctk.CTkProgressBar(
            rodape,
            width=240,
            height=10,
            progress_color=COR_AZUL,
            fg_color="#EDE3CE",
        )

        self.blocoStatus = ctk.CTkFrame(rodape, fg_color="transparent")
        self.blocoStatus.pack(anchor="w")

        ctk.CTkLabel(
            self.blocoStatus, text="●", font=("Arial", 14), text_color=COR_AMARELO
        ).pack(side="left", padx=(2, 8))

        self.lblStatusTexto = ctk.CTkLabel(
            self.blocoStatus,
            text="Sistema pronto para transcrever",
            font=("Ubuntu", 12, "bold"),
            text_color="#FFFFFF",
        )
        self.lblStatusTexto.pack(side="left")