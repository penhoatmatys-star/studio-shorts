# Comment les scripts qui marchent sont construits

Généré par `outils/synthese.py` depuis le corpus et ses annotations. Ne pas éditer à la main.

## Voix mesurée (médianes par script)

| | Max Parra 1 min | TopFoot 1 min | Max Parra 20-38 s |
|---|---|---|---|
| Mots | 270 | 251 | 108.0 |
| Mots par phrase | 25 | 11.5 | 25.75 |
| Part de phrases ≤ 8 mots | 0.08 | 0.26 | 0.0 |
| Part de phrases ≥ 25 mots | 0.5 | 0.05 | 0.5 |
| Mots du hook | 27 | 14 | 22.0 |
| « tu / vous » pour 100 mots | 0.0 | 1.19 | 0.0 |
| Questions | 0 | 0 | 0.0 |

Le script modèle validé par Matys (Dembélé / Mbappé / Enrique) : 24 mots par phrase, 0 % de phrases courtes, hook de 20 mots, zéro « tu », zéro question. **La voix à viser est celle de Max Parra**, y compris sur l'actu ; TopFoot sert pour la mécanique des preuves enchaînées.

Liaisons de Max Parra (pour 100 mots) : « mais » 1.09, « parce que » 0.38, « alors » 0.3, « donc » 0.25, « sauf que » 0.21, « beaucoup » 0.2, « vu que » 0.17, « tout le monde » 0.16, « bizarrement » 0.13, « et pour cause » 0.09, « en fait » 0.05, « c'est là que » 0.05, « personne ne se doutait » 0.04, « étrangement » 0.04, « aujourd'hui » 0.03, « pour une très bonne raison » 0.03, « du coup » 0.02, « en réalité » 0.02

## Max Parra, shorts d'1 min (71 scripts annotés)

### Hooks, du plus vu au moins vu (vues médianes)

| Type | Nb | Vues médianes | Exemple le plus vu (1re phrase) |
|---|---|---|---|
| liste_techniques | 1 | 10,832,264 | « Voici trois vraies techniques qu'utilisent les cyclistes à la télé pour tricher pendant une course. » |
| quand_ce_mystere | 39 | 2,007,840 | « Quand ce joueur africain est rentré sur le terrain en demi-finale de coupe, étrangement, personne n'a compris ce qu'il faisait là et même son entraîneur semblait très surpris vu qu'il n'avait pas demandé à faire un chang » |
| autre | 7 | 1,597,362 | « Après avoir filmé des vidéos de son fils doué au basket, ce père de famille va faire croire à toute l'Amérique que c'était un prodige du basket pendant plusieurs années jusqu'à que tout le monde découvre que ce n'était q » |
| detail_etrange_regarde | 11 | 1,534,722 | « Regarde bien cette femme parce que sur cette photo, elle se fait attaquer par un homme en plein milieu d'un marathon mais ce qu'elle savait pas c'est que son attaque allait changer à tout jamais les règles de la compétit » |
| pourquoi_question | 8 | 1,475,236 | « Qu'est-ce qui se passerait si un lanceur de javelot lançait par erreur son Javelot sur un caméraman ou un arbitre ? » |
| fait_chiffre | 1 | 1,419,758 | « Il y a 12 ans, Nike avait prédit le problème du football moderne dans une publicité juste avant la Coupe du monde, mais personne ne les a écoutés parce qu'en 2014, dans la pub The Last Game, on voit les meilleurs joueurs » |
| tu_tes_deja_demande | 4 | 929,718 | « Tu t'es déjà demandé qui montrait le plus vite le col le plus dur de France entre un cycliste amateur, un pro et un cycliste du Tour de France ? » |

Héros d'abord décrit sans son nom : **55 scripts sur 71** (77 %).

### Suites de temps les plus fréquentes

