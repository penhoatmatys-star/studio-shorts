"""Test à l'aveugle : mélange des scripts à juger avec de vrais scripts de la base, les donne à un
juge Claude neuf (sans contexte) qui doit dire lesquels sont écrits par une IA. Si le juge repère nos
scripts facilement, la méthode n'est pas encore bonne.

  python .claude/skills/script-shorts/outils/test_aveugle.py a.txt b.txt c.txt [--vrais 3] [--format long]

Chaque fichier = un script (les lignes [CLIP …] sont retirées, comme dans une transcription).
"""
import argparse
import json
import os
import random
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(ICI)))
sys.path.insert(0, os.path.join(RACINE, "studio"))
import serveur  # noqa: E402

SCHEMA = {"type": "object", "properties": {"jugements": {"type": "array", "items": {"type": "object", "properties": {
    "n": {"type": "integer"}, "proba_ia": {"type": "number", "description": "0 à 100"},
    "indices": {"type": "string", "description": "ce qui t'a fait pencher, concrètement (1-2 phrases)"}},
    "required": ["n", "proba_ia", "indices"]}}}, "required": ["jugements"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fichiers", nargs="+")
    p.add_argument("--vrais", type=int, default=3)
    p.add_argument("--format", default="long")
    a = p.parse_args()
    corpus = [s for s in json.load(open(os.path.join(ICI, "donnees", "corpus.json"), encoding="utf-8"))
              if s["format"] == a.format and s["createur"] == "maxparra"]
    rng = random.Random()
    vrais = rng.sample(sorted(corpus, key=lambda s: -s["vues"])[:40], a.vrais)
    items = [{"source": "vrai:" + s["id"], "texte": s["texte"]} for s in vrais]
    for f in a.fichiers:
        t = open(f, encoding="utf-8").read()
        t = re.sub(r"(?m)^\s*\[CLIP[^\n]*\n?", "", t)
        items.append({"source": "nous:" + os.path.basename(f), "texte": re.sub(r"\s+", " ", t).strip()})
    rng.shuffle(items)
    blocs = "\n\n".join(f"### Texte {i + 1}\n{x['texte']}" for i, x in enumerate(items))
    prompt = f"""Voici {len(items)} voix off de YouTube Shorts sport en français. Certaines ont été écrites par
des créateurs humains (transcrites automatiquement : ignore totalement les fautes d'orthographe, les
mots mal transcrits et la ponctuation), d'autres ont été écrites par une IA. Le nombre de chaque n'est
pas indiqué. Pour chaque texte, donne la probabilité (0-100) qu'il soit écrit par une IA et les indices
concrets de style ou de structure qui te font pencher (pas l'orthographe).

{blocs}"""
    d = serveur.appel_claude(prompt, schema=SCHEMA, outils="Read", timeout=600, modele="opus")
    res = {j["n"]: j for j in d["jugements"]}
    print("| Texte | Source réelle | Proba IA | Indices |\n|---|---|---|---|")
    for i, x in enumerate(items):
        j = res.get(i + 1, {})
        print(f"| {i + 1} | {x['source']} | {j.get('proba_ia', '?')} | {j.get('indices', '')} |")
    nous = [res[i + 1]["proba_ia"] for i, x in enumerate(items) if x["source"].startswith("nous") and i + 1 in res]
    vrai = [res[i + 1]["proba_ia"] for i, x in enumerate(items) if x["source"].startswith("vrai") and i + 1 in res]
    print(f"\nMoyenne proba IA : nos scripts {sum(nous) / max(1, len(nous)):.0f} / vrais scripts {sum(vrai) / max(1, len(vrai)):.0f}")


if __name__ == "__main__":
    main()
