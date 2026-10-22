def formatarTempo(segundo):
    minutos = int(segundo // 60)
    segs = int(segundo % 60)
    return f"{minutos:02d}:{segs:02d}"