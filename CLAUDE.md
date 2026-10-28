# CLAUDE.md — Projet « short automatisation » (Shorts style Max Parra / Niche Trap)

Manuel d'opération pour le robot. Ces règles sont **prioritaires** et s'appliquent à
chaque vidéo. Objectif : produire des YouTube Shorts viraux, voix off humaine, montage
rapide façon Max Parra, ouverts directement dans CapCut.

Utilisateur : le créateur de contenu qui utilise ce studio (travaille en français). Le style décrit ci-dessous est celui de Matys Penhoat, le créateur d'origine.
Mémoire longue durée du projet : voir `…/.claude/projects/…/memory/` (`MEMORY.md`).

---

## 1. Sélection & format des clips (RÈGLE D'OR)

1. **Toujours privilégier le 9:16** (sources TikTok / Reels / YouTube Shorts).
   Le 16:9 n'est qu'un **dernier recours** quand aucun 9:16 propre n'existe.
2. **Un clip 9:16 doit être PUR** : aucun sous-titre, aucun texte incrusté, aucun
   filigrane/watermark, aucun bouton « subscribe », aucun bandeau d'un autre créateur.
   → Vérifier CHAQUE clip téléchargé en extrayant des frames (planche-contact ffmpeg)
   AVANT de le couper. Écarter tout clip non pur, ou recadrer pour retirer le bandeau
   si c'est en bord d'image uniquement.
3. **Les edits verticaux 9:16 de Mbappé/joueurs sont autorisés et recherchés** s'ils
   sont pertinents, propres et de bonne qualité. Un léger branding propre à un edit est
   toléré ; les gros bandeaux de sous-titres narratifs et les CTA parasites sont interdits.
4. **Qualité maximale toujours** : 1080×1920 > 720p. Préférer la meilleure source dispo.

## 2. Composition / flou (le flou se fait DANS CAPCUT, pas en ffmpeg)

- **Clip 9:16** → plein cadre (cover, remplit 1080×1920). **JAMAIS de flou** :
  il remplit déjà l'écran.
- **Clip 16:9** → méthode « deux couches » faite **par CapCut** (et non pré-incrustée
  par ffmpeg, pour préserver la netteté du clip de devant) :
  - couche du dessus = le clip 16:9 **agrandi à ~181 % (`zoom` 1.8, défaut du script)** —
    règle fixée par Matys le 2026-10-08 avec une vidéo d'exemple (CapCut, Échelle 100 % → 181 %) :
    le plan doit être nettement plus visible qu'à x1, **sans le zoomer pour remplir l'écran** :
    il reste une bande de fond flou en haut et en bas, et on ne coupe qu'une partie raisonnable
    des côtés. Donc : jamais x1 (plan minuscule), jamais de recadrage plein écran / cover sur un
    16:9, pas d'animation de zoom, et pas de valeurs au cas par cas (x1,6, x2…) : 1.8 partout.
    Seule exception : descendre un plan à ~1.5 (`{"zoom": 1.5}`) si un élément essentiel (visage,
    ballon, joueur nommé) serait coupé sur le bord ;
  - couche du dessous = le même clip étiré plein écran + **flou** ;
  - techniquement : `seg.add_background_filling("blur", blur=BLUR)` (= `canvas_blur`
    natif CapCut). Le clip source reste en **format natif 16:9** (NE PAS pré-flouter
    ni pré-recadrer en 1080×1920 avec ffmpeg).
- `monter_edl.py` applique ceci **automatiquement** selon le ratio du clip :
  vertical (h/l ≥ 1.5) → cover, sans flou ; sinon → fit + `canvas_blur`.

## 3. Transitions & enchaînement (clean, net, rapide)

- Style = **coupes franches rapides**, « clean, net et rapide ». Rythme mesuré chez Matys :
  short 15-30 s → 11-16 plans (1,2-1,8 s/plan) ; **short d'1 min → 25-43 plans
  (2-2,8 s/plan)**. Pas d'animation d'entrée (`anim` = 0). Transitions rares et
  choisies dans SES transitions CapCut (voir §10), ~1 coupe sur 4, jamais la même deux
  fois de suite.