- (8×, 1,686,178 vues méd.) hook → mise en place → explication → mise en place → retournement → dénouement
- (8×, 1,512,564 vues méd.) hook → mise en place → retournement → dénouement
- (6×, 2,751,129 vues méd.) hook → mise en place → explication → retournement → dénouement
- (6×, 1,427,512 vues méd.) hook → mise en place → retournement → mise en place → dénouement
- (4×, 1,578,013 vues méd.) hook → mise en place → retournement → explication → dénouement
- (3×, 1,238,949 vues méd.) hook → mise en place → explication → dénouement
- (3×, 998,409 vues méd.) hook → mise en place → explication → mise en place → dénouement
- (2×, 1,865,602 vues méd.) hook → preuve → mise en place → retournement → dénouement

### Comment chaque temps commence (2 premiers mots les plus fréquents)

- **escalade** (106) : « sauf que » 11 %, « mais le » 5 %, « et ça » 4 %, « et pour » 4 %, « mais ce » 3 %
- **mystere** (80) : « mais alors » 9 %, « sauf que » 8 %, « et pour » 6 %, « donc qu'est-ce » 6 %, « mais le » 6 %
- **hook** (71) : « quand ce » 28 %, « quand cette » 8 %, « quand cet » 6 %, « regarde bien » 6 %, « tu t'es » 6 %
- **retournement** (61) : « sauf que » 13 %, « mais ce » 7 %, « mais c'est » 7 %, « mais même » 3 %, « sauf qu'au » 3 %
- **explication** (57) : « parce que » 9 %, « et pour » 9 %, « sauf que » 7 %, « et ça » 5 %, « en fait » 5 %
- **contexte** (55) : « parce que » 18 %, « le mec » 7 %, « et pour » 5 %, « la femme » 4 %, « parce qu'au » 4 %
- **payoff** (55) : « en fait » 7 %, « et pour » 5 %, « et bien » 4 %, « alors par » 4 %, « parce que » 4 %
- **chute** (48) : « ceci dit » 10 %, « yeah » 6 %, « sauf que » 4 %, « et même » 4 %, « ce qui » 4 %
- **preuve_clip** (18) : « et il » 6 %, « ici on » 6 %, « quand guidé » 6 %, « vu qu'au » 6 %, « et c'est » 6 %
- **cta** (2) : « et ça » 50 %, « si vous » 50 %
- **opinion** (1) : « eh bien » 100 %

### Chutes

fait_final 75 %, coupe_net 13 %, morale_antithese 7 %, cta 3 %, autre 3 %

### Procédés relevés dans les 12 scripts les plus vus

- **💀 Je m’y attendais pas…** (12,168,793 vues) : Ouvre en désignant le joueur par sa nationalité ('ce joueur africain') sans le nommer ; Enchaîne les 'Et pour cause' pour passer de l'effet à l'explication ; Annonce le renversement avant de le montrer ('un plan qui allait miraculeusement fonctionner') ; Raconte tout au futur proche ('il va crier', 'il va rapidement en profiter') ; Relance après le premier but avec 'et ça s'arrête pas là' pour faire monter vers le second
  - pourquoi ça marche : Une situation absurde et visible dès la première image, puis une explication qui se révèle seulement après la colère de l'entraîneur.
- **La dernière… 💀** (10,832,264 vues) : Chiffre annoncé dès la première phrase ('trois vraies techniques') qui sert de squelette ; Ordre croissant annoncé à voix haute ('ça va être de pire en pire') ; Chaque technique ouvre par 'Ça c'est loin d'être la pire' / 'rien comparé à la troisième' pour relancer ; S'adresse au spectateur ('je suis sûr que tu la connais pas') ; Pose la question du spectateur lui-même ('c'est quoi le rapport avec la triche ?') avant de répondre
  - pourquoi ça marche : Le format liste classée avec la pire en dernier tient jusqu'à la fin, et la troisième est prouvée par une vidéo en direct.
