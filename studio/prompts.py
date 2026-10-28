"""Prompts et schémas JSON envoyés à Claude Code par le studio."""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_VIDEO = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "titre": {"type": "string", "description": "ce qu'on voit / ce qui est dit"},
        "format": {"type": "string", "enum": ["9:16", "16:9", "?"]},
        "parle": {"type": "boolean", "description": "clip parlé utilisable comme preuve"},
        "usage": {"type": "string", "description": "hook, preuve, action, émotion, payoff…"},
        "alerte": {"type": "string", "description": "bandeau, watermark, à vérifier… (vide si rien)"},
    },
    "required": ["url", "titre", "format"],
}

SCHEMA_VEILLE = {
    "type": "object",
    "properties": {
        "titre": {"type": "string", "description": "« Veille sport — jeudi 8 octobre 2026 matin »"},
        "date": {"type": "string", "description": "AAAA-MM-JJ"},
        "moment": {"type": "string"},
        "tldr": {"type": "string"},
        "sujets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "slug court, ex. maupay_dezerbi"},
                    "titre": {"type": "string"},
                    "note": {"type": "number", "description": "/10"},
                    "verdict": {"type": "string", "enum": ["go", "surveiller", "non"]},
                    "suite": {"type": "boolean", "description": "rebondissement d'un sujet déjà proposé"},
                    "sport": {"type": "string"},
                    "format": {"type": "string", "enum": ["long", "court"],
                               "description": "long = short d'1 min, court = short de 25-30 s"},
                    "resume": {"type": "string", "description": "2 phrases max"},
                    "faits": {"type": "array", "items": {"type": "string"}},
                    "pourquoi": {"type": "string"},
                    "angle": {"type": "string"},
                    "videos": {"type": "array", "items": _VIDEO},
                    "a_trouver": {"type": "array", "items": {"type": "string"},
                                  "description": "images encore à chercher"},
                    "photos": {"type": "array", "items": {"type": "string"},
                               "description": "idées de photos d'incrustation"},
                    "citations": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"auteur": {"type": "string"}, "texte": {"type": "string"},
                                       "source": {"type": "string"}, "video": {"type": "string"}},
                        "required": ["auteur", "texte"]}},
                    "sources": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"titre": {"type": "string"}, "url": {"type": "string"}},
                        "required": ["titre", "url"]}},
                    "fiabilite": {"type": "string", "enum": ["confirme", "partiel", "rumeur"]},
                    "fiabilite_detail": {"type": "string"},
                    "echeance": {"type": "string", "description": "prochaine date clé (match, verdict…)"},
                    "hooks": {"type": "array", "items": {"type": "string"}},
                    "structure": {"type": "array", "items": {"type": "string"}},
                    "scores": {"type": "object", "properties": {
                        "viral": {"type": "number"}, "faits": {"type": "number"},
                        "images": {"type": "number"}}},
                },
                "required": ["id", "titre", "note", "verdict", "resume", "faits", "videos", "sources",
                             "fiabilite"],
            },
        },
        "ecartes": {"type": "array", "items": {
            "type": "object",
            "properties": {"titre": {"type": "string"}, "raison": {"type": "string"}},
            "required": ["titre", "raison"]}},
    },
    "required": ["titre", "date", "tldr", "sujets"],
}

SCHEMA_SUJET = SCHEMA_VEILLE["properties"]["sujets"]["items"]

SCHEMA_SCRIPTS = {
    "type": "object",
    "properties": {
        "scripts": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "titre": {"type": "string", "description": "nom court du script / de l'angle"},
                    "mecanisme": {"type": "string",
                                  "description": "hook et structure Max Parra utilisés"},
                    "texte": {"type": "string",
                              "description": "script complet, paragraphes séparés par une ligne vide, "
                                             "clips parlés en ligne à part : [CLIP Nom] citation exacte"},
                    "clips": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"moment": {"type": "string"}, "description": {"type": "string"},
                                       "url": {"type": "string"}},
                        "required": ["description"]}},
                    "forces": {"type": "string"},
                    "risques": {"type": "string", "description": "faits à vérifier, clip introuvable…"},
                },
                "required": ["titre", "mecanisme", "texte"],
            },
        }
    },
    "required": ["scripts"],
}

