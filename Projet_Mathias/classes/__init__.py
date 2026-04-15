"""
Package classes — modèles génériques pour les données sportives.

Importe directement les classes principales :

    from classes import Joueur, Joueurs, Equipe, Equipes, Match, Matchs
    from classes import Sport, TypeSport, SPORTS
"""

from .joueur import Joueur, Joueurs
from .equipe import Equipe, Equipes
from .match import Match, Matchs
from .sport import (
    Sport, TypeSport, CategorieSport,
    SPORTS, SPORTS_PAR_NOM,
    get_sport, filtrer_par_type, filtrer_par_categorie,
)

__all__ = [
    "Joueur", "Joueurs",
    "Equipe", "Equipes",
    "Match", "Matchs",
    "Sport", "TypeSport", "CategorieSport",
    "SPORTS", "SPORTS_PAR_NOM",
    "get_sport", "filtrer_par_type", "filtrer_par_categorie",
]
