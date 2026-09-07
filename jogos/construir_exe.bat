@echo off
REM Gera o Fliperama.exe, que roda sem precisar de Python instalado.
REM Rode UMA vez; o resultado aparece em jogos\dist\Fliperama.exe
setlocal
cd /d "%~dp0"
title Construindo o Fliperama.exe

set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Instale o Python primeiro: https://www.python.org/downloads/
  pause
  exit /b 1
)

echo Instalando as ferramentas de construcao...
%PY% -m pip install --user pygame pyinstaller

echo Construindo (leva alguns minutos)...
%PY% -m PyInstaller --noconfirm --onefile --windowed --clean ^
  --name Fliperama --icon icone.ico main.py

if exist dist\Fliperama.exe (
  echo.
  echo Pronto: dist\Fliperama.exe
  echo Arraste esse arquivo para a area de trabalho e clique duas vezes.
) else (
  echo.
  echo A construcao falhou. A mensagem acima diz o motivo.
)
pause