SCHEMA_CHAT = {
    "type": "object",
    "properties": {
        "reponse": {"type": "string", "description": "réponse courte à Matys (2-4 phrases)"},
        "texte": {"type": ["string", "null"],
                  "description": "le script COMPLET modifié, ou null si aucune modification"},
    },
    "required": ["reponse", "texte"],
}

SCHEMA_PROD_CHAT = {
    "type": "object",
    "properties": {
        "reponse": {"type": "string", "description": "réponse à Matys, courte et concrète"},
        "consigne": {"type": ["string", "null"],
                     "description": "si Matys demande un changement : la consigne claire et autonome "
                                    "à transmettre à l'agent de montage ; sinon null"},
    },
    "required": ["reponse", "consigne"],
}

FORMATS = {   # Matys 2026-10-28 : chaque jour 4 shorts d'1 min + 5 shorts de 25-30 s
    "long": {"libelle": "1 minute", "mots": "260-275", "clips": "1 à 3",
             "montage": "short d'1 min : 25-43 plans (2-2,8 s/plan), musique skyfall par défaut"},
    "court": {"libelle": "25 à 30 secondes", "mots": "110-130", "clips": "0 ou 1 (court)",
              "montage": "short de 25-30 s : 11-16 plans (1,2-1,8 s/plan), musique tiki par défaut"},
}


def fmt(sujet):
    return FORMATS.get((sujet or {}).get("format"), FORMATS["long"])


SKILL = ".claude/skills/script-shorts"
PY = os.path.relpath(sys.executable, RACINE).replace("\\", "/") if sys.executable.startswith(RACINE) else "python3"
# outils du skill script-shorts (exemples.py, verif.py) : seules commandes shell autorisées pour écrire
OUTILS_SCRIPT = f"Read,Glob,Grep,WebSearch,WebFetch,Write,Bash({PY}:*)"


def regles_script(sujet=None):
    f = fmt(sujet)
    k = "court" if f is FORMATS["court"] else "long"
    return f"""Méthode d'écriture OBLIGATOIRE : lis et suis À LA LETTRE `{SKILL}/SKILL.md` (skill
script-shorts). En résumé : (1) lis `scripts_modeles.md` et `{SKILL}/donnees/structures.md` ;
(2) `{PY} {SKILL}/outils/exemples.py "<joueurs, club, ce qui s'est passé>" --format {k} --style <maxparra|mix> -n 3`
et lis les 3 vrais scripts en entier ; (3) copie la suite de temps du plus proche ; (4) écris dans la
voix de la base : phrases longues qui s'enchaînent (~25 mots), hook d'une seule longue phrase, pas de
« tu / vous », pas de question, pas de fragment punchy, ton plat, chute = un fait ; (5) écris le
script dans `studio/_jobs/brouillon_<id du sujet>.txt` puis
`{PY} {SKILL}/outils/verif.py studio/_jobs/brouillon_<id du sujet>.txt --format {k}` et corrige jusqu'à « OK ».
- Cible : {f['libelle']} dite par le clone (≈ 4,5 mots/s) → {f['mots']} mots de VO, HORS clips.
- Clips parlés : ligne à part `[CLIP Nom] citation exacte` (vraie citation sourcée, jamais
  inventée ; en langue étrangère → traduction française). {f['clips']} clip(s).
- Aucune invention : un fait non confirmé est dit au conditionnel ou retiré.
- Prononciation : écrire les nombres et sigles comme on les dit si c'est ambigu."""


