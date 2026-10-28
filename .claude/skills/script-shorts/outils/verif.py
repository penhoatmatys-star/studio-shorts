"""Compare un script à la voix mesurée des créateurs et liste les écarts à corriger.

  python .claude/skills/script-shorts/outils/verif.py script.txt --style maxparra --format long
  (ou le texte sur l'entrée standard : ... verif.py - --style topfoot)

Sortie : les mesures du script, la cible (médiane de la base), et une liste « À CORRIGER ».
Code de sortie 1 s'il reste des écarts bloquants.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from empreinte import mesurer  # noqa: E402

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTS = {"long": (260, 275), "court": (110, 130)}
# Interdits de Matys (CLAUDE.md global et mémoire « style rédaction anti-IA »)
INTERDITS = {"—": "tiret cadratin", " du coup": "« du coup » (banni par Matys)",
             "explorons": "mot banni", "plongeons": "mot banni", "il convient de noter": "mot banni",
             "robuste": "mot banni", "transformer": "mot banni"}


def verifier(texte, style, fmt):
    m = mesurer(texte)
    emp = json.load(open(os.path.join(ICI, "donnees", "empreinte.json"), encoding="utf-8"))
    cible = emp["maxparra_court" if fmt == "court" else f"{style}_long"]
    bloquant, conseil = [], []
    lo, hi = MOTS[fmt]
    if not lo - 10 <= m["mots"] <= hi + 10:
        bloquant.append(f"{m['mots']} mots de VO, cible {lo}-{hi}")
    med = cible["mots_par_phrase_mediane"]
    if abs(m["mots_par_phrase_mediane"] - med) > med * 0.35:
        sens = "trop hachées : fusionne avec « parce que », « vu que », « alors », « sauf que »" \
            if m["mots_par_phrase_mediane"] < med else "trop longues : coupe aux retournements"
        bloquant.append(f"phrases de {m['mots_par_phrase_mediane']} mots en médiane, la base est à {med} ({sens})")
    cc = cible["part_phrases_courtes_<=8"]
    if m["part_phrases_courtes_<=8"] > cc + 0.12:
        bloquant.append(f"{int(m['part_phrases_courtes_<=8'] * 100)} % de phrases de 8 mots ou moins, la base est à "
                        f"{int(cc * 100)} % : les fragments punchy sonnent IA")
    hk = cible["hook_mots"]
    if abs(m["hook_mots"] - hk) > hk * 0.45:
        conseil.append(f"hook de {m['hook_mots']} mots, la base est à {hk}")
    if style != "topfoot" and m["tu_vous_pour_100"] > 0.8:
        conseil.append("beaucoup de « tu / vous » : Max Parra raconte, il ne s'adresse presque jamais au spectateur")
    if m["questions"] > 1:
        conseil.append(f"{m['questions']} questions : la base en a 0 en médiane")
    for t in m["tics_ia"]:
        bloquant.append(f"tic d'écriture IA : « {t} »")
    low = texte.lower()
    for k, v in INTERDITS.items():
        if k in low:
            bloquant.append(v)
    if re.search(r"\b(?:ce n'est pas|c'est pas)\b[^.!?]{1,60}[,.] *c'est\b", low):
        bloquant.append("formule « ce n'est pas X, c'est Y » (interdite)")
    return m, cible, bloquant, conseil


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("fichier", help="fichier texte, ou - pour l'entrée standard")
    # La VOIX visée est toujours celle de Max Parra (le script modèle de Matys la suit aussi) ;
    # --style topfoot ne sert qu'à mesurer un texte de TopFoot.
    p.add_argument("--style", default="maxparra", choices=["maxparra", "topfoot"])
    p.add_argument("--format", default="long", choices=["long", "court"])
    a = p.parse_args()
    texte = sys.stdin.read() if a.fichier == "-" else open(a.fichier, encoding="utf-8").read()
    m, cible, bloquant, conseil = verifier(texte, a.style, a.format)
    print(f"Script : {m['mots']} mots, phrases {m['mots_par_phrase_mediane']} mots (médiane), "
          f"{int(m['part_phrases_courtes_<=8'] * 100)} % courtes, hook {m['hook_mots']} mots")
    print(f"Base   : {cible['mots']} mots, phrases {cible['mots_par_phrase_mediane']} mots, "
          f"{int(cible['part_phrases_courtes_<=8'] * 100)} % courtes, hook {cible['hook_mots']} mots")
    for x in bloquant:
        print("À CORRIGER :", x)
    for x in conseil:
        print("À VÉRIFIER :", x)
    if not bloquant:
        print("OK : dans la voix de la base.")
    sys.exit(1 if bloquant else 0)
