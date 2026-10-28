# -*- coding: utf-8 -*-
"""
monter_short.py — Monte un short EXACTEMENT dans le style Max Parra, dans CapCut.

Style reproduit (analysé sur 15 de ses vidéos) :
  - ENCHAÎNEMENT RAPIDE de plusieurs clips : une coupe toutes les ~1,3 s (~15 plans / 20 s)
  - une seule voix off continue par-dessus
  - clips en 9:16 plein cadre (cover) + zoom léger, MUETS
  - sous-titres BLANCS, petits, minuscules, CENTRÉS au milieu, contour + ombre noire
  - 2-3 mots à la fois (style légendes auto)
  - PAS de texte d'accroche incrusté (le titre vit dans le titre YouTube)

Usage :
    python monter_short.py shorts/djokovic

Dossier du projet :
    clips/          -> mets ici TES ~15 clips (mp4/mov/...). Ils seront enchaînés dans l'ordre.
                       (à défaut : un seul clip.mp4 à la racine, qui sera redécoupé en jump-cuts)
    voix.mp3        -> ta voix off (mp3/wav/m4a)
    config.json     -> { "cut_seconds": 1.3, "zoom": 1.1, "titre": "..." }
    soustitres.srt  (optionnel)  -> sous-titres timés (le mieux)
    texte.txt       (optionnel)  -> à défaut, découpé auto en groupes de 2-3 mots

Après : ouvre CapCut, le projet est déjà monté.
"""

import os
import re
import sys
import json
import glob

import pyJianYingDraft as d
from pyJianYingDraft import (
    TrackType, VideoSegment, AudioSegment, TextSegment, TextStyle,
    ClipSettings, TextBorder, TextShadow, VideoMaterial, AudioMaterial, Timerange,
)

# ----------------------------------------------------------------------------- réglages globaux
# Dossier des brouillons CapCut (Windows ou macOS)
_DRAFT_DIRS = [
    os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft"),
    os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft"),
]
DRAFT_DIR = next((p for p in _DRAFT_DIRS if os.path.isdir(p)), _DRAFT_DIRS[0])
CANVAS_W, CANVAS_H = 1080, 1920          # 9:16
FPS = 30

CUT_SECONDS = 1.3                        # durée par défaut d'un plan (cadence Max Parra)
ZOOM = 1.1                               # étirement LÉGER du clip de devant (qualité conservée)
BLUR = 0.08                              # intensité du fond flou (compo "fond flou" Max Parra)

# sous-titres style Max Parra
BLANC = (1.0, 1.0, 1.0)
TAILLE_SOUS_TITRE = 7.0
SOUS_TITRE_Y = -0.15                     # ~centre, légèrement en dessous (0 = centre exact)
SOUS_TITRE_MAX_CHARS = 14               # ~2-3 mots par sous-titre
BORDURE = TextBorder(color=(0, 0, 0), width=15.0)
OMBRE = TextShadow(color=(0, 0, 0), alpha=0.9, diffuse=15.0, distance=6.0, angle=-45.0)

VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv", ".webm")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".aac", ".flac")


def ajouter_piste(script, track_type, nom):
    """Crée une piste. pyJianYingDraft a renommé add_track() en append_track(TrackSpec)
    selon les versions : on gère les deux."""
    if hasattr(script, "add_track"):
        return script.add_track(track_type, nom)
    from pyJianYingDraft import TrackSpec
    return script.append_track(TrackSpec(track_type=track_type, name=nom))


def lister(dossier, exts):
    return [os.path.join(dossier, f) for f in sorted(os.listdir(dossier))
            if os.path.splitext(f)[1].lower() in exts] if os.path.isdir(dossier) else []


def trouver(dossier, exts):
    f = lister(dossier, exts)
    return f[0] if f else None


