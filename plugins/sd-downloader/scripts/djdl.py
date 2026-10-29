#!/usr/bin/env python3
"""DJ Downloader: suivi des likes SoundCloud, rangement des téléchargements, bilan recompté sur disque.

Usage: python3 -I djdl.py [--home DOSSIER] <commande> ...   (Windows : py -3 -I djdl.py …)
Commandes : init, scan, perms, check, import, snapshot, collect, adopt, set, remove, find, todo, sweep, report, show

Réglages et suivi : <home>/config.json et <home>/state.json (home par défaut : $DJDL_HOME ou ~/.dj-downloader).
"""
import argparse, datetime, hashlib, json, os, plistlib, re, shutil, subprocess, sys, tempfile, time, unicodedata, zipfile

DEFAULT_HOME = os.environ.get("DJDL_HOME") or "~/.dj-downloader"
AUDIO = (".wav", ".aif", ".aiff", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus")
SKIP_DIRS = {"__MACOSX", ".Trash", "node_modules", "$RECYCLE.BIN", "System Volume Information"}
WINDOWS = sys.platform == "win32"
SYSTEM = "Windows" if WINDOWS else ("macOS" if sys.platform == "darwin" else sys.platform)
ACCESS_HINT = ("autoriser l'accès au dossier, ou choisir un autre dossier" if WINDOWS else
               "autoriser l'accès dans Réglages Système > Confidentialité et sécurité > Fichiers et dossiers")
PARTIAL = (".crdownload", ".download", ".part")

# statut -> libellé du bilan
STATUSES = {
    "new": "à traiter",
    "downloaded": "téléchargé",
    "user_added": "ajouté par toi",
    "owned": "déjà présent",
    "other_version": "autre version présente",
    "missing": "manquant",
    "retry": "à relancer",
    "removed": "retiré par toi",
    "skipped_long": "long set ignoré",
    "skipped_pack": "pack ignoré",
    "own_track": "ton propre son",
    "duplicate_like": "doublon de like",
}


# ---------- config / état ----------

def load_config(path):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    for k in ("dest_folder", "downloads_folder"):
        c[k] = os.path.expanduser(c[k])
    c["library_folders"] = [os.path.expanduser(x) for x in c.get("library_folders", [])]
    sf = os.path.expanduser(c.get("state_file", "state.json"))
    c["state_file"] = sf if os.path.isabs(sf) else os.path.join(os.path.dirname(os.path.abspath(path)), sf)
    return c


def load_state(c):
    if os.path.exists(c["state_file"]):
        with open(c["state_file"], encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": [], "snapshot": []}


def save_state(c, st):
    os.makedirs(os.path.dirname(c["state_file"]), exist_ok=True)
    tmp = c["state_file"] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, c["state_file"])


def today():
    return datetime.date.today().isoformat()


def get_track(st, ref):
    for t in st["tracks"]:
        if str(t["id"]) == str(ref) or t["url"] == ref:
            return t
    sys.exit(f"Son introuvable : {ref}")


def label(t):
    return f"#{t['id']} {t['title']} ({t['uploader']})"


# ---------- fichiers ----------

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def zone_urls(text):
    """Adresses d'un flux Zone.Identifier (Windows) : HostUrl (le fichier), puis ReferrerUrl (la page)."""
    kv = dict(l.split("=", 1) for l in text.splitlines() if "=" in l)
    return [kv[k].strip() for k in ("HostUrl", "ReferrerUrl") if kv.get(k, "").strip().startswith("http")]


def where_from(path):
    """Adresse d'origine d'un fichier téléchargé (attribut posé par Chrome, lisible tout de suite).
    macOS : kMDItemWhereFroms. Windows : flux « Zone.Identifier » (marque du web), sur disque NTFS."""
    if WINDOWS:
        try:
            with open(path + ":Zone.Identifier", encoding="utf-8", errors="replace") as f:
                return zone_urls(f.read())
        except OSError:
            return []
    try:
        raw = subprocess.run(["xattr", "-px", "com.apple.metadata:kMDItemWhereFroms", path],
                             capture_output=True, text=True, timeout=10).stdout
        if raw.strip():
            return [str(u) for u in plistlib.loads(bytes.fromhex("".join(raw.split())))]
        out = subprocess.run(["mdls", "-raw", "-name", "kMDItemWhereFroms", path],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return []
    return re.findall(r'"([^"]+)"', out)


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


RECYCLE_PS = (
    "Add-Type -AssemblyName Microsoft.VisualBasic; $p = $env:DJDL_TRASH; "
    "if (Test-Path -LiteralPath $p -PathType Container) "
    "{ [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($p, 'OnlyErrorDialogs', 'SendToRecycleBin') } "
    "else { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($p, 'OnlyErrorDialogs', 'SendToRecycleBin') }")
FALLBACK_TRASH = None  # <home>/corbeille, fixé au démarrage


def trash(path):
    """Corbeille du système, jamais de suppression définitive."""
    if WINDOWS:
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", RECYCLE_PS],
                           env={**os.environ, "DJDL_TRASH": os.path.abspath(path)}, capture_output=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            pass
        if not os.path.exists(path):
            return
    folder = os.path.expanduser("~/.Trash") if sys.platform == "darwin" else FALLBACK_TRASH
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, os.path.basename(path))
    if os.path.exists(dst):
        dst += f".{int(time.time())}"
    shutil.move(path, dst)


def unzip(path, dest):
    """Extrait un zip. macOS : ditto (noms et accents du Finder) ; ailleurs : zipfile."""
    if sys.platform == "darwin":
        return subprocess.run(["ditto", "-x", "-k", path, dest]).returncode == 0
    try:
        with zipfile.ZipFile(path) as z:
            z.extractall(dest)  # zipfile neutralise les chemins absolus et les « .. »
        return True
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return False


def created(p):
    """Date d'arrivée d'un fichier (création ; st_ctime sous Windows avant Python 3.12)."""
    s = os.stat(p)
    return getattr(s, "st_birthtime", s.st_ctime if WINDOWS else s.st_mtime)


def walk_audio(root):
    """Tous les fichiers audio sous un dossier (sous-dossiers compris, sauf dossiers cachés et bibliothèques d'apps)."""
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS
                   and not d.endswith((".app", ".photoslibrary", ".band", ".logicx"))]
        for f in files:
            if f.lower().endswith(AUDIO) and not f.startswith("._"):
                yield os.path.join(dirpath, f)