def prompt_veille(nom, consigne="", quotidien=False):
    if quotidien:
        composition = """COMPOSITION IMPOSÉE (veille du jour, demande de Matys) : exactement 9 sujets GO.
  - 4 sujets `format: "long"` (short d'1 minute) : principalement du TENNIS (3 sujets tennis)
    et AU MOINS 1 sujet FOOT.
  - 5 sujets `format: "court"` (short de 25-30 s) : des histoires qui tiennent en un seul fil
    (une phrase choc, un geste, un chiffre, un retournement), tennis en priorité, foot possible.
  Les plus solides et les plus riches en images vont en « long ». Ce qui ne tient pas va dans
  `ecartes` avec la raison."""
    else:
        composition = """Retiens 3 à 5 sujets (GO ou à surveiller), chacun avec `format` "long" (1 min)
  ou "court" (25-30 s) selon ce que l'histoire peut porter."""
    return f"""Tu fais la veille actu sport pour la chaîne de Shorts de Matys (projet tiktokt, dossier courant).
Lis d'abord CLAUDE.md (§4 écriture, §6 recherche de clips) et `GUIDE_SCRIPTS_FUSION.md`.

1. Évite les redites : lis les 3 derniers rapports `shorts/_veille/*.json` ; un sujet déjà traité
   ne revient que s'il y a un vrai rebondissement (`suite: true`).
2. Balaie l'actu des dernières 24-48 h (WebSearch en français ET en anglais, 15-30 recherches) :
   tennis (ATP, WTA, Français, embrouilles, déclarations, records, blessures, coachs, sponsors)
   et foot (Ligue 1, PSG, OM, Real, Barça, Mbappé, Yamal, Bleus, mercato confirmé, clashs,
   conférences de presse). Cherche ce qui fait réagir un ado / jeune adulte français : conflit,
   phrase choc, injustice, retournement, chiffre fou, échéance proche.
3. {composition}
4. Pour chaque sujet retenu : faits recoupés sur 2 sources fiables (sinon `rumeur`), citations
   EXACTES (qui, où, quand) utilisables en clips parlés, 2-3 recherches YouTube (priorité aux
   /shorts/ 9:16 sans sous-titres ni bandeau ; extraits de match, conférences, interviews) avec
   pour chaque URL : format, parlé ou non, usage, alerte. `hooks` (2-3, façon Max Parra) et
   `structure` (4-6 temps pour un long, 3 pour un court), `scores` (viral, faits, images /10),
   note /10 honnête, `echeance`, `photos` (idées d'incrustation), `a_trouver`.
5. Écris `shorts/_veille/{nom}.json` conforme au schéma `studio/schema_veille.json` (lis-le),
   puis `shorts/_veille/{nom}.md`, la version lisible du même rapport (TL;DR puis un bloc par
   sujet). `titre` du rapport : « Veille sport, <jour> <date> ». Ne télécharge rien.
{('Consigne particulière de Matys : ' + consigne) if consigne else ''}
Termine en répondant juste : « Veille écrite : {nom} »."""


def prompt_recherche(texte):
    return f"""Matys veut faire un Short TikTok/YouTube d'1 minute (voix off, storytelling Max Parra)
sur ce sujet qu'il a tapé dans la barre de recherche du studio :

« {texte} »

Tu es dans le projet tiktokt (dossier courant ; CLAUDE.md pour le format). Documente ce sujet
exactement comme un sujet de veille, pour qu'il puisse ensuite le valider et lancer les scripts :
1. Recherches web (WebSearch, en français ET en anglais, 6-12 recherches) : les faits, la
   chronologie, le contexte et les précédents, les chiffres, les citations EXACTES (qui, où,
   quand), l'actualité la plus récente et la prochaine échéance (match, verdict, date).
   Recoupe sur au moins 2 sources fiables ; ce qui n'est pas confirmé est marqué rumeur.
2. Vidéos (3-5 recherches YouTube) : priorité aux /shorts/ 9:16 sans sous-titres ni bandeau,
   extraits de match, conférences de presse, interviews (clips parlés = preuves). Pour chaque URL :
   format, parlé ou non, usage dans le short, alerte éventuelle. Note dans `a_trouver` ce qui manque.
3. Angle : ce qui accroche un ado/jeune adulte français, 2-3 hooks façon Max Parra (modèle
   `scripts_modeles.md`, analyse `shorts/_recherche_maxparra/analyse_storytelling.md`) et une
   structure en 4-6 temps.
4. Note /10 honnête (potentiel viral × solidité des faits × images disponibles), `scores`,
   verdict go/surveiller/non. Si le sujet est faible, dis-le dans `pourquoi` plutôt que de gonfler.
`id` = slug court du sujet. Écris en français, ton naturel. Ne télécharge rien."""


