from tkinter import filedialog


def selecionarArquivos():
    caminhos = filedialog.askopenfilenames(
        title="Selecionar Áudios",
        filetypes=[
            ("Arquivos de Áudio", "*.mp3 *.wav *.m4a *.ogg *.aac *.flac *.mp4 *.vtt"),
            ("Todos os Arquivos", "*.*"),
        ],
    )
    return list(caminhos)
