// Studio Shorts : veille → script (+ chat IA) → production, dans une ossature de logiciel de montage.
const $ = (s, el = document) => el.querySelector(s);
const viewer = $("#viewer"), insp = $("#inspecteur"), bibli = $("#bibli");
const S = { veilles: [], veille: null, vid: null, sid: null, vue: "veille", scid: null, ia: null, polls: {},
  onglet: memo("bibli") || "sujets", montages: [], recherches: [], video: {} };

const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const ic = (n, cls = "") => `<svg class="ic ${cls}" aria-hidden="true"><use href="#i-${n}"/></svg>`;
const api = async (url, corps) => {
  const r = await fetch(url, corps ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corps) } : {});
  const d = await r.json();
  if (!r.ok) throw new Error(d.erreur || r.statusText);
  return d;
};
const ytId = (u) => (String(u).match(/(?:shorts\/|v=|youtu\.be\/|embed\/)([\w-]{11})/) || [])[1];
const VERDICT = { go: "GO", surveiller: "À surveiller", non: "Pas assez" };
const FIAB = { confirme: "Confirmé", partiel: "Partiellement confirmé", rumeur: "Rumeur" };
const FORMATS = { long: { lib: "1 min", titre: "Shorts d'1 minute", cible: [260, 275] },
  court: { lib: "25-30 s", titre: "Shorts de 25-30 secondes", cible: [110, 130] } };
const formatDe = (s) => FORMATS[s?.format] || FORMATS.long;
// Veille du jour : les sujets d'1 min d'abord, puis les 25-30 s ; dans chaque groupe, par note
const trier = (sujets) => [...sujets].sort((a, b) => (b.perso ? 1 : 0) - (a.perso ? 1 : 0)
  || (a.format === "court") - (b.format === "court") || (b.note || 0) - (a.note || 0));
const groupes = (sujets) => (sujets.some((s) => s.format) ? ["long", "court"].map((f) => [FORMATS[f].titre,
  trier(sujets).filter((s) => (s.format || "long") === f)]).filter(([, l]) => l.length) : [["", trier(sujets)]]);
const MAC = /Mac/.test(navigator.platform);
const compterMots = (t) => (String(t).replace(/\[[^\]]*\]/g, " ").match(/[\wÀ-ÿ'’-]+/g) || []).length;
const fmtNote = (n) => (n == null ? ic("pen") : Number.isInteger(n) ? n : Number(n).toFixed(1).replace(".", ","));
const heure = (t) => (t ? new Date(t * 1000).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }) : "");
const minutes = (j) => Math.max(0, Math.round(((j.fin || Date.now() / 1000) - j.debut) / 60));

function memo(cle, val) {
  try { if (val === undefined) return localStorage.getItem(cle); localStorage.setItem(cle, val); } catch (e) { return null; }
}

/* ------------------------------------------------------------------ navigation */
function aller(vue, sid = S.sid) {
  location.hash = ["", S.vid, sid || "", sid && vue !== "detail" ? vue : ""].join("/").replace(/\/+$/, "");
}
window.addEventListener("hashchange", lireHash);
async function lireHash() {
  const [, vid, sid, vue] = location.hash.split("/");
  if (vid) await chargerVeille(decodeURIComponent(vid));  // toujours frais : l'état bouge côté serveur
  S.sid = sid ? decodeURIComponent(sid) : null;
  S.vue = sid ? (vue || "detail") : "veille";
  rendre();
}

/* ------------------------------------------------------------------ données */
async function init() {
  $("#raccourci").textContent = MAC ? "⌘ K" : "Ctrl K";
  verifierIA();
  surveillerVersion();
  S.veilles = await api("/api/veilles");
  remplirChoixVeilles();
  $("#choixVeille").onchange = (e) => { location.hash = "/" + e.target.value; };
  if (!location.hash && S.veilles[0]) location.hash = "/" + S.veilles[0].id;
  else await lireHash();
  const jv = memo("jobVeille");
  if (jv) suivreVeille(jv);
  suivreMontages();
  suivreRecherches();
}
async function surveillerVersion() {
  try {
    const { v } = await api("/api/version");
    if (S.version && v !== S.version) {
      const a = document.activeElement;
      if (!(a && ["TEXTAREA", "INPUT"].includes(a.tagName) && a.value)) return location.reload();
    }
    S.version = S.version || v;
  } catch (e) { /* serveur en redémarrage */ }
  setTimeout(surveillerVersion, 20000);
}
function libelleVeille(v) {
  const [d, m] = v.id.split("_");
  const date = new Date(d + "T12:00");
  const jour = isNaN(date) ? d : date.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "short" });
  return `${jour} · ${m || ""}${v.json ? ` · ${v.nb} sujets` : ""}`;
}
function remplirChoixVeilles() {
  const sel = $("#choixVeille");
  sel.innerHTML = S.veilles.map((v) => `<option value="${esc(v.id)}">${esc(libelleVeille(v))}</option>`).join("") || "<option>Aucune veille</option>";
  if (S.vid) sel.value = S.vid;
}
async function chargerVeille(vid) {
  S.vid = vid;
  S.veille = await api("/api/veille/" + encodeURIComponent(vid));
  $("#choixVeille").value = vid;
}
async function rafraichir() { S.veille = await api("/api/veille/" + encodeURIComponent(S.vid)); }
const sujet = () => (S.veille?.sujets || []).find((s) => s.id === S.sid);
const etatSujet = (id = S.sid) => (S.veille?.etat || {})[id] || {};
const iaOk = () => !!S.ia?.ok;

async function verifierIA() {
  try { S.ia = await api("/api/auth"); } catch (e) { S.ia = { ok: false, raison: e.message }; }
  const p = $("#ia");
  p.className = "etat-ia " + (S.ia.ok ? "ok" : "ko");
  p.lastElementChild.textContent = S.ia.ok ? "IA connectée" : "IA non connectée";
  const b = $("#bandeau");
  b.hidden = S.ia.ok;
  if (!S.ia.ok) {
    b.innerHTML = `L'IA du studio n'est pas connectée sur cet ordinateur. Une seule fois, dans un terminal ouvert dans le dossier du projet,
      lance <code>claude auth login</code> et connecte-toi avec ton compte Claude, puis <a href="#" id="reIA">revérifie</a>.
      ${S.ia.raison ? `<br><span class="sous">${esc(S.ia.raison)}</span>` : ""}`;
    $("#reIA").onclick = (e) => { e.preventDefault(); verifierIA(); };
  }
  ["#btnScript", "#btnVeille", "#champRecherche"].forEach((s) => ($(s).disabled = !S.ia.ok));
  if (S.veille) rendre();
}

function suivreJob(id, chaque, fin, intervalle = 2500) {
  clearTimeout(S.polls[id]);
  const tour = async () => {
    let j;
    try { j = await api("/api/job/" + id); } catch (e) { return; }
    chaque && chaque(j);
    if (j.statut === "en_cours") S.polls[id] = setTimeout(tour, intervalle);
    else fin && fin(j);
  };
  tour();
}

