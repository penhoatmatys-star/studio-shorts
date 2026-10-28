# 🎬 Montage auto des shorts "Niche Trap" dans CapCut

Génère un projet CapCut **déjà monté** (clip 9:16 muet + ta voix off + accroche jaune + sous-titres) en une commande. Tu n'as plus qu'à ouvrir CapCut, ajuster 2-3 détails et exporter.

## Une fois (déjà fait sur ce PC)
```
python -m pip install pyJianYingDraft
```

## Pour chaque vidéo

1. Crée un dossier dans `shorts/` (copie `shorts/_MODELE`), nomme-le comme le sujet, ex. `shorts/djokovic`.
2. Mets dedans :
   - **`clip.mp4`** — le clip source (téléchargé). Accepté : mp4, mov, mkv, webm.
   - **`voix.mp3`** — ta voix off enregistrée. Accepté : mp3, wav, m4a.
   - **`config.json`** — voir ci-dessous.
   - *(optionnel)* **`soustitres.srt`** — sous-titres timés (le plus propre).
   - *(optionnel)* **`texte.txt`** — à défaut de .srt : le texte est découpé et réparti auto sur la durée de la VO (placeholder à recaler dans CapCut).
3. Lance :
   ```
   python monter_short.py shorts/djokovic
   ```
4. Ouvre **CapCut** → le projet `djokovic` est dans tes brouillons, déjà monté.

## config.json
```json
{
  "hook": "Invaincu... puis DISQUALIFIÉ 💀",   // texte d'accroche en haut
  "titre": "djokovic",                          // info (le nom du dossier sert de nom de projet)
  "clip_start_s": 0,                            // démarrer le clip à X secondes de la source
  "zoom": 1.0,                                  // 1.0 = plein cadre ; 1.2 = zoom +20%
  "hook_seconds": 3                             // durée d'affichage de l'accroche
}
```

## Ce que le script fait (gabarit)
- Clip **recadré 9:16 plein cadre** (cover), **MUET**, calé sur la durée de la voix off.
- **Voix off** posée sur la piste audio.
- **Accroche** en haut : gros, gras, jaune (0 → `hook_seconds`).
- **Sous-titres** en bas : gros, gras, jaune (depuis le .srt ou le texte.txt).

## Sous-titres : la meilleure méthode
Comme c'est **ta voix**, le plus précis :
1. Laisse le script poser clip + VO + accroche.
2. Dans CapCut : **Texte → Légendes automatiques** (FR) → transcrit ta voix en 1 clic.
3. Applique ton style jaune une fois, enregistre-le comme préréglage.

Le `texte.txt` sert juste de **placeholder rapide** si tu veux des sous-titres déjà posés (timing approximatif à ajuster).

## Réglages de style
Tout est en haut de `monter_short.py` : couleur jaune, tailles, positions verticales du hook et des sous-titres. Modifie une fois, c'est appliqué à tous les shorts.
```
