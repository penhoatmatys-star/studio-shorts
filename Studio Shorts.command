#!/bin/bash
# Studio Shorts sur macOS : double-clic dans le Finder.
cd "$(dirname "$0")"
export PYTHONUTF8=1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
if [ ! -x .venv/bin/python ]; then
  echo "Lance d'abord « Installer (Mac).command »"
  read -r -p "Entrée pour fermer"
  exit 1
fi
mkdir -p studio/_jobs shorts/_veille
exec .venv/bin/python studio/app.py
