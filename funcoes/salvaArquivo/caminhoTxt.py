import os
from tkinter import Tk
from tkinter import filedialog


def selecionarCaminhoSalvarTxt(nome="ataDoProjetoA.txt") -> str:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    pastaPadrao = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "salvarArquivo")
    )
    os.makedirs(pastaPadrao, exist_ok=True)

    caminho = filedialog.asksaveasfilename(
        parent=root,
        title="Salvar Transcrição",
        initialdir=pastaPadrao,
        initialfile=nome,
        defaultextension=".txt",
        filetypes=[("Arquivo de Texto", "*.txt")],
    )

    root.update()
    root.destroy()
    return caminho