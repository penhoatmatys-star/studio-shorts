# -*- coding: utf-8 -*-
"""
monter_edl.py — Monte un short à partir d'une LISTE DE DÉCOUPE (EDL) précise.

Au lieu d'enchaîner des clips entiers, on pose des extraits EXACTS de vidéos
sources longues (fichier, début, fin), dans l'ordre du récit, sous la voix off.
C'est ce qui permet le "auto-derush" : découper une vidéo longue en rapport
avec le script.

Dossier projet :
    edl.json      -> { "zoom":1.1, "beats":[ ["chemin/source.mp4", debut_s, fin_s], ... ] }
    voix.mp3      -> ta voix off (mp3/wav/m4a)
    texte.txt     (optionnel) -> sous-titres auto (2-3 mots)  OU  soustitres.srt

Usage :
    python monter_edl.py shorts/djokovic
"""

import os, sys, json
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import pyJianYingDraft as d
from pyJianYingDraft import (
    TrackType, VideoSegment, AudioSegment, StickerSegment, ClipSettings,
    VideoMaterial, AudioMaterial, Timerange,
)
from monter_short import (
    DRAFT_DIR, CANVAS_W, CANVAS_H, FPS, AUDIO_EXT, BLUR, trouver, patch_pour_capcut,
    cover_scale, ajouter_piste, patch_meta_capcut,
)

ANIM_ZOOM = next((m for m in d.IntroType if m.name == "轻微放大"), list(d.IntroType)[33])  # léger zoom-avant
ANIM_DUR = 500_000     # durée du punch zoom (0.5s) au début de chaque clip

# --- Style Matys, mesuré sur ses brouillons CapCut (voir STYLE_MONTAGE.md) ---
ZOOM_169 = 1.8         # 16:9 agrandi à ~181 % sur le fond flou (exemple vidéo de Matys, 2026-10-08)
HOOK_S = 6.5           # la musique change de volume à ~6.5 s (fin du hook)
MUSIQUE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_assets", "musique")
MUSIQUES = {           # nom: (fichier, départ dans le morceau s, volume hook, volume suite)
    "tiki":      ("tiki_tiki_slowed.m4a", 0.0, 0.50, 0.27),      # shorts ~15-30 s
    "skyfall":   ("skyfall_karaoke.m4a", 1.8, 0.40, 0.50),       # shorts ~60 s
    "cornfield": ("cornfield_chase.m4a", 31.3, 0.60, 0.60),      # partie émotion / payoff
    "radiohead": ("radiohead_everything.m4a", 0.2, 0.90, 0.90),
}
# Matys 2026-10-08 (medvedev_djokovic) : « baisse un peu le son des transitions et de la musique »,
# à appliquer par défaut. Facteurs réglables par projet : edl "vol_musique" / "vol_transitions".
VOL_MUSIQUE = 0.7      # x volumes ci-dessus (radiohead 0.9 -> 0.63, skyfall 0.5 -> 0.35…)
VOL_WOOSH = 0.5        # volume des woosh de transition (était 0.8)
# Matys 2026-10-28 : voix off montée à +18,5 dB (CapCut stocke un facteur linéaire : 10^(dB/20)),
# ding d'intro un peu plus bas, flèche plus petite et absente d'une vidéo sur 4.
VO_DB = 18.5           # edl "vo_db" pour un autre réglage
VOL_DING_INTRO = 0.5   # était 0.8 (≈ -4 dB)
FLECHE_ID = "7496729827391606069"   # sticker CapCut "Emphasis Stickers Circle & Arrow EN"
FLECHE_XY = (-0.3, 0.3)             # position par défaut ; l'agent la cale sur le joueur (_bin/fleche.py)
FLECHE_SCALE = 0.4                  # était 0.5
# Zone sûre TikTok / YouTube Shorts (coordonnées CapCut : centre 0, bords ±1, y vers le haut) :
# en haut la barre de recherche et les onglets (~11 %), en bas légende, musique et barre de
# commentaires (~25 %), à droite la colonne like / commentaires / partage (~15 %).
FLECHE_ZONE = {"x": (-0.78, 0.55), "y": (-0.42, 0.70)}
FLECHE_JOURNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shorts", "_fleche.json")