def parse_srt(path):
    with open(path, encoding="utf-8-sig") as fh:
        blocs = re.split(r"\n\s*\n", fh.read().strip())
    out = []
    for b in blocs:
        m = re.search(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", b)
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        deb = ((h1*3600 + m1*60 + s1)*1000 + ms1) * 1000
        fin = ((h2*3600 + m2*60 + s2)*1000 + ms2) * 1000
        lignes = b.split("\n")
        txt = " ".join(lignes[2:]).strip() or " ".join(lignes[1:]).strip()
        out.append((deb, fin, txt))
    return out


def decouper_texte(texte, total_us, max_chars=SOUS_TITRE_MAX_CHARS):
    """Découpe en petits groupes de 2-3 mots et répartit le temps proportionnellement
    (placeholder rapide ; les Légendes auto de CapCut restent plus précises)."""
    mots = texte.split()
    lignes, cur = [], ""
    for w in mots:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lignes.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lignes.append(cur)
    total = sum(len(l) for l in lignes) or 1
    out, t = [], 0
    for l in lignes:
        dur = int(total_us * len(l) / total)
        out.append((t, t + dur, l)); t += dur
    return out


def cover_scale(w, h):
    canvas_ar = CANVAS_W / CANVAS_H
    ar = w / h
    return (ar / canvas_ar) if ar > canvas_ar else (canvas_ar / ar)


# CapCut nomme son fichier de projet draft_content.json sous Windows
# et draft_info.json sous macOS.
DRAFT_FILES = ("draft_content.json", "draft_info.json")


def patch_meta_capcut(nom, duree_us):
    """pyJianYingDraft laisse draft_meta_info.json à moitié vide (draft_fold_path,
    draft_root_path, draft_name, tm_duration…). Sous Windows CapCut s'en accommode ;
    sous macOS il ne retrouve pas les médias du projet, charge une timeline VIDE et
    l'enregistre par-dessus — le montage est perdu. On remplit donc ces champs."""
    import time
    dossier = os.path.join(DRAFT_DIR, nom)
    fp = os.path.join(dossier, "draft_meta_info.json")
    if not os.path.exists(fp):
        return False
    meta = json.load(open(fp, encoding="utf-8"))
    now = int(time.time() * 1_000_000)
    meta.update({
        "draft_fold_path": dossier,
        "draft_root_path": DRAFT_DIR,
        "draft_name": nom,
        "draft_cover": "draft_cover.jpg",
        "draft_new_version": "155.0.0",
        "tm_duration": int(duree_us),
        "tm_draft_create": meta.get("tm_draft_create") or now,
        "tm_draft_modified": now,
    })
    # champs attendus par CapCut macOS et absents de la sortie pyJianYingDraft
    meta.setdefault("draft_timeline_materials_size_", 0)
    for cle, val in (("draft_cloud_package_type", ""), ("cloud_draft_sync", False),
                     ("draft_is_ae_produce", False), ("draft_is_cloud_temp_draft", False),
                     ("draft_is_web_article_video", False), ("draft_need_rename_folder", False),
                     ("cloud_draft_cover", False), ("draft_web_article_video_enter_from", ""),
                     ("tm_draft_cloud_entry_id", 0), ("tm_draft_cloud_parent_entry_id", 0),
                     ("tm_draft_cloud_space_id", 0), ("tm_draft_cloud_user_id", 0)):
        meta.setdefault(cle, val)
    json.dump(meta, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
    return True


def patch_pour_capcut(nom):
    """pyJianYingDraft écrit une signature JianYing ('lv') que CapCut refuse
    ('unusual path'). On réinjecte la signature CapCut ('cc') copiée depuis un
    vrai projet existant de la machine, et on écrit le projet sous les deux
    noms de fichier possibles (Windows / macOS)."""
    dossier = os.path.join(DRAFT_DIR, nom)
    src = next((os.path.join(dossier, f) for f in DRAFT_FILES
                if os.path.exists(os.path.join(dossier, f))), None)
    if not src:
        print("     [!] patch CapCut: projet généré introuvable.")
        return False

    ref = None
    for dd in sorted(glob.glob(os.path.join(DRAFT_DIR, "*")), key=os.path.getmtime, reverse=True):
        if os.path.basename(dd) == nom:
            continue
        for f in DRAFT_FILES:
            fp = os.path.join(dd, f)
            if not os.path.exists(fp):
                continue
            try:
                cand = json.load(open(fp, encoding="utf-8"))
            except Exception:
                continue
            if cand.get("platform", {}).get("app_source") == "cc":
                ref = cand
                break
        if ref:
            break
    if not ref:
        print("     [!] patch CapCut: aucun projet 'cc' de référence trouvé.")
        return False

    dc = json.load(open(src, encoding="utf-8"))
    dc["draft_type"] = "video"
    dc["platform"] = ref["platform"]
    dc["last_modified_platform"] = ref["last_modified_platform"]
    for cle in ("new_version", "version"):
        if ref.get(cle):
            dc[cle] = ref[cle]
    # CapCut lit draft_info.json (mac) ou draft_content.json (windows) : on écrit les deux
    for f in DRAFT_FILES:
        json.dump(dc, open(os.path.join(dossier, f), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"     [+] signature CapCut appliquée (app_version {ref['platform'].get('app_version')}).")
    return True


def main(project_dir):
    project_dir = os.path.abspath(project_dir)
    nom = os.path.basename(project_dir.rstrip("\\/"))
    cfg_path = os.path.join(project_dir, "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.exists(cfg_path) else {}

    cut_us = int(float(cfg.get("cut_seconds", CUT_SECONDS)) * 1_000_000)
    zoom = float(cfg.get("zoom", ZOOM))

    # ---- clips : dossier clips/ prioritaire, sinon clip.* à la racine
    clip_paths = lister(os.path.join(project_dir, "clips"), VIDEO_EXT)
    if not clip_paths:
        c = trouver(project_dir, VIDEO_EXT)
        clip_paths = [c] if c else []
    if not clip_paths:
        sys.exit(f"[X] Aucun clip (mets-les dans {project_dir}\\clips\\)")

    voix_path = trouver(project_dir, AUDIO_EXT)
    if not voix_path:
        sys.exit(f"[X] Aucune voix off (audio) dans {project_dir}")

    mats = [VideoMaterial(p) for p in clip_paths]
    amat = AudioMaterial(voix_path)
    vo_dur = amat.duration

    # ---- projet
    folder = d.DraftFolder(DRAFT_DIR)
    script = folder.create_draft(nom, CANVAS_W, CANVAS_H, fps=FPS, allow_replace=True)
    ajouter_piste(script, TrackType.video, "video")
    ajouter_piste(script, TrackType.audio, "vo")

    # ---- enchaînement rapide des clips sous la voix off
    cursor = [0] * len(mats)         # position de lecture dans chaque clip
    t = 0
    i = 0
    n_plans = 0
    while t < vo_dur:
        mat = mats[i % len(mats)]
        seg_dur = min(cut_us, vo_dur - t)
        start = cursor[i % len(mats)]
        if start + seg_dur > mat.duration:        # on a épuisé ce clip -> on reboucle au début
            start = 0
        if seg_dur > mat.duration:                # clip plus court que la tranche
            seg_dur = mat.duration
        # clip de devant : étirement léger (qualité conservée) + fond flou auto par-derrière
        seg = VideoSegment(
            mat,
            Timerange(t, seg_dur),
            source_timerange=Timerange(start, seg_dur),
            volume=0.0,
            clip_settings=ClipSettings(scale_x=zoom, scale_y=zoom),
        )
        seg.add_background_filling("blur", blur=BLUR)
        script.add_segment(seg, "video")
        cursor[i % len(mats)] = start + seg_dur
        t += seg_dur
        i += 1
        n_plans += 1

    # ---- voix off
    script.add_segment(AudioSegment(amat, Timerange(0, vo_dur), volume=1.0), "vo")

    script.save()
    patch_pour_capcut(nom)
    print(f"[OK] '{nom}' monté dans CapCut.")
    print(f"     {vo_dur/1e6:.1f}s | {len(mats)} clip(s) source -> {n_plans} plans "
          f"(~{vo_dur/1e6/max(n_plans,1):.2f}s/plan)")
    print("     (sous-titres : à faire toi-même dans CapCut)")
    print("     -> Ouvre CapCut, le projet est dans tes brouillons.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage : python monter_short.py <dossier_du_projet>")
    main(sys.argv[1])
