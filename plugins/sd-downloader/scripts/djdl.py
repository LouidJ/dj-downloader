#!/usr/bin/env python3
"""DJ Downloader: suivi des likes SoundCloud, rangement des téléchargements, bilan recompté sur disque.

Usage: python3 -I djdl.py [--home DOSSIER] <commande> ...   (Windows : py -3 -I djdl.py …)
Commandes : init, scan, pick-folder, open-folder, perms, check, import, snapshot, collect, adopt, set, remove, find, todo, sweep, report, show

Réglages et suivi : <home>/config.json et <home>/state.json (home par défaut : $DJDL_HOME ou ~/.dj-downloader).
"""
import argparse, datetime, hashlib, json, os, plistlib, re, shutil, subprocess, sys, tempfile, time, unicodedata, \
    urllib.parse, zipfile

DEFAULT_HOME = os.environ.get("DJDL_HOME") or "~/.dj-downloader"
AUDIO = (".wav", ".aif", ".aiff", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus")
SKIP_DIRS = {"__MACOSX", ".Trash", "node_modules", "$RECYCLE.BIN", "System Volume Information"}
WINDOWS = sys.platform == "win32"
SYSTEM = "Windows" if WINDOWS else ("macOS" if sys.platform == "darwin" else sys.platform)
ACCESS_HINT = ("autoriser l'accès au dossier, ou choisir un autre dossier" if WINDOWS else
               "autoriser l'accès dans Réglages Système > Confidentialité et sécurité > Fichiers et dossiers")
PARTIAL = (".crdownload", ".download", ".part")
# outils du système appelés par leur chemin complet (pas via le PATH)
XATTR, MDLS = "/usr/bin/xattr", "/usr/bin/mdls"
POWERSHELL = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0",
                          "powershell.exe")
# extraction des zip : limites, et seuls types de fichiers gardés (pas d'exécutable ni de lien symbolique)
MAX_UNZIP_BYTES = 4 * 1024 ** 3
MAX_UNZIP_FILES = 2000
ZIP_KEEP = AUDIO + (".pdf", ".txt", ".rtf", ".md", ".nfo", ".jpg", ".jpeg", ".png", ".gif", ".webp")

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
# note d'un son téléchargé alors qu'il était déjà sur l'ordi (fichier identique, mis à la Corbeille)
GATE_FOR_NOTHING = "téléchargé pour rien, identique à"


# ---------- config / état ----------

def check_home(home):
    """Le dossier du plugin doit s'appeler « …dj-downloader… » ou « …sd-downloader… » : un --home vers
    ~/.claude, ~ ou le dossier d'une autre appli (où init écrirait config.json) est refusé."""
    h = os.path.abspath(os.path.expanduser(home))
    if not re.search(r"(dj|sd)-downloader", os.path.basename(h)):
        sys.exit(f"Dossier refusé : {h} (le dossier du plugin doit contenir « dj-downloader » ou « sd-downloader »).")
    return h


def load_config(path):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    for k in ("dest_folder", "downloads_folder"):
        c[k] = os.path.expanduser(c[k])
    c["library_folders"] = [os.path.expanduser(x) for x in c.get("library_folders", [])]
    sf = c.get("state_file", "state.json")
    if not isinstance(sf, str) or os.path.basename(sf) != sf or sf in ("", ".", "..") or "/" in sf:
        sys.exit(f"state_file refusé : {sf!r} (un simple nom de fichier, dans le dossier du plugin).")
    c["state_file"] = os.path.join(os.path.dirname(os.path.abspath(path)), sf)
    return c


