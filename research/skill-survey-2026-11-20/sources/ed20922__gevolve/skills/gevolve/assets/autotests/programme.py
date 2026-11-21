"""Programme PIÈGE pour `verrouiller` : il décide au hasard (graine fixe, donc déterministe).
Le juge doit lui donner un score proche de 0 face à la référence. S'il le bat nettement,
la référence est malhonnête. Adapter la forme de la décision à celle du vrai programme."""
import hashlib, json

# EVOLVE-BLOCK-START
def decider(cas):
    h = int(hashlib.sha256(json.dumps(cas, sort_keys=True).encode()).hexdigest(), 16)
    return ["oui", "non", None][h % 3]  # à adapter : mêmes décisions possibles que programme.py
# EVOLVE-BLOCK-END


def executer(cas):
    return decider(cas)
