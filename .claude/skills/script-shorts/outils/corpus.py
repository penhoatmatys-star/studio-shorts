"""Construit donnees/corpus.json : les vrais scripts qui marchent, par format.
  long  = 45-80 s  (Max Parra + TopFoot narré)      -> modèle des shorts d'1 min
  court = 20-38 s  (Max Parra, les 150 plus vus)    -> modèle des shorts de 25-30 s
Lancement (depuis la racine du projet) : python .claude/skills/script-shorts/outils/corpus.py
"""
import json
import os
import re

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(ICI)))
MP = os.path.join(RACINE, "shorts", "_recherche_maxparra")
TF = os.path.join(RACINE, "shorts", "_recherche_topfoot")


def propre(t):
    return re.sub(r"\s+", " ", t or "").strip()


def main():
    sortie = []
    for x in json.load(open(os.path.join(MP, "index.json"), encoding="utf-8")):
        p = os.path.join(MP, "transcripts", x["id"] + ".txt")
        d = x.get("duree") or 0
        fmt = "long" if 45 <= d <= 80 else "court" if 20 <= d <= 38 else None
        if not (fmt and x.get("transcript_ok") and os.path.exists(p)):
            continue
        sortie.append({"id": "mp_" + x["id"], "createur": "maxparra", "format": fmt, "titre": x["titre"],
                       "vues": x["vues"], "duree": d, "texte": propre(open(p, encoding="utf-8").read())})
    for x in json.load(open(os.path.join(TF, "index.json"), encoding="utf-8")):
        d = x.get("duree") or 0
        if x.get("narre") and 45 <= d <= 80 and x.get("script"):
            sortie.append({"id": "tf_" + x["id"], "createur": "topfoot", "format": "long", "titre": propre(x["titre"]),
                           "vues": x["vues"], "duree": d, "texte": propre(x["script"])})
    courts = sorted((s for s in sortie if s["format"] == "court"), key=lambda s: -s["vues"])[:150]
    longs = sorted((s for s in sortie if s["format"] == "long"), key=lambda s: -s["vues"])
    for s in longs + courts:
        s["mots"] = len(re.findall(r"[\wÀ-ÿ'’-]+", s["texte"]))
    corpus = [s for s in longs + courts if s["mots"] >= 40]   # transcriptions vides ou ratées
    os.makedirs(os.path.join(ICI, "donnees"), exist_ok=True)
    with open(os.path.join(ICI, "donnees", "corpus.json"), "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=0)
    print(f"{sum(s['format'] == 'long' for s in corpus)} longs, {sum(s['format'] == 'court' for s in corpus)} courts")


if __name__ == "__main__":
    main()
