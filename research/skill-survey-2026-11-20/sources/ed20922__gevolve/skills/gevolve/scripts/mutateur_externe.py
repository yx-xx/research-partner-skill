#!/usr/bin/env python3
"""Mutateur gevolve hors Claude : GPT (Codex CLI) ou n'importe quel modèle OpenRouter.

Usage :
  python3 mutateur_externe.py --modele codex:gpt-5.6-sol --dossier <évolution> \
      --variante <variantes/vNNNN.py> --brief <fichier brief>
  python3 mutateur_externe.py --modele openrouter:deepseek/deepseek-v4-pro-0813 ...

Le modèle ne reçoit QUE du texte : le brief, OBJECTIF.md et les programmes cités dans le
brief (jamais les données, ni le juge, ni un score de validation). Il rend le nouveau contenu
du bloc EVOLVE ; ce script le remet en place dans le fichier de la variante, puis imprime
IDEE / NICHE pour `gevolve.py evaluer`. Aucun accès web, aucun outil côté modèle.
Le modèle utilisé est consigné dans <évolution>/modeles.jsonl.
Code de sortie non nul = échec : lancer quand même `gevolve.py evaluer` (l'échec est compté).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

DEBUT, FIN = "# EVOLVE-BLOCK-START", "# EVOLVE-BLOCK-END"

CONSIGNE = """
Tu n'as accès à aucun outil ni au web : tout ce qu'il te faut est ci-dessus. N'exécute rien.
Réponds EXACTEMENT dans ce format, rien d'autre :

```python
<le NOUVEAU contenu complet du bloc, c'est-à-dire tout le code qui doit se trouver entre
la ligne "# EVOLVE-BLOCK-START" et la ligne "# EVOLVE-BLOCK-END" (ces deux lignes exclues)>
```
IDEE: <ton idée en une phrase>
NICHE: <sa famille, en quelques mots>
"""


def lire(p):
    return Path(p).read_text(encoding="utf-8")


def prompt(dossier, variante, brief):
    morceaux = [brief, "\n\n===== OBJECTIF.md =====\n" + lire(dossier / "OBJECTIF.md")]
    for nom in ("CONTEXTE.md", "LECONS.md"):  # phase A : cadre du mécanisme, état de l'art, leçons (train seulement)
        if (dossier / nom).exists():
            morceaux.append(f"\n\n===== {nom} =====\n" + lire(dossier / nom))
    vus = {variante.resolve()}
    morceaux.append(f"\n\n===== TON FICHIER ({variante.name}) =====\n" + lire(variante))
    for m in re.findall(r"[\w./~-]+\.py", brief):
        p = Path(m).expanduser()
        if not p.is_absolute():
            p = dossier / p
        p = p.resolve()
        if p in vus or not p.exists() or "variantes" not in p.parts:
            continue  # seulement d'autres variantes : jamais le juge ni les données
        vus.add(p)
        morceaux.append(f"\n\n===== {p.name} (inspiration ou second parent) =====\n" + lire(p))
    return "".join(morceaux) + "\n" + CONSIGNE


def appel_openrouter(modele, texte):
    import os
    cle = os.environ.get("OPENROUTER_API_KEY") or (Path.home() / ".config/openrouter/key").read_text().strip()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({"model": modele, "messages": [{"role": "user", "content": texte}],
                         "temperature": 0.8, "max_tokens": 12000}).encode(),
        headers={"Authorization": f"Bearer {cle}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return d["choices"][0]["message"]["content"] or ""


def appel_codex(modele, texte):
    with tempfile.TemporaryDirectory() as vide:
        sortie = Path(vide) / "reponse.txt"
        subprocess.run(["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                        "--sandbox", "read-only", "-C", vide, "-m", modele, "-o", str(sortie), "-"],
                       input=texte, text=True, capture_output=True, timeout=900)
        return sortie.read_text() if sortie.exists() else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modele", required=True)
    ap.add_argument("--dossier", required=True)
    ap.add_argument("--variante", required=True)
    ap.add_argument("--brief", required=True)
    a = ap.parse_args()
    dossier, variante = Path(a.dossier).resolve(), Path(a.variante)
    if not variante.is_absolute():
        variante = dossier / variante
    fournisseur, _, modele = a.modele.partition(":")
    texte = prompt(dossier, variante, lire(a.brief))
    rep = appel_codex(modele, texte) if fournisseur == "codex" else appel_openrouter(modele, texte)
    code = re.search(r"```(?:python)?\n(.*?)```", rep, re.S)
    idee = re.search(r"^IDEE:\s*(.+)$", rep, re.M)
    niche = re.search(r"^NICHE:\s*(.+)$", rep, re.M)
    if not (code and idee):
        sys.exit(f"réponse inexploitable de {a.modele} : {rep[:400]!r}")
    corps = code.group(1).rstrip("\n")
    corps = "\n".join(l for l in corps.split("\n") if l.strip() not in (DEBUT, FIN))
    src = lire(variante)
    i, j = src.index(DEBUT), src.index(FIN)
    variante.write_text(src[:i + len(DEBUT)] + "\n" + corps + "\n" + src[j:], encoding="utf-8")
    nom_court = modele.split("/")[-1]
    with open(dossier / "modeles.jsonl", "a") as f:
        f.write(json.dumps({"variante": variante.parent.name if variante.stem == "programme" else variante.stem, "modele": a.modele}) + "\n")
    print(f"IDEE: [{nom_court}] {idee.group(1).strip()}")
    print(f"NICHE: {(niche.group(1).strip() if niche else 'divers')}")


if __name__ == "__main__":
    main()