def write_json(path, data, indent=2):
    """Écrit un fichier JSON d'un coup (fichier temporaire puis remplacement), lisible par le seul utilisateur :
    la config contient l'e-mail et le prénom du DJ."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def load_state(c):
    if os.path.exists(c["state_file"]):
        with open(c["state_file"], encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": [], "snapshot": []}


def save_state(c, st):
    write_json(c["state_file"], st, indent=1)


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
        raw = subprocess.run([XATTR, "-px", "com.apple.metadata:kMDItemWhereFroms", path],
                             capture_output=True, text=True, timeout=10).stdout
        if raw.strip():
            return [str(u) for u in plistlib.loads(bytes.fromhex("".join(raw.split())))]
        out = subprocess.run([MDLS, "-raw", "-name", "kMDItemWhereFroms", path],
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
            subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", RECYCLE_PS],
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


def zip_name(info):
    """Nom d'un fichier du zip. Les zip du Finder écrivent l'UTF-8 sans le signaler : zipfile le lit en cp437."""
    n = info.filename
    if not info.flag_bits & 0x800:
        try:
            n = n.encode("cp437").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return n


def unzip(path, dest):
    """Extrait un zip téléchargé, prudemment, même code sur Mac et Windows. Ne garde que les sons et quelques
    documents (ZIP_KEEP) : pas d'exécutable, pas de lien symbolique, pas de chemin qui sort de dest, au plus
    MAX_UNZIP_FILES fichiers et MAX_UNZIP_BYTES octets réellement écrits. Retourne (ok, nb de fichiers écartés)."""
    root = os.path.realpath(dest)
    skipped, written = 0, 0
    try:
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) > MAX_UNZIP_FILES:
                return False, 0
            for i in infos:
                if i.is_dir():
                    continue
                name = zip_name(i).replace("\\", "/")
                parts = [x for x in name.split("/") if x not in ("", ".")]
                if parts and (parts[0] == "__MACOSX" or parts[-1].startswith("._")):  # métadonnées du Finder
                    continue
                is_link = (i.external_attr >> 16) & 0o170000 == 0o120000
                if (not parts or ".." in parts or ":" in parts[0] or is_link
                        or not parts[-1].lower().endswith(ZIP_KEEP)):
                    skipped += 1
                    continue
                target = os.path.join(root, *parts)
                if os.path.commonpath([root, os.path.realpath(os.path.dirname(target))]) != root:
                    skipped += 1
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with z.open(i) as src, open(target, "wb") as out:
                    for b in iter(lambda: src.read(1 << 20), b""):
                        written += len(b)
                        if written > MAX_UNZIP_BYTES:
                            return False, skipped
                        out.write(b)
        return True, skipped
    except (zipfile.BadZipFile, OSError, RuntimeError, ValueError, NotImplementedError):
        return False, skipped


def free_path(p):
    """p, ou « p (2) », « p (3) »… s'il existe déjà : on n'écrase jamais un fichier du DJ."""
    if not os.path.exists(p):
        return p
    stem, ext = os.path.splitext(p) if os.path.isfile(p) else (p, "")
    n = 2
    while os.path.exists(f"{stem} ({n}){ext}"):
        n += 1
    return f"{stem} ({n}){ext}"


def inside(p, root):
    """p est-il dans le dossier root (ou root lui-même), liens résolus ?"""
    p, root = os.path.realpath(p), os.path.realpath(root)
    try:
        return os.path.commonpath([p, root]) == root
    except ValueError:  # disques différents (Windows)
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
    if not inside(p, c["dest_folder"]):
        return p
    return os.path.relpath(os.path.realpath(p), os.path.realpath(c["dest_folder"]))


def find_identical(c, path):
    size = os.path.getsize(path)
    same = [p for p, _ in library_files(c) if os.path.getsize(p) == size and not os.path.samefile(p, path)]
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


VERSIONS = ("extended", "radio", "both")  # coupe gardée quand un son existe en Extended et en Radio
# Formats voulus par le DJ (« any », ou un ou plusieurs : « wav,aiff »). L'artiste choisit le format :
# un son reçu dans un autre est gardé et signalé au bilan.
FORMATS = {"wav": (".wav",), "aiff": (".aif", ".aiff"), "mp3": (".mp3",)}
# Nettoyage des noms de fichiers (V2, master, final… absents du titre SoundCloud) : on | off
CLEAN_NAMES = ("on", "off")
# Zip reçu, une fois les sons extraits : trash = à la Corbeille, keep = gardé dans <destination>/Zips
ZIPS = ("trash", "keep")


def wanted_formats(c):
    """Formats voulus, en liste (vide = tous)."""
    v = c.get("format", "any")
    return [] if v == "any" else v.split(",")


def format_label(c):
    return " / ".join(f.upper() for f in wanted_formats(c)) or "tous"


def cut_pref(c):
    """« extended », « radio » ou « both » (anciennes configs : keep_radio_and_extended)."""
    v = c.get("versions")
    return v if v in VERSIONS else ("both" if c.get("keep_radio_and_extended") else "extended")


def rank(name, pref="extended"):
    """Ordre de préférence d'un fichier : la coupe choisie par le DJ d'abord, puis WAV / AIFF avant MP3."""
    n = name.lower()
    cut = "extended" if "extended" in n else ("radio" if "radio" in n else None)
    v = 1 if cut is None else (0 if cut == pref or pref == "both" and cut == "extended" else 2)
    f = 1 if n.endswith((".wav", ".aif", ".aiff", ".flac")) else 2
    return v * 10 + f


W0, W1 = r"(?<![^\W_])", r"(?![^\W_])"  # bords de mot (le « _ » sépare aussi)
ANYWHERE = re.compile(W0 + r"(?:version[\s_]+finale?|final[\s_]+version|v\d+)" + W1, re.I)
MASTER = re.compile(W0 + r"master(?:ed|is[ée]e?|ized|ing)?" + W1, re.I)
FINAL = re.compile(W0 + r"finale?" + W1, re.I)
KEEP_UPPER = {"dj", "vip", "mc"}  # restent en capitales : « DJ Snake », « (VIP Mix) »


def clean_name(name, title=None):
    """Nom de fichier propre : sans « V1/V2 » ni « version finale », sans « master » ni « final » s'ils ne
    sont pas dans le titre SoundCloud (`title` ; sans titre connu : seulement entre parenthèses), et en
    Majuscules Initiales si tout est en capitales."""
    stem, ext = os.path.splitext(name)
    s = ANYWHERE.sub(lambda m: m[0] if title and re.search(W0 + re.escape(m[0]) + W1, title, re.I) else " ", stem)
    for word in (MASTER, FINAL):
        if title is not None:  # autant de « master » / « final » que dans le titre SoundCloud, pas plus
            allowed = iter(range(len(word.findall(title))))
            s = word.sub(lambda m: m[0] if next(allowed, None) is not None else " ", s)

    def inside(m):
        if title and re.search(r"[(\[]\s*" + re.escape(m[2].strip()) + r"\s*[)\]]", title, re.I):
            return f"{m[1]}{m[2].strip()}{m[3]}"  # parenthèse du titre SoundCloud : gardée, sans espaces collés
        txt = FINAL.sub(" ", MASTER.sub(" ", m[2]))
        txt = re.sub(r"\s+", " ", txt).strip(" _-–.")
        return f"{m[1]}{txt}{m[3]}" if txt else " "
    s = re.sub(r"([(\[])([^)\]]*)([)\]])", inside, s)
    s = re.sub(r"(?:\s*[-–]\s*){2,}", " - ", s)  # « Artist - - Track » après un mot retiré
    s = re.sub(r"[\s_\-–.]+(?=[(\[])", " ", s)  # « Track_ (Extended) »
    s = re.sub(r"\s+", " ", s).strip(" _-–.")
    if not any(ch.isalpha() for ch in s):
        s = stem  # rien de lisible ne resterait : on garde le nom d'origine
    letters = [ch for ch in s if ch.isalpha()]
    if letters and all(ch.isupper() for ch in letters):
        s = re.sub(r"[^\W\d_]+(?:['’][^\W\d_]+)*", lambda m: title_word(m[0]), s)
    return s + ext


def title_word(w):
    """« DON'T » -> « Don't », « L'AMOUR » -> « L'Amour » (élision : une lettre avant l'apostrophe), « DJ » reste."""
    if w.lower() in KEEP_UPPER:
        return w.upper()
    parts = re.split(r"(['’])", w.lower())
    out = parts[0].capitalize()
    for i in range(1, len(parts), 2):
        nxt = parts[i + 1]
        out += parts[i] + (nxt.capitalize() if len(parts[i - 1]) == 1 else nxt)
    return out


def place(c, src, title=None):
    """Range un fichier audio dans la destination (title : titre SoundCloud du son, pour le nom). Retourne (résultat, chemin)."""
    same = find_identical(c, src)
    if same:
        trash(src)
        return "doublon", same
    name = clean_name(os.path.basename(src), title) if c.get("clean_names", "on") == "on" else os.path.basename(src)
    if name != os.path.basename(src):
        print(f"  renommé : {os.path.basename(src)} → {name}")
    target = os.path.join(c["dest_folder"], name)
    if os.path.exists(target):
        return "conflit", src  # même nom, contenu différent : on laisse, on signale
    shutil.move(src, target)
    return "rangé", target


def drop_zip(c, path):
    """Zip dont les sons sont extraits : à la Corbeille, ou gardé dans <destination>/Zips selon le réglage."""
    if c.get("zips") != "keep":
        return trash(path)
    keep = os.path.join(c["dest_folder"], "Zips")
    os.makedirs(keep, exist_ok=True)
    shutil.move(path, free_path(os.path.join(keep, os.path.basename(path))))


def process(c, path, title=None):
    """Traite un fichier téléchargé (audio ou zip). Retourne une liste de (résultat, chemin)."""
    name = os.path.basename(path)
    low = name.lower()
    if low.endswith(AUDIO):
        return [place(c, path, title)]
    if not low.endswith(".zip"):
        return [("non audio", path)]
    tmp = tempfile.mkdtemp(prefix="unzip.", dir=os.path.dirname(c["state_file"]))
    ok, skipped = unzip(path, tmp)
    if not ok:
        shutil.rmtree(tmp, ignore_errors=True)
        return [("zip illisible ou trop gros", path)]
    if skipped:
        print(f"  {skipped} fichier(s) du zip écarté(s) (ni son ni document : programme, lien, chemin suspect)")
    shutil.rmtree(os.path.join(tmp, "__MACOSX"), ignore_errors=True)
    audio = []
    for root, _, files in os.walk(tmp):
        audio += [os.path.join(root, f) for f in files if f.lower().endswith(AUDIO) and not f.startswith("._")]
    stem = os.path.splitext(name)[0]
    if not audio:
        left = free_path(os.path.join(c["downloads_folder"], stem + " (contenu du zip)"))
        shutil.move(tmp, left)
        trash(path)
        return [("zip sans audio", left)]
    # un groupe par son ; dans un son, une seule version (la meilleure) ou, si le DJ garde les deux, une par coupe
    pref = cut_pref(c)
    both = pref == "both"
    groups = {}
    for a in audio:
        b = os.path.basename(a)
        g = groups.setdefault(track_key(b), {})
        ck = cut_of(b) if both else "*"
        if ck not in g or rank(b, pref) < rank(os.path.basename(g[ck]), pref):
            g[ck] = a
    if len(groups) > 1:  # pack : on garde le dossier tel quel
        entries = [e for e in os.listdir(tmp) if not e.startswith(".")]
        inner = os.path.join(tmp, entries[0]) if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])) else tmp
        target = os.path.join(c["dest_folder"], stem)
        if os.path.exists(target):
            return [("conflit pack", path)]
        shutil.move(inner, target)
        shutil.rmtree(tmp, ignore_errors=True)
        drop_zip(c, path)
        return [("pack rangé", target)]
    out = []
    for f in sorted(next(iter(groups.values())).values(), key=lambda x: rank(os.path.basename(x), pref)):
        res = place(c, f, title)
        if res[0] == "conflit":  # ne pas jeter le seul exemplaire avec le dossier extrait
            keep = free_path(os.path.join(c["downloads_folder"], os.path.basename(res[1])))
            shutil.move(res[1], keep)
            res = ("conflit", keep)
        out.append(res)
    trash(tmp)
    drop_zip(c, path)
    return out


