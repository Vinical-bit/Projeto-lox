"""Teste de fumaca: roda todos os jogos sem tela, com comandos aleatorios.

Nao prova que o jogo e divertido - prova que ele nao quebra sozinho.
Uso:  python testes/fumaca.py
"""

import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from motor.nucleo import ALTURA, LARGURA  # noqa: E402
from titulos import boxe, galinha, rio, submarino  # noqa: E402

CLASSES = [galinha.Jogo, rio.Jogo, submarino.Jogo, boxe.Jogo]
QUADROS = 3600  # um minuto de jogo a 60 fps


class Mao:
    """Um jogador de mentira, que aperta teclas ao acaso."""

    def __init__(self):
        self.x = self.y = 0
        self.acao = False
        self.acao_apertou = False

    def sortear(self):
        if random.random() < 0.05:
            self.x = random.choice([-1, 0, 1])
        if random.random() < 0.05:
            self.y = random.choice([-1, 0, 1])
        antes = self.acao
        self.acao = random.random() < 0.3
        self.acao_apertou = self.acao and not antes


class EntradaFalsa:
    def __init__(self):
        self.p1 = Mao()
        self.p2 = Mao()
        self.voltar = self.confirmar = self.pausar = self.reiniciar_pedido = False

    x = property(lambda self: self.p1.x)
    y = property(lambda self: self.p1.y)
    acao = property(lambda self: self.p1.acao)
    acao_apertou = property(lambda self: self.p1.acao_apertou)

    def sortear(self):
        self.p1.sortear()
        self.p2.sortear()


def rodar_um(Classe, modo_crianca):
    jogo = Classe(modo_crianca=modo_crianca, som=None)
    mini = pygame.Surface((LARGURA, ALTURA))
    grande = pygame.Surface((LARGURA * 4, ALTURA * 4))
    ent = EntradaFalsa()
    fins = 0
    for quadro in range(QUADROS):
        ent.sortear()
        jogo.atualizar(1 / 60.0, ent)
        jogo.desenhar(mini)
        jogo.desenhar_hud(grande, 4)
        assert jogo.pontos >= 0, f"{Classe.nome}: pontuacao negativa"
        if jogo.terminou:
            fins += 1
            jogo.reiniciar()
    return fins


def main():
    pygame.init()
    pygame.display.set_mode((32, 32))
    falhas = 0
    for Classe in CLASSES:
        for modo_crianca in (True, False):
            etiqueta = "crianca" if modo_crianca else "normal "
            try:
                fins = rodar_um(Classe, modo_crianca)
                print(f"ok   {Classe.nome:<14} [{etiqueta}] {QUADROS} quadros, {fins} partida(s)")
            except Exception as erro:  # noqa: BLE001 - e um teste de fumaca
                falhas += 1
                print(f"FALHA {Classe.nome:<14} [{etiqueta}] {type(erro).__name__}: {erro}")
                import traceback
                traceback.print_exc()
    pygame.quit()
    if falhas:
        print(f"\n{falhas} falha(s)")
        return 1
    print("\ntudo certo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