- **Jamais deux clips qui se répètent à la suite** (même image / même plan quasi
  identique enchaîné) : ça crée un effet de bug. Varier les sources entre plans voisins.
  `monter_edl.py` **refuse** deux beats adjacents de même source à plages qui se
  chevauchent (garde-fou anti-doublon).
- **Raisonner en FAMILLE VISUELLE, pas en fichier source.** Deux sources différentes
  peuvent donner des plans quasi identiques — typiquement deux conférences de presse du
  même homme sur le même fond sponsors. Le garde-fou du script ne les voit pas passer.
  Donc : étiqueter chaque source par famille (`presse`, `entrainement`, `vestiaire`,
  `tribunes`…), **jamais deux plans voisins de la même famille**, et **plafonner une
  famille à ~20 % des plans**. Sinon le montage se lit comme une boucle même sans
  doublon strict.
- À la jonction de deux clips, **pas de saut/tremblement d'écran** : éviter qu'un plan
  démarre sur un mouvement de caméra brutal juste après la coupe. Choisir des points
  d'entrée stables.
- **Les 2 premiers clips sont les plus importants** : les plus représentatifs du sujet
  et les plus accrocheurs (hook visuel fort). **Le tout premier plan doit être un clip
  VERTICAL natif (portrait, plein écran, sans fond flou)** avec le sujet seul à l'image
  (exigence Matys 2026-10-07 ; il dit « 16:9 » pour parler du format portrait : un paysage
  avec fond flou ne compte PAS). Jamais un plan générique en ouverture.

## 4. Écriture des scripts (voix off)

- Cible : **1 minute** par défaut, **dit à l'oral** → calibrer sur le débit du clone
  (≈ 4,5 mots/s ⇒ **~260-275 mots**). Exemples de scripts 1 min actu sport : `scripts_2026-10-05.md`.
- **Deux formats depuis le 2026-10-28** (champ `format` du sujet) : `long` = 1 min (260-275 mots,
  25-43 plans) et `court` = **25-30 s** (110-130 mots, un seul fil, 11-16 plans, musique tiki).
- **Veille du jour** (chaque matin, Matys 2026-10-28) : 9 sujets, **4 shorts d'1 min** (3 tennis +
  au moins 1 foot) et **5 shorts de 25-30 s**, avec un script écrit d'office pour chacun.
- **SKILL `script-shorts` OBLIGATOIRE pour tout script** (`.claude/skills/script-shorts/SKILL.md`,
  2026-10-28) : on écrit en imitant les 3 vrais scripts les plus proches (`outils/exemples.py`), dans
  la voix mesurée de la base (phrases ~25 mots qui s'enchaînent, hook d'une longue phrase, pas de
  « tu », pas de fragments), puis `outils/verif.py` jusqu'à « OK ». Il prime sur les règles ci-dessous
  quand elles divergent.
- **MODÈLE DE RÉFÉRENCE : `scripts_modeles.md`** (Dembélé / Mbappé / Enrique, jugé
  « parfait »). Le relire avant chaque script et en reproduire les mécanismes : hook
  « cette réponse de X est la raison pour laquelle… » + clip immédiat, clips parlés comme
  preuves, duel arbitré par un tiers, retournement « Sauf que… », chute en antithèse +
  échéance datée. Y ajouter chaque nouveau script validé comme parfait.
- **GUIDE DE FUSION : `GUIDE_SCRIPTS_FUSION.md`** (Max Parra + @topfoot_youss, bases triées par vues
  dans `shorts/_recherche_maxparra/` et `shorts/_recherche_topfoot/`). Le lire avant chaque script :
  catalogue de hooks, mécaniques de suspense, squelette d'1 min, procédure d'humanisation.
- **On part du principe qu'un HUMAIN écoute** la vidéo : ton naturel, rythme parlé,
  pas de phrases robotiques.
