"""Programme que /gevolve fait évoluer : rangement de colis dans des bacs, un colis à la fois.

Seul le code entre les balises EVOLVE-BLOCK-START et EVOLVE-BLOCK-END peut changer :
gevolve refuse toute variante modifiée ailleurs.
"""

# EVOLVE-BLOCK-START
def priorite(objet, reste, capacite, neuf):
    """Premier bac où le colis tient (first fit) : tous les bacs ouverts à égalité, le bac neuf en dernier."""
    return -1.0 if neuf else 0.0
# EVOLVE-BLOCK-END


# Interface stable appelée par evaluate.py : ne pas modifier.
def executer(cas):
    """Range les colis dans l'ordre d'arrivée. Pour chaque colis, le bac choisi est celui dont la priorité est la
    plus haute parmi les bacs où il tient, un bac neuf compris ; à égalité, le plus ancien."""
    cap = cas["capacite"]
    restes, choix = [], []
    for objet in cas["objets"]:
        meilleur, ou = None, None
        for i, r in enumerate(restes):
            if r >= objet:
                p = priorite(objet, r, cap, False)
                if meilleur is None or p > meilleur:
                    meilleur, ou = p, i
        p = priorite(objet, cap, cap, True)
        if meilleur is None or p > meilleur:
            restes.append(cap)
            ou = len(restes) - 1
        restes[ou] -= objet
        choix.append(ou)
    return choix
