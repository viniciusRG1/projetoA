import os
import threading
from funcoes.AnalisadorDeAudio.analisarAudio import analisarAudio
from Tela.dashboardTk import DashboardApp


def processarReuniao(listaArquivos, app):
    dados = {
        "tipo": "presencial",
        "teams": [],
        "presenciais": listaArquivos,
    }
    try:
        caminhoDocx = analisarAudio(
            dados,
            callbackProgresso=app.painelLateral.atualizarProgresso,
        )

        if caminhoDocx and os.path.exists(caminhoDocx):
            app.painelLateral.finalizarProgresso("Ata gerada com sucesso!")
            pasta = os.path.dirname(caminhoDocx)
            app.after(0, lambda: app.painelLateral.carregarDocumentos(pasta))
        else:
            app.painelLateral.finalizarProgresso("Concluído!")
    except Exception as e:
        app.painelLateral.finalizarProgresso(f"Erro: {e}")
        print(f"Erro no processamento: {e}")


def iniciar():
    app = None

    def aoDisparar(arquivos):
        app.painelLateral.iniciarProgresso("Iniciando transcrição...")
        threading.Thread(
            target=processarReuniao,
            args=(arquivos, app),
            daemon=True,
        ).start()

    app = DashboardApp(callbackProcessar=aoDisparar)
    app.mainloop()


if __name__ == "__main__":
    iniciar()