- **🤯 Rien ne se passe comme prévu…** (6,880,387 vues) : Deux 'Sauf que' successifs qui annulent chaque attente posée avant ; Annonce 'une bonne raison' sans la donner ; Explique d'abord le dispositif (lumières) puis son défaut, avant de raconter la course ; Montre le public qui doute ('elle avait perdu la tête') avant la preuve ; Chiffre final en contraste (14 secondes d'avance) pour clore
  - pourquoi ça marche : Une anomalie visuelle (courir au-delà des lumières) est expliquée par un défaut technique du dispositif, puis retournée en coup de génie.
- **💀 Je m’y attendais pas du tout…** (6,452,612 vues) : Hook sur l'âge du joueur ('18 ans') et sur un 'détail très étrange' à repérer dans les images ; Chaîne de 'Alors... va...' pour faire avancer la dispute par petites étapes ; Utilise 'Sauf qu'étrangement' pour installer le conflit avec le gardien ; Annonce l'issue sans la dire ('sans s'imaginer que c'était la meilleure décision de sa vie') ; Garde la résolution (l'arrêt du tir) pour la dernière phrase
  - pourquoi ça marche : Un petit conflit visible (herbe arrachée, gardien têtu) se développe pas à pas jusqu'à un renversement annoncé à l'avance.
