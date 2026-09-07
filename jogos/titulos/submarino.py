"""Submarino Resgate - inspirado no classico do submarino e dos tubaroes (1983).

Desca, encoste nos mergulhadores para resgatar e volte para a superficie
para deixa-los em seguranca e encher o tanque de oxigenio.
"""

import math
import random

import pygame

from motor.nucleo import ALTURA, CORES, JogoBase, LARGURA, barra, colide, texto

SUPERFICIE = 34          # linha da agua
FUNDO = ALTURA - 12
MAX_MERGULHADORES = 6


class Jogo(JogoBase):
    nome = "Submarino"
    descricao = "Resgate os mergulhadores e suba para respirar"
    cor = CORES["azul_escuro"]
    ajuda = "SETAS e ESPACO"

    def reiniciar(self):
        self.pontos = 0
        self.terminou = False
        self.vidas = 99 if self.modo_crianca else 3
        self.x = LARGURA / 2 - 7
        self.y = 60.0
        self.olhando = 1
        self.oxigenio = 1.0
        self.resgatados = 0
        self.imune = 1.0
        self.recarga = 0.0
        self.tiros = []
        self.inimigos = []
        self.mergulhadores = []
        self.tiros_inimigos = []
        self.explosoes = []
        self._t_inimigo = 1.0
        self._t_mergulhador = 2.0
        self._tempo = 0.0

    # --- nascimentos -----------------------------------------------------
    def _nascer_inimigo(self):
        lado = random.choice([-1, 1])
        x = -16.0 if lado > 0 else float(LARGURA)
        y = random.uniform(SUPERFICIE + 12, FUNDO - 10)
        tipo = "tubarao"
        if not self.modo_crianca and self.pontos > 300 and random.random() < 0.4:
            tipo = "inimigo"
        vel = random.uniform(14, 26) if self.modo_crianca else random.uniform(22, 42)
        self.inimigos.append({
            "tipo": tipo, "x": x, "y": y, "vx": vel * lado,
            "fase": random.uniform(0, 6.28), "recarga": random.uniform(1.5, 4.0),
        })
        self._t_inimigo = random.uniform(2.2, 3.6) if self.modo_crianca else random.uniform(1.0, 2.2)

    def _nascer_mergulhador(self):
        lado = random.choice([-1, 1])
        x = -8.0 if lado > 0 else float(LARGURA)
        y = random.uniform(SUPERFICIE + 20, FUNDO - 8)
        self.mergulhadores.append({"x": x, "y": y, "vx": 9.0 * lado})
        self._t_mergulhador = random.uniform(2.0, 4.0)

    # --- ciclo -----------------------------------------------------------
    def atualizar(self, dt, ent):
        self._passar_aviso(dt)
        if self.terminou:
            return
        self._tempo += dt

        vel = 52.0 if self.modo_crianca else 68.0
        if ent.x:
            self.olhando = ent.x
        self.x = max(0.0, min(LARGURA - 14.0, self.x + ent.x * vel * dt))
        self.y = max(float(SUPERFICIE - 6), min(float(FUNDO - 8), self.y + ent.y * vel * dt))

        na_superficie = self.y <= SUPERFICIE - 1
        if na_superficie:
            antes = self.oxigenio
            self.oxigenio = min(1.0, self.oxigenio + 0.5 * dt)
            if self.oxigenio > antes + 0.001 and int(self._tempo * 3) % 2 == 0:
                self.avisar("AR!", 0.3)
            if self.resgatados:
                ganho = self.resgatados * (100 if self.modo_crianca else 50)
                self.pontos += ganho
                self.avisar(f"+{ganho}", 1.2)
                self.tocar("ponto")
                self.resgatados = 0
        else:
            self.oxigenio -= (0.012 if self.modo_crianca else 0.035) * dt
            if self.oxigenio <= 0:
                self.oxigenio = 0.0
                self._bateu("SEM AR!")
                self.y = float(SUPERFICIE)
                self.oxigenio = 0.6

        # tiros do jogador
        self.recarga -= dt
        if (ent.acao or self.modo_crianca) and self.recarga <= 0 and not na_superficie:
            self.recarga = 0.30
            self.tiros.append([self.x + (14 if self.olhando > 0 else 0), self.y + 3, self.olhando])
            self.tocar("tiro")
        for t in self.tiros:
            t[0] += 165 * t[2] * dt
        self.tiros = [t for t in self.tiros if -6 < t[0] < LARGURA + 6]

        self._t_inimigo -= dt
        if self._t_inimigo <= 0:
            self._nascer_inimigo()
        self._t_mergulhador -= dt
        if self._t_mergulhador <= 0 and len(self.mergulhadores) < 4:
            self._nascer_mergulhador()

        self._mover_inimigos(dt)
        self._mover_mergulhadores(dt)
        self._checar_colisoes(dt)

        for e in self.explosoes:
            e[2] -= dt
        self.explosoes = [e for e in self.explosoes if e[2] > 0]

    def _mover_inimigos(self, dt):
        for i in self.inimigos:
            i["x"] += i["vx"] * dt
            i["y"] += math.sin(self._tempo * 2 + i["fase"]) * 8 * dt
            i["y"] = max(SUPERFICIE + 8, min(FUNDO - 8, i["y"]))
            if i["tipo"] == "inimigo" and not self.modo_crianca:
                i["recarga"] -= dt
                if i["recarga"] <= 0:
                    i["recarga"] = random.uniform(2.0, 4.0)
                    d = 1 if i["vx"] > 0 else -1
                    self.tiros_inimigos.append([i["x"] + (14 if d > 0 else 0), i["y"] + 3, d])
        self.inimigos = [i for i in self.inimigos if -30 < i["x"] < LARGURA + 30]
        for t in self.tiros_inimigos:
            t[0] += 90 * t[2] * dt
        self.tiros_inimigos = [t for t in self.tiros_inimigos if -6 < t[0] < LARGURA + 6]

    def _mover_mergulhadores(self, dt):
        for m in self.mergulhadores:
            m["x"] += m["vx"] * dt
        self.mergulhadores = [m for m in self.mergulhadores if -20 < m["x"] < LARGURA + 20]

    def _checar_colisoes(self, dt):
        sub = (self.x, self.y, 14, 8)

        for t in list(self.tiros):
            rt = (t[0], t[1], 4, 2)
            for i in list(self.inimigos):
                if colide(rt, (i["x"], i["y"], 14, 8)):
                    self.inimigos.remove(i)
                    if t in self.tiros:
                        self.tiros.remove(t)
                    self.pontos += 30 if i["tipo"] == "tubarao" else 60
                    self.explosoes.append([i["x"] + 7, i["y"] + 4, 0.3])
                    self.tocar("ponto")
                    break

        for m in list(self.mergulhadores):
            if colide(sub, (m["x"], m["y"], 6, 8)):
                self.mergulhadores.remove(m)
                if self.resgatados < MAX_MERGULHADORES:
                    self.resgatados += 1
                    self.avisar("RESGATOU!", 0.8)
                    self.tocar("recurso")

        if self.imune > 0:
            self.imune -= dt
            return
        for i in self.inimigos:
            if colide(sub, (i["x"], i["y"], 14, 8)):
                self._bateu("OPA!")
                return
        for t in self.tiros_inimigos:
            if colide(sub, (t[0], t[1], 4, 2)):
                self._bateu("OPA!")
                return

    def _bateu(self, msg):
        self.explosoes.append([self.x + 7, self.y + 4, 0.4])
        self.avisar(msg, 1.0)
        self.tocar("opa")
        self.imune = 1.6
        if self.modo_crianca:
            self.inimigos = [i for i in self.inimigos if abs(i["x"] - self.x) > 30]
        else:
            self.vidas -= 1
            self.inimigos.clear()
            self.tiros_inimigos.clear()
            if self.vidas <= 0:
                self.terminou = True
                self.tocar("fim")

    # --- desenho ---------------------------------------------------------
    def desenhar(self, tela):
        tela.fill(CORES["azul_escuro"])
        pygame.draw.rect(tela, CORES["azul"], (0, 0, LARGURA, SUPERFICIE))
        pygame.draw.rect(tela, CORES["amarelo"], (LARGURA - 26, 6, 10, 10))  # sol
        for x in range(0, LARGURA, 8):
            onda = int(math.sin(self._tempo * 2 + x * 0.3) * 1.5)
            pygame.draw.rect(tela, CORES["branco"], (x, SUPERFICIE + onda, 5, 2))
        pygame.draw.rect(tela, CORES["marrom"], (0, FUNDO, LARGURA, ALTURA - FUNDO))

        for m in self.mergulhadores:
            x, y = int(m["x"]), int(m["y"])
            pygame.draw.rect(tela, CORES["pele"], (x + 1, y, 4, 3))
            pygame.draw.rect(tela, CORES["laranja"], (x, y + 3, 6, 5))

        for i in self.inimigos:
            self._desenhar_inimigo(tela, i)
        for t in self.tiros:
            pygame.draw.rect(tela, CORES["branco"], (int(t[0]), int(t[1]), 4, 2))
        for t in self.tiros_inimigos:
            pygame.draw.rect(tela, CORES["vermelho"], (int(t[0]), int(t[1]), 4, 2))
        for e in self.explosoes:
            r = int(3 + (0.4 - e[2]) * 22)
            pygame.draw.circle(tela, CORES["laranja"], (int(e[0]), int(e[1])), max(2, r), 2)

        if self.imune <= 0 or int(self.imune * 12) % 2 == 0:
            self._desenhar_sub(tela)

        for n in range(self.resgatados):
            pygame.draw.rect(tela, CORES["laranja"], (4 + n * 7, ALTURA - 9, 5, 7))

    def _desenhar_inimigo(self, tela, i):
        x, y = int(i["x"]), int(i["y"])
        if i["tipo"] == "tubarao":
            pygame.draw.rect(tela, CORES["cinza"], (x + 2, y + 2, 10, 5))
            pygame.draw.rect(tela, CORES["cinza"], (x + 5, y, 4, 2))       # barbatana
            rabo = x + 12 if i["vx"] < 0 else x - 2
            pygame.draw.rect(tela, CORES["cinza"], (rabo, y + 1, 2, 6))
        else:
            pygame.draw.rect(tela, CORES["vermelho"], (x, y + 1, 14, 6))
            pygame.draw.rect(tela, CORES["branco"], (x + 5, y - 2, 4, 3))

    def _desenhar_sub(self, tela):
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(tela, CORES["amarelo"], (x, y + 1, 14, 7))
        pygame.draw.rect(tela, CORES["branco"], (x + 5, y - 2, 4, 3))
        pygame.draw.rect(tela, CORES["azul"], (x + (10 if self.olhando > 0 else 2), y + 3, 3, 3))
        helice = x + (-2 if self.olhando > 0 else 14)
        pygame.draw.rect(tela, CORES["cinza"], (helice, y + 2, 2, 5))

    def desenhar_hud(self, tela, escala):
        texto(tela, f"PONTOS {self.pontos}", 8, 6, CORES["branco"], 26)
        barra(tela, 8, tela.get_height() - 26, 160, 14, self.oxigenio,
              CORES["azul"] if self.oxigenio > 0.25 else CORES["vermelho"])
        texto(tela, "OXIGENIO", 174, tela.get_height() - 26, CORES["branco"], 22)
        if not self.modo_crianca:
            texto(tela, f"VIDAS {self.vidas}", tela.get_width() - 110, 6, CORES["branco"], 26)
        if self.aviso:
            texto(tela, self.aviso, tela.get_width() // 2, tela.get_height() // 3,
                  CORES["amarelo"], 60, centro=True)

    def icone(self, tela, ret):
        pygame.draw.rect(tela, CORES["azul_escuro"], ret)
        pygame.draw.rect(tela, CORES["azul"], (ret.x, ret.y, ret.w, 10))
        pygame.draw.rect(tela, CORES["amarelo"], (ret.centerx - 7, ret.centery, 14, 7))
        pygame.draw.rect(tela, CORES["branco"], (ret.centerx - 2, ret.centery - 3, 4, 3))
        pygame.draw.rect(tela, CORES["cinza"], (ret.x + 6, ret.bottom - 16, 10, 5))
        pygame.draw.rect(tela, CORES["laranja"], (ret.right - 14, ret.bottom - 14, 6, 6))
