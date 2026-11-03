# Choisir les sons à télécharger

Le DJ dit avec ses mots quels sons il veut. Traduis sa demande en une sélection, **annonce-la en une ligne** (« Je prends tes likes du 29/10, 6 sons »), puis lance le run. Si la demande ne dit pas quels sons, propose des choix à cocher (voir plus bas), ne demande pas d'écrire.

Les dates : aujourd'hui est la date du jour sur l'ordi (`date +%F`). « Hier », « cette semaine » (depuis lundi), « ce mois-ci », « depuis vendredi », « depuis le 20 »… : calcule la date de début en AAAA-MM-JJ.

Aucune limite de nombre ni de jour : on prend tout ce que la demande couvre. Réglages du script de lecture des likes (`playbook.md` §2a) : `N`, `SINCE`, `STOP`.

| Le DJ dit… | Lecture | Import |
|---|---|---|
| « mes nouveaux likes », « mets à jour », le choix `Mes nouveaux likes` ou `Tous mes likes` | likes §2a : `N=Infinity`, `STOP=` sortie de `djdl known` | `djdl import F --new` (premier passage : tous ses likes, l'annoncer avec le nombre) |
| « tous mes likes » | likes §2a : `N=Infinity` | `djdl import F` |
| « les 20 derniers », « mes 20 derniers likes » | likes §2a : `N=20` | `djdl import F --limit 20` |
| « likés aujourd'hui » | likes §2a : `SINCE='<aujourd'hui>'` | `djdl import F --since <aujourd'hui>` |
| « likés hier » | likes §2a : `SINCE='<hier>'` | `djdl import F --since <hier> --until <hier>` |
| « cette semaine », « depuis le 20 octobre » | likes §2a : `SINCE='<date>'` | `djdl import F --since <date>` |
| « les 10 derniers likés aujourd'hui » | likes §2a : `SINCE='<aujourd'hui>'` | `djdl import F --since <aujourd'hui> --limit 10` |
| « télécharge ma playlist » (sans lien) | §2b avec `soundcloud.download_playlist` de la config | `djdl import F --source "playlist:<titre>"` |
| un lien de playlist, ou « la playlist <nom> » | §2b avec ce lien (sinon chercher la playlist sur `soundcloud.com/<likes_of>/sets`, ou du compte des gates si `likes_of` est vide) | `djdl import F --source "playlist:<titre>"` |
| un ou plusieurs liens de sons collés | §2b avec ces liens | `djdl import F --source liens` |

`F` est le fichier écrit au §2c.

Après `import` :

- La ligne « Sélection : … » dit combien de sons sont nouveaux et lesquels étaient déjà suivis (avec leur statut). Un son déjà « téléchargé », « déjà présent » ou « retiré » n'est pas refait. Un son « manquant » ou « à relancer » qui revient dans une sélection peut être retenté : demande au DJ seulement s'il y en a.
- Traiter cette sélection : `djdl todo --last`. Les sons « à relancer » dont la date est arrivée y sont toujours ajoutés.
- Une grosse sélection (des centaines de sons) se traite en entier, sans s'arrêter ni demander. Si la session est interrompue, le run suivant reprend là où il en était : les sons faits ne sont jamais refaits.
- Bilan de cette sélection : `djdl report --last`.

## Des cases à cocher, pas de texte à écrire

Le DJ ne doit rien avoir à taper. Pose tes questions avec l'outil **`AskUserQuestion`** : il affiche des choix cliquables, et « Other » reste là pour écrire autre chose. Chaque description de choix commence par une **majuscule**. Seulement si cet outil n'est pas disponible, pose la question en texte.

**Langue** : les libellés ci-dessous sont en français. Utilise la langue de la config (`language`, choisie au réglage), ou celle où le DJ t'écrit s'il en change, et traduis-les (par exemple `My new likes (Recommended)`, `Go (Recommended)` / `Cancel`), et parle-lui dans cette langue pendant tout le run.

**Si la demande ne dit pas quels sons** (la commande seule, « télécharge », « lance-toi »…) : **un seul** appel `AskUserQuestion` avec ces deux questions. Si la config dit `"go": "auto"`, seulement la première (le feu vert est déjà donné).

1. Question « Quels sons je télécharge ? », en-tête `Sons`, choix unique :
   - premier choix, selon `djdl known` (lancé avant la question) :
     - `[]` (aucun like encore suivi, première utilisation) : `Tous mes likes (Recommended)` : Je télécharge tous tes likes ;
     - sinon : `Mes nouveaux likes (Recommended)` : Tout ce que tu as liké depuis la dernière fois ;
   - `Likés aujourd'hui` : Seulement les likes du jour ;
   - première utilisation (`djdl known` vaut `[]`) : `Mes 20 derniers likes` : Les 20 likes les plus récents ; ensuite : `⚙️ Réglages` : Formats, versions, noms de fichiers, zips (menu « ⚙️ Réglages » du skill) ;
   - `Ma playlist` : Ta playlist « À télécharger » (seulement si `soundcloud.download_playlist` est réglé ; sinon, `Les tracks de cette playlist` : Colle le lien d'une playlist dans « Autre chose », je télécharge toutes ses tracks (publique ou privée)).

   `Les tracks de cette playlist` : si le DJ a collé un lien dans « Autre chose », prends-le ; sinon demande-le en une phrase (« Colle le lien de la playlist SoundCloud. »), puis traite-le comme un lien de playlist (tableau ci-dessus). Quatre choix au plus : « cette semaine », « 20 derniers » et les autres dates ou nombres s'écrivent dans « Autre chose ».

   Dans « Other », le DJ peut écrire un autre nombre, une date, ou coller un lien de playlist ou de sons. Traduis-le avec le tableau ci-dessus.
2. Question « Je fais tout jusqu'au bilan ? », en-tête `Feu vert`, choix unique :
   - `Go (Recommended)`. Description d'une ligne : « Je fais les gates avec `<account>` et je range dans `<dossier>`. » Pas la liste des actions, pas l'e-mail. C'est le feu vert du run (étape 2b) ;
   - `Montre-moi d'abord` : Je lis la sélection, je te dis combien de sons et de gates, puis tu valides.

**Si la demande dit déjà quels sons** mais sans feu vert : pose seulement le feu vert, à l'étape 2b, une fois la sélection lue et comparée. Utilise `AskUserQuestion`, en-tête `Feu vert`. La question tient en une ligne : « Je télécharge Thriller (Christian Maas Edit) ? » pour un son, « Je télécharge 12 sons (3 directs, 6 Hypeddit, 3 Droploud) ? » pour plusieurs. Deux choix : `Go (Recommended)` (même description d'une ligne que ci-dessus) et `Annuler`.

**Ne demande pas le feu vert** si le DJ a déjà répondu `Go`, s'il a écrit « go pour tout », s'il n'y a aucun gate, ou si la config dit `"go": "auto"` (sauf au-delà de 30 gates).

Utilise aussi `AskUserQuestion` pour les rares autres questions d'un run, par exemple « Retenter les 3 sons manquants qui reviennent ? » avec `Oui` / `Non`.

Conseil à donner au DJ s'il demande comment choisir facilement : créer sur SoundCloud une playlist (publique ou avec lien privé) « À télécharger », y ajouter les sons au fil de l'eau, puis dire « télécharge ma playlist ». Les sons déjà téléchargés ne sont jamais refaits, donc pas besoin de vider la playlist.
