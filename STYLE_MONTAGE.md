# Style de montage de Matys (mesuré dans CapCut)

Source : les 375 brouillons CapCut, dont 48 shorts verticaux montés en entier entre mars et
août 2026. Le style actuel (juin-août 2026) se lit sur les 19 projets passés par le robot
puis finis à la main : bouche, cartons, david_rose, egypte_iran, fils_cincinnati,
france_irak, france_suede, haaland_mbappe, jonathan_tah, mbappe_enerve, mbappe_ronaldo_1min,
mbappe_vitesse2, neves, real_madrid_vinicius, ronaldo_tatouage, yamal, yamal_dribble,
yamal_messi. Les chiffres ci-dessous en sont tirés (scripts dans `_analyse/capcut/`).

Légende : [AUTO] = fait par `monter_edl.py`, [MANUEL] = reste à faire dans CapCut.

## 1. Rythme et cadrage

Un short de 15-30 s compte 11 à 16 plans (1,2 à 1,8 s par plan). Un short d'une minute en
compte 25 à 43 (2 à 2,8 s par plan). La règle « ~1,3 s par plan » du CLAUDE.md vaut donc
pour les formats courts ; sur une minute Matys laisse respirer un peu plus.

Les clips 16:9 gardent le fond flou CapCut et sont agrandis à **~181 %** (règle montrée par
Matys en vidéo le 2026-10-08 : Échelle 100 % → 181 % dans CapCut). Le plan devient bien
visible mais n'est pas zoomé plein écran : il reste une bande floue en haut et en bas et on ne
perd qu'une partie raisonnable des côtés. [AUTO] `zoom` vaut 1.8 par défaut dans
`monter_edl.py` ; ne pas écrire d'autre valeur globale (ni 1.0, ni 2.0) ; par plan, seulement
`{"zoom": 1.5}` si un élément essentiel serait coupé au bord.

Le petit zoom d'entrée « 轻微放大 » sur un plan sur trois est gardé tel quel. [AUTO]

## 2. Flèche d'intro + ding

Présente dans 15 des 19 projets. Sticker CapCut « Emphasis Stickers Circle & Arrow EN »
(resource_id `7496729827391606069`), de 0 s jusqu'à la première coupe (0,7 à 1,7 s),
échelle 0,4-0,6, placée là où se trouve l'élément à montrer (souvent en haut, y ≈ 0,3 à
0,67). Elle revient parfois une 2e fois en cours de vidéo quand la VO désigne quelque chose
(real_madrid 16,9 s, yamal_messi 12,7 s, mbappe_ronaldo 15,6 s).

Le son qui l'accompagne est le preset « My presets13 » posé à 0 s (27 fois sur 32 flèches
appariées), volume 0,55-1,0. Variante plus rare : My presets48 ou My presets7 à 0 s.

[AUTO] la flèche est posée en (-0,3 ; 0,5). [MANUEL] la déplacer sur l'élément et ajouter le
ding (preset chiffré, voir §4). Option edl : `"fleche": false` ou `"fleche_xy": [x, y]`.

## 3. Musique de fond

Toujours une instrumentale importée depuis `Videos/4K Video Downloader+` (copies audio dans
`_assets/musique/`) :