/* ------------------------------------------------------------------ rendu global */
function rendre() {
  document.querySelectorAll("#pages button").forEach((b) => {
    const v = b.dataset.vue;
    b.classList.toggle("actif", v === S.vue || (v === "veille" && S.vue === "detail"));
    b.disabled = v !== "veille" && !S.sid;
  });
  rendreBibli();
  if (!S.veille) {
    viewer.innerHTML = ecranVide("veille", "Aucun rapport de veille", "Lance une nouvelle veille, ou tape ton propre sujet dans la barre du haut pour que Claude le documente.");
    insp.innerHTML = "";
    return;
  }
  ({ veille: vueVeille, detail: vueDetail, scripts: vueScripts, production: vueProduction }[S.vue] || vueVeille)();
  const cle = S.vid + S.sid + S.vue;
  if (cle !== S.derniereVue) viewer.scrollTop = 0;
  S.derniereVue = cle;
}
const ecranVide = (icone, titre, texte, bouton = "") =>
  `<div class="ecran-vide"><div>${ic(icone)}<h2>${esc(titre)}</h2><p>${texte}</p>${bouton}</div></div>`;
const blocInsp = (html) => `<div class="pane-body">${html}</div>`;

document.querySelectorAll("#pages button").forEach((b) => (b.onclick = () => allerPage(b.dataset.vue)));
function allerPage(v) {
  if (v !== "veille" && !S.sid) return;
  if (v === "veille") return S.vue === "detail" || !S.sid ? (location.hash = "/" + S.vid) : aller("detail");
  aller(v);
}

/* ------------------------------------------------------------------ bibliothèque */
document.querySelectorAll("[data-bibli]").forEach((b) => (b.onclick = () => { S.onglet = b.dataset.bibli; memo("bibli", S.onglet); rendreBibli(); }));
function rendreBibli() {
  document.querySelectorAll("[data-bibli]").forEach((b) => b.setAttribute("aria-selected", b.dataset.bibli === S.onglet));
  const sujets = S.veille?.sujets || [];
  $("#nSujets").textContent = sujets.length || "";
  const enCours = S.montages.filter((x) => x.statut === "en_cours").length;
  $("#nMontages").textContent = enCours || (S.montages.length || "");
  $("#nMontages").classList.toggle("vif", enCours > 0);
  if (S.onglet === "montages") return rendreFile();

  const attente = S.recherches.filter((j) => j.statut === "en_cours").map((j) => `<li><div class="rang" aria-busy="true">
      <div class="note"><span class="anim"></span></div><div><div class="t">${esc(j.meta.texte)}</div><div class="m">Claude documente le sujet…</div></div></div></li>`).join("");
  const ecartes = S.veille?.ecartes || [];
  bibli.innerHTML = (attente || sujets.length) ? `<ul class="liste">${attente}</ul>${groupes(sujets).map(([titre, l]) =>
      `${titre ? `<div class="sep-liste">${esc(titre)} · ${l.length}</div>` : ""}<ul class="liste">${l.map(rangSujet).join("")}</ul>`).join("")}
    ${ecartes.length ? `<div class="sep-liste">Écartés</div>${ecartes.map((e) => `<div class="ecarte"><b>${esc(e.titre)}</b><br>${esc(e.raison)}</div>`).join("")}` : ""}`
    : `<div class="vide-bibli">${S.veille && !S.veille.sujets ? "Ce rapport est en ancien format : convertis-le depuis l'inspecteur." : "Pas encore de sujet."}</div>`;
  bibli.querySelectorAll("[data-id]").forEach((b) => (b.onclick = () => ouvrirSujet(b.dataset.id)));
}
function rangSujet(s) {
  const e = etatSujet(s.id);
  const etat = e.production ? `<span class="etat prod">${ic("film")} en production</span>`
    : e.scripts?.length ? `<span class="etat">${ic("script")} ${e.scripts.length} script${e.scripts.length > 1 ? "s" : ""}</span>`
    : e.valide ? `<span class="etat">${ic("check")} validé</span>` : "";
  const meta = [`<span class="mono">${formatDe(s).lib}</span>`, s.script_perso ? "ton script" : s.perso ? "ton sujet" : "",
    esc(s.sport || ""), etat].filter(Boolean).join(" · ");
  return `<li><button class="rang ${s.id === S.sid ? "ici" : ""}" data-id="${esc(s.id)}">
    <div class="note ${s.verdict || ""}">${fmtNote(s.note)}</div>
    <div><div class="t">${esc(s.titre)}</div><div class="m">${meta || VERDICT[s.verdict] || ""}</div></div></button></li>`;
}
function ouvrirSujet(id) {
  const s = (S.veille.sujets || []).find((x) => x.id === id) || {};
  const e = etatSujet(id);
  const vue = s.script_perso ? (e.production ? "/production" : "/scripts") : "";
  location.hash = `/${S.vid}/${id}${vue}`;
}
function rendreFile() {
  bibli.innerHTML = S.montages.map((x) => {
    const st = x.statut === "en_cours" ? `${x.modif ? "modif" : "rendu"} · ${minutes(x)} min`
      : x.statut === "termine" ? `prêt · ${heure(x.fin)}` : x.statut === "arrete" ? "arrêté" : "erreur";
    const ici = S.vue === "production" && S.sid === x.sujet && S.vid === x.veille;
    return `<button class="job ${x.statut} ${ici ? "ici" : ""}" data-v="${esc(x.veille)}" data-s="${esc(x.sujet)}">
      <div class="t"><span>${esc(x.projet)}</span><span class="st">${st}</span></div>
      <div class="titre">${esc(x.titre)}</div>
      ${x.statut === "en_cours" ? `<div class="barre-rendu"><i></i></div>${x.derniere ? `<div class="der">${esc(x.derniere)}</div>` : ""}` : ""}
      ${x.statut === "erreur" && x.erreur ? `<div class="der">${esc(x.erreur)}</div>` : ""}</button>`;
  }).join("") || `<div class="vide-bibli">Aucun montage. Valide un sujet, choisis un script et lance la production : il apparaîtra ici comme dans une file de rendu.</div>`;
  bibli.querySelectorAll(".job").forEach((b) => (b.onclick = () => { location.hash = `/${b.dataset.v}/${b.dataset.s}/production`; }));
}

