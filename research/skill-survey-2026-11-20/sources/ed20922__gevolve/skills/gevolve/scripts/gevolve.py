#!/usr/bin/env python3
"""gevolve — boucle d'évolution de programmes à la manière d'AlphaEvolve.

Tient le dossier d'une évolution : juge figé (empreintes), variantes, base chaînée des
résultats, choix des parents (élites par niche), évaluation en cascade avec marge
d'erreur, tableau, test scellé ouvert une seule fois. Bibliothèque standard uniquement.

  gevolve.py init <dossier> [--nom N] [--plafond 40] [--par-generation 4]
  gevolve.py benchmark <dossier>
  gevolve.py temoin <dossier> --capture <relevé en direct.jsonl> [--tolerance 1e-9] [--accepter "raison"]
  gevolve.py verrouiller <dossier>
  gevolve.py parents <dossier> [--k K]
  gevolve.py nouveau <dossier> --parent vXXXX[:cap] [--parent vYYYY[:cap] ...]
      cap = raffiner | famille | retour | croiser | simplifier | patron | libre (rendu par `parents`)
  gevolve.py patrons <dossier> [--variante vX] [--calibrer N]
  gevolve.py evaluer <dossier> vNNNN --idee "..." --niche "..."
  gevolve.py lecons <dossier>
  gevolve.py voir <dossier> vNNNN
  gevolve.py tableau <dossier> [--n 5]
  gevolve.py scelle <dossier> [vXXXX] [--force "raison"]
  gevolve.py piste <dossier> liste
  gevolve.py piste <dossier> ouvrir <nom> --mecanisme "..." --refute "..." [--depuis <piste>] [--depart vX]
                                           [--hors-juge "donnée qui manque"]
  gevolve.py piste <dossier> fermer <nom> --raison "..."

Pistes (14/11/2026, clé « pistes », absente des évolutions plus anciennes) : chaque hypothèse est
une piste nommée (mécanisme + chiffre qui la réfuterait). Le budget d'une génération est réparti
entre les pistes actives, chaque variante est rattachée à sa piste, une piste sans progrès est
dite épuisée et doit être fermée avec sa raison ; la boucle ne s'arrête plus à la première
stagnation, elle attend qu'on ouvre une nouvelle piste (jusqu'à pistes.max). Chaque piste ouverte
relève la barre du champion (Bonferroni sur le nombre de pistes). Même date : clés « determinisme »
(chaque variante est lancée deux fois sur « rapide »), « informations » (statut de chaque
information dans RECHERCHE.md) et « univers » figées au verrou.

Phase A, seulement pour les évolutions créées depuis (clés de config.json absentes
des plus anciennes, qui gardent leur comportement) : base complète (toute variante valide peut
servir de parent, statut « neutre »), gardée = gain sur le dernier ancêtre gardé au-delà de la
marge ET gain réparti sur les familles (juge généralisateur), CAP « simplifier », diagnostic du
train par segments donné aux mutateurs, carnet de leçons, relevé témoin et CONTEXTE.md requis
au verrou.

Recherche (09/11/2026, clés « recherche » et « voie », absentes des évolutions plus anciennes) :
RECHERCHE.md (recherche externe, inventaire de nos études, approches à mesurer, grille déclarée) et
un benchmark EXÉCUTÉ requis au verrou : `benchmark` note sur le train seulement chaque approche
connue et chaque cellule de la grille, codées dans benchmark/ ; la meilleure devient v0000. Si la
qualification conclut à la grille, voie = "grille" : aucune génération, v0000 va seul au test
scellé. `lecons` classe aussi les échecs (bruit, pire, concentré…) et mesure le rapport
signal/bruit des retouches.

Patrons (11/11/2026, clé « patrons ») : `patrons` explore seul toutes les variables connues à
l'instant de la décision (entrée du programme, instant, segments) et leurs découpages (heure,
tranche de 10 min, minute, jour de semaine, quintiles), sur le train seulement : découverte sur
un mois sur deux, barre maxT par permutation, confirmation de Holm sur les autres mois, plancher,
répartition par mois. Sortie = variable + direction, jamais de seuil ni de trade ; CAP « patron »
limité à un tiers du budget ; registre patrons.jsonl.

Contrat du juge : voir assets/evaluate.py. gevolve lance
  <interpreteur> evaluate.py --programme <fichier> --split {rapide,train,validation,test}
avec GEVOLVE_RESULTAT=<fichier.json> où le juge écrit soit {"cas": [...]} (recommandé :
gevolve calcule score, N et marge d'erreur par blocs de jours), soit {"score": x, ...}.
gevolve ne lit jamais ce que le juge ou le programme impriment.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import datetime as dt
import difflib
import fcntl
import hashlib
import io
import json
import math
import os
import random
import re
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import time
import tokenize
import uuid
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
ETAT_DIR = Path(os.environ.get("GEVOLVE_ETAT", "~/.local/share/gevolve")).expanduser()

GARDES = ("initial", "garde", "simplifiee")  # validés : candidats au titre de champion
PARENTABLES = GARDES + ("exploration", "neutre")  # peuvent servir de point de départ
CAPS = ("raffiner", "famille", "retour", "croiser", "simplifier", "patron", "libre")
REGLES = ("programme", "evaluateur", "interpreteur", "n_min", "n_min_validation", "marge_se",
          "imports_permis", "verification_statique", "succes_test", "plafond", "cible_validation", "arret_stagnation",
          # Phase A : absentes des évolutions plus anciennes, donc jamais contrôlées chez elles
          "base_complete", "generalisation", "diagnostic_n_min", "temoin", "contexte", "fin_train",
          # Recherche (09/11 au soir)
          "recherche", "voie",
          # Recherche de patrons
          "patrons",
          # 14/11 : « univers » changeait la définition du score sans être figé ; pistes, déterminisme, informations
          "univers", "determinisme", "informations", "pistes")
PISTES_DEFAUT = {"max": 6, "arret": 6}
STATUTS_INFO = ("vérifiée-juge", "vérifiée-source", "non vérifiée", "à obtenir", "abandonnée")
VOIES = ("evolution", "grille")
GENERALISATION_DEFAUT = {"cles": ["mois"], "part_min": 0.6, "n_min": 20}
# `typing` n'y est plus : typing.get_type_hints évalue une annotation écrite en chaîne,
# ce qui ouvrait open() au programme sans jamais l'écrire en clair.
IMPORTS_DEFAUT = ["math", "statistics", "itertools", "functools", "collections", "bisect", "heapq",
                  "dataclasses", "datetime", "decimal", "fractions", "re"]
# Chemins détournés vers open/eval sans les nommer, reproduits le 08/11 :
#  - cadres d'exécution : (x for x in []).gi_frame.f_builtins["open"] rend le vrai open() ;
#  - évaluation de chaînes : get_type_hints, functools.singledispatch, ForwardRef.evaluate.
DETOURS = {"gi_frame", "gi_code", "gi_yieldfrom", "cr_frame", "cr_code", "cr_await", "ag_frame", "ag_code",
           "ag_await", "f_builtins", "f_globals", "f_locals", "f_back", "f_code", "f_trace", "tb_frame",
           "tb_next", "singledispatch", "singledispatchmethod", "get_type_hints", "ForwardRef",
           "evaluate_forward_ref", "get_annotations", "evaluate"}
NOMS_INTERDITS = {"open", "eval", "exec", "compile", "__import__", "globals", "locals", "vars", "getattr",
                  "setattr", "delattr", "breakpoint", "input", "exit", "quit", "memoryview", "help",
                  "attrgetter", "methodcaller"} | DETOURS
ATTRIBUTS_INTERDITS = {"sys", "os", "modules", "system", "popen", "subprocess", "builtins", "io", "importlib",
                       "inspect", "gc", "ctypes", "open", "exec", "eval", "compile", "getattr", "setattr",
                       "pathlib", "shutil", "socket", "pickle", "marshal", "loader", "spec",
                       "attrgetter", "methodcaller"} | DETOURS
BALISE = re.compile(r"^\s*(#|//|--|;|/\*|<!--)\s*EVOLVE-BLOCK-(START|END)\b")
TIRAGES = 400  # rééchantillonnages pour la marge d'erreur
EXEMPLE_SUCCES = '{"z": 1.645, "seuil": 0.0, "battre_initial": true}'


# ---------------------------------------------------------------- utilitaires

def maintenant() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def erreur(msg: str, code: int = 2):
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(code)


def sha_texte(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha_fichier(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def f6(x) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.6g}"


def signe(x) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:+.4g}"


def ouvrir(p: str) -> Path:
    d = Path(p).expanduser().resolve()
    if not (d / "config.json").exists():
        erreur(f"{d} n'est pas un dossier gevolve (config.json absent)")
    return d


UNIV: dict | None = None  # mode « pire univers » (config.json → "univers"), sinon None


def cfg_lire(d: Path) -> dict:
    global UNIV
    c = json.loads((d / "config.json").read_text(encoding="utf-8"))
    UNIV = c.get("univers")
    return c


def cfg_ecrire(d: Path, c: dict):
    (d / "config.json").write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def nom_prog(cfg: dict) -> str:
    return Path(cfg["programme"]).name


def est_python(cfg: dict) -> bool:
    return nom_prog(cfg).endswith(".py")


def fichier_variante(d: Path, cfg: dict, vid: str) -> Path:
    return d / "variantes" / vid / nom_prog(cfg)


def lire_texte(p: Path) -> str:
    """Lecture sans conversion des fins de ligne : même octets, même empreinte."""
    return p.read_bytes().decode("utf-8")


def lister_variantes(etat: dict) -> list[str]:
    """Les variantes créées par `nouveau`, d'après l'état hors du dossier (pas d'après les dossiers)."""
    return sorted(etat.get("variantes", {}))


@contextlib.contextmanager
def verrou_fichier(d: Path):
    """Sérialise les écritures (base, état, numéros de variante) entre appels parallèles."""
    with open(d / ".gevolve.lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


# ----------------------------------------------------- état hors du dossier

def etat_chemin(cfg: dict) -> Path:
    return ETAT_DIR / f"{cfg['id']}.json"


def etat_lire(cfg: dict) -> dict:
    p = etat_chemin(cfg)
    if not p.exists():
        erreur(f"état de l'évolution introuvable ({p}) : verrou perdu ou falsifié. Ouvrir une nouvelle évolution.")
    return json.loads(p.read_text(encoding="utf-8"))


def etat_ecrire(cfg: dict, e: dict, d: Path):
    ETAT_DIR.mkdir(parents=True, exist_ok=True)
    e["dossier"] = str(d)
    tmp = etat_chemin(cfg).with_suffix(".tmp")
    tmp.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(etat_chemin(cfg))


# ------------------------------------------------------------ base chaînée

def base_lignes(d: Path) -> list[str]:
    p = d / "base.jsonl"
    return [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def controler_base(d: Path, etat: dict) -> list[dict]:
    lignes, prev, base = base_lignes(d), "", []
    for i, l in enumerate(lignes, 1):
        r = json.loads(l)
        if r.get("prev") != prev:
            erreur(f"base.jsonl modifiée hors de gevolve (ligne {i}) : commande refusée")
        prev = sha_texte(l)
        base.append(r)
    if len(lignes) != etat["base_n"] or prev != etat["base_dernier"]:
        erreur("base.jsonl ne correspond plus à l'état enregistré (ligne ajoutée, retirée ou modifiée) : commande refusée")
    return base


def base_ajouter(d: Path, cfg: dict, rec: dict):
    """À appeler sous verrou_fichier."""
    etat = etat_lire(cfg)
    controler_base(d, etat)
    rec["prev"] = etat["base_dernier"]
    ligne = json.dumps(rec, ensure_ascii=False)
    with (d / "base.jsonl").open("a", encoding="utf-8") as f:
        f.write(ligne + "\n")
    etat["base_n"] += 1
    etat["base_dernier"] = sha_texte(ligne)
    etat_ecrire(cfg, etat, d)


# ------------------------------------------------------------ juge figé

def empreintes(d: Path, cfg: dict) -> dict:
    """Empreintes complètes ; clés relatives pour ce qui est dans le dossier (survit à un déplacement)."""
    out = {}
    for rel in cfg["fichiers_figes"]:
        p = Path(rel).expanduser()
        interne = not p.is_absolute()
        if interne:
            p = d / rel
        if not p.exists():
            erreur(f"fichier figé introuvable : {rel}")
        fichiers = (sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts)
                    if p.is_dir() else [p])
        for q in fichiers:
            out[str(q.relative_to(d)) if interne else str(q)] = sha_fichier(q)
    return out


def controler(d: Path, cfg: dict, donnees: bool = True) -> tuple[dict, list[dict]]:
    if not cfg.get("verrou"):
        erreur("évolution non verrouillée : lancer `verrouiller` d'abord")
    etat = etat_lire(cfg)
    figees = etat["verrou"]["regles"]  # une évolution plus ancienne fige moins de clés
    chg = [k for k in figees if cfg.get(k) != figees.get(k)]
    if chg:
        erreur(f"règles modifiées depuis le verrou ({', '.join(chg)}) : commande refusée")
    if donnees:
        act, ref = empreintes(d, cfg), etat["verrou"]["empreintes"]
        diff = sorted(k for k in set(ref) | set(act) if ref.get(k) != act.get(k))
        if diff:
            erreur("le juge ou les données ont changé depuis le verrou (" + ", ".join(diff[:5])
                   + ") : commande refusée. Remettre les fichiers d'origine, ou ouvrir une nouvelle évolution.")
    return etat, controler_base(d, etat)


# ------------------------------------------------- blocs EVOLVE

def balises(texte: str, python: bool) -> list[tuple[int, str]]:
    """(numéro de ligne, START|END) des vraies balises ; en Python, seuls les commentaires comptent."""
    lignes = texte.splitlines()
    if python:
        try:
            res = []
            for tok in tokenize.generate_tokens(io.StringIO(texte).readline):
                if tok.type == tokenize.COMMENT:
                    m = re.match(r"#\s*EVOLVE-BLOCK-(START|END)\b", tok.string)
                    if m and lignes[tok.start[0] - 1][: tok.start[1]].strip() == "":
                        res.append((tok.start[0], m.group(1)))
            return res
        except Exception:  # fichier cassé : on retombe sur la lecture ligne à ligne
            pass
    return [(i, m.group(2)) for i, l in enumerate(lignes, 1) if (m := BALISE.match(l))]


def decouper(texte: str, python: bool) -> tuple[list[str], list[tuple[int, int]]]:
    """Segments hors zone (balises comprises) et zones modifiables (lignes de début, fin)."""
    lignes = texte.splitlines(keepends=True)
    segs, zones, debut, ouvert = [], [], 0, None
    for num, sorte in balises(texte, python):
        if sorte == "START":
            if ouvert is not None:
                raise ValueError("EVOLVE-BLOCK-START imbriqué")
            segs.append("".join(lignes[debut:num]))
            ouvert = num
        else:
            if ouvert is None:
                raise ValueError("EVOLVE-BLOCK-END sans START")
            zones.append((ouvert + 1, num - 1))
            debut, ouvert = num - 1, None
    if ouvert is not None:
        raise ValueError("EVOLVE-BLOCK non fermé")
    segs.append("".join(lignes[debut:]))
    return segs, zones


def dunder(s: str) -> bool:
    return len(s) > 4 and s.startswith("__") and s.endswith("__")


def _annotations(n) -> list:
    """Annotations portées par un nœud. Une annotation sans chaîne est contrôlée comme le reste du
    code ; une chaîne, elle, est du code que typing ou functools évaluent sans que l'AST le montre."""
    if isinstance(n, ast.arg):
        return [n.annotation]
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [n.returns]
    if isinstance(n, ast.AnnAssign):
        return [n.annotation]
    return []


def controle_statique(texte: str, zones: list[tuple[int, int]], permis: list[str]) -> list[str]:
    """Refuse dans les zones ce qui sert à sortir du programme : fichiers, processus, introspection."""
    try:
        arbre = ast.parse(texte)
    except SyntaxError:
        return []  # la cascade « rapide » rapportera l'erreur
    fautes = set()
    for n in ast.walk(arbre):
        ln = getattr(n, "lineno", None)
        if ln is None or not any(a <= ln <= b for a, b in zones):
            continue
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in permis:
                    fautes.add(f"ligne {ln} : import {a.name} non permis")
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            if n.level or mod.split(".")[0] not in permis:
                fautes.add(f"ligne {ln} : from {'.' * n.level}{mod} import non permis")
            for a in n.names:  # `from functools import singledispatch as s` échappait au contrôle des noms
                if a.name == "*" or a.name.startswith("_") or a.name in NOMS_INTERDITS | ATTRIBUTS_INTERDITS:
                    fautes.add(f"ligne {ln} : from {mod} import {a.name} interdit")
        elif type(n).__name__ == "TypeAlias" or getattr(n, "type_params", None):
            fautes.add(f"ligne {ln} : paramètres de type et « type X = … » interdits (évalués à la demande)")
        if any(a is not None and any(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in ast.walk(a))
               for a in _annotations(n)):
            fautes.add(f"ligne {ln} : annotation contenant une chaîne interdite (typing ou functools "
                       "l'évalueraient comme du code)")
        # 14/11 : `match g: case object(gi_frame=f)` lit un attribut sans nœud Attribute : le nom est
        # dans MatchClass.kwd_attrs. On le contrôle comme un attribut, et aucun nom de détour ne doit
        # apparaître dans un champ d'identifiant, quel que soit le nœud.
        if type(n).__name__ == "MatchClass":
            for nom in n.kwd_attrs:
                if nom.startswith("_") or nom in ATTRIBUTS_INTERDITS:
                    fautes.add(f"ligne {ln} : attribut .{nom} interdit (motif de classe)")
        for _champ, val in ast.iter_fields(n):
            for nom in (val if isinstance(val, list) else [val]):
                if isinstance(nom, str) and nom in DETOURS and not isinstance(n, ast.Constant):
                    fautes.add(f"ligne {ln} : {nom} interdit")
        if isinstance(n, ast.Name) and (n.id in NOMS_INTERDITS or dunder(n.id)):
            fautes.add(f"ligne {ln} : {n.id} interdit")
        elif (isinstance(n, ast.Attribute) and n.attr == "compile" and isinstance(n.value, ast.Name)
              and n.value.id == "re" and "re" in permis):
            pass  # re.compile : usage normal d'un import permis (refusé à tort jusqu'au 14/11)
        elif isinstance(n, ast.Attribute) and (n.attr.startswith("_") or n.attr in ATTRIBUTS_INTERDITS):
            fautes.add(f"ligne {ln} : attribut .{n.attr} interdit")
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and "__" in n.value:
            fautes.add(f"ligne {ln} : chaîne contenant « __ » interdite (accès détourné aux attributs internes)")
    return sorted(fautes)[:6]


# ------------------------------------------------- lancer le juge

def lire_resultat(p: Path) -> dict:
    if not p.exists():
        raise ValueError("le juge n'a pas écrit de fichier résultat (GEVOLVE_RESULTAT)")
    data = json.loads(p.read_text(encoding="utf-8"))
    if "cas" in data:
        cas, vus = [], set()
        for c in data["cas"]:
            cid = str(c["id"])
            if cid in vus:
                raise ValueError(f"identifiant de cas en double : {cid}")
            vus.add(cid)
            g = c.get("gain")
            r = c.get("ref", 0.0) or 0.0
            if g is not None and not math.isfinite(float(g)) or not math.isfinite(float(r)):
                raise ValueError(f"gain ou ref non fini pour le cas {cid}")
            x = {"id": cid, "jour": c.get("jour"), "gain": None if g is None else float(g), "ref": float(r)}
            if c.get("univers") is not None:
                x["univers"] = str(c["univers"])
            # Familles et segments (diagnostic du train, juge généralisateur) : {"region": "nord", ...}
            seg = {str(k): str(v) for k, v in (c.get("segments") or {}).items() if v is not None} \
                if isinstance(c.get("segments"), dict) else {}
            if c.get("famille") is not None:
                seg["famille"] = str(c["famille"])
            if seg:
                x["segments"] = seg
            # Recherche de patrons : variables connues à l'instant de la décision
            if isinstance(c.get("variables"), dict):
                x["variables"] = {str(k): v for k, v in c["variables"].items()
                                  if v is None or isinstance(v, (str, int, float, bool))}
            if c.get("instant"):
                x["instant"] = str(c["instant"])
            if c.get("mise") is not None:  # rendement cumulé (succes_test.rendement_min), 11/11
                x["mise"] = float(c["mise"])
            cas.append(x)
        return {"mode": "cas", "cas": cas}
    if "temoin" in data:  # relevé témoin : entrées reconstruites à partir des données historiques
        return {"mode": "temoin", "cas": [{"id": str(c["id"]), "entree": c.get("entree")} for c in data["temoin"]]}
    if "sonde" in data:
        return {"mode": "sonde", "n": int(data["sonde"]), "jours": data.get("jours")}
    if "score" in data:
        sc = float(data["score"])
        if not math.isfinite(sc):
            raise ValueError("score non fini")
        return {"mode": "score", "score": sc, "n": data.get("n"), "ref": data.get("ref"), "se": data.get("se")}
    raise ValueError("fichier résultat sans « cas » ni « score »")


def lancer(d: Path, cfg: dict, prog: Path, split: str, scelle: bool = False, sonde: bool = False,
           temoin: Path | None = None) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="gevolve-"))
    sortie = tmp / f"resultat-{uuid.uuid4().hex}.json"
    cmd = [os.path.expanduser(cfg.get("interpreteur", "python3")), str(d / cfg["evaluateur"]),
           "--programme", str(prog), "--split", split]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GEVOLVE_")}
    env.update(GEVOLVE_RESULTAT=str(sortie), PYTHONDONTWRITEBYTECODE="1")
    if scelle:
        env["GEVOLVE_SCELLE"] = "1"
    if sonde:
        env["GEVOLVE_SONDE"] = "1"  # le juge compte les cas du test sans lancer le programme
    if temoin is not None:
        env["GEVOLVE_TEMOIN"] = str(temoin)  # le juge reconstruit les entrées des cas capturés, sans programme
    t0 = time.time()
    try:
        # groupe de processus à part : au délai dépassé, on tue aussi l'exécuteur lancé par le juge
        p = subprocess.Popen(cmd, cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             env=env, start_new_session=True)
        try:
            out, err = p.communicate(timeout=cfg.get("timeout_s", 600))
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(p.pid, signal.SIGKILL)
            p.communicate()
            raise
        duree = round(time.time() - t0, 1)
        if p.returncode != 0:
            queue = (err or out or "").strip().splitlines()[-6:]
            return {"ok": False, "duree_s": duree, "erreur": (f"code {p.returncode} : " + " | ".join(queue))[-900:]}
        res = lire_resultat(sortie)
        res.update(ok=True, duree_s=duree)
        return res
    except subprocess.TimeoutExpired:
        return {"ok": False, "erreur": f"délai dépassé ({cfg.get('timeout_s', 600)} s)"}
    except OSError as e:
        return {"ok": False, "erreur": f"interpréteur introuvable ou inexécutable : {e}"}
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        return {"ok": False, "erreur": f"résultat du juge invalide : {e}"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- statistique

def _jours_univers(cas: list[dict]) -> dict:
    """{jour: {univers: [somme, n]}} sur les cas où le programme agit."""
    g: dict = {}
    for c in cas:
        k = c["jour"] or "#" + c["id"]
        u = g.setdefault(k, {})
        s = u.setdefault(c.get("univers", "?"), [0.0, 0])
        if c["gain"] is not None:
            s[0] += c["gain"] - c["ref"]
            s[1] += 1
    return g


def score_univers(jours: list[dict], detail: bool = False):
    """Score « pire univers » : pour chaque univers listé, moyenne par trade + λ·CVaR_α des moyennes
    journalières (CVaR négative = pénalité). Univers avec moins de n_min_univers trades : 0 (s'abstenir
    = la référence), ce qui plafonne le score à 0 tant qu'on ne trade pas partout."""
    lam, alpha, nmin = float(UNIV.get("lambda_cvar", 0.0)), float(UNIV.get("alpha", 0.05)), int(UNIV.get("n_min_univers", 1))
    bloc = UNIV.get("bloc_cvar", "semaine")
    par: dict = {}
    for cle, j in jours:
        b = cle
        if bloc == "semaine":
            try:
                b = "%d-%02d" % dt.date.fromisoformat(cle).isocalendar()[:2]
            except (ValueError, TypeError):
                pass
        for u, (sm, n) in j.items():
            p = par.setdefault(u, [0.0, 0, {}])
            p[0] += sm; p[1] += n
            if n:
                q = p[2].setdefault(b, [0.0, 0])
                q[0] += sm; q[1] += n
    res = {}
    for u in UNIV.get("liste") or sorted(par):
        sm, n, blocs = par.get(u, [0.0, 0, {}])
        dj = [a / m for a, m in blocs.values()]
        if n < nmin or not dj:
            res[u] = {"n": n, "moy": (sm / n if n else None), "cvar": None, "score": 0.0}
            continue
        dj = sorted(dj)
        k = max(1, int(math.ceil(alpha * len(dj))))
        cvar = sum(dj[:k]) / k
        res[u] = {"n": n, "moy": sm / n, "cvar": cvar, "score": sm / n + lam * min(0.0, cvar)}
    sc = min(r["score"] for r in res.values()) if res else float("nan")
    return (sc, res) if detail else sc


def agreger(cas: list[dict]) -> dict | None:
    """Score = moyenne de (gain − ref) sur les cas où le programme a agi
    (mode univers : pire univers − pénalité CVaR, voir score_univers)."""
    if UNIV is not None:
        n = sum(1 for c in cas if c["gain"] is not None)
        if not n:
            return None
        sc, det = score_univers(list(_jours_univers(cas).items()), detail=True)
        return {"score": sc, "n": n, "ref": 0.0, "univers": det}
    vals = [c["gain"] - c["ref"] for c in cas if c["gain"] is not None]
    if not vals:
        return None
    return {"score": sum(vals) / len(vals), "n": len(vals),
            "ref": sum(c["ref"] for c in cas if c["gain"] is not None) / len(vals)}


def _groupes(cas: list[dict]) -> dict:
    g: dict[str, list] = {}
    for c in cas:
        s = g.setdefault(c["jour"] or "#" + c["id"], [0.0, 0])
        if c["gain"] is not None:
            s[0] += c["gain"] - c["ref"]
            s[1] += 1
    return g


def erreur_type(cas: list[dict], cas_ref: list[dict] | None, graine: str) -> float:
    """Marge d'erreur (écart-type bootstrap par blocs de jours) du score, ou de score − score_ref
    quand cas_ref est donné : les deux programmes sont alors rééchantillonnés sur les mêmes jours."""
    if cas_ref is not None and {c["id"] for c in cas} != {c["id"] for c in cas_ref}:
        raise ValueError("comparaison sur des cas différents (split ou juge changé ?)")
    if UNIV is not None:
        ja, jb = _jours_univers(cas), (_jours_univers(cas_ref) if cas_ref is not None else None)
        cles = sorted(ja)
        if len(cles) < 2:
            return float("nan")
        rng = random.Random(graine)
        tirages = []
        for _ in range(TIRAGES):
            ks = [cles[rng.randrange(len(cles))] for _k in range(len(cles))]
            a = score_univers([(k, ja[k]) for k in ks])
            b = score_univers([(k, jb[k]) for k in ks]) if jb is not None else 0.0
            tirages.append(a - b)
        return statistics.stdev(tirages)
    ga = _groupes(cas)
    gb = _groupes(cas_ref) if cas_ref is not None else None
    cles = sorted(ga)
    if len(cles) < 2:
        return float("nan")
    rng = random.Random(graine)
    tirages = []
    for _ in range(TIRAGES):
        sa = na = sb = nb = 0
        for _k in range(len(cles)):
            k = cles[rng.randrange(len(cles))]
            sa += ga[k][0]; na += ga[k][1]
            if gb is not None:
                sb += gb[k][0]; nb += gb[k][1]
        if na == 0 or (gb is not None and nb == 0):
            continue
        tirages.append(sa / na - (sb / nb if gb is not None else 0.0))
    return statistics.stdev(tirages) if len(tirages) >= 2 else float("nan")


def stats_par_univers(cas: list[dict], graine: str) -> dict:
    """Pour le verdict du test : {univers: (moyenne par trade, marge bootstrap par jours, N, jours)}."""
    out = {}
    for u in sorted({c.get("univers", "?") for c in cas}):
        g = _groupes([c for c in cas if c.get("univers", "?") == u])
        g = {k: v for k, v in g.items() if v[1]}
        n = sum(v[1] for v in g.values())
        if not n:
            out[u] = (None, float("nan"), 0, 0)
            continue
        cles = sorted(g)
        rng = random.Random(graine + u)
        t = []
        for _ in range(TIRAGES):
            sa = na = 0
            for _k in range(len(cles)):
                k = cles[rng.randrange(len(cles))]
                sa += g[k][0]; na += g[k][1]
            if na:
                t.append(sa / na)
        out[u] = (sum(v[0] for v in g.values()) / n, statistics.stdev(t) if len(t) >= 2 and len(cles) >= 2 else float("nan"), n, len(cles))
    return out


def ecart_apparie(cas: list[dict], cas_ref: list[dict], graine: str) -> tuple[float | None, float]:
    a, b = agreger(cas), agreger(cas_ref)
    if a is None or b is None:
        return None, float("nan")
    return a["score"] - b["score"], erreur_type(cas, cas_ref, graine)


def valeur_segment(c: dict, cle: str) -> str | None:
    """Famille d'un cas pour une clé : « mois » se déduit du jour, le reste vient du juge (segments)."""
    if cle == "mois":
        j = c.get("jour") or ""
        return j[:7] if re.match(r"\d{4}-\d{2}", j) else None
    return (c.get("segments") or {}).get(cle)


def rendement_cumule(cas: list[dict]) -> float | None:
    """Σ (gain − ref) ÷ Σ mise sur les cas où le programme agit ; None si le juge n'écrit pas de mise."""
    ag = [c for c in cas if c["gain"] is not None]
    if not ag or any(c.get("mise") is None for c in ag):
        return None
    m = sum(c["mise"] for c in ag)
    return sum(c["gain"] - c["ref"] for c in ag) / m if m > 0 else None


def moyenne_simple(cas: list[dict]) -> tuple[float, int] | None:
    """Moyenne de (gain − ref) sur les cas où le programme agit, sans le mode « pire univers »."""
    vals = [c["gain"] - c["ref"] for c in cas if c["gain"] is not None]
    return (sum(vals) / len(vals), len(vals)) if vals else None


def generalisation(cas: list[dict], cas_ref: list[dict], g: dict | None) -> dict | None:
    """Juge généralisateur (mode de Tao et al. : noter sur une famille d'instances, pas une seule).
    Pour chaque clé (mois, actif…), on compare la variante à sa référence famille par famille.
    Une famille compte si les décisions y diffèrent et si les deux programmes y agissent au moins
    n_min fois ; le gain doit être positif dans au moins part_min de ces familles. Moins de deux
    familles qui comptent : la clé ne dit rien (non applicable). Un filtre qui retire une famille
    entière ne se juge donc pas sur cette clé, mais sur les autres (les mois, par défaut).
    Pour les mois, une règle sélective est jugée sur des blocs de mois consécutifs d'au moins n_min
    trades ; « confiné » seulement si plus de la moitié de ses trades tombent dans un seul mois."""
    if not g:
        return None
    nmin, part = int(g.get("n_min", 20)), float(g.get("part_min", 0.6))
    ref = {c["id"]: c for c in cas_ref}
    res, ok = {}, True
    for cle in g.get("cles") or ["mois"]:
        fam: dict[str, tuple[list, list]] = {}
        for c in cas:
            v, r = valeur_segment(c, cle), ref.get(c["id"])
            if v is None or r is None:
                continue
            a, b = fam.setdefault(v, ([], []))
            a.append(c)
            b.append(r)
        pos = tot = assez = 0
        for v, (a, b) in fam.items():
            mb = moyenne_simple(b)
            assez += mb is not None and mb[1] >= nmin
            if all(x["gain"] == y["gain"] and x["ref"] == y["ref"] for x, y in zip(a, b)):
                continue  # mêmes décisions dans cette famille : elle ne dit rien
            ma = moyenne_simple(a)
            if ma is None or mb is None or min(ma[1], mb[1]) < nmin:
                continue
            tot += 1
            pos += ma[0] > mb[0]
        confine = False
        if tot < 2 and cle == "mois":
            # Règle sélective (peu de trades par mois) : on regroupe les mois consécutifs en blocs
            # d'au moins n_min trades de chaque côté, puis on juge les blocs. Sans ce regroupement,
            # une règle à 3 trades par mois gagnante partout était déclarée « confinée » (repro du 09/11).
            blocs, a_cur, b_cur = [], [], []
            for v in sorted(fam):
                a_cur += fam[v][0]
                b_cur += fam[v][1]
                ma, mb = moyenne_simple(a_cur), moyenne_simple(b_cur)
                if ma and mb and min(ma[1], mb[1]) >= nmin:
                    blocs.append((a_cur, b_cur))
                    a_cur, b_cur = [], []
            if blocs and (a_cur or b_cur):  # reste trop petit : rattaché au dernier bloc
                blocs[-1] = (blocs[-1][0] + a_cur, blocs[-1][1] + b_cur)
            pos = tot = 0
            for a, b in blocs:
                if all(x["gain"] == y["gain"] and x["ref"] == y["ref"] for x, y in zip(a, b)):
                    continue
                ma, mb = moyenne_simple(a), moyenne_simple(b)
                tot += 1
                pos += ma[0] > mb[0]
        if tot >= 2:
            bon = pos / tot >= part
        elif cle == "mois" and assez >= 2:
            # Le temps est la seule famille qu'une règle honnête ne peut pas viser. Même regroupés en
            # blocs, moins de deux blocs comparables : on ne refuse que si les trades de la variante sont
            # vraiment concentrés (plus de la moitié dans un seul mois) ; sinon la clé ne dit rien.
            par_mois = [sum(1 for c in a if c["gain"] is not None) for a, _ in fam.values()]
            total = sum(par_mois)
            confine = total > 0 and max(par_mois) > total / 2
            bon = not confine
        else:
            bon = True  # un seul actif touché (ex. « sans la région nord ») : jugé sur les autres clés
        res[cle] = {"positives": pos, "familles": tot, "ok": bon, "confine": confine}
        ok = ok and bon
    return {"ok": ok, "cles": res}


def texte_generalisation(g: dict | None) -> str:
    if not g:
        return ""
    return ", ".join(f"{k} {v['positives']}/{v['familles']}"
                     + (" (confiné à une période)" if v.get("confine") else "" if v["familles"] >= 2 else " (n/a)")
                     for k, v in g["cles"].items())


# ------------------------------------------------- recherche : benchmark exécuté

def sha_cas(cas: list[dict]) -> str:
    """Empreinte des décisions d'un programme sur un split : deux programmes de même empreinte agissent pareil."""
    return sha_texte(json.dumps(cas, sort_keys=True, ensure_ascii=False))


def repartition(cas: list[dict], cfg: dict) -> dict:
    """{clé: [familles en gain, familles avec assez de cas]} contre « ne rien faire » (gain − ref > 0)."""
    g = cfg.get("generalisation") or GENERALISATION_DEFAUT
    nmin, out = int(g.get("n_min", 20)), {}
    for cle in g.get("cles") or ["mois"]:
        fam: dict[str, list] = {}
        for c in cas:
            v = valeur_segment(c, cle) if c["gain"] is not None else None
            if v is None:
                continue
            s = fam.setdefault(v, [0.0, 0])
            s[0] += c["gain"] - c["ref"]
            s[1] += 1
        assez = [s for s in fam.values() if s[1] >= nmin]
        out[cle] = [sum(1 for s in assez if s[0] > 0), len(assez)]
    return out


def texte_repartition(r: dict | None) -> str:
    return " · ".join(f"{k} {p}/{t}" for k, (p, t) in (r or {}).items())


def empreinte_juge(d: Path, cfg: dict) -> str:
    """Le juge et ses données, sans les textes de cadrage (.md) qui changent encore après le benchmark."""
    rels = [r for r in dict.fromkeys([cfg["evaluateur"], "executeur.py", *cfg.get("fichiers_figes", [])])
            if not str(r).endswith(".md") and Path(r).parts[:1] != ("benchmark",)]
    tmp = dict(cfg, fichiers_figes=[r for r in rels if (Path(r).expanduser() if Path(r).expanduser().is_absolute()
                                                         else d / r).exists()])
    return sha_texte(json.dumps(empreintes(d, tmp), sort_keys=True))


def programmes_benchmark(d: Path, cfg: dict) -> list[Path]:
    b = d / "benchmark"
    suffixe = Path(nom_prog(cfg)).suffix
    return sorted(p for p in b.glob(f"*{suffixe}") if p.is_file()) if b.is_dir() else []


def biais_selection(k: int) -> float:
    """Espérance du maximum de k tirages normaux centrés réduits (approximation de Blom). Sert à dire de
    combien la meilleure de k cellules d'une grille est gonflée par le seul hasard (cellules corrélées :
    c'est un plafond)."""
    if k < 2:
        return 0.0
    return statistics.NormalDist().inv_cdf((k - 0.375) / (k + 0.25))


def diagnostic(cas: list[dict], nmin: int, maxv: int = 8) -> list[str]:
    """Où le programme gagne et perd sur le TRAIN, par segment (mois + segments du juge). Seuls les
    segments d'au moins nmin trades, avec leur marge (par cas, approximative) : jamais de trade
    individuel, sinon le mutateur écrirait une règle qui exclut exactement les pertes du train."""
    cles = ["mois"] + sorted({k for c in cas for k in (c.get("segments") or {})})
    lignes = []
    for cle in cles:
        g: dict[str, list[float]] = {}
        for c in cas:
            v = valeur_segment(c, cle)
            if c["gain"] is not None and v is not None:
                g.setdefault(v, []).append(c["gain"] - c["ref"])
        items = sorted(((v, xs) for v, xs in g.items() if len(xs) >= nmin), key=lambda t: statistics.fmean(t[1]))
        if len(items) < 2:
            continue
        if len(items) > maxv:
            items = items[: maxv // 2] + items[-(maxv // 2):]
        lignes.append(f"{cle} : " + " · ".join(
            f"{v} {statistics.fmean(xs):+.3g} ±{statistics.stdev(xs) / math.sqrt(len(xs)):.2g} (N {len(xs)})"
            for v, xs in items))
    return lignes


# ------------------------------------------------- recherche de patrons
#
# Le diagnostic ne regarde que des segments choisis d'avance. `patrons` explore seul toutes les
# variables du cas connues à l'instant de la décision (entrée du programme + instant), en dérive
# les découpages (heure, tranche de 10 min, minute, jour de semaine, quintiles…), et cherche où le
# P&L du programme est nettement plus bas (filtre à essayer) ou plus haut (condition à essayer).
# Protections, d'après la revue GPT-6.1 / Opus 5.5 / DeepSeek V4 / GLM 5.3 du 11/11 :
#  - découverte sur un mois sur deux du train, confirmation sur les autres (jamais au hasard) ;
#  - barre de découverte = permutation maxT (P&L mélangés à l'intérieur de chaque mois, toute la
#    recherche relancée) : elle compte d'office tous les découpages essayés ;
#  - confirmation : Holm sur les candidats, alpha divisé par le nombre d'analyses déjà faites ;
#  - plancher économique, effet réparti sur les mois, aucune concentration sur un mois ;
#  - cible = P&L par trade avec et sans la case, pas le taux de pertes ;
#  - sortie = variable + direction, jamais un seuil ni un trade ; registre des pistes (patrons.jsonl).

PATRONS_DEFAUT = {"n_min_total": 300, "n_min_case": 30, "permutations": 300, "candidats_max": 5,
                  "plancher": None, "alpha": 0.05, "part_mois": 0.6, "concentration_max": 0.5,
                  "part_budget_max": 1 / 3, "niveaux_max": 24}
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    return None


def variables_brutes(c: dict) -> dict:
    """Variables d'un cas : « variables » écrites par le juge (dérivées de l'entrée du programme,
    donc connues à l'instant de la décision), « instant », segments, et le jour."""
    v = dict(c.get("variables") or {})
    if c.get("instant"):
        v.setdefault("instant", c["instant"])
    for k, x in (c.get("segments") or {}).items():
        v.setdefault("segment." + k, x)
    if c.get("jour"):
        v.setdefault("jour", c["jour"])
    return v


def deriver(cas: list[dict], niveaux_max: int) -> dict:
    """{nom de variable dérivée: (type, {id du cas: valeur})}. type « ordre » (valeurs ordonnées,
    découpées en quintiles ou en bins naturels) ou « niveau » (catégories). Les découpages ne
    dépendent jamais du P&L : ils sont fixés par les seules valeurs des variables."""
    brutes: dict[str, dict] = {}
    for c in cas:
        for k, x in variables_brutes(c).items():
            brutes.setdefault(k, {})[c["id"]] = x
    out: dict[str, tuple[str, dict]] = {}
    for k, vals in brutes.items():
        xs = [x for x in vals.values() if x is not None]
        if not xs:
            continue
        if all(isinstance(x, str) and _ISO.match(x) for x in xs):
            temps = {}
            for i, x in vals.items():
                try:
                    temps[i] = dt.datetime.fromisoformat(x.replace("Z", "+00:00"))
                except (ValueError, TypeError, AttributeError):
                    pass
            out[f"{k}:heure"] = ("cycle", {i: t.hour for i, t in temps.items()})
            out[f"{k}:tranche_10min"] = ("cycle", {i: t.hour * 6 + t.minute // 10 for i, t in temps.items()})
            out[f"{k}:minute"] = ("cycle", {i: t.minute for i, t in temps.items()})
            out[f"{k}:minute_dans_10"] = ("cycle", {i: t.minute % 10 for i, t in temps.items()})
            out[f"{k}:jour_semaine"] = ("niveau", {i: "lun mar mer jeu ven sam dim".split()[t.weekday()] for i, t in temps.items()})
            continue
        if k == "jour" or all(isinstance(x, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", x) for x in xs):
            js = {}
            for i, x in vals.items():
                try:
                    js[i] = dt.date.fromisoformat(x)
                except (ValueError, TypeError):
                    pass
            out[f"{k}:jour_semaine"] = ("niveau", {i: "lun mar mer jeu ven sam dim".split()[j.weekday()] for i, j in js.items()})
            continue
        nums = {i: _num(x) for i, x in vals.items()}
        if sum(x is not None for x in nums.values()) >= 0.9 * len(xs):
            nums = {i: x for i, x in nums.items() if x is not None}
            if len(set(nums.values())) <= 1:
                continue
            out[k] = ("ordre", nums)
            continue
        cats = {i: str(x) for i, x in vals.items() if x is not None}
        if 2 <= len(set(cats.values())) <= niveaux_max:
            out[k] = ("niveau", cats)
    return out


def cases(derivees: dict, ids_trade: list[str]) -> list[tuple[str, str, frozenset]]:
    """Toutes les cases testées : (variable, libellé lisible, ensemble d'ids). Ordre : quintiles,
    plus les deux queues (2 quintiles bas, 2 hauts). Cycle (heure, minute…) : chaque valeur et des
    fenêtres de 3 valeurs voisines. Niveau : chaque catégorie. Le libellé donne une direction,
    jamais un seuil chiffré : c'est le mutateur qui choisit le seuil, le juge qui tranche."""
    ens = set(ids_trade)
    out = []
    for var, (typ, vals) in derivees.items():
        v = {i: x for i, x in vals.items() if i in ens}
        if len(v) < 2:
            continue
        if typ == "ordre":
            tri = sorted(v.values())
            bornes = [tri[int(len(tri) * q / 5)] for q in range(1, 5)]
            def qn(x):
                return sum(x > b for b in bornes)
            qs = {i: qn(x) for i, x in v.items()}
            noms = ["très bas", "bas", "moyen", "haut", "très haut"]
            for q in range(5):
                out.append((var, f"{var} {noms[q]} (quintile {q + 1}/5)", frozenset(i for i, x in qs.items() if x == q)))
            out.append((var, f"{var} bas (2 quintiles du bas)", frozenset(i for i, x in qs.items() if x <= 1)))
            out.append((var, f"{var} haut (2 quintiles du haut)", frozenset(i for i, x in qs.items() if x >= 3)))
        elif typ == "cycle":
            niveaux = sorted(set(v.values()))
            for n in niveaux:
                out.append((var, f"{var} = {n}", frozenset(i for i, x in v.items() if x == n)))
            if len(niveaux) >= 6:
                for n in niveaux:
                    fen = {n - 1, n, n + 1}
                    out.append((var, f"{var} autour de {n}", frozenset(i for i, x in v.items() if x in fen)))
        else:
            for n in sorted(set(v.values())):
                out.append((var, f"{var} = {n}", frozenset(i for i, x in v.items() if x == n)))
    vus, uniq = set(), []
    for var, lib, s in out:  # deux découpages identiques ne comptent qu'une fois
        if s not in vus:
            vus.add(s)
            uniq.append((var, lib, s))
    return uniq


def _stat_case(pnl: dict, jour: dict, s: frozenset, nmin: int) -> tuple[float, float, int] | None:
    """Écart de P&L moyen par trade dans la case contre hors de la case, et son t avec une marge
    regroupée par jour (plusieurs trades d'un même jour ne sont pas indépendants)."""
    dedans = [i for i in pnl if i in s]
    dehors = [i for i in pnl if i not in s]
    if len(dedans) < nmin or len(dehors) < nmin:
        return None
    ma = statistics.fmean(pnl[i] for i in dedans)
    mb = statistics.fmean(pnl[i] for i in dehors)

    def var_moy(ids, m):
        g: dict = {}
        for i in ids:
            g[jour[i]] = g.get(jour[i], 0.0) + (pnl[i] - m)
        n = len(ids)
        k = len(g)
        if k < 2:
            return float("inf")
        return sum(x * x for x in g.values()) / (n * n) * k / (k - 1)
    se = math.sqrt(var_moy(dedans, ma) + var_moy(dehors, mb))
    if not se or not math.isfinite(se):
        return None
    return ma - mb, (ma - mb) / se, len(dedans)


def _melanger(pnl: dict, mois: dict, rng: random.Random) -> dict:
    """P&L permutés à l'intérieur de chaque mois : garde l'effet mois, casse tout lien avec les variables."""
    par: dict = {}
    for i in pnl:
        par.setdefault(mois[i], []).append(i)
    out = {}
    for ids in par.values():
        vals = [pnl[i] for i in ids]
        rng.shuffle(vals)
        out.update(zip(ids, vals))
    return out


def _max_t(pnl, jour, cs, nmin) -> float:
    m = 0.0
    for _, _, s in cs:
        r = _stat_case(pnl, jour, s, nmin)
        if r and abs(r[1]) > m:
            m = abs(r[1])
    return m


def _z_holm(alpha: float, k: int, rang: int) -> float:
    """z bilatéral de Holm pour le candidat de rang `rang` (0 = le plus fort) parmi k."""
    a = alpha / max(1, k - rang)
    return statistics.NormalDist().inv_cdf(1 - a / 2)


def chercher_patrons(cas: list[dict], p: dict, n_analyses_avant: int, graine: str) -> dict:
    """Recherche complète, train seulement. Rend {"etat", "n", "n_cases", "barre", "candidats": [...]}.
    Chaque candidat : variable, libellé, sens, effet découverte et confirmation, statut :
      patron     : confirmé sur les mois non vus, au-dessus du plancher, réparti sur les mois ;
      exception  : confirmé mais porté par un seul mois, ou instable d'un mois à l'autre ;
      bruit      : significatif en découverte, pas en confirmation (ou sous le plancher)."""
    trades = [c for c in cas if c["gain"] is not None]
    pnl = {c["id"]: c["gain"] - c["ref"] for c in trades}
    jour = {c["id"]: c.get("jour") or "#" + c["id"] for c in trades}
    mois = {i: (j[:7] if re.match(r"\d{4}-\d{2}", j) else j) for i, j in jour.items()}
    res = {"n": len(trades), "candidats": []}
    if len(trades) < p["n_min_total"]:
        res["etat"] = f"éteint : {len(trades)} trades sur le train, sous le minimum de {p['n_min_total']}"
        return res
    liste_mois = sorted(set(mois.values()))
    if len(liste_mois) < 4:
        res["etat"] = f"éteint : {len(liste_mois)} mois sur le train, il en faut au moins 4 (2 de découverte, 2 de confirmation)"
        return res
    dec_mois = set(liste_mois[0::2])
    der = deriver(cas, int(p["niveaux_max"]))
    cs = cases(der, list(pnl))
    res["n_variables"], res["n_cases"] = len(der), len(cs)
    pd = {i: x for i, x in pnl.items() if mois[i] in dec_mois}
    pc = {i: x for i, x in pnl.items() if mois[i] not in dec_mois}
    nmin = int(p["n_min_case"])
    rng = random.Random(graine)
    maxs = sorted(_max_t(_melanger(pd, mois, rng), jour, cs, nmin) for _ in range(int(p["permutations"])))
    barre = maxs[min(len(maxs) - 1, int(math.ceil(0.95 * len(maxs))) - 1)] if maxs else float("inf")
    res["barre"] = barre
    trouves = []
    for var, lib, s in cs:
        r = _stat_case(pd, jour, s, nmin)
        if r and abs(r[1]) > barre:
            trouves.append((abs(r[1]), var, lib, s, r))
    trouves.sort(key=lambda t: -t[0])
    # une variable ne propose qu'une case (la plus forte) : 5 quintiles voisins ne font pas 5 idées
    un_par_var, vus = [], set()
    for t in trouves:
        if t[1] not in vus:
            vus.add(t[1])
            un_par_var.append(t)
    res["n_decouverte"] = len(trouves)
    cands = un_par_var[: int(p["candidats_max"])]
    alpha = float(p["alpha"]) / (1 + n_analyses_avant)  # le budget d'erreur est partagé entre analyses
    plancher = p.get("plancher")
    moy_tout = statistics.fmean(pnl.values())
    for rang, (_, var, lib, s, rd) in enumerate(cands):
        rc = _stat_case(pc, jour, s, nmin)
        sens = "plus bas" if rd[0] < 0 else "plus haut"
        cand = {"variable": var, "case": lib, "sens": sens, "effet_decouverte": rd[0], "t_decouverte": rd[1],
                "n_decouverte": rd[2]}
        # ce que changerait la règle sur tout le train : exclure la case (si P&L plus bas) ou s'y limiter
        ids_garde = [i for i in pnl if (i not in s) == (rd[0] < 0)]
        if ids_garde:
            cand["gain_par_trade"] = statistics.fmean(pnl[i] for i in ids_garde) - moy_tout
            cand["part_trades_gardes"] = len(ids_garde) / len(pnl)
        # répartition sur les mois de tout le train
        par_mois: dict = {}
        for i in pnl:
            if i in s:
                par_mois.setdefault(mois[i], []).append(pnl[i])
        m_hors = {m: statistics.fmean([pnl[i] for i in pnl if mois[i] == m and i not in s] or [0.0]) for m in par_mois}
        ecarts = {m: statistics.fmean(xs) - m_hors[m] for m, xs in par_mois.items() if len(xs) >= 10}
        bons = sum(1 for e in ecarts.values() if (e < 0) == (rd[0] < 0))
        cand["mois_dans_le_sens"] = f"{bons}/{len(ecarts)}"
        contrib = {m: sum(xs) - len(xs) * m_hors[m] for m, xs in par_mois.items()}
        tot = sum(contrib.values())
        cand["part_mois_principal"] = max((c / tot for c in contrib.values()), default=0.0) if tot and (tot < 0) == (rd[0] < 0) else 1.0
        if rc is None:
            cand["statut"], cand["raison"] = "bruit", f"moins de {nmin} trades dans la case sur les mois de confirmation"
        else:
            cand["effet_confirmation"], cand["t_confirmation"], cand["n_confirmation"] = rc
            zb = _z_holm(alpha, len(cands), rang)
            if (rc[0] < 0) != (rd[0] < 0) or abs(rc[1]) < zb:
                cand["statut"], cand["raison"] = "bruit", f"ne se confirme pas sur les mois non vus (t {rc[1]:+.2f}, barre {zb:.2f})"
            elif plancher is not None and cand.get("gain_par_trade", 0.0) < float(plancher):
                cand["statut"], cand["raison"] = "bruit", f"confirmé mais sous le plancher ({cand.get('gain_par_trade', 0):+.3g} < {plancher} par trade)"
            elif cand["part_mois_principal"] > float(p["concentration_max"]):
                cand["statut"], cand["raison"] = "exception", f"{cand['part_mois_principal']:.0%} de l'effet vient d'un seul mois"
            elif ecarts and bons / len(ecarts) < float(p["part_mois"]):
                cand["statut"], cand["raison"] = "exception", f"dans le bon sens sur {bons}/{len(ecarts)} mois seulement"
            else:
                cand["statut"] = "patron"
        res["candidats"].append(cand)
    res["etat"] = "fait"
    return res


def calibrer_patrons(cas: list[dict], p: dict, tours: int, graine: str) -> dict:
    """Taux de fausses alertes : la recherche complète sur des P&L mélangés dans chaque mois doit
    sortir zéro patron dans au moins 95 % des tours. Puis un patron injecté doit être retrouvé."""
    rng = random.Random(graine)
    trades = [c for c in cas if c["gain"] is not None]
    mois = {c["id"]: (c.get("jour") or "#")[:7] for c in trades}
    pnl = {c["id"]: c["gain"] - c["ref"] for c in trades}
    p2 = dict(p, permutations=min(int(p["permutations"]), 100))
    alertes = 0
    for t in range(tours):
        mel = _melanger(pnl, mois, rng)
        faux = [dict(c, gain=c["ref"] + mel[c["id"]]) if c["id"] in mel else c for c in cas]
        r = chercher_patrons(faux, p2, 0, f"{graine}-cal{t}")
        if any(x["statut"] == "patron" for x in r["candidats"]):
            alertes += 1
    # patron injecté : sur des P&L mélangés, une variable artificielle pénalise un tiers des trades
    mel = _melanger(pnl, mois, rng)
    sd = statistics.pstdev(pnl.values()) or 1.0
    ids = sorted(pnl)
    marque = set(rng.sample(ids, len(ids) // 3))
    inj = []
    for c in cas:
        if c["id"] in mel:
            c = dict(c, gain=c["ref"] + mel[c["id"]] - (0.5 * sd if c["id"] in marque else 0.0))
            c["variables"] = dict(c.get("variables") or {}, _injecte=("A" if c["id"] in marque else "B"))
        inj.append(c)
    r = chercher_patrons(inj, p2, 0, f"{graine}-inj")
    retrouve = any(x["statut"] == "patron" and x["variable"] == "_injecte" for x in r["candidats"])
    return {"tours": tours, "fausses_alertes": alertes, "taux": alertes / tours if tours else float("nan"),
            "injecte_retrouve": retrouve}


def texte_patron(c: dict) -> str:
    """Hypothèse transmise au mutateur : variable et direction, jamais de seuil chiffré ni de trade."""
    if c["sens"] == "plus bas":
        return f"P&L plus bas quand {c['case']} → hypothèse : tester un filtre qui évite ce cas"
    return f"P&L plus haut quand {c['case']} → hypothèse : tester une condition qui privilégie ce cas"


def complexite(texte: str, zones: list[tuple[int, int]]) -> int | None:
    """Taille d'une règle dans les blocs EVOLVE : comparaisons, conditions et constantes numériques.
    Sert au CAP « simplifier » : une simplification doit faire baisser ce compte."""
    try:
        arbre = ast.parse(texte)
    except SyntaxError:
        return None
    n = 0
    for x in ast.walk(arbre):
        ln = getattr(x, "lineno", None)
        if ln is None or not any(a <= ln <= b for a, b in zones):
            continue
        if isinstance(x, ast.Compare):
            n += len(x.ops)
        elif isinstance(x, (ast.If, ast.IfExp)):
            n += 1
        elif isinstance(x, ast.BoolOp):
            n += len(x.values) - 1
        elif isinstance(x, ast.Constant) and isinstance(x.value, (int, float)) and not isinstance(x.value, bool):
            n += 1
    return n


def reference_garde(rec: dict, connus: dict) -> dict:
    """Le dernier ancêtre gardé (ou v0000) : c'est contre lui qu'une variante doit faire ses preuves.
    Une lignée de retouches « neutres » qui s'additionnent finit ainsi par être jugée sur son total."""
    while rec["statut"] not in GARDES and rec.get("parent") in connus:
        rec = connus[rec["parent"]]
    return rec


def resultats_ecrire(d: Path, vid: str, split: str, cas: list[dict]) -> str:
    (d / "resultats").mkdir(exist_ok=True)
    p = d / "resultats" / f"{vid}_{split}.json"
    p.write_text(json.dumps(cas, ensure_ascii=False), encoding="utf-8")
    return sha_fichier(p)


def resultats_lire(d: Path, rec: dict, split: str) -> list[dict]:
    p = d / "resultats" / f"{rec['id']}_{split}.json"
    if not p.exists() or sha_fichier(p) != rec.get("sha_res", {}).get(split):
        erreur(f"résultats de {rec['id']} ({split}) absents ou modifiés : commande refusée")
    return json.loads(p.read_text(encoding="utf-8"))


def verifier_programme(d: Path, cfg: dict, rec: dict):
    p = fichier_variante(d, cfg, rec["id"])
    if not p.exists() or sha_fichier(p) != rec.get("sha_prog"):
        erreur(f"le programme de {rec['id']} a été modifié après sa notation : commande refusée")


# ------------------------------------------------- résumé / champion

# ------------------------------------------------- pistes (hypothèses), 14/11/2026

def pistes_on(cfg: dict) -> bool:
    return bool(cfg.get("pistes"))


def params_pistes(cfg: dict) -> dict:
    return dict(PISTES_DEFAUT, **(cfg["pistes"] if isinstance(cfg.get("pistes"), dict) else {}))


def nom_piste(s: str) -> str:
    return re.sub(r"[^\w-]+", "-", (s or "").strip().lower()).strip("-")


def etat_pistes(etat: dict, cfg: dict, base: list[dict]) -> dict:
    """{nom: fiche de la piste + n (variantes créées), evaluees, gardees, serie (essais de suite sans
    variante gardée), epuisee, active}. Une piste est épuisée après `pistes.arret` essais de suite
    sans progrès : elle ne reçoit plus de variante, il faut la fermer avec sa raison.
    Les variantes cassées (refus statique, plantage, non déterministe) et les doublons ne comptent pas."""
    p = params_pistes(cfg)
    crees: dict[str, int] = {}
    for nom in (etat.get("pistes_variantes") or {}).values():
        crees[nom] = crees.get(nom, 0) + 1
    out = {}
    for nom, x in (etat.get("pistes") or {}).items():
        recs = [r for r in base if r.get("piste") == nom]
        serie = 0
        for r in reversed(recs):
            if r["statut"] in ("garde", "simplifiee"):
                break
            if r["statut"] in CASSES or r["statut"] == "identique":
                continue  # un programme cassé ou un doublon ne dit rien de l'hypothèse
            serie += 1
        epuisee = x["statut"] == "ouverte" and serie >= int(p["arret"])
        trains = [r["train"] for r in recs if r["statut"] in PARENTABLES and r.get("train") is not None]
        out[nom] = dict(x, n=crees.get(nom, 0), evaluees=len(recs), serie=serie, epuisee=epuisee,
                        gardees=sum(r["statut"] in ("garde", "simplifiee") for r in recs),
                        meilleur_train=max(trains) if trains else None,
                        active=x["statut"] == "ouverte" and not epuisee)
    return out


def n_pistes_comptees(etat: dict) -> int:
    """Pistes qui ont eu droit au juge (ouvertes ou fermées) : chacune est un essai de plus."""
    return sum(1 for x in (etat.get("pistes") or {}).values() if x["statut"] in ("ouverte", "fermee"))


def z_champion(etat: dict, cfg: dict) -> float:
    """Barre du champion en marges d'erreur. Sans piste : 1, comme avant. Avec k pistes, le risque
    d'une marge (≈ 16 %, unilatéral) est partagé entre elles (Bonferroni) : 3 pistes → 1,62 marge,
    6 pistes → 1,94. Ouvrir une piste n'est donc jamais gratuit."""
    k = n_pistes_comptees(etat) if pistes_on(cfg) else 1
    if k <= 1:
        return 1.0
    nd = statistics.NormalDist()
    return nd.inv_cdf(1 - (1 - nd.cdf(1.0)) / k)


Z_CHAMPION = 1.0  # posé par resume() : nombre de marges exigé du gain en validation


def borne(r: dict, mode: str) -> float:
    if mode == "cas":
        if r["id"] == "v0000":
            return 0.0
        g, s = r.get("gain_val"), r.get("se_gain_val")
        if g is None or s is None or math.isnan(s):
            return -math.inf  # marge incalculable : on ne peut rien affirmer, donc pas champion
        return g - Z_CHAMPION * s
    return r.get("validation") if r.get("validation") is not None else -math.inf


def resume(etat: dict, cfg: dict, base: list[dict], mode: str) -> dict:
    global Z_CHAMPION
    Z_CHAMPION = z_champion(etat, cfg)
    variantes = lister_variantes(etat)
    notees = {r["id"] for r in base}
    orphelines = [v for v in variantes if v not in notees]
    evalues = [r for r in base if r["id"] != "v0000"]
    gardes = [r for r in base if r["statut"] in GARDES]
    if cfg.get("voie") == "grille":
        # La qualification a conclu qu'un balayage déclaré d'avance suffit : pas de génération, le meilleur
        # programme du benchmark (v0000) va directement au test scellé.
        return {"variantes": variantes, "orphelines": [], "evalues": evalues, "gardes": gardes,
                "champion": next((r for r in base if r["id"] == "v0000"), None), "grille": True,
                "fin": "voie grille : pas de génération, v0000 (meilleur du benchmark) va seul au test", "attente": None}
    cands = [r for r in gardes if r.get("validation") is not None]
    if cfg.get("generalisation"):
        # en validation aussi, le gain sur v0000 doit être réparti sur les familles
        cands = [r for r in cands if r["id"] == "v0000" or (r.get("gen_val") or {}).get("ok", True)]
    # Une simplification validée (borne > 0) remplace son parent : à résultat égal, la règle la plus courte.
    simplifs_ok = [r["id"] for r in cands if r["statut"] == "simplifiee" and borne(r, mode) > 0]
    ombres = {r["parent"] for r in cands if r["id"] in simplifs_ok}
    cands = [r for r in cands if r["id"] not in ombres]
    champion = max(cands, key=lambda r: borne(r, mode)) if cands else None
    raison, attente = None, None
    if len(variantes) >= cfg["plafond"]:
        if orphelines:
            attente = "évaluer d'abord les variantes orphelines : " + ", ".join(orphelines)
        else:
            raison = f"plafond de {cfg['plafond']} variantes atteint"
    cible = cfg.get("cible_validation")
    if raison is None and not orphelines and cible is not None and champion and champion["id"] != "v0000" \
            and borne(champion, mode) >= cible:
        raison = f"cible de validation {cible} atteinte par {champion['id']}"
    stag = cfg.get("arret_stagnation")
    ep = etat_pistes(etat, cfg, base) if pistes_on(cfg) else {}
    if pistes_on(cfg):
        # Avec des pistes, une stagnation ne clôt plus l'évolution : elle épuise UNE piste. La boucle
        # attend alors qu'on en ouvre une autre, et ne finit que lorsque toutes celles permises ont servi.
        if raison is None and not orphelines and not any(x["active"] for x in ep.values()):
            k, kmax = n_pistes_comptees(etat), int(params_pistes(cfg)["max"])
            if k >= kmax:
                raison = f"les {k} pistes permises (pistes.max) sont fermées ou épuisées"
            else:
                attente = (f"aucune piste active ({k}/{kmax} ouvertes jusqu'ici) : fermer les pistes épuisées avec leur "
                           "raison, puis `gevolve.py piste <dossier> ouvrir …` ; ou `scelle --force` pour s'arrêter là")
    elif raison is None and not orphelines and stag:
        # Seul un vrai progrès remet le compteur à zéro. Une exploration n'en est pas un : l'étiquette
        # de famille vient du mutateur, et une étiquette neuve à chaque essai ferait passer du bruit
        # pour une nouvelle piste, si bien que la boucle ne s'arrêterait jamais (reproduit le 08/11).
        serie = 0
        for r in reversed(evalues):
            if r["statut"] == "garde":
                break
            serie += 1
        if serie >= stag:
            raison = f"stagnation : {serie} variantes de suite sans progrès (arret_stagnation={stag}, explorations comprises)"
    return {"variantes": variantes, "orphelines": orphelines, "evalues": evalues, "gardes": gardes,
            "champion": champion, "fin": raison, "attente": attente, "simplifiees_validees": simplifs_ok,
            "pistes": ep}


def scelle_lu(etat: dict):
    if etat.get("scelle"):
        erreur(f"évolution close par le test scellé du {etat['scelle']} : plus de variante ni d'évaluation", 3)


# ---------------------------------------------------------------- commandes

def cmd_init(a):
    d = Path(a.dossier).expanduser().resolve()
    if (d / "config.json").exists():
        erreur(f"{d} contient déjà une évolution")
    d.mkdir(parents=True, exist_ok=True)
    (d / "variantes").mkdir(exist_ok=True)
    (d / "benchmark").mkdir(exist_ok=True)
    for nom in ("FICHE.md", "CONTEXTE.md", "RECHERCHE.md", "LECONS.md", "OBJECTIF.md", "programme.py", "evaluate.py",
                "executeur.py", "autotests/programme.py"):
        if not (d / nom).exists():
            (d / nom).parent.mkdir(exist_ok=True)
            shutil.copy(ASSETS / nom, d / nom)
    (d / "base.jsonl").touch()
    cfg = {
        "id": uuid.uuid4().hex, "nom": a.nom or d.name, "cree": maintenant(),
        "programme": "programme.py", "evaluateur": "evaluate.py", "interpreteur": "python3",
        "fichiers_figes": ["evaluate.py", "executeur.py"],
        "plafond": a.plafond, "par_generation": a.par_generation, "timeout_s": 600,
        "n_min": 0, "n_min_validation": 0, "marge_se": 1.0,
        "imports_permis": IMPORTS_DEFAUT, "verification_statique": True,
        "succes_test": None, "cible_validation": None, "arret_stagnation": 3 * a.par_generation,
        # Phase A
        "base_complete": True, "generalisation": dict(GENERALISATION_DEFAUT), "diagnostic_n_min": 30,
        "temoin": "requis", "contexte": "requis", "fin_train": None,
        # Recherche (09/11/2026 au soir) : RECHERCHE.md + benchmark exécuté requis ; voie choisie par la qualification
        "recherche": "requis", "voie": "evolution",
        # Recherche de patrons : plancher = gain minimal par trade, dans l'unité du juge
        "patrons": dict(PATRONS_DEFAUT),
        # 14/11/2026 : registre de pistes (max = pistes qui auront droit au juge, arret = essais de suite sans
        # progrès avant qu'une piste soit dite épuisée) ; chaque variante lancée deux fois sur « rapide » ;
        # statut de chaque information dans RECHERCHE.md ; "pistes": null rend l'ancien arrêt par stagnation
        "pistes": dict(PISTES_DEFAUT, arret=2 * a.par_generation), "determinisme": True, "informations": "requis",
        "univers": None,
        "verrou": None,
    }
    cfg_ecrire(d, cfg)
    print(f"Évolution « {cfg['nom']} » créée dans {d}")
    print("Recherche d'abord : RECHERCHE.md (recherche externe, inventaire de nos études avec leur période, approches")
    print("à mesurer, grille déclarée), puis chaque approche et chaque cellule de grille codée dans benchmark/")
    print("(grille_*.py pour les cellules) et `gevolve.py benchmark` (train seulement) ; la meilleure devient")
    print("programme.py. Si une grille suffit : voie = \"grille\" dans config.json (pas de génération).")
    print("À remplir avant de verrouiller : FICHE.md (qualification comprise, validée par l'utilisateur),")
    print("CONTEXTE.md (cadre du mécanisme, état de l'art, nos études avec leur période ; relu par l'utilisateur),")
    print("OBJECTIF.md, programme.py (blocs EVOLVE), evaluate.py, autotests/programme.py (programme au hasard) ;")
    print("dans config.json : interpreteur, fichiers_figes (juge + données), n_min, n_min_validation, marge_se,")
    print(f"imports_permis, fin_train, le seuil de réussite du test succes_test (ex. {EXEMPLE_SUCCES}),")
    print("puis le relevé témoin (`gevolve.py temoin`), ou temoin = {\"sans_objet\": \"raison\"}.")


def cmd_benchmark(a):
    """Benchmark exécuté (recherche, AVANT le verrou) : chaque approche connue (littérature, nos études)
    et chaque cellule de la grille déclarée dans RECHERCHE.md, codées comme des programmes dans
    benchmark/, sont notées par le juge sur le TRAIN seulement. Les chiffres des articles portent sur
    d'autres marchés et d'autres périodes : seul notre juge les rend comparables. La meilleure approche
    devient v0000 ; la grille dit si une évolution aurait quelque chose à faire au-delà de seuils."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    if cfg.get("verrou"):
        erreur("le benchmark se fait AVANT le verrou : il choisit le point de départ et la voie (évolution ou grille)")
    progs = programmes_benchmark(d, cfg)
    if len(progs) < 2:
        erreur("benchmark/ doit contenir au moins deux programmes : les approches connues (littérature, nos "
               "études) et les cellules de la grille déclarée dans RECHERCHE.md (fichiers grille_*), chacun "
               "copié de programme.py, seul le bloc EVOLVE changé")
    p0 = d / cfg["programme"]
    try:
        ref_segs, _ = decouper(lire_texte(p0), est_python(cfg))
    except ValueError as e:
        erreur(f"programme : {e}")
    r0 = lancer(d, cfg, p0, "train")
    if not r0["ok"]:
        erreur(f"le juge échoue sur programme.py (train) : {r0.get('erreur')}")
    mode = r0["mode"]
    a0 = agreger(r0["cas"]) if mode == "cas" else None
    lignes = []
    for p in progs:
        x = {"nom": p.stem, "fichier": str(p.relative_to(d)), "sha": sha_fichier(p), "grille": p.stem.startswith("grille")}
        texte = lire_texte(p)
        try:
            segs, zones = decouper(texte, est_python(cfg))
        except ValueError as e:
            segs, zones, x["erreur"] = None, [], f"balises EVOLVE : {e}"
        if "erreur" not in x and (segs != ref_segs or not zones):
            x["erreur"] = "code différent de programme.py hors des blocs EVOLVE : il ne pourrait pas devenir v0000"
        if "erreur" not in x and est_python(cfg) and cfg.get("verification_statique", True):
            fautes = controle_statique(texte, zones, cfg.get("imports_permis", IMPORTS_DEFAUT))
            if fautes:
                x["erreur"] = "contrôle statique : " + " ; ".join(fautes)
        if "erreur" not in x:
            r = lancer(d, cfg, p, "train")  # le train seulement : jamais la validation ni le test
            if not r["ok"]:
                x["erreur"] = r.get("erreur")
            elif r["mode"] != mode:
                x["erreur"] = f"le juge a rendu un résultat de mode {r['mode']} au lieu de {mode}"
            elif mode == "cas":
                ag = agreger(r["cas"])
                if ag is None:
                    x["erreur"] = "n'agit sur aucun cas du train"
                else:
                    sc = sha_cas(r["cas"])  # graine tirée des décisions : mêmes décisions, même marge
                    x.update(score=ag["score"], n=ag["n"], se=erreur_type(r["cas"], None, f"bench-{sc}"),
                             jours=len({c["jour"] or "#" + c["id"] for c in r["cas"] if c["gain"] is not None}),
                             familles=repartition(r["cas"], cfg), sha_cas=sc)
                    if a0 is not None:
                        dv, sv = ecart_apparie(r["cas"], r0["cas"], f"bench-{sc}-vs-programme")
                        x.update(vs_programme=dv, se_vs_programme=sv)
            else:
                x.update(score=r["score"], n=r.get("n"))
        lignes.append(x)
    notes = [x for x in lignes if x.get("score") is not None]
    grille = [x for x in notes if x["grille"]]
    out = {"date": maintenant(), "sha_juge": empreinte_juge(d, cfg), "mode": mode, "programmes": lignes,
           "programme": {"sha": sha_fichier(p0), "sha_cas": sha_cas(r0["cas"]) if mode == "cas" else None,
                         "score": a0 and a0["score"], "n": a0 and a0["n"],
                         "se": erreur_type(r0["cas"], None, f"bench-{sha_cas(r0['cas'])}") if a0 else None},
           "grille_k": len(grille)}
    (d / "benchmark" / "resultats.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"BENCHMARK (train seulement, jamais la validation ni le test) — {len(lignes)} programmes, {len(notes)} notés")
    if mode == "cas":
        print(f"  {'programme':<28} {'score':>9} {'±':>7} {'N':>6} {'jours':>6}  {'familles en gain':<22} {'vs programme.py':>16}")
        for x in sorted(notes, key=lambda x: -x["score"]):
            vs = (f"{signe(x['vs_programme'])} ±{f6(x.get('se_vs_programme'))}" if x.get("vs_programme") is not None else "—")
            print(f"  {x['nom'][:28]:<28} {signe(x['score']):>9} {f6(x['se']):>7} {x['n']:>6} {x['jours']:>6}  "
                  f"{texte_repartition(x['familles'])[:22]:<22} {vs:>16}")
        if a0:
            print(f"  {'(programme.py actuel)':<28} {signe(a0['score']):>9} {f6(out['programme']['se']):>7} {a0['n']:>6}")
        else:
            print("  programme.py n'agit sur aucun cas : le remplacer par le meilleur programme du benchmark.")
    else:
        for x in sorted(notes, key=lambda x: -x["score"]):
            print(f"  {x['nom'][:28]:<28} {f6(x['score']):>10} N={x.get('n')}   (sans marge d'erreur)")
    for x in lignes:
        if x.get("erreur"):
            print(f"  ÉCARTÉ {x['nom']} : {x['erreur'][:200]}")
    if grille:
        g = max(grille, key=lambda x: x["score"])
        k = len(grille)
        print(f"GRILLE : {k} cellule(s), meilleure {g['nom']} {signe(g['score'])}"
              + (f" ±{f6(g.get('se'))}" if g.get("se") is not None else ""))
        if g.get("se") and k >= 2:
            print(f"  La meilleure de {k} cellules est gonflée par le seul hasard d'au plus "
                  f"{f6(biais_selection(k) * g['se'])} ({biais_selection(k):.2f} marge) : le retrancher avant de la "
                  "comparer aux approches connues. La grille doit avoir été déclarée dans RECHERCHE.md AVANT ce benchmark.")
    else:
        print("GRILLE : aucune cellule (grille_*) : impossible de vérifier qu'un simple balayage de seuils ne suffit pas.")
    if notes:
        best = max(notes, key=lambda x: x["score"])
        meme = [x["nom"] for x in notes if mode == "cas" and x.get("sha_cas") == out["programme"]["sha_cas"]]
        print(f"BENCHMARK_MEILLEUR={best['nom']} PROGRAMME={','.join(meme) or 'aucun'}")
        print("Ensuite : copier le meilleur dans programme.py (ou dire dans la fiche pourquoi un autre), recopier ce "
              "tableau dans RECHERCHE.md et la ligne « Benchmark » de la fiche, puis qualifier : voie évolution ou grille.")


def cmd_verrouiller(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    if cfg.get("verrou"):
        erreur(f"déjà verrouillée le {cfg['verrou']['date']}")
    if etat_chemin(cfg).exists():
        erreur(f"un état existe déjà pour cette évolution ({etat_chemin(cfg)}) : ouvrir une nouvelle évolution")
    if not cfg.get("succes_test"):
        erreur("inscrire le seuil de réussite du test AVANT de verrouiller (config.json → succes_test, "
               f"ex. {EXEMPLE_SUCCES}) : décidé après coup, il ne prouverait rien")
    fiche = d / "FICHE.md"
    if not fiche.exists():
        erreur("FICHE.md manquante : l'objectif reformulé et les 5 questions, validés par l'utilisateur, "
               "doivent exister avant le verrou (gabarit dans assets/FICHE.md)")
    txt = fiche.read_text(encoding="utf-8")
    # On cherche les champs du gabarit restés tels quels, pas n'importe quel « < … > » :
    # « agir si score < 0,70 et écart > 5 » est une vraie réponse.
    gabarit = (ASSETS / "FICHE.md").read_text(encoding="utf-8")
    restes = sorted({c for c in re.findall(r"<[^<>\n]+>", gabarit) if c in txt}, key=txt.index)
    if restes:
        erreur("FICHE.md contient encore des champs du gabarit non remplis (" + ", ".join(restes[:3])
               + (", …" if len(restes) > 3 else "") + ") : chaque question doit avoir une réponse chiffrée")
    # [ \t]* et non \s* : sinon une ligne vide « Validée par l'utilisateur : » prenait la ligne suivante
    m = re.search(r"^Validée par l'utilisateur[ \t]*:[ \t]*(\S.*)$", txt, re.M)
    if not m:
        erreur("FICHE.md : la ligne « Validée par l'utilisateur : <qui, quand> » est vide. "
               "Seul l'utilisateur valide la définition de la réussite, jamais le modèle.")
    figer = []  # fichiers de cadrage à figer en plus du juge
    if cfg.get("contexte") == "requis":
        ctx = d / "CONTEXTE.md"
        if not ctx.exists():
            erreur("CONTEXTE.md manquant : cadre du mécanisme, état de l'art et nos études doivent être écrits "
                   "avant le verrou (gabarit dans assets/CONTEXTE.md)")
        tc = ctx.read_text(encoding="utf-8")
        gab = (ASSETS / "CONTEXTE.md").read_text(encoding="utf-8")
        restes = sorted({c for c in re.findall(r"<[^<>\n]+>", gab) if c in tc}, key=tc.index)
        if restes:
            erreur("CONTEXTE.md contient encore des champs du gabarit (" + ", ".join(restes[:3])
                   + (", …" if len(restes) > 3 else "") + ")")
        if not re.search(r"^Relu par l'utilisateur[ \t]*:[ \t]*(\S.*)$", tc, re.M):
            erreur("CONTEXTE.md : la ligne « Relu par l'utilisateur : <qui, quand> » est vide. Le cadre du mécanisme "
                   "oriente toutes les mutations : l'utilisateur doit l'avoir lu.")
        if cfg.get("fin_train"):
            # Une étude interne mesurée après la fin du train dit aux mutateurs ce qui marche en validation.
            corps = "\n".join(l for l in tc.splitlines() if not l.startswith("Relu par l'utilisateur"))
            tardives = sorted({x for x in re.findall(r"\b(20\d\d-\d\d-\d\d)\b", corps) if x > cfg["fin_train"]}
                              | {x for x in re.findall(r"\b(\d\d/\d\d/20\d\d)\b", corps)
                                 if "-".join(reversed(x.split("/"))) > cfg["fin_train"]})
            if tardives:
                print(f"AVERTISSEMENT : CONTEXTE.md cite des dates après la fin du train ({cfg['fin_train']}) : "
                      + ", ".join(tardives[:6]) + ". Si ce sont des résultats d'études mesurés sur la validation ou "
                      "le test, les retirer : les mutateurs liraient ce qui marche en validation.")
        else:
            print("AVERTISSEMENT : fin_train absent de config.json : impossible de repérer dans CONTEXTE.md les "
                  "études mesurées sur la période de validation.")
        figer.append("CONTEXTE.md")
    tm = cfg.get("temoin")
    if tm == "requis":
        tj = d / "temoin.json"
        if not tj.exists():
            erreur("relevé témoin requis avant le verrou : capturer en direct l'entrée de vrais instants de décision, "
                   "puis `gevolve.py temoin <dossier> --capture <fichier>` quand les données historiques de ces "
                   "instants existent. Sans objet (pas de données datées) : temoin = {\"sans_objet\": \"raison\"}.")
        t = json.loads(tj.read_text(encoding="utf-8"))
        cap = d / t.get("capture", "")
        if not cap.is_file() or sha_fichier(cap) != t.get("sha_capture"):
            erreur("relevé témoin : le fichier capturé a changé ou disparu depuis `temoin` : le relancer")
        if not (t.get("ok") or t.get("accepte")):
            erreur(f"relevé témoin en échec ({t.get('identiques')}/{t.get('n')} entrées identiques, "
                   f"{t.get('absents')} absentes) : une donnée historique n'est pas ce qu'on voyait en direct "
                   "(fuite, révision, horodatage). Corriger le juge, ou `temoin --accepter \"raison\"` si l'écart est compris.")
        print(f"Relevé témoin : {t.get('identiques')}/{t.get('n')} entrées identiques"
              + (f" — écarts acceptés : {t['accepte']}" if t.get("accepte") and not t.get("ok") else ""))
        figer += ["temoin.json", t["capture"]]
    elif isinstance(tm, dict) and tm.get("sans_objet"):
        print(f"Relevé témoin : sans objet ({tm['sans_objet']})")
    elif tm is not None:
        erreur("config.json → temoin : \"requis\" ou {\"sans_objet\": \"raison\"}")
    voie = cfg.get("voie")
    if voie is not None and voie not in VOIES:
        erreur(f"config.json → voie : {' ou '.join(VOIES)} (choisie par la qualification)")
    bench = None
    if cfg.get("recherche") == "requis":
        rch = d / "RECHERCHE.md"
        if not rch.exists():
            erreur("RECHERCHE.md manquant : recherche externe, inventaire de nos études, approches à mesurer et "
                   "grille déclarée doivent être écrits avant le verrou (gabarit dans assets/RECHERCHE.md)")
        tr = rch.read_text(encoding="utf-8")
        gab = (ASSETS / "RECHERCHE.md").read_text(encoding="utf-8")
        restes = sorted({c for c in re.findall(r"<[^<>\n]+>", gab) if c in tr}, key=tr.index)
        if restes:
            erreur("RECHERCHE.md contient encore des champs du gabarit (" + ", ".join(restes[:3])
                   + (", …" if len(restes) > 3 else "") + ")")
        if cfg.get("informations") == "requis":
            # Chaque information qui compte porte un statut : qui l'a cherchée importe moins que de savoir
            # si elle est vérifiée. Rien ne reste « à obtenir » au verrou : obtenue, ou abandonnée en le disant.
            infos = re.findall(r"^\s*[-*]\s*\[(" + "|".join(STATUTS_INFO) + r")\]\s*(.*)$", tr, re.M)
            if not infos:
                erreur("RECHERCHE.md, section « Informations » : aucune ligne « - [statut] information — source — qui ». "
                       "Statuts : " + ", ".join(STATUTS_INFO))
            attente = [x for s, x in infos if s == "à obtenir"]
            if attente:
                erreur(f"RECHERCHE.md : {len(attente)} information(s) encore « à obtenir » (" + " ; ".join(x[:60] for x in attente[:3])
                       + ") : les obtenir (de l'utilisateur ou par la recherche), ou les passer en [abandonnée] en disant pourquoi")
            comptes = {s: sum(1 for y, _ in infos if y == s) for s in STATUTS_INFO}
            print("Informations : " + ", ".join(f"{v} {k}" for k, v in comptes.items() if v))
            if comptes["non vérifiée"]:
                print("  Une information non vérifiée n'entre dans CONTEXTE.md que marquée « [non vérifiée] » : "
                      "les mutateurs ne doivent pas la prendre pour un fait.")
        bj = d / "benchmark" / "resultats.json"
        if not bj.exists():
            erreur("benchmark exécuté requis avant le verrou : coder les approches connues et les cellules de la grille "
                   "dans benchmark/, puis `gevolve.py benchmark <dossier>` (train seulement)")
        bench = json.loads(bj.read_text(encoding="utf-8"))
        if bench.get("sha_juge") != empreinte_juge(d, cfg):
            erreur("le juge ou ses données ont changé depuis le benchmark : ses chiffres ne valent plus. "
                   "Relancer `gevolve.py benchmark`.")
        actuels = {str(p.relative_to(d)): sha_fichier(p) for p in programmes_benchmark(d, cfg)}
        if actuels != {x["fichier"]: x["sha"] for x in bench.get("programmes", [])}:
            erreur("benchmark/ a changé depuis `gevolve.py benchmark` (programme ajouté, retiré ou modifié) : le relancer")
        if not [x for x in bench["programmes"] if x.get("score") is not None]:
            erreur("aucun programme du benchmark n'a été noté : rien à quoi comparer le point de départ")
        figer += ["RECHERCHE.md", "benchmark"]
    prog = d / cfg["programme"]
    try:
        _, zones = decouper(lire_texte(prog), est_python(cfg))
    except ValueError as e:
        erreur(f"programme : {e}")
    if not zones:
        erreur("programme sans bloc EVOLVE-BLOCK-START / EVOLVE-BLOCK-END : rien à faire évoluer")
    if est_python(cfg) and cfg.get("verification_statique", True):
        fautes = controle_statique(lire_texte(prog), zones, cfg.get("imports_permis", IMPORTS_DEFAUT))
        if fautes:
            erreur("le programme initial ne passe pas le contrôle statique de ses propres blocs EVOLVE "
                   "(toutes ses variantes seraient refusées) : " + " ; ".join(fautes))
    for f in (cfg["evaluateur"], "executeur.py", "OBJECTIF.md", "FICHE.md", *figer):
        if (d / f).exists() and f not in cfg["fichiers_figes"]:
            cfg["fichiers_figes"].insert(0, f)

    v0 = d / "variantes" / "v0000"
    v0.mkdir(parents=True, exist_ok=True)
    shutil.copy(prog, v0 / nom_prog(cfg))
    (v0 / "meta.json").write_text(json.dumps({"id": "v0000", "parent": None, "cree": maintenant()}))
    p0 = v0 / nom_prog(cfg)

    res = {}
    for split in ("rapide", "train", "validation"):
        r = lancer(d, cfg, p0, split)
        if not r["ok"]:
            erreur(f"le programme initial échoue sur « {split} » : {r.get('erreur')}. "
                   "Corriger evaluate.py ou programme.py avant de verrouiller.")
        res[split] = r
    mode = res["train"]["mode"]
    if any(r["mode"] != mode for r in res.values()):
        erreur("le juge ne rend pas le même type de résultat sur tous les splits")
    if mode == "cas" and (agreger(res["train"]["cas"]) is None or agreger(res["validation"]["cas"]) is None):
        erreur("le programme initial n'agit sur aucun cas (gain toujours None) : impossible de servir de référence")
    if bench is not None and mode == "cas":
        notes = [x for x in bench["programmes"] if x.get("score") is not None]
        best = max(notes, key=lambda x: x["score"])
        s0, t0 = sha_cas(res["train"]["cas"]), agreger(res["train"]["cas"])["score"]
        meme = [x["nom"] for x in notes if x.get("sha_cas") == s0]
        print(f"Benchmark : {len(notes)} programmes notés sur le train ({bench.get('grille_k', 0)} cellules de grille) ; "
              f"v0000 = {', '.join(meme) or 'aucun'} ; meilleur : {best['nom']} {signe(best['score'])} ±{f6(best.get('se'))}")
        if not meme:
            print("  AVERTISSEMENT : v0000 ne prend les décisions d'aucun programme du benchmark : le point de départ "
                  "n'a pas été mesuré avec les approches connues.")
        elif best["nom"] not in meme and best["score"] - (best.get("se") or 0) > t0:
            print(f"  AVERTISSEMENT : {best['nom']} bat v0000 de plus d'une marge sur le train : partir de lui, ou dire "
                  "dans la fiche pourquoi pas.")
    if voie == "grille":
        print("VOIE=grille : aucune génération. v0000 (le meilleur du benchmark) ira seul au test scellé, contre le "
              "seuil inscrit ; `scelle` quand le test est mûr.")
    if mode == "cas":
        if not cfg.get("n_min") or not cfg.get("n_min_validation"):
            erreur("n_min et n_min_validation valent 0 : une variante qui n'agit que sur 3 cas chanceux "
                   "pourrait devenir champion. Les fixer dans config.json (ex. 300 et 100), ou 1 si c'est voulu.")
        for split in ("train", "validation"):
            vals = [c["gain"] - c["ref"] for c in res[split]["cas"] if c["gain"] is not None]
            if max(vals) - min(vals) < 1e-12 and not a.accepter_score_constant:
                erreur(f"sur « {split} », gain − ref vaut {vals[0]:.6g} pour TOUS les cas du programme initial "
                       "(marge d'erreur nulle). Cause habituelle : la référence recopie le gain (ex. « acheter au "
                       "hasard au même prix » appliqué au résultat réalisé), si bien que toute variante aura 0 ±0. "
                       "Prendre ref = 0 avec le prix comme probabilité. Si c'est vraiment voulu : --accepter-score-constant.")
        jours = len({c["jour"] or "#" + c["id"] for c in res["train"]["cas"]})
        if jours < 2:
            erreur("le train tient en un seul « jour » : la marge d'erreur est incalculable et toute variante serait refusée")
        if len({c["jour"] or "#" + c["id"] for c in res["validation"]["cas"]}) < 2:
            erreur("la validation tient en un seul « jour » : la marge du gain en validation est incalculable, "
                   "aucune variante ne pourrait devenir championne. Allonger la validation.")
        # Auto-test 1 : le juge est déterministe (sinon « identique » et l'écart apparié n'ont pas de sens)
        bis = lancer(d, cfg, p0, "train")
        if not bis["ok"] or bis.get("cas") != res["train"]["cas"]:
            erreur("auto-test : deux appels du juge sur le même programme et le même split ne rendent pas les mêmes "
                   "cas. Fixer les graines et l'ordre de tri dans evaluate.py.")
        print(f"Auto-test déterminisme : OK ({len(res['train']['cas'])} cas identiques sur deux appels)")
        # Auto-test 2 (piège) : un programme au hasard ne doit pas battre la référence
        hasard = d / "autotests" / nom_prog(cfg)
        if hasard.exists():
            rh = lancer(d, cfg, hasard, "train")
            if not rh["ok"] or agreger(rh["cas"]) is None:
                erreur(f"auto-test piège : autotests/{nom_prog(cfg)} échoue ou n'agit sur aucun cas ({rh.get('erreur')})")
            ah, seh = agreger(rh["cas"]), erreur_type(rh["cas"], None, "piege-train")
            if seh and not math.isnan(seh):
                z = ah["score"] / seh
            else:
                z = 0.0 if ah["score"] == 0 else math.copysign(math.inf, ah["score"])
            print(f"Auto-test piège (programme au hasard) : train={f6(ah['score'])} ±{f6(seh)} N={ah['n']} (z={z:.2f})")
            # Unilatéral : seul un hasard qui BAT la référence la rend malhonnête. Un hasard qui perd
            # est normal dès qu'il paie des frais ou le spread.
            if z > 3:
                erreur("auto-test piège : un programme qui décide au hasard BAT la référence de plus de 3 marges. "
                       "La référence n'est pas honnête (la boucle apprendrait la tendance de la période). Revoir gain_et_ref().")
            if z < -3:
                print("  AVERTISSEMENT : le hasard perd nettement contre la référence (z < −3). Normal s'il paie des "
                      "frais ou le spread ; sinon, vérifier gain_et_ref() : la référence est peut-être trop avantagée.")
        else:
            print(f"AVERTISSEMENT : pas de autotests/{nom_prog(cfg)} (programme qui décide au hasard). "
                  "Le juge n'est pas testé contre une référence malhonnête.")
        # Auto-test 3 (alerte, pas un refus) : le suiveur naïf achète le côté qui vient de bouger. Dans un
        # marché qui digère l'information, il perd au moins le coût d'un aller-retour. S'il gagne nettement,
        # soit une donnée de l'entrée connaît le futur (fuite), soit le marché est vraiment en retard.
        suiveur = d / "autotests" / f"suiveur{Path(nom_prog(cfg)).suffix}"
        if suiveur.exists():
            rs = lancer(d, cfg, suiveur, "train")
            if not rs["ok"] or agreger(rs["cas"]) is None:
                erreur(f"auto-test suiveur : {suiveur.name} échoue ou n'agit sur aucun cas ({rs.get('erreur')})")
            a_s, se_s = agreger(rs["cas"]), erreur_type(rs["cas"], None, "suiveur-train")
            z_s = a_s["score"] / se_s if se_s and not math.isnan(se_s) else 0.0
            print(f"Auto-test suiveur naïf : train={f6(a_s['score'])} ±{f6(se_s)} N={a_s['n']} (z={z_s:.2f})")
            if z_s > 3:
                print("  ALERTE : le suiveur naïf bat la référence de plus de 3 marges. Fuite probable (une donnée de "
                      "l'entrée connaît déjà la suite) ou vrai retard du marché : le prouver avec le relevé témoin "
                      "et la date de chaque champ AVANT de lancer la première génération.")
    if lancer(d, cfg, p0, "test")["ok"]:
        erreur("evaluate.py rend un résultat sur « test » sans GEVOLVE_SCELLE=1 : fermer ce split avant de verrouiller.")
    # Le test n'est plus lancé ici : on demande seulement au juge de compter ses cas (GEVOLVE_SONDE=1),
    # sans faire tourner le programme. Ainsi « ouvert une seule fois » est littéralement vrai.
    sd = lancer(d, cfg, p0, "test", sonde=True)
    if sd["ok"] and sd.get("mode") == "sonde":
        if sd["n"] <= 0 and not a.test_a_venir:
            erreur("le split « test » est vide : le test scellé serait impossible "
                   "(--test-a-venir si le test est du paper trading encore à collecter)")
        if sd["n"] <= 0:
            print("Test scellé À VENIR : 0 cas aujourd'hui (paper trading à collecter). `scelle` refusera "
                  "tant que le juge n'en compte pas assez.")
        else:
            print(f"Test scellé : {sd['n']} cas prêts, programme jamais lancé dessus.")
    else:
        print("AVERTISSEMENT : le juge ne sait pas compter le test sans le lancer (GEVOLVE_SONDE, voir le "
              "gabarit evaluate.py). Le test n'est pas vérifié avant l'ouverture finale.")

    cfg["verrou"] = {"date": maintenant()}
    etat = {"id": cfg["id"], "mode": mode, "base_n": 0, "base_dernier": "", "scelle": None, "variantes": {},
            "verrou": {"date": cfg["verrou"]["date"], "empreintes": empreintes(d, cfg),
                       "regles": {k: cfg.get(k) for k in REGLES}}}
    cfg_ecrire(d, cfg)
    etat_ecrire(cfg, etat, d)

    rec = {"id": "v0000", "parent": None, "idee": "programme initial", "niche": "initial",
           "statut": "initial", "date": maintenant(), "sha_prog": sha_fichier(p0), "sha_res": {}}
    if mode == "cas":
        for split in ("rapide", "train", "validation"):
            rec["sha_res"][split] = resultats_ecrire(d, "v0000", split, res[split]["cas"])
        t, v = agreger(res["train"]["cas"]), agreger(res["validation"]["cas"])
        rec.update(train=t["score"], n_train=t["n"], ref_train=t["ref"],
                   se_train=erreur_type(res["train"]["cas"], None, "v0000-train"),
                   validation=v["score"], n_val=v["n"], ref_val=v["ref"],
                   se_val=erreur_type(res["validation"]["cas"], None, "v0000-validation"))
    else:
        rec.update(train=res["train"]["score"], n_train=res["train"].get("n"),
                   validation=res["validation"]["score"], n_val=res["validation"].get("n"))
    with verrou_fichier(d):
        base_ajouter(d, cfg, rec)
    print(f"VERROU posé — {len(etat['verrou']['empreintes'])} fichier(s) figé(s), mode « {mode} ».")
    print(f"v0000 (initial) : train={f6(rec['train'])} ±{f6(rec.get('se_train'))} N={rec.get('n_train')} | "
          f"validation={f6(rec['validation'])} ±{f6(rec.get('se_val'))} N={rec.get('n_val')}")
    print(f"Seuil de réussite du test inscrit : {json.dumps(cfg['succes_test'])}")
    print(f"Plafond : {cfg['plafond']} variantes, {cfg['par_generation']} par génération, marge {cfg['marge_se']} × erreur.")
    if mode == "cas":
        print(f"EFFET MINIMAL VISIBLE : la marge d'erreur de v0000 vaut ±{f6(rec.get('se_train'))} sur le train et "
              f"±{f6(rec.get('se_val'))} sur la validation. Une retouche qui gagne moins que "
              f"{cfg.get('marge_se', 1.0)} × sa propre marge (du même ordre) n'est pas gardée. Si les retouches "
              "attendues (FICHE, qualification) sont de cet ordre ou plus petites, la boucle fera surtout du "
              "réglage de seuils : préférer une grille déclarée d'avance et le test scellé.")
        if cfg.get("generalisation"):
            print(f"Juge généralisateur : gain exigé dans au moins {cfg['generalisation'].get('part_min')} des familles "
                  f"({', '.join(cfg['generalisation'].get('cles') or ['mois'])}, N ≥ {cfg['generalisation'].get('n_min')} "
                  "par famille), sur le train pour être gardée, en validation pour être championne.")


def ancetres(rec: dict, connus: dict) -> list[str]:
    out, p = [], rec.get("parent")
    while p and p in connus:
        out.append(p)
        p = connus[p].get("parent")
    return out


def emplacements_pistes(etat: dict, cfg: dict, base: list[dict], connus: dict, k: int, enfants: dict,
                        reussis: set, rng: random.Random) -> list[tuple]:
    """Répartit les k variantes de la génération entre les pistes actives (la moins servie d'abord).
    Première variante d'une piste : CAP libre, depuis son point de départ (v0000 par défaut) : c'est
    le retour en arrière, on repart d'avant les choix des autres pistes. Ensuite le CAP tourne À
    L'INTÉRIEUR de la piste : raffiner son meilleur, le simplifier une fois, revenir à un autre de
    ses essais ou à son départ, croiser avec le meilleur d'une autre piste active."""
    ep = etat_pistes(etat, cfg, base)
    actives = sorted(n for n, x in ep.items() if x["active"])
    if not actives:
        return []
    complete, caps_vus = bool(cfg.get("base_complete")), etat.get("caps", {})
    charge = {n: ep[n]["n"] for n in actives}
    donnes = {n: 0 for n in actives}
    out = []
    for _ in range(k):
        nom = min(actives, key=lambda n: (charge[n], n))
        j = donnes[nom]
        charge[nom] += 1
        donnes[nom] += 1
        membres = [r for r in base if r.get("piste") == nom and r["statut"] in PARENTABLES]
        depart = connus.get(ep[nom].get("depart") or "v0000") or connus["v0000"]
        if not membres:
            out.append(("libre", depart, None, nom))
            continue
        best = max(membres, key=lambda r: r["train"])
        bloque = enfants.get(best["id"], 0) >= cfg["par_generation"] and best["id"] not in reussis
        seq = ["retour", "croiser", "raffiner"] if bloque else ["raffiner", "retour", "croiser"]
        deja = any(p == best["id"] and caps_vus.get(v) == "simplifier" for v, p in etat.get("variantes", {}).items())
        if complete and best["statut"] == "garde" and not deja:
            seq.insert(1, "simplifier")
        cap, r, avec = seq[j % len(seq)], best, None
        if cap == "retour":
            cands = [c for c in membres if c["id"] != best["id"]] + [depart]
            r = rng.choices(cands, weights=[1 / (1 + enfants.get(c["id"], 0)) for c in cands])[0]
        if cap == "croiser":
            autres = [x for x in base if x.get("piste") in actives and x.get("piste") != nom and x["statut"] in PARENTABLES]
            avec = max(autres, key=lambda x: x["train"]) if autres else None
            if avec is None:
                cap = "raffiner"
        out.append((cap, r, avec, nom))
    return out


def cmd_parents(a):
    """Un emplacement = un parent + un CAP imposé au mutateur. Le CAP « retour » repart d'un ancêtre
    du meilleur ou d'une branche peu explorée : c'est le retour en arrière d'AlphaEvolve, qui évite
    de grimper indéfiniment la même colline. Aucun score de validation n'est affiché ici : il ne
    doit jamais atteindre les mutateurs."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    etat, base = controler(d, cfg, donnees=False)
    if cfg.get("voie") == "grille":
        erreur("voie grille (qualification) : pas de génération. `scelle` ouvrira le test pour v0000 quand il sera mûr.")
    connus = {r["id"]: r for r in base}
    pool = [r for r in base if r["statut"] in PARENTABLES]
    valides = [r for r in pool if r["statut"] in GARDES]
    k = a.k or cfg["par_generation"]
    enfants: dict[str, int] = {}
    for p in etat.get("variantes", {}).values():
        enfants[p] = enfants.get(p, 0) + 1
    reussis = {r["parent"] for r in base if r["statut"] == "garde"}  # une exploration n'est pas un succès du parent
    meilleur = max(valides, key=lambda r: r["train"])
    elites: dict[str, dict] = {}
    for r in pool:
        if r["niche"] not in elites or r["train"] > elites[r["niche"]]["train"]:
            elites[r["niche"]] = r
    autres_niches = sorted((r for r in elites.values() if r["niche"] != meilleur["niche"]),
                           key=lambda r: r["train"], reverse=True)
    lignee = set(ancetres(meilleur, connus))
    bloque = enfants.get(meilleur["id"], 0) >= cfg["par_generation"] and meilleur["id"] not in reussis
    sequence = (["retour", "famille", "retour", "croiser", "raffiner"] if bloque
                else ["raffiner", "famille", "retour", "croiser"])
    complete = bool(cfg.get("base_complete"))
    caps_vus = etat.get("caps", {})
    deja_simplifie = any(p == meilleur["id"] and caps_vus.get(v) == "simplifier"
                         for v, p in etat.get("variantes", {}).items())
    if complete and meilleur["id"] != "v0000" and not deja_simplifie and k >= 2:
        # une fois par meilleur : retirer une condition, pour que les choix hérités soient remis en cause
        sequence = sequence[: k - 1] + ["simplifier"] if len(sequence) >= k else sequence[:-1] + ["simplifier"]
    # Base complète : rang sur le train (les bons tirés plus souvent), pénalité aux parents déjà prolifiques.
    rang = {r["id"]: i for i, r in enumerate(sorted(pool, key=lambda r: r["train"], reverse=True))}
    rng = random.Random(len(base))
    pris: set[str] = set()

    def tirer(cands: list[dict], poids: list[float]) -> dict | None:
        lib = [(c, w) for c, w in zip(cands, poids) if c["id"] not in pris]
        if not lib:
            return None
        return rng.choices([c for c, _ in lib], weights=[w for _, w in lib])[0]

    emplacements = []
    for i in range(k):
        cap = sequence[i % len(sequence)]
        avec = None
        if cap == "famille":
            r = tirer(autres_niches, [1 / (j + 1) for j in range(len(autres_niches))])
            if r is None:
                cap = "retour"
        if cap == "retour":
            cands = [c for c in pool if c["id"] != meilleur["id"]]
            # ancêtres du meilleur favorisés, branches déjà beaucoup essayées défavorisées
            r = tirer(cands, [(2.0 if c["id"] in lignee else 1.0) / (1 + enfants.get(c["id"], 0))
                              / (math.sqrt(1 + rang[c["id"]]) if complete else 1.0) for c in cands])
            if r is None:
                cap = "raffiner"
        if cap == "simplifier":
            r = meilleur
        if cap == "croiser":
            r = meilleur
            secs = autres_niches or sorted((c for c in pool if c["id"] != meilleur["id"]),
                                           key=lambda c: c["train"], reverse=True)
            avec = secs[0] if secs else None
            if avec is None:
                cap = "raffiner"
        if cap == "raffiner":
            r = meilleur
        if cap in ("famille", "retour"):
            pris.add(r["id"])
        emplacements.append((cap, r, avec, None))
    if pistes_on(cfg):
        emplacements = emplacements_pistes(etat, cfg, base, connus, k, enfants, reussis, random.Random(len(base)))
        bloque = False
        if not emplacements:
            ep = etat_pistes(etat, cfg, base)
            for nom, x in ep.items():
                if x["epuisee"]:
                    print(f"PISTE ÉPUISÉE : {nom} ({x['serie']} essais de suite sans variante gardée) → "
                          f"`gevolve.py piste {d} fermer {nom} --raison \"…\"`")
            erreur("aucune piste active. Ouvrir une piste : `gevolve.py piste " + str(d) + " ouvrir <nom> --mecanisme \"d'où "
                   "viendrait l'avantage\" --refute \"le chiffre qui la réfuterait\"` (une piste fermée s'en sert avec "
                   "--depuis <piste>). Une hypothèse qui demande une donnée absente de l'entrée du programme : --hors-juge.", 3)

    pats = etat.get("patrons") or []
    if pats:
        deja = sum(1 for c in etat.get("caps", {}).values() if c == "patron")
        if deja < int(cfg["plafond"] * params_patrons(cfg)["part_budget_max"]):
            for j, (cap, r, avec, pst) in enumerate(emplacements):
                if cap == "raffiner":
                    emplacements[j] = ("patron", r, None, pst)
                    break
    s = resume(etat, cfg, base, etat["mode"])
    print(f"PARENTS ({len(emplacements)} emplacements) — {len(s['variantes'])}/{cfg['plafond']} variantes créées"
          + (" — le meilleur stagne : priorité au retour en arrière" if bloque else ""))
    for i, (cap, r, avec, pst) in enumerate(emplacements, 1):
        print(f"  {i}. CAP={cap} PARENT={r['id']} niche={r['niche']} train={f6(r['train'])}"
              f" enfants={enfants.get(r['id'], 0)} — {r['idee']}" + (f"\n     PISTE={pst}" if pst else ""))
        print(f"     fichier : {fichier_variante(d, cfg, r['id'])}")
        if avec:
            print(f"     AVEC={avec['id']} niche={avec['niche']} — {avec['idee']} — {fichier_variante(d, cfg, avec['id'])}")
    print("COMMANDE : gevolve.py nouveau " + str(d) + " "
          + " ".join(f"--parent {r['id']}:{cap}" + (f":{pst}" if pst else "") for cap, r, _, pst in emplacements))
    if pistes_on(cfg):
        print("PISTES (à citer dans le brief de chaque variante : son nom, son mécanisme, ce qui la réfuterait) :")
        for nom, x in s["pistes"].items():
            if x["statut"] == "ouverte":
                print(f"  {nom} [{'épuisée' if x['epuisee'] else 'active'}] {x['n']} variante(s), {x['gardees']} gardée(s), "
                      f"{x['serie']} de suite sans progrès — mécanisme : {x['mecanisme']} — réfutée si : {x.get('refute')}")
                if x["epuisee"]:
                    print(f"    → épuisée : `gevolve.py piste {d} fermer {nom} --raison \"…\"`, puis ouvrir une piste "
                          "tirée de ce qu'elle a appris (--depuis)")
        fermees = [f"{nom} ({x.get('raison')})" for nom, x in s["pistes"].items() if x["statut"] == "fermee"]
        if fermees:
            print("  fermées, à ne pas rouvrir sous un autre nom : " + " ; ".join(fermees))
    vus = {r["id"] for _, r, _, _ in emplacements} | {av["id"] for _, _, av, _ in emplacements if av}
    inspi = [r for r in autres_niches if r["id"] not in vus][:3]
    if inspi:
        print("AUTRES ÉLITES (inspiration) :")
        for r in inspi:
            print(f"  {r['id']} niche={r['niche']} train={f6(r['train'])} — {fichier_variante(d, cfg, r['id'])}")
    if pats:
        print("PATRONS CONFIRMÉS (train, `gevolve.py patrons`) — à donner tels quels au mutateur du CAP patron :")
        for x in pats:
            print("  - " + x["texte"])
    niches = sorted({r["niche"] for r in base if r["niche"] != "initial"})
    print("NICHES EXISTANTES : " + (", ".join(niches) or "aucune encore"))
    if s["orphelines"]:
        print("ORPHELINES à évaluer avant tout : " + ", ".join(s["orphelines"]))
    print(f"HISTORIQUE ({min(a.historique, len(base))} derniers essais, train seulement) :")
    for r in base[-a.historique:]:
        print(f"  {r['id']} {r['statut']:<20} niche={r['niche']:<16} train={f6(r.get('train'))} — {r['idee']}")
    nmin_diag = cfg.get("diagnostic_n_min")
    if nmin_diag and etat["mode"] == "cas":
        # Le retour d'information d'AlphaEvolve, protégé pour un juge bruité : train seulement, segments
        # d'au moins N trades avec leur marge, jamais de trade individuel.
        for pid in dict.fromkeys(r["id"] for _, r, _, _ in emplacements):
            lignes = diagnostic(resultats_lire(d, connus[pid], "train"), int(nmin_diag))
            if lignes:
                print(f"DIAGNOSTIC {pid} (train seulement, gain − ref par segment, segments de N ≥ {nmin_diag}) :")
                for l in lignes:
                    print("  " + l)
    if complete:
        n_ev = len(s["evalues"])
        retard = n_ev - etat.get("lecons_n", 0)
        print("CONTEXTE.md (figé) et LECONS.md sont à citer dans chaque brief."
              + (f" LECONS.md n'a pas été refait depuis {retard} variantes : lancer `gevolve.py lecons` et le "
                 "réécrire (train seulement) avant cette génération." if retard >= 2 * cfg["par_generation"] else ""))


def cmd_nouveau(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    with verrou_fichier(d):
        etat, base = controler(d, cfg, donnees=False)
        scelle_lu(etat)
        if cfg.get("voie") == "grille":
            erreur("voie grille (qualification) : pas de génération. `scelle` ouvrira le test pour v0000 quand il sera mûr.")
        connus = {r["id"]: r for r in base}
        demandes = []
        ep = etat_pistes(etat, cfg, base) if pistes_on(cfg) else {}
        for spec in a.parent:
            p, cap, pst = (spec.split(":") + ["", ""])[:3]
            cap = cap or "libre"
            if cap not in CAPS:
                erreur(f"cap « {cap} » inconnu ({', '.join(CAPS)})")
            if p not in connus or connus[p]["statut"] not in PARENTABLES:
                erreur(f"parent {p} inconnu ou non gardé")
            if pistes_on(cfg):
                if pst not in ep:
                    erreur(f"chaque variante appartient à une piste : --parent {p}:{cap}:<piste> "
                           f"(pistes : {', '.join(n for n, x in ep.items() if x['active']) or 'aucune active, en ouvrir une'})")
                if not ep[pst]["active"]:
                    erreur(f"piste « {pst} » {'épuisée' if ep[pst]['epuisee'] else ep[pst]['statut']} : elle ne reçoit plus de "
                           "variante. La fermer avec sa raison et en ouvrir une autre.")
            elif pst:
                erreur("cette évolution n'a pas de registre de pistes (créée avant le 14/11) : --parent vX:cap")
            verifier_programme(d, cfg, connus[p])
            demandes.append((p, cap, pst or None))
        variantes = lister_variantes(etat)
        n_pat = sum(1 for _, c, _ in demandes if c == "patron")
        if n_pat:
            if not etat.get("patrons"):
                erreur("CAP patron sans patron confirmé : lancer `gevolve.py patrons` d'abord")
            deja = sum(1 for c in etat.get("caps", {}).values() if c == "patron")
            maxi = int(cfg["plafond"] * params_patrons(cfg)["part_budget_max"])
            if deja + n_pat > maxi:
                erreur(f"CAP patron : {deja} déjà utilisés, {n_pat} demandés, maximum {maxi} "
                       "(un tiers du budget, pour garder de l'exploration)")
        if len(variantes) + len(a.parent) > cfg["plafond"]:
            erreur(f"plafond : {len(variantes)}/{cfg['plafond']} variantes déjà créées, {len(a.parent)} demandées")
        suivant = max([int(v[1:]) for v in variantes] + [0]) + 1
        for p, cap, pst in demandes:
            vid = f"v{suivant:04d}"
            suivant += 1
            dst = d / "variantes" / vid
            if dst.exists():
                shutil.rmtree(dst)  # reste d'une création interrompue, jamais enregistrée
            dst.mkdir()
            shutil.copy(fichier_variante(d, cfg, p), dst / nom_prog(cfg))
            (dst / "meta.json").write_text(json.dumps({"id": vid, "parent": p, "cree": maintenant()}))
            etat["variantes"][vid] = p
            etat.setdefault("caps", {})[vid] = cap
            if pst:
                etat.setdefault("pistes_variantes", {})[vid] = pst
            print(f"VARIANTE={vid} PARENT={p} CAP={cap}" + (f" PISTE={pst}" if pst else "") + f" FICHIER={dst / nom_prog(cfg)}")
        etat_ecrire(cfg, etat, d)


def cmd_evaluer(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    etat, base = controler(d, cfg, donnees=True)
    scelle_lu(etat)
    mode = etat["mode"]
    connus = {r["id"]: r for r in base}
    vid = a.variante
    if vid in connus:
        erreur(f"{vid} déjà évaluée ({connus[vid]['statut']})")
    vdir = d / "variantes" / vid
    if vid not in etat.get("variantes", {}) or not (vdir / nom_prog(cfg)).exists():
        erreur(f"variante {vid} introuvable : la créer avec `nouveau`")
    parent = connus[etat["variantes"][vid]]  # le parent vient de l'état, pas de meta.json (éditable)
    verifier_programme(d, cfg, parent)
    rec = {"id": vid, "parent": parent["id"], "idee": a.idee.strip(),
           "niche": (a.niche or "divers").strip().lower().replace(" ", "-"), "date": maintenant(), "sha_res": {},
           "cap": etat.get("caps", {}).get(vid)}
    if (etat.get("pistes_variantes") or {}).get(vid):
        rec["piste"] = etat["pistes_variantes"][vid]
    niche_neuve = rec["niche"] not in {r["niche"] for r in base if r["statut"] in PARENTABLES} | {"divers"}
    complete, cap, statut_final = bool(cfg.get("base_complete")), rec["cap"], "garde"

    def conclure(statut: str, raison: str | None = None):
        rec["statut"] = statut
        if raison:
            rec["raison"] = raison
        with verrou_fichier(d):
            _, b2 = controler(d, cfg, donnees=False)
            if any(r["id"] == vid for r in b2):
                erreur(f"{vid} a été évaluée en parallèle entre-temps")
            if statut in PARENTABLES:  # doublon évalué en parallèle : relu sous verrou
                jumeau = next((r["id"] for r in b2 if r.get("sha_prog") == rec.get("sha_prog")
                               or (rec["sha_res"].get("train") and r.get("sha_res", {}).get("train") == rec["sha_res"]["train"])), None)
                if jumeau:
                    rec["statut"], rec["raison"] = "identique", f"même code ou même comportement que {jumeau} (évalué en parallèle)"
            base_ajouter(d, cfg, rec)
        ligne = f"RESULTAT {vid} {rec['statut']}"
        if rec.get("train") is not None:
            ligne += f" train={f6(rec['train'])}"
            if mode == "cas" and rec.get("diff_parent") is not None:
                ligne += f" ({signe(rec['diff_parent'])} ±{f6(rec.get('se_diff_parent'))} vs {rec.get('reference', parent['id'])})"
                if rec.get("gen_train"):
                    ligne += f" familles en gain : {texte_generalisation(rec['gen_train'])}"
            else:
                ligne += f" (parent {parent['id']} {f6(parent['train'])})"
        if rec.get("validation") is not None:
            ligne += f" validation={f6(rec['validation'])}"
            if mode == "cas":
                ligne += f" gain vs v0000 {signe(rec.get('gain_val'))} ±{f6(rec.get('se_gain_val'))}"
        if rec.get("n_train") is not None:
            ligne += f" N={rec['n_train']}"
        print(ligne)
        if rec.get("raison"):
            print(f"  raison : {rec['raison']}")
        n = len(base_lignes(d)) - 1
        print(f"  budget : {n} évaluées, {len(lister_variantes(etat))}/{cfg['plafond']} créées")

    # 1. le dossier de la variante ne contient que le programme et une meta.json intacte
    en_trop = [x.name for x in vdir.iterdir() if x.name not in (nom_prog(cfg), "meta.json", "__pycache__", ".DS_Store")]
    if en_trop:
        return conclure("fichier_en_trop", "fichiers ajoutés dans la variante : " + ", ".join(en_trop))
    try:
        meta_parent = json.loads((vdir / "meta.json").read_text())["parent"]
    except (OSError, ValueError, KeyError):
        meta_parent = None
    if meta_parent != parent["id"]:
        return conclure("hors_zone", f"meta.json modifiée (parent annoncé {meta_parent}, réel {parent['id']})")
    # 2. instantané : on évalue exactement les octets qui sont notés
    brut = (vdir / nom_prog(cfg)).read_bytes()
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError:
        return conclure("echec_rapide", "programme illisible en UTF-8")
    rec["sha_prog"] = hashlib.sha256(brut).hexdigest()
    instant = Path(tempfile.mkdtemp(prefix="gevolve-v-")) / nom_prog(cfg)
    instant.write_bytes(brut)
    try:
        ref_segs, _ = decouper(lire_texte(fichier_variante(d, cfg, "v0000")), est_python(cfg))
        try:
            segs, zones = decouper(texte, est_python(cfg))
        except ValueError as e:
            return conclure("hors_zone", f"balises EVOLVE abîmées : {e}")
        if segs != ref_segs:
            return conclure("hors_zone", "code modifié en dehors des blocs EVOLVE")
        deja = next((r["id"] for r in base if r.get("sha_prog") == rec["sha_prog"]), None)
        if deja:
            return conclure("identique", f"code identique à {deja}")
        if est_python(cfg) and cfg.get("verification_statique", True):
            fautes = controle_statique(texte, zones, cfg.get("imports_permis", IMPORTS_DEFAUT))
            if fautes:
                return conclure("interdit", " ; ".join(fautes))

        # 3. cascade
        r = lancer(d, cfg, instant, "rapide")
        if not r["ok"]:
            return conclure("echec_rapide", r.get("erreur"))
        if r["mode"] != mode:
            return conclure("echec_rapide", f"le juge a rendu un résultat de mode {r['mode']} au lieu de {mode}")
        if cfg.get("determinisme"):
            # 14/11 : seul v0000 était testé. Un programme qui trie par hash() ou tire au hasard change de
            # décisions d'un lancement à l'autre : son train et sa validation ne mesureraient pas le même programme.
            r2 = lancer(d, cfg, instant, "rapide")
            if not r2["ok"] or (r2.get("cas") if mode == "cas" else r2.get("score")) != (r.get("cas") if mode == "cas" else r.get("score")):
                return conclure("non_deterministe", "deux lancements sur « rapide » ne rendent pas les mêmes décisions "
                                "(hasard non semé, ordre d'un ensemble, horloge)")

        r = lancer(d, cfg, instant, "train")
        if not r["ok"]:
            return conclure("echec_train", r.get("erreur"))
        if mode == "cas":
            ag = agreger(r["cas"])
            rec["sha_res"]["train"] = resultats_ecrire(d, vid, "train", r["cas"])
            if ag is None:
                return conclure("aucun_cas", "le programme n'agit sur aucun cas du train")
            rec.update(train=ag["score"], n_train=ag["n"], ref_train=ag["ref"],
                       se_train=erreur_type(r["cas"], None, f"{vid}-train"))
            if cfg.get("n_min") and ag["n"] < cfg["n_min"]:
                return conclure("trop_peu", f"N={ag['n']} < n_min={cfg['n_min']}")
            # même comportement qu'une variante déjà notée (code différent, décisions identiques)
            jumeau = next((x["id"] for x in base if x.get("sha_res", {}).get("train") == rec["sha_res"]["train"]), None)
            if jumeau:
                return conclure("identique", f"comportement identique à {jumeau} sur tout le train (code différent)")
            # Base complète : on se mesure au dernier ancêtre gardé, pas au parent (qui peut être « neutre »).
            # Une simplification, elle, se mesure à son parent : elle doit faire aussi bien avec moins.
            ref_rec = parent if (not complete or cap == "simplifier") else reference_garde(parent, connus)
            if ref_rec["id"] != parent["id"]:
                rec["reference"] = ref_rec["id"]
            try:
                ref_cas = resultats_lire(d, ref_rec, "train")
                graine = f"{vid}-vs-parent" if ref_rec["id"] == parent["id"] else f"{vid}-vs-{ref_rec['id']}"
                diff, se = ecart_apparie(r["cas"], ref_cas, graine)
            except ValueError as e:
                return conclure("juge_incoherent", f"{e} : le juge rend des cas différents d'un appel à l'autre")
            rec.update(diff_parent=diff, se_diff_parent=se)
            if diff is None:
                return conclure("neutre" if complete else "rejete", f"aucun cas comparable avec {ref_rec['id']}")
            if math.isnan(se) or se <= 0:
                return conclure("marge_incalculable", f"gain {signe(diff)} mais marge d'erreur incalculable "
                                "(trop peu de jours) : on refuse plutôt que de garder du bruit")
            marge = cfg.get("marge_se", 1.0) * se
            gen = generalisation(r["cas"], ref_cas, cfg.get("generalisation"))
            if gen:
                rec["gen_train"] = gen
            if cap == "simplifier" and complete:
                cx_p = complexite(lire_texte(fichier_variante(d, cfg, parent["id"])),
                                  decouper(lire_texte(fichier_variante(d, cfg, parent["id"])), est_python(cfg))[1])
                cx_v = complexite(texte, zones)
                rec["complexite"] = [cx_p, cx_v]
                if cx_v is None or cx_p is None or cx_v >= cx_p:
                    return conclure("neutre", f"pas plus simple que {parent['id']} ({cx_v} ≥ {cx_p} comparaisons, "
                                    "conditions et constantes)")
                if diff <= -marge:
                    return conclure("neutre", f"plus simple ({cx_v} < {cx_p}) mais nettement moins bon que "
                                    f"{parent['id']} ({signe(diff)} ±{f6(se)}) : la condition retirée servait")
                statut_final = "simplifiee"
            elif diff < marge or (gen and not gen["ok"]):
                if complete:
                    # Base complète (AlphaEvolve garde tout) : point de départ possible, jamais validée ni championne.
                    pourquoi = (f"{signe(diff)} ±{f6(se)} vs {ref_rec['id']} : nettement moins bon" if diff <= -marge
                                else f"{signe(diff)} ±{f6(se)} vs {ref_rec['id']} : pas distinguable du bruit" if diff < marge
                                else f"gain {signe(diff)} ±{f6(se)} concentré ({texte_generalisation(gen)} familles "
                                     f"en gain, il en faut {cfg['generalisation'].get('part_min')})")
                    return conclure("neutre", pourquoi + " ; reste dans la base comme parent possible")
                if gen and not gen["ok"] and diff >= marge:
                    return conclure("rejete", f"gain {signe(diff)} concentré ({texte_generalisation(gen)} familles en gain)")
            else:
                statut_final = "garde"
            if not complete and diff < marge:
                # Retour en arrière façon AlphaEvolve : une idée d'une famille NOUVELLE, pas nettement pire
                # que son parent, est gardée comme point de départ (sans validation, jamais champion).
                if niche_neuve and diff > -marge:
                    return conclure("exploration", f"nouvelle famille, {signe(diff)} ±{f6(se)} vs parent : "
                                    "pas un progrès, mais gardée comme point de départ pour plus tard")
                if diff <= 0:
                    return conclure("rejete", f"moins bon que le parent ({signe(diff)} ±{f6(se)})")
                return conclure("rejete", f"gain sur le parent {signe(diff)} < {cfg.get('marge_se', 1.0)} × erreur "
                                          f"({f6(se)}) : pas distinguable du bruit")
        else:
            rec.update(train=r["score"], n_train=r.get("n"))
            if cfg.get("n_min") and (r.get("n") or 0) < cfg["n_min"]:
                return conclure("trop_peu", f"N={r.get('n')} < n_min={cfg['n_min']}")
            if r["score"] <= parent["train"]:
                if niche_neuve and r["score"] >= connus["v0000"]["train"]:
                    return conclure("exploration", f"nouvelle famille, train {f6(r['score'])} ≤ parent "
                                    f"{f6(parent['train'])} mais ≥ v0000 : gardée comme point de départ")
                return conclure("rejete", f"train {f6(r['score'])} ≤ parent {f6(parent['train'])}")

        r = lancer(d, cfg, instant, "validation")
        if not r["ok"]:
            return conclure("echec_validation", r.get("erreur"))
        if mode == "cas":
            ag = agreger(r["cas"])
            rec["sha_res"]["validation"] = resultats_ecrire(d, vid, "validation", r["cas"])
            if ag is None:
                return conclure("aucun_cas", "le programme n'agit sur aucun cas de la validation")
            rec.update(validation=ag["score"], n_val=ag["n"], ref_val=ag["ref"],
                       se_val=erreur_type(r["cas"], None, f"{vid}-validation"))
            try:
                g, s = ecart_apparie(r["cas"], resultats_lire(d, connus["v0000"], "validation"), f"{vid}-vs-v0000")
            except ValueError as e:
                return conclure("juge_incoherent", f"{e} : le juge rend des cas différents d'un appel à l'autre")
            rec.update(gain_val=g, se_gain_val=s)
            gv = generalisation(r["cas"], resultats_lire(d, connus["v0000"], "validation"), cfg.get("generalisation"))
            if gv:
                rec["gen_val"] = gv  # lu par resume() : une championne doit aussi gagner sur la plupart des familles
            if cfg.get("n_min_validation") and ag["n"] < cfg["n_min_validation"]:
                return conclure("trop_peu", f"validation N={ag['n']} < n_min_validation={cfg['n_min_validation']}")
        else:
            rec.update(validation=r["score"], n_val=r.get("n"))
        if sha_fichier(vdir / nom_prog(cfg)) != rec["sha_prog"]:
            return conclure("modifie_pendant", "le fichier de la variante a changé pendant l'évaluation")
        return conclure(statut_final)
    finally:
        shutil.rmtree(instant.parent, ignore_errors=True)


def cmd_voir(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    etat, base = controler(d, cfg, donnees=False)
    connus = {r["id"]: r for r in base}
    parent = etat.get("variantes", {}).get(a.variante)
    r = connus.get(a.variante)
    if r:
        print(f"{a.variante} {r['statut']} niche={r['niche']} — {r['idee']}" + (f" ({r['raison']})" if r.get("raison") else ""))
    if parent:
        avant = lire_texte(fichier_variante(d, cfg, parent)).splitlines(keepends=True)
        apres = lire_texte(fichier_variante(d, cfg, a.variante)).splitlines(keepends=True)
        sys.stdout.writelines(difflib.unified_diff(avant, apres, parent, a.variante))


CASSES = ("fichier_en_trop", "hors_zone", "echec_rapide", "interdit", "echec_train", "echec_validation", "non_deterministe",
          "aucun_cas", "juge_incoherent", "marge_incalculable", "modifie_pendant")


def issue(r: dict, marge_se: float) -> str:
    """Ce qui est arrivé à une variante, en une catégorie lisible (train seulement)."""
    st = r["statut"]
    if st in ("garde", "simplifiee"):
        return "progrès"
    if st == "identique":
        return "doublon"
    if st == "trop_peu":
        return "trop peu d'achats"
    if st == "exploration":
        return "exploration"
    if st in CASSES:
        return "cassée"
    if (r.get("raison") or "").startswith("pas plus simple"):
        return "pas plus simple"
    dfp, se = r.get("diff_parent"), r.get("se_diff_parent")
    if dfp is not None and se and not math.isnan(se):
        m = marge_se * se
        if dfp <= -m:
            return "pire"
        if dfp >= m and r.get("gen_train") and not r["gen_train"].get("ok", True):
            return "concentrée"
    return "bruit"


def analyse(evalues: list[dict], cfg: dict) -> list[str]:
    """Ce qui marche et ce qui rate, en chiffres (train seulement) : issue de chaque variante, rapport
    signal/bruit des retouches, ce que vaut chaque condition retirée par une simplification, familles
    épuisées et familles à creuser. Sert à écrire LECONS.md et à choisir les CAP de la génération suivante."""
    ms = float(cfg.get("marge_se", 1.0))
    out = []
    comptes: dict[str, int] = {}
    for r in evalues:
        k = issue(r, ms)
        comptes[k] = comptes.get(k, 0) + 1
    ordre = ["progrès", "bruit", "pire", "concentrée", "trop peu d'achats", "doublon", "pas plus simple", "exploration", "cassée"]
    out.append("issues : " + " · ".join(f"{k} {comptes[k]}" for k in ordre if k in comptes))
    mesures = [(abs(r["diff_parent"]), r["se_diff_parent"]) for r in evalues
               if r.get("diff_parent") is not None and r.get("se_diff_parent") and not math.isnan(r["se_diff_parent"])
               and r.get("cap") != "simplifier"]
    if len(mesures) >= 3:
        de, se = statistics.median(x for x, _ in mesures), statistics.median(s for _, s in mesures)
        rap = de / se if se else math.inf
        out.append(f"signal/bruit des retouches : écart médian |Δ| {f6(de)} contre marge médiane {f6(se)} → {rap:.2f}"
                   + (" : la plupart des retouches sont plus petites que la marge, le juge ne peut pas les départager. "
                      "Privilégier simplifier, famille et retour ; raffiner un seuil ne se verra pas."
                      if rap < 1 else " : les retouches sont en général visibles par le juge."))
    simples = [r for r in evalues if r.get("cap") == "simplifier" and r.get("diff_parent") is not None]
    for r in simples:
        cx = r.get("complexite") or [None, None]
        out.append(f"condition retirée par {r['id']} (de {r['parent']}, complexité {cx[0]}→{cx[1]}) : "
                   f"{signe(r['diff_parent'])} ±{f6(r.get('se_diff_parent'))} → elle rapportait {signe(-r['diff_parent'])}"
                   + (" (rien de visible : à retirer)" if r["statut"] == "simplifiee" else ""))
    fam: dict[str, list[dict]] = {}
    for r in evalues:
        fam.setdefault(r["niche"], []).append(r)
    epuisees, creuser = [], []
    for niche, rs in fam.items():
        prog = [r for r in rs if issue(r, ms) == "progrès"]
        z = [r["diff_parent"] / r["se_diff_parent"] for r in rs if r.get("diff_parent") is not None
             and r.get("se_diff_parent") and not math.isnan(r["se_diff_parent"])]
        if len(rs) >= 3 and not prog and (not z or max(z) < ms):
            epuisees.append(f"{niche} ({len(rs)} essais, meilleur {max(z):.1f} marge)" if z else f"{niche} ({len(rs)} essais)")
        prom = [r["id"] for r in rs if r["statut"] in ("neutre", "exploration") and r.get("diff_parent") is not None
                and r.get("se_diff_parent") and 0.5 * ms * r["se_diff_parent"] <= r["diff_parent"]
                and (not r.get("gen_train") or r["gen_train"].get("ok", True))]
        if prom:
            creuser.append(f"{niche} : {', '.join(prom)}")
    if epuisees:
        out.append("familles épuisées (≥ 3 essais, aucun progrès, jamais au-delà de la marge) : " + " ; ".join(epuisees))
    if creuser:
        out.append("familles à creuser (gain d'au moins une demi-marge, réparti, pas encore prouvé) : " + " ; ".join(creuser))
    return out


def cmd_lecons(a):
    """Matière brute du carnet de leçons (LECONS.md), TRAIN SEULEMENT : par famille d'idées, ce qui a
    été essayé, contre qui, avec quel écart. Claude en tire LECONS.md, que les mutateurs lisent."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    with verrou_fichier(d):
        etat, base = controler(d, cfg, donnees=False)
        evalues = [r for r in base if r["id"] != "v0000"]
        etat["lecons_n"] = len(evalues)
        etat_ecrire(cfg, etat, d)
    print(f"MATIÈRE POUR LECONS.md — {len(evalues)} variantes, train seulement. N'y ajouter AUCUN chiffre de "
          "validation ni de test : les mutateurs le liront.")
    if evalues:
        print("ANALYSE (train seulement) :")
        for l in analyse(evalues, cfg):
            print("  " + l)
    if pistes_on(cfg):
        print("PISTES (train seulement) — dire dans LECONS.md, pour chacune, ce qu'elle a appris ; une piste épuisée se "
              "ferme avec sa raison, et la suivante part de cette raison :")
        for nom, x in etat_pistes(etat, cfg, base).items():
            if x["statut"] == "hors_juge":
                continue
            ecarts = [r["diff_parent"] for r in base if r.get("piste") == nom and r.get("diff_parent") is not None]
            print(f"  {nom} [{'fermée' if x['statut'] == 'fermee' else 'épuisée' if x['epuisee'] else 'active'}] "
                  f"{x['evaluees']} essai(s), {x['gardees']} gardé(s), {x['serie']} de suite sans progrès"
                  + (f", meilleur écart train {signe(max(ecarts))}" if ecarts else "")
                  + f" — réfutée si : {x.get('refute')}" + (f" — fermée : {x.get('raison')}" if x.get("raison") else ""))
    familles: dict[str, list[dict]] = {}
    for r in evalues:
        familles.setdefault(r["niche"], []).append(r)
    for niche, rs in sorted(familles.items(), key=lambda t: -len(t[1])):
        st: dict[str, int] = {}
        for r in rs:
            st[r["statut"]] = st.get(r["statut"], 0) + 1
        ecarts = [r["diff_parent"] for r in rs if r.get("diff_parent") is not None]
        print(f"  {niche} : {len(rs)} essai(s) — " + ", ".join(f"{k} {v}" for k, v in sorted(st.items()))
              + (f" — meilleur écart train {signe(max(ecarts))}" if ecarts else ""))
        for r in rs:
            raison = r.get("raison") or ""
            raison = "" if "validation" in raison else raison[:110]
            print(f"    {r['id']} {r['statut']:<11} cap={r.get('cap') or 'libre':<10} "
                  + (f"{signe(r.get('diff_parent'))} ±{f6(r.get('se_diff_parent'))} vs {r.get('reference', r['parent'])}"
                     if r.get("diff_parent") is not None else "pas d'écart mesuré")
                  + (f" · familles {texte_generalisation(r['gen_train'])}" if r.get("gen_train") else "")
                  + f" — {r['idee'][:100]}" + (f" [{raison}]" if raison and r["statut"] != "garde" else ""))
    reg = d / "patrons.jsonl"
    n_reg = len([l for l in reg.read_text(encoding="utf-8").splitlines() if l.strip()]) if reg.exists() else 0
    if etat["mode"] == "cas":
        print(f"PATRONS : {n_reg} analyse(s) faite(s). Lancer `gevolve.py patrons {d}` pour chercher pourquoi le meilleur "
              "gagne et perd (toutes les variables, train seulement), puis reporter patrons, exceptions et bruit dans LECONS.md.")
    print("À ÉCRIRE dans LECONS.md (court) : ce qui marche, ce qui rate et pourquoi, les familles épuisées, "
          "ce qu'il reste à essayer. Puis le citer dans les briefs de la génération suivante, et choisir les CAP "
          "d'après l'ANALYSE. Un écart sous la marge s'écrit « indistinguable du bruit », jamais comme une explication.")


def params_patrons(cfg: dict) -> dict:
    return dict(PATRONS_DEFAUT, **(cfg.get("patrons") or {}))


def cmd_patrons(a):
    """Recherche de patrons dans les trades d'une variante, TRAIN SEULEMENT (par défaut le meilleur
    sur le train : un patron déjà neutralisé par un de ses filtres ne remonte pas). Enregistre chaque
    analyse dans patrons.jsonl (registre : les pistes rejetées ne reviennent pas, et chaque analyse
    réduit le budget d'erreur des suivantes). Avec --calibrer N : taux de fausses alertes sur des
    P&L mélangés, et un patron injecté qui doit être retrouvé."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    etat, base = controler(d, cfg, donnees=False)
    if etat["mode"] != "cas":
        erreur("recherche de patrons : le juge doit rendre des cas ({\"cas\": [...]}), pas un score global")
    p = params_patrons(cfg)
    connus = {r["id"]: r for r in base}
    if a.variante:
        if a.variante not in connus:
            erreur(f"{a.variante} inconnue ou pas encore évaluée")
        rec = connus[a.variante]
    else:
        rec = max((r for r in base if r["statut"] in GARDES and r.get("train") is not None), key=lambda r: r["train"])
    cas = resultats_lire(d, rec, "train")
    if not any(c.get("variables") or c.get("instant") for c in cas):
        print("ATTENTION : aucun cas ne porte « variables » ni « instant » : seuls le jour et les segments sont "
              "explorés. Le juge doit écrire les variables de l'entrée (voir assets/evaluate.py, variables_du_cas).")
    if p.get("plancher") is None:
        print("ATTENTION : patrons.plancher n'est pas fixé dans config.json : aucun gain minimal par trade n'est exigé.")
    if a.calibrer:
        cal = calibrer_patrons(cas, p, a.calibrer, f"{cfg['id']}-{rec['id']}")
        print(f"CALIBRATION {rec['id']} (train) : {cal['fausses_alertes']}/{cal['tours']} tours sur P&L mélangés ont sorti "
              f"un patron ({cal['taux']:.0%}, attendu ≤ 5 %) ; patron injecté retrouvé : {'oui' if cal['injecte_retrouve'] else 'NON'}")
        if cal["taux"] > 0.10:
            print("  → trop de fausses alertes : ne pas transmettre de patron aux mutateurs sur cette évolution.")
        if not cal["injecte_retrouve"]:
            print("  → l'outil n'a pas la puissance de voir un effet d'une demi-déviation sur un tiers des trades : "
                  "un « rien trouvé » ne prouve pas l'absence de patron.")
        return
    reg = d / "patrons.jsonl"
    avant = [json.loads(l) for l in reg.read_text(encoding="utf-8").splitlines() if l.strip()] if reg.exists() else []
    rejetes = {(c["variable"], c["case"]) for x in avant for c in x.get("candidats", []) if c["statut"] != "patron"}
    r = chercher_patrons(cas, p, len(avant), f"{cfg['id']}-{rec['id']}-{len(avant)}")
    print(f"PATRONS {rec['id']} (train seulement, {r['n']} trades) — analyse n° {len(avant) + 1}")
    if r["etat"] != "fait":
        print("  " + r["etat"] + ". Rien n'est transmis aux mutateurs.")
        return
    print(f"  {r['n_variables']} variables dérivées, {r['n_cases']} cases testées ; barre de découverte maxT "
          f"|t| > {r['barre']:.2f} (95e centile du meilleur hasard) ; {r['n_decouverte']} case(s) au-dessus, "
          f"{len(r['candidats'])} candidat(s) retenu(s) (un par variable)")
    for c in r["candidats"]:
        if (c["variable"], c["case"]) in rejetes and c["statut"] == "patron":
            c["statut"], c["raison"] = "bruit", "déjà rejeté par une analyse précédente : ne revient pas"
        conf = (f" ; confirmation {c['effet_confirmation']:+.3g} (t {c['t_confirmation']:+.2f}, N {c['n_confirmation']})"
                if "effet_confirmation" in c else "")
        print(f"  [{c['statut'].upper()}] {c['case']} : P&L {c['sens']} — découverte {c['effet_decouverte']:+.3g} "
              f"(t {c['t_decouverte']:+.2f}, N {c['n_decouverte']}){conf} ; mois dans le sens {c['mois_dans_le_sens']}"
              + (f" ; règle sur tout le train {c['gain_par_trade']:+.3g} par trade, {c['part_trades_gardes']:.0%} des trades gardés"
                 if "gain_par_trade" in c else "")
              + (f" — {c['raison']}" if c.get("raison") else ""))
    confirmes = [c for c in r["candidats"] if c["statut"] == "patron"]
    with verrou_fichier(d):
        with reg.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"date": maintenant(), "variante": rec["id"], "n": r["n"], "barre": r["barre"],
                                "n_cases": r["n_cases"], "candidats": r["candidats"]}, ensure_ascii=False) + "\n")
        e2 = etat_lire(cfg)
        e2["patrons"] = [{"variable": c["variable"], "texte": texte_patron(c)} for c in confirmes]
        etat_ecrire(cfg, e2, d)
    if confirmes:
        print("HYPOTHÈSES POUR LES MUTATEURS (CAP patron, variable + direction, aucun seuil ni trade) :")
        for c in confirmes:
            print("  - " + texte_patron(c))
        print("  À recopier dans LECONS.md (section « patrons »). Les exceptions et le bruit y vont aussi, "
              "comme pistes fermées.")
    else:
        print("Aucun patron confirmé. Noter les pistes fermées dans LECONS.md ; ne pas les retenter à la main.")


def cmd_piste(a):
    """Registre des hypothèses. Une piste = un mécanisme nommé et le chiffre qui le réfuterait.
    Ouvrir une piste coûte : elle relève la barre du champion (z_champion) et il n'y en a que pistes.max.
    Fermer une piste demande une raison : c'est d'elle que part la piste suivante (--depuis).
    --hors-juge : l'hypothèse demande une donnée que l'entrée du programme n'a pas. Le juge est figé,
    elle est donc seulement notée pour une prochaine évolution, sans rien coûter à celle-ci."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    with verrou_fichier(d):
        etat, base = controler(d, cfg, donnees=False)
        if not pistes_on(cfg):
            erreur("cette évolution n'a pas de registre de pistes (clé « pistes » de config.json, mise par `init` depuis le 14/11)")
        pistes = etat.setdefault("pistes", {})
        if a.action == "liste":
            ep = etat_pistes(etat, cfg, base)
            print(f"PISTES — {n_pistes_comptees(etat)}/{params_pistes(cfg)['max']} ont eu droit au juge ; barre du champion : "
                  f"{z_champion(etat, cfg):.2f} marge(s)")
            for nom, x in ep.items():
                et = {"fermee": "fermée", "hors_juge": "hors juge"}.get(x["statut"], "épuisée" if x["epuisee"] else "active")
                print(f"  {nom} [{et}] {x['n']} variante(s), {x['gardees']} gardée(s), {x['serie']} de suite sans progrès"
                      + (f", depuis {x['depuis']}" if x.get("depuis") else "") + f"\n    mécanisme : {x['mecanisme']}"
                      + (f"\n    réfutée si : {x['refute']}" if x.get("refute") else "")
                      + (f"\n    donnée qui manque : {x['hors_juge']}" if x.get("hors_juge") else "")
                      + (f"\n    fermée : {x['raison']}" if x.get("raison") else ""))
            if not ep:
                print("  aucune piste encore : en ouvrir deux à quatre, tirées de RECHERCHE.md et de la fiche")
            return
        scelle_lu(etat)
        nom = nom_piste(a.nom)
        if not nom:
            erreur("nom de piste manquant (lettres, chiffres, tirets)")
        connus = {r["id"]: r for r in base}
        if a.action == "ouvrir":
            if nom in pistes:
                erreur(f"piste « {nom} » déjà {pistes[nom]['statut']} : une piste fermée ne se rouvre pas, en ouvrir une autre avec --depuis {nom}")
            if not (a.mecanisme or "").strip():
                erreur("--mecanisme \"d'où viendrait l'avantage, en une phrase testable\" est obligatoire")
            if a.depuis and nom_piste(a.depuis) not in pistes:
                erreur(f"--depuis {a.depuis} : piste inconnue")
            x = {"statut": "ouverte", "mecanisme": a.mecanisme.strip(), "refute": (a.refute or "").strip() or None,
                 "ouverte_le": maintenant(), "depuis": nom_piste(a.depuis) if a.depuis else None, "depart": None}
            if a.hors_juge:
                x.update(statut="hors_juge", hors_juge=a.hors_juge.strip())
            else:
                if not x["refute"]:
                    erreur("--refute \"le chiffre, mesuré comment, qui réfuterait cette piste\" est obligatoire : "
                           "une hypothèse qu'aucun résultat ne peut contredire ne se teste pas")
                kmax = int(params_pistes(cfg)["max"])
                if n_pistes_comptees(etat) >= kmax:
                    erreur(f"{kmax} pistes ont déjà eu droit au juge (pistes.max, figé au verrou) : chaque piste de plus "
                           "est une chance de plus de trouver du hasard. Noter celle-ci avec --hors-juge, ou sceller.")
                if a.depart:
                    if a.depart not in connus or connus[a.depart]["statut"] not in PARENTABLES:
                        erreur(f"--depart {a.depart} : variante inconnue ou non parentable")
                    x["depart"] = a.depart
            pistes[nom] = x
        else:  # fermer
            if nom not in pistes or pistes[nom]["statut"] != "ouverte":
                erreur(f"piste « {nom} » inconnue ou déjà fermée")
            if not (a.raison or "").strip():
                erreur("--raison \"ce que la piste a montré, en chiffres du train\" est obligatoire : c'est la leçon")
            pistes[nom].update(statut="fermee", raison=a.raison.strip(), fermee_le=maintenant())
        etat_ecrire(cfg, etat, d)
        with (d / "pistes.jsonl").open("a", encoding="utf-8") as f:  # journal lisible ; l'état fait foi
            f.write(json.dumps(dict(pistes[nom], nom=nom, action=a.action, date=maintenant()), ensure_ascii=False) + "\n")
    x = pistes[nom]
    if x["statut"] == "hors_juge":
        print(f"PISTE {nom} notée HORS JUGE (donnée qui manque : {x['hors_juge']}) : elle ne coûte rien à cette évolution "
              "et attend la prochaine, dont l'entrée du programme l'aura.")
    elif a.action == "ouvrir":
        print(f"PISTE {nom} ouverte ({n_pistes_comptees(etat)}/{params_pistes(cfg)['max']}) — barre du champion : "
              f"{z_champion(etat, cfg):.2f} marge(s) d'erreur en validation")
    else:
        print(f"PISTE {nom} fermée : {x['raison']}. La recopier dans LECONS.md ; si elle ouvre une idée, "
              f"`piste ouvrir <nom> --depuis {nom}`.")


def aplatir(x, prefixe: str = "") -> dict:
    """{"a": {"b": [1, 2]}} → {"a.b[0]": 1, "a.b[1]": 2} : pour comparer deux entrées champ par champ."""
    out: dict = {}
    if isinstance(x, dict):
        for k, v in x.items():
            out.update(aplatir(v, f"{prefixe}.{k}" if prefixe else str(k)))
        if not x:
            out[prefixe] = {}
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out.update(aplatir(v, f"{prefixe}[{i}]"))
        if not x:
            out[prefixe] = []
    else:
        out[prefixe] = x
    return out


def egal(a, b, tol: float) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    return a == b


def cmd_temoin(a):
    """Relevé témoin : ce que le programme aurait vu EN DIRECT (capturé aux vrais instants de décision)
    doit être identique à ce que le juge reconstruit après coup avec les données historiques. Un écart
    trahit une fuite (champ daté à son début, cote publiée plus tard), une révision des données ou une
    jointure fausse : les verrous protègent le juge contre le programme, pas contre un juge mal nourri."""
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    if cfg.get("verrou"):
        erreur("le relevé témoin se fait AVANT le verrou : son résultat est figé avec le juge")
    cap = Path(a.capture).expanduser().resolve()
    try:
        rel = cap.relative_to(d)
    except ValueError:
        erreur("le fichier capturé doit être dans le dossier de l'évolution : il sera figé au verrou")
    if not cap.is_file():
        erreur(f"{rel} introuvable")
    direct: dict = {}
    for i, l in enumerate(cap.read_text(encoding="utf-8").splitlines(), 1):
        if not l.strip():
            continue
        try:
            x = json.loads(l)
            direct[str(x["id"])] = x["entree"]
        except (ValueError, KeyError, TypeError) as e:
            erreur(f"{rel} ligne {i} : il faut une ligne JSON {{\"id\": …, \"entree\": …}} ({e})")
    if not direct:
        erreur("relevé témoin vide")
    r = lancer(d, cfg, d / cfg["programme"], "temoin", temoin=cap)
    if not r["ok"]:
        erreur(f"le juge n'a pas reconstruit les entrées : {r.get('erreur')} (split « temoin », voir le gabarit evaluate.py)")
    if r.get("mode") != "temoin":
        erreur("le juge doit répondre au split « temoin » par {\"temoin\": [{\"id\": …, \"entree\": …}, …]}")
    hist = {c["id"]: c["entree"] for c in r["cas"]}
    absents = sorted(set(direct) - set(hist))
    ecarts: dict[str, int] = {}
    exemples, identiques = [], 0
    for cid in sorted(set(direct) & set(hist)):
        fa, fb = aplatir(direct[cid]), aplatir(hist[cid])
        diff = [k for k in sorted(set(fa) | set(fb)) if k not in fa or k not in fb or not egal(fa[k], fb[k], a.tolerance)]
        if not diff:
            identiques += 1
            continue
        for k in diff:
            ecarts[k] = ecarts.get(k, 0) + 1
            if len(exemples) < 12:
                exemples.append({"id": cid, "champ": k, "direct": fa.get(k, "absent"), "historique": fb.get(k, "absent")})
    ok = not absents and not ecarts
    out = {"date": maintenant(), "capture": str(rel), "sha_capture": sha_fichier(cap), "tolerance": a.tolerance,
           "n": len(direct), "identiques": identiques, "absents": len(absents), "ids_absents": absents[:20],
           "ecarts": ecarts, "exemples": exemples, "ok": ok, "accepte": (a.accepter if a.accepter and not ok else None)}
    (d / "temoin.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"RELEVÉ TÉMOIN : {identiques}/{len(direct)} entrées identiques, {len(absents)} absentes de la reconstruction")
    for k, n in sorted(ecarts.items(), key=lambda t: -t[1])[:10]:
        ex = next(e for e in exemples if e["champ"] == k) if any(e["champ"] == k for e in exemples) else None
        print(f"  {k} : {n} écart(s)" + (f" — ex. {ex['id']} : direct {ex['direct']!r}, historique {ex['historique']!r}" if ex else ""))
    if absents:
        print("  absents : " + ", ".join(absents[:8]))
    if len(direct) < 10:
        print("  AVERTISSEMENT : moins de 10 instants : un champ qui ne fuit qu'à certaines heures peut passer inaperçu.")
    if ok:
        print("TEMOIN=ok : ce que voit le juge correspond à ce qu'on voyait en direct.")
    elif out["accepte"]:
        print(f"TEMOIN=accepte (écarts consignés, raison : {out['accepte']})")
    else:
        print("TEMOIN=ecarts : corriger le juge (ou --accepter \"raison\" si l'écart est compris), puis relancer.")


def cmd_tableau(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    etat, base = controler(d, cfg, donnees=False)
    mode = etat["mode"]
    s = resume(etat, cfg, base, mode)
    top = sorted(s["gardes"], key=lambda r: r["train"], reverse=True)[: a.n]
    print(f"Évolution « {cfg['nom']} » — {d}")
    if mode == "cas":
        print(f"  {'id':<6} {'niche':<16} {'train':>10} {'±':>8} {'gain valid.':>12} {'±':>8} {'N':>6}  idée")
        for r in top:
            print(f"  {r['id']:<6} {r['niche'][:16]:<16} {f6(r['train']):>10} {f6(r.get('se_train')):>8} "
                  f"{signe(0.0 if r['id'] == 'v0000' else r.get('gain_val')):>12} {f6(r.get('se_gain_val')):>8} "
                  f"{str(r.get('n_train') or '—'):>6}  {r['idee'][:60]}")
    else:
        print(f"  {'id':<6} {'niche':<16} {'train':>10} {'valid.':>10} {'N':>6}  idée   (sans marge d'erreur)")
        for r in top:
            print(f"  {r['id']:<6} {r['niche'][:16]:<16} {f6(r['train']):>10} {f6(r.get('validation')):>10} "
                  f"{str(r.get('n_train') or '—'):>6}  {r['idee'][:60]}")
    stats: dict[str, int] = {}
    for r in s["evalues"]:
        stats[r["statut"]] = stats.get(r["statut"], 0) + 1
    print("  statuts : " + (", ".join(f"{k} {v}" for k, v in sorted(stats.items())) or "aucune variante encore"))
    caps: dict[str, list[int]] = {}
    for r in s["evalues"]:
        c = caps.setdefault(r.get("cap") or "libre", [0, 0, 0])
        c[0] += 1
        c[1] += r["statut"] in ("garde", "simplifiee")
        c[2] += r["statut"] in ("exploration", "neutre")
    if caps:
        print("  par cap (essayées / gardées / explorations) : "
              + ", ".join(f"{k} {v[0]}/{v[1]}/{v[2]}" for k, v in sorted(caps.items())))
    explo = [r for r in base if r["statut"] == "exploration"]
    if explo:
        print("  points de départ en réserve : " + ", ".join(f"{r['id']} ({r['niche']})" for r in explo[-6:]))
    neutres = [r for r in base if r["statut"] == "neutre"]
    if neutres:
        print(f"  base complète : {len(neutres)} variante(s) neutre(s), parents possibles, jamais championnes")
    # « Validée » = même règle que resume() (borne > 0, familles en validation) : elle remplace son parent.
    # Les autres ont seulement passé le train (plus simples, pas nettement moins bonnes que leur parent).
    simples = [r for r in base if r["statut"] == "simplifiee"]
    ok = set(s.get("simplifiees_validees") or [])
    validees = [r for r in simples if r["id"] in ok]
    refusees = [r for r in simples if r["id"] not in ok]
    if validees:
        print("  simplifications validées : " + ", ".join(f"{r['id']} (de {r['parent']})" for r in validees))
    if refusees:
        print("  simplifiées sur le train, refusées en validation : "
              + ", ".join(f"{r['id']} (de {r['parent']})" for r in refusees))
    if pistes_on(cfg):
        print(f"  pistes ({n_pistes_comptees(etat)}/{params_pistes(cfg)['max']} ont eu droit au juge ; barre du champion "
              f"{Z_CHAMPION:.2f} marge(s)) :")
        for nom, x in s["pistes"].items():
            et = {"fermee": "fermée", "hors_juge": "hors juge"}.get(x["statut"], "épuisée" if x["epuisee"] else "active")
            print(f"    {nom:<22} {et:<9} {x['n']} variante(s), {x['gardees']} gardée(s)"
                  + (f", meilleur train {f6(x['meilleur_train'])}" if x.get("meilleur_train") is not None else "")
                  + (f" — {x['raison'][:70]}" if x.get("raison") else "")
                  + (f" — manque : {x['hors_juge'][:60]}" if x.get("hors_juge") else ""))
    if etat.get("scelle"):
        sp = d / "scelle.json"
        sc = json.loads(sp.read_text()) if sp.exists() else {"date": etat["scelle"], "variante": "?", "verdict": "inconnu"}
        print(f"  évolution close le {sc['date']} ({sc.get('variante')}) : verdict {sc['verdict']}")
    print(f"EVOLUTION={cfg['nom']}")
    print(f"VARIANTES={len(s['variantes'])}/{cfg['plafond']} EVALUEES={len(s['evalues'])} "
          f"ORPHELINES={','.join(s['orphelines']) or 'aucune'}")
    c = s["champion"]
    if c and mode == "cas":
        print(f"CHAMPION={c['id']} GAIN_VALIDATION={signe(0.0 if c['id'] == 'v0000' else c.get('gain_val'))} "
              f"±{f6(c.get('se_gain_val'))} BORNE={signe(borne(c, mode))}")
    elif c:
        print(f"CHAMPION={c['id']} VALIDATION={f6(c.get('validation'))}")
    if s.get("grille"):
        print("VOIE=grille (pas de génération : v0000, le meilleur du benchmark, va seul au test scellé)")
    elif not c or c["id"] == "v0000":
        print("AUCUN_CHAMPION=oui (aucune variante ne bat v0000 en validation au-delà de sa marge : "
              "`scelle` close l'évolution SANS ouvrir le test, qui reste vierge)")
    if s["fin"]:
        print(f"FIN=oui ({s['fin']})")
    elif etat.get("scelle"):
        # 14/11 : après un `scelle --force`, FIN restait « non » et une condition /goal ne se remplissait jamais
        print("FIN=oui (évolution close par le test scellé)")
    else:
        print("FIN=non (" + (s["attente"] or f"budget restant {cfg['plafond'] - len(s['variantes'])}") + ")")


def cmd_scelle(a):
    d = ouvrir(a.dossier)
    cfg = cfg_lire(d)
    with verrou_fichier(d):
        etat, base = controler(d, cfg, donnees=True)
        scelle_lu(etat)
        mode = etat["mode"]
        s = resume(etat, cfg, base, mode)
        if not s["fin"] and not a.force:
            erreur("la boucle n'est pas finie (FIN=non) : le test ne s'ouvre qu'à la fin. "
                   "Pour l'ouvrir quand même, --force \"raison\" (consigné dans scelle.json).", 3)
        connus = {r["id"]: r for r in base}
        grille = bool(s.get("grille"))
        if grille and a.variante not in (None, "v0000"):
            erreur("voie grille : seul v0000 (le meilleur du benchmark) va au test")
        if a.variante == "v0000" and not grille:
            erreur("v0000 est la référence : on n'ouvre pas le test pour la comparer à elle-même")
        vid = "v0000" if grille else (a.variante or (s["champion"] and s["champion"]["id"]))
        if not grille and not a.variante and (not vid or vid == "v0000"):
            out = {"date": maintenant(), "variante": None, "verdict": "aucun_champion", "test_ouvert": False,
                   "variantes_evaluees": len(s["evalues"]), "force": a.force}
            (d / "scelle.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
            etat["scelle"] = out["date"]
            etat_ecrire(cfg, etat, d)
            print(f"AUCUN CHAMPION après {len(s['evalues'])} variantes : aucune ne bat v0000 en validation au-delà "
                  "de sa marge. L'évolution est close SANS ouvrir le test : il reste vierge pour une prochaine évolution.")
            print("VERDICT=aucun_champion")
            return
        if not vid or vid not in connus or connus[vid]["statut"] not in GARDES:
            erreur(f"variante {vid} inconnue ou non validée (une exploration n'a pas de validation)")
        verifier_programme(d, cfg, connus[vid])
        verifier_programme(d, cfg, connus["v0000"])
        # Le test est-il mûr ? On compte AVANT de poser la marque : un test à venir encore vide
        # ne doit pas brûler l'unique ouverture.
        sd = lancer(d, cfg, fichier_variante(d, cfg, "v0000"), "test", sonde=True)
        if sd["ok"] and sd.get("mode") == "sonde":
            jmin = (cfg.get("succes_test") or {}).get("jours_min")
            if sd["n"] <= 0:
                erreur("le split test est encore vide : rien n'a été scellé, réessayer quand les données seront là")
            if jmin and (sd.get("jours") or 0) < jmin:
                erreur(f"test pas encore mûr : {sd.get('jours')} jours sur {jmin} inscrits au verrou. Rien n'a été scellé.")
        # Marque posée AVANT de lancer : un plantage pendant le test laisse l'évolution close,
        # on ne peut donc pas relancer le test jusqu'à ce qu'il plaise.
        debut = maintenant()
        (d / "scelle.json").write_text(json.dumps({"date": debut, "variante": vid, "verdict": "interrompu",
                                                    "force": a.force}, ensure_ascii=False) + "\n")
        etat["scelle"] = debut
        etat_ecrire(cfg, etat, d)
        r = lancer(d, cfg, fichier_variante(d, cfg, vid), "test", scelle=True)
        r0 = r if grille else lancer(d, cfg, fichier_variante(d, cfg, "v0000"), "test", scelle=True)
        if not (r["ok"] and r0["ok"]):
            # échec propre, aucun score lu ni affiché : on retire la marque
            etat["scelle"] = None
            etat_ecrire(cfg, etat, d)
            (d / "scelle.json").unlink(missing_ok=True)
            erreur(f"le test n'a pas pu tourner : {r.get('erreur') or r0.get('erreur')} (aucun score lu, rien n'a été scellé)")
        st = cfg["succes_test"]
        out = {"date": debut, "variante": vid, "force": a.force, "succes_test": st, "test_ouvert": True,
               "variantes_evaluees": len(s["evalues"])}
        if mode == "cas":
            ag, ag0 = agreger(r["cas"]), agreger(r0["cas"])
            se = erreur_type(r["cas"], None, f"{vid}-test")
            diff, se_d = ecart_apparie(r["cas"], r0["cas"], f"{vid}-test-vs-v0000")
            z, seuil = float(st.get("z", 1.645)), float(st.get("seuil", 0.0))
            ok_abs = ag is not None and not math.isnan(se) and ag["score"] - z * se > seuil
            if ok_abs and st.get("moyenne_min") is not None:  # seuil sur la moyenne elle-même, en plus de la borne
                ok_abs = ag["score"] > float(st["moyenne_min"])
            rend = rendement_cumule(r["cas"])
            out["rendement_cumule"] = rend
            if st.get("rendement_min") is not None:  # Σ gain ÷ Σ mise ≥ seuil (le juge écrit « mise » par cas)
                ok_abs = ok_abs and rend is not None and rend >= float(st["rendement_min"])
            if UNIV is not None and st.get("par_univers"):
                # verdict univers par univers : chaque univers présent au test doit passer seul
                pu = stats_par_univers(r["cas"], f"{vid}-test-u")
                out["par_univers"] = {u: {"moyenne": m, "se": e, "n": n, "jours": nj} for u, (m, e, n, nj) in pu.items()}
                mm = float(st.get("moyenne_min", -math.inf))
                ok_abs = bool(pu) and all(m is not None and not math.isnan(e) and m > mm and m - z * e > seuil
                                          for m, e, n, nj in pu.values())
                for u, (m, e, n, nj) in pu.items():
                    print(f"  univers {u} : moyenne={f6(m)} ±{f6(e)} N={n} jours={nj}"
                          + ("" if m is None or math.isnan(e) else f" (IC95 {f6(m - 1.96 * e)} à {f6(m + 1.96 * e)})"))
            ok_init = grille or (not st.get("battre_initial", True)) or (
                vid != "v0000" and diff is not None and not math.isnan(se_d) and diff - z * se_d > 0)
            out.update(test=ag and ag["score"], n_test=ag and ag["n"], ref_test=ag and ag["ref"], se_test=se,
                       v0000_test=ag0 and ag0["score"], gain_test=diff, se_gain_test=se_d,
                       verdict="réussi" if ok_abs and ok_init else "échec")
            if st.get("n_min") is not None and (not ag or ag["n"] < int(st["n_min"])):
                out["verdict"] = "insuffisant"  # trop peu de trades au test : ni réussite ni échec, suite en paper
            ligne = (f"TEST SCELLÉ — {vid} : score={f6(out['test'])} ±{f6(se)} N={out['n_test']} "
                     + (f"rendement cumulé={rend:+.2%} " if rend is not None else "")
                     + 
                     f"(intervalle {f6(out['test'] - 1.96 * se) if ag else '—'} à {f6(out['test'] + 1.96 * se) if ag else '—'})"
                     + (" | voie grille : v0000 seul, contre le seuil inscrit" if grille
                        else f" | gain sur v0000 {signe(diff)} ±{f6(se_d)}"))
            if grille:
                out["voie"] = "grille"
        else:
            seuil = float(st.get("seuil", 0.0))
            ok_init = grille or (not st.get("battre_initial", True)) or r["score"] > r0["score"]
            out.update(test=r["score"], n_test=r.get("n"), v0000_test=r0["score"],
                       verdict="réussi" if r["score"] > seuil and ok_init else "échec")
            ligne = f"TEST SCELLÉ — {vid} : score={f6(r['score'])} N={r.get('n')} | v0000 : {f6(r0['score'])}"
        (d / "scelle.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(ligne)
    print(f"VERDICT={out['verdict']} (seuil inscrit avant la première génération : {json.dumps(st)})"
          + (f" — ouverture forcée : {a.force}" if a.force else ""))
    if s.get("grille"):
        print("Voie grille : v0000 est le meilleur d'un benchmark noté sur le train ; ce test, ouvert une fois, dit ce "
              "qu'il vaut. L'évolution est maintenant close.")
    else:
        print(f"Le champion a été choisi parmi {len(s['evalues'])} variantes : sa validation est gonflée par la "
              "sélection. Seul ce test, ouvert une fois, dit ce qu'il vaut. L'évolution est maintenant close.")


def main():
    ap = argparse.ArgumentParser(description="Boucle d'évolution à la AlphaEvolve")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dossier"); p.add_argument("--nom")
    p.add_argument("--plafond", type=int, default=40); p.add_argument("--par-generation", type=int, default=4)
    p = sp.add_parser("benchmark"); p.add_argument("dossier")
    p = sp.add_parser("verrouiller"); p.add_argument("dossier")
    p.add_argument("--accepter-score-constant", action="store_true")
    p.add_argument("--test-a-venir", action="store_true", help="test = paper trading pas encore collecté")
    p.add_argument("--piege-unilateral", action="store_true", help="sans effet : le piège est unilatéral par défaut depuis le 08/11")
    p = sp.add_parser("parents"); p.add_argument("dossier"); p.add_argument("--k", type=int)
    p.add_argument("--historique", type=int, default=20)
    p = sp.add_parser("nouveau"); p.add_argument("dossier"); p.add_argument("--parent", action="append", required=True)
    p = sp.add_parser("evaluer"); p.add_argument("dossier"); p.add_argument("variante")
    p.add_argument("--idee", required=True); p.add_argument("--niche", default="divers")
    p = sp.add_parser("voir"); p.add_argument("dossier"); p.add_argument("variante")
    p = sp.add_parser("lecons"); p.add_argument("dossier")
    p = sp.add_parser("patrons"); p.add_argument("dossier"); p.add_argument("--variante")
    p.add_argument("--calibrer", type=int, default=0)
    p = sp.add_parser("temoin"); p.add_argument("dossier"); p.add_argument("--capture", required=True)
    p.add_argument("--tolerance", type=float, default=1e-9); p.add_argument("--accepter", metavar="RAISON")
    p = sp.add_parser("tableau"); p.add_argument("dossier"); p.add_argument("--n", type=int, default=5)
    p = sp.add_parser("scelle"); p.add_argument("dossier"); p.add_argument("variante", nargs="?")
    p.add_argument("--force", metavar="RAISON")
    p = sp.add_parser("piste"); p.add_argument("dossier"); p.add_argument("action", choices=["liste", "ouvrir", "fermer"])
    p.add_argument("nom", nargs="?"); p.add_argument("--mecanisme"); p.add_argument("--refute")
    p.add_argument("--depuis", metavar="PISTE"); p.add_argument("--depart", metavar="VARIANTE")
    p.add_argument("--hors-juge", metavar="DONNEE"); p.add_argument("--raison")
    a = ap.parse_args()
    {"init": cmd_init, "benchmark": cmd_benchmark, "verrouiller": cmd_verrouiller, "parents": cmd_parents, "nouveau": cmd_nouveau,
     "evaluer": cmd_evaluer, "voir": cmd_voir, "lecons": cmd_lecons, "patrons": cmd_patrons, "temoin": cmd_temoin,
     "tableau": cmd_tableau, "scelle": cmd_scelle, "piste": cmd_piste}[a.cmd](a)


if __name__ == "__main__":
    main()