def prompt_conversion(chemin_md):
    return f"""Lis le rapport de veille `{chemin_md}` et convertis-le, sans rien inventer ni rien
perdre d'utile, au format JSON demandé (schéma fourni). Une entrée `videos` par URL YouTube citée
(format déduit : /shorts/ = 9:16), les citations exactes dans `citations`, les sujets écartés dans
`ecartes`. Les hooks / structure proposés vont dans le sujet concerné. `id` = slug court."""


def prompt_scripts(veille, sujet, consigne, nombre):
    s = {k: v for k, v in sujet.items()}
    return f"""Tu écris des scripts de voix off pour un YouTube Short / TikTok de {fmt(sujet)['libelle']}
de Matys (projet tiktokt, dossier courant). Sujet de la veille {veille.get('id')} :

```json
{json.dumps(s, ensure_ascii=False, indent=1)}
```

{regles_script(sujet)}

Avant d'écrire, vérifie avec WebSearch les points marqués « à vérifier » / rumeur du sujet et
les faits datés (qui entraîne qui aujourd'hui, scores, dates) — 2 à 5 recherches max.

Écris {nombre} scripts COMPLETS et vraiment différents (hook, angle ou structure différents :
par ex. un « citation → conséquence », un « Si tu… » ou antithèse sèche, un duel), chacun
de qualité « modèle ». Pour chaque script : `mecanisme` (hook + structure utilisés, en une
phrase), `clips` (les clips parlés et plans clés, avec l'URL candidate si connue), `forces`,
`risques`.
{('Consigne de Matys : ' + consigne) if consigne else ''}"""


def prompt_chat(sujet, script, message):
    historique = "\n".join(("Matys : " if m["role"] == "moi" else "Toi : ") + m["x"]
                           for m in script.get("chat", [])[-10:-1])
    return f"""Tu es l'assistant d'écriture de Matys dans son studio de Shorts (projet tiktokt).
Sujet : {sujet.get('titre')} — {sujet.get('resume', '')}

Script actuel ({script.get('titre')}) :
---
{script['texte']}
---

{regles_script(sujet)}

Échanges précédents :
{historique or '(aucun)'}

Nouvelle demande de Matys : {message}

Si la demande implique de modifier le script, renvoie dans `texte` le script COMPLET modifié
(même format, garde ~{fmt(sujet)['mots']} mots hors clips sauf demande contraire) et explique en 1-2 phrases
ce que tu as changé dans `reponse`. Si c'est une question, réponds dans `reponse` et mets
`texte` à null. Tu peux vérifier un fait avec WebSearch si besoin."""