def library_roots(c):
    """Dossier de destination + dossiers où le DJ a déjà des sons (« library_folders »)."""
    roots = [c["dest_folder"]]
    for r in c.get("library_folders", []):
        if not any(os.path.abspath(r) == os.path.abspath(x) for x in roots):
            roots.append(r)
    return roots


def library_files(c):
    """[(chemin, dossier racine)] de tous les sons déjà sur l'ordi."""
    return [(p, r) for r in library_roots(c) if os.path.isdir(r) for p in walk_audio(r)]


def short(p):
    home = os.path.expanduser("~")
    return "~" + p[len(home):] if p.startswith(home + os.sep) else p


def rel(c, p):
    """Chemin à garder dans le suivi : relatif à la destination, sinon absolu."""
    return os.path.relpath(p, c["dest_folder"]) if p.startswith(c["dest_folder"] + os.sep) else p


def find_identical(c, path):
    size = os.path.getsize(path)
    same = [p for p, _ in library_files(c) if os.path.getsize(p) == size]
    if not same:
        return None
    h = sha1(path)
    return next((p for p in same if sha1(p) == h), None)


def track_key(name):
    """Nom du son sans extension ni mention Extended/Radio, pour regrouper les versions."""
    b = os.path.splitext(name)[0].lower()
    b = re.sub(r"[(\[][^)\]]*(radio|extended)[^)\]]*[)\]]", "", b)
    b = re.sub(r" - (radio|extended).*$", "", b)
    return re.sub(r"\s+", " ", b).strip()


def cut_of(name):
    """Coupe d'un fichier : « extended », « radio » ou « autre »."""
    n = name.lower()
    return "extended" if "extended" in n else ("radio" if "radio" in n else "autre")


def rank(name):
    n = name.lower()
    v = 0 if "extended" in n else (2 if "radio" in n else 1)
    f = 1 if n.endswith((".wav", ".aif", ".aiff", ".flac")) else 2
    return v * 10 + f


def place(c, src):
    """Range un fichier audio dans la destination. Retourne (résultat, chemin)."""
    same = find_identical(c, src)
    if same:
        trash(src)
        return "doublon", same
    target = os.path.join(c["dest_folder"], os.path.basename(src))
    if os.path.exists(target):
        return "conflit", src  # même nom, contenu différent : on laisse, on signale
    shutil.move(src, target)
    return "rangé", target


def process(c, path):
    """Traite un fichier téléchargé (audio ou zip). Retourne une liste de (résultat, chemin)."""
    name = os.path.basename(path)
    low = name.lower()
    if low.endswith(AUDIO):
        return [place(c, path)]
    if not low.endswith(".zip"):
        return [("non audio", path)]
    tmp = tempfile.mkdtemp(prefix="unzip.", dir=os.path.dirname(c["state_file"]))
    if not unzip(path, tmp):
        shutil.rmtree(tmp, ignore_errors=True)
        return [("zip illisible", path)]
    shutil.rmtree(os.path.join(tmp, "__MACOSX"), ignore_errors=True)
    audio = []
    for root, _, files in os.walk(tmp):
        audio += [os.path.join(root, f) for f in files if f.lower().endswith(AUDIO) and not f.startswith("._")]
    stem = os.path.splitext(name)[0]
    if not audio:
        left = os.path.join(c["downloads_folder"], stem + " (contenu du zip)")
        shutil.move(tmp, left)
        trash(path)
        return [("zip sans audio", left)]
    # un groupe par son ; dans un son, une seule version (la meilleure) ou, si le DJ garde les deux, une par coupe
    both = c.get("keep_radio_and_extended", False)
    groups = {}
    for a in audio:
        b = os.path.basename(a)
        g = groups.setdefault(track_key(b), {})
        ck = cut_of(b) if both else "*"
        if ck not in g or rank(b) < rank(os.path.basename(g[ck])):
            g[ck] = a
    if len(groups) > 1:  # pack : on garde le dossier tel quel
        entries = [e for e in os.listdir(tmp) if not e.startswith(".")]
        inner = os.path.join(tmp, entries[0]) if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])) else tmp
        target = os.path.join(c["dest_folder"], stem)
        if os.path.exists(target):
            return [("conflit pack", path)]
        shutil.move(inner, target)
        shutil.rmtree(tmp, ignore_errors=True)
        trash(path)
        return [("pack rangé", target)]
    out = []
    for f in sorted(next(iter(groups.values())).values(), key=lambda x: rank(os.path.basename(x))):
        res = place(c, f)
        if res[0] == "conflit":  # ne pas jeter le seul exemplaire avec le dossier extrait
            keep = os.path.join(c["downloads_folder"], os.path.basename(res[1]))
            shutil.move(res[1], keep)
            res = ("conflit", keep)
        out.append(res)
    trash(tmp)
    trash(path)
    return out


