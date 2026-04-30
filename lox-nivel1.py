import subprocess
import os
import json

nome = input("Qual o seu nome? ")

print(f"Lox: Prazer, {nome}!")

while True:
    comando = input("Digite um comando: ").lower().strip()


    if "chrome" in comando:
        print(f"Lox: Claro sr, Abrindo o chrome {nome}...")
        os.system("start chrome")

    elif "bloco de notas" in comando:
        print(f"Claro sr, Abrindo Bloco de notas {nome}...")
        subprocess.Popen('notepad')

    elif "vs" in comando:
        print(f"Claro sr, Abrindo o vs code {nome}...")
        subprocess.Popen("code", shell=True)

    elif "whatsapp" in comando:
        print(f"Claro sr, Abrindo o whatsapp {nome}...")
        subprocess.Popen("start Whatsapp://", shell=True)

    elif "calculadora" in comando:
        print(f"Claro sr, Abrindo a calculadora {nome}...")
        subprocess.Popen("calc.exe")


    elif comando == "sair":
        print(f"Foi um prazer servir {nome}")
        break
    
    else:
        print("comando não reconhecido")