def prompt_production(projet, options):
    o = options or {}
    lignes = []
    if o.get("zoom"):
        lignes.append(f"- Zoom des clips 16:9 : {o['zoom']} au lieu du standard 1.8 (choisi par Matys).")
    if o.get("musique"):
        lignes.append(f"- Musique : {o['musique']}.")
    if o.get("notes"):
        lignes.append(f"- Notes de Matys : {o['notes']}")
    f = FORMATS.get(o.get("format"), FORMATS["long"])
    lignes.insert(0, f"- Format : {f['libelle']} → {f['montage']} (CLAUDE.md §3).")
    opts = "\n".join(lignes)
    return f"""Tu produis de bout en bout le short `shorts/{projet}/` du projet tiktokt (dossier courant),
en mode autonome : Matys a cliqué « Lancer la production » dans le studio et n'est pas là pour
répondre aux questions. Ne pose aucune question, prends les décisions raisonnables et note-les.

Entrées :
- `shorts/{projet}/script_studio.md` : le script final validé par Matys (clips parlés en
  lignes `[CLIP Nom] citation`).
- `shorts/{projet}/brief.json` : le sujet de la veille (faits, vidéos candidates, citations,
  sources, idées de photos) et les options. Si `sujet.script_perso` est vrai, Matys a écrit le
  script lui-même sans passer par la veille : le brief est presque vide (seulement son
  `contexte` éventuel). Déduis alors le sujet du script, vérifie les faits par WebSearch et
  trouve toi-même les clips, citations et photos. Ne réécris pas son script : s'il manque un
  [CLIP] ou si un fait est faux, note-le dans `_production.md` (VO = son texte, mot pour mot).

Options :
{opts}

Procédure — suis CLAUDE.md (lis-le en entier d'abord), STYLE_MONTAGE.md :
1. `texte.txt` = le texte de VO (sans les lignes [CLIP]). S'il y a des clips parlés : VO
   générée en parties + blancs de la durée de chaque clip (cf. `shorts/dembele_enrique/_vo/`).
2. Voix off avec le clone : `.venv/Scripts/python.exe generer_voix.py {projet}` (ou par parties).
3. Transcription mot à mot (`_bin/transcrire.py`), puis mise à jour de `texte.txt`.
4. Recherche des clips (WebSearch youtube.com, priorité aux /shorts/ 9:16 purs, en partant des
   vidéos du brief), téléchargement avec `.venv312/Scripts/python.exe telecharger.py`, planches-contact
   (`_bin/planche.py`) et vérification visuelle de CHAQUE clip (Read des planches) — règle d'or §1.
   1er plan = clip vertical natif du sujet seul. Familles visuelles, pas de doublon voisin.
5. 3 à 6 photos d'incrustation (§9) — pas de navigateur ici : passe par l'API Wikimedia
   Commons ou des URLs d'images directes trouvées par WebSearch/WebFetch ; regarde chaque image.
6. `edl.json` calé sur les timestamps réels (beats, clips parlés avec {{"son": 1.0}},
   traductions à l'écran si clip étranger, images), puis les SOUS-TITRES :
   `.venv/Scripts/python.exe _bin/sous_titres.py shorts/{projet}` (une seule ligne à la fois, jamais 2 —
   demande de Matys ; `monter_edl.py` les génère aussi s'ils manquent). Volumes : musique et woosh
   de transition sont déjà baissés par défaut (Matys) — ne pas les remonter ; réglables par
   `"vol_musique"` (défaut 0.7) et `"vol_transitions"` (défaut 0.5) dans l'edl.
   Son des photos : « ding » sur 2 photos sur 3 (demande Matys : ça attire plus l'oreille),
   1006 sur la 3e — automatique (`"son_photo"`: "mix" par défaut, "ding" ou "1006").
   Voix off à +18,5 dB et ding d'intro baissé : automatiques, ne pas y toucher.
   FLÈCHE D'INTRO (CLAUDE.md §8) : elle sert à DÉSIGNER le joueur (ou l'élément) du 1er plan.
   Lance `.venv/Scripts/python.exe _bin/fleche.py shorts/{projet}`, regarde `_frames/fleche.png`
   (Read), repère le joueur, puis essaie `_bin/fleche.py shorts/{projet} <x> <y>` jusqu'à ce que
   le viseur soit sur lui (tête / buste), HORS des zones rouges (barre de recherche en haut,
   légende et commentaires en bas, boutons à droite sur TikTok et YouTube Shorts). Écris alors
   `"fleche_xy": [x, y]` dans l'edl. Ne mets PAS de clé `"fleche"` : `monter_edl.py` décide seul
   (flèche sur 3 vidéos sur 4).
7. Rendu de contrôle `_bin/rendu.py {projet}` → `apercu.mp4`, regarde quelques frames.
8. Montage CapCut (OBLIGATOIRE, ne jamais sauter cette étape) : UNIQUEMENT via
   `.venv/Scripts/python.exe _bin/monter_capcut.py shorts/{projet}` — il ferme CapCut, monte, rouvre
   CapCut et vérifie que le brouillon tient. D'autres montages peuvent tourner en même temps :
   ce script attend son tour s'il le faut (n'appelle jamais monter_edl.py ni fermer_capcut.bat
   directement, et ne tue jamais CapCut toi-même).
9. Écris `shorts/{projet}/_production.md` : ce qui a été fait, clips retenus (URL + usage),
   décisions prises, points à vérifier, et la checklist de finition de STYLE_MONTAGE.md
   (sauf « légendes auto » : les sous-titres sont déjà posés).

Consignes en direct : Matys peut t'écrire depuis le studio pendant que tu travailles. Ses
consignes arrivent dans `shorts/{projet}/_consignes.md` (une ligne horodatée par consigne).
Relis ce fichier au début et entre CHAQUE étape ; applique toute nouvelle consigne (même si
ça oblige à refaire une étape), et note dans `_production.md` comment tu l'as appliquée.

Termine par un résumé de 5-8 lignes (même contenu que la fin de _production.md)."""


