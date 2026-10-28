# Guide d'écriture des scripts 1 min : fusion Max Parra + TopFoot

À lire avec `scripts_modeles.md` (référence validée) avant chaque script. Les deux bases :

- `shorts/_recherche_maxparra/` : 931 shorts transcrits, `index.json` trié par vues, `analyse_storytelling.md`.
- `shorts/_recherche_topfoot/` : @topfoot_youss, `index.json` + `base.md` triés par vues, un fichier par script dans `scripts/`.
  Mise à jour : `.venv312/Scripts/python.exe _bin/veille_tiktok.py topfoot_youss` (avec `VN=400`), puis
  `.venv/Scripts/python.exe _bin/topfoot_transcrire.py topfoot_youss 160`, puis `.venv312/Scripts/python.exe _bin/topfoot_base.py`.

## 1. Ce que montrent les chiffres (et ce qu'ils ne montrent pas)

TopFoot : 400 vidéos listées, médiane 214 k vues, durée médiane 65 s. Sur les 120 vidéos les plus vues transcrites, environ la
moitié sont des montages sans voix off (musique, ambiance : le record de 15,5 M est un montage). Seules les
vidéos narrées comptent pour l'écriture : **78 scripts, 150 à 330 mots (cœur : 220-295), médiane 558 k vues, 60-70 s**.
C'est notre format exact.

Honnêteté sur la base : à cette taille (78 scripts), ni le sujet (Coupe du monde, PSG, Mbappé), ni le « sauf que », ni le
nombre de « parce que », ni la présence d'un appel à s'abonner ne font bouger la médiane de façon fiable.
**Ce qui sépare les 2-4 M des 500 k, c'est la première phrase.** Les tableaux ci-dessous portent donc sur le hook.

Max Parra (rappel) : « la vraie raison » 4,1 M, « personne n'a compris » 1,1 M, « Si tu… » 1,7 M,
« Quand [sujet] [geste étrange] » 880 k sur 254 vidéos, ses formats d'1 min font ~1 M en médiane.

## 2. Catalogue de hooks (les 2 bases fusionnées)

Règle commune : **la 1re phrase promet une explication qu'on ne donne pas encore.** Elle contient soit
un fait précis (nom, chiffre, minute), soit un jugement fort, jamais une généralité.

| # | Gabarit | Origine | Exemple réel | Vues |
|---|---|---|---|---|
| 1 | **Jugement fort annoncé, justifié juste après** : « Je pense qu'on va assister à [superlatif négatif ou positif] de [période] » + « Parce que… » | TopFoot | La Coupe du Monde la plus honteuse | 3,8 M |
| 2 | **Fausse lecture du viewer, corrigée dans la phrase d'après** : « Tu crois voir [X banal] ? En réalité, c'est peut-être ce qui [a causé un gros résultat]. » | TopFoot | Dégagements de Safonov | 2,6 M |
| 3 | **« Et si je vous disais que [hypothèse précise] ? »** | TopFoot + Max Parra | Mbappé refait la carrière de CR7 | 1,6 M |
| 4 | **Chiffre sec ou durée absurde en ouverture** (« 0,05 % », « 438 minutes debout ») | TopFoot | Le supporter debout 438 minutes | 1,4 M |
| 5 | **Cause avant l'événement** : « Tout commence une semaine plus tôt… » puis « Sauf que » | TopFoot | Guendouzi, la guerre OL-Fener | 1,4 M |
| 6 | **« La vraie raison » / « Pourquoi [star] fait X ? »** | Max Parra | Ronaldo refuse de serrer la main de Kanté | 2,9 M |
| 7 | **« Quand [sujet] [geste étrange], personne n'a compris… »** (idéal avec un clip du geste) | Max Parra | Le joueur africain en demi-finale | 12,2 M |
| 8 | **Antithèse sur une personne** : « Personne ne voulait de lui pour [X], mais c'est lui qui vient [sauver] » | TopFoot | Le Marocain que personne ne voulait | 548 k |
| 9 | **Promesse / scène humaine annoncée** : « [Nom] a fait une promesse. » | TopFoot | Diomandé et sa sœur | 673 k |
| 10 | **« Cette réponse / cette phrase de X est la raison pour laquelle… » + clip** | Notre modèle | Dembélé / Enrique | référence |
| 11 | **« Si tu… »** hypothèse à la 2e personne | Max Parra | Si tu trouves du pétrole… | 1,7 M |

