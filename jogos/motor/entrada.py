"""Leitura de teclado e controle (joystick) num formato unico.

Os jogos nunca olham teclas diretamente: eles perguntam para a Entrada
`ent.x`, `ent.y`, `ent.acao`... Assim da para plugar um controle de USB
depois sem mexer em nenhum jogo.
"""

import pygame


class Jogador:
    """Estado de um jogador: direcao (-1, 0 ou 1) e botao de acao."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.acao = False        # botao segurado
        self.acao_apertou = False  # virou True neste quadro


class Entrada:
    def __init__(self):
        self.p1 = Jogador()
        self.p2 = Jogador()
        self.voltar = False       # ESC
        self.confirmar = False    # ENTER / ESPACO (borda)
        self.pausar = False       # P (borda)
        self.reiniciar_pedido = False  # R (borda)
        self._antes = {}
        self.controles = []

    def abrir_controles(self):
        pygame.joystick.init()
        self.controles = []
        for i in range(pygame.joystick.get_count()):
            c = pygame.joystick.Joystick(i)
            c.init()
            self.controles.append(c)

    # atalhos para o jogador 1 (a maioria dos jogos usa so ele)
    @property
    def x(self):
        return self.p1.x

    @property
    def y(self):
        return self.p1.y

    @property
    def acao(self):
        return self.p1.acao

    @property
    def acao_apertou(self):
        return self.p1.acao_apertou

    def _borda(self, nome, valor):
        antes = self._antes.get(nome, False)
        self._antes[nome] = valor
        return valor and not antes

    def atualizar(self):
        t = pygame.key.get_pressed()

        # --- jogador 1: setas + espaco -------------------------------
        self.p1.x = (1 if t[pygame.K_RIGHT] else 0) - (1 if t[pygame.K_LEFT] else 0)
        self.p1.y = (1 if t[pygame.K_DOWN] else 0) - (1 if t[pygame.K_UP] else 0)
        acao1 = t[pygame.K_SPACE] or t[pygame.K_RETURN] or t[pygame.K_KP_ENTER]

        # --- jogador 2: WASD + shift esquerdo -------------------------
        self.p2.x = (1 if t[pygame.K_d] else 0) - (1 if t[pygame.K_a] else 0)
        self.p2.y = (1 if t[pygame.K_s] else 0) - (1 if t[pygame.K_w] else 0)
        acao2 = t[pygame.K_LSHIFT] or t[pygame.K_e] or t[pygame.K_TAB]

        # --- controles USB -------------------------------------------
        for i, c in enumerate(self.controles[:2]):
            alvo = self.p1 if i == 0 else self.p2
            ex = ey = 0
            if c.get_numaxes() >= 2:
                ax, ay = c.get_axis(0), c.get_axis(1)
                ex = 1 if ax > 0.5 else (-1 if ax < -0.5 else 0)
                ey = 1 if ay > 0.5 else (-1 if ay < -0.5 else 0)
            if c.get_numhats() >= 1:
                hx, hy = c.get_hat(0)
                ex = ex or hx
                ey = ey or -hy
            botao = any(c.get_button(b) for b in range(min(4, c.get_numbuttons())))
            alvo.x = alvo.x or ex
            alvo.y = alvo.y or ey
            if i == 0:
                acao1 = acao1 or botao
            else:
                acao2 = acao2 or botao

        self.p1.acao = bool(acao1)
        self.p2.acao = bool(acao2)
        self.p1.acao_apertou = self._borda("acao1", self.p1.acao)
        self.p2.acao_apertou = self._borda("acao2", self.p2.acao)

        self.voltar = self._borda("esc", t[pygame.K_ESCAPE])
        self.confirmar = self.p1.acao_apertou
        self.pausar = self._borda("pausa", t[pygame.K_p])
        self.reiniciar_pedido = self._borda("reiniciar", t[pygame.K_r])
