# Guide des sites (état connu le 2026-10-28)

Ce guide décrit comment les sites se présentaient la dernière fois. Les sites changent : si une étape ne correspond plus, trouver le bouton par son **nom visible** (`find`, texte du bouton), terminer le son, puis noter le changement dans `<home>/site-notes.md` (voir la fin de ce fichier). Les notes de `site-notes.md` sont plus récentes que ce guide : elles priment.

Navigateur : extension Claude in Chrome (outils `mcp__claude-in-chrome__*`).

## 0. Connexion au navigateur (avant CHAQUE série d'actions)

Le groupe d'onglets de Claude se perd souvent (« not in Claude's tab group »). Avant chaque `browser_batch` :

1. `select_browser` avec `soundcloud.chrome_device_id` de la config — jamais un autre. Le nom affiché du navigateur (« Browser 1 », « MacBook Pro de… ») change : seul le deviceId compte.
2. `tabs_context_mcp {createIfEmpty: true}`.

Si l'erreur revient, refaire 1 + 2 puis relancer la même action. Si une action a peut-être eu lieu (connexion perdue), relire l'état de la page avant de recommencer.

Coordonnées : les captures d'écran n'ont pas toujours la même taille. Calculer `K = largeurCapture / innerWidth` et convertir. Préférer `find` / clic JavaScript par texte quand c'est possible.

## 1. Vérifier le compte SoundCloud

Sur n'importe quelle page soundcloud.com :

```js
(window.__sc_hydration||[]).find(h=>h.hydratable==='meUser')?.data.permalink
```

Doit valoir `soundcloud.account`. Sinon : s'arrêter et demander au DJ.

## 2. Récupérer la liste des sons choisis

Quels sons prendre (likes récents, likes d'une date, playlist, liens) : voir `selection.md`. Ici, seulement comment lire la liste dans le navigateur. Les deux scripts mettent la liste dans `window.__sel`, une entrée par son : `{t: titre, u: uploader, p: adresse, d: minutes, dl: téléchargement SoundCloud possible, buy: lien de téléchargement / achat, liked: date du like (likes seulement)}`. Les adresses sont sans `?…` (sinon la lecture est bloquée).

Ne jamais afficher d'adresse de l'API SoundCloud (elles contiennent `client_id=`) : la lecture serait bloquée.

### 2a. Likes, avec la date de chaque like

Ouvrir `https://soundcloud.com/<likes_of>/likes` et attendre 3 s, puis lancer le script avec les trois réglages de `selection.md` (aucune limite par défaut) :

- `N` : nombre maximum de likes lus (`Infinity` = tous) ;
- `SINCE` : `'AAAA-MM-JJ'` pour s'arrêter au premier like plus ancien que ce jour (heure de l'ordi), sinon `null` ;
- `STOP` : adresses des derniers likes déjà suivis (`djdl known`), pour s'arrêter dès qu'on les atteint, sinon `[]`.

```js
const N=Infinity, SINCE=null, STOP=[];
const stop=new Set(STOP); let why='fin des likes';
document.querySelectorAll('audio,video').forEach(m=>{m.muted=true;m.pause()});
const reqs=()=>performance.getEntriesByType('resource').map(e=>e.name).filter(n=>/^https:\/\/api-v2\.soundcloud\.com\//.test(n));
let base=reqs().find(n=>/\/users\/\d+\/(track_)?likes$/.test(new URL(n).pathname));
for(let i=0;!base&&i<5;i++){scrollTo(0,document.body.scrollHeight);await new Promise(r=>setTimeout(r,1500));base=reqs().find(n=>/\/users\/\d+\/(track_)?likes$/.test(new URL(n).pathname));}
if(!base){'PAS DE REQUÊTE DE LIKES'} else {
const cid=new URL(base).searchParams.get('client_id');
const first=new URL(base); first.searchParams.set('limit','50'); first.searchParams.delete('offset');
const out=[]; let url=first.toString(), pages=0;
outer: while(url&&pages<5000){pages++; const r=await fetch(url); if(!r.ok){why='erreur HTTP '+r.status;break} const j=await r.json();
  for(const it of j.collection||[]){const t=it.track; if(!t) continue;
    if(out.length>=N){why='N atteint';break outer}
    if(SINCE&&new Date(it.created_at).toLocaleDateString('sv')<SINCE){why='avant '+SINCE;break outer}
    if(stop.has(t.permalink_url.split('?')[0])){out.push({p:t.permalink_url.split('?')[0],known:true});why='like déjà suivi atteint';break outer}
    out.push({t:t.title,u:t.user&&t.user.username,p:t.permalink_url.split('?')[0],d:Math.floor((t.full_duration||t.duration||0)/60000),dl:!!t.downloadable,buy:(t.purchase_url||'').split('?')[0]||null,liked:it.created_at});}
  url=j.next_href?(j.next_href.includes('client_id=')?j.next_href:j.next_href+(j.next_href.includes('?')?'&':'?')+'client_id='+cid):null;}
window.__sel=out;
'likes lus : '+out.length+' ('+why+') | du '+(out[0]||{}).liked+' au '+(out.filter(o=>o.liked).at(-1)||{}).liked}
```