| morceau | quand | départ dans le morceau | volume |
|---|---|---|---|
| TIKI TIKI (Slowed) | shorts 15-30 s (8 projets) | 0 s | ~0,5 jusqu'à 6,5-7 s, puis 0,27 |
| Skyfall karaoke (Adele) | shorts ~60 s (4 projets + toute l'ère avril-juin) | 1,8 s | ~0,4 puis ~0,5 dès 6,6 s |
| Cornfield Chase (Interstellar) | partie émotion / fin, relaie Skyfall | 31-33 s | 0,6-1,0 |
| Radiohead Everything In Its Right Place | alternative calme | 0,2 s | 0,85-1,0 |
| My presets8 / My presets3 | yamal, yamal_dribble, mbappe_ronaldo, haaland, yamal_messi | 0 s | ~1,0 |

Le geste constant : la musique est coupée en deux segments vers 6,5 s, à la fin du hook,
pour changer de volume (TIKI baisse, Skyfall remonte un peu). [AUTO] choix par défaut : tiki
si la vidéo fait 35 s ou moins, skyfall au-delà. Option edl : `"musique": "cornfield"`,
`"radiohead"`, un chemin, ou `false` ; `"musique_debut": 31.3` pour démarrer ailleurs.
[MANUEL] relayer par Cornfield Chase sur le payoff si besoin (fait dans fils_cincinnati à
34 s) ; les presets 8 et 3 sont chiffrés.

## 4. Bruitages

Densité : environ 10 par minute sur un 60 s, 11 à 22 par minute sur un 15-30 s. Ils ne sont
pas sur chaque coupe (environ une coupe sur deux ou trois). Ils démarrent juste avant la
coupe (0 à 0,5 s avant) pour que l'impact tombe dessus. Volume 1,0 sauf mention.

Tous viennent de ses presets combinés CapCut (« My presetsN »). Rôles déduits des positions :

| preset | durée | usage observé |
|---|---|---|
| 13 | 0,83 s | ding de la flèche, à 0 s |
| 36 | 0,87 s | son de coupe le plus utilisé (40 fois), ~0,1 s avant la coupe |
| 2 | 2,73 s | 2e bruitage du short (1,2-4,5 s), sorte de montée |
| 49 puis 50 | 2-3 s / 1,1-1,3 s | duo juste après le ding (49 vers 0,8-2,4 s, 50 environ 2 s après) |
| 51 | 1,83 s | coupe, ~0,5 s avant |
| 7 | 2,0 s | coupe ; parfois à 0 s à la place du ding |
| 52 | 0,7 s | petit accent |
| 1 | 0,9 s | petit accent |
| 56 | 3,67 s | gros impact sur un moment fort, volume poussé (1,7) |
| 48 | 0,83 s | ding alternatif |

Ouverture type : 13 à 0 s, puis soit 49 + 50 dans les 4 premières secondes, soit 2 vers
2-4 s, puis 36 sur la coupe suivante.

Blocage : CapCut chiffre les fichiers audio de ces presets (dans les brouillons comme dans
`User Data/Presets/Combination`). Le robot ne peut pas les poser tant que Matys ne fournit
pas les sons en clair. [MANUEL] pour l'instant. Solution prévue : un projet CapCut avec les
presets 13, 36, 2, 49, 50, 51, 7, 52, 1, 56, 48 posés l'un après l'autre avec 1 s de blanc,
exporté en audio seul ; le robot le découpe dans `_assets/sfx/` et les place selon ce tableau.

## 5. Sous-titres

Légendes automatiques CapCut (fr-FR) sur la voix, avec le modèle de sous-titres
« 短文本-弹出 » (texte court, apparition pop). Rendu constant sur les 19 projets :
Montserrat, taille 13, blanc, contour noir 0,116, échelle 0,7-0,92 (médiane 0,78), position
y entre -0,2 et -0,53 (médiane -0,4, donc dans le tiers bas). Environ 6 mots et 1,4 s par
sous-titre (egypte_iran : 2 mots, 0,6 s).

Ancien style (avril-juin 2026, projets 0412 à 0611) : jaune #F0FF00, taille 10, 2-3 mots par
sous-titre, sans modèle. Ne plus l'utiliser.

[MANUEL] le robot ne peut pas déclencher les légendes auto ni appliquer ce modèle.

## 6. Photos en incrustation

2 à 7 photos par vidéo (jpg de joueur, capture, image générée) sur une piste au-dessus,
échelle ~0,65, 1,2 à 5 s, posées quand la VO nomme une personne ou un objet. Centrées (x 0, y 0 à 0,3), aucune
animation. [AUTO depuis 2026-10-06] clé edl `images` + bruitage 1006 à l'apparition (voir CLAUDE.md §8).

## 7. Le reste, plus rare

Transitions : 0 à 3 par vidéo, presque toujours « Film Erase », parfois « Flash Snap » ou
« Aura Flash », aux changements de partie du récit. Jamais sur chaque coupe.
Effet « White Flash 2 » sur les 0,4 premières secondes : 3 projets.
Filtre « 4K » sur toute la durée : 6 projets sur 19.
Stickers de floutage (« Blur & Censored ») pour masquer un texte ou un logo : yamal_dribble.
Volume de la VO monté à ~8,5 (≈ +18 dB) sur les enregistrements micro ; avec la voix clonée
ElevenLabs, vérifier le niveau avant de toucher au gain.

## Checklist de finition dans CapCut (ce qui reste après le robot)

1. Déplacer la flèche sur l'élément, ajouter le ding (preset 13).
2. Bruitages : 49+50 ou 2 en ouverture, puis 36/51/7 juste avant une coupe sur deux ou trois,
   56 sur le moment fort.
3. Légendes auto + modèle « 短文本-弹出 », recaler la taille vers 0,78 et y vers -0,4.
4. Photos en incrustation sur les noms cités.
5. Si besoin : une ou deux « Film Erase », relais Cornfield Chase sur le payoff.

## Refaire l'analyse

Dans `_analyse/capcut/` : `python extract.py` lit `draft_content.json` (ou `.bak`) de chaque
brouillon et écrit `projets.json` ; `agg.py` sélectionne les shorts finis (`sel.json`) et
compte effets, stickers, polices ; `deep.py` donne rythme, zoom, musique, flèches ;
`subs.py` le style des sous-titres ; `bgm.py` musique et placement des bruitages sur les
projets nommés. Lancer avec `PYTHONIOENCODING=utf-8`. À refaire quand le style évolue.

## Mise à jour 2026-10-05 : bruitages 1005*.MP3 et transitions

Matys a fourni 9 sons en clair (`_assets/sfx_oct/`, copiés de Téléchargements). Rôles déduits de
l'analyse audio (durée, instant du pic, spectre), rapprochés des presets de §4. Non écoutés.

| fichier | durée / pic | rôle dans le robot | preset proche |
|---|---|---|---|
| 1005(1) | 0,86 s / 0,09 s | `ding` à 0 s | 13, 48 |
| 1005(2) | 0,91 s / 0,25 s | `swoosh` posé sur chaque transition | |
| 1005(3) | 0,86 s / 0,06 s | `click`, accent de coupe | 36, 52 |
| 1005(4) | 1,10 s / 0,10 s | `impact`, vers 62 % de la vidéo | 51, 7 |
| 1005(5) | 0,94 s / 0,38 s | `tonal`, accent de coupe | |
| 1005(6) | 2,77 s / 1,76 s | `riser`, pic calé sur la coupe vers 6,5 s | 2 |
| 1005(7) | 0,52 s / 0,09 s | `punch`, accent de coupe | |
| 1005(8) et 1005 | 0,24 s | `pop`, accent de coupe | |

`monter_edl.py` : plus d'animation d'entrée (`anim` vaut 0 par défaut) ; ~1 transition sur 4
coupes, toujours différente de la précédente, tirée dans une liste de 15 (Film Erase, flashs,
fondus rapides, 0,35 s) ; sons répartis sur plusieurs pistes `sfx`. Options edl : `transitions`
(false), `transitions_pas`, `sfx` (false), `impact_beat`, `seed`.

Piège : `anim` dans l'edl.json (ex. 3) pose des animations d'entrée ; mettre `"anim": 0`. Les transitions doivent être ajoutées aux segments AVANT `script.add_segment`, sinon elles ne sont pas écrites dans le brouillon.
