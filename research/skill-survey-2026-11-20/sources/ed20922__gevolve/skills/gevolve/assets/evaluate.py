#!/usr/bin/env python3
"""Juge de l'évolution. FIGÉ dès que `gevolve.py verrouiller` a tourné : ne plus y toucher.

Ce que gevolve lance :
    python3 evaluate.py --programme <fichier> --split {rapide,train,validation,test}
avec GEVOLVE_RESULTAT=<fichier.json>. Le juge y écrit, pour chaque cas du split :
    {"cas": [{"id": "...", "jour": "AAAA-MM-JJ", "gain": nombre ou null, "ref": nombre}, ...]}
  gain = résultat de la décision du programme sur ce cas (null = il s'abstient, non compté)
  ref  = résultat d'une référence honnête sur le même cas (0 s'il n'y en a pas)
gevolve calcule lui-même SCORE = moyenne(gain − ref) sur les cas où le programme agit,
N, et la marge d'erreur en rééchantillonnant des JOURS entiers (les cas d'un même jour se
ressemblent : les compter comme indépendants rendrait la marge trop petite).
Pour un problème où le score n'est pas une moyenne par cas, écrire plutôt
    {"score": x, "n": ..., "ref": ...}  (mode « score », sans marge d'erreur).

Ce qu'il faut remplir : charger_cas() et gain_et_ref(). Le reste est la protection.

Règles :
  - Découper par le TEMPS : train = le plus ancien, validation = la suite, test = le plus
    récent. « rapide » = un petit morceau du train.
  - L'« entree » d'un cas ne contient que ce qu'on savait au moment de décider. La
    « verite » (résultat, règlement) reste dans le juge.
  - La référence doit être honnête et NE PAS recopier le gain. Pour du trading : ref = 0,
    avec le prix payé pris comme probabilité (gain = issue − prix − frais). Piège classique :
    « acheter au hasard au même prix » appliqué au résultat réalisé redonne exactement le gain,
    et tout le monde score 0 ±0 (`verrouiller` le refuse désormais).
  - Mettre dans autotests/programme.py un programme qui décide AU HASARD (graine fixe) :
    `verrouiller` vérifie qu'il ne bat pas la référence.
  - Rester déterministe : même programme + même split = mêmes cas, même ordre.
  - Le split « test » ne répond qu'avec GEVOLVE_SCELLE=1, posé par `gevolve.py scelle`.
    Avec GEVOLVE_SONDE=1, le juge écrit seulement {"sonde": nombre de cas du test}, sans
    lancer le programme : `verrouiller` vérifie ainsi que le test existe sans l'ouvrir.

Phase A :
  - Familles et segments : chaque cas peut porter "segments": {"region": "nord", "taille": "petit"}.
    gevolve s'en sert pour le diagnostic du train donné aux mutateurs (où le programme gagne et
    perd) et pour le juge généralisateur (config.json → generalisation.cles ; « mois » se déduit
    du jour). Un segment décrit le cas, il ne dépend pas de la décision.
  - Date de chaque donnée : un cas peut porter "instant" (ISO, moment de la décision) et
    "connu_a": {"source": ISO} ; verifier_instant() refuse tout cas où une source est datée
    après l'instant. Dater la publication réelle, pas l'événement (une bougie minute est datée
    de son début, et sa clôture n'est connue qu'à la fin).
  - Patrons : chaque ligne porte aussi "variables" (champs simples de l'entrée du
    programme, voir variables_du_cas) et "instant". `gevolve.py patrons` y cherche, sur le train
    seulement, où le programme gagne et perd, sans liste de variables écrite à la main.
  - Relevé témoin : le split « temoin » (GEVOLVE_TEMOIN=<fichier capturé en direct>) reconstruit,
    avec les données historiques, l'entrée des cas capturés, sans lancer le programme. Il doit
    passer par le même code que train et validation : c'est ce code qu'on vérifie.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent


def charger_cas(split):
    """À REMPLIR. Liste des cas du split, triée par date. Chaque cas est un dict :
        {"id": identifiant unique, "jour": "AAAA-MM-JJ",
         "entree": ce que le programme reçoit (JSON simple),
         "verite": ce que seul le juge voit,
         facultatif : "segments": {...}, "instant": ISO, "connu_a": {"source": ISO}}
    split « temoin » : les cas de la période du relevé témoin, construits avec les données
    historiques par le même code que les autres splits (identifiants = ceux de la capture).
    """
    raise NotImplementedError("écrire charger_cas() avant de verrouiller")


def variables_du_cas(c, prefixe="", profondeur=0):
    """Variables offertes à la recherche de patrons : les champs simples de l'ENTRÉE du programme
    (nombres, textes, booléens, dictionnaires imbriqués aplatis), jamais la vérité. Ce que le
    programme reçoit est connu à l'instant de la décision, et le relevé témoin le vérifie : on ne
    peut donc pas y glisser une donnée du futur. Les listes (séries de prix…) sont résumées par
    leur longueur et leur dernière valeur. Ajouter ici des variables dérivées de l'entrée
    seulement (écart, pente…), jamais de « verite »."""
    e = c.get("entree") if not prefixe else c
    out = {}
    if not isinstance(e, dict) or profondeur > 2:
        return out
    for k, x in e.items():
        nom = f"{prefixe}{k}"
        if isinstance(x, (str, int, float, bool)) or x is None:
            out[nom] = x
        elif isinstance(x, dict):
            out.update(variables_du_cas(x, nom + ".", profondeur + 1))
        elif isinstance(x, list):
            out[nom + ".n"] = len(x)
            if x and isinstance(x[-1], (int, float)) and not isinstance(x[-1], bool):
                out[nom + ".dernier"] = x[-1]
    return out


def verifier_instant(cas):
    """Refuse un cas dont une source est datée après l'instant de décision (fuite du futur)."""
    instant = cas.get("instant")
    for source, quand in (cas.get("connu_a") or {}).items():
        if instant is not None and str(quand) > str(instant):
            sys.exit(f"cas {cas.get('id')} : la source « {source} » est connue à {quand}, après la décision ({instant})")


