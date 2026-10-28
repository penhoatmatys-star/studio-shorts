"""Dessine l'icône de l'app (studio/web/logo.svg) en studio/studio.ico, pour Windows.
Lancement : .venv/Scripts/python.exe studio/icone.py"""
import os

from PIL import Image, ImageDraw

ICI = os.path.dirname(os.path.abspath(__file__))
T = 1024  # dessin en grand puis réduction : bords nets à toutes les tailles
k = T / 32
img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, T - 1, T - 1], radius=7 * k, fill="#1d1f24")
d.rounded_rectangle([10 * k, 4.5 * k, 22 * k, 27.5 * k], radius=2.5 * k, outline="#f08a3c", width=int(2 * k))
d.polygon([(14 * k, 12.5 * k), (14 * k, 19.5 * k), (19.5 * k, 16 * k)], fill="#f08a3c")
img.save(os.path.join(ICI, "studio.ico"), sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
img.resize((256, 256), Image.LANCZOS).save(os.path.join(ICI, "web", "logo.png"))
print("ok")
