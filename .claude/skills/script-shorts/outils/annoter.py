"""Découpe chaque script du corpus temps par temps (hook, contexte, retournement, chute…) avec
Claude en mode headless, par lots, et range le résultat dans donnees/annotations.json.
Reprend là où il s'est arrêté (les scripts déjà annotés sont sautés).

Lancement : .venv/Scripts/python.exe -X utf8 .claude/skills/script-shorts/outils/annoter.py [nb_courts]
"""
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(ICI)))
sys.path.insert(0, os.path.join(RACINE, "studio"))
import serveur  # noqa: E402  (appel_claude : CLI Claude Code headless)

SORTIE = os.path.join(ICI, "donnees", "annotations.json")
LOT = 8
VERROU = threading.Lock()

ROLES = ["hook", "contexte", "mystere", "explication", "preuve_clip", "escalade", "retournement",
         "payoff", "chute", "cta", "opinion"]
SCHEMA = {"type": "object", "properties": {"annotations": {"type": "array", "items": {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "sport": {"type": "string"},
        "mots_cles": {"type": "array", "items": {"type": "string"},
                      "description": "joueurs, clubs, compétitions, thème (5-8)"},
        "hook_type": {"type": "string", "enum": ["quand_ce_mystere", "pourquoi_question", "tu_tes_deja_demande",
                                                 "detail_etrange_regarde", "opinion_forte", "citation_reponse",
                                                 "liste_techniques", "fait_chiffre", "autre"]},
        "hook_promesse": {"type": "string", "description": "ce que le hook promet sans le dire (1 phrase)"},
        "nom_cache_au_debut": {"type": "boolean",
                               "description": "le héros est d'abord désigné sans son nom (ce joueur, cette athlète…)"},
        "temps": {"type": "array", "items": {"type": "object", "properties": {
            "role": {"type": "string", "enum": ROLES},
            "debut": {"type": "string", "description": "les 3 à 6 premiers mots EXACTS du passage"},
            "fonction": {"type": "string", "description": "ce que fait ce passage, en 8-15 mots"}},
            "required": ["role", "debut", "fonction"]}},
        "chute_type": {"type": "string", "enum": ["fait_final", "morale_antithese", "coupe_net", "cta", "question", "autre"]},
        "procedes": {"type": "array", "items": {"type": "string"},
                     "description": "3-5 procédés d'écriture concrets observés (pas des généralités)"},
        "pourquoi_ca_marche": {"type": "string", "description": "1 phrase"},
    },
    "required": ["id", "sport", "mots_cles", "hook_type", "hook_promesse", "nom_cache_au_debut", "temps",
                 "chute_type", "procedes", "pourquoi_ca_marche"]}}},
    "required": ["annotations"]}


def prompt(lot):
    blocs = "\n\n".join(f"### id: {s['id']} | {s['vues']:,} vues | {s['duree']} s\n{s['texte']}" for s in lot)
    return f"""Tu es analyste de scripts de YouTube Shorts / TikTok sport en français. Voici {len(lot)}
transcriptions de vidéos qui ont très bien marché (transcription automatique : coquilles possibles, et des
passages peuvent être des extraits d'interview ou de commentaire plutôt que la voix off).

Pour CHAQUE script, découpe-le en temps successifs (rôle + 3-6 premiers mots exacts + fonction) et
relève ce qui le rend efficace. Sois concret et fidèle au texte : décris ce que l'auteur FAIT
(ex. « décrit le geste sans nommer le joueur », « annonce une explication avec 'pour une très bonne
raison' », « raconte au futur proche 'il va' »), pas des généralités (« crée du suspense »).

{blocs}"""


def charger():
    try:
        with open(SORTIE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main(nb_courts=60):
    corpus = json.load(open(os.path.join(ICI, "donnees", "corpus.json"), encoding="utf-8"))
    cibles = [s for s in corpus if s["format"] == "long"] + [s for s in corpus if s["format"] == "court"][:nb_courts]
    faits = charger()
    reste = [s for s in cibles if s["id"] not in faits]
    lots = [reste[i:i + LOT] for i in range(0, len(reste), LOT)]
    print(f"{len(faits)} déjà annotés, {len(reste)} à faire en {len(lots)} lots", flush=True)

    def un(lot):
        try:
            d = serveur.appel_claude(prompt(lot), schema=SCHEMA, outils="Read", timeout=900, modele="sonnet")
        except Exception as e:  # noqa: BLE001
            print("lot raté :", str(e)[-200:], flush=True)
            return
        ids = {s["id"] for s in lot}
        with VERROU:
            tout = charger()
            for a in d.get("annotations", []):
                if a.get("id") in ids:
                    tout[a["id"]] = a
            with open(SORTIE, "w", encoding="utf-8") as f:
                json.dump(tout, f, ensure_ascii=False, indent=0)
            print(f"{len(tout)} annotés", flush=True)
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(un, lots))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