- **Le geste le plus intelligent de l’histoire.** (5,980,983 vues) : Le geste est décrit seul au début, sans en donner la raison ; Écarte une fausse explication ('pas vraiment fait ça pour lui voler sa victoire') ; Souligne que seul un patineur d'élite pouvait le voir ; Décrit le danger au ralenti avec des verbes d'action ('se coince', 's'enfonce de plus en plus') ; Mesure le risque avec 'une fraction de seconde de potentiellement se casser la cheville'
  - pourquoi ça marche : Un geste qui passe pour de la violence est remplacé par un acte de protection, expliqué au ralenti.
- **🧐 Une course très étrange au JO…** (5,339,856 vues) : Hook centré sur un détail visuel précis ('en regardant ses jambes') ; Pose le soupçon du public avant de le renverser avec le handicap invisible ; Nomme les athlètes à la deuxième phrase seulement ('Carisma et Vitiran') ; Enchaîne 'Sauf que le problème c'est que' puis 'Mais même si beaucoup trouvaient ça injuste' pour alterner objection et réponse ; Chute en antithèse 'si pour les deux Italiennes... pour Carisma...'
  - pourquoi ça marche : Un soupçon d'injustice est installé puis nuancé par la règle et le handicap, et la chute oppose deux destins.
- **🤯 Elle s’endort en pleine finale des JO…** (5,224,889 vues) : Mise en contraste de la norme (échauffement) et de l'action étrange (dormir) ; 'Tout était calculé' annonce que le geste absurde est un plan ; Explique la règle du concours avant de montrer la stratégie ; Chute qui reprend les éléments du hook : 'championne olympique après une sieste et seulement deux sauts' ; Présente la rivale par son statut (championne en titre, ultra favorite) pour monter l'enjeu
  - pourquoi ça marche : Une action absurde dans un moment très sérieux, la règle du concours rend le plan logique, et la chute reprend le mot 'sieste'.
- **💀 Je m’y attendais pas…** (3,900,449 vues) : Pose d'abord l'étrangeté (elle pleure, elle pointe un enfant) sans l'expliquer ; Fait croire à une excuse puis renverse avec l'explication ('l'enfant n'était pas innocent') ; Annonce 'la plus grosse erreur de sa carrière' pour l'arbitre avant de la montrer ; Revient sur la balle de match pour rejouer la scène une seconde fois en pleine tension ; Chute sur la perte du match 'qu'elle préparait depuis plusieurs années'
  - pourquoi ça marche : Le public et l'arbitre se trompent pendant que le spectateur attend la preuve, qui arrive à la balle de match.
- **😳 Il a découvert son secret…** (3,870,873 vues) : désigne le héros par sa tenue (« ce coureur en rouge ») au lieu de son nom ; annonce un bénéfice caché (« la meilleure chose qui pouvait lui arriver ») avant d'expliquer ; raconte tout au futur proche (« il va partir », « va tenter », « va réaliser ») ; enchaîne les « Sauf que » pour relancer l'intrigue à chaque palier ; garde le secret technique pour le milieu, après deux échecs de Gatlin
  - pourquoi ça marche : La défaite devient une quête avec un secret à découvrir, et chaque « Sauf que » relance la tension jusqu'à une chute émotionnelle visuelle.
- **💀 Le scandale…** (3,740,018 vues) : désigne la championne par « cette africaine » sans la nommer ; annonce « quelque chose de très étrange en revoyant les images » pour pousser à rewatch ; empile les bizarreries en gradation (« le pire », « encore plus bizarre ») ; pose la question « s'il s'agissait réellement de femmes » avant la réponse médicale ; rouvre un mystère mineur (shorts) après la résolution principale
  - pourquoi ça marche : Les anomalies visibles s'accumulent avant la réponse scientifique, et un dernier mystère garde l'attention jusqu'à la fin.
- **🧠 C’était une idée de génie…** (2,871,075 vues) : décrit l'action absurde sans expliquer, puis répète « il s'avère que » pour annoncer le retournement ; revient en arrière (« si on revient à la fin du 3e quart ») pour poser la preuve ; annonce « une règle très souvent oubliée » avant de l'énoncer ; utilise « Sauf que » deux fois pour casser chaque certitude ; boucle sur la scène du hook en toute fin
  - pourquoi ça marche : Le geste absurde est montré d'abord, la raison arrive après un retour en arrière, et la fin reboucle sur l'image du hook.
- **🥺 C’est incroyable…** (2,810,245 vues) : ordonne au spectateur de regarder la photo (« Regarde bien ») avant toute explication ; cache le nom de l'héroïne dans le hook, révélé à la phrase suivante ; pose la question à voix haute (« Donc qu'est-ce qui s'est passé ? ») ; empile des « Sauf que » en cascade pour enchaîner les obstacles ; utilise « ce qu'il savait pas » pour annoncer l'intervention du mari
  - pourquoi ça marche : Une image choc est suivie d'une histoire à rebondissements qui se termine sur un fait historique clair.

## TopFoot, shorts d'1 min (57 scripts annotés)

### Hooks, du plus vu au moins vu (vues médianes)

| Type | Nb | Vues médianes | Exemple le plus vu (1re phrase) |
|---|---|---|---|
| fait_chiffre | 5 | 944,600 | « Il est resté debout pendant 438 minutes avant de définitivement tomber. » |
| tu_tes_deja_demande | 4 | 896,150 | « Tu crois voir un dégagement raté de Saphonoff ? » |
| citation_reponse | 8 | 755,750 | « C'est un mélange de joueurs, de toutes les émotions qu'on appartient ensemble. » |
| opinion_forte | 12 | 699,400 | « Je pense qu'on va assister à la Coupe du Monde la plus honteuse de ces dernières années. » |
| autre | 16 | 642,650 | « Et si je vous disais que Mbappé est en train de reproduire exactement la carrière de Cristiano Ronaldo au Real Madrid. » |
| detail_etrange_regarde | 7 | 556,900 | « Ça, c'est la photo que Ilia Zabarni a publié sur Instagram après la supercoupe d'Europe. » |
| pourquoi_question | 4 | 548,750 | « Quelle est la probabilité pour que deux enfants du même quartier se retrouvent en demi-finale de l'île des champions ? » |
| liste_techniques | 1 | 476,700 | « Samuel Patti, Naël, violence policière, les paris sportifs, les migrants, à chaque fois me bâpé aurait pu se taire, il ne l'a jamais fait. » |

Héros d'abord décrit sans son nom : **17 scripts sur 57** (30 %).

### Suites de temps les plus fréquentes

- (3×, 549,900 vues méd.) hook → mise en place → preuve → mise en place → dénouement → cta
- (3×, 559,500 vues méd.) hook → mise en place → preuve → retournement → explication → mise en place → dénouement → cta
- (2×, 1,426,150 vues méd.) hook → mise en place → preuve → dénouement
- (2×, 1,006,050 vues méd.) hook → mise en place → retournement → dénouement → cta
- (2×, 1,073,650 vues méd.) hook → mise en place → preuve → mise en place → dénouement
- (2×, 593,450 vues méd.) hook → mise en place → preuve → mise en place → explication → mise en place → dénouement → cta
- (1×, 3,800,000 vues méd.) hook → mise en place → preuve → mise en place → retournement → dénouement → cta
- (1×, 2,600,000 vues méd.) hook → mise en place → preuve → explication → dénouement → cta

### Comment chaque temps commence (2 premiers mots les plus fréquents)

- **escalade** (80) : « et ce » 4 %, « et le » 4 %, « il y » 4 %, « et même » 4 %, « parce que » 2 %
- **hook** (57) : « et si » 9 %, « vous avez » 4 %, « je pense » 2 %, « tu crois » 2 %, « c'est un » 2 %
- **preuve_clip** (51) : « et même » 4 %, « prenons l'irak » 2 %, « parce qu'hier » 2 %, « ma famille » 2 %, « mbappé arrive » 2 %
- **contexte** (49) : « parce que » 20 %, « on est » 8 %, « hier soir » 6 %, « parce qu'avant » 4 %, « cristiano ronaldo » 4 %
- **explication** (49) : « parce que » 27 %, « et c'est » 8 %, « sauf que » 6 %, « et ce » 4 %, « donc l'idée » 2 %
- **chute** (48) : « parce que » 8 %, « et c'est » 6 %, « et à » 4 %, « donc saphonov » 2 %, « alors là » 2 %
- **cta** (45) : « et si » 93 %, « est-ce que » 2 %, « pour vous » 2 %, « alors demain » 2 %
- **payoff** (36) : « et là » 6 %, « le vainqueur » 6 %, « et quelques » 6 %, « et c'est » 6 %, « parce qu'une » 3 %
- **retournement** (34) : « sauf que » 15 %, « mais le » 12 %, « et c'est » 9 %, « mais ce » 6 %, « pendant ce » 6 %
- **mystere** (30) : « et ce » 7 %, « la première » 3 %, « qu'est-ce que » 3 %, « il passe » 3 %, « et surtout » 3 %
- **opinion** (14) : « et je » 7 %, « madame je » 7 %, « vraiment déjà » 7 %, « et cette » 7 %, « oui des » 7 %

### Chutes

morale_antithese 54 %, cta 18 %, fait_final 18 %, question 4 %, autre 4 %, coupe_net 4 %

### Procédés relevés dans les 12 scripts les plus vus

- **La Coupe du Monde la plus honteuse ?** (3,800,000 vues) : ouvre sur une opinion à la première personne au lieu d'un mystère ; personnifie l'adversaire (« leur premier adversaire, Donald Trump ») ; empile des cas concrets chiffrés (10 heures, 7 heures) avant la thèse ; qualifie l'Irak d'« exemple le plus absurde » pour monter en gravité ; reformule la thèse en antithèse finale (gagner sur le terrain / gagner le droit d'entrer)
  - pourquoi ça marche : Opinion nette suivie de faits précis et vérifiables qui montent en absurdité, puis une antithèse mémorable qui se partage.
- **Les dégagements en touche de Safonov…** (2,600,000 vues) : Adresse directe en « tu » dans le hook ; Fausse lecture (erreur) corrigée immédiatement par « en réalité » ; Répétition « encore, encore, et encore » pour appuyer le motif ; Chiffre précis 7 sur 10 avec côté nommé ; Chaîne de « Parce que » / « Donc » comme raisonnement tactique ; Résumé en « Autrement dit » pour simplifier l'explication ; Enumération « D'abord… Ensuite » pour les deux bénéfices
  - pourquoi ça marche : Le hook retourne ce que le spectateur croit avoir vu, et l'explication tactique est livrée en enchaînement causal simple avec un chiffre à l'appui.
- **Marquinhos… les larmes du capitaine 🥹** (2,100,000 vues) : extrait d'interview brute, sans voix off visible dans la transcription ; commence sans présentation, sur le sentiment ; énumère des noms de légendes qui parlent aux fans ; rappelle l'attente de 12 ans pour donner du poids au titre ; finit sur « Il est à nous, on la ramène à la maison »
  - pourquoi ça marche : Les mots du joueur portent l'émotion directement, avec des noms connus et le poids de 12 ans d'attente.
- **Doku, vas-y avec plaisir !** (1,900,000 vues) : Ouvre directement sur la citation de la chroniqueuse, sans présentation. ; Adresse « Madame » deux fois, au début et à la fin, ce qui fait une boucle et personnalise le propos. ; Contredit la phrase avec « Vraiment ? Déjà, Doku ne parle pas de… » puis redéfinit le sujet. ; Élargit un cas précis à un propos général sur le football (« machines », « robot »). ; Concède l'objection (« Oui, des centaines de joueurs rêveraient… ») avant la réfutation. ; Termine par une antithèse symétrique : « quelques jours » contre « à vie ».
  - pourquoi ça marche : Une phrase qui indigne ouvre la vidéo, et la réponse suit un plan clair qui donne raison au spectateur avec une chute à retenir.
- **Mbappé et CR7 ? Meilleure histoire** (1,600,000 vues) : Répète la même structure de phrase pour Ronaldo puis pour Mbappé (« Premier match de X… Premier match de Y… ») pour que la coïncidence se lise toute seule ; Donne un chiffre exact dès le début (86 buts) et le fait revenir ; Insère des relances de progression: « Mais ce n'est que le début », « Et maintenant, ça devient complètement fou » ; Termine par une phrase conditionnelle laissée ouverte qui projette sur l'avenir ; Ne commente jamais: laisse les chiffres faire la démonstration, sans adjectifs
  - pourquoi ça marche : Chaque paire de phrases miroir donne une petite récompense, et l'auditeur attend la prochaine coïncidence jusqu'à la fin.
- **L’histoire forte de Michel Kuala Mboladinga dit Lumumba !** (1,400,000 vues) : Ouvre sur un chiffre précis (438 minutes) suivi de « avant de définitivement tomber » ; Décrit le geste en détail avant d'en donner la signification ; Annonce « ce geste n'avait rien d'anodin » pour déclencher l'explication ; Fait entrer une citation d'un témoin comme preuve de popularité ; Garde l'anecdote d'Amoura qui imite le geste sans le savoir comme dernière révélation
  - pourquoi ça marche : Le chiffre intrigue, puis la signification du geste donne une émotion plus forte que le simple fait d'être resté debout.
- **Guendouzi a créé une guerre !** (1,400,000 vues) : Commence par « Tout commence une semaine plus tôt » pour raconter dans l'ordre chronologique ; Nomme l'origine (le geste associé à Marseille) avant l'explosion du match retour ; Utilise « Et là, » deux fois pour marquer chaque bascule ; Résume l'ensemble en une formule: « un match banal qui s'est transformé en véritable guerre » ; Enchaîne sans explication ni opinion, uniquement l'action
  - pourquoi ça marche : Le récit chronologique donne un déclencheur clair et une escalade qui monte jusqu'à la bagarre générale.
- **Le ballon d’or le plus évident ?😮‍💨** (1,300,000 vues) : Ouvre sur une citation d'invité qui énumère les titres sans nommer le joueur ; Enchaîne les avis concordants de plusieurs voix pour installer une évidence ; Ajoute une phrase tardive du type « tout le monde voterait la même chose » pour verrouiller le consensus ; Laisse une interruption (« Non, non, non ») créer un doute avant la chute ; Termine par une seule phrase qui donne le nom du vainqueur avec « pourtant »
  - pourquoi ça marche : La liste de titres et le « je comprends plus rien » donnent envie de vérifier si l'évidence s'est confirmée, et la chute tient en une phrase factuelle.
- **Yassine Gessime, d’oublié à « briller » @Gessime-yassine** (1,200,000 vues) : Ouvre par une opinion générale (« mauvaise stratégie de détection ») avant de nommer le joueur ; Utilise « Parce que si aujourd'hui… pratiquement tous les clubs l'ont refusé » pour poser le contraste ; Déroule la biographie en ordre chronologique avec des marqueurs temporels (« À 18 ans », « quelques mois plus tard ») ; Cite les raisons exactes des refus (« bon joueur, mais trop frêle ; bon dribbleur mais pas assez de passes ») ; Montre la rupture avec « Et là, tout s'accélère » puis les chiffres (60 matchs, 7 millions) ; Finit en généralisant par des exemples de joueurs refusés pour leur physique avant le CTA
  - pourquoi ça marche : La thèse est posée avant l'histoire donc chaque étape devient la preuve de l'opinion, et la chute rapproche le joueur de stars connues.
- **Les malaises inquiétant de Jamal Musiala…** (1,200,000 vues) : Ouvre par un titre chiffré, deux faits courts et graves ; Donne la chronologie jour par jour (samedi puis aujourd'hui) avec des phrases courtes ; Corrige l'hypothèse du club (« chaleur et déshydratation ») par le deuxième malaise introduit par « Sauf que » ; Répète la formule « c'est inquiétant » pour appuyer l'enjeu sans adjectif d'émotion supplémentaire ; Retarde le diagnostic avec « ce qu'il se passe » puis le traduit en image (« son cerveau se met sur pause ») ; Ferme sur une question ouverte sur la suite de sa carrière
  - pourquoi ça marche : Le chiffre dans la première phrase suffit à retenir l'attention et la révélation du diagnostic arrive tard, ce qui fait attendre la suite.
- **L’Irlande a joué contre Israël… pour la Palestine ! 🇵🇸** (1,200,000 vues) : Ouvre par deux phrases courtes qui s'opposent (« ne voulait pas… Finalement, elle l'a fait pour… ») ; Annonce « un message » avant le match puis le montre en trois gestes concrets (brassard, tête baissée, refus de poignée de main) ; Résume la décision en une phrase simple : « L'Irlande va jouer, mais avec un objectif » ; Accélère avec un repère de temps précis (« 16 minutes », 2-0) avant la scène forte ; Annonce « probablement l'image la plus forte de la soirée » puis décrit le geste étape par étape ; Ferme sur une phrase en deux temps (jouer / ne pas oublier) puis le CTA
  - pourquoi ça marche : Le paradoxe de l'ouverture est résolu par des gestes visibles et la scène du brassard donne une image précise à retenir.
- **Toutes mes condoléances à Didier Deschamps** (1,000,000 vues) : Part d'un fait d'actualité (absence de Deschamps) pour amener un sujet secondaire, Stéphan ; Annonce « un homme que vous avez vu pendant plus de dix ans sans jamais vraiment comprendre son importance » avant de le nommer ; Appuie le portrait sur deux cas précis et datés (2018 contre l'Argentine et Messi, coup de pied arrêté contre l'Uruguay avec Griezmann) ; Résume en une formule qui fait office de thèse (« le monde de Guy Stéphan, les détails ») ; Reprend la formule d'ouverture « homme de l'ombre » en dernière phrase
  - pourquoi ça marche : Il accroche sur une actu forte et transforme un personnage de second plan en sujet, avec deux preuves tactiques concrètes.

