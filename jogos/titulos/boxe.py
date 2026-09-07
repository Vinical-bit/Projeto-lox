"""Ringue de Boxe - inspirado no classico de boxe visto de cima (1980).

Vale para um jogador contra o computador ou para dois na mesma teclado:
basta o segundo jogador encostar em W/A/S/D que ele entra na luta.
"""

import random

import pygame

from motor.nucleo import ALTURA, CORES, JogoBase, LARGURA, barra, colide, texto

RING = pygame.Rect(12, 40, 136, 150)   # area util do ringue
LARG_BOX, ALT_BOX = 16, 26
ALCANCE = 12                            # quanto o braco estica


def _novo_boxeador(x, y, cor, olhando):
    return {
        "x": float(x), "y": float(y), "cor": cor, "olhando": olhando,
        "pontos": 0, "atordoado": 0.0, "soco": 0.0, "recarga": 0.0,
        "acertou_neste_soco": False, "decisao": 0.0,
    }


class Jogo(JogoBase):
    nome = "Boxe"
    descricao = "Um contra um - o segundo jogador entra na hora"
    cor = CORES["vermelho"]
    ajuda = "SETAS e ESPACO"

    def reiniciar(self):
        self.pontos = 0
        self.terminou = False
        self.humano2 = False
        self.tempo = 60.0 if self.modo_crianca else 120.0
        self.a = _novo_boxeador(RING.x + 16, RING.centery - 13, CORES["azul"], 1)
        self.b = _novo_boxeador(RING.right - 32, RING.centery - 13, CORES["cinza_escuro"], -1)
        self.faisca = []

    # --- ciclo -----------------------------------------------------------
    def atualizar(self, dt, ent):
        self._passar_aviso(dt)
        if self.terminou:
            return

        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = 0.0
            self._acabar()
            return

        if ent.p2.x or ent.p2.y or ent.p2.acao:
            if not self.humano2:
                self.humano2 = True
                self.avisar("2 JOGADORES!", 1.2)

        self._mover(self.a, ent.p1.x, ent.p1.y, ent.p1.acao_apertou, dt)
        if self.humano2:
            self._mover(self.b, ent.p2.x, ent.p2.y, ent.p2.acao_apertou, dt)
        else:
            self._mover_computador(dt)

        self._separar()
        self.a["olhando"] = 1 if self.a["x"] <= self.b["x"] else -1
        self.b["olhando"] = -self.a["olhando"]
        self._checar_socos(self.a, self.b)
        self._checar_socos(self.b, self.a)

        for f in self.faisca:
            f[2] -= dt
        self.faisca = [f for f in self.faisca if f[2] > 0]

        self.pontos = self.a["pontos"]
        if max(self.a["pontos"], self.b["pontos"]) >= 100:
            self._acabar()

    def _mover(self, bx, dx, dy, socar, dt):
        bx["recarga"] = max(0.0, bx["recarga"] - dt)
        if bx["soco"] > 0:
            bx["soco"] -= dt
            if bx["soco"] <= 0:
                bx["acertou_neste_soco"] = False
        if bx["atordoado"] > 0:
            bx["atordoado"] -= dt
            return
        vel = 46.0 if self.modo_crianca else 58.0
        bx["x"] = max(RING.x, min(RING.right - LARG_BOX, bx["x"] + dx * vel * dt))
        bx["y"] = max(RING.y, min(RING.bottom - ALT_BOX, bx["y"] + dy * vel * dt))
        if socar and bx["recarga"] <= 0:
            bx["soco"] = 0.18
            bx["recarga"] = 0.32
            bx["acertou_neste_soco"] = False

    def _mover_computador(self, dt):
        b, a = self.b, self.a
        b["decisao"] -= dt
        dificuldade = 0.9 if self.modo_crianca else 0.25
        if b["decisao"] <= 0:
            b["decisao"] = random.uniform(dificuldade * 0.5, dificuldade)
            b["_dx"] = 0
            b["_dy"] = 0
            if self.modo_crianca and random.random() < 0.5:
                pass  # de vez em quando o computador so passeia
            else:
                # posicao boa para socar: encostado no lado de fora do jogador
                alvo_x = a["x"] + LARG_BOX + 4 if a["x"] < b["x"] else a["x"] - LARG_BOX - 4
                if b["x"] > alvo_x + 3:
                    b["_dx"] = -1
                elif b["x"] < alvo_x - 3:
                    b["_dx"] = 1
                if abs(a["y"] - b["y"]) > 4:
                    b["_dy"] = 1 if a["y"] > b["y"] else -1
        perto = abs(a["x"] - b["x"]) < LARG_BOX + ALCANCE and abs(a["y"] - b["y"]) < 12
        chance = 0.06 if self.modo_crianca else 0.9
        socar = perto and random.random() < chance * dt * 6
        self._mover(b, b.get("_dx", 0), b.get("_dy", 0), socar, dt)

    def _separar(self):
        """Impede que os dois fiquem em cima um do outro."""
        ra = (self.a["x"], self.a["y"], LARG_BOX, ALT_BOX)
        rb = (self.b["x"], self.b["y"], LARG_BOX, ALT_BOX)
        if colide(ra, rb):
            meio = (self.a["x"] + self.b["x"]) / 2
            self.a["x"] = max(RING.x, min(RING.right - LARG_BOX, meio - LARG_BOX - 1))
            self.b["x"] = max(RING.x, min(RING.right - LARG_BOX, meio + 1))

    def _luva(self, bx):
        if bx["olhando"] > 0:
            return (bx["x"] + LARG_BOX, bx["y"] + 7, ALCANCE, 6)
        return (bx["x"] - ALCANCE, bx["y"] + 7, ALCANCE, 6)

    def _checar_socos(self, quem, alvo):
        if quem["soco"] <= 0 or quem["acertou_neste_soco"] or alvo["atordoado"] > 0:
            return
        if colide(self._luva(quem), (alvo["x"], alvo["y"], LARG_BOX, ALT_BOX)):
            quem["acertou_neste_soco"] = True
            quem["pontos"] += 1
            alvo["atordoado"] = 0.35
            alvo["x"] = max(RING.x, min(RING.right - LARG_BOX,
                                        alvo["x"] + 8 * quem["olhando"]))
            self.faisca.append([self._luva(quem)[0], quem["y"] + 8, 0.25])
            self.tocar("soco")

    def _acabar(self):
        self.terminou = True
        self.tocar("fim")

    def resultado(self):
        if self.a["pontos"] > self.b["pontos"]:
            return "VOCE GANHOU!" if not self.humano2 else "JOGADOR 1 GANHOU!"
        if self.b["pontos"] > self.a["pontos"]:
            return "O ROBO GANHOU!" if not self.humano2 else "JOGADOR 2 GANHOU!"
        return "EMPATE! BOA LUTA!"

    # --- desenho ---------------------------------------------------------
    def desenhar(self, tela):
        tela.fill(CORES["azul_escuro"])
        pygame.draw.rect(tela, CORES["cinza"], RING.inflate(10, 10))
        pygame.draw.rect(tela, CORES["branco"], RING)
        for i in range(1, 3):
            pygame.draw.rect(tela, CORES["vermelho"], (RING.x, RING.y + i * 4, RING.w, 1))
            pygame.draw.rect(tela, CORES["azul"], (RING.x, RING.bottom - i * 4, RING.w, 1))
        for f in self.faisca:
            pygame.draw.circle(tela, CORES["amarelo"], (int(f[0]), int(f[1])), 4, 1)
        self._desenhar_boxeador(tela, self.b)
        self._desenhar_boxeador(tela, self.a)

    def _desenhar_boxeador(self, tela, bx):
        x, y = int(bx["x"]), int(bx["y"])
        corpo = bx["cor"] if bx["atordoado"] <= 0 else CORES["rosa"]
        luva = CORES["vermelho"] if bx is self.a else CORES["laranja"]
        pygame.draw.rect(tela, CORES["preto"], (x - 1, y - 1, LARG_BOX + 2, ALT_BOX + 2))
        pygame.draw.rect(tela, corpo, (x, y, LARG_BOX, ALT_BOX))
        pygame.draw.rect(tela, CORES["pele"], (x + 4, y + 5, 8, 8))               # cabeca
        pygame.draw.rect(tela, CORES["preto"], (x, y + ALT_BOX - 7, LARG_BOX, 7))  # calcao
        if bx["soco"] > 0:
            lx, ly, lw, lh = [int(v) for v in self._luva(bx)]
            pygame.draw.rect(tela, luva, (lx, ly, lw, lh))
        else:
            lado = x + LARG_BOX - 5 if bx["olhando"] > 0 else x
            pygame.draw.rect(tela, luva, (lado, y + 7, 5, 6))

    def desenhar_hud(self, tela, escala):
        larg = tela.get_width()
        texto(tela, f"{self.a['pontos']}", 30, 8, CORES["azul"], 44)
        texto(tela, f"{self.b['pontos']}", larg - 46, 8, CORES["cinza"], 44)
        barra(tela, larg // 2 - 60, 16, 120, 12, self.tempo / (60.0 if self.modo_crianca else 120.0),
              CORES["amarelo"])
        if not self.humano2:
            texto(tela, "WASD + SHIFT: 2o jogador entra", larg // 2, tela.get_height() - 22,
                  CORES["cinza"], 22, centro=True)
        if self.aviso:
            texto(tela, self.aviso, larg // 2, tela.get_height() // 3, CORES["amarelo"], 54, centro=True)

    def icone(self, tela, ret):
        pygame.draw.rect(tela, CORES["cinza"], ret)
        interno = ret.inflate(-10, -10)
        pygame.draw.rect(tela, CORES["branco"], interno)
        pygame.draw.rect(tela, CORES["azul"], (interno.x + 4, interno.centery - 8, 10, 16))
        pygame.draw.rect(tela, CORES["cinza_escuro"], (interno.right - 14, interno.centery - 8, 10, 16))
        pygame.draw.rect(tela, CORES["amarelo"], (interno.centerx - 3, interno.centery - 3, 6, 6))
