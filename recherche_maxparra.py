# -*- coding: utf-8 -*-
"""
recherche_maxparra.py — Collecte les Shorts de la chaine Max Parra (@maxparra9)
pour constituer une base d'analyse storytelling/hooks.

Pour chaque short :
  - id, titre, vues, duree, date
  - transcription FR (sous-titres auto .vtt -> texte brut)

Sortie : shorts/_recherche_maxparra/
  - index.json          (metadonnees triees par vues)
  - subs/<id>.fr.vtt     (sous-titres bruts)
  - transcripts/<id>.txt (texte nettoye)
"""
import os, re, json, glob, sys
import yt_dlp

CHANNEL = "https://www.youtube.com/@maxparra9/shorts"
OUT = os.path.join("shorts", "_recherche_maxparra")
SUBS = os.path.join(OUT, "subs")
TRANS = os.path.join(OUT, "transcripts")
N_MAX = 55

for dd in (OUT, SUBS, TRANS):
    os.makedirs(dd, exist_ok=True)


def log(msg):
    with open(os.path.join(OUT, "_log.txt"), "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def vtt_to_text(path):
    """Sous-titres auto YouTube .vtt -> texte continu sans doublons/timecodes."""
    try:
        raw = open(path, encoding="utf-8").read()
    except Exception:
        return ""
    lines = []
    for ln in raw.splitlines():
        if "-->" in ln or ln.strip() == "" or ln.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        ln = re.sub(r"<[^>]+>", "", ln)          # tags <00:00:00.000>
        ln = re.sub(r"\s+", " ", ln).strip()
        if ln and (not lines or lines[-1] != ln):
            lines.append(ln)
    # dedup consecutif de fragments repetes par le rolling caption
    out = []
    for ln in lines:
        if out and (ln in out[-1] or out[-1] in ln):
            if len(ln) > len(out[-1]):
                out[-1] = ln
            continue
        out.append(ln)
    return " ".join(out)


def main():
    # 1) liste plate des shorts
    flat = yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True,
                             "skip_download": True, "playlistend": N_MAX})
    info = flat.extract_info(CHANNEL, download=False)
    entries = [e for e in (info.get("entries") or []) if e.get("id")][:N_MAX]
    log(f"shorts listes: {len(entries)}")

    # 2) sous-titres FR auto + metadonnees, video par video
    sub_opts = {
        "quiet": True, "no_warnings": True, "skip_download": True,
        "writeautomaticsub": True, "writesubtitles": True,
        "subtitleslangs": ["fr", "fr-FR", "fr-orig"], "subtitlesformat": "vtt",
        "outtmpl": os.path.join(SUBS, "%(id)s.%(ext)s"),
    }
    rows = []
    for n, e in enumerate(entries, 1):
        vid = e["id"]
        url = f"https://www.youtube.com/watch?v={vid}"
        try:
            with yt_dlp.YoutubeDL(sub_opts) as ydl:
                meta = ydl.extract_info(url, download=True)
        except Exception as ex:
            log(f"[X] {vid}: {str(ex)[:100]}")
            continue
        # localiser le vtt telecharge
        vtts = glob.glob(os.path.join(SUBS, f"{vid}*.vtt"))
        txt = vtt_to_text(vtts[0]) if vtts else ""
        if txt:
            open(os.path.join(TRANS, f"{vid}.txt"), "w", encoding="utf-8").write(txt)
        rows.append({
            "id": vid,
            "titre": meta.get("title", ""),
            "vues": meta.get("view_count") or 0,
            "duree": meta.get("duration") or 0,
            "date": meta.get("upload_date", ""),
            "mots_transcript": len(txt.split()),
            "transcript_ok": bool(txt),
        })
        log(f"[{n}/{len(entries)}] {vid} vues={rows[-1]['vues']} mots={rows[-1]['mots_transcript']}")

    rows.sort(key=lambda r: r["vues"], reverse=True)
    json.dump(rows, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    log(f"FINI. {len(rows)} shorts, {sum(r['transcript_ok'] for r in rows)} transcripts.")


if __name__ == "__main__":
    main()