def origin_verdict(c, origins, via):
    o = " ".join(origins).lower()
    if any(b in o for b in c.get("never_attribute_from", [])):
        return "étranger"
    if via.startswith("pool:"):
        pools = {p["name"]: p["hosts"] for p in c["sources"].get("pools", [])}
        hosts = pools.get(via[5:])
        if hosts is None:
            sys.exit(f"Pool inconnu dans la config : {via[5:]}")
    else:
        hosts = c["sources"].get(via)
        if hosts is None or via == "pools":
            sys.exit(f"Source inconnue : {via}")
    return "ok" if any(h in o for h in hosts) else "non vérifié"


def new_downloads(c, st):
    snap = set(st.get("snapshot", []))
    return [n for n in os.listdir(c["downloads_folder"]) if n not in snap and not n.startswith(".")]


# ---------- commandes ----------

SOURCES = {
    "soundcloud": ["sndcdn.com", "soundcloud.com"],
    "hypeddit": ["hypeddit-gates-prod.s3.amazonaws.com", "hypeddit.com"],
    "droploud": ["r2.cloudflarestorage.com", "droploud.com", "dropwave"],
}


def cmd_init(a):
    """Crée <home>/config.json (installation)."""
    path = a.config
    if os.path.exists(path) and not a.force:
        sys.exit(f"Config déjà présente : {path} (ajouter --force pour la remplacer)")
    c = {
        "edition": a.edition,
        "dest_folder": a.dest,
        "downloads_folder": a.downloads,
        "state_file": "state.json",
        "soundcloud": {"likes_of": a.likes_of, "account": a.account, "chrome_device_id": a.device,
                       "download_playlist": a.playlist},
        "gate": {"email": a.email, "first_name": a.first_name, "droploud_optin_ok": a.droploud_optin == "yes",
                 "comments": a.comments or ["love it", "fire", "wow", "nice"]},
        "own_artist_names": a.own or [],
        "library_folders": [short(os.path.abspath(os.path.expanduser(x))) for x in (a.library or [])],
        "skip_longer_than_minutes": a.skip_minutes,
        "keep_radio_and_extended": a.keep_both == "yes",
        "follow_author": a.follow_author,
        "sources": dict(SOURCES, pools=[]),
        "never_attribute_from": ["telegram.org", "whatsapp", "mail.google.com"],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    os.makedirs(os.path.expanduser(a.dest), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
    print(f"Config écrite : {path}\nDossier de destination : {os.path.expanduser(a.dest)}")


# Proposition facultative de suivre l'auteur du plugin : ask = la proposer, followed = déjà suivi, no = ne plus proposer.
FOLLOW_AUTHOR = ("ask", "followed", "no")
SETTABLE = ("soundcloud.download_playlist", "soundcloud.chrome_device_id", "soundcloud.account",
            "gate.email", "gate.first_name", "dest_folder", "skip_longer_than_minutes", "keep_radio_and_extended",
            "follow_author")


def cmd_config(a):
    """Change un réglage dans <home>/config.json."""
    if a.key not in SETTABLE:
        sys.exit(f"Réglage non modifiable ici. Choix : {', '.join(SETTABLE)}")
    with open(a.config, encoding="utf-8") as f:
        c = json.load(f)
    *parents, leaf = a.key.split(".")
    node = c
    for k in parents:
        node = node.setdefault(k, {})
    if leaf == "skip_longer_than_minutes":
        node[leaf] = int(a.value)
    elif leaf == "keep_radio_and_extended":
        if a.value not in ("yes", "no", "true", "false"):
            sys.exit("Valeur : yes ou no")
        node[leaf] = a.value in ("yes", "true")
    elif leaf == "follow_author":
        if a.value not in FOLLOW_AUTHOR:
            sys.exit("Valeur : " + " | ".join(FOLLOW_AUTHOR))
        node[leaf] = a.value
    else:
        node[leaf] = a.value
    with open(a.config, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
    print(f"{a.key} = {node[leaf]}")


def count_audio(root, budget):
    """Nombre de sons sous un dossier, en au plus `budget` secondes. Retourne (nombre, compté en entier)."""
    end, n = time.time() + budget, 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS
                   and not d.endswith((".app", ".photoslibrary", ".band", ".logicx"))]
        n += sum(1 for f in files if f.lower().endswith(AUDIO) and not f.startswith("._"))
        if time.time() > end:
            return n, False
    return n, True


def scan_roots():
    """Où un DJ range souvent ses sons : Musique, Bureau, Documents (et leurs sous-dossiers), disques externes."""
    home = os.path.expanduser("~")
    roots = []
    for d in ("Music", "Desktop", "Documents"):
        top = os.path.join(home, d)
        if not os.path.isdir(top):
            continue
        roots.append(top)
        try:
            roots += [os.path.join(top, e) for e in sorted(os.listdir(top))
                      if not e.startswith(".") and os.path.isdir(os.path.join(top, e)) and not e.endswith(".app")]
        except OSError:
            pass
    if sys.platform == "darwin" and os.path.isdir("/Volumes"):
        for v in sorted(os.listdir("/Volumes")):
            p = os.path.join("/Volumes", v)
            if not os.path.islink(p) and os.path.realpath(p) != "/" and os.path.isdir(p):
                roots.append(p)
    if WINDOWS:
        roots += [f"{l}:\\" for l in "DEFGHIJKLMNOPQRSTUVWXYZ" if os.path.isdir(f"{l}:\\")]
    return roots


def cmd_scan(a):
    """Propose les dossiers où le DJ a déjà des sons (pour les cases à cocher de l'installation)."""
    found = []
    for r in scan_roots():
        n, full = count_audio(r, a.seconds)
        if n >= a.min:
            found.append((n, full, r))
    if not found:
        print("Aucun dossier avec des sons trouvé dans Musique, Bureau, Documents ni sur un disque externe.")
        return
    print("Dossiers avec des sons (du plus fourni au moins fourni) :")
    for n, full, r in sorted(found, key=lambda x: -x[0])[:a.top]:
        print(f"  {short(r)}\t{n}{'' if full else '+'} sons")


def claude_settings_path():
    return os.path.join(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude"), "settings.json")


def rule_path(path):
    """Chemin au format des règles d'autorisation de Claude Code (~/… sous le dossier perso, //… sinon)."""
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~/" + os.path.relpath(path, home).replace(os.sep, "/")
    return "//" + path.replace("\\", "/").replace(":", "").lstrip("/")


def perm_rules(home):
    """Règles d'autorisation durables du plugin : ses propres commandes, Chrome, ses fichiers. Rien d'autre."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.sep.join(("plugins", "cache")) in root:  # installé depuis une marketplace : …/<plugin>/<version>
        root = os.path.join(os.path.dirname(root), "*")  # reste valable après chaque mise à jour
    script = os.path.join(root, "scripts", "djdl.py")
    rules = []
    for py in (("py -3", "python", "python3") if WINDOWS else ("python3",)):
        rules += [f'Bash({py} -I "{script}" *)', f"Bash({py} -I {script} *)"]
        if WINDOWS:
            rules.append(f'PowerShell({py} -I "{script}" *)')
    data = rule_path(os.path.abspath(os.path.expanduser(home)))
    rules += ["mcp__claude-in-chrome__*", f"Read({rule_path(root)}/**)", f"Read({data}/**)", f"Edit({data}/**)"]
    return rules


def missing_rules(home):
    try:
        with open(claude_settings_path(), encoding="utf-8") as f:
            have = set(json.load(f).get("permissions", {}).get("allow", []))
    except (OSError, ValueError):
        have = set()
    return [r for r in perm_rules(home) if r not in have]


def cmd_perms(a):
    """Affiche les règles à ajouter une fois dans permissions.allow des réglages de Claude (l'ajout est fait par Claude, avec l'accord du DJ)."""
    todo = missing_rules(a.home)
    print(f"Réglages de Claude : {claude_settings_path()}")
    if not todo:
        print("Autorisation unique : déjà donnée.")
        return
    print("Règles à ajouter dans permissions.allow :")
    print(json.dumps(todo, ensure_ascii=False, indent=2))


def cmd_library(a):
    """Liste / ajoute / retire les dossiers où le DJ a déjà des sons."""
    with open(a.config, encoding="utf-8") as f:
        c = json.load(f)
    lst = c.setdefault("library_folders", [])
    if a.action in ("add", "remove"):
        if not a.path:
            sys.exit("Préciser le dossier.")
        path = os.path.abspath(os.path.expanduser(a.path))
        stored = short(path)
        if a.action == "add":
            if not os.path.isdir(path):
                sys.exit(f"Dossier introuvable : {path}")
            try:
                os.listdir(path)
            except PermissionError:
                sys.exit(f"Dossier illisible ({ACCESS_HINT}) : {path}")
            if stored not in lst:
                lst.append(stored)
        else:
            if stored not in lst:
                sys.exit(f"Pas dans la liste : {stored}")
            lst.remove(stored)
        with open(a.config, "w", encoding="utf-8") as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
    print(f"Destination : {c['dest_folder']} (toujours comparée)")
    for r in lst:
        full = os.path.expanduser(r)
        n = sum(1 for _ in walk_audio(full)) if os.path.isdir(full) else None
        print(f"  {r} : " + (f"{n} sons" if n is not None else "INTROUVABLE (disque débranché ?)"))
    if not lst:
        print("  (aucun autre dossier)")


def cmd_check(c, st, a):
    """Vérifie que l'installation est utilisable."""
    bad = []
    for k in ("dest_folder", "downloads_folder"):
        if not os.path.isdir(c[k]):
            bad.append(f"{k} introuvable : {c[k]}")
        else:
            try:
                os.listdir(c[k])
            except PermissionError:
                bad.append(f"{k} illisible ({ACCESS_HINT}) : {c[k]}")
    sc, g = c["soundcloud"], c["gate"]
    for k, v in (("soundcloud.likes_of", sc.get("likes_of")), ("soundcloud.account", sc.get("account")),
                 ("soundcloud.chrome_device_id", sc.get("chrome_device_id")), ("gate.email", g.get("email"))):
        if not v or "@exemple" in str(v) or str(v).isupper():
            bad.append(f"{k} à remplir")
    print(f"Système : {SYSTEM} | Python {sys.version.split()[0]}")
    if WINDOWS and not shutil.which("powershell"):
        bad.append("PowerShell introuvable : impossible d'envoyer les doublons à la Corbeille")
    print(f"Édition : {c.get('edition')} | likes de : {sc.get('likes_of')} | compte gates : {sc.get('account')}")
    for r in c.get("library_folders", []):
        if not os.path.isdir(r):
            print(f"  ATTENTION : dossier de sons introuvable (disque débranché ?) : {r}")
    print("Versions : " + ("Radio ET Extended gardées" if c.get("keep_radio_and_extended") else "Extended seulement (avant Radio)"))
    print(f"Dossiers comparés avant téléchargement : {', '.join(short(r) for r in library_roots(c))}")
    print(f"Destination : {c['dest_folder']} | sons suivis : {len(st['tracks'])}"
          f" | pools : {', '.join(p['name'] for p in c['sources'].get('pools', [])) or 'aucun'}")
    if sc.get("download_playlist"):
        print(f"Playlist à télécharger : {sc['download_playlist']}")
    print("Autorisation unique : " + ("donnée" if not missing_rules(a.home) else
                                       "pas encore donnée (voir « perms »), Claude demandera la permission à chaque étape"))
    for b in bad:
        print("  À CORRIGER : " + b)
    print("OK" if not bad else "INCOMPLET")
    return 1 if bad else 0

def liked_day(d):
    """Jour local (AAAA-MM-JJ) du like, à partir de l'horodatage UTC de SoundCloud."""
    ts = datetime.datetime.fromisoformat(d["liked"].replace("Z", "+00:00"))
    return ts.astimezone().date().isoformat()


def cmd_import(c, st, a):
    """Ajoute au suivi les sons choisis par le DJ. Le fichier liste les sons du plus récent au plus ancien."""
    by_url = {t["url"]: t for t in st["tracks"]}
    nid = max([t["id"] for t in st["tracks"]], default=0)
    own = [norm(x) for x in c.get("own_artist_names", [])]
    with open(a.file, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    for d in rows:
        d["p"] = d["p"].split("?")[0]
    if a.since or a.until:
        rows = [d for d in rows if not d.get("known")]  # repère « déjà suivi » de la lecture des likes
        if any(not d.get("liked") for d in rows):
            sys.exit("--since/--until demandent la date du like (champ « liked ») : récupérer les likes avec leurs dates.")
        rows = [d for d in rows if (not a.since or liked_day(d) >= a.since) and (not a.until or liked_day(d) <= a.until)]
    if a.new:
        cut = next((i for i, d in enumerate(rows) if d["p"] in by_url), None)
        if cut is None:
            print("Aucun like déjà suivi dans cette liste : premier passage, tous les likes de la liste sont pris.")
        else:
            rows = rows[:cut]
    if a.limit:
        rows = rows[:a.limit]
    added, known, seen = [], [], set()
    for d in rows:
        if d["p"] in seen:
            continue
        seen.add(d["p"])
        if d["p"] in by_url:
            known.append(by_url[d["p"]]["id"])
            continue
        if d.get("known"):  # repère seul, son absent du suivi : rien à ajouter
            continue
        nid += 1
        t = {"id": nid, "title": d["t"], "uploader": d.get("u", ""), "url": d["p"],
             "minutes": d.get("d"), "sc_download": d.get("dl"), "buy": d.get("buy"),
             "status": "new", "source": None, "file": None, "note": "", "updated": today(),
             "from": a.source}
        if d.get("liked"):
            t["liked"] = d["liked"]
        if t["minutes"] and t["minutes"] >= c["skip_longer_than_minutes"]:
            t["status"] = "skipped_long"
        elif any(o and o in norm(t["title"] + " " + t["uploader"]) for o in own):
            t["status"] = "own_track"
        st["tracks"].append(t)
        by_url[d["p"]] = t
        added.append(nid)
    sel = " ".join(x for x in (a.source, a.new and "nouveaux", a.since and f"depuis {a.since}",
                               a.until and f"jusqu'au {a.until}", a.limit and f"max {a.limit}") if x)
    st.setdefault("batches", []).append({"n": len(st.get("batches", [])) + 1, "date": today(),
                                         "selection": sel, "added": added, "known": known})
    print(f"Sélection : {sel} -> {len(rows)} sons : {len(added)} nouveaux dans le suivi"
          f"{f' (#{added[0]} à #{added[-1]})' if added else ''}, {len(known)} déjà suivis.")
    for i in known:
        t = by_url_id(st, i)
        print(f"  déjà suivi : {label(t)} [{STATUSES[t['status']]}]")


def cmd_known(c, st, a):
    """Adresses des derniers likes déjà suivis (pour arrêter la lecture des likes dès qu'on les atteint)."""
    likes = [t for t in st["tracks"] if t.get("from") in (None, "likes")]
    dated = sorted((t for t in likes if t.get("liked")), key=lambda t: t["liked"], reverse=True)
    legacy = sorted((t for t in likes if not t.get("liked")), key=lambda t: t["id"])
    print(json.dumps([t["url"] for t in (dated + legacy)[:a.latest]]))


def by_url_id(st, i):
    return next(t for t in st["tracks"] if t["id"] == i)


def last_batch_ids(st):
    b = (st.get("batches") or [None])[-1]
    if not b:
        sys.exit("Aucune sélection importée pour l'instant.")
    return set(b["added"]) | set(b["known"])


def cmd_snapshot(c, st, a):
    st["snapshot"] = sorted(os.listdir(c["downloads_folder"]))
    print(f"Instantané de Téléchargements : {len(st['snapshot'])} éléments.")


def cmd_collect(c, st, a):
    t = get_track(st, a.track)
    deadline = time.time() + a.wait
    while True:
        new = new_downloads(c, st)
        busy = [n for n in new if n.lower().endswith(PARTIAL)]
        done = [n for n in new if not n.lower().endswith(PARTIAL)]
        if done and not busy:
            break
        if time.time() > deadline:
            print(f"RIEN après {a.wait}s pour {label(t)}" + (f" (encore en cours : {busy})" if busy else ""))
            return 1
        time.sleep(2)
    took = False
    for n in done:
        p = os.path.join(c["downloads_folder"], n)
        if os.path.isdir(p):
            print(f"  dossier ignoré : {n}")
            continue
        origins = where_from(p)
        v = origin_verdict(c, origins, a.via)
        host = re.sub(r"^https?://([^/]+).*", r"\1", origins[0]) if origins else "?"
        if v == "étranger" or (v == "non vérifié" and not a.accept_unverified):
            print(f"  PAS ATTRIBUÉ ({v}, origine {host}) : {n} — laissé dans Téléchargements")
            continue
        results = process(c, p)
        for res, path in results:
            print(f"  {res} : {os.path.relpath(path, c['dest_folder']) if path.startswith(c['dest_folder']) else path}")
        new = [x for r, x in results if r in ("rangé", "pack rangé")]
        dup = [x for r, x in results if r == "doublon"]
        if new or dup:
            took = True
            t.update(status="downloaded" if new else "owned", source=a.via, origin=host,
                     updated=today(), file=rel(c, (new or dup)[0]))
            if len(new) > 1:
                t["note"] = "versions gardées : " + " + ".join(cut_of(os.path.basename(x)) for x in new)
            elif not new:
                t["note"] = "fichier identique déjà présent"
    st["snapshot"] = sorted(os.listdir(c["downloads_folder"]))
    print(("OK " if took else "ÉCHEC ") + label(t))
    return 0 if took else 1


def cmd_adopt(c, st, a):
    """Range un fichier ajouté par le DJ et l'associe (optionnellement) à un son."""
    p = os.path.expanduser(a.file)
    results = process(c, p) if not p.startswith(c["dest_folder"]) else [("déjà rangé", p)]
    for res, path in results:
        print(f"  {res} : {path}")
    if a.track:
        t = get_track(st, a.track)
        res, path = results[0]
        if res in ("rangé", "pack rangé", "doublon", "déjà rangé"):
            t.update(status="user_added", source="user", updated=today(),
                     file=rel(c, path))
            print("OK " + label(t))
    st["snapshot"] = sorted(os.listdir(c["downloads_folder"]))


def cmd_set(c, st, a):
    if a.status not in STATUSES:
        sys.exit(f"Statut inconnu. Choix : {', '.join(STATUSES)}")
    for ref in a.tracks:
        t = get_track(st, ref)
        t["status"], t["updated"] = a.status, today()
        if a.note is not None:
            t["note"] = a.note
        if a.source:
            t["source"] = a.source
        if a.file:
            t["file"] = a.file
        if a.status == "retry":
            t["retry_after"] = (datetime.date.today() + datetime.timedelta(days=a.days)).isoformat()
        print(f"{label(t)} -> {STATUSES[a.status]}")


def cmd_remove(c, st, a):
    a.status, a.source, a.file, a.days = "removed", None, None, 1
    cmd_set(c, st, a)


def split_title(title):
    """('titre de base', {mots de version}) — la version = ce qui est entre () ou []."""
    base = re.sub(r"[(\[].*?[)\]]", " ", title)
    vers = " ".join(re.findall(r"[(\[](.*?)[)\]]", title))
    generic = {"extended", "original", "mix", "radio", "edit", "club", "version", "free", "download",
               "dl", "remix", "rework", "vip", "feat", "ft", "the", "x", "and", "vocal"}
    vw = {w for w in norm(vers).split() if w not in generic and len(w) > 1}
    return norm(base), vw


def title_parts(title, uploader):
    """(mots du titre, mots de version, mots d'artiste) d'un titre SoundCloud."""
    if " - " in title:
        artist, rest = title.split(" - ", 1)
    else:
        artist, rest = uploader, title
    base, vw = split_title(rest)
    junk = {"free", "download", "dl", "buy", "filtered", "out", "now"}
    core = [w for w in base.split() if w not in junk]
    while core and core[0] in ("the", "a"):
        core = core[1:]
    aw = {w for w in norm(artist).split() if len(w) > 2} - {"records", "music", "official", "the", "feat"}
    return core, vw, aw, cut_kind(rest)


def cut_kind(text):
    """« extended », « radio » ou None d'après le titre."""
    w = norm(text).split()
    return "extended" if "extended" in w else ("radio" if "radio" in w else None)


def match_files(core, vw, aw, files, kind=None, strict_cut=False):
    """[(verdict, chemin)] des fichiers qui contiennent le titre. L'artiste peut être dans le nom ou dans les dossiers."""
    hits = []
    for p, root in files:
        name = os.path.basename(p)
        toks = norm(name).split()
        n = set(toks)
        it = iter(toks)
        if not core or not all(w in it for w in core):  # mots du titre présents, dans l'ordre
            continue
        folders = os.path.relpath(os.path.dirname(p), root).split(os.sep)[-2:]
        ctx = n | set(norm(" ".join(f for f in folders if f != ".")).split())
        same_version = all(w in n for w in vw) if vw else not split_title(name.split(" - ", 1)[-1])[1]
        if kind == "extended" and cut_kind(name) == "radio":  # on veut l'Extended, l'ordi n'a que la Radio
            same_version = False
        if strict_cut and kind and cut_kind(name) != kind:  # le DJ garde Radio et Extended : chaque coupe compte à part
            same_version = False
        same_artist = not aw or bool(aw & ctx)
        verdict = "MÊME VERSION" if same_version and same_artist else (
            "autre artiste" if same_version else "autre version")
        hits.append((verdict, p))
    return sorted(hits, key=lambda h: h[0] != "MÊME VERSION")


def cmd_find(c, st, a):
    """Cherche sur l'ordi (destination + dossiers de sons du DJ) si un son est déjà présent."""
    t = get_track(st, a.track) if not a.text else None
    title = a.text or t["title"]
    core, vw, aw, kind = title_parts(title, "" if a.text else t["uploader"])
    hits = match_files(core, vw, aw, library_files(c), kind, c.get("keep_radio_and_extended", False))
    print(f"Recherche : {title}  (titre : {' '.join(core)} | artiste : {' '.join(sorted(aw)) or '?'}"
          f" | version : {' '.join(sorted(vw)) or 'originale'})")
    for v, p in hits:
        print(f"  {v} : {short(p)}")
    if not hits:
        print("  rien trouvé")


def cmd_dedupe(c, st, a):
    """Compare les sons choisis (pas encore téléchargés) avec les sons déjà sur l'ordi, avant tout téléchargement."""
    if not a.last and not a.tracks:
        sys.exit("Préciser --last ou des numéros de sons.")
    ids = last_batch_ids(st) if a.last else {int(x) for x in a.tracks}
    files = library_files(c)
    print(f"Comparaison avec {len(files)} sons déjà sur l'ordi ({', '.join(short(r) for r in library_roots(c))})")
    owned, check = 0, 0
    for t in st["tracks"]:
        if t["id"] not in ids or t["status"] not in ("new", "retry", "missing", "other_version"):
            continue
        core, vw, aw, kind = title_parts(t["title"], t["uploader"])
        hits = match_files(core, vw, aw, files, kind, c.get("keep_radio_and_extended", False))
        if hits and hits[0][0] == "MÊME VERSION":
            owned += 1
            print(f"  DÉJÀ SUR L'ORDI : {label(t)}\n      -> {short(hits[0][1])}")
            if not a.dry_run:
                t.update(status="owned", note=f"déjà sur l'ordi : {short(hits[0][1])}", updated=today(),
                         file=rel(c, hits[0][1]))
        elif hits:
            check += 1
            print(f"  à vérifier ({hits[0][0]}) : {label(t)}\n      -> {short(hits[0][1])}")
    print(f"{owned} déjà sur l'ordi" + (" (non marqués : --dry-run)" if a.dry_run else " (marqués « déjà présent », pas retéléchargés)")
          + f", {check} à vérifier (autre version ou autre artiste : téléchargés quand même).")


def cmd_todo(c, st, a):
    d = today()
    only = last_batch_ids(st) if a.last else None
    for t in st["tracks"]:
        due = t["status"] == "retry" and t.get("retry_after", d) <= d  # toujours repris, quelle que soit la sélection
        if only is not None and t["id"] not in only and not due:
            continue
        if t["status"] == "new" or due:
            print(f"{label(t)}  [{t['status']}] {t['url']}" + (f"  buy={t['buy']}" if t.get("buy") else ""))


def stray(c, hours=24):
    """Musique ou zip arrivés dans Téléchargements ces dernières heures (le reste appartient au DJ)."""
    out = []
    since = time.time() - hours * 3600
    for n in os.listdir(c["downloads_folder"]):
        p = os.path.join(c["downloads_folder"], n)
        if os.path.isfile(p) and n.lower().endswith(AUDIO + (".zip",)) and created(p) >= since:
            o = where_from(p)
            out.append((n, re.sub(r"^https?://([^/]+).*", r"\1", o[0]) if o else "?"))
    return out


def cmd_sweep(c, st, a):
    s = stray(c, getattr(a, "hours", 24))
    print(f"Musique restée dans Téléchargements : {len(s)}")
    for n, h in s:
        print(f"  {n}   (origine {h})")


def cmd_report(c, st, a):
    groups = {}
    problems = []
    only = last_batch_ids(st) if a.last else None
    for t in st["tracks"]:
        if a.only and not (a.only[0] <= t["id"] <= a.only[1]):
            continue
        if only is not None and t["id"] not in only:
            continue
        groups.setdefault(t["status"], []).append(t)
        if t["status"] in ("downloaded", "user_added") and t.get("file"):
            if not os.path.exists(os.path.join(c["dest_folder"], t["file"])):
                where = os.path.join(c["downloads_folder"], os.path.basename(t["file"]))
                problems.append(f"{label(t)} : fichier absent de la destination"
                                + (" (encore dans Téléchargements)" if os.path.exists(where) else ""))
    total = sum(len(v) for v in groups.values())
    what = f"sélection « {st['batches'][-1]['selection']} », " if a.last else ""
    print(f"BILAN ({what}{total} sons, recompté sur le disque le {today()})")
    for s in STATUSES:
        if s in groups:
            print(f"  {STATUSES[s]:<24} {len(groups[s])}")
    for s in ("missing", "other_version", "retry", "new"):
        if groups.get(s):
            print(f"\n{STATUSES[s].upper()} :")
            for t in groups[s]:
                extra = f" — {t['note']}" if t.get("note") else ""
                extra += f" (à partir du {t['retry_after']})" if s == "retry" else ""
                print(f"  {label(t)}{extra}")
    if problems:
        print("\nPROBLÈMES :")
        for p in problems:
            print("  " + p)
    s = stray(c, getattr(a, "hours", 24))
    if s:
        print(f"\nMUSIQUE RESTÉE DANS TÉLÉCHARGEMENTS ({len(s)}) :")
        for n, h in s:
            print(f"  {n}   (origine {h})")


def cmd_show(c, st, a):
    print(json.dumps(get_track(st, a.track), ensure_ascii=False, indent=1))


def main():
    for s in (sys.stdout, sys.stderr):  # accents et flèches lisibles aussi sous Windows
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default=DEFAULT_HOME, help="dossier des réglages et du suivi")
    ap.add_argument("--config", help="chemin de config (par défaut <home>/config.json)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init", help="installation : crée la config")
    p.add_argument("--edition", choices=("soundcloud", "personal"), default="soundcloud")
    p.add_argument("--likes-of", required=True, help="profil SoundCloud dont on télécharge les likes")
    p.add_argument("--account", required=True, help="compte SoundCloud utilisé pour les gates (repost, autorisation)")
    p.add_argument("--device", required=True, help="deviceId du navigateur Chrome à utiliser")
    p.add_argument("--email", required=True); p.add_argument("--first-name", required=True)
    p.add_argument("--droploud-optin", choices=("yes", "no"), required=True,
                   help="le DJ accepte de cocher la case d'inscription obligatoire des gates Droploud")
    p.add_argument("--dest", default="~/Music/SoundCloud Downloads"); p.add_argument("--downloads", default="~/Downloads")
    p.add_argument("--own", action="append", help="nom d'artiste du DJ (répétable)")
    p.add_argument("--playlist", help="lien de la playlist « à télécharger » du DJ (optionnel)")
    p.add_argument("--library", action="append", help="dossier où le DJ a déjà des sons, comparé avant téléchargement (répétable)")
    p.add_argument("--comments", nargs="+"); p.add_argument("--skip-minutes", type=int, default=45)
    p.add_argument("--keep-both", choices=("yes", "no"), default="no",
                   help="garder la Radio ET l'Extended quand les deux existent (sinon : seulement l'Extended)")
    p.add_argument("--follow-author", choices=FOLLOW_AUTHOR, default="ask",
                   help="proposition facultative de suivre l'auteur du plugin sur SoundCloud")
    p.add_argument("--force", action="store_true")
    sp.add_parser("check", help="vérifier l'installation")
    p = sp.add_parser("config", help="changer un réglage"); p.add_argument("key"); p.add_argument("value")
    p = sp.add_parser("scan", help="installation : trouver les dossiers où le DJ a déjà des sons")
    p.add_argument("--min", type=int, default=10, help="nombre minimal de sons pour proposer un dossier")
    p.add_argument("--top", type=int, default=12); p.add_argument("--seconds", type=float, default=4.0)
    sp.add_parser("perms", help="installation : règles pour n'autoriser le plugin qu'une seule fois")
    p = sp.add_parser("library", help="dossiers de sons déjà sur l'ordi : list | add <dossier> | remove <dossier>")
    p.add_argument("action", nargs="?", default="list", choices=("list", "add", "remove")); p.add_argument("path", nargs="?")
    p = sp.add_parser("import", help="ajouter les sons choisis (jsonl du plus récent au plus ancien : t,u,p,d,dl,buy,liked)")
    p.add_argument("file")
    p.add_argument("--source", default="likes", help="likes | playlist:<titre> | liens")
    p.add_argument("--limit", type=int, help="garder les N premiers (les plus récents)")
    p.add_argument("--since", help="likes à partir de ce jour (AAAA-MM-JJ, heure locale)")
    p.add_argument("--until", help="likes jusqu'à ce jour inclus (AAAA-MM-JJ)")
    p.add_argument("--new", action="store_true", help="seulement les likes plus récents que le dernier like déjà suivi")
    sp.add_parser("snapshot", help="à faire juste AVANT un clic de téléchargement")
    p = sp.add_parser("collect", help="attendre le fichier, vérifier son origine, le ranger")
    p.add_argument("track"); p.add_argument("--via", required=True, help="soundcloud | hypeddit | droploud | pool:<nom>")
    p.add_argument("--wait", type=int, default=60); p.add_argument("--accept-unverified", action="store_true")
    p = sp.add_parser("adopt", help="ranger un fichier ajouté par le DJ"); p.add_argument("file"); p.add_argument("--track")
    for name in ("set", "remove"):
        p = sp.add_parser(name)
        if name == "set":
            p.add_argument("status")
        p.add_argument("tracks", nargs="+"); p.add_argument("--note")
        if name == "set":
            p.add_argument("--source"); p.add_argument("--file"); p.add_argument("--days", type=int, default=1)
    p = sp.add_parser("dedupe", help="avant de télécharger : marquer les sons choisis déjà présents sur l'ordi")
    p.add_argument("tracks", nargs="*"); p.add_argument("--last", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p = sp.add_parser("find", help="déjà présent ? même version ?"); p.add_argument("track", nargs="?"); p.add_argument("--text")
    p = sp.add_parser("known", help="adresses des derniers likes suivis"); p.add_argument("--latest", type=int, default=10)
    p = sp.add_parser("todo", help="sons à traiter maintenant"); p.add_argument("--last", action="store_true", help="seulement la dernière sélection")
    p = sp.add_parser("sweep", help="musique restée dans Téléchargements"); p.add_argument("--hours", type=int, default=24)
    p = sp.add_parser("report", help="bilan recompté sur le disque"); p.add_argument("--only", type=int, nargs=2, metavar=("DE", "A"))
    p.add_argument("--last", action="store_true", help="seulement la dernière sélection importée")
    p = sp.add_parser("show"); p.add_argument("track")
    a = ap.parse_args()
    global FALLBACK_TRASH
    FALLBACK_TRASH = os.path.join(os.path.expanduser(a.home), "corbeille")
    a.config = os.path.expanduser(a.config or os.path.join(a.home, "config.json"))
    if a.cmd == "init":
        return cmd_init(a)
    if a.cmd == "scan":
        return cmd_scan(a)
    if a.cmd == "perms":
        return cmd_perms(a)
    if not os.path.exists(a.config):
        sys.exit(f"Pas encore installé : {a.config} introuvable (lancer « init »).")
    if a.cmd == "config":
        return cmd_config(a)
    if a.cmd == "library":
        return cmd_library(a)
    c = load_config(a.config)
    st = load_state(c)
    fn = globals()["cmd_" + a.cmd]
    rc = fn(c, st, a)
    if a.cmd not in ("check", "known", "find", "todo", "sweep", "report", "show"):
        save_state(c, st)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
