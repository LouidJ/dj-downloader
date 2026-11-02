---
name: setup
description: Installe SD Downloader pour un DJ (langue, profil de likes, compte pour les gates, navigateur Chrome, e-mail, dossier). À lancer une fois avant le premier téléchargement, ou pour changer un réglage. EN: sets up SD Downloader for a DJ (language, likes profile, gates account, Chrome browser, email, folder); run once before the first download, or to change a setting.
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

Parle au DJ simplement, une question à la fois quand c'est possible.

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

## 2. Questions au DJ : détecter d'abord, puis faire cocher

Le DJ ne doit presque rien écrire. **Devine d'abord** ce que tu peux, puis pose les questions avec **`AskUserQuestion`**, en choix cliquables (2 à 4 par question, ta recommandation en premier avec « (Recommended) »). « Other » reste toujours là pour écrire autre chose. Regroupe jusqu'à 4 questions par appel. Ne pose en texte libre que ce qui ne peut pas se deviner : l'e-mail et le prénom.

**A. Détecter (une seule question possible : le navigateur)**
- **Navigateur** : `list_connected_browsers`, sans rien ouvrir. Le DJ peut avoir d'autres profils Chrome (perso, travail, boutique…) : n'y ouvre **aucune** page sans son accord.
  - Consignes du DJ (CLAUDE.md…) : seule une consigne qui désigne un navigateur **pour SoundCloud** (ou ce plugin) décide. Une consigne qui réserve un navigateur à autre chose (Instagram, boutique…) ne dit pas lequel prendre ici : écarte ce navigateur, et pose la question ci-dessous pour les autres. Ne choisis jamais un navigateur parce qu'une consigne l'autorise pour une autre tâche.
  - Un seul navigateur connecté : c'est lui.
  - Plusieurs : `AskUserQuestion`, `Navigateur` : « Plusieurs navigateurs Chrome sont connectés à Claude. Lequel est celui de SoundCloud ? » Un choix par navigateur (son nom affiché ; 3 au plus, les autres se tapent dans « Other »), plus `Je ne sais pas`. Description : le nom se voit dans l'extension Claude du profil Chrome que tu utilises pour SoundCloud.
  - `Je ne sais pas` : deuxième question, `Vérifier` : « Je peux ouvrir soundcloud.com dans chacun (un onglet, refermé aussitôt) pour trouver celui où tu es connecté ? » `Oui, vérifie` / `Non, je déconnecte l'extension des autres profils`. Seulement après « Oui » : pour chaque navigateur, `select_browser`, ouvrir soundcloud.com, lire le compte (`playbook.md` §1), fermer l'onglet ; rien d'autre. Après « Non » : attendre que le DJ le fasse, puis refaire `list_connected_browsers`.
  - Garde le deviceId choisi. Ensuite, ne touche plus jamais aux autres navigateurs.
- **Compte des gates** : dans ce navigateur seulement, ouvrir soundcloud.com et lire le compte connecté (`playbook.md` §1). Pas connecté : demander au DJ de se connecter lui-même, puis relire. Sur la même page, lire aussi l'e-mail et le prénom du compte, pour les proposer à la question D : `const me = (window.__sc_hydration||[]).find(h=>h.hydratable==='meUser')?.data; ({email: me?.primary_email, prenom: me?.first_name})`. Ne les utilise que pour cette question.
- **Accès de Chrome aux sites, une fois pour toutes** : dans ce navigateur, ouvre aussi hypeddit.com et droploud.com. Si l'extension demande l'accès à un site (soundcloud.com, hypeddit.com, droploud.com), dis au DJ de choisir l'option qui autorise **toujours** ce site. Les commandes du plugin, elles, sont déjà autorisées par l'étape 1 : pendant les téléchargements, plus aucune fenêtre d'autorisation.
- **Dossiers de sons** : `djdl scan`. Il liste les dossiers qui contiennent déjà des sons, avec leur nombre.

**B. Premier appel `AskUserQuestion`**
1. `Gates` : « Pour les gates (suivre, reposter, commenter), j'utilise le compte SoundCloud connecté dans Chrome, **<compte>** ? »
   - `Oui, <compte> (Recommended)`
   - `Non, j'en connecte un autre`

   Explique dans la description qu'un deuxième compte SoundCloud garde le compte principal propre. Si le DJ en connecte un autre, attends qu'il le fasse, puis relis le compte connecté.