/* ------------------------------------------------------------------ 1. veille : vue d'ensemble */
function vueVeille() {
  const v = S.veille;
  if (!v.sujets) {
    viewer.innerHTML = `<div class="page"><h1>${esc(v.id)}</h1><div class="rapport">${md(v.markdown || "")}</div></div>`;
    insp.innerHTML = blocInsp(`<div class="insp-titre">Ancien format</div>
      <p class="aide">Ce rapport n'existe qu'en Markdown. La conversion le rend cliquable (environ 1 min).</p>
      <button class="btn principal grand" id="conv" ${iaOk() ? "" : "disabled"}>Convertir ce rapport</button>`);
    $("#conv").onclick = async (e) => {
      e.target.disabled = true; e.target.innerHTML = `<span class="anim"></span> Conversion…`;
      const j = await api("/api/convertir", { veille: v.id });
      suivreJob(j.id, null, async (f) => {
        if (f.statut !== "termine") return toast("Conversion ratée : " + f.erreur, false);
        await chargerVeille(v.id); rendre();
      });
    };
    return;
  }
  const attente = S.recherches.filter((j) => j.statut === "en_cours").map((j) => `<div class="tuile attente">
      <div class="vig"><span class="anim"></span></div><div class="t">${esc(j.meta.texte)}</div><div class="m">Recherche en cours, 3 à 6 min</div></div>`).join("");
  viewer.innerHTML = `<div class="page">
    <div class="entete-page"><div><h1>${esc(v.titre || v.id)}</h1><div class="sous">${esc(libelleVeille({ ...v, json: true, nb: v.sujets.length }))}</div></div></div>
    ${v.tldr ? `<p class="tldr">${esc(v.tldr)}</p>` : ""}
    ${attente ? `<div class="chutier">${attente}</div>` : ""}
    ${groupes(v.sujets).map(([titre, l]) => `${titre ? `<h3>${esc(titre)}</h3>` : ""}<div class="chutier">${l.map(tuile).join("")}</div>`).join("")}</div>`;
  viewer.querySelectorAll(".tuile[data-id]").forEach((b) => (b.onclick = () => ouvrirSujet(b.dataset.id)));

  const go = v.sujets.filter((s) => s.verdict === "go").length;
  const top = Math.max(0, ...v.sujets.map((s) => s.note || 0));
  const prods = v.sujets.filter((s) => etatSujet(s.id).production).length;
  insp.innerHTML = blocInsp(`<div class="insp-bloc"><div class="insp-titre">Rapport</div>
      <dl>
        <div class="prop"><dt>Date</dt><dd class="mono">${esc(v.date || v.id.split("_")[0])}</dd></div>
        <div class="prop"><dt>Moment</dt><dd>${esc(v.moment || v.id.split("_")[1] || "")}</dd></div>
        <div class="prop"><dt>Sujets</dt><dd class="mono">${v.sujets.length}</dd></div>
        <div class="prop"><dt>Verdict GO</dt><dd class="mono">${go}</dd></div>
        <div class="prop"><dt>Meilleure note</dt><dd class="mono">${fmtNote(top)}/10</dd></div>
        <div class="prop"><dt>En production</dt><dd class="mono">${prods}</dd></div>
      </dl></div>
    <div class="insp-bloc"><div class="insp-titre">Par où commencer</div>
      <p class="aide">Ouvre un sujet dans la bibliothèque ou le chutier, regarde ses vidéos au moniteur, puis valide-le ici pour que Claude écrive les scripts.</p>
      <p class="aide">Un sujet en tête ? Tape-le dans la barre du haut (${MAC ? "⌘" : "Ctrl"} K). Un script déjà écrit ? Bouton « Mon script ».</p></div>`);
}
function tuile(s) {
  const id = (s.videos || []).map((x) => ytId(x.url)).find(Boolean);
  const e = etatSujet(s.id);
  const etat = e.production ? "en production" : e.scripts?.length ? `${e.scripts.length} scripts` : e.valide ? "validé" : VERDICT[s.verdict] || "";
  return `<button class="tuile" data-id="${esc(s.id)}">
    <div class="vig">${id ? `<img loading="lazy" src="https://i.ytimg.com/vi/${id}/hqdefault.jpg" alt="">` : `<div class="sans">${ic("film")}</div>`}
      <span class="note ${s.verdict || ""}">${fmtNote(s.note)}</span></div>
    <div class="t">${esc(s.titre)}</div>
    <div class="m">${[formatDe(s).lib, s.sport, `${(s.videos || []).length} vidéos`, etat].filter(Boolean).map(esc).join(" · ")}</div></button>`;
}