- **Storytelling façon Max Parra** (chaîne de réf : https://www.youtube.com/@maxparra9).
  Base d'analyse de ses hooks & structures : `shorts/_recherche_maxparra/`
  (`index.json` = méta triées par vues, `transcripts/` = scripts, plus la synthèse
  `analyse_storytelling.md`). À chaque nouveau script, **choisir la structure / le hook
  le plus adapté et le plus viral** parmi ces patterns.

## 5. Transcription de la voix off (OBLIGATOIRE avant de monter)

- La voix vient soit de Matys (`voix.mp3` déposé), soit du **clone ElevenLabs**
  (`generer_voix.py`, voir §7). Dans les deux cas :
- **Dès que le `voix.mp3` existe, le transcrire MOT POUR MOT avec timestamps**
  via `faster_whisper` (modèle `small`, `language='fr'`, `word_timestamps=True`).
  → C'est la voix RÉELLE qui fait foi, PAS le `texte.txt` que j'avais écrit : Matys
  reformule souvent en enregistrant (ex. il a ajouté « quand on regarde Messi et Neymar »).
- À partir de la transcription horodatée, **mapper chaque segment de phrase au clip qui
  l'illustre** (si la VO nomme un joueur/objet à la seconde X → un plan de ce joueur/objet
  doit tomber à la seconde X). Caler les `beats` de l'EDL sur ces timestamps réels.
- Mettre à jour `texte.txt` avec la transcription exacte (référence sous-titres CapCut).

## 6. Recherche de clips (automatique)

- **Claude doit trouver les clips lui-même** via `WebSearch` (domaine youtube.com) sans
  demander à l'utilisateur de chercher. Recherches parallèles par type de plan nécessaire
  (hook visuel, action, émotion, payoff), puis téléchargement direct avec `telecharger.py`.
- Priorité aux URLs `/shorts/` (9:16 natif). Éviter les compilations 16:9.
- **Bannir les « edits » (titres avec #edit, watermark de créateur, textes incrustés,
  effets de zoom/transition) même en 9:16** : souvent pas vraiment 9:16 plein cadre et
  parasités par du texte. Privilégier les images de match brutes / officielles FIFA.
- **Vérifier CHAQUE clip retenu en planche-contact** avant de l'intégrer (cf. règle d'or §1).
- Lancer `telecharger.py` immédiatement après avoir les IDs, sans attendre confirmation.

## 7. Pipeline technique

### DEUX environnements Python — ne jamais les intervertir

| Usage | Interpréteur | Pourquoi |
|---|---|---|
| **Télécharger** (`yt-dlp`) | `.venv312/Scripts/python.exe` | yt-dlp récent exige Python ≥ 3.10. Avec le 3.9 système, YouTube ne sert plus que du **640×360** sur les vidéos longues. |
| **Monter** (`monter_edl.py`) | `.venv/Scripts/python.exe` | seul à avoir la version de `pyJianYingDraft` attendue par les scripts. |

```bash
.venv312/Scripts/python.exe telecharger.py shorts/<projet>/_src <id…>
.venv/Scripts/python.exe    monter_edl.py  shorts/<projet>
```

Si `.venv312` manque : `uv venv --python 3.12 .venv312 && uv pip install --python .venv312 -U yt-dlp imageio-ffmpeg`.

### Scripts

