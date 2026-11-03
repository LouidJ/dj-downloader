# SD Downloader — télécharge tes likes et tes playlists SoundCloud automatiquement

**🇬🇧 English: [README.en.md](README.en.md)** · Le réglage te demande ta langue : tout se fait ensuite dans ta langue.

Plugin gratuit pour Claude, pour les DJ sur Mac et Windows. Tu likes des sons sur SoundCloud, ou tu les mets dans une playlist, et Claude les télécharge pour toi :

- **téléchargement SoundCloud direct** quand l'artiste l'autorise ;
- **gates Hypeddit et Droploud** : follow, like, repost, commentaire, e-mail… Claude fait toutes les étapes ;
- **rangement** : chaque fichier va directement dans ton dossier. Pour un zip, il garde la meilleure version (la coupe que tu as choisie, WAV/AIFF avant MP3) et jette le reste. Extended, Radio ou les deux : tu choisis à l'installation, ou plus tard (« garde aussi les versions radio »). Les doublons partent à la corbeille ;
- **bilan** à la fin : ce qui est téléchargé, déjà présent, ignoré (longs sets, doublons) et ce qui manque, avec la raison ;
- **pas de doublon** : avant de télécharger, Claude regarde ton dossier et saute les sons que tu as déjà, dans la même version ; le bilan te dit lequel tu avais ;
- **jamais deux fois le même son** : chaque son est suivi d'un run à l'autre, même s'il revient dans une playlist ;
- **s'adapte** : si un site change, Claude trouve le nouveau bouton, termine, et note le changement pour les fois suivantes.

**Tu n'as jamais utilisé Claude ?** Suis le guide pas à pas, une question à la fois : [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/). Version texte : [GUIDE.md](GUIDE.md).

**Never used Claude?** Step-by-step guide, one question at a time: [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/). Text version: [GUIDE.en.md](GUIDE.en.md).

## Ce qu'il te faut

- Un Mac ou un PC Windows, avec Google Chrome.
- Python 3 (déjà là sur Mac après `xcode-select --install` ; sur Windows, depuis python.org en cochant « Add python.exe to PATH »). L'installation guidée vérifie et t'explique.
- L'app Claude (onglet Code) ou Claude Code, avec un abonnement Claude.
- L'extension [**Claude in Chrome**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn), connectée.
- Ton compte SoundCloud connecté dans ce Chrome. Claude y lit tout seul ton e-mail et ton prénom pour les gates.

## Installation

Dans Claude (onglet Code ou terminal), tape :

```
/plugin install sd-downloader --marketplace LouidJ/dj-downloader
```

(Claude Code v2.1.275 ou plus récent. Sinon : `/plugin marketplace add LouidJ/dj-downloader` puis `/plugin install sd-downloader@dj-downloader`.)

Dans l'app Claude (onglet Code), le plus simple est de coller : « Installe le plugin sd-downloader depuis le dépôt GitHub LouidJ/dj-downloader ». Claude s'occupe du reste. Ouvre ensuite une nouvelle session.

Pour recevoir les améliorations toutes seules : `/plugin` → **Marketplaces** → `dj-downloader` → **Enable auto-update**.

Puis clique le bouton **🎧 Installer SD Downloader** au-dessus de la zone où tu écris (ou tape `/sd-downloader:setup`).

Deux questions à cliquer : ta langue et où ranger les sons. Le compte SoundCloud, l'e-mail et le prénom sont lus tout seuls. Il ne te demande jamais de mot de passe : tu te connectes toi-même. À la fin, un bouton lance ton premier téléchargement.

## Utilisation

Clique **🎧 Télécharger mes nouveaux likes** au-dessus de la zone où tu écris : Claude prend tout ce que tu as liké depuis la dernière fois, fait les gates avec ton compte (tu as donné ton accord une fois au réglage), range tout, joue un petit son et te donne le bilan.

Tu peux aussi dire ce que tu veux avec tes mots :

| Tu dis | Claude prend |
|---|---|
| « Télécharge mes nouveaux likes » | tout ce que tu as liké depuis la dernière fois |
| « Télécharge les 20 derniers » | tes 20 derniers likes |
| « Télécharge ce que j'ai liké aujourd'hui » | les likes du jour (marche aussi avec « hier », « depuis lundi », « depuis le 20 octobre ») |
| « Télécharge ma playlist » | ta playlist « À télécharger » (proposée après ton premier téléchargement) |
| « Télécharge cette playlist : <lien> » | une playlist entière, même privée avec son lien privé |
| « Télécharge ces sons : <liens> » | les sons collés |

Ou bien `/sd-downloader:download-likes 20 derniers`.

**Le plus simple pour choisir** : crée une playlist SoundCloud « À télécharger », publique ou privée avec son lien privé. Ajoutes-y les sons au fil de l'eau, puis dis « télécharge ma playlist ». Les sons déjà téléchargés ne sont jamais refaits : pas besoin de vider la playlist.

Ensuite :

- « retire #12 de la liste » : ce son ne sera plus jamais proposé ;
- « montre le bilan » ;
- « réessaie demain » : pour un son à retenter plus tard ;
- « ma playlist à télécharger, c'est <lien> » : pour la changer ;
- « demande-moi avant les gates » : Claude te redemande l'accord à chaque téléchargement.

## Bon à savoir

- Les gates Droploud exigent parfois de s'inscrire aux nouvelles de l'artiste pour donner le son : Claude coche la case, comme tu le ferais.
- Facultatif : à la fin du réglage, Claude te propose une seule fois de suivre l'auteur du plugin sur SoundCloud. Il ne suit que si tu dis oui, et ne demande rien si tu le suis déjà.
- Aucune limite : prends 5 sons ou 500, Claude va jusqu'au bout. Si SoundCloud bloque un téléchargement direct (limite de SoundCloud), Claude passe tout de suite par le gate Hypeddit / Droploud quand il existe.
- Beatport, Bandcamp et les autres sites payants ne sont pas touchés : ces sons sont listés comme manquants.
- Tes réglages et ton suivi restent sur ton Mac (`~/.claude/plugins/data/`). Ils sont supprimés si tu désinstalles le plugin. Tes fichiers audio, eux, restent dans ton dossier.
- Respecte les artistes : ne télécharge que ce qu'ils offrent gratuitement.

Licence MIT.
