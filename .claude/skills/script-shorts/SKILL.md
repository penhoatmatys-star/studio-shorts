---
name: script-shorts
description: Écrire ou retoucher un script de voix off de YouTube Short / TikTok sport en français (1 min ou 25-30 s) qui sonne humain, en imitant les vrais scripts qui marchent (Max Parra, TopFoot, scripts validés par Matys). À utiliser pour TOUT script du projet short automatisation : veille du jour, scripts du studio, chat de retouche, « mon script ».
---

# Script de Short qui sonne humain

On n'écrit pas à partir de règles : on écrit **en imitant de vrais scripts qui ont marché**, gardés
sous les yeux. La base : 196 scripts d'1 min et 150 scripts de 20-38 s (`donnees/corpus.json`), leur
découpage temps par temps (`donnees/annotations.json`) et la voix mesurée (`donnees/empreinte.json`,
synthèse lisible dans `donnees/structures.md`).

Les outils se lancent depuis la racine du projet avec l'interpréteur Python disponible
(`.venv/Scripts/python.exe` sur le PC de Matys, `python3` ailleurs). `S=.claude/skills/script-shorts/outils`.

## 1. Lire la référence (une fois par session)

- `scripts_modeles.md` : les scripts validés « parfaits » par Matys. Ils passent avant tout le reste.
- `.claude/skills/script-shorts/donnees/structures.md` : comment ces créateurs construisent vraiment
  leurs scripts (hooks qui font le plus de vues, enchaînements de temps, mots d'attaque de chaque temps).

## 2. Sortir les 3 scripts les plus proches et les lire EN ENTIER

```bash
python $S/exemples.py "<joueurs, club, compétition, ce qui s'est passé>" --format long|court --style maxparra|topfoot|mix -n 3
```

- `--style maxparra` : histoire d'un moment, d'un geste, d'une règle méconnue, d'un détail étrange.
- `--style mix` : actu chaude, polémique, déclaration (TopFoot apporte la mécanique « preuves enchaînées »).
- Lis chaque texte à voix haute dans ta tête : longueur des phrases, mots de liaison, moment où le
  nom tombe, façon d'amener un clip, dernière phrase.

## 3. Copier la STRUCTURE du meilleur exemple, pas un squelette générique

Écris d'abord le plan : reprends la suite de temps de l'exemple le plus proche (ex. hook mystère →
contexte → explication de la règle → retournement « Sauf que » → payoff → fait final) et, pour
chaque temps, la fonction qu'il aura dans TON sujet. Si ton sujet a des citations filmées, chaque
clip parlé remplace un temps « preuve » (modèle Dembélé de `scripts_modeles.md`).

## 4. Écrire d'un jet, dans la VOIX de la base

La voix est celle de Max Parra, que le script modèle de Matys suit aussi (mesures du 2026-10-28) :

- **Phrases longues qui s'enchaînent** : ~25 mots en médiane, moitié des phrases à 25 mots ou plus,
  presque jamais de phrase de 8 mots ou moins. On relie avec « parce que », « vu que », « alors »,
  « sauf que », « et pour cause », « ce qui fait que », « mais ».
- **Hook = une seule longue phrase** (~27 mots en 1 min, ~22 en court) qui montre une scène ou une
  phrase forte et promet une explication sans la donner (« …personne ne se doutait qu'il avait fait
  ça pour une très bonne raison »). Le héros est souvent d'abord décrit (« ce joueur de 18 ans »,
  « cette athlète ») et nommé plus tard.
- **On raconte, on ne s'adresse pas au spectateur** : pas de « tu / vous », pas de question
  rhétorique, pas d'« imaginez ». Narration au passé ou au futur proche (« il va s'approcher »).
- **Ton plat, faits concrets** : pas d'adjectif qui commente l'émotion (incroyable, fou,
  historique, légendaire, choc), pas de « véritable », « littéralement », « et là », « le verdict ».
- **Chute = un fait** (le résultat, le chiffre final, la date qui tranche) ; antithèse sèche
  possible façon modèle Dembélé. Pas de morale expliquée, pas d'appel à s'abonner.
- **Pas trop propre** (test à l'aveugle du 2026-10-28 : un juge a repéré les anciens scripts à 85 %
  pour ces raisons) : un humain qui raconte se répète un peu, relance avec « Et le pire »,
  « Mais ce que personne ne savait », « Et c'est justement ici que ça devient intéressant »,
  réutilise « bizarrement » deux fois, ajoute un détail concret un peu en trop. Les transitions ne
  sont pas toutes parfaitement logiques. Pas de gabarit appliqué à la lettre : le hook « Cette
  réponse de X est la raison pour laquelle… » est UN hook possible, pas celui de chaque script.
  Pas d'antithèse de fin calculée qui reboucle sur le hook à chaque fois : souvent la vidéo
  s'arrête sur le dernier fait, sans conclusion.
- Longueur : **260-275 mots** (1 min) ou **110-130 mots** (25-30 s), hors lignes `[CLIP Nom] citation`.
- Interdits de Matys : tiret cadratin, « ce n'est pas X, c'est Y », « du coup », emoji.

## 5. Vérifier contre la base et corriger

```bash
python $S/verif.py <fichier ou -> --format long|court
```

Corrige chaque « À CORRIGER », relance jusqu'à « OK ». Les « À VÉRIFIER » se jugent au cas par cas.

## 6. Relecture finale à voix haute

- Chaque phrase se dit d'un souffle naturel, comme un pote qui raconte (couper seulement si on
  manque d'air, jamais pour « faire punchy »).
- Le nom du héros tombe au bon moment, le premier fait concret arrive avant la 3e phrase.
- Rien d'inventé : un fait non confirmé est au conditionnel ou retiré ; les citations [CLIP] sont
  exactes et sourcées (traduction française si étrangère).
- Compare une dernière fois ton hook aux 3 hooks des exemples : s'il sonne plus « écrit », réécris-le.

## Mettre la base à jour

`outils/corpus.py` (reconstruit le corpus depuis `shorts/_recherche_*`), `outils/empreinte.py`
(remesure la voix), `outils/annoter.py` (découpe les nouveaux scripts), `outils/synthese.py`
(regénère `structures.md`). Ajoute chaque script validé par Matys à `scripts_modeles.md`.
