# Studio Shorts (Windows) — mode d'emploi

Interface qui fait la veille actu sport, écrit des scripts de Shorts d'1 min, puis monte
la vidéo (voix off, clips, photos, musique, sous-titres) directement dans CapCut.

## Ce qu'il te faut (comptes à toi, rien n'est partagé)
1. **Compte Claude payant (Pro/Max)** : c'est l'IA qui cherche les clips et monte. Une
   production consomme pas mal de quota. Claude Code est installé par l'installeur.
2. **Voix off ElevenLabs** : déjà configurée (clé et voix partagées dans `_voix_clone/elevenlabs.json`) — rien à faire.
3. **CapCut** (version Windows, depuis capcut.com) ouvert au moins une fois avec **un projet
   créé et enregistré** (n'importe lequel) : le robot en copie la signature pour que CapCut
   accepte ses montages.
4. Windows 10/11 avec **winget** (déjà présent sur Windows 11).

## Installation (une seule fois)
1. Dézippe le dossier où tu veux (ex. `C:\Studio_Shorts`, évite les chemins très longs).
2. Double-clic sur **« 1 - Installer.bat »** (si SmartScreen bloque : « Informations
   complémentaires » → « Exécuter quand même »). Attends la fin (5-10 min).
3. Ouvre un **nouveau** terminal (PowerShell) et tape `claude auth login`, connecte-toi.

## Utilisation
- Double-clic sur **« Studio Shorts.bat »** → le studio s'ouvre sur http://localhost:8765.
  Une fenêtre réduite reste dans la barre des tâches : c'est le serveur, ne la ferme pas.
- Demande la veille, clique un sujet, choisis un script (ou colle le tien via « ✍️ Mon script »),
  puis « Lancer la production ». Suis le journal en direct ; le chat sert aux retouches.
- Le montage s'ouvre dans CapCut. **Ne touche pas à CapCut pendant qu'un montage se fait**
  (il est fermé/rouvert automatiquement).
- Termine avec la checklist de `STYLE_MONTAGE.md` (flèche, légendes, etc.).

## Bon à savoir
- Les règles de montage (`CLAUDE.md`, `STYLE_MONTAGE.md`, `scripts_modeles.md`) sont le style
  de Matys : modifie-les pour adapter le rendu à ta chaîne. L'IA t'appelle parfois « Matys ».
- Les vidéos sont créées dans `shorts\<projet>\` ; les brouillons CapCut dans
  `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`.
- Cette version Windows n'a pas pu être testée sur un vrai PC par son auteur : si une étape
  échoue, envoie une capture du message d'erreur.
