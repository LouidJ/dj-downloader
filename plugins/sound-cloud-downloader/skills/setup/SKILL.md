---
name: setup
description: Installe Sound Cloud Downloader pour un DJ (profil de likes, compte pour les gates, navigateur Chrome, e-mail, dossier). À lancer une fois avant le premier téléchargement, ou pour changer un réglage.
disable-model-invocation: true
---

# Installation de Sound Cloud Downloader

Parle au DJ dans sa langue, simplement, une question à la fois quand c'est possible. Ne tape jamais de mot de passe et ne crée aucun compte : le DJ se connecte lui-même.

Outil : `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/djdl.py" --home "${CLAUDE_PLUGIN_DATA}"` (appelé `djdl` ci-dessous).
Sous **Windows**, si `python3` ne répond pas, remplace-le par `py -3` (ou `python`). Garde les guillemets autour des chemins.

## 1. Prérequis

- **Python 3.9 ou plus** doit répondre :
  - **Mac** : `python3 --version`. Sinon, demande au DJ de lancer lui-même `xcode-select --install` dans le Terminal, puis de revenir.
  - **Windows** : essaie `python3 --version`, puis `py -3 --version`, puis `python --version`, et garde le premier qui affiche « Python 3.x » pour toutes les commandes `djdl`. Si aucun ne répond (ou si le Microsoft Store s'ouvre), demande au DJ d'installer Python depuis python.org (Download Python, puis à l'installation **cocher « Add python.exe to PATH »**), puis d'ouvrir une nouvelle session.
- L'extension **Claude in Chrome** doit être installée et connectée dans Chrome. Appelle `list_connected_browsers`. Si rien n'est connecté, donne au DJ le lien direct https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn. Il clique « Ajouter à Chrome », puis se connecte dans l'extension avec le même compte Claude. Attends, puis réessaie.

## 2. Questions au DJ : détecter d'abord, puis faire cocher

Le DJ ne doit presque rien écrire. **Devine d'abord** ce que tu peux, puis pose les questions avec **`AskUserQuestion`**, en choix cliquables (2 à 4 par question, ta recommandation en premier avec « (Recommended) »). « Other » reste toujours là pour écrire autre chose. Regroupe jusqu'à 4 questions par appel. Ne pose en texte libre que ce qui ne peut pas se deviner : l'e-mail et le prénom.

**A. Détecter, sans rien demander**
- **Navigateur et compte des gates** : `list_connected_browsers`. Pour chaque navigateur : `select_browser`, ouvrir soundcloud.com, lire le compte connecté (`playbook.md` §1). Garde son deviceId et son compte. Ne touche plus jamais aux autres navigateurs.
- **Nom affiché** de ce compte (sur sa page de profil).
- **Dossiers de sons** : `djdl scan`. Il liste les dossiers qui contiennent déjà des sons, avec leur nombre.

**B. Premier appel `AskUserQuestion`**
1. `Gates` : « Pour les gates (suivre, reposter, commenter), j'utilise le compte SoundCloud connecté dans Chrome, **<compte>** ? »
   - `Oui, <compte> (Recommended)`
   - `Non, j'en connecte un autre`

   Explique dans la description qu'un deuxième compte SoundCloud garde le compte principal propre. Si le DJ en connecte un autre, attends qu'il le fasse, puis relis le compte connecté.
2. `Likes` : « De quel profil je télécharge les likes ? »
   - `<compte> (Recommended)`
   - `Un autre profil` : le DJ colle l'adresse dans « Other » ; garde seulement `<profil>`.
3. `Droploud` : « Certains gates Droploud obligent à cocher « J'accepte de recevoir ce son et des nouvelles de l'artiste ». Je peux la cocher pour toi ? »
   - `Oui (Recommended)`
   - `Non` : ces sons seront marqués manquants.
4. `Versions` : « Quand un son existe en Radio et en Extended ? »
   - `Seulement l'Extended (Recommended)`
   - `Garder les deux`

**C. Deuxième appel `AskUserQuestion`**
5. `Rangement` : « Où je range les sons téléchargés ? »
   - `Musique › SoundCloud Downloads (Recommended)` : `~/Music/SoundCloud Downloads`
   - `Bureau › SoundCloud Downloads` : `~/Desktop/SoundCloud Downloads`
   - jusqu'à 2 dossiers trouvés par `scan` qui ressemblent à un dossier de téléchargements (par exemple « … Downloads »).
6. `Mes sons` (**multiSelect**) : « Où sont les sons que tu as déjà ? Je les compare avant chaque téléchargement pour ne jamais télécharger un son en double. »
   - les 4 dossiers de `scan` les plus utiles, avec leur nombre de sons, par exemple « Musique › PioneerDJ (1849 sons) ». Évite un dossier déjà compris dans un autre choix ;
   - une clé USB ou un disque externe se colle dans « Other ». Un disque débranché est simplement ignoré ce jour-là.
7. `Artiste` : « Tu sors des sons sous quel nom ? Je ne les téléchargerai jamais. »
   - `<nom affiché> (Recommended)`
   - `Je ne produis pas`
   - « Other » pour un autre nom, ou plusieurs.
8. `Playlist` : « Tu veux une playlist SoundCloud « À télécharger » ? Tu y ajoutes des sons pendant que tu digs, puis un clic suffit pour tout télécharger. »
   - `Pas maintenant (Recommended)`
   - `Oui, je colle son lien` : le lien va dans « Other ». Il peut être public ou privé.

**D. En texte, une seule question** : « Dernière chose : quel e-mail et quel prénom je donne aux gates ? » Conseille une adresse secondaire, parce que les artistes y enverront des nouvelles.

Les réglages avancés gardent leur valeur par défaut, sans question :
- longs sets ignorés au-delà de 45 min ;
- commentaires « love it », « fire », « wow », « nice » ;
- téléchargements de Chrome dans `~/Downloads`.

Le DJ peut les changer plus tard en le demandant.

## 3. Écrire la config

```bash
djdl init --likes-of <profil> --account <compte-gates> --device <deviceId> \
  --email <email> --first-name <prénom> --droploud-optin yes|no \
  --own "<nom d'artiste>" --dest "<dossier>" [--playlist <lien>] [--library "<dossier>" …] [--keep-both yes|no] [--comments "love it" "fire"] [--skip-minutes 45]
```

(`--force` pour remplacer une config existante. Plus tard : `djdl library add "<dossier>"` / `remove` / `list`.) Puis `djdl check` : tout doit être OK. Si un dossier est « illisible » : sur **Mac**, le DJ autorise l'accès (Réglages Système → Confidentialité et sécurité → Fichiers et dossiers, ou Accès complet au disque) pour l'application qui fait tourner Claude ; sur **Windows**, il choisit un dossier de son profil (Musique, Documents) ou vérifie que le disque externe est branché. Sur Windows, les chemins se donnent tels quels (ex. `D:\Musique\Sets`).

## 4. Fin

Dis au DJ que c'est prêt. Pour télécharger, il tape `/sound-cloud-downloader:download-likes`, puis coche ce qu'il veut et clique « Go ». Il peut aussi demander avec ses mots :
- « télécharge mes nouveaux likes »
- « télécharge les 20 derniers »
- « télécharge ce que j'ai liké aujourd'hui » (ou « depuis lundi »)
- « télécharge ma playlist », ou en collant un lien de playlist ou de sons

ou lancer `/sound-cloud-downloader:download-likes`.
