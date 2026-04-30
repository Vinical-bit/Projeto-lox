import subprocess
import os
import json

nome = input("Qual o seu nome? ")

print(f"Lox: Prazer, {nome}!")

comandos = {
    "chrome":{
        "acao": lambda: os.system("start chrome"),
        "msg": f"Claro sr, Abrindo o chrome {nome}...",
    },
    "bloco de notas":{
        "acao": lambda:subprocess.Popen("notepad"),
        "msg": f"Claro sr, Abrindo o bloco de notas {nome}...",
    },
    "vs":{
        "acao": lambda: subprocess.Popen("code", shell=True),
        "msg": f"Claro sr, Abrindo o Vs code {nome}...",
    },
    "calculadora": {
        "acao": lambda: subprocess.Popen("calc.exe"),
        "msg": f"Claro sr, Abrindo a Calculadora {nome}...",
    },
    "whatsapp":{
        "acao":lambda: subprocess.Popen("start whatsapp://", shell=True),
        "msg": f"Claro sr, Abrindo o Whatsapp {nome}...",
    },

    "spotify": {
        "acao": lambda: subprocess.Popen("start spotify://", shell=True),
        "msg": f"Claro sr, Abrindo Spotify {nome}...",
    },

    "relogio": {
        "acao": lambda: subprocess.Popen("start ms-clock:", shell=True),
        "msg": f"Claro sr, Abrindo o Relogio {nome}...",
    },

}

while True:
    comando = input("Digite um comando: ").lower()

    if comando == "sair":
        print(f"Foi um prazer servir {nome}")
        break
    
    encontrou = False

    for chave in comandos:
        if chave in comando:
            print(comandos[chave]["msg"])
            comandos[chave]["acao"]()
            encontrou = True
            break
    if not encontrou:
        print(f"Desculpa {nome} não entedi")





