# Fliperama de Casa

Quatro jogos no estilo Atari 2600, feitos em Python + pygame, pensados para
jogar com uma criança pequena (a partir de uns 4 anos) e para servir de
oficina: dá para abrir o código, mudar um número e ver o efeito na hora.

Tudo é desenhado numa telinha de **160x210 pixels** — a mesma proporção do
Atari — e depois ampliada. É por isso que o visual é quadradão de propósito.

## Como rodar

```bash
cd jogos
pip install -r requirements.txt
python main.py
```

Atalhos para abrir direto num jogo (útil para deixar um atalho na área de
trabalho da criança):

```bash
python main.py --galinha
python main.py --rio
python main.py --submarino
python main.py --boxe
python main.py --dificil     # desliga o modo criança
python main.py --sem-som
```

## Os jogos

| Jogo | O que faz | Controles |
| --- | --- | --- |
| **A Galinha** | Atravessar a estrada sem ser atropelado | Só ↑ e ↓ |
| **Rio Perigoso** | Subir o rio, atirar e reabastecer | ← → (↑↓ mudam a velocidade), espaço atira |
| **Submarino** | Resgatar mergulhadores e subir para respirar | Setas, espaço atira |
| **Boxe** | Um contra um, de cima | Setas + espaço (2º jogador: WASD + Shift) |

Comece pela **Galinha**: são só duas teclas e ninguém morre. É o melhor
primeiro contato com um controle.

No **Boxe**, o segundo jogador entra sozinho: basta encostar em W/A/S/D que
o computador sai e você assume. Serve para jogar pai contra filho no mesmo
teclado.

## Modo criança (ligado por padrão)

Os jogos originais de Atari eram difíceis de propósito — eram feitos para
adultos gastarem fichas. Para uma criança de 4 anos isso vira frustração em
dois minutos. O modo criança muda o jogo, não só a velocidade:

- **ninguém perde o jogo**: bater é um "OPA!", uma piscadinha e segue;
- combustível e oxigênio acabam ~3x mais devagar;
- tudo se move mais devagar e o rio é mais largo;
- no Rio e no Submarino a arma **atira sozinha** — uma coisa a menos para
  coordenar;
- na Galinha não existe cronômetro: dá para ficar atravessando o dia inteiro;
- o boxeador do computador é lento e distraído.

Aperte **C** a qualquer momento (no menu ou dentro do jogo) para ligar e
desligar. Com o modo desligado o jogo fica parecido com o original: vidas,
tempo e fim de jogo.

## Teclas gerais

| Tecla | O que faz |
| --- | --- |
| Setas | mover / escolher no menu |
| Espaço | confirmar / atirar / socar |
| ESC | voltar ao menu (e sair, se já estiver no menu) |
| C | liga e desliga o modo criança |
| P | pausa |
| R | recomeça a partida |
| F | tela cheia |

Controle de USB também funciona: o direcional e qualquer um dos quatro
primeiros botões. Dois controles = dois jogadores no Boxe.

## Sobre emuladores e ROMs

Estes **não são** os jogos originais nem emuladores: são jogos novos,
escritos aqui do zero, inspirados nas mecânicas dos clássicos de 1980-83.

Rodar os cartuchos originais exige duas coisas separadas: um emulador (o
[Stella](https://stella-emu.github.io/) é livre e legal) e as ROMs, que
continuam sendo obra protegida — a Activision ainda é dona de River Raid,
Seaquest, Freeway e Boxing. Baixar essas ROMs da internet não é legal, mesmo
que o jogo tenha 40 anos e mesmo que "todo mundo faça". Os caminhos legítimos
são coletâneas oficiais (o *Atari 50*, por exemplo) ou extrair a ROM de um
cartucho que você mesmo possui.

Por isso o menu daqui abre jogos próprios. Se um dia você tiver ROMs de forma
legítima, dá para acrescentar um item no menu que chama o Stella — é o mesmo
`subprocess` que o `lox.py` já usa na raiz do projeto.

## Como acrescentar um jogo novo

O `main.py` não conhece nenhum jogo por dentro: ele só chama quatro métodos.
Para criar o quinto jogo:

1. copie `titulos/galinha.py` para `titulos/meu_jogo.py`;
2. mantenha a classe chamada `Jogo` herdando de `JogoBase` e preencha
   `nome`, `descricao`, `cor` e `ajuda`;
3. escreva `reiniciar`, `atualizar(dt, ent)`, `desenhar(tela)`,
   `desenhar_hud(tela, escala)` e `icone(tela, ret)`;
4. importe no `main.py` e acrescente a classe na lista `JOGOS`.

Nunca leia o teclado direto: use o `ent` que chega no `atualizar`
(`ent.x`, `ent.y`, `ent.acao`, `ent.acao_apertou`). É assim que o mesmo
código funciona no teclado e no controle.

## Teste

```bash
python testes/fumaca.py
```

Roda os quatro jogos sem abrir janela, um minuto de jogo cada um, nos dois
modos, apertando teclas ao acaso. Não prova que o jogo é divertido — prova
que ele não quebra sozinho. Rode isso depois de mexer em qualquer coisa.

## Estrutura

```
jogos/
├── main.py            menu e laço principal
├── motor/
│   ├── nucleo.py      resolução, cores, classe base, desenho
│   ├── entrada.py     teclado e controle num formato único
│   └── som.py         bipes sintetizados na hora (sem arquivos)
├── titulos/           um arquivo por jogo
└── testes/fumaca.py   teste automático
```
