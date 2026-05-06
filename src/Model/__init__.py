"""
Package classes — modèles génériques pour les données sportives.

Importe directement les classes principales :

    from classes import Joueur, Joueurs, Equipe, Equipes, Match, Matchs
    from classes import Sport, TypeSport, SPORTS
    from classes import StatsSport
"""

from .joueur import Joueur, Joueurs
from .equipe import Equipe, Equipes
from .match import Match, Matchs
from .sport import (
    Sport, TypeSport, CategorieSport, TypeCompetition,
    SPORTS, SPORTS_PAR_NOM,
    get_sport, filtrer_par_type, filtrer_par_categorie,
    filtrer_par_competition, filtrer,
)
from .stats_sport import StatsSport

__all__ = [
    "Joueur", "Joueurs",
    "Equipe", "Equipes",
    "Match", "Matchs",
    "Sport", "TypeSport", "CategorieSport", "TypeCompetition",
    "SPORTS", "SPORTS_PAR_NOM",
    "get_sport", "filtrer_par_type", "filtrer_par_categorie",
    "filtrer_par_competition", "filtrer",
    "StatsSport",
]