À éviter en ouverture (TopFoot comme Max Parra) : « Ce / Cette X… » sec sans fait, le simple annonce de
sujet (« Aujourd'hui on parle de… »), les questions fermées sans enjeu (la question simple fait 624 k
contre 723 k sans, à échantillon faible).

## 3. Mécaniques de suspense (ce qui retient jusqu'à la fin)

1. **La réponse est annoncée mais retardée.** Le hook dit « c'est la raison de X » et la raison arrive aux deux
   tiers, après une chaîne de « parce que ». Chaque « parce que » répond à moitié et ouvre le suivant.
2. **La série qui s'accélère.** Malédiction de la Ligue des champions : 2019, 2020, 2021… sept cas bâtis sur la
   même phrase (« il se fait les ligaments, quelques mois après »), le cas du jour tombe en dernier. Le cerveau
   voit le motif et attend le dernier maillon. À utiliser dès que le sujet a 4 précédents ou plus.
3. **Le nom ou le détail clé repoussé.** Le Marocain « que personne ne voulait » : on apprend son nom, puis son
   prénom sur le maillot, à la fin seulement. Garder le plus parlant pour le dernier tiers.
4. **Le faux calme puis l'escalade.** « Un match plutôt calme. Sauf que… » (Guendouzi). Poser le banal, puis
   casser.
5. **Une relance explicite vers 2/3 du temps** : « Et c'est là que le scénario devient fou », « Sauf que le plus
   terrifiant commence maintenant », « Mais ce qu'il savait pas, c'est que… ».
