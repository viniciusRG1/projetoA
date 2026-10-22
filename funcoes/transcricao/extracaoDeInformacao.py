import json
import re
import ollama


def limparJson(texto: str) -> str:
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL)
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    return match.group(0) if match else texto.strip()


def removerFrasesDuplicadas(texto: str) -> str:
    if not texto:
        return ""
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    frasesUnicas = []
    vistas = set()

    for f in frases:
        fLimpa = f.strip()
        fNorm = fLimpa.lower()
        if fNorm and fNorm not in vistas:
            vistas.add(fNorm)
            frasesUnicas.append(fLimpa)

    return " ".join(frasesUnicas)


def limitarCincoPalavras(texto: str) -> str:
    palavras = texto.strip().split()[:5]
    return " ".join(palavras)


def extrairParticipantesDoTxt(textoBruto: str) -> list:
    padrao = r"\]\s*([^(\n:]+?)(?:\s*\(|:)"
    encontrados = re.findall(padrao, textoBruto)

    nomesValidos = set()
    for nome in encontrados:
        limpo = nome.strip()
        if limpo and limpo.lower() != "desconhecido":
            nomesValidos.add(limpo)

    if not nomesValidos:
        return [{"nome": "Participante", "cargo": "-"}]

    return [{"nome": n, "cargo": "Participante"} for n in sorted(nomesValidos)]


def extrairMetadados(textoBruto: str):
    dia, horario = "--/--/----", "--:--"
    m = re.search(
        r"Data de reunião:\s*(\d{2}/\d{2}/\d{4})\s*às\s*(\d{2}:\d{2})", textoBruto
    )
    if m:
        dia, horario = m.group(1), m.group(2)
    return dia, horario


def comprimirTexto(textoBruto: str) -> list:
    linhasLimpas = []
    vistas = set()

    for linha in textoBruto.splitlines():
        txt = linha.strip()
        if not txt or "Data de reunião:" in txt:
            continue
        txt = re.sub(r"\s*\([^)]*\)", "", txt)
        txt = re.sub(r"\[\d{2}:\d{2}\s*até\s*\d{2}:\d{2}\]\s*", "", txt).strip()

        txtNorm = txt.lower()
        if txt and txtNorm not in vistas:
            vistas.add(txtNorm)
            linhasLimpas.append(txt)

    return linhasLimpas


def quebrarEmLotes(linhas: list, tamanhoLote: int = 24) -> list:
    lotes = []
    for i in range(0, len(linhas), tamanhoLote):
        lote = "\n".join(linhas[i : i + tamanhoLote])
        lotes.append(lote)
    return lotes if lotes else [""]


def processarLote(loteTexto: str, modelo: str) -> dict:
    prompt = f"""
Trecho de reunião:
\"\"\"
{loteTexto}
\"\"\"

Extraia tópicos e decisões deste trecho sem repetir frases.
Defina um título de no máximo 5 palavras.
Responda exclusivamente em JSON:
{{
  "titulo": "Frase de até cinco palavras",
  "temas": [
    {{"tema": "Tópico", "situacao": "Discussão e argumentos"}}
  ],
  "decisoes": [
    {{"acao": "Ação", "responsavel": "Responsável", "prazo": "Prazo", "status": "Status"}}
  ]
}}
"""

    resp = ollama.chat(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={
            "temperature": 0.0,
            "num_predict": 1024,
            "num_ctx": 2048,
        },
        keep_alive=0,
    )

    try:
        dados = json.loads(limparJson(resp["message"]["content"]))
        for t in dados.get("temas", []):
            t["situacao"] = removerFrasesDuplicadas(t.get("situacao", ""))
        return dados
    except Exception:
        return {"titulo": "", "temas": [], "decisoes": []}