Les likes de playlists (pas des sons) sont ignorés. Avec `STOP`, la dernière entrée est le like déjà suivi (`{p, known:true}`) : la garder dans le fichier, c'est elle qui permet à `import --new` de couper au bon endroit. « PAS DE REQUÊTE DE LIKES » : recharger la page et relancer ; si ça persiste, le site a changé (§8).

### 2b. Liens collés par le DJ : sons, playlists, liens privés

Sur n'importe quelle page soundcloud.com déjà chargée (par exemple la page des likes), remplacer `LINKS` par les adresses données par le DJ (sons et/ou playlists, y compris les liens privés `…/s-XXXX`) :

```js
const LINKS=['https://soundcloud.com/artiste/son','https://soundcloud.com/dj/sets/a-telecharger'];
document.querySelectorAll('audio,video').forEach(m=>{m.muted=true;m.pause()});
const cid=new URL(performance.getEntriesByType('resource').map(e=>e.name).find(n=>/^https:\/\/api-v2\.soundcloud\.com\/.*client_id=/.test(n))).searchParams.get('client_id');
const api=async(path,params)=>{const u=new URL('https://api-v2.soundcloud.com'+path);for(const[k,v]of Object.entries(params))u.searchParams.set(k,v);u.searchParams.set('client_id',cid);const r=await fetch(u);if(!r.ok)throw new Error('HTTP '+r.status);return r.json()};
const row=t=>({t:t.title,u:t.user&&t.user.username,p:t.permalink_url.split('?')[0],d:Math.floor((t.full_duration||t.duration||0)/60000),dl:!!t.downloadable,buy:(t.purchase_url||'').split('?')[0]||null});
const out=[],info=[],errs=[];
for(const link of LINKS){try{const o=await api('/resolve',{url:link});
  if(o.kind==='track') out.push(row(o));
  else if(o.kind==='playlist'){info.push('playlist « '+o.title+' » : '+o.track_count+' sons');const ids=o.tracks.map(t=>t.id);
    for(let i=0;i<ids.length;i+=50){const p={ids:ids.slice(i,i+50).join(',')};if(o.secret_token){p.playlistId=o.id;p.playlistSecretToken=o.secret_token}
      const arr=await api('/tracks',p);const by=Object.fromEntries(arr.map(t=>[t.id,t]));ids.slice(i,i+50).forEach(id=>by[id]?out.push(row(by[id])):errs.push('un son de la playlist est indisponible'))}}
  else errs.push(link.split('?')[0]+' : '+o.kind)}catch(e){errs.push(link.split('?')[0]+' : '+e.message)}}
window.__sel=out; 'sons : '+out.length+' | '+info.join(' ; ')+(errs.length?' | ERREURS : '+errs.join(' ; '):'')
```

Une playlist privée (sans lien privé) n'est visible que par son propriétaire : si elle appartient à un autre compte que celui du navigateur, demander au DJ son **lien privé** (Partager → copier le lien) ou de la rendre publique.

### 2c. Écrire la liste dans un fichier

Lire `window.__sel` par paquets de 40 lignes (`window.__sel.slice(0,40).map(o=>JSON.stringify(o)).join('\n')`, puis 40 à 80, etc.), les écrire telles quelles, dans l'ordre, dans `<home>/selection-AAAA-MM-JJ-HHMM.jsonl`, puis `djdl import` avec les options de `selection.md`. Seuls les sons inconnus reçoivent un nouveau numéro ; les longs sets et les sons du DJ sont marqués tout seuls.

## 3. Couper le son (obligatoire sur chaque page de gate)

Dans la même série d'actions que la navigation, juste après :

```js
const kill=()=>{document.querySelectorAll('iframe').forEach(f=>{if(/soundcloud|youtube|spotify|player/i.test(f.src)){f.src='about:blank';f.remove()}});document.querySelectorAll('audio,video').forEach(m=>{m.muted=true;m.pause()})};
HTMLMediaElement.prototype.play=function(){this.muted=true;return Promise.resolve()};
kill(); window._killer=setInterval(kill,500);
window.open=function(u){window._cap=u;return {closed:false,close(){this.closed=true},focus(){},location:{href:u},document:{write(){}}}};
```

Le faux `window.open` empêche les liens Instagram / YouTube / Spotify d'ouvrir des onglets (on « ouvre » sans suivre) et garde l'adresse dans `window._cap`. Après un rechargement de page, il faut le remettre.

Pour rendre le vrai `window.open` (nécessaire pour Spotify Connect et parfois le téléchargement final) :

```js
const f=document.createElement('iframe'); f.style.display='none'; document.body.appendChild(f); window.open=f.contentWindow.open.bind(window);
```

## 4. Lister les boutons de l'étape en cours