6. **Fraîcheur datée** : « hier soir », « cette nuit », « ce soir ». Le viewer sent que l'info est chaude.
7. **La chute reboucle sur le hook** : on reprend les mots de la 1re phrase, mais ils veulent dire autre chose
   (« Tu crois voir un dégagement raté » devient « avec Enrique, rien n'est laissé au hasard »).
8. **Échéance ouverte** (notre modèle) : une date et un lieu qui laissent la question en suspens, utile
   pour les commentaires.

## 4. Squelette d'1 minute (≈ 265 mots, 4,5 mots/s)

| Temps | Mots | Rôle |
|---|---|---|
| 0-5 s | 20-30 | Hook (catalogue §2) + clip immédiat si citation ou geste |
| 5-15 s | 40-50 | Enjeu et décor : qui, quand, contre qui, un chiffre |
| 15-35 s | 80-90 | Déroulé factuel en « parce que / et / alors », un détail concret par phrase, passage au présent narratif (« va + infinitif » chez Max Parra) |
| 35-45 s | 45 | Retournement : « Sauf que… » ou « Et c'est là que… », info que le viewer ignore |
| 45-55 s | 45 | Payoff : la réponse annoncée dans le hook, avec preuve (stat, clip parlé) |
| 55-60 s | 20 | Chute : reboucle sur le hook, ou antithèse + échéance datée |

Clips parlés : un par acte au maximum, préparés par la VO (« Il dit ça, lorsqu'on lui demande… ») puis la VO se tait.
Appel à s'abonner : TopFoot en met un à la fin sur 39 vidéos sur 55, sans effet mesurable sur les vues. Max Parra n'en met pas.
Par défaut on n'en met pas, sauf demande de Matys.

## 5. Humaniser (voix de Matys, pas « TikTok IA »)

Garder les règles de `style-redaction-anti-ia` : phrases longues qui s'enchaînent, ton plat et factuel,
pas d'adjectif qui commente l'émotion (bouleversant, incroyable, fou), pas de fragment punchy isolé, pas de
morale. TopFoot le confirme : même ses scripts à 2-4 M restent sobres, l'effet vient du fait choisi et de l'ordre
dans lequel on le révèle, pas de l'emphase.

Gabarits d'oralité à reprendre : « Parce que… », « Sauf que… », « Donc… », « Résultat, … », « Et là, … »,
« Alors que… », « Autrement dit… ». Tutoiement léger du viewer, une fois ou deux (« tu te dis »).

Procédure : écrire d'un jet, puis (1) fusionner les phrases courtes, (2) supprimer les adjectifs d'émotion et les
formules en trois, (3) lire à voix haute : toute phrase qui ne passe pas d'un souffle est coupée, (4) chasser
les mots finissant en « é » pour le clone, (5) compter 260-275 mots, (6) passer le texte au skill `humanizer` si un
tic d'IA persiste.

## 6. Méthode pour chaque nouveau script

1. Vérifier les faits (score, minute, citation) AVANT d'écrire. Aucune citation non retrouvée dans une source.
2. Choisir le hook dans §2 selon la matière : citation filmée = #10 ou #2, chiffre fort = #4, événement chaud
   = #1 ou #5, destin d'un joueur = #8 ou #9, série de précédents = #3 + série (§3.2).
3. Écrire 2 à 3 versions de la 1re phrase et garder celle qui promet le plus sans révéler la réponse.
4. Dérouler le squelette §4 en notant à côté de chaque phrase le clip prévu (point d'ancrage du montage).
5. Livrer à Matys avec : le hook choisi, la mécanique de suspense utilisée, et ce qui n'a pas pu être vérifié.
   Pas de voix tant qu'il n'a pas validé.

## 7. Banque de tournures (extraite des deux bases, à utiliser en priorité)

Mesurée sur 78 scripts TopFoot narrés et 128 scripts Max Parra de 45 s et plus. Écrire avec ces mots, pas avec les miens.

Débuts de phrase les plus fréquents (nombre d'occurrences) :
- **Sauf que** (71 chez Max Parra, 13 TopFoot) : le retournement. **Parce que / Parce qu'à…** (43 / 58) : l'explication, souvent en tête de paragraphe.
- **Et pour cause**, **Et c'est là que…**, **Et même…**, **Et surtout,**, **Et là,**, **Et ça,** : relances.
- **Mais ce que…**, **Mais bizarrement,**, **Mais alors,**, **Mais malgré…** (Max Parra) ; **Autrement dit,**, **Donc oui,** (TopFoot).
- **Ceci dit,**, **En fait,**, **Et bien,**, **Il s'avère que…**, **Donc qu'est-ce qui s'est passé ?** (Max Parra, question qui relance au milieu).
- **Résultat,** (TopFoot, pour annoncer la conséquence), **Prenons X, par exemple.**, **Et ce n'est pas un cas isolé.**

Expressions de fond : **tout le monde**, **personne ne se doutait**, **en plein milieu de**, **dès le début**, **à ce moment-là**, **à cause de**, **le problème c'est que**, **le pire c'est**, **le plus étrange c'est**, **quelque chose de très étrange**, **un détail très étrange**, **pour une très bonne raison**, **quelques semaines / mois plus tard**, **beaucoup vont remarquer**.

Verbes derrière « va » chez Max Parra : commencer (34), faire (27), être (26), avoir (18), arriver (18), décider (18), réussir (16), remarquer (15), perdre (12), prendre (10), refuser (9), sortir (8), finir (8).
Les infinitifs en -er passent bien avec le clone (confirmé par Matys le 2026-10-24) : « va + infinitif » s'emploie sans restriction. Le « é » accentué final (pénalité, aligné) reste à éviter tant que Matys n'a pas dit le contraire.

Ce que TopFoot ajoute : phrases d'entrée simples (« Prenons l'Irak, par exemple »), cause avant événement (« Tout commence une semaine plus tôt »), annonce du chiffre en phrase séparée.
À ne pas copier : les « et si tu veux plus… abonne-toi » et les répétitions du type « qu'elle fait » sont des artefacts de transcription ou des CTA, pas du style.
