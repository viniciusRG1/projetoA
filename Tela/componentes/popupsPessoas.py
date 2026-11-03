import os
from tkinter import filedialog
import customtkinter as ctk

from funcoes.AnalisadorDeAudio.analisarAudio import cadastrarPessoas
from funcoes.bancoDeVoz.bancoDeVoz import bancoVoz, salvarBanco
from Tela.constantes import (
    COR_AZUL,
    COR_AZUL_HOVER,
    COR_CARD_DROP,
    COR_FUNDO,
)

CAMINHO_ICO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "icones", "icone.ico")
)


def aplicarIcone(janela):
    if os.path.exists(CAMINHO_ICO):
        janela.after(200, lambda: janela.iconbitmap(CAMINHO_ICO))


class JanelaCadastrarPessoa(ctk.CTkToplevel):

    def __init__(self, master, aoSalvar=None):
        super().__init__(master)
        self.aoSalvar = aoSalvar
        self.caminhoAudio = ""

        self.title("Cadastrar Voz")
        self.geometry("380x330")
        self.resizable(False, False)
        self.configure(fg_color=COR_FUNDO)

        self.attributes("-topmost", False)
        self.after(100, self.lift)
        aplicarIcone(self)

        ctk.CTkLabel(
            self,
            text="Novo Cadastro de Voz",
            font=("Arial", 16, "bold"),
            text_color="#1F2937",
        ).pack(pady=(16, 10))

        self.txtNome = ctk.CTkEntry(
            self, placeholder_text="Nome da pessoa", width=300, height=36
        )
        self.txtNome.pack(pady=4)

        self.txtCargo = ctk.CTkEntry(
            self, placeholder_text="Cargo da pessoa", width=300, height=36
        )
        self.txtCargo.pack(pady=4)

        self.lblAudio = ctk.CTkLabel(
            self,
            text="Nenhum áudio selecionado",
            font=("Arial", 11),
            text_color="#5C6E82",
        )
        self.lblAudio.pack(pady=(4, 6))

        ctk.CTkButton(
            self,
            text="Selecionar Áudio de Amostra",
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            height=32,
            command=self._selecionarAmostra,
        ).pack(pady=4)

        ctk.CTkButton(
            self,
            text="Salvar no Banco",
            fg_color=COR_AZUL,
            hover_color=COR_AZUL_HOVER,
            height=36,
            width=300,
            command=self._salvar,
        ).pack(pady=(14, 0))

    def _selecionarAmostra(self):
        caminho = filedialog.askopenfilename(
            title="Áudio de Referência",
            filetypes=[("Áudio", "*.wav *.mp3 *.m4a *.ogg *.flac")],
        )
        if caminho:
            self.caminhoAudio = caminho
            self.lblAudio.configure(text=os.path.basename(caminho))

    def _salvar(self):
        nome = self.txtNome.get().strip()
        cargo = self.txtCargo.get().strip()
        if not nome or not cargo or not self.caminhoAudio:
            return

        cadastrarPessoas(nome, cargo, self.caminhoAudio)

        if self.aoSalvar:
            self.aoSalvar()
        self.destroy()


class JanelaListarPessoas(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Vozes Cadastradas")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=COR_FUNDO)

        self.attributes("-topmost", False)
        self.after(100, self.lift)
        aplicarIcone(self)

        ctk.CTkLabel(
            self,
            text="Vozes Cadastradas",
            font=("Arial", 16, "bold"),
            text_color="#1F2937",
        ).pack(pady=(14, 8))

        self.scroll = ctk.CTkScrollableFrame(
            self, width=350, height=270, fg_color=COR_CARD_DROP
        )
        self.scroll.pack(padx=16, pady=8, fill="both", expand=True)

        self._renderizarLista()

    def _renderizarLista(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not bancoVoz:
            ctk.CTkLabel(
                self.scroll,
                text="Nenhuma pessoa cadastrada.",
                text_color="#5C6E82",
            ).pack(pady=20)
            return

        for nome, dados in bancoVoz.items():
            cargo = (
                dados.get("cargo", "Sem cargo")
                if isinstance(dados, dict)
                else "Sem cargo"
            )

            linha = ctk.CTkFrame(self.scroll, fg_color="#EDE3CE", height=42)
            linha.pack(fill="x", pady=4, padx=4)
            linha.pack_propagate(False)

            infoFrame = ctk.CTkFrame(linha, fg_color="transparent")
            infoFrame.pack(side="left", padx=10, fill="y")

            ctk.CTkLabel(
                infoFrame,
                text=nome,
                font=("Arial", 12, "bold"),
                text_color="#1F2937",
            ).pack(anchor="w")

            ctk.CTkLabel(
                infoFrame,
                text=cargo,
                font=("Arial", 10),
                text_color="#5C6E82",
            ).pack(anchor="w")

            ctk.CTkButton(
                linha,
                text="✕",
                width=24,
                height=24,
                fg_color="transparent",
                text_color="#882222",
                hover_color="#FFB3B3",
                command=lambda n=nome: self._remover(n),
            ).pack(side="right", padx=6)

    def _remover(self, nome):
        if nome in bancoVoz:
            del bancoVoz[nome]
            salvarBanco(bancoVoz)
            self._renderizarLista()