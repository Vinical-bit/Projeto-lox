# Projeto Lox

Repositório pessoal com duas coisas independentes:

1. **`lox*.py` (raiz)** — assistente de linha de comando que abre programas do
   Windows por palavra-chave. Três versões do mesmo exercício, do mais simples
   ao mais escalável: `lox-nivel1.py` (if/elif), `lox-nivel2.py` e `lox.py`
   (dicionário de comandos com `lambda`).
2. **`jogos/`** — "Fliperama de Casa": quatro jogos estilo Atari 2600 em Python
   + pygame, feitos para brincar com uma criança de ~4 anos e para servir de
   oficina de código. Ver `jogos/README.md`.

## Contexto importante

O objetivo dos jogos é **coordenação motora de criança pequena e mostrar o que
dá para fazer com IA** — não é recriar a dificuldade dos originais. Por isso o
**modo criança vem ligado por padrão** e é uma regra de design, não um detalhe:

- ninguém perde o jogo (bater é um "OPA!", piscada e segue);
- recursos (combustível, oxigênio) caem ~3x mais devagar;
- tiro automático no Rio e no Submarino — mirar, atirar e desviar ao mesmo
  tempo é carga demais nessa idade;
- sem cronômetro na Galinha.

A tecla `C` alterna para o modo original (vidas, tempo, fim de jogo). Ao mexer
em qualquer jogo, mantenha os dois modos funcionando.

## Como rodar e testar

```bash
cd jogos
pip install -r requirements.txt
python main.py                 # ou jogar.bat no Windows
python testes/fumaca.py        # OBRIGATÓRIO depois de mexer em qualquer jogo
```

`testes/fumaca.py` roda os quatro jogos sem abrir janela (SDL dummy), um minuto
cada um, nos dois modos, com comandos aleatórios, e percorre
abertura → menu → jogo → menu → abertura. É rápido e pega quase toda quebra.

O executável do Windows é construído pelo GitHub Actions
(`.github/workflows/executavel.yml`) e também por `jogos/construir_exe.bat`
(PyInstaller, `--onefile --windowed`). O ícone vem de
`jogos/ferramentas/gerar_icone.py`, que desenha e escreve o `.ico` na mão.

## Convenções de código

- **Código e comentários em português**, sem acentos nos identificadores e nos
  comentários (evita dor de cabeça de encoding no Windows); textos que aparecem
  na tela também vão sem acento, porque a fonte padrão do pygame renderiza mal.
- Cada jogo é um arquivo em `jogos/titulos/` com uma classe `Jogo(JogoBase)` e
  cinco métodos: `reiniciar`, `atualizar(dt, ent)`, `desenhar(tela)`,
  `desenhar_hud(tela, escala)`, `icone(tela, ret)`. O `main.py` não conhece
  nada além disso — para acrescentar um jogo, basta criar o arquivo e incluir a
  classe na lista `JOGOS`.
- **Nunca ler o teclado direto dentro de um jogo.** Use o `ent` que chega em
  `atualizar` (`ent.x`, `ent.y`, `ent.acao`, `ent.acao_apertou`, `ent.p2`). É o
  que faz o mesmo código funcionar com teclado e com controle USB.
- Tudo é desenhado numa superfície interna de **160x210** (proporção do Atari
  2600) e ampliada por `main.py`. Só o HUD é desenhado na tela grande, para o
  texto ficar legível.
- Sem dependências novas sem necessidade: hoje o projeto usa **só o pygame**.
  Sons são gerados em código (`motor/som.py`), o ícone também.

## Git

Trabalho em andamento na branch `claude/jogo-atributos-n7fdqb`. `main` ainda
tem só o assistente Lox.
