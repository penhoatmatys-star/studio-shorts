#!/usr/bin/env python3
"""Écrit le brouillon CapCut d'un projet (Windows), en sécurité même si plusieurs montages tournent.

    .venv/Scripts/python.exe _bin/monter_capcut.py shorts/<projet>

Verrou exclusif (les autres montages attendent), puis : ferme CapCut, lance monter_edl.py,
contrôle le brouillon, rouvre CapCut et recontrôle.
"""
import glob
import json
import msvcrt
import os
import subprocess
import sys
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERROU = os.path.join(RACINE, "_bin", ".capcut.lock")
DRAFTS = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")


def capcut_ouvert():
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"], capture_output=True, text=True, errors="replace")
    return "CapCut.exe" in r.stdout


def fermer_capcut():
    if not capcut_ouvert():
        return
    subprocess.run(["taskkill", "/IM", "CapCut.exe"], capture_output=True)
    for _ in range(20):
        if not capcut_ouvert():
            time.sleep(1)
            return
        time.sleep(1)
    subprocess.run(["taskkill", "/F", "/T", "/IM", "CapCut.exe"], capture_output=True)
    time.sleep(2)


def rouvrir_capcut():
    cands = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe")) + \
            glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\*\CapCut.exe"))
    if cands:
        os.startfile(cands[0])
    else:
        print("[!] CapCut.exe introuvable : ouvre CapCut à la main.")


def controle(nom):
    for f in ("draft_content.json", "draft_info.json"):
        p = os.path.join(DRAFTS, nom, f)
        if os.path.exists(p):
            break
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        pistes = len(d.get("tracks", []))
        segs = sum(len(t.get("segments", [])) for t in d.get("tracks", []))
        return pistes, segs, d.get("duration", 0) / 1e6
    except (OSError, ValueError, UnboundLocalError):
        return 0, 0, 0


def monter(projet):
    fermer_capcut()
    if capcut_ouvert():
        sys.exit("[X] CapCut refuse de se fermer : brouillon non écrit.")
    r = subprocess.run([os.path.join(RACINE, ".venv", "Scripts", "python.exe"),
                        os.path.join(RACINE, "monter_edl.py"), projet], cwd=RACINE)
    if r.returncode:
        sys.exit("[X] monter_edl.py a échoué (code %d)" % r.returncode)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    projet = sys.argv[1].rstrip("/\\")
    nom = os.path.basename(projet)
    with open(VERROU, "w") as verrou:
        while True:
            try:
                msvcrt.locking(verrou.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                print("[…] un autre montage écrit dans CapCut : j'attends mon tour", flush=True)
                time.sleep(5)
        for essai in (1, 2):
            monter(projet)
            avant = controle(nom)
            print("[OK] brouillon écrit : %d pistes, %d segments, %.1f s" % avant, flush=True)
            rouvrir_capcut()
            time.sleep(20)
            apres = controle(nom)
            if apres[0] and apres[1] >= avant[1]:
                print("[OK] CapCut a gardé le projet : %d pistes, %d segments" % apres[:2])
                return
            print("[!] CapCut a vidé le brouillon (%d pistes) : nouvel essai" % apres[0], flush=True)
        sys.exit("[X] CapCut a écrasé le brouillon deux fois : à vérifier à la main.")


if __name__ == "__main__":
    main()
