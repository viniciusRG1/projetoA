from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Pt, RGBColor
from Tela.constantes import (
    COR_BORDA,
    COR_AZUL_2,
    COR_CREME

)



def definirFundoCelula(celula, corHex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{corHex}"/>')
    celula._tc.get_or_add_tcPr().append(shading)


def aplicarBordasTabela(tabela):
    tblPr = tabela._tbl.tblPr
    bordas = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
        f"</w:tblBorders>"
    )
    tblPr.append(bordas)


def adicionarLinhaDivisoria(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    pBrd = parse_xml(
        f'<w:pBrd {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="{COR_AZUL_2}"/></w:pBrd>'
    )
    p._p.get_or_add_pPr().append(pBrd)


def formatarCabecalhoTabela(linha, larguras=None):
    for i, celula in enumerate(linha.cells):
        definirFundoCelula(celula, COR_AZUL_2)
        celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        if larguras and i < len(larguras):
            celula.width = larguras[i]
        for p in celula.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.name = "Calibri"
                r.font.size = Pt(10)


def formatarLinhaDados(linha, larguras=None):
    for i, celula in enumerate(linha.cells):
        definirFundoCelula(celula, COR_CREME)
        celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        if larguras and i < len(larguras):
            celula.width = larguras[i]
        for p in celula.paragraphs:
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)