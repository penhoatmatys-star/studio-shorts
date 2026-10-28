"""Veille du jour, lancée chaque matin par le Planificateur de tâches Windows (tâche
« Studio Shorts - veille du jour ») : 9 sujets (4 shorts d'1 min dont 3 tennis et 1 foot,
5 shorts de 25-30 s) puis un script écrit pour chacun. Le résultat s'ouvre dans l'app.

Un seul ordinateur la lance (celui de Matys) : les veilles sont partagées par le dossier shorts/.
Lancement manuel : .venv/Scripts/python.exe -X utf8 studio/quotidien.py
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serveur  # noqa: E402

if __name__ == "__main__":
    try:
        msg = serveur.veille_du_jour_bloquante()
    except Exception as e:  # noqa: BLE001
        msg = "erreur : %s" % e
    with open(os.path.join(serveur.JOBS, "quotidien.log"), "a", encoding="utf-8") as f:
        f.write("%s  %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    print(msg)
