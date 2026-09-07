"""Bipes sintetizados na mao, sem depender de arquivos nem de numpy.

Se o computador nao tiver som (ou o mixer falhar), tudo vira silencio e o
jogo continua funcionando normalmente.
"""

import array
import math

import pygame

TAXA = 22050


def _onda(freq, ms, volume=0.35, tipo="quadrada"):
    """Gera uma onda simples em 16 bits mono."""
    n = int(TAXA * ms / 1000)
    dados = array.array("h")
    for i in range(n):
        fase = (i * freq / TAXA) % 1.0
        if tipo == "quadrada":
            v = 1.0 if fase < 0.5 else -1.0
        elif tipo == "ruido":
            v = math.sin(i * i * 0.0007) * math.sin(i * 0.1)
        else:  # dente de serra
            v = 2.0 * fase - 1.0
        # fade rapido no fim para nao estalar
        env = min(1.0, (n - i) / max(1, n * 0.25))
        dados.append(int(max(-1.0, min(1.0, v * env)) * volume * 32767))
    return dados


class Som:
    def __init__(self, ligado=True):
        self.ligado = ligado
        self.efeitos = {}
        if not ligado:
            return
        try:
            pygame.mixer.pre_init(TAXA, -16, 1, 512)
            pygame.mixer.init(TAXA, -16, 1, 512)
        except pygame.error:
            self.ligado = False
            return
        receitas = {
            "tiro": (880, 60, 0.25, "quadrada"),
            "ponto": (1200, 90, 0.30, "quadrada"),
            "opa": (140, 220, 0.35, "serra"),
            "recurso": (620, 140, 0.30, "quadrada"),
            "menu": (700, 45, 0.20, "quadrada"),
            "fim": (200, 400, 0.30, "serra"),
            "soco": (300, 70, 0.35, "ruido"),
        }
        for nome, (f, ms, vol, tipo) in receitas.items():
            try:
                self.efeitos[nome] = pygame.mixer.Sound(buffer=_onda(f, ms, vol, tipo))
            except pygame.error:
                self.ligado = False
                return

    def tocar(self, nome):
        if not self.ligado:
            return
        efeito = self.efeitos.get(nome)
        if efeito:
            efeito.play()
