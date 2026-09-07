#!/usr/bin/env bash
# Versao para Linux e macOS do jogar.bat. Torne executavel com: chmod +x jogar.sh
cd "$(dirname "$0")" || exit 1
python3 -c "import pygame" 2>/dev/null || python3 -m pip install --user -r requirements.txt
exec python3 main.py "$@"
