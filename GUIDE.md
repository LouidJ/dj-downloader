# Premiers pas : tu n'as jamais utilisé Claude

*[English version](GUIDE.en.md) · Guide interactif, une question à la fois : [ouvrir](https://louidj.github.io/dj-downloader/)*

Installation : ~20 minutes, une seule fois. Ensuite, une phrase à chaque fois. Aucun code à écrire.

## 0. Ce qu'il te faut

- Un **Mac** ou un **PC Windows** (10 ou 11), avec **Google Chrome**.
- Un **abonnement Claude payant** (Pro ou Max) : il donne accès à l'onglet « Code » de l'app, où vit le plugin.
- Conseillé : un **deuxième compte SoundCloud** pour les gates (ils demandent de suivre, reposter, commenter). Ton compte principal reste propre.
- Ton **e-mail SoundCloud** : tu le donnes une fois au réglage, les gates le transmettent aux artistes.

## 1. Installer l'app Claude

1. Télécharge l'app sur [claude.ai/download](https://claude.ai/download) et installe-la : sur Mac, glisse-la dans Applications ; sur Windows, lance l'installateur.
2. Ouvre-la et connecte-toi.
3. En haut de la fenêtre, clique sur l'onglet **Code**. C'est là que tout se passe.
4. Si l'app demande un dossier de travail, crée un dossier `DJ` dans Documents et choisis-le. Ta musique n'ira pas là.
5. **Windows** : si l'app te demande d'installer **Git pour Windows**, accepte et suis l'installation proposée (options par défaut). Elle en a besoin pour lancer les commandes.

> **Parler à Claude** : tu écris en bas, dans la zone de texte, comme dans une messagerie, puis Entrée. En français, normalement. Un message qui commence par `/` est une commande : en tapant `/`, la liste s'affiche.

## 2. Préparer Chrome

1. Ouvre l'extension [**Claude**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) sur le Chrome Web Store (éditeur : Anthropic) et clique **Ajouter à Chrome**.
2. Épingle l'extension (icône puzzle en haut à droite).
3. Connecte-toi dans l'extension avec **le même compte Claude** que dans l'app.
4. Dans ce Chrome, connecte-toi à **SoundCloud avec le compte pour les gates**.

Pendant les téléchargements, laisse Chrome ouvert et ne touche pas aux onglets que Claude a ouverts (ils sont regroupés et colorés).

## 3. Installer le plugin

Dans l'onglet Code, ouvre une nouvelle session et colle :

```
Installe le plugin sd-downloader depuis le dépôt GitHub LouidJ/dj-downloader, active-le avec la mise à jour automatique, puis dis-moi quand c'est prêt.
```

1. Claude demande la permission de modifier ses réglages : clique **Autoriser**. Il fait tout le reste.
2. Quand c'est prêt, **ouvre une nouvelle session** : le plugin se charge au démarrage.

Dans le terminal (Claude Code), une seule commande suffit : `/plugin install sd-downloader --marketplace LouidJ/dj-downloader`.

## 4. Tes réglages : deux clics, c'est tout

Clique le bouton **🎧 Installer SD Downloader** au-dessus de la zone où tu écris (ou tape `/sd-downloader:setup`). S'il n'apparaît pas, ouvre une autre nouvelle session. Claude vérifie d'abord que tout est prêt. **Sur Windows**, il peut te demander d'installer **Python** : sur [python.org](https://www.python.org/downloads/), clique Download Python, lance l'installateur et **coche « Add python.exe to PATH »** avant Install. Ouvre ensuite une nouvelle session et retape la commande.

Il te demande d'abord ta **langue** : tout le reste se fait dans ta langue. Ensuite Claude **devine tout seul** le compte SoundCloud connecté dans Chrome, ton e-mail et ton prénom : rien à écrire. Il ne te pose que **deux questions à cliquer** :
- où ranger les sons (Musique, un nouveau dossier sur le Bureau, ou un dossier que tu choisis dans une fenêtre) ;
- en option, une playlist « À télécharger ».

Le reste est réglé pour toi : les likes de ton compte, la version Extended (avant la Radio), et les sons déjà dans ton dossier ne sont jamais retéléchargés. Tu changes ce que tu veux d'une phrase (« garde aussi les versions radio », « mon e-mail c'est … »).

À la fin, Claude te propose une fois, **sans obligation**, de suivre l'auteur du plugin sur SoundCloud, puis affiche un résumé de 3 lignes et un bouton **🚀 Lancer**. Le résumé te prévient : à chaque téléchargement, Claude fera les gates (suivre, liker, reposter, commenter) avec ton compte, sans te redemander. Si tu préfères qu'il demande à chaque fois, dis « demande-moi avant les gates ».

> **Une seule autorisation.** Au début du réglage, Claude te prévient puis affiche **une seule** fenêtre : clique **Autoriser**. Elle couvre le plugin pour toujours, même après ses mises à jour. Ensuite, l'extension Chrome demande l'accès à soundcloud.com, hypeddit.com et droploud.com : choisis à chaque fois l'option qui autorise **toujours** le site. Sur Mac, si le système demande l'accès à Téléchargements ou Musique, accepte. Après ça, plus aucune fenêtre pendant les téléchargements.

## 5. Premier téléchargement

Clique **🚀 Lancer** à la fin du réglage. Claude te demande quels sons (*Mes nouveaux likes*, *Likés aujourd'hui*, *Mes 20 derniers likes*, *Ma playlist*). Pour un tout premier essai, choisis *Autre* et écris « 3 derniers ».

Ensuite :
1. Claude saute les sons déjà dans ton dossier.
2. Il enchaîne tout seul. Dans Chrome, tu le vois ouvrir les pages et cliquer. Le son des pages est coupé.
3. À la fin, un petit son, puis le bilan en tableaux. Les fichiers sont déjà rangés.

Il ne te demande rien pendant le run. Seules exceptions : un CAPTCHA (tu le fais toi-même), un mot de passe, un paiement, un mauvais compte connecté, ou plus de 30 gates d'un coup (SoundCloud pourrait limiter ton compte : tu choisis).

## Au quotidien

Clique le bouton **🎧 Télécharger mes nouveaux likes** au-dessus de la zone où tu écris. C'est tout : Claude prend tout ce que tu as liké depuis la dernière fois.

Pour autre chose, écris-le avec tes mots : « télécharge ce que j'ai liké depuis lundi », « télécharge ma playlist », « télécharge cette playlist : lien ».

**L'astuce de la playlist** : crée sur SoundCloud une playlist « À télécharger ». Pendant que tu digs, ajoute-y les sons. Le soir, dis « télécharge ma playlist ». Les sons déjà téléchargés ne sont jamais refaits.

Autres phrases : « retire #12 de la liste », « garde aussi les versions radio », « montre le bilan ».

## Lire le bilan

- **téléchargé** : le fichier est dans ton dossier.
- **déjà présent** : tu l'avais déjà, même version.
- **long set ignoré** : plus de 45 minutes.
- **manquant** : pas de téléchargement gratuit (Beatport, Bandcamp…) ou gate bloqué. La raison est écrite à côté.
- **à relancer** : refait tout seul au prochain run.

## Si ça coince

- **Claude attend** : regarde sous son dernier message s'il y a des choix ou un bouton **Go** à cliquer. S'il s'est arrêté, écris « continue jusqu'au bout ».
- **Une fenêtre d'autorisation s'affiche** : lis-la et clique **Autoriser**. Si c'est Chrome qui demande l'accès à un site, choisis l'option qui l'autorise **toujours**.
- **Chrome pas connecté** : Chrome ouvert, extension Claude connectée au même compte, puis « réessaie ».
- **La connexion à Chrome saute souvent** (surtout sur Droploud) : pendant un téléchargement, une seule conversation Claude dans Chrome à la fois ; garde la fenêtre Chrome ouverte et le Mac/PC éveillé ; mets à jour Chrome et l'extension Claude. Si un gate est resté sur « Drop unlocked! », clique toi-même sur **Download**, puis dis « range le fichier ».
- **« Pas encore installé »** : tape `/sd-downloader:setup`.
- **CAPTCHA** : fais-le toi-même dans l'onglet, puis « c'est fait ».
- **Tout arrêter** : bouton Stop à côté de la zone de texte (ou Échap). Rien n'est perdu, le prochain run reprend où il en était.
- **Un son gratuit marqué manquant** : « Télécharge ce son : lien ».

## Ce que Claude fait en ton nom

- Avec le compte des gates : suivre, liker, reposter, commenter court, seulement quand un gate l'exige et après ton « go ».
- Donner ton prénom et ton e-mail aux gates qui les demandent.
- Jamais : taper un mot de passe, créer un compte, payer.
- Tes réglages et ton suivi restent sur ton ordi. Tes fichiers audio restent dans ton dossier, même si tu désinstalles le plugin.

Respecte les artistes : ne télécharge que ce qu'ils offrent gratuitement.
