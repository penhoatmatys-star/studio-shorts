"""Regénère donnees/structures.md : ce que font VRAIMENT les scripts qui marchent, en chiffres et
en exemples (hooks par vues, suites de temps, mots d'attaque de chaque temps, chutes, voix mesurée).

Lancement : python .claude/skills/script-shorts/outils/synthese.py
"""
import json
import os
import re
import statistics as st
from collections import Counter, defaultdict

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger():
    corpus = {s["id"]: s for s in json.load(open(os.path.join(ICI, "donnees", "corpus.json"), encoding="utf-8"))}
    ann = json.load(open(os.path.join(ICI, "donnees", "annotations.json"), encoding="utf-8"))
    emp = json.load(open(os.path.join(ICI, "donnees", "empreinte.json"), encoding="utf-8"))
    return corpus, {k: v for k, v in ann.items() if k in corpus}, emp


def premiere_phrase(t):
    return re.split(r"(?<=[.!?…])\s+", t.strip())[0]


def attaque(debut):
    return " ".join(re.findall(r"[\wÀ-ÿ'’-]+", debut.lower())[:2])


def section(titre, scripts, corpus, ann):
    ids = [i for i in scripts if i in ann]
    if not ids:
        return ""
    vues = {i: corpus[i]["vues"] for i in ids}
    L = [f"## {titre} ({len(ids)} scripts annotés)\n"]

    par_hook = defaultdict(list)
    for i in ids:
        par_hook[ann[i]["hook_type"]].append(i)
    L.append("### Hooks, du plus vu au moins vu (vues médianes)\n")
    L.append("| Type | Nb | Vues médianes | Exemple le plus vu (1re phrase) |\n|---|---|---|---|")
    for h, l in sorted(par_hook.items(), key=lambda kv: -st.median(vues[i] for i in kv[1])):
        best = max(l, key=lambda i: vues[i])
        ex = premiere_phrase(corpus[best]["texte"])[:220].replace("|", "/")
        L.append(f"| {h} | {len(l)} | {int(st.median(vues[i] for i in l)):,} | « {ex} » |")
    cache = sum(ann[i]["nom_cache_au_debut"] for i in ids)
    L.append(f"\nHéros d'abord décrit sans son nom : **{cache} scripts sur {len(ids)}** "
             f"({round(100 * cache / len(ids))} %).\n")

    # temps regroupés en grandes étapes, sinon chaque script a sa propre suite
    macro = {"contexte": "mise en place", "mystere": "mise en place", "escalade": "mise en place",
             "opinion": "mise en place", "explication": "explication", "preuve_clip": "preuve",
             "retournement": "retournement", "payoff": "dénouement", "chute": "dénouement",
             "cta": "cta", "hook": "hook"}
    seqs = Counter()
    vues_seq = defaultdict(list)
    for i in ids:
        roles = []
        for t in ann[i]["temps"]:
            r = macro.get(t["role"], t["role"])
            if not roles or roles[-1] != r:
                roles.append(r)
        k = " → ".join(roles)
        seqs[k] += 1
        vues_seq[k].append(vues[i])
    L.append("### Suites de temps les plus fréquentes\n")
    for k, n in seqs.most_common(8):
        L.append(f"- ({n}×, {int(st.median(vues_seq[k])):,} vues méd.) {k}")

    attaques = defaultdict(Counter)
    for i in ids:
        for t in ann[i]["temps"]:
            attaques[t["role"]][attaque(t["debut"])] += 1
    L.append("\n### Comment chaque temps commence (2 premiers mots les plus fréquents)\n")
    for r, c in sorted(attaques.items(), key=lambda kv: -sum(kv[1].values())):
        total = sum(c.values())
        top = ", ".join(f"« {w} » {round(100 * n / total)} %" for w, n in c.most_common(5))
        L.append(f"- **{r}** ({total}) : {top}")

    chutes = Counter(ann[i]["chute_type"] for i in ids)
    L.append("\n### Chutes\n")
    L.append(", ".join(f"{k} {round(100 * n / len(ids))} %" for k, n in chutes.most_common()))

    L.append("\n### Procédés relevés dans les 12 scripts les plus vus\n")
    for i in sorted(ids, key=lambda i: -vues[i])[:12]:
        L.append(f"- **{corpus[i]['titre'][:60]}** ({vues[i]:,} vues) : " + " ; ".join(ann[i]["procedes"]))
        L.append(f"  - pourquoi ça marche : {ann[i]['pourquoi_ca_marche']}")
    return "\n".join(L) + "\n"


def voix(emp):
    L = ["## Voix mesurée (médianes par script)\n",
         "| | Max Parra 1 min | TopFoot 1 min | Max Parra 20-38 s |\n|---|---|---|---|"]
    g = [emp["maxparra_long"], emp["topfoot_long"], emp["maxparra_court"]]
    for k, lib in [("mots", "Mots"), ("mots_par_phrase_mediane", "Mots par phrase"),
                   ("part_phrases_courtes_<=8", "Part de phrases ≤ 8 mots"),
                   ("part_phrases_longues_>=25", "Part de phrases ≥ 25 mots"), ("hook_mots", "Mots du hook"),
                   ("tu_vous_pour_100", "« tu / vous » pour 100 mots"), ("questions_par_script", "Questions")]:
        L.append(f"| {lib} | " + " | ".join(str(x[k]) for x in g) + " |")
    L.append("\nLe script modèle validé par Matys (Dembélé / Mbappé / Enrique) : 24 mots par phrase, 0 % de "
             "phrases courtes, hook de 20 mots, zéro « tu », zéro question. **La voix à viser est celle de "
             "Max Parra**, y compris sur l'actu ; TopFoot sert pour la mécanique des preuves enchaînées.\n")
    lia = emp["maxparra_long"]["liaisons_pour_100_moyenne"]
    L.append("Liaisons de Max Parra (pour 100 mots) : " + ", ".join(f"« {k} » {v}" for k, v in lia.items()) + "\n")
    return "\n".join(L)


def main():
    corpus, ann, emp = charger()
    groupes = [("Max Parra, shorts d'1 min", "maxparra", "long"), ("TopFoot, shorts d'1 min", "topfoot", "long"),
               ("Max Parra, shorts de 20-38 s", "maxparra", "court")]
    md = ["# Comment les scripts qui marchent sont construits\n",
          "Généré par `outils/synthese.py` depuis le corpus et ses annotations. Ne pas éditer à la main.\n",
          voix(emp)]
    for titre, c, f in groupes:
        md.append(section(titre, [i for i, s in corpus.items() if s["createur"] == c and s["format"] == f], corpus, ann))
    with open(os.path.join(ICI, "donnees", "structures.md"), "w", encoding="utf-8") as fo:
        fo.write("\n".join(md))
    print(f"structures.md : {len(ann)} scripts annotés")


if __name__ == "__main__":
    main()
