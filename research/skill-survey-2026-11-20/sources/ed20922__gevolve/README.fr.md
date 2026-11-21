# gevolve

**L'évolution de programmes à la manière d'AlphaEvolve, en skill Claude Code, faite pour les juges auxquels on
ne peut pas se fier entièrement.**

Un modèle propose beaucoup de petites modifications d'un programme, un juge automatique note chacune, on garde
les bonnes et on repart d'elles. Cette boucle est puissante, et il est facile de s'y mentir : sur une note
bruitée, elle finit toujours par « trouver » quelque chose. gevolve, c'est la boucle plus la discipline qui
l'en empêche.

Il vous dit honnêtement quand votre idée ne marche pas. C'est sa fonction.

[English version](README.md)

## Ce que c'est

Un skill [Claude Code](https://claude.com/claude-code) (`/gevolve`), un script Python (bibliothèque standard
seule) et un sous-agent. Claude tient la conversation, écrit le juge et lance les sous-agents ; le script fait
tout ce qui doit être exact : empreintes, journal chaîné, budget, marges d'erreur, test scellé.

## Ce qui le distingue

Les versions libres d'AlphaEvolve soignent le moteur de recherche et supposent une note exacte. Les boucles
d'expériences autonomes gardent une modification quand la mesure de validation monte. C'est juste quand le juge
est déterministe. La plupart des vrais problèmes (prévision, règles de décision, tout ce qui se mesure sur un
historique) ne le sont pas. gevolve ajoute ce qu'un juge bruité exige :

| Problème | Ce que fait gevolve |
|---|---|
| Une variante paraît meilleure par chance | Elle n'est gardée que si son gain sur son parent dépasse sa **marge d'erreur**, calculée en rééchantillonnant des jours entiers. |
| Le gain vient d'un seul mois chanceux | **Juge généralisateur** : le gain doit se voir dans la plupart des familles (mois, actifs, segments). |
| La validation s'use à force de sélection | Un **test scellé** que la boucle ne voit jamais, ouvert une fois. Le seuil de réussite est écrit **avant** la première génération, et figé. |
| Le juge ou les données changent en douce | Tout est **figé par empreinte** au verrou. Toute commande refuse de tourner si une empreinte a bougé. |
| Le programme évolué triche | Il tourne dans un **processus séparé**, reçoit un cas à la fois, ne peut ni lire un fichier, ni lancer un processus, ni atteindre le juge. |
| Une donnée du futur entre dans l'entrée | Chaque cas peut porter la **date de chaque source** ; un cas dont une source est postérieure à la décision est refusé. Un relevé témoin compare l'entrée en direct à sa reconstruction. |
| La référence est malhonnête | Auto-tests avant le verrou : un **programme au hasard** ne doit pas battre la référence, le juge doit être déterministe. |
| On règle des seuils au lieu de découvrir | **Qualification avant toute génération** : les approches connues et une grille déclarée sont notées par le même juge. Si la grille suffit, gevolve le dit et saute l'évolution. |
| Les mutateurs apprennent ce qui marche en validation | Les sous-agents ne voient **jamais un score de validation**. Leur diagnostic vient du train, par segment. |
| Une seule idée est creusée sans fin | Un **registre d'hypothèses** (« pistes ») : chacune a son mécanisme et le chiffre qui la réfuterait ; une piste sans progrès est fermée avec sa raison. |

Avant tout code, le skill mène aussi avec vous une courte conception d'expérience : cinq questions fixes
(mesure, référence, données et dates, seuil de réussite, limites), sans réponse floue. **C'est vous, pas le
modèle, qui validez ce que « réussir » veut dire.**

## Ce que ce n'est pas

- **Pas un générateur de gains.** Il ne crée pas d'information. Sur un problème bruité sans donnée nouvelle, il
  prouve proprement qu'il n'y a rien.
- **Pas un remplaçant de la grille.** Si la solution tient en deux seuils, une grille coûte moins. gevolve le
  mesure et le dit.
- **Pas gratuit.** Une mutation coûte environ 18 000 jetons ; une évolution de 40 variantes avec sa recherche se
  compte en centaines de milliers.

## Où il sert

| Le mieux (note exacte) | Bien (note bruitée, beaucoup de cas) | À éviter |
|---|---|---|
| Vitesse d'une fonction, d'une requête | Prévision (demande, délais, probabilités) | Aucune note automatique possible |
| Heuristiques : rangement, tournées, plannings | Classement et détection avec historique étiqueté | Quelques dizaines de cas |
| Compression, mémoire, taille | Règles de décision jugées sur l'historique, trading compris | Une solution qui tient en deux seuils |

## Installation

Il faut Claude Code et Python 3.10 ou plus, sous macOS ou Linux (testé avec Python 3.14 sous macOS).

```bash
git clone https://github.com/ed20922/gevolve.git
cd gevolve
./install.sh
```

Puis, dans Claude Code : `/gevolve objectif "…"`.

## L'exemple

[`examples/bin_packing`](examples/bin_packing) est une évolution complète, prête à verrouiller : ranger des
colis dans des bacs, un colis à la fois. Voir son README.

## Langue

Les instructions du skill, le sous-agent, les gabarits et l'exemple sont en anglais. Le script garde ses noms de
commandes, ses clés de configuration et ses messages en français.

## Crédits et licence

Inspiré d'AlphaEvolve (Novikov et al., Google DeepMind, 2025) et de FunSearch (Romera-Paredes et al., Nature,
2023). Sans lien avec Google DeepMind ni Anthropic. Licence MIT.