/* ------------------------------------------------------------------ 1b. fiche sujet : moniteur source */
function vueDetail() {
  const s = sujet();
  if (!s) { viewer.innerHTML = ecranVide("alert", "Sujet introuvable", "Il a peut-être été retiré de ce rapport."); insp.innerHTML = ""; return; }
  if (s.script_perso) return aller(etatSujet().production ? "production" : "scripts");
  const e = etatSujet();
  const vids = s.videos || [];
  const idx = Math.min(S.video[s.id] || 0, Math.max(0, vids.length - 1));
  const sec = (titre, html) => (html ? `<h3>${titre}</h3>${html}` : "");
  viewer.innerHTML = `<div class="page">
    <div class="entete-page"><div><h1>${esc(s.titre)}</h1>
      <div class="ligne" style="margin-top:10px"><span class="puce">${ic("film")} short ${formatDe(s).lib}</span>
        ${s.verdict ? `<span class="puce ${s.verdict}">${VERDICT[s.verdict]}</span>` : ""}
        ${s.fiabilite ? `<span class="puce ${s.fiabilite}">${FIAB[s.fiabilite] || esc(s.fiabilite)}</span>` : ""}
        ${s.sport ? `<span class="puce">${esc(s.sport)}</span>` : ""}${s.echeance ? `<span class="puce">${esc(s.echeance)}</span>` : ""}</div></div></div>
    ${vids.length ? `<div id="moniteur"></div><div class="pellicule">${vids.map((v, i) => photogramme(v, i, i === idx)).join("")}</div>` : ""}
    <div class="colonnes">
      <div>
        ${sec("Résumé", s.resume ? `<p class="prose">${esc(s.resume)}</p>` : "")}
        ${sec("Les faits", s.faits?.length ? `<ul class="faits">${s.faits.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>` : "")}
        ${sec("Citations, clips parlés possibles", (s.citations || []).map((c) => `<div class="citation">${ic("quote")}<div>« ${esc(c.texte)} »
          <cite>${esc(c.auteur)}${c.source ? ", " + esc(c.source) : ""}${c.video ? ` · <a href="${esc(c.video)}" target="_blank">vidéo</a>` : ""}</cite></div></div>`).join(""))}
        ${sec("Pourquoi ça marche", s.pourquoi ? `<p class="prose">${esc(s.pourquoi)}</p>` : "")}
        ${sec("Angle vidéo", s.angle ? `<p class="prose">${esc(s.angle)}</p>` : "")}
      </div>
      <div>
        ${sec("Hooks proposés", (s.hooks || []).map((h) => `<div class="hook">${esc(h)}</div>`).join(""))}
        ${sec("Structure", s.structure?.length ? `<ol class="structure">${s.structure.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>` : "")}
        ${sec("Encore à trouver", s.a_trouver?.length ? `<ul class="faits">${s.a_trouver.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "")}
        ${sec("Photos d'incrustation", s.photos?.length ? `<div class="ligne">${s.photos.map((p) => `<span class="puce">${esc(p)}</span>`).join("")}</div>` : "")}
        ${sec("Sources", s.sources?.length ? `<ul class="sources">${s.sources.map((x) => `<li><a href="${esc(x.url)}" target="_blank">${esc(x.titre)} ${ic("ext")}</a></li>`).join("")}</ul>` : "")}
        ${sec("Fiabilité", s.fiabilite_detail ? `<p class="prose sous">${esc(s.fiabilite_detail)}</p>` : "")}
      </div>
    </div></div>`;
  if (vids.length) montrerVideo(s, idx);
  viewer.querySelectorAll(".photogramme").forEach((b) => (b.onclick = () => {
    S.video[s.id] = +b.dataset.i;
    viewer.querySelectorAll(".photogramme").forEach((x) => x.classList.toggle("ici", x === b));
    montrerVideo(s, +b.dataset.i);
  }));

  const sc = s.scores || {};
  const jauge = (k, lib) => (sc[k] == null ? "" : `<div class="jauge"><span>${lib}</span>
    <span class="piste">${Array.from({ length: 10 }, (_, i) => `<i class="${i < sc[k] ? "on" : ""}"></i>`).join("")}</span><b>${sc[k]}</b></div>`);
  insp.innerHTML = blocInsp(`<div class="insp-bloc">
      <div class="ligne" style="gap:12px;margin-bottom:12px"><div class="note ${s.verdict || ""}">${fmtNote(s.note)}</div>
        <div><div class="insp-titre" style="margin:0">Faire ce short ?</div><div class="sous" style="font-size:12px">Note de la veille sur 10</div></div></div>
      ${jauge("viral", "Potentiel viral")}${jauge("faits", "Solidité")}${jauge("images", "Images")}
    </div>
    <div class="insp-bloc">
      ${e.scripts?.length ? `<button class="btn grand" id="voir" style="margin-bottom:12px">${ic("script")} Ouvrir les ${e.scripts.length} scripts</button>` : ""}
      <label class="champ">Consigne pour les scripts
        <textarea id="consigne" rows="4" placeholder="Facultatif : angle, ton, clip à placer, hook à tester…"></textarea></label>
      <div class="ligne espace" style="margin:12px 0">
        <label class="champ" style="flex-direction:row;align-items:center;gap:8px">Nombre
          <select id="nombre"><option>2</option><option selected>3</option><option>4</option></select></label></div>
      <button class="btn principal grand" id="go" ${iaOk() ? "" : "disabled"}>${ic("check")} Valider et écrire les scripts</button>
      <p class="aide">Claude relit tes scripts modèles et le guide Max Parra, vérifie les faits douteux puis écrit les scripts (2 à 4 min).</p>
    </div>`);
  if ($("#voir")) $("#voir").onclick = () => aller("scripts");
  $("#go").onclick = () => lancerScripts($("#consigne").value, +$("#nombre").value, false);
}
function photogramme(v, i, ici) {
  const id = ytId(v.url);
  return `<button class="photogramme ${ici ? "ici" : ""}" data-i="${i}" title="${esc(v.titre)}">
    <div class="vig">${id ? `<img loading="lazy" src="https://i.ytimg.com/vi/${id}/mqdefault.jpg" alt="">` : ""}
      <span class="fmt">${v.parle ? ic("mic") : ""}${esc(v.format || "?")}</span></div>
    <div class="lg">${esc(v.titre)}</div></button>`;
}
function montrerVideo(s, i) {
  const v = s.videos[i], id = ytId(v.url);
  $("#moniteur").innerHTML = `<div class="moniteur ${v.format === "9:16" ? "vertical" : ""}">
      ${id ? `<img class="affiche" src="https://i.ytimg.com/vi/${id}/hqdefault.jpg" alt="">` : ""}
      <button class="lancer" aria-label="Lire la vidéo"><span>${ic("play", "plein")}</span></button></div>
    <div class="legende-moniteur"><span>${esc(v.titre)}${v.usage ? ` <span class="sous">· ${esc(v.usage)}</span>` : ""}
      ${v.alerte ? `<br><span class="alerte">${ic("alert")} ${esc(v.alerte)}</span>` : ""}</span>
      <a href="${esc(v.url)}" target="_blank" style="white-space:nowrap">Ouvrir ${ic("ext")}</a></div>`;
  $("#moniteur .lancer").onclick = () => {
    if (!id) return window.open(v.url, "_blank");
    $("#moniteur .moniteur").innerHTML = `<iframe src="https://www.youtube.com/embed/${id}?autoplay=1&rel=0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe>`;
  };
}
async function lancerScripts(consigne, nombre, ajouter) {
  try { await api("/api/scripts", { veille: S.vid, sujet: S.sid, consigne, nombre, ajouter }); } catch (e) { return toast(e.message, false); }
  await rafraichir();
  aller("scripts");
}