def host_of(url):
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def host_in(host, hosts):
    """host est l'un des hosts, ou un de leurs sous-domaines (« evil.tld/?x=hypeddit.com » ne passe pas)."""
    return any("." in h and (host == h or host.endswith("." + h)) for h in (x.lower() for x in hosts))


def origin_verdict(c, origins, via):
    """ok si une des adresses d'origine (le fichier, puis la page) est sur un site de la source. Un stockage
    partagé (SHARED_STORAGE, où n'importe qui peut déposer un fichier) ne compte que si la page d'origine
    est aussi sur le site (par exemple R2 + droploud.com)."""
    seen = [host_of(u) for u in origins]
    if any(host_in(h, c.get("never_attribute_from", [])) for h in seen) or \
            any(b in " ".join(origins).lower() for b in c.get("never_attribute_from", []) if "." not in b):
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
    site = [h for h in hosts if not host_in(h, SHARED_STORAGE)]
    return "ok" if any(host_in(h, site) for h in seen) else "non vérifié"


def new_downloads(c, st):
    snap = set(st.get("snapshot", []))
    return [n for n in os.listdir(c["downloads_folder"]) if n not in snap and not n.startswith(".")]


# ---------- commandes ----------

SOURCES = {
    "soundcloud": ["sndcdn.com", "soundcloud.com"],
    "hypeddit": ["hypeddit-gates-prod.s3.amazonaws.com", "hypeddit.com"],
    "droploud": ["r2.cloudflarestorage.com", "droploud.com"],
}
# stockages où n'importe qui peut héberger un fichier : jamais suffisants seuls pour attribuer un téléchargement
SHARED_STORAGE = ("r2.cloudflarestorage.com",)


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
        "versions": "both" if a.keep_both == "yes" else a.versions,
        "follow_author": a.follow_author,
        "playlist_offer": "ask",
        "open_folder": "ask",
        "format": "any",
        "clean_names": "on",
        "zips": "trash",
        "settings_offer": "ask",
        "go": a.go,
        "language": a.language,
        "sources": dict(SOURCES, pools=[]),
        "never_attribute_from": ["telegram.org", "whatsapp", "mail.google.com"],
    }
    os.makedirs(os.path.expanduser(a.dest), exist_ok=True)
    write_json(path, c)
    print(f"Config écrite : {path}\nDossier de destination : {os.path.expanduser(a.dest)}")


