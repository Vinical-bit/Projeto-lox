"""Desenha o icone do fliperama e salva em icone.ico (usado pelo atalho e pelo .exe).

Nao usa nenhuma biblioteca de imagem: o pygame salva um PNG e aqui o PNG e
embrulhado no formato .ico na mao. Um .ico e so um cabecalho pequeno seguido
das imagens - da para montar com struct.
"""

import io
import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from motor.nucleo import desenhar_joystick  # noqa: E402

LADO = 32          # arte em 32x32...
FINAL = 256        # ...ampliada para 256x256, que e o tamanho maximo do .ico


def desenhar():
    """Amplia o joystick da tela inicial para o tamanho do icone."""
    tela = pygame.Surface((FINAL, FINAL))
    desenhar_joystick(tela, pygame.Rect(0, 0, FINAL, FINAL))
    return tela


def png_bytes(superficie):
    buffer = io.BytesIO()
    pygame.image.save(superficie, buffer, "icone.png")
    return buffer.getvalue()


def escrever_ico(caminho, dados_png):
    largura = 0 if FINAL >= 256 else FINAL     # 0 significa 256 no formato .ico
    cabecalho = struct.pack("<HHH", 0, 1, 1)   # reservado, tipo=icone, 1 imagem
    entrada = struct.pack(
        "<BBBBHHII", largura, largura, 0, 0, 1, 32, len(dados_png), 6 + 16
    )
    with open(caminho, "wb") as arquivo:
        arquivo.write(cabecalho + entrada + dados_png)


def main():
    pygame.init()
    pygame.display.set_mode((32, 32))
    destino = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icone.ico")
    escrever_ico(destino, png_bytes(desenhar()))
    pygame.quit()
    print(f"icone gerado em {destino}")


if __name__ == "__main__":
    main()
