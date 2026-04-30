import subprocess
import os
import json

nome = input("Qual o seu nome? ")

print(f"Lox: Prazer, {nome}!")

comandos = {
    "chrome": ["chrome","navegador","google"] {
        "acao": lambda: os.system("start chrome"),
        "msg": f"Claro sr, Abrindo o chrome {nome}..."
    },
    "bloco de notas": lambda:subprocess.Popen("notepad"),
    "vs": lambda: subprocess.Popen("code", shell=True),
    "calculadora": lambda: subprocess.Popen("calc.exe"),
    "whatsapp": lambda: subprocess.Popen("start whatsapp://", shell=True),
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