def sintetizarMacroTemas(temasBrutos: list, modelo: str) -> tuple:
    if len(temasBrutos) <= 1:
        for t in temasBrutos:
            t["situacao"] = removerFrasesDuplicadas(t.get("situacao", ""))
        return "Alinhamento Geral de Operações", temasBrutos

    textoTemas = ""
    for t in temasBrutos:
        sitLimpa = removerFrasesDuplicadas(t.get("situacao", ""))
        textoTemas += f"- Tema: {t.get('tema')}\n  Situação: {sitLimpa}\n"

    prompt = f"""
Temas extraídos:
\"\"\"
{textoTemas}
\"\"\"

1. Crie no campo "subtitulo" uma frase de NO MÁXIMO 5 PALAVRAS que resuma o assunto principal da reunião.
2. Agrupe os itens em macro-assuntos sem frases repetidas no campo "temas".

Responda exclusivamente em JSON:
{{
  "subtitulo": "Frase até cinco palavras",
  "temas": [
    {{"tema": "Título do Macro-Assunto", "situacao": "Síntese dos argumentos e contexto sem repetições"}}
  ]
}}
"""

    resp = ollama.chat(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={
            "temperature": 0.0,
            "num_predict": 1024,
            "num_ctx": 2048,
        },
        keep_alive=0,
    )

    subtitulo = "Alinhamento Geral da Reunião"
    try:
        dados = json.loads(limparJson(resp["message"]["content"]))
        macroTemas = dados.get("temas", [])
        if dados.get("subtitulo"):
            subtitulo = dados["subtitulo"]
        if not macroTemas:
            macroTemas = temasBrutos
    except Exception:
        macroTemas = temasBrutos

    for mt in macroTemas:
        mt["situacao"] = removerFrasesDuplicadas(mt.get("situacao", ""))

    return limitarCincoPalavras(subtitulo), macroTemas


def mesclarLotes(resultados: list, modelo: str) -> dict:
    temasBrutos = []
    decisoesTodas = []
    acoesVistas = set()

    for r in resultados:
        for t in r.get("temas", []):
            if t.get("tema") and t.get("situacao"):
                temasBrutos.append(t)

        for d in r.get("decisoes", []):
            acao = removerFrasesDuplicadas(d.get("acao", "")).strip()
            acaoNorm = acao.lower()
            if acaoNorm and acaoNorm not in acoesVistas:
                acoesVistas.add(acaoNorm)
                d["acao"] = acao
                decisoesTodas.append(d)

    subtituloFinal, temasConsolidados = sintetizarMacroTemas(temasBrutos, modelo)

    for dec in decisoesTodas:
        if not dec.get("responsavel"):
            dec["responsavel"] = "Equipe"
        if not dec.get("prazo"):
            dec["prazo"] = "A definir"
        if not dec.get("status"):
            dec["status"] = "Pendente"

    if not temasConsolidados:
        temasConsolidados = [
            {"tema": "Geral", "situacao": "Discussão e alinhamento dos pontos tratados."}
        ]

    if not decisoesTodas:
        decisoesTodas = [
            {
                "acao": "Dar andamento às pautas",
                "responsavel": "Equipe",
                "prazo": "Próxima reunião",
                "status": "Em andamento",
            }
        ]

    return {
        "titulo": "ATA de Reunião",
        "subtitulo": subtituloFinal,
        "temas": temasConsolidados,
        "decisoes": decisoesTodas,
    }


def extrairDadosComLlm(
    caminhoTxt: str, modelo="llama3.2:3b", callbackProgresso=None
) -> dict:
    if callbackProgresso:
        callbackProgresso(0.1, "Lendo arquivo...")

    with open(caminhoTxt, "r", encoding="utf-8") as f:
        bruto = f.read()

    dia, horario = extrairMetadados(bruto)
    participantes = extrairParticipantesDoTxt(bruto)
    linhas = comprimirTexto(bruto)
    lotes = quebrarEmLotes(linhas, tamanhoLote=24)

    totalLotes = len(lotes)
    resultadosLotes = []

    for idx, lote in enumerate(lotes):
        if callbackProgresso:
            progressoAtual = 0.2 + (0.5 * (idx / totalLotes))
            callbackProgresso(progressoAtual, f"Processando lote {idx + 1} de {totalLotes}...")

        res = processarLote(lote, modelo)
        resultadosLotes.append(res)

    if callbackProgresso:
        callbackProgresso(0.75, "Consolidando macro-assuntos...")

    dadosFinais = mesclarLotes(resultadosLotes, modelo)

    if callbackProgresso:
        callbackProgresso(0.9, "Finalizando montagem...")

    dadosFinais["dia"] = dia
    dadosFinais["horario"] = horario
    dadosFinais["participantes"] = participantes

    return dadosFinais