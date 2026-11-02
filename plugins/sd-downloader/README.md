# SD Downloader

Plugin gratuit pour les DJ, sur Mac et Windows. Tu choisis des sons SoundCloud (tes nouveaux likes, ceux du jour, les 20 derniers, une playlist ou des liens). Claude récupère les **téléchargements gratuits que les artistes proposent** : le bouton de téléchargement SoundCloud, ou les gates Hypeddit et Droploud. Il range les fichiers dans ton dossier sans doublons, puis te fait un bilan.

*English: a free plugin for DJs. It collects the free downloads that artists offer for the SoundCloud tracks you pick (likes, a playlist or links), either through SoundCloud's own download button or through Hypeddit and Droploud download gates. It files the tracks in your music folder without duplicates and reports what it got and what is missing. Paid stores are never touched.*

## Utilisation

1. `/sd-downloader:setup` : réglages, une seule fois. Claude détecte ton compte et tes dossiers, tu coches les choix.
2. `/sd-downloader:download-likes` : tu coches les sons voulus, tu cliques **Go**, Claude fait le reste.

Guide pas à pas pour débutants : [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/) (FR / EN), ou en texte : [GUIDE.md](../../GUIDE.md), [GUIDE.en.md](../../GUIDE.en.md).

## Ce dont le plugin a besoin

- L'extension **Claude in Chrome**, connectée. Claude s'en sert pour ouvrir soundcloud.com, hypeddit.com et droploud.com dans **ton** Chrome, avec **tes** comptes.
- Python 3, pour le petit outil local `scripts/djdl.py`.

## Ce que le plugin fait, et où vont tes données

**Dans ton navigateur**, à travers Claude in Chrome :
- Il lit tes likes ou ta playlist sur soundcloud.com. Ce sont les réponses que la page SoundCloud reçoit déjà ; elles ne partent nulle part ailleurs.
- Il clique sur le bouton de téléchargement SoundCloud quand l'artiste l'a activé.
- Il remplit les gates Hypeddit et Droploud. Avec ton compte SoundCloud, il suit l'artiste, like, reposte, laisse un commentaire court et autorise l'application SoundCloud du gate. Il donne ton **prénom** et ton **e-mail** aux gates qui les demandent. Tout cela ne se fait qu'après ton **Go**, une fois par session de téléchargement. La case « recevoir les nouvelles de l'artiste » de Droploud n'est cochée que si tu l'as accepté au réglage.
- **Facultatif** : à la fin du réglage, puis à la fin d'une grosse playlist (10 sons ou plus), il te propose de suivre l'auteur du plugin sur SoundCloud ([Luigi Hayek](https://soundcloud.com/luigi-hayek)). Il ne suit que si tu cliques « Oui ». Si tu le suis déjà, il ne demande rien. « Ne plus me proposer » arrête pour de bon. Le plugin marche pareil quelle que soit ta réponse.
- Il ne tape jamais de mot de passe, ne crée aucun compte, ne paie rien et ne résout pas les CAPTCHA.

**Sur ton ordinateur**, avec `scripts/djdl.py` (Python, sans aucun accès réseau) :
- Il range les fichiers arrivés dans Téléchargements. Il vérifie leur adresse d'origine (métadonnée posée par Chrome : macOS `kMDItemWhereFroms` via `xattr` / `mdls`, Windows flux `Zone.Identifier`). Il décompresse les zip (`ditto` sur Mac, Python ailleurs) et envoie les doublons à la Corbeille (PowerShell sous Windows). Rien n'est jamais supprimé définitivement.
- **Une seule autorisation.** Au tout début du réglage, avec ton accord (une fenêtre : tu cliques Autoriser), `scripts/autoriser.py` ajoute à tes réglages de Claude Code (`~/.claude/settings.json`, liste `permissions.allow`) quelques règles, sans rien changer d'autre. Il garde une copie de l'ancien fichier (`settings.json.avant-djdl`). Ces règles autorisent uniquement l'outil `djdl.py` de **cette version** du plugin et les fichiers du plugin. Après une mise à jour, le réglage redemande l'accord une fois. `djdl perms` affiche les règles. L'extension Claude in Chrome n'est **pas** autorisée en permanence : elle l'est seulement pendant un réglage ou un téléchargement, et uniquement pour les outils dont le plugin a besoin. Pour tout retirer : `python3 -I scripts/autoriser.py --home <dossier du plugin> --remove`. Tu peux les retirer de ce fichier quand tu veux : Claude redemandera alors la permission à chaque étape.
- Il lit, sans les modifier, les dossiers de musique que tu indiques, pour ne pas télécharger un son que tu as déjà.
- Il garde tes réglages et ton suivi dans le dossier de données du plugin (`config.json`, `state.json`). On y trouve : les profils SoundCloud, l'identifiant du navigateur choisi, ton prénom et ton e-mail pour les gates, tes dossiers, et la liste des sons suivis. Ce dossier est supprimé quand tu désinstalles le plugin. Tes fichiers audio restent dans ton dossier.

**Aucune donnée n'est envoyée à l'auteur du plugin ni à un autre service.** Les seules données transmises sont ton prénom et ton e-mail, aux gates Hypeddit / Droploud qui les exigent pour te donner le son.

## Respect des artistes

Le plugin ne récupère que ce que les artistes offrent gratuitement. Les sons vendus sur Beatport, Bandcamp ou ailleurs sont listés comme manquants, jamais contournés. Ce plugin est indépendant : il n'est affilié ni à SoundCloud, ni à Hypeddit, ni à Droploud.

Licence MIT.
