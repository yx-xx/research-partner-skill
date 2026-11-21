"""Exécute le programme évolué, séparé du juge. FIGÉ avec le juge.

Lancé par evaluate.py sans site utilisateur (python -s), avec un environnement réduit à quatre
variables (dont PYTHONHASHSEED=0, que -I faisait ignorer), depuis un dossier vide. Lit une entrée JSON par ligne sur stdin, répond une décision JSON par ligne.
Le programme ne voit donc que l'entrée du cas en cours : ni la vérité, ni les cas futurs,
ni les autres splits, ni la mémoire du juge. Ce qu'il imprime part sur stderr et ne peut
pas se mêler aux décisions.

Une fois le programme chargé, un crochet d'audit (sys.addaudithook, qu'on ne peut plus
retirer) refuse l'écriture de fichiers, la lecture hors de l'installation Python, les
processus, le réseau et ctypes. C'est une seconde barrière : le contrôle statique de
gevolve n'est qu'une liste noire, et le 08/11 on l'a contourné deux fois (annotation en
chaîne évaluée par typing, gi_frame.f_builtins["open"]).
"""
import importlib.util
import json
import os
import sys

BLOQUES = ("os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty", "os.kill",
           "os.killpg", "subprocess.", "socket.", "ctypes.", "os.remove", "os.rename", "os.rmdir",
           "os.mkdir", "os.chmod", "os.chown", "os.chflags", "os.lchflags", "os.symlink", "os.link",
           "os.truncate", "os.utime", "os.putenv", "os.unsetenv", "os.setxattr", "os.removexattr",
           "shutil.", "webbrowser.", "pty.", "urllib.", "http.", "ftplib.", "smtplib.", "poplib.",
           "imaplib.", "nntplib.", "telnetlib.", "sqlite3.")
# 14/11 : `_posixsubprocess.fork_exec` lance un processus sans aucun événement d'audit, et un
# sous-interpréteur n'hérite pas du crochet. On refuse donc le chargement de ces modules, par
# l'événement « import » (levé aussi pour un module d'extension chargé par importlib).
IMPORTS_BLOQUES = {"_posixsubprocess", "subprocess", "multiprocessing", "_multiprocessing", "ctypes", "_ctypes",
                   "socket", "_socket", "ssl", "_ssl", "mmap", "pty", "fcntl", "resource", "_posixshmem",
                   "_interpreters", "_xxsubinterpreters", "_interpchannels", "_xxinterpchannels", "_interpqueues",
                   "interpreters", "concurrent", "asyncio", "_asyncio", "selectors", "socketserver", "xmlrpc",
                   "_testcapi", "_testinternalcapi", "_testlimitedcapi", "_testmultiphase", "dbm", "_dbm", "_gdbm",
                   "shelve", "webbrowser", "http", "urllib", "ftplib", "smtplib", "_winapi", "msvcrt", "pip",
                   "ensurepip", "venv", "runpy", "code", "codeop", "pdb", "bdb", "idlelib", "tkinter", "_tkinter"}
ECRITURE = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


def fermer_les_sorties():
    racines = tuple({os.path.realpath(p) + os.sep
                     for p in (sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix)})
    realpath, fspath = os.path.realpath, os.fspath

    def dans_python(chemin):
        try:
            return realpath(fspath(chemin)).startswith(racines)
        except (TypeError, ValueError):
            return False

    def garde(ev, args):
        if ev == "open":
            chemin, mode, drapeaux = (tuple(args) + (None, None, None))[:3]
            if isinstance(chemin, int):
                return  # descripteurs déjà ouverts (stdin, stdout, stderr) : rien de neuf
            ecrit = (any(c in mode for c in "wax+") if isinstance(mode, str)
                     else bool((drapeaux or 0) & ECRITURE))
            if ecrit or not dans_python(chemin):
                raise PermissionError(f"gevolve : fichier refusé au programme évolué ({chemin})")
        elif ev == "import":
            if args and isinstance(args[0], str) and args[0].split(".")[0] in IMPORTS_BLOQUES:
                raise PermissionError(f"gevolve : module {args[0]} refusé au programme évolué")
        elif ev in ("os.listdir", "os.scandir"):
            if args and args[0] is not None and not dans_python(args[0]):
                raise PermissionError("gevolve : lecture de dossier refusée au programme évolué")
        elif ev.startswith(BLOQUES):
            raise PermissionError(f"gevolve : {ev} refusé au programme évolué")

    sys.addaudithook(garde)


def main():
    decisions = sys.stdout
    sys.stdout = sys.stderr  # avant le chargement : un print du programme ne décale rien
    # 14/11 : lancé sans -I (qui faisait ignorer PYTHONHASHSEED=0 : hash() changeait d'un lancement à
    # l'autre). Le dossier du juge ne doit donc pas rester dans sys.path, et le hasard global est semé.
    ici = os.path.dirname(os.path.realpath(__file__))
    sys.path[:] = [p for p in sys.path if p and os.path.realpath(p) != ici]
    for nom in IMPORTS_BLOQUES:
        sys.modules.pop(nom, None)
    import random
    random.seed(0)
    spec = importlib.util.spec_from_file_location("programme_evolue", sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    code = spec.loader.get_code("programme_evolue")  # lu AVANT le crochet ; exécuté APRÈS,
    fermer_les_sorties()                              # pour que le code de premier niveau soit couvert
    exec(code, module.__dict__)
    for ligne in sys.stdin:
        decisions.write(json.dumps(module.executer(json.loads(ligne))) + "\n")
        decisions.flush()


main()