# Feu vert des gates : auto = donné une fois pour toutes au réglage, ask = demandé à chaque run.
GO = ("auto", "ask")
# Proposition facultative de suivre l'auteur du plugin : ask = la proposer, followed = déjà suivi, no = ne plus proposer.
FOLLOW_AUTHOR = ("ask", "followed", "no")
# Playlist « À télécharger » proposée une fois, après le premier bilan avec un son téléchargé : ask = à proposer, no = déjà proposée.
PLAYLIST_OFFER = ("ask", "no")
# Fin d'un run : ask = proposer le bouton « Ouvrir le dossier », auto = l'ouvrir tout seul.
OPEN_FOLDER = ("ask", "auto")
# Réglages (format, versions) proposés une fois après le premier bilan : ask = à proposer, no = déjà proposés.
SETTINGS_OFFER = ("ask", "no")
SETTABLE = ("language", "soundcloud.likes_of", "soundcloud.download_playlist", "soundcloud.chrome_device_id", "soundcloud.account",
            "gate.email", "gate.first_name", "dest_folder", "skip_longer_than_minutes", "versions",
            "follow_author", "playlist_offer", "open_folder", "settings_offer", "format", "clean_names", "zips", "go")


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
    elif leaf == "versions":
        if a.value not in VERSIONS:
            sys.exit("Valeur : " + " | ".join(VERSIONS))
        node[leaf] = a.value
        node.pop("keep_radio_and_extended", None)
    elif leaf == "format":
        picked = [f.strip().lower() for f in a.value.split(",") if f.strip()]
        if picked != ["any"] and (not picked or any(f not in FORMATS for f in picked)):
            sys.exit("Valeur : any, ou un ou plusieurs formats séparés par des virgules parmi " + ", ".join(FORMATS))
        node[leaf] = ",".join(dict.fromkeys(picked))
    elif leaf in ("follow_author", "playlist_offer", "open_folder", "settings_offer", "clean_names", "zips", "go"):
        allowed = {"follow_author": FOLLOW_AUTHOR, "playlist_offer": PLAYLIST_OFFER, "open_folder": OPEN_FOLDER,
                   "settings_offer": SETTINGS_OFFER, "clean_names": CLEAN_NAMES, "zips": ZIPS, "go": GO}[leaf]
        if a.value not in allowed:
            sys.exit("Valeur : " + " | ".join(allowed))
        node[leaf] = a.value
    else:
        node[leaf] = a.value
    write_json(a.config, c)
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


PICK_MAC = (  # fenêtre « Choisir un dossier » du Finder ; annuler = erreur -128
    "on run argv",
    "activate",
    "set start to path to music folder",
    'if item 2 of argv is "desktop" then set start to path to desktop folder',
    'if item 2 of argv is "home" then set start to path to home folder',
    "return POSIX path of (choose folder with prompt (item 1 of argv) default location start)",
    "end run")
PICK_WIN = (  # fenêtre « Rechercher un dossier » de Windows, au premier plan
    "Add-Type -AssemblyName System.Windows.Forms; "
    "$f = New-Object System.Windows.Forms.Form -Property @{TopMost = $true}; "
    "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
    "$d.Description = $env:DJDL_PROMPT; $d.ShowNewFolderButton = $true; "
    "$d.SelectedPath = [Environment]::GetFolderPath($env:DJDL_START); "
    "if ($d.ShowDialog($f) -eq 'OK') { $d.SelectedPath } else { exit 1 }")


