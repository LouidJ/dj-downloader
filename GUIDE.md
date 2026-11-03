# Premiers pas : tu n'as jamais utilisé Claude

*[English version](GUIDE.en.md) · Guide interactif, une question à la fois : [ouvrir](https://louidj.github.io/dj-downloader/)*

Installation : ~15 minutes, une seule fois. Ensuite, une phrase à chaque fois. Aucun code à écrire.

## 0. Ce qu'il te faut

- Un **Mac** ou un **PC Windows** (10 ou 11), avec **Google Chrome**.
- Un **abonnement Claude payant** (Pro ou Max) : le plugin marche dans l'app Claude (Cowork), et l'extension Chrome en a aussi besoin.
- Conseillé : un **deuxième compte SoundCloud** pour les gates (ils demandent de suivre, reposter, commenter). Ton compte principal reste propre.

## 1. Installer l'app Claude

1. Télécharge l'app sur [claude.ai/download](https://claude.ai/download) et installe-la : sur Mac, glisse-la dans Applications ; sur Windows, lance l'installateur.
2. Ouvre-la et connecte-toi. Tu arrives sur l'écran principal (icône bulle en haut à gauche) : c'est là que tout se passe.

> **Parler à Claude** : tu écris en bas, dans la zone de texte, comme dans une messagerie, puis Entrée. En français, normalement. Un message qui commence par `/` est une commande : en tapant `/`, la liste s'affiche.

## 2. Préparer Chrome

1. Ouvre l'extension [**Claude**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) sur le Chrome Web Store (éditeur : Anthropic) et clique **Ajouter à Chrome**.
2. Épingle l'extension (icône puzzle en haut à droite).
3. Connecte-toi dans l'extension avec **le même compte Claude** que dans l'app.
4. Dans ce Chrome, connecte-toi à **SoundCloud avec le compte pour les gates**.

Pendant les téléchargements, laisse Chrome ouvert et ne touche pas aux onglets que Claude a ouverts (ils sont regroupés et colorés).

## 3. Installer le plugin

1. Dans l'app, sur l'écran principal, clique **Personnalisation** dans la barre de gauche, puis **Plugins**.
2. Clique **Ajouter**, puis l'option pour ajouter une marketplace, et colle `LouidJ/dj-downloader`.
3. Installe **SD Downloader** dans la liste.

## 4. Avant chaque tâche : tes dossiers et le mode Auto

À faire à **chaque** nouvelle tâche SD Downloader (réglage compris) :

1. Clique **Créer** en haut à gauche : une nouvelle tâche s'ouvre.
2. Clique **+** à côté de la zone de texte, puis **Ajouter un dossier**, et choisis **Téléchargements**. Recommence pour le dossier où ranger tes sons (par exemple **Musique**).
3. En bas à droite de la zone de texte, clique **Manuel** et choisis **Auto**.

> **Pourquoi Auto ?** En mode Manuel, Claude te demande la permission à chaque série de clics dans Chrome : des dizaines de fenêtres. En Auto, il agit seul pour les actions courantes et ne demande que pour ce qui est risqué. N'utilise pas le mode qui saute toutes les autorisations.

## 5. Tes réglages

Dans la tâche, tape `/sd-downloader:setup`.

Claude te demande ta **langue** : tout le reste se fait dans ta langue. Ensuite il trouve **tout seul** le Chrome où SoundCloud est ouvert, le compte connecté, ton e-mail et ton prénom : rien à écrire. Il range les sons dans le dossier que tu as ajouté (dans Musique, il crée « SoundCloud Downloads »). Un bouton **↩️ Revenir en arrière** te laisse toujours changer d'avis.

Le reste est réglé pour toi : les likes de ton compte, la version Extended (avant la Radio), et les sons déjà dans ton dossier ne sont jamais retéléchargés. Tes réglages et l'historique restent dans ton dossier de sons (dossier caché `.sd-downloader`).

À la fin, Claude te propose une fois, **sans obligation**, de suivre l'auteur du plugin sur SoundCloud, puis affiche un résumé de 2 lignes et un bouton **🚀 Lancer**. Le résumé te prévient : à chaque téléchargement, Claude fera les gates (suivre, liker, reposter, commenter) avec ton compte, sans te redemander. Si tu préfères qu'il demande à chaque fois, dis « demande-moi avant les gates ».

> **Les fenêtres à accepter, une seule fois** : pour soundcloud.com, hypeddit.com et droploud.com, choisis **Toujours autoriser pour ce site web** ; pour la connexion à ton Chrome, **Autoriser**.

## 6. Premier téléchargement

Clique **🚀 Lancer** à la fin du réglage. Claude te demande quels sons (*Tous mes likes*, *Likés aujourd'hui*, *Mes 20 derniers likes*, *Les tracks de cette playlist*). Pour un tout premier essai, choisis *Autre* et écris « 3 derniers ».

Ensuite :
1. Claude saute les sons déjà dans ton dossier.
2. Il enchaîne tout seul. Dans Chrome, tu le vois ouvrir les pages et cliquer. Le son des pages est coupé.
3. À la fin, un bilan court : combien de nouveaux sons, et un tableau. Les fichiers sont déjà rangés dans ton dossier.

Il ne te demande rien pendant le run. Seules exceptions : un CAPTCHA (tu le fais toi-même), un mot de passe, un paiement, un mauvais compte connecté, ou plus de 30 gates d'un coup (SoundCloud pourrait limiter ton compte : tu choisis).

## Au quotidien

Nouvelle tâche, tes deux dossiers avec **+**, mode **Auto**, puis écris « télécharge mes nouveaux likes ». Claude prend tout ce que tu as liké depuis la dernière fois.

Pour autre chose, écris-le avec tes mots : « télécharge ce que j'ai liké depuis lundi », « télécharge ma playlist », « télécharge cette playlist : lien ».

**L'astuce de la playlist** : crée sur SoundCloud une playlist « À télécharger ». Pendant que tu digs, ajoute-y les sons. Le soir, dis « télécharge ma playlist ». Les sons déjà téléchargés ne sont jamais refaits.

Autres phrases : « retire #12 de la liste », « garde aussi les versions radio », « seulement les WAV », « montre le bilan ». Le choix **⚙️ Réglages** (à partir du 2e lancement) règle les formats (WAV, AIFF, MP3, un ou plusieurs, ou tous), les versions (Extended, Radio ou les deux), le nettoyage des noms de fichiers (V2, master…) et les zips (Corbeille ou gardés). Si l'artiste ne propose qu'un autre format, le son est gardé et signalé dans le bilan.

## Lire le bilan

- **téléchargé** : le fichier est dans ton dossier.
- **déjà présent** : tu l'avais déjà, même version.
- **long set ignoré** : plus de 45 minutes.
- **manquant** : pas de téléchargement gratuit (Beatport, Bandcamp…) ou gate bloqué. La raison est écrite à côté.
- **à relancer** : refait tout seul au prochain run.

## Tu as aussi Claude Code ?

Le plugin marche aussi dans l'onglet **Code** (`</>`) : `/plugin install sd-downloader --marketplace LouidJ/dj-downloader`, puis le bouton **🎧** au-dessus de la zone de texte. Là, il y a moins de fenêtres d'autorisation, un petit son à la fin, et un bouton **📂 Ouvrir le dossier**. **Windows** : l'app peut demander **Git pour Windows**, et Claude peut demander **Python** ([python.org](https://www.python.org/downloads/), cocher « Add python.exe to PATH »).

## Si ça coince

- **Claude attend** : regarde sous son dernier message s'il y a des choix ou un bouton **Go** à cliquer. S'il s'est arrêté, écris « continue jusqu'au bout ».
- **Une fenêtre à chaque clic** : la tâche est en mode Manuel. Passe-la en **Auto**, en bas à droite.
- **Claude ne trouve pas ton dossier** : clique **+**, puis **Ajouter un dossier**, et choisis-le. Puis « c'est fait ».
- **Chrome pas connecté** : Chrome ouvert, extension Claude connectée au même compte, puis « réessaie ».
- **La connexion à Chrome saute souvent** (surtout sur Droploud) : pendant un téléchargement, une seule conversation Claude dans Chrome à la fois ; garde la fenêtre Chrome ouverte et le Mac/PC éveillé ; mets à jour Chrome et l'extension Claude. Si un gate est resté sur « Drop unlocked! », clique toi-même sur **Download**, puis dis « range le fichier ».
- **« Pas encore installé »** : tape `/sd-downloader:setup`.
- **CAPTCHA** : fais-le toi-même dans l'onglet, puis « c'est fait ».
- **Tout arrêter** : bouton Stop à côté de la zone de texte (ou Échap). Rien n'est perdu, le prochain run reprend où il en était.
- **Un son gratuit marqué manquant** : « Télécharge ce son : lien ».

## Ce que Claude fait en ton nom

- Avec le compte des gates : suivre, liker, reposter, commenter court, seulement quand un gate l'exige.
- Donner ton prénom et ton e-mail aux gates qui les demandent.
- Jamais : taper un mot de passe, créer un compte, payer, ouvrir un lien trouvé dans un fichier téléchargé.
- Tes réglages et ton suivi restent dans ton dossier de sons. Tes fichiers audio restent dans ton dossier, même si tu désinstalles le plugin.

Respecte les artistes : ne télécharge que ce qu'ils offrent gratuitement.
