"""Rio Perigoso - inspirado no classico do aviaozinho subindo o rio (1982).

O rio e gerado linha a linha enquanto a tela rola, entao ele nunca acaba e
nunca se repete. Combustivel acaba: passe por cima dos tanques amarelos.
"""

import random

import pygame

from motor.nucleo import ALTURA, CORES, JogoBase, LARGURA, barra, colide, texto

Y_AVIAO = 182
PONTOS = {"barco": 30, "heli": 60, "aviao": 100, "ponte": 500}
TAMANHOS = {
    "barco": (14, 7),
    "heli": (13, 7),
    "aviao": (14, 6),
    "combustivel": (8, 14),
}


class Jogo(JogoBase):
    nome = "Rio Perigoso"
    descricao = "Suba o rio, atire e reabasteca"
    cor = CORES["azul"]
    ajuda = "SETAS e ESPACO"

    def reiniciar(self):
        self.pontos = 0
        self.terminou = False
        self.vidas = 99 if self.modo_crianca else 3
        self.comb = 1.0
        self.x = LARGURA / 2 - 4
        self.imune = 1.0
        self.tiros = []
        self.objetos = []
        self.explosoes = []
        self.recarga = 0.0
        self.linhas = 0
        self._sobra = 0.0
        self._proximo = 40
        self._reta = 0
        self._c = LARGURA / 2
        self._w = 90.0 if self.modo_crianca else 76.0
        self._alvo_c = self._c
        self._alvo_w = self._w
        self.vel = 34.0 if self.modo_crianca else 55.0
        self.margens = [self._nova_linha() for _ in range(ALTURA)]

    # --- geracao do rio -------------------------------------------------
    def _limites_largura(self):
        if self.modo_crianca:
            return 68.0, 120.0
        return 40.0, 110.0

    def _nova_linha(self):
        min_w, max_w = self._limites_largura()
        if self._reta > 0:
            self._reta -= 1
        else:
            if random.random() < 0.02:
                self._alvo_w = random.uniform(min_w, max_w)
            if random.random() < 0.02:
                self._alvo_c = random.uniform(max_w / 2 + 8, LARGURA - max_w / 2 - 8)
            passo = 0.25 if self.modo_crianca else 0.45
            self._w += max(-passo, min(passo, self._alvo_w - self._w))
            self._c += max(-passo, min(passo, self._alvo_c - self._c))
        self._w = max(min_w, min(max_w, self._w))
        meia = self._w / 2
        self._c = max(meia + 6, min(LARGURA - meia - 6, self._c))
        return (self._c - meia, self._c + meia)

    def _margem_em(self, y):
        i = int(max(0, min(ALTURA - 1, y)))
        return self.margens[i]

    def _nascer_algo(self):
        esq, dir_ = self.margens[0]
        intervalo = 55 if self.modo_crianca else 34
        self._proximo = intervalo + random.randint(0, intervalo)

        if self.linhas > 300 and random.random() < 0.10:
            self._reta = 30
            esq, dir_ = self.margens[0]
            self.objetos.append({
                "tipo": "ponte", "x": esq, "y": -10.0, "vx": 0.0,
                "larg": dir_ - esq, "alt": 10, "vida": 1,
            })
            return

        opcoes = ["barco", "barco", "combustivel", "heli"]
        if not self.modo_crianca and self.pontos > 400:
            opcoes.append("aviao")
        tipo = random.choice(opcoes)
        larg, alt = TAMANHOS[tipo]
        x = random.uniform(esq + 2, max(esq + 2, dir_ - larg - 2))
        vx = 0.0
        if tipo == "barco":
            vx = random.choice([-1, 1]) * random.uniform(6, 14)
        elif tipo == "heli":
            vx = random.choice([-1, 1]) * random.uniform(14, 26)
        elif tipo == "aviao":
            vx = random.choice([-1, 1]) * random.uniform(30, 45)
        if self.modo_crianca:
            vx *= 0.6
        self.objetos.append({
            "tipo": tipo, "x": x, "y": -float(alt), "vx": vx,
            "larg": larg, "alt": alt, "vida": 1,
        })

    # --- ciclo ----------------------------------------------------------
    def atualizar(self, dt, ent):
        self._passar_aviso(dt)
        if self.terminou:
            return

        # velocidade do scroll (cima acelera, baixo freia)
        base = 34.0 if self.modo_crianca else 55.0
        alvo = base + (18 if ent.y < 0 else (-14 if ent.y > 0 else 0))
        self.vel += (alvo - self.vel) * min(1.0, dt * 4)

        # rola o rio
        self._sobra += self.vel * dt
        while self._sobra >= 1.0:
            self._sobra -= 1.0
            self.linhas += 1
            self.margens.insert(0, self._nova_linha())
            self.margens.pop()
            for o in self.objetos:
                o["y"] += 1
            self._proximo -= 1
            if self._proximo <= 0:
                self._nascer_algo()

        # aviao
        self.x += ent.x * (58.0 if self.modo_crianca else 72.0) * dt
        self.x = max(0.0, min(LARGURA - 9.0, self.x))

        # tiro: no modo crianca o aviaozinho atira sozinho
        self.recarga -= dt
        quer_atirar = ent.acao or self.modo_crianca
        if quer_atirar and self.recarga <= 0:
            self.recarga = 0.22
            self.tiros.append([self.x + 4.0, float(Y_AVIAO)])
            self.tocar("tiro")

        for t in self.tiros:
            t[1] -= 190 * dt
        self.tiros = [t for t in self.tiros if t[1] > -4]

        # combustivel
        gasto = 0.010 if self.modo_crianca else 0.030
        self.comb -= gasto * dt
        if self.comb <= 0:
            self.comb = 0.0
            self._bateu("SEM GASOLINA!")

        for o in self.objetos:
            o["x"] += o["vx"] * dt
            if o["vx"]:
                esq, dir_ = self._margem_em(o["y"] + o["alt"] / 2)
                if o["x"] < esq:
                    o["x"], o["vx"] = esq, abs(o["vx"])
                elif o["x"] + o["larg"] > dir_:
                    o["x"], o["vx"] = dir_ - o["larg"], -abs(o["vx"])
        self.objetos = [o for o in self.objetos if o["y"] < ALTURA + 20 and o["vida"] > 0]

        self._checar_tiros()
        self._checar_aviao(dt)

        for e in self.explosoes:
            e[2] -= dt
        self.explosoes = [e for e in self.explosoes if e[2] > 0]

    def _checar_tiros(self):
        for t in list(self.tiros):
            alvo_tiro = (t[0], t[1], 2, 4)
            for o in self.objetos:
                if o["tipo"] == "combustivel":
                    continue  # tanque nao explode: e amigo da crianca
                if colide(alvo_tiro, (o["x"], o["y"], o["larg"], o["alt"])):
                    o["vida"] = 0
                    self.pontos += PONTOS.get(o["tipo"], 10)
                    self.explosoes.append([o["x"] + o["larg"] / 2, o["y"] + o["alt"] / 2, 0.3])
                    if t in self.tiros:
                        self.tiros.remove(t)
                    self.tocar("ponto")
                    if o["tipo"] == "ponte":
                        self.avisar("PASSOU!", 1.2)
                    break

    def _checar_aviao(self, dt):
        aviao = (self.x, Y_AVIAO, 9, 10)
        for o in self.objetos:
            if not colide(aviao, (o["x"], o["y"], o["larg"], o["alt"])):
                continue
            if o["tipo"] == "combustivel":
                self.comb = min(1.0, self.comb + 0.55 * dt)
                self.avisar("GASOLINA", 0.3)
                continue
            if self.imune <= 0:
                self._bateu("OPA!")
                return

        if self.imune > 0:
            self.imune -= dt
            return
        esq, dir_ = self._margem_em(Y_AVIAO + 5)
        if self.x < esq or self.x + 9 > dir_:
            self._bateu("OPA!")

    def _bateu(self, msg):
        self.explosoes.append([self.x + 4, Y_AVIAO + 5, 0.4])
        self.avisar(msg, 1.0)
        self.tocar("opa")
        self.imune = 1.6
        esq, dir_ = self._margem_em(Y_AVIAO + 5)
        self.x = (esq + dir_) / 2 - 4
        self.comb = max(self.comb, 0.35)
        if not self.modo_crianca:
            self.vidas -= 1
            if self.vidas <= 0:
                self.terminou = True
                self.tocar("fim")

    # --- desenho ---------------------------------------------------------
    def desenhar(self, tela):
        tela.fill(CORES["verde_escuro"])
        for y in range(ALTURA):
            esq, dir_ = self.margens[y]
            pygame.draw.rect(tela, CORES["azul_escuro"], (int(esq), y, max(1, int(dir_ - esq)), 1))
        # faixa de areia na beira, para a margem ficar bem visivel
        for y in range(ALTURA):
            esq, dir_ = self.margens[y]
            pygame.draw.rect(tela, CORES["amarelo"], (max(0, int(esq) - 2), y, 2, 1))
            pygame.draw.rect(tela, CORES["amarelo"], (int(dir_), y, 2, 1))

        for o in self.objetos:
            self._desenhar_objeto(tela, o)
        for t in self.tiros:
            pygame.draw.rect(tela, CORES["branco"], (int(t[0]), int(t[1]), 2, 4))
        for e in self.explosoes:
            r = int(3 + (0.4 - e[2]) * 22)
            pygame.draw.circle(tela, CORES["laranja"], (int(e[0]), int(e[1])), max(2, r), 2)

        if self.imune <= 0 or int(self.imune * 12) % 2 == 0:
            self._desenhar_aviao(tela)

    def _desenhar_objeto(self, tela, o):
        x, y, w, h = int(o["x"]), int(o["y"]), int(o["larg"]), int(o["alt"])
        if o["tipo"] == "barco":
            pygame.draw.rect(tela, CORES["branco"], (x, y + 2, w, h - 2))
            pygame.draw.rect(tela, CORES["vermelho"], (x + w // 2 - 1, y, 3, 4))
        elif o["tipo"] == "heli":
            pygame.draw.rect(tela, CORES["amarelo"], (x + 2, y + 2, w - 4, h - 2))
            pygame.draw.rect(tela, CORES["branco"], (x, y, w, 1))
        elif o["tipo"] == "aviao":
            pygame.draw.rect(tela, CORES["rosa"], (x, y + 2, w, 2))
            pygame.draw.rect(tela, CORES["branco"], (x + w // 2 - 2, y, 4, h))
        elif o["tipo"] == "combustivel":
            pygame.draw.rect(tela, CORES["amarelo"], (x, y, w, h))
            pygame.draw.rect(tela, CORES["preto"], (x + 2, y + 4, w - 4, 6))
        elif o["tipo"] == "ponte":
            pygame.draw.rect(tela, CORES["marrom"], (x, y, w, h))
            for i in range(0, w, 6):
                pygame.draw.rect(tela, CORES["preto"], (x + i, y, 2, h))

    def _desenhar_aviao(self, tela):
        x, y = int(self.x), Y_AVIAO
        pygame.draw.rect(tela, CORES["branco"], (x + 3, y, 3, 10))     # fuselagem
        pygame.draw.rect(tela, CORES["amarelo"], (x, y + 4, 9, 3))     # asa
        pygame.draw.rect(tela, CORES["amarelo"], (x + 1, y + 8, 7, 2))  # cauda
        pygame.draw.rect(tela, CORES["vermelho"], (x + 3, y - 1, 3, 1))  # bico

    def desenhar_hud(self, tela, escala):
        texto(tela, f"PONTOS {self.pontos}", 8, 6, CORES["branco"], 26)
        barra(tela, 8, tela.get_height() - 26, 160, 14, self.comb,
              CORES["amarelo"] if self.comb > 0.25 else CORES["vermelho"])
        texto(tela, "GASOLINA", 174, tela.get_height() - 26, CORES["branco"], 22)
        if not self.modo_crianca:
            texto(tela, f"VIDAS {self.vidas}", tela.get_width() - 110, 6, CORES["branco"], 26)
        if self.aviso:
            texto(tela, self.aviso, tela.get_width() // 2, tela.get_height() // 3,
                  CORES["amarelo"], 60, centro=True)

    def icone(self, tela, ret):
        pygame.draw.rect(tela, CORES["verde_escuro"], ret)
        pygame.draw.rect(tela, CORES["azul_escuro"], (ret.centerx - 12, ret.y, 24, ret.h))
        pygame.draw.rect(tela, CORES["branco"], (ret.centerx - 8, ret.y + 8, 10, 5))
        pygame.draw.rect(tela, CORES["amarelo"], (ret.centerx + 3, ret.y + 20, 6, 10))
        x, y = ret.centerx - 4, ret.bottom - 20
        pygame.draw.rect(tela, CORES["branco"], (x + 3, y, 3, 10))
        pygame.draw.rect(tela, CORES["amarelo"], (x, y + 4, 9, 3))