- `telecharger.py <dossier> <id…>` : download yt-dlp, H.264/mp4.
- `monter_edl.py <projet>` : monte depuis `edl.json`
  (`{ "musique":"skyfall", "images":[…], "beats":[ [chemin, debut_s, fin_s], … ] }`),
  pose la voix off `voix.mp3`, flou auto selon ratio (16:9 agrandi à 181 %), **musique en 2
  segments, flèche sticker d'intro, photos d'incrustation, bruitages, transitions de
  Matys**, puis patch signature + patch méta macOS.
  Options edl : `zoom` (1.8), `anim` (0), `gap`, `musique` (tiki/skyfall/cornfield/
  radiohead/chemin/false), `musique_debut`, `fleche` (false), `fleche_xy`, `images`,
  `sfx` (false), `accents`, `impact_beat`, `transitions` (false), `transitions_pas` (4),
  `seed`. Par plan (4e élément du beat) : `{"son": 1.0, "zoom": 1.5}`.
  **Clip parlé** (on garde son son) : beat `[chemin, debut, fin, {"son": 1.0}]` ; la VO
  doit contenir un blanc de même durée à cet endroit (VO générée en parties puis concaténée
  avec des silences, cf. `shorts/dembele_enrique/_vo/`). `_bin/rendu.py` le gère aussi.
  **Clip parlé en langue étrangère → traduction à l'écran AUTOMATIQUE** : clé edl
  `"textes": [{"texte": "« … »", "t": 22.64, "dur": 2.6, "y": -0.4}]` (piste texte,
  Montserrat blanc contour noir, calée sur le blanc de la VO). Non rendue par `_bin/rendu.py`.
- `generer_voix.py <projet>` : voix off avec le **clone ElevenLabs** de Matys
  (`texte.txt` → `voix.mp3`, l'ancienne voix est gardée en `.bak`). Variantes :
  `--texte "…" --out x.mp3`, `--fichier f.txt`, `--prise prise.m4a` (Voice Changer :
  la prise brute de Matys → voix studio du clone, ~1000 crédits/min),
  `--nettoyer voix.mp3` (retire seulement les respirations). Config :
  `_voix_clone/elevenlabs.json` (clé API, `voice_id`, modèle `eleven_v4`,
  `corrections_phonetiques` à enrichir quand un nom est mal prononcé — ex.
  Wijnaldum → Veinaldum). **Ne jamais afficher ni recopier la clé API.**
  Lancer avec `.venv/Scripts/python.exe` (requests + faster_whisper y sont).
- `telecharger_images.py shorts/<projet> nom=URL …` : photos d'incrustation → `images/nom.jpg`.
- `_sheet.py` / `_sheet16.py` : planches-contact rapides (variantes Windows de `_bin/planche.py`).
- `monter_short.py` : variante « clips entiers » (fallback).
- `_bin/transcrire.py <projet>` : transcription horodatée (faster-whisper) → `_mots.json`.
- `_bin/planche.py <projet>` : planches-contact de `_src/` → `_frames/` (vérif obligatoire).
- `_bin/nettoyer.py <projet> <id>:<top|bottom>:<pct>` : retire un bandeau **en bord d'image**
  puis re-remplit le 1080×1920 (jamais de flou sur un 9:16). Vérifier le résultat en
  planche-contact : les bandeaux descendent souvent plus bas qu'estimé (jusqu'à 35 %).
- `_bin/rendu.py <projet>` : rend `apercu.mp4` depuis l'EDL, pour contrôler le montage
  sans ouvrir CapCut.

### CapCut

- **Patch signature obligatoire** : pyJianYingDraft écrit `app_source:"lv"` ;
  `patch_pour_capcut()` réinjecte `"cc"` depuis un projet CapCut existant, sinon CapCut
  refuse d'ouvrir (« unusual path »).
- Brouillons : macOS `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`,
  Windows `C:\Users\<toi>\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft`.
  `DRAFT_DIR` détecte automatiquement.
- **Le fichier de projet n'a pas le même nom selon l'OS** : `draft_info.json` sur macOS,
  `draft_content.json` sur Windows. `patch_pour_capcut()` écrit **les deux**.
- **Patch `draft_meta_info.json` obligatoire sur macOS** : pyJianYingDraft laisse
  `draft_fold_path`, `draft_root_path`, `draft_name`, `tm_duration` **vides**. Windows
  s'en accommode ; **macOS non** — CapCut ne retrouve pas les médias, ouvre une timeline
  VIDE et **l'enregistre par-dessus le montage**. `patch_meta_capcut()` remplit ces
  champs + `draft_type: "video"`. Sans lui, le montage est silencieusement détruit à la
  première ouverture.
