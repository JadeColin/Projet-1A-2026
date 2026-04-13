"""
Package classes — modèles génériques pour les données sportives.

Importe directement les six classes principales :

    from classes import Joueur, Joueurs, Equipe, Equipes, Match, Matchs
"""

from .joueur import Joueur, Joueurs
from .equipe import Equipe, Equipes
from .match import Match, Matchs

__all__ = ["Joueur", "Joueurs", "Equipe", "Equipes", "Match", "Matchs"]
