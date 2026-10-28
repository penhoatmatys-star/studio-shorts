"""Ressort les vrais scripts les plus proches d'un sujet, à garder sous les yeux pour écrire.

  python .claude/skills/script-shorts/outils/exemples.py "Sinner forfait Paris Bercy blessure" --format long --style maxparra -n 3

--style : maxparra (histoire d'un moment, d'un geste, d'une règle méconnue), topfoot (actu, polémique,
déclaration, opinion), mix (2 + 1). Classement : mots en commun avec le sujet, pondérés par les vues,
puis on varie les types de hook. Affiche le texte intégral et son découpage temps par temps.
"""
import argparse
import json
import math
import os
import re
import unicodedata

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDES = set("""le la les un une des de du d l et en au aux a à ce cet cette ces se sa son ses sur pour par
dans avec qui que qu quoi ne pas plus est sont été être avoir il elle ils elles on je tu nous vous lui leur
y c s n mais ou donc or ni car tout tous très bien fait faire comme alors quand vu va vont après avant""".split())


def norm(t):
    t = unicodedata.normalize("NFD", (t or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in VIDES}


def charger():
    corpus = json.load(open(os.path.join(ICI, "donnees", "corpus.json"), encoding="utf-8"))
    try:
        ann = json.load(open(os.path.join(ICI, "donnees", "annotations.json"), encoding="utf-8"))
    except (OSError, ValueError):
        ann = {}
    for s in corpus:
        s["ann"] = ann.get(s["id"])
    return corpus


def chercher(requete, fmt="long", style="mix", n=3):
    corpus = [s for s in charger() if s["format"] == fmt]
    q = norm(requete)

    def score(s):
        a = s["ann"] or {}
        sac = norm(s["titre"] + " " + s["texte"]) | norm(" ".join(a.get("mots_cles", [])) + " " + a.get("sport", ""))
        commun = len(q & sac)
        return (1 + commun) * math.log10(max(10, s["vues"]))

    def top(createur, k):
        if k <= 0:
            return []
        cands = sorted((s for s in corpus if createur in (None, s["createur"])), key=score, reverse=True)
        pris, hooks = [], set()
        for s in cands:                      # varier les types de hook
            h = (s["ann"] or {}).get("hook_type")
            if h and h in hooks and len(cands) > k * 3:
                continue
            pris.append(s)
            hooks.add(h)
            if len(pris) == k:
                break
        return pris
    if fmt == "court" or style == "maxparra":
        return top("maxparra", n)
    if style == "topfoot":
        return top("topfoot", n)
    return top("maxparra", n - n // 3) + top("topfoot", n // 3)


def afficher(s):
    a = s["ann"] or {}
    lignes = [f"## {s['id']} · {s['createur']} · {s['vues']:,} vues · {s['duree']} s · {s['titre']}"]
    if a:
        lignes.append(f"hook : {a['hook_type']} · nom caché au début : {a['nom_cache_au_debut']} · chute : {a['chute_type']}")
        lignes.append(f"promesse du hook : {a['hook_promesse']}")
        lignes += [f"  {i + 1}. [{t['role']}] « {t['debut']}… » : {t['fonction']}" for i, t in enumerate(a["temps"])]
        lignes.append("procédés : " + " ; ".join(a["procedes"]))
    lignes.append("\n" + s["texte"] + "\n")
    return "\n".join(lignes)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("requete")
    p.add_argument("--format", default="long", choices=["long", "court"])
    p.add_argument("--style", default="mix", choices=["maxparra", "topfoot", "mix"])
    p.add_argument("-n", type=int, default=3)
    a = p.parse_args()
    print("\n".join(afficher(s) for s in chercher(a.requete, a.format, a.style, a.n)))
