import os
from pathlib import Path
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

DIRETORIO_ATUAL = Path(__file__).resolve().parent
ARQUIVO_BANCO = "../banco_vozes.pt"

def carregarBanco():
    if os.path.exists(ARQUIVO_BANCO):
        return torch.load(ARQUIVO_BANCO, map_location=device)
    return {}

def salvarBanco(banco):
    torch.save(banco, ARQUIVO_BANCO)

bancoVoz = carregarBanco()