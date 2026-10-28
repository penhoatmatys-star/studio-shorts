"""Veille TikTok : python _bin/veille_tiktok.py handle1 handle2 ...
Récupère les ~N dernières vidéos de chaque compte (yt-dlp + curl_cffi) dans shorts/_veille_tiktok/<handle>.json
et affiche médiane des vues + top vidéos."""
import json, subprocess, sys, statistics, datetime, pathlib
from concurrent.futures import ThreadPoolExecutor

OUT = pathlib.Path(__file__).resolve().parent.parent / "shorts" / "_veille_tiktok"
N = int(__import__("os").environ.get("VN","150"))

def fetch(h, essai=0):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--playlist-end", str(N), "-J",
                        f"https://www.tiktok.com/@{h}"], capture_output=True, text=True, encoding="utf-8")
    try:
        es = [e for e in json.loads(r.stdout)["entries"] if e]
    except Exception:
        return fetch(h, 1) if essai == 0 else (h, [])
    vids = [{"id": e["id"], "url": f"https://www.tiktok.com/@{h}/video/{e['id']}", "titre": e.get("description") or e.get("title"),
             "vues": e.get("view_count") or 0, "likes": e.get("like_count") or 0, "duree": e.get("duration"),
             "date": datetime.date.fromtimestamp(e["timestamp"]).isoformat() if e.get("timestamp") else None} for e in es]
    (OUT / f"{h}.json").write_text(json.dumps(vids, ensure_ascii=False, indent=1), encoding="utf-8")
    return h, vids

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(1) as ex:
        for h, v in ex.map(fetch, sys.argv[1:]):
            if not v:
                print(f"## @{h} : rien"); continue
            d = [x["duree"] for x in v if x["duree"]]
            print(f"## @{h} : {len(v)} vidéos, médiane {statistics.median(x['vues'] for x in v):,.0f} vues, durée méd {statistics.median(d) if d else '?'} s, {v[-1]['date']} -> {v[0]['date']}")
            for x in sorted(v, key=lambda x: -x["vues"])[:4]:
                print(f"   {x['vues']:>11,} | {x['duree']}s | {x['date']} | {(x['titre'] or '')[:90]}")