/* ------------------------------------------------------------------ 2. atelier de script */
function vueScripts() {
  const s = sujet(), e = etatSujet();
  if (!s) return vueDetail();
  const scripts = e.scripts || [];
  if (e.job_scripts && !S.polls["suivi" + e.job_scripts]) {
    S.polls["suivi" + e.job_scripts] = 1;
    suivreJob(e.job_scripts, (j) => {
      if (j.statut === "en_cours") { S.attenteScripts = j.id; if (S.vue === "scripts" && !$("#attente")) rendre(); }
    }, async (j) => {
      const attendait = S.attenteScripts;
      S.attenteScripts = null;
      if (j.statut === "erreur" && attendait) toast("Écriture des scripts ratée : " + j.erreur, false);
      await rafraichir(); if (S.vue === "scripts") rendre();
    }, 4000);
  }
  if (S.attenteScripts) {
    viewer.innerHTML = `<div class="ecran-vide" id="attente"><div><span class="anim" style="width:28px;height:28px;border-width:3px;margin-bottom:16px"></span>
      <h2>Claude écrit les scripts</h2><p>Relecture des scripts modèles, vérification des faits, rédaction. Compte 2 à 4 minutes, tu peux aller voir un autre sujet.</p></div></div>`;
    insp.innerHTML = blocInsp(`<div class="insp-titre">${esc(s.titre)}</div><p class="aide">Les scripts apparaîtront ici avec l'assistant d'écriture.</p>`);
    return;
  }
  if (!scripts.length) {
    viewer.innerHTML = ecranVide("script", "Pas encore de script", "Valide d'abord le sujet depuis sa fiche : Claude écrira 2 à 4 scripts.",
      `<button class="btn principal" id="ret">${ic("back")} Aller à la fiche</button>`);
    insp.innerHTML = "";
    $("#ret").onclick = () => aller("detail");
    return;
  }
  if (!scripts.find((x) => x.id === S.scid)) S.scid = e.choisi && scripts.find((x) => x.id === e.choisi) ? e.choisi : scripts[0].id;
  const sc = scripts.find((x) => x.id === S.scid);
  const prod = e.production;
  viewer.innerHTML = `
    <div class="pistes" role="tablist">${scripts.map((x, i) => `<button role="tab" class="piste-btn ${x.id === S.scid ? "actif" : ""}" data-id="${x.id}" aria-selected="${x.id === S.scid}">
        <b>${x.id === e.choisi ? ic("star", "plein") : ""}${i + 1}. ${esc(x.titre)}</b><small>${x.mots} mots</small></button>`).join("")}</div>
    <div class="editeur">
      <div class="outils-script">
        <div class="mecanisme">${esc(sc.mecanisme || "")}</div>
        <div class="ligne">
          <button class="btn petit fantome" id="plus">${ic("plus")} Un autre</button>
          <button class="btn petit fantome" id="refaire">${ic("refresh")} Tout réécrire</button>
          ${sc.versions?.length ? `<button class="btn petit fantome" id="annuler">${ic("undo")} Version précédente</button>` : ""}
          <button class="btn petit ${sc.id === e.choisi ? "choisi" : ""}" id="choisir">${ic("star", sc.id === e.choisi ? "plein" : "")} ${sc.id === e.choisi ? "Choisi" : "Choisir"}</button></div>
      </div>
      <div class="vumetre" id="vumetre"></div>
      <textarea class="texte-script" id="texte" spellcheck="false" aria-label="Texte du script">${esc(sc.texte)}</textarea>
      ${sc.clips?.length || sc.forces || sc.risques ? `<div class="notes-script">
        <div>${sc.clips?.length ? `<h3>Clips</h3><ul class="faits">${sc.clips.map((c) => `<li>${c.moment ? `<b>${esc(c.moment)}</b> : ` : ""}${esc(c.description)}${c.url ? ` <a href="${esc(c.url)}" target="_blank">${ic("ext")}</a>` : ""}</li>`).join("")}</ul>` : ""}</div>
        <div>${sc.forces ? `<h3>Forces</h3><p>${esc(sc.forces)}</p>` : ""}${sc.risques ? `<h3>À vérifier</h3><p>${esc(sc.risques)}</p>` : ""}</div></div>` : ""}
      <section class="rendu" aria-labelledby="titreRendu">
        <div class="ligne espace"><h2 id="titreRendu">Lancer la production</h2>
          ${prod ? `<button class="btn petit fantome" id="voirProd">${ic("film")} Voir la production en cours</button>` : ""}</div>
        <p class="aide" style="margin:6px 0 0">Voix off avec le clone ElevenLabs (crédits), transcription, clips vérifiés, photos, EDL, aperçu, puis brouillon CapCut. 20 à 45 min.</p>
        <div class="rendu-grille">
          <label class="champ">Nom du projet <input id="projet" class="mono" value="${esc(prod?.projet || s.id)}"></label>
          <label class="champ">Zoom des 16:9 <select id="zoom"><option value="">181 % (standard)</option><option value="1.5">150 % (plus large)</option><option value="2.0">200 % (plus serré)</option></select></label>
          <label class="champ">Musique <select id="musique"><option value="">Auto (skyfall en 1 min)</option><option>skyfall</option><option>cornfield</option><option>tiki</option><option>radiohead</option><option value="false">Aucune</option></select></label>
        </div>
        <textarea id="notes" rows="2" placeholder="Notes pour le montage (facultatif) : plan d'ouverture précis, musique, photo à mettre…"></textarea>
        <div class="bas"><label class="case"><input type="checkbox" id="modele"> Ajouter aux scripts modèles</label>
          <button class="btn principal" id="prod" ${iaOk() ? "" : "disabled"}>${ic("play", "plein")} Lancer la production</button></div>
      </section>
    </div>`;

  viewer.querySelectorAll(".piste-btn[data-id]").forEach((o) => (o.onclick = async () => { await sauverTexte(); S.scid = o.dataset.id; rendre(); }));
  const ta = $("#texte");
  const compter = () => vumetre($("#vumetre"), ta.value, formatDe(s).cible);
  ta.oninput = compter; compter();
  ta.onblur = sauverTexte;
  $("#choisir").onclick = async () => { await sauverTexte(); await api("/api/script", { veille: S.vid, sujet: S.sid, script: sc.id, choisi: sc.id }); await rafraichir(); rendre(); };
  if ($("#annuler")) $("#annuler").onclick = async () => { await api("/api/script", { veille: S.vid, sujet: S.sid, script: sc.id, annuler: true }); await rafraichir(); rendre(); };
  if ($("#voirProd")) $("#voirProd").onclick = () => aller("production");
  $("#plus").onclick = () => demander("Un script de plus", "Consigne pour ce nouveau script (facultatif)", (c) => lancerScripts(c, 1, true));
  $("#refaire").onclick = () => demander("Tout réécrire", "Qu'est-ce qui ne va pas ? (facultatif)", (c) => lancerScripts(c, 3, false));
  $("#prod").onclick = () => lancerProduction(sc);

  insp.innerHTML = panneauChat("Assistant d'écriture", `Sur « ${sc.titre} »`, sc.chat || [], sc.chat_attente,
    "Demande une retouche : « hook plus agressif », « raccourcis à 250 mots », « ajoute le clip de Mourinho en preuve », « vérifie la date du match ».",
    ["Hook plus percutant", "Raccourcis un peu", "Chute plus forte", "Plus parlé, moins écrit", "Vérifie les faits"]);
  brancherChat(async (t) => {
    if (sc.chat_attente) return;
    const j = await api("/api/chat", { veille: S.vid, sujet: S.sid, script: sc.id, message: t, texte: $("#texte").value });
    await rafraichir(); rendre();
    suivreJob(j.id, null, async () => { await rafraichir(); if (S.vue === "scripts") rendre(); });
  });
  if (sc.chat_attente && !S.polls["chat" + sc.id]) {
    S.polls["chat" + sc.id] = setTimeout(async () => { delete S.polls["chat" + sc.id]; await rafraichir(); if (S.vue === "scripts") rendre(); }, 3000);
  }
}
function vumetre(el, texte, CIBLE = FORMATS.long.cible) {
  const n = compterMots(texte), max = Math.round(CIBLE[1] * 1.25);
  const etat = n >= CIBLE[0] - 15 && n <= CIBLE[1] + 15 ? "ok" : n > CIBLE[1] + 15 ? "trop" : "";
  const clips = (texte.match(/\[CLIP/g) || []).length;
  el.className = "vumetre " + etat;
  el.innerHTML = `<b>${n}</b> mots
    <span class="echelle" title="Cible : ${CIBLE[0]} à ${CIBLE[1]} mots"><span class="cible" style="left:${(CIBLE[0] - 15) / max * 100}%;width:${(CIBLE[1] - CIBLE[0] + 30) / max * 100}%"></span>
      <span class="niveau" style="transform:scaleX(${Math.min(1, n / max)})"></span></span>
    <span class="mono">≈ ${Math.round(n / 4.5)} s</span>${clips ? `<span>· ${clips} clip${clips > 1 ? "s" : ""} parlé${clips > 1 ? "s" : ""}</span>` : ""}`;
}
async function sauverTexte() {
  const ta = $("#texte");
  const sc = (etatSujet().scripts || []).find((x) => x.id === S.scid);
  if (!ta || !sc || ta.value === sc.texte) return;
  await api("/api/script", { veille: S.vid, sujet: S.sid, script: sc.id, texte: ta.value });
  await rafraichir();
}

function panneauChat(titre, sous, chat, attente, vide, suggestions) {
  return `<div class="chat">
    <div class="pane-head"><h2>${esc(titre)}</h2><span class="sous" style="font-size:12px;margin-left:auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" id="modeChat">${esc(sous)}</span></div>
    <div class="pane-body" id="fil">${filChat(chat, attente, vide)}</div>
    <div class="suggestions" id="sugg">${suggestions.map((t) => `<button type="button">${esc(t)}</button>`).join("")}</div>
    <form class="saisie" id="formChat"><textarea id="msg" rows="1" aria-label="Ta demande" placeholder="Ta demande… (Entrée pour envoyer)" ${iaOk() ? "" : "disabled"}></textarea>
      <button class="btn principal" aria-label="Envoyer" ${iaOk() ? "" : "disabled"}>${ic("send")}</button></form></div>`;
}
function filChat(chat, attente, vide, texteAttente = "je réfléchis…") {
  return (chat.map((m) => `<div class="bulle ${m.role}">${m.role === "ia" ? md(m.x) : esc(m.x)}
      ${m.consigne ? `<span class="modif">${ic("send")} consigne transmise à l'agent</span>` : ""}
      ${m.modifie ? `<span class="modif">${ic("check")} ${S.vue === "production" ? "modification appliquée" : "script modifié"}</span>` : ""}</div>`).join("")
    || `<div class="chat-vide">${esc(vide)}</div>`)
    + (attente ? `<div class="bulle ia" id="filAttente"><span class="anim"></span> ${esc(texteAttente)}</div>` : "");
}
function brancherChat(envoyer) {
  const fil = $("#fil"); fil.scrollTop = fil.scrollHeight;
  const f = $("#formChat"), msg = $("#msg");
  $("#sugg").querySelectorAll("button").forEach((b) => (b.onclick = () => { msg.value = b.textContent; msg.focus(); }));
  msg.oninput = () => { msg.style.height = "auto"; msg.style.height = Math.min(160, msg.scrollHeight + 2) + "px"; };
  msg.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); f.requestSubmit(); } };
  f.onsubmit = async (e) => {
    e.preventDefault();
    const t = msg.value.trim();
    if (!t) return;
    try { await envoyer(t); } catch (err) { toast(err.message, false); }
  };
}

async function lancerProduction(sc) {
  await sauverTexte();
  const o = { zoom: $("#zoom").value, musique: $("#musique").value, notes: $("#notes").value.trim() };
  const projet = $("#projet").value.trim();
  const modele = $("#modele").checked;
  modale(`<h2>Lancer la production ?</h2>
    <p>Projet <code>shorts/${esc(projet)}</code> avec « ${esc(sc.titre)} » (${sc.mots} mots).</p>
    <p class="sous">La voix off consomme des crédits ElevenLabs. CapCut sera fermé le temps d'écrire le brouillon. Tu peux fermer l'app : le travail continue et tu le retrouves dans la file des montages.</p>
    <div class="pied-modale"><button class="btn fantome" data-fermer>Annuler</button><button class="btn principal" id="mok">${ic("play", "plein")} Lancer</button></div>`);
  $("#mok").onclick = async () => {
    fermerModale();
    try { await api("/api/production", { veille: S.vid, sujet: S.sid, script: sc.id, projet, options: o, modele_parfait: modele }); }
    catch (e) { return toast(e.message, false); }
    await rafraichir(); aller("production"); suivreMontages();
  };
}

/* ------------------------------------------------------------------ 3. production */
function vueProduction() {
  const s = sujet(), p0 = etatSujet().production;
  if (!s || !p0) {
    viewer.innerHTML = ecranVide("film", "Pas encore de production", "Choisis un script dans l'atelier, puis lance la production.",
      `<button class="btn principal" id="ret">${ic("script")} Aller aux scripts</button>`);
    insp.innerHTML = "";
    if ($("#ret")) $("#ret").onclick = () => aller("scripts");
    return;
  }
  const jeton = (S.jetonProd = (S.jetonProd || 0) + 1); // une seule boucle de suivi à la fois
  viewer.innerHTML = `<div class="prod">
    <section class="prod-journal" aria-label="Journal de l'agent">
      <div class="pane-head"><h2 class="mono" style="font-size:13px">${esc(p0.projet)}</h2>
        <span class="statut" id="statut"><span class="anim"></span> démarrage…</span>
        <button class="btn petit danger" id="stop" style="margin-left:auto">${ic("stop", "plein")} Arrêter</button></div>
      <div class="journal" id="journal"></div>
    </section>
    <section class="prod-moniteur" aria-label="Aperçu">
      <div class="cadre-916" id="cadre">L'aperçu 9:16 apparaîtra ici quand le montage sera rendu.</div>
      <div id="rapport"></div>
    </section></div>`;
  insp.innerHTML = panneauChat("IA du montage", s.titre, [], false, "", []);
  const journal = $("#journal");
  const vus = {};
  let enCours = true, attente = false, nChat = -1, dernierFini = null;

  $("#stop").onclick = async () => {
    const p = etatSujet().production;
    modale(`<h2>Arrêter le montage ?</h2><p class="sous">L'agent s'arrête tout de suite. Ce qui est déjà fait reste dans <code>shorts/${esc(p.projet)}</code>.</p>
      <div class="pied-modale"><button class="btn fantome" data-fermer>Continuer</button><button class="btn principal" id="mok">${ic("stop", "plein")} Arrêter</button></div>`);
    $("#mok").onclick = async () => { fermerModale(); await api("/api/arreter", { job: p.job }); tour(true); };
  };

  const ICONES = { bash: "bash", read: "read", write: "pen", edit: "pen", search: "search", web: "web" };
  const afficherJob = (j, titre) => {
    if (!j.flux) return;
    if (!(j.id in vus)) {
      vus[j.id] = 0;
      if (titre) { const d = document.createElement("div"); d.className = "separateur"; d.textContent = titre; journal.appendChild(d); }
    }
    const bas = journal.scrollTop + journal.clientHeight >= journal.scrollHeight - 30;
    j.flux.lignes.slice(vus[j.id]).forEach((l) => {
      const d = document.createElement("div");
      d.className = l.t;
      if (l.t === "outil") d.innerHTML = ic(ICONES[l.k] || "bash") + `<span>${esc(l.x)}</span>`;
      else d.textContent = l.x;
      journal.appendChild(d);
    });
    vus[j.id] = j.flux.n;
    if (bas) journal.scrollTop = journal.scrollHeight;
  };

  const rendreChat = (p) => {
    const chat = p.chat || [];
    attente = !!p.chat_attente;
    $("#modeChat").textContent = enCours ? "pendant le montage" : "montage fini";
    const sugg = enCours ? ["Tu en es où ?", "Quels clips as-tu gardés ?", "Change la musique", "Mets une photo de plus"]
      : ["Raccourcis le hook", "Change le 1er plan", "Ajoute une photo", "Musique plus calme"];
    if ($("#sugg").dataset.mode !== String(enCours)) {
      $("#sugg").dataset.mode = String(enCours);
      $("#sugg").innerHTML = sugg.map((t) => `<button type="button">${t}</button>`).join("");
      $("#sugg").querySelectorAll("button").forEach((b) => (b.onclick = () => { $("#msg").value = b.textContent; $("#msg").focus(); }));
    }
    if (chat.length === nChat && !attente === !$("#filAttente")) return;
    nChat = chat.length;
    const fil = $("#fil");
    fil.innerHTML = filChat(chat, attente, enCours
      ? "Pendant le montage, pose tes questions ou demande un changement : il est transmis à l'agent entre deux étapes. Ex : « pourquoi ce clip en ouverture ? », « prends plutôt le plan vertical de l'entraînement »."
      : "Le montage est fini. Demande une modification : l'agent la fait dans la même session et remet le brouillon dans CapCut. Ex : « coupe la phrase sur Séville », « musique plus fort au début ».",
      enCours ? "je regarde…" : "je modifie le montage… (suis le journal)");
    fil.scrollTop = fil.scrollHeight;
  };

  brancherChat(async (t) => {
    if (attente) return;
    if (!enCours && !confirm("L'agent va reprendre le montage pour ta demande (ça peut recoûter des crédits si la voix change). On y va ?")) return;
    $("#msg").value = "";
    await api("/api/prod_chat", { veille: S.vid, sujet: S.sid, message: t });
    tour(true);
  });

  let occupe = false;
  const tour = async (immediat) => {
    if (S.vue !== "production" || jeton !== S.jetonProd) return;
    if (occupe) { if (!immediat) setTimeout(tour, 3000); return; }
    occupe = true;
    try { await tourInterne(); } catch (e) { /* serveur occupé : on réessaie */ } finally { occupe = false; }
    if (!immediat) setTimeout(tour, enCours || attente ? 3000 : 8000);
  };
  const tourInterne = async () => {
    await rafraichir();
    const p = etatSujet().production;
    const jobs = p.jobs || [p.job];
    for (const [i, id] of jobs.entries()) {
      if (vus[id] !== undefined && id !== p.job) continue;
      const j = await api(`/api/job/${id}`);
      afficherJob(j, i ? `Modification : ${j.meta.demande || ""}` : "");
      if (id !== p.job) continue;
      enCours = j.statut === "en_cours";
      const st = $("#statut");
      st.className = "statut " + (j.statut === "termine" ? "ok" : j.statut === "erreur" ? "ko" : "");
      st.innerHTML = enCours ? `<span class="anim"></span> en cours · ${minutes(j)} min · ${vus[id]} étapes`
        : j.statut === "termine" ? `${ic("check")} terminé en ${minutes(j)} min` : j.statut === "arrete" ? "arrêté" : `${ic("alert")} erreur`;
      $("#stop").hidden = !enCours;
      if (!enCours && dernierFini !== j.id) {
        dernierFini = j.id;
        $("#cadre").innerHTML = `<video controls preload="metadata" src="/apercu/${encodeURIComponent(p.projet)}?v=${j.id}"></video>`;
        $("#cadre video").onerror = () => { $("#cadre").textContent = "Pas d'aperçu rendu pour ce projet."; };
        $("#rapport").innerHTML = `<div class="rapport">
          ${j.statut === "erreur" ? `<p style="color:var(--no)">${esc(j.erreur || "")}</p>` : ""}
          ${j.resultat ? md(j.resultat) : ""}
          <p class="sous">Brouillon CapCut : <code>${esc(p.projet)}</code> · détails dans <code>shorts/${esc(p.projet)}/_production.md</code></p></div>`;
      } else if (enCours) { dernierFini = null; }
    }
    rendreChat(p);
  };
  tour();
}

/* ------------------------------------------------------------------ recherche d'un sujet libre */
$("#formRecherche").onsubmit = async (e) => {
  e.preventDefault();
  const champ = $("#champRecherche"), texte = champ.value.trim();
  if (!texte) return;
  try { await api("/api/recherche", { texte, veille: S.vid }); } catch (err) { return toast(err.message, false); }
  champ.value = ""; champ.blur();
  S.onglet = "sujets"; memo("bibli", "sujets");
  toast("Claude documente « " + texte + " ». La fiche s'ouvrira toute seule (3 à 6 min).", true);
  suivreRecherches();
};
async function suivreRecherches() {
  let jobs = [];
  try { jobs = (await api("/api/jobs")).filter((j) => j && j.type === "recherche"); } catch (e) { return; }
  const avant = S.recherches.filter((j) => j.statut === "en_cours").length;
  S.recherches = jobs;
  const enCours = jobs.filter((j) => j.statut === "en_cours");
  if (avant !== enCours.length || enCours.length) { rendreBibli(); if (S.vue === "veille" && S.veille?.sujets) vueVeille(); }
  const vues = JSON.parse(memo("recherchesVues") || "[]");
  for (const j of jobs.filter((x) => x.statut !== "en_cours" && !vues.includes(x.id))) {
    vues.push(j.id);
    memo("recherchesVues", JSON.stringify(vues.slice(-50)));
    if (Date.now() / 1000 - (j.fin || 0) > 600) continue;  // vieux résultat : on ne saute pas dessus
    if (j.statut === "erreur") { toast("La recherche « " + j.meta.texte + " » a échoué : " + j.erreur, false); continue; }
    if (j.resultat) {
      S.veilles = await api("/api/veilles"); remplirChoixVeilles();
      location.hash = `/${j.resultat.veille}/${j.resultat.sujet}`;
      return;
    }
  }
  clearTimeout(S.pollRecherche);
  if (enCours.length) S.pollRecherche = setTimeout(suivreRecherches, 5000);
}

/* ------------------------------------------------------------------ boîtes */
const dlg = $("#modale");
function modale(html) {
  $("#modaleBoite").innerHTML = html;
  if (!dlg.open) dlg.showModal();
  dlg.querySelectorAll("[data-fermer]").forEach((b) => (b.onclick = fermerModale));
}
const fermerModale = () => dlg.open && dlg.close();
dlg.addEventListener("click", (e) => { if (e.target === dlg) fermerModale(); });
function demander(titre, label, ok) {
  modale(`<h2>${esc(titre)}</h2><textarea id="mq" rows="4" placeholder="${esc(label)}"></textarea>
    <div class="pied-modale"><button class="btn fantome" data-fermer>Annuler</button><button class="btn principal" id="mok">Lancer</button></div>`);
  $("#mq").focus();
  $("#mok").onclick = () => { const v = $("#mq").value; fermerModale(); ok(v); };
}

/* « Mon script » */
$("#btnScript").onclick = () => ouvrirMonScript();
function ouvrirMonScript() {
  if (!iaOk()) return toast("Connecte d'abord l'IA (voir le bandeau).", false);
  modale(`<h2>Envoyer ton script</h2>
    <p class="sous">Colle le texte de la voix off ou glisse un fichier .txt / .md. Pour un clip parlé, mets une ligne à part : <code>[CLIP Mbappé] la citation</code>.</p>
    <div class="formulaire">
      <label class="champ">Titre du sujet <input id="msTitre" placeholder="Ex : Mbappé recadré par Mourinho"></label>
      <label class="champ">Nom du projet <input id="msProjet" class="mono" placeholder="auto si vide"></label>
      <label class="champ large">Script <textarea id="msTexte" class="depot" placeholder="Cette réponse de … est la raison pour laquelle …"></textarea>
        <span class="vumetre" id="msCompteur"></span></label>
      <label class="champ large">Contexte pour l'agent (facultatif)
        <textarea id="msContexte" rows="2" placeholder="Liens YouTube à utiliser, plan d'ouverture voulu, photos, faits à vérifier…"></textarea></label>
      <label class="champ">Zoom des 16:9 <select id="msZoom"><option value="">181 % (standard)</option><option value="1.5">150 %</option><option value="2.0">200 %</option></select></label>
      <label class="champ">Musique <select id="msMusique"><option value="">Auto</option><option>skyfall</option><option>cornfield</option><option>tiki</option><option>radiohead</option><option value="false">Aucune</option></select></label>
    </div>
    <div class="pied-modale">
      <button class="btn fantome" data-fermer>Annuler</button>
      <button class="btn" id="msAtelier">${ic("script")} Ouvrir dans l'atelier</button>
      <button class="btn principal" id="msLancer">${ic("play", "plein")} Lancer le montage</button></div>`);
  const ta = $("#msTexte");
  const compter = () => vumetre($("#msCompteur"), ta.value);
  ta.oninput = compter; compter();
  ta.ondragover = (e) => { e.preventDefault(); ta.classList.add("survol"); };
  ta.ondragleave = () => ta.classList.remove("survol");
  ta.ondrop = async (e) => {
    e.preventDefault(); ta.classList.remove("survol");
    const f = e.dataTransfer.files[0];
    if (!f) return;
    ta.value = await f.text(); compter();
    if (!$("#msTitre").value) $("#msTitre").value = f.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ");
  };
  $("#msTitre").oninput = () => { $("#msProjet").placeholder = slugJs($("#msTitre").value) || "auto si vide"; };
  const envoyer = async (lancer, bouton) => {
    const corps = { texte: ta.value, titre: $("#msTitre").value, projet: $("#msProjet").value || $("#msTitre").value,
      contexte: $("#msContexte").value, lancer,
      options: { zoom: $("#msZoom").value, musique: $("#msMusique").value, notes: $("#msContexte").value.trim() } };
    bouton.disabled = true;
    let r;
    try { r = await api("/api/mon_script", corps); } catch (err) { bouton.disabled = false; return toast(err.message, false); }
    fermerModale();
    S.veilles = await api("/api/veilles"); remplirChoixVeilles();
    location.hash = `/${r.veille}/${r.sujet}/${r.lance ? "production" : "scripts"}`;
    suivreMontages();
  };
  $("#msLancer").onclick = (e) => envoyer(true, e.currentTarget);
  $("#msAtelier").onclick = (e) => envoyer(false, e.currentTarget);
  $("#msTitre").focus();
}
const slugJs = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 40);

/* veille à la demande */
$("#btnVeille").onclick = () => {
  if (!iaOk()) return toast("Connecte d'abord l'IA (voir le bandeau).", false);
  modale(`<h2>Nouvelle veille actu sport</h2>
    <p class="sous">Claude balaie l'actu des dernières 24 à 48 h, vérifie les faits et cherche les vidéos. La veille du jour se lance aussi toute seule chaque matin.</p>
    <label class="case" style="margin:12px 0"><input type="checkbox" id="mqJour" checked>
      Formule du jour : 4 shorts d'1 min (3 tennis, 1 foot) et 5 shorts de 25-30 s, avec un script écrit pour chacun</label>
    <textarea id="mq" rows="3" placeholder="Consigne (facultatif) : focus Sinner, un sujet Mbappé, pas de mercato…"></textarea>
    <div class="pied-modale"><button class="btn fantome" data-fermer>Annuler</button><button class="btn principal" id="mok">${ic("refresh")} Lancer la veille</button></div>`);
  $("#mq").focus();
  $("#mok").onclick = async () => {
    const consigne = $("#mq").value, quotidien = $("#mqJour").checked;
    fermerModale();
    const j = await api("/api/veille", { consigne, quotidien, forcer: false });
    memo("jobVeille", j.id);
    suivreVeille(j.id);
  };
};
function suivreVeille(id) {
  const b = $("#btnVeille"), g = $("#pbGauche");
  suivreJob(id, (j) => {
    if (j.statut !== "en_cours") return;
    b.disabled = true;
    g.innerHTML = `<span class="anim"></span> Veille en cours · ${minutes(j)} min · ${j.flux?.n || 0} étapes`;
  }, async (j) => {
    memo("jobVeille", "");
    b.disabled = !iaOk(); g.innerHTML = "";
    if (j.statut !== "termine") { if (j.statut === "erreur") toast("Veille ratée : " + j.erreur, false); return; }
    S.veilles = await api("/api/veilles"); remplirChoixVeilles();
    toast("Nouvelle veille prête.", true);
    location.hash = "/" + (j.meta.veille || S.veilles[0].id);
  }, 5000);
}

/* ------------------------------------------------------------------ file des montages */
async function suivreMontages() {
  clearTimeout(S.pollMontages);
  let items;
  try { items = await api("/api/productions"); } catch (e) { S.pollMontages = setTimeout(suivreMontages, 8000); return; }
  S.statutsMontages = S.statutsMontages || {};
  for (const x of items) {
    if (S.statutsMontages[x.job] === "en_cours" && x.statut !== "en_cours") {
      toast(x.statut === "termine" ? `${x.projet} : ${x.modif ? "modification faite" : "montage terminé, brouillon dans CapCut"}`
        : `${x.projet} : ${x.statut === "arrete" ? "arrêté" : "erreur"}`, x.statut === "termine",
        () => { location.hash = `/${x.veille}/${x.sujet}/production`; });
    }
    S.statutsMontages[x.job] = x.statut;
  }
  S.montages = items;
  rendreBibli();
  const n = items.filter((x) => x.statut === "en_cours").length;
  $("#pbDroite").innerHTML = items.length ? `<button class="pb-lien" id="pbFile">${n ? `<span class="anim"></span> ${n} montage${n > 1 ? "s" : ""} en cours` : `${ic("queue")} ${items.length} montage${items.length > 1 ? "s" : ""} récents`}</button>` : "";
  if ($("#pbFile")) $("#pbFile").onclick = () => { S.onglet = "montages"; memo("bibli", "montages"); rendreBibli(); };
  S.pollMontages = setTimeout(suivreMontages, n ? 4000 : 15000);
}

function toast(texte, ok, clic) {
  const d = document.createElement("button");
  d.className = "toast" + (ok ? "" : " ko");
  d.innerHTML = ic(ok ? "check" : "alert") + `<span>${esc(texte)}</span>`;
  d.onclick = () => { clic && clic(); d.remove(); };
  $("#toasts").appendChild(d);
  setTimeout(() => d.remove(), ok ? 8000 : 14000);
}

/* ------------------------------------------------------------------ clavier */
document.addEventListener("keydown", (e) => {
  const mod = MAC ? e.metaKey : e.ctrlKey;
  if (mod && e.key.toLowerCase() === "k") { e.preventDefault(); $("#champRecherche").focus(); }
  if (mod && ["1", "2", "3"].includes(e.key)) { e.preventDefault(); allerPage(["veille", "scripts", "production"][+e.key - 1]); }
});

/* ------------------------------------------------------------------ mini markdown */
function md(t) {
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\*(.+?)\*/g, "<i>$1</i>")
    .replace(/`(.+?)`/g, "<code>$1</code>").replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  let html = "", liste = false;
  for (const l of String(t).split("\n")) {
    const m = l.match(/^\s*[-*]\s+(.*)/);
    if (m) { if (!liste) { html += "<ul>"; liste = true; } html += `<li>${inline(m[1])}</li>`; continue; }
    if (liste) { html += "</ul>"; liste = false; }
    const h = l.match(/^(#{1,3})\s+(.*)/);
    if (h) html += `<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`;
    else if (l.trim() === "---") html += "<hr>";
    else if (l.trim()) html += `<p>${inline(l)}</p>`;
  }
  return html + (liste ? "</ul>" : "");
}

init();
