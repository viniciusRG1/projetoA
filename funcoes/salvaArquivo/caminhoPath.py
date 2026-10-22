import json
import os

ARQUIVO_CONFIG = "config.json"



def carregarPastaSalva() -> str:
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("pasta_atas", "")
        except Exception:
            return ""
    return ""


def salvarPastaConfig(caminho: str):
    dados = {"pasta_atas": caminho}
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")