---
name: setup
description: Installe SD Downloader pour un DJ (langue, navigateur Chrome, dossier de rangement ; le compte SoundCloud, l'e-mail et le prénom sont lus tout seuls). À lancer une fois avant le premier téléchargement, ou pour changer un réglage. EN: sets up SD Downloader for a DJ (language, Chrome browser, download folder; SoundCloud account, email and first name are read automatically); run once before the first download, or to change a setting.
disable-model-invocation: true
allowed-tools:
  - 'Bash(python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" *)'
  - 'Bash(python3 -I ${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py *)'
  - 'Bash(py -3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" *)'
  - 'Bash(py -3 -I ${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py *)'
  - 'Bash(python -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" *)'
  - 'Bash(python -I ${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py *)'
  - 'PowerShell(py -3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" *)'
  - 'PowerShell(python -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" *)'
  - 'mcp__claude-in-chrome__list_connected_browsers'
  - 'mcp__claude-in-chrome__select_browser'
  - 'mcp__claude-in-chrome__tabs_context_mcp'
  - 'mcp__claude-in-chrome__tabs_create_mcp'
  - 'mcp__claude-in-chrome__tabs_close_mcp'
  - 'mcp__claude-in-chrome__navigate'
  - 'mcp__claude-in-chrome__javascript_tool'
  - 'mcp__claude-in-chrome__find'
  - 'mcp__claude-in-chrome__read_page'
  - 'mcp__claude-in-chrome__get_page_text'
  - 'mcp__claude-in-chrome__computer'
  - 'mcp__claude-in-chrome__form_input'
  - 'mcp__claude-in-chrome__browser_batch'
---

# Installation de SD Downloader

Parle au DJ simplement, une question à la fois quand c'est possible. Comme pour les téléchargements : rien avant la première question, aucun récit des vérifications (« je lance check », « je lis ton compte »…), zéro jargon à l'écran (`djdl`, config, deviceId, script, commande, JSON, chemin technique), y compris dans la description courte des commandes que l'app affiche (« Je prépare ton dossier », jamais « Lancer djdl init »).

## 0. Langue, avant tout le reste

Si le DJ a écrit quelque chose avec la commande (ex. `/sd-downloader:setup in English please`), prends cette langue sans demander. Sinon, la toute première chose est un `AskUserQuestion` (il n'ouvre aucune fenêtre d'autorisation) : `Langue` : « Langue / Language 🌍 »
- `Français`
- `English`
- `Español`
- `Italiano`

« Autre / Other » pour une autre langue. Aucun choix « (Recommended) ». Ensuite, **tout** le réglage se fait dans cette langue : tes phrases, les questions, les libellés et descriptions des choix (ceux ci-dessous sont en français : traduis-les), le bouton de fin. Garde le code de la langue (`fr`, `en`, `es`, `it`…) pour `djdl init --language`. Les messages de `djdl` et d'`autoriser.py` (bilan, erreurs, « À CORRIGER »…) sont écrits en français : pour un DJ d'une autre langue, ne les recopie jamais tels quels, redis-les dans sa langue (noms de fichiers, de dossiers et de sons inchangés). Ne tape jamais de mot de passe et ne crée aucun compte : le DJ se connecte lui-même.

Outil : `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" --home "${CLAUDE_PLUGIN_DATA}"` (appelé `djdl` ci-dessous).
Sous **Windows**, si `python3` ne répond pas, remplace-le par `py -3` (ou `python`). Garde les guillemets autour des chemins.

## 1. Une seule autorisation, en tout premier

C'est la **première action** du réglage après la question de langue, avant tout autre outil : ni `python3 --version`, ni Chrome, ni lecture de fichier, ni `djdl`. Chaque appel fait avant pourrait ouvrir sa propre fenêtre d'autorisation.

1. Dis au DJ, en deux phrases : « Pour ne pas te demander la permission à chaque étape, je t'en demande une seule maintenant. Elle autorise uniquement l'outil du plugin, l'extension Claude in Chrome et les fichiers du plugin. Une fenêtre va s'afficher : clique **Autoriser**. »
2. Lance `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/autoriser.py" --home "${CLAUDE_PLUGIN_DATA}"`. Ce script ajoute lui-même les règles du plugin aux réglages de Claude, sans toucher au reste, et garde une copie de l'ancien fichier. Il répond « donnée » ou « déjà donnée ». Ne modifie jamais toi-même le fichier de réglages.
   - **Python ne répond pas** (commande introuvable) :
     - **Mac** : demande au DJ de lancer lui-même `xcode-select --install` dans le Terminal, puis de revenir.
     - **Windows** : réessaie la même commande avec `py -3`, puis avec `python`. Garde le premier qui marche pour toutes les commandes `djdl`. Si aucun ne répond (ou si le Microsoft Store s'ouvre), demande au DJ d'installer Python depuis python.org (Download Python, puis à l'installation **cocher « Add python.exe to PATH »**), puis d'ouvrir une nouvelle session.
   - **« Réglages illisibles » ou « Écriture impossible »** : rien n'a été changé. Dis-le au DJ en une phrase et continue.
   - **Le DJ refuse** : continue quand même. Claude demandera simplement la permission à chaque étape.

## 1b. Claude in Chrome

L'extension **Claude in Chrome** doit être installée et connectée dans Chrome. Appelle `list_connected_browsers`. Si rien n'est connecté, donne au DJ le lien direct https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn. Il clique « Ajouter à Chrome », puis se connecte dans l'extension avec le même compte Claude. Attends, puis réessaie.

## 2. Deviner presque tout, puis une question

Le but : le DJ répond à **deux questions en tout** (la langue, le dossier), et rien d'autre. Tout le reste se devine ou prend sa valeur par défaut. Les questions se posent avec **`AskUserQuestion`**, en choix cliquables (2 à 4 par question, ta recommandation en premier avec « (Recommended) ») ; « Other » reste là pour écrire autre chose. Chaque description de choix commence par une **majuscule** (« Tu choisis… », « Le bouton… »).

**A. Détecter (une seule question possible : le navigateur)**
- **Navigateur** : `list_connected_browsers`, sans rien ouvrir. Le DJ peut avoir d'autres profils Chrome (perso, travail, boutique…) : n'y ouvre **aucune** page sans son accord.
  - Consignes du DJ (CLAUDE.md…) : seule une consigne qui désigne un navigateur **pour SoundCloud** (ou ce plugin) décide. Une consigne qui réserve un navigateur à autre chose (Instagram, boutique…) ne dit pas lequel prendre ici : écarte ce navigateur, et pose la question ci-dessous pour les autres. Ne choisis jamais un navigateur parce qu'une consigne l'autorise pour une autre tâche.
  - Un seul navigateur connecté : c'est lui.
  - Plusieurs : `AskUserQuestion`, `Navigateur` : « Plusieurs navigateurs Chrome sont connectés à Claude. Lequel est celui de SoundCloud ? » Un choix par navigateur (son nom affiché ; 3 au plus, les autres se tapent dans « Other »), plus `Je ne sais pas`. Description : le nom se voit dans l'extension Claude du profil Chrome que tu utilises pour SoundCloud.
  - `Je ne sais pas` : deuxième question, `Vérifier` : « Je peux ouvrir soundcloud.com dans chacun (un onglet, refermé aussitôt) pour trouver celui où tu es connecté ? » `Oui, vérifie` / `Non, je déconnecte l'extension des autres profils`. Seulement après « Oui » : pour chaque navigateur, `select_browser`, ouvrir soundcloud.com, lire le compte (`playbook.md` §1), fermer l'onglet ; rien d'autre. Après « Non » : attendre que le DJ le fasse, puis refaire `list_connected_browsers`.
  - Garde le deviceId choisi. Ensuite, ne touche plus jamais aux autres navigateurs.
- **Prévenir avant la première page ouverte dans Chrome** : l'app Claude va demander, pour chaque site (soundcloud.com, hypeddit.com, droploud.com), si Claude peut l'ouvrir. Le plugin ne peut pas donner cet accord à la place du DJ. Dis-le en une ligne avant d'ouvrir soundcloud.com : « 3 fenêtres d'autorisation vont s'afficher (SoundCloud, Hypeddit, Droploud) : clique **Toujours autoriser pour ce site web**, et on ne te les redemandera plus. »
- **Compte SoundCloud, e-mail, prénom, sans question** : dans ce navigateur seulement, ouvrir soundcloud.com et lire le compte connecté (`playbook.md` §1). Pas connecté : demander au DJ de se connecter lui-même, puis relire. Ce compte sert pour les gates **et** pour les likes. Sur la même page, lire l'e-mail et le prénom du compte : `const me = (window.__sc_hydration||[]).find(h=>h.hydratable==='meUser')?.data; ({email: me?.primary_email, prenom: me?.first_name})`. Ils vont dans la config tels quels et s'affichent dans le résumé de fin. Seulement s'il en manque un, demande-le en texte (une phrase). N'invente jamais d'adresse ou de prénom (ni adresse de test, ni « au hasard »). Si un gate pré-remplit déjà une adresse, elle sera gardée telle quelle.
- **Accès de Chrome aux sites, une fois pour toutes** : dans ce navigateur, ouvre aussi hypeddit.com et droploud.com. Si l'extension demande l'accès à un site (soundcloud.com, hypeddit.com, droploud.com), dis au DJ de choisir l'option qui autorise **toujours** ce site. Les commandes du plugin, elles, sont déjà autorisées par l'étape 1 : pendant les téléchargements, plus aucune fenêtre d'autorisation.
- **Dossiers** : `djdl scan`, seulement pour proposer au choix `Rangement` un dossier de téléchargements qui existe déjà.

**B. Un seul appel `AskUserQuestion`, une question**

Pas de question sur une playlist « À télécharger » ici : un DJ qui n'a encore rien téléchargé la comprend mal. Elle est proposée une seule fois, après le premier bilan avec un son téléchargé (skill `download-likes`, étape 6).

1. `Rangement` : « Où je range les sons téléchargés ? 📁 »
   - `Musique › SoundCloud Downloads (Recommended)` : description « Nouveau dossier dans Musique » → `~/Music/SoundCloud Downloads`
   - `📁 Nouveau dossier sur le Bureau` : description « Je crée « SoundCloud Downloads » sur ton Bureau ; pour un autre nom, écris-le dans « Autre » » → `~/Desktop/SoundCloud Downloads`
   - au plus 1 dossier trouvé par `scan` qui ressemble à un dossier de téléchargements (par exemple « … Downloads ») ;
   - `📂 Choisir un autre dossier…` : description « Une fenêtre s'ouvre, tu cliques sur le dossier (bouton « Nouveau dossier » pour en créer un) ».

   Réponse dans « Autre » : un simple nom (sans `/` ni `\`) → nouveau dossier `~/Desktop/<nom>` ; un chemin → tel quel. `djdl init` crée le dossier s'il n'existe pas. Les sons déjà dans ce dossier ne seront jamais retéléchargés.

**Choisir un dossier dans une fenêtre** (après cet appel, si le DJ a pris `📂 Choisir un autre dossier…`) : dis-lui en une ligne qu'une fenêtre du Finder (Windows : de l'Explorateur) va s'ouvrir, peut-être derrière les autres fenêtres. Puis lance, avec un délai de Bash de 6 minutes (`timeout: 360000`) :

```bash
djdl pick-folder --prompt "Où ranger les sons téléchargés ?"
```

La sortie « Dossier choisi : <chemin> » donne le dossier. « Aucun dossier choisi » : le DJ a annulé, repose la question. Si la commande dit que la fenêtre est indisponible, demande le chemin en texte. Un chemin écrit dans « Other » reste accepté tel quel.

Tout le reste garde sa valeur par défaut, sans question :
- likes : ceux du compte connecté ;
- versions : Extended (avant Radio) ;
- feu vert des gates donné une fois pour toutes (`--go auto`) : il est annoncé dans le résumé de fin ;
- longs sets ignorés au-delà de 45 min ;
- commentaires « love it », « fire », « wow », « nice » ;
- téléchargements de Chrome dans `~/Downloads`.

Le DJ peut tout changer plus tard d'une phrase (« garde aussi les versions radio », « mes likes sont sur <profil> », « mon e-mail c'est … », « demande-moi avant les gates »).

## 3. Écrire la config

```bash
djdl init --likes-of <compte> --account <compte> --device <deviceId> \
  --email <email> --first-name <prénom> --language <code> \
  --dest "<dossier>" --go auto
```

(`--force` pour remplacer une config existante.) Puis `djdl check` : tout doit être OK. Si un dossier est « illisible » : sur **Mac**, le DJ autorise l'accès (Réglages Système → Confidentialité et sécurité → Fichiers et dossiers, ou Accès complet au disque) pour l'application qui fait tourner Claude ; sur **Windows**, il choisit un dossier de son profil (Musique, Documents) ou vérifie que le disque externe est branché. Sur Windows, les chemins se donnent tels quels (ex. `D:\Musique\Sets`).

## 4. Facultatif : suivre l'auteur du plugin

Le plugin est gratuit, partagé par le DJ Luigi Hayek. Propose une seule fois, sans insister, de le suivre sur SoundCloud. Le plugin marche exactement pareil quelle que soit la réponse.

1. Dans le navigateur de la config (son deviceId, jamais un autre), ouvre https://soundcloud.com/luigi-hayek et lis le bouton de suivi. S'il affiche déjà « Following » / « Abonné » : `djdl config follow_author followed`, ferme l'onglet et n'en parle pas.
2. Sinon, `AskUserQuestion`, `Soutien` : « Facultatif : SD Downloader est gratuit, fait par le DJ Luigi Hayek. Tu veux le suivre sur SoundCloud ? Ça ne change rien au plugin. »
   - `Oui, suis-le pour moi` : description « Avec ton compte <compte> »
   - `Non merci`

   Aucun choix « (Recommended) » ici.
3. « Oui » : clique « Follow » une seule fois, vérifie que le bouton passe à « Following », puis `djdl config follow_author followed`. « Non merci » : ne suis pas, `djdl config follow_author no` (on ne le reproposera plus). Ferme l'onglet.

Ne suis jamais sans ce « Oui ». Si la page ne charge pas ou si le compte connecté n'est pas `<compte>`, laisse tomber sans en parler.

## 5. Fin : un résumé de 2 lignes et un bouton

Pas de mode d'emploi. Écris ce résumé (traduit dans la langue du DJ), rien de plus :

> ## ✅ SD Downloader est prêt
> 🎧 **<compte>** · ✉️ <email> · 📁 **<dossier>**
>
> _Je fais les gates avec ton compte, sans te redemander : suivre, liker, reposter, commenter, connecter le gate à SoundCloud. Pour changer quoi que ce soit, dis-le en une phrase._

Puis un seul `AskUserQuestion`, `Télécharger` : « On lance le premier téléchargement ? 🚀 »
- `🚀 Lancer (Recommended)` : description « Tu choisis quels sons, je fais le reste »
- `Plus tard` : description « Le bouton 🎧 au-dessus de la zone de saisie lance tes nouveaux likes quand tu veux »

« Lancer » : appelle tout de suite le skill `sd-downloader:download-likes` (outil `Skill`), sans argument : il propose lui-même le choix des sons. « Plus tard » : une phrase pour dire au revoir, rien d'autre.