def gain_et_ref(decision, cas):
    """À REMPLIR. Rendre (gain, ref) pour ce cas : gain de la décision (None si le programme
    s'abstient), ref = gain de la référence honnête sur le même cas."""
    raise NotImplementedError("écrire gain_et_ref() avant de verrouiller")


def decisions(programme, entrees):
    """Fait tourner le programme dans un processus séparé et lui passe les entrées une à une."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "PYTHONSAFEPATH": "1"}
    # 14/11 : plus de -I, qui fait ignorer ces variables (hash() des chaînes changeait d'un lancement à
    # l'autre). L'environnement ne contient qu'elles ; -s écarte le site utilisateur, PYTHONSAFEPATH et
    # executeur.py retirent le dossier du juge de sys.path.
    with tempfile.TemporaryDirectory() as vide, tempfile.TemporaryFile() as journal:
        p = subprocess.Popen([sys.executable, "-s", str(ICI / "executeur.py"), str(Path(programme).resolve())],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=journal,
                             cwd=vide, env=env, text=True, bufsize=1)
        sorties = []
        try:
            for e in entrees:
                p.stdin.write(json.dumps(e) + "\n")
                p.stdin.flush()
                ligne = p.stdout.readline()
                if not ligne:
                    break
                sorties.append(json.loads(ligne))
        except (BrokenPipeError, json.JSONDecodeError):
            pass
        finally:
            p.kill()
            p.wait()
        if len(sorties) != len(entrees):
            journal.seek(0)
            sys.stderr.write(journal.read().decode("utf-8", "replace")[-1500:])
            sys.exit(f"le programme s'est arrêté au cas {len(sorties) + 1} sur {len(entrees)}")
    return sorties


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--programme", required=True)
    ap.add_argument("--split", required=True, choices=["rapide", "train", "validation", "test", "temoin"])
    a = ap.parse_args()
    dest = os.environ.get("GEVOLVE_RESULTAT")
    if a.split == "temoin":  # relevé témoin : reconstruire les entrées capturées en direct, sans programme
        capture = os.environ.get("GEVOLVE_TEMOIN")
        if not capture:
            sys.exit("split temoin : GEVOLVE_TEMOIN absent (lancé par `gevolve.py temoin`)")
        ids = {str(json.loads(l)["id"]) for l in Path(capture).read_text(encoding="utf-8").splitlines() if l.strip()}
        cas = [c for c in charger_cas("temoin") if str(c["id"]) in ids]
        for c in cas:
            verifier_instant(c)
        if dest:
            Path(dest).write_text(json.dumps({"temoin": [{"id": str(c["id"]), "entree": c["entree"]} for c in cas]}),
                                  encoding="utf-8")
        return
    if a.split == "test" and os.environ.get("GEVOLVE_SONDE") == "1":
        if dest:  # compter sans lancer le programme : le test reste vierge
            cas = charger_cas("test")  # les jours servent à succes_test.jours_min (test à venir)
            Path(dest).write_text(json.dumps({"sonde": len(cas), "jours": len({c.get("jour") for c in cas})}),
                                  encoding="utf-8")
        return
    if a.split == "test" and os.environ.get("GEVOLVE_SCELLE") != "1":
        sys.exit("split test fermé : il ne s'ouvre que par `gevolve.py scelle`")
    cas = charger_cas(a.split)
    for c in cas:
        verifier_instant(c)
    lignes = []
    for c, d in zip(cas, decisions(a.programme, [c["entree"] for c in cas])):
        gain, ref = gain_et_ref(d, c)
        ligne = {"id": str(c["id"]), "jour": c.get("jour"), "gain": gain, "ref": ref or 0.0}
        if c.get("segments"):
            ligne["segments"] = c["segments"]  # diagnostic du train, juge généralisateur
        v = variables_du_cas(c)
        if v:
            ligne["variables"] = v  # recherche de patrons (gevolve.py patrons), train seulement
        if c.get("instant"):
            ligne["instant"] = c["instant"]
        lignes.append(ligne)
    if dest:
        Path(dest).write_text(json.dumps({"cas": lignes}), encoding="utf-8")
    agis = sum(1 for l in lignes if l["gain"] is not None)
    print(f"{a.split} : {agis} cas notés sur {len(lignes)}")  # pour l'humain ; gevolve ne lit pas ceci


if __name__ == "__main__":
    main()
