#!/usr/bin/env python3
"""Studio Shorts en application de bureau (Windows et macOS).

Lance le serveur du studio sur un port libre, en local, puis l'ouvre dans une fenêtre
native (pywebview : WebView2 sur Windows, WebKit sur macOS). Fermer la fenêtre arrête
le serveur ; les productions en cours continuent (ce sont des process détachés).

Lancement :  .venv/Scripts/python.exe studio/app.py   (macOS : .venv/bin/python studio/app.py)
"""
import os
import sys
import threading

import webview

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serveur  # noqa: E402

ICO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studio.ico")


def icone_windows(fenetre):
    """Sur Windows, pywebview reprend l'icône de pythonw.exe : on pose la nôtre sur la fenêtre."""
    try:
        from System import Action
        from System.Drawing import Icon
        f = fenetre.native
        f.Invoke(Action(lambda: setattr(f, "Icon", Icon(ICO))))
    except Exception as e:  # noqa: BLE001  (icône par défaut, rien de grave)
        print("icône :", e, file=sys.stderr)


def veille_auto():
    """Filet de sécurité de la tâche planifiée : app ouverte après 7 h sans veille du jour (ni en
    cours) → on la lance. Seulement sur le PC de Matys (Windows) : les veilles sont partagées, le
    Mac d'Elian ne la lance pas (STUDIO_VEILLE_AUTO=1 / 0 pour forcer)."""
    import time
    from datetime import datetime
    while os.environ.get("STUDIO_VEILLE_AUTO", "1" if os.name == "nt" else "0") != "0":
        if datetime.now().hour >= 7 and not serveur.veille_en_cours():
            if not serveur.veille_du_jour_faite():
                serveur.action_veille({"quotidien": True})
            else:  # veille finie pendant que l'app était fermée : on écrit les scripts manquants
                serveur.scripts_du_jour(datetime.now().strftime("%Y-%m-%d_jour"))
        time.sleep(600)


if __name__ == "__main__":
    http = serveur.serveur_http(0)  # port 0 = libre, pas de conflit avec un vieux serveur
    threading.Thread(target=http.serve_forever, daemon=True).start()
    threading.Thread(target=veille_auto, daemon=True).start()
    fenetre = webview.create_window("Studio Shorts", "http://127.0.0.1:%d/" % http.server_address[1],
                                    width=1480, height=920, min_size=(1100, 680), background_color="#16171a")
    if os.name == "nt":
        fenetre.events.shown += lambda: icone_windows(fenetre)
    webview.start(private_mode=False)  # garde le localStorage (onglet ouvert, panneaux) entre deux sessions