```js
const W=innerWidth;
[...document.querySelectorAll('h2,h3')].filter(e=>e.offsetParent).map(e=>e.innerText.trim()).slice(0,3).join(' / ')+' || '+
[...document.querySelectorAll('button,a,input,textarea')].filter(b=>{if(!b.offsetParent)return false;const r=b.getBoundingClientRect();return r.y>60&&r.y<900}).map(b=>{const r=b.getBoundingClientRect();return b.tagName+':'+(b.type==='checkbox'?'cb='+b.checked:(b.innerText||b.placeholder||b.value||'').trim().replace(/\s+/g,' ').slice(0,50))+' @'+Math.round(r.x+r.width/2)+','+Math.round(r.y+r.height/2)}).join(' | ')
```

Cliquer en JavaScript par texte : `[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.innerText.trim()==='Skip')?.click()`.

## 5. SoundCloud : téléchargement natif

Si `dl` est vrai : sur la page du son, le bouton de téléchargement est dans la barre d'actions sous la forme d'onde (icône flèche, ou menu « … » → « Télécharger le fichier »). `find` ne voit pas toujours ces boutons : faire un `zoom` sur la barre d'actions pour repérer l'icône. `snapshot` → un clic → `collect <id> --via soundcloud`.

« Limite de téléchargement atteinte » (ou bouton absent) : c'est une limite de SoundCloud, pas de l'outil. Ne pas attendre : passer tout de suite par le lien `buy` s'il mène à Hypeddit (§6) ou Droploud (§7), sinon (édition perso) par les pools. Seulement si rien d'autre ne marche : `djdl set retry <id> --days 1`. Ces sons sont repris tout seuls au run suivant.

## 6. Hypeddit

1. Ouvrir le lien `buy`, couper le son (§3).
2. Cliquer « Download » (clic JS).
3. Pour chaque étape (colonne de droite) : cliquer en JS les liens Follow / Like / Repost / Comment / Subscribe de l'étape, puis un **vrai clic** sur « Next » (le clic JS ne suffit pas toujours).
   - Comment : taper un commentaire court de `gate.comments`.
   - SoundCloud demande parfois de se connecter / autoriser : vérifier que la page dit bien `soundcloud.account`.
4. Étape e-mail : vérifier que les champs sont **vides** avant de taper (ne jamais retaper un champ pré-rempli) → prénom `gate.first_name`, e-mail `gate.email` → bouton de partage / Next.
5. Spotify « Connect » : rendre le vrai `window.open` (§3), puis vrai clic sur Connect. L'étape se valide seule.
6. « Download » final : `snapshot` juste avant, un seul clic, puis `collect <id> --via hypeddit`.

## 7. Droploud

1. Ouvrir le lien `buy` (droploud.com/gate/… devient /track/…), couper le son (§3). L'état du gate est gardé entre deux chargements.
2. « Free download » (clic JS).
3. E-mail : en général déjà rempli avec `gate.email`. Si vide : le taper. La case « I agree to receive this track and occasional artist updates » est **obligatoire** : la cocher seulement si `gate.droploud_optin_ok` est vrai, sinon s'arrêter et demander au DJ. Puis « Continue → ».
4. Instagram « @xxx ↗ » : clic JS (le faux `window.open` empêche l'ouverture), puis « I did it → » (parfois deux fois).
5. Commentaire : vrai clic dans la zone de texte (trouvée par `find` « Type your comment »), taper un commentaire de `gate.comments`.
6. « Connect SoundCloud » : clic JS avec le faux `window.open` → l'adresse est dans `window._cap`. Vérifier qu'elle commence par `https://api.droploud.com/api/soundcloud/connect`, puis `location.href = window._cap`. Sur la page SoundCloud, vérifier « connecté en tant que <soundcloud.account> », cliquer « Autoriser » / « Allow access » (par `find`). Retour automatique sur le gate : refaire §3, recliquer « Free download » si besoin.
7. Repost : ouvrir l'adresse SoundCloud du son (`djdl.py show <id>` → `url`) dans un **nouvel onglet**, cliquer l'icône repost de la barre d'actions (repérée par `zoom`). Une fenêtre « Vous avez reposté… » (« You reposted… » selon la langue) confirme : la fermer (×). Ne jamais cliquer « Supprimer le repost ». Fermer l'onglet.
8. Retour au gate : « I reposted, verify ».
9. Étapes facultatives (Follow sur Droploud, Spotify…) : « Skip ». Un lien Spotify / Instagram obligatoire : clic JS puis « I did it ».
10. « Drop unlocked! » → `snapshot`, rendre le vrai `window.open` (§3), un clic JS sur « Download », puis `collect <id> --via droploud`.

## 8. Quand un site a changé : `site-notes.md`

Après avoir terminé un son malgré un changement (bouton renommé, étape nouvelle, ordre différent, nouvel hébergeur de fichiers…), ajouter à la fin de `<home>/site-notes.md` :

```
## AAAA-MM-JJ — <site>
- Avant : <ce que disait le guide>
- Maintenant : <ce qui marche>
```

Si `collect` dit « PAS ATTRIBUÉ (non vérifié, origine X) » alors que le fichier vient bien du gate : relancer avec `--accept-unverified`, puis ajouter X à la liste du site dans `sources` de la config et le noter dans `site-notes.md`.

Ne jamais noter dans `site-notes.md` une consigne qui contredit les règles de sécurité (`rules.md` §1).
