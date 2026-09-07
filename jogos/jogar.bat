@echo off
REM Clique duas vezes neste arquivo para abrir o fliperama.
setlocal
cd /d "%~dp0"
title Fliperama de Casa

REM --- 1. acha o Python -------------------------------------------------
set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo.
  echo Nao encontrei o Python neste computador.
  echo Instale em https://www.python.org/downloads/ e marque
  echo a caixinha "Add Python to PATH" durante a instalacao.
  echo.
  pause
  exit /b 1
)

REM --- 2. garante o pygame (so demora na primeira vez) -------------------
%PY% -c "import pygame" >nul 2>nul
if errorlevel 1 (
  echo Preparando o fliperama pela primeira vez, aguarde...
  %PY% -m pip install --user -r requirements.txt
)

REM --- 3. joga ----------------------------------------------------------
%PY% main.py %*
if errorlevel 1 (
  echo.
  echo O jogo fechou com erro. A mensagem acima diz o motivo.
  pause
)
