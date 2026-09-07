"""Nucleo compartilhado dos jogos.

A ideia e imitar a tela do Atari 2600: tudo e desenhado numa telinha de
160x210 pixels e depois ampliado. Isso deixa o visual quadradinho de propósito
e simplifica muito as contas de posicao dentro dos jogos.
"""

import pygame

# Resolucao interna (a mesma proporcao do Atari 2600).
LARGURA = 160
ALTURA = 210
FPS = 60

CORES = {
    "preto": (0, 0, 0),
    "branco": (236, 236, 236),
    "cinza": (120, 120, 120),
    "cinza_escuro": (60, 60, 60),
    "vermelho": (214, 60, 60),
    "laranja": (232, 140, 40),
    "amarelo": (232, 210, 70),
    "verde": (80, 180, 80),
    "verde_escuro": (40, 110, 60),
    "azul": (70, 130, 220),
    "azul_escuro": (30, 60, 140),
    "roxo": (150, 90, 200),
    "rosa": (230, 140, 170),
    "marrom": (140, 100, 60),
    "pele": (240, 200, 160),
}

_fontes = {}


def fonte(tamanho):
    """Devolve (e guarda em cache) a fonte padrao no tamanho pedido."""
    if tamanho not in _fontes:
        _fontes[tamanho] = pygame.font.Font(None, tamanho)
    return _fontes[tamanho]


def texto(superficie, msg, x, y, cor=CORES["branco"], tamanho=20, centro=False, sombra=True):
    """Escreve um texto. Com centro=True, (x, y) e o centro do texto."""
    img = fonte(tamanho).render(str(msg), True, cor)
    ret = img.get_rect()
    if centro:
        ret.center = (x, y)
    else:
        ret.topleft = (x, y)
    if sombra:
        escura = fonte(tamanho).render(str(msg), True, CORES["preto"])
        superficie.blit(escura, (ret.x + max(1, tamanho // 14), ret.y + max(1, tamanho // 14)))
    superficie.blit(img, ret)
    return ret


def barra(superficie, x, y, larg, alt, fracao, cor, fundo=CORES["cinza_escuro"], borda=CORES["branco"]):
    """Desenha uma barrinha de recurso (combustivel, oxigenio, tempo...)."""
    fracao = max(0.0, min(1.0, fracao))
    pygame.draw.rect(superficie, fundo, (x, y, larg, alt))
    if fracao > 0:
        pygame.draw.rect(superficie, cor, (x, y, max(1, int(larg * fracao)), alt))
    pygame.draw.rect(superficie, borda, (x, y, larg, alt), 1)


def colide(a, b):
    """Colisao simples entre dois retangulos (x, y, largura, altura)."""
    return (
        a[0] < b[0] + b[2]
        and a[0] + a[2] > b[0]
        and a[1] < b[1] + b[3]
        and a[1] + a[3] > b[1]
    )


def desenhar_joystick(destino, ret, fundo=(16, 18, 34)):
    """Joystick de fliperama, desenhado em 32x32 e ampliado para `ret`.

    Serve tanto para a tela inicial quanto para gerar o icone do executavel,
    entao a arte fica num lugar so.
    """
    arte = pygame.Surface((32, 32))
    arte.fill(fundo)
    pygame.draw.rect(arte, CORES["amarelo"], (1, 1, 30, 30), 1)
    pygame.draw.rect(arte, CORES["cinza_escuro"], (6, 21, 20, 7))   # base
    pygame.draw.rect(arte, CORES["cinza"], (14, 10, 4, 12))         # haste
    pygame.draw.circle(arte, CORES["vermelho"], (16, 9), 5)         # manopla
    pygame.draw.circle(arte, CORES["rosa"], (14, 7), 2)             # brilho
    pygame.draw.rect(arte, CORES["verde"], (7, 23, 4, 3))           # botao
    pygame.draw.rect(arte, CORES["azul"], (21, 23, 4, 3))           # botao
    destino.blit(pygame.transform.scale(arte, (ret.w, ret.h)), ret.topleft)
    return arte


class JogoBase:
    """Contrato que todo jogo da pasta `titulos` precisa cumprir.

    O `main.py` so conhece estes metodos, entao um jogo novo entra no menu
    sem precisar mexer em mais nada.
    """

    nome = "Jogo"
    descricao = ""
    cor = CORES["cinza"]
    ajuda = "Setas para mover"

    def __init__(self, modo_crianca=True, som=None):
        self.modo_crianca = modo_crianca
        self.som = som
        self.pontos = 0
        self.terminou = False
        self.recorde_msg = ""
        self.aviso = ""          # texto grande e curto na tela ("OPA!", "BOA!")
        self.aviso_tempo = 0.0
        self.reiniciar()

    # --- ciclo de vida -------------------------------------------------
    def reiniciar(self):
        """Volta o jogo ao estado inicial."""

    def atualizar(self, dt, ent):
        """Avanca a simulacao. `dt` em segundos, `ent` e um motor.entrada.Entrada."""

    def desenhar(self, tela):
        """Desenha na telinha de 160x210."""

    def desenhar_hud(self, tela, escala):
        """Desenha textos na tela grande (fica mais legivel que na telinha)."""

    def icone(self, tela, ret):
        """Miniatura do jogo mostrada no menu, dentro do retangulo `ret`."""
        pygame.draw.rect(tela, self.cor, ret)

    # --- utilitarios ---------------------------------------------------
    def avisar(self, msg, segundos=1.0):
        self.aviso = msg
        self.aviso_tempo = segundos

    def _passar_aviso(self, dt):
        if self.aviso_tempo > 0:
            self.aviso_tempo -= dt
            if self.aviso_tempo <= 0:
                self.aviso = ""

    def tocar(self, nome):
        if self.som:
            self.som.tocar(nome)
