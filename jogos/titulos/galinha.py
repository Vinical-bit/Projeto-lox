"""A Galinha Atravessada - inspirado no classico da galinha na estrada (1981).

E o jogo mais facil da colecao e o melhor para comecar com uma crianca
pequena: usa SO duas teclas, para cima e para baixo. Ser atropelado nao
mata ninguem, so empurra a galinha um pouco para tras.
"""

import random

import pygame

from motor.nucleo import ALTURA, CORES, JogoBase, LARGURA, barra, colide, texto

TOPO_GRAMA = 18          # altura da faixa de grama de cima (a chegada)
BASE_GRAMA = 192         # onde comeca a grama de baixo (a largada)
FAIXAS = 8
ALT_FAIXA = (BASE_GRAMA - TOPO_GRAMA) / FAIXAS

CORES_CARROS = [
    CORES["vermelho"], CORES["azul"], CORES["amarelo"],
    CORES["roxo"], CORES["laranja"], CORES["branco"],
]


class Jogo(JogoBase):
    nome = "A Galinha"
    descricao = "Atravesse a estrada sem se assustar"
    cor = CORES["verde"]
    ajuda = "CIMA e BAIXO"

    def reiniciar(self):
        self.pontos = 0
        self.terminou = False
        self.gx = LARGURA / 2 - 4
        self.gy = float(ALTURA - 14)
        self.imune = 0.0
        self.tempo = None if self.modo_crianca else 136.0
        self.piscar = 0.0
        self.carros = []
        for faixa in range(FAIXAS):
            self._povoar_faixa(faixa)

    def _velocidade_base(self):
        if self.modo_crianca:
            return 18.0
        return 32.0 + min(30.0, self.pontos * 1.5)

    def _povoar_faixa(self, faixa):
        """Cria os carros de uma faixa, espalhados e com velocidade propria."""
        para_direita = faixa < FAIXAS / 2
        base = self._velocidade_base()
        vel = base * random.uniform(0.7, 1.4) * (1 if para_direita else -1)
        comp = random.choice([14, 18, 22])
        quantos = 2 if self.modo_crianca else 3
        espaco = LARGURA / quantos
        for i in range(quantos):
            self.carros.append({
                "faixa": faixa,
                "x": i * espaco + random.uniform(0, espaco - comp),
                "vel": vel,
                "comp": comp,
                "cor": random.choice(CORES_CARROS),
            })

    def _rect_carro(self, c):
        y = TOPO_GRAMA + c["faixa"] * ALT_FAIXA + ALT_FAIXA / 2 - 5
        return (c["x"], y, c["comp"], 10)

    def atualizar(self, dt, ent):
        self._passar_aviso(dt)
        if self.terminou:
            return

        if self.tempo is not None:
            self.tempo -= dt
            if self.tempo <= 0:
                self.tempo = 0
                self.terminou = True
                self.tocar("fim")
                return

        # galinha: so sobe e desce
        velocidade = 55.0 if self.modo_crianca else 70.0
        self.gy += ent.y * velocidade * dt
        self.gy = max(4.0, min(ALTURA - 14.0, self.gy))

        # carros
        for c in self.carros:
            c["x"] += c["vel"] * dt
            if c["vel"] > 0 and c["x"] > LARGURA:
                c["x"] = -c["comp"] - random.uniform(0, 40)
            elif c["vel"] < 0 and c["x"] + c["comp"] < 0:
                c["x"] = LARGURA + random.uniform(0, 40)

        # atropelamento: empurra para tras, nunca tira vida
        if self.imune > 0:
            self.imune -= dt
        else:
            galinha = (self.gx, self.gy, 8, 9)
            for c in self.carros:
                if colide(galinha, self._rect_carro(c)):
                    self.gy = min(ALTURA - 14.0, self.gy + (10 if self.modo_crianca else 26))
                    self.imune = 0.6
                    self.avisar("OPA!", 0.7)
                    self.tocar("opa")
                    break

        # chegou do outro lado
        if self.gy <= TOPO_GRAMA - 10:
            self.pontos += 1
            self.gy = float(ALTURA - 14)
            self.avisar("BOA!", 0.9)
            self.tocar("ponto")

    def desenhar(self, tela):
        tela.fill(CORES["cinza_escuro"])
        pygame.draw.rect(tela, CORES["verde"], (0, 0, LARGURA, TOPO_GRAMA))
        pygame.draw.rect(tela, CORES["verde"], (0, BASE_GRAMA, LARGURA, ALTURA - BASE_GRAMA))

        # faixas tracejadas
        for faixa in range(1, FAIXAS):
            y = int(TOPO_GRAMA + faixa * ALT_FAIXA)
            for x in range(0, LARGURA, 12):
                pygame.draw.rect(tela, CORES["amarelo"], (x, y, 6, 1))

        for c in self.carros:
            x, y, w, h = self._rect_carro(c)
            pygame.draw.rect(tela, c["cor"], (int(x), int(y), w, h))
            pygame.draw.rect(tela, CORES["preto"], (int(x) + 3, int(y) + 2, w - 6, h - 4))
            farol = int(x) + (w - 2 if c["vel"] > 0 else 0)
            pygame.draw.rect(tela, CORES["amarelo"], (farol, int(y) + 3, 2, 4))

        self._desenhar_galinha(tela)

    def _desenhar_galinha(self, tela):
        if self.imune > 0 and int(self.imune * 12) % 2 == 0:
            return
        x, y = int(self.gx), int(self.gy)
        pygame.draw.rect(tela, CORES["branco"], (x, y, 8, 7))       # corpo
        pygame.draw.rect(tela, CORES["branco"], (x + 2, y - 3, 4, 4))  # cabeca
        pygame.draw.rect(tela, CORES["vermelho"], (x + 3, y - 5, 2, 2))  # crista
        pygame.draw.rect(tela, CORES["laranja"], (x + 6, y - 2, 2, 1))   # bico
        pygame.draw.rect(tela, CORES["laranja"], (x + 1, y + 7, 2, 2))   # pes
        pygame.draw.rect(tela, CORES["laranja"], (x + 5, y + 7, 2, 2))

    def desenhar_hud(self, tela, escala):
        texto(tela, f"ATRAVESSOU: {self.pontos}", 8, 6, CORES["branco"], 26)
        if self.tempo is not None:
            barra(tela, tela.get_width() - 108, 10, 100, 10, self.tempo / 136.0, CORES["amarelo"])
        if self.aviso:
            texto(tela, self.aviso, tela.get_width() // 2, tela.get_height() // 2,
                  CORES["amarelo"], 64, centro=True)

    def icone(self, tela, ret):
        pygame.draw.rect(tela, CORES["cinza_escuro"], ret)
        pygame.draw.rect(tela, CORES["verde"], (ret.x, ret.y, ret.w, 6))
        pygame.draw.rect(tela, CORES["verde"], (ret.x, ret.bottom - 6, ret.w, 6))
        for i in range(3):
            y = ret.y + 10 + i * 9
            pygame.draw.rect(tela, CORES_CARROS[i], (ret.x + 4 + i * 9, y, 12, 6))
        cx, cy = ret.centerx, ret.bottom - 14
        pygame.draw.rect(tela, CORES["branco"], (cx - 4, cy, 8, 7))
        pygame.draw.rect(tela, CORES["branco"], (cx - 2, cy - 3, 4, 4))
        pygame.draw.rect(tela, CORES["vermelho"], (cx - 1, cy - 5, 2, 2))
