from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from funcoes.padraoAta.estilizacaoWord import (
    adicionarLinhaDivisoria,
    aplicarBordasTabela,
    formatarCabecalhoTabela,
    formatarLinhaDados,
)
from funcoes.transcricao.extracaoDeInformacao import extrairDadosComLlm


def _criarTabela(doc, cabecalhos, larguras, dadosLinhas):
    tabela = doc.add_table(rows=1, cols=len(cabecalhos))
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    aplicarBordasTabela(tabela)

    for i, texto in enumerate(cabecalhos):
        tabela.rows[0].cells[i].paragraphs[0].text = texto
    formatarCabecalhoTabela(tabela.rows[0], larguras)

    for linha in dadosLinhas:
        row = tabela.add_row()
        for i, val in enumerate(linha):
            row.cells[i].paragraphs[0].text = str(val or "-")
        formatarLinhaDados(row, larguras)


def gerarWordEstilizado(dados: dict, caminhoSalvar: str):
    doc = Document()

    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = Inches(0.8)
        sec.left_margin = sec.right_margin = Inches(0.8)

    pTit = doc.add_paragraph()
    pTit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pTit.paragraph_format.space_after = Pt(2)

    rTit = pTit.add_run("ATA de Reunião")
    rTit.font.bold = True
    rTit.font.size = Pt(16)
    rTit.font.color.rgb = RGBColor(31, 56, 100)

    pSub = doc.add_paragraph()
    pSub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pSub.paragraph_format.space_after = Pt(4)
    rData = pSub.add_run(
        f"Horário: {dados.get('horario', '--:--')} Dia: {dados.get('dia', '--/--/----')}"
    )
    rData.font.italic = True
    rData.font.size = Pt(9.5)

    adicionarLinhaDivisoria(doc)

    participantes = [
        [p.get("nome", ""), p.get("cargo", "Participante")]
        for p in dados.get("participantes", [])
    ]
    _criarTabela(doc, ["Participantes", "Cargo"], [Inches(3.35), Inches(3.35)], participantes)

    pTema = doc.add_paragraph()
    pTema.paragraph_format.space_before = Pt(14)
    pTema.paragraph_format.space_after = Pt(4)
    rTema = pTema.add_run("1. Temas abordados na reunião")
    rTema.font.bold = True
    rTema.font.size = Pt(11)
    adicionarLinhaDivisoria(doc)

    temas = [
        [t.get("tema", ""), t.get("situacao", "")]
        for t in dados.get("temas", [])
    ]
    _criarTabela(doc, ["Tema", "Situação"], [Inches(2.2), Inches(4.5)], temas)

    pDec = doc.add_paragraph()
    pDec.paragraph_format.space_before = Pt(14)
    pDec.paragraph_format.space_after = Pt(4)
    rDec = pDec.add_run("2. Decisões Tomadas")
    rDec.font.bold = True
    rDec.font.size = Pt(11)
    adicionarLinhaDivisoria(doc)

    decisoes = [
        [
            d.get("acao", ""),
            d.get("responsavel", ""),
            d.get("prazo", ""),
            d.get("status", ""),
        ]
        for d in dados.get("decisoes", [])
    ]
    _criarTabela(
        doc,
        ["Ação", "Responsável", "Prazo", "Status"],
        [Inches(3.0), Inches(1.5), Inches(1.0), Inches(1.2)],
        decisoes,
    )

    doc.save(caminhoSalvar)


def gerarAtaCompleta(caminhoTxt: str, caminhoSalvarDocx: str, callbackProgresso=None):
    dados = extrairDadosComLlm(caminhoTxt, callbackProgresso=callbackProgresso)

    if callbackProgresso:
        callbackProgresso(0.9, "Gravando arquivo Word...")

    gerarWordEstilizado(dados, caminhoSalvarDocx)

    if callbackProgresso:
        callbackProgresso(1.0, "Concluído com sucesso!")