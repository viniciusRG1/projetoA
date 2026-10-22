# 🎙️ Painel de Reuniões: Transcrição, Biometria Vocal e Atas com IA

Sistema desktop local e privado para transcrição automatizada de reuniões presenciais e online, identificação biométrica de locutores por voz e sumarização executiva em formato Word (`.docx`) utilizando modelos de inteligência artificial de ponta.

---

## 🚀 Funcionalidades

- **Identificação Biométrica de Voz (Diarização):** Cadastro prévio de locutores e identificação automática de quem falou em cada trecho por similaridade de cosseno.
- **Detecção de Atividade de Voz (VAD):** Filtro inteligente de silêncios e ruídos de fundo via Silero VAD.
- **Sincronização Multicanal:** Alinhamento temporal via correlação cruzada de gravações feitas por múltiplos dispositivos (ex.: microfones de celulares distintos no mesmo ambiente).
- **Transcrição de Alta Precisão:** Reconhecimento acústico em língua portuguesa acelerado via CTranslate2.
- **Geração Executiva de Atas:**
  - Extração semântica em lotes (24 frases por bloco), ideal para máquinas com 8 GB de RAM.
  - Consolidação automática em **macro-assuntos** sem repetições.
  - Subtítulo resumido de até 5 palavras ao lado do cabeçalho.
  - Matriz de ações e decisões com responsáveis e prazos definidos.
- **Privacidade Total:** 100% do processamento roda localmente na máquina, sem envio de áudio ou texto para APIs de terceiros.

---

## 🧠 Modelos e Tecnologias

| Função | Modelo / Tecnologia | Mantenedor |
| :--- | :--- | :--- |
| **Interface Gráfica** | CustomTkinter + TkinterDnD2 | Comunidade Open-Source |
| **Processamento de Áudio** | FFmpeg & SciPy | FFmpeg / SciPy |
| **Deteção de Voz (VAD)** | Silero VAD (v4.0) | Silero Team |
| **Biometria Vocal** | ECAPA-TDNN (`spkrec-ecapa-voxceleb`) | SpeechBrain (Mila) |
| **Transcrição (ASR)** | Faster-Whisper (`medium` - int8) | OpenAI / SYSTRAN |
| **Estruturação da Ata** | Llama 3.2 (3B) | Meta AI (via Ollama) |
| **Geração de Documentos** | python-docx | Python-Docx Team |

---

## 📋 Pré-requisitos

1. **Python 3.12 (64-bit)**
2. **FFmpeg** instalado e adicionado às variáveis de ambiente (PATH) ou com o binário `ffmpeg.exe` na raiz do projeto.
3. **Ollama** instalado e em execução no sistema.

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Criar e ativar o ambiente virtual (Python 3.12)
```bash
# Windows (CMD)
py -3.12 -m venv .venv
.venv\Scripts\activate.bat

# Windows (PowerShell)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar o PyTorch

- **Para máquinas sem placa de vídeo (apenas CPU):**
  ```bash
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  ```

- **Para máquinas com GPU NVIDIA (CUDA 12.1):**
  ```bash
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```

### 4. Instalar as demais dependências
```bash
pip install -r requirements.txt
```

### 5. Baixar o modelo no Ollama
Abra um terminal e execute:
```bash
ollama pull llama3.2:3b
```

---

## 📂 Estrutura de Pastas

```text
├── Main/
│   └── Principal.py               # Ponto de entrada da aplicação
├── Tela/
│   ├── componentes/
│   │   ├── cardsModulos.py        # Área de drag-and-drop e listagem de áudios
│   │   ├── painelLateral.py       # Menu lateral, histórico de atas e barra de progresso
│   │   └── popupsPessoas.py       # Janelas de cadastro e visualização de vozes
│   ├── constantes.py              # Paleta de cores e temas visuais
│   ├── dashboardTk.py             # Janela principal (CustomTkinter)
│   └── icones/                    # Ícones e recursos gráficos
├── funcoes/
│   ├── AnalisadorDeAudio/
│   │   └── analisarAudio.py       # Pipeline de VAD, biometria e transcrição
│   ├── bancoDeVoz/
│   │   └── bancoDeVoz.py          # Gestão do banco de vetores (banco_vozes.pt)
│   ├── carregarEtratarAudio/      # Decodificação com FFmpeg e sincronização de áudios
│   ├── padraoAta/                 # Estilização visual de tabelas e bordas do Word
│   ├── salvaArquivo/              # Exportação de arquivos TXT e DOCX
│   └── transcricao/
│       ├── extracaoDeInformacao.py# Extração em lotes e geração de atas via LLM
│       └── transcricao.py         # Módulo Faster-Whisper
├── controlador.py                 # Orquestração entre a interface e os módulos
├── requirements.txt               # Lista de pacotes do Python
└── README.md                      # Manual do projeto
```

---

## 🖥️ Como Executar

Com o Ollama rodando em segundo plano e a `.venv` ativada:

```bash
python Main/Principal.py
```

### Passo a passo básico:
1. **Cadastrar Vozes:** Clique em *Cadastrar Pessoa*, informe o nome e selecione um áudio curto de amostra da voz da pessoa (sem sobreposição de vozes).
2. **Carregar Reunião:** Arraste um ou mais áudios da reunião para o centro da tela (ou clique para selecionar).
3. **Iniciar Processo:** Clique em *Iniciar Transcrição*. O sistema fará a sincronização, transcrição, diarização e gerará automaticamente a ata em `.docx`.
4. **Gerar Ata de TXT Avulso:** Caso já tenha uma transcrição pronta em formato `.txt`, utilize o botão *Gerar Ata de TXT* no painel lateral.