- **Fermer CapCut** avant de (re)lancer un montage (fichier `.locked` sinon) : le faire
  soi-même avec `_bin/fermer_capcut.bat` (demande Matys 2026-10-08 : ne plus sauter le montage
  parce que CapCut est ouvert). ⚠️ Vérifier ensuite `tasklist | findstr CapCut` **avant d'écrire**, et ne
  jamais écrire si ça répond. Après le montage : le relancer (monter_capcut.py le fait), ~20 s, recontrôler le brouillon.
- **Après le montage, contrôler que CapCut a bien gardé le projet** :
  `draft_info.json` doit garder ses ~7 pistes (video, vo, photos, sfx…, fleche, musique)
  et N segments. S'il tombe à 0 piste /
  `duration: 0`, c'est que CapCut a écrasé le montage (cf. `draft_meta_info.json` ci-dessus).
- **Sandbox CapCut macOS** : CapCut ne lit librement que `~/Movies` ; un média sous
  `~/Documents` donne « unsupported media » / « Relier des fichiers multimédia ».
  `monter_edl.py` embarque donc chaque média dans `<brouillon>/materials/` (lien physique,
  `embarquer_medias()`). Si un vieux brouillon le fait quand même : relier dossier par dossier
  (`_src`, `_assets/sfx_oct`, `_assets/musique`) — relier la racine `tiktokt` échoue.
- Sous-titres : **posés par le robot** (demande Matys 2026-10-08) — `monter_edl.py` les génère tout seul s'ils manquent dans l'edl (`"sous_titres": false` pour s'en passer), sinon `.venv/Scripts/python.exe _bin/sous_titres.py shorts/<projet>` après la transcription → clé edl `sous_titres` → piste « sous-titres » de `monter_edl.py`. **Jamais 2 lignes** : ≤ 18 caractères / 4 mots par sous-titre, `auto_wrapping` désactivé. Texte de `texte.txt` (orthographe), timing de `_mots.json`, jamais en même temps qu'une traduction `textes`.

### Windows

- Ce paquet est la version **Windows** : interpréteurs `.venv/Scripts/python.exe` et
  `.venv312/Scripts/python.exe` (chemins avec `/` depuis Git Bash), `_bin/ffmpeg.exe`.
- Les passages « macOS » ci-dessus (sandbox, `~/Movies`, TCC) ne s'appliquent pas.
- Définir `PYTHONUTF8=1` si un script plante sur des accents.

## 8. Finition : le style de montage de Matys

**Lire `STYLE_MONTAGE.md` avant chaque montage.** Mesuré sur ses brouillons CapCut :
musique de fond (TIKI TIKI pour 15-30 s, Skyfall karaoke pour 60 s, Cornfield Chase pour
le payoff, volume qui change à ~6,5 s = fin du hook), flèche d'intro + ding, bruitages
juste avant une coupe sur 2-3, sous-titres (légendes auto, modèle « 短文本-弹出 »,
Montserrat 13 blanc contour noir, échelle ~0,78, y ≈ -0,4), photos incrustées,
transitions rares. `monter_edl.py` pose déjà : 16:9 à 181 %, musique 2 segments,
flèche sticker, photos, bruitages, transitions.

**Réglages Matys 2026-10-28 (automatiques dans `monter_edl.py`)** :
- Voix off à **+18,5 dB** (edl `vo_db`) ; ding d'intro baissé à 0,5 (edl `vol_ding_intro`).
- Flèche d'intro plus petite (échelle 0,4) et **sur 3 vidéos sur 4** seulement (décision gardée par
  projet dans `shorts/_fleche.json` ; edl `"fleche": true/false` pour forcer).