def prompt_prod_observateur(projet, sujet, journal, chat, message):
    historique = "\n".join(("Matys : " if m["role"] == "moi" else "Toi : ") + m["x"]
                           for m in chat[-9:-1])
    return f"""Tu es l'assistant du studio de Matys. Un AUTRE agent Claude est en train de produire
le short `shorts/{projet}/` (VO, clips, photos, EDL, CapCut) et tu ne dois RIEN modifier :
tu observes et tu réponds. Sujet : {sujet.get('titre')}.

Ce que l'agent de montage a fait jusqu'ici (dernières étapes de son journal) :
---
{journal or '(il vient de démarrer)'}
---
Tu peux lire les fichiers du projet pour répondre précisément : `shorts/{projet}/` (texte.txt,
edl.json, _mots.json, _frames/, _src/, images/, _consignes.md, script_studio.md, brief.json).

Échanges précédents :
{historique or '(aucun)'}

Message de Matys : {message}

- Si c'est une question (avancement, clips choisis, durée, pourquoi tel choix…) : réponds
  concrètement en 1-4 phrases, `consigne` = null.
- Si Matys demande un changement (autre clip, autre musique, couper une phrase, photo en plus…) :
  écris dans `consigne` une instruction claire et autonome pour l'agent de montage (il la lira
  entre deux étapes), et confirme dans `reponse` que c'est transmis et quand ça sera pris en
  compte. Si le changement touche la voix off déjà générée, préviens que ça recoûte des crédits."""


def prompt_prod_modif(projet, demande, meme_session):
    contexte = ("Tu reprends ta propre session : tu as produit ce short juste avant." if meme_session
                else f"Lis d'abord `shorts/{projet}/_production.md`, `edl.json` et CLAUDE.md : "
                     "c'est un short déjà produit.")
    return f"""Matys a regardé le short `shorts/{projet}/` et t'écrit depuis le studio :

« {demande} »

{contexte}
- Si c'est une question, réponds simplement, sans rien modifier.
- Si c'est une modification : applique-la en suivant CLAUDE.md (ne régénère la voix off que si
  c'est indispensable, ça coûte des crédits ElevenLabs), refais le rendu `_bin/rendu.py {projet}`,
  puis remonte le brouillon CapCut si l'EDL a changé ou s'il n'existe pas encore, UNIQUEMENT via
  `.venv/Scripts/python.exe _bin/monter_capcut.py shorts/{projet}` (il gère CapCut et attend son tour si
  un autre montage tourne). Mets à jour `_production.md`.
Ne pose aucune question. Termine par 2-5 lignes pour Matys : ce que tu as fait (ou ta réponse)."""


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_veille.json"), "w") as f:
        json.dump(SCHEMA_VEILLE, f, ensure_ascii=False, indent=1)
    print("schema_veille.json écrit")
