# -*- coding: utf-8 -*-
"""Base @topfoot_youss triée par vues -> shorts/_recherche_topfoot/{index.json,base.md,scripts/<id>.txt}
python _bin/topfoot_base.py   (.venv312)"""
import json, re, pathlib, shutil, statistics
root = pathlib.Path(__file__).resolve().parent.parent
src = root / "shorts" / "_veille_tiktok"
out = root / "shorts" / "_recherche_topfoot"; (out / "scripts").mkdir(parents=True, exist_ok=True)
vids = {v["id"]: v for v in json.load(open(src / "topfoot_youss.json", encoding="utf-8"))}

HOOKS = [  # (nom, regex sur la 1re phrase)
    ("Question directe « Pourquoi… ? »", r"^pourquoi"),
    ("Tu crois / Tu penses voir… (fausse piste au 'tu')", r"^(tu|vous) (crois|pense|vois|as vu|savais)"),
    ("« Vous avez prévu / Est-ce que vous vous rappelez »", r"^(vous avez|est-ce que (vous|tu)|vous vous rappelez|vous souvenez)"),
    ("Prédiction / jugement fort (« Je pense que… la plus honteuse »)", r"^(je pense|on va|ça va|c'est (le|la))"),
    ("« Cette nuit / Ce soir / Demain… » (échéance immédiate)", r"^(cette nuit|ce soir|demain|dans quelques|aujourd'hui|hier)"),
    ("« On n'avait jamais vu ça… » (inédit)", r"^(on n'avait|jamais|personne|c'est la première|c'est la première fois)"),
    ("Constat chiffré / fait sec", r"^\D{0,40}\d"),
]
def hook_type(first):
    f = first.lower().strip()
    for n, r in HOOKS:
        if re.search(r, f): return n
    return "Affirmation directe sur un sujet / un nom"

rows = []
for f in (src / "topfoot_youss_scripts").glob("*.txt"):
    t = f.read_text(encoding="utf-8").strip(); i = f.stem; v = vids.get(i)
    if not v or not t: continue
    mots = len(t.split()); sents = re.split(r"(?<=[.!?…])\s+", t)
    narre = mots >= 150
    low = t.lower()
    rows.append({
        "id": i, "url": v["url"], "vues": v["vues"], "likes": v["likes"], "duree": v["duree"], "date": v["date"],
        "titre": re.sub(r"#\S+", "", v["titre"] or "").strip(), "mots": mots, "narre": narre,
        "hook": sents[0] if narre else None, "type_hook": hook_type(sents[0]) if narre else None,
        "chute": " ".join(sents[-2:]) if narre else None,
        "marqueurs": {k: len(re.findall(p, low)) for k, p in {
            "sauf que": r"sauf que", "parce que": r"parce que", "mais": r"\bmais\b", "et pour cause": r"et pour cause",
            "chiffres": r"\d+", "tu/vous": r"\b(tu|vous)\b"}.items()},
        "script": t})
    shutil.copy(f, out / "scripts" / f.name)
rows.sort(key=lambda r: -r["vues"])
json.dump(rows, open(out / "index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

nar = [r for r in rows if r["narre"]]
L = [f"# Base @topfoot_youss : {len(rows)} vidéos transcrites, dont {len(nar)} narrées (voix off)\n",
     f"Médiane vues narrées : {statistics.median(r['vues'] for r in nar):,.0f}\n"]
by = {}
for r in nar: by.setdefault(r["type_hook"], []).append(r["vues"])
L.append("\n## Types de hook (narrées)\n\n| Hook | Nb | Vues méd. |\n|---|---|---|")
for k, v in sorted(by.items(), key=lambda kv: -statistics.median(kv[1])):
    L.append(f"| {k} | {len(v)} | {statistics.median(v):,.0f} |")
L.append("\n## Classement par vues (narrées)\n")
for n, r in enumerate(nar, 1):
    L.append(f"### {n}. {r['vues']:,} vues | {r['duree']} s | {r['mots']} mots | {r['date']}\n{r['url']}\n\n"
             f"**Hook** ({r['type_hook']}) : {r['hook']}\n\n**Chute** : {r['chute']}\n\n<details><summary>script</summary>\n\n{r['script']}\n\n</details>\n")
L.append("\n## Montages sans voix off (hors analyse de script)\n")
for r in rows:
    if not r["narre"]: L.append(f"- {r['vues']:,} | {r['duree']} s | {r['titre'][:80]} | {r['url']}")
(out / "base.md").write_text("\n".join(L), encoding="utf-8")
print(len(rows), "vidéos,", len(nar), "narrées ->", out)