def poser_musique(script, edl, total_us):
    """Musique de fond en 2 segments : plus forte pendant le hook, puis volume 'suite'.
    edl 'musique' : False = aucune, nom de MUSIQUES, ou chemin. Défaut : tiki (<= 35 s) / skyfall."""
    nom = edl.get("musique", "tiki" if total_us <= 35_000_000 else "skyfall")
    if not nom:
        return "pas de musique"
    fichier, src0, v_hook, v_suite = MUSIQUES.get(nom, (nom, 0.0, 0.5, 0.35))
    k = float(edl.get("vol_musique", VOL_MUSIQUE))
    v_hook, v_suite = round(v_hook * k, 3), round(v_suite * k, 3)
    path = fichier if os.path.isabs(fichier) else os.path.join(MUSIQUE_DIR, fichier)
    if not os.path.exists(path):
        return f"musique introuvable : {path}"
    mat = AudioMaterial(path)
    src0_us = int(float(edl.get("musique_debut", src0)) * 1_000_000)
    dispo = mat.duration - src0_us
    if dispo <= 0:
        return f"musique_debut ({src0_us/1e6:.1f}s) au-delà de la fin du morceau"
    total = min(total_us, dispo)
    hook = min(int(HOOK_S * 1_000_000), total)
    ajouter_piste(script, TrackType.audio, "musique")
    for t0, dur, vol in ((0, hook, v_hook), (hook, total - hook, v_suite)):
        if dur > 0:
            script.add_segment(AudioSegment(mat, Timerange(t0, dur),
                               source_timerange=Timerange(src0_us + t0, dur), volume=vol), "musique")
    return f"musique '{os.path.basename(path)}' (vol {v_hook} hook -> {v_suite} à {hook/1e6:.1f}s)"


def poser_textes(script, edl):
    """Textes à l'écran (ex. traduction d'un clip parlé en langue étrangère), style sous-titres
    de Matys : Montserrat, blanc, contour noir, tiers bas.
    edl 'textes': [{"texte": "...", "t": 22.6, "dur": 2.6, "y": -0.4, "taille": 9}, ...]"""
    items = edl.get("textes") or []
    if not items:
        return "aucun texte"
    ajouter_piste(script, TrackType.text, "textes")
    for it in items:
        a = int(float(it["t"]) * 1_000_000)
        dur = int(float(it["dur"]) * 1_000_000)
        script.add_segment(d.TextSegment(
            it["texte"], Timerange(a, dur),
            font=d.FontType.Montserrat_Black,
            style=d.TextStyle(size=float(it.get("taille", 9.0)), color=(1.0, 1.0, 1.0),
                              align=1, auto_wrapping=True, max_line_width=0.8),
            border=d.TextBorder(color=(0.0, 0.0, 0.0), width=40.0),
            clip_settings=ClipSettings(transform_y=float(it.get("y", -0.4)))), "textes")
    return f"{len(items)} texte(s) à l'écran à " + ", ".join(f"{float(i['t']):.1f}s" for i in items)


ST_INTRO = next((m for m in d.TextIntro if m.name == "弹入"), None)   # apparition « pop »


