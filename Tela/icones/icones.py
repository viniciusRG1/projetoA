import customtkinter as ctk
from PIL import Image, ImageDraw
from Tela.constantes import COR_AMARELO, COR_AZUL


def desenharIconeOnda(tamanho=36, corFundo=COR_AMARELO, corOnda=COR_AZUL):
    fator = 4
    dim = tamanho * fator
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, dim, dim], radius=10 * fator, fill=corFundo)

    largura = 2 * fator
    espacamento = 4.5 * fator
    alturas = [0.25, 0.55, 0.90, 0.55, 0.25]
    cx, cy = dim / 2, dim / 2

    for i, alt in enumerate(alturas):
        x = cx + (i - 2) * espacamento
        h = (dim * 0.45) * alt
        draw.rounded_rectangle(
            [x - largura / 2, cy - h / 2, x + largura / 2, cy + h / 2],
            radius=largura / 2,
            fill=corOnda,
        )

    imgReduzida = img.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=imgReduzida, size=(tamanho, tamanho))


def desenharIconeUpload(tamanho=64, corFundo=COR_AZUL, corIcone="#FFFFFF"):
    fator = 4
    dim = tamanho * fator
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, dim, dim], radius=16 * fator, fill=corFundo)

    cx, cy = dim / 2, dim / 2
    esp = int(2.5 * fator)
    bw, by_top, by_bot = 14 * fator, cy + 2 * fator, cy + 10 * fator

    draw.line([(cx - bw, by_top), (cx - bw, by_bot)], fill=corIcone, width=esp)
    draw.line([(cx - bw, by_bot), (cx + bw, by_bot)], fill=corIcone, width=esp)
    draw.line([(cx + bw, by_bot), (cx + bw, by_top)], fill=corIcone, width=esp)
    draw.line([(cx, cy + 4 * fator), (cx, cy - 8 * fator)], fill=corIcone, width=esp)

    sw = 7 * fator
    draw.line([(cx - sw, cy - 2 * fator), (cx, cy - 9 * fator)], fill=corIcone, width=esp)
    draw.line([(cx + sw, cy - 2 * fator), (cx, cy - 9 * fator)], fill=corIcone, width=esp)

    imgReduzida = img.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=imgReduzida, size=(tamanho, tamanho))


def desenharIconePasta(tamanho=18, cor="#FFFFFF"):
    fator = 4
    dim = tamanho * fator
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [2 * fator, 3 * fator, 7 * fator, 6 * fator],
        radius=1 * fator,
        fill=cor,
    )
    draw.rounded_rectangle(
        [2 * fator, 5 * fator, 16 * fator, 15 * fator],
        radius=2 * fator,
        fill=cor,
    )

    imgReduzida = img.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=imgReduzida, size=(tamanho, tamanho))