- La flèche **désigne le joueur** (ou l'élément) du 1er plan : `_bin/fleche.py shorts/<projet> [x y]`
  sort `_frames/fleche.png` (1er plan cadré 1080×1920, viseur, zones masquées en rouge) ; viser le
  joueur puis écrire `"fleche_xy": [x, y]`. Elle reste **hors des zones de l'interface TikTok /
  YouTube Shorts** (barre de recherche en haut, légende et commentaires en bas, boutons à droite) :
  `monter_edl.py` la recale dans la zone sûre si besoin. **À la fin de chaque montage, rappeler à
Matys la checklist de finition** de `STYLE_MONTAGE.md` (déplacer la flèche sur
l'élément, légendes auto + modèle, relais Cornfield si besoin).

## 9. Vraies photos en incrustation (AUTO, demande Matys 2026-10-06)

À chaque montage, **Claude ajoute lui-même 3 à 6 vraies photos** sur les passages
importants : quand la VO nomme un joueur, un coach, un club, un trophée, un titre de
presse, un chiffre clé. But : donner au viewer quelque chose de nouveau à regarder.
- Style mesuré sur 14 de ses brouillons : piste au-dessus de la vidéo, centrée, échelle
  ~0,65 (0,5-0,78), durée 1,3-5 s (médiane ~2,2), aucune animation, posée pile sur le mot
  de la VO (timestamps de la transcription). Pas deux photos collées, pas dans les 2
  premières secondes sauf si c'est le hook.
- Recherche : Google Images dans le **navigateur intégré** (`google.com/search?tbm=isch&q=…`)
  puis ouvrir l'image pour avoir son URL directe ; secours : API Wikimedia Commons.
  Photo réelle, nette, ≥ 400 px, sans gros watermark ni texte parasite. **Regarder
  chaque image (Read) avant de la garder.**
- Téléchargement : `.venv/Scripts/python.exe telecharger_images.py shorts/<projet> nom=URL …`
  → `images/nom.jpg` (converti en JPG via ffmpeg).
- EDL : `"images": [ {"src":"images/olise.jpg","t":21.9,"dur":2.2,"y":0,"scale":0.65}, … ]`
  (ou `["images/olise.jpg", 21.9, 2.2]`).
- **Son à l'apparition de chaque image, automatique** : surtout le **ding** `1005(1)` (Matys
  2026-10-08 : « plus de ding, ça attire plus l'oreille ») → ding sur 2 photos sur 3 (pic calé sur
  l'apparition), `1006` sur la 3e. Edl `"son_photo"` : `"mix"` (défaut) / `"ding"` / `"1006"`.

## 10. Bruitages, musique & transitions (état 2026-10-06)

- Sons dans `_assets/sfx_oct/` (fournis en clair par Matys, ses presets CapCut étant
  chiffrés) : `1005(1)` ding à 0 s, `1005(6)` riser dont le pic tombe sur la coupe ~6,5 s,
  `1005(4)` impact vers 62 % de la vidéo, ding `1005(1)` (2 photos sur 3) ou `1006` à chaque photo.
- Transitions : **uniquement** `standard_woosh.mp3` / `fast_woosh.mp3` (pack Lewi Pilgrim,
  validés par Matys), en alternance, pic calé sur la coupe.
- Accents de coupe (click/punch/pop/tonal) : gardés en réserve, **OFF**
  (`"accents": true` pour les remettre).
- Transitions vidéo : les vraies transitions CapCut de Matys (ids natifs relevés dans ses
  brouillons : Film Erase en tête, Flash Snap, Mix, Aura Flash, Pull In II, Fly Away…),
  tirées au sort pondéré. Elles doivent être posées sur les segments **avant**
  `script.add_segment`, sinon elles ne sont pas écrites.
- Musiques dans `_assets/musique/` (tiki_tiki_slowed, skyfall_karaoke, cornfield_chase,
  radiohead_everything). Défaut : tiki si ≤ 35 s, skyfall au-delà.
- **Volumes baissés par défaut** (Matys 2026-10-08, « baisse un peu le son des transitions et de la
  musique ») : musique x0,7 (`VOL_MUSIQUE`, edl `vol_musique`), woosh de transition 0,5 au lieu de
  0,8 (`VOL_WOOSH`, edl `vol_transitions`).

## 10 bis. Studio Shorts (interface veille → scripts → production)

Le studio est une **application de bureau** (`studio/app.py`, raccourci « Studio Shorts »),
partagée avec Elian (Mac). La **veille du jour** tourne seule chaque matin (`studio/quotidien.py`,
tâche Windows créée par `Activer la veille du jour.bat`, et relance par l'app ouverte après 7 h
sur le PC de Matys) : formule 4 × 1 min + 5 × 25-30 s, scripts écrits d'office.

Quand Matys demande **« la veille actu sport »** (ou « la veille »), le résultat s'affiche dans
l'interface `studio/` et non en texte dans le chat :
1. Faire la veille (procédure `~/.claude/scheduled-tasks/veille-actu-sport/SKILL.md`) en écrivant
   le `.md` ET le `.json` (`studio/schema_veille.json`) dans `shorts/_veille/` — ou, si un rapport
   du jour existe déjà, se contenter de l'afficher.
2. Démarrer le serveur s'il ne tourne pas : `.venv/Scripts/python.exe studio/serveur.py` en tâche de fond
   via Bash (le lanceur de prévisualisation n'a pas accès à `~/Documents`), puis ouvrir
   `http://localhost:8765` dans le navigateur intégré (`preview_start` avec `url`).
   Matys peut aussi double-cliquer `Studio Shorts.bat`.
- Dans l'interface : il clique un sujet (note, faits, vidéos jouables, citations, hooks, sources),
  le valide → l'IA écrit 2-4 scripts (`studio/prompts.py`, mêmes règles que §4) ; chat latéral
  pour les retouches ; bouton « Lancer la production » → agent Claude Code autonome qui suit ce
  CLAUDE.md (VO clone, clips, photos, EDL, aperçu, CapCut) et écrit `shorts/<projet>/_production.md`.
- Écran Production = journal en direct + **chat avec l'IA du montage** : pendant le travail, un
  observateur (lecture seule) répond et transforme les demandes de changement en consignes dans
  `shorts/<projet>/_consignes.md`, que l'agent relit entre chaque étape ; une fois fini, chaque
  demande relance l'agent sur sa propre session (`--resume`) pour appliquer la modification.
- **Barre de recherche** (en haut de la veille) : Matys tape son propre sujet → Claude le documente
  comme un sujet de veille (`prompt_recherche`) et l'ajoute en tête de la veille affichée (ou de
  `shorts/_veille/AAAA-MM-JJ_perso.json`) ; ensuite même parcours scripts → production.
- **« ✍️ Mon script »** (en haut, et à côté de la recherche) : Matys colle son script tout prêt
  (ou glisse un .txt) → sujet `script_perso` dans `shorts/_veille/AAAA-MM-JJ_perso.json`, puis
  montage lancé tout de suite ou ouverture dans l'atelier. La VO reste son texte mot pour mot ;
  l'agent trouve lui-même clips, citations et photos.
- Plusieurs productions peuvent tourner en parallèle (panneau « Montages » sur le côté). L'étape
  CapCut passe toujours par `_bin/monter_capcut.py shorts/<projet>` : verrou exclusif (un brouillon
  à la fois), ferme CapCut, `monter_edl.py`, rouvre CapCut et vérifie que le brouillon tient.
- L'IA du studio = le CLI Claude Code (`claude`), connecté une fois par
  `claude auth login`. État des sujets : `shorts/_veille/studio/<veille>.json` ; journaux des
  tâches : `studio/_jobs/`.

## 11. Dossier d’un projet

```
shorts/<nom>/
  voix.mp3      voix off
  texte.txt     texte intégral de la VO (référence sous-titres)
  edl.json      liste de découpe (beats, musique, images…)
  images/       photos d'incrustation (telecharger_images.py)
  clips/        clips coupés, au format NATIF (9:16 plein cadre OU 16:9 brut)
  _src/         sources longues téléchargées (yt-dlp)
  _frames/      planches-contact de vérification
```
