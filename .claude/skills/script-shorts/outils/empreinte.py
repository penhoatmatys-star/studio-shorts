"""Empreinte de voix mesurée sur le corpus (pas d'avis, des comptes) -> donnees/empreinte.json
et donnees/empreinte.md. Sert aussi de module : mesurer(texte) pour comparer un script à la base.

Lancement : python .claude/skills/script-shorts/outils/empreinte.py
"""
import json
import os
import re
import statistics as st
from collections import Counter

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Liaisons et tournures suivies (minuscules). Comptées pour 100 mots.
LIAISONS = ["et pour cause", "sauf que", "parce que", "alors", "vu que", "étant donné que", "ce qui fait que",
            "mais", "donc", "en fait", "du coup", "bizarrement", "étrangement", "à la surprise générale",
            "personne ne se doutait", "tout le monde", "beaucoup", "en réalité", "autrement dit", "pour une très bonne raison",
            "c'est ici que", "c'est là que", "et c'est pour ça que", "aujourd'hui", "abonne-toi", "abonnez-vous"]
# Tics d'écriture IA en français : à éviter (absents ou rarissimes dans la base)
TICS_IA = ["imaginez", "et là,", "le verdict", "résultat :", "spoiler", "plot twist", "accrochez-vous",
           "vous n'allez pas croire", "incroyable mais vrai", "le pire ?", "la suite ?", "mais attendez",
           "et ce n'est pas tout", "véritable", "véritablement", "littéralement", "tout simplement",
           "il faut savoir que", "en effet", "par ailleurs", "néanmoins", "toutefois", "ainsi,", "en somme",
           "force est de constater", "au final", "un coup de maître", "a fait trembler", "un séisme",
           "historique", "légendaire", "choc", "fracassant", "retentissant", "en coulisses", "dans l'ombre"]


def phrases(t):
    return [p.strip() for p in re.split(r"(?<=[.!?…])\s+", t) if len(p.strip()) > 1]


def mots(t):
    return re.findall(r"[\wÀ-ÿ'’-]+", t)


def mesurer(texte):
    t = re.sub(r"\[[^\]]*\]", " ", texte)          # [CLIP …] et [musique] ne sont pas dits par la VO
    ph = phrases(t)
    n = max(1, len(mots(t)))
    low = " " + t.lower() + " "
    lg = [len(mots(p)) for p in ph] or [0]
    return {
        "mots": n,
        "phrases": len(ph),
        "mots_par_phrase_mediane": st.median(lg),
        "part_phrases_courtes_<=8": round(sum(x <= 8 for x in lg) / len(lg), 2),
        "part_phrases_longues_>=25": round(sum(x >= 25 for x in lg) / len(lg), 2),
        "hook_mots": lg[0],
        "hook": ph[0] if ph else "",
        "chute": ph[-1] if ph else "",
        "va_infinitif_pour_100": round(100 * len(re.findall(r"\b(?:va|vont|allait|allaient)\s+[a-zà-ÿ]+(?:er|ir|re)\b", low)) / n, 2),
        "tu_vous_pour_100": round(100 * len(re.findall(r"\b(?:tu|te|toi|vous|ton|ta|tes|votre|vos)\b", low)) / n, 2),
        "je_pour_100": round(100 * len(re.findall(r"\b(?:je|j'|moi|me)\b", low)) / n, 2),
        "questions": sum(p.endswith("?") for p in ph),
        "liaisons_pour_100": {k: round(100 * low.count(" " + k) / n, 2) for k in LIAISONS if low.count(" " + k)},
        "tics_ia": [k for k in TICS_IA if " " + k in low],
    }


def profil(scripts):
    m = [mesurer(s["texte"]) for s in scripts]
    def med(k):
        return round(st.median(x[k] for x in m), 2)
    liaisons = Counter()
    for x in m:
        liaisons.update(x["liaisons_pour_100"])
    ouvertures = Counter(" ".join(mots(x["hook"])[:2]).lower() for x in m)
    return {
        "n": len(m),
        "mots": med("mots"),
        "mots_par_phrase_mediane": med("mots_par_phrase_mediane"),
        "part_phrases_courtes_<=8": med("part_phrases_courtes_<=8"),
        "part_phrases_longues_>=25": med("part_phrases_longues_>=25"),
        "hook_mots": med("hook_mots"),
        "va_infinitif_pour_100": med("va_infinitif_pour_100"),
        "tu_vous_pour_100": med("tu_vous_pour_100"),
        "je_pour_100": med("je_pour_100"),
        "questions_par_script": med("questions"),
        "liaisons_pour_100_moyenne": {k: round(v / len(m), 2) for k, v in liaisons.most_common(18)},
        "ouvertures_frequentes": ouvertures.most_common(12),
        "tics_ia_presents_dans_la_base": Counter(t for x in m for t in x["tics_ia"]).most_common(10),
    }


def main():
    corpus = json.load(open(os.path.join(ICI, "donnees", "corpus.json"), encoding="utf-8"))
    groupes = {
        "maxparra_long": [s for s in corpus if s["createur"] == "maxparra" and s["format"] == "long"],
        "topfoot_long": [s for s in corpus if s["createur"] == "topfoot" and s["format"] == "long"],
        "maxparra_court": [s for s in corpus if s["format"] == "court"],
    }
    res = {k: profil(v) for k, v in groupes.items()}
    with open(os.path.join(ICI, "donnees", "empreinte.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