def poser_sous_titres(script, edl):
    """Sous-titres de la VO, style Matys (Montserrat 13 blanc contour noir, échelle 0,78,
    y -0,4), UNE SEULE LIGNE à la fois (retour à la ligne désactivé, segments courts).
    edl 'sous_titres': [{"texte": "...", "t": 0.0, "dur": 1.2}, ...] (cf. _bin/sous_titres.py)"""
    items = edl.get("sous_titres") or []
    if not items:
        return "pas de sous-titres (Légendes auto dans CapCut)"
    ajouter_piste(script, TrackType.text, "sous-titres")
    fin_prec = 0
    for it in items:
        a = max(round(float(it["t"]) * 1e6), fin_prec)        # arrondi µs : jamais de chevauchement
        dur = round((float(it["t"]) + float(it["dur"])) * 1e6) - a
        if dur < 100_000:
            continue
        fin_prec = a + dur
        seg = d.TextSegment(
            it["texte"], Timerange(a, dur),
            font=d.FontType.Montserrat_Black,
            style=d.TextStyle(size=13.0, color=(1.0, 1.0, 1.0), align=1, auto_wrapping=False),
            border=d.TextBorder(color=(0.0, 0.0, 0.0), width=40.0),
            clip_settings=ClipSettings(transform_y=float(it.get("y", -0.4)), scale_x=0.78, scale_y=0.78))
        if ST_INTRO is not None:
            seg.add_animation(ST_INTRO, duration=min(200_000, dur // 2))
        script.add_segment(seg, "sous-titres")
    return f"{len(items)} sous-titre(s) sur une ligne"


def fleche_ce_coup_ci(nom):
    """Flèche sur 3 vidéos sur 4 (Matys 2026-10-28). Décision mémorisée par projet dans
    shorts/_fleche.json : un remontage garde la même ; un nouveau projet n'a pas de flèche
    si les 3 précédents en avaient une."""
    try:
        with open(FLECHE_JOURNAL, encoding="utf-8") as f:
            journal = json.load(f)
    except (OSError, ValueError):
        journal = {}
    if nom not in journal:
        derniers = list(journal.values())[-3:]
        journal[nom] = not (len(derniers) == 3 and all(derniers))
        with open(FLECHE_JOURNAL, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=1)
    return journal[nom]


def dans_zone_sure(x, y):
    (x0, x1), (y0, y1) = FLECHE_ZONE["x"], FLECHE_ZONE["y"]
    return min(max(x, x0), x1), min(max(y, y0), y1)


def poser_fleche(script, edl, cuts, total_us, nom):
    """Flèche d'intro (sticker CapCut) de 0 jusqu'à la 1re coupe, pointée sur le joueur.
    edl 'fleche' : true / false force le choix, sinon 3 vidéos sur 4."""
    if not edl.get("fleche", fleche_ce_coup_ci(nom)):
        return "pas de flèche (1 vidéo sur 4, ou edl 'fleche': false)"
    fin = cuts[1] if len(cuts) > 1 else min(total_us, 1_200_000)
    x0, y0 = edl.get("fleche_xy", FLECHE_XY)
    x, y = dans_zone_sure(x0, y0)
    sc = float(edl.get("fleche_scale", FLECHE_SCALE))
    ajouter_piste(script, TrackType.sticker, "fleche")
    script.add_segment(StickerSegment(FLECHE_ID, Timerange(0, fin), clip_settings=ClipSettings(
        transform_x=x, transform_y=y, scale_x=sc, scale_y=sc)), "fleche")
    recale = f" (recalée depuis ({x0}, {y0}) : hors zone sûre TikTok/Shorts)" if (x, y) != (x0, y0) else ""
    defaut = "" if "fleche_xy" in edl else " [position par défaut : pointer le joueur avec _bin/fleche.py]"
    return f"flèche 0-{fin/1e6:.2f}s en ({x:.2f}, {y:.2f}) échelle {sc}{recale}{defaut}"


# --- Bruitages 2026-10-05 (fichiers 1005*.MP3 de Matys, rôles déduits de l'analyse audio) ---
SFX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_assets", "sfx_oct")
SFX_ROLES = {          # rôle: (fichier, durée s, instant du pic s)  ~ équivalent preset CapCut
    "ding":    ("1005(1).MP3", 0.86, 0.09),   # ~ preset 13 / 48 : ding de la flèche, à 0 s
    "swoosh":  ("1005(2).MP3", 0.91, 0.25),   # souffle doux : poser SUR une transition
    "click":   ("1005(3).MP3", 0.86, 0.06),   # ~ preset 36 / 52 : petit accent de coupe
    "impact":  ("1005(4).MP3", 1.10, 0.10),   # ~ preset 51 / 7 : coup grave, moment fort
    "tonal":   ("1005(5).MP3", 0.94, 0.38),   # note tenue : relance / info clé
    "riser":   ("1005(6).MP3", 2.77, 1.76),   # ~ preset 2 : montée, pic à 1,76 s
    "punch":   ("1005(7).MP3", 0.52, 0.09),   # coup sec grave
    "pop":     ("1005(8).MP3", 0.24, 0.06),   # micro accent
    "woosh_std":  ("standard_woosh.mp3", 1.05, 0.30),   # 2026-10-06 : sons de TRANSITION validés (pack Lewi Pilgrim)
    "woosh_fast": ("fast_woosh.mp3",     1.20, 0.40),
    "photo":   ("1006.MP3",    0.23, 0.0),    # 2026-10-06 : TOUJOURS posé quand une image apparaît
}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
SFX_CUT_CYCLE = ["click", "punch", "pop", "click", "tonal", "punch", "pop"]   # varie, jamais 2 fois pareil
# Transitions RÉELLES de Matys, relevées dans ses brouillons CapCut (ids natifs, pas ceux de
# pyJianYingDraft qui n'a pas ces effets). nom: (resource_id, overlap, durée s moyenne chez lui, poids)
TRANSITIONS_MATYS = {
    "Film Erase":    ("7303835940022129153", True,  0.56, 5),
    "Flash Snap":    ("7563945244606237957", True,  0.50, 3),
    "Mix":           ("6724845717472416269", True,  0.36, 2),
    "Aura Flash":    ("7606284443216792850", True,  0.57, 2),
    "Pull In II":    ("7291211157254181377", True,  0.52, 2),
    "Fly Away":      ("7521482072578362625", True,  0.54, 2),
    "Left":          ("6726711499676455435", False, 0.40, 1),
    "Pull in":       ("6724226861666144779", False, 0.47, 1),
    "Blur Zoom Out": ("7298273321471185410", True,  0.50, 1),
    "Snapshot":      ("7351356201088586241", True,  0.40, 1),
}


class _TransMeta:
    """Imite TransitionType pour poser une transition CapCut native absente de pyJianYingDraft."""
    def __init__(self, name):
        rid, ov, dur, _ = TRANSITIONS_MATYS[name]
        self.value = type("M", (), dict(name=name, effect_id=rid, resource_id=rid,
                                        default_duration=int(dur * 1e6), is_overlap=ov))


def poser_transitions(edl, segs, rng):
    """Vraies transitions de Matys (pas d'animation d'entrée) : ~1 coupe sur 4, jamais la même
    deux fois de suite, tirage pondéré par son usage (Film Erase en tête)."""
    if edl.get("transitions", True) is False or len(segs) < 3:
        return [], 0
    pas = int(edl.get("transitions_pas", 4))
    noms = list(TRANSITIONS_MATYS)
    idx, last = [], None
    for i in range(2, len(segs), pas):                       # coupe entre segs[i-1] et segs[i]
        cand = [n for n in noms if n != last]
        nom = rng.choices(cand, weights=[TRANSITIONS_MATYS[n][3] for n in cand])[0]
        segs[i - 1].add_transition(_TransMeta(nom))
        idx.append((i, nom)); last = nom
    return idx, len(idx)


def _audio(role):
    f, dur, pic = SFX_ROLES[role]
    return AudioMaterial(os.path.join(SFX_DIR, f)), dur, pic


def poser_bruitages(script, edl, cuts, total_us, trans_idx, photo_us=()):
    """Ding à 0 s ; riser dont le pic tombe sur la coupe ~6,5 s ; un accent sur 1 coupe sur 2-3
    (varié) démarrant 0,1 s avant ; swoosh sur chaque transition ; impact vers 62 % de la vidéo."""
    if edl.get("sfx", True) is False:
        return "pas de bruitages"
    pistes, occ, n, manquants = [], {}, 0, set()     # plusieurs pistes sfx : un son qui chevauche passe sur la suivante
    def poser(role, start_us, vol=1.0):
        nonlocal n
        if not os.path.exists(os.path.join(SFX_DIR, SFX_ROLES[role][0])):
            manquants.add(SFX_ROLES[role][0])
            return
        mat, dur, _ = _audio(role)
        start_us = max(0, int(start_us))
        dd = min(int(dur * 1e6), total_us - start_us, mat.duration)
        if dd <= 0:
            return
        for nom in ("sfx", "sfx2", "sfx3", "sfx4"):
            if nom not in occ:
                ajouter_piste(script, TrackType.audio, nom); occ[nom] = []
            if all(start_us >= b or start_us + dd <= a for a, b in occ[nom]):
                occ[nom].append((start_us, start_us + dd))
                script.add_segment(AudioSegment(mat, Timerange(start_us, dd),
                                   source_timerange=Timerange(0, dd), volume=vol), nom)
                n += 1
                return
    used = set()
    # image à l'écran => bruitage. Matys 2026-10-08 : « plus de ding que l'autre bruitage, ça attire
    # plus l'oreille » -> mode "mix" (défaut) = ding sur 2 photos sur 3, 1006 sur la 3e ;
    # edl "son_photo": "ding" (toutes) / "1006" (ancien comportement).
    mode = edl.get("son_photo", "mix")
    for k, t_us in enumerate(photo_us):
        ding = mode == "ding" or (mode == "mix" and k % 3 != 2)
        if ding:
            poser("ding", t_us - int(SFX_ROLES["ding"][2] * 1e6), 0.9)   # pic du ding pile sur l'image
        else:
            poser("photo", t_us, 1.0)
        if t_us in cuts: used.add(cuts.index(t_us))
    poser("ding", 0, float(edl.get("vol_ding_intro", VOL_DING_INTRO))); used.add(0)
    # riser : son pic (1,76 s) tombe sur la coupe la plus proche de HOOK_S
    c_hook = min(range(1, len(cuts)), key=lambda i: abs(cuts[i] / 1e6 - HOOK_S))
    pic = int(SFX_ROLES["riser"][2] * 1e6)
    poser("riser", cuts[c_hook] - pic, 0.7); used.add(c_hook)
    # impact : coupe la plus proche de 62 % (ou edl 'impact_beat')
    c_imp = int(edl.get("impact_beat", min(range(1, len(cuts)), key=lambda i: abs(cuts[i] - 0.62 * total_us))))
    poser("impact", cuts[c_imp] - int(SFX_ROLES["impact"][2] * 1e6), 0.9); used.add(c_imp)
    # swoosh sur les transitions
    for k, (i, _nom) in enumerate(trans_idx):          # transitions : UNIQUEMENT standard / fast woosh, en alternance
        if i not in used and i < len(cuts):
            role = ("woosh_std", "woosh_fast")[k % 2]
            poser(role, cuts[i] - int(SFX_ROLES[role][2] * 1e6), float(edl.get("vol_transitions", VOL_WOOSH))); used.add(i)
    # accents de coupe (click/punch/pop...) : gardés en réserve, OFF par défaut (Matys 2026-10-06)
    k, i, pas = 0, 2, 2
    if not edl.get("accents", False):
        i = len(cuts)
    while i < len(cuts):
        if all(abs(i - u) > 1 for u in used):
            role = SFX_CUT_CYCLE[k % len(SFX_CUT_CYCLE)]; k += 1
            poser(role, cuts[i] - int(0.1 * 1e6), 0.85); used.add(i)
        i += pas; pas = 3 if pas == 2 else 2
    if manquants:
        print(f"     [!] sons absents de {SFX_DIR} (ignorés) : {', '.join(sorted(manquants))}")
    return f"bruitages x{n} (ding, riser coupe {c_hook}, impact coupe {c_imp}, {len(photo_us)} son(s) image (ding/1006 mode {mode}), {len(trans_idx)} woosh de transition)"


IMG_SCALE = 0.65       # médiane de ses incrustations (0,5-0,78)
IMG_DUR = 2.2          # médiane 1,3-5 s


def poser_images(script, edl, project_dir, total_us):
    """Vraies photos en incrustation (style Matys, mesuré sur 14 brouillons) : piste au-dessus
    de la vidéo, centrées, échelle ~0,65, sans animation, posées quand la VO nomme la personne /
    l'objet. edl 'images' : [ {"src": "images/x.jpg", "t": 7.6, "dur": 2.2, "y": 0, "scale": 0.65} ]
    ou [ "images/x.jpg", 7.6, 2.2 ]. Renvoie les instants (µs) où une image apparaît."""
    items = edl.get("images") or []
    if not items:
        return [], "aucune image"
    ajouter_piste(script, TrackType.video, "photos")
    starts = []
    for it in items:
        if isinstance(it, (list, tuple)):
            it = dict(zip(("src", "t", "dur"), it))
        src = it["src"] if os.path.isabs(it["src"]) else os.path.join(project_dir, it["src"])
        t0 = int(float(it["t"]) * 1e6)
        dur = min(int(float(it.get("dur", IMG_DUR)) * 1e6), total_us - t0)
        if dur <= 0:
            continue
        sc = float(it.get("scale", IMG_SCALE))
        script.add_segment(VideoSegment(VideoMaterial(src), Timerange(t0, dur), clip_settings=ClipSettings(
            scale_x=sc, scale_y=sc, transform_y=float(it.get("y", 0)))), "photos")
        starts.append(t0)
    return starts, f"{len(starts)} image(s) en incrustation à " + ", ".join(f"{x/1e6:.1f}s" for x in starts)



def embarquer_medias(nom):
    """CapCut macOS (App Store) est SANDBOXÉ : il ne lit librement que ~/Movies. Un média
    référencé sous ~/Documents s'ouvre en « unsupported media » / « Relier des fichiers »
    (vécu sur dembele_enrique, 2026-10-07). On place donc chaque média dans
    <brouillon>/materials/ par lien physique (aucun espace disque en plus) et on réécrit
    les chemins du projet. Inutile sous Windows."""
    if os.name == "nt":
        return 0
    import shutil
    dossier = os.path.join(DRAFT_DIR, nom)
    dest = os.path.join(dossier, "materials")
    os.makedirs(dest, exist_ok=True)
    n = 0
    for f in ("draft_content.json", "draft_info.json"):
        fp = os.path.join(dossier, f)
        if not os.path.exists(fp):
            continue
        dc = json.load(open(fp, encoding="utf-8"))
        for liste in dc.get("materials", {}).values():
            if not isinstance(liste, list):
                continue
            for m in liste:
                src = m.get("path") if isinstance(m, dict) else None
                if not src or not os.path.isabs(src) or src.startswith(dest) or not os.path.exists(src):
                    continue
                # préfixe = dossier parent, pour éviter les collisions de noms (ex. voix.mp3)
                cible = os.path.join(dest, os.path.basename(os.path.dirname(src)) + "__" + os.path.basename(src))
                if not os.path.exists(cible):
                    try:
                        os.link(src, cible)
                    except OSError:
                        shutil.copy2(src, cible)
                m["path"] = cible
                n += 1
        json.dump(dc, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
    return n


def beats_animes(edl, n):
    """Quels clips reçoivent le zoom-punch. edl 'anim' : False/0=aucun, True=tous,
    entier N=un clip sur N, liste=ces index. Défaut : aucun."""
    a = edl.get("anim", 0)   # pas d'animation d'entrée (demande Matys 2026-10-05)
    if a is True:
        return set(range(n))
    if not a:
        return set()
    if isinstance(a, int):
        return set(range(0, n, max(1, a)))
    if isinstance(a, (list, tuple)):
        return set(int(x) for x in a)
    return set()


def main(project_dir):
    project_dir = os.path.abspath(project_dir)
    nom = os.path.basename(project_dir.rstrip("\\/"))
    edl = json.load(open(os.path.join(project_dir, "edl.json"), encoding="utf-8"))
    # sous-titres automatiques (Matys 2026-10-08) : générés s'ils manquent ("sous_titres": false = aucun)
    if "sous_titres" not in edl and all(os.path.exists(os.path.join(project_dir, f))
                                        for f in ("_mots.json", "texte.txt")):
        import subprocess
        st = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bin", "sous_titres.py")
        subprocess.run([sys.executable, st, project_dir], check=True, stdout=subprocess.DEVNULL)
        edl = json.load(open(os.path.join(project_dir, "edl.json"), encoding="utf-8"))
    zoom = float(edl.get("zoom", ZOOM_169))
    beats = edl["beats"]
    gap_us = int(float(edl.get("gap", 0)) * 1_000_000)   # mini-noir entre clips (0 = coupes franches)

    voix = trouver(project_dir, AUDIO_EXT)
    if not voix:
        sys.exit(f"[X] Pas de voix off dans {project_dir}")
    amat = AudioMaterial(voix)
    vo_dur = amat.duration

    folder = d.DraftFolder(DRAFT_DIR)
    script = folder.create_draft(nom, CANVAS_W, CANVAS_H, fps=FPS, allow_replace=True)
    ajouter_piste(script, TrackType.video, "video")
    ajouter_piste(script, TrackType.audio, "vo")

    anim_set = beats_animes(edl, len(beats))   # clips qui reçoivent le zoom-punch (de temps en temps)

    # --- Garde-fou anti-doublon : deux beats VOISINS de même source avec des plages
    #     qui se chevauchent => plan quasi répété = effet de "bug". On bloque pour forcer
    #     la correction de l'EDL (varier la source ou écarter les plages). ---
    for i in range(1, len(beats)):
        s0, a0, b0 = beats[i - 1][:3]
        s1, a1, b1 = beats[i][:3]
        if os.path.abspath(s0) == os.path.abspath(s1) and a1 < b0 and a0 < b1:
            sys.exit(f"[X] beats {i-1}/{i} : même source '{os.path.basename(s1)}' avec plages "
                     f"qui se chevauchent ({a0}-{b0}s / {a1}-{b1}s). Pas de plan répété à la "
                     f"suite : varie la source ou écarte les plages.")

    cache = {}
    t = 0
    cuts = []                                  # temps de début de chaque clip (pour les bruitages)
    segs = []
    photo_idx = []
    n_vert = n_blur = 0
    for i, beat in enumerate(beats):
        src, a, b = beat[:3]
        # 4e élément optionnel {"son": 1.0} : clip PARLÉ dont on garde le son d'origine
        # (la VO doit contenir un blanc à cet endroit). Par défaut les clips sont muets.
        opt = beat[3] if len(beat) > 3 and isinstance(beat[3], dict) else {}
        vol = float(opt.get("son", 0.0))
        z = float(opt.get("zoom", zoom))   # zoom propre au plan (ex. 1.0 si un élément est en bord d'image)
        if i > 0:
            t += gap_us                       # laisse un court noir entre les clips
        src = os.path.abspath(src)
        if src not in cache:
            cache[src] = VideoMaterial(src)
        mat = cache[src]
        a_us, b_us = int(a * 1_000_000), int(b * 1_000_000)
        b_us = min(b_us, mat.duration)
        dur = b_us - a_us
        if dur <= 0:
            continue
        # 9:16 (ou plus haut) -> plein cadre (cover), AUCUN flou ; sinon 16:9 -> fit + flou CapCut
        vertical = (mat.height / mat.width) >= 1.5
        if vertical:
            sc = cover_scale(mat.width, mat.height)
            seg = VideoSegment(mat, Timerange(t, dur), source_timerange=Timerange(a_us, dur),
                               volume=vol, clip_settings=ClipSettings(scale_x=sc, scale_y=sc))
            n_vert += 1
        else:
            seg = VideoSegment(mat, Timerange(t, dur), source_timerange=Timerange(a_us, dur),
                               volume=vol, clip_settings=ClipSettings(scale_x=z, scale_y=z))
            seg.add_background_filling("blur", blur=BLUR)   # fond flou NATIF CapCut (16:9 seulement)
            n_blur += 1
        if i in anim_set:
            seg.add_animation(ANIM_ZOOM, duration=ANIM_DUR)   # punch zoom (seulement certains clips)
        if src.lower().endswith(IMG_EXT):
            photo_idx.append(len(cuts))
        segs.append(seg)
        cuts.append(t)
        t += dur

    # transitions AVANT d'ajouter les segments (sinon pyJianYingDraft n'enregistre pas la matière)
    import random
    rng = random.Random(edl.get("seed", nom))
    trans_idx, n_trans = poser_transitions(edl, segs, rng)
    for seg in segs:
        script.add_segment(seg, "video")

    # voix off, montée à +18,5 dB (Matys 2026-10-28)
    vo_db = float(edl.get("vo_db", VO_DB))
    script.add_segment(AudioSegment(amat, Timerange(0, vo_dur), volume=10 ** (vo_db / 20)), "vo")

    img_us, msg_img = poser_images(script, edl, project_dir, min(t, vo_dur))
    photo_us = sorted(set(img_us) | {cuts[i] for i in photo_idx})
    msg_sfx = poser_bruitages(script, edl, cuts, min(t, vo_dur), trans_idx, photo_us) if cuts else "pas de bruitages"
    msg_trans = ", ".join(f"coupe {i}: {n}" for i, n in trans_idx) or "aucune"

    msg_fleche = poser_fleche(script, edl, cuts, t, nom)
    msg_musique = poser_musique(script, edl, min(t, vo_dur))
    msg_textes = poser_textes(script, edl)
    msg_st = poser_sous_titres(script, edl)

    script.save()
    n_emb = embarquer_medias(nom)            # sandbox CapCut macOS : médias dans le brouillon
    patch_pour_capcut(nom)
    patch_meta_capcut(nom, max(t, vo_dur))   # indispensable sur macOS (sinon timeline vide écrasée)
    print(f"[OK] '{nom}' monté : {len(beats)} plans, {t/1e6:.1f}s de vidéo, VO {vo_dur/1e6:.1f}s (+{vo_db} dB)")
    print(f"     {n_vert} clip(s) 9:16 plein cadre (sans flou) | {n_blur} clip(s) 16:9 + flou CapCut")
    print(f"     {msg_fleche}")
    print(f"     {msg_musique}")
    print(f"     {msg_img} (+ ding / bruitage 1006 à l'apparition)")
    print(f"     {msg_textes}")
    print(f"     {msg_st}")
    print(f"     {msg_sfx}")
    print(f"     transitions x{n_trans} : {msg_trans}")
    print(f"     {n_emb} média(s) embarqué(s) dans le brouillon (sandbox CapCut)")
    if not edl.get("sous_titres"):
        print("     (sous-titres : à faire toi-même dans CapCut, ou _bin/sous_titres.py)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage : python monter_edl.py <dossier_projet>")
    main(sys.argv[1])