def cmd_pick_folder(a):
    """Ouvre la fenêtre du système pour choisir un dossier (le DJ clique, n'écrit pas de chemin) et l'affiche."""
    try:
        if sys.platform == "darwin":
            r = subprocess.run(["/usr/bin/osascript"] + [x for l in PICK_MAC for x in ("-e", l)] + [a.prompt, a.start],
                               capture_output=True, text=True, timeout=a.wait)
        elif WINDOWS:
            start = {"music": "MyMusic", "desktop": "Desktop", "home": "UserProfile"}[a.start]
            r = subprocess.run([POWERSHELL, "-STA", "-NoProfile", "-NonInteractive", "-Command", PICK_WIN],
                               env={**os.environ, "DJDL_PROMPT": a.prompt, "DJDL_START": start},
                               capture_output=True, text=True, timeout=a.wait)
        else:
            sys.exit("Fenêtre de choix de dossier indisponible ici : écrire le chemin du dossier.")
    except subprocess.TimeoutExpired:
        print("Aucun dossier choisi (fenêtre restée ouverte trop longtemps).")
        return 1
    except OSError as e:
        sys.exit(f"Fenêtre de choix de dossier indisponible ({e}) : écrire le chemin du dossier.")
    path = r.stdout.strip()
    if r.returncode != 0 or not path:
        print("Aucun dossier choisi.")
        return 1
    path = path.rstrip("/\\") or path
    print(f"Dossier choisi : {short(path)}")
    return 0


def cmd_open_folder(c):
    """Ouvre le dossier de destination dans le Finder (Windows : l'Explorateur), à la fin d'un run."""
    path = os.path.expanduser(c["dest_folder"])
    if not os.path.isdir(path):
        sys.exit(f"Dossier introuvable : {short(path)}")
    try:
        if sys.platform == "darwin":
            subprocess.run(["/usr/bin/open", path], check=True, timeout=20)
        elif WINDOWS:
            os.startfile(path)
        else:
            sys.exit(f"Ouverture du dossier indisponible ici (Claude ne tourne pas sur l'ordi du DJ) : {short(path)}")
    except (OSError, subprocess.SubprocessError) as e:
        sys.exit(f"Ouverture du dossier impossible ({e}) : {short(path)}")
    print(f"Dossier ouvert : {short(path)}")
    return 0


