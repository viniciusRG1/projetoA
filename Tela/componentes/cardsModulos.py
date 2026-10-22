import os
import customtkinter as ctk
from PIL import Image,ImageDraw
from Tela.constantes import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_CARD_DROP,
    COR_FUNDO,
    COR_SIDEBAR,
    COR_TEXTO_ESCURO,
    COR_VERMELHO,
    COR_VERMELHO_HOVER
)
from Tela.icones.icones import desenharIconeOnda, desenharIconeUpload


class CardsModulos(ctk.CTkFrame):

    def __init__(
        self, master, aoSelecionar, aoProcessar=None, aoLimpar=None, aoRemover=None
    ):
        super().__init__(master, fg_color=COR_FUNDO, corner_radius=0)
        self.aoSelecionar = aoSelecionar
        self.aoProcessar = aoProcessar
        self.aoLimpar = aoLimpar
        self.aoRemover = aoRemover
        self.arquivosAtuais = []
        self.iconeJoia = self._carregarIconeJoia()

        self.iconeUpload = desenharIconeUpload(64, COR_AZUL, "#FFFFFF")
        self.iconeAudio = desenharIconeOnda(48)
        self.iconeAudioArrasto = desenharIconeOnda(64)
        self.iconeX = self._carregarIconeX()

        self._montarLayout()
        #self._montarBotaoAjuda()

    def _carregarIconeJoia(self, tamanho=(64, 64)):
        caminho = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "icones", "joia.png")
        )
        if os.path.exists(caminho):
            img = Image.open(caminho).convert("RGBA")
            img = img.resize(tamanho, Image.Resampling.LANCZOS)

            mascara = Image.new("L", tamanho, 0)
            desenho = ImageDraw.Draw(mascara)
            raio = tamanho[0] // 5

            desenho.rounded_rectangle(
                (0, 0, tamanho[0], tamanho[1]), radius=raio, fill=255
            )
            img.putalpha(mascara)

            return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
        return None

    def _carregarIconeX(self):
        caminho = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "icones", "X.png")
        )
        if not os.path.exists(caminho):
            caminho = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "icones", "X")
            )
        if os.path.exists(caminho):
            img = Image.open(caminho)
            return ctk.CTkImage(light_image=img, dark_image=img, size=(14, 14))
        return None

    def _montarLayout(self):
        self.topoBarra = ctk.CTkFrame(self, fg_color="transparent")
        self.topoBarra.pack(fill="x", padx=45, pady=(16, 4))

        self.lblContagem = ctk.CTkLabel(
            self.topoBarra,
            text="",
            font=("Ubuntu", 16, "bold"),
            text_color=COR_TEXTO_ESCURO,
        )
        self.lblContagem.pack(side="left")

        self.containerDashed = ctk.CTkFrame(self, fg_color="transparent")
        self.containerDashed.pack(expand=True, fill="both", padx=45, pady=(0, 10))

        self.canvasDashed = ctk.CTkCanvas(
            self.containerDashed, bg=COR_FUNDO, highlightthickness=0
        )
        self.canvasDashed.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvasDashed.bind("<Configure>", self._redesenharAreaPontilhada)

        self.conteudoVazio = ctk.CTkFrame(self.containerDashed, fg_color=COR_CARD_DROP)
        self.conteudoVazio.place(relx=0.5, rely=0.5, anchor="center")

        self.btnUpload = ctk.CTkButton(
            self.conteudoVazio,
            text="",
            image=self.iconeUpload,
            width=64,
            height=64,
            fg_color="transparent",
            hover_color="#EFE3C6",
            command=self.aoSelecionar,
        )
        self.btnUpload.pack(pady=(0, 14))

        self.lblTitulo = ctk.CTkLabel(
            self.conteudoVazio,
            text="Arraste seu áudio para cá",
            font=("Arial", 20, "bold"),
            text_color=COR_TEXTO_ESCURO,
        )
        self.lblTitulo.pack(pady=(0, 4))

        linha = ctk.CTkFrame(self.conteudoVazio, fg_color=COR_CARD_DROP)
        linha.pack(pady=(0, 20))

        ctk.CTkLabel(linha, text="ou ", font=("Arial", 13), text_color="#5C6E82").pack(side="left")
        link = ctk.CTkLabel(
            linha,
            text="clique para selecionar",
            font=("Arial", 13, "bold"),
            text_color=COR_SIDEBAR,
            cursor="hand2",
        )
        link.pack(side="left")
        link.bind("<Button-1>", lambda _: self.aoSelecionar())
        ctk.CTkLabel(linha, text=" no seu computador", font=("Arial", 13), text_color="#5C6E82").pack(side="left")

        ctk.CTkLabel(
            self.conteudoVazio,
            text="MP3  •  WAV  •  M4A",
            font=("Arial", 11),
            text_color="#8F836F",
        ).pack()

        self.scrollArquivos = ctk.CTkScrollableFrame(
            self.containerDashed,
            fg_color=COR_CARD_DROP,
            corner_radius=0,
        )

        self.botoesBarra = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkButton(
            self.botoesBarra,
            text="Adicionar",
            font=("Arial", 12, "bold"),
            fg_color=COR_AZUL,
            border_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            height=36,
            command=self.aoSelecionar,
        ).pack(side="left", padx=(0, 10))

        if self.aoLimpar:
            ctk.CTkButton(
                self.botoesBarra,
                text="Limpar",
                font=("Arial", 12, "bold"),
                fg_color=COR_VERMELHO,
                hover_color=COR_VERMELHO_HOVER,
                height=36,
                command=self.aoLimpar,
            ).pack(side="left")

        if self.aoProcessar:
            self.btnProcessar = ctk.CTkButton(
                self.botoesBarra,
                text="Iniciar Transcrição",
                font=("Arial", 13, "bold"),
                fg_color=COR_AZUL,
                hover_color=COR_AZUL_HOVER,
                height=36,
                corner_radius=10,
                command=self.aoProcessar,
            )
            self.btnProcessar.pack(side="right")

    def destacarArrasto(self, ativo: bool):
        cor = COR_AZUL if ativo else "#5D87B8"
        if ativo:
            if self.iconeJoia:
                self.btnUpload.configure(image=self.iconeJoia)
            else:
                print("Ícone joia não carregado.")
            self.lblTitulo.configure(text="Solte o áudio aqui")
        else:
            self.btnUpload.configure(image=self.iconeUpload)
            self.lblTitulo.configure(text="Arraste seu áudio para cá")

        self.canvasDashed.itemconfig("borda_arco", outline=cor)
        self.canvasDashed.itemconfig("borda_linha", fill=cor)
    def _removerArquivo(self, caminho):
        if self.aoRemover:
            self.aoRemover(caminho)

    def atualizarVisual(self, listaArquivos: list):
        self.arquivosAtuais = list(listaArquivos)

        if not self.arquivosAtuais:
            self.lblContagem.configure(text="")
            self.scrollArquivos.place_forget()
            self.botoesBarra.pack_forget()
            self.conteudoVazio.place(relx=0.5, rely=0.5, anchor="center")
            return

        self.conteudoVazio.place_forget()

        total = len(self.arquivosAtuais)
        plural = "s" if total > 1 else ""
        self.lblContagem.configure(text=f"{total} arquivo{plural} carregado{plural}")

        for w in self.scrollArquivos.winfo_children():
            w.destroy()

        COLUNAS = 3
        for col in range(COLUNAS):
            self.scrollArquivos.grid_columnconfigure(col, weight=1)

        for idx, caminho in enumerate(self.arquivosAtuais):
            linha = idx // COLUNAS
            coluna = idx % COLUNAS
            nome = os.path.basename(caminho)

            cardItem = ctk.CTkFrame(
                self.scrollArquivos, fg_color="transparent", width=140
            )
            cardItem.grid(row=linha, column=coluna, padx=12, pady=8, sticky="n")

            topoCard = ctk.CTkFrame(
                cardItem, fg_color="transparent", height=20, width=140
            )
            topoCard.pack(fill="x")
            topoCard.pack_propagate(False)

            btnExcluir = ctk.CTkButton(
                topoCard,
                text="" if self.iconeX else "✕",
                image=self.iconeX,
                width=18,
                height=18,
                fg_color="transparent",
                hover_color="#FFB3B3",
                corner_radius=9,
                command=lambda c=caminho: self._removerArquivo(c),
            )
            btnExcluir.pack(side="right")

            ctk.CTkLabel(
                cardItem,
                text="",
                image=self.iconeAudio,
                width=48,
                height=48,
            ).pack(pady=(2, 6))

            ctk.CTkLabel(
                cardItem,
                text=nome,
                font=("Ubuntu", 14),
                text_color=COR_TEXTO_ESCURO,
                wraplength=140,
                justify="center",
            ).pack()

        self.scrollArquivos.place(
            relx=0.03, rely=0.04, relwidth=0.94, relheight=0.92
        )
        self.botoesBarra.pack(fill="x", padx=45, pady=(0, 20))

    def _redesenharAreaPontilhada(self, event=None):
        self.canvasDashed.delete("all")
        w = self.canvasDashed.winfo_width()
        h = self.canvasDashed.winfo_height()
        if w <= 30 or h <= 30:
            return

        pad, r = 2, 22
        d = r * 2
        corBorda = "#5D87B8"
        dash = (6, 5)

        x1, y1, x2, y2 = pad, pad, w - pad, h - pad

        self.canvasDashed.create_rectangle(x1 + r, y1, x2 - r, y2, fill=COR_CARD_DROP, outline="")
        self.canvasDashed.create_rectangle(x1, y1 + r, x2, y2 - r, fill=COR_CARD_DROP, outline="")
        self.canvasDashed.create_oval(x1, y1, x1 + d, y1 + d, fill=COR_CARD_DROP, outline="")
        self.canvasDashed.create_oval(x2 - d, y1, x2, y1 + d, fill=COR_CARD_DROP, outline="")
        self.canvasDashed.create_oval(x1, y2 - d, x1 + d, y2, fill=COR_CARD_DROP, outline="")
        self.canvasDashed.create_oval(x2 - d, y2 - d, x2, y2, fill=COR_CARD_DROP, outline="")

        self.canvasDashed.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, style="arc", outline=corBorda, width=2, dash=dash, tags="borda_arco")
        self.canvasDashed.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, style="arc", outline=corBorda, width=2, dash=dash, tags="borda_arco")
        self.canvasDashed.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, style="arc", outline=corBorda, width=2, dash=dash, tags="borda_arco")
        self.canvasDashed.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, style="arc", outline=corBorda, width=2, dash=dash, tags="borda_arco")

        self.canvasDashed.create_line(x1 + r, y1, x2 - r, y1, fill=corBorda, width=2, dash=dash, tags="borda_linha")
        self.canvasDashed.create_line(x2, y1 + r, x2, y2 - r, fill=corBorda, width=2, dash=dash, tags="borda_linha")
        self.canvasDashed.create_line(x2 - r, y2, x1 + r, y2, fill=corBorda, width=2, dash=dash, tags="borda_linha")
        self.canvasDashed.create_line(x1, y2 - r, x1, y1 + r, fill=corBorda, width=2, dash=dash, tags="borda_linha")
    def _montarBotaoAjuda(self):
        btnAjuda = ctk.CTkButton(
            self,
            text="?",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#FFFFFF",
            hover_color="#F0F0F0",
            text_color="#4B5563",
            font=("Arial", 14, "bold"),
        )
        btnAjuda.place(relx=0.96, rely=0.95, anchor="center")