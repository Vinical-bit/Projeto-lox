"""Fliperama de casa - menu com quatro jogos no estilo Atari.

Rode com:  python main.py
Atalhos:   setas = escolher/jogar | espaco = confirmar/atirar | ESC = voltar
           C = modo crianca | P = pausa | R = recomecar | F = tela cheia
"""

import math
import sys

import pygame

from motor import entrada as mod_entrada
from motor.nucleo import ALTURA, CORES, LARGURA, desenhar_joystick, texto
from motor.som import Som
from titulos import boxe, galinha, rio, submarino

JOGOS = [galinha.Jogo, rio.Jogo, submarino.Jogo, boxe.Jogo]
FPS = 60


def escolher_escala():
    """Maior ampliacao inteira que cabe na tela do computador."""
    try:
        info = pygame.display.Info()
        maxx = int((info.current_w * 0.9) // LARGURA)
        maxy = int((info.current_h * 0.85) // ALTURA)
        return max(2, min(6, min(maxx, maxy)))
    except pygame.error:
        return 3


class Fliperama:
    def __init__(self, escala=None, modo_crianca=True, com_som=True):
        pygame.init()
        pygame.display.set_caption("Fliperama de Casa")
        self.escala = escala or escolher_escala()
        self.tela = pygame.display.set_mode((LARGURA * self.escala, ALTURA * self.escala))
        self.mini = pygame.Surface((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()
        self.som = Som(com_som)
        self.ent = mod_entrada.Entrada()
        self.ent.abrir_controles()
        self.modo_crianca = modo_crianca
        self.selecao = 0
        self.estado = "abertura"
        self.relogio_abertura = 0.0
        self.jogo = None
        self.pausado = False
        self.tela_cheia = False
        self.rodando = True
        self.icones = self._preparar_icones()

    def _preparar_icones(self):
        icones = []
        for Classe in JOGOS:
            sup = pygame.Surface((48, 60))
            amostra = Classe(modo_crianca=True, som=None)
            amostra.icone(sup, pygame.Rect(0, 0, 48, 60))
            icones.append(sup)
        return icones

    # --- laco principal ---------------------------------------------------
    def rodar(self):
        while self.rodando:
            dt = min(0.05, self.relogio.tick(FPS) / 1000.0)
            self._eventos()
            self.ent.atualizar()
            if self.estado == "abertura":
                self._abertura(dt)
            elif self.jogo is None:
                self._menu(dt)
            else:
                self._partida(dt)
            pygame.display.flip()
        pygame.quit()

    def _eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.rodando = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_f:
                    self._alternar_tela_cheia()
                elif e.key == pygame.K_c:
                    self.modo_crianca = not self.modo_crianca
                    self.som.tocar("menu")
                    if self.jogo:
                        self._abrir(self.selecao)
                elif e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT) \
                        and self.estado == "menu" and self.jogo is None:
                    self._mover_selecao(e.key)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if self.estado == "abertura":
                    if self._botao_iniciar().collidepoint(e.pos):
                        self._comecar()
                elif self.jogo is None:
                    for i, ret in enumerate(self._cartoes()):
                        if ret.collidepoint(e.pos):
                            self.selecao = i
                            self._abrir(i)

    def _alternar_tela_cheia(self):
        self.tela_cheia = not self.tela_cheia
        tamanho = (LARGURA * self.escala, ALTURA * self.escala)
        bandeira = pygame.FULLSCREEN if self.tela_cheia else 0
        self.tela = pygame.display.set_mode(tamanho, bandeira)

    def _mover_selecao(self, tecla):
        colunas = 2
        if tecla == pygame.K_RIGHT:
            self.selecao = (self.selecao + 1) % len(JOGOS)
        elif tecla == pygame.K_LEFT:
            self.selecao = (self.selecao - 1) % len(JOGOS)
        elif tecla == pygame.K_DOWN:
            self.selecao = (self.selecao + colunas) % len(JOGOS)
        elif tecla == pygame.K_UP:
            self.selecao = (self.selecao - colunas) % len(JOGOS)
        self.som.tocar("menu")

    def _abrir(self, indice):
        self.estado = "menu"
        self.jogo = JOGOS[indice](modo_crianca=self.modo_crianca, som=self.som)
        self.pausado = False

    def _comecar(self):
        self.estado = "menu"
        self.som.tocar("menu")

    # --- tela inicial -----------------------------------------------------
    def _botao_iniciar(self):
        larg, alt = self.tela.get_size()
        return pygame.Rect(0, 0, int(larg * 0.56), int(alt * 0.11)) \
            .move(int(larg * 0.22), int(alt * 0.63))

    def _abertura(self, dt):
        if self.ent.voltar:
            self.rodando = False
            return
        if self.ent.confirmar:
            self._comecar()
            return

        self.relogio_abertura += dt
        larg, alt = self.tela.get_size()
        pulso = (math.sin(self.relogio_abertura * 3) + 1) / 2

        self.tela.fill((16, 18, 34))
        for i in range(0, larg, 8):   # faixa de listras, so enfeite
            cor = CORES["azul_escuro"] if (i // 8) % 2 else (22, 26, 48)
            pygame.draw.rect(self.tela, cor, (i, 0, 8, int(alt * 0.02)))
            pygame.draw.rect(self.tela, cor, (i, alt - int(alt * 0.02), 8, int(alt * 0.02)))

        texto(self.tela, "FLIPERAMA", larg // 2, int(alt * 0.11),
              CORES["amarelo"], int(alt * 0.10), centro=True)
        texto(self.tela, "DE CASA", larg // 2, int(alt * 0.19),
              CORES["laranja"], int(alt * 0.07), centro=True)

        lado = int(alt * 0.26)
        desenhar_joystick(self.tela, pygame.Rect(larg // 2 - lado // 2, int(alt * 0.28), lado, lado))

        botao = self._botao_iniciar()
        pygame.draw.rect(self.tela, (30, 34, 60), botao, border_radius=12)
        pygame.draw.rect(self.tela, CORES["verde"], botao, 3 + int(pulso * 4), border_radius=12)
        texto(self.tela, "INICIAR", botao.centerx, botao.centery,
              CORES["branco"] if pulso > 0.3 else CORES["verde"],
              int(botao.h * 0.62), centro=True)

        texto(self.tela, "aperte ESPACO ou clique em INICIAR", larg // 2, int(alt * 0.78),
              CORES["cinza"], int(alt * 0.030), centro=True)

        # os quatro jogos aparecendo embaixo, so para dar gosto
        lado_icone = int(alt * 0.075)
        total = len(self.icones) * lado_icone + (len(self.icones) - 1) * 12
        x = larg // 2 - total // 2
        for i, icone in enumerate(self.icones):
            destaque = int(self.relogio_abertura * 1.5) % len(self.icones) == i
            mini = pygame.transform.scale(icone, (int(lado_icone * 0.8), lado_icone))
            ret = mini.get_rect(topleft=(x + i * (lado_icone + 12), int(alt * 0.83)))
            if destaque:
                pygame.draw.rect(self.tela, CORES["amarelo"], ret.inflate(6, 6), 2)
            self.tela.blit(mini, ret)

        modo = "MODO CRIANCA LIGADO" if self.modo_crianca else "MODO ORIGINAL"
        texto(self.tela, f"{modo}  -  tecla C muda", larg // 2, int(alt * 0.955),
              CORES["verde"] if self.modo_crianca else CORES["laranja"],
              int(alt * 0.028), centro=True)

    # --- menu -------------------------------------------------------------
    def _cartoes(self):
        larg, alt = self.tela.get_size()
        margem = int(larg * 0.06)
        vao = int(larg * 0.05)
        topo = int(alt * 0.20)
        base = int(alt * 0.86)
        lc = (larg - 2 * margem - vao) // 2
        ac = (base - topo - vao) // 2
        rets = []
        for i in range(len(JOGOS)):
            linha, coluna = divmod(i, 2)
            rets.append(pygame.Rect(margem + coluna * (lc + vao),
                                    topo + linha * (ac + vao), lc, ac))
        return rets

    def _menu(self, dt):
        if self.ent.voltar:
            self.estado = "abertura"
        if self.ent.confirmar:
            self._abrir(self.selecao)
            return

        larg, alt = self.tela.get_size()
        self.tela.fill((16, 18, 34))
        texto(self.tela, "FLIPERAMA DE CASA", larg // 2, int(alt * 0.06),
              CORES["amarelo"], int(alt * 0.055), centro=True)
        modo = "MODO CRIANCA: LIGADO" if self.modo_crianca else "MODO CRIANCA: DESLIGADO"
        texto(self.tela, modo, larg // 2, int(alt * 0.115),
              CORES["verde"] if self.modo_crianca else CORES["laranja"],
              int(alt * 0.030), centro=True)

        for i, ret in enumerate(self._cartoes()):
            escolhido = i == self.selecao
            classe = JOGOS[i]
            pygame.draw.rect(self.tela, (30, 34, 60), ret, border_radius=10)
            pygame.draw.rect(self.tela, classe.cor if escolhido else (70, 74, 110),
                             ret, 4 if escolhido else 2, border_radius=10)
            lado = min(ret.w - 20, int(ret.h * 0.52))
            icone = pygame.transform.scale(self.icones[i], (int(lado * 0.8), lado))
            self.tela.blit(icone, icone.get_rect(center=(ret.centerx, ret.y + ret.h * 0.42)))
            texto(self.tela, classe.nome, ret.centerx, int(ret.bottom - ret.h * 0.20),
                  CORES["branco"] if escolhido else CORES["cinza"],
                  int(ret.h * 0.16), centro=True)
            texto(self.tela, classe.ajuda, ret.centerx, int(ret.bottom - ret.h * 0.07),
                  CORES["cinza"], int(ret.h * 0.085), centro=True)

        texto(self.tela, "SETAS escolhem - ESPACO joga - C muda o modo - ESC volta",
              larg // 2, int(alt * 0.94), CORES["cinza"], int(alt * 0.028), centro=True)

    # --- partida ----------------------------------------------------------
    def _partida(self, dt):
        if self.ent.voltar:
            self.jogo = None
            return
        if self.ent.pausar:
            self.pausado = not self.pausado
        if self.ent.reiniciar_pedido:
            self._abrir(self.selecao)
            return

        if self.jogo.terminou and self.ent.confirmar:
            self._abrir(self.selecao)
            return

        if not self.pausado and not self.jogo.terminou:
            self.jogo.atualizar(dt, self.ent)

        self.jogo.desenhar(self.mini)
        pygame.transform.scale(self.mini, self.tela.get_size(), self.tela)
        self.jogo.desenhar_hud(self.tela, self.escala)

        if self.pausado:
            self._cortina("PAUSADO", "aperte P para voltar")
        elif self.jogo.terminou:
            resultado = getattr(self.jogo, "resultado", None)
            titulo = resultado() if callable(resultado) else f"FIM! {self.jogo.pontos} PONTOS"
            self._cortina(titulo, "ESPACO joga de novo - ESC volta ao menu")

    def _cortina(self, titulo, rodape):
        larg, alt = self.tela.get_size()
        veu = pygame.Surface((larg, alt), pygame.SRCALPHA)
        veu.fill((0, 0, 0, 170))
        self.tela.blit(veu, (0, 0))
        texto(self.tela, titulo, larg // 2, alt // 2 - int(alt * 0.04),
              CORES["amarelo"], int(alt * 0.06), centro=True)
        texto(self.tela, rodape, larg // 2, alt // 2 + int(alt * 0.04),
              CORES["branco"], int(alt * 0.030), centro=True)


def main(argv):
    modo_crianca = "--dificil" not in argv
    com_som = "--sem-som" not in argv
    fliperama = Fliperama(modo_crianca=modo_crianca, com_som=com_som)
    for i, classe in enumerate(JOGOS):
        if f"--{classe.__module__.split('.')[-1]}" in argv:
            fliperama.selecao = i
            fliperama._abrir(i)
    fliperama.rodar()


if __name__ == "__main__":
    main(sys.argv[1:])