2. `Likes` : « De quel profil je télécharge les likes ? Pour un autre profil, écris son nom ou son adresse dans « Autre ». »
   - `<compte> (Recommended)` : description « les likes du compte connecté ».
   - `Aucun` : description « je ne télécharge que des liens ou des playlists ». Alors `--likes-of ""` ; si le DJ demande un jour ses likes, le skill lui demandera le profil.
   - Réponse écrite dans « Autre » : garde seulement `<profil>` (de `soundcloud.com/<profil>`, sans le reste de l'adresse).

   Ne mets pas de choix « Un autre profil » : « Autre » sert déjà à l'écrire.
3. `Versions` : « Quand un son existe en Extended et en Radio, je garde quelle version ? »
   - `Extended version (Recommended)` → `--versions extended`
   - `Radio version` → `--versions radio`
   - `Les deux` → `--versions both`

**C. Deuxième appel `AskUserQuestion`**
4. `Rangement` : « Où je range les sons téléchargés ? 📁 »
   - `Musique › SoundCloud Downloads (Recommended)` : description « nouveau dossier dans Musique » → `~/Music/SoundCloud Downloads`
   - `📁 Nouveau dossier sur le Bureau` : description « je crée « SoundCloud Downloads » sur ton Bureau ; pour un autre nom, écris-le dans « Autre » » → `~/Desktop/SoundCloud Downloads`
   - au plus 1 dossier trouvé par `scan` qui ressemble à un dossier de téléchargements (par exemple « … Downloads ») ;
   - `📂 Choisir un autre dossier…` : description « une fenêtre s'ouvre, tu cliques sur le dossier (bouton « Nouveau dossier » pour en créer un) ».

   Réponse dans « Autre » : un simple nom (sans `/` ni `\`) → nouveau dossier `~/Desktop/<nom>` ; un chemin → tel quel. `djdl init` crée le dossier s'il n'existe pas.
5. `Mes sons` (**multiSelect**) : « Évite les doublons : je vérifie si tu as déjà téléchargé une partie des tracks pour ne pas les avoir en double. »
   - les 4 dossiers de `scan` les plus utiles, avec leur nombre de sons, par exemple « Musique › PioneerDJ (1849 sons) ». Évite un dossier déjà compris dans un autre choix ;
   - au plus 3 dossiers de `scan` si tu ajoutes le choix suivant ;
   - `📂 Choisir un autre dossier…` : description « une fenêtre s'ouvre, tu cliques sur le dossier (clé USB, disque externe…) ». Un disque débranché est simplement ignoré ce jour-là.

**Choisir un dossier dans une fenêtre** (après ce deuxième appel, si le DJ a pris `📂 Choisir un autre dossier…`) : dis-lui en une ligne qu'une fenêtre du Finder (Windows : de l'Explorateur) va s'ouvrir, peut-être derrière les autres fenêtres. Puis lance, avec un délai de Bash de 6 minutes (`timeout: 360000`) :

```bash
djdl pick-folder --prompt "Où ranger les sons téléchargés ?"          # Rangement
djdl pick-folder --prompt "Un dossier où tu as déjà des sons" --start home   # Mes sons (une fois par dossier)
```

La sortie « Dossier choisi : <chemin> » donne le dossier. Pour `Mes sons`, demande ensuite (`AskUserQuestion`) « Un autre dossier ? » `Non, c'est tout (Recommended)` / `📂 Oui, un autre` et recommence tant qu'il dit oui. « Aucun dossier choisi » : le DJ a annulé, repose la question. Si la commande dit que la fenêtre est indisponible, demande le chemin en texte. Un chemin écrit dans « Other » reste accepté tel quel.
6. `Playlist` : « Tu veux une playlist SoundCloud « À télécharger » ? Tu y ajoutes des sons pendant que tu digs, puis un clic suffit pour tout télécharger. »
   - `Pas maintenant (Recommended)`
   - `Oui, je colle son lien` : le lien va dans « Other ». Il peut être public ou privé.

**D. Troisième appel `AskUserQuestion` : e-mail et prénom, deux questions dans le même cadre**
- `E-mail` : « Ton e-mail pour les gates ? Tu ne le donnes qu'une fois, ensuite je le remplis moi-même. ✉️ »
  - `<e-mail lu sur SoundCloud> (Recommended)` : description « l'e-mail de ton compte SoundCloud <compte> »
  - `Une autre adresse` : description « écris-la dans « Autre » »
- `Prénom` : « Ton prénom pour les gates ? 🙂 »
  - `<prénom lu sur SoundCloud> (Recommended)` : description « le prénom de ton profil SoundCloud »
  - `Un autre prénom` : description « écris-le dans « Autre » »

Si SoundCloud n'a pas donné l'e-mail ou le prénom, demande-le en texte à la place de ce choix. Si le DJ choisit « Une autre adresse » / « Un autre prénom » sans rien écrire, redemande-le en texte. Garde exactement ce qu'il choisit ou écrit. N'invente jamais d'adresse ou de prénom (ni adresse de test, ni « au hasard »). Si un gate pré-remplit déjà une adresse, elle sera gardée telle quelle.

Les réglages avancés gardent leur valeur par défaut, sans question :
- longs sets ignorés au-delà de 45 min ;
- commentaires « love it », « fire », « wow », « nice » ;
- téléchargements de Chrome dans `~/Downloads`.

Le DJ peut les changer plus tard en le demandant.

## 3. Écrire la config

```bash
djdl init --likes-of <profil> --account <compte-gates> --device <deviceId> \
  --email <email> --first-name <prénom> --language <code> \
  --dest "<dossier>" [--playlist <lien>] [--library "<dossier>" …] [--versions extended|radio|both] [--comments "love it" "fire"] [--skip-minutes 45]
```

(`--force` pour remplacer une config existante. Plus tard : `djdl library add "<dossier>"` / `remove` / `list`.) Puis `djdl check` : tout doit être OK. Si un dossier est « illisible » : sur **Mac**, le DJ autorise l'accès (Réglages Système → Confidentialité et sécurité → Fichiers et dossiers, ou Accès complet au disque) pour l'application qui fait tourner Claude ; sur **Windows**, il choisit un dossier de son profil (Musique, Documents) ou vérifie que le disque externe est branché. Sur Windows, les chemins se donnent tels quels (ex. `D:\Musique\Sets`).

## 4. Facultatif : suivre l'auteur du plugin

Le plugin est gratuit, partagé par le DJ Luigi Hayek. Propose une seule fois, sans insister, de le suivre sur SoundCloud. Le plugin marche exactement pareil quelle que soit la réponse.

1. Dans le navigateur de la config (son deviceId, jamais un autre), ouvre https://soundcloud.com/luigi-hayek et lis le bouton de suivi. S'il affiche déjà « Following » / « Abonné » : `djdl config follow_author followed`, ferme l'onglet et n'en parle pas.
2. Sinon, `AskUserQuestion`, `Soutien` : « Facultatif : SD Downloader est gratuit, fait par le DJ Luigi Hayek. Tu veux le suivre sur SoundCloud ? Ça ne change rien au plugin. »
   - `Oui, suis-le pour moi` : description « avec ton compte <compte> »
   - `Non merci`

   Aucun choix « (Recommended) » ici.
3. « Oui » : clique « Follow » une seule fois, vérifie que le bouton passe à « Following », puis `djdl config follow_author followed`. « Non merci » : ne suis pas, laisse le réglage tel quel (on reproposera seulement à la fin d'une grosse playlist). Ferme l'onglet.

Ne suis jamais sans ce « Oui ». Si la page ne charge pas ou si le compte connecté n'est pas `<compte>`, laisse tomber sans en parler.

## 5. Fin : un bouton pour lancer le premier téléchargement

Pas de mode d'emploi en texte. Un seul `AskUserQuestion`, `Télécharger` : « C'est prêt ! On lance le téléchargement ? 🚀 »
- `🚀 Lancer le téléchargement (Recommended)` : description « je te montre quoi télécharger, tu coches et tu cliques Go »
- `Plus tard` : description « tape /sd-downloader:download-likes quand tu veux, ou dis-moi « télécharge mes nouveaux likes » »

« Lancer » : appelle tout de suite le skill `sd-downloader:download-likes` (outil `Skill`), sans argument : il propose lui-même les choix à cocher puis le bouton Go. « Plus tard » : une phrase pour dire au revoir, rien d'autre.
