# Example: online bin packing

Items of size 1–100 arrive one at a time and must be placed immediately into bins of capacity 100. The program
only decides the priority of a bin for the incoming item (`priorite(objet, reste, capacite, neuf)`); the frozen
part of `programme.py` does the packing, so the heuristic cannot look ahead.

- **Score**: bins saved per instance compared with first fit (higher is better).
- **Data**: synthetic instances (120 items, Weibull sizes), ten per fictitious day. Train: January–March 2024,
  validation: April–May, sealed test: June.
- **Starting program**: best fit, the best known approach in the benchmark.

| Program (train) | Bins saved per instance | ± |
|---|---|---|
| best fit | +0.287 | 0.017 |
| first fit (the reference) | 0 | |
| best fit avoiding gaps under 3 | −0.097 | 0.019 |
| worst fit | −3.215 | 0.037 |

The folder is shipped **before the lock**. Work on a copy:

```bash
G=~/.claude/skills/gevolve/scripts/gevolve.py
cp -R examples/bin_packing /tmp/bin_packing
python3 $G benchmark /tmp/bin_packing
python3 $G verrouiller /tmp/bin_packing
```

Then `/gevolve run /tmp/bin_packing` in Claude Code. The random-program self-test loses heavily here (z ≈ −68):
that is expected, random packing is simply bad, and the script only prints a warning.

The documents (`FICHE.md`, `RECHERCHE.md`, `CONTEXTE.md`, `OBJECTIF.md`) show what a filled-in evolution looks
like. The lines starting with `Validée par l'utilisateur :` and `Relu par l'utilisateur :` keep their French prefix
because the script checks them; here they are placeholders written by the example's author.
