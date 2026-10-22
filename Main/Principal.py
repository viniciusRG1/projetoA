import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from funcoes.link.controlador import iniciar

if __name__ == "__main__":
    iniciar()