def claude_settings_path():
    return os.path.join(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude"), "settings.json")


def rule_path(path):
    """Chemin au format des règles d'autorisation de Claude Code (~/… sous le dossier perso, //… sinon)."""
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~/" + os.path.relpath(path, home).replace(os.sep, "/")
    return "//" + path.replace("\\", "/").replace(":", "").lstrip("/")


def plugin_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def perm_rules(home):
    """Règles d'autorisation durables : le seul djdl.py de CETTE version du plugin (pas de « * » dans le
    chemin, sinon « …/*/scripts » laisserait passer « …/../données/scripts »), et ses fichiers.
    Ni autoriser.py (son accord doit toujours passer par une fenêtre), ni Claude in Chrome (couvert
    pendant les runs par `allowed-tools` des skills, à ne pas ouvrir à toutes les sessions)."""
    root = plugin_root()
    script = os.path.join(root, "scripts", "djdl.py")
    rules = []
    for py in (("py -3", "python", "python3") if WINDOWS else ("python3",)):
        rules += [f'Bash({py} -I "{script}" *)', f"Bash({py} -I {script} *)"]
        if WINDOWS:
            rules.append(f'PowerShell({py} -I "{script}" *)')
    data = rule_path(os.path.abspath(os.path.expanduser(home)))
    rules += [f"Read({rule_path(root)}/**)", f"Read({data}/**)", f"Edit({data}/**)"]
    return rules


def stale_rule(r, home):
    """Règle laissée par une ancienne version du plugin (chemin en « * », autre version, Chrome pour tous)."""
    if r in perm_rules(home):
        return False
    if r == "mcp__claude-in-chrome__*":
        return True
    root = plugin_root()
    base = os.path.dirname(root) if os.sep.join(("plugins", "cache")) in root else root  # toutes versions
    return any(m in r for m in (base + os.sep, base + "/", rule_path(base) + "/"))


def settings_allow():
    try:
        with open(claude_settings_path(), encoding="utf-8") as f:
            return json.load(f).get("permissions", {}).get("allow", [])
    except (OSError, ValueError, AttributeError):
        return []


def missing_rules(home):
    have = set(settings_allow())
    return [r for r in perm_rules(home) if r not in have]


def perms_ok(home):
    """Donnée = toutes les règles de cette version présentes, et plus aucune d'une ancienne version."""
    return not missing_rules(home) and not any(stale_rule(r, home) for r in settings_allow())


def write_rules(home, remove=False):
    """Seul endroit qui écrit les réglages de Claude, appelé par autoriser.py (jamais par la ligne de
    commande de djdl) : ajoute les règles du plugin, ou les retire ; retire aussi celles des anciennes
    versions. Aucune autre règle ni clé touchée ; copie datée de l'ancien fichier."""
    path = os.path.realpath(claude_settings_path())  # suit un éventuel lien symbolique
    try:
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
    except FileNotFoundError:
        s = {}
    except (OSError, ValueError) as e:
        sys.exit(f"Réglages illisibles, rien n'est changé ({e}).")
    if not isinstance(s, dict) or not isinstance(s.setdefault("permissions", {}), dict) \
            or not isinstance(s["permissions"].setdefault("allow", []), list):
        sys.exit("Réglages d'une forme inattendue, rien n'est changé.")
    allow = s["permissions"]["allow"]
    ours = set(perm_rules(home))
    keep = [r for r in allow if not stale_rule(r, home) and not (remove and r in ours)]
    added = [] if remove else [r for r in perm_rules(home) if r not in keep]
    if keep + added == allow:
        return 0, 0
    s["permissions"]["allow"] = keep + added
    backup = os.path.exists(path)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if backup:
            shutil.copy2(path, f"{path}.avant-djdl-{time.strftime('%Y%m%d-%H%M%S')}")
        tmp = path + ".djdl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
            f.write("\n")
        if backup:
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except OSError as e:
        sys.exit(f"Écriture impossible, rien n'est changé ({e}).")
    return len(added), len(allow) - len(keep)


def cmd_perms(a):
    """Affiche les règles d'autorisation du plugin à ajouter (l'ajout passe par autoriser.py, avec une fenêtre)."""
    print(f"Réglages de Claude : {claude_settings_path()}")
    if perms_ok(a.home):
        print("Autorisation unique : déjà donnée.")
        return
    print("Autorisation unique : pas encore donnée. autoriser.py ajoutera :")
    print(json.dumps(missing_rules(a.home), ensure_ascii=False, indent=2))
    old = [r for r in settings_allow() if stale_rule(r, a.home)]
    if old:
        print("et retirera ces règles d'une ancienne version :")
        print(json.dumps(old, ensure_ascii=False, indent=2))


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
        write_json(a.config, c)
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
    for k, v in (("soundcloud.account", sc.get("account")),
                 ("soundcloud.chrome_device_id", sc.get("chrome_device_id")), ("gate.email", g.get("email")),
                 ("gate.first_name", g.get("first_name"))):
        # valeur d'exemple restée telle quelle (un prénom en majuscules, « JB », est un vrai prénom)
        if not v or "@exemple" in str(v) or (str(v).isupper() and k != "gate.first_name"):
            bad.append(f"{k} à remplir")
    print(f"Système : {SYSTEM} | Python {sys.version.split()[0]}")
    if WINDOWS and not os.path.isfile(POWERSHELL):
        bad.append("PowerShell introuvable : impossible d'envoyer les doublons à la Corbeille")
    print(f"Édition : {c.get('edition')} | likes de : {sc.get('likes_of') or 'aucun profil (liens et playlists)'}"
          f" | compte gates : {sc.get('account')}")
    for r in c.get("library_folders", []):
        if not os.path.isdir(r):
            print(f"  ATTENTION : dossier de sons introuvable (disque débranché ?) : {r}")
    print("Versions : " + {"both": "Radio ET Extended gardées", "radio": "Radio seulement (avant Extended)",
                           "extended": "Extended seulement (avant Radio)"}[cut_pref(c)])
    print("Format : " + format_label(c) + ("" if not wanted_formats(c) else " (un autre format reçu est gardé et signalé)"))
    print("Noms de fichiers : " + ("nettoyés (V2, master, final… retirés s'ils ne sont pas dans le titre SoundCloud)"
                                   if c.get("clean_names", "on") == "on" else "gardés tels quels"))
    print("Zips : " + ("gardés dans Zips" if c.get("zips") == "keep" else "mis à la Corbeille une fois les sons extraits"))
    print(f"Dossiers comparés avant téléchargement : {', '.join(short(r) for r in library_roots(c))}")
    print(f"Destination : {c['dest_folder']} | sons suivis : {len(st['tracks'])}"
          f" | pools : {', '.join(p['name'] for p in c['sources'].get('pools', [])) or 'aucun'}")
    if sc.get("download_playlist"):
        print(f"Playlist à télécharger : {sc['download_playlist']}")
    print("Autorisation unique : " + ("donnée" if perms_ok(a.home) else
                                       "pas encore donnée (lancer autoriser.py), Claude demandera la permission à chaque étape"))
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
        results = process(c, p, t["title"])
        for res, path in results:
            print(f"  {res} : {rel(c, path)}")
        new = [x for r, x in results if r in ("rangé", "pack rangé")]
        dup = [x for r, x in results if r == "doublon"]
        if new or dup:
            took = True
            t.update(status="downloaded" if new else "owned", source=a.via, origin=host,
                     updated=today(), file=rel(c, (new or dup)[0]))
            exts = tuple(e for f in wanted_formats(c) for e in FORMATS[f])
            wrong = [x for x in new if exts and os.path.isfile(x) and not x.lower().endswith(exts)]
            if wrong:
                t["wrong_format"] = os.path.splitext(wrong[0])[1].lstrip(".").upper()
                print(f"  format : reçu en {t['wrong_format']} au lieu de {format_label(c)} (gardé)")
            if len(new) > 1:
                t["note"] = "versions gardées : " + " + ".join(cut_of(os.path.basename(x)) for x in new)
            elif not new:
                t["note"] = f"{GATE_FOR_NOTHING} : {short(dup[0])}"
    st["snapshot"] = sorted(os.listdir(c["downloads_folder"]))
    print(("OK " if took else "ÉCHEC ") + label(t))
    return 0 if took else 1


def cmd_adopt(c, st, a):
    """Range un fichier ajouté par le DJ et l'associe (optionnellement) à un son."""
    p = os.path.expanduser(a.file)
    t = get_track(st, a.track) if a.track else None
    if not os.path.exists(p):
        sys.exit(f"Fichier introuvable : {p}")
    in_library = any(inside(p, r) for r in library_roots(c))
    results = [("déjà rangé", p)] if in_library else process(c, p, t and t["title"])
    for res, path in results:
        print(f"  {res} : {path}")
    if t:
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


# Mentions promo des titres SoundCloud, qui ne disent rien de la version :
# « {HYPEDDIT #55 FREE DOWNLOAD} », « [FREE DL] », « (FILTERED) », « (OUT NOW) »…
PROMO = re.compile(r"[(\[{][^)\]}]*?(?:free\s*d(?:own)?l(?:oad)?|freedl|hypeddit|droploud|filtered|"
                   r"out\s+now|buy|click|support(?:ed)?|premiere)[^)\]}]*[)\]}]", re.I)


def strip_promo(title):
    """Titre sans mentions promo ni blocs {…}."""
    t = PROMO.sub(" ", title)
    t = re.sub(r"\{[^}]*\}", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def split_title(title):
    """('titre de base', {mots de version}) — la version = ce qui est entre () ou []."""
    base = re.sub(r"[(\[].*?[)\]]", " ", title)
    vers = " ".join(re.findall(r"[(\[](.*?)[)\]]", title))
    generic = {"extended", "original", "mix", "radio", "edit", "club", "version", "free", "download",
               "dl", "remix", "rework", "vip", "feat", "ft", "the", "x", "and", "vocal",
               "filtered", "hypeddit", "droploud", "out", "now", "buy"}
    vw = {w for w in norm(vers).split() if w not in generic and len(w) > 1}
    return norm(base), vw


def title_candidates(title, uploader):
    """Lectures possibles d'un titre : « Artiste - Titre » d'abord, puis « Titre - Artiste »."""
    t = strip_promo(title)
    if " - " not in t:
        return [parts_of(uploader, t, artist_in_title=False)]
    left, right = t.split(" - ", 1)
    return [parts_of(left, right), parts_of(right, left)]


def best_match(title, uploader, files, pref="extended"):
    """(lecture retenue, [(verdict, chemin)]). La lecture « Titre - Artiste » ne sert que si elle trouve
    la même version : sinon on garde « Artiste - Titre », pour ne pas signaler de faux « à vérifier »."""
    cands = title_candidates(title, uploader)
    found = []
    for i, cand in enumerate(cands):
        core, vw, aw, kind = cand
        # lecture inversée : tout « l'artiste » doit être dans le nom, sinon « Latch | Renyn Remix »
        # passerait pour un artiste et le remix pour l'original déjà présent
        found.append((cand, match_files(core, vw, aw, files, kind, pref, all_artists=i > 0)))
        if found[-1][1] and found[-1][1][0][0] == "MÊME VERSION":
            return found[-1]
    return found[0]


def parts_of(artist, rest, artist_in_title=True):
    """Une lecture : la version (entre () ou []) compte des deux côtés du « - »,
    pour « Titre - Artiste (Remix) » comme pour « Artiste - Titre (Remix) ».
    Les parenthèses du nom de l'uploader (« JUNO (DE) ») ne sont pas une version."""
    base, vw = split_title(rest)
    abase, avw = split_title(artist)
    avw = {w for w in avw if len(w) > 2} if artist_in_title else set()
    junk = {"free", "download", "dl", "buy", "filtered", "out", "now", "hypeddit", "droploud"}
    core = [w for w in base.split() if w not in junk]
    while core and core[0] in ("the", "a"):
        core = core[1:]
    aw = {w for w in abase.split() if len(w) > 2} - {"records", "music", "official", "the", "feat"}
    return core, vw | avw, aw, cut_kind(rest) or cut_kind(artist)


def cut_kind(text):
    """« extended », « radio » ou None d'après le titre."""
    w = norm(text).split()
    return "extended" if "extended" in w else ("radio" if "radio" in w else None)


def match_files(core, vw, aw, files, kind=None, pref="extended", all_artists=False):
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
        if vw:
            same_version = all(w in n for w in vw)
        else:
            # sans version dans le titre : le fichier n'en a pas non plus, ou seulement des mots du titre
            # (« Latch | Renyn Remix » = « Latch (Renyn Remix) »), le reste du titre étant hors parenthèses
            # (« Tik Tok » ≠ « Adjust (Tik Tok) »)
            fbase, fv = split_title(name.split(" - ", 1)[-1])
            same_version = not fv or (fv <= set(core) and any(w in fbase.split() for w in core if w not in fv))
        other = {"extended": "radio", "radio": "extended"}.get(pref)
        if kind == pref and cut_kind(name) == other:  # on veut la coupe préférée, l'ordi n'a que l'autre
            same_version = False
        if pref == "both" and kind and cut_kind(name) != kind:  # le DJ garde Radio et Extended : chaque coupe compte à part
            same_version = False
        same_artist = not aw or (aw <= ctx if all_artists else bool(aw & ctx))
        verdict = "MÊME VERSION" if same_version and same_artist else (
            "autre artiste" if same_version else "autre version")
        hits.append((verdict, p))
    return sorted(hits, key=lambda h: h[0] != "MÊME VERSION")


def cmd_find(c, st, a):
    """Cherche sur l'ordi (destination + dossiers de sons du DJ) si un son est déjà présent."""
    t = get_track(st, a.track) if not a.text else None
    title = a.text or t["title"]
    (core, vw, aw, kind), hits = best_match(title, "" if a.text else t["uploader"], library_files(c),
                                            cut_pref(c))
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
        hits = best_match(t["title"], t["uploader"], files, cut_pref(c))[1]
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
    wasted = [t for t in groups.get("owned", []) if t.get("note", "").startswith(GATE_FOR_NOTHING)]
    if wasted:
        print(f"\nTÉLÉCHARGÉS POUR RIEN ({len(wasted)}, déjà sur l'ordi sans être repérés avant : "
              "fichier mis à la Corbeille, gate fait quand même) :")
        for t in wasted:
            print(f"  {label(t)} — {t['note'][len(GATE_FOR_NOTHING) + 3:]}")
    off = [t for t in groups.get("downloaded", []) if t.get("wrong_format")]
    if wanted_formats(c) and off:
        print(f"\nAUTRE FORMAT QUE {format_label(c)} ({len(off)}, gardés : l'artiste ne propose que ce format) :")
        for t in off:
            print(f"  {label(t)} — {t['wrong_format']}")
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
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init", help="installation : crée la config")
    p.add_argument("--edition", choices=("soundcloud", "personal"), default="soundcloud")
    p.add_argument("--likes-of", default="", help="profil SoundCloud dont on télécharge les likes (vide : liens et playlists seulement)")
    p.add_argument("--account", required=True, help="compte SoundCloud utilisé pour les gates (repost, autorisation)")
    p.add_argument("--device", required=True, help="deviceId du navigateur Chrome à utiliser")
    p.add_argument("--email", required=True); p.add_argument("--first-name", required=True)
    p.add_argument("--droploud-optin", choices=("yes", "no"), default="yes",
                   help="cocher la case d'inscription obligatoire des gates Droploud (oui par défaut : sans elle, pas de son)")
    p.add_argument("--dest", default="~/Music/SoundCloud Downloads"); p.add_argument("--downloads", default="~/Downloads")
    p.add_argument("--own", action="append", help="nom d'artiste du DJ (répétable)")
    p.add_argument("--playlist", help="lien de la playlist « à télécharger » du DJ (optionnel)")
    p.add_argument("--library", action="append", help="dossier où le DJ a déjà des sons, comparé avant téléchargement (répétable)")
    p.add_argument("--comments", nargs="+"); p.add_argument("--skip-minutes", type=int, default=45)
    p.add_argument("--versions", choices=VERSIONS, default="extended",
                   help="quand un son existe en Extended et en Radio : extended, radio, ou both (les deux)")
    p.add_argument("--keep-both", choices=("yes", "no"), default="no", help=argparse.SUPPRESS)  # ancien nom de --versions both
    p.add_argument("--language", default="fr", help="langue du DJ pour parler et pour les questions (fr, en, es, it…)")
    p.add_argument("--go", choices=GO, default="ask",
                   help="feu vert des gates : auto = donné au réglage pour tous les runs, ask = demandé à chaque run")
    p.add_argument("--follow-author", choices=FOLLOW_AUTHOR, default="ask",
                   help="proposition facultative de suivre l'auteur du plugin sur SoundCloud")
    p.add_argument("--force", action="store_true")
    sp.add_parser("check", help="vérifier l'installation")
    p = sp.add_parser("config", help="changer un réglage"); p.add_argument("key"); p.add_argument("value")
    p = sp.add_parser("scan", help="installation : trouver les dossiers où le DJ a déjà des sons")
    p.add_argument("--min", type=int, default=10, help="nombre minimal de sons pour proposer un dossier")
    p.add_argument("--top", type=int, default=12); p.add_argument("--seconds", type=float, default=4.0)
    p = sp.add_parser("pick-folder", help="installation : fenêtre du système pour choisir un dossier (pas de chemin à écrire)")
    p.add_argument("--prompt", default="Choisis un dossier")
    p.add_argument("--start", choices=("music", "desktop", "home"), default="music", help="dossier ouvert au départ")
    p.add_argument("--wait", type=int, default=300, help="secondes avant d'abandonner")
    sp.add_parser("open-folder", help="fin d'un run : ouvre le dossier des sons dans le Finder / l'Explorateur")
    sp.add_parser("perms", help="installation : règles pour n'autoriser le plugin qu'une seule fois (ajout : autoriser.py)")
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
    a.home = check_home(a.home)
    global FALLBACK_TRASH
    FALLBACK_TRASH = os.path.join(a.home, "corbeille")
    a.config = os.path.join(a.home, "config.json")
    if a.cmd == "init":
        return cmd_init(a)
    if a.cmd == "scan":
        return cmd_scan(a)
    if a.cmd == "perms":
        return cmd_perms(a)
    if a.cmd == "pick-folder":
        return cmd_pick_folder(a)
    if not os.path.exists(a.config):
        sys.exit(f"Pas encore installé : {a.config} introuvable (lancer « init »).")
    if a.cmd == "config":
        return cmd_config(a)
    if a.cmd == "library":
        return cmd_library(a)
    c = load_config(a.config)
    if a.cmd == "open-folder":
        return cmd_open_folder(c)
    st = load_state(c)
    fn = globals()["cmd_" + a.cmd]
    rc = fn(c, st, a)
    if a.cmd not in ("check", "known", "find", "todo", "sweep", "report", "show"):
        save_state(c, st)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
