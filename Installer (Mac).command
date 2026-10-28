#!/bin/bash
# Studio Shorts : installation sur macOS (équivalent de « 1 - Installer.bat »).
# Double-clic dans le Finder. La première fois : clic droit > Ouvrir (Gatekeeper).
set -e
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
echo "== Studio Shorts : installation (5-10 min, ~2 Go) =="

if ! command -v uv >/dev/null; then
  echo "-> installation de uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
if ! command -v claude >/dev/null; then
  echo "-> installation de Claude Code"
  curl -fsSL https://claude.ai/install.sh | bash
fi
mkdir -p studio/_jobs shorts/_veille

echo "-> environnement de MONTAGE (.venv)"
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
SP=$(.venv/bin/python -c "import site;print(site.getsitepackages()[-1])")
rm -rf "$SP/pyJianYingDraft" && cp -R vendor/pyJianYingDraft "$SP/pyJianYingDraft"

echo "-> environnement de TELECHARGEMENT (.venv312)"
uv venv --python 3.12 .venv312
uv pip install --python .venv312/bin/python -U yt-dlp imageio-ffmpeg

echo "-> ffmpeg"
.venv/bin/python -c "import imageio_ffmpeg,shutil,os;shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(),'_bin/ffmpeg');os.chmod('_bin/ffmpeg',0o755)"
chmod +x "Studio Shorts.command"

echo
echo "== Installation terminée =="
echo "Reste à faire, une seule fois :"
echo "  1. claude auth login   (connexion à ton compte Claude)"
echo "  2. copier _voix_clone/elevenlabs.json (clé ElevenLabs, à recevoir de Matys en privé, jamais par Git)"
echo "  3. installer CapCut et l'ouvrir une fois"
echo "Ensuite : double-clic sur « Studio Shorts.command »."
read -r -p "Entrée pour fermer"
