import os

while True:
    comando = input("Digite um comando: ").lower()

    if comando == "abrir chrome":
        os.system("start chrome")

    elif comando == "abrir bloco de notas":
        os.system("notepad")

    elif comando == "sair":
        break

    else:
        print("Comando não reconhecido") 