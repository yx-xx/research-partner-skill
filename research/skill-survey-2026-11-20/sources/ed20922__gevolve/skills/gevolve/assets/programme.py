"""Programme que /gevolve fait évoluer.

Seul le code entre les balises EVOLVE-BLOCK-START et EVOLVE-BLOCK-END peut changer :
gevolve refuse toute variante modifiée ailleurs. Il peut y avoir plusieurs blocs.
"""

# EVOLVE-BLOCK-START
def decider(cas):
    """Décision pour un cas. Point de départ volontairement simple et qui fonctionne."""
    return None
# EVOLVE-BLOCK-END


# Interface stable appelée par evaluate.py : ne pas modifier.
def executer(cas):
    return decider(cas)
