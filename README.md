# SD Downloader — télécharge tes likes et tes playlists SoundCloud automatiquement

Plugin gratuit pour Claude, pour les DJ sur Mac et Windows. Tu likes des sons sur SoundCloud, ou tu les mets dans une playlist, et Claude les télécharge pour toi :

- **téléchargement SoundCloud direct** quand l'artiste l'autorise ;
- **gates Hypeddit et Droploud** : follow, like, repost, commentaire, e-mail… Claude fait toutes les étapes ;
- **rangement** : chaque fichier va directement dans ton dossier. Pour un zip, il garde la meilleure version (Extended avant Radio, WAV/AIFF avant MP3) et jette le reste. Tu préfères garder la Radio **et** l'Extended ? Dis-le à l'installation, ou plus tard : « garde aussi les versions radio ». Les doublons partent à la corbeille ;
- **bilan** à la fin : ce qui est téléchargé, déjà présent, ignoré (longs sets, tes propres sons) et ce qui manque, avec la raison ;
- **compare avec tes sons** : avant de télécharger, Claude regarde dans tes dossiers (Musique, rekordbox, Serato, clé USB…) et saute les sons que tu as déjà, dans la même version ;
- **jamais deux fois le même son** : chaque son est suivi d'un run à l'autre, même s'il revient dans une playlist ;
- **s'adapte** : si un site change, Claude trouve le nouveau bouton, termine, et note le changement pour les fois suivantes.

**Tu n'as jamais utilisé Claude ?** Suis le guide pas à pas, une question à la fois : [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/). Version texte : [GUIDE.md](GUIDE.md).

**Never used Claude?** Step-by-step guide, one question at a time: [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/). Text version: [GUIDE.en.md](GUIDE.en.md).

## Ce qu'il te faut

- Un Mac ou un PC Windows, avec Google Chrome.
- Python 3 (déjà là sur Mac après `xcode-select --install` ; sur Windows, depuis python.org en cochant « Add python.exe to PATH »). L'installation guidée vérifie et t'explique.
- L'app Claude (onglet Code) ou Claude Code, avec un abonnement Claude.
- L'extension [**Claude in Chrome**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn), connectée.
- Conseillé : un **second compte SoundCloud** pour les gates (reposts, follows), connecté dans ce Chrome. Ton compte principal reste propre.
- Conseillé : une adresse e-mail secondaire pour les gates.

## Installation

Dans Claude (onglet Code ou terminal), tape :

```
/plugin install sd-downloader --marketplace LouidJ/dj-downloader
```

(Claude Code v2.1.275 ou plus récent. Sinon : `/plugin marketplace add LouidJ/dj-downloader` puis `/plugin install sd-downloader@dj-downloader`.)

Dans l'app Claude (onglet Code), le plus simple est de coller : « Installe le plugin sd-downloader depuis le dépôt GitHub LouidJ/dj-downloader ». Claude s'occupe du reste. Ouvre ensuite une nouvelle session.

Pour recevoir les améliorations toutes seules : `/plugin` → **Marketplaces** → `dj-downloader` → **Enable auto-update**.

Puis lance l'installation guidée :

```
/sd-downloader:setup
```

Claude te demande ton profil SoundCloud, le compte pour les gates, ton e-mail, ton nom d'artiste, ton dossier de téléchargement et les dossiers où tu as déjà des sons. Il ne te demande jamais de mot de passe : tu te connectes toi-même.

## Utilisation

Tape `/sd-downloader:download-likes` : Claude te propose des choix (nouveaux likes, likés aujourd'hui, 20 derniers, ta playlist…). Tu coches, puis tu cliques **Go**. Rien à écrire.

Tu peux aussi dire ce que tu veux avec tes mots :

| Tu dis | Claude prend |
|---|---|
| « Télécharge mes nouveaux likes » | tout ce que tu as liké depuis la dernière fois |
| « Télécharge les 20 derniers » | tes 20 derniers likes |
| « Télécharge ce que j'ai liké aujourd'hui » | les likes du jour (marche aussi avec « hier », « depuis lundi », « depuis le 20 octobre ») |
| « Télécharge ma playlist » | ta playlist « À télécharger » (donnée à l'installation) |
| « Télécharge cette playlist : <lien> » | une playlist entière, même privée avec son lien privé |
| « Télécharge ces sons : <liens> » | les sons collés |

Ou bien `/sd-downloader:download-likes 20 derniers`.

**Le plus simple pour choisir** : crée une playlist SoundCloud « À télécharger », publique ou privée avec son lien privé. Ajoutes-y les sons au fil de l'eau, puis dis « télécharge ma playlist ». Les sons déjà téléchargés ne sont jamais refaits : pas besoin de vider la playlist.

Ensuite :

- « retire #12 de la liste » : ce son ne sera plus jamais proposé ;
- « montre le bilan » ;
- « réessaie demain » : pour un son à retenter plus tard ;
- « ma playlist à télécharger, c'est <lien> » : pour la changer ;
- « compare aussi avec ma clé USB » : ajoute un dossier de sons à comparer.

## Bon à savoir

- Les gates Droploud exigent parfois de s'inscrire aux nouvelles de l'artiste. Claude te demande une fois à l'installation si tu es d'accord. Si tu refuses, ces sons sont marqués manquants.
- Aucune limite : prends 5 sons ou 500, Claude va jusqu'au bout. Si SoundCloud bloque un téléchargement direct (limite de SoundCloud), Claude passe tout de suite par le gate Hypeddit / Droploud quand il existe.
- Beatport, Bandcamp et les autres sites payants ne sont pas touchés : ces sons sont listés comme manquants.
- Tes réglages et ton suivi restent sur ton Mac (`~/.claude/plugins/data/`). Ils sont supprimés si tu désinstalles le plugin. Tes fichiers audio, eux, restent dans ton dossier.
- Respecte les artistes : ne télécharge que ce qu'ils offrent gratuitement.

Licence MIT